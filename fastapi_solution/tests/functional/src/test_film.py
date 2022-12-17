import pytest
from http import HTTPStatus
from tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_get_all_filmworks(es_write_filmwork, make_get_request):
    response = await make_get_request('/films')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == test_settings.TEST_QUANTITY

# @pytest.mark.asyncio
# async def test_film(es_write_filmwork, make_get_request):
