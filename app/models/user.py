from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(300), nullable=False)

    # admin / user
    role = Column(String(50), default="user")

    created_at = Column(DateTime, default=datetime.utcnow)