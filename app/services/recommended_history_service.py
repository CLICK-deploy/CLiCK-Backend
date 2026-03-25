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
