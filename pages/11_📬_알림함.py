"""ALERT-002 알림함. 등록된 알림 키워드의 발송 이력을 조회하고 읽음 처리한다."""

import streamlit as st

from app.auth_guard import require_login
from app.session import init_session_state
from components.top_nav import render_top_nav
from config.constants import SessionKeys
from services.alert_service import generate_alert_history

st.set_page_config(page_title="알림함 - TrendFit", page_icon="📬", layout="wide")
init_session_state()
render_top_nav(current_group="mypage")

st.title("📬 알림함")
require_login()

st.caption(
    "실제 배치 발송 워커(FR-ALERT-003) 연동 전 단계로, 등록된 알림 키워드가 임계치를 넘었다고 "
    "가정한 샘플 발송 이력입니다."
)

alert_rules = st.session_state[SessionKeys.ALERT_RULES]

if not alert_rules:
    st.info("등록된 알림 키워드가 없습니다.")
    if st.button("급상승 알림 설정하러 가기", type="primary"):
        st.switch_page("pages/5_🔔_급상승_알림.py")
    st.stop()

if st.session_state[SessionKeys.ALERT_HISTORY] is None:
    st.session_state[SessionKeys.ALERT_HISTORY] = generate_alert_history(alert_rules)

if st.button("새로고침"):
    st.session_state[SessionKeys.ALERT_HISTORY] = generate_alert_history(alert_rules)
    st.rerun()

history = st.session_state[SessionKeys.ALERT_HISTORY]
unread_count = sum(1 for entry in history if not entry.is_read)

st.divider()
st.markdown(f"#### 발송 이력 ({len(history)}건, 안 읽음 {unread_count}건)")

if not history:
    st.info("발송된 알림이 아직 없습니다.")
else:
    for entry in history:
        with st.container(border=True):
            info_col, status_col, read_col = st.columns([3, 1, 1])
            with info_col:
                title = f"**{entry.keyword}**" if entry.is_read else f"**🔵 {entry.keyword}**"
                st.markdown(title)
                st.caption(f"Spike Score {entry.spike_score} · {entry.sent_at:%Y-%m-%d %H:%M} UTC · {entry.channel}")
            with status_col:
                if entry.status == "failed":
                    st.badge("발송 실패", color="red")
                else:
                    st.badge("발송 완료", color="green")
            with read_col:
                if not entry.is_read:
                    if st.button("읽음 처리", key=f"read_{entry.alert_history_id}", use_container_width=True):
                        entry.is_read = True
                        st.rerun()
