from flask import Blueprint, request, jsonify, make_response
from services.auth_service import login_user, register_user
from flask_jwt_extended import (
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies,
    jwt_required,
    unset_jwt_cookies,
    get_jwt_identity,
    create_access_token,
)

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        new_user = register_user(data)

        # Crear tokens para el nuevo usuario
        access_token = create_access_token(identity=new_user.uuid)
        refresh_token = create_refresh_token(identity=new_user.uuid)

        response = make_response(
            jsonify({"msg": "User registered successfully", "user": new_user.to_dict()})
        )

        # Establecer cookies HTTP-only
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        return response, 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Registration failed"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        result = login_user(data)
        if not result:
            return jsonify({"msg": "Invalid credentials"}), 401

        response = make_response(
            jsonify({"msg": "Login successful", "user": result["user"].to_dict()})
        )

        # Establecer cookies HTTP-only
        set_access_cookies(response, result["access_token"])
        set_refresh_cookies(response, result["refresh_token"])

        return response, 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = make_response(jsonify({"msg": "Logout successful"}))
    unset_jwt_cookies(response)
    return response, 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)

    response = make_response(jsonify({"msg": "Token refreshed"}))
    set_access_cookies(response, new_token)
    return response, 200
