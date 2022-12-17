import os

import psycopg2

connection = psycopg2.connect(
    host=os.environ.get('POSTGRES_HOST', 'localhost'),
    database=os.environ.get('POSTGRES_DB', 'postgres'),
    user=os.environ.get('POSTGRES_USER', 'qchat'),
    password=os.environ.get('POSTGRES_PASSWORD', 'qchat'),
    port=os.environ.get('POSTGRES_PORT', 54321)
)

connection.autocommit = True

schema = os.environ.get('SCHEMA', 'content')
