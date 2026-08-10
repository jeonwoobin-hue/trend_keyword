"""CURATE-001 콘텐츠 큐레이션 피드. 관심 키워드 관련 인기 콘텐츠를 커서 기반으로 조회한다."""

import streamlit as st

from app.auth_guard import require_login
from app.session import init_session_state
from config.constants import CURATION_PLATFORMS, SessionKeys, WidgetKeys
from services.curation_service import add_scrap, get_curated_contents, remove_scrap

st.set_page_config(page_title="콘텐츠 큐레이션 - TrendFit", page_icon="🎬", layout="wide")
init_session_state()

_PLATFORM_ICONS = {"youtube": "▶️", "instagram": "📸", "news": "📰", "x": "✖️"}

st.title("🎬 콘텐츠 큐레이션")
st.caption("실제 외부 콘텐츠 연동 전 단계로, 카드에 표시되는 값은 샘플 데이터입니다.")
require_login()

new_keyword_filter = st.session_state.pop(SessionKeys.CURATION_KEYWORD_FILTER, None)
if new_keyword_filter:
    st.session_state[SessionKeys.CURATION_ACTIVE_KEYWORD] = new_keyword_filter
    st.session_state[SessionKeys.CURATION_CONTENTS] = []
    st.session_state[SessionKeys.CURATION_CURSOR] = None

active_keyword = st.session_state[SessionKeys.CURATION_ACTIVE_KEYWORD]
if active_keyword:
    filter_col, clear_col = st.columns([4, 1])
    filter_col.caption(f"'{active_keyword}' 관련 콘텐츠")
    if clear_col.button("전체 보기", use_container_width=True):
        st.session_state[SessionKeys.CURATION_ACTIVE_KEYWORD] = None
        st.session_state[SessionKeys.CURATION_CONTENTS] = []
        st.session_state[SessionKeys.CURATION_CURSOR] = None
        st.rerun()

platform_labels = dict(CURATION_PLATFORMS)
selected_platforms = st.multiselect(
    "플랫폼 필터",
    options=[value for value, _ in CURATION_PLATFORMS],
    format_func=lambda value: platform_labels[value],
    key=WidgetKeys.CURATION_PLATFORM_MULTISELECT,
)
if selected_platforms != st.session_state[SessionKeys.CURATION_PLATFORM_FILTER]:
    st.session_state[SessionKeys.CURATION_PLATFORM_FILTER] = selected_platforms
    st.session_state[SessionKeys.CURATION_CONTENTS] = []
    st.session_state[SessionKeys.CURATION_CURSOR] = None

active_platforms = st.session_state[SessionKeys.CURATION_PLATFORM_FILTER]

if not st.session_state[SessionKeys.CURATION_CONTENTS]:
    first_page = get_curated_contents(active_keyword, None, active_platforms)
    st.session_state[SessionKeys.CURATION_CONTENTS] = first_page.contents
    st.session_state[SessionKeys.CURATION_CURSOR] = first_page.next_cursor

contents = st.session_state[SessionKeys.CURATION_CONTENTS]

if not contents:
    st.info("관련 콘텐츠가 아직 없습니다.")
else:
    scrapped_ids = {item.content_id for item in st.session_state[SessionKeys.SCRAPPED_CONTENTS]}

    for content in contents:
        with st.container(border=True):
            icon_col, body_col, scrap_col = st.columns([1, 5, 1])
            with icon_col:
                st.markdown(f"### {_PLATFORM_ICONS.get(content.platform, '📄')}")
            with body_col:
                st.markdown(f"**{content.title}**")
                st.caption(f"{content.source} · {content.published_at:%Y-%m-%d}")
                if not content.is_available:
                    st.caption(":red[원문을 찾을 수 없습니다.]")
                elif st.button("원문 이동", key=f"content_open_{content.content_id}"):
                    st.info("실제 원문 링크 연동 전 단계입니다.")
            with scrap_col:
                is_scrapped = content.content_id in scrapped_ids
                label = "★ 스크랩됨" if is_scrapped else "☆ 스크랩"
                if st.button(label, key=f"scrap_{content.content_id}", use_container_width=True):
                    scraps = st.session_state[SessionKeys.SCRAPPED_CONTENTS]
                    if is_scrapped:
                        st.session_state[SessionKeys.SCRAPPED_CONTENTS] = remove_scrap(scraps, content.content_id)
                    else:
                        st.session_state[SessionKeys.SCRAPPED_CONTENTS] = add_scrap(scraps, content)
                    st.rerun()

    st.divider()
    next_cursor = st.session_state[SessionKeys.CURATION_CURSOR]
    if next_cursor:
        if st.button("더 보기", type="primary", use_container_width=True):
            next_page = get_curated_contents(active_keyword, next_cursor, active_platforms)
            st.session_state[SessionKeys.CURATION_CONTENTS] = contents + next_page.contents
            st.session_state[SessionKeys.CURATION_CURSOR] = next_page.next_cursor
            st.rerun()
    else:
        st.caption("마지막 콘텐츠까지 모두 확인했습니다.")
