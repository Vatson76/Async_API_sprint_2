import enum
import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID

from db import db


class DefaultRoleEnum(enum.Enum):
    guest = "guest"
    superuser = "superuser"
    staff = "staff"
    subscriber = "subscriber"


class Role(db.Model):
    __tablename__ = 'roles'
    __table_args__ = {"schema": "auth"}

    id = db.Column(UUID(as_uuid=True), primary_key=True,
                   default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(255))
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    class Meta:
        PROTECTED_ROLE_NAMES = (
            DefaultRoleEnum.guest.value,
            DefaultRoleEnum.superuser.value,
            DefaultRoleEnum.staff.value,
            DefaultRoleEnum.subscriber.value,
        )


class UserRole(db.Model):
    __tablename__ = 'user_role'
    __table_args__ = {"schema": "auth"}

    id = db.Column(UUID(as_uuid=True), primary_key=True,
                   default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True),
                        db.ForeignKey('auth.users.id', ondelete="CASCADE"))
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.roles.id'))
