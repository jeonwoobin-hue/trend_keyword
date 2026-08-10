"""services/auth_service.py 단위 테스트 (SRS FR-AUTH-001/FR-AUTH-003)."""

import pytest

from config.constants import MIN_PASSWORD_LENGTH, SIGNUP_VERIFICATION_CODE_LENGTH
from services.auth_service import (
    AuthError,
    complete_signup,
    is_verification_code_valid,
    login,
    request_signup_verification,
)


def test_login_success_derives_display_name_from_email():
    user = login("trend.fit@example.com", "password123")

    assert user.email == "trend.fit@example.com"
    assert user.display_name == "trend.fit"


def test_login_trims_email_whitespace():
    user = login("  test@example.com  ", "password123")
    assert user.email == "test@example.com"


def test_login_empty_credentials_raise_valid_001():
    with pytest.raises(AuthError) as exc_info:
        login("", "")
    assert exc_info.value.code == "VALID_001"


def test_login_invalid_email_format_raises_valid_002():
    with pytest.raises(AuthError) as exc_info:
        login("not-an-email", "password123")
    assert exc_info.value.code == "VALID_002"


def test_login_password_too_short_raises_valid_002():
    short_password = "a" * (MIN_PASSWORD_LENGTH - 1)

    with pytest.raises(AuthError) as exc_info:
        login("test@example.com", short_password)
    assert exc_info.value.code == "VALID_002"


def test_request_signup_verification_returns_code_of_configured_length():
    code = request_signup_verification("new@example.com", "password123", "password123", True)

    assert len(code) == SIGNUP_VERIFICATION_CODE_LENGTH
    assert code.isdigit()


def test_request_signup_verification_password_mismatch_raises_valid_002():
    with pytest.raises(AuthError) as exc_info:
        request_signup_verification("new@example.com", "password123", "different123", True)
    assert exc_info.value.code == "VALID_002"


def test_request_signup_verification_terms_not_agreed_raises_valid_001():
    with pytest.raises(AuthError) as exc_info:
        request_signup_verification("new@example.com", "password123", "password123", False)
    assert exc_info.value.code == "VALID_001"


def test_request_signup_verification_invalid_email_raises_valid_002():
    with pytest.raises(AuthError) as exc_info:
        request_signup_verification("not-an-email", "password123", "password123", True)
    assert exc_info.value.code == "VALID_002"


def test_is_verification_code_valid_matches_and_trims_input():
    assert is_verification_code_valid("  123456  ", "123456") is True
    assert is_verification_code_valid("000000", "123456") is False


def test_complete_signup_derives_display_name_from_email():
    user = complete_signup("new.user@example.com")

    assert user.email == "new.user@example.com"
    assert user.display_name == "new.user"
