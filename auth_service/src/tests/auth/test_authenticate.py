from http import HTTPStatus


def test_authenticate_user(client, session, test_user, test_user_access_token):
    headers = {
        'Authorization': 'Bearer {}'.format(test_user_access_token)
    }
    response = client.get(
        "auth/api/v1/auth/authenticate",
        headers=headers
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json['user_roles'] == ['guest']
