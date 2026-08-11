"""콘텐츠 큐레이션 조회 및 스크랩 도메인 로직 (functional-spec FR-CURATE-001, SRS FR-CURATE-003).

실제 외부 콘텐츠 연동(유튜브/인스타그램/뉴스/X API 등)이 붙기 전까지, 이 모듈은
커서 기반 페이지네이션 계약과 동일한 형태의 목(mock) 데이터를 생성한다. 실제 연동 시
`get_curated_contents()` 내부만 교체하고 시그니처/반환 타입(`CurationResult`)은 유지한다.
스크랩 목록은 실제 DB가 붙기 전까지 호출부(현재는 `st.session_state`)가 들고 있고,
이 모듈은 추가/제거 순수 로직만 담당한다.
"""

from datetime import datetime, timedelta, timezone

from config.constants import (
    CONTENT_RELATED_KEYWORDS_TOP_N,
    CURATION_PAGE_SIZE,
    CURATION_PLATFORMS,
    CURATION_TOTAL_MOCK_ITEMS,
)
from models.curation import ContentDetail, ContentItem, CurationResult

_TITLE_TEMPLATES = [
    "{topic} 총정리",
    "요즘 화제인 {topic}, 직접 살펴봤습니다",
    "{topic} 관련 뉴스 모음",
    "이번 주 {topic} 트렌드 브리핑",
    "{topic} 추천 콘텐츠 TOP 5",
]

_SOURCE_LABELS = dict(CURATION_PLATFORMS)
_DEFAULT_TOPIC = "관심 키워드"

# 이 배수번째 항목마다 원문이 삭제된 상태(RES_003)로 표시해 예외 UX를 시연한다.
_UNAVAILABLE_EVERY_N = 7

# 콘텐츠 상세(CURATE-002)의 연관 키워드 태그를 만드는 접미사 목록.
_RELATED_KEYWORD_SUFFIXES = ["최신 소식", "추천", "리뷰 모음", "비교"]


def get_curated_contents(
    keyword: str | None, cursor: str | None, platforms: list[str] | None = None
) -> CurationResult:
    """키워드(선택)·플랫폼(선택) 조건에 맞는 콘텐츠를 커서 기준으로 `CURATION_PAGE_SIZE`개씩 반환한다.

    Args:
        keyword: 특정 키워드 경유 진입 시 해당 키워드. 없으면 일반 피드.
        cursor: 이전 응답의 `next_cursor`. 없으면 첫 페이지.
        platforms: 필터링할 플랫폼 값 목록(`CURATION_PLATFORMS` 참고). 없거나 빈 리스트면 전체.
    """
    topic = keyword or _DEFAULT_TOPIC
    offset = int(cursor) if cursor else 0

    pool = _build_mock_pool(topic)
    if platforms:
        pool = [item for item in pool if item.platform in platforms]

    page = pool[offset : offset + CURATION_PAGE_SIZE]
    next_offset = offset + CURATION_PAGE_SIZE
    next_cursor = str(next_offset) if next_offset < len(pool) else None

    return CurationResult(contents=page, next_cursor=next_cursor)


def get_content_detail(content_id: str, keyword: str | None) -> ContentDetail | None:
    """콘텐츠 1건의 상세(CURATE-002)를 조회한다. 없으면 `None`(RES_001).

    Args:
        content_id: 조회할 콘텐츠 ID.
        keyword: 해당 콘텐츠가 속한 피드의 키워드 조건(`get_curated_contents()`와 동일한 값).
            일반 피드에서 진입했다면 `None`.
    """
    topic = keyword or _DEFAULT_TOPIC
    item = next((item for item in _build_mock_pool(topic) if item.content_id == content_id), None)
    if item is None:
        return None

    return ContentDetail(
        content_id=item.content_id,
        title=item.title,
        thumbnail=item.thumbnail,
        source=item.source,
        platform=item.platform,
        published_at=item.published_at,
        url=item.url,
        is_available=item.is_available,
        related_keywords=_build_related_keywords(topic),
    )


def add_scrap(existing: list[ContentItem], content: ContentItem) -> list[ContentItem]:
    """콘텐츠를 스크랩 목록에 추가한다 (FR-CURATE-003). 이미 있으면 그대로 반환한다."""
    if any(item.content_id == content.content_id for item in existing):
        return existing
    return [*existing, content]


def remove_scrap(existing: list[ContentItem], content_id: str) -> list[ContentItem]:
    """스크랩 목록에서 콘텐츠를 제거한다."""
    return [item for item in existing if item.content_id != content_id]


def _build_related_keywords(topic: str) -> list[str]:
    """콘텐츠 상세(CURATE-002)의 연관 키워드 태그를 주제 기반으로 생성한다."""
    return [f"{topic} {suffix}" for suffix in _RELATED_KEYWORD_SUFFIXES[:CONTENT_RELATED_KEYWORDS_TOP_N]]


def _build_mock_pool(topic: str) -> list[ContentItem]:
    """주제별로 안정적인(재실행해도 동일한) 콘텐츠 목록을 생성한다."""
    platforms = [value for value, _ in CURATION_PLATFORMS]

    items = []
    for index in range(CURATION_TOTAL_MOCK_ITEMS):
        platform = platforms[index % len(platforms)]
        template = _TITLE_TEMPLATES[index % len(_TITLE_TEMPLATES)]
        items.append(
            ContentItem(
                content_id=f"content_{topic}_{index}",
                title=template.format(topic=topic),
                thumbnail="",
                source=_SOURCE_LABELS[platform],
                platform=platform,
                published_at=datetime.now(timezone.utc) - timedelta(hours=index * 3),
                url=f"https://example.com/{platform}/{index}",
                is_available=(index % _UNAVAILABLE_EVERY_N != 0),
            )
        )
    return items
