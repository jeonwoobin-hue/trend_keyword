"""MY-002 계정 설정. 알림 수신 설정(FR-PROFILE-003)과 회원 탈퇴(FR-PROFILE-004)를 관리한다."""

import streamlit as st

from app.auth_guard import require_login
from app.session import clear_user_data, init_session_state
from config.constants import NOTIFY_CHANNELS, SessionKeys, WidgetKeys

st.set_page_config(page_title="계정 설정 - TrendFit", page_icon="⚙️", layout="wide")
init_session_state()

st.title("⚙️ 계정 설정")
require_login()

auth_user = st.session_state[SessionKeys.AUTH_USER]

st.markdown("#### 계정 정보")
st.write(f"**이메일**: {auth_user.email}")

st.divider()

st.markdown("#### 알림 수신 설정 (기본값)")
st.caption("여기서 설정한 수신 방식은 급상승 알림 키워드를 새로 등록할 때 기본으로 선택됩니다.")

channel_labels = dict(NOTIFY_CHANNELS)
selected_channels = st.multiselect(
    "알림 수신 방식",
    options=[value for value, _ in NOTIFY_CHANNELS],
    default=st.session_state[SessionKeys.NOTIFY_CHANNEL_PREFERENCE],
    format_func=lambda value: channel_labels[value],
    key=WidgetKeys.ACCOUNT_NOTIFY_CHANNEL_MULTISELECT,
)

if st.button("저장", type="primary"):
    st.session_state[SessionKeys.NOTIFY_CHANNEL_PREFERENCE] = selected_channels
    st.toast("알림 수신 설정이 저장되었습니다.")

st.divider()

st.markdown("#### 회원 탈퇴")
st.warning(
    "탈퇴하면 관심사 프로필, 등록한 알림 키워드, 생성한 리포트 등 이 계정의 모든 데이터가 "
    "초기화됩니다. 실제 서버 저장소 연동 전 단계로, 지금은 현재 세션의 데이터만 지워집니다."
)

confirm_delete = st.checkbox("위 내용을 확인했으며 탈퇴에 동의합니다.", key=WidgetKeys.ACCOUNT_DELETE_CONFIRM_CHECKBOX)
if st.button("회원 탈퇴", type="primary", disabled=not confirm_delete):
    clear_user_data()
    st.switch_page("Home.py")

st.divider()
if st.button("마이페이지로 돌아가기"):
    st.switch_page("pages/6_🙋_마이페이지.py")
