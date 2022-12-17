import psycopg2

from app.core.config import settings


async def get_postgres_connection():
    """Функция для установления соединения с postgres"""
    return psycopg2.connect(
            host=settings.POSTGRES_HOST,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            port=settings.POSTGRES_PORT,
        )
