"""DASH-002 키워드 상세. 검색량 추이, 감성 비율, 연관 키워드를 보여준다."""

import pandas as pd
import streamlit as st

from app.auth_guard import require_login
from app.session import init_session_state
from components.top_nav import render_top_nav
from config.constants import (
    AGE_GROUP_OPTIONS,
    CATEGORIES,
    DASHBOARD_CACHE_TTL_SECONDS,
    DEFAULT_PERIOD,
    DEMOGRAPHIC_GENDERS,
    PERIOD_OPTIONS,
    SessionKeys,
    WidgetKeys,
)
from models.dashboard import KeywordDetail
from services.dashboard_service import get_keyword_detail

st.set_page_config(page_title="키워드 상세 - TrendFit", page_icon="🔍", layout="wide")
init_session_state()
render_top_nav(current_group="trend")


@st.cache_data(ttl=DASHBOARD_CACHE_TTL_SECONDS)
def _load_keyword_detail(keyword_id: str, period: str) -> KeywordDetail | None:
    return get_keyword_detail(keyword_id, period)


st.title("🔍 키워드 상세")
st.caption("실제 외부 데이터 연동 전 단계로, 표시되는 값은 샘플 데이터입니다.")
require_login()

keyword_id = st.session_state.get(SessionKeys.SELECTED_KEYWORD_ID)

if not keyword_id:
    st.info("대시보드에서 키워드를 먼저 선택해주세요.")
    if st.button("트렌드 대시보드로 이동"):
        st.switch_page("pages/3_📊_트렌드_대시보드.py")
    st.stop()

period_labels = dict(PERIOD_OPTIONS)
default_period_index = [value for value, _ in PERIOD_OPTIONS].index(DEFAULT_PERIOD)
selected_period = st.selectbox(
    "탐색 기간",
    options=[value for value, _ in PERIOD_OPTIONS],
    format_func=lambda value: period_labels[value],
    index=default_period_index,
    key=WidgetKeys.DASH_DETAIL_PERIOD_FILTER,
)

detail = _load_keyword_detail(keyword_id, selected_period)

if detail is None:
    st.error("해당 키워드 정보를 찾을 수 없습니다.")
    if st.button("트렌드 대시보드로 이동"):
        st.switch_page("pages/3_📊_트렌드_대시보드.py")
    st.stop()

category_label = dict(CATEGORIES).get(detail.category, detail.category)

header_col, alert_col = st.columns([3, 1])
with header_col:
    st.subheader(detail.keyword)
    st.caption(category_label)
with alert_col:
    if st.button("🔔 알림 설정", use_container_width=True):
        st.session_state[SessionKeys.ALERT_PREFILL_KEYWORD] = detail.keyword
        st.switch_page("pages/5_🔔_급상승_알림.py")

st.divider()

st.markdown("#### 검색량 추이")
trend_df = pd.DataFrame(
    [{"구간": point.label, "언급량": point.mention_count} for point in detail.trend_series]
).set_index("구간")
st.line_chart(trend_df, height=240)

st.divider()

st.markdown("#### 감성 분석")
if detail.sentiment is None:
    st.warning("감성 분석을 위한 데이터가 충분하지 않습니다.")
else:
    pos_col, neg_col, neu_col = st.columns(3)
    pos_col.metric("긍정", f"{detail.sentiment.positive:.0%}")
    neg_col.metric("부정", f"{detail.sentiment.negative:.0%}")
    neu_col.metric("중립", f"{detail.sentiment.neutral:.0%}")

st.divider()

st.markdown("#### 연령·성별 관심도")
st.caption("실제 데이터 소스 연동 전 단계로, 상대 비중을 목(mock) 데이터로 보여줍니다.")

age_labels = dict(AGE_GROUP_OPTIONS)
age_df = pd.DataFrame(
    [
        {"연령대": age_labels.get(group_id, group_id), "비중": weight}
        for group_id, weight in detail.demographics.age_group_weights.items()
    ]
).set_index("연령대")
st.bar_chart(age_df, horizontal=True)

gender_labels = dict(DEMOGRAPHIC_GENDERS)
gender_cols = st.columns(len(detail.demographics.gender_weights))
for col, (gender_id, weight) in zip(gender_cols, detail.demographics.gender_weights.items()):
    col.metric(gender_labels.get(gender_id, gender_id), f"{weight:.0%}")

st.divider()

st.markdown("#### 연관 키워드")
if detail.related_keywords:
    st.markdown(" ".join(f":blue-badge[{kw}]" for kw in detail.related_keywords))
else:
    st.caption("연관 키워드가 없습니다.")

st.divider()
if st.button("관련 콘텐츠 보기"):
    st.session_state[SessionKeys.CURATION_KEYWORD_FILTER] = detail.keyword
    st.switch_page("pages/8_🎬_콘텐츠_큐레이션.py")
