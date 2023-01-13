from typing import Optional

from pydantic import BaseSettings, PostgresDsn, Field


class Database(BaseSettings):
    db: str = 'public'
    user: str = 'postgres'
    password: str = 'postgres'
    host: str = Field('localhost', env='DB_HOST')
    port: int = Field('5432', env='DB_PORT')

    class Config:
        env_prefix = 'postgres_'


class Settings(BaseSettings):
    JWT_SECRET_KEY: str = 'top secret'
    db = Database()
    POSTGRES_URL: PostgresDsn = f'postgresql://{db.user}:{db.password}@{db.host}:{db.port}/{db.db}'

    REDIS_AUTH_HOST: str = 'localhost'
    REDIS_AUTH_PORT: int = 6379

    REFRESH_TOKEN_EXPIRES_DAYS: int = 1
    ACCESS_TOKEN_EXPIRES_HOURS: int = 1

    JWT_COOKIE_SECURE: bool = False


settings = Settings()

