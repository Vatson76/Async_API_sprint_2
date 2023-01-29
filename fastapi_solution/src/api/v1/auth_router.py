from aioredis import Redis
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from app.connections.redis import get_redis
from services.auth_service import AuthService, LoginResponse

router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


@router.post("/login")
async def login_api(
    form_data: OAuth2PasswordRequestForm = Depends(),
    redis: Redis = Depends(get_redis),
    token: str = Depends(oauth2_scheme)
) -> LoginResponse:

    response = await AuthService(redis=redis).login(email=form_data.username, password=form_data.password)

    return response
