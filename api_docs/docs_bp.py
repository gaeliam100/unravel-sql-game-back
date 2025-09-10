from flask import Blueprint, request, jsonify, make_response
from flask_restx import Api, Resource, fields
from services.auth_service import login_user, register_user
from flask_jwt_extended import (
    set_access_cookies,
    set_refresh_cookies,
    jwt_required,
    unset_jwt_cookies,
    create_access_token,
    create_refresh_token,
)

# Cambiar el nombre del Blueprint para evitar conflictos
docs_bp = Blueprint("docs_bp", __name__)  # Cambió de "auth_bp" a "docs_bp"
api = Api(
    docs_bp,
    doc="/docs/",
    title="Unravel SQL Game API",
    description="Documentación completa de la API",
)

# Modelos para documentación automática
login_model = api.model(
    "Login",
    {
        "username": fields.String(
            required=True, description="Nombre de usuario", example="testuser"
        ),
        "password": fields.String(
            required=True, description="Contraseña", example="password123"
        ),
    },
)

register_model = api.model(
    "Register",
    {
        "username": fields.String(
            required=True, description="Nombre de usuario", example="newuser"
        ),
        "password": fields.String(
            required=True, description="Contraseña", example="password123"
        ),
    },
)

user_response = api.model(
    "UserResponse",
    {
        "uuid": fields.String(description="UUID del usuario"),
        "username": fields.String(description="Nombre de usuario"),
        "createdAt": fields.DateTime(description="Fecha de creación"),
    },
)

success_response = api.model(
    "SuccessResponse",
    {
        "msg": fields.String(description="Mensaje de éxito"),
        "user": fields.Nested(user_response),
    },
)

error_response = api.model(
    "ErrorResponse",
    {
        "error": fields.String(description="Mensaje de error"),
        "msg": fields.String(description="Mensaje de error alternativo"),
    },
)

# Namespace para organizar endpoints
auth_ns = api.namespace("auth", description="Endpoints de autenticación")
users_ns = api.namespace("users", description="Endpoints de usuario")


@auth_ns.route("/login")
class Login(Resource):
    @api.expect(login_model)
    @api.response(200, "Login exitoso", success_response)
    @api.response(401, "Credenciales inválidas", error_response)
    def post(self):
        """Iniciar sesión de usuario"""
        try:
            data = request.get_json()
            result = login_user(data)
            if not result:
                return {"msg": "Invalid credentials"}, 401

            response = make_response(
                {"msg": "Login successful", "user": result["user"].to_dict()}
            )
            set_access_cookies(response, result["access_token"])
            set_refresh_cookies(response, result["refresh_token"])
            return response, 200

        except Exception as e:
            return {"error": str(e)}, 400


@auth_ns.route("/register")
class Register(Resource):
    @api.expect(register_model)
    @api.response(201, "Usuario registrado exitosamente", success_response)
    @api.response(400, "Error en los datos", error_response)
    def post(self):
        """Registrar un nuevo usuario"""
        try:
            data = request.get_json()
            new_user = register_user(data)

            access_token = create_access_token(identity=new_user.uuid)
            refresh_token = create_refresh_token(identity=new_user.uuid)

            response = make_response(
                {"msg": "User registered successfully", "user": new_user.to_dict()}
            )

            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)

            return response, 201

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": "Registration failed"}, 500


@auth_ns.route("/logout")
class Logout(Resource):
    @api.response(200, "Logout exitoso")
    @api.doc(security="cookieAuth")
    def post(self):
        """Cerrar sesión de usuario"""
        from flask_jwt_extended import verify_jwt_in_request

        try:
            verify_jwt_in_request()
            response = make_response({"msg": "Logout successful"})
            unset_jwt_cookies(response)
            return response, 200
        except Exception as e:
            return {"error": "Authentication required"}, 401


@auth_ns.route("/refresh")
class Refresh(Resource):
    @api.response(200, "Token renovado")
    @api.doc(security="cookieAuth")
    def post(self):
        """Renovar token de acceso"""
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

        try:
            verify_jwt_in_request(refresh=True)
            current_user = get_jwt_identity()
            new_token = create_access_token(identity=current_user)

            response = make_response({"msg": "Token refreshed"})
            set_access_cookies(response, new_token)
            return response, 200
        except Exception as e:
            return {"error": "Refresh token required"}, 401


@users_ns.route("/me")
class CurrentUser(Resource):
    @api.response(200, "Usuario actual", user_response)
    @api.response(404, "Usuario no encontrado", error_response)
    @api.response(401, "No autorizado", error_response)
    @api.doc(security="cookieAuth")
    def get(self):
        """Obtener información del usuario actual"""
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        from services.user_service import get_user_by_uuid

        try:
            verify_jwt_in_request()
            current_user_uuid = get_jwt_identity()
            user = get_user_by_uuid(current_user_uuid)
            if not user:
                return {"msg": "user not found"}, 404
            return user.to_dict(), 200
        except Exception as e:
            return {"msg": "Authentication required"}, 401


# Configurar autenticación por cookies en Swagger
authorizations = {
    "cookieAuth": {
        "type": "apiKey",
        "in": "cookie",
        "name": "access_token_cookie",
        "description": "Cookie de autenticación JWT",
    }
}
api.authorizations = authorizations
