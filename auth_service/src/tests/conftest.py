from pathlib import Path

import flask_migrate
import pytest
from sqlalchemy.orm import Session

from app import app, init_db

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database, drop_database

test_database_url = 'postgresql://qchat:qchat@localhost:54321/test'


@pytest.fixture(scope='session', autouse=True)
def flask_app():
    app.config.update({
        "TESTING": True,
        'SQLALCHEMY_DATABASE_URI': test_database_url
    })
    init_db(app)
    yield app


@pytest.fixture()
def engine(flask_app):
    engine = create_engine(test_database_url)
    if not database_exists(engine.url):
        create_database(engine.url)
    with flask_app.app_context():
        migrations_path = Path(__file__).resolve().parent.parent.parent / 'migrations'
        flask_migrate.upgrade(migrations_path, 'head')
        yield engine
        flask_migrate.downgrade(migrations_path, 'base')


@pytest.fixture(scope="function", autouse=True)
def session(engine):
    with Session(engine, expire_on_commit=False) as session:
        yield session
        session.rollback()


@pytest.fixture()
def client(flask_app):
    return flask_app.test_client()


@pytest.fixture()
def runner(flask_app):
    return flask_app.test_cli_runner()
