from http import HTTPStatus

from sqlalchemy.future import select
from models.users import User


def test_register(client, session):
    response = client.post(
        "auth/api/v1/auth/register",
        data={
            'email': 'test_user@mail.ru',
            'password': 'test_password',
            'password2': 'test_password'
        }
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json['access_token']
    assert response.json['refresh_token']

    users = session.execute(select(User)).scalars().all()
    assert len(users) == 1
    assert users[0].email == 'test_user@mail.ru'


def test_register_with_wrong_email(client, session):
    response = client.post(
        "auth/api/v1/auth/register",
        data={
            'email': 'wrong_email',
            'password': 'test_password',
            'password2': 'test_password'
        }
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_register_with_different_passwords(client, session):
    response = client.post(
        "auth/api/v1/auth/register",
        data={
            'email': 'test_user@mail.ru',
            'password': 'test_password',
            'password2': 'test_password2'
        }
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_register_with_existing_credentials(client, session, test_user):
    response = client.post(
        "auth/api/v1/auth/register",
        data={
            'email': 'test@mail.ru',
            'password': 'test_password',
            'password2': 'test_password'
        }
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
