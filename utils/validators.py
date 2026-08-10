"""특정 도메인에 종속되지 않는 공통 검증 유틸."""

import re

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(value: str) -> bool:
    """대략적인 이메일 형식 여부를 확인한다."""
    return bool(_EMAIL_PATTERN.match(value.strip()))
