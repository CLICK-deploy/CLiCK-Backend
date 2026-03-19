# ※ 참고 사항: "건가", "이유는", "이유는?", "이유" 등으로 끝나는 거 다 의문점이 맞고 원래 거 쓰는 거로 고치고 싶은 거임. 새로운 더 효율적인 거 있으면 그거로 고치고 그러고 싶어서 그러는 거 ㅇㅇ 지금 해둔 거 다 의미있으면 그대로 편하게 넘어가버리고 싶은 거도 있고

## requirements.txt, pyproject.toml
- bcrypt, google-generativeai, psycopg2-library 다 바꿔도 되는 건가

## package.json
- swagger-editor는 API 테스트니까 그대로 두는 게 맞는 건가

## app/core/security.py
- from passlib.context import CryptContext에서 bcrypt 이용하는 방식으로 바꾼 이유는?

## app/main.py
- allow_credentials = False로 해야 실행이 되는 이유는? True 해야지 우리 의도 아닌강

## app/schemas/gpt.py
- id: UUID를 id: int로 바꾼 이유는?

## app/services/event_service.py
- select(User).where(User.user_id == user_id)에서 select(User).where(User.device_uuid == user_id)로 바꾼 이유
- 원래 코드에서 fixed_prompt[:255]나 fixed_prompt = result.get("improved_prompt") 이런 것들로 바꾼 이유

## alembic/env.py
- """Run migration in 'offline' mode.~""" 주석이 지워지고 """Run migrations in 'online' mode.~" 주석이 지워지고 일부러 지운건가
- 라이브러리 import 상단으로 옮겨주고 config.set_main_option을 지워서 뭐로 어케 바꾼건지&settings.DATABASE_URL 이런 거 말고 그냥 DATABASE_URL로 해도 되는 거 아닌가

## alembic/versions/06e990cb07eb_add_role_to_histories_table.py
- op.add_column이 message_role = sa.Enum & message_role.create 두 개가 추가되고 내용이 바꾼 거는 요약한 건가? downgrade는 sa.Enum 그대로 밖에 있는데

## alembic/versions/e50fd74c2d61_extend_password_column_to_255.py
- 이 부분은 왜 생성되었는가? 수정된 거 이전 버전에서 뭘 수정했고 왜 수정한 건가



## 구글 docs, 기능정의서 참고해서 추가기능들 구현
- https://docs.google.com/document/d/1V9flFbFdSxqGwn8ztWwXvtxAC_EjOTpPwFmaNVvMWQY/edit?tab=t.v0fzxa4wo64p#heading=h.rk8ohwvg9zpm
- 
- 복잡한 문장 / 간단한 문장 구분 및 처리 분할, 무료 버전 시 횟수 제한&사용 가능한 템플릿 제작 등등
- 주석, 에러 같은 거 한국어로 바꿀 수 있으면 바꿔주고, db도 언급한 식으로 수정 가능하면 수정하고, 인증부도 token 사용하는 방식으로 바꾸고, refresh_token 이용해서 refresh 엔드포인트에서 토큰 새로고침하고, token secret key .env 설정에 넣고 사용할 수 있게 해주면 좋겠고 등등


# 추가사항

## app/api/v1/routers/auth.py
- "refresh"로 access token 새로고침하는 api 서버 endpoint 필요하고 프론트랑 연동하는 방식&프론트, 백 모두 인증 과정 제대로 해두기
- check_duplicate는 db에서 unique 걸려서 중복 제거하는 거를 sql error 참조해서 뽑아서 해석하게 해도 되긴 한데 그대로 갈건지 필요하고

## app/services/history_service.py
- MessageRole.USER.value if role == MessageRole.USER.value else MessageRole.AI 같은 거로 바꾼 이유
- limit이랑 테이블 바꾼 이유

## app/services/user_service.py
- is_exist_user 그대로 두고 check_duplicate도 그대로 두는 건가