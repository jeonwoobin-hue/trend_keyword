"""Streamlit 세션 상태 초기화 공용 모듈. Home.py 및 각 pages 진입 시 호출한다."""

import streamlit as st

from config.constants import SessionKeys


def init_session_state() -> None:
    """`st.session_state` 기본값을 없을 때만 채운다."""
    defaults = {
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
        SessionKeys.ADMIN_SPIKE_BATCH_STATUS: None,
        SessionKeys.ADMIN_USERS: None,
        SessionKeys.ADMIN_BLACKLIST: [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
