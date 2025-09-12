import psycopg2
import psycopg2.extras
from config import Config
from flask_sqlalchemy import SQLAlchemy
import pymysql


def get_connection():
    return psycopg2.connect(
        Config.DATABASE_URL,
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def get_mysql_connection():
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
        cursorclass=pymysql.cursors.DictCursor
    )

db = SQLAlchemy()

def init_app_with_binds(app):
    """Inicializar la aplicación con múltiples binds de base de datos"""
    # Configurar binds para múltiples bases de datos
    mysql_uri = f"mysql+pymysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}/{Config.MYSQL_DATABASE}"
    app.config['SQLALCHEMY_BINDS'] = {
        'mysql': mysql_uri
    }
    db.init_app(app)