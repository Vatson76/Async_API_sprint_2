from datetime import timedelta
from http import HTTPStatus

from db import init_db, db
from auth_service.src.api.users import auth
from auth_service.src.api.roles import admin
from flask_jwt_extended import JWTManager
from flask import Flask, jsonify
from settings import settings
from services.redis import redis

#Models import for creation in db
from auth_service.src.models.users import User, AuthHistory
from auth_service.src.models.roles import Role, UserRole

app = Flask(__name__)

#Config
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=settings.ACCESS_TOKEN_EXPIRES_HOURS)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=settings.REFRESH_TOKEN_EXPIRES_DAYS)
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"] = settings.JWT_COOKIE_SECURE
app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = settings.POSTGRES_URL

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(admin, url_prefix='/admin')
jwt = JWTManager(app)

jwt_redis_blocklist = redis


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(email=identity).first()


@app.errorhandler(422)
def resource_not_found(error):
    return jsonify(error=str(error)), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify(error=str(error)), HTTPStatus.NOT_FOUND


@app.errorhandler(400)
def bad_request(error):
    return jsonify(error=str(error)), HTTPStatus.BAD_REQUEST


@app.errorhandler(403)
def forbidden(error):
    return jsonify(error=str(error)), HTTPStatus.FORBIDDEN


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify(error=str(error)), HTTPStatus.METHOD_NOT_ALLOWED


def create_app():
    init_db(app)
    with app.app_context():
        db.create_all()
    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
