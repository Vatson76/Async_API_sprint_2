from psycopg2.extras import NamedTupleCursor

from etl.helpers import get_postgres_connection


class PostgresExtractor:
    """
    Получает данные по переданному sql запросу
    :param query: строка запроса, подходящая по структуре под метод format
    и содержащая в себе указатель на last_modified,
    т.к. необходимо вставить дату последней модификации
    """

    def __init__(self, query: str):
        self.query = query

    async def get_data(
            self,
            last_modified: str = '2000-01-01 00:00:01.271835 +00:00',
    ):
        """
            Генератор (дабы не выгружать весь результат запроса в БД в память)
            для получения необходимых данных
        """
        pg_connection = await get_postgres_connection()

        with pg_connection.cursor(cursor_factory=NamedTupleCursor) as pg_cursor:
            pg_cursor.execute(self.query.format(last_modified=last_modified))
            for row in pg_cursor:
                yield row
