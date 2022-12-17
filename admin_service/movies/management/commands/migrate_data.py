import os
from dataclasses import asdict

from django.core.management import BaseCommand

from sqlite_to_postgres.services.helpers import table_to_dataclass
from sqlite_to_postgres.services.postgres.processor import load_data_to_db, get_db_tables
from sqlite_to_postgres.services.postgres.connection import connection
from sqlite_to_postgres.services.context_managers import conn_context
from sqlite_to_postgres.services.sqllite.processor import read_data_from_table


class Command(BaseCommand):
    def handle(self, *args, **options):
        with connection.cursor() as postgre_curs, conn_context(os.environ.get('SQLITE_DB_PATH')) as sqlite_conn:
            table_names = get_db_tables(cursor=postgre_curs)
            for table_name in table_names:
                data_to_migrate = list()
                for data in read_data_from_table(table_name=table_name, conn=sqlite_conn):
                    data_to_migrate.append(asdict(table_to_dataclass[table_name](**dict(data))))
                    if len(data_to_migrate) == 1000:
                        load_data_to_db(data_to_migrate=data_to_migrate, table_name=table_name, cursor=postgre_curs)
                        data_to_migrate = list()
                if data_to_migrate:
                    load_data_to_db(data_to_migrate=data_to_migrate, table_name=table_name, cursor=postgre_curs)
