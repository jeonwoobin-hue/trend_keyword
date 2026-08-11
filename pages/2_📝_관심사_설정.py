"""ONBOARD-001 관심사·조건 설정. 관심 분야/목적/연령대/플랫폼/기간을 입력받아 프로필을 만든다."""

import streamlit as st

from app.auth_guard import require_login
from app.session import init_session_state
from components.top_nav import render_top_nav
from config.constants import (
    AGE_GROUP_OPTIONS,
    CATEGORIES,
    GENDER_OPTIONS,
    MAX_INTERESTS,
    PERIOD_OPTIONS,
    PLATFORM_OPTIONS,
    PURPOSE_OPTIONS,
    SessionKeys,
    WidgetKeys,
)
from services.profile_service import ProfileValidationError, build_preview_keywords, register_interest_profile

st.set_page_config(page_title="관심사 설정 - TrendFit", page_icon="📝", layout="wide")
init_session_state()
render_top_nav(current_group="mypage")

st.title("📝 관심사·조건 설정")
require_login()

has_profile = st.session_state[SessionKeys.USER_PROFILE] is not None
is_editing = st.session_state[SessionKeys.ONBOARD_EDIT_MODE]

if has_profile and not is_editing:
    profile = st.session_state[SessionKeys.USER_PROFILE]
    interest_labels = dict(CATEGORIES)
    purpose_labels = dict(PURPOSE_OPTIONS)
    age_labels = dict(AGE_GROUP_OPTIONS)
    platform_labels = dict(PLATFORM_OPTIONS)

    st.success("관심사 설정이 완료되었습니다.")
    st.markdown("#### 선택 조건 요약")
    st.write(f"**관심 분야**: {', '.join(interest_labels.get(i, i) for i in profile.interests)}")
    st.write(f"**목적**: {purpose_labels.get(profile.purpose, profile.purpose)}")
    st.write(f"**연령대**: {age_labels.get(profile.age_group, profile.age_group)}")
    st.write(f"**선호 플랫폼**: {', '.join(platform_labels.get(p, p) for p in profile.platforms)}")

    preview_keywords = st.session_state[SessionKeys.ONBOARDING_PREVIEW_KEYWORDS]
    if preview_keywords:
        st.markdown("#### 추천 키워드 미리보기")
        st.markdown(" ".join(f":blue-badge[{kw}]" for kw in preview_keywords))

    button_col1, button_col2 = st.columns(2)
    with button_col1:
        if st.button("관심사 수정", use_container_width=True):
            st.session_state[SessionKeys.ONBOARD_EDIT_MODE] = True
            st.rerun()
    with button_col2:
        if st.button("대시보드로 이동", type="primary", use_container_width=True):
            st.switch_page("pages/3_📊_트렌드_대시보드.py")

else:
    st.caption("관심 분야, 목적, 연령대, 선호 플랫폼, 탐색 기간을 선택해주세요.")

    interests = st.multiselect(
        f"관심 분야 (최대 {MAX_INTERESTS}개)",
        options=[value for value, _ in CATEGORIES],
        format_func=lambda value: dict(CATEGORIES)[value],
        max_selections=MAX_INTERESTS,
        key=WidgetKeys.ONBOARD_INTERESTS,
    )
    purpose = st.selectbox(
        "이용 목적",
        options=[value for value, _ in PURPOSE_OPTIONS],
        format_func=lambda value: dict(PURPOSE_OPTIONS)[value],
        key=WidgetKeys.ONBOARD_PURPOSE,
    )
    age_col, gender_col = st.columns(2)
    with age_col:
        age_group = st.selectbox(
            "연령대",
            options=[value for value, _ in AGE_GROUP_OPTIONS],
            format_func=lambda value: dict(AGE_GROUP_OPTIONS)[value],
            key=WidgetKeys.ONBOARD_AGE_GROUP,
        )
    with gender_col:
        gender = st.selectbox(
            "성별",
            options=[value for value, _ in GENDER_OPTIONS],
            format_func=lambda value: dict(GENDER_OPTIONS)[value],
            key=WidgetKeys.ONBOARD_GENDER,
        )
    platforms = st.multiselect(
        "선호 플랫폼",
        options=[value for value, _ in PLATFORM_OPTIONS],
        format_func=lambda value: dict(PLATFORM_OPTIONS)[value],
        key=WidgetKeys.ONBOARD_PLATFORMS,
    )
    period = st.selectbox(
        "탐색 기간",
        options=[value for value, _ in PERIOD_OPTIONS],
        format_func=lambda value: dict(PERIOD_OPTIONS)[value],
        key=WidgetKeys.ONBOARD_PERIOD,
    )

    if not interests:
        st.caption(":red[관심 분야를 1개 이상 선택해주세요.]")
    if not platforms:
        st.caption(":red[선호 플랫폼을 1개 이상 선택해주세요.]")

    is_valid = bool(interests) and bool(platforms)
    if st.button("다음", type="primary", disabled=not is_valid):
        try:
            profile = register_interest_profile(interests, purpose, age_group, gender, platforms, period)
        except ProfileValidationError as error:
            st.error(error.message)
        else:
            st.session_state[SessionKeys.USER_PROFILE] = profile
            st.session_state[SessionKeys.ONBOARDING_PREVIEW_KEYWORDS] = build_preview_keywords(
                profile.interests, profile.period
            )
            st.session_state[SessionKeys.ONBOARD_EDIT_MODE] = False
            st.rerun()
