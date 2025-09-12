import os
import re
from typing import Any, Dict, List, Tuple
from db import db
from sqlalchemy import text


def execute_sql(lstr: str, decimal: float):

    if(decimal in [1.1, 1.2, 1.3, 2.1]):
        return evaluate_stringQ(lstr);
    else:
        return validate_sql_query(lstr, decimal);

def evaluate_stringQ(lstr: str):
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

def validate_sql_query(sql_query: str, decimal: float):
    try:
        # Obtener el engine de MySQL y ejecutar la consulta
        mysql_engine = db.get_engine(bind='mysql')
        with mysql_engine.connect() as connection:
            res = connection.execute(text(sql_query))
            rows = res.fetchall()
            row_count = len(rows)
        
        if(decimal in [3.2, 3.3, 3.4]):
            if(row_count == 1):
                return {
                    "msg": "success",
                    "code": 200
                }
            else:
                return {
                    "msg": "error",
                    "code": 400
                }
        elif(decimal == 4.2):
            if(row_count == 2):
                return {
                    "msg": "success",
                    "code": 200
                }
            else:
                return {
                    "msg": "error",
                    "code": 400
                }
        else:
            if(row_count > 0):
                return {
                    "msg": "success",
                    "code": 200
                }
            else:
                return {
                    "msg": "error",
                    "code": 400
                }
    except Exception as e:
        return {
            "msg": f"SQL Error: {str(e)}",
            "code": 400
        }