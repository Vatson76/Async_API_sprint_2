from datetime import timedelta
from http import HTTPStatus

from authlib.integrations.flask_client import OAuth
from flasgger import Swagger
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor

from sqlalchemy.future import select

from commands.admin import commands
from db import init_db, db
from settings import settings
from services.redis import redis
from services.tracer import configure_tracer


#Models import for creation in db
from models.users import User

if settings.TRACER_ENABLED:
    configure_tracer()
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

#Config
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=settings.ACCESS_TOKEN_EXPIRES_HOURS)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=settings.REFRESH_TOKEN_EXPIRES_DAYS)
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"] = settings.JWT_COOKIE_SECURE
app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = settings.POSTGRES_URL
app.config["SECRET_KEY"] = settings.SECRET_KEY


app.register_blueprint(commands)

jwt = JWTManager(app)

jwt_redis_blocklist = redis

migrate = Migrate(app, db)
init_db(app)

oauth = OAuth(app)
oauth.init_app(app)

swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'APISpecification',
            "route": '/auth/APISpecification',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "specs_route": "/auth/apidocs",
}

swag = Swagger(app, config=swagger_config, template_file="swagger/specs.yml")


if settings.TRACER_ENABLED:
    @app.before_request
    def before_request():
        request_id = request.headers.get('X-Request-Id')
        if not request_id:
            raise RuntimeError('request id is required')
        tracer = trace.get_tracer(__name__)
        span = tracer.start_span('auth')
        span.set_attribute('http.request_id', request_id)
        span.end()


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return db.session.execute(select(User).where(User.email == identity)).scalars().one()


@app.errorhandler(HTTPStatus.UNPROCESSABLE_ENTITY)
def resource_not_found(error):
    return jsonify(error=str(error)), HTTPStatus.UNPROCESSABLE_ENTITY


@app.errorhandler(HTTPStatus.NOT_FOUND)
def not_found(error):
    return jsonify(error=str(error)), HTTPStatus.NOT_FOUND


@app.errorhandler(HTTPStatus.BAD_REQUEST)
def bad_request(error):
    return jsonify(error=str(error)), HTTPStatus.BAD_REQUEST


@app.errorhandler(HTTPStatus.FORBIDDEN)
def forbidden(error):
    return jsonify(error=str(error)), HTTPStatus.FORBIDDEN


@app.errorhandler(HTTPStatus.METHOD_NOT_ALLOWED)
def method_not_allowed(error):
    return jsonify(error=str(error)), HTTPStatus.METHOD_NOT_ALLOWED


if __name__ == '__main__':
    from api.v1 import v1
    app.register_blueprint(v1)
    app.run()
