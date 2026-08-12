"""로컬 시크릿(.streamlit/secrets.toml) 로더.

`api/`·`worker/`는 Streamlit 런타임 밖에서 별도 프로세스로 실행되므로 `st.secrets` 대신 파일을
직접 읽는다 — app/api/worker 어디서든 동일하게 동작하고, services 계층이 streamlit 패키지에
의존하지 않도록 하기 위함이다. Streamlit Community Cloud에 배포한 경우 대시보드(Settings →
Secrets)에 입력한 내용을 플랫폼이 동일한 경로(`.streamlit/secrets.toml`)에 그대로 파일로 만들어
주기 때문에, 이 로더는 로컬/클라우드 배포 어디서나 동일하게 동작한다.
"""

import tomllib
from functools import lru_cache
from pathlib import Path

_SECRETS_PATH = Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml"
_DEFAULT_APP_BASE_URL = "http://localhost:8501"  # secrets.toml에 [app] base_url이 없을 때(로컬 개발)


@lru_cache(maxsize=1)
def _load_secrets() -> dict:
    if not _SECRETS_PATH.exists():
        return {}
    with _SECRETS_PATH.open("rb") as f:
        return tomllib.load(f)


def get_secret_section(section: str) -> dict:
    """secrets.toml의 `[section]` 테이블을 반환한다. 파일/섹션이 없으면 빈 dict."""
    return _load_secrets().get(section, {})


def get_app_base_url() -> str:
    """OAuth `redirect_to` 등에 쓰는 앱 배포 URL을 반환한다.

    로컬 개발과 Streamlit Cloud 배포가 서로 다른 URL을 쓰므로(도메인은 코드가 아니라 환경마다
    달라지는 값), secrets.toml의 `[app] base_url`을 우선 쓰고 없으면 로컬 기본값으로 대체한다.
    """
    return get_secret_section("app").get("base_url", _DEFAULT_APP_BASE_URL)
