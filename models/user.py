from db import db
from datetime import datetime
import uuid

class User(db.Model):
    __tablename__ = "user"

    uuid = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "username": self.username,
            "createdAt": self.createdAt.isoformat()
        }
