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

db = SQLAlchemy()