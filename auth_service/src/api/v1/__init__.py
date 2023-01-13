from flask import Blueprint
from api.v1.roles import admin
from api.v1.users import auth

v1 = Blueprint('v1', __name__, url_prefix='/auth/api/v1')

v1.register_blueprint(admin)
v1.register_blueprint(auth)
