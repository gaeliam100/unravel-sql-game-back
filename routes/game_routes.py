from flask import Blueprint, request, jsonify
from services.game_service import execute_sql
from services.game_service import test_mysql_connection

game_bp = Blueprint("game", __name__)

@game_bp.route("/test-mysql-connection", methods=["GET"])
def test_mysql_conn():
    result = test_mysql_connection()
    return jsonify(result), result.get('code', 200)

@game_bp.route("/validate-str", methods=["POST"])
def validate_str():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"msg": "No JSON data provided", "code": 400}), 400
            
        lstr = data.get('query')
        decimal = data.get('decimal')
        
        if not lstr:
            return jsonify({"msg": "Query parameter is required", "code": 400}), 400
        if decimal is None:
            return jsonify({"msg": "Decimal parameter is required", "code": 400}), 400
            
        lstr = lstr.lower()
        result = execute_sql(lstr, decimal)
        return jsonify(result), result.get('code', 200)
        
    except Exception as e:
        return jsonify({"msg": f"Internal error: {str(e)}", "code": 500}), 500