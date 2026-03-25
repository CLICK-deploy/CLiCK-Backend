from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class RecommendedHistory(Base):
    __tablename__ = "recommended_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    chat_id = Column(String(200), nullable=True)  # None이면 global 추천
    title = Column(String(30), nullable=False)
    content = Column(String(1000), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    user = relationship("User", back_populates="recommended_histories")
