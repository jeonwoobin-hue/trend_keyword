"""COM-002 로그인. 이메일/비밀번호로 로그인한다."""

import streamlit as st

from app.session import init_session_state
from config.constants import SessionKeys, WidgetKeys
from services.auth_service import AuthError, login

st.set_page_config(page_title="로그인 - TrendFit", page_icon="🔑", layout="wide")
init_session_state()

st.title("🔑 로그인")


def _next_page_after_login() -> str:
    """온보딩 완료 여부에 따라 로그인 후 이동할 페이지를 결정한다."""
    if st.session_state[SessionKeys.USER_PROFILE] is not None:
        return "pages/3_📊_트렌드_대시보드.py"
    return "pages/2_📝_관심사_설정.py"


if st.session_state[SessionKeys.IS_AUTHENTICATED]:
    auth_user = st.session_state[SessionKeys.AUTH_USER]
    st.success(f"{auth_user.display_name}님, 이미 로그인되어 있습니다.")
    if st.button("계속하기", type="primary"):
        st.switch_page(_next_page_after_login())
    st.stop()

st.caption("실제 인증 백엔드 연동 전 단계로, 형식이 올바른 이메일·비밀번호(8자 이상)면 로그인됩니다.")

with st.form(key=WidgetKeys.LOGIN_FORM):
    email_value = st.text_input("이메일", key=WidgetKeys.LOGIN_EMAIL_INPUT)
    password_value = st.text_input("비밀번호", type="password", key=WidgetKeys.LOGIN_PASSWORD_INPUT)
    submitted = st.form_submit_button("로그인", type="primary", use_container_width=True)

if submitted:
    try:
        auth_user = login(email_value, password_value)
    except AuthError as error:
        st.error(error.message)
    else:
        st.session_state[SessionKeys.IS_AUTHENTICATED] = True
        st.session_state[SessionKeys.AUTH_USER] = auth_user
        st.switch_page(_next_page_after_login())

st.divider()

social_col1, social_col2 = st.columns(2)
with social_col1:
    st.button(
        "구글로 로그인", disabled=True, use_container_width=True, help="소셜 로그인(FR-AUTH-002, P2)은 준비 중입니다."
    )
with social_col2:
    st.button(
        "카카오로 로그인", disabled=True, use_container_width=True, help="소셜 로그인(FR-AUTH-002, P2)은 준비 중입니다."
    )

link_col1, link_col2 = st.columns(2)
with link_col1:
    if st.button("회원가입", use_container_width=True):
        st.switch_page("pages/1_🧾_회원가입.py")
with link_col2:
    if st.button("비밀번호 찾기", use_container_width=True):
        st.info("비밀번호 재설정(FR-AUTH-004, P2)은 준비 중입니다.")
