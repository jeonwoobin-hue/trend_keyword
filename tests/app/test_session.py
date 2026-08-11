"""app/session.py 단위 테스트 (FR-PROFILE-004 회원 탈퇴 시 개인 데이터 초기화).

`st.session_state`는 `streamlit run` 밖에서도 동작하지만("bare mode") 경고 로그가 함께
출력된다 — 기능에는 영향이 없는 정상적인 경고다.
"""

import streamlit as st

from app.session import clear_user_data, init_session_state
from config.constants import SessionKeys
from models.alert import AlertRule
from models.auth import AuthSession, AuthUser


def _seed_logged_in_user_with_data() -> None:
    init_session_state()
    st.session_state[SessionKeys.IS_AUTHENTICATED] = True
    st.session_state[SessionKeys.AUTH_USER] = AuthUser(id="user_1", email="test@example.com", display_name="test")
    st.session_state[SessionKeys.AUTH_SESSION] = AuthSession(access_token="access", refresh_token="refresh")
    st.session_state[SessionKeys.ALERT_RULES] = [
        AlertRule(
            alert_id="alert_1",
            keyword="키워드",
            threshold_score=70,
            notify_channels=["inapp"],
            created_at="2026-08-11T00:00:00Z",
        )
    ]
    st.session_state[SessionKeys.REPORTS] = ["dummy_report"]
    st.session_state[SessionKeys.NOTIFY_CHANNEL_PREFERENCE] = ["email"]


def test_clear_user_data_resets_authentication_and_personal_data():
    _seed_logged_in_user_with_data()

    clear_user_data()

    assert st.session_state[SessionKeys.IS_AUTHENTICATED] is False
    assert st.session_state[SessionKeys.AUTH_USER] is None
    assert st.session_state[SessionKeys.AUTH_SESSION] is None
    assert st.session_state[SessionKeys.ALERT_RULES] == []
    assert st.session_state[SessionKeys.REPORTS] == []


def test_clear_user_data_does_not_touch_admin_state():
    init_session_state()
    st.session_state[SessionKeys.ADMIN_BLACKLIST] = ["금지어"]

    clear_user_data()

    assert st.session_state[SessionKeys.ADMIN_BLACKLIST] == ["금지어"]


def test_clear_user_data_resets_notify_preference_to_configured_default():
    from config.constants import DEFAULT_NOTIFY_CHANNELS

    _seed_logged_in_user_with_data()
    clear_user_data()

    assert st.session_state[SessionKeys.NOTIFY_CHANNEL_PREFERENCE] == list(DEFAULT_NOTIFY_CHANNELS)
