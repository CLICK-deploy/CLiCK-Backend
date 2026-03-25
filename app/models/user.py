from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.session import Base
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLAlchemyEnum

class Plan(PyEnum):
    GENERAL = "GENERAL"
    VIP = "VIP"

class User(Base):
    __tablename__ = "users"

    now = datetime.now(timezone(timedelta(hours=9)))

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    nickname = Column(String(20), unique=True, index=True, nullable=True)
    password = Column(String(255), nullable=True)
    gender = Column(String(10), nullable=True)
    age = Column(String(10), nullable=True)
    plan = Column(SQLAlchemyEnum(Plan), nullable=True, default=Plan.GENERAL)
    lastLogin = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    analyze_histories = relationship("AnalyzeHistory", back_populates="user")
    input_histories = relationship("InputHistory", back_populates="user")
    recommended_histories = relationship("RecommendedHistory", back_populates="user")