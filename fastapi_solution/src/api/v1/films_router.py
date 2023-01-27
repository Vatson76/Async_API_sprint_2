from http import HTTPStatus

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends, HTTPException, Query

from app.connections.elastic import get_es_connection
from app.connections.redis import get_redis
from app.dependencies import AllowedUser
from app.serializers.query_params_classes import PaginationDataParams
from models.film import Film, FilmDetailed
from services.films_toolkit import FilmsToolkit

router = APIRouter()


async def get_films_toolkit(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_es_connection),
) -> FilmsToolkit:
    return FilmsToolkit(redis=redis, elastic=elastic)


@router.get(
    '/',
    response_model=list[Film],
    summary='All movies',
    description='Returns all filmworks'
)
async def get_all_filmworks(
    film_service: FilmsToolkit = Depends(get_films_toolkit),
    pagination_data: PaginationDataParams = Depends(PaginationDataParams),
    genre: str = Query(None, description='Filter by genre uuid', alias='filter[genre]'),
    allowed: bool = Depends(AllowedUser('GUEST'))
) -> list[Film]:
    """Returns all filmworks."""
    films = await film_service.list(
        pagination_data=pagination_data,
        genre=genre
    )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Films not found')
    return films


@router.get(
    '/search',
    response_model=list[Film],
    summary='Full-text search',
    description='Returns filmworks according to the search'
)
async def films_search(
    pagination_data: PaginationDataParams = Depends(PaginationDataParams),
    query: str = Query(None, description="Part of the filmwork's data"),
    film_service: FilmsToolkit = Depends(get_films_toolkit),
    allowed: bool = Depends(AllowedUser('SUBSCRIBER'))
) -> list[Film]:
    """Returns list of filmworks by the parameter specified in the query."""
    if not allowed:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Only subscribers can use these endpoint')
    films = await film_service.list(
        pagination_data=pagination_data,
        query=query
    )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Films not found')
    return films


@router.get(
    '/{film_id}',
    response_model=FilmDetailed,
    summary='Information about the film',
    description='Returns information about a movie by its id',
)
async def film_details(
    film_id: str,
    film_service: FilmsToolkit = Depends(get_films_toolkit),
    allowed: bool = Depends(AllowedUser('GUEST'))
) -> FilmDetailed:
    """Returns filmwork's detailed description."""
    film = await film_service.get(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Film not found')
    return FilmDetailed(uuid=film_id, **film.dict(by_alias=True))
