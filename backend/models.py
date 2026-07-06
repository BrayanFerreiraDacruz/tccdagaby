"""
Modelos de dados (SQLAlchemy) da plataforma Study Time.

Tabelas:
  - users      : contas de usuário (RF01, RF02, RF03)
  - schedules  : cronogramas de estudo personalizados (RF04, RF05, RF06)
  - attempts   : registro de questões respondidas / desempenho (RF09, RF10, RF11)
"""
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    schedules = db.relationship(
        "Schedule", backref="user", cascade="all, delete-orphan", lazy=True
    )
    attempts = db.relationship(
        "Attempt", backref="user", cascade="all, delete-orphan", lazy=True
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Schedule(db.Model):
    __tablename__ = "schedules"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title = db.Column(db.String(150), nullable=False)
    discipline = db.Column(db.String(80))  # área de estudo (ex.: matematica)
    weekday = db.Column(db.Integer, nullable=False)  # 0=Domingo ... 6=Sábado
    start_time = db.Column(db.String(5), nullable=False)  # "HH:MM"
    end_time = db.Column(db.String(5), nullable=False)  # "HH:MM"
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "discipline": self.discipline,
            "weekday": self.weekday,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Attempt(db.Model):
    __tablename__ = "attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    year = db.Column(db.Integer, nullable=False)
    question_index = db.Column(db.Integer, nullable=False)
    discipline = db.Column(db.String(80))
    language = db.Column(db.String(20))
    chosen = db.Column(db.String(1), nullable=False)  # A..E
    correct = db.Column(db.String(1), nullable=False)  # A..E
    is_correct = db.Column(db.Boolean, nullable=False)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "year": self.year,
            "question_index": self.question_index,
            "discipline": self.discipline,
            "language": self.language,
            "chosen": self.chosen,
            "correct": self.correct,
            "is_correct": self.is_correct,
            "answered_at": self.answered_at.isoformat() if self.answered_at else None,
        }
