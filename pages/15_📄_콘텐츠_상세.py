"""CURATE-002 콘텐츠 상세. 콘텐츠 미리보기, 연관 키워드 태그를 보여주고 원문 이동·스크랩을 제공한다."""

import streamlit as st

from app.auth_guard import require_login
from app.session import init_session_state
from components.top_nav import render_top_nav
from config.constants import SessionKeys
from models.curation import ContentDetail, ContentItem
from services.curation_service import add_scrap, get_content_detail, remove_scrap

st.set_page_config(page_title="콘텐츠 상세 - TrendFit", page_icon="📄", layout="wide")
init_session_state()
render_top_nav(current_group="insight")

_PLATFORM_ICONS = {"naver_blog": "📝", "youtube": "▶️", "instagram": "📸", "threads": "🧵"}


@st.cache_data(ttl=60)
def _load_content_detail(content_id: str, keyword: str | None) -> ContentDetail | None:
    return get_content_detail(content_id, keyword)


st.title("📄 콘텐츠 상세")
st.caption("실제 외부 콘텐츠 연동 전 단계로, 표시되는 값은 샘플 데이터입니다.")
require_login()

content_id = st.session_state.get(SessionKeys.SELECTED_CONTENT_ID)

if not content_id:
    st.info("콘텐츠 큐레이션에서 콘텐츠를 먼저 선택해주세요.")
    if st.button("콘텐츠 큐레이션으로 이동"):
        st.switch_page("pages/8_🎬_콘텐츠_큐레이션.py")
    st.stop()

active_keyword = st.session_state[SessionKeys.CURATION_ACTIVE_KEYWORD]
detail = _load_content_detail(content_id, active_keyword)

if detail is None:
    st.error("해당 콘텐츠 정보를 찾을 수 없습니다.")
    if st.button("콘텐츠 큐레이션으로 이동"):
        st.switch_page("pages/8_🎬_콘텐츠_큐레이션.py")
    st.stop()

icon_col, title_col = st.columns([1, 9])
with icon_col:
    st.markdown(f"## {_PLATFORM_ICONS.get(detail.platform, '📄')}")
with title_col:
    st.subheader(detail.title)
    st.caption(f"{detail.source} · {detail.published_at:%Y-%m-%d}")

st.divider()

st.markdown("#### 콘텐츠 미리보기")
if not detail.is_available:
    st.warning("원문을 찾을 수 없습니다.")
else:
    st.info("실제 원문 미리보기 연동 전 단계입니다.")

action_col1, action_col2 = st.columns(2)
with action_col1:
    if not detail.is_available:
        st.button("원문 이동", disabled=True, use_container_width=True)
    elif st.button("원문 이동", type="primary", use_container_width=True):
        st.info("실제 원문 링크 연동 전 단계입니다.")
with action_col2:
    scrapped_ids = {item.content_id for item in st.session_state[SessionKeys.SCRAPPED_CONTENTS]}
    is_scrapped = detail.content_id in scrapped_ids
    label = "★ 스크랩됨" if is_scrapped else "☆ 스크랩"
    if st.button(label, use_container_width=True):
        scraps = st.session_state[SessionKeys.SCRAPPED_CONTENTS]
        if is_scrapped:
            st.session_state[SessionKeys.SCRAPPED_CONTENTS] = remove_scrap(scraps, detail.content_id)
        else:
            scrap_item = ContentItem(
                content_id=detail.content_id,
                title=detail.title,
                thumbnail=detail.thumbnail,
                source=detail.source,
                platform=detail.platform,
                published_at=detail.published_at,
                url=detail.url,
                is_available=detail.is_available,
            )
            st.session_state[SessionKeys.SCRAPPED_CONTENTS] = add_scrap(scraps, scrap_item)
        st.rerun()

st.divider()

st.markdown("#### 연관 키워드")
if detail.related_keywords:
    st.markdown(" ".join(f":blue-badge[{kw}]" for kw in detail.related_keywords))
else:
    st.caption("연관 키워드가 없습니다.")

st.divider()
if st.button("← 콘텐츠 큐레이션으로 돌아가기"):
    st.switch_page("pages/8_🎬_콘텐츠_큐레이션.py")
