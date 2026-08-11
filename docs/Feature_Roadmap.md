# Feature_Roadmap.md — 기능 영역 및 구현 현황

> 공통 규칙은 [../CLAUDE.md](../CLAUDE.md) 참고. 요구사항 원본은
> [../TrendFit-ux-docs/srs.md](../TrendFit-ux-docs/srs.md), 상세 처리로직은
> [../TrendFit-ux-docs/functional-spec.md](../TrendFit-ux-docs/functional-spec.md) 참고.
> P2/P3 항목의 실제 착수 여부/우선순위 조정은 [product/Backlog.md](../product/Backlog.md)에서 트래킹합니다.

## P1(1차 출시) 기능 영역

> 구현 현황의 **목업 구현**은 Streamlit 화면이 `services/`의 목(mock) 데이터로 동작한다는 뜻이며,
> 실제 FastAPI 백엔드(`api/`)·배치 워커(`worker/`)·외부 데이터 연동은 아직 없습니다. 상세는
> 바로 아래 "구현 방식 참고" 절 참고.

| 영역 | 관련 화면 | 대표 요구사항 | 구현 현황 |
|---|---|---|---|
| 인증 | COM-001~003 | FR-AUTH-001 이메일 로그인, FR-AUTH-002 소셜 로그인, FR-AUTH-003 회원가입, FR-AUTH-004 비밀번호 재설정, FR-AUTH-005 로그아웃 | 목업 구현 (`Home.py`, `pages/0_로그인`, `pages/1_회원가입`, `pages/13_비밀번호_재설정`, `pages/6_마이페이지`) — 소셜 로그인은 실제 OAuth 연동 전 목업, 비밀번호 재설정은 인증번호를 화면에 노출하고 새 비밀번호는 저장하지 않는 목업 |
| 관심사 온보딩 | ONBOARD-001, 002 | FR-ONBOARD-001~003 관심 분야/목적/조건 설정 및 저장 | ONBOARD-001 목업 구현 (`pages/2_관심사_설정`) — ONBOARD-002는 별도 화면 대신 같은 페이지 내 제출 후 요약으로 대체 |
| 트렌드 대시보드 | DASH-001 | FR-DASH-001 핫 키워드, FR-DASH-002 언급량 시각화, FR-DASH-006 기간 필터 | 목업 구현 (`pages/3_트렌드_대시보드`) |
| Spike Score | DASH-001/002, ADMIN-001 | FR-DASH-003 급상승 지수 산출(배치) | 화면 표시값만 목업(난수 생성) — 실제 산출식·배치 워커는 미착수 |
| 키워드 상세 | DASH-002 | FR-DASH-004 검색량 추이·감성분석 조회, FR-DASH-005 연령/성별 가중치 보정 | 목업 구현 (`pages/4_키워드_상세`) — FR-DASH-005는 가중치 표시 UI와 `DemographicWeights` 모델까지는 구현됐지만, `dashboard_service._build_demographic_weights()`가 난수를 정규화해 보여주는 것뿐이라 실제 보정 산식은 미정([KPI_Definitions.md](KPI_Definitions.md) 참고) |
| 인사이트 리포트 | REPORT-001, 002 | FR-REPORT-001 생성 요청, FR-REPORT-002 이슈 요약, FR-REPORT-003 연관성 지도, FR-REPORT-004 저장/공유/PDF, FR-REPORT-005 유사 관심사 비교 추천 | 목업 구현 (`pages/7_인사이트_리포트`, `pages/10_리포트_상세`) — Word Cloud/Network Graph는 접근성을 위해 막대그래프·연관 쌍 표로 대체 표현. PDF 다운로드는 fpdf 기반 실제 생성(`report_export_service.build_report_pdf`), 공유 링크는 백엔드 없는 표시용 목업. 유사 관심사 비교 추천은 고정 분야 매핑 기반 목 데이터([KPI_Definitions.md](KPI_Definitions.md) 참고) |
| 급상승 알림 | ALERT-001, 002 | FR-ALERT-001 키워드 등록, FR-ALERT-002 임계치 설정, FR-ALERT-004 알림 히스토리 | 목업 구현 (`pages/5_급상승_알림`, `pages/11_알림함`, 세션 동안만 유지). FR-ALERT-002(임계치 설정, SRS는 P2로 분류)는 functional-spec의 FR-ALERT-001 등록 플로우에 포함돼 함께 구현됨. 실제 발송 배치 워커(FR-ALERT-003)가 없어 알림함은 등록 키워드 기준 이력을 시뮬레이션. 알림함의 "키워드 상세 보기"(IA "알림 상세 이동")는 `dashboard_service.find_keyword_id_by_name()`으로 알림 키워드를 목 키워드 풀과 이름 대조해 DASH-002로 이동 — 풀에 없는 자유 입력 키워드는 버튼 비활성화 |
| 콘텐츠 큐레이션 | CURATE-001, 002 | FR-CURATE-001 관련 콘텐츠 큐레이션, FR-CURATE-002 플랫폼별 필터, FR-CURATE-003 스크랩 | 목업 구현 (`pages/8_콘텐츠_큐레이션`, `pages/15_콘텐츠_상세`) — CURATE-001은 커서 기반 "더 보기", 플랫폼 필터는 멀티셀렉트가 `get_curated_contents()`에서 실제로 목록을 필터링. CURATE-002는 카드의 "상세보기"로 진입, 콘텐츠 미리보기·연관 키워드 태그(주제 기반 목업)를 보여주고 원문 이동·스크랩 제공. 스크랩은 `add_scrap`/`remove_scrap` + `pages/6_마이페이지` 목록 표시까지 구현(세션 저장만, 영속화 없음) |
| 프로필/마이페이지 | MY-001, 002 | FR-PROFILE-001 프로필 조회, FR-PROFILE-002 관심사 수정, FR-PROFILE-003 알림 수신 설정, FR-PROFILE-004 회원 탈퇴 | 목업 구현 (`pages/6_마이페이지`, `pages/14_계정_설정`) — 계정 정보(표시 이름)·비밀번호 변경·기본 탐색 기간 설정까지 구현되어 IA의 MY-002 기능이 모두 채워짐. 알림 수신 설정은 세션 저장만, 비밀번호 변경은 `services/auth_service.change_password()`가 현재 비밀번호를 대조 없이 형식만 확인(실제 계정 저장소 없음), 회원 탈퇴는 `clear_user_data()`로 사용자 개인 데이터를 실제로 초기화 |
| 관리자 | ADMIN-001, 002 | FR-ADMIN-001 데이터 수집 모니터링, FR-ADMIN-002 사용자·키워드 관리 | 목업 구현 (`pages/9_관리자`, `pages/12_사용자_키워드_관리`) — 외부 연동 상태는 실제 미구현 값 그대로 표시(가짜 수치 없음), 사용자 목록·키워드 통계·신고 내역은 샘플 데이터, 키워드 블랙리스트는 실제 CRUD. `AuthUser.role`(`config.ADMIN_EMAILS` 화이트리스트 기반 목업)과 `require_admin()`으로 로그인 여부뿐 아니라 관리자 역할까지 확인 |

## 구현 방식 참고

- 현재 모든 화면은 `Home.py`/`pages/`(Streamlit)에서 `services/`의 목(mock) 데이터로 동작합니다.
  `api/`(FastAPI), `worker/`(배치 스케줄러), 외부 데이터 연동(네이버 데이터랩·구글 트렌드·유튜브·X·
  포털 뉴스, [API_Design.md](API_Design.md) §8 연동 현황 참고)은 아직 착수 전입니다.
- 인증(로그인/회원가입)과 알림·리포트 등록은 실제 DB 대신 `st.session_state`에만 저장되어,
  브라우저 세션이 끊기면 초기화됩니다.
- 로그인이 필요한 화면(IA 접근권한 `U`)은 `app/auth_guard.py`의 `require_login()`으로 접근을
  제어합니다. 관리자 전용(`A`) 화면(`pages/9_관리자`, `pages/12_사용자_키워드_관리`)은
  `require_admin()`으로 로그인 여부와 `AuthUser.role`(`UserRole.ADMIN`)을 함께 확인합니다.
  역할은 실제 사용자 저장소 대신 `config.ADMIN_EMAILS` 화이트리스트로 판별하는 목업이라,
  실제 DB가 생기면 역할 컬럼 조회로 교체해야 합니다. 대시보드(DASH-001)는 IA상 비로그인
  사용자도 열람 가능(`G/U`)해 가드를 적용하지 않았습니다.
- `services/`의 `dashboard_service.py`, `alert_service.py`, `profile_service.py`, `auth_service.py`,
  `report_service.py`, `report_export_service.py`, `curation_service.py`, `admin_service.py` 8개
  모듈과 `app/session.py`가 `tests/services/`·`tests/app/`에 pytest 101건으로 커버되어
  있습니다(`python -m pytest -q`).
- 이 저장소는 [github.com/jeonwoobin-hue/trend_keyword](https://github.com/jeonwoobin-hue/trend_keyword)에
  `main` 브랜치로 푸시되어 있습니다.
- 각 서비스 모듈은 실제 연동 시 내부 구현만 교체하고 함수 시그니처/반환 타입은 유지하도록
  설계되어 있습니다(모듈 docstring에 명시).

## 제공 지표 (SRS 기준)

- 분야별 핫 키워드 / 언급량
- Spike Score(급상승 지수)
- 검색량 추이, 감성 분석 비율(긍정/부정/중립)
- 연관 키워드, 연령·성별 관심도 가중치 보정
- 이슈 요약, 키워드 연관성(Word Cloud, Network Graph)
- 유사 관심사 그룹 비교 추천 키워드

지표별 계산식/미정 사항은 [KPI_Definitions.md](KPI_Definitions.md) 참고.

## 신규 기능 추가 규칙

새로운 분석/제품 기능을 추가할 때는 다음 구조를 따릅니다:

1. **제공 지표/분석 항목** 정의
2. 반복 사용되는 지표는 [KPI_Definitions.md](KPI_Definitions.md)에 등록
3. API가 필요한 기능은 [API_Design.md](API_Design.md)의 공통 응답 포맷/에러코드 표를 따름
4. AI가 개입하는 기능(이슈 요약, 추천 키워드 등)은 [Prompt_Guide.md](Prompt_Guide.md)의 원칙 준수
5. 이 문서에 항목 추가 + 구현 현황 갱신
6. P1 범위 밖(P2/P3) 아이디어는 [product/Backlog.md](../product/Backlog.md)에 등록
