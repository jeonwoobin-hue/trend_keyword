"""로컬 시크릿(.streamlit/secrets.toml) 로더.

`api/`·`worker/`는 Streamlit 런타임 밖에서 별도 프로세스로 실행되므로 `st.secrets` 대신 파일을
직접 읽는다 — app/api/worker 어디서든 동일하게 동작하고, services 계층이 streamlit 패키지에
의존하지 않도록 하기 위함이다. 배포 환경에서는 이 파일 대신 환경변수/시크릿 매니저로 대체한다
(ops/Deployment.md 참고).
"""

import tomllib
from functools import lru_cache
from pathlib import Path

_SECRETS_PATH = Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml"


@lru_cache(maxsize=1)
def _load_secrets() -> dict:
    if not _SECRETS_PATH.exists():
        return {}
    with _SECRETS_PATH.open("rb") as f:
        return tomllib.load(f)


def get_secret_section(section: str) -> dict:
    """secrets.toml의 `[section]` 테이블을 반환한다. 파일/섹션이 없으면 빈 dict."""
    return _load_secrets().get(section, {})
