"""트렌드 대시보드 데이터 조회.

실제 외부 데이터 연동(`services/*_client.py`)이 붙기 전까지, 이 모듈은
functional-spec.md FR-DASH-001/FR-DASH-004, SRS FR-DASH-005 응답 계약과 동일한 형태의
목(mock) 데이터를 생성한다. 실제 연동 시 내부 구현만 실제 API 클라이언트 호출로 교체하고,
공개 함수의 시그니처와 반환 타입(`DashboardKeywordsResult`, `KeywordDetail`)은 유지한다.

연령·성별 관심도 가중치 보정(FR-DASH-005)은 실제 데이터 소스 미확보로 산정 방법이 미정이라
(docs/KPI_Definitions.md 참고), 그룹별 상대 비중만 무작위로 생성해 보여준다.
"""

import random
from datetime import datetime, timezone

from config.constants import (
    AGE_GROUP_OPTIONS,
    CATEGORIES,
    CATEGORY_ALL,
    DASHBOARD_TOP_N,
    DEMOGRAPHIC_GENDERS,
    RELATED_KEYWORDS_TOP_N,
    SENTIMENT_MIN_MENTION_COUNT,
)
from models.dashboard import (
    DashboardKeywordsResult,
    DashboardMeta,
    DemographicWeights,
    KeywordDetail,
    SentimentRatio,
    TrendKeyword,
    TrendPoint,
)

# 카테고리별 (keyword_id, keyword) 목 데이터 풀
_MOCK_KEYWORD_POOLS: dict[str, list[tuple[str, str]]] = {
    "fashion": [
        ("fashion_denim_jacket", "가을 데님 재킷"),
        ("fashion_musinsa_sale", "무신사 블랙프라이데이"),
        ("fashion_eco_fabric", "친환경 소재 원단"),
        ("fashion_retro_sneakers", "레트로 스니커즈"),
        ("fashion_capsule_wardrobe", "미니멀 캡슐 옷장"),
        ("fashion_vintage_reform", "빈티지 리폼"),
    ],
    "it_tech": [
        ("it_tech_on_device_ai", "온디바이스 AI"),
        ("it_tech_foldable", "폴더블 신제품"),
        ("it_tech_open_llm", "오픈소스 LLM"),
        ("it_tech_wearable_health", "웨어러블 헬스 기기"),
        ("it_tech_low_power_chip", "저전력 반도체"),
        ("it_tech_genai_plan", "생성형 AI 요금제"),
    ],
    "travel": [
        ("travel_autumn_foliage", "가을 단풍 여행지"),
        ("travel_lcc_deal", "저비용항공 특가"),
        ("travel_local_stay", "로컬 체험 숙소"),
        ("travel_car_camping", "차박 캠핑 코스"),
        ("travel_new_direct_route", "신규 해외 직항 노선"),
        ("travel_pet_friendly", "반려동물 동반 여행"),
    ],
    "finance": [
        ("finance_isa_update", "ISA 계좌 개편"),
        ("finance_youth_loan", "청년 정책 대출"),
        ("finance_reits", "리츠 배당주"),
        ("finance_fx_hedge", "환율 변동 대응"),
        ("finance_pension_default", "퇴직연금 디폴트옵션"),
        ("finance_budget_app", "가계부 자동화 앱"),
    ],
    "beauty": [
        ("beauty_sunscreen", "저자극 선크림"),
        ("beauty_glass_skin", "글래스 스킨 루틴"),
        ("beauty_vegan_cert", "비건 인증 화장품"),
        ("beauty_scalp_care", "두피 케어"),
        ("beauty_cushion_new", "쿠션 신제품"),
        ("beauty_tone_up_cream", "톤업 크림 비교"),
    ],
}

_PERIOD_LABELS: dict[str, list[str]] = {
    "24h": ["-24h", "-20h", "-16h", "-12h", "-8h", "-4h", "지금"],
    "1w": ["-6일", "-5일", "-4일", "-3일", "-2일", "-1일", "오늘"],
    "1m": ["-4주", "-3주", "-2주", "-1주", "이번주"],
}


def get_dashboard_keywords(category: str, period: str) -> DashboardKeywordsResult:
    """분야·기간 조건에 맞는 핫 키워드를 Spike Score 기준 상위 `DASHBOARD_TOP_N`개 반환한다.

    Args:
        category: 관심 분야 값. `CATEGORY_ALL`이면 전체 분야를 대상으로 한다.
        period: 조회 기간 (`24h`/`1w`/`1m`).
    """
    target_categories = [value for value, _ in CATEGORIES] if category == CATEGORY_ALL else [category]

    keywords = [
        keyword
        for target in target_categories
        for keyword in _build_mock_keywords(target, period)
    ]
    keywords.sort(key=lambda item: item.spike_score, reverse=True)

    return DashboardKeywordsResult(
        keywords=keywords[:DASHBOARD_TOP_N],
        meta=DashboardMeta(period=period, updated_at=datetime.now(timezone.utc)),
    )


def get_keyword_detail(keyword_id: str, period: str) -> KeywordDetail | None:
    """키워드 ID로 상세 데이터를 조회한다.

    Returns:
        존재하지 않는 키워드 ID면 `None` (호출부에서 RES_001로 처리).
    """
    for category, pool in _MOCK_KEYWORD_POOLS.items():
        for candidate_id, name in pool:
            if candidate_id == keyword_id:
                return _build_keyword_detail(candidate_id, name, category, period)
    return None


def _build_mock_keywords(category: str, period: str) -> list[TrendKeyword]:
    """카테고리·기간 조합마다 안정적인(재실행해도 동일한) 목 데이터를 생성한다."""
    rng = random.Random(f"{category}:{period}")

    result = []
    for keyword_id, name in _MOCK_KEYWORD_POOLS[category]:
        trend_graph = _generate_trend_points(rng, period)
        result.append(
            TrendKeyword(
                keyword_id=keyword_id,
                keyword=name,
                category=category,
                mention_count=trend_graph[-1].mention_count,
                spike_score=round(rng.uniform(10, 99), 1),
                trend_graph=trend_graph,
            )
        )
    return result


def _build_keyword_detail(keyword_id: str, name: str, category: str, period: str) -> KeywordDetail:
    """키워드 1건의 상세 목 데이터(추이·감성·연관 키워드)를 생성한다."""
    rng = random.Random(f"{keyword_id}:{period}:detail")
    trend_series = _generate_trend_points(rng, period)

    sentiment = None
    if trend_series[-1].mention_count >= SENTIMENT_MIN_MENTION_COUNT:
        positive = rng.uniform(0.3, 0.7)
        negative = rng.uniform(0.05, max(0.05, 1 - positive - 0.05))
        sentiment = SentimentRatio(
            positive=round(positive, 2),
            negative=round(negative, 2),
            neutral=round(1 - positive - negative, 2),
        )

    related_pool = [kw for pool in _MOCK_KEYWORD_POOLS.values() for _, kw in pool if kw != name]
    related_keywords = rng.sample(related_pool, k=min(RELATED_KEYWORDS_TOP_N, len(related_pool)))

    demographics = DemographicWeights(
        age_group_weights=_build_demographic_weights(rng, [g for g, _ in AGE_GROUP_OPTIONS]),
        gender_weights=_build_demographic_weights(rng, [g for g, _ in DEMOGRAPHIC_GENDERS]),
    )

    return KeywordDetail(
        keyword_id=keyword_id,
        keyword=name,
        category=category,
        trend_series=trend_series,
        sentiment=sentiment,
        related_keywords=related_keywords,
        demographics=demographics,
    )


def _build_demographic_weights(rng: random.Random, group_ids: list[str]) -> dict[str, float]:
    """그룹별 상대 비중을 생성한다(합계 1.0). 산정 방법은 docs/KPI_Definitions.md 참고."""
    raw_values = [rng.uniform(0.5, 1.5) for _ in group_ids]
    total = sum(raw_values)
    return {group_id: round(value / total, 3) for group_id, value in zip(group_ids, raw_values)}


def _generate_trend_points(rng: random.Random, period: str) -> list[TrendPoint]:
    """기간별 라벨에 맞는 언급량 추이 포인트를 생성한다."""
    return [TrendPoint(label=label, mention_count=rng.randint(500, 50_000)) for label in _PERIOD_LABELS[period]]
