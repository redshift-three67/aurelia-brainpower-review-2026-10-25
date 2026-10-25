from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from apps.web.main import create_app


ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "apps" / "web" / "static"
ADMIN_HTML = STATIC_DIR / "admin.html"
ADMIN_JS = STATIC_DIR / "admin-catalog.js"
INDEX_HTML = STATIC_DIR / "index.html"


class AsgiResponse:
    def __init__(self, status_code: int, body: bytes, headers: list[tuple[bytes, bytes]]):
        self.status_code = status_code
        self.body = body
        self.text = body.decode("utf-8")
        self.headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in headers
        }


def request(app: Any, method: str, path: str) -> AsgiResponse:
    async def run() -> AsgiResponse:
        sent = False
        events: list[dict[str, Any]] = []

        async def receive() -> dict[str, Any]:
            nonlocal sent
            if sent:
                return {"type": "http.disconnect"}
            sent = True
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message: dict[str, Any]) -> None:
            events.append(message)

        await app(
            {
                "type": "http",
                "asgi": {"version": "3.0"},
                "http_version": "1.1",
                "method": method,
                "path": path,
                "raw_path": path.encode("ascii"),
                "query_string": b"",
                "headers": [(b"host", b"testserver")],
                "client": ("testclient", 50000),
                "server": ("testserver", 80),
                "scheme": "http",
            },
            receive,
            send,
        )
        response_start = next(
            event for event in events if event["type"] == "http.response.start"
        )
        response_body = b"".join(
            event.get("body", b"")
            for event in events
            if event["type"] == "http.response.body"
        )
        return AsgiResponse(
            response_start["status"],
            response_body,
            response_start["headers"],
        )

    return asyncio.run(run())


def test_admin_catalog_shell_is_separate_from_operator_workbench() -> None:
    admin_html = ADMIN_HTML.read_text(encoding="utf-8")
    index_html = INDEX_HTML.read_text(encoding="utf-8")

    assert 'id="admin-catalog-app"' in admin_html
    assert 'src="/static/admin-catalog.js"' in admin_html
    assert 'href="/static/app.css"' in admin_html
    assert "Admin Catalog" in admin_html
    assert "admin_nonce" not in admin_html

    assert "wizard-stepper" not in admin_html
    assert "scan-form" not in admin_html
    assert "/static/admin.html" not in index_html
    assert "admin-catalog.js" not in index_html


def test_admin_catalog_js_bootstraps_from_fragment_without_persistence() -> None:
    source = ADMIN_JS.read_text(encoding="utf-8")

    assert "window.location.hash" in source
    assert "admin_nonce" in source
    assert "history.replaceState" in source
    assert '"/api/admin/bootstrap/exchange"' in source
    assert 'method: "POST"' in source
    assert '"/api/admin/catalog/status"' in source
    assert '"/api/admin/catalog/entries"' in source
    assert '"/api/admin/catalog/runtime"' in source
    assert "loadRuntime" in source
    assert "admin-load-runtime" in source
    assert '"X-Morphic-Admin-Token"' in source
    assert "let adminToken" in source
    assert "localStorage" not in source
    assert "sessionStorage" not in source
    assert "document.cookie" not in source
    assert "location.search" not in source
    assert "innerHTML" not in source


def test_admin_catalog_surface_exposes_separated_mutation_sections() -> None:
    admin_html = ADMIN_HTML.read_text(encoding="utf-8")

    for expected in (
        'id="admin-status"',
        'id="admin-entries"',
        'id="admin-draft-section"',
        'id="admin-validation-section"',
        'id="admin-publish-section"',
        'id="admin-activation-section"',
        'id="admin-rollback-section"',
        'id="admin-runtime-section"',
        'id="admin-load-runtime"',
        'id="admin-runtime-source"',
        'id="admin-runtime-revision"',
        'id="admin-runtime-redacted"',
        'id="admin-runtime"',
        'id="admin-reason"',
        'id="admin-diff"',
    ):
        assert expected in admin_html


def test_admin_catalog_static_page_is_served_no_store() -> None:
    response = request(create_app(), "GET", "/static/admin.html")

    assert response.status_code == 200
    assert 'id="admin-catalog-app"' in response.text
    assert response.headers["cache-control"] == (
        "no-store, no-cache, must-revalidate, max-age=0"
    )
    assert response.headers["pragma"] == "no-cache"
    assert response.headers["expires"] == "0"
