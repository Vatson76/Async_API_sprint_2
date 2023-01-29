from typing import Any, Type, Optional

import aiohttp
from pydantic import BaseModel

from app.enums import UserRoles
from app.toolkits import RedisCacheToolkit
from app.core.config import settings


class HTTPResponse(BaseModel):
    body: Any
    headers: dict
    status: int


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str


class AuthService(RedisCacheToolkit):

    @property
    def entity_model(self) -> Optional[Type[BaseModel]]:
        """Модель сущности, None, если у сущности отсутствует модель"""
        return None

    auth_service_url = settings.NGINX_URL + '/auth/api/v1'

    async def login(self, email: str, password: str) -> LoginResponse:
        url = self.auth_service_url + '/auth/login'
        session = aiohttp.ClientSession()
        async with session.post(
            url,
            data={'email': email, 'password': password},
        ) as response:
            resp = HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
        await session.close()

        return LoginResponse(**resp.body)

    async def authenticate(self, token: str):
        role = await self._get_cached_data(key=token)
        if role:
            return role
        else:
            url = self.auth_service_url + '/auth/authenticate'
            session = aiohttp.ClientSession()
            async with session.get(
                    url,
                    headers={'Authorization': f'Bearer {token}'},
            ) as response:
                resp = HTTPResponse(
                    body=await response.json(),
                    headers=response.headers,
                    status=response.status,
                )
            await session.close()
            user_roles = resp.body['user_roles']
            if 'superuser' in user_roles:
                role = UserRoles.ADMIN.value
            elif 'subscriber' in user_roles:
                role = UserRoles.SUBSCRIBER.value
            else:
                role = UserRoles.GUEST.value
            await self._cache_data(key=token, data=role)
            return role
