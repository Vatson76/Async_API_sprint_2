import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db import db
from models.roles import UserRole


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {"schema": "auth"}

    id = db.Column(UUID(as_uuid=True), primary_key=True,
                   default=uuid.uuid4, unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    refresh_token = db.Column(db.String(500), unique=True, nullable=False)
    registered_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=True, default=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    roles = relationship("Role", secondary=UserRole.__table__)


class DeviceTypeEnum(enum.Enum):
    mobile = 'mobile'
    web = 'web'
    smart = 'smart'


class AuthHistory(db.Model):
    __tablename__ = 'auth_history'
    __table_args__ = (
        UniqueConstraint('id', 'device'),
        {
            'postgresql_partition_by': 'LIST (device)',
            'schema': 'auth'
        }
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True,
                   default=uuid.uuid4,  nullable=False)
    user_id = db.Column(UUID(as_uuid=True),
                        db.ForeignKey('auth.users.id',
                                      ondelete="CASCADE"),
                        nullable=False)
    user_agent = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(100))
    device = db.Column(db.Text, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow())


class SocialAccount(db.Model):
    __tablename__ = 'social_account'
    __table_args__ = (
        UniqueConstraint('social_id', 'social_name', name='social_pk'),
        {"schema": "auth"}
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True,
                   default=uuid.uuid4,  nullable=False)
    user_id = db.Column(UUID(as_uuid=True),
                        db.ForeignKey('auth.users.id',
                                      ondelete="CASCADE"),
                        nullable=False)
    user = db.relationship(User,
                           backref=db.backref('social_accounts', lazy=True))

    social_id = db.Column(db.Text, nullable=False)
    social_name = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'
