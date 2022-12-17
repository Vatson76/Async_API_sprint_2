import json
import uuid
from typing import Type, Optional, Union, List

from elasticsearch import NotFoundError
from orjson import orjson
from pydantic import BaseModel

from app.core.config import settings
from app.serializers.query_params_classes import PaginationDataParams
from app.toolkits import BaseToolkit
from models.film import Film
from models.person import Person


class PersonsToolkit(BaseToolkit):
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
        person = await self.get_person_from_cache(person_id=pk)
        if person is not None:
            return person
        else:
            person = await super().get(pk=pk)
            await self.put_person_to_cache(person)
            return person

    async def persons_list(
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
        persons = await self.get_persons_from_cache(params=params)
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
                await self.put_persons_to_cache(persons, params)
                return persons
            else:
                return None

    async def get_persons_films(self, pk: Union[str, uuid.UUID]) -> Optional[List[Film]]:
        try:
            doc = await self.elastic.get(self.entity_name, pk)
        except NotFoundError:
            return None
        return [Film(**film) for film in doc['_source']['films']]

    async def get_person_from_cache(self, person_id: Union[str, uuid.UUID]) -> Optional[Person]:
        data = await self.redis.get(str(person_id))
        if not data:
            return
        person = Person.parse_raw(data)
        return person

    async def get_persons_from_cache(self, params) -> Optional[List[Person]]:
        key = json.dumps(params, sort_keys=True)
        data = await self.redis.get(key)
        if not data:
            return
        persons = [Person.parse_raw(item) for item in orjson.loads(data)]
        return persons

    async def put_person_to_cache(self, person: Person):
        await self.redis.set(
            person.uuid,
            person.json(by_alias=True),
            ex=settings.REDIS_CACHE_TTL
        )

    async def put_persons_to_cache(self, persons: List[Person], params: dict) -> None:
        key = json.dumps(params, sort_keys=True)
        await self.redis.set(
            key,
            orjson.dumps([person.json(by_alias=True) for person in persons]),
            ex=settings.REDIS_CACHE_TTL
        )
