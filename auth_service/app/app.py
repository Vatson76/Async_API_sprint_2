import os
from datetime import timedelta

from flask import Flask, jsonify
from db import init_db, db
from auth.auth_router import auth
from flask_jwt_extended import JWTManager

#Models import for creation in db
from auth.models import User


app = Flask(__name__)

app.register_blueprint(auth)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=1)
# Here you can globally configure all the ways you want to allow JWTs to
# be sent to your web application. By default, this will be only headers.
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]

# If true this will only allow the cookies that contain your JWTs to be sent
# over https. In production, this should always be set to True
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get('SECRET_KEY')  # Change this!
jwt = JWTManager(app)


@app.errorhandler(422)
def resource_not_found(e):
    return jsonify(error=str(e)), 422


@app.route('/hello-world')
def hello_world():
    return 'Hello, World!'


def main():
    init_db(app)
    with app.app_context():
        db.create_all()
    app.run()


if __name__ == '__main__':
    main()

