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
    TEST_POSTGRES_URL = 'postgresql://postgres:postgres@localhost:5432/test'

    REDIS_AUTH_HOST: str = 'localhost'
    REDIS_AUTH_PORT: int = 6379

    REFRESH_TOKEN_EXPIRES_DAYS: int = 1
    ACCESS_TOKEN_EXPIRES_HOURS: int = 1

    JWT_COOKIE_SECURE: bool = False

    REQUEST_LIMIT_PER_MINUTE: int = 20

    SECRET_KEY: str = Field("secretkey", env="SECRET_KEY")

    TRACER_ENABLED: bool = False
    TRACER_HOST: str = 'jaeger'
    TRACER_PORT: int = 6831


class OAuthSettings(BaseSettings):
    GOOGLE_CLIENT_ID: str = Field(..., env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(..., env="GOOGLE_CLIENT_SECRET")
    GOOGLE_SERVER_METADATA_URL: str = Field(..., env="GOOGLE_SERVER_METADATA_URL")
    GOOGLE_PROVIDER = "google"
    YANDEX_ID: str = Field(..., env="YANDEX_ID")
    YANDEX_SECRET: str = Field(..., env="YANDEX_SECRET")
    YANDEX_PROVIDER = "yandex"
    YANDEX_AUTHORIZE_URL: str = Field(..., env="YANDEX_AUTHORIZE_URL")
    YANDEX_TOKEN_URL: str = Field(..., env="YANDEX_TOKEN_URL")
    YANDEX_PROFILE_URL: str = Field(..., env="YANDEX_PROFILE_URL")

    class Config:
        env_file = '.env'


settings = Settings()
oauth_settings = OAuthSettings()
