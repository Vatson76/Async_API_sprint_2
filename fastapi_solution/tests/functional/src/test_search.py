import pytest

from testdata.es_data import movies_data


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'query': 'The Star'},
                {'status': 200, 'length': 20}
        ),
        (
                {'query': 'Mashed potato'},
                {'status': 404, 'length': 1}
        )
    ]
)
@pytest.mark.asyncio
async def test_search(query_data, expected_answer, make_get_request):
    response = await make_get_request('/films/search', params=query_data)
    assert response.status == expected_answer['status']
    assert len(response.body) == expected_answer['length']
