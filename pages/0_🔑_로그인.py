"""COM-002 로그인. 이메일/비밀번호 또는 구글/카카오 OAuth로 로그인한다."""

import streamlit as st

from app.session import init_session_state
from components.top_nav import render_top_nav
from config.constants import APP_BASE_URL, SessionKeys, SOCIAL_PROVIDERS, WidgetKeys
from services.auth_service import AuthError, complete_social_login, get_social_login_url, login

st.set_page_config(page_title="로그인 - TrendFit", page_icon="🔑", layout="wide")
init_session_state()
render_top_nav()

st.title("🔑 로그인")


def _next_page_after_login() -> str:
    """온보딩 완료 여부에 따라 로그인 후 이동할 페이지를 결정한다."""
    if st.session_state[SessionKeys.USER_PROFILE] is not None:
        return "pages/3_📊_트렌드_대시보드.py"
    return "pages/2_📝_관심사_설정.py"


def _oauth_redirect_to() -> str:
    """소셜 로그인이 끝난 뒤 Supabase가 되돌아올 이 페이지의 URL."""
    return f"{APP_BASE_URL}/로그인"


# --- OAuth 리다이렉트 콜백 처리 ---
# 구글/카카오 동의 후 Supabase가 이 페이지로 ?code=...를 붙여 되돌려준다. 어느 프로바이더로
# 로그인했는지는 콜백만으로 알 수 없어, 이 페이지 로드 시점에 저장돼 있던 code_verifier 후보들을
# 순서대로 시도한다(최대 프로바이더 개수만큼).
_oauth_code = st.query_params.get("code")
if _oauth_code:
    st.query_params.clear()
    _pending_verifiers = st.session_state.get(SessionKeys.OAUTH_CODE_VERIFIERS) or {}
    st.session_state[SessionKeys.OAUTH_CODE_VERIFIERS] = {}

    _oauth_user, _oauth_session, _oauth_error = None, None, None
    for _verifier in _pending_verifiers.values():
        try:
            _oauth_user, _oauth_session = complete_social_login(_oauth_code, _verifier)
            break
        except AuthError as error:
            _oauth_error = error

    if _oauth_user is not None:
        st.session_state[SessionKeys.IS_AUTHENTICATED] = True
        st.session_state[SessionKeys.AUTH_USER] = _oauth_user
        st.session_state[SessionKeys.AUTH_SESSION] = _oauth_session
        st.switch_page(_next_page_after_login())
    else:
        st.error(_oauth_error.message if _oauth_error else "소셜 로그인 처리에 실패했습니다. 다시 시도해주세요.")

if st.session_state[SessionKeys.IS_AUTHENTICATED]:
    auth_user = st.session_state[SessionKeys.AUTH_USER]
    st.success(f"{auth_user.display_name}님, 이미 로그인되어 있습니다.")
    if st.button("계속하기", type="primary"):
        st.switch_page(_next_page_after_login())
    st.stop()

with st.form(key=WidgetKeys.LOGIN_FORM):
    email_value = st.text_input("이메일", key=WidgetKeys.LOGIN_EMAIL_INPUT)
    password_value = st.text_input("비밀번호", type="password", key=WidgetKeys.LOGIN_PASSWORD_INPUT)
    submitted = st.form_submit_button("로그인", type="primary", use_container_width=True)

if submitted:
    try:
        auth_user, auth_session = login(email_value, password_value)
    except AuthError as error:
        st.error(error.message)
    else:
        st.session_state[SessionKeys.IS_AUTHENTICATED] = True
        st.session_state[SessionKeys.AUTH_USER] = auth_user
        st.session_state[SessionKeys.AUTH_SESSION] = auth_session
        st.switch_page(_next_page_after_login())

st.divider()

social_col1, social_col2 = st.columns(2)
social_columns = {SOCIAL_PROVIDERS[0][0]: social_col1, SOCIAL_PROVIDERS[1][0]: social_col2}
_verifiers = {}
for provider_id, provider_label in SOCIAL_PROVIDERS:
    login_url, code_verifier = get_social_login_url(provider_id, _oauth_redirect_to())
    _verifiers[provider_id] = code_verifier
    with social_columns[provider_id]:
        st.link_button(f"{provider_label}로 로그인", login_url, use_container_width=True)
st.session_state[SessionKeys.OAUTH_CODE_VERIFIERS] = _verifiers

link_col1, link_col2 = st.columns(2)
with link_col1:
    if st.button("회원가입", use_container_width=True):
        st.switch_page("pages/1_🧾_회원가입.py")
with link_col2:
    if st.button("비밀번호 찾기", use_container_width=True):
        st.switch_page("pages/13_🔓_비밀번호_재설정.py")
