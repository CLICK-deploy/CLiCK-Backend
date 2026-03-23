### ※ 참고 사항: "거?", ""이유?" 등으로 끝나는 거 다 의문점이 맞고 원래 거 쓰는 거로 고치고 싶은 거임. 
새로운 더 효율적인 거 있으면 고치고 싶어서 그러는 거 ㅇㅇ. 해둔 거 다 의미있으면 그대로 편하게 넘어가버리고 싶은 거도 있고
### ※ 참고 사항(코드적): expires_in 추가&여러모로 터치는 했으니까 읽어보고, is_exist_user&is_nickname_taken 마냥 중복들도 지워두고 효율 깎는 거 잘 찾아보고.
### ※ 참고 사항(코드적): frontend에 userID랑 access_token이랑 같이 저장할 필요 없음. 다 처리하려고 만든 JWT 토큰만 access_token, refresh_token 이런 거일 테니까.

## requirements.txt, pyproject.toml
- bcrypt, google-generativeai, psycopg2-library 다 바꾸기?

## package.json
- swagger-editor는 API 테스트니까 그대로 두기?

## app/core/security.py
- from passlib.context import CryptContext에서 bcrypt 이용하는 방식으로 바꾼 이유?

## app/main.py
- allow_credentials = False 실행하는 이유?

## app/schemas/gpt.py
- id: UUID를 id: int로 바꾼 이유?

## app/services/event_service.py
- select(User).where(User.user_id == user_id)에서 select(User).where(User.device_uuid == user_id)로 바꾼 이유?
- 원래 코드에서 fixed_prompt[:255]나 fixed_prompt = result.get("improved_prompt") 이런 것들로 바꾼 이유?

## alembic/env.py
- """Run migration in 'offline' mode.(하고 나머지 내용)""" 주석이 지워지고 """Run migrations in 'online' mode.(하고 나머지 내용)""" 주석이 지워졌는데 지운 이유?
- 라이브러리 import 상단으로 옮겨주고 config.set_main_option을 지워서 뭐로 어케 바꾼건지&settings.DATABASE_URL 이런 거 말고 그냥 DATABASE_URL로 해도 되는 거?

## alembic/versions/06e990cb07eb_add_role_to_histories_table.py
- op.add_column이 message_role = sa.Enum & message_role.create 두 개가 추가되고 내용이 바꾼 거는 요약한 거? downgrade는 sa.Enum 그대로 밖에 있는데

## alembic/versions/e50fd74c2d61_extend_password_column_to_255.py
- 이 부분은 왜 생성된 거짐? 수정된 거 이전 버전에서 뭘 수정했고 왜 수정한 건지 이유?



# 마지막 필수 전달사항
## 구글 docs, 기능정의서 참고해서 추가기능들 구현(하단 첫 2개는 링크)
- https://docs.google.com/document/d/1V9flFbFdSxqGwn8ztWwXvtxAC_EjOTpPwFmaNVvMWQY/edit?tab=t.v0fzxa4wo64p#heading=h.rk8ohwvg9zpm
- https://docs.google.com/spreadsheets/d/1274NpbXueSE6YXW4-D1YAzOI0u6kFPhbjSQSBRZ1zN0/edit?gid=0#gid=0
- refresh_token 이용해서 refresh 엔드포인트 만들어서 그 엔드포인트에서 토큰 새로고침할 것 
- 복잡한 문장 / 간단한 문장 구분 및 처리 분할, 무료 버전 시 횟수 제한&사용 가능한 템플릿 제작, UI 수정(폴더나 방? 속에 있는 거도 제대로 동작하게, 로그인 버튼 누르면 관련해서 다 뜨는데 조건 붙여서(로그인 안 했을 때 로그아웃 버튼 뜬다든지) 렌더링하고 이런 식으로 등) 등등
- 주석, 에러 같은 거 한국어로 바꿀 수 있으면 바꿔주고, db도 언급한 식으로 수정 가능하면 수정하고, 인증부도 token 사용하는 방식으로 바꾸고, token secret key .env 설정에 넣고 사용할 수 있게 해주면 좋겠고 등등


# 추가사항

## app/api/v1/routers/auth.py
- "refresh"로 access token 새로고침하는 api 서버 endpoint 필요하고 프론트랑 연동하는 방식&프론트, 백 모두 인증 과정 제대로 해두기
- check_duplicate는 db에서 unique 걸려서 중복 제거하는 거를 sql error 참조해서 뽑아서 해석하게 해도 되긴 한데 그대로 갈건지 필요

## app/services/history_service.py
- MessageRole.USER.value if role == MessageRole.USER.value else MessageRole.AI 같은 거로 바꾼 이유
- limit이랑 테이블 바꾼 이유

## app/services/user_service.py
- is_exist_user 그대로 두고 check_duplicate도 그대로 두는 거?
- is_exist_user랑 is_nickname_taken이랑 같은 함수라 퉁쳐도 될 거 같음.
