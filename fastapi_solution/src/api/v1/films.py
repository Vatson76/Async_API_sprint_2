from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from app.serializers.query_params_classes import PaginationDataParams
from models.film import Film, FilmDetailed
from services.film import FilmService, get_film_service

router = APIRouter()


@router.get(
    '/',
    response_model=list[Film],
    summary='All movies',
    description='Returns all filmworks'
)
async def get_all_filmworks(
    film_service: FilmService = Depends(get_film_service),
    pagination_data: PaginationDataParams = Depends(PaginationDataParams),
    genre: str = Query(None, description='Filter by genre uuid', alias='filter[genre]')
) -> list[Film]:
    """Returns all filmworks."""
    films = await film_service.get_all_films(
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
    film_service: FilmService = Depends(get_film_service)
) -> list[Film]:
    """Returns list of filmworks by the parameter specified in the query."""
    films = await film_service.get_all_films(
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
    film_service: FilmService = Depends(get_film_service)
) -> FilmDetailed:
    """Returns filmwork's detailed description."""
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Film not found')
    return FilmDetailed(uuid=film_id, **film.dict(by_alias=True))
