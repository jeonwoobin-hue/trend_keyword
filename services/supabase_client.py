"""Supabase 연결 모듈.

블로그 프로젝트와 같은 Supabase 프로젝트를 공유하되(무료 플랜 프로젝트 한도로 인한 결정,
product/CHANGELOG.md 2026-08-12 참고), TrendFit 데이터는 `trendfit` 스키마 아래로 격리한다.

Coding_Convention.md §4-1은 커넥션 캐싱에 `@st.cache_resource`를 권장하지만, 이 모듈은
`api/`·`worker/`(Streamlit 런타임 밖)에서도 재사용되므로 대신 프레임워크 독립적인
`functools.lru_cache`로 싱글턴을 유지한다.
"""

from functools import lru_cache

from supabase import Client, ClientOptions, create_client

from config.constants import SUPABASE_SCHEMA
from config.secrets import get_secret_section


class SupabaseConfigError(Exception):
    """secrets.toml에 `[supabase]` 설정이 없거나 불완전할 때 발생한다."""


def _get_supabase_secrets() -> dict:
    secrets = get_secret_section("supabase")
    if not secrets.get("url"):
        raise SupabaseConfigError(".streamlit/secrets.toml에 [supabase] url이 설정되어 있지 않습니다.")
    return secrets


def create_supabase_client(access_token: str | None = None) -> Client:
    """anon key 기반의 새 클라이언트를 만든다.

    Streamlit은 여러 브라우저 세션이 한 프로세스를 공유하므로, 로그인 세션(JWT)을 캐시된 싱글턴
    클라이언트에 실어 두면 사용자 간에 세션이 섞일 수 있다. 그래서 로그인/회원가입 등 인증이
    관여하는 호출은 매번 이 함수로 새 클라이언트를 만들어 쓰고, 이미 로그인된 사용자를 대신해
    조회할 때는 `access_token`으로 해당 요청에만 인증 컨텍스트를 지정한다.
    """
    secrets = _get_supabase_secrets()
    anon_key = secrets.get("anon_key")
    if not anon_key:
        raise SupabaseConfigError(".streamlit/secrets.toml에 [supabase] anon_key가 설정되어 있지 않습니다.")

    client = create_client(secrets["url"], anon_key, options=ClientOptions(schema=SUPABASE_SCHEMA))
    if access_token:
        client.postgrest.auth(access_token)
    return client


@lru_cache(maxsize=1)
def get_supabase_admin_client() -> Client:
    """service_role key 기반 클라이언트(RLS 우회).

    사용자 세션과 무관한 정적 키만 사용하므로(로그인 상태를 들고 있지 않음) 프로세스 전역에서
    안전하게 공유할 수 있다. `worker/jobs`·관리자 전용 로직에서만 사용하고, 이 클라이언트로 조회한
    데이터를 그대로 클라이언트(브라우저)에 노출하지 않는다.
    """
    secrets = _get_supabase_secrets()
    service_role_key = secrets.get("service_role_key")
    if not service_role_key:
        raise SupabaseConfigError(".streamlit/secrets.toml에 [supabase] service_role_key가 설정되어 있지 않습니다.")

    return create_client(secrets["url"], service_role_key, options=ClientOptions(schema=SUPABASE_SCHEMA))
