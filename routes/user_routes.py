from flask import Blueprint, request, jsonify
from services import user_service

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/", methods=["GET"])
def get_users():
    users = user_service.get_all_users()
    return jsonify([u.to_dict() for u in users])

@user_bp.route("/", methods=["POST"])
def create_user():
    data = request.json
    new_user = user_service.create_user(data)
    return jsonify(new_user.to_dict()), 201
