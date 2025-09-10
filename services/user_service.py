from models.user import User
from db import db
from datetime import datetime, timezone
import uuid
import bcrypt

def get_all_users():
    return User.query.all()

def get_user_by_uuid(user_uuid):
    return User.query.filter_by(uuid=user_uuid).first()

def create_user(data):
    if "username" not in data:
        raise KeyError("Falta el parámetro 'username' en los datos de entrada.")
    password_bytes = data["password"].encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    new_user = User(
        uuid=str(uuid.uuid4()),
        username=data["username"],
        password=hashed.decode("utf-8"),
        createdAt=datetime.now(timezone.utc)
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user