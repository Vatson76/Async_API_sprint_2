import uuid
from typing import Optional, Type, Union, List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from pydantic import BaseModel
from app.serializers.query_params_classes import PaginationDataParams
from app.toolkits import BaseToolkit, RedisCacheToolkit
from models.film import FilmDetailed

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmsToolkit(BaseToolkit, RedisCacheToolkit):

    def __init__(self, elastic: AsyncElasticsearch, redis: Redis):
        BaseToolkit.__init__(self, elastic)
        RedisCacheToolkit.__init__(self, redis)

    @property
    def entity_name(self) -> str:
        """Имя сущности, над которой будет работать тулкит"""
        return 'movies'

    @property
    def pk_field_name(self) -> str:
        """Наименование ключевого атрибута сущности"""
        return 'id'

    @property
    def entity_model(self) -> Type[BaseModel]:
        """Модель сущности"""
        return FilmDetailed

    @property
    def exc_does_not_exist(self) -> Exception:
        """Класс исключения, вызываемый при ошибке поиска экземпляра модели в get"""
        return Exception('Не удалось получить данные о фильме по указанным параметрам')

    async def list(
        self,
        pagination_data: PaginationDataParams,
        query: str = None,
        genre: str = None,
    ) -> Optional[List[FilmDetailed]]:

        params = {
            'page_size': pagination_data.page_size,
            'page': pagination_data.page,
            'sort': pagination_data.sort,
            'genre': genre,
            'query': query,
            'entity_name': self.entity_name
        }
        films = await self.get_cached_instances(params)
        body = None
        if films is not None:
            return films
        else:
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
            films = await super().list(pagination_data=pagination_data, body=body)
            if films is not None:
                await self.cache_instances_by_params(params, films)
                return films
            else:
                return None

    async def get(self, pk: Union[str, uuid.UUID]):
        film = await self.get_cached_instance_by_pk(pk=pk)
        if film is not None:
            return film
        else:
            film = await super().get(pk=pk)
            await self.cache_instance(film)
            return film
