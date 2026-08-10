"""services/alert_service.py 단위 테스트 (functional-spec FR-ALERT-001/003)."""

import pytest

from config.constants import ALERT_HISTORY_MAX_EVENTS_PER_KEYWORD, MAX_ALERT_KEYWORD_LENGTH, MAX_ALERT_KEYWORDS
from services.alert_service import AlertValidationError, generate_alert_history, register_alert, remove_alert


def test_register_alert_success():
    rule = register_alert([], "저비용항공 특가", 70, ["inapp"])

    assert rule.keyword == "저비용항공 특가"
    assert rule.threshold_score == 70
    assert rule.notify_channels == ["inapp"]
    assert rule.alert_id.startswith("alert_")


def test_register_alert_strips_whitespace():
    rule = register_alert([], "  키워드  ", 70, ["inapp"])
    assert rule.keyword == "키워드"


def test_register_alert_empty_keyword_raises_valid_001():
    with pytest.raises(AlertValidationError) as exc_info:
        register_alert([], "   ", 70, ["inapp"])
    assert exc_info.value.code == "VALID_001"


def test_register_alert_keyword_too_long_raises_valid_002():
    too_long = "가" * (MAX_ALERT_KEYWORD_LENGTH + 1)
    with pytest.raises(AlertValidationError) as exc_info:
        register_alert([], too_long, 70, ["inapp"])
    assert exc_info.value.code == "VALID_002"


def test_register_alert_no_channel_raises_valid_001():
    with pytest.raises(AlertValidationError) as exc_info:
        register_alert([], "키워드", 70, [])
    assert exc_info.value.code == "VALID_001"


def test_register_alert_duplicate_raises_valid_003():
    existing = [register_alert([], "키워드", 70, ["inapp"])]

    with pytest.raises(AlertValidationError) as exc_info:
        register_alert(existing, "키워드", 80, ["email"])
    assert exc_info.value.code == "VALID_003"


def test_register_alert_max_keywords_raises_valid_003():
    existing = []
    for i in range(MAX_ALERT_KEYWORDS):
        existing.append(register_alert(existing, f"키워드{i}", 70, ["inapp"]))

    with pytest.raises(AlertValidationError) as exc_info:
        register_alert(existing, "초과 키워드", 70, ["inapp"])
    assert exc_info.value.code == "VALID_003"


def test_remove_alert_filters_target_only():
    rule_a = register_alert([], "키워드A", 70, ["inapp"])
    rule_b = register_alert([rule_a], "키워드B", 70, ["inapp"])

    remaining = remove_alert([rule_a, rule_b], rule_a.alert_id)

    assert remaining == [rule_b]


def test_generate_alert_history_empty_when_no_rules():
    assert generate_alert_history([]) == []


def test_generate_alert_history_only_for_registered_keywords():
    rule = register_alert([], "저비용항공 특가", 70, ["inapp"])

    history = generate_alert_history([rule])

    assert history
    assert all(entry.keyword == "저비용항공 특가" for entry in history)
    assert all(entry.channel in rule.notify_channels for entry in history)
    assert all(rule.threshold_score <= entry.spike_score <= 100 for entry in history)
    assert len(history) <= ALERT_HISTORY_MAX_EVENTS_PER_KEYWORD


def test_generate_alert_history_sorted_by_sent_at_desc():
    rule_a = register_alert([], "키워드A", 70, ["inapp"])
    rule_b = register_alert([rule_a], "키워드B", 70, ["inapp"])

    history = generate_alert_history([rule_a, rule_b])
    sent_ats = [entry.sent_at for entry in history]

    assert sent_ats == sorted(sent_ats, reverse=True)


def test_generate_alert_history_is_deterministic():
    rule = register_alert([], "키워드", 70, ["inapp"])

    first = generate_alert_history([rule])
    second = generate_alert_history([rule])

    assert [e.alert_history_id for e in first] == [e.alert_history_id for e in second]
    assert [e.spike_score for e in first] == [e.spike_score for e in second]
    assert [e.status for e in first] == [e.status for e in second]


def test_generate_alert_history_defaults_unread():
    rule = register_alert([], "키워드", 70, ["inapp"])
    history = generate_alert_history([rule])

    assert all(not entry.is_read for entry in history)
