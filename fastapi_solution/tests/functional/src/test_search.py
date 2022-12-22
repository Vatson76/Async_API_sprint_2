import json

import pytest


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'query': 'The Star', 'page[size]': 10},
                {'status': 200, 'length': 10}
        ),
        (
                {'query': 'Mashed potato', 'page[size]': 20},
                {'status': 404, 'length': 1}
        )
    ]
)
@pytest.mark.asyncio
async def test_films_search(query_data, expected_answer, make_get_request):
    response = await make_get_request('/films/search', params=query_data)
    assert response.status == expected_answer['status']
    assert len(response.body) == expected_answer['length']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'query': 'Dan', 'page[size]': 11},
                {'status': 200, 'length': 11}
        ),
        (
                {'query': 'Lui', 'page[size]': 20},
                {'status': 404, 'length': 1}
        )
    ]
)
@pytest.mark.asyncio
async def test_persons_search(query_data, expected_answer, make_get_request):
    response = await make_get_request('/persons/search', params=query_data)
    assert response.status == expected_answer['status']
    assert len(response.body) == expected_answer['length']


@pytest.mark.asyncio
async def test_films_search_cache(make_get_request, redis_client):
    response = await make_get_request('/films/search', params={'query': 'The Star'})
    params = {
        'page_size': 50,
        'page': 1,
        'sort': '',
        'genre': None,
        'query': 'The Star',
        'entity_name': 'movies'
    }
    key = json.dumps(params, sort_keys=True)
    data = await redis_client.get(key)
    assert data


@pytest.mark.asyncio
async def test_persons_search_cache(make_get_request, redis_client):
    response = await make_get_request('/persons/search', params={'query': 'Dan'})
    params = {
        'page_size': 50,
        'page': 1,
        'sort': '',
        'query': 'Dan',
        'entity_name': 'persons'
    }
    key = json.dumps(params, sort_keys=True)
    data = await redis_client.get(key)
    assert data


@pytest.mark.asyncio
async def test_films_search_body(make_get_request):
    response = await make_get_request('/films/search', params={'query': 'The Star', 'page[size]': 10})
    film = response.body[0]
    assert film['id']
    assert film['title'] == 'The Star'
    assert film['imdb_rating'] == 8.5


@pytest.mark.asyncio
async def test_persons_search_body(make_get_request):
    response = await make_get_request('/persons/search', params={'query': 'Dan', 'page[size]': 10})
    person = response.body[0]
    assert person['id']
    assert person['name'] == 'Dan'
    assert person['roles'] == ['actor']
    assert person['film_ids']
