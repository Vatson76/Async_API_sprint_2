import enum

from app import oauth
from db import db
from models.users import SocialAccount, User
from settings import oauth_settings
from services.helpers import (create_tokens, get_user_from_db, hash_password)


class OAuthServices(enum.Enum):
    YANDEX = 'yandex'
    GOOGLE = 'google'


def get_or_create_social_account(social_id: str, social_name: str, email: str):
    user = get_user_from_db(email=email)
    access_token, refresh_token = create_tokens(identity=email)
    if not user:
        user = User(
            email=email,
            password=hash_password("Qwerty123"),
            refresh_token=refresh_token
            )
        db.session.add(user)
        db.session.commit()
    social_account = SocialAccount.query.filter_by(
        social_id=social_id,
        social_name=social_name,
    ).first()
    if not social_account:
        social_account = SocialAccount(
            social_id=social_id,
            social_name=social_name,
            user_id=user.id,
        )
        db.session.add(social_account)
        db.session.commit()
    return access_token, refresh_token


def register_google():
    google_service = oauth.register(
        name=oauth_settings.GOOGLE_PROVIDER,
        client_id=oauth_settings.GOOGLE_CLIENT_ID,
        client_secret=oauth_settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url=oauth_settings.GOOGLE_SERVER_METADATA_URL,
        client_kwargs={"scope": "openid email profile"},
    )
    return google_service


def register_yandex():
    yandex_service = oauth.register(
            name=oauth_settings.YANDEX_PROVIDER,
            client_id=oauth_settings.YANDEX_ID,
            client_secret=oauth_settings.YANDEX_SECRET,
            authorize_url=oauth_settings.YANDEX_AUTHORIZE_URL,
            response_type="code",
            display="popup",
            scope="login:info login:email",
        )
    return yandex_service
