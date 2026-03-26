from app.models.recommended_history import RecommendedHistory
from sqlalchemy.orm import Session
from typing import Sequence
from sqlalchemy import select


def create_recommended_history(user_id: int, chat_id: str | None, title: str, content: str, db: Session) -> RecommendedHistory:
    new_rec = RecommendedHistory(
        user_id=user_id,
        chat_id=chat_id,
        title=title,
        content=content,
    )
    db.add(new_rec)
    db.commit()
    db.refresh(new_rec)
    return new_rec


def get_recommended_histories(user_id: int, db: Session) -> Sequence[RecommendedHistory]:
    query = select(RecommendedHistory).where(
        RecommendedHistory.user_id == user_id
    ).order_by(RecommendedHistory.created_at.desc())
    return db.execute(query).scalars().all()


def get_latest_by_chat(user_id: int, chat_id: str | None, db: Session) -> RecommendedHistory | None:
    """채팅방 전환 시 LLM 없이 DB에서 최신 추천 1건을 반환한다."""
    query = (
        select(RecommendedHistory)
        .where(
            RecommendedHistory.user_id == user_id,
            RecommendedHistory.chat_id == chat_id,  # None이면 global
        )
        .order_by(RecommendedHistory.created_at.desc())
        .limit(1)
    )
    return db.execute(query).scalar_one_or_none()
