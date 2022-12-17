from typing import Optional

from elasticsearch import AsyncElasticsearch

es: Optional[AsyncElasticsearch] = None


async def get_es_connection():
    """Функция для установления соединения с es"""
    return es
