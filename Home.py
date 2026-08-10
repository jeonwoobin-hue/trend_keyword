"""Streamlit 진입점. 실행: streamlit run Home.py

랜딩(COM-001): 서비스 소개, 핵심 가치 문구, 시작하기/로그인 진입, 대표 트렌드 미리보기.
"""

import streamlit as st

from app.session import init_session_state
from config.constants import (
    PAGE_ICON,
    PAGE_LAYOUT,
    PAGE_TITLE,
    SERVICE_DESCRIPTION,
    SERVICE_TAGLINE,
)

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=PAGE_LAYOUT)
init_session_state()

st.title(f"{PAGE_ICON} {PAGE_TITLE}")
st.subheader(SERVICE_TAGLINE)
st.write(SERVICE_DESCRIPTION)

st.divider()

col_start, col_login = st.columns(2)
with col_start:
    if st.button("시작하기", type="primary", use_container_width=True):
        st.switch_page("pages/2_📝_관심사_설정.py")
with col_login:
    if st.button("로그인", use_container_width=True):
        st.switch_page("pages/0_🔑_로그인.py")

st.divider()

st.subheader("대표 트렌드 미리보기")
st.caption("분야별 핫 키워드는 대시보드 연동 후 이곳에 표시됩니다.")
st.info("데이터 연동 준비 중입니다.")
