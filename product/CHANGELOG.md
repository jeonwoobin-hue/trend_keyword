# CHANGELOG.md

날짜순으로 기록합니다 (최신이 위).

## 2026-08-12 (9)

- 인사이트 리포트의 키워드 연관성 지도(Network Graph, FR-REPORT-003) 연결 로직을 실제 계산으로
  교체. 기존엔 노드 연결이 완전히 랜덤 트리였음 — `utils/statistics.pearson_correlation()`(신규,
  공통 통계 유틸)로 언급량 추이 시계열 간 피어슨 상관계수를 구하고, 각 키워드를 상관 절댓값이
  가장 큰 키워드와 연결(`report_service._build_network_graph()`). 그래프 구조(노드 N개, 엣지
  N-1개 트리)는 그대로 유지.
- `docs/KPI_Definitions.md`에 "키워드 연관성 지도" 항목 신설, 계산식·엣지 케이스(표준편차 0 →
  상관관계 0)·미정 사항 기록.
- 이슈 요약(FR-REPORT-002)은 이번엔 손대지 않음 — 실제 AI 생성으로 바꾸려면 LLM API 연동이
  새로 필요해 별도로 진행하기로 함.
- `tests/utils/test_statistics.py` 신규 작성. 전체 테스트 128건 통과.

## 2026-08-12 (8)

- Spike Score(FR-DASH-003) 산출 로직을 실제로 구현. `services/spike_score_service.
  calculate_spike_score()`가 언급량 시계열에서 `(당일 − lookback 이동평균) ÷ lookback 표준편차`
  z-score를 구하고 시그모이드로 0~100에 정규화 — functional-spec.md가 정규화 함수를 명시하지
  않아 시그모이드로 확정(docs/KPI_Definitions.md 변경 이력에 근거 기록). 표준편차 0 엣지 케이스는
  문서대로 0점 처리.
- `services/dashboard_service.py`의 목 언급량 시계열 생성 방식도 함께 손봄 — 기존엔 그래프의 각
  포인트가 완전히 독립된 난수라 계산식을 붙여도 무의미했음. 키워드별 기준선(baseline) + 자연스러운
  변동으로 바꾸고, 약 15%의 키워드는 당일 값에 배수(1.15~1.8배)를 곱해 실제 급상승처럼 연출
  (`config.constants`의 `TREND_BASELINE_RANGE`/`TREND_NOISE_RATIO`/`SPIKE_KEYWORD_PROBABILITY`/
  `SPIKE_MULTIPLIER_RANGE`). 처음엔 배수를 2~4.5배로 뒀더니 시그모이드가 곧바로 포화돼 대시보드
  상위 20개가 전부 100.0으로 보여서(실제 브라우저로 확인 후 발견) 배수·비율을 낮춰 점수 차이가
  자연스럽게 드러나도록 조정. 결과적으로 대시보드의 Spike Score 정렬이 실제로 "급상승한 키워드가
  위로 온다"는 의미를 가짐.
- 데이터 자체(언급량 시계열)는 여전히 목업이지만, **계산 로직은 실제 산식**이라 외부 데이터 연동
  시 입력만 실제 API 응답으로 갈아끼우면 됨 — `worker/jobs`(매시간 배치)·ADMIN-001 수동 재계산은
  아직 없음, 지금은 대시보드 응답 생성 시 즉시 계산.
- `tests/services/test_spike_score_service.py` 신규 작성(경계값·엣지 케이스·결정성 포함). 전체
  테스트 120건 통과.

## 2026-08-12 (7)

- **프론트엔드 배포 확정**: Streamlit Community Cloud, `https://trend-keyword.streamlit.app/`.
  사용자가 이미 로컬과 별개로 배포해 테스트 중이었다는 걸 소셜 로그인 디버깅 도중 발견 — 그동안
  로컬 기준으로만 안내하고 있었음.
- 카카오 소셜 로그인 KOE205(잘못된 요청) 원인 확인: "카카오계정(이메일)" 동의항목이 비즈니스 인증
  없는 앱엔 "권한 없음" 상태라 요청 자체가 거부됨. `KAKAO_OAUTH_SCOPES`(`profile_nickname
  profile_image`)로 요청 범위를 좁혀 이메일 없이 로그인하도록 조정(`complete_social_login`은
  이미 이메일이 없을 때 `{user_id}@social.trendfit`로 대체하게 설계되어 있어 추가 변경 불필요).
- **`APP_BASE_URL`을 상수에서 시크릿으로 이동**: 로컬(`http://localhost:8501`)과 배포
  (`https://trend-keyword.streamlit.app`)가 서로 다른 URL을 쓰는데 코드에 하드코딩돼 있던 게
  배포본에서 OAuth가 안 되는 근본 원인 중 하나였음. `config/secrets.py`에 `get_app_base_url()`
  추가(secrets.toml `[app] base_url`, 없으면 로컬 기본값). Streamlit Cloud는 대시보드 Settings →
  Secrets에 넣은 내용을 플랫폼이 그대로 `.streamlit/secrets.toml` 파일로 만들어주므로, 기존
  파일 기반 로더가 로컬/배포 어디서나 동일하게 동작함.
- [ops/Deployment.md](../ops/Deployment.md)에 Streamlit Cloud Secrets 설정 확인 항목, 배포 URL을
  Supabase Redirect URLs에 추가해야 한다는 점 정리. 전체 테스트 111건 통과.

## 2026-08-12 (6)

- 소셜 로그인(FR-AUTH-002) 대시보드 설정 완료. Google Cloud Console에 TrendFit 전용 OAuth 클라이언트
  (기존에 다른 용도로 있던 클라이언트는 재사용하지 않고 새로 생성), Kakao Developers에 TrendFit 앱을
  만들고 둘 다 Supabase 콜백 URL을 리다이렉트 URI로 등록. Supabase Authentication → Providers에서
  Google/Kakao 활성화 + Client ID/Secret 등록, → URL Configuration → Redirect URLs에
  `http://localhost:8501/로그인` 추가.
  - 실제 authorize URL로 왕복 검증: 처음엔 Google이 "provider is not enabled"로 실패 —
    Client ID/Secret은 맞게 들어가 있었지만 "Enable Sign in with Google" 토글 자체가 꺼져 있던
    설정 누락이었음, 토글 켜고 해결. 이후 구글/카카오 둘 다 실제 로그인 화면(accounts.google.com,
    accounts.kakao.com)까지 정상 도달하는 것을 브라우저로 확인.
  - 카카오는 스크립트(urllib)로 테스트할 때만 404가 났는데, 실제 브라우저로 확인하니 정상 —
    카카오 로그인 페이지의 봇 차단성 동작으로 판단, 실제 설정 문제 아님.
  - 최종 로그인 완료(비밀번호 입력)는 사용자 본인 계정으로 직접 테스트 필요.

## 2026-08-12 (5)

- 소셜 로그인(FR-AUTH-002, P2) 코드 연동 착수. `login_with_social_provider()`(완전 목업) 제거,
  대신 `get_social_login_url()`/`complete_social_login()` 추가 — Supabase Auth OAuth(PKCE) 흐름.
  - Streamlit은 서버사이드 프레임워크라 SDK의 `sign_in_with_oauth()`가 기대하는 "브라우저가
    콜백을 자동으로 받는" 모델을 못 씀 — 대신 `code_verifier`/`code_challenge`를
    `supabase_auth.helpers`로 직접 만들어 Supabase `/auth/v1/authorize`로 리다이렉트하고,
    `pages/0_로그인`이 되돌아온 `?code=`를 `st.query_params`로 읽어 `exchange_code_for_session()`
    으로 세션을 교환한다.
  - `code_verifier`는 프로바이더별로 `st.session_state[SessionKeys.OAUTH_CODE_VERIFIERS]`(dict)에
    저장. 콜백 시점엔 어느 프로바이더로 로그인했는지 알 수 없어 저장된 후보를 순서대로 시도.
  - `config.constants.APP_BASE_URL` 추가(OAuth `redirect_to` 등에 사용, 로컬 개발 기준값 — 배포
    도메인이 정해지면 Supabase Redirect URLs와 함께 갱신 필요).
  - **아직 남은 것(대시보드 설정)**: Supabase Authentication → Providers에 Google/Kakao Client
    ID·Secret 등록, → URL Configuration에 Redirect URL 등록. 둘 다 각 콘솔(Google Cloud Console,
    Kakao Developers)에서 앱 등록이 먼저 필요해 별도로 진행 예정([ops/Deployment.md](../ops/Deployment.md)
    참고) — 코드는 준비됐지만 이 설정 전까지는 실제 로그인이 되지 않음.
- 전체 테스트 109건 통과.

## 2026-08-12 (4)

- 이메일 인증 코드(OTP) 발송을 실제로 완성. Supabase 기본 메일러는 커스텀 SMTP 없이는 템플릿
  편집 자체가 막혀 있어(대시보드에서 확인), Resend를 커스텀 SMTP로 연결하고 "Confirm signup"·
  "Reset Password" 템플릿을 `{{ .Token }}`(6자리 코드) 방식으로 교체. 발신자는 Resend 도메인
  미검증 상태라 `onboarding@resend.dev`로 설정(도메인 검증 시 자체 도메인으로 교체 필요,
  [ops/Deployment.md](../ops/Deployment.md) 참고).
- **실제 이메일로 전체 플로우 검증**: `jeonwoobin@gmail.com`으로 회원가입 → 실제 수신한 코드로
  `complete_signup()` 호출까지 end-to-end로 확인. 사용자 요청으로 이 테스트 계정은 삭제하지 않고
  유지.
- **버그 픽스(실제 검증 중 발견)**: `_load_or_create_profile()`이 `maybe_single().execute()`의
  반환값에서 곧바로 `.data`에 접근하고 있었는데, postgrest-py는 일치하는 행이 없으면 `.data`가
  `None`인 응답 객체가 아니라 **`execute()` 자체가 `None`을 반환**한다(`Optional[SingleAPIResponse]`).
  그 결과 최초 회원가입/로그인처럼 프로필이 아직 없는, 실제로는 가장 흔한 경로에서
  `AttributeError`로 크래시가 나고 있었다 — 가짜 클라이언트로 만든 단위 테스트는 이 케이스를
  `SimpleNamespace(data=None)`으로 잘못 흉내 내고 있어 걸러내지 못했고, 실제 이메일로 처음부터
  끝까지 테스트하는 과정에서만 드러났다. `existing is not None and existing.data`로 수정하고,
  테스트 픽스처도 실제 동작(`None` 반환)에 맞게 정정.
- 전체 테스트 106건 통과.

## 2026-08-12 (3)

- 회원 탈퇴(MY-002, FR-PROFILE-004) 시 Supabase의 실제 계정 삭제까지 마무리. `services/auth_service.
  delete_account()`가 `service_role` Admin API(`auth.admin.delete_user`)로 `auth.users` 계정을
  삭제하면 `trendfit.profiles`는 외래키 `on delete cascade`로 함께 삭제된다(`pages/14_계정_설정`).
  소셜 로그인(P2, 실제 Supabase 계정이 없는 목업 경로)은 기존처럼 로컬 세션만 초기화.
- **실제 계정으로 검증**: Admin API로 이메일 인증까지 끝난 테스트 계정을 직접 만들고
  `trendfit.profiles` 행도 넣은 뒤 `delete_account()`를 호출 — profiles 행이 cascade로 사라지고,
  `auth.users`에서도 계정이 실제로 삭제된 것(`get_user_by_id`가 "User not found")까지 확인.
  이메일 인증 플로우 없이 관리자 API만으로 만든 자체 완결형 테스트라 실제 이메일이 필요 없었음.
- `tests/services/test_auth_service.py`에 `delete_account` 성공/실패 케이스 추가. 전체 테스트
  106건 통과.

## 2026-08-12 (2)

- `services/auth_service.py`의 목(mock) 로그인/회원가입/비밀번호 재설정/변경 로직을 Supabase Auth +
  `trendfit.profiles` 실제 연동으로 교체(로그인 FR-AUTH-001, 회원가입 FR-AUTH-003, 비밀번호 재설정
  FR-AUTH-004, 계정 설정의 비밀번호 변경·표시 이름 수정 MY-002). 이메일 인증/비밀번호 재설정은
  화면에 코드를 노출하던 목업 대신 Supabase의 이메일 OTP(6자리 코드)로 실제 발송된다 — 배포 전
  Supabase 대시보드에서 Email Templates를 코드 방식(`{{ .Token }}`)으로 설정해야 동작함
  ([ops/Deployment.md](../ops/Deployment.md) 참고).
- **버그 픽스(구현 중 발견)**: `services/supabase_client.py`의 anon 클라이언트를 프로세스 전역
  싱글턴(`lru_cache`)으로 캐싱하고 있었는데, Streamlit은 여러 브라우저 세션이 한 프로세스를
  공유하므로 로그인 세션(JWT)을 그 싱글턴에 실으면 사용자 간에 세션이 섞일 수 있는 구조적 결함이
  있었다. 아직 실제 로그인 코드가 없어 문제가 드러나기 전에 발견 — 로그인 연동을 시작하며
  `get_supabase_client()`(캐시된 싱글턴)를 제거하고, 인증이 관여하는 호출마다 새 클라이언트를
  만드는 `create_supabase_client(access_token=None)`으로 교체했다. `service_role` 클라이언트는
  사용자 세션을 들고 있지 않아 싱글턴으로 유지해도 안전해 그대로 둠.
- `models/auth.py`: `AuthUser`에 `id`(uuid) 추가, 세션 토큰 전용 `AuthSession` 모델 추가.
  `config/constants.py`에 `SessionKeys.AUTH_SESSION` 추가(로그아웃/회원 탈퇴 시 함께 초기화).
- 회원가입/비밀번호 재설정 화면(`pages/1_회원가입`, `pages/13_비밀번호_재설정`)의 흐름을 실제 OTP에
  맞게 조정 — 더 이상 인증번호를 화면에 노출하지 않고, 비밀번호 재설정은 "코드 확인"과 "새 비밀번호
  저장"을 한 단계로 합침(Supabase의 recovery OTP는 한 번 검증하면 세션으로 소비되어, 확인 단계를
  분리하면 코드를 두 번 써야 하는 문제가 있었음).
- 남은 목업: 소셜 로그인(FR-AUTH-002, P2, OAuth 프로바이더 설정 필요)과 회원 탈퇴 시 실제
  Supabase 계정 삭제(FR-PROFILE-004, 현재는 로컬 세션만 초기화) — 별도 작업으로 진행 예정.
- `tests/services/test_auth_service.py`를 Supabase 클라이언트를 가짜로 대체(monkeypatch)하는
  방식으로 전면 재작성, `tests/app/test_session.py`도 `AuthUser.id` 필수화에 맞춰 갱신.
- **실제 앱으로 검증**: `streamlit run Home.py`를 띄워 로그인 화면에서 존재하지 않는 계정으로
  로그인을 시도해 실제 Supabase Auth 호출까지 왕복하고 정확한 에러 메시지가 뜨는 것을 확인. 회원가입
  화면은 브라우저 자동화로 약관 동의 체크박스를 제어하기 어려워, 대신 `request_signup_verification()`을
  직접 호출해 실제 Supabase에 왕복시켜 검증.
  - 그 과정에서 **버그 발견 및 수정**: Supabase가 `example.com`처럼 형식은 맞지만 실제로 받을 수
    없다고 판단하는 이메일을 `email_address_invalid`로 거부하는데, `request_signup_verification()`이
    모든 Supabase 에러를 "이미 가입된 이메일"(VALID_003)로 뭉뚱그려 잘못된 메시지를 보여주고
    있었다. Supabase 에러 코드별로 분기(`email_address_invalid` → VALID_002, `user_already_exists`
    → VALID_003, 그 외 → SERVER_005)하도록 수정하고 테스트 2건 추가.
  - 전체 테스트 104건 통과.

## 2026-08-12

- Supabase 연결 계층 착수(1단계 "DB+실제 인증"의 첫 조각). 원래 계획은 TrendFit 전용 프로젝트
  생성이었으나, 무료 플랜의 조직당 활성 프로젝트 한도(2개)에 이미 도달해 있어 블로그 프로젝트를
  공유하고 `trendfit` 스키마로 데이터를 격리하는 방식으로 변경(사용자 결정, 다른 프로젝트에
  영향 없음 확인).
  - `config/secrets.py`: `.streamlit/secrets.toml` 로더 — `api/`·`worker/`가 Streamlit 런타임
    밖에서도 동일하게 시크릿을 읽을 수 있도록 `st.secrets` 대신 파일을 직접 파싱
  - `services/supabase_client.py`: anon/service_role 키 기반 클라이언트 팩토리(`get_supabase_client`,
    `get_supabase_admin_client`), 모든 조회는 `trendfit` 스키마로 제한
  - `config/constants.py`에 `SUPABASE_SCHEMA` 추가, `requirements.txt`에 `supabase==2.31.0` 추가
  - `.streamlit/secrets.toml.example` 추가(실값은 git 제외, 로컬에서 복사해 채우는 방식)
  - Supabase 대시보드에서 `trendfit` 스키마 생성 + Settings → Data API의 Exposed schemas에 추가
    완료. REST API로 anon/service_role key 왕복 테스트 통과(`PGRST205` — 존재하지 않는 테이블을
    조회했을 때 나오는 정상 응답까지 확인. 이전엔 `PGRST106 Invalid schema`로 실패했었음)
  - `trendfit.profiles` 테이블 설계(`supabase/migrations/0001_create_profiles.sql`) — Supabase
    Auth(`auth.users`)에 인증(비밀번호 해시·이메일 인증·JWT 발급)을 위임하고, TrendFit 전용 필드
    (표시 이름·역할·알림 기본값)만 담는 1:1 확장 테이블로 설계
  - **`auth.users`에는 트리거를 달지 않기로 결정**: `auth.users`는 블로그 프로젝트와 공유하는
    테이블이라, 트리거를 달면 앱 구분 없이 모든 회원가입(블로그 포함)에 실행되어 블로그 가입
    흐름에까지 영향을 준다. 대신 TrendFit 회원가입 완료 시 서비스 코드가 `trendfit.profiles`에
    명시적으로 행을 insert하는 방식으로 설계(사용자 결정, 2026-08-12)
  - `0001_create_profiles.sql` 실행 후 REST API로 조회하니 `42501 permission denied for schema
    trendfit` — Supabase는 새 스키마 생성 시 `anon`/`authenticated`/`service_role` 역할에 기본
    권한을 주지 않는다는 걸 확인. `supabase/migrations/0002_grant_trendfit_privileges.sql`로
    schema usage + 테이블 권한 + 향후 테이블에도 자동 적용되는 default privileges까지 부여
  - 두 마이그레이션(0001, 0002) 모두 SQL Editor에서 실행 완료. anon/service_role key 양쪽으로
    `trendfit.profiles` 조회 정상 동작(`200 []`, RLS 적용 상태로 빈 결과) 확인
  - 다음 단계: `auth_service.py` 등 목(mock) 로직을 실제 Supabase Auth 연동으로 교체 — 별도
    작업으로 진행 예정

## 2026-08-11

- `Home.py` Streamlit 진입점 및 랜딩(COM-001) 구현
- 인증 화면 구현(목업): 로그인(COM-002), 회원가입(COM-003, 이메일 인증 mock), 로그아웃 — `services/auth_service.py`
- 관심사 온보딩(ONBOARD-001) 구현 — `services/profile_service.py`
- 트렌드 대시보드(DASH-001), 키워드 상세(DASH-002) 구현(목 데이터) — `services/dashboard_service.py`
- 급상승 알림 설정(ALERT-001) 구현(세션 저장) — `services/alert_service.py`
- 마이페이지(MY-001) 구현 — 프로필 조회, 관심사 수정 진입, 로그아웃
- `requirements.txt` 작성
- 인사이트 리포트 목록/상세(REPORT-001, REPORT-002) 구현 — `services/report_service.py`,
  Word Cloud/Network Graph는 접근성을 위해 막대그래프·연관 쌍 표로 대체 표현
- 콘텐츠 큐레이션(CURATE-001) 구현 — `services/curation_service.py`, 커서 기반 "더 보기"
- 관리자 대시보드(ADMIN-001) 구현 — `services/admin_service.py`, 외부 연동은 실제 미구현 상태
  그대로 표시(가짜 수치 없음), Spike Score 배치는 목 데이터 기준 재계산 시연
- 로그인 라우트 가드 적용 — `app/auth_guard.py`의 `require_login()`을 온보딩·키워드 상세·알림·
  리포트·큐레이션·마이페이지·관리자 화면에 적용 (대시보드는 IA상 비로그인도 열람 가능해 제외)
- 알림함(ALERT-002) 구현 — `pages/11_알림함`, 실제 발송 배치 워커(FR-ALERT-003)가 없어 등록 키워드
  기준으로 발송 이력을 시뮬레이션(읽음 처리 포함). 백로그 점검 중 임계치 설정(FR-ALERT-002, BL-006)이
  이미 ALERT-001 등록 플로우에 구현돼 있던 걸 확인해 `product/Backlog.md`에서 완료로 정정
- 사용자·키워드 관리(ADMIN-002) 구현 — `pages/12_사용자_키워드_관리`, 사용자 목록/등록 키워드
  통계/신고 내역은 샘플 데이터, 키워드 블랙리스트는 실제 CRUD(세션 저장). `product/Backlog.md`
  BL-011 완료로 정정
- Git 저장소 초기화 및 첫 커밋/푸시 —
  [github.com/jeonwoobin-hue/trend_keyword](https://github.com/jeonwoobin-hue/trend_keyword) `main`
  브랜치로 전체 코드베이스 최초 반영
- 유사 관심사 비교 추천 키워드(REPORT-002, FR-REPORT-005) 구현 — 고정 분야 매핑
  (`SIMILAR_CATEGORIES`: 패션↔뷰티↔여행, IT테크↔재테크) 기반 목 데이터. `docs/KPI_Definitions.md`의
  "산정 방법: 미정"을 확정 내용으로 갱신, `product/Backlog.md` BL-005 완료로 정정
- `tests/services/`에 서비스 계층 pytest 총 67건 작성 (dashboard/alert/profile/auth/report/
  curation/admin 7개 모듈)
- `docs/Feature_Roadmap.md` 구현 현황을 위 내용 기준으로 갱신
- 위 화면들은 전부 `services/`의 목(mock) 데이터로 동작 — 실제 백엔드(`api/`)·배치 워커(`worker/`)·
  외부 데이터 연동은 미착수. SRS의 8개 P1 기능 영역(인증~관리자) 화면이 모두 최소 목업으로 구현됨
- 관심 분야를 네이버 주제 필터 기준 20개 카테고리로 확장 — `services/dashboard_service.py` 목
  데이터 풀 보강, `TrendFit-ux-docs/srs.md`·`functional-spec.md`·`ia.md` v1.1로 갱신
- 사이드바 15개 화면 평면 나열을 상단 호버 드롭다운 메뉴(홈/트렌드/인사이트/마이페이지/관리자)로
  개편 — 신규 `components/top_nav.py`. 순수 HTML 링크 클릭 시 Streamlit 세션이 초기화되는 문제를
  발견해, 화면에 보이지 않는 iframe 스크립트로 숨겨진 네이티브 사이드바 링크를 대신 클릭하는
  방식으로 우회
- 관리자 역할(role) 기반 접근 제어 구현 — `AuthUser.role`, `config.ADMIN_EMAILS` 화이트리스트
  (정식 사용자 저장소 도입 전 임시 방식), `app/auth_guard.py`의 `require_admin()`. 관리자
  화면(ADMIN-001/002)과 상단 메뉴의 관리자 그룹 노출을 로그인 여부가 아닌 역할 기준으로 제한
- `product/Backlog.md` 상태값을 실제 코드와 대조해 정정 — BL-001·002·004·008·009·010·012를
  대기→완료로, BL-003(연령/성별 가중치 보정)은 UI/모델만 있고 실제 산식이 없어 진행중으로 반영
- `docs/Feature_Roadmap.md` 구현 현황 표를 위 정정에 맞춰 갱신, 관리자 역할 접근 제어 설명
  최신화, 테스트 건수(67→91)·서비스 모듈 수(7→8, `report_export_service.py` 누락 보완) 정정
- `TrendFit-ux-docs/ia.md`를 v1.2로 갱신 — 비밀번호 재설정을 별도 화면(COM-004)으로 승격,
  실제 상단 메뉴 그룹을 반영한 "상단 메뉴 구조" 절/다이어그램 신규 추가(콘텐츠 흐름 계층도는
  원본 그대로 유지)
- `TrendFit-ux-docs/srs.md`·`functional-spec.md`를 v1.2로 갱신 — 문서 간 버전 참조 동기화,
  관리자 역할 판별 방식(이메일 화이트리스트 임시 방식) 각주 추가. 요구사항 텍스트 자체는 변경 없음
- `tests/services/test_auth_service.py`에 역할 판별 테스트 4건 추가, `python -m pytest -q` 91건
  전체 통과 확인
- 콘텐츠 상세(CURATE-002) 구현 — 신규 `pages/15_📄_콘텐츠_상세.py`, `services/curation_service.py`에
  `get_content_detail()` 추가(연관 키워드 태그는 주제 기반 목업), `models/curation.py`에
  `ContentDetail` 모델 추가. `pages/8_콘텐츠_큐레이션` 카드의 "상세보기"에서 진입, 원문 이동·스크랩
  제공(스크랩은 기존 마이페이지 목록과 연동). 상단 메뉴 인사이트 그룹에도 추가.
  `TrendFit-ux-docs/ia.md` v1.3, `docs/Feature_Roadmap.md` 갱신, 테스트 4건 추가로 95건 전체 통과
- 계정 설정(MY-002) 빠진 기능 보강 — IA에는 "정보 수정, 비밀번호 변경, 회원 탈퇴"가 정의돼
  있었는데 알림 수신 설정·회원 탈퇴만 구현돼 있던 걸 확인해 나머지를 채움. 표시 이름 수정,
  기본 탐색 기간 설정(관심사 프로필의 `period` 필드 직접 수정), 비밀번호 변경(신규
  `services/auth_service.change_password()`, 현재 비밀번호는 형식만 확인) 추가.
  `docs/Feature_Roadmap.md` 갱신, 테스트 4건 추가로 99건 전체 통과
- 알림함(ALERT-002) "키워드 상세 보기" 구현 — IA의 "알림 상세(키워드 상세) 이동" 기능이
  빠져있던 걸 확인해 추가. 신규 `services/dashboard_service.find_keyword_id_by_name()`으로
  알림 키워드 텍스트를 목 키워드 풀과 이름 대조해 `keyword_id`를 찾고 DASH-002로 이동.
  급상승 알림 등록 시 자유 입력한 키워드가 목 데이터 풀에 없으면 버튼을 비활성화해 그레이스풀하게
  처리(실제 로그인 세션에서 매칭/비매칭 두 경우 모두 브라우저로 확인). 테스트 2건 추가로 101건
  전체 통과
- `api/`(FastAPI 백엔드) 착수 계획 수립, DB를 Supabase(PostgreSQL)로 확정(`CLAUDE.md` §6,
  `ops/Deployment.md` 갱신). 결론: `services/`가 이미 API 계약 형태로 설계돼 있어 `api/` 라우터
  자체는 짧은 작업이지만, DB·실제 인증 없이 먼저 붙이면 지금의 세션 목업과 실질적으로 동일해
  가치가 없음 — "DB+실제 인증(1단계) → api/ 라우터(2단계) → worker/ 배치(4단계)" 순으로 묶어서
  진행하기로 함. 1단계 착수는 별도 세션에서 진행 예정

## 2026-08-10

- 프로젝트 규칙 문서(`CLAUDE.md`, `docs/`) 및 폴더 구조(`product/`, `ops/`, `deliverables/`, 코드 스켈레톤) 초기 세팅
