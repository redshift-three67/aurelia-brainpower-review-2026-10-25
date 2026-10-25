from pathlib import Path

from apps.web.main import create_app
from apps.web.reports import ReportCatalog
from tests.test_web_shell import request


def test_report_catalog_client_view_shows_only_html_with_grouping(
    tmp_path: Path,
) -> None:
    report_root = tmp_path / "reports"
    session_dir = (
        report_root
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20260115_101530_TOP3_SESSION"
    )
    session_dir.mkdir(parents=True)
    (session_dir / "20260115_101530_multiplex_scan.html").write_text(
        "<html><body>HTML Bericht</body></html>",
        encoding="utf-8",
    )
    (session_dir / "20260115_101530_multiplex_scan.json").write_text(
        '{"focus": "Bronchien"}',
        encoding="utf-8",
    )
    (session_dir / "20260115_101530_multiplex_scan.txt").write_text(
        "Text Bericht",
        encoding="utf-8",
    )
    (session_dir / "20260115_101530_multiplex_scan.pdf").write_bytes(b"%PDF-1.4\n")

    catalog = ReportCatalog([report_root])

    payload = catalog.list(client_view=True)

    assert payload["count"] == 1
    assert payload["client_count"] == 1
    assert payload["clients"][0]["client_id"] == "Mustermann_Klaus_09041966_Augsburg"
    assert payload["clients"][0]["label"] == "Mustermann Klaus 09041966 Augsburg"
    assert payload["clients"][0]["session_count"] == 1
    assert payload["clients"][0]["file_count"] == 1

    session = payload["clients"][0]["sessions"][0]
    assert session["session_id"] == "20260115_101530_TOP3_SESSION"
    assert session["label"] == "2026-01-15 10:15:30"

    report = session["files"][0]
    assert report["kind"] == "HTML"
    assert report["file_name"] == "20260115_101530_multiplex_scan.html"
    assert report["label"] == "Multiplex Scan"


def test_reports_api_returns_client_friendly_html_only_listing(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    client_dir = report_root / "Mustermann_Klaus_09041966_Augsburg"
    client_dir.mkdir(parents=True)
    (client_dir / "20260115_101530_multiplex_scan.html").write_text(
        "<html><body>Bericht</body></html>",
        encoding="utf-8",
    )
    (client_dir / "20260115_101530_multiplex_scan.json").write_text(
        '{"focus": "Bronchien"}',
        encoding="utf-8",
    )

    app = create_app(runtime_dir=tmp_path / "runtime", report_roots=[report_root])

    response = request(app, "GET", "/api/reports")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    session = payload["clients"][0]["sessions"][0]
    assert [entry["kind"] for entry in session["files"]] == ["HTML"]
    assert session["files"][0]["label"] == "Multiplex Scan"
