"""인증(COM-002) 데이터 모델."""

from pydantic import BaseModel

from config.constants import UserRole


class AuthUser(BaseModel):
    """로그인된 사용자 정보."""

    email: str
    display_name: str
    role: str = UserRole.USER
