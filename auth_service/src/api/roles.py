import click as click
from http import HTTPStatus
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from db import db
from models.roles import Role, UserRole
from models.users import User
from services.helpers import admin_required, hash_password

admin = Blueprint('admin', __name__)


@admin.cli.command('createsuperuser')
@click.argument('name')
@click.argument('password')
def create_superuser(name, password):
    hash = hash_password(password)
    superuser = User(login=name, password=hash, is_admin=True)
    db.session.add(superuser)
    db.session.commit()
    return 'Superuser created'


@admin.route('roles/add', methods=['POST'])
@jwt_required()
@admin_required()
def create_role():
    if not request.json:
        return jsonify(
            {
                "msg": "Missing JSON in request"
            }
        ), HTTPStatus.BAD_REQUEST
    if 'name' not in request.json:
        return jsonify(
            {
                "msg": "Missing name parameter"
            }
        ), HTTPStatus.BAD_REQUEST
    data = request.json
    name = data['name']
    if Role.query.filter_by(name=name).first() is None:
        try:
            new_role = Role(name=name, description=data.get('description'))
            db.session.add(new_role)
        except:
            db.rollback()
        else:
            db.session.commit()
        return jsonify({'message': f'Role {name} created'}), HTTPStatus.CREATED
    return jsonify(
        message="Wrong data",
        errors=[{"name": f"Role name <{name}> already exists"}],
    ), HTTPStatus.BAD_REQUEST


@admin.route('roles/get', methods=['GET'])
@jwt_required()
@admin_required()
def roles_list():
    roles = db.session.query(Role.id, Role.name, Role.description).all()
    result = [
        {
            'uuid': role.id,
            'name': role.name,
            'description': role.description
        } for role in roles
    ]
    return jsonify(result), HTTPStatus.OK


@admin.route('roles/<uuid:role_uuid>/edit', methods=['PATCH'])
@jwt_required()
@admin_required()
def edit_role(role_uuid):
    if not request.json:
        return jsonify(
            {
                "msg": "Missing JSON in request"
            }
        ), HTTPStatus.BAD_REQUEST
    if 'name' not in request.json:
        return jsonify(
            {
                "msg": "Missing name parameter"
            }
        ), HTTPStatus.BAD_REQUEST
    data = request.json
    if len(data["name"]) == 0:
        return jsonify(
            {
                'message': 'The name field cannot be empty'
            }
        ), HTTPStatus.BAD_REQUEST
    role = Role.query.get(role_uuid)
    if role is None:
        return jsonify(
            {
                'message': 'Role with such uuid is not found.'
            }
        ), HTTPStatus.NOT_FOUND
    Role.query.filter_by(id=role_uuid).update(data)
    db.session.commit()
    return jsonify(
        message=f'Role with uuid <{role_uuid}> is edited'
    ), HTTPStatus.OK


@admin.route('roles/<uuid:role_uuid>/delete', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_role(role_uuid):
    role = Role.query.filter_by(id=role_uuid).first()
    if role is None:
        return jsonify(
            {
                'message': 'Role with such uuid is not found.'
            }
        ), HTTPStatus.NOT_FOUND
    Role.query.filter_by(id=role_uuid).delete()
    db.session.commit()
    return jsonify(
        message=f'Role with uuid <{role_uuid}> is deleted'
    ), HTTPStatus.OK


@admin.route("/users/<uuid:user_uuid>/roles", methods=["GET"])
@jwt_required()
@admin_required()
def get_user_roles_list(user_uuid):
    user = User.query.get(user_uuid)
    if not user:
        return jsonify(
            {
                'message': 'User with such uuid is not found.'
            }
        ), HTTPStatus.NOT_FOUND
    user_roles = UserRole.query.filter_by(user_id=user_uuid).all()
    role_ids = [ro.role_id for ro in user_roles]
    result = []
    for role_id in role_ids:
        one_role = Role.query.filter(Role.id == role_id).first().name
        result.append({'name': one_role})
    return jsonify(roles=result), HTTPStatus.OK


@admin.route("/users/<uuid:user_uuid>/add-role", methods=["POST"])
@jwt_required()
@admin_required()
def add_user_role(user_uuid):
    data = request.get_json()
    user = User.query.filter_by(id=user_uuid).first()
    role = Role.query.filter_by(name=data['name']).first()
    if role is None:
        return jsonify(
            {
                'message': 'Role with such name is not found.'
            }
        ), HTTPStatus.NOT_FOUND
    user_role = UserRole(user_id=user.id, role_id=role.id)
    db.session.add(user_role)
    db.session.commit()
    return jsonify(message='Role for User created'), HTTPStatus.CREATED


@admin.route('/users/<uuid:user_uuid>/delete-role', methods=['POST'])
@jwt_required()
@admin_required()
def delete_user_role(user_uuid):
    data = request.get_json()
    user = User.query.filter_by(id=user_uuid).first()
    role = Role.query.filter_by(name=data['name']).first()
    user_role = UserRole.query.filter_by(
        user_id=user.id, role_id=role.id).first()
    db.session.delete(user_role)
    db.session.commit()
    return jsonify(message='Role for User deleted'), HTTPStatus.OK
