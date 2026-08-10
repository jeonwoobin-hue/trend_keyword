"""관심사 프로필 등록 도메인 로직 (functional-spec FR-ONBOARD-001).

실제 DB 연동 전까지 프로필은 호출부(현재는 `st.session_state`)가 들고 있고,
이 모듈은 검증 규칙과 추천 키워드 미리보기 산출 로직만 담당한다.
"""

from config.constants import MAX_INTERESTS, MIN_INTERESTS, PREVIEW_KEYWORDS_TOP_N
from models.profile import InterestProfile
from services.dashboard_service import get_dashboard_keywords


class ProfileValidationError(Exception):
    """등록 실패 시 사용자 메시지를 함께 담는 예외 (API_Design.md §3 공통 에러 코드 기준)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def register_interest_profile(
    interests: list[str],
    purpose: str,
    age_group: str,
    gender: str | None,
    platforms: list[str],
    period: str,
) -> InterestProfile:
    """관심사 프로필을 검증 후 생성한다.

    Raises:
        ProfileValidationError: 관심 분야·선호 플랫폼 미선택 또는 개수 제한 위반 시.
    """
    if not interests:
        raise ProfileValidationError("VALID_001", "관심 분야를 1개 이상 선택해주세요.")
    if not (MIN_INTERESTS <= len(interests) <= MAX_INTERESTS):
        raise ProfileValidationError("VALID_002", f"관심 분야는 최대 {MAX_INTERESTS}개까지 선택할 수 있습니다.")
    if not platforms:
        raise ProfileValidationError("VALID_001", "선호 플랫폼을 1개 이상 선택해주세요.")

    return InterestProfile(
        interests=interests,
        purpose=purpose,
        age_group=age_group,
        gender=gender,
        platforms=platforms,
        period=period,
    )


def build_preview_keywords(interests: list[str], period: str) -> list[str]:
    """선택한 관심 분야 기준 추천 키워드 상위 `PREVIEW_KEYWORDS_TOP_N`개를 산출한다."""
    candidates = [
        keyword
        for interest in interests
        for keyword in get_dashboard_keywords(category=interest, period=period).keywords
    ]
    candidates.sort(key=lambda item: item.spike_score, reverse=True)
    return [item.keyword for item in candidates[:PREVIEW_KEYWORDS_TOP_N]]
