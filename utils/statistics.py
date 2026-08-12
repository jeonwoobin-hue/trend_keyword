"""특정 도메인에 종속되지 않는 공통 통계 유틸."""

import statistics


def pearson_correlation(series_a: list[float], series_b: list[float]) -> float:
    """두 시계열의 피어슨 상관계수를 계산한다(-1~1, 1에 가까울수록 함께 움직임).

    Raises:
        ValueError: 두 시계열의 길이가 다르거나, 포인트가 2개 미만인 경우.

    Returns:
        어느 한쪽이라도 표준편차가 0(값이 전부 동일)이면 상관관계를 정의할 수 없어 0.0으로
        처리한다(에러 아님 — services/spike_score_service.calculate_spike_score()의 표준편차 0
        처리와 같은 관례).
    """
    if len(series_a) != len(series_b):
        raise ValueError("두 시계열의 길이가 같아야 상관계수를 계산할 수 있습니다.")
    if len(series_a) < 2:
        raise ValueError("상관계수 계산에는 최소 2개 이상의 데이터 포인트가 필요합니다.")

    stdev_a = statistics.pstdev(series_a)
    stdev_b = statistics.pstdev(series_b)
    if stdev_a == 0 or stdev_b == 0:
        return 0.0

    mean_a = statistics.mean(series_a)
    mean_b = statistics.mean(series_b)
    covariance = sum((a - mean_a) * (b - mean_b) for a, b in zip(series_a, series_b)) / len(series_a)
    return covariance / (stdev_a * stdev_b)
