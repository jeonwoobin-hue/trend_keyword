"""관심사 프로필(ONBOARD-001) 데이터 모델.

functional-spec.md FR-ONBOARD-001 요청 계약과 일치시킨다.
"""

from pydantic import BaseModel, Field


class InterestProfile(BaseModel):
    """사용자 관심사 프로필."""

    interests: list[str]
    purpose: str
    age_group: str = Field(alias="ageGroup")
    gender: str | None = None
    platforms: list[str]
    period: str

    model_config = {"populate_by_name": True}
