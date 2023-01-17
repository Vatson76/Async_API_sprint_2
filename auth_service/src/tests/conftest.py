import flask_migrate
import pytest
import datetime

from sqlalchemy.orm import Session

from app import app, init_db

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from models.roles import Role
from settings import settings


from flask_jwt_extended import create_access_token

from models.users import User
from services.helpers import hash_password
from pathlib import Path


test_database_url = settings.TEST_POSTGRES_URL


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
def session(engine, mocker):
    with Session(engine, expire_on_commit=False) as session:
        mocker.patch('db.db.session', session)
        yield session
        session.rollback()


@pytest.fixture()
def client(flask_app):
    return flask_app.test_client()


@pytest.fixture()
def runner(flask_app):
    return flask_app.test_cli_runner()


@pytest.fixture()
def test_user(session, role_guest):
    password = hash_password('test_password')
    user = User(
        email='test@mail.ru',
        password=password,
        refresh_token='adsfadfadfdaf',
        registered_at=datetime.datetime.now(),
        is_admin=False,
        active=True,
        roles=[role_guest]
    )
    session.add(user)
    session.commit()
    return user


@pytest.fixture()
def test_user_access_token(session, test_user):
    token = create_access_token(test_user.email)
    return token


@pytest.fixture()
def role_guest(session):
    role = Role(
        name='guest',
        description='guest role',
    )
    session.add(role)
    session.commit()
    return role


@pytest.fixture()
def role_superuser(session):
    role = Role(
        name='superuser',
        description='superuser role',
    )
    session.add(role)
    session.commit()
    return role


@pytest.fixture()
def role_staff(session):
    role = Role(
        name='staff',
        description='staff role',
    )
    session.add(role)
    session.commit()
    return role


@pytest.fixture()
def role_test(session):
    role = Role(
        name='test',
        description='test role',
    )
    session.add(role)
    session.commit()
    return role


@pytest.fixture()
def test_admin(session):
    password = hash_password('password123')
    admin = User(
        email='super@mail.ru',
        password=password,
        refresh_token='adsfadfadfdafdserfg',
        registered_at=datetime.datetime.now(),
        is_admin=True,
        active=True,
    )
    session.add(admin)
    session.commit()
    return admin


@pytest.fixture()
def test_admin_access_token(session, test_admin):
    token = create_access_token(test_admin.email)
    return token
