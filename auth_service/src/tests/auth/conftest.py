import datetime

import pytest
from models.users import User


@pytest.fixture()
def test_user(session):
    user = User(
        email='test@mail.ru',
        password='1314134134143',
        refresh_token='adsfadfadfdaf',
        registered_at=datetime.datetime.now(),
        is_admin=False,
        active=True
    )
    session.add(user)
    session.commit()
    return user
