from flask import Blueprint, jsonify, abort
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_pydantic import validate
from pydantic import BaseModel, validator, EmailStr
from sqlalchemy.exc import SQLAlchemyError

from auth.models import User
from db import db
from services.helpers import hash_password

auth = Blueprint('auth', __name__)


class RegisterFormDataModel(BaseModel):
    email: EmailStr
    password: str
    password2: str

    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v


@auth.route('/register', methods=['POST'])
@validate()
def register(form: RegisterFormDataModel):
    email = form.email
    password = hash_password(form.password)
    user = User(email=email, password=password)
    db.session.add(user)
    try:
        db.session.commit()
    except SQLAlchemyError:
        abort(422, description='User already exists')

    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)

    return jsonify(access_token=access_token, refresh_token=refresh_token)
