"""REPORT-002 리포트 상세. 이슈 요약, Word Cloud, 키워드 연관성 Network Graph를 보여준다."""

import pandas as pd
import streamlit as st

from app.auth_guard import require_login
from app.session import init_session_state
from config.constants import CATEGORIES, PERIOD_OPTIONS, SessionKeys
from services.report_service import get_report_by_id

st.set_page_config(page_title="리포트 상세 - TrendFit", page_icon="🗺️", layout="wide")
init_session_state()

st.title("🗺️ 리포트 상세")
require_login()

report_id = st.session_state.get(SessionKeys.SELECTED_REPORT_ID)
report = get_report_by_id(st.session_state[SessionKeys.REPORTS], report_id) if report_id else None

if report is None:
    st.info("리포트 목록에서 리포트를 먼저 선택해주세요.")
    if st.button("인사이트 리포트로 이동", type="primary"):
        st.switch_page("pages/7_📰_인사이트_리포트.py")
    st.stop()

category_label = dict(CATEGORIES).get(report.category, report.category)
period_label = dict(PERIOD_OPTIONS).get(report.period, report.period)

st.subheader(report.title)
st.caption(f"{category_label} · {period_label} · {report.created_at:%Y-%m-%d %H:%M} UTC")
st.caption("실제 이슈 요약·Word Cloud·Network Graph 산출 연동 전 단계로, 목(mock) 데이터입니다.")

st.divider()
st.markdown("#### 이슈 요약")
st.write(report.summary)

st.divider()
st.markdown("#### Word Cloud")
if report.word_cloud:
    word_cloud_df = pd.DataFrame(
        [{"키워드": item.keyword, "가중치": item.weight} for item in report.word_cloud]
    ).set_index("키워드")
    st.bar_chart(word_cloud_df, horizontal=True)
else:
    st.caption("Word Cloud 데이터가 없습니다.")

st.divider()
st.markdown("#### 키워드 연관성 (Network Graph)")
st.caption("그래프 대신 연관 관계를 표로 표현합니다 (스크린리더 접근성, UI_UX_Rules.md §3).")

node_labels = {node.id: node.label for node in report.network_graph.nodes}
if report.network_graph.edges:
    edge_rows = [
        {
            "키워드 A": node_labels.get(edge.source, edge.source),
            "키워드 B": node_labels.get(edge.target, edge.target),
            "연관도": edge.weight,
        }
        for edge in report.network_graph.edges
    ]
    st.dataframe(pd.DataFrame(edge_rows), use_container_width=True, hide_index=True)
else:
    st.caption("연관성 데이터가 없습니다.")

st.divider()
st.markdown("#### 추천 키워드")
if report.recommended_keywords:
    st.markdown(" ".join(f":blue-badge[{kw}]" for kw in report.recommended_keywords))
else:
    st.caption("추천 키워드가 없습니다.")

st.divider()
st.caption("리포트 저장·공유·PDF 다운로드(FR-REPORT-004, P2)는 아직 준비 중입니다.")
if st.button("목록으로"):
    st.switch_page("pages/7_📰_인사이트_리포트.py")
