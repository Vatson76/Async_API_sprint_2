from http import HTTPStatus


def test_login(client, session, test_user):
    response = client.post(
        "auth/api/v1/auth/login",
        data={
            'email': 'test@mail.ru',
            'password': 'test_password',
        }
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json['access_token']
    assert response.json['refresh_token']


def test_login_by_non_existing_user(client, session):
    response = client.post(
        "auth/api/v1/auth/login",
        data={
            'email': 'non_existing_user@mail.ru',
            'password': 'test_password',
        }
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_login_with_wrong_password(client, session, test_user):
    response = client.post(
        "auth/api/v1/auth/login",
        data={
            'email': 'test@mail.ru',
            'password': 'wrong_password',
        }
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
