from app.models.history import History, MessageRole
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.gpt import RoomTrace
from typing import Sequence
from sqlalchemy import select, and_

def _get_user(nickname: str, db: Session):
    user = db.execute(select(User).where(User.nickname == nickname)).scalar()
    return user

def create_history(in_: RoomTrace, role:MessageRole, db:Session):
    user = _get_user(in_.userID, db)
    if user is None:
        return None

    role_value = MessageRole.USER.value if role == MessageRole.USER.value else MessageRole.AI
    new_history = History(
            user_id=user.user_id,
            room_id=in_.chatID,
            role=role_value,
            topic=in_.prompt)
    db.add(new_history)
    db.commit()
    db.refresh(new_history)
    return new_history


def get_histories(user_id: str, room_id: str, db: Session):
    user = _get_user(user_id, db)
    if user is None:
        return []
    query = select(History).where(and_(History.user_id == user.user_id, History.room_id == room_id)).order_by(History.created_at.desc()).limit(10)
    histories : Sequence[History] = db.execute(query).scalars().all()
    return histories

def get_histories_new(user_id: str, db: Session):
    user = _get_user(user_id, db)
    if user is None:
        return []
    query = select(History).where(History.user_id == user.user_id).order_by(
        History.created_at.desc()).limit(10)
    histories: Sequence[History] = db.execute(query).scalars().all()
    return histories