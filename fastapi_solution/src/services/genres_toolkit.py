import uuid

from typing import Type, Optional, Union

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from pydantic import BaseModel

from app.serializers.query_params_classes import PaginationDataParams
from app.toolkits import BaseToolkit, RedisCacheToolkit
from models.genre import Genre


class GenresToolkit(BaseToolkit, RedisCacheToolkit):

    def __init__(self, elastic: AsyncElasticsearch, redis: Redis):
        BaseToolkit.__init__(self, elastic)
        RedisCacheToolkit.__init__(self, redis)

    @property
    def entity_name(self) -> str:
        """Имя сущности, над которой будет работать тулкит"""
        return 'genres'

    @property
    def pk_field_name(self) -> str:
        """Наименование ключевого атрибута сущности"""
        return 'id'

    @property
    def entity_model(self) -> Type[BaseModel]:
        """Модель сущности"""
        return Genre

    @property
    def exc_does_not_exist(self) -> Exception:
        """Класс исключения, вызываемый при ошибке поиска экземпляра модели в get"""
        return Exception('Не удалось получить данные о жанре по указанным параметрам')

    async def get(self, pk: Union[str, uuid.UUID]):
        genre = await self.get_cached_instance_by_pk(pk=pk)
        if genre is not None:
            return genre
        else:
            genre = await super().get(pk=pk)
            if genre is not None:
                await self.cache_instance(genre)
                return genre
            else:
                return None

    async def list(self, pagination_data: PaginationDataParams, body: Optional[dict] = None):
        params = {
            'page_size': pagination_data.page_size,
            'page': pagination_data.page,
            'sort': pagination_data.sort,
            'entity_name': self.entity_name
        }
        genres = await self.get_cached_instances(params=params)
        if genres is not None:
            return genres
        else:
            genres = await super().list(pagination_data=pagination_data)
            if genres is not None:
                await self.cache_instances_by_params(params, genres)
                return genres
            else:
                return None
