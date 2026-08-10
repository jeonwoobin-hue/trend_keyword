"""리포트 내보내기(PDF 다운로드·공유 링크) 도메인 로직 (SRS FR-REPORT-004).

PDF 생성은 로컬 Windows 폰트(맑은 고딕)에 의존한다. 실제 배포 환경(리눅스 컨테이너 등)에서는
한글 폰트 파일을 프로젝트에 번들링하고 `REPORT_PDF_FONT_PATH`를 교체해야 한다. 공유 링크는
실제 백엔드·영속 저장소가 없어 리포트 ID를 포함한 표시용 URL만 생성한다(다른 세션에서는 열리지 않음).
"""

from fpdf import FPDF

from config.constants import CATEGORIES, PERIOD_OPTIONS, REPORT_PDF_FONT_PATH, REPORT_SHARE_LINK_BASE_URL
from models.report import Report

_FONT_NAME = "Malgun"


class ReportExportError(Exception):
    """PDF 생성 실패 시 사용자 메시지를 함께 담는 예외 (API_Design.md §3 공통 에러 코드 기준)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def build_report_pdf(report: Report) -> bytes:
    """리포트 내용을 PDF 바이트로 생성한다.

    Raises:
        ReportExportError: 한글 렌더링에 필요한 폰트 파일을 찾을 수 없을 때.
    """
    pdf = FPDF()
    pdf.add_page()
    try:
        pdf.add_font(_FONT_NAME, "", REPORT_PDF_FONT_PATH)
    except FileNotFoundError as error:
        raise ReportExportError("SERVER_001", "PDF 생성에 필요한 한글 폰트를 찾을 수 없습니다.") from error

    category_label = dict(CATEGORIES).get(report.category, report.category)
    period_label = dict(PERIOD_OPTIONS).get(report.period, report.period)

    _write_line(pdf, report.title, size=16)
    _write_line(pdf, f"{category_label} · {period_label} · {report.created_at:%Y-%m-%d %H:%M} UTC", size=10)
    pdf.ln(4)

    _add_section(pdf, "이슈 요약", report.summary)
    _add_section(
        pdf, "Word Cloud", ", ".join(f"{item.keyword}({item.weight})" for item in report.word_cloud) or "-"
    )
    _add_section(pdf, "추천 키워드", ", ".join(report.recommended_keywords) or "-")
    _add_section(pdf, "유사 관심사 비교 추천 키워드", ", ".join(report.similar_group_keywords) or "-")

    return bytes(pdf.output())


def _add_section(pdf: FPDF, heading: str, body: str) -> None:
    """PDF에 소제목 + 본문 한 블록을 추가한다."""
    _write_line(pdf, heading, size=13)
    _write_line(pdf, body, size=10)
    pdf.ln(3)


def _write_line(pdf: FPDF, text: str, size: int) -> None:
    """한 줄(또는 자동 줄바꿈 블록)을 쓰고, 다음 줄을 위해 x좌표를 왼쪽 여백으로 되돌린다.

    `multi_cell`의 기본값(`new_x=XPos.RIGHT`)은 x를 방금 쓴 텍스트의 오른쪽 끝에 남겨두어,
    다음 호출의 가용 폭(w=0)이 거의 0이 되는 문제가 있어 명시적으로 재설정한다.
    """
    pdf.set_font(_FONT_NAME, size=size)
    pdf.multi_cell(0, size * 0.7, text=text, new_x="LMARGIN", new_y="NEXT")


def build_share_link(report_id: str) -> str:
    """리포트 공유 링크를 생성한다 (실제 백엔드 없음 — 표시용 목 링크)."""
    return f"{REPORT_SHARE_LINK_BASE_URL}/{report_id}"
