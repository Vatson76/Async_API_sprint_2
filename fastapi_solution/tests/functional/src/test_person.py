import json
import random
import uuid
from http import HTTPStatus

import pytest

from testdata.es_data import person, persons_data, persons_movies
from utils.helpers import make_get_request


@pytest.mark.asyncio
async def test_person_list():
    response = await make_get_request('/persons/')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == len(persons_data)


@pytest.mark.asyncio
async def test_get_one_person(redis_client):
    random_elem = random.randint(0, len(persons_data)-1)
    person = persons_data[random_elem]
    person_id = person.get('id')

    response = await make_get_request(f'/persons/{person_id}/')
    cache = await redis_client.get(person_id)

    assert response.status == HTTPStatus.OK
    assert response.body.get('id') == person_id
    assert response.body.get('full_name') == person.get('full_name')
    assert response.body.get('roles') == person.get('roles')
    assert cache


@pytest.mark.asyncio
async def test_persons_films_by_id_with_role_guest(es_client):
    movie_id = uuid.UUID(persons_movies.get('id'))
    person_id = uuid.UUID(person.get('id'))
    person_films = person.get('films')[0]
    await es_client.create('persons', person_id, person)
    await es_client.create('movies', movie_id, persons_movies)

    response = await make_get_request(f"/persons/{person_id}/film")

    assert response.status == HTTPStatus.FORBIDDEN


# @pytest.mark.asyncio
# async def test_persons_films_by_id(es_client):
#     movie_id = uuid.UUID(persons_movies.get('id'))
#     person_id = uuid.UUID(person.get('id'))
#     person_films = person.get('films')[0]
#     await es_client.create('persons', person_id, person)
#     await es_client.create('movies', movie_id, persons_movies)
#
#     response = await make_get_request(f"/persons/{person_id}/film")
#
#     assert response.status == HTTPStatus.OK
#     assert response.body[0].get('id') == person_films.get('id')
#     assert response.body[0].get('title') == person_films.get('title')


@pytest.mark.parametrize("page, page_size, expected_count", [
    (1, 1, 1),
    (1, 10, 10),
    (2, 10, 10),
    (1, 40, 40),
    (2, 20, 20)
])
@pytest.mark.asyncio
async def test_persons_pagination(page, page_size, expected_count):
    response = await make_get_request('/persons/',
                                      params={
                                          "page[number]": page,
                                          "page[size]": page_size}
                                      )
    assert response.status == HTTPStatus.OK
    assert len(response.body) == expected_count


@pytest.mark.asyncio
async def test_person_id_invalid():
    response = await make_get_request('/persons/random_id')
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_genre_sorting_by_inappropriate_field():
    response = await make_get_request(
        '/persons/', params={'sort': '-unknown'}
    )
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_persons_endpoint_cache(redis_client):
    page_size = 10
    params = {
        'page_size': page_size,
        'page': 1,
        'sort': '',
        'query': None,
        'entity_name': 'persons'
    }
    key = json.dumps(params, sort_keys=True)

    response = await make_get_request(
        '/persons/', params={'page[size]': page_size}
    )
    cache = await redis_client.get(key)

    assert response.status == HTTPStatus.OK
    assert cache
