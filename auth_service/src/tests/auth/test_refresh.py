from http import HTTPStatus

from flask_jwt_extended import create_refresh_token


def test_refresh(client, session, test_user):
    refresh_token = create_refresh_token(test_user.email)
    test_user.refresh_token = refresh_token
    session.commit()
    headers = {
        'Authorization': 'Bearer {}'.format(refresh_token)
    }
    response = client.post(
        "auth/api/v1/auth/refresh",
        headers=headers
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json['access_token']


def test_refresh_with_wrong_token(client, session, test_user, test_user_access_token):
    headers = {
        'Authorization': 'Bearer {}'.format(test_user_access_token)
    }
    response = client.post(
        "auth/api/v1/auth/refresh",
        headers=headers
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
