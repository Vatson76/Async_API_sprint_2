import uuid
import enum

from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import UUID
from db import db


class UserRolesEnum(enum.Enum):
    UNAUTHORIZED = 'UNAUTHORIZED'
    AUTHORIZED = 'AUTHORIZED'
    PAID = 'PAID'
    SUPERUSER = 'SUPERUSER'


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {"schema": "public"}
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(Enum(UserRolesEnum))
    refresh_token = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.login}>'
