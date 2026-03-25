from app.models.analyze_history import AnalyzeHistory
from sqlalchemy.orm import Session
from fastapi import HTTPException


def create_event(user_id: int, input_prompt: str, result: dict, db: Session) -> AnalyzeHistory:
    fixed_prompt = result.get("improved_prompt") or result.get("full_suggestion", "")
    reason = result.get("task_type") or ""
    new_event = AnalyzeHistory(user_id=user_id,
                      input_prompt=input_prompt,
                      fixed_prompt=fixed_prompt[:255],
                      reason=reason[:255])
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    print(f"created events : {new_event.user_id}")
    return new_event