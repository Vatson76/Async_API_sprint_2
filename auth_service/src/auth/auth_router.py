from typing import Optional

from flask import Blueprint, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity, create_access_token, current_user, decode_token
from flask_pydantic import validate
from pydantic import BaseModel, validator, EmailStr
from sqlalchemy.exc import SQLAlchemyError

from auth.models import User
from db import db
from services.helpers import (
    hash_password, get_user_from_db, check_passwords_match,
    create_tokens, revoke_token, set_user_refresh_token
)

auth = Blueprint('auth', __name__)


class PasswordModel(BaseModel):
    password: str


class RegistrationPasswordModel(PasswordModel):
    password2: str

    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v


class UserFormDataModel(PasswordModel):
    email: EmailStr


class RegistrationFormDataModel(UserFormDataModel, RegistrationPasswordModel):
    pass


class ChangeFormDataModel(UserFormDataModel, RegistrationPasswordModel):
    email: Optional[str]
    password: Optional[str]
    password2: Optional[str]


@auth.route('/register', methods=['POST'])
@validate()
def register(form: RegistrationFormDataModel):
    email = form.email
    password = hash_password(form.password)
    access_token, refresh_token = create_tokens(identity=email)
    user = User(email=email, password=password, refresh_token=refresh_token)
    db.session.add(user)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        abort(422, description='User already exists')

    return jsonify(access_token=access_token, refresh_token=refresh_token)


@auth.route('/login', methods=['POST'])
@validate()
def login(form: UserFormDataModel):
    user = get_user_from_db(email=form.email)
    if user is None:
        abort(404, description='User does not exist')
    else:
        existing_password = user.password
        if check_passwords_match(existing_password=existing_password, entered_password=form.password):
            access_token, refresh_token = create_tokens(identity=user.email)
            set_user_refresh_token(user=user, refresh_token=refresh_token)
            return jsonify(access_token=access_token, refresh_token=refresh_token)
        else:
            abort(401, description='Passwords does not match')


@auth.route("/logout", methods=["DELETE"])
@jwt_required(verify_type=False)
def logout():
    token = get_jwt()
    revoke_token(token)

    return jsonify(msg=f"{token['type'].capitalize()} token successfully revoked")


@auth.route('/user/change', methods=['POST'])
@jwt_required()
@validate()
def change(form: ChangeFormDataModel):
    user = current_user
    email = form.email
    password = form.password
    try:
        if email is not None:
            user.email = email
        if password is not None:
            password = hash_password(form.password)
            user.password = password
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        abort(422, 'Incorrect data')


@auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_refresh_token = decode_token(current_user.refresh_token)
    token = get_jwt()
    if user_refresh_token == token:
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return jsonify(access_token=access_token)
    else:
        abort(401, description='Wrong refresh token')
