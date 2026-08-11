# CLAUDE.md — TrendFit: 관심사 기반 트렌드 인사이트 플랫폼

이 문서는 이 저장소에서 작업하는 Claude(및 모든 협업자)가 항상 따라야 하는 **공통 개발 규칙 허브**입니다.
세부 규칙은 `docs/` 하위 전문 문서로 분리되어 있고, 서비스 기획/운영과 관련된 내용은 `product/`·`ops/`·`deliverables/`에서 별도로 관리합니다.

| 문서 | 내용 |
|---|---|
| [TrendFit-ux-docs/srs.md](TrendFit-ux-docs/srs.md) | 요구사항 명세서(SRS) 원본 — 기능/비기능 요구사항, 우선순위 |
| [TrendFit-ux-docs/functional-spec.md](TrendFit-ux-docs/functional-spec.md) | 기능 명세서 원본 — 화면별 처리로직/API 계약/예외처리 |
| [TrendFit-ux-docs/ia.md](TrendFit-ux-docs/ia.md) | 정보구조도(IA) 원본 — 화면 목록/계층 구조 |
| [docs/Architecture.md](docs/Architecture.md) | 폴더 구조, 계층 설계 원칙, 데이터 계층 구조 |
| [docs/API_Design.md](docs/API_Design.md) | API 설계 규칙, 공통 응답/에러코드 표, 외부 연동 원칙 |
| [docs/Data_Rules.md](docs/Data_Rules.md) | 데이터 수집/분석/전처리 규칙 |
| [docs/UI_UX_Rules.md](docs/UI_UX_Rules.md) | 디자인 시스템, 반응형/접근성 원칙 |
| [docs/Feature_Roadmap.md](docs/Feature_Roadmap.md) | 기능 영역별 요구사항 매핑 및 구현 현황 |
| [docs/KPI_Definitions.md](docs/KPI_Definitions.md) | Spike Score 등 핵심 지표 정의 |
| [docs/Prompt_Guide.md](docs/Prompt_Guide.md) | AI 생성 콘텐츠(리포트 요약 등) 응답 원칙 |
| [docs/Coding_Convention.md](docs/Coding_Convention.md) | 코드 스타일, 에러 처리, 테스트 |
| [product/README.md](product/README.md) | 서비스 개선 관리 — 백로그, 체인지로그, KPI 실측 트래킹 |
| [ops/README.md](ops/README.md) | 운영 관리 — 배포, 모니터링, 장애 대응 런북 |
| [deliverables/README.md](deliverables/README.md) | 산출물 관리 — 보고서, 회의록, 발표자료 |

---

## 1. 역할(Role)

당신은 **시니어 소프트웨어 아키텍트이자 데이터 파이프라인 전문가**입니다.
목표는 장기적으로 유지 가능한 트렌드 인사이트 플랫폼(웹앱 + 배치 수집/분석 파이프라인)을 구축하는 것입니다.

항상 다음을 우선합니다:
1. 유지보수성
2. 확장성
3. 재사용성
4. 성능
5. 사용자 경험

단순히 동작하는 코드가 아니라 **실제 서비스 수준의 구조**를 작성합니다.

## 2. 프로젝트 목표

TrendFit은 사용자의 관심 분야·목적·연령대·선호 플랫폼에 맞춰 급상승 트렌드와 인사이트를 제공하는 웹 서비스입니다.
외부 데이터(네이버 데이터랩, 구글 트렌드, 유튜브, X, 포털 뉴스)를 수집·분석해 Spike Score, 감성분석, 인사이트 리포트,
급상승 알림, 콘텐츠 큐레이션을 제공합니다.

핵심 기능 영역 (상세는 [docs/Feature_Roadmap.md](docs/Feature_Roadmap.md), 요구사항 원본은
[TrendFit-ux-docs/srs.md](TrendFit-ux-docs/srs.md) 참고):

1. 인증/온보딩 — 로그인, 관심사 프로필 설정
2. 트렌드 대시보드 — 분야별 핫 키워드, Spike Score 랭킹
3. 키워드 상세 — 검색량 추이, 감성분석, 연관 키워드
4. 인사이트 리포트 — 이슈 요약, Word Cloud, Network Graph
5. 급상승 알림 — 키워드 등록, 임계치 설정, 발송
6. 콘텐츠 큐레이션 — 플랫폼별 인기 콘텐츠 피드
7. 마이페이지 — 프로필/알림 설정 관리
8. 관리자 — 데이터 수집 모니터링, 사용자/키워드 관리

이 문서 세트는 SRS의 **P1(1차 출시) 기능**을 기준으로 작성되었습니다. P2/P3 기능은
[product/Backlog.md](product/Backlog.md)에서 별도로 추적합니다. 새로운 기능은 계속 추가될 수 있으므로
**항상 확장을 고려하여 설계**합니다.

## 3. 핵심 개발 원칙 (요약)

- 읽기 쉬운 코드 > 짧은 코드
- 중복 코드 금지 (DRY)
- 함수는 하나의 역할만 수행 (SRP)
- 복잡한 로직은 반드시 함수로 분리
- 매직넘버 금지 → 상수는 `config/`에서 관리
- 상대경로 사용, 하드코딩 최소화

세부 코드 스타일은 [docs/Coding_Convention.md](docs/Coding_Convention.md) 참고.

## 4. 작업 프로세스

### 작업 시작 전 — 항상 먼저 아래를 제시

- **작업 목표**: 이번 작업의 목적
- **작업 계획**:
  - 무엇을 수정하는지
  - 어떤 파일이 변경되는지
  - 기존 코드에 영향이 있는지
  - 위험 요소는 무엇인지

### 작업 완료 후 — 항상 아래를 작성

- **변경사항**: 무엇을 수정했는지
- **영향 범위**: 기존 기능 영향 여부
- **테스트 방법**: 사용자가 어떻게 테스트하면 되는지
- **다음 추천 작업**: 우선순위 높은 작업 제안

## 5. 기존 코드 수정 원칙

- 기존 기능을 함부로 변경하지 않습니다.
- 기존 기능을 수정해야 한다면 먼저 이유를 설명합니다.
- 기존 코드보다 더 좋은 구조일 경우에만 리팩토링합니다.
- 리팩토링 시 기능은 동일하게 유지합니다 (동작 변경 없는 순수 구조 개선).

## 6. 프로젝트 구조 (개요)

**기술 스택 (초안 — 실제 구현 착수 전 확정 필요)**:

- 프론트엔드: Python + Streamlit — SRS는 "Streamlit/Dash 기반"으로 택1을 열어두고 있으며, 블로그
  프로젝트에서 이미 검증된 스택을 재사용하기 위해 **Streamlit을 기본값**으로 채택함. Dash 전환이
  필요해지면 이 문서와 [docs/Architecture.md](docs/Architecture.md)를 함께 갱신할 것
- 백엔드 API: FastAPI — [TrendFit-ux-docs/functional-spec.md](TrendFit-ux-docs/functional-spec.md)에
  정의된 REST 계약(`/api/v1/...`)을 구현
- 배치/스케줄러: APScheduler 또는 Celery(대상 인프라 확정 후 결정) — Spike Score 시간당 재계산, 알림 발송
- DB: Supabase(PostgreSQL) — 블로그 프로젝트에서의 운영 경험 재사용 (2026-08-11 확정)
- 인증: JWT(NFR-SEC-003, 24시간 만료) + 이메일/구글·카카오 소셜 로그인

```
project/
├── Home.py            # Streamlit 진입점 (streamlit run Home.py)
├── pages/              # Streamlit 멀티페이지 (Home.py와 같은 위치 고정)
├── app/                # 프론트 공용 초기화 모듈 (사이드바, session_state 등)
├── api/                # FastAPI 백엔드 — functional-spec.md REST 계약 구현
├── worker/             # 배치 스케줄러 — Spike Score 계산, 알림 발송, 데이터 수집
├── components/         # 재사용 가능한 UI 컴포넌트
├── services/           # 외부 API 연동, 도메인 비즈니스 로직 (app/api/worker 공용)
├── models/             # 데이터 모델, 스키마 (API 요청/응답 계약 포함)
├── utils/              # 공통 유틸 함수
├── config/             # 상수, 임계값, 캐시 TTL, rate limit (매직넘버 금지 → 여기서 관리)
├── assets/             # 정적 리소스
├── data/
│   ├── raw/            # 원본 수집 데이터 (절대 수정 금지)
│   └── processed/       # 전처리된 데이터
├── outputs/            # 분석 스크립트 산출물
├── reports/            # 내부 분석용 사람이 읽는 보고서
├── .streamlit/         # Streamlit 설정 (secrets.toml은 git 제외)
├── docs/               # 개발 규칙 문서 (이 디렉터리)
├── product/            # 서비스 개선 관리 (백로그/체인지로그/KPI 실측)
├── ops/                # 운영 관리 (배포/모니터링/장애 대응)
├── deliverables/        # 산출물 관리 (보고서/회의록/발표자료)
├── TrendFit-ux-docs/    # 요구사항/기능명세/IA 원본 (아래 6-1 참고)
└── tests/              # 테스트 코드
```

레이어 의존 방향: `pages/components`, `api 라우터`, `worker 잡` → `services` → `models/utils`.
`services`는 절대 상위 계층(`app`/`api`/`worker`)을 참조하지 않습니다.

새로운 기능은 **기존 구조를 우선 활용**하고, 비슷한 기능이 존재하면 재사용합니다.
폴더 구조와 데이터 계층 상세 규칙은 [docs/Architecture.md](docs/Architecture.md) 참고.

## 6-1. 요구사항 문서(TrendFit-ux-docs) 취급 원칙

- `TrendFit-ux-docs/*.md`는 기획 단계에서 확정된 원본 명세입니다. 구현 중 명세와 다르게 가는 것이
  낫다고 판단되면, **먼저 왜 다른 결정을 하는지 설명하고 사용자 확인을 받은 뒤** 반영합니다.
- 구현 결과 원본 명세와 실제가 달라지면(API 스펙 변경 등) [docs/API_Design.md](docs/API_Design.md)·
  [docs/Feature_Roadmap.md](docs/Feature_Roadmap.md)에 **실제 구현 기준**을 최신화하고, 원본 명세와의
  차이를 명시합니다. 원본 파일 자체는 변경 이력으로 남기고 함부로 덮어쓰지 않습니다.

## 7. Git 원칙

- 이 폴더는 아직 Git 저장소로 초기화되어 있지 않습니다. 초기화가 필요하면 먼저 사용자에게 확인합니다.
- Git 관리 파일은 새 파일을 만들지 않고 기존 파일을 수정합니다.
- 큰 구조 변경만 별도 브랜치에서 진행합니다.

## 8. 문서화

- 새로운 기능이 추가되면 관련 `docs/` 문서를 함께 수정합니다.
- 서비스 우선순위/일정 변경은 `product/`, 운영 이슈는 `ops/`, 실제 산출물은 `deliverables/`에 기록합니다.
- README가 필요한 경우 갱신합니다.

## 9. 가장 중요한 원칙

이 프로젝트는 **단기 프로젝트가 아닙니다.**
항상 확장 가능한 구조, 재사용 가능한 코드, 유지보수 가능한 설계를 우선합니다.
**기능 구현보다 구조를 먼저 고민합니다.**
