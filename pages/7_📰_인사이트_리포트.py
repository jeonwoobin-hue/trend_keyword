"""REPORT-001 인사이트 리포트 목록. 조건별 리포트를 생성하고 카드로 조회한다."""

import streamlit as st

from app.auth_guard import require_login
from app.session import init_session_state
from components.top_nav import render_top_nav
from config.constants import (
    CATEGORIES,
    CATEGORY_ALL,
    CATEGORY_ALL_LABEL,
    DEFAULT_PERIOD,
    PERIOD_OPTIONS,
    SessionKeys,
    WidgetKeys,
)
from services.report_service import ReportValidationError, generate_report

st.set_page_config(page_title="인사이트 리포트 - TrendFit", page_icon="📰", layout="wide")
init_session_state()
render_top_nav(current_group="insight")

st.title("📰 인사이트 리포트")
require_login()
st.caption(
    "실제 이슈 요약·Word Cloud·Network Graph 산출 연동 전 단계로, 목(mock) 데이터로 리포트가 생성됩니다."
)

category_labels = dict(CATEGORIES)
period_labels = dict(PERIOD_OPTIONS)
default_period_index = [value for value, _ in PERIOD_OPTIONS].index(DEFAULT_PERIOD)

with st.form(key=WidgetKeys.REPORT_GENERATE_FORM):
    st.markdown("#### 리포트 생성")
    gen_col1, gen_col2 = st.columns(2)
    with gen_col1:
        gen_category = st.selectbox(
            "관심 분야",
            options=[value for value, _ in CATEGORIES],
            format_func=lambda value: category_labels[value],
            key=WidgetKeys.REPORT_CATEGORY_SELECT,
        )
    with gen_col2:
        gen_period = st.selectbox(
            "탐색 기간",
            options=[value for value, _ in PERIOD_OPTIONS],
            format_func=lambda value: period_labels[value],
            index=default_period_index,
            key=WidgetKeys.REPORT_PERIOD_SELECT,
        )
    gen_title = st.text_input("제목 (선택, 미입력 시 자동 생성)", key=WidgetKeys.REPORT_TITLE_INPUT)
    generate_submitted = st.form_submit_button("리포트 생성", type="primary", use_container_width=True)

if generate_submitted:
    with st.spinner("리포트를 생성하는 중입니다..."):
        try:
            report = generate_report(gen_category, gen_period, gen_title)
        except ReportValidationError as error:
            st.error(error.message)
        else:
            st.session_state[SessionKeys.REPORTS] = [report, *st.session_state[SessionKeys.REPORTS]]
            st.toast(f"'{report.title}' 리포트가 생성되었습니다.")

st.divider()

reports = st.session_state[SessionKeys.REPORTS]

filter_options = [(CATEGORY_ALL, CATEGORY_ALL_LABEL), *CATEGORIES]
filter_labels = dict(filter_options)
selected_filter = st.selectbox(
    "분야 필터",
    options=[value for value, _ in filter_options],
    format_func=lambda value: filter_labels[value],
    key=WidgetKeys.REPORT_LIST_CATEGORY_FILTER,
)

filtered_reports = (
    reports if selected_filter == CATEGORY_ALL else [r for r in reports if r.category == selected_filter]
)

st.markdown(f"#### 리포트 목록 ({len(filtered_reports)}건)")

if not filtered_reports:
    st.info("생성된 리포트가 없습니다. 위에서 조건을 선택해 리포트를 생성해보세요.")
else:
    for report in filtered_reports:
        with st.container(border=True):
            header_col, date_col = st.columns([3, 1])
            with header_col:
                st.markdown(f"**{report.title}**")
                st.caption(f"{category_labels.get(report.category, report.category)} · {period_labels[report.period]}")
            with date_col:
                st.caption(f"{report.created_at:%Y-%m-%d %H:%M} UTC")

            st.write(report.summary)

            if st.button("상세보기", key=f"report_detail_{report.report_id}", use_container_width=True):
                st.session_state[SessionKeys.SELECTED_REPORT_ID] = report.report_id
                st.switch_page("pages/10_🗺️_리포트_상세.py")
