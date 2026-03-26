from __future__ import annotations

import json
import re
from typing import Dict, List, Optional
from app.core.config import settings
from app.core.prompts.prompt_loader import IMPROVE_SYS_PROMPT
from app.services import user_service, analyze_history_service
from app.db.session import get_db
from app.models.user import User
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import google.generativeai as genai
from app.core.security import get_current_user

router = APIRouter(prefix="")

genai.configure(api_key=settings.GEMINI_API_KEY)


# -----------------------------
# Request / Response Schemas
# -----------------------------
class AnalyzePromptRequest(BaseModel):
    chatID: Optional[str] = None
    prompt: str


class AnalyzePromptResponse(BaseModel):
    tags: List[str]
    patches: Dict[str, List[dict]]
    full_suggestion: str


# -----------------------------
# Utilities
# -----------------------------
def coerce_json_from_text(text: str) -> dict:
    """마크다운 코드블록 제거 후 JSON 추출. 앞뒤 비JSON 텍스트 허용."""
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end + 1])
    except Exception:
        pass
    raise ValueError("Failed to parse JSON from model output.")


# -----------------------------
# Endpoint
# -----------------------------
@router.post(
    path="/analyze-prompt",
    summary="사용자가 입력한 프롬프트를 분석하여 개선안을 제안",
    response_model=AnalyzePromptResponse,
)
async def analyze_prompt(in_: AnalyzePromptRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 1) 유저 존재 여부는 토큰으로 보장됨

    # 2) LLM 호출
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            system_instruction=IMPROVE_SYS_PROMPT,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=2048,
                response_mime_type="application/json",
            )
        )
        chat = model.start_chat(history=[
            {"role": "user", "parts": ["도커에 대해 설명해줘"]},
            {"role": "model", "parts": ['{"patches": [{"tag": "문체/스타일 개선", "from": "도커", "to": "Docker"}, {"tag": "모호/지시 불명확", "from": "설명해줘", "to": "컨테이너 개념과 이미지/레지스트리 중심으로 설명해줘."}], "full_suggestion": "Docker에 대해 컨테이너 개념과 이미지/레지스트리 중심으로 설명해줘."}']},
            {"role": "user", "parts": ["인공지능에 대해 자세하고 상세하게 설명 해줬스면 좋겠어."]},
            {"role": "model", "parts": ['{"patches": [{"tag": "모호/지시 불명확", "from": "설명", "to": "기본 개념을 3가지 핵심 포인트로 설명"}, {"tag": "구조/길이 중복", "from": "자세하고 상세하게", "to": "자세하게"}, {"tag": "오타/맞춤법", "from": "해줬스면", "to": "해주었으면"}], "full_suggestion": "인공지능에 대해 자세하게 기본 개념을 3가지 핵심 포인트로 설명 해주었으면 좋겠어."}']},
        ])
        resp = chat.send_message(in_.prompt)
        raw_text = resp.text.strip()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM API 연동 에러: {e}")
    try:
        parsed = coerce_json_from_text(raw_text)
    except ValueError:
        raise HTTPException(status_code=502, detail=f"GPT 응답 JSON 파싱 실패: {raw_text[:200]}")

    # 4) 스펙 형식으로 변환
    # LLM은 patches를 배열로 반환: [{"tag":..,"from":..,"to":..}, ...]
    # 스펙은 patches를 dict로: {"tag_name": {"from":..,"to":..}}
    raw_patches: list = parsed.get("patches", [])
    tags: List[str] = []
    patches: Dict[str, List[dict]] = {}
    for p in raw_patches:
        tag = p.get("tag", "")
        if tag and tag not in tags:
            tags.append(tag)
        patches.setdefault(tag, []).append({"from": p.get("from", ""), "to": p.get("to", "")})

    full_suggestion: str = parsed.get("full_suggestion", in_.prompt)

    # 5) DB 저장 (실패해도 응답은 반환)
    try:
        analyze_history_service.create_event(
            current_user.user_id,
            in_.prompt,
            {"improved_prompt": full_suggestion, "task_type": ", ".join(tags)},
            db,
        )
    except Exception as e:
        print(f"DB Event Log Error: {e}")

    return AnalyzePromptResponse(tags=tags, patches=patches, full_suggestion=full_suggestion)
