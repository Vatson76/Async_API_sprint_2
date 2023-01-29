from typing import Optional, List

from aioredis import Redis
from fastapi import Depends, Request

from api.v1.auth_router import oauth2_scheme
from app.connections.redis import get_redis
from app.enums import UserRoles
from services.auth_service import AuthService


async def get_current_user_role(
    request: Request,
    redis: Redis = Depends(get_redis),
    # иначе fastapi в /docs не узнает, где нужна авторизация
    dummy_token: Optional[str] = Depends(oauth2_scheme),
) -> str:
    authorization_header: str = request.headers.get("Authorization")
    if not authorization_header:
        return UserRoles.GUEST.value
    token = authorization_header.split(' ')[-1]
    role = await AuthService(redis=redis).authenticate(token=token)
    return role


class AllowedUser:
    def __init__(self, allowed_role: Optional[str] = UserRoles.GUEST.value):
        self.allowed_role = allowed_role

    def __call__(self, role=Depends(get_current_user_role)):
        if role == UserRoles.ADMIN.value:
            return True
        elif self.allowed_role == UserRoles.SUBSCRIBER.value and role != UserRoles.GUEST.value:
            return True
        elif self.allowed_role == UserRoles.GUEST.value and role in (UserRoles.SUBSCRIBER.value, UserRoles.GUEST.value):
            return True
        return False
