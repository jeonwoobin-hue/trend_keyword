"""로그인·회원가입 도메인 로직 (SRS FR-AUTH-001/FR-AUTH-003).

실제 인증 백엔드(JWT 발급, 이메일 발송 등, NFR-SEC-003)가 붙기 전까지, 이메일 형식과
비밀번호 최소 길이만 검증하는 목(mock) 인증이다. 회원가입의 이메일 인증도 실제 SMTP
연동 전이라 인증번호를 호출부(화면)에 그대로 반환해 보여주는 방식으로 대신한다.
실제 연동 시 내부 구현만 교체하고 공개 함수의 시그니처/반환 타입은 유지한다.
"""

import random

from config.constants import MIN_PASSWORD_LENGTH, SIGNUP_VERIFICATION_CODE_LENGTH
from models.auth import AuthUser
from utils.validators import is_valid_email


class AuthError(Exception):
    """로그인 실패 시 사용자 메시지를 함께 담는 예외 (API_Design.md §3 공통 에러 코드 기준)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def login(email: str, password: str) -> AuthUser:
    """이메일·비밀번호로 로그인한다.

    Raises:
        AuthError: 필수값 누락, 이메일 형식 오류, 비밀번호 길이 미달 시.
    """
    normalized_email = email.strip()

    if not normalized_email or not password:
        raise AuthError("VALID_001", "이메일과 비밀번호를 입력해주세요.")
    if not is_valid_email(normalized_email):
        raise AuthError("VALID_002", "올바른 이메일 형식이 아닙니다.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise AuthError("VALID_002", f"비밀번호는 최소 {MIN_PASSWORD_LENGTH}자 이상이어야 합니다.")

    display_name = normalized_email.split("@", 1)[0]
    return AuthUser(email=normalized_email, display_name=display_name)


def request_signup_verification(
    email: str,
    password: str,
    password_confirm: str,
    agreed_to_terms: bool,
) -> str:
    """가입 정보를 검증하고 이메일 인증번호를 발급한다.

    Raises:
        AuthError: 필수값 누락, 이메일 형식 오류, 비밀번호 길이·불일치, 약관 미동의 시.

    Returns:
        발급된 인증번호 (실제 이메일 발송 연동 전까지 화면에 그대로 노출한다).
    """
    normalized_email = email.strip()

    if not normalized_email or not password or not password_confirm:
        raise AuthError("VALID_001", "이메일과 비밀번호를 입력해주세요.")
    if not is_valid_email(normalized_email):
        raise AuthError("VALID_002", "올바른 이메일 형식이 아닙니다.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise AuthError("VALID_002", f"비밀번호는 최소 {MIN_PASSWORD_LENGTH}자 이상이어야 합니다.")
    if password != password_confirm:
        raise AuthError("VALID_002", "비밀번호가 일치하지 않습니다.")
    if not agreed_to_terms:
        raise AuthError("VALID_001", "약관에 동의해주세요.")

    return _generate_verification_code()


def is_verification_code_valid(input_code: str, expected_code: str) -> bool:
    """사용자가 입력한 인증번호가 발급된 인증번호와 일치하는지 확인한다."""
    return input_code.strip() == expected_code


def complete_signup(email: str) -> AuthUser:
    """이메일 인증 완료 후 계정을 생성한다."""
    normalized_email = email.strip()
    display_name = normalized_email.split("@", 1)[0]
    return AuthUser(email=normalized_email, display_name=display_name)


def _generate_verification_code() -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(SIGNUP_VERIFICATION_CODE_LENGTH))
