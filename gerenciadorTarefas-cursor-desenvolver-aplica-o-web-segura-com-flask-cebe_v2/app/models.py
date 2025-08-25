from datetime import datetime
from typing import Optional, List
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db  # Importar normalmente

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    tasks = db.relationship("Task", back_populates="owner", lazy=True)
    histories = db.relationship("TaskHistory", back_populates="actor", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(32), nullable=False, default="todo")
    position = db.Column(db.Integer, nullable=False, default=0)

    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    owner = db.relationship("User", back_populates="tasks")

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    histories = db.relationship("TaskHistory", back_populates="task", lazy=True, cascade="all, delete-orphan")

class TaskHistory(db.Model):
    __tablename__ = "task_histories"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String(64), nullable=False)
    from_status = db.Column(db.String(32), nullable=True)
    to_status = db.Column(db.String(32), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    details = db.Column(db.Text, nullable=True)

    task = db.relationship("Task", back_populates="histories")
    actor = db.relationship("User", back_populates="histories")

def get_next_position(owner_id: int, status: str) -> int:
    existing = Task.query.filter_by(owner_id=owner_id, status=status).order_by(Task.position.desc()).first()
    return (existing.position + 1) if existing else 1
