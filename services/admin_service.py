"""관리자 도메인 로직 (SRS FR-ADMIN-001/002, functional-spec FR-DASH-003).

외부 데이터 연동은 API_Design.md §8 기준 전부 미구현이므로, `list_data_source_statuses()`는
가짜 호출량을 만들어내지 않고 실제 미구현 상태를 그대로 반환한다. Spike Score 배치는
`dashboard_service`의 목 데이터를 기준으로 재계산 결과를 시뮬레이션한다.

사용자·키워드 관리(ADMIN-002)는 실제 다중 사용자 DB 연동 전 단계라, 사용자 목록/키워드 통계/
신고 내역을 결정론적 목(mock) 데이터로 생성한다. 키워드 블랙리스트는 실제 DB 없이도 정직하게
구현 가능해 진짜 CRUD(빈 목록에서 시작, 직접 추가/삭제)로 두었다.
"""

import random
from datetime import datetime, timedelta, timezone

from config.constants import (
    ADMIN_KEYWORD_STAT_TOP_N,
    ADMIN_MOCK_REPORT_COUNT,
    ADMIN_MOCK_USER_COUNT,
    CATEGORIES,
    CATEGORY_ALL,
    EXTERNAL_DATA_SOURCES,
    MAX_BLACKLIST_KEYWORD_LENGTH,
)
from models.admin import AdminUser, ContentReport, DataSourceStatus, KeywordStat, SpikeBatchStatus
from services.dashboard_service import get_dashboard_keywords

_REPORT_REASONS = ["스팸/광고", "욕설·비방", "저작권 침해 의심", "허위 정보"]


class BlacklistValidationError(Exception):
    """블랙리스트 등록 실패 시 사용자 메시지를 함께 담는 예외 (API_Design.md §3 기준)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def list_data_source_statuses() -> list[DataSourceStatus]:
    """외부 데이터 소스별 연동 상태를 조회한다."""
    return [
        DataSourceStatus(source_id=source_id, source_label=label, status="not_integrated")
        for source_id, label in EXTERNAL_DATA_SOURCES
    ]


def run_spike_batch_recalculation() -> SpikeBatchStatus:
    """Spike Score 배치를 (모의로) 재실행하고 결과를 반환한다."""
    updated_count = sum(
        len(get_dashboard_keywords(category=category, period="1w").keywords) for category, _ in CATEGORIES
    )
    return SpikeBatchStatus(
        last_run_at=datetime.now(timezone.utc),
        updated_keyword_count=updated_count,
        failed_keyword_count=0,
    )


def list_admin_users() -> list[AdminUser]:
    """샘플 사용자 목록을 조회한다 (실제 다중 사용자 DB 연동 전 단계)."""
    rng = random.Random("admin:users")
    return [
        AdminUser(
            user_id=f"user_{index:03d}",
            email=f"user{index:03d}@example.com",
            joined_at=datetime.now(timezone.utc) - timedelta(days=rng.randint(1, 365)),
        )
        for index in range(1, ADMIN_MOCK_USER_COUNT + 1)
    ]


def list_keyword_stats() -> list[KeywordStat]:
    """샘플 등록 키워드 통계를 조회한다 (기존 대시보드 목 키워드를 재사용)."""
    rng = random.Random("admin:keyword_stats")
    keywords = get_dashboard_keywords(category=CATEGORY_ALL, period="1w").keywords[:ADMIN_KEYWORD_STAT_TOP_N]
    return [
        KeywordStat(keyword=keyword.keyword, registered_count=rng.randint(5, 300)) for keyword in keywords
    ]


def list_content_reports() -> list[ContentReport]:
    """샘플 콘텐츠 신고 내역을 조회한다."""
    rng = random.Random("admin:content_reports")
    keywords = get_dashboard_keywords(category=CATEGORY_ALL, period="1w").keywords[:ADMIN_MOCK_REPORT_COUNT]
    return [
        ContentReport(
            report_id=f"report_{index}",
            content_title=f"{keyword.keyword} 관련 게시물",
            reason=rng.choice(_REPORT_REASONS),
            reported_at=datetime.now(timezone.utc) - timedelta(hours=index * 5 + 1),
        )
        for index, keyword in enumerate(keywords)
    ]


def add_blacklisted_keyword(existing: list[str], keyword: str) -> list[str]:
    """키워드 블랙리스트에 새 항목을 추가한다.

    Raises:
        BlacklistValidationError: 필수값 누락, 길이 초과, 중복 등록 시.
    """
    normalized = keyword.strip()

    if not normalized:
        raise BlacklistValidationError("VALID_001", "키워드를 입력해주세요.")
    if len(normalized) > MAX_BLACKLIST_KEYWORD_LENGTH:
        raise BlacklistValidationError(
            "VALID_002", f"키워드는 최대 {MAX_BLACKLIST_KEYWORD_LENGTH}자까지 입력할 수 있습니다."
        )
    if normalized in existing:
        raise BlacklistValidationError("VALID_003", "이미 블랙리스트에 등록된 키워드입니다.")

    return [*existing, normalized]


def remove_blacklisted_keyword(existing: list[str], keyword: str) -> list[str]:
    """키워드 블랙리스트에서 항목을 제거한다."""
    return [item for item in existing if item != keyword]
