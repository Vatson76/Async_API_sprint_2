import json
import uuid

from typing import Type, Optional, List, Union
from orjson import orjson
from pydantic import BaseModel

from app.core.config import settings
from app.serializers.query_params_classes import PaginationDataParams
from app.toolkits import BaseToolkit
from models.genre import Genre


class GenresToolkit(BaseToolkit):
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
        genre = await self.get_genre_from_cache(genre_id=pk)
        if genre is not None:
            return genre
        else:
            genre = await super().get(pk=pk)
            if genre is not None:
                await self.put_genre_to_cache(genre)
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
        genres = await self.get_genres_from_cache(params=params)
        if genres is not None:
            return genres
        else:
            genres = await super().list(pagination_data=pagination_data)
            if genres is not None:
                await self.put_genres_to_cache(genres=genres, params=params)
                return genres
            else:
                return None

    async def get_genre_from_cache(self, genre_id: Union[str, uuid.UUID]) -> Optional[Genre]:
        data = await self.redis.get(str(genre_id))
        if not data:
            return
        genre = Genre.parse_raw(data)
        return genre

    async def get_genres_from_cache(self, params) -> Optional[List[Genre]]:
        key = json.dumps(params, sort_keys=True)
        data = await self.redis.get(key)
        if not data:
            return
        genres = [Genre.parse_raw(item) for item in orjson.loads(data)]
        return genres

    async def put_genre_to_cache(self, genre: Genre):
        await self.redis.set(genre.uuid, genre.json(by_alias=True), ex=settings.REDIS_CACHE_TTL)
        await self.redis.set(
            genre.uuid,
            genre.json(by_alias=True),
            ex=settings.REDIS_CACHE_TTL
        )

    async def put_genres_to_cache(self, genres: List[Genre], params: dict) -> None:
        key = json.dumps(params, sort_keys=True)
        await self.redis.set(
            key,
            orjson.dumps([genre.json(by_alias=True) for genre in genres]),
            ex=settings.REDIS_CACHE_TTL
        )
