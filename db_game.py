from config import Config
from flask_sqlalchemy import SQLAlchemy
import pymysql

def get_mysql_connection():
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
        cursorclass=pymysql.cursors.DictCursor
    )

db_game = SQLAlchemy()