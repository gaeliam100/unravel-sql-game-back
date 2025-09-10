from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.user_service import get_user_by_uuid  # suponiendo que existe

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    current_user_uuid = get_jwt_identity()
    user = get_user_by_uuid(current_user_uuid)
    if not user:
        return jsonify({"msg": "user not found"}), 404
    return jsonify(user.to_dict()), 200
