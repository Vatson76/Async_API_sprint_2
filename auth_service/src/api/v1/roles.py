from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from db import db
from models.roles import Role, UserRole
from models.users import User
from services.helpers import admin_required, rate_limit

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("roles/add", methods=["POST"])
@rate_limit()
@jwt_required()
@admin_required()
def create_role():
    if not request.json:
        return jsonify({"msg": "Missing JSON in request"}), HTTPStatus.BAD_REQUEST
    if "name" not in request.json:
        return jsonify({"msg": "Missing name parameter"}), HTTPStatus.BAD_REQUEST
    data = request.json
    name = data["name"]
    if db.session.query(Role).filter_by(name=name).first() is None:
        try:
            new_role = Role(name=name, description=data.get("description"))
            db.session.add(new_role)
        except:
            db.rollback()
        else:
            db.session.commit()
        return jsonify({"message": "Role created"}), HTTPStatus.CREATED
    return (
        jsonify(
            message="Wrong data",
            errors=[{"name": f"Role name <{name}> already exists"}],
        ),
        HTTPStatus.BAD_REQUEST,
    )


@admin.route("roles/", methods=["GET"])
@rate_limit()
@jwt_required()
@admin_required()
def roles_list():
    roles = db.session.query(Role.id, Role.name, Role.description).all()
    result = [
        {"uuid": role.id, "name": role.name, "description": role.description}
        for role in roles
    ]
    return jsonify(result), HTTPStatus.OK


@admin.route("roles/<uuid:role_uuid>/edit", methods=["PATCH"])
@rate_limit()
@jwt_required()
@admin_required()
def edit_role(role_uuid):
    if not request.json:
        return (
            jsonify({"msg": "Missing JSON in request"}),
            HTTPStatus.BAD_REQUEST,
        )
    if "name" not in request.json:
        return (
            jsonify({"msg": "Missing name parameter"}),
            HTTPStatus.BAD_REQUEST,
        )
    data = request.json
    if len(data["name"]) == 0:
        return (
            jsonify({"message": "The name field cannot be empty"}),
            HTTPStatus.BAD_REQUEST,
        )
    role = db.session.query(Role).get(role_uuid)
    if role is None:
        return (
            jsonify({"message": "Role with such uuid is not found."}),
            HTTPStatus.NOT_FOUND,
        )
    db.session.query(Role).filter_by(id=role_uuid).update(data)
    db.session.commit()
    return jsonify(message="Role edited"), HTTPStatus.OK


@admin.route("roles/<uuid:role_uuid>/delete", methods=["DELETE"])
@rate_limit()
@jwt_required()
@admin_required()
def delete_role(role_uuid):
    role = db.session.query(Role).filter_by(id=role_uuid).first()
    if role is None:
        return (
            jsonify({"message": "Role with such uuid is not found."}),
            HTTPStatus.NOT_FOUND,
        )
    db.session.query(Role).filter_by(id=role_uuid).delete()
    db.session.commit()
    return jsonify(message="Role deleted"), HTTPStatus.NO_CONTENT


@admin.route("/users/<uuid:user_uuid>/roles", methods=["GET"])
@rate_limit()
@jwt_required()
@admin_required()
def get_user_roles_list(user_uuid):
    user = db.session.query(User).get(user_uuid)
    if not user:
        return (
            jsonify({"message": "User with such uuid is not found."}),
            HTTPStatus.NOT_FOUND,
        )
    user_roles = db.session.query(UserRole).filter_by(user_id=user_uuid).all()
    role_ids = [ro.role_id for ro in user_roles]
    result = []
    for role_id in role_ids:
        one_role = db.session.query(Role).filter(
            Role.id == role_id).first().name
        result.append({"name": one_role})
    return jsonify(roles=result), HTTPStatus.OK


@admin.route("/users/<uuid:user_uuid>/add-role", methods=["POST"])
@rate_limit()
@jwt_required()
@admin_required()
def add_user_role(user_uuid):
    data = request.get_json()
    user = db.session.query(User).filter_by(id=user_uuid).first()
    role = db.session.query(Role).filter_by(name=data["name"]).first()
    if role is None:
        return (
            jsonify({"message": "Role with such name is not found."}),
            HTTPStatus.NOT_FOUND,
        )
    user_role = UserRole(user_id=user.id, role_id=role.id)
    db.session.add(user_role)
    db.session.commit()
    return jsonify(message="Role for User created"), HTTPStatus.CREATED


@admin.route("/users/<uuid:user_uuid>/delete-role", methods=["DELETE"])
@rate_limit()
@jwt_required()
@admin_required()
def delete_user_role(user_uuid):
    data = request.get_json()
    user = db.session.query(User).filter_by(id=user_uuid).first()
    role = db.session.query(Role).filter_by(name=data["name"]).first()
    if role is None:
        return (
            jsonify({"message": "Role with such name is not found."}),
            HTTPStatus.NOT_FOUND,
        )
    user_role = (
        db.session.query(UserRole).filter_by(
            user_id=user.id, role_id=role.id).first()
    )
    db.session.delete(user_role)
    db.session.commit()
    return jsonify(message="Role for User deleted"), HTTPStatus.OK
