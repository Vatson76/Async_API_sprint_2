import os
import psycopg2.extras

from sqlite3 import Row

a = psycopg2.OperationalError

db_path = os.environ.get('SQLITE_DB_PATH')


def get_db_tables(conn, desc=False) -> list[str]:
    curs = conn.cursor()
    curs.execute("SELECT name FROM sqlite_master WHERE type='table';")
    data = curs.fetchall()
    table_names = [table_data['name'] for table_data in data]
    table_names.sort(key=len, reverse=desc)
    return table_names


def read_data_from_table(table_name: str, conn) -> Row:
    curs = conn.cursor()
    curs.execute(f"SELECT * FROM {table_name};")
    for row in curs:
        yield row
