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

record_model = api.model(
    "Record",
    {
        "time": fields.Integer(required=True, description="Tiempo del juego en segundos", example=120),
        "level": fields.Integer(required=True, description="Nivel del juego", example=1),
        "difficulty": fields.String(required=True, description="Dificultad del juego", example="easy", enum=["easy", "medium", "hard"]),
        "errorCount": fields.Integer(required=True, description="Número de errores", example=3),
        "idUser": fields.String(required=True, description="UUID del usuario", example="123e4567-e89b-12d3-a456-426614174001"),
    },
)

record_response = api.model(
    "RecordResponse",
    {
        "uuid": fields.String(description="UUID del record"),
        "time": fields.Integer(description="Tiempo del juego en segundos"),
        "level": fields.Integer(description="Nivel del juego"),
        "difficulty": fields.String(description="Dificultad del juego"),
        "errorCount": fields.Integer(description="Número de errores"),
        "createdAt": fields.DateTime(description="Fecha de creación"),
        "idUser": fields.String(description="UUID del usuario"),
    },
)

record_uuid_response = api.model(
    "RecordCreateResponse",
    {
        "message": fields.String(description="Mensaje de confirmación", example="Record saved successfully"),
    },
)

ranking_player = api.model(
    "RankingPlayer", 
    {
        "position": fields.Integer(description="Posición en el ranking", example=1),
        "username": fields.String(description="Nombre del usuario", example="player123"),
        "time": fields.Integer(description="Mejor tiempo en segundos", example=120),
        "errorCount": fields.Integer(description="Menor número de errores", example=2),
        "isCurrentUser": fields.Boolean(description="Si es el usuario actual", example=False)
    }
)

ranking_response = api.model(
    "RankingResponse",
    {
        "level": fields.Integer(description="Nivel consultado", example=1),
        "difficulty": fields.String(description="Dificultad consultada", example="easy"),
        "top5": fields.List(fields.Nested(ranking_player), description="Top 5 jugadores"),
        "currentUser": fields.Nested(ranking_player, description="Datos del usuario actual", allow_null=True),
        "totalPlayers": fields.Integer(description="Total de jugadores que completaron este nivel", example=25)
    }
)

# Namespace para organizar endpoints
auth_ns = api.namespace("auth", description="Endpoints de autenticación")
users_ns = api.namespace("users", description="Endpoints de usuario")
records_ns = api.namespace("record", description="Endpoints de records del juego")


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


@records_ns.route("/create-record")
class CreateRecord(Resource):
    @api.expect(record_model)
    @api.response(201, "Record creado exitosamente", record_uuid_response)
    @api.response(400, "Error en los datos", error_response)
    @api.response(403, "ID de usuario no coincide", error_response)
    @api.response(401, "No autorizado", error_response)
    @api.doc(security="cookieAuth")
    def post(self):
        """Crear un nuevo record con todos los datos del cliente"""
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        from services.record_service import create_record
        from flask import request

        try:
            verify_jwt_in_request()
            current_user_uuid = get_jwt_identity()
            
            data = request.get_json()
            
            if not data:
                return {"error": "No data provided"}, 400
            
            required_fields = ['time', 'level', 'difficulty', 'errorCount', 'idUser']
            for field in required_fields:
                if field not in data:
                    return {"error": f"Missing required field: {field}"}, 400
            
            if data['idUser'] != current_user_uuid:
                return {"error": "User ID mismatch"}, 403
            
            valid_difficulties = ['easy', 'medium', 'hard']
            if data['difficulty'] not in valid_difficulties:
                return {"error": f"Invalid difficulty. Must be one of: {', '.join(valid_difficulties)}"}, 400
            
            try:
                data['time'] = int(data['time'])
                data['level'] = int(data['level'])
                data['errorCount'] = int(data['errorCount'])
            except (ValueError, TypeError):
                return {"error": "time, level, and errorCount must be valid integers"}, 400
            
            if data['time'] < 0 or data['level'] < 1 or data['errorCount'] < 0:
                return {"error": "time and errorCount must be >= 0, level must be >= 1"}, 400
            
            new_record = create_record(data)
            
            return {"message": "Record saved successfully"}, 201
            
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": "Authentication required"}, 401


@records_ns.route("/ranking/<string:difficulty>/<int:level>")
class LevelRanking(Resource):
    @api.response(200, "Ranking del nivel", ranking_response)
    @api.response(400, "Parámetros inválidos", error_response)
    @api.response(404, "No hay datos para este nivel", error_response)
    @api.response(401, "No autorizado", error_response)
    @api.doc(
        security="cookieAuth",
        params={
            "difficulty": {
                "description": "Dificultad del nivel",
                "enum": ["easy", "medium", "hard"],
                "required": True,
                "type": "string"
            },
            "level": {
                "description": "Número del nivel",
                "required": True,
                "type": "integer",
                "minimum": 1
            }
        }
    )
    def get(self, difficulty, level):
        """Obtener ranking de un nivel específico - Top 5 + posición del usuario actual"""
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        from services.record_service import get_ranking_by_level

        try:
            verify_jwt_in_request()
            current_user_uuid = get_jwt_identity()
            
            valid_difficulties = ['easy', 'medium', 'hard']
            if difficulty not in valid_difficulties:
                return {"error": f"Invalid difficulty. Must be one of: {', '.join(valid_difficulties)}"}, 400
            
            if level < 1:
                return {"error": "Level must be >= 1"}, 400
            
            ranking = get_ranking_by_level(difficulty, level, current_user_uuid)
            
            if not ranking:
                return {"error": "No ranking data available for this level"}, 404
            
            if ranking['totalPlayers'] == 0:
                return {
                    "level": level,
                    "difficulty": difficulty,
                    "top5": [],
                    "currentUser": None,
                    "totalPlayers": 0,
                    "message": "No players have completed this level yet"
                }, 200
            
            return ranking, 200
            
        except Exception as e:
            return {"error": "Authentication required"}, 401


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
