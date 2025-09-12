from db import db
from datetime import datetime
import uuid

class Record(db.Model):
    __tablename__ = "record"

    uuid = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    time = db.Column(db.Integer, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    errorCount = db.Column(db.Integer, nullable=False)
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    idUser = db.Column(db.String, db.ForeignKey('user.uuid', ondelete='CASCADE'), nullable=False)

    # Relación con el modelo User
    user = db.relationship('User', backref=db.backref('records', lazy=True, cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "time": self.time,
            "level": self.level,
            "difficulty": self.difficulty,
            "errorCount": self.errorCount,
            "createdAt": self.createdAt.isoformat(),
            "idUser": self.idUser
        }
