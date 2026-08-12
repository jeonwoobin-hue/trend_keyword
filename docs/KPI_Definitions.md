# KPI_Definitions.md — 핵심 지표 정의 및 변경 이력 관리

> 공통 규칙은 [../CLAUDE.md](../CLAUDE.md) 참고. 지표를 코드/화면/AI 응답에서 언급할 때는 반드시 이 문서의
> 명칭·계산식과 일치시킵니다([Prompt_Guide.md](Prompt_Guide.md) 참고). 원본 정의는
> [../TrendFit-ux-docs/functional-spec.md](../TrendFit-ux-docs/functional-spec.md) FR-DASH-003 참고.

## Spike Score (급상승 지수)

- **정의**: 키워드의 검색량·언급량이 평상시 대비 급증한 정도를 0~100으로 정규화한 지수
- **계산식**: `(당일 언급량 − lookbackWindow 이동평균) ÷ lookbackWindow 표준편차`(z-score)를
  시그모이드(`100 / (1 + e^-z)`)로 0~100에 정규화. z=0(평상시와 동일)이면 50점, 급증할수록
  100에, 급감할수록 0에 가까워짐 — `services/spike_score_service.calculate_spike_score()`로
  구현·검증됨(`tests/services/test_spike_score_service.py`)
- **lookbackWindow**: `7d`(기본값) 또는 `30d` — 배치 요청 시 지정. 지금은 실제 배치 전이라
  `dashboard_service`가 화면에 쓰는 목 언급량 시계열 전체를 그대로 lookback으로 사용(마지막
  포인트가 "당일", 나머지가 lookback)
- **산출 주기**: 매시간 배치(스케줄러) + 관리자 수동 재계산(ADMIN-001) — **배치 워커(worker/jobs)
  자체는 아직 없음**. 지금은 `services/dashboard_service.py`가 대시보드 응답을 만들 때마다
  계산식만 즉시 적용하는 상태(공식은 진짜, 배치 인프라는 목업)
- **엣지 케이스**:
  - 표준편차가 0인 키워드 → Spike Score **0**으로 정상 처리(에러 아님, 결측 아님)
  - 원본 데이터 수집 실패 등 이상치는 필터링 후 결측 처리, 이전 캐시된 점수 유지
- **미정 사항(구현 시 확정 필요)**: "언급량(mentionCount)"이 검색량/소셜 언급/뉴스 언급 중 어떤 소스를
  어떤 비중으로 합산한 값인지는 SRS/기능명세서에 구체적 산식이 없음 — 실제 데이터 소스 연동 시점에
  아래 "변경 이력"에 확정 근거와 함께 기록할 것

## 감성 분석 비율

- **정의**: 특정 키워드와 관련된 게시물·기사의 긍정/부정/중립 여론 비율 (`positive + negative + neutral = 1`)
- **데이터 소스/모델**: 미정 — 실제 감성분석 모델/API 연동 시 이 항목에 기록
- **표시 조건**: 언급량이 충분하지 않은 신규 키워드는 "감성 분석을 위한 데이터가 충분하지 않습니다"
  (`VALID_003`)로 안내하고 해당 영역을 비활성화(FR-DASH-004 예외처리 참고)

## 연령·성별 관심도 가중치 보정 (DASH-002, FR-DASH-005, P2)

- **정의**: 원본 관심도 데이터에 연령/성별 특성을 반영해 보정한 값. 연령대별·성별별 비중의 합은 각각 1.0
- **산정 방법(목 데이터 기준)**: 연령대(`AGE_GROUP_OPTIONS` 6구간)·성별(남/여) 그룹마다 무작위 값을
  생성해 정규화 (`services/dashboard_service.py`의 `_build_demographic_weights`)
- **미정 사항**: 실제 가중치 산식은 데이터 소스(유튜브/X 등) 확보 후 확정 필요. 지금 값은 그룹 간
  상대적 크기 비교 UI를 보여주기 위한 무작위 목 데이터일 뿐, 실제 인구통계 특성을 반영하지 않음

## 연관 키워드 (DASH-002)

- **정의**: 특정 키워드와 동시 언급 빈도가 높은 키워드
- **산정 방법(목 데이터 기준)**: 전체 목 키워드 풀에서 자기 자신을 제외하고 무작위 추출
  (`services/dashboard_service.py`, 상위 `RELATED_KEYWORDS_TOP_N`개). 실제 동시 언급 빈도 계산
  로직은 미정 — 외부 데이터 연동 시 확정할 것

## 유사 관심사 비교 추천 키워드 (REPORT-002, FR-REPORT-005)

- **정의**: 관심 분야와 유사한 분야 그룹의 데이터를 비교하여 도출한 추가 추천 키워드
- **산정 방법(목 데이터 기준)**: `config/constants.py`의 `SIMILAR_CATEGORIES`에 정의된 고정
  분야 매핑(예: 패션↔뷰티↔리빙, IT테크↔자동차↔경제/비즈니스, 방송/연예↔대중음악↔영화)에서
  Spike Score 상위 `SIMILAR_GROUP_KEYWORDS_TOP_N`개를 추천 (`services/report_service.py`의
  `_build_similar_group_keywords`)
- **미정 사항**: 지금의 분야 매핑은 실제 사용자 행동 데이터 없이 임의로 정한 고정값이다. 실제
  유사도는 사용자 행동/코호트 데이터 기반 클러스터링으로 재계산해야 하며, 확정 시 이 항목과
  `config.SIMILAR_CATEGORIES`를 함께 갱신할 것

## 변경 이력

| 날짜 | 변경 내용 | 근거 |
|---|---|---|
| 2026-08-10 | 문서 최초 작성 — functional-spec.md FR-DASH-003 기준 Spike Score 정의, 나머지 지표는 미정으로 표시 | 프로젝트 초기 세팅 |
| 2026-08-11 | 유사 관심사 비교 추천 키워드(FR-REPORT-005) 산정 방법 확정 — 고정 분야 매핑 기반 목 데이터 방식. 연관 키워드(DASH-002)의 기존 목 산정 방식도 함께 명시 | REPORT-002 구현(BL-005) |
| 2026-08-12 | Spike Score의 "0~100 정규화" 방식을 시그모이드(`100/(1+e^-z)`)로 확정 — functional-spec.md는 정규화 함수를 specify하지 않아 직접 결정. `services/spike_score_service.py`로 계산식 실제 구현, `dashboard_service`가 목 언급량 시계열에 적용 | Spike Score 산출 로직 구현 |
| 2026-08-11 | 연령·성별 관심도 가중치 보정(FR-DASH-005) 산정 방법 확정 — 그룹별 무작위 정규화 목 데이터 방식 | DASH-002 구현(BL-003) |
