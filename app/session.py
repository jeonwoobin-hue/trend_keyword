"""Streamlit 세션 상태 초기화 공용 모듈. Home.py 및 각 pages 진입 시 호출한다."""

import streamlit as st

from config.constants import DEFAULT_NOTIFY_CHANNELS, SessionKeys


def _default_session_values() -> dict:
    """세션 상태 기본값 매핑을 반환한다 (매 호출마다 새 리스트 인스턴스를 만들어 공유 참조를 피한다)."""
    return {
        SessionKeys.IS_AUTHENTICATED: False,
        SessionKeys.USER_PROFILE: None,
        SessionKeys.SELECTED_KEYWORD_ID: None,
        SessionKeys.ALERT_RULES: [],
        SessionKeys.ALERT_PREFILL_KEYWORD: None,
        SessionKeys.ALERT_HISTORY: None,
        SessionKeys.ONBOARDING_PREVIEW_KEYWORDS: [],
        SessionKeys.AUTH_USER: None,
        SessionKeys.ONBOARD_EDIT_MODE: False,
        SessionKeys.REPORTS: [],
        SessionKeys.SELECTED_REPORT_ID: None,
        SessionKeys.CURATION_CONTENTS: [],
        SessionKeys.CURATION_CURSOR: None,
        SessionKeys.CURATION_ACTIVE_KEYWORD: None,
        SessionKeys.CURATION_KEYWORD_FILTER: None,
        SessionKeys.CURATION_PLATFORM_FILTER: [],
        SessionKeys.SELECTED_CONTENT_ID: None,
        SessionKeys.ADMIN_SPIKE_BATCH_STATUS: None,
        SessionKeys.ADMIN_USERS: None,
        SessionKeys.ADMIN_BLACKLIST: [],
        SessionKeys.NOTIFY_CHANNEL_PREFERENCE: list(DEFAULT_NOTIFY_CHANNELS),
        SessionKeys.SCRAPPED_CONTENTS: [],
    }


# 회원 탈퇴(FR-PROFILE-004) 시 초기화할 사용자 개인 데이터 키. 관리자 도구 상태(ADMIN_*)는
# 개인 데이터가 아니므로 제외한다.
_USER_SCOPED_KEYS = [
    SessionKeys.IS_AUTHENTICATED,
    SessionKeys.AUTH_USER,
    SessionKeys.USER_PROFILE,
    SessionKeys.ONBOARDING_PREVIEW_KEYWORDS,
    SessionKeys.ONBOARD_EDIT_MODE,
    SessionKeys.ALERT_RULES,
    SessionKeys.ALERT_HISTORY,
    SessionKeys.ALERT_PREFILL_KEYWORD,
    SessionKeys.REPORTS,
    SessionKeys.SELECTED_REPORT_ID,
    SessionKeys.SELECTED_KEYWORD_ID,
    SessionKeys.CURATION_CONTENTS,
    SessionKeys.CURATION_CURSOR,
    SessionKeys.CURATION_ACTIVE_KEYWORD,
    SessionKeys.CURATION_PLATFORM_FILTER,
    SessionKeys.SELECTED_CONTENT_ID,
    SessionKeys.NOTIFY_CHANNEL_PREFERENCE,
    SessionKeys.SCRAPPED_CONTENTS,
]


def init_session_state() -> None:
    """`st.session_state` 기본값을 없을 때만 채운다."""
    for key, value in _default_session_values().items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_user_data() -> None:
    """회원 탈퇴(FR-PROFILE-004) 시 사용자 개인 데이터를 초기값으로 되돌린다."""
    defaults = _default_session_values()
    for key in _USER_SCOPED_KEYS:
        st.session_state[key] = defaults[key]
