import uuid
from http import HTTPStatus
from typing import List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends, HTTPException

from app.connections.elastic import get_es_connection
from app.connections.redis import get_redis
from app.dependencies import AllowedUser
from app.serializers.query_params_classes import PaginationDataParams
from models.genre import Genre
from services.genres_toolkit import GenresToolkit

router = APIRouter()


async def get_genres_toolkit(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_es_connection),
) -> GenresToolkit:
    return GenresToolkit(redis=redis, elastic=elastic)


@router.get("/{genre_uid}", response_model=Genre)
async def genre_get_api(
    genre_uid: uuid.UUID,
    genres_toolkit: GenresToolkit = Depends(get_genres_toolkit),
    allowed: bool = Depends(AllowedUser('GUEST'))
) -> Genre:
    genre = await genres_toolkit.get(pk=genre_uid)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Genre not found')
    return genre


@router.get("/", response_model=List[Genre])
async def genres_get_list_api(
    pagination_data: PaginationDataParams = Depends(PaginationDataParams),
    genres_toolkit: GenresToolkit = Depends(get_genres_toolkit),
    allowed: bool = Depends(AllowedUser('GUEST'))
) -> List[Genre]:
    genres = await genres_toolkit.list(pagination_data=pagination_data)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Genres not found')
    return genres
