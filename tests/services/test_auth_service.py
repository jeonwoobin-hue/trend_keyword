"""services/auth_service.py 단위 테스트 (SRS FR-AUTH-001~004).

`services.auth_service`는 이제 Supabase Auth/`trendfit.profiles`에 실제로 접속한다. 네트워크 호출
없이 검증하기 위해 `create_supabase_client`를 얇은 가짜 클라이언트로 대체(monkeypatch)한다 —
`services/supabase_client.py` 자체의 접속 로직은 이 테스트의 대상이 아니다.
"""

from types import SimpleNamespace

import pytest
from supabase_auth.errors import AuthApiError

import services.auth_service as auth_service
from config.constants import ADMIN_EMAILS, MIN_PASSWORD_LENGTH, UserRole
from services.auth_service import (
    AuthError,
    change_password,
    complete_signup,
    complete_social_login,
    delete_account,
    get_social_login_url,
    login,
    request_password_reset,
    request_signup_verification,
    reset_password,
    update_display_name,
)


class _FakeQueryBuilder:
    """`.table("profiles").select(...).eq(...).execute()` 형태의 체이닝을 흉내낸다.

    실제 호출에서 쓰는 메서드(select/insert/update/eq/maybe_single)는 전부 self를 반환해 체이닝만
    유지하고, `execute()`만 `responses`에서 마지막으로 호출된 연산(select/insert/update)에 대응하는
    결과를 돌려준다.
    """

    def __init__(self, responses: dict):
        self._responses = responses
        self._operation = None

    def select(self, *_args, **_kwargs):
        self._operation = "select"
        return self

    def insert(self, *_args, **_kwargs):
        self._operation = "insert"
        return self

    def update(self, *_args, **_kwargs):
        self._operation = "update"
        return self

    def eq(self, *_args, **_kwargs):
        return self

    def maybe_single(self):
        return self

    def execute(self):
        return self._responses[self._operation]


class _FakeAuth:
    """`client.auth.*` 호출을 테스트별로 지정한 함수/예외로 대체한다."""

    def __init__(self, **overrides):
        self._overrides = overrides

    def __getattr__(self, name):
        return self._overrides.get(name, lambda *args, **kwargs: None)


class _FakeClient:
    def __init__(self, auth: _FakeAuth | None = None, table_responses: dict | None = None):
        self.auth = auth or _FakeAuth()
        self._table_responses = table_responses or {}

    def table(self, _name: str):
        return _FakeQueryBuilder(self._table_responses)


def _patch_client(monkeypatch, client: _FakeClient) -> None:
    monkeypatch.setattr(auth_service, "create_supabase_client", lambda access_token=None: client)


def _fake_auth_response(user_id: str = "uuid-1", email: str = "trend.fit@example.com"):
    user = SimpleNamespace(id=user_id, email=email)
    session = SimpleNamespace(access_token="access-token", refresh_token="refresh-token")
    return SimpleNamespace(user=user, session=session)


def _profile_row(display_name: str, role: str = UserRole.USER) -> dict:
    return {"display_name": display_name, "role": role}


# --- login ---


def test_login_success_returns_user_and_session(monkeypatch):
    auth_response = _fake_auth_response(email="trend.fit@example.com")
    client = _FakeClient(
        auth=_FakeAuth(sign_in_with_password=lambda _creds: auth_response),
        table_responses={"select": SimpleNamespace(data=_profile_row("trend.fit"))},
    )
    _patch_client(monkeypatch, client)

    user, session = login("trend.fit@example.com", "password123")

    assert user.id == "uuid-1"
    assert user.email == "trend.fit@example.com"
    assert user.display_name == "trend.fit"
    assert user.role == UserRole.USER
    assert session.access_token == "access-token"


def test_login_bootstraps_profile_on_first_login(monkeypatch):
    admin_email = ADMIN_EMAILS[0]
    auth_response = _fake_auth_response(email=admin_email)
    client = _FakeClient(
        auth=_FakeAuth(sign_in_with_password=lambda _creds: auth_response),
        table_responses={
            # maybe_single().execute()는 일치하는 행이 없으면 None을 그대로 반환한다(postgrest-py).
            "select": None,
            "insert": SimpleNamespace(data=[_profile_row(admin_email.split("@")[0], UserRole.ADMIN)]),
        },
    )
    _patch_client(monkeypatch, client)

    user, _session = login(admin_email, "password123")

    assert user.role == UserRole.ADMIN


def test_login_auth_failure_raises_valid_002(monkeypatch):
    def _raise(_creds):
        raise AuthApiError("invalid_grant", 400, "invalid_credentials")

    client = _FakeClient(auth=_FakeAuth(sign_in_with_password=_raise))
    _patch_client(monkeypatch, client)

    with pytest.raises(AuthError) as exc_info:
        login("trend.fit@example.com", "wrong-password")
    assert exc_info.value.code == "VALID_002"


def test_login_empty_credentials_raise_valid_001():
    with pytest.raises(AuthError) as exc_info:
        login("", "")
    assert exc_info.value.code == "VALID_001"


def test_login_invalid_email_format_raises_valid_002():
    with pytest.raises(AuthError) as exc_info:
        login("not-an-email", "password123")
    assert exc_info.value.code == "VALID_002"


# --- request_signup_verification ---


def test_request_signup_verification_success_returns_none(monkeypatch):
    client = _FakeClient(auth=_FakeAuth(sign_up=lambda _creds: None))
    _patch_client(monkeypatch, client)

    assert request_signup_verification("new@example.com", "password123", "password123", True) is None


def test_request_signup_verification_already_registered_raises_valid_003(monkeypatch):
    def _raise(_creds):
        raise AuthApiError("user already registered", 400, "user_already_exists")

    client = _FakeClient(auth=_FakeAuth(sign_up=_raise))
    _patch_client(monkeypatch, client)

    with pytest.raises(AuthError) as exc_info:
        request_signup_verification("new@example.com", "password123", "password123", True)
    assert exc_info.value.code == "VALID_003"


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


def test_request_signup_verification_supabase_rejected_email_raises_valid_002(monkeypatch):
    """로컬 정규식은 통과하지만 Supabase가 예약 도메인 등으로 거부하는 이메일(email_address_invalid)."""

    def _raise(_creds):
        raise AuthApiError("email address invalid", 400, "email_address_invalid")

    client = _FakeClient(auth=_FakeAuth(sign_up=_raise))
    _patch_client(monkeypatch, client)

    with pytest.raises(AuthError) as exc_info:
        request_signup_verification("new@example.com", "password123", "password123", True)
    assert exc_info.value.code == "VALID_002"


def test_request_signup_verification_unknown_supabase_error_raises_server_005(monkeypatch):
    def _raise(_creds):
        raise AuthApiError("rate limited", 429, "over_email_send_rate_limit")

    client = _FakeClient(auth=_FakeAuth(sign_up=_raise))
    _patch_client(monkeypatch, client)

    with pytest.raises(AuthError) as exc_info:
        request_signup_verification("new@example.com", "password123", "password123", True)
    assert exc_info.value.code == "SERVER_005"


# --- complete_signup ---


def test_complete_signup_success_returns_user_and_session(monkeypatch):
    auth_response = _fake_auth_response(email="new.user@example.com")
    client = _FakeClient(
        auth=_FakeAuth(verify_otp=lambda _params: auth_response),
        table_responses={
            "select": None,  # maybe_single().execute()는 일치하는 행이 없으면 None을 그대로 반환한다.
            "insert": SimpleNamespace(data=[_profile_row("new.user")]),
        },
    )
    _patch_client(monkeypatch, client)

    user, session = complete_signup("new.user@example.com", "123456")

    assert user.email == "new.user@example.com"
    assert user.display_name == "new.user"
    assert session.access_token == "access-token"


def test_complete_signup_invalid_code_raises_valid_002(monkeypatch):
    def _raise(_params):
        raise AuthApiError("otp expired", 403, "otp_expired")

    client = _FakeClient(auth=_FakeAuth(verify_otp=_raise))
    _patch_client(monkeypatch, client)

    with pytest.raises(AuthError) as exc_info:
        complete_signup("new.user@example.com", "000000")
    assert exc_info.value.code == "VALID_002"


# --- request_password_reset ---


def test_request_password_reset_success_returns_none(monkeypatch):
    client = _FakeClient(auth=_FakeAuth(reset_password_email=lambda _email: None))
    _patch_client(monkeypatch, client)

    assert request_password_reset("existing@example.com") is None


def test_request_password_reset_empty_email_raises_valid_001():
    with pytest.raises(AuthError) as exc_info:
        request_password_reset("   ")
    assert exc_info.value.code == "VALID_001"


def test_request_password_reset_invalid_email_raises_valid_002():
    with pytest.raises(AuthError) as exc_info:
        request_password_reset("not-an-email")
    assert exc_info.value.code == "VALID_002"


# --- reset_password ---


def test_reset_password_success_returns_none(monkeypatch):
    auth_response = _fake_auth_response(email="existing@example.com")
    client = _FakeClient(auth=_FakeAuth(verify_otp=lambda _params: auth_response))
    _patch_client(monkeypatch, client)

    assert reset_password("existing@example.com", "123456", "newpassword123", "newpassword123") is None


def test_reset_password_invalid_code_raises_valid_002(monkeypatch):
    def _raise(_params):
        raise AuthApiError("otp expired", 403, "otp_expired")

    client = _FakeClient(auth=_FakeAuth(verify_otp=_raise))
    _patch_client(monkeypatch, client)

    with pytest.raises(AuthError) as exc_info:
        reset_password("existing@example.com", "000000", "newpassword123", "newpassword123")
    assert exc_info.value.code == "VALID_002"


def test_reset_password_too_short_raises_valid_002():
    short_password = "a" * (MIN_PASSWORD_LENGTH - 1)

    with pytest.raises(AuthError) as exc_info:
        reset_password("existing@example.com", "123456", short_password, short_password)
    assert exc_info.value.code == "VALID_002"


def test_reset_password_mismatch_raises_valid_002():
    with pytest.raises(AuthError) as exc_info:
        reset_password("existing@example.com", "123456", "newpassword123", "different123")
    assert exc_info.value.code == "VALID_002"


# --- change_password ---


def test_change_password_success_returns_new_session(monkeypatch):
    auth_response = _fake_auth_response(email="trend.fit@example.com")
    client = _FakeClient(
        auth=_FakeAuth(sign_in_with_password=lambda _creds: auth_response),
        table_responses={"select": SimpleNamespace(data=_profile_row("trend.fit"))},
    )
    _patch_client(monkeypatch, client)

    session = change_password("trend.fit@example.com", "oldpassword123", "newpassword123", "newpassword123")

    assert session.access_token == "access-token"


def test_change_password_current_password_wrong_raises_valid_002(monkeypatch):
    def _raise(_creds):
        raise AuthApiError("invalid_grant", 400, "invalid_credentials")

    client = _FakeClient(auth=_FakeAuth(sign_in_with_password=_raise))
    _patch_client(monkeypatch, client)

    with pytest.raises(AuthError) as exc_info:
        change_password("trend.fit@example.com", "wrong-password", "newpassword123", "newpassword123")
    assert exc_info.value.code == "VALID_002"


def test_change_password_missing_current_raises_valid_001():
    with pytest.raises(AuthError) as exc_info:
        change_password("trend.fit@example.com", "", "newpassword123", "newpassword123")
    assert exc_info.value.code == "VALID_001"


def test_change_password_new_password_too_short_raises_valid_002():
    short_password = "a" * (MIN_PASSWORD_LENGTH - 1)

    with pytest.raises(AuthError) as exc_info:
        change_password("trend.fit@example.com", "oldpassword123", short_password, short_password)
    assert exc_info.value.code == "VALID_002"


def test_change_password_mismatch_raises_valid_002():
    with pytest.raises(AuthError) as exc_info:
        change_password("trend.fit@example.com", "oldpassword123", "newpassword123", "different123")
    assert exc_info.value.code == "VALID_002"


# --- update_display_name ---


def test_update_display_name_success_returns_trimmed_name(monkeypatch):
    client = _FakeClient(table_responses={"update": SimpleNamespace(data=None)})
    _patch_client(monkeypatch, client)

    assert update_display_name("access-token", "uuid-1", "  새 이름  ") == "새 이름"


def test_update_display_name_blank_raises_valid_001():
    with pytest.raises(AuthError) as exc_info:
        update_display_name("access-token", "uuid-1", "   ")
    assert exc_info.value.code == "VALID_001"


# --- delete_account ---


class _FakeAdminAPI:
    def __init__(self, delete_user=None):
        self._delete_user = delete_user or (lambda _id: None)

    def delete_user(self, user_id: str):
        return self._delete_user(user_id)


class _FakeAdminAuth:
    def __init__(self, admin: _FakeAdminAPI):
        self.admin = admin


class _FakeAdminClient:
    def __init__(self, admin: _FakeAdminAPI):
        self.auth = _FakeAdminAuth(admin)


def test_delete_account_success_returns_none(monkeypatch):
    calls = []
    admin_client = _FakeAdminClient(_FakeAdminAPI(delete_user=lambda user_id: calls.append(user_id)))
    monkeypatch.setattr(auth_service, "get_supabase_admin_client", lambda: admin_client)

    assert delete_account("uuid-1") is None
    assert calls == ["uuid-1"]


def test_delete_account_failure_raises_server_005(monkeypatch):
    def _raise(_user_id):
        raise AuthApiError("not found", 404, "user_not_found")

    admin_client = _FakeAdminClient(_FakeAdminAPI(delete_user=_raise))
    monkeypatch.setattr(auth_service, "get_supabase_admin_client", lambda: admin_client)

    with pytest.raises(AuthError) as exc_info:
        delete_account("uuid-1")
    assert exc_info.value.code == "SERVER_005"


# --- get_social_login_url / complete_social_login (OAuth PKCE) ---


def test_get_social_login_url_embeds_provider_and_challenge(monkeypatch):
    monkeypatch.setattr(
        auth_service, "get_secret_section", lambda _section: {"url": "https://proj.supabase.co"}
    )

    url, verifier = get_social_login_url("google", "http://localhost:8501/로그인")

    assert url.startswith("https://proj.supabase.co/auth/v1/authorize?")
    assert "provider=google" in url
    assert "code_challenge=" in url
    assert "code_challenge_method=s256" in url
    assert len(verifier) == 64
    assert verifier not in url  # URL에는 challenge(해시값)만 담기고 verifier 원문은 없어야 한다


def test_get_social_login_url_without_scopes_omits_scopes_param(monkeypatch):
    monkeypatch.setattr(
        auth_service, "get_secret_section", lambda _section: {"url": "https://proj.supabase.co"}
    )

    url, _ = get_social_login_url("google", "http://localhost:8501/로그인")

    assert "scopes=" not in url


def test_get_social_login_url_with_scopes_includes_them(monkeypatch):
    monkeypatch.setattr(
        auth_service, "get_secret_section", lambda _section: {"url": "https://proj.supabase.co"}
    )

    url, _ = get_social_login_url(
        "kakao", "http://localhost:8501/로그인", scopes="profile_nickname profile_image"
    )

    assert "scopes=profile_nickname" in url


def test_get_social_login_url_different_calls_produce_different_verifiers(monkeypatch):
    monkeypatch.setattr(
        auth_service, "get_secret_section", lambda _section: {"url": "https://proj.supabase.co"}
    )

    _, verifier_a = get_social_login_url("google", "http://localhost:8501/로그인")
    _, verifier_b = get_social_login_url("kakao", "http://localhost:8501/로그인")

    assert verifier_a != verifier_b


def test_complete_social_login_success_returns_user_and_session(monkeypatch):
    auth_response = _fake_auth_response(user_id="uuid-oauth", email="oauth.user@example.com")
    client = _FakeClient(
        auth=_FakeAuth(exchange_code_for_session=lambda _params: auth_response),
        table_responses={
            "select": None,
            "insert": SimpleNamespace(data=[_profile_row("oauth.user")]),
        },
    )
    _patch_client(monkeypatch, client)

    user, session = complete_social_login("auth-code", "code-verifier")

    assert user.id == "uuid-oauth"
    assert user.email == "oauth.user@example.com"
    assert session.access_token == "access-token"


def test_complete_social_login_invalid_code_raises_valid_002(monkeypatch):
    def _raise(_params):
        raise AuthApiError("invalid code", 400, "bad_code_verifier")

    client = _FakeClient(auth=_FakeAuth(exchange_code_for_session=_raise))
    _patch_client(monkeypatch, client)

    with pytest.raises(AuthError) as exc_info:
        complete_social_login("auth-code", "wrong-verifier")
    assert exc_info.value.code == "VALID_002"
