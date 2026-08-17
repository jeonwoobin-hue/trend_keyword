"""services/report_service.py 단위 테스트 (functional-spec FR-REPORT-001/002/003)."""

from types import SimpleNamespace

import pytest

from config.constants import (
    MAX_REPORT_TITLE_LENGTH,
    NETWORK_GRAPH_NODE_TOP_N,
    REPORT_RECOMMENDED_KEYWORDS_TOP_N,
    SIMILAR_CATEGORIES,
    SIMILAR_GROUP_KEYWORDS_TOP_N,
)
from services import report_service
from services.dashboard_service import get_dashboard_keywords
from services.gemini_client import GeminiConfigError
from services.report_service import ReportValidationError, generate_report, get_report_by_id


def test_generate_report_sets_category_and_period():
    report = generate_report("fashion", "1w", None)

    assert report.category == "fashion"
    assert report.period == "1w"
    assert report.report_id.startswith("rep_")


def test_generate_report_auto_generates_title_when_blank():
    report = generate_report("fashion", "1w", "")
    assert "패션" in report.title
    assert "1w" in report.title


def test_generate_report_uses_explicit_title():
    report = generate_report("fashion", "1w", "나만의 제목")
    assert report.title == "나만의 제목"


def test_generate_report_title_too_long_raises_valid_002():
    too_long = "가" * (MAX_REPORT_TITLE_LENGTH + 1)

    with pytest.raises(ReportValidationError) as exc_info:
        generate_report("fashion", "1w", too_long)
    assert exc_info.value.code == "VALID_002"


def test_generate_report_word_cloud_weights_within_unit_range():
    report = generate_report("fashion", "1w", None)

    assert report.word_cloud
    assert all(0 < item.weight <= 1.0 for item in report.word_cloud)
    assert max(item.weight for item in report.word_cloud) == 1.0


def test_generate_report_network_graph_forms_connected_tree():
    dashboard = get_dashboard_keywords(category="fashion", period="1w")
    expected_node_count = min(NETWORK_GRAPH_NODE_TOP_N, len(dashboard.keywords))

    report = generate_report("fashion", "1w", None)

    assert len(report.network_graph.nodes) == expected_node_count
    assert len(report.network_graph.edges) == expected_node_count - 1


def test_generate_report_recommended_keywords_respects_top_n():
    report = generate_report("fashion", "1w", None)
    dashboard = get_dashboard_keywords(category="fashion", period="1w")
    expected_len = min(REPORT_RECOMMENDED_KEYWORDS_TOP_N, len(dashboard.keywords))

    assert len(report.recommended_keywords) == expected_len


def test_generate_report_word_cloud_and_network_graph_are_deterministic():
    first = generate_report("fashion", "1w", None)
    second = generate_report("fashion", "1w", None)

    assert first.word_cloud == second.word_cloud
    assert first.network_graph == second.network_graph


def test_get_report_by_id_finds_matching_report():
    report = generate_report("fashion", "1w", None)
    other = generate_report("travel", "1w", None)

    found = get_report_by_id([report, other], report.report_id)

    assert found is not None
    assert found.report_id == report.report_id


def test_get_report_by_id_returns_none_when_missing():
    report = generate_report("fashion", "1w", None)

    assert get_report_by_id([report], "no_such_id") is None


def test_generate_report_similar_group_keywords_come_from_similar_categories():
    report = generate_report("fashion", "1w", None)

    similar_categories = SIMILAR_CATEGORIES["fashion"]
    candidate_keywords = {
        keyword.keyword
        for category in similar_categories
        for keyword in get_dashboard_keywords(category=category, period="1w").keywords
    }

    assert report.similar_group_keywords
    assert len(report.similar_group_keywords) <= SIMILAR_GROUP_KEYWORDS_TOP_N
    # 유사 그룹(beauty/travel)에서만 추천되고, 리포트 자체 분야(fashion)는 섞이지 않아야 한다.
    assert all(kw in candidate_keywords for kw in report.similar_group_keywords)


def test_generate_report_similar_group_keywords_is_deterministic():
    first = generate_report("fashion", "1w", None)
    second = generate_report("fashion", "1w", None)

    assert first.similar_group_keywords == second.similar_group_keywords


def _fake_gemini_client(summary_text: str):
    def generate_content(model, contents):
        return SimpleNamespace(text=summary_text)

    return SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))


def test_generate_report_uses_ai_summary_when_gemini_available(monkeypatch):
    monkeypatch.setattr(
        report_service, "create_gemini_client", lambda: _fake_gemini_client("AI가 생성한 이슈 요약입니다.")
    )

    report = generate_report("fashion", "1w", None)

    assert report.summary == "AI가 생성한 이슈 요약입니다."


def test_generate_report_falls_back_to_template_when_gemini_raises_config_error(monkeypatch):
    def _raise():
        raise GeminiConfigError("키 없음")

    monkeypatch.setattr(report_service, "create_gemini_client", _raise)

    report = generate_report("fashion", "1w", None)

    dashboard = get_dashboard_keywords(category="fashion", period="1w")
    top_names = ", ".join(k.keyword for k in dashboard.keywords[:3])
    assert report.summary == report_service._build_fallback_summary("패션", dashboard.keywords)
    assert top_names in report.summary


def test_generate_report_falls_back_to_template_when_gemini_returns_empty_text(monkeypatch):
    monkeypatch.setattr(report_service, "create_gemini_client", lambda: _fake_gemini_client("  "))

    report = generate_report("fashion", "1w", None)

    dashboard = get_dashboard_keywords(category="fashion", period="1w")
    assert report.summary == report_service._build_fallback_summary("패션", dashboard.keywords)


def test_summary_prompt_includes_keyword_names_and_period_as_grounding():
    dashboard = get_dashboard_keywords(category="fashion", period="1w")

    prompt = report_service._build_summary_prompt("패션", dashboard.keywords, "1w")

    assert dashboard.keywords[0].keyword in prompt
    assert "최근 1주일" in prompt
