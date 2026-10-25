from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"
MAIN_PY = ROOT / "apps" / "web" / "main.py"
REPORTS_PY = ROOT / "apps" / "web" / "reports.py"


def test_report_catalog_renders_external_metadata_as_text_nodes() -> None:
    source = APP_JS.read_text(encoding="utf-8")
    report_catalog = source.split("function renderReportCatalog(", 1)[1].split(
        "function renderReportPreviewLoading", 1
    )[0]

    assert ".innerHTML" not in report_catalog
    assert "textContent" in report_catalog
    assert "document.createElement(\"details\")" not in report_catalog
    assert "document.createElement(\"summary\")" not in report_catalog
    assert 'document.createElement("button")' in report_catalog
    assert 'clientMeta.className = "report-item-client"' in report_catalog
    assert 'clientMeta.textContent = entry.client_label' in report_catalog
    assert 'sessionMeta.className = "report-item-session"' in report_catalog
    assert 'sessionMeta.textContent = entry.session_label' in report_catalog
    assert 'renderReportPreview(entry.id, caseGeneration, "manual")' in report_catalog
    assert "rl.appendChild(item)" in report_catalog


def test_report_file_route_streams_without_constructing_file_response() -> None:
    source = MAIN_PY.read_text(encoding="utf-8")
    route = source.split('@app.get("/api/reports/{report_id}/file")', 1)[1].split(
        "    def _start_operation_owner", 1
    )[0]

    assert "StreamingResponse" in route
    assert "FileResponse" not in route
    assert ".file_path(" not in route


def test_report_preview_has_no_path_reopen_or_fallback_search() -> None:
    reports_source = REPORTS_PY.read_text(encoding="utf-8")
    main_source = MAIN_PY.read_text(encoding="utf-8")

    assert "Path.read_text" not in reports_source
    assert ".read_text(" not in reports_source
    assert "def _find(" not in reports_source
    assert "._find(" not in reports_source
    assert "report_catalog_factory().file_path(" not in main_source
