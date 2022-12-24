import json
from http import HTTPStatus

import pytest

from testdata.es_data import movies_data
from utils.helpers import make_get_request


@pytest.mark.asyncio
async def test_get_all_filmworks():
    response = await make_get_request('/films/', params={'sort': 'imdb_rating'})

    film = response.body[0]
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 40
    assert film['id']
    assert film['imdb_rating'] == 5.5
    assert film['title'] == 'Django'


@pytest.mark.asyncio
async def test_film_desc_sorting():
    response = await make_get_request('/films/', params={'sort': '-imdb_rating'})
    assert response.status == HTTPStatus.OK
    assert response.body[0]['imdb_rating'] == 8.5


@pytest.mark.asyncio
async def test_film_sorting_by_inappropriate_field():
    response = await make_get_request('/films/', params={'sort': '-test'})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_film_pagination():
    response = await make_get_request('/films/', params={'page[size]': 15})
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 15


@pytest.mark.asyncio
async def test_films_endpoint_cache(redis_client):
    page_size = 15
    params = {
        'page_size': page_size,
        'page': 1,
        'sort': '',
        'genre': None,
        'query': None,
        'entity_name': 'movies'
    }
    key = json.dumps(params, sort_keys=True)

    response = await make_get_request('/films/', params={'page[size]': page_size})
    data = await redis_client.get(key)

    assert response.status == HTTPStatus.OK
    assert data


@pytest.mark.asyncio
async def test_get_film(redis_client):
    original_film = movies_data[0]
    film_id = original_film['id']

    response = await make_get_request(f'/films/{film_id}')
    data = await redis_client.get(film_id)

    film = response.body
    assert response.status == HTTPStatus.OK
    assert film['id'] == original_film['id']
    assert film['title'] == original_film['title']
    assert film['imdb_rating'] == original_film['imdb_rating']
    assert film['description'] == original_film['description']
    assert film['genres'] == original_film['genres']
    assert film['actors'] == original_film['actors']
    assert film['writers'] == original_film['writers']
    assert film['directors'] == original_film['directors']
    assert data
