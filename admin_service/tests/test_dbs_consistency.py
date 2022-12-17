import os
import sys
from dataclasses import asdict

import psycopg2.extras

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from sqlite_to_postgres.services.postgres.processor import get_db_tables as get_postgres_tables
from sqlite_to_postgres.services.postgres.connection import connection, schema

from sqlite_to_postgres.services.context_managers import conn_context
from sqlite_to_postgres.services.helpers import table_to_dataclass


def test_dbs_consistency():
    with connection.cursor() as postgre_curs, conn_context(
        os.environ.get('SQLITE_DB_PATH')
    ) as sqlite_conn:
        sqlite_cursor = sqlite_conn.cursor()
        tables = get_postgres_tables(cursor=postgre_curs)
        for table_name in tables:
            count_query = "SELECT COUNT(id) from {table_name}"
            postgre_curs.execute(count_query.format(table_name=f"{schema}.{table_name}"))
            result = postgre_curs.fetchall()
            postgres_count = result[0][0]
            sqlite_cursor.execute(count_query.format(table_name=table_name))
            try:
                sqlite_count = sqlite_cursor.fetchone()[0]
            except TypeError:
                sqlite_count = 0
            print()
            assert postgres_count == sqlite_count, (
                'Количество строк в таблице {table} не совпадает.'.format(
                    table=table_name
                )
            )


def test_test_dbs_data_consistency():
    with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as postgre_curs, \
            conn_context(os.environ.get('SQLITE_DB_PATH')) as sqlite_conn:
        sqlite_cursor = sqlite_conn.cursor()
        tables = get_postgres_tables(cursor=postgre_curs)
        for table_name in tables:
            count_query = "SELECT * from {table_name}"
            postgre_curs.execute(count_query.format(table_name=f"{schema}.{table_name}"))
            result = postgre_curs.fetchall()
            for data in result:
                postgres_data = table_to_dataclass[table_name](**data)
                query = count_query.format(
                    table_name=table_name
                ) + f" WHERE {table_name}.id = '{postgres_data.id}'"
                sqlite_cursor.execute(query)
                result = dict(sqlite_cursor.fetchone())
                sqlite_data = table_to_dataclass[table_name](**result)
                assert asdict(postgres_data) == asdict(sqlite_data)
