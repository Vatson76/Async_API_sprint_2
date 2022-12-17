from django.core.management import BaseCommand

from sqlite_to_postgres.services.postgres.processor import get_db_tables
from sqlite_to_postgres.services.postgres.connection import connection, schema


class Command(BaseCommand):
    def handle(self, *args, **options):
        with connection.cursor() as postgre_curs:
            table_names = get_db_tables(desc=True, cursor=postgre_curs)
            for table_name in table_names:
                postgre_curs.execute(f"DELETE FROM {schema}.{table_name}")
