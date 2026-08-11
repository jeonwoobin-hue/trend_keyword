"""MY-002 계정 설정. 계정 정보 수정·비밀번호 변경, 기본 탐색 기간, 알림 수신 설정(FR-PROFILE-003),
회원 탈퇴(FR-PROFILE-004)를 관리한다."""

import streamlit as st

from app.auth_guard import require_login
from app.session import clear_user_data, init_session_state
from components.top_nav import render_top_nav
from config.constants import NOTIFY_CHANNELS, PERIOD_OPTIONS, SessionKeys, WidgetKeys
from services.auth_service import AuthError, change_password, delete_account, update_display_name

st.set_page_config(page_title="계정 설정 - TrendFit", page_icon="⚙️", layout="wide")
init_session_state()
render_top_nav(current_group="mypage")

st.title("⚙️ 계정 설정")
require_login()

auth_user = st.session_state[SessionKeys.AUTH_USER]

st.markdown("#### 계정 정보")
st.caption(f"이메일: {auth_user.email} (변경 불가)")

display_name_value = st.text_input(
    "표시 이름", value=auth_user.display_name, key=WidgetKeys.ACCOUNT_DISPLAY_NAME_INPUT
)
if st.button("정보 저장"):
    auth_session = st.session_state[SessionKeys.AUTH_SESSION]
    if auth_session is None:
        # 소셜 로그인(FR-AUTH-002)은 아직 목(mock)이라 Supabase 세션이 없다 — 로컬 세션에만 반영한다.
        st.session_state[SessionKeys.AUTH_USER] = auth_user.model_copy(update={"display_name": display_name_value})
        st.toast("계정 정보가 저장되었습니다.")
    else:
        try:
            saved_name = update_display_name(auth_session.access_token, auth_user.id, display_name_value)
        except AuthError as error:
            st.error(error.message)
        else:
            st.session_state[SessionKeys.AUTH_USER] = auth_user.model_copy(update={"display_name": saved_name})
            st.toast("계정 정보가 저장되었습니다.")

st.divider()

st.markdown("#### 기본 탐색 기간")
profile = st.session_state[SessionKeys.USER_PROFILE]
if profile is None:
    st.info("관심사 설정을 먼저 완료하면 기본 탐색 기간을 설정할 수 있습니다.")
    if st.button("관심사 설정하기"):
        st.switch_page("pages/2_📝_관심사_설정.py")
else:
    period_labels = dict(PERIOD_OPTIONS)
    period_values = [value for value, _ in PERIOD_OPTIONS]
    selected_period = st.selectbox(
        "탐색 기간",
        options=period_values,
        format_func=lambda value: period_labels[value],
        index=period_values.index(profile.period),
        key=WidgetKeys.ACCOUNT_DEFAULT_PERIOD_SELECT,
    )
    if st.button("탐색 기간 저장"):
        st.session_state[SessionKeys.USER_PROFILE] = profile.model_copy(update={"period": selected_period})
        st.toast("기본 탐색 기간이 저장되었습니다.")

st.divider()

st.markdown("#### 비밀번호 변경")
with st.form(key=WidgetKeys.ACCOUNT_PASSWORD_FORM, clear_on_submit=True):
    current_password = st.text_input(
        "현재 비밀번호", type="password", key=WidgetKeys.ACCOUNT_CURRENT_PASSWORD_INPUT
    )
    new_password = st.text_input("새 비밀번호", type="password", key=WidgetKeys.ACCOUNT_NEW_PASSWORD_INPUT)
    new_password_confirm = st.text_input(
        "새 비밀번호 확인", type="password", key=WidgetKeys.ACCOUNT_NEW_PASSWORD_CONFIRM_INPUT
    )
    password_submitted = st.form_submit_button("비밀번호 변경", type="primary")

if password_submitted:
    try:
        new_session = change_password(auth_user.email, current_password, new_password, new_password_confirm)
    except AuthError as error:
        st.error(error.message)
    else:
        st.session_state[SessionKeys.AUTH_SESSION] = new_session
        st.toast("비밀번호가 변경되었습니다.")

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
    "탈퇴하면 계정이 완전히 삭제되며, 관심사 프로필·등록한 알림 키워드·생성한 리포트 등 이 계정의 "
    "모든 데이터가 초기화됩니다. 이 작업은 되돌릴 수 없습니다."
)

confirm_delete = st.checkbox("위 내용을 확인했으며 탈퇴에 동의합니다.", key=WidgetKeys.ACCOUNT_DELETE_CONFIRM_CHECKBOX)
if st.button("회원 탈퇴", type="primary", disabled=not confirm_delete):
    auth_session = st.session_state[SessionKeys.AUTH_SESSION]
    if auth_session is None:
        # 소셜 로그인(FR-AUTH-002)은 아직 목(mock)이라 삭제할 실제 Supabase 계정이 없다.
        clear_user_data()
        st.switch_page("Home.py")
    else:
        try:
            delete_account(auth_user.id)
        except AuthError as error:
            st.error(error.message)
        else:
            clear_user_data()
            st.switch_page("Home.py")

st.divider()
if st.button("마이페이지로 돌아가기"):
    st.switch_page("pages/6_🙋_마이페이지.py")
