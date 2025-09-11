from flask import Blueprint, request, jsonify
from services.game_service import execute_sql

bp_validate = Blueprint("validate_sql", __name__, url_prefix="/api")

@bp_validate.post("/validate-sql")
def validate_sql():

    data = request.get_json(silent=True) or {}
    query = data.get("query")
    if not isinstance(query, str):
        return jsonify({"error": "No hay query presente en la peticion"}), 400

    status, payload = execute_sql(query)
    return jsonify(payload), status

