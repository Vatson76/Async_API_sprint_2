import abc
import json
import logging

from typing import Any, Optional, Type, Union

from redis import Redis

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        with open(self.file_path, 'w+') as f:
            json.dump(state, f)

    def retrieve_state(self) -> dict:
        try:
            with open(self.file_path, 'r') as f:
                state = json.load(f)
                return state
        except (FileNotFoundError, json.JSONDecodeError):
            return {}


class RedisStorage(BaseStorage):
    def __init__(self, db):
        self.db = db

    def save_state(self, state: dict) -> None:
        self.db.mset(state)

    def retrieve_state(self) -> Union[dict, Redis]:
        return self.db


class State:
    """
    Класс для хранения состояния при работе с данными, чтобы постоянно не перечитывать данные с начала.
    Здесь представлена реализация с сохранением состояния в файл.
    В целом ничего не мешает поменять это поведение на работу с БД или распределённым хранилищем.
    """

    def __init__(self, storage: Type[BaseStorage]):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Set the state for a specific key."""
        self.storage.save_state(state={key: value})

    def get_state(self, key: str) -> Any:
        """Get the state by a specific key."""
        return self.storage.retrieve_state().get(key)
