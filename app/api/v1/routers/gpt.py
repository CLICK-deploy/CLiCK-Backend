# TODO: max_tokens&temperature 조정할 것

import json
import re
from typing import Dict, List
from app.core.config import settings
from app.core.prompts.prompt_loader import IMPROVE_SYS_PROMPT, REC_SYS_PROMPT1, REC_SYS_PROMPT2
from app.schemas.gpt import RoomTrace, RecommendInput
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
import google.generativeai as genai
from app.services import user_service, event_service, history_service
from app.db.session import get_db
from app.services.history_service import create_history, get_histories, get_histories_new

router = APIRouter(prefix="")

genai.configure(api_key=settings.GEMMA_API_KEY)


@router.post(path="/trace_input", summary="유저 질문 수집 -> 유저의 관심사 파악")
def trace_input_prompt(in_: RoomTrace, db:Session = Depends(get_db)):
    if not user_service.is_exist_user(in_.userID, db):
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")

    history_service.create_history(in_, 'user', db)
    return {"status": "success"}

@router.post(path="/trace_output_prompt", summary="ai 답변 수집 -> 유저의 관심사 파악")
def trace_output_prompt(in_: RoomTrace, db:Session = Depends(get_db)):
    if not user_service.is_exist_user(in_.userID, db):
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")

    history_service.create_history(in_, 'ai', db)
    return {"status": "success"}

@router.post("/recommended-prompts", summary="유저별 관심사 기반 추천 프롬프트 1개 생성",
             response_model=Dict[str, dict])
async def get_recommend_prompts(in_: RecommendInput, db: Session = Depends(get_db)):
    # 1) 조건에 따른 히스토리 조회 및 시스템 프롬프트 할당
    if in_.chatID is None:
        # 새 채팅 — 전체 히스토리 기반, global 키 사용
        histories = get_histories_new(in_.userID, db)
        sys_prompt = REC_SYS_PROMPT2
        response_key = "global"
    else:
        # 기존 채팅방
        histories = get_histories(in_.userID, in_.chatID, db)
        sys_prompt = REC_SYS_PROMPT1
        response_key = in_.chatID

    topics = [h.topic for h in histories]

    # 히스토리가 전혀 없으면 빈 객체 반환
    if not topics:
        return {response_key: {}}

    # 2) 모델 호출
    user_payload = {"topics": topics}

    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config=genai.GenerationConfig(
                temperature=0.4,
                max_output_tokens=5000,
                response_mime_type="application/json",
            ),
        )
        resp = model.generate_content([
            {"role": "user", "parts": [f"{sys_prompt}\n\n{json.dumps(user_payload, ensure_ascii=False)}"]},
        ])
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

    return {response_key: result}

"""
@router.post(path="/analyze-prompt1", summary="사용자가 입력한 프롬프트를 분석하여 개선안을 제안")
async def analyze_prompt(in_: InputPrompt, db:Session = Depends(get_db)):
    if not user_service.is_exist_user(in_.user_id, db):
        user_service.create_user(in_.user_id, db)

    try:
        response = client.chat_completion(
            model="gemma-3-1b-it",
            messages=[
                {
                    "role": "system",
                    "content": IMPROVE_SYS_PROMPT
                },{"role": "user", "content": "도커에 대해 설명해줘"},
                {"role": "assistant", "content": '''
            {
  "patches": [
    { "tag": "문체/스타일 개선", "from": "도커", "to": "Docker", "occurrence": 1 },
    { "tag": "모호/지시 불명확", "from": "설명해줘", "to": "컨테이너 개념과 이미지/레지스트리 중심으로 설명해줘", "occurrence": 1 }
  ],
  "full_suggestion": "Docker에 대해 컨테이너 개념과 이미지/레지스트리 중심으로 설명해줘."
}
                '''},
                {"role": "user", "content": "인공지능에 대해 자세하고 상세하게 설명 해줬스면 좋겠어."},
                {"role": "assistant", "content": '''{
            patches: [
                {“tag”:“모호/지시 불명확”.
                        “from”: "설명",
                        “to”: "기본 개념을 3가지 핵심 포인트로 설명"
                    }
                ,
                {“tag”:구조/길이 중복”,
                        “from”: "자세하고 상세하게",
                        “to”: "자세하게"
                    },
               {“tag”: "오타/맞춤법”:,
                        “from”: "해줬스면",
                        “to”: "해주었으면”}
            ],
  "full_suggestion": "FastAPI 파일 업로드 단계별 코드 예시와 보안 고려사항을 포함해 알려줘"
}'''
},
                {"role": "user", "content": in_.input_prompt}
            ],response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "PromptEdit",
            "strict": True,  # 스키마 강제
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "patches": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "tag": { "type": "string", "minLength": 1 },
                                "from": { "type": "string", "minLength": 1 },
                                "to":   { "type": "string", "minLength": 1 }
                            },
                            "required": ["tag", "from", "to"]
                        }
                    },
                    "full_suggestion": { "type": "string", "minLength": 1 }
                },
                "required": ["patches", "full_suggestion"]
            }
        }
    },
            max_tokens=800,
            # 필요 시 파라미터: temperature=0.3, max_tokens=800 등
        )

        raw = response.choices[0].message.content
        res = json.loads(raw)
        print(raw)
        # 2) DB 저장 (event)
        event_service.create_event(in_.user_id, in_.input_prompt, res, db)

        # 3) 그대로 클라이언트에 반환(topic/patches/full_suggestion 사용)
        return res

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""