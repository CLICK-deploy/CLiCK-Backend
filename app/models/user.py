from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.session import Base
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLAlchemyEnum

class Grade(PyEnum):
    GENERAL = "general"
    VIP = "vip"

class User(Base):
    __tablename__ = "users"

    now = datetime.now(timezone(timedelta(hours=9)))

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    # 고민해보기: device_uuid를 사용해 고생한만큼 효용이 나올까?(일단 2명은 있으면 좋겠다고 함)
    device_uuid = Column(String(36), unique=True)
    nickname = Column(String(20), nullable=True, unique=True)
    password = Column(String(255), nullable=True)
    gender = Column(String(10), nullable=True)
    age = Column(String(10), nullable=True)
    grade = Column(SQLAlchemyEnum(Grade), nullable=True, default=Grade.GENERAL)
    lastLogin = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    events = relationship("Event", back_populates="user")
    histories = relationship("History", back_populates="user")