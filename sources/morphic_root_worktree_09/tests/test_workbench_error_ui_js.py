from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"


def test_preview_and_scan_start_expose_api_error_detail() -> None:
    source = APP_JS.read_text(encoding="utf-8")

    assert "function apiErrorMessage(error, fallback)" in source
    assert 'showInlineState(apiErrorMessage(e, "Vorschau fehlgeschlagen"), "bad")' in source
    assert 'apiErrorMessage(e, "Start fehlgeschlagen")' in source
    assert 'showInlineState(message, "bad")' in source


def test_start_operation_retention_does_not_infer_authority_from_status_or_detail() -> None:
    source = APP_JS.read_text(encoding="utf-8")
    retention = source.split("function shouldRetainStartOperation(error) {", 1)[1].split(
        "\n}", 1
    )[0]

    assert "if (!error?.status) return true;" in retention
    assert 'return error.startOperationDisposition !== "safe-to-replace";' in retention
    assert "error.status >= 500" not in retention
    assert "payload?.detail" not in retention
    assert "failed before job creation" not in retention
