import uuid
from typing import Type, Optional, Union, List

from aioredis import Redis
from elasticsearch import NotFoundError, AsyncElasticsearch
from pydantic import BaseModel

from app.serializers.query_params_classes import PaginationDataParams
from app.toolkits import BaseToolkit, RedisCacheToolkit
from models.film import Film
from models.person import Person


class PersonsToolkit(BaseToolkit, RedisCacheToolkit):

    def __init__(self, elastic: AsyncElasticsearch, redis: Redis):
        BaseToolkit.__init__(self, elastic)
        RedisCacheToolkit.__init__(self, redis)

    @property
    def entity_name(self) -> str:
        """Имя сущности, над которой будет работать тулкит"""
        return 'persons'

    @property
    def pk_field_name(self) -> str:
        """Наименование ключевого атрибута сущности"""
        return 'id'

    @property
    def entity_model(self) -> Type[BaseModel]:
        """Модель сущности"""
        return Person

    @property
    def exc_does_not_exist(self) -> Exception:
        """Класс исключения, вызываемый при ошибке поиска экземпляра модели в get"""
        return Exception('Не удалось получить данные о человеке по указанным параметрам')

    async def get(self, pk: Union[str, uuid.UUID]):
        person = await self.get_cached_instance_by_pk(pk=pk)
        if person is not None:
            return person
        else:
            person = await super().get(pk=pk)
            await self.cache_instance(person)
            return person

    async def list(
            self,
            pagination_data: PaginationDataParams,
            query: str = None,
    ) -> Optional[List[Person]]:
        params = {
            'page_size': pagination_data.page_size,
            'page': pagination_data.page,
            'sort': pagination_data.sort,
            'query': query,
            'entity_name': self.entity_name
        }
        persons = await self.get_cached_instances(params=params)
        if persons is not None:
            return persons
        else:
            search_fields = [
                    'name^2',
                    'roles',
                ]
            body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": search_fields,
                    }
                }
            } if query is not None else None
            persons = await super().list(pagination_data=pagination_data, body=body)
            if persons is not None:
                await self.cache_instances_by_params(params, persons)
                return persons
            else:
                return None

    async def get_persons_films(self, pk: Union[str, uuid.UUID]) -> Optional[List[Film]]:
        try:
            doc = await self.elastic.get(self.entity_name, pk)
        except NotFoundError:
            return None
        return [Film(**film) for film in doc['_source']['films']]
