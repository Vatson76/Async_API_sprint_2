from pydantic import BaseSettings, Field


class ElasticSettings(BaseSettings):
    hosts: str = Field('http://localhost:9200', env='ELASTIC_ADDRESS')


class RedisSettings(BaseSettings):
    host: str = Field('localhost', env='REDIS_HOST')
    port: str = Field('6379', env='REDIS_PORT')
    decode_responses: bool = True


class TestSettings(BaseSettings):
    ELASTIC_DSN: ElasticSettings = ElasticSettings()
    REDIS_DSN: RedisSettings = RedisSettings()
    REDIS_URL: str = 'redis://localhost:6379'
    SERVICE_URL: str = 'http://localhost:8001/api/v1'
    TEST_QUANTITY: int = 1

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


test_settings = TestSettings()
