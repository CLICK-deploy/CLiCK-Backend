from app.models.event import Event
from app.models.user import User
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import select


def create_event(user_id:str, input_prompt, result, db:Session) -> Event:
    user = db.execute(
        select(User).where(User.device_uuid == user_id)
    ).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 user_id")

    fixed_prompt = result.get("improved_prompt") or result.get("full_suggestion", "")
    reason = result.get("task_type") or ""
    new_event = Event(user_id=user.user_id,
                      input_prompt=input_prompt,
                      fixed_prompt=fixed_prompt[:255],
                      reason=reason[:255])
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    print(f"created events : {new_event.user_id}")
    return new_event