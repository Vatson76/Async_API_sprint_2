import hashlib
import os
import random
from datetime import datetime, timedelta
from functools import wraps
from http import HTTPStatus
from typing import Tuple

from flask import jsonify, request
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                current_user)
from sqlalchemy.future import select

from models.users import AuthHistory, DeviceTypeEnum, User
from settings import settings
from db import db
from services.redis import redis


def rate_limit():
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            pipline = redis.pipeline()
            now = datetime.now()
            key = f"{request.remote_addr}:{now.minute}"
            pipline.incr(key, 1)
            pipline.expire(key, 59)
            request_number = pipline.execute()[0]
            if request_number > settings.REQUEST_LIMIT_PER_MINUTE:
                return jsonify(
                    msg="Too many requests"), HTTPStatus.TOO_MANY_REQUESTS
            return func(*args, **kwargs)
        return inner
    return wrapper


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            if current_user.is_admin:
                return fn(*args, **kwargs)
            return jsonify(
                message="You need to be an admin to view this page."
            ), HTTPStatus.FORBIDDEN
        return decorator
    return wrapper


def add_auth_history(user, request):
    user_agent = request.headers.get("user-agent", "")
    user_host = request.headers.get("host", "")
    user_agent = user_agent.lower()
    if ("iphone" in user_agent) or ("android" in user_agent):
        device = DeviceTypeEnum.mobile.value
    elif "smart-tv" in user_agent:
        device = DeviceTypeEnum.smart.value
    else:
        device = DeviceTypeEnum.web.value
    user_auth = AuthHistory(user_id=user.id,
                            user_agent=user_agent,
                            ip_address=user_host,
                            device=device)
    db.session.add(user_auth)
    db.session.commit()


def hash_password(password: str) -> str:
    algorithm = "sha256"
    iterations = random.randint(100000, 150000)
    salt = os.urandom(32)  # Новая соль для данного пользователя
    key = hashlib.pbkdf2_hmac(algorithm, password.encode("utf-8"), salt, iterations)

    return f"{algorithm}${iterations}${salt.hex()}${key.hex()}"


def check_passwords_match(existing_password: str, entered_password: str) -> bool:
    algorithm, iterations, salt, existing_key = existing_password.split("$")
    key = hashlib.pbkdf2_hmac(algorithm, entered_password.encode("utf-8"), bytes.fromhex(salt), int(iterations))
    if existing_key == str(key.hex()):
        return True
    return False


def create_tokens(identity: str) -> Tuple[str, str]:
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    return access_token, refresh_token


def get_token_expire_time(token_type: str):
    if token_type == "access":
        return timedelta(hours=settings.ACCESS_TOKEN_EXPIRES_HOURS)
    elif token_type == "refresh":
        return timedelta(hours=settings.REFRESH_TOKEN_EXPIRES_DAYS)


def get_user_from_db(email: str) -> User:
    return db.session.execute(select(User).where(User.email == email)).scalars().one_or_none()


def revoke_token(token):
    jti = token["jti"]
    ttype = token["type"]
    redis.set(jti, "", ex=get_token_expire_time(ttype))


def set_user_refresh_token(user: User, refresh_token: str):
    user.refresh_token = refresh_token
    db.session.commit()
