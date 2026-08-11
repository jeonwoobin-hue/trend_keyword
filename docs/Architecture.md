# Architecture.md — 폴더 구조 및 설계 원칙

> 공통 규칙은 [../CLAUDE.md](../CLAUDE.md) 참고. 기술 스택(초안): **Python + Streamlit(프론트) + FastAPI(백엔드) + 배치 워커**.

## 1. 폴더 구조 상세

```
project/
├── Home.py            # Streamlit 진입점 (streamlit run Home.py). 최상위 고정 위치 필수
├── pages/              # Streamlit 멀티페이지 (Home.py와 반드시 같은 위치). 화면 1개 = 파일 1개
├── app/                # 프론트 공용 초기화 모듈 (사이드바, session_state 초기화 등) — Home.py/pages에서 import
├── api/                # FastAPI 백엔드 — functional-spec.md의 REST 계약(/api/v1/...)을 구현
│   ├── routers/        # 리소스별 라우터 (profile, dashboard, reports, alerts, curations, admin ...)
│   └── deps/           # 인증/DB 세션 등 공용 의존성
├── worker/             # 배치 스케줄러 — Spike Score 계산(매시간), 알림 발송, 외부 데이터 수집
│   └── jobs/           # 잡 1개 = 파일 1개, 각 잡은 실패 시 관리자 알림 + 중복 실행 방지
├── components/         # 여러 페이지에서 재사용되는 UI 컴포넌트 함수
├── services/           # 외부 API 연동, 도메인 비즈니스 로직 (app/api/worker 공용, 핵심 계층)
├── models/             # 데이터 모델, 스키마, 타입 정의 (API 요청/응답 계약 포함)
├── utils/              # 특정 도메인에 종속되지 않는 공통 유틸 함수
├── config/             # 상수, 환경설정, 임계값, 캐시 TTL, rate limit (매직넘버는 반드시 여기서 관리)
├── assets/             # 이미지, 폰트 등 정적 리소스
├── data/
│   ├── raw/            # 원본 수집 데이터 (외부 API 응답 원본 스냅샷)
│   └── processed/       # 전처리/정제된 데이터 (Spike Score·감성분석 입력)
├── outputs/            # 분석 스크립트가 생성하는 산출물 (차트, 중간 결과 등)
├── reports/            # 내부 분석용, 사람이 읽는 보고서 (사용자向 "인사이트 리포트"와는 별개 — §3 참고)
├── .streamlit/         # Streamlit 설정 (config.toml, secrets.toml — secrets는 git 제외)
├── supabase/
│   └── migrations/     # DB 마이그레이션 SQL (Supabase CLI 없이 SQL Editor에서 순서대로 직접 실행,
│                        # 파일명 번호 순서 = 실행 순서). blog_dashboard_data 프로젝트를 블로그와
│                        # 공유하므로 전부 trendfit 스키마 안에서만 생성/변경한다
├── docs/               # 개발 규칙 문서
├── product/            # 서비스 개선 관리
├── ops/                # 운영 관리
├── deliverables/        # 산출물 관리
├── TrendFit-ux-docs/    # 요구사항/기능명세/IA 원본
└── tests/              # 테스트 코드 (소스와 동일한 폴더 구조로 미러링)
```

> **Streamlit 제약**: 멀티페이지 자동 인식을 위해 `pages/`는 반드시 진입 스크립트(`Home.py`)와 동일한
> 디렉터리(루트)에 있어야 합니다. `app/`을 진입점으로 착각하지 않도록 주의합니다.

## 2. 계층 설계 원칙

- **새 기능은 기존 구조를 우선 활용**합니다. 새 최상위 폴더를 만들기 전, 기존 폴더(`services/`, `utils/` 등)로
  표현 가능한지 먼저 검토합니다.
- **비슷한 기능이 존재하면 재사용**합니다. 새로 작성하기 전 `services/`, `utils/`에 유사 함수가 있는지 먼저 검색합니다.
- 의존 방향: `pages/components`, `api/routers`, `worker/jobs` → `services` → `models/utils`.
  `services`는 절대 `app`/`api`/`worker`를 참조하지 않습니다(역방향 금지).
- `api/routers`는 요청 검증(Pydantic)과 응답 조립만 담당하고, 실제 로직은 `services/`에 위임합니다(얇은 라우터).
- `worker/jobs`는 외부 트리거(스케줄러) 진입점 역할만 하고, 계산 로직은 `services/`에 둬 API에서도 재사용 가능하게 합니다.
- `config/`는 값이 바뀔 때 코드 수정 없이 설정만 바꾸면 되도록 설계합니다.

## 3. "리포트/산출물" 용어 구분 (혼동 주의)

TrendFit에는 이름이 비슷한 개념이 두 가지 있어 명확히 구분합니다.

| 용어 | 위치 | 대상 | 설명 |
|---|---|---|---|
| 인사이트 리포트 (REPORT-001/002) | DB에 저장, API로 제공 | 서비스 사용자 | 사용자가 요청해 생성되는 제품 기능. `services/`에서 생성, `api/`로 응답 |
| `reports/` 폴더 | 로컬 파일 | 개발팀 내부 | EDA·모델 성능 점검 등 개발 과정에서 사람이 읽는 분석 보고서 |
| `deliverables/` 폴더 | 로컬 파일 | 프로젝트 이해관계자 | 주간보고/회의록/발표자료 등 프로젝트 관리 산출물 |

## 4. 데이터 관리 원칙

| 위치 | 용도 | 규칙 |
|---|---|---|
| `data/raw/` | 원본 수집 데이터 | **절대 수정하지 않음.** 읽기 전용으로 취급 |
| `data/processed/` | 전처리 데이터 | `raw/`에서 파생, 재생성 가능해야 함 |
| `outputs/` | 분석 결과 | 스크립트 재실행 시 재생성 가능해야 함 |
| `reports/` | 개발팀 내부 보고서 | 사람이 읽는 최종 산출물 |

데이터 분석 세부 규칙(결측치/이상치/최신성 확인 등)은 [Data_Rules.md](Data_Rules.md) 참고.

## 5. 새 기능 추가 시 체크리스트

1. 기존 폴더/모듈로 표현 가능한가?
2. 재사용 가능한 기존 함수/컴포넌트가 있는가?
3. 상수/임계값을 `config/`에 분리했는가?
4. `data/raw/`를 변경하지 않았는가?
5. `api/` 계약이 [TrendFit-ux-docs/functional-spec.md](../TrendFit-ux-docs/functional-spec.md)와 다르면
   [API_Design.md](API_Design.md)에 실제 기준을 기록했는가?
6. 관련 `docs/` 문서를 함께 갱신했는가?
