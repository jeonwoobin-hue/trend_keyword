"""로그인·회원가입·비밀번호 재설정·소셜 로그인 도메인 로직 (SRS FR-AUTH-001~004).

Supabase Auth(`auth.users`)로 인증하고, TrendFit 전용 필드(표시 이름·역할)는 `trendfit.profiles`에
따로 둔다(services/supabase_client.py, supabase/migrations/ 참고). 이메일 인증(FR-AUTH-003)과
비밀번호 재설정(FR-AUTH-004)은 Supabase의 이메일 OTP(6자리 코드) 방식을 쓴다 — Supabase 프로젝트
Authentication → Email Templates에서 "Confirm signup"·"Reset password" 템플릿에 `{{ .Token }}`이
포함되도록 설정되어 있어야 실제로 코드가 발송된다(기본 템플릿은 링크 방식, ops/Deployment.md 참고).

소셜 로그인(FR-AUTH-002, P2)은 실제 OAuth 연동 전이라 여전히 목(mock)이다 — 실제 연동 시 Supabase
Authentication → Providers 설정과 Streamlit의 리다이렉트 처리(별도 작업)가 필요하다.
"""

from supabase_auth.errors import AuthApiError

from config.constants import ADMIN_EMAILS, MIN_PASSWORD_LENGTH, UserRole
from models.auth import AuthSession, AuthUser
from services.supabase_client import create_supabase_client, get_supabase_admin_client
from utils.validators import is_valid_email


class AuthError(Exception):
    """실패 시 사용자 메시지를 함께 담는 예외 (API_Design.md §3 공통 에러 코드 기준)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _resolve_role(email: str) -> str:
    """이메일이 관리자 화이트리스트(config.ADMIN_EMAILS)에 있으면 관리자 역할을 부여한다.

    실제 다중 관리자 관리 기능(FR-ADMIN-002)이 붙기 전까지, 최초 프로필 생성 시에만 이 화이트리스트로
    role을 결정한다. 이후 role 변경은 DB의 `trendfit.profiles.role`을 직접 갱신한다.
    """
    if email.lower() in {admin_email.lower() for admin_email in ADMIN_EMAILS}:
        return UserRole.ADMIN
    return UserRole.USER


def _session_to_model(session) -> AuthSession:
    return AuthSession(access_token=session.access_token, refresh_token=session.refresh_token)


def _load_or_create_profile(client, user_id: str, email: str) -> dict:
    """`trendfit.profiles`에서 프로필을 가져오고, 없으면(최초 로그인/가입 직후) 만든다."""
    existing = client.table("profiles").select("*").eq("id", user_id).maybe_single().execute()
    if existing.data:
        return existing.data

    display_name = email.split("@", 1)[0]
    created = (
        client.table("profiles")
        .insert({"id": user_id, "display_name": display_name, "role": _resolve_role(email)})
        .execute()
    )
    return created.data[0]


def _authenticate(email: str, password: str, error_message: str) -> tuple[AuthUser, AuthSession]:
    """이메일·비밀번호로 Supabase Auth 세션을 만들고, 프로필까지 채운 `AuthUser`를 반환한다."""
    client = create_supabase_client()
    try:
        auth_response = client.auth.sign_in_with_password({"email": email, "password": password})
    except AuthApiError as error:
        raise AuthError("VALID_002", error_message) from error

    user, session = auth_response.user, auth_response.session
    scoped_client = create_supabase_client(access_token=session.access_token)
    profile = _load_or_create_profile(scoped_client, user.id, user.email)

    auth_user = AuthUser(id=user.id, email=user.email, display_name=profile["display_name"], role=profile["role"])
    return auth_user, _session_to_model(session)


def login(email: str, password: str) -> tuple[AuthUser, AuthSession]:
    """이메일·비밀번호로 로그인한다.

    Raises:
        AuthError: 필수값 누락, 이메일 형식 오류, 또는 Supabase Auth 인증 실패 시.
    """
    normalized_email = email.strip()

    if not normalized_email or not password:
        raise AuthError("VALID_001", "이메일과 비밀번호를 입력해주세요.")
    if not is_valid_email(normalized_email):
        raise AuthError("VALID_002", "올바른 이메일 형식이 아닙니다.")

    return _authenticate(normalized_email, password, "이메일 또는 비밀번호가 올바르지 않습니다.")


def request_signup_verification(
    email: str,
    password: str,
    password_confirm: str,
    agreed_to_terms: bool,
) -> None:
    """가입 정보를 검증하고 Supabase Auth로 이메일 인증 코드 발송을 요청한다.

    Raises:
        AuthError: 필수값 누락, 이메일 형식 오류, 비밀번호 길이·불일치, 약관 미동의, 또는 이미
            가입된 이메일인 경우.
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

    client = create_supabase_client()
    try:
        client.auth.sign_up({"email": normalized_email, "password": password})
    except AuthApiError as error:
        # Supabase는 형식은 맞지만 실제로 받을 수 없다고 판단한 이메일(예: example.com 같은 예약
        # 도메인)도 email_address_invalid로 거부한다 — 로컬 정규식 검사(is_valid_email)로는
        # 걸러지지 않아 별도로 구분해야 "이미 가입됨"과 다른 정확한 메시지를 보여줄 수 있다.
        if error.code == "email_address_invalid":
            raise AuthError("VALID_002", "올바른 이메일 형식이 아닙니다.") from error
        if error.code == "user_already_exists":
            raise AuthError("VALID_003", "이미 가입된 이메일입니다.") from error
        raise AuthError("SERVER_005", "가입 요청을 처리하지 못했습니다. 잠시 후 다시 시도해주세요.") from error


def complete_signup(email: str, verification_code: str) -> tuple[AuthUser, AuthSession]:
    """이메일로 받은 인증 코드를 확인하고 가입을 완료한다.

    Raises:
        AuthError: 인증 코드가 올바르지 않거나 만료된 경우.
    """
    normalized_email = email.strip()
    client = create_supabase_client()
    try:
        auth_response = client.auth.verify_otp(
            {"email": normalized_email, "token": verification_code.strip(), "type": "signup"}
        )
    except AuthApiError as error:
        raise AuthError("VALID_002", "인증번호가 올바르지 않거나 만료되었습니다.") from error

    user, session = auth_response.user, auth_response.session
    scoped_client = create_supabase_client(access_token=session.access_token)
    profile = _load_or_create_profile(scoped_client, user.id, user.email)

    auth_user = AuthUser(id=user.id, email=user.email, display_name=profile["display_name"], role=profile["role"])
    return auth_user, _session_to_model(session)


def request_password_reset(email: str) -> None:
    """비밀번호 재설정 인증 코드 발송을 요청한다.

    Raises:
        AuthError: 이메일 미입력 또는 형식 오류 시.
    """
    normalized_email = email.strip()

    if not normalized_email:
        raise AuthError("VALID_001", "이메일을 입력해주세요.")
    if not is_valid_email(normalized_email):
        raise AuthError("VALID_002", "올바른 이메일 형식이 아닙니다.")

    client = create_supabase_client()
    try:
        client.auth.reset_password_email(normalized_email)
    except AuthApiError as error:
        raise AuthError("SERVER_005", "인증번호 발송에 실패했습니다. 잠시 후 다시 시도해주세요.") from error


def reset_password(email: str, verification_code: str, new_password: str, new_password_confirm: str) -> None:
    """인증 코드를 확인하고 새 비밀번호로 재설정한다.

    Raises:
        AuthError: 비밀번호 길이 미달·확인값 불일치, 또는 인증 코드가 올바르지 않은 경우.
    """
    if len(new_password) < MIN_PASSWORD_LENGTH:
        raise AuthError("VALID_002", f"비밀번호는 최소 {MIN_PASSWORD_LENGTH}자 이상이어야 합니다.")
    if new_password != new_password_confirm:
        raise AuthError("VALID_002", "비밀번호가 일치하지 않습니다.")

    client = create_supabase_client()
    try:
        auth_response = client.auth.verify_otp(
            {"email": email.strip(), "token": verification_code.strip(), "type": "recovery"}
        )
    except AuthApiError as error:
        raise AuthError("VALID_002", "인증번호가 올바르지 않거나 만료되었습니다.") from error

    session = auth_response.session
    scoped_client = create_supabase_client(access_token=session.access_token)
    scoped_client.auth.set_session(session.access_token, session.refresh_token)
    scoped_client.auth.update_user({"password": new_password})
    scoped_client.auth.sign_out()


def change_password(
    email: str, current_password: str, new_password: str, new_password_confirm: str
) -> AuthSession:
    """로그인한 상태에서 비밀번호를 변경한다 (MY-002 계정 설정, FR-PROFILE-002 계정 정보 수정).

    현재 비밀번호로 재인증하는 것으로 본인 확인을 대신하고(Supabase Auth는 세션 상태에서 별도의
    "현재 비밀번호 대조" API를 제공하지 않음), 그 결과로 발급되는 세션으로 비밀번호를 변경한다.

    Raises:
        AuthError: 현재 비밀번호 미입력·불일치, 또는 새 비밀번호 길이 미달·확인값 불일치 시.

    Returns:
        비밀번호 변경 후의 새 세션 — 호출부가 `st.session_state[SessionKeys.AUTH_SESSION]`을 갱신해야 한다.
    """
    if not current_password:
        raise AuthError("VALID_001", "현재 비밀번호를 입력해주세요.")
    if len(new_password) < MIN_PASSWORD_LENGTH:
        raise AuthError("VALID_002", f"비밀번호는 최소 {MIN_PASSWORD_LENGTH}자 이상이어야 합니다.")
    if new_password != new_password_confirm:
        raise AuthError("VALID_002", "비밀번호가 일치하지 않습니다.")

    _, session = _authenticate(email.strip(), current_password, "현재 비밀번호가 올바르지 않습니다.")

    client = create_supabase_client(access_token=session.access_token)
    client.auth.set_session(session.access_token, session.refresh_token)
    client.auth.update_user({"password": new_password})
    return session


def update_display_name(access_token: str, user_id: str, display_name: str) -> str:
    """계정 설정(MY-002)에서 표시 이름을 변경한다.

    Raises:
        AuthError: 표시 이름을 비워서 저장하려는 경우.

    Returns:
        저장된(공백 제거) 표시 이름.
    """
    normalized_name = display_name.strip()
    if not normalized_name:
        raise AuthError("VALID_001", "표시 이름을 입력해주세요.")

    client = create_supabase_client(access_token=access_token)
    client.table("profiles").update({"display_name": normalized_name}).eq("id", user_id).execute()
    return normalized_name


def delete_account(user_id: str) -> None:
    """회원 탈퇴(MY-002, FR-PROFILE-004) 시 Supabase의 실제 계정을 삭제한다.

    `auth.users`에서 계정을 지우면 `trendfit.profiles`도 외래키 `on delete cascade`로 함께
    삭제된다(supabase/migrations/0001_create_profiles.sql 참고). 계정 삭제는 일반 사용자
    세션(anon key + RLS)으로는 할 수 없는 관리자 동작이라 `service_role` 클라이언트를 쓴다.

    Raises:
        AuthError: Supabase 쪽에서 삭제가 실패한 경우(SERVER_005).
    """
    try:
        get_supabase_admin_client().auth.admin.delete_user(user_id)
    except AuthApiError as error:
        raise AuthError("SERVER_005", "회원 탈퇴 처리에 실패했습니다. 잠시 후 다시 시도해주세요.") from error


def login_with_social_provider(provider: str) -> AuthUser:
    """소셜 로그인(FR-AUTH-002)을 시뮬레이션한다.

    실제 OAuth 연동 전까지, 실제 동의 화면 없이 즉시 로그인 처리한다. Supabase Auth와 연결되어
    있지 않으므로 `id`도 세션 내 임시값이고, 비밀번호 변경 등 실제 세션 토큰이 필요한 기능은
    이 경로로 로그인한 계정에서는 쓸 수 없다.
    """
    display_name = f"{provider}_user"
    email = f"{display_name}@example.com"
    return AuthUser(id=f"mock-{provider}", email=email, display_name=display_name, role=_resolve_role(email))
