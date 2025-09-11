import os
import re
from typing import Any, Dict, List, Tuple
from db_game import db_game
from sqlalchemy import text

@app.route('/api/validate_str', methods=['POST'])
def evaluate_string():
    lstr = request.body.get('query')
    #hay tres casos ['^create database (.*);', '{^show tables from (.*);', '^use (.*);']
    patterns = [r'^create database (.*);', r'^show tables from (.*);', r'^use (.*);']
    lstr = lstr.lower()

    if(re.fullmatch(patterns[0], lstr)):#create database (.*);
        return {
            "msg": "success",
            "code": 200
        }
    elif(re.fullmatch(patterns[1], lstr)):#show tables from (.*);
        return {
            "msg": "success",
            "code": 200
        }
    elif(re.fullmatch(patterns[2], lstr)):#use (.*);
        return {
            "msg": "success",
            "code": 200
        }
    else:#ninguna de las anteriores
        return {
            "msg": "error",
            "code": 400
        }
    
@app.route('/api/validate_sql_query', methods=['POST'])
def validate_sql_query():
    sql_query = request.body.get('query')
    decimal = request.body.get('decimal')

    res = db_game.session.execute(text(sql_query))
    if(decimal in [3.2, 3.3, 3.4]):
        if(res.count() == 1):
            return {
                "msg": "success",
                "code": 200
            }
    elif(decimal == 4.2):
        if(res.count() == 2):
            return {
                "msg": "success",
                "code": 200
            }
    else:
        if(res.count() > 0):
            return {
                "msg": "success",
                "code": 200
            }
        else:
            return {
                "msg": "error",
                "code": 400
            }