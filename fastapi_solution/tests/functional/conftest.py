import aiohttp
import aioredis
import asyncio
import pytest
from elasticsearch import AsyncElasticsearch, helpers
from pydantic import BaseModel

from .utils.helpers import delete_docs, gendata
from .testdata.es_mapping import movies_index
from .testdata.es_data import data_movie
from .settings import test_settings


class HTTPResponse(BaseModel):
    body: dict
    headers: dict
    status: int


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(**test_settings.ELASTIC_DSN.dict())
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def redis_client():
    client = await aioredis.from_url(
        test_settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    yield client
    client.close()


@pytest.fixture(scope='session')
async def session():
    async with aiohttp.ClientSession() as session:
        yield session
    await session.close()


@pytest.fixture
async def make_get_request(session):
    async def inner(path: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = test_settings.SERVICE_URL + path
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
    return inner


@pytest.fixture(scope='session')
async def es_write_filmwork(es_client):
    index = 'movies'
    if not es_client.indices.exists(index=index):
        es_client.indices.create(movies_index)
    data = data_movie
    await helpers.async_bulk(es_client, gendata(data_movie, index))
    await asyncio.sleep(1)
    yield data
    # удаляем загруженные в elastic данные
    await helpers.async_bulk(es_client, delete_docs(data, index))
