"""인사이트 리포트 생성 도메인 로직 (functional-spec FR-REPORT-001/002/003, SRS FR-REPORT-005).

실제 이슈 요약(AI)·Word Cloud·Network Graph 산출 로직이 붙기 전까지, 이 모듈은
`dashboard_service`의 키워드 데이터를 재사용해 목(mock) 리포트를 생성한다. 실제 연동 시
`generate_report()` 내부만 교체하고 시그니처/반환 타입(`Report`)은 유지한다.

유사 관심사 비교 추천(FR-REPORT-005)은 실제 사용자 행동 기반 유사도 클러스터링 전까지,
`config.SIMILAR_CATEGORIES`의 고정 매핑으로 "유사 분야"를 정의한다. 산정 방법은
docs/KPI_Definitions.md와 일치시킬 것.
"""

import random
import uuid
from datetime import datetime, timezone

from config.constants import (
    CATEGORIES,
    MAX_REPORT_TITLE_LENGTH,
    NETWORK_GRAPH_NODE_TOP_N,
    REPORT_RECOMMENDED_KEYWORDS_TOP_N,
    SIMILAR_CATEGORIES,
    SIMILAR_GROUP_KEYWORDS_TOP_N,
    WORD_CLOUD_TOP_N,
)
from models.dashboard import TrendKeyword
from models.report import NetworkEdge, NetworkGraph, NetworkNode, Report, WordCloudItem
from services.dashboard_service import get_dashboard_keywords

_CATEGORY_LABELS = dict(CATEGORIES)


class ReportValidationError(Exception):
    """생성 실패 시 사용자 메시지를 함께 담는 예외 (API_Design.md §3 공통 에러 코드 기준)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def generate_report(category: str, period: str, title: str | None) -> Report:
    """조건(분야/기간)에 맞는 인사이트 리포트를 생성한다.

    Raises:
        ReportValidationError: 제목이 최대 길이를 초과할 때.
    """
    normalized_title = (title or "").strip()
    if len(normalized_title) > MAX_REPORT_TITLE_LENGTH:
        raise ReportValidationError(
            "VALID_002", f"제목은 최대 {MAX_REPORT_TITLE_LENGTH}자까지 입력할 수 있습니다."
        )

    keywords = get_dashboard_keywords(category=category, period=period).keywords
    category_label = _CATEGORY_LABELS.get(category, category)
    resolved_title = normalized_title or f"{category_label} {period} 트렌드 리포트"

    return Report(
        report_id=f"rep_{uuid.uuid4().hex[:8]}",
        title=resolved_title,
        category=category,
        period=period,
        summary=_build_summary(category_label, keywords),
        word_cloud=_build_word_cloud(keywords),
        network_graph=_build_network_graph(keywords),
        recommended_keywords=[k.keyword for k in keywords[:REPORT_RECOMMENDED_KEYWORDS_TOP_N]],
        similar_group_keywords=_build_similar_group_keywords(category, period),
        created_at=datetime.now(timezone.utc),
    )


def _build_similar_group_keywords(category: str, period: str) -> list[str]:
    """유사 분야 그룹(SIMILAR_CATEGORIES)의 Spike Score 상위 키워드를 추가 추천으로 산출한다."""
    similar_categories = SIMILAR_CATEGORIES.get(category, [])
    candidates = [
        keyword
        for similar_category in similar_categories
        for keyword in get_dashboard_keywords(category=similar_category, period=period).keywords
    ]
    candidates.sort(key=lambda item: item.spike_score, reverse=True)
    return [item.keyword for item in candidates[:SIMILAR_GROUP_KEYWORDS_TOP_N]]


def get_report_by_id(reports: list[Report], report_id: str) -> Report | None:
    """세션에 보관된 리포트 목록에서 ID로 리포트를 찾는다. 없으면 `None`."""
    return next((report for report in reports if report.report_id == report_id), None)


def _build_summary(category_label: str, keywords: list[TrendKeyword]) -> str:
    """상위 키워드를 언급하는 요약 문장을 생성한다."""
    if not keywords:
        return f"최근 {category_label} 분야에서 유의미한 트렌드 데이터를 찾지 못했습니다."

    top_names = ", ".join(k.keyword for k in keywords[:3])
    return (
        f"최근 {category_label} 분야에서는 '{top_names}' 관련 언급이 가장 활발했습니다. "
        "Spike Score 상위 키워드를 중심으로 트렌드가 형성되고 있습니다."
    )


def _build_word_cloud(keywords: list[TrendKeyword]) -> list[WordCloudItem]:
    """Spike Score를 0~1로 정규화해 Word Cloud 가중치로 사용한다."""
    top = keywords[:WORD_CLOUD_TOP_N]
    if not top:
        return []

    max_score = max(k.spike_score for k in top)
    return [WordCloudItem(keyword=k.keyword, weight=round(k.spike_score / max_score, 2)) for k in top]


def _build_network_graph(keywords: list[TrendKeyword]) -> NetworkGraph:
    """상위 키워드를 노드로, 임의의 트리 구조 연결을 엣지로 구성한다."""
    top = keywords[:NETWORK_GRAPH_NODE_TOP_N]
    nodes = [NetworkNode(id=k.keyword_id, label=k.keyword) for k in top]

    rng = random.Random(f"network:{','.join(k.keyword_id for k in top)}")
    edges = [
        NetworkEdge(
            source=top[rng.randint(0, index - 1)].keyword_id,
            target=top[index].keyword_id,
            weight=round(rng.uniform(0.2, 1.0), 2),
        )
        for index in range(1, len(top))
    ]
    return NetworkGraph(nodes=nodes, edges=edges)
