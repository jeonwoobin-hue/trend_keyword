"""COM-003 회원가입. 이메일 인증을 거쳐 계정을 생성한다."""

import streamlit as st

from app.session import init_session_state
from components.top_nav import render_top_nav
from config.constants import SessionKeys, WidgetKeys
from services.auth_service import (
    AuthError,
    complete_signup,
    is_verification_code_valid,
    request_signup_verification,
)

st.set_page_config(page_title="회원가입 - TrendFit", page_icon="🧾", layout="wide")
init_session_state()
render_top_nav()

_STEP_KEY = "signup_step"  # "info" | "verify"
_PENDING_EMAIL_KEY = "signup_pending_email"
_VERIFICATION_CODE_KEY = "signup_verification_code"

st.title("🧾 회원가입")

if st.session_state[SessionKeys.IS_AUTHENTICATED]:
    st.info("이미 로그인되어 있습니다.")
    if st.button("계속하기", type="primary"):
        st.switch_page("pages/2_📝_관심사_설정.py")
    st.stop()

step = st.session_state.get(_STEP_KEY, "info")

if step == "verify":
    pending_email = st.session_state[_PENDING_EMAIL_KEY]
    verification_code = st.session_state[_VERIFICATION_CODE_KEY]

    st.success(f"{pending_email}로 인증번호를 보냈습니다.")
    st.caption(f"실제 이메일 발송 연동 전 단계로, 인증번호를 화면에 표시합니다: **{verification_code}**")

    with st.form(key=WidgetKeys.SIGNUP_CODE_FORM):
        code_value = st.text_input("인증번호", key=WidgetKeys.SIGNUP_CODE_INPUT)
        verify_submitted = st.form_submit_button("인증 확인", type="primary", use_container_width=True)

    if verify_submitted:
        if is_verification_code_valid(code_value, verification_code):
            auth_user = complete_signup(pending_email)
            st.session_state[SessionKeys.IS_AUTHENTICATED] = True
            st.session_state[SessionKeys.AUTH_USER] = auth_user
            st.session_state[_STEP_KEY] = "info"
            st.session_state.pop(_PENDING_EMAIL_KEY, None)
            st.session_state.pop(_VERIFICATION_CODE_KEY, None)
            st.switch_page("pages/2_📝_관심사_설정.py")
        else:
            st.error("인증번호가 일치하지 않습니다.")

    if st.button("정보 다시 입력하기"):
        st.session_state[_STEP_KEY] = "info"
        st.rerun()

else:
    st.caption("이메일, 비밀번호, 약관 동의 후 이메일 인증을 거치면 가입이 완료됩니다.")

    with st.form(key=WidgetKeys.SIGNUP_INFO_FORM):
        email_value = st.text_input("이메일", key=WidgetKeys.SIGNUP_EMAIL_INPUT)
        password_value = st.text_input("비밀번호", type="password", key=WidgetKeys.SIGNUP_PASSWORD_INPUT)
        password_confirm_value = st.text_input(
            "비밀번호 확인", type="password", key=WidgetKeys.SIGNUP_PASSWORD_CONFIRM_INPUT
        )
        agreed_to_terms = st.checkbox(
            "이용약관 및 개인정보 처리방침에 동의합니다.", key=WidgetKeys.SIGNUP_TERMS_CHECKBOX
        )
        info_submitted = st.form_submit_button("인증번호 받기", type="primary", use_container_width=True)

    if info_submitted:
        try:
            verification_code = request_signup_verification(
                email_value, password_value, password_confirm_value, agreed_to_terms
            )
        except AuthError as error:
            st.error(error.message)
        else:
            st.session_state[_PENDING_EMAIL_KEY] = email_value.strip()
            st.session_state[_VERIFICATION_CODE_KEY] = verification_code
            st.session_state[_STEP_KEY] = "verify"
            st.rerun()

st.divider()
if st.button("이미 계정이 있으신가요? 로그인"):
    st.switch_page("pages/0_🔑_로그인.py")
