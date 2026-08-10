"""services/auth_service.py 단위 테스트 (SRS FR-AUTH-001~004)."""

import pytest

from config.constants import MIN_PASSWORD_LENGTH, SIGNUP_VERIFICATION_CODE_LENGTH
from services.auth_service import (
    AuthError,
    complete_signup,
    is_verification_code_valid,
    login,
    login_with_social_provider,
    request_password_reset,
    request_signup_verification,
    reset_password,
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


def test_request_password_reset_returns_code_of_configured_length():
    code = request_password_reset("existing@example.com")

    assert len(code) == SIGNUP_VERIFICATION_CODE_LENGTH
    assert code.isdigit()


def test_request_password_reset_empty_email_raises_valid_001():
    with pytest.raises(AuthError) as exc_info:
        request_password_reset("   ")
    assert exc_info.value.code == "VALID_001"


def test_request_password_reset_invalid_email_raises_valid_002():
    with pytest.raises(AuthError) as exc_info:
        request_password_reset("not-an-email")
    assert exc_info.value.code == "VALID_002"


def test_reset_password_success_returns_none():
    assert reset_password("newpassword123", "newpassword123") is None


def test_reset_password_too_short_raises_valid_002():
    short_password = "a" * (MIN_PASSWORD_LENGTH - 1)

    with pytest.raises(AuthError) as exc_info:
        reset_password(short_password, short_password)
    assert exc_info.value.code == "VALID_002"


def test_reset_password_mismatch_raises_valid_002():
    with pytest.raises(AuthError) as exc_info:
        reset_password("newpassword123", "different123")
    assert exc_info.value.code == "VALID_002"


def test_login_with_social_provider_derives_user_from_provider():
    user = login_with_social_provider("google")

    assert user.email == "google_user@example.com"
    assert user.display_name == "google_user"
