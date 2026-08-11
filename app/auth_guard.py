"""화면 접근 제어 공용 헬퍼 (IA 접근권한 열: G=비로그인, U=로그인, A=관리자)."""

import streamlit as st

from config.constants import SessionKeys, UserRole


def require_login(message: str = "로그인이 필요합니다.") -> None:
    """로그인하지 않은 세션이면 안내 후 스크립트 실행을 중단한다.

    로그인된 세션이면 아무 것도 하지 않고 즉시 반환해 페이지가 이어서 렌더링되게 한다.
    """
    if st.session_state[SessionKeys.IS_AUTHENTICATED]:
        return

    st.info(message)
    if st.button("로그인하러 가기", type="primary"):
        st.switch_page("pages/0_🔑_로그인.py")
    st.stop()


def require_admin(message: str = "관리자만 접근할 수 있는 화면입니다.") -> None:
    """관리자 역할(`UserRole.ADMIN`)이 아닌 세션이면 안내 후 스크립트 실행을 중단한다.

    로그인 여부까지 함께 확인한다 — 별도로 `require_login()`을 먼저 호출할 필요는 없다.
    """
    require_login()

    auth_user = st.session_state[SessionKeys.AUTH_USER]
    if auth_user is not None and auth_user.role == UserRole.ADMIN:
        return

    st.info(message)
    if st.button("홈으로 이동", type="primary"):
        st.switch_page("Home.py")
    st.stop()
