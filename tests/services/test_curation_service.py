"""services/curation_service.py 단위 테스트 (functional-spec FR-CURATE-001, SRS FR-CURATE-003)."""

from config.constants import CURATION_PAGE_SIZE, CURATION_TOTAL_MOCK_ITEMS
from services.curation_service import add_scrap, get_curated_contents, remove_scrap


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


def test_get_curated_contents_platform_filter_restricts_results():
    result = get_curated_contents("패션", None, platforms=["youtube"])

    assert result.contents
    assert all(item.platform == "youtube" for item in result.contents)


def test_get_curated_contents_platform_filter_paginates_over_filtered_pool_only():
    keyword = "패션"
    platforms = ["youtube", "threads"]
    seen_ids: list[str] = []
    cursor = None

    for _ in range(10):
        page = get_curated_contents(keyword, cursor, platforms)
        seen_ids.extend(item.content_id for item in page.contents)
        cursor = page.next_cursor
        if cursor is None:
            break

    assert cursor is None
    assert 0 < len(seen_ids) < CURATION_TOTAL_MOCK_ITEMS
    assert len(set(seen_ids)) == len(seen_ids)


def test_get_curated_contents_empty_platform_list_returns_all():
    filtered_empty = get_curated_contents("패션", None, platforms=[])
    unfiltered = get_curated_contents("패션", None)

    assert [i.content_id for i in filtered_empty.contents] == [i.content_id for i in unfiltered.contents]


def test_add_scrap_appends_new_content():
    content = get_curated_contents("패션", None).contents[0]

    result = add_scrap([], content)

    assert result == [content]


def test_add_scrap_is_idempotent_for_same_content():
    content = get_curated_contents("패션", None).contents[0]
    once = add_scrap([], content)

    twice = add_scrap(once, content)

    assert twice == once
    assert len(twice) == 1


def test_remove_scrap_filters_target_only():
    first, second = get_curated_contents("패션", None).contents[:2]
    scraps = add_scrap(add_scrap([], first), second)

    remaining = remove_scrap(scraps, first.content_id)

    assert remaining == [second]
