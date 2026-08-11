# CHANGELOG.md

날짜순으로 기록합니다 (최신이 위).

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
