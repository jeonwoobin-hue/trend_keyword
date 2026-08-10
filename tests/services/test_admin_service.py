"""services/admin_service.py 단위 테스트 (SRS FR-ADMIN-001/002)."""

import pytest

from config.constants import (
    ADMIN_KEYWORD_STAT_TOP_N,
    ADMIN_MOCK_REPORT_COUNT,
    ADMIN_MOCK_USER_COUNT,
    CATEGORIES,
    EXTERNAL_DATA_SOURCES,
    MAX_BLACKLIST_KEYWORD_LENGTH,
)
from services.admin_service import (
    BlacklistValidationError,
    add_blacklisted_keyword,
    list_admin_users,
    list_content_reports,
    list_data_source_statuses,
    list_keyword_stats,
    remove_blacklisted_keyword,
    run_spike_batch_recalculation,
)
from services.dashboard_service import get_dashboard_keywords


def test_list_data_source_statuses_covers_all_configured_sources():
    statuses = list_data_source_statuses()

    assert len(statuses) == len(EXTERNAL_DATA_SOURCES)
    assert all(status.status == "not_integrated" for status in statuses)
    assert {s.source_id for s in statuses} == {source_id for source_id, _ in EXTERNAL_DATA_SOURCES}


def test_run_spike_batch_recalculation_counts_all_mock_keywords():
    expected_total = sum(
        len(get_dashboard_keywords(category=category, period="1w").keywords) for category, _ in CATEGORIES
    )

    result = run_spike_batch_recalculation()

    assert result.updated_keyword_count == expected_total
    assert result.failed_keyword_count == 0
    assert result.last_run_at is not None


def test_list_admin_users_returns_configured_count_and_unique_ids():
    users = list_admin_users()

    assert len(users) == ADMIN_MOCK_USER_COUNT
    assert len({u.user_id for u in users}) == ADMIN_MOCK_USER_COUNT
    assert all(not u.is_suspended for u in users)


def test_list_keyword_stats_respects_top_n():
    stats = list_keyword_stats()
    assert len(stats) == ADMIN_KEYWORD_STAT_TOP_N
    assert all(stat.registered_count > 0 for stat in stats)


def test_list_content_reports_respects_configured_count():
    reports = list_content_reports()
    assert len(reports) == ADMIN_MOCK_REPORT_COUNT
    assert len({r.report_id for r in reports}) == ADMIN_MOCK_REPORT_COUNT


def test_add_blacklisted_keyword_success():
    result = add_blacklisted_keyword([], "금지어")
    assert result == ["금지어"]


def test_add_blacklisted_keyword_empty_raises_valid_001():
    with pytest.raises(BlacklistValidationError) as exc_info:
        add_blacklisted_keyword([], "   ")
    assert exc_info.value.code == "VALID_001"


def test_add_blacklisted_keyword_too_long_raises_valid_002():
    too_long = "가" * (MAX_BLACKLIST_KEYWORD_LENGTH + 1)
    with pytest.raises(BlacklistValidationError) as exc_info:
        add_blacklisted_keyword([], too_long)
    assert exc_info.value.code == "VALID_002"


def test_add_blacklisted_keyword_duplicate_raises_valid_003():
    with pytest.raises(BlacklistValidationError) as exc_info:
        add_blacklisted_keyword(["금지어"], "금지어")
    assert exc_info.value.code == "VALID_003"


def test_remove_blacklisted_keyword_filters_target_only():
    result = remove_blacklisted_keyword(["금지어A", "금지어B"], "금지어A")
    assert result == ["금지어B"]
