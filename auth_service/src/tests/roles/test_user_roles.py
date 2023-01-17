from http import HTTPStatus
from sqlalchemy.future import select

from models.roles import UserRole, Role
from models.users import User


def get_user_uuid(session, user):
    user_uuid = session.execute(select(User.id).filter_by(
        email=user.email)).scalars().all()[0]
    return user_uuid


def find_role_names(session, user_uuid):
    roles_uuid = session.execute(select(UserRole.role_id).filter_by(
        user_id=user_uuid)).scalars().all()
    role_names = []
    for role_uuid in roles_uuid:
        role_names.append(session.execute(select(Role.name).filter_by(
            id=role_uuid)).scalars().all())
    return role_names


def test_user_role_list(client, session, test_admin,
                        test_admin_access_token, test_user):
    user_uuid = get_user_uuid(session, test_user)
    users_roles = find_role_names(session, user_uuid)
    headers = {
        'Authorization': 'Bearer {}'.format(test_admin_access_token)
    }
    response = client.get(
        f"auth/api/v1/admin/users/{user_uuid}/roles",
        headers=headers
    )
    role_names = []
    for role in users_roles:
        role_names.append({"name": role[0]})

    assert response.status_code == HTTPStatus.OK
    assert response.json["roles"] == role_names


def test_user_add_role(
        client, session, test_admin,
        test_admin_access_token, test_user, role_staff
):
    user_uuid = get_user_uuid(session, test_user)
    user_roles = find_role_names(session, user_uuid)

    assert len(user_roles) == 1
    assert user_roles == [["guest"]]

    headers = {
        'Authorization': 'Bearer {}'.format(test_admin_access_token)
    }
    response = client.post(
        f"auth/api/v1/admin/users/{user_uuid}/add-role",
        headers=headers, json={"name": role_staff.name}
    )
    user_roles = find_role_names(session, user_uuid)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json == {'message': 'Role for User created'}
    assert len(user_roles) == 2
    assert user_roles == [["guest"], ["staff"]]


def test_user_delete_role(
        client, session, test_admin, test_admin_access_token, test_user
):
    user_uuid = get_user_uuid(session, test_user)
    user_roles = find_role_names(session, user_uuid)

    assert len(user_roles) == 1
    assert user_roles == [["guest"]]

    headers = {
        'Authorization': 'Bearer {}'.format(test_admin_access_token)
    }
    response = client.delete(
        f"auth/api/v1/admin/users/{user_uuid}/delete-role",
        headers=headers, json={"name": user_roles[0][0]}
    )
    user_roles = find_role_names(session, user_uuid)

    assert len(user_roles) == 0
    assert response.json == {'message': 'Role for User deleted'}
    assert response.status_code == HTTPStatus.OK
