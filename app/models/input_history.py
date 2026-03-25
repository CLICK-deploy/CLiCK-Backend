from sqlalchemy import Index, DateTime, Column, Integer, String, ForeignKey
from app.db.session import Base
from sqlalchemy.sql import func, desc
from sqlalchemy.orm import relationship

class InputHistory(Base):
    __tablename__ = 'input_history'
    history_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    room_id = Column(String(200), nullable=False)
    input = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    user = relationship("User", back_populates="input_histories")

    __table_args__ = (
        Index("idx_input_hist_user_room_created", "user_id", "room_id", desc("created_at")),
    )