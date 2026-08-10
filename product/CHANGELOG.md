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
- `tests/services/`에 서비스 계층 pytest 총 57건 작성 (dashboard/alert/profile/auth/report/
  curation/admin 7개 모듈)
- `docs/Feature_Roadmap.md` 구현 현황을 위 내용 기준으로 갱신
- 위 화면들은 전부 `services/`의 목(mock) 데이터로 동작 — 실제 백엔드(`api/`)·배치 워커(`worker/`)·
  외부 데이터 연동은 미착수. SRS의 8개 P1 기능 영역(인증~관리자) 화면이 모두 최소 목업으로 구현됨

## 2026-08-10

- 프로젝트 규칙 문서(`CLAUDE.md`, `docs/`) 및 폴더 구조(`product/`, `ops/`, `deliverables/`, 코드 스켈레톤) 초기 세팅
