"""Spike Score(급상승 지수) 산출 로직 (SRS FR-DASH-003).

정의·계산식은 [docs/KPI_Definitions.md](../docs/KPI_Definitions.md),
[TrendFit-ux-docs/functional-spec.md](../TrendFit-ux-docs/functional-spec.md) FR-DASH-003
처리 로직 4단계 기준 — "(당일 언급량 − lookbackWindow 이동평균) ÷ lookbackWindow 표준편차"를
0~100 스케일로 정규화한다.

실제 매시간 배치(worker/jobs)와 관리자 수동 재계산(ADMIN-001)은 아직 없다 — 이 모듈은 그 배치가
호출할 "산출 공식" 자체이며, 지금은 `services/dashboard_service.py`가 목(mock) 언급량 시계열에
바로 적용해 화면에 보여준다. 실제 배치가 붙을 때 이 함수는 그대로 재사용하면 된다.
"""

import math
import statistics


def calculate_spike_score(mention_counts: list[int]) -> float:
    """언급량 시계열(오래된 순, 마지막 값이 "당일")로 Spike Score(0~100)를 계산한다.

    "당일 언급량"은 시계열의 마지막 값, lookback 구간은 그 이전 나머지 전부다. z-score
    `(당일 − 이동평균) ÷ 표준편차`를 시그모이드로 0~100에 정규화한다(z=0 → 50점, 평상시보다
    급증할수록 100에 가까워짐) — functional-spec.md는 "0~100 스케일로 정규화"만 명시하고 구체적인
    정규화 함수는 정하지 않아, 이 프로젝트에서 시그모이드로 확정했다(docs/KPI_Definitions.md
    변경 이력 참고).

    Raises:
        ValueError: 데이터 포인트가 2개 미만(당일 + lookback 최소 1개)인 경우.

    Returns:
        표준편차가 0이면 0.0(KPI_Definitions.md 명시 엣지 케이스 — 에러 아님).
    """
    if len(mention_counts) < 2:
        raise ValueError("Spike Score 계산에는 당일 값 포함 최소 2개의 데이터 포인트가 필요합니다.")

    today = mention_counts[-1]
    lookback_window = mention_counts[:-1]

    mean = statistics.mean(lookback_window)
    stdev = statistics.pstdev(lookback_window)

    if stdev == 0:
        return 0.0

    z_score = (today - mean) / stdev
    return round(100 / (1 + math.exp(-z_score)), 1)
