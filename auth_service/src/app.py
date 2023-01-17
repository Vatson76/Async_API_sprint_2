from datetime import timedelta
from http import HTTPStatus

from flasgger import Swagger
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from sqlalchemy.future import select

from api.v1 import v1
from commands.admin import commands
from db import init_db, db
from settings import settings
from services.redis import redis

#Models import for creation in db
from models.users import User

app = Flask(__name__)

#Config
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=settings.ACCESS_TOKEN_EXPIRES_HOURS)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=settings.REFRESH_TOKEN_EXPIRES_DAYS)
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"] = settings.JWT_COOKIE_SECURE
app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = settings.POSTGRES_URL

app.register_blueprint(v1)
app.register_blueprint(commands)

jwt = JWTManager(app)

jwt_redis_blocklist = redis

migrate = Migrate(app, db)
init_db(app)

swag = Swagger(app, template_file="swagger/specs.yml")


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return db.session.execute(select(User).where(User.email == identity)).scalars().one()


@app.errorhandler(422)
def resource_not_found(error):
    return jsonify(error=str(error)), HTTPStatus.UNPROCESSABLE_ENTITY


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


if __name__ == '__main__':
    app.run()
