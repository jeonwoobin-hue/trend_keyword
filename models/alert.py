"""급상승 알림(ALERT-001/002) 데이터 모델.

functional-spec.md FR-ALERT-001/FR-ALERT-003 응답 계약과 일치시킨다.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class AlertRule(BaseModel):
    """등록된 급상승 알림 키워드 1건."""

    alert_id: str = Field(alias="alertId")
    keyword: str
    threshold_score: int = Field(alias="thresholdScore")
    notify_channels: list[str] = Field(alias="notifyChannels")
    created_at: datetime = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class AlertHistoryEntry(BaseModel):
    """발송된 알림 히스토리 1건 (ALERT-002)."""

    alert_history_id: str = Field(alias="alertHistoryId")
    keyword: str
    spike_score: float = Field(alias="spikeScore")
    sent_at: datetime = Field(alias="sentAt")
    channel: str
    status: str  # "sent" | "failed"
    # 공식 응답 계약에는 없는 필드. IA의 "알림 읽음 처리" UX를 시연하기 위한 목 전용 상태.
    is_read: bool = False

    model_config = {"populate_by_name": True}
