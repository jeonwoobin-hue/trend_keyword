"""화면 접근 제어 공용 헬퍼 (IA 접근권한 열: G=비로그인, U=로그인, A=관리자).

역할(관리자/일반 사용자) 필드가 아직 없어 `require_login()`이 U/A 등급을 함께 담당한다.
관리자 전용(A) 화면에 적용할 때는 페이지에 그 사실을 안내하는 문구를 함께 둘 것.
"""

import streamlit as st

from config.constants import SessionKeys


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
