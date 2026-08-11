"""DASH-001 트렌드 대시보드. 분야·기간 필터로 핫 키워드 Spike Score 랭킹을 보여준다."""

import streamlit as st

from app.session import init_session_state
from components.keyword_card import render_keyword_card
from components.top_nav import render_top_nav
from config.constants import (
    CATEGORIES,
    CATEGORY_ALL,
    CATEGORY_ALL_LABEL,
    DASHBOARD_CACHE_TTL_SECONDS,
    DEFAULT_PERIOD,
    PERIOD_OPTIONS,
    SessionKeys,
    WidgetKeys,
)
from models.dashboard import DashboardKeywordsResult
from services.dashboard_service import get_dashboard_keywords

st.set_page_config(page_title="트렌드 대시보드 - TrendFit", page_icon="📊", layout="wide")
init_session_state()
render_top_nav(current_group="trend")


@st.cache_data(ttl=DASHBOARD_CACHE_TTL_SECONDS)
def _load_dashboard_keywords(category: str, period: str) -> DashboardKeywordsResult:
    return get_dashboard_keywords(category=category, period=period)


st.title("📊 트렌드 대시보드")
st.caption("실제 외부 데이터 연동 전 단계로, 카드에 표시되는 값은 샘플 데이터입니다.")

category_options = [(CATEGORY_ALL, CATEGORY_ALL_LABEL), *CATEGORIES]
category_labels = dict(category_options)
period_labels = dict(PERIOD_OPTIONS)
default_period_index = [value for value, _ in PERIOD_OPTIONS].index(DEFAULT_PERIOD)

filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    selected_category = st.selectbox(
        "관심 분야",
        options=[value for value, _ in category_options],
        format_func=lambda value: category_labels[value],
        key=WidgetKeys.DASH_CATEGORY_FILTER,
    )
with filter_col2:
    selected_period = st.selectbox(
        "탐색 기간",
        options=[value for value, _ in PERIOD_OPTIONS],
        format_func=lambda value: period_labels[value],
        index=default_period_index,
        key=WidgetKeys.DASH_PERIOD_FILTER,
    )

result = _load_dashboard_keywords(selected_category, selected_period)

st.caption(f"갱신 시각: {result.meta.updated_at:%Y-%m-%d %H:%M} UTC")

if not result.keywords:
    st.info("표시할 트렌드 데이터가 없습니다.")
else:
    for rank, keyword in enumerate(result.keywords, start=1):
        detail_clicked = render_keyword_card(rank, keyword)
        if detail_clicked:
            st.session_state[SessionKeys.SELECTED_KEYWORD_ID] = keyword.keyword_id
            st.switch_page("pages/4_🔍_키워드_상세.py")
