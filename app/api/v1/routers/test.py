from __future__ import annotations

import json
import re
from typing import Dict, List, Optional
from app.core.config import settings
from app.core.prompts.prompt_loader import IMPROVE_SYS_PROMPT
from app.services import user_service, event_service
from app.db.session import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import google.generativeai as genai

router = APIRouter(prefix="")

genai.configure(api_key=settings.GEMMA_API_KEY)


# -----------------------------
# Request / Response Schemas
# -----------------------------
class AnalyzePromptRequest(BaseModel):
    userID: str
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
async def analyze_prompt(in_: AnalyzePromptRequest, db: Session = Depends(get_db)):
    # 1) 유저 존재 여부 확인
    if not user_service.is_exist_user(in_.userID, db):
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")

    # 2) LLM 호출
    try:
        gemini_model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=8192,
                response_mime_type="application/json",
            ),
        )
        response = gemini_model.generate_content([
            {"role": "user", "parts": [f"{IMPROVE_SYS_PROMPT}\n\n{in_.prompt}"]},
        ])
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM API 연동 에러: {e}")

    # 3) 응답 파싱
    raw_text = response.text.strip()
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
        event_service.create_event(
            in_.userID,
            in_.prompt,
            {"improved_prompt": full_suggestion, "task_type": ", ".join(tags)},
            db,
        )
    except Exception as e:
        print(f"DB Event Log Error: {e}")

    return AnalyzePromptResponse(tags=tags, patches=patches, full_suggestion=full_suggestion)
