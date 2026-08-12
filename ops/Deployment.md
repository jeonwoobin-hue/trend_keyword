# Deployment.md — 배포 가이드

> SRS §2.3 운영 환경: 클라우드 인프라(컨테이너 기반), Streamlit/Dash 애플리케이션 서버 + 별도 배치 서버.
> 프론트엔드는 Streamlit Community Cloud(`https://trend-keyword.streamlit.app/`)로 확정(2026-08-12).
> `api/`(FastAPI)·`worker/`(배치)의 인프라는 아직 미확정입니다.

## 배포 대상

- [x] 프론트엔드(Streamlit 앱) — Streamlit Community Cloud, `https://trend-keyword.streamlit.app/`
  (2026-08-12). **배포본이 로컬과 다르게 동작하면 아래부터 확인**:
  - [ ] Streamlit Cloud 대시보드 **Settings → Secrets**에 로컬 `.streamlit/secrets.toml`과 동일한
    내용이 들어있는지(플랫폼이 이 값을 그대로 `.streamlit/secrets.toml` 파일로 만들어주므로
    `config/secrets.py`가 로컬과 동일하게 동작함) — `[app] base_url`은 로컬과 달리 실제 배포 URL
    (`https://trend-keyword.streamlit.app`)로 넣어야 함
  - [ ] `ImportError`/`ModuleNotFoundError`가 뜨면 대개 배포본이 최신 커밋을 아직 못 받아온
    상태 — 대시보드에서 **Reboot app**으로 강제 재기동
- [ ] 백엔드 API(FastAPI)
- [ ] 배치 워커(스케줄러)
- [x] DB(Supabase/PostgreSQL — 2026-08-11 확정, 2026-08-12 연결+검증 완료. 전용 프로젝트가 아니라
  블로그 프로젝트(`blog_dashboard_data`)를 공유하고 `trendfit` 스키마로 격리 — 무료 플랜 프로젝트
  한도로 인한 결정, [product/CHANGELOG.md](../product/CHANGELOG.md) 2026-08-12 참고. `trendfit.profiles`
  테이블까지 마이그레이션 적용 완료(`supabase/migrations/`), REST API 조회 검증 완료)
- [x] 인증(Supabase Auth) — 2026-08-12 `services/auth_service.py` 실제 연동 완료(로그인/회원가입/
  비밀번호 재설정/변경/회원 탈퇴). 회원 탈퇴(`delete_account()`)는 `service_role` Admin API로
  `auth.users` 계정을 실제로 삭제 — 테스트 계정 생성→삭제로 `auth.users`·`trendfit.profiles`
  cascade까지 실제 확인 완료.
  - [x] 이메일 발송 — Supabase 기본 메일러는 커스텀 SMTP 없이는 템플릿(본문) 편집 자체가
    막혀 있어(대시보드 배너로 확인), Resend를 커스텀 SMTP로 연결(`smtp.resend.com`, 포트 465,
    Sender `onboarding@resend.dev` — Resend에 도메인 미검증 상태라 이 발신자만 허용됨. 도메인
    검증하면 자체 도메인 발신자로 교체 가능). "Confirm signup"·"Reset Password" 템플릿을
    `{{ .Token }}`(6자리 코드) 방식으로 교체 완료
  - [x] 실제 이메일(`jeonwoobin@gmail.com`)로 회원가입 → 코드 수신 → `complete_signup()`까지
    전체 플로우 실제 검증 완료(2026-08-12). 그 과정에서 `maybe_single().execute()`가 행이 없을
    때 `None`을 그대로 반환하는 걸 놓쳐 최초 가입 시 크래시 나던 버그를 발견해 수정
  - [ ] Authentication → Sessions의 JWT 만료 시간이 NFR-SEC-003(24시간) 기준과 맞는지(기본값은
    보통 1시간)
  - [x] 소셜 로그인(FR-AUTH-002, P2) 코드 연동 완료(2026-08-12) — `get_social_login_url()`이
    PKCE `code_verifier`/`code_challenge`를 직접 만들어 Supabase `/auth/v1/authorize`로 보내고,
    리다이렉트로 돌아오면 `complete_social_login()`이 `exchange_code_for_session()`으로 세션을
    교환한다(Streamlit은 브라우저 콜백을 못 받아 SDK의 `sign_in_with_oauth()`는 쓰지 않음).
    - [x] Google Cloud Console에 TrendFit 전용 OAuth 클라이언트(웹 애플리케이션) 생성, Kakao
      Developers에 TrendFit 앱 생성 — 둘 다 리다이렉트 URI를 Supabase 콜백
      (`https://qyqahxckbzbvrvtqdbdi.supabase.co/auth/v1/callback`)으로 등록(2026-08-12)
    - [x] Supabase Authentication → Providers에서 Google/Kakao 활성화 + Client ID/Secret 등록,
      → URL Configuration → Redirect URLs에 `http://localhost:8501/로그인` 추가(2026-08-12).
      **배포 URL(`https://trend-keyword.streamlit.app/로그인`)도 같은 목록에 추가해야 함** — 앱의
      `redirect_to`는 `config/secrets.py.get_app_base_url()`이 secrets.toml `[app] base_url`에서
      읽으므로, Streamlit Cloud Secrets에 이 값을 배포 URL로 설정해야 배포본에서도 맞게 동작함
    - [x] 카카오 동의항목(Kakao Developers → 카카오 로그인 → 동의항목) 중 "카카오계정(이메일)"은
      비즈니스 인증 없는 앱엔 권한 자체가 없어("권한 없음") 요청 시 KOE205로 거부됨을 발견
      (2026-08-12). 이메일 없이도 로그인되도록 이미 설계돼 있어(`complete_social_login`이 이메일
      없으면 `{user_id}@social.trendfit`로 대체), 닉네임/프로필 사진만 요청하도록
      `config.constants.KAKAO_OAUTH_SCOPES`로 범위를 좁힘. 나중에 이메일이 꼭 필요해지면 카카오
      "추가 기능 신청"으로 승인받아야 함
    - [ ] 실제 로그인 완료(비밀번호 입력)는 배포 URL 기준으로 아직 검증 중 — 로컬에선 사용자가
      직접 테스트 가능한 부분까지 확인했으나(구글/카카오 비밀번호는 대신 입력할 수 없음), 배포
      URL을 Redirect URLs에 추가한 뒤 배포본에서 재확인 필요
  - [ ] Resend 발신 도메인 검증(실제 서비스 오픈 전 — 지금은 `onboarding@resend.dev`로만 발송 가능)

## 환경변수/시크릿 체크리스트

시크릿 값 자체는 절대 이 문서나 git에 커밋하지 않습니다 — 실제 값은 각 환경(로컬
`.streamlit/secrets.toml`, Streamlit Cloud는 대시보드 Settings → Secrets — 플랫폼이 동일 경로에
파일로 만들어줘서 로컬과 같은 `config/secrets.py` 로더가 그대로 동작함)에만 보관합니다.

| 항목 | 용도 | 위치(로컬 기준) |
|---|---|---|
| 외부 트렌드/소셜/뉴스 API 키 | [docs/API_Design.md](../docs/API_Design.md) §8 연동 현황 참고 | `.streamlit/secrets.toml` |
| DB 접속 정보 | Supabase 등 | `.streamlit/secrets.toml` |
| 앱 배포 URL(`[app] base_url`) | OAuth `redirect_to` 등 (`config.secrets.get_app_base_url()`) | `.streamlit/secrets.toml` — 환경마다 값이 다름(로컬 `http://localhost:8501`, Streamlit Cloud는 실제 배포 URL) |
| JWT 시크릿 | 인증 토큰 서명 | 환경변수 |
| OAuth 클라이언트 ID/Secret | 구글/카카오 소셜 로그인 | Supabase 대시보드(Authentication → Providers)에 직접 저장 — 앱 코드/secrets.toml에는 없음 |
| 이메일 발송(Resend SMTP) 자격증명 | 회원가입/비밀번호 재설정 인증 메일(Supabase Auth 내장 발송) | Supabase 대시보드(Authentication → Emails → SMTP Settings)에 직접 저장 — 앱 코드/secrets.toml에는 없음 |

## 배포 체크리스트 (초안)

1. [ ] `docs/Coding_Convention.md` 기준 테스트 통과 확인
2. [ ] 배치 워커 중복 실행 방지 락 동작 확인
3. [ ] 신규 외부 연동이 있다면 [docs/API_Design.md](../docs/API_Design.md) §8에 반영됐는지 확인
4. [ ] 배포 후 `product/CHANGELOG.md`에 기록
