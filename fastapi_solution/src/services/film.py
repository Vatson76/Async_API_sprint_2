import json
from functools import lru_cache
from typing import Optional

import orjson
from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from app.connections.elastic import get_es_connection
from app.connections.redis import get_redis
from app.serializers.query_params_classes import PaginationDataParams
from models.film import ESFilm, Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_all_films(
        self,
        pagination_data: PaginationDataParams,
        genre: str = None,
        query: str = None
    ) -> Optional[list[Film]]:
        params = {
            'page_size': pagination_data.page_size,
            'page': pagination_data.page,
            'sort': pagination_data.sort,
            'genre': genre,
            'query': query
        }
        films = await self._films_from_cache(params)
        if not films:
            films = await self._get_films_from_elastic(pagination_data, genre, query)
            if not films:
                return
            await self._put_films_to_cache(films, params)
        return films

    async def _get_films_from_elastic(
        self,
        pagination_data: PaginationDataParams,
        genre: str = None,
        query: str = None,
        body: Optional[dict] = None
    ) -> Optional[list[Film]]:
        """Returns list of filmworks according to genre or search."""
        if (sort := pagination_data.sort) and sort.startswith('-'):
            sort = sort.lstrip('-')+':desc'
        if genre:
            body = {
                'query': {
                    'nested': {
                        'path': "genres",
                        'query': {
                            'bool': {
                                'must': [
                                    {
                                        'match': {
                                            'genres.id': genre
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            }

        search_fields = [
                'title^5',
                'description^4',
                'genre^3',
                '*_names^2',
            ]
        if query:
            body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": search_fields,
                    }
                }
            }
        films = await self.elastic.search(
            index='movies',
            body=body,
            params={
                'size': pagination_data.page_size,
                'from': pagination_data.page - 1,
                'sort': sort
            }
        )
        return [Film(uuid=doc['_id'], **doc['_source']) for doc in films['hits']['hits']]

    async def get_by_id(self, film_id: str) -> Optional[ESFilm]:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)
        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[ESFilm]:
        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return None
        return ESFilm(uuid=['_id'], **doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[ESFilm]:
        data = await self.redis.get(film_id)
        if not data:
            return
        film = ESFilm.parse_raw(data)
        return film

    async def _films_from_cache(self, params) -> Optional[list[Film]]:
        key = json.dumps(params, sort_keys=True)
        data = await self.redis.get(key)
        if not data:
            return
        films = [Film.parse_raw(item) for item in orjson.loads(data)]
        return films

    async def _put_film_to_cache(self, film: ESFilm):
        await self.redis.set(
            film.uuid,
            film.json(by_alias=True),
            ex=FILM_CACHE_EXPIRE_IN_SECONDS
        )

    async def _put_films_to_cache(self, films, params) -> None:
        key = json.dumps(params, sort_keys=True)
        await self.redis.set(
            key,
            orjson.dumps([film.json(by_alias=True) for film in films]),
            ex=FILM_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_es_connection),
) -> FilmService:
    return FilmService(redis, elastic)
