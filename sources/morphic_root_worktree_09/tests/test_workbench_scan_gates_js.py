from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"


def test_scan_actions_require_complete_payload_and_consents() -> None:
    source = APP_JS.read_text(encoding="utf-8")

    assert "function validateScanPayload(payload, options = {})" in source
    assert '"Lokale Verarbeitung und Berichtserzeugung bestaetigen"' in source
    assert '"Wellbeing-Hinweis akzeptieren"' in source
    assert "const validationMessage = validateScanPayload(body);" in source
    assert "const validationMessage = validateScanPayload(body, {includeGroupActivation: true});" in source
    assert source.count("if (validationMessage)") >= 2


def test_scan_start_requires_server_job_id_before_navigation() -> None:
    source = APP_JS.read_text(encoding="utf-8")

    assert "const jobId = String(result.job_id || \"\").trim();" in source
    assert 'throw new Error("Serverantwort enthält keine Job-ID.")' in source
    assert "pollScanJob(jobId)" in source
