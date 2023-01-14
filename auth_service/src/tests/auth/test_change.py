from http import HTTPStatus


def test_change_user_email(client, session, test_user, test_user_access_token):
    headers = {
        'Authorization': 'Bearer {}'.format(test_user_access_token)
    }
    response = client.post(
        "auth/api/v1/auth/user/change",
        data={
            'email': 'changed@mail.ru',
        },
        headers=headers
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json['access_token']
    assert response.json['refresh_token']

    session.refresh(test_user)
    assert test_user.email == 'changed@mail.ru'


def test_change_user_password(client, session, test_user, test_user_access_token):
    headers = {
        'Authorization': 'Bearer {}'.format(test_user_access_token)
    }
    original_password = test_user.password
    response = client.post(
        "auth/api/v1/auth/user/change",
        data={
            'password': 'changed_password',
        },
        headers=headers
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json['access_token']
    assert response.json['refresh_token']

    session.refresh(test_user)
    assert test_user.password != original_password
