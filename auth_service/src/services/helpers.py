import hashlib
import os
import random
from datetime import timedelta
from typing import Tuple
from flask_jwt_extended import create_access_token, create_refresh_token

from db import db
from services.redis import redis
from settings import settings
from auth.models import User


def hash_password(password: str) -> str:
    algorithm = 'sha256'
    iterations = random.randint(100000, 150000)
    salt = os.urandom(32)  # Новая соль для данного пользователя
    key = hashlib.pbkdf2_hmac(algorithm, password.encode('utf-8'), salt, iterations)

    return f'{algorithm}${iterations}${salt.hex()}${key.hex()}'


def check_passwords_match(existing_password: str, entered_password: str) -> bool:
    algorithm, iterations, salt, existing_key = existing_password.split('$')
    key = hashlib.pbkdf2_hmac(algorithm, entered_password.encode('utf-8'), bytes.fromhex(salt), int(iterations))
    if existing_key == str(key.hex()):
        return True
    return False


def create_tokens(identity: str) -> Tuple[str, str]:
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    return access_token, refresh_token


def get_token_expire_time(token_type: str):
    if token_type == 'access':
        return timedelta(hours=settings.ACCESS_TOKEN_EXPIRES_HOURS)
    elif token_type == 'refresh':
        return timedelta(hours=settings.REFRESH_TOKEN_EXPIRES_DAYS)


def get_user_from_db(email: str) -> User:
    return User.query.filter_by(email=email).first()


def revoke_token(token):
    jti = token["jti"]
    ttype = token["type"]
    redis.set(jti, "", ex=get_token_expire_time(ttype))


def set_user_refresh_token(user: User, refresh_token: str):
    user.refresh_token = refresh_token
    db.session.commit()
