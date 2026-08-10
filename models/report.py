"""인사이트 리포트(REPORT-001/002) 데이터 모델.

functional-spec.md FR-REPORT-001 응답 계약과 일치시킨다.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class WordCloudItem(BaseModel):
    """Word Cloud 키워드 1건."""

    keyword: str
    weight: float


class NetworkNode(BaseModel):
    """Network Graph 노드 1건."""

    id: str
    label: str


class NetworkEdge(BaseModel):
    """Network Graph 엣지 1건."""

    source: str
    target: str
    weight: float


class NetworkGraph(BaseModel):
    """키워드 연관성 Network Graph."""

    nodes: list[NetworkNode]
    edges: list[NetworkEdge]


class Report(BaseModel):
    """생성된 인사이트 리포트 1건."""

    report_id: str = Field(alias="reportId")
    title: str
    category: str
    period: str
    summary: str
    word_cloud: list[WordCloudItem] = Field(alias="wordCloud")
    network_graph: NetworkGraph = Field(alias="networkGraph")
    recommended_keywords: list[str] = Field(alias="recommendedKeywords")
    # 공식 응답 계약에는 없는 필드. 유사 관심사 그룹 비교 추천(FR-REPORT-005)을 위한 목 전용 필드.
    similar_group_keywords: list[str] = Field(default_factory=list, alias="similarGroupKeywords")
    created_at: datetime = Field(alias="createdAt")

    model_config = {"populate_by_name": True}
