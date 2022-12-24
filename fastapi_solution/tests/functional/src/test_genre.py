import json
import random
import uuid
from http import HTTPStatus

import pytest

from testdata.es_data import genres_data
from utils.helpers import make_get_request


@pytest.mark.asyncio
async def test_get_all_genres():
    response = await make_get_request('/genres/')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == len(genres_data)


@pytest.mark.parametrize("page, page_size, expected_count", [
    (1, 1, 1),
    (1, 10, 10),
    (2, 10, 10),
    (1, 40, 40),
    (2, 20, 20)
])
@pytest.mark.asyncio
async def test_genre_pagination(page, page_size, expected_count):
    response = await make_get_request('/genres/',
                                      params={
                                          "page[number]": page,
                                          "page[size]": page_size}
                                      )
    assert response.status == HTTPStatus.OK
    assert len(response.body) == expected_count


@pytest.mark.asyncio
async def test_get_one_genre(redis_client):
    random_elem = random.randint(0, len(genres_data)-1)
    genre = genres_data[random_elem]
    genre_id = genre.get('id')

    response = await make_get_request(f'/genres/{genre_id}/')
    cache = await redis_client.get(genre_id)

    assert response.status == HTTPStatus.OK
    assert response.body.get('id') == genre_id
    assert response.body.get('name') == genre.get('name')
    assert cache


@pytest.mark.asyncio
async def test_genre_sorting_by_inappropriate_field():
    response = await make_get_request(
        '/genres/', params={'sort': '-unknown'}
    )
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_genre_id_invalid():
    response = await make_get_request('/genres/random_id')
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_cache_genre(es_client):
    genre_id = str(uuid.uuid4())
    genre_data = {"id": genre_id, "name": "Test_genre"}
    await es_client.create('genres', genre_id, genre_data)

    response_first = await make_get_request(f'/genres/{genre_id}/')

    assert response_first.status == HTTPStatus.OK

    await es_client.delete('genres', genre_id)

    response_second = await make_get_request(f'/genres/{genre_id}/')

    assert response_second.status == HTTPStatus.OK
    assert response_first.body == response_second.body


@pytest.mark.asyncio
async def test_genres_endpoint_cache(redis_client):
    page_size = 10
    params = {
        'page_size': page_size,
        'page': 1,
        'sort': '',
        'entity_name': 'genres'
    }
    key = json.dumps(params, sort_keys=True)

    response = await make_get_request(
        '/genres/', params={'page[size]': page_size}
    )
    cache = await redis_client.get(key)

    assert response.status == HTTPStatus.OK
    assert cache
