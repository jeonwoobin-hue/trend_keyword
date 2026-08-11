"""앱 전역 상수. 매직넘버·하드코딩 문자열은 여기서 관리한다 (CLAUDE.md §3)."""

# --- Streamlit 페이지 설정 ---
PAGE_TITLE = "TrendFit"
PAGE_ICON = "📈"
PAGE_LAYOUT = "wide"

SERVICE_TAGLINE = "관심사에 맞춘 급상승 트렌드를 가장 먼저 만나보세요"
SERVICE_DESCRIPTION = (
    "TrendFit은 관심 분야·목적·연령대·선호 플랫폼에 맞춰 "
    "네이버 데이터랩, 구글 트렌드, 유튜브, X, 포털 뉴스 데이터를 분석해 "
    "급상승 키워드와 인사이트를 제공합니다."
)


class SessionKeys:
    """`st.session_state`에서 사용하는 키 이름 (페이지 간 오타/충돌 방지)."""

    IS_AUTHENTICATED = "is_authenticated"
    USER_PROFILE = "user_profile"
    SELECTED_KEYWORD_ID = "selected_keyword_id"
    ALERT_RULES = "alert_rules"
    ALERT_PREFILL_KEYWORD = "alert_prefill_keyword"
    ALERT_HISTORY = "alert_history"
    ONBOARDING_PREVIEW_KEYWORDS = "onboarding_preview_keywords"
    AUTH_USER = "auth_user"
    ONBOARD_EDIT_MODE = "onboard_edit_mode"
    REPORTS = "reports"
    SELECTED_REPORT_ID = "selected_report_id"
    CURATION_CONTENTS = "curation_contents"
    CURATION_CURSOR = "curation_cursor"
    CURATION_ACTIVE_KEYWORD = "curation_active_keyword"
    CURATION_KEYWORD_FILTER = "curation_keyword_filter"
    CURATION_PLATFORM_FILTER = "curation_platform_filter"
    SCRAPPED_CONTENTS = "scrapped_contents"
    ADMIN_SPIKE_BATCH_STATUS = "admin_spike_batch_status"
    ADMIN_USERS = "admin_users"
    ADMIN_BLACKLIST = "admin_blacklist"
    NOTIFY_CHANNEL_PREFERENCE = "notify_channel_preference"


class WidgetKeys:
    """Streamlit 위젯 `key` 인자에 쓰는 상수 (페이지 간 key 충돌 방지, Coding_Convention §4-1)."""

    DASH_CATEGORY_FILTER = "dash_category_filter"
    DASH_PERIOD_FILTER = "dash_period_filter"
    DASH_DETAIL_PERIOD_FILTER = "dash_detail_period_filter"
    ALERT_FORM = "alert_form"
    ALERT_KEYWORD_INPUT = "alert_keyword_input"
    ALERT_THRESHOLD_SLIDER = "alert_threshold_slider"
    ALERT_CHANNEL_MULTISELECT = "alert_channel_multiselect"
    ONBOARD_INTERESTS = "onboard_interests"
    ONBOARD_PURPOSE = "onboard_purpose"
    ONBOARD_AGE_GROUP = "onboard_age_group"
    ONBOARD_GENDER = "onboard_gender"
    ONBOARD_PLATFORMS = "onboard_platforms"
    ONBOARD_PERIOD = "onboard_period"
    LOGIN_FORM = "login_form"
    LOGIN_EMAIL_INPUT = "login_email_input"
    LOGIN_PASSWORD_INPUT = "login_password_input"
    SIGNUP_INFO_FORM = "signup_info_form"
    SIGNUP_EMAIL_INPUT = "signup_email_input"
    SIGNUP_PASSWORD_INPUT = "signup_password_input"
    SIGNUP_PASSWORD_CONFIRM_INPUT = "signup_password_confirm_input"
    SIGNUP_TERMS_CHECKBOX = "signup_terms_checkbox"
    SIGNUP_CODE_FORM = "signup_code_form"
    SIGNUP_CODE_INPUT = "signup_code_input"
    REPORT_GENERATE_FORM = "report_generate_form"
    REPORT_CATEGORY_SELECT = "report_category_select"
    REPORT_PERIOD_SELECT = "report_period_select"
    REPORT_TITLE_INPUT = "report_title_input"
    REPORT_LIST_CATEGORY_FILTER = "report_list_category_filter"
    ADMIN_BLACKLIST_FORM = "admin_blacklist_form"
    ADMIN_BLACKLIST_INPUT = "admin_blacklist_input"
    RESET_EMAIL_FORM = "reset_email_form"
    RESET_EMAIL_INPUT = "reset_email_input"
    RESET_CODE_FORM = "reset_code_form"
    RESET_CODE_INPUT = "reset_code_input"
    RESET_PASSWORD_FORM = "reset_password_form"
    RESET_NEW_PASSWORD_INPUT = "reset_new_password_input"
    RESET_NEW_PASSWORD_CONFIRM_INPUT = "reset_new_password_confirm_input"
    CURATION_PLATFORM_MULTISELECT = "curation_platform_multiselect"
    ACCOUNT_NOTIFY_CHANNEL_MULTISELECT = "account_notify_channel_multiselect"
    ACCOUNT_DELETE_CONFIRM_CHECKBOX = "account_delete_confirm_checkbox"


# --- 관심 분야 (SRS FR-ONBOARD-001 / functional-spec ONBOARD-001과 동일 목록 재사용) ---
# 네이버 주제 필터 체계를 기준으로 확장(2026-08-12, 사용자 요청) — 원본 SRS는
# "패션/IT테크/여행/재테크/뷰티 등"으로 예시만 들었을 뿐 확정 목록이 아니었음.
CATEGORY_ALL = "all"
CATEGORY_ALL_LABEL = "전체"
CATEGORIES = [
    ("travel", "여행"),
    ("fashion", "패션"),
    ("beauty", "뷰티"),
    ("food", "푸드"),
    ("it_tech", "IT테크"),
    ("car", "자동차"),
    ("living", "리빙"),
    ("parenting", "육아"),
    ("health", "생활건강"),
    ("game", "게임"),
    ("pet", "동물/펫"),
    ("sports_leisure", "운동/레저"),
    ("pro_sports", "프로스포츠"),
    ("entertainment", "방송/연예"),
    ("music", "대중음악"),
    ("movie", "영화"),
    ("performing_arts", "공연/전시/예술"),
    ("book", "도서"),
    ("economy_business", "경제/비즈니스"),
    ("education", "어학/교육"),
]

# --- 대시보드 기간 필터 (functional-spec FR-DASH-001 / FR-DASH-006) ---
PERIOD_OPTIONS = [
    ("24h", "최근 24시간"),
    ("1w", "최근 1주일"),
    ("1m", "최근 1개월"),
]
DEFAULT_PERIOD = "1w"

# --- 대시보드 데이터 정책 ---
DASHBOARD_TOP_N = 20  # functional-spec FR-DASH-001: 언급량·Spike Score 기준 상위 20개 반환
DASHBOARD_CACHE_TTL_SECONDS = 3600  # NFR-PERF-002: 최대 1시간 이내 데이터 반영

# --- 키워드 상세(DASH-002) 데이터 정책 (functional-spec FR-DASH-004) ---
RELATED_KEYWORDS_TOP_N = 10  # "연관 키워드 Top 10" 명시
# 언급량이 이 값 미만이면 감성분석 데이터 부족(VALID_003)으로 간주해 해당 영역을 비활성화한다.
SENTIMENT_MIN_MENTION_COUNT = 2000

# --- 연령·성별 관심도 가중치 보정(DASH-002) 정책 (SRS FR-DASH-005, P2) ---
# 실제 데이터 소스(유튜브/X 등) 미확보로 보정 산식이 미정이다(docs/KPI_Definitions.md 참고).
# 연령대는 온보딩의 AGE_GROUP_OPTIONS를 재사용하고, 성별은 집계 표시에 맞게 남/여만 사용한다.
DEMOGRAPHIC_GENDERS = [
    ("male", "남성"),
    ("female", "여성"),
]

# --- 급상승 알림(ALERT-001) 정책 (functional-spec FR-ALERT-001) ---
MAX_ALERT_KEYWORDS = 20  # 사용자당 최대 등록 키워드 수
MAX_ALERT_KEYWORD_LENGTH = 50
DEFAULT_THRESHOLD_SCORE = 70  # Spike Score 0~100, 기본값 70
NOTIFY_CHANNELS = [
    ("email", "이메일"),
    ("inapp", "인앱"),
]
DEFAULT_NOTIFY_CHANNELS = ["inapp"]  # 이메일 발송 연동 전이라 인앱만 기본 선택

# --- 급상승 알림 히스토리(ALERT-002) 정책 (functional-spec FR-ALERT-003/FR-ALERT-004) ---
# 실제 배치 발송 워커(FR-ALERT-003)가 없어, 등록된 키워드마다 발송됐다고 가정한 이력을 생성한다.
ALERT_HISTORY_MAX_EVENTS_PER_KEYWORD = 3
ALERT_HISTORY_FAILURE_RATE = 0.15  # SERVER_005 발송 실패 상태를 일부 섞어 예외 UX 시연

# --- 관심사 프로필(ONBOARD-001) 옵션 (functional-spec FR-ONBOARD-001/002) ---
MIN_INTERESTS = 1
MAX_INTERESTS = 5

PURPOSE_OPTIONS = [
    ("content_planning", "콘텐츠 기획"),
    ("sales", "상품 판매"),
    ("market_research", "시장 조사"),
    ("casual", "기분 전환"),
]

AGE_GROUP_OPTIONS = [
    ("10s", "10대"),
    ("20s", "20대"),
    ("30s", "30대"),
    ("40s", "40대"),
    ("50s", "50대"),
    ("60plus", "60대 이상"),
]

GENDER_OPTIONS = [
    ("unspecified", "선택 안 함"),
    ("male", "남성"),
    ("female", "여성"),
]

PLATFORM_OPTIONS = [
    ("naver_blog", "네이버 블로그"),
    ("youtube", "유튜브"),
    ("instagram", "인스타그램"),
    ("threads", "쓰레드"),
]

PREVIEW_KEYWORDS_TOP_N = 5  # functional-spec: 추천 키워드 상위 5개 사전 산출

# --- 로그인(COM-002) 정책 (SRS FR-AUTH-001) ---
# SRS/functional-spec에 비밀번호 정책이 별도로 정의되어 있지 않아, 실제 인증 백엔드 연동 전까지
# 임시로 최소 길이만 적용한다. 실제 연동 시 정책을 재검토할 것.
MIN_PASSWORD_LENGTH = 8


class UserRole:
    """`AuthUser.role`에서 사용하는 값 (IA 접근권한 열 U=일반 사용자, A=관리자에 대응)."""

    USER = "user"
    ADMIN = "admin"


# --- 역할(ADMIN) 판별 정책 ---
# 실제 사용자 저장소·역할 관리 기능(functional-spec FR-ADMIN-002 범위 밖)이 붙기 전까지,
# 이 화이트리스트에 등록된 이메일로 로그인하면 관리자(UserRole.ADMIN)로 간주하는 목(mock)이다.
# 실제 운영 전환 시 DB의 역할 컬럼 조회로 교체하고 이 목록은 제거할 것.
ADMIN_EMAILS = [
    "admin@trendfit.com",
]

# --- 회원가입(COM-003) 정책 (SRS FR-AUTH-003) ---
# 실제 이메일 발송(SMTP) 연동 전까지 인증번호를 화면에 직접 노출하는 목(mock) 인증이다.
SIGNUP_VERIFICATION_CODE_LENGTH = 6

# --- 소셜 로그인(COM-002) 정책 (SRS FR-AUTH-002, P2) ---
# 실제 OAuth 연동 전까지 버튼 클릭 시 즉시 로그인 처리하는 목(mock)이다.
SOCIAL_PROVIDERS = [
    ("google", "구글"),
    ("kakao", "카카오"),
]

# --- 인사이트 리포트(REPORT-001) 정책 (functional-spec FR-REPORT-001) ---
MAX_REPORT_TITLE_LENGTH = 50  # 미입력 시 자동 생성
WORD_CLOUD_TOP_N = 15
NETWORK_GRAPH_NODE_TOP_N = 8
REPORT_RECOMMENDED_KEYWORDS_TOP_N = 5

# --- 유사 관심사 비교 추천(REPORT-002) 정책 (SRS FR-REPORT-005) ---
# 실제 사용자 행동 기반 유사도 클러스터링 전까지, 고정 매핑으로 "유사 분야"를 정의한다.
# 산정 방법은 docs/KPI_Definitions.md "유사 관심사 비교 추천 키워드" 항목과 일치시킬 것.
SIMILAR_CATEGORIES: dict[str, list[str]] = {
    "travel": ["education", "living"],
    "fashion": ["beauty", "living"],
    "beauty": ["fashion", "food"],
    "food": ["living", "beauty"],
    "it_tech": ["car", "economy_business"],
    "car": ["it_tech", "economy_business"],
    "living": ["fashion", "food"],
    "parenting": ["health", "pet"],
    "health": ["parenting", "pet"],
    "game": ["sports_leisure", "pro_sports"],
    "pet": ["parenting", "health"],
    "sports_leisure": ["pro_sports", "game"],
    "pro_sports": ["sports_leisure", "game"],
    "entertainment": ["music", "movie"],
    "music": ["entertainment", "movie"],
    "movie": ["entertainment", "performing_arts"],
    "performing_arts": ["movie", "book"],
    "book": ["performing_arts", "education"],
    "economy_business": ["it_tech", "car"],
    "education": ["book", "travel"],
}
SIMILAR_GROUP_KEYWORDS_TOP_N = 5

# --- 리포트 PDF/공유(REPORT-002) 정책 (SRS FR-REPORT-004) ---
# PDF 한글 렌더링은 Windows 시스템 폰트(맑은 고딕)에 의존한다. 리눅스/컨테이너 배포 시
# 이 경로가 없으므로, 한글 폰트 파일을 프로젝트에 번들링하고 경로를 교체해야 한다.
REPORT_PDF_FONT_PATH = "C:/Windows/Fonts/malgun.ttf"
# 실제 백엔드/영속 저장소가 없어, 다른 세션·기기에서는 열리지 않는 표시용 목 링크다.
REPORT_SHARE_LINK_BASE_URL = "https://trendfit.app/reports"

# --- 콘텐츠 큐레이션(CURATE-001) 정책 (functional-spec FR-CURATE-001) ---
CURATION_PAGE_SIZE = 10  # 커서 1회 요청당 반환 개수
CURATION_TOTAL_MOCK_ITEMS = 37  # "더 보기"가 끝나는 지점을 보여주기 위한 임의의 목 데이터 총량
CURATION_PLATFORMS = [
    ("naver_blog", "네이버 블로그"),
    ("youtube", "유튜브"),
    ("instagram", "인스타그램"),
    ("threads", "쓰레드"),
]

# --- 관리자 대시보드(ADMIN-001) 정책 (SRS FR-ADMIN-001) ---
# 외부 연동은 API_Design.md §8 기준 전부 미구현이라, 가짜 호출량 대신 실제 상태를 그대로 보여준다.
EXTERNAL_DATA_SOURCES = [
    ("naver_datalab", "네이버 데이터랩"),
    ("google_trends", "구글 트렌드"),
    ("youtube_api", "유튜브 데이터 API"),
    ("x_api", "X(트위터) API"),
    ("news_api", "포털 뉴스 검색 API"),
]

# --- 사용자·키워드 관리(ADMIN-002) 정책 (SRS FR-ADMIN-002) ---
# 실제 다중 사용자 DB 연동 전 단계라, 사용자 목록/키워드 통계/신고 내역은 전부 샘플 데이터다.
ADMIN_MOCK_USER_COUNT = 8
ADMIN_MOCK_REPORT_COUNT = 4
ADMIN_KEYWORD_STAT_TOP_N = 6
MAX_BLACKLIST_KEYWORD_LENGTH = 50
