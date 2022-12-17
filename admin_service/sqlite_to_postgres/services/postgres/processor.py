import psycopg2.extras

from sqlite_to_postgres.services.helpers import table_to_insert_query
from sqlite_to_postgres.services.postgres.connection import schema


def get_db_tables(cursor, desc=False, ) -> list[str]:
    cursor.execute(f"""SELECT table_name FROM information_schema.tables
           WHERE table_schema = '{schema}'""")
    table_names = [table_data[0] for table_data in cursor.fetchall()]
    table_names.sort(key=len, reverse=desc)
    return table_names


def load_data_to_db(data_to_migrate: list, table_name: str, cursor) -> None:
    try:
        psycopg2.extras.execute_batch(cursor, table_to_insert_query[table_name], data_to_migrate)
    except psycopg2.Error as e:
        for data in data_to_migrate:
            try:
                cursor.execute(table_to_insert_query[table_name], data)
            except psycopg2.Error as e:
                pass
