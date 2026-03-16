from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password
from sqlalchemy import select
from typing import Optional

def is_exist_user(nickname: str, db: Session) -> bool:
    query = select(User).where(User.nickname == nickname)
    return db.execute(query).scalar() is not None

def is_nickname_taken(nickname: str, db: Session) -> bool:
    query = select(User).where(User.nickname == nickname)
    return db.execute(query).scalar() is not None

def signup(nickname: str, password: str, age_group: Optional[str], gender: Optional[str], db: Session) -> Optional[User]:
    """신규 회원가입. 닉네임 중복이면 None 반환."""
    if is_nickname_taken(nickname, db):
        return None
    new_user = User(
        nickname=nickname,
        password=hash_password(password),
        age=age_group,
        gender=gender,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_user(nickname: str, password: str, db: Session) -> Optional[User]:
    """로그인. 닉네임 없거나 비밀번호 불일치 시 None 반환."""
    user = db.execute(select(User).where(User.nickname == nickname)).scalar()
    if user is None:
        return None
    if user.password and verify_password(password, user.password):
        return user
    return None

