import os
import re
from typing import Any, Dict, List, Tuple
from db_game import db_game
from sqlalchemy import text


def evaluateString(lstr: str, decimal: float):

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