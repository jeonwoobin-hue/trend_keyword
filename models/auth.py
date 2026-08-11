"""인증(COM-002) 데이터 모델."""

from pydantic import BaseModel

from config.constants import UserRole


class AuthUser(BaseModel):
    """로그인된 사용자 정보."""

    id: str
    email: str
    display_name: str
    role: str = UserRole.USER


class AuthSession(BaseModel):
    """Supabase Auth 세션 토큰.

    `AuthUser`는 화면 표시용 데이터라 분리하고, 이후 인증이 필요한 요청(비밀번호 변경 등)에 쓰는
    토큰만 따로 담는다.
    """

    access_token: str
    refresh_token: str
