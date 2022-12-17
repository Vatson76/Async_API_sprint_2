from pydantic import BaseSettings


class Settings(BaseSettings):
    ELASTIC_HOST: str = 'localhost'
    ELASTIC_PORT: int = 9200
    POSTGRES_DB: str = 'postgres'
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'postgres'
    POSTGRES_HOST: str = 'localhost'
    POSTGRES_PORT: int = 5432
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379


settings = Settings()
