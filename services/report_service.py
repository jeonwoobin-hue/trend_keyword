"""인사이트 리포트 생성 도메인 로직 (functional-spec FR-REPORT-001/002/003, SRS FR-REPORT-005).

이슈 요약(FR-REPORT-002)은 2026-08-18부터 Gemini API로 실제 생성한다(`_generate_ai_summary()`,
docs/Prompt_Guide.md 원칙 준수). 키 미설정·네트워크 오류·빈 응답 등 어떤 이유로든 호출이 실패하면
`_build_fallback_summary()`(상위 키워드를 언급하는 고정 템플릿)로 대체한다 — 리포트 생성 자체가
AI 가용성에 좌우되지 않도록 하기 위한 의도적 설계(사용자 확인 완료, product/CHANGELOG.md 참고).

키워드 연관성 지도(FR-REPORT-003)의 Network Graph는 `utils/statistics.pearson_correlation()`로
언급량 추이 시계열 간 상관관계를 실제로 계산해 연결한다(docs/KPI_Definitions.md 참고) — 노드는
여전히 목 데이터(`dashboard_service`의 시계열)이지만, 어떤 키워드끼리 연결되는지는 그 데이터에서
정직하게 산출된다.

유사 관심사 비교 추천(FR-REPORT-005)은 실제 사용자 행동 기반 유사도 클러스터링 전까지,
`config.SIMILAR_CATEGORIES`의 고정 매핑으로 "유사 분야"를 정의한다. 산정 방법은
docs/KPI_Definitions.md와 일치시킬 것.
"""

import logging
import uuid
from datetime import datetime, timezone

from config.constants import (
    CATEGORIES,
    GEMINI_SUMMARY_MODEL,
    MAX_REPORT_TITLE_LENGTH,
    NETWORK_GRAPH_NODE_TOP_N,
    PERIOD_OPTIONS,
    REPORT_RECOMMENDED_KEYWORDS_TOP_N,
    SIMILAR_CATEGORIES,
    SIMILAR_GROUP_KEYWORDS_TOP_N,
    WORD_CLOUD_TOP_N,
)
from models.dashboard import TrendKeyword
from models.report import NetworkEdge, NetworkGraph, NetworkNode, Report, WordCloudItem
from services.dashboard_service import get_dashboard_keywords
from services.gemini_client import create_gemini_client
from utils.statistics import pearson_correlation

logger = logging.getLogger(__name__)

_CATEGORY_LABELS = dict(CATEGORIES)
_PERIOD_LABELS = dict(PERIOD_OPTIONS)


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
        summary=_build_summary(category_label, keywords, period),
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


def _build_summary(category_label: str, keywords: list[TrendKeyword], period: str) -> str:
    """이슈 요약(FR-REPORT-002)을 Gemini로 생성하고, 실패하면 고정 템플릿으로 대체한다."""
    fallback = _build_fallback_summary(category_label, keywords)
    if not keywords:
        return fallback

    try:
        return _generate_ai_summary(category_label, keywords, period)
    except Exception:
        logger.exception("Gemini 이슈 요약 생성 실패 - 고정 템플릿으로 대체합니다.")
        return fallback


def _generate_ai_summary(category_label: str, keywords: list[TrendKeyword], period: str) -> str:
    """상위 키워드 데이터를 근거로 Gemini에 이슈 요약 생성을 요청한다."""
    client = create_gemini_client()
    response = client.models.generate_content(
        model=GEMINI_SUMMARY_MODEL,
        contents=_build_summary_prompt(category_label, keywords, period),
    )
    text = (response.text or "").strip()
    if not text:
        raise ValueError("Gemini가 빈 응답을 반환했습니다.")
    return text


def _build_summary_prompt(category_label: str, keywords: list[TrendKeyword], period: str) -> str:
    """docs/Prompt_Guide.md 원칙(핵심 결과·근거·불확실성 표시)을 반영한 프롬프트를 만든다."""
    period_label = _PERIOD_LABELS.get(period, period)
    top = keywords[:3]
    keyword_lines = "\n".join(f"- {k.keyword} (Spike Score {k.spike_score:.1f})" for k in top)

    return (
        "당신은 트렌드 인사이트 플랫폼 TrendFit의 리포트 작성자입니다.\n"
        f"아래는 '{category_label}' 분야의 {period_label} 언급량 기준 상위 키워드입니다:\n"
        f"{keyword_lines}\n\n"
        "이 데이터를 근거로 이슈 요약을 한국어 2~3문장으로 작성하세요. 다음을 반드시 지키세요.\n"
        "1. 어떤 트렌드가 형성되고 있는지 핵심 결과를 먼저 제시할 것\n"
        f"2. 근거로 위 키워드명과 '{period_label} 언급량 기준'이라는 표현을 자연스럽게 포함할 것\n"
        "3. 전문 용어를 최소화하고 이해하기 쉬운 문장으로 쓸 것\n"
        "4. 목록이나 마크다운 서식(별표, 헤더 등) 없이 자연스러운 문단으로 쓸 것\n"
        "5. 위에 없는 사실을 추측해서 덧붙이지 말 것"
    )


def _build_fallback_summary(category_label: str, keywords: list[TrendKeyword]) -> str:
    """Gemini 호출이 실패하거나 데이터가 없을 때 쓰는 고정 템플릿 요약."""
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
