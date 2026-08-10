"""급상승 알림 키워드 등록/삭제 및 발송 히스토리 도메인 로직 (functional-spec FR-ALERT-001/003).

실제 저장소(DB)가 붙기 전까지 알림 목록은 호출부(현재는 `st.session_state`)가 들고 있고,
이 모듈은 검증 규칙과 등록/삭제 순수 로직만 담당한다. 실제 연동 시 저장소만 교체하면 된다.
알림 발송 히스토리(`generate_alert_history`)는 실제 배치 발송 워커(FR-ALERT-003)가 없어,
등록된 키워드마다 임계치를 넘어 발송됐다고 가정한 목(mock) 이력을 생성한다.
"""

import random
import uuid
from datetime import datetime, timedelta, timezone

from config.constants import (
    ALERT_HISTORY_FAILURE_RATE,
    ALERT_HISTORY_MAX_EVENTS_PER_KEYWORD,
    MAX_ALERT_KEYWORD_LENGTH,
    MAX_ALERT_KEYWORDS,
)
from models.alert import AlertHistoryEntry, AlertRule


class AlertValidationError(Exception):
    """등록 실패 시 사용자 메시지를 함께 담는 예외 (API_Design.md §3 공통 에러 코드 기준)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def register_alert(
    existing_rules: list[AlertRule],
    keyword: str,
    threshold_score: int,
    notify_channels: list[str],
) -> AlertRule:
    """새 알림 키워드를 등록한다.

    Raises:
        AlertValidationError: 필수값 누락, 길이 초과, 중복 등록, 최대 개수 초과 시.
    """
    normalized_keyword = keyword.strip()

    if not normalized_keyword:
        raise AlertValidationError("VALID_001", "키워드를 입력해주세요.")
    if len(normalized_keyword) > MAX_ALERT_KEYWORD_LENGTH:
        raise AlertValidationError(
            "VALID_002", f"키워드는 최대 {MAX_ALERT_KEYWORD_LENGTH}자까지 입력할 수 있습니다."
        )
    if not notify_channels:
        raise AlertValidationError("VALID_001", "알림 수신 방식을 1개 이상 선택해주세요.")
    if any(rule.keyword == normalized_keyword for rule in existing_rules):
        raise AlertValidationError("VALID_003", "이미 등록된 키워드입니다.")
    if len(existing_rules) >= MAX_ALERT_KEYWORDS:
        raise AlertValidationError(
            "VALID_003", f"알림 키워드는 최대 {MAX_ALERT_KEYWORDS}개까지 등록할 수 있습니다."
        )

    return AlertRule(
        alert_id=f"alert_{uuid.uuid4().hex[:8]}",
        keyword=normalized_keyword,
        threshold_score=threshold_score,
        notify_channels=notify_channels,
        created_at=datetime.now(timezone.utc),
    )


def remove_alert(existing_rules: list[AlertRule], alert_id: str) -> list[AlertRule]:
    """등록된 알림 키워드를 삭제한 새 목록을 반환한다."""
    return [rule for rule in existing_rules if rule.alert_id != alert_id]


def generate_alert_history(alert_rules: list[AlertRule]) -> list[AlertHistoryEntry]:
    """등록된 알림 키워드를 기준으로 과거 발송 이력을 시뮬레이션한다 (최신순 정렬)."""
    history = [entry for rule in alert_rules for entry in _generate_entries_for_rule(rule)]
    history.sort(key=lambda entry: entry.sent_at, reverse=True)
    return history


def _generate_entries_for_rule(rule: AlertRule) -> list[AlertHistoryEntry]:
    rng = random.Random(f"alert_history:{rule.alert_id}")
    event_count = rng.randint(1, ALERT_HISTORY_MAX_EVENTS_PER_KEYWORD)

    entries = []
    for index in range(event_count):
        status = "failed" if rng.random() < ALERT_HISTORY_FAILURE_RATE else "sent"
        entries.append(
            AlertHistoryEntry(
                alert_history_id=f"{rule.alert_id}_hist_{index}",
                keyword=rule.keyword,
                spike_score=round(rng.uniform(rule.threshold_score, 100), 1),
                sent_at=datetime.now(timezone.utc) - timedelta(hours=index * 6 + 1),
                channel=rng.choice(rule.notify_channels),
                status=status,
            )
        )
    return entries
