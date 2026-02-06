from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class Event(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    # 글자 수 제한(input_prompt) 고민: TEXT + 앱 제한(10000~20000, 40000자가 맥스치, 등급에 따라 구분지을 거 같으니 고민) 어떤가 
    input_prompt = Column(String(255), nullable=False)
    fixed_prompt = Column(String(255), nullable=False)
    reason = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    user = relationship("User", back_populates="events")