"""콘텐츠 큐레이션(CURATE-001) 데이터 모델.

functional-spec.md FR-CURATE-001 응답 계약과 일치시킨다.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ContentItem(BaseModel):
    """큐레이션 콘텐츠 카드 1건."""

    content_id: str = Field(alias="contentId")
    title: str
    thumbnail: str
    source: str
    platform: str
    published_at: datetime = Field(alias="publishedAt")
    url: str
    # 공식 응답 계약에는 없는 필드. 원문 삭제(RES_003) 예외 UX를 시연하기 위한 목 전용 플래그.
    is_available: bool = True

    model_config = {"populate_by_name": True}


class CurationResult(BaseModel):
    """`get_curated_contents()` 반환 타입."""

    contents: list[ContentItem]
    next_cursor: str | None = Field(default=None, alias="nextCursor")

    model_config = {"populate_by_name": True}
