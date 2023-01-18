from http import HTTPStatus
from sqlalchemy.future import select

from models.roles import Role


def test_role_create(client, session, test_admin_access_token):
    headers = {
        'Authorization': 'Bearer {}'.format(test_admin_access_token)
    }
    response = client.post(
        "auth/api/v1/admin/roles/add",
        headers=headers, json={"name": "test_role"}
    )
    roles = session.execute(select(Role)).scalars().all()

    assert len(roles) == 1
    assert roles[0].name == "test_role"
    assert response.status_code == HTTPStatus.CREATED


def test_role_update(client, session, test_admin_access_token, role_test):
    roles = session.execute(select(Role)).scalars().all()
    role_uuid, role_name = roles[0].id, roles[0].name

    assert role_name == "test"

    headers = {
        'Authorization': 'Bearer {}'.format(test_admin_access_token)
    }
    response = client.patch(
        f"auth/api/v1/admin/roles/{role_uuid}/edit",
        headers=headers, json={"name": "updated_role"}
    )
    roles = session.execute(select(Role)).scalars().all()

    assert response.status_code == HTTPStatus.OK
    assert roles[0].name == "updated_role"


def test_list_roles(client, session, test_admin_access_token,
                    role_test, role_guest, role_superuser, role_staff):
    roles = session.execute(select(Role)).scalars().all()
    result = [
        {
            'uuid': str(role.id),
            'name': role.name,
            'description': role.description
        } for role in roles
    ]
    headers = {
        'Authorization': 'Bearer {}'.format(test_admin_access_token)
    }
    response = client.get("auth/api/v1/admin/roles/", headers=headers)

    assert response.status_code == HTTPStatus.OK
    assert len(roles) == len(response.json)
    assert response.json == result


def test_role_delete(client, session, test_admin_access_token, role_test):
    roles = session.execute(select(Role)).scalars().all()
    role_uuid, role_name = roles[0].id, roles[0].name

    assert role_name == "test"
    assert len(roles) == 1

    headers = {
        'Authorization': 'Bearer {}'.format(test_admin_access_token)
    }
    response = client.delete(
        f"auth/api/v1/admin/roles/{role_uuid}/delete", headers=headers
    )
    roles = session.execute(select(Role)).scalars().all()

    assert len(roles) == 0
    assert response.status_code == HTTPStatus.NO_CONTENT
