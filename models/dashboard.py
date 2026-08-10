"""트렌드 대시보드(DASH-001) API 응답 계약.

functional-spec.md FR-DASH-001 `GET /api/v1/dashboard/keywords` 응답 형태와 일치시킨다.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class TrendPoint(BaseModel):
    """언급량 추이 그래프의 한 지점."""

    label: str
    mention_count: int = Field(alias="mentionCount")

    model_config = {"populate_by_name": True}


class TrendKeyword(BaseModel):
    """대시보드 키워드 카드 1건."""

    keyword_id: str = Field(alias="keywordId")
    keyword: str
    category: str
    mention_count: int = Field(alias="mentionCount")
    spike_score: float = Field(alias="spikeScore")
    trend_graph: list[TrendPoint] = Field(alias="trendGraph")

    model_config = {"populate_by_name": True}


class DashboardMeta(BaseModel):
    """대시보드 응답 부가 정보."""

    period: str
    updated_at: datetime = Field(alias="updatedAt")
    is_delayed: bool = Field(default=False, alias="isDelayed")

    model_config = {"populate_by_name": True}


class DashboardKeywordsResult(BaseModel):
    """`get_dashboard_keywords()` 반환 타입."""

    keywords: list[TrendKeyword]
    meta: DashboardMeta


class SentimentRatio(BaseModel):
    """긍·부정·중립 감성 비율 (합 1.0)."""

    positive: float
    negative: float
    neutral: float


class DemographicWeights(BaseModel):
    """연령·성별 관심도 가중치 보정 (SRS FR-DASH-005, P2). 각 그룹 비중의 합은 1.0."""

    age_group_weights: dict[str, float] = Field(alias="ageGroupWeights")
    gender_weights: dict[str, float] = Field(alias="genderWeights")

    model_config = {"populate_by_name": True}


class KeywordDetail(BaseModel):
    """키워드 상세(DASH-002) 응답. `sentiment`는 데이터 부족 시 None(VALID_003)."""

    keyword_id: str = Field(alias="keywordId")
    keyword: str
    category: str
    trend_series: list[TrendPoint] = Field(alias="trendSeries")
    sentiment: SentimentRatio | None = None
    related_keywords: list[str] = Field(alias="relatedKeywords")
    demographics: DemographicWeights = Field(alias="demographics")

    model_config = {"populate_by_name": True}
