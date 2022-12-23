import aioredis
import asyncio
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch

from testdata.es_data import genres_data, movies_data, persons_data
from testdata.es_mapping import genres_index, movies_index, persons_index
from settings import test_settings


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


async def write_data_to_elastic(es_client: AsyncElasticsearch, index: dict, data: dict):
    index_name = index['index']
    if not await es_client.indices.exists(index=index_name):
        await es_client.indices.create(index_name, index['body'])
    bulk_query = []
    for row in data:
        action = {"index": {"_index": index_name, "_id": row["id"]}}
        doc = row
        bulk_query.append(action)
        bulk_query.append(doc)
    response = await es_client.bulk(bulk_query, index_name, refresh=True)
    if response['errors']:
        raise Exception('Ошибка записи данных в Elasticsearch')


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


@pytest_asyncio.fixture(scope='session', autouse=True)
async def es_write_filmworks(es_client):
    await write_data_to_elastic(es_client, movies_index, movies_data)


@pytest_asyncio.fixture(scope='session', autouse=True)
async def es_write_persons(es_client):
    await write_data_to_elastic(es_client, persons_index, persons_data)


@pytest_asyncio.fixture(scope='session', autouse=True)
async def es_write_genres(es_client):
    await write_data_to_elastic(es_client, genres_index, genres_data)
