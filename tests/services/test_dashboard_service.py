"""services/dashboard_service.py 단위 테스트 (functional-spec FR-DASH-001/FR-DASH-004)."""

import pytest

from config.constants import CATEGORIES, CATEGORY_ALL, DASHBOARD_TOP_N, RELATED_KEYWORDS_TOP_N
from services.dashboard_service import get_dashboard_keywords, get_keyword_detail

PERIODS = ["24h", "1w", "1m"]


@pytest.mark.parametrize("period", PERIODS)
def test_get_dashboard_keywords_single_category_returns_only_that_category(period):
    category = CATEGORIES[0][0]

    result = get_dashboard_keywords(category=category, period=period)

    assert result.keywords
    assert all(keyword.category == category for keyword in result.keywords)
    assert result.meta.period == period


def test_get_dashboard_keywords_sorted_by_spike_score_desc():
    result = get_dashboard_keywords(category=CATEGORY_ALL, period="1w")

    scores = [keyword.spike_score for keyword in result.keywords]
    assert scores == sorted(scores, reverse=True)


def test_get_dashboard_keywords_all_categories_capped_at_top_n():
    result = get_dashboard_keywords(category=CATEGORY_ALL, period="1w")
    assert len(result.keywords) == DASHBOARD_TOP_N


def test_get_dashboard_keywords_is_deterministic():
    first = get_dashboard_keywords(category="fashion", period="1w")
    second = get_dashboard_keywords(category="fashion", period="1w")

    assert [k.keyword_id for k in first.keywords] == [k.keyword_id for k in second.keywords]
    assert [k.spike_score for k in first.keywords] == [k.spike_score for k in second.keywords]


def test_get_keyword_detail_unknown_id_returns_none():
    assert get_keyword_detail("no_such_keyword", "1w") is None


def test_get_keyword_detail_known_id_matches_dashboard_entry():
    dashboard = get_dashboard_keywords(category="fashion", period="1w")
    target = dashboard.keywords[0]

    detail = get_keyword_detail(target.keyword_id, "1w")

    assert detail is not None
    assert detail.keyword_id == target.keyword_id
    assert detail.keyword == target.keyword
    assert detail.category == "fashion"
    assert len(detail.related_keywords) == RELATED_KEYWORDS_TOP_N
    assert target.keyword not in detail.related_keywords


def test_get_keyword_detail_sentiment_ratio_sums_to_one_when_present():
    for category, _ in CATEGORIES:
        dashboard = get_dashboard_keywords(category=category, period="1w")
        for keyword in dashboard.keywords:
            detail = get_keyword_detail(keyword.keyword_id, "1w")
            if detail.sentiment is not None:
                total = detail.sentiment.positive + detail.sentiment.negative + detail.sentiment.neutral
                assert total == pytest.approx(1.0, abs=0.02)


def test_get_keyword_detail_is_deterministic():
    dashboard = get_dashboard_keywords(category="fashion", period="1w")
    keyword_id = dashboard.keywords[0].keyword_id

    first = get_keyword_detail(keyword_id, "1w")
    second = get_keyword_detail(keyword_id, "1w")

    assert first.trend_series == second.trend_series
    assert first.sentiment == second.sentiment
    assert first.related_keywords == second.related_keywords
