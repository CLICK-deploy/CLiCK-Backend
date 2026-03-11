from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password
from sqlalchemy import select
from typing import Optional

def is_exist_user(user_id: str, db: Session) -> bool:
    query = select(User).where(User.device_uuid == user_id)
    user = db.execute(query).scalar()
    return user is not None

def create_user(user_id: str, db: Session):
    new_user = User(device_uuid=user_id)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    print(f"created users : {new_user.user_id}")

def is_nickname_taken(nickname: str, db: Session) -> bool:
    query = select(User).where(User.nickname == nickname)
    return db.execute(query).scalar() is not None

def register_or_login(nickname: str, password: str, age_group: Optional[str], gender: Optional[str], db: Session) -> Optional[User]:
    """닉네임이 없으면 회원가입, 있으면 로그인 시도."""
    user = db.execute(select(User).where(User.nickname == nickname)).scalar()
    if user is None:
        # 신규 가입
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
    # 기존 유저 — 비밀번호 검증
    if user.password and verify_password(password, user.password):
        return user
    return None

