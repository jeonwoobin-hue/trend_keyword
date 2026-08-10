"""services/curation_service.py 단위 테스트 (functional-spec FR-CURATE-001)."""

from config.constants import CURATION_PAGE_SIZE, CURATION_TOTAL_MOCK_ITEMS
from services.curation_service import get_curated_contents


def test_get_curated_contents_first_page_size_and_cursor():
    result = get_curated_contents(None, None)

    assert len(result.contents) == CURATION_PAGE_SIZE
    assert result.next_cursor == str(CURATION_PAGE_SIZE)


def test_get_curated_contents_pagination_reaches_end_exactly_once():
    keyword = "패션"
    seen_ids: list[str] = []
    cursor = None

    for _ in range(10):  # 안전장치: 무한 루프 방지
        page = get_curated_contents(keyword, cursor)
        seen_ids.extend(item.content_id for item in page.contents)
        cursor = page.next_cursor
        if cursor is None:
            break

    assert cursor is None
    assert len(seen_ids) == CURATION_TOTAL_MOCK_ITEMS
    assert len(set(seen_ids)) == CURATION_TOTAL_MOCK_ITEMS


def test_get_curated_contents_is_deterministic():
    first = get_curated_contents("패션", None)
    second = get_curated_contents("패션", None)

    assert [item.content_id for item in first.contents] == [item.content_id for item in second.contents]


def test_get_curated_contents_different_keyword_yields_different_ids():
    fashion = get_curated_contents("패션", None)
    travel = get_curated_contents("여행", None)

    fashion_ids = {item.content_id for item in fashion.contents}
    travel_ids = {item.content_id for item in travel.contents}
    assert fashion_ids.isdisjoint(travel_ids)


def test_get_curated_contents_marks_some_items_unavailable():
    seen_unavailable = False
    cursor = None
    for _ in range(10):
        page = get_curated_contents("패션", cursor)
        if any(not item.is_available for item in page.contents):
            seen_unavailable = True
        cursor = page.next_cursor
        if cursor is None:
            break

    assert seen_unavailable
