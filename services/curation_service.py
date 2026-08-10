"""콘텐츠 큐레이션 조회 도메인 로직 (functional-spec FR-CURATE-001).

실제 외부 콘텐츠 연동(유튜브/인스타그램/뉴스/X API 등)이 붙기 전까지, 이 모듈은
커서 기반 페이지네이션 계약과 동일한 형태의 목(mock) 데이터를 생성한다. 실제 연동 시
`get_curated_contents()` 내부만 교체하고 시그니처/반환 타입(`CurationResult`)은 유지한다.
"""

from datetime import datetime, timedelta, timezone

from config.constants import CURATION_PAGE_SIZE, CURATION_PLATFORMS, CURATION_TOTAL_MOCK_ITEMS
from models.curation import ContentItem, CurationResult

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


def get_curated_contents(keyword: str | None, cursor: str | None) -> CurationResult:
    """키워드(선택) 관련 콘텐츠를 커서 기준으로 `CURATION_PAGE_SIZE`개씩 반환한다.

    Args:
        keyword: 특정 키워드 경유 진입 시 해당 키워드. 없으면 일반 피드.
        cursor: 이전 응답의 `next_cursor`. 없으면 첫 페이지.
    """
    topic = keyword or _DEFAULT_TOPIC
    offset = int(cursor) if cursor else 0

    pool = _build_mock_pool(topic)
    page = pool[offset : offset + CURATION_PAGE_SIZE]
    next_offset = offset + CURATION_PAGE_SIZE
    next_cursor = str(next_offset) if next_offset < len(pool) else None

    return CurationResult(contents=page, next_cursor=next_cursor)


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
