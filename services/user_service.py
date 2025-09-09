from models.user import User
from db import db
from datetime import datetime, timezone
import uuid
import bcrypt

def get_all_users():
    return User.query.all()

def create_user(data):
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
