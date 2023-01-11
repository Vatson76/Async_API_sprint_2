import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from db import db


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {"schema": "public"}

    id = db.Column(UUID(as_uuid=True), primary_key=True,
                   default=uuid.uuid4, unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    refresh_token = db.Column(db.String, unique=True, nullable=False)
    registered_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=True, default=False)
    active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


class DeviceTypeEnum(enum.Enum):
    mobile = 'mobile'
    web = 'web'
    smart = 'smart'


def create_partition(target, connection, **kw) -> None:
    """ creating partition by session """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "auth_history_smart" 
        PARTITION OF "auth_history" FOR VALUES IN ('smart')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "auth_history_mobile" 
        PARTITION OF "auth_history" FOR VALUES IN ('mobile')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "auth_history_web" 
        PARTITION OF "auth_history" FOR VALUES IN ('web')"""
    )


class AuthHistory(db.Model):
    __tablename__ = 'auth_history'
    # __table_args__ = {"schema": "public"}
    __table_args__ = (
        UniqueConstraint('id', 'device'),
        {
            'postgresql_partition_by': 'LIST (device)',
            'listeners': [('after_create', create_partition)],
        }
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True,
                   default=uuid.uuid4,  nullable=False)
    user_id = db.Column(UUID(as_uuid=True),
                        db.ForeignKey('public.users.id'),
                        nullable=False)
    user_agent = db.Column(db.String, nullable=False)
    ip_address = db.Column(db.String(100))
    device = db.Column(db.Text, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow())
