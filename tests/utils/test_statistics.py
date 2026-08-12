"""utils/statistics.py 단위 테스트."""

import pytest

from utils.statistics import pearson_correlation


def test_identical_series_are_perfectly_correlated():
    series = [10, 20, 15, 30, 25]
    assert pearson_correlation(series, series) == pytest.approx(1.0)


def test_inverted_series_are_perfectly_negatively_correlated():
    series_a = [10, 20, 15, 30, 25]
    series_b = [-value for value in series_a]
    assert pearson_correlation(series_a, series_b) == pytest.approx(-1.0)


def test_linear_scale_does_not_change_correlation():
    series_a = [10, 20, 15, 30, 25]
    series_b = [value * 3 + 7 for value in series_a]
    assert pearson_correlation(series_a, series_b) == pytest.approx(1.0)


def test_zero_variance_series_returns_zero_not_error():
    assert pearson_correlation([100, 100, 100], [1, 5, 3]) == 0.0


def test_mismatched_lengths_raise_value_error():
    with pytest.raises(ValueError):
        pearson_correlation([1, 2, 3], [1, 2])


def test_single_point_raises_value_error():
    with pytest.raises(ValueError):
        pearson_correlation([1], [1])


def test_result_is_deterministic_for_same_input():
    series_a = [3, 7, 2, 9, 5]
    series_b = [4, 8, 1, 10, 6]
    assert pearson_correlation(series_a, series_b) == pearson_correlation(series_a, series_b)


def test_unrelated_series_have_low_magnitude_correlation():
    # 서로 무관하게 번갈아 움직이는 시계열은 상관계수가 강한 양/음 상관(±1에 근접)이 아니어야 한다.
    series_a = [10, 20, 10, 20, 10, 20]
    series_b = [15, 15, 25, 25, 15, 15]
    assert abs(pearson_correlation(series_a, series_b)) < 0.5
