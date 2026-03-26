import json
import re
from typing import Dict, List
from app.core.config import settings
from app.core.prompts.prompt_loader import IMPROVE_SYS_PROMPT, REC_SYS_PROMPT1, REC_SYS_PROMPT2
from app.schemas.gpt import RoomTrace, RecommendInput
from app.models.user import User
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
import google.generativeai as genai
from app.services import user_service, analyze_history_service, input_history_service
from app.services import recommended_history_service
from app.db.session import get_db
from app.services.input_history_service import create_history, get_histories, get_histories_new
from app.core.security import get_current_user

router = APIRouter(prefix="")

genai.configure(api_key=settings.GEMINI_API_KEY)


@router.post(path="/trace_input", summary="유저 질문 수집 -> 유저의 관심사 파악")
def trace_input_prompt(in_: RoomTrace, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    input_history_service.create_history(in_, current_user.user_id, db)
    return {"status": "success"}

@router.post(path="/trace_output_prompt", summary="ai 답변 수집 -> 유저의 관심사 파악")
def trace_output_prompt(in_: RoomTrace, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    input_history_service.create_history(in_, current_user.user_id, db)
    return {"status": "success"}

@router.post("/recommended-prompts", summary="유저별 관심사 기반 추천 프롬프트 1개 생성",
             response_model=Dict[str, dict])
async def get_recommend_prompts(in_: RecommendInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 빈 문자열도 None으로 처리
    chat_id = in_.chatID if in_.chatID else None

    print(f"[recommended-prompts] user_id={current_user.user_id}, chatID={repr(chat_id)}, generate={in_.generate}")

    response_key = chat_id if chat_id else "global"

    # generate=False: 채팅방 전환 시 DB 캐시만 조회 (LLM 호출 없음)
    if not in_.generate:
        cached = recommended_history_service.get_latest_by_chat(current_user.user_id, chat_id, db)
        if cached:
            return {response_key: {"title": cached.title, "content": cached.content}}
        return {response_key: {}}

    # generate=True: LLM으로 새 추천 생성
    if chat_id is None:
        # 새 채팅 — 전체 히스토리 기반, global 키 사용
        histories = get_histories_new(current_user.user_id, db)
        sys_prompt = REC_SYS_PROMPT2
    else:
        # 기존 채팅방
        histories = get_histories(current_user.user_id, chat_id, db)
        sys_prompt = REC_SYS_PROMPT1

    topics = [h.input for h in histories]
    print(f"[recommended-prompts] fetched {len(topics)} topics from room={repr(response_key)}: {topics}")

    # 히스토리가 전혀 없으면 빈 객체 반환
    if not topics:
        return {response_key: {}}

    # 2) 모델 호출
    user_payload = {"topics": topics}

    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            system_instruction=sys_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                max_output_tokens=1024
            )
        )
        resp = model.generate_content(json.dumps(user_payload, ensure_ascii=False))
        raw = resp.text.strip()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM 모델 호출 실패: {e}")

    # 3) JSON 파싱
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw).strip()
    try:
        data = json.loads(raw)
    except Exception:
        try:
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end > start:
                data = json.loads(raw[start:end + 1])
            else:
                raise ValueError
        except Exception:
            raise HTTPException(status_code=502, detail=f"추천 프롬프트 응답(JSON) 파싱 실패: {raw[:200]}")

    # LLM이 반환한 키(local/global) 에서 단일 객체 추출
    item: dict = data.get("local") or data.get("global") or {}

    # 배열로 왔을 경우 첫 번째 항목만 사용
    if isinstance(item, list):
        item = item[0] if item else {}

    result = {
        "title": item.get("title", "")[:30],
        "content": item.get("content", ""),
    }

    # 추천 결과를 recommended_history 테이블에 저장
    if result["title"] or result["content"]:
        recommended_history_service.create_recommended_history(
            user_id=current_user.user_id,
            chat_id=chat_id,
            title=result["title"],
            content=result["content"],
            db=db,
        )

    return {response_key: result}



"""
        res = json.loads(raw)
   
        # 3) 그대로 클라이언트에 반환(topic/patches/full_suggestion 사용)
        return res
"""