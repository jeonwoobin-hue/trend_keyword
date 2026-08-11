"""상단 호버 드롭다운 메뉴 컴포넌트.

기존에는 Streamlit이 `pages/` 아래 15개 스크립트를 사이드바에 그대로 나열했다. 화면이
많아질수록 목록이 길어지는 문제가 있어, 상위 카테고리(트렌드/인사이트/마이페이지/관리자)에
마우스를 올리면 하위 화면이 펼쳐지는 상단 메뉴로 대체한다. 사이드바 기본 내비게이션은 숨긴다.

Streamlit은 `pages/3_📊_트렌드_대시보드.py` 같은 파일명에서 앞자리 숫자(`3_`)와 아이콘
이모지를 제거한 나머지를 URL 경로로 사용한다(`/트렌드_대시보드`). 그 규칙을 `_slug()`로
그대로 옮겨, 파일명이 곧 링크 주소가 되도록 했다 — 파일이 나중에 옮겨져도 이 표만 고치면
링크가 깨지지 않는다.
"""

import re

import streamlit as st
import streamlit.components.v1 as components

from config.constants import PAGE_ICON, PAGE_TITLE, SessionKeys, UserRole

_LEADING_NUMBER_RE = re.compile(r"^\d+_")
_LEADING_EMOJI_RE = re.compile("^[\U0001F300-\U0001FAFF☀-➿]️?_")

# (라벨, pages/ 파일 경로)
_NavItem = tuple[str, str]

# (그룹 key, 그룹 라벨, 하위 항목, 관리자(UserRole.ADMIN)에게만 노출할지 여부)
# 하위 항목이 없는 그룹(홈)은 그룹 라벨 클릭이 곧 이동 링크가 된다.
_NAV_GROUPS: list[tuple[str, str, list[_NavItem], bool]] = [
    ("home", "🏠 홈", [], False),
    (
        "trend",
        "📊 트렌드",
        [
            ("트렌드 대시보드", "pages/3_📊_트렌드_대시보드.py"),
            ("키워드 상세", "pages/4_🔍_키워드_상세.py"),
            ("급상승 알림", "pages/5_🔔_급상승_알림.py"),
        ],
        False,
    ),
    (
        "insight",
        "📰 인사이트",
        [
            ("인사이트 리포트", "pages/7_📰_인사이트_리포트.py"),
            ("리포트 상세", "pages/10_🗺️_리포트_상세.py"),
            ("콘텐츠 큐레이션", "pages/8_🎬_콘텐츠_큐레이션.py"),
            ("콘텐츠 상세", "pages/15_📄_콘텐츠_상세.py"),
        ],
        False,
    ),
    (
        "mypage",
        "🙋 마이페이지",
        [
            ("마이페이지", "pages/6_🙋_마이페이지.py"),
            ("관심사 설정", "pages/2_📝_관심사_설정.py"),
            ("계정 설정", "pages/14_⚙️_계정_설정.py"),
            ("비밀번호 재설정", "pages/13_🔓_비밀번호_재설정.py"),
            ("알림함", "pages/11_📬_알림함.py"),
        ],
        False,
    ),
    (
        "admin",
        "🛠️ 관리자",
        [
            ("관리자 대시보드", "pages/9_🛠️_관리자.py"),
            ("사용자·키워드 관리", "pages/12_🗂️_사용자_키워드_관리.py"),
        ],
        True,
    ),
]


def _slug(file_path: str) -> str:
    """`pages/3_📊_트렌드_대시보드.py` → `/트렌드_대시보드` (Home.py는 `/`)."""
    if file_path == "Home.py":
        return "/"
    stem = file_path.rsplit("/", 1)[-1].removesuffix(".py")
    stem = _LEADING_NUMBER_RE.sub("", stem)
    stem = _LEADING_EMOJI_RE.sub("", stem)
    return f"/{stem}"


_NAV_CSS = """
<style>
[data-testid="stSidebar"] { display: none; }

.tf-nav {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    margin: -1rem -1rem 1.5rem -1rem;
    border-bottom: 1px solid rgba(128, 128, 128, 0.25);
    background: rgba(128, 128, 128, 0.06);
    font-family: inherit;
}
.tf-nav a { text-decoration: none; color: inherit; }
.tf-brand {
    font-weight: 700;
    font-size: 1.05rem;
    padding: 10px 14px 10px 4px;
    margin-right: 8px;
    white-space: nowrap;
}
.tf-item { position: relative; }
.tf-item > a, .tf-item > span.tf-label {
    display: block;
    padding: 10px 14px;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    white-space: nowrap;
}
.tf-item.active > a, .tf-item.active > span.tf-label {
    box-shadow: inset 0 -2px 0 0 #ff4b4b;
}
.tf-item > a:hover, .tf-item > span.tf-label:hover {
    background: rgba(128, 128, 128, 0.15);
}
.tf-dropdown {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    min-width: 200px;
    padding: 6px;
    border-radius: 8px;
    border: 1px solid rgba(128, 128, 128, 0.25);
    background: var(--tf-dropdown-bg, #ffffff);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
    z-index: 999;
}
.tf-item:hover .tf-dropdown { display: block; }
.tf-dropdown a {
    display: block;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.92rem;
    white-space: nowrap;
}
.tf-dropdown a:hover { background: rgba(128, 128, 128, 0.15); }

@media (prefers-color-scheme: dark) {
    .tf-dropdown { --tf-dropdown-bg: #262730; }
}
</style>
"""


# 순수 HTML `<a href>`로 페이지를 이동시키면 브라우저가 실제로 새로고침되어 Streamlit
# 세션(session_state, 로그인 상태 포함)이 통째로 초기화된다. 반면 Streamlit이 자체적으로
# 그리는 사이드바 링크(`data-testid="stSidebarNavLink"`, CSS로 화면에서만 숨김)는 프론트엔드의
# 클라이언트 사이드 라우팅을 타므로 세션이 유지된다. 그래서 클릭 시 실제 이동은 막고
# (`preventDefault`) 같은 경로를 가진 숨겨진 사이드바 링크를 대신 클릭해 위임한다.
#
# `st.markdown(unsafe_allow_html=True)`는 XSS 방지를 위해 `onclick` 같은 인라인 이벤트
# 속성을 조용히 제거한다. 그래서 클릭 처리는 `st.components.v1.html()`로 만든, 화면에 보이지
# 않는 iframe 안의 `<script>`가 담당한다 — iframe은 부모 문서와 동일 출처라 `window.parent`로
# 실제 페이지 DOM에 이벤트 리스너를 붙일 수 있고, 여기 담긴 `<script>`는 (markdown과 달리)
# 정상적으로 실행된다.
#
# 페이지를 옮길 때마다 이 iframe도 새로 마운트되므로 리스너도 매번 새로 붙인다 — "이미
# 붙였으면 건너뛰기" 같은 플래그를 문서에 남기지 않는다. 예전엔 그런 플래그를 뒀었는데,
# 이전 페이지의 iframe이 사라지면 브라우저가 그 iframe이 등록한 리스너를 자동으로 정리해
# 버려서, 플래그만 "이미 붙어있음"으로 남고 실제로 반응하는 리스너는 없는 상태가 되는 버그가
# 있었다 (그 상태에서 메뉴를 클릭하면 진짜 페이지 새로고침이 일어나 로그인 세션이 날아갔다).
_NAV_SCRIPT = """
<script>
(function () {
    var doc = window.parent.document;

    function navigate(href) {
        var links = doc.querySelectorAll('[data-testid="stSidebarNavLink"]');
        for (var i = 0; i < links.length; i++) {
            var pathname = decodeURIComponent(
                new URL(links[i].getAttribute("href"), doc.location.origin).pathname
            );
            if (pathname === href) {
                links[i].click();
                return;
            }
        }
        doc.location.href = href;
    }

    doc.addEventListener("click", function (event) {
        var link = event.target.closest("a.tf-navlink");
        if (!link) return;
        event.preventDefault();
        navigate(link.getAttribute("data-tf-href"));
    });
})();
</script>
"""


def _nav_anchor(label: str, href: str, class_attr: str = "") -> str:
    """세션을 유지한 채 `href`로 이동하는 `<a>` 태그를 만든다 (클릭 처리는 `_NAV_SCRIPT` 참고)."""
    class_html = f"tf-navlink {class_attr}".strip()
    return f'<a class="{class_html}" href="{href}" data-tf-href="{href}" target="_self">{label}</a>'


def render_top_nav(current_group: str | None = None) -> None:
    """상단 호버 드롭다운 메뉴를 렌더링한다.

    각 페이지 스크립트에서 `init_session_state()` 다음 줄에 호출한다. `current_group`에
    현재 페이지가 속한 그룹 key(`trend`/`insight`/`mypage`/`admin`)를 넘기면 해당 메뉴가
    강조 표시된다.
    """
    auth_user = st.session_state.get(SessionKeys.AUTH_USER)
    is_admin = auth_user is not None and auth_user.role == UserRole.ADMIN

    parts = [_NAV_CSS, '<nav class="tf-nav">']
    parts.append(_nav_anchor(f"{PAGE_ICON} {PAGE_TITLE}", "/", "tf-brand"))

    for key, label, items, admin_only in _NAV_GROUPS:
        if admin_only and not is_admin:
            continue

        active_class = " active" if key == current_group else ""

        if key == "home":
            parts.append(f'<div class="tf-item{active_class}">{_nav_anchor(label, "/")}</div>')
            continue

        parts.append(f'<div class="tf-item{active_class}">')
        parts.append(f'<span class="tf-label">{label}</span>')
        parts.append('<div class="tf-dropdown">')
        for item_label, file_path in items:
            parts.append(_nav_anchor(item_label, _slug(file_path)))
        parts.append("</div></div>")

    parts.append("</nav>")
    st.markdown("".join(parts), unsafe_allow_html=True)
    components.html(_NAV_SCRIPT, height=0)
