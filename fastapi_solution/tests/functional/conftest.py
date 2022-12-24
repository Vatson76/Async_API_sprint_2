import asyncio

import aioredis
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch

from settings import test_settings


pytest_plugins = [
   "fixtures.load_data_in_es",
]


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def es_client():
    async with AsyncElasticsearch(hosts=[test_settings.ELASTIC_DSN.hosts]) as client:
        yield client


@pytest_asyncio.fixture(scope='session', autouse=True)
async def redis_client():
    client = await aioredis.from_url(
        test_settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    yield client
    client.close()
