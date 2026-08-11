"""로그인·회원가입·비밀번호 재설정·소셜 로그인 도메인 로직 (SRS FR-AUTH-001~004).

실제 인증 백엔드(JWT 발급, 이메일 발송 등, NFR-SEC-003)가 붙기 전까지, 이메일 형식과
비밀번호 최소 길이만 검증하는 목(mock) 인증이다. 회원가입/비밀번호 재설정의 이메일 인증도
실제 SMTP 연동 전이라 인증번호를 호출부(화면)에 그대로 반환해 보여주는 방식으로 대신한다.
소셜 로그인(FR-AUTH-002)도 실제 OAuth 연동 전이라 버튼 클릭 시 즉시 로그인 처리하는
목(mock)이다. 실제 연동 시 내부 구현만 교체하고 공개 함수의 시그니처/반환 타입은 유지한다.

비밀번호 재설정(FR-AUTH-004)은 애초에 비밀번호를 저장하는 실제 계정 저장소가 없어(로그인이
형식 검증만으로 통과되는 목이기 때문), "이전 비밀번호"라는 개념 자체가 없다. 여기서는 절차
(이메일 인증 → 새 비밀번호 설정)만 시연하며, 새 비밀번호는 실제로 저장되지 않는다.
"""

import random

from config.constants import ADMIN_EMAILS, MIN_PASSWORD_LENGTH, SIGNUP_VERIFICATION_CODE_LENGTH, UserRole
from models.auth import AuthUser
from utils.validators import is_valid_email


class AuthError(Exception):
    """로그인 실패 시 사용자 메시지를 함께 담는 예외 (API_Design.md §3 공통 에러 코드 기준)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _resolve_role(email: str) -> str:
    """이메일이 관리자 화이트리스트(config.ADMIN_EMAILS)에 있으면 관리자 역할을 부여한다."""
    if email.lower() in {admin_email.lower() for admin_email in ADMIN_EMAILS}:
        return UserRole.ADMIN
    return UserRole.USER


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
    return AuthUser(email=normalized_email, display_name=display_name, role=_resolve_role(normalized_email))


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
    return AuthUser(email=normalized_email, display_name=display_name, role=_resolve_role(normalized_email))


def _generate_verification_code() -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(SIGNUP_VERIFICATION_CODE_LENGTH))


def request_password_reset(email: str) -> str:
    """비밀번호 재설정 인증번호를 발급한다.

    Raises:
        AuthError: 이메일 미입력 또는 형식 오류 시.

    Returns:
        발급된 인증번호 (실제 이메일 발송 연동 전까지 화면에 그대로 노출한다).
    """
    normalized_email = email.strip()

    if not normalized_email:
        raise AuthError("VALID_001", "이메일을 입력해주세요.")
    if not is_valid_email(normalized_email):
        raise AuthError("VALID_002", "올바른 이메일 형식이 아닙니다.")

    return _generate_verification_code()


def reset_password(new_password: str, new_password_confirm: str) -> None:
    """새 비밀번호 형식을 검증한다.

    실제 계정 저장소가 없어 저장은 하지 않고 검증 절차만 시연한다.

    Raises:
        AuthError: 비밀번호 길이 미달 또는 확인값 불일치 시.
    """
    if len(new_password) < MIN_PASSWORD_LENGTH:
        raise AuthError("VALID_002", f"비밀번호는 최소 {MIN_PASSWORD_LENGTH}자 이상이어야 합니다.")
    if new_password != new_password_confirm:
        raise AuthError("VALID_002", "비밀번호가 일치하지 않습니다.")


def change_password(current_password: str, new_password: str, new_password_confirm: str) -> None:
    """로그인한 상태에서 비밀번호를 변경한다 (MY-002 계정 설정, FR-PROFILE-002 계정 정보 수정).

    실제 계정 저장소가 없어 현재 비밀번호는 대조하지 않고 미입력 여부만 확인한다. 새 비밀번호
    검증 규칙은 `reset_password()`와 동일하다.

    Raises:
        AuthError: 현재 비밀번호 미입력, 새 비밀번호 길이 미달, 확인값 불일치 시.
    """
    if not current_password:
        raise AuthError("VALID_001", "현재 비밀번호를 입력해주세요.")
    reset_password(new_password, new_password_confirm)


def login_with_social_provider(provider: str) -> AuthUser:
    """소셜 로그인(FR-AUTH-002)을 시뮬레이션한다.

    실제 OAuth 연동 전까지, 실제 동의 화면 없이 즉시 로그인 처리한다.
    """
    display_name = f"{provider}_user"
    email = f"{display_name}@example.com"
    return AuthUser(email=email, display_name=display_name, role=_resolve_role(email))
