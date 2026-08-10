"""여러 화면에서 재사용되는 키워드 카드 UI 컴포넌트 (UI_UX_Rules.md §5)."""

import pandas as pd
import streamlit as st

from config.constants import CATEGORIES
from models.dashboard import TrendKeyword

_CATEGORY_LABELS = dict(CATEGORIES)


def render_keyword_card(rank: int, keyword: TrendKeyword) -> bool:
    """키워드 카드 1건을 렌더링한다.

    Returns:
        카드 내 "상세보기" 버튼이 이번 렌더에서 클릭되었는지 여부.
    """
    with st.container(border=True):
        header_col, score_col = st.columns([3, 1])
        with header_col:
            st.markdown(f"**{rank}. {keyword.keyword}**")
            st.caption(_CATEGORY_LABELS.get(keyword.category, keyword.category))
        with score_col:
            st.metric("Spike Score", f"{keyword.spike_score:.1f}")

        st.caption(f"언급량 {keyword.mention_count:,}건")

        trend_df = pd.DataFrame(
            [{"구간": point.label, "언급량": point.mention_count} for point in keyword.trend_graph]
        ).set_index("구간")
        st.line_chart(trend_df, height=120)

        return st.button(
            "상세보기",
            key=f"keyword_detail_{keyword.keyword_id}",
            use_container_width=True,
        )
