from datetime import timedelta

from flask import Flask, jsonify
from db import init_db, db
from auth.auth_router import auth
from flask_jwt_extended import JWTManager

#Models import for creation in db
from auth.models import User
from settings import settings
from services.redis import redis


app = Flask(__name__)

#Config
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=settings.ACCESS_TOKEN_EXPIRES_HOURS)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=settings.REFRESH_TOKEN_EXPIRES_DAYS)
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"] = settings.JWT_COOKIE_SECURE
app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = settings.POSTGRES_URL


app.register_blueprint(auth)
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
def resource_not_found(e):
    return jsonify(error=str(e)), 422


def main():
    init_db(app)
    with app.app_context():
        db.create_all()
    app.run()


if __name__ == '__main__':
    main()

