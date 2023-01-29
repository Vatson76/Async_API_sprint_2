from http import HTTPStatus
import requests

from flask import Blueprint, jsonify, request
from flask import url_for
from flask_pydantic import validate

from settings import oauth_settings
from services.helpers import rate_limit
from services.networks import (
    register_google,
    get_or_create_social_account,
    register_yandex,
    OAuthServices
)

social_network = Blueprint("social", __name__, url_prefix="/social")


#TODO: переделать с использованием шаблонного метода


@social_network.route("/login/<social_network_name>", methods=["GET"])
@rate_limit()
@validate
def social_login(social_network_name: str):
    if social_network_name == OAuthServices.GOOGLE.value:
        google_service = register_google()
        redirect_uri = url_for("v1.social.auth_google", _external=True)
        return google_service.authorize_redirect(redirect_uri=redirect_uri)
    elif social_network_name == OAuthServices.YANDEX.value:
        yandex_service = register_yandex()
        redirect_uri = url_for("v1.social.auth_yandex", _external=True)
        return yandex_service.authorize_redirect(redirect_uri=redirect_uri)


@social_network.route("/auth/<social_network_name>", methods=["GET"])
@rate_limit()
def social_auth(social_network_name: str):
    social_name, email, social_id = None, None, None
    if social_network_name == OAuthServices.GOOGLE.value:
        google_service = register_google()
        token = google_service.authorize_access_token()
        user_info = token.get("userinfo")
        social_id: str = user_info.get("sub")
        email: str = user_info.get("email")
        social_name = OAuthServices.GOOGLE.value
    elif social_network_name == OAuthServices.GOOGLE.value:
        code: str = request.args.get("code")
        yandex_response = requests.post(
            url=oauth_settings.YANDEX_TOKEN_URL,
            data={
                "client_id": oauth_settings.YANDEX_ID,
                "client_secret": oauth_settings.YANDEX_SECRET,
                "code": code,
                "grant_type": "authorization_code",
            },
        ).json()
        access_token: str = yandex_response.get("access_token")
        user_info_response = requests.get(
            url=oauth_settings.YANDEX_PROFILE_URL,
            params={
                "format": "json",
                "with_openid_identity": 1,
                "oauth_token": access_token,
            },
        ).json()
        social_id: str = user_info_response.get("id")
        email: str = user_info_response.get("default_email")
        social_name = OAuthServices.YANDEX.value
    if social_id is None or email is None or social_name is None:
        return jsonify(message='Can not log you in with provided data'), HTTPStatus.BAD_REQUEST
    access_token, refresh_token = get_or_create_social_account(
        social_id, social_name, email)
    return jsonify(
        message=f"You logged in as {email}",
        access_token=access_token,
        refresh_token=refresh_token
    ), HTTPStatus.OK
