from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from apps.web.main import create_app


ROOT = Path(__file__).resolve().parents[1]
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"
SAFE_SOURCE_KEYS = {
    "active",
    "description",
    "enabled",
    "id",
    "label",
    "scopes",
    "status",
    "warnings",
}
FORBIDDEN_WORKBENCH_SOURCE_KEYS = {
    "approval_receipt",
    "documentation_url",
    "download_url",
    "endpoint",
    "homepage",
    "import_policy",
    "license",
    "local_path",
    "name",
    "source_type",
    "trust_level",
}


class AsgiResponse:
    def __init__(self, status_code: int, body: bytes):
        self.status_code = status_code
        self.body = body
        self.text = body.decode("utf-8")

    def json(self) -> dict[str, Any]:
        return json.loads(self.text)


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

        scope = {
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
        }
        await app(scope, receive, send)
        status = next(
            event["status"]
            for event in events
            if event["type"] == "http.response.start"
        )
        response_body = b"".join(
            event.get("body", b"")
            for event in events
            if event["type"] == "http.response.body"
        )
        return AsgiResponse(status, response_body)

    return asyncio.run(run())


def test_sources_api_returns_reduced_workbench_safe_view() -> None:
    response = request(create_app(), "GET", "/api/sources")

    payload = response.json()
    sources = payload["sources"]

    assert response.status_code == 200
    assert sources
    assert {"active", "disabled", "quarantined"}.issubset(payload["status_counts"])
    assert any(source["id"] == "clark_frequencies_legacy" for source in sources)
    assert all("label" in source for source in sources)
    assert all("name" not in source for source in sources)
    assert all(set(source).issubset(SAFE_SOURCE_KEYS) for source in sources)
    for source in sources:
        assert not (set(source) & FORBIDDEN_WORKBENCH_SOURCE_KEYS)


def test_workbench_sources_dom_uses_label_contract_not_name_or_admin_details() -> None:
    source = APP_JS.read_text(encoding="utf-8")
    block = source.split("const sources = await window.MorphicWorkbenchApi.loadSources();", 1)[
        1
    ].split("/* \u2500\u2500 Hardware Truth", 1)[0]

    assert "s.label" in block
    assert "s.name" not in block
    assert "local_path" not in block
    assert "import_policy" not in block
    assert "trust_level" not in block
