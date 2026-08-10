"""services/profile_service.py 단위 테스트 (functional-spec FR-ONBOARD-001)."""

import pytest

from config.constants import MAX_INTERESTS, PREVIEW_KEYWORDS_TOP_N
from services.dashboard_service import get_dashboard_keywords
from services.profile_service import ProfileValidationError, build_preview_keywords, register_interest_profile


def test_register_interest_profile_success():
    profile = register_interest_profile(
        interests=["fashion", "travel"],
        purpose="content_planning",
        age_group="20s",
        gender="female",
        platforms=["instagram", "youtube"],
        period="1w",
    )

    assert profile.interests == ["fashion", "travel"]
    assert profile.purpose == "content_planning"
    assert profile.age_group == "20s"
    assert profile.gender == "female"
    assert profile.platforms == ["instagram", "youtube"]
    assert profile.period == "1w"


def test_register_interest_profile_no_interests_raises_valid_001():
    with pytest.raises(ProfileValidationError) as exc_info:
        register_interest_profile([], "casual", "20s", None, ["news"], "24h")
    assert exc_info.value.code == "VALID_001"


def test_register_interest_profile_too_many_interests_raises_valid_002():
    too_many = [f"interest_{i}" for i in range(MAX_INTERESTS + 1)]

    with pytest.raises(ProfileValidationError) as exc_info:
        register_interest_profile(too_many, "casual", "20s", None, ["news"], "24h")
    assert exc_info.value.code == "VALID_002"


def test_register_interest_profile_no_platforms_raises_valid_001():
    with pytest.raises(ProfileValidationError) as exc_info:
        register_interest_profile(["fashion"], "casual", "20s", None, [], "24h")
    assert exc_info.value.code == "VALID_001"


def test_build_preview_keywords_single_interest_matches_top_dashboard_keywords():
    dashboard = get_dashboard_keywords(category="fashion", period="1w")
    expected = [keyword.keyword for keyword in dashboard.keywords[:PREVIEW_KEYWORDS_TOP_N]]

    preview = build_preview_keywords(["fashion"], "1w")

    assert preview == expected


def test_build_preview_keywords_respects_top_n():
    preview = build_preview_keywords(["fashion", "travel", "it_tech"], "1w")
    assert len(preview) == PREVIEW_KEYWORDS_TOP_N
