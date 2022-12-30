from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    JWT_SECRET_KEY: str = 'top secret'
    POSTGRES_URL: str = 'postgresql://postgres:postgres@localhost:5432/postgres'

    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379

    REFRESH_TOKEN_EXPIRES_DAYS: int = 1
    ACCESS_TOKEN_EXPIRES_HOURS: int = 1

    JWT_COOKIE_SECURE: bool = False


settings = Settings()

