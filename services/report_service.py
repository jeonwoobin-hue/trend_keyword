"""인사이트 리포트 생성 도메인 로직 (functional-spec FR-REPORT-001/002/003, SRS FR-REPORT-005).

실제 이슈 요약(AI) 산출 로직이 붙기 전까지, `_build_summary()`는 상위 키워드를 언급하는 고정
템플릿 문장을 생성한다. 실제 연동 시 `generate_report()` 내부만 교체하고 시그니처/반환 타입
(`Report`)은 유지한다.

키워드 연관성 지도(FR-REPORT-003)의 Network Graph는 `utils/statistics.pearson_correlation()`로
언급량 추이 시계열 간 상관관계를 실제로 계산해 연결한다(docs/KPI_Definitions.md 참고) — 노드는
여전히 목 데이터(`dashboard_service`의 시계열)이지만, 어떤 키워드끼리 연결되는지는 그 데이터에서
정직하게 산출된다.

유사 관심사 비교 추천(FR-REPORT-005)은 실제 사용자 행동 기반 유사도 클러스터링 전까지,
`config.SIMILAR_CATEGORIES`의 고정 매핑으로 "유사 분야"를 정의한다. 산정 방법은
docs/KPI_Definitions.md와 일치시킬 것.
"""

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
from utils.statistics import pearson_correlation

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
    """상위 키워드를 노드로, 언급량 추이 상관관계가 가장 높은 키워드끼리 연결한다.

    각 키워드를 그보다 먼저 놓인 키워드들 중 언급량 시계열이 가장 비슷하게 움직인(피어슨
    상관계수 절댓값이 가장 큰) 것과 연결한다 — 트리 구조(노드 N개에 엣지 N-1개)는 유지하되,
    "어디에 연결할지"를 실제 데이터로 정한다(docs/KPI_Definitions.md 참고).
    """
    top = keywords[:NETWORK_GRAPH_NODE_TOP_N]
    nodes = [NetworkNode(id=k.keyword_id, label=k.keyword) for k in top]
    series = {k.keyword_id: [point.mention_count for point in k.trend_graph] for k in top}

    edges = []
    for index in range(1, len(top)):
        candidates = top[:index]
        best_candidate = max(
            candidates,
            key=lambda candidate: abs(pearson_correlation(series[top[index].keyword_id], series[candidate.keyword_id])),
        )
        correlation = pearson_correlation(series[top[index].keyword_id], series[best_candidate.keyword_id])
        edges.append(
            NetworkEdge(
                source=best_candidate.keyword_id,
                target=top[index].keyword_id,
                weight=round(abs(correlation), 2),
            )
        )
    return NetworkGraph(nodes=nodes, edges=edges)
