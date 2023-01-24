from datetime import timedelta
from http import HTTPStatus

from flasgger import Swagger
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from opentelemetry.sdk.resources import Resource
from sqlalchemy.future import select

from api.v1 import v1
from commands.admin import commands
from db import init_db, db
from settings import settings
from services.redis import redis

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

#Models import for creation in db
from models.users import User


def configure_tracer() -> None:
    trace.set_tracer_provider(TracerProvider(resource=Resource.create(attributes={'service.name': 'auth'})))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name='jaeger',
                agent_port=6831,
            )
        )
    )
    # Чтобы видеть трейсы в консоли
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


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

app.register_blueprint(v1)
app.register_blueprint(commands)

jwt = JWTManager(app)

jwt_redis_blocklist = redis

migrate = Migrate(app, db)
init_db(app)

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
