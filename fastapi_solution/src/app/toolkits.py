import json
import uuid
from abc import ABC, abstractmethod
from typing import Optional, Type, Union, List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from orjson import orjson
from pydantic import BaseModel

from app.core.config import settings
from app.serializers.query_params_classes import PaginationDataParams


class BaseToolkit(ABC):
    """Базовый тулкит для реализации базовых REST методов"""

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    @property
    @abstractmethod
    def entity_name(self) -> str:
        """Имя сущности, над которой будет работать тулкит"""
        pass

    @property
    @abstractmethod
    def pk_field_name(self) -> str:
        """Наименование ключевого атрибута сущности"""
        pass

    @property
    @abstractmethod
    def entity_model(self) -> Type[BaseModel]:
        """Модель сущности"""
        pass

    @property
    @abstractmethod
    def exc_does_not_exist(self) -> Exception:
        """Класс исключения, вызываемый при ошибке поиска экземпляра модели в get"""
        pass

    async def list(
            self,
            pagination_data: PaginationDataParams,
            body: Optional[dict] = None
    ):
        if (sort := pagination_data.sort) and sort.startswith('-'):
            sort = sort.lstrip('-')+':desc'
        try:
            data = await self.elastic.search(
                index=self.entity_name,
                body=body,
                params={
                    'size': pagination_data.page_size,
                    'from': pagination_data.page - 1,
                    'sort': sort
                }
            )
        except NotFoundError:
            return None
        return [self.entity_model(uuid=doc['_id'], **doc['_source']) for doc in data['hits']['hits']]

    async def get(self, pk: Union[str, uuid.UUID]):
        try:
            doc = await self.elastic.get(self.entity_name, pk)
        except NotFoundError:
            return None
        return self.entity_model(uuid=doc['_id'], **doc['_source'])


class RedisCacheToolkit(ABC):
    """Класс, предоставляющий возможность кэшировать сущности по ключу"""
    def __init__(self, redis: Redis):
        self.redis = redis

    @property
    @abstractmethod
    def entity_model(self) -> Type[BaseModel]:
        """Модель сущности"""
        pass

    async def _cache_data(self, key: str, data: str):
        await self.redis.set(
            key,
            data,
            ex=settings.REDIS_CACHE_TTL
        )

    async def cache_instance(self, instance: Type[BaseModel]):
        await self._cache_data(
            key=instance.uuid,
            data=instance.json(by_alias=True),
        )

    async def cache_instances_by_params(self, params: dict, instances: List[Type[BaseModel]]):
        await self._cache_data(
            key=json.dumps(params, sort_keys=True),
            data=orjson.dumps([instance.json(by_alias=True) for instance in instances]),
            )

    async def _get_cached_data(self, key: str):
        data = await self.redis.get(str(key))
        if not data:
            return None
        return data

    async def get_cached_instance_by_pk(self, pk: Union[str, uuid.UUID]) -> Optional[Type[BaseModel]]:
        data = await self.redis.get(str(pk))
        if not data:
            return
        instance = self.entity_model.parse_raw(data)
        return instance

    async def get_cached_instances(self, params) -> Optional[List[Type[BaseModel]]]:
        key = json.dumps(params, sort_keys=True)
        data = await self.redis.get(key)
        if not data:
            return
        instances = [self.entity_model.parse_raw(item) for item in orjson.loads(data)]
        return instances
