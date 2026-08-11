"""ALERT-001 급상승 알림 설정. 알림 키워드를 등록/삭제하고 임계치·수신 방식을 관리한다."""

import streamlit as st

from app.auth_guard import require_login
from app.session import init_session_state
from components.top_nav import render_top_nav
from config.constants import (
    DEFAULT_THRESHOLD_SCORE,
    MAX_ALERT_KEYWORD_LENGTH,
    MAX_ALERT_KEYWORDS,
    NOTIFY_CHANNELS,
    SessionKeys,
    WidgetKeys,
)
from services.alert_service import AlertValidationError, register_alert, remove_alert

st.set_page_config(page_title="급상승 알림 설정 - TrendFit", page_icon="🔔", layout="wide")
init_session_state()
render_top_nav(current_group="trend")

st.title("🔔 급상승 알림 설정")
require_login()
st.caption(
    "등록한 키워드의 Spike Score가 임계치를 넘으면 알림을 받습니다. "
    "실제 발송(이메일/배치 워커) 연동 전 단계로, 지금은 등록 내역이 세션 동안만 유지됩니다."
)
if st.button("📬 알림함 보기"):
    st.switch_page("pages/11_📬_알림함.py")

prefill_keyword = st.session_state.pop(SessionKeys.ALERT_PREFILL_KEYWORD, None)
if prefill_keyword:
    st.session_state[WidgetKeys.ALERT_KEYWORD_INPUT] = prefill_keyword

channel_labels = dict(NOTIFY_CHANNELS)
alert_rules = st.session_state[SessionKeys.ALERT_RULES]

with st.form(key=WidgetKeys.ALERT_FORM, clear_on_submit=True):
    st.markdown("#### 키워드 추가")
    keyword_col, threshold_col = st.columns([2, 1])
    with keyword_col:
        keyword_value = st.text_input(
            "키워드", key=WidgetKeys.ALERT_KEYWORD_INPUT, max_chars=MAX_ALERT_KEYWORD_LENGTH
        )
    with threshold_col:
        threshold_value = st.slider(
            "Spike 임계치",
            min_value=0,
            max_value=100,
            value=DEFAULT_THRESHOLD_SCORE,
            key=WidgetKeys.ALERT_THRESHOLD_SLIDER,
        )
    channel_values = st.multiselect(
        "알림 수신 방식",
        options=[value for value, _ in NOTIFY_CHANNELS],
        default=st.session_state[SessionKeys.NOTIFY_CHANNEL_PREFERENCE],
        format_func=lambda value: channel_labels[value],
        key=WidgetKeys.ALERT_CHANNEL_MULTISELECT,
        help="기본값은 마이페이지 > 계정 설정에서 바꿀 수 있습니다.",
    )
    submitted = st.form_submit_button("키워드 추가", type="primary")

if submitted:
    try:
        new_rule = register_alert(alert_rules, keyword_value, threshold_value, channel_values)
    except AlertValidationError as error:
        st.error(error.message)
    else:
        st.session_state[SessionKeys.ALERT_RULES] = [*alert_rules, new_rule]
        st.toast(f"'{new_rule.keyword}' 알림이 등록되었습니다.")

st.divider()

alert_rules = st.session_state[SessionKeys.ALERT_RULES]
st.markdown(f"#### 등록된 키워드 ({len(alert_rules)}/{MAX_ALERT_KEYWORDS})")

if not alert_rules:
    st.info("등록된 알림 키워드가 없습니다.")
else:
    for rule in alert_rules:
        with st.container(border=True):
            keyword_col, threshold_col, channel_col, delete_col = st.columns([2, 1, 2, 1])
            keyword_col.markdown(f"**{rule.keyword}**")
            threshold_col.caption(f"임계치 {rule.threshold_score}")
            channel_col.caption(", ".join(channel_labels[channel] for channel in rule.notify_channels))
            if delete_col.button("삭제", key=f"delete_{rule.alert_id}", use_container_width=True):
                st.session_state[SessionKeys.ALERT_RULES] = remove_alert(alert_rules, rule.alert_id)
                st.rerun()
