from app.models.history import History, MessageRole
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.gpt import RoomTrace
from typing import Sequence
from sqlalchemy import select, and_

def create_history(in_: RoomTrace, role:MessageRole, db:Session):
    if role == MessageRole.USER.value:
        query = select(User).where(User.device_uuid == in_.user_id)
        user = db.execute(query).scalar()

        new_history = History(
                user_id=user.user_id,
                room_id=in_.room_id,
                role=MessageRole.USER.value,
                topic=in_.input_prompt)
        db.add(new_history)
        db.commit()
        db.refresh(new_history)
        return new_history
    else:
        query = select(User).where(User.device_uuid == in_.user_id)
        user = db.execute(query).scalar()

        new_history = History(
            user_id=user.user_id,
            room_id=in_.room_id,
            role=MessageRole.AI,
            topic=in_.input_prompt) # input_prompt 좀 가공하기(핵심만 뽑는다든가)
        db.add(new_history)
        db.commit()
        db.refresh(new_history)
        return new_history


def get_histories(user_id: str, room_id: str, db: Session):
    query = select(User).where(User.device_uuid == user_id)
    user = db.execute(query).scalar()
    query = select(History).where(and_(History.user_id == user.user_id, History.room_id == room_id)).order_by(History.created_at.desc()).limit(2)
    histories : Sequence[History] = db.execute(query).scalars().all()
    return histories

def get_histories_new(user_id: str, db: Session):
    query = select(User).where(User.device_uuid == user_id)
    user = db.execute(query).scalar()
    query = select(History).where(History.user_id == user.user_id).order_by(
        History.created_at.desc()).limit(2)
    histories: Sequence[History] = db.execute(query).scalars().all()
    return histories