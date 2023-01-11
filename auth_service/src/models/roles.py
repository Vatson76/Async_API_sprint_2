import enum
import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID

from db import db


class DefaultRoleEnum(enum.Enum):
    guest = "guest"
    superuser = "superuser"
    staff = "staff"


class Role(db.Model):
    __tablename__ = 'roles'
    __table_args__ = {"schema": "public", "extend_existing": True}

    id = db.Column(UUID(as_uuid=True), primary_key=True,
                   default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(255))
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'{self.name}. {self.description}'

    class Meta:
        PROTECTED_ROLE_NAMES = (
            DefaultRoleEnum.guest.value,
            DefaultRoleEnum.superuser.value,
            DefaultRoleEnum.staff.value,
        )


class UserRole(db.Model):
    __tablename__ = 'user_role'
    __table_args__ = {"schema": "public"}

    id = db.Column(UUID(as_uuid=True), primary_key=True,
                   default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('public.users.id'))
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('public.roles.id'))