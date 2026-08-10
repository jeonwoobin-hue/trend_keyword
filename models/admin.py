"""관리자 대시보드(ADMIN-001) 데이터 모델."""

from datetime import datetime

from pydantic import BaseModel, Field


class DataSourceStatus(BaseModel):
    """외부 데이터 소스 연동 상태 1건."""

    source_id: str = Field(alias="sourceId")
    source_label: str = Field(alias="sourceLabel")
    status: str  # API_Design.md §8 기준 현재는 전부 "not_integrated"

    model_config = {"populate_by_name": True}


class SpikeBatchStatus(BaseModel):
    """Spike Score 배치 최근 실행 현황 (functional-spec FR-DASH-003)."""

    last_run_at: datetime = Field(alias="lastRunAt")
    updated_keyword_count: int = Field(alias="updatedKeywordCount")
    failed_keyword_count: int = Field(alias="failedKeywordCount")

    model_config = {"populate_by_name": True}


class AdminUser(BaseModel):
    """사용자 관리(ADMIN-002) 목록 1건. 실제 다중 사용자 DB 연동 전까지는 샘플 데이터."""

    user_id: str = Field(alias="userId")
    email: str
    joined_at: datetime = Field(alias="joinedAt")
    is_suspended: bool = Field(default=False, alias="isSuspended")

    model_config = {"populate_by_name": True}


class KeywordStat(BaseModel):
    """등록 키워드 통계(ADMIN-002) 1건."""

    keyword: str
    registered_count: int = Field(alias="registeredCount")

    model_config = {"populate_by_name": True}


class ContentReport(BaseModel):
    """콘텐츠 신고 내역(ADMIN-002) 1건."""

    report_id: str = Field(alias="reportId")
    content_title: str = Field(alias="contentTitle")
    reason: str
    reported_at: datetime = Field(alias="reportedAt")

    model_config = {"populate_by_name": True}
