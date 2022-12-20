from typing import List, Dict, Any

import aiohttp
import aioredis
import asyncio
import pytest
from elasticsearch import AsyncElasticsearch, helpers
from pydantic import BaseModel

from testdata.es_data import movies_data
from utils.helpers import gendata, delete_docs
from testdata.es_mapping import movies_index
from settings import test_settings


class HTTPResponse(BaseModel):
    body: Any
    headers: dict
    status: int


@pytest.fixture(scope='session')
async def es_client_maker():
    client = AsyncElasticsearch(**test_settings.ELASTIC_DSN.dict())
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def redis_client_maker():
    client = await aioredis.from_url(
        test_settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    yield client
    client.close()


# @pytest.fixture(scope='session')
# def session():
#     return aiohttp.ClientSession()


@pytest.fixture
def make_get_request():
    async def inner(path: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = test_settings.SERVICE_API_V1_URL + path
        session = aiohttp.ClientSession()
        async with session.get(url, params=params) as response:
            resp = HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
        await session.close()
        return resp
    return inner


@pytest.fixture(scope='session')
async def es_write_filmworks(es_client_maker):
    index = movies_index['index']
    async for es_client in es_client_maker:
        if not await es_client.indices.exists(index=index):
            await es_client.indices.create(index, movies_index['body'])
        await helpers.async_bulk(es_client, gendata(movies_data, index))
        await asyncio.sleep(1)
        yield
        # удаляем загруженные в elastic данные
        await helpers.async_bulk(es_client, delete_docs(movies_data, index))
