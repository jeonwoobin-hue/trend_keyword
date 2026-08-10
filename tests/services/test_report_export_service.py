"""services/report_export_service.py 단위 테스트 (SRS FR-REPORT-004)."""

import services.report_export_service as report_export_service
from config.constants import REPORT_SHARE_LINK_BASE_URL
from services.report_export_service import ReportExportError, build_report_pdf, build_share_link
from services.report_service import generate_report


def test_build_report_pdf_returns_valid_pdf_bytes():
    report = generate_report("fashion", "1w", None)

    pdf_bytes = build_report_pdf(report)

    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 0


def test_build_report_pdf_raises_report_export_error_when_font_missing(monkeypatch):
    monkeypatch.setattr(report_export_service, "REPORT_PDF_FONT_PATH", "C:/no/such/font.ttf")
    report = generate_report("fashion", "1w", None)

    try:
        build_report_pdf(report)
    except ReportExportError as error:
        assert error.code == "SERVER_001"
    else:
        raise AssertionError("ReportExportError를 기대했지만 발생하지 않았습니다.")


def test_build_share_link_includes_report_id_and_base_url():
    link = build_share_link("rep_abc123")

    assert link == f"{REPORT_SHARE_LINK_BASE_URL}/rep_abc123"
    assert link.startswith("https://")
