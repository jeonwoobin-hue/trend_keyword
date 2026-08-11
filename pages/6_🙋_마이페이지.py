"""MY-001 마이페이지. 프로필 정보, 등록된 알림 키워드 조회 및 관심사 수정/로그아웃."""

import streamlit as st

from app.auth_guard import require_login
from app.session import init_session_state
from components.top_nav import render_top_nav
from config.constants import (
    AGE_GROUP_OPTIONS,
    CATEGORIES,
    PLATFORM_OPTIONS,
    PURPOSE_OPTIONS,
    SessionKeys,
)
from services.curation_service import remove_scrap

st.set_page_config(page_title="마이페이지 - TrendFit", page_icon="🙋", layout="wide")
init_session_state()
render_top_nav(current_group="mypage")

st.title("🙋 마이페이지")
require_login()

auth_user = st.session_state[SessionKeys.AUTH_USER]
st.caption(f"{auth_user.email}로 로그인 중")

st.divider()

st.markdown("#### 프로필 정보")
profile = st.session_state[SessionKeys.USER_PROFILE]

if profile is None:
    st.info("아직 관심사가 설정되지 않았습니다.")
    if st.button("관심사 설정하기", type="primary"):
        st.switch_page("pages/2_📝_관심사_설정.py")
else:
    interest_labels = dict(CATEGORIES)
    purpose_labels = dict(PURPOSE_OPTIONS)
    age_labels = dict(AGE_GROUP_OPTIONS)
    platform_labels = dict(PLATFORM_OPTIONS)

    st.write(f"**관심 분야**: {', '.join(interest_labels.get(i, i) for i in profile.interests)}")
    st.write(f"**목적**: {purpose_labels.get(profile.purpose, profile.purpose)}")
    st.write(f"**연령대**: {age_labels.get(profile.age_group, profile.age_group)}")
    st.write(f"**선호 플랫폼**: {', '.join(platform_labels.get(p, p) for p in profile.platforms)}")

    if st.button("관심사 수정"):
        st.session_state[SessionKeys.ONBOARD_EDIT_MODE] = True
        st.switch_page("pages/2_📝_관심사_설정.py")

st.divider()

st.markdown("#### 등록된 알림 키워드")
alert_rules = st.session_state[SessionKeys.ALERT_RULES]

if not alert_rules:
    st.info("등록된 알림 키워드가 없습니다.")
else:
    st.markdown(" ".join(f":blue-badge[{rule.keyword}]" for rule in alert_rules))

if st.button("급상승 알림 설정하러 가기"):
    st.switch_page("pages/5_🔔_급상승_알림.py")

st.divider()

st.markdown("#### 스크랩한 콘텐츠")
scrapped_contents = st.session_state[SessionKeys.SCRAPPED_CONTENTS]

if not scrapped_contents:
    st.info("스크랩한 콘텐츠가 없습니다.")
    if st.button("콘텐츠 큐레이션 보러 가기"):
        st.switch_page("pages/8_🎬_콘텐츠_큐레이션.py")
else:
    for content in scrapped_contents:
        with st.container(border=True):
            title_col, remove_col = st.columns([5, 1])
            with title_col:
                st.markdown(f"**{content.title}**")
                st.caption(f"{content.source} · {content.published_at:%Y-%m-%d}")
            with remove_col:
                if st.button("제거", key=f"scrap_remove_{content.content_id}", use_container_width=True):
                    st.session_state[SessionKeys.SCRAPPED_CONTENTS] = remove_scrap(
                        scrapped_contents, content.content_id
                    )
                    st.rerun()

st.divider()

st.markdown("#### 계정")
account_col, logout_col = st.columns(2)
with account_col:
    if st.button("⚙️ 계정 설정", use_container_width=True):
        st.switch_page("pages/14_⚙️_계정_설정.py")
with logout_col:
    if st.button("로그아웃", type="primary", use_container_width=True):
        st.session_state[SessionKeys.IS_AUTHENTICATED] = False
        st.session_state[SessionKeys.AUTH_USER] = None
        st.switch_page("Home.py")
