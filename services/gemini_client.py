"""Gemini(Google GenAI) 연결 모듈.

인사이트 리포트 이슈 요약(FR-REPORT-002) 등 AI 생성 콘텐츠(docs/Prompt_Guide.md)에서 공용으로
사용한다. `services/supabase_client.py`와 같은 패턴 — secrets.toml에서 키를 읽어 호출마다 새
클라이언트를 만든다(무거운 연결 상태를 들고 있지 않아 캐싱할 이유가 없음).
"""

from google import genai
from google.genai import types

from config.constants import GEMINI_REQUEST_TIMEOUT_MS
from config.secrets import get_secret_section


class GeminiConfigError(Exception):
    """secrets.toml에 `[gemini]` api_key가 설정되어 있지 않을 때 발생한다."""


def create_gemini_client() -> genai.Client:
    """secrets.toml의 `[gemini] api_key`로 클라이언트를 만든다.

    호출부(report_service 등)는 이 함수가 던지는 예외를 잡아 고정 템플릿으로 폴백해야 한다 —
    로컬 개발 환경처럼 키가 없는 경우에도 앱 자체는 정상 동작해야 하기 때문이다.
    """
    api_key = get_secret_section("gemini").get("api_key")
    if not api_key:
        raise GeminiConfigError(".streamlit/secrets.toml에 [gemini] api_key가 설정되어 있지 않습니다.")

    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=GEMINI_REQUEST_TIMEOUT_MS),
    )
