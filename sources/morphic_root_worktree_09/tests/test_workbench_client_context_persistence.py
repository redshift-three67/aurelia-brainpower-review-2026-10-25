from __future__ import annotations

from pathlib import Path

from apps.web.main import create_app
from tests.test_web_shell import request


ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "apps" / "web" / "static" / "index.html"
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"


def test_workbench_draft_rejects_optional_client_context_without_explicit_consent(
    tmp_path: Path,
) -> None:
    app = create_app(runtime_dir=tmp_path)

    response = request(
        app,
        "PUT",
        "/api/workbench/draft",
        json_body={
            "draft": {
                "birth_time": "08:30",
                "email": "synthetic@example.invalid",
            },
            "updated_at": None,
            "persist_sensitive_data": False,
        },
    )

    assert response.status_code == 422
    assert "explizite" in response.json()["detail"]


def test_optional_client_context_is_explicitly_opt_in_and_not_part_of_scan_payload() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    payload = APP_JS.read_text(encoding="utf-8")

    assert 'id="optional-client-context"' in html
    assert 'name="birth_time"' in html
    assert 'name="email"' in html
    assert 'name="notes"' in html
    assert 'id="context-persistence-consent"' in html
    assert 'id="save-client-context-button"' in html
    assert "function clientContextDraftPayload()" in payload
    assert "persist_sensitive_data: true" in payload
    scan_payload = payload.split("function formScanPayload(options = {})", 1)[1].split(
        "function clientContextDraftPayload()", 1
    )[0]
    for field_name in ("birth_time", "email", "notes"):
        assert f"{field_name}:" not in scan_payload
