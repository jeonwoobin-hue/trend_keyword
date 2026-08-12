"""services/spike_score_service.py 단위 테스트 (SRS FR-DASH-003, docs/KPI_Definitions.md)."""

import pytest

from services.spike_score_service import calculate_spike_score


def test_today_equals_average_scores_fifty():
    # lookback 평균과 당일 값이 같으면 z-score 0 → 시그모이드 정규화의 중간값.
    # lookback 자체에 변동이 있어야 표준편차 0(별도 엣지 케이스)과 구분된다.
    assert calculate_spike_score([90, 100, 110, 100]) == 50.0


def test_today_far_above_average_scores_near_hundred():
    score = calculate_spike_score([90, 100, 110, 100, 95, 900])
    assert score > 90


def test_today_far_below_average_scores_near_zero():
    score = calculate_spike_score([890, 900, 910, 900, 905, 100])
    assert score < 10


def test_zero_stdev_returns_zero_not_error():
    # lookback window 전체가 동일한 값이면 표준편차 0 — KPI_Definitions.md 명시 엣지 케이스
    assert calculate_spike_score([500, 500, 500, 999]) == 0.0


def test_score_is_always_within_bounds():
    score = calculate_spike_score([10, 5000, 1, 999999])
    assert 0.0 <= score <= 100.0


def test_result_is_deterministic_for_same_input():
    values = [120, 130, 90, 140, 300]
    assert calculate_spike_score(values) == calculate_spike_score(values)


def test_single_data_point_raises_value_error():
    with pytest.raises(ValueError):
        calculate_spike_score([100])


def test_empty_list_raises_value_error():
    with pytest.raises(ValueError):
        calculate_spike_score([])


def test_higher_relative_spike_scores_higher_than_smaller_spike():
    small_spike = calculate_spike_score([90, 100, 110, 100, 150])
    big_spike = calculate_spike_score([90, 100, 110, 100, 400])
    assert big_spike > small_spike
