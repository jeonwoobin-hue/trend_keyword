"""ADMIN-002 사용자·키워드 관리. 사용자 계정, 등록 키워드 통계, 신고 내역, 키워드 블랙리스트를 관리한다."""

import streamlit as st

from app.auth_guard import require_login
from app.session import init_session_state
from config.constants import MAX_BLACKLIST_KEYWORD_LENGTH, SessionKeys, WidgetKeys
from services.admin_service import (
    BlacklistValidationError,
    add_blacklisted_keyword,
    list_admin_users,
    list_content_reports,
    list_keyword_stats,
    remove_blacklisted_keyword,
)

st.set_page_config(page_title="사용자·키워드 관리 - TrendFit", page_icon="🗂️", layout="wide")
init_session_state()

st.title("🗂️ 사용자·키워드 관리")
st.caption(
    "관리자 전용 화면입니다. 현재는 로그인 여부만 확인하며, 역할(관리자/일반 사용자) 기반 "
    "접근 제어는 아직 구현되어 있지 않습니다."
)
require_login()
st.caption("실제 다중 사용자 DB 연동 전 단계로, 사용자 목록·키워드 통계·신고 내역은 모두 샘플 데이터입니다.")

if st.session_state[SessionKeys.ADMIN_USERS] is None:
    st.session_state[SessionKeys.ADMIN_USERS] = list_admin_users()

st.divider()
st.markdown("#### 사용자 목록")

for user in st.session_state[SessionKeys.ADMIN_USERS]:
    with st.container(border=True):
        email_col, joined_col, status_col, action_col = st.columns([3, 2, 1, 1])
        email_col.markdown(f"**{user.email}**")
        joined_col.caption(f"가입일 {user.joined_at:%Y-%m-%d}")
        with status_col:
            if user.is_suspended:
                st.badge("정지됨", color="red")
            else:
                st.badge("활성", color="green")
        with action_col:
            label = "정지 해제" if user.is_suspended else "정지"
            if st.button(label, key=f"suspend_{user.user_id}", use_container_width=True):
                user.is_suspended = not user.is_suspended
                st.rerun()

st.divider()
st.markdown("#### 등록 키워드 통계")

for stat in list_keyword_stats():
    stat_col1, stat_col2 = st.columns([3, 1])
    stat_col1.write(stat.keyword)
    stat_col2.write(f"{stat.registered_count}회")

st.divider()
st.markdown("#### 키워드 블랙리스트 관리")

blacklist = st.session_state[SessionKeys.ADMIN_BLACKLIST]

with st.form(key=WidgetKeys.ADMIN_BLACKLIST_FORM, clear_on_submit=True):
    new_keyword = st.text_input(
        "블랙리스트에 추가할 키워드", key=WidgetKeys.ADMIN_BLACKLIST_INPUT, max_chars=MAX_BLACKLIST_KEYWORD_LENGTH
    )
    submitted = st.form_submit_button("추가", type="primary")

if submitted:
    try:
        st.session_state[SessionKeys.ADMIN_BLACKLIST] = add_blacklisted_keyword(blacklist, new_keyword)
    except BlacklistValidationError as error:
        st.error(error.message)

blacklist = st.session_state[SessionKeys.ADMIN_BLACKLIST]
if not blacklist:
    st.caption("블랙리스트에 등록된 키워드가 없습니다.")
else:
    for keyword in blacklist:
        badge_col, remove_col = st.columns([4, 1])
        with badge_col:
            st.badge(keyword, color="red")
        with remove_col:
            if st.button("제거", key=f"blacklist_remove_{keyword}", use_container_width=True):
                st.session_state[SessionKeys.ADMIN_BLACKLIST] = remove_blacklisted_keyword(blacklist, keyword)
                st.rerun()

st.divider()
st.markdown("#### 신고 내역")

reports = list_content_reports()
if not reports:
    st.caption("신고된 콘텐츠가 없습니다.")
else:
    for report in reports:
        with st.container(border=True):
            st.markdown(f"**{report.content_title}**")
            st.caption(f"사유: {report.reason} · {report.reported_at:%Y-%m-%d %H:%M} UTC")
