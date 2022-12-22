from pydantic import BaseSettings, Field


class ElasticSettings(BaseSettings):
    hosts: str = Field('elastic_test:9200', env='ELASTIC_URL')


class RedisSettings(BaseSettings):
    host: str = Field('redis_test', env='REDIS_HOST')
    port: str = Field('6379', env='REDIS_PORT')
    decode_responses: bool = True


class TestSettings(BaseSettings):
    ELASTIC_DSN: ElasticSettings = ElasticSettings()
    REDIS_DSN: RedisSettings = RedisSettings()
    REDIS_URL: str = 'redis://redis_test:6379'
    SERVICE_URL: str = 'http://fastapi_test:80'
    SERVICE_API_V1_URL: str = SERVICE_URL + '/api/v1'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


test_settings = TestSettings()
