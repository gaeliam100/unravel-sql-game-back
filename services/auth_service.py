from models.user import User
from db import db
from datetime import datetime, timezone
import uuid
import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token

def hash_password(plain_pwd: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_pwd.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(plain_pwd: str, hashed_pwd: str) -> bool:
    return bcrypt.checkpw(plain_pwd.encode('utf-8'), hashed_pwd.encode('utf-8'))

def register_user(data):
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        raise ValueError("username and password are required")

    existing = User.query.filter_by(username=username).first()
    if existing:
        raise ValueError("username already exists")

    new_user = User(
        uuid=str(uuid.uuid4()),# type: ignore
        username=username, # type: ignore
        password=hash_password(password),# type: ignore
        createdAt=datetime.now(timezone.utc)# type: ignore
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user

def login_user(data):
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        raise ValueError("username and password are required")

    user = User.query.filter_by(username=username).first()
    if not user or not check_password(password, user.password):
        return None

    # Crear ambos tokens
    access_token = create_access_token(identity=user.uuid)
    refresh_token = create_refresh_token(identity=user.uuid)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user
    }