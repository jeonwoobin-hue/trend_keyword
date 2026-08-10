"""COM-002 비밀번호 재설정. 이메일 인증 후 새 비밀번호를 설정한다 (SRS FR-AUTH-004)."""

import streamlit as st

from app.session import init_session_state
from config.constants import WidgetKeys
from services.auth_service import AuthError, request_password_reset, reset_password

st.set_page_config(page_title="비밀번호 재설정 - TrendFit", page_icon="🔓", layout="wide")
init_session_state()

_STEP_KEY = "reset_step"  # "email" | "verify" | "new_password" | "done"
_PENDING_EMAIL_KEY = "reset_pending_email"
_VERIFICATION_CODE_KEY = "reset_verification_code"

st.title("🔓 비밀번호 재설정")
st.caption(
    "실제 계정 저장소 연동 전 단계로, 이메일 인증 → 새 비밀번호 설정 절차만 시연합니다 "
    "(입력한 새 비밀번호는 실제로 저장되지 않습니다)."
)

step = st.session_state.get(_STEP_KEY, "email")

if step == "done":
    st.success("비밀번호가 재설정되었습니다. 새 비밀번호로 로그인해주세요.")
    if st.button("로그인하러 가기", type="primary"):
        st.session_state[_STEP_KEY] = "email"
        st.switch_page("pages/0_🔑_로그인.py")
    st.stop()

if step == "new_password":
    pending_email = st.session_state[_PENDING_EMAIL_KEY]
    st.caption(f"{pending_email} 인증이 완료되었습니다. 새 비밀번호를 입력해주세요.")

    with st.form(key=WidgetKeys.RESET_PASSWORD_FORM):
        new_password = st.text_input(
            "새 비밀번호", type="password", key=WidgetKeys.RESET_NEW_PASSWORD_INPUT
        )
        new_password_confirm = st.text_input(
            "새 비밀번호 확인", type="password", key=WidgetKeys.RESET_NEW_PASSWORD_CONFIRM_INPUT
        )
        password_submitted = st.form_submit_button("비밀번호 재설정", type="primary", use_container_width=True)

    if password_submitted:
        try:
            reset_password(new_password, new_password_confirm)
        except AuthError as error:
            st.error(error.message)
        else:
            st.session_state[_STEP_KEY] = "done"
            st.session_state.pop(_PENDING_EMAIL_KEY, None)
            st.session_state.pop(_VERIFICATION_CODE_KEY, None)
            st.rerun()

elif step == "verify":
    pending_email = st.session_state[_PENDING_EMAIL_KEY]
    verification_code = st.session_state[_VERIFICATION_CODE_KEY]

    st.success(f"{pending_email}로 인증번호를 보냈습니다.")
    st.caption(f"실제 이메일 발송 연동 전 단계로, 인증번호를 화면에 표시합니다: **{verification_code}**")

    with st.form(key=WidgetKeys.RESET_CODE_FORM):
        code_value = st.text_input("인증번호", key=WidgetKeys.RESET_CODE_INPUT)
        verify_submitted = st.form_submit_button("인증 확인", type="primary", use_container_width=True)

    if verify_submitted:
        if code_value.strip() == verification_code:
            st.session_state[_STEP_KEY] = "new_password"
            st.rerun()
        else:
            st.error("인증번호가 일치하지 않습니다.")

else:
    st.markdown("#### 이메일 인증")
    with st.form(key=WidgetKeys.RESET_EMAIL_FORM):
        email_value = st.text_input("가입 시 사용한 이메일", key=WidgetKeys.RESET_EMAIL_INPUT)
        email_submitted = st.form_submit_button("인증번호 받기", type="primary", use_container_width=True)

    if email_submitted:
        try:
            verification_code = request_password_reset(email_value)
        except AuthError as error:
            st.error(error.message)
        else:
            st.session_state[_PENDING_EMAIL_KEY] = email_value.strip()
            st.session_state[_VERIFICATION_CODE_KEY] = verification_code
            st.session_state[_STEP_KEY] = "verify"
            st.rerun()

st.divider()
if st.button("로그인으로 돌아가기"):
    st.session_state[_STEP_KEY] = "email"
    st.switch_page("pages/0_🔑_로그인.py")
