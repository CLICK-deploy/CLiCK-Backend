from app.models.input_history import InputHistory
from sqlalchemy.orm import Session
from app.schemas.gpt import RoomTrace
from typing import Sequence
from sqlalchemy import select, and_


def create_history(in_: RoomTrace, user_id: int, db: Session):
    new_history = InputHistory(
            user_id=user_id,
            room_id=in_.chatID,
            input=in_.prompt)
    db.add(new_history)
    db.commit()
    db.refresh(new_history)
    return new_history


def get_histories(user_id: int, room_id: str, db: Session):
    query = select(InputHistory).where(and_(InputHistory.user_id == user_id, InputHistory.room_id == room_id)).order_by(InputHistory.created_at.desc()).limit(10)
    histories: Sequence[InputHistory] = db.execute(query).scalars().all()
    return histories


def get_histories_new(user_id: int, db: Session):
    query = select(InputHistory).where(InputHistory.user_id == user_id).order_by(
        InputHistory.created_at.desc()).limit(10)
    histories: Sequence[InputHistory] = db.execute(query).scalars().all()
    return histories