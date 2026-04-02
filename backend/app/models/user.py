"""
用户数据模型
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

from app.models.task import Base


class User(Base):
    """用户数据库模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(10), default="user")  # 'admin' | 'user'
    xhs_cookies_encrypted = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
