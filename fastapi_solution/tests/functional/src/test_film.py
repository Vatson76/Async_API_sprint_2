import pytest
from http import HTTPStatus


@pytest.mark.asyncio
async def test_get_all_filmworks(es_write_filmworks, make_get_request):
    response = await make_get_request('/films/')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 40

# @pytest.mark.asyncio
# async def test_film(es_write_filmwork, make_get_request):
