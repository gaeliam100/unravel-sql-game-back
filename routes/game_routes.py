from flask import Blueprint, request, jsonify
from services.game_service import execute_sql
import game_service as gs

bp_validateStr = Blueprint("validate_str", __name__, url_prefix="/api")

@bp_validateStr.post("/validate-str")
def validate_str():
    lstr = request.json.get('query')
    decimal = request.json.get('decimal')
    return gs.evaluateString(lstr, decimal)