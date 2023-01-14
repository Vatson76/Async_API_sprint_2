from typing import Optional

from http import HTTPStatus
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import (create_access_token, current_user,
                                decode_token, get_jwt, get_jwt_identity,
                                jwt_required)
from flask_pydantic import validate
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.exc import SQLAlchemyError

from models.users import AuthHistory, User
from services.helpers import (add_auth_history,
                                             check_passwords_match,
                                             create_tokens, get_user_from_db,
                                             hash_password, revoke_token,
                                             set_user_refresh_token)
from db import db

auth = Blueprint('auth', __name__, url_prefix='/auth')


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


@auth.route("/authenticate", methods=["GET"])
@jwt_required()
def authenticate():
    user_roles = [role.name for role in current_user.roles]
    return jsonify(user_roles=user_roles)


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
        abort(HTTPStatus.NOT_FOUND, description='User does not exist')
    else:
        existing_password = user.password
        if check_passwords_match(
                existing_password=existing_password,
                entered_password=form.password
        ):
            access_token, refresh_token = create_tokens(identity=user.email)
            set_user_refresh_token(user=user, refresh_token=refresh_token)
            add_auth_history(user, request)
            return jsonify(
                message='Successful Entry',
                access_token=access_token,
                refresh_token=refresh_token
            )
        else:
            abort(HTTPStatus.UNAUTHORIZED, description='Passwords does not match')


@auth.route("/logout", methods=["DELETE"])
@jwt_required(verify_type=False)
def logout():
    token = get_jwt()
    revoke_token(token)

    return jsonify(
        msg=f"{token['type'].capitalize()} token successfully revoked"
    )


@auth.route('/user/change', methods=['POST'])
@jwt_required()
@validate()
def change(form: ChangeFormDataModel):
    user = current_user
    email = form.email
    password = form.password
    if email is not None:
        user.email = email
    if password is not None:
        password = hash_password(form.password)
        user.password = password
    access_token, refresh_token = create_tokens(identity=user.email)
    set_user_refresh_token(user=user, refresh_token=refresh_token)
    db.session.commit()
    return jsonify(
        message='User data is changed.',
        access_token=access_token,
        refresh_token=refresh_token
    ), HTTPStatus.OK


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
        abort(HTTPStatus.UNAUTHORIZED, description='Wrong refresh token')


@auth.route('/users/<uuid:user_uuid>/auth-history', methods=['GET'])
@jwt_required()
def get_auth_history(user_uuid):
    if current_user.id != user_uuid:
        abort(HTTPStatus.FORBIDDEN)
    history = AuthHistory.query.filter_by(user_id=user_uuid).all()
    result = []
    for row in history:
        result.append(
            {
                'id': row.id,
                'user_agent': row.user_agent,
                'ip_address': row.ip_address,
                'created': row.created
             }
        )
    return jsonify(message='User login history',
                   user_login_history=result)
