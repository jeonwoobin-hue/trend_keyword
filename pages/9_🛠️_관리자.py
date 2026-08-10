"""ADMIN-001 관리자 대시보드. 데이터 수집 현황과 Spike Score 배치 상태를 모니터링한다."""

import streamlit as st

from app.auth_guard import require_login
from app.session import init_session_state
from config.constants import SessionKeys
from services.admin_service import list_data_source_statuses, run_spike_batch_recalculation

st.set_page_config(page_title="관리자 대시보드 - TrendFit", page_icon="🛠️", layout="wide")
init_session_state()

st.title("🛠️ 관리자 대시보드")
st.caption(
    "관리자 전용 화면입니다. 현재는 로그인 여부만 확인하며, 역할(관리자/일반 사용자) 기반 "
    "접근 제어는 아직 구현되어 있지 않습니다."
)
require_login()

if st.button("🗂️ 사용자·키워드 관리"):
    st.switch_page("pages/12_🗂️_사용자_키워드_관리.py")

st.markdown("#### 외부 데이터 연동 현황")
st.caption("실제 외부 API 연동 전 단계입니다 (docs/API_Design.md §8 참고).")

for source in list_data_source_statuses():
    with st.container(border=True):
        label_col, status_col = st.columns([3, 1])
        label_col.markdown(f"**{source.source_label}**")
        with status_col:
            st.badge("미구현", color="gray")

st.divider()

st.markdown("#### Spike Score 배치 현황")
st.caption("실제 배치 스케줄러 연동 전 단계로, '지금 재계산'은 목(mock) 데이터를 다시 집계합니다.")

if st.session_state[SessionKeys.ADMIN_SPIKE_BATCH_STATUS] is None:
    st.session_state[SessionKeys.ADMIN_SPIKE_BATCH_STATUS] = run_spike_batch_recalculation()

batch_status = st.session_state[SessionKeys.ADMIN_SPIKE_BATCH_STATUS]

metric_col1, metric_col2, metric_col3 = st.columns(3)
metric_col1.metric("마지막 실행", f"{batch_status.last_run_at:%Y-%m-%d %H:%M} UTC")
metric_col2.metric("갱신된 키워드", f"{batch_status.updated_keyword_count}건")
metric_col3.metric("실패 키워드", f"{batch_status.failed_keyword_count}건")

if st.button("지금 재계산", type="primary"):
    st.session_state[SessionKeys.ADMIN_SPIKE_BATCH_STATUS] = run_spike_batch_recalculation()
    st.toast("Spike Score 재계산이 완료되었습니다.")
    st.rerun()

st.divider()

st.markdown("#### 현재 세션 통계")
st.caption("실제 다중 사용자 집계 전 단계로, 지금 접속한 세션 기준 값입니다.")

stat_col1, stat_col2, stat_col3 = st.columns(3)
stat_col1.metric("관심사 설정 여부", "완료" if st.session_state[SessionKeys.USER_PROFILE] else "미설정")
stat_col2.metric("등록된 알림 키워드", f"{len(st.session_state[SessionKeys.ALERT_RULES])}건")
stat_col3.metric("생성된 리포트", f"{len(st.session_state[SessionKeys.REPORTS])}건")
