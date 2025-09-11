from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.record_service import create_record, get_ranking_by_level

record_bp = Blueprint('record', __name__)

@record_bp.route('/create-record', methods=['POST'])
@jwt_required()
def create_new_record():
    """
    Crea un nuevo record para el usuario actual.
    
    Body JSON:
        time (int): Tiempo del juego en segundos
        level (int): Nivel del juego
        difficulty (str): Dificultad del juego (easy, medium, hard)
        errorCount (int): Número de errores
        idUser (str): UUID del usuario
        
    Returns:
        201: {"message": "Record saved successfully"} si se crea exitosamente
        400: Error en los datos
        403: User ID mismatch
    """
    try:
        # Obtener el usuario actual del JWT
        current_user_uuid = get_jwt_identity()
        
        # Obtener datos del body
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validar campos requeridos
        required_fields = ['time', 'level', 'difficulty', 'errorCount', 'idUser']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validar que el idUser coincida con el usuario autenticado
        if data['idUser'] != current_user_uuid:
            return jsonify({"error": "User ID mismatch"}), 403
        
        # Validar dificultades permitidas
        valid_difficulties = ['easy', 'medium', 'hard']
        if data['difficulty'] not in valid_difficulties:
            return jsonify({
                "error": f"Invalid difficulty. Must be one of: {', '.join(valid_difficulties)}"
            }), 400
        
        # Validar que los valores numéricos sean correctos
        try:
            data['time'] = int(data['time'])
            data['level'] = int(data['level'])
            data['errorCount'] = int(data['errorCount'])
        except (ValueError, TypeError):
            return jsonify({"error": "time, level, and errorCount must be valid integers"}), 400
        
        # Validar que los valores sean positivos o cero
        if data['time'] < 0 or data['level'] < 1 or data['errorCount'] < 0:
            return jsonify({"error": "time and errorCount must be >= 0, level must be >= 1"}), 400
        
        # Crear el record
        new_record = create_record(data)
        
        # Devolver mensaje de confirmación
        return jsonify({"message": "Record saved successfully"}), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@record_bp.route('/ranking/<difficulty>/<int:level>', methods=['GET'])
@jwt_required()
def get_level_ranking(difficulty, level):
    """
    Obtiene el ranking de un nivel específico.
    
    URL Parameters:
        difficulty (str): Dificultad del nivel (easy, medium, hard)
        level (int): Número del nivel
        
    Returns:
        200: Ranking con top 5 y posición del usuario actual
        400: Parámetros inválidos
        404: No hay datos para este nivel
    """
    try:
        # Obtener el usuario actual del JWT
        current_user_uuid = get_jwt_identity()
        
        # Validar dificultad
        valid_difficulties = ['easy', 'medium', 'hard']
        if difficulty not in valid_difficulties:
            return jsonify({
                "error": f"Invalid difficulty. Must be one of: {', '.join(valid_difficulties)}"
            }), 400
        
        # Validar nivel
        if level < 1:
            return jsonify({"error": "Level must be >= 1"}), 400
        
        # Obtener el ranking
        ranking = get_ranking_by_level(difficulty, level, current_user_uuid)
        
        if not ranking:
            return jsonify({"error": "No ranking data available for this level"}), 404
        
        if ranking['totalPlayers'] == 0:
            return jsonify({
                "level": level,
                "difficulty": difficulty,
                "top5": [],
                "currentUser": None,
                "totalPlayers": 0,
                "message": "No players have completed this level yet"
            }), 200
        
        return jsonify(ranking), 200
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
