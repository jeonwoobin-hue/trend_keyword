"""트렌드 대시보드 데이터 조회.

실제 외부 데이터 연동(`services/*_client.py`)이 붙기 전까지, 이 모듈은
functional-spec.md FR-DASH-001/FR-DASH-004, SRS FR-DASH-005 응답 계약과 동일한 형태의
목(mock) 데이터를 생성한다. 실제 연동 시 내부 구현만 실제 API 클라이언트 호출로 교체하고,
공개 함수의 시그니처와 반환 타입(`DashboardKeywordsResult`, `KeywordDetail`)은 유지한다.

Spike Score(FR-DASH-003)는 `services/spike_score_service.calculate_spike_score()`로 실제
산출 공식을 적용한다 — 언급량 시계열 자체는 아직 목 데이터이지만, 점수는 그 시계열로부터
문서화된 계산식(docs/KPI_Definitions.md)대로 정직하게 계산된다(난수 아님).

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
    SPIKE_KEYWORD_PROBABILITY,
    SPIKE_MULTIPLIER_RANGE,
    TREND_BASELINE_RANGE,
    TREND_NOISE_RATIO,
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
from services.spike_score_service import calculate_spike_score

# 카테고리별 (keyword_id, keyword) 목 데이터 풀. CATEGORIES(config/constants.py)와 키가 일치해야 한다.
_MOCK_KEYWORD_POOLS: dict[str, list[tuple[str, str]]] = {
    "travel": [
        ("travel_autumn_foliage", "가을 단풍 여행지"),
        ("travel_lcc_deal", "저비용항공 특가"),
        ("travel_local_stay", "로컬 체험 숙소"),
        ("travel_car_camping", "차박 캠핑 코스"),
        ("travel_new_direct_route", "신규 해외 직항 노선"),
        ("travel_pet_friendly", "반려동물 동반 여행"),
    ],
    "fashion": [
        ("fashion_denim_jacket", "가을 데님 재킷"),
        ("fashion_musinsa_sale", "무신사 블랙프라이데이"),
        ("fashion_eco_fabric", "친환경 소재 원단"),
        ("fashion_retro_sneakers", "레트로 스니커즈"),
        ("fashion_capsule_wardrobe", "미니멀 캡슐 옷장"),
        ("fashion_vintage_reform", "빈티지 리폼"),
    ],
    "beauty": [
        ("beauty_sunscreen", "저자극 선크림"),
        ("beauty_glass_skin", "글래스 스킨 루틴"),
        ("beauty_vegan_cert", "비건 인증 화장품"),
        ("beauty_scalp_care", "두피 케어"),
        ("beauty_cushion_new", "쿠션 신제품"),
        ("beauty_tone_up_cream", "톤업 크림 비교"),
    ],
    "food": [
        ("food_meal_kit", "밀키트 신제품 비교"),
        ("food_zero_sugar", "제로 슈거 음료 열풍"),
        ("food_omakase", "오마카세 예약 전쟁"),
        ("food_camping_meal", "캠핑 요리 레시피"),
        ("food_vegan_restaurant", "비건 맛집 리스트"),
        ("food_coffee_trend", "스페셜티 커피 트렌드"),
    ],
    "it_tech": [
        ("it_tech_on_device_ai", "온디바이스 AI"),
        ("it_tech_foldable", "폴더블 신제품"),
        ("it_tech_open_llm", "오픈소스 LLM"),
        ("it_tech_wearable_health", "웨어러블 헬스 기기"),
        ("it_tech_low_power_chip", "저전력 반도체"),
        ("it_tech_genai_plan", "생성형 AI 요금제"),
    ],
    "car": [
        ("car_ev_subsidy", "전기차 보조금 개편"),
        ("car_used_market", "중고차 시세 급등"),
        ("car_compact_suv", "소형 SUV 신차 비교"),
        ("car_autonomous", "자율주행 기능 리뷰"),
        ("car_tire_review", "사계절 타이어 추천"),
        ("car_rental_price", "장기렌트 가격 비교"),
    ],
    "living": [
        ("living_small_space", "원룸 인테리어 아이디어"),
        ("living_smart_home", "스마트홈 기기 추천"),
        ("living_furniture_sale", "가구 시즌 세일"),
        ("living_plant_care", "반려식물 키우기"),
        ("living_storage_hack", "수납 정리 꿀팁"),
        ("living_eco_product", "친환경 생활용품"),
    ],
    "parenting": [
        ("parenting_newborn_item", "신생아 필수템 리스트"),
        ("parenting_school_prep", "초등 입학 준비물"),
        ("parenting_kids_book", "연령별 육아 도서 추천"),
        ("parenting_daycare", "어린이집 대기 현황"),
        ("parenting_kids_travel", "아이와 가는 국내 여행지"),
        ("parenting_allowance", "자녀 용돈 교육법"),
    ],
    "health": [
        ("health_sleep_routine", "수면의 질 개선 루틴"),
        ("health_home_workout", "홈트레이닝 챌린지"),
        ("health_supplement", "영양제 조합 추천"),
        ("health_diet_trend", "저속노화 식단"),
        ("health_mental_care", "번아웃 자가진단"),
        ("health_checkup", "건강검진 항목 정리"),
    ],
    "game": [
        ("game_new_release", "신작 게임 출시 소식"),
        ("game_mobile_ranking", "모바일 게임 순위 변동"),
        ("game_esports_match", "e스포츠 경기 결과"),
        ("game_console_sale", "콘솔 할인 정보"),
        ("game_indie_pick", "인디 게임 추천"),
        ("game_update_patch", "인기 게임 업데이트 패치"),
    ],
    "pet": [
        ("pet_food_review", "반려동물 사료 비교"),
        ("pet_hospital_cost", "동물병원 진료비 부담"),
        ("pet_training_tip", "강아지 훈련 꿀팁"),
        ("pet_cafe", "반려동물 동반 카페"),
        ("pet_insurance", "펫보험 가입 트렌드"),
        ("pet_adoption", "유기동물 입양 후기"),
    ],
    "sports_leisure": [
        ("sports_running_gear", "러닝화 신제품 리뷰"),
        ("sports_golf_boom", "골프 입문자 장비"),
        ("sports_climbing", "클라이밍 입문 코스"),
        ("sports_yoga_class", "요가 클래스 후기"),
        ("sports_camping_gear", "캠핑 장비 추천"),
        ("sports_swimming", "수영 초보 강습"),
    ],
    "pro_sports": [
        ("pro_sports_baseball", "프로야구 순위 경쟁"),
        ("pro_sports_soccer", "축구 이적 시장 소식"),
        ("pro_sports_basketball", "농구 플레이오프 일정"),
        ("pro_sports_volleyball", "배구 국가대표 소식"),
        ("pro_sports_golf_tour", "골프 투어 결과"),
        ("pro_sports_esports_league", "e스포츠 리그 순위"),
    ],
    "entertainment": [
        ("entertainment_drama_casting", "신작 드라마 캐스팅"),
        ("entertainment_variety_show", "예능 프로그램 화제성"),
        ("entertainment_idol_comeback", "아이돌 컴백 소식"),
        ("entertainment_awards", "연예 시상식 후보"),
        ("entertainment_issue", "연예계 이슈 정리"),
        ("entertainment_ott_release", "OTT 신규 공개작"),
    ],
    "music": [
        ("music_chart_ranking", "음원 차트 순위 변동"),
        ("music_new_album", "신규 앨범 발매 소식"),
        ("music_concert_ticket", "콘서트 티켓 예매 전쟁"),
        ("music_festival_lineup", "음악 페스티벌 라인업"),
        ("music_collab", "아티스트 콜라보 소식"),
        ("music_playlist_trend", "인기 플레이리스트 트렌드"),
    ],
    "movie": [
        ("movie_box_office", "박스오피스 순위"),
        ("movie_new_release", "개봉 예정작 소식"),
        ("movie_ott_original", "OTT 오리지널 영화"),
        ("movie_director_interview", "감독 인터뷰 화제"),
        ("movie_review_buzz", "관람평 화제성"),
        ("movie_sequel_news", "후속작 제작 소식"),
    ],
    "performing_arts": [
        ("art_exhibition", "인기 전시회 리뷰"),
        ("art_musical_ticket", "뮤지컬 티켓 예매"),
        ("art_gallery_opening", "갤러리 신규 오픈"),
        ("art_classical_concert", "클래식 공연 소식"),
        ("art_pop_up", "아트 팝업 스토어"),
        ("art_photo_exhibit", "사진전 화제작"),
    ],
    "book": [
        ("book_bestseller", "베스트셀러 순위 변동"),
        ("book_new_release", "신간 도서 소개"),
        ("book_reading_club", "독서모임 트렌드"),
        ("book_ebook_sale", "전자책 할인 정보"),
        ("book_author_interview", "작가 인터뷰 화제"),
        ("book_award", "문학상 수상작 소식"),
    ],
    "economy_business": [
        ("economy_business_isa_update", "ISA 계좌 개편"),
        ("economy_business_youth_loan", "청년 정책 대출"),
        ("economy_business_reits", "리츠 배당주"),
        ("economy_business_fx_hedge", "환율 변동 대응"),
        ("economy_business_pension_default", "퇴직연금 디폴트옵션"),
        ("economy_business_budget_app", "가계부 자동화 앱"),
    ],
    "education": [
        ("education_exam_prep", "자격증 시험 준비 트렌드"),
        ("education_language_app", "어학 학습 앱 비교"),
        ("education_online_class", "온라인 강의 인기 강좌"),
        ("education_study_abroad", "해외 어학연수 정보"),
        ("education_kids_english", "아이 영어 교육법"),
        ("education_certificate", "인기 자격증 순위"),
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


def find_keyword_id_by_name(keyword: str) -> str | None:
    """키워드 이름으로 `keyword_id`를 찾는다 (ALERT-002 알림 상세 이동).

    급상승 알림 키워드(`AlertRule.keyword`)는 자유 입력 텍스트라 목 키워드 풀에 없을 수도
    있다 — 그 경우 `None`을 반환하고 호출부가 "상세 정보 없음"으로 처리한다.
    """
    for pool in _MOCK_KEYWORD_POOLS.values():
        for candidate_id, name in pool:
            if name == keyword:
                return candidate_id
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
                spike_score=calculate_spike_score([point.mention_count for point in trend_graph]),
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
    """기간별 라벨에 맞는 언급량 추이 포인트를 생성한다.

    포인트마다 완전히 독립된 난수 대신, 키워드별 기준선(baseline)에 자연스러운 변동을 준 시계열을
    만든다 — Spike Score(services/spike_score_service)가 이 시계열의 평균·표준편차로 실제
    계산되므로, 값들이 서로 무관하면 계산식이 있어도 결과가 여전히 난수와 다를 바 없어진다.
    일부 키워드는 당일(마지막 포인트)에 실제로 급상승한 것처럼 배수를 곱해, 급상승/평상시 키워드가
    Spike Score로 실제 구분되는 것을 보여준다.
    """
    labels = _PERIOD_LABELS[period]
    baseline = rng.randint(*TREND_BASELINE_RANGE)
    counts = [max(0, round(rng.gauss(baseline, baseline * TREND_NOISE_RATIO))) for _ in labels]

    if rng.random() < SPIKE_KEYWORD_PROBABILITY:
        counts[-1] = round(counts[-1] * rng.uniform(*SPIKE_MULTIPLIER_RANGE))

    return [TrendPoint(label=label, mention_count=count) for label, count in zip(labels, counts)]
