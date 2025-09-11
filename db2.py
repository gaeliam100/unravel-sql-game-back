import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling

load_dotenv()

pool = pooling.MySQLConnectionPool(
    pool_name=os.getenv("DB_POOL_NAME", "pool_app"),
    pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
    pool_reset_session=True,
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASS", ""),
    database=os.getenv("DB_NAME", "unravel_game"),
    charset="utf8mb4",
    collation="utf8mb4_unicode_ci",
)

def get_conn2():
    return pool.get_connection()