import json
import random
import uuid

import pytest
from http import HTTPStatus

from testdata.es_data import persons_data, persons_movies, person


@pytest.mark.asyncio
async def test_person_list(make_get_request):
    response = await make_get_request('/persons/')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == len(persons_data)


@pytest.mark.asyncio
async def test_get_one_person(make_get_request, redis_client):
    random_elem = random.randint(0, len(persons_data)-1)
    person = persons_data[random_elem]
    person_id = person.get('id')
    response = await make_get_request(f'/persons/{person_id}/')
    received_data = response.body
    assert response.status == HTTPStatus.OK
    assert received_data.get('id') == person_id
    assert received_data.get('full_name') == person.get('full_name')
    assert received_data.get('roles') == person.get('roles')
    cache = await redis_client.get(person_id)
    assert cache

#поиск фильмов персоны по id, не работает
@pytest.mark.asyncio
async def test_persons_films_by_id(make_get_request, es_client):
    movie_id = uuid.UUID(persons_movies.get('id'))
    person_id = uuid.UUID(person.get('id'))
    await es_client.create('persons', person_id, person)
    await es_client.create('movies', movie_id, persons_movies)
    response = await make_get_request(f"/persons/{person_id}/film")
    assert response.status == HTTPStatus.OK
    assert response.body.get('film') == person.get('films')


@pytest.mark.parametrize("page, page_size, expected_count", [
    (1, 1, 1),
    (1, 10, 10),
    (2, 10, 10),
    (1, 40, 40),
    (2, 20, 20)
])
@pytest.mark.asyncio
async def test_persons_pagination(
        make_get_request, page, page_size, expected_count):
    response = await make_get_request('/persons/',
                                      params={
                                          "page[number]": page,
                                          "page[size]": page_size}
                                      )
    assert response.status == HTTPStatus.OK
    assert len(response.body) == expected_count


@pytest.mark.asyncio
async def test_person_id_invalid(make_get_request):
    response = await make_get_request('/persons/random_id')
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_genre_sorting_by_inappropriate_field(make_get_request):
    response = await make_get_request(
        '/persons/', params={'sort': '-unknown'}
    )
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_persons_endpoint_cache(make_get_request, redis_client):
    page_size = 10
    response = await make_get_request(
        '/persons/', params={'page[size]': page_size}
    )
    assert response.status == HTTPStatus.OK
    params = {
        'page_size': page_size,
        'page': 1,
        'sort': '',
        'query': None,
        'entity_name': 'persons'
    }
    key = json.dumps(params, sort_keys=True)
    cache = await redis_client.get(key)
    assert cache
