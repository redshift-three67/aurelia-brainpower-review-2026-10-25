from __future__ import annotations

import asyncio
from typing import Any

from apps.web.main import create_app


def _get_headers(app: Any, origin: str | None = None) -> dict[str, str]:
    async def run() -> dict[str, str]:
        sent = False
        events: list[dict[str, Any]] = []
        headers = [(b"host", b"testserver")]
        if origin:
            headers.append((b"origin", origin.encode("ascii")))

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
                "method": "GET",
                "path": "/api/health",
                "raw_path": b"/api/health",
                "query_string": b"",
                "headers": headers,
                "client": ("testclient", 50000),
                "server": ("testserver", 80),
                "scheme": "http",
            },
            receive,
            send,
        )
        response_start = next(event for event in events if event["type"] == "http.response.start")
        return {key.decode("latin-1").lower(): value.decode("latin-1") for key, value in response_start["headers"]}

    return asyncio.run(run())


def test_local_operator_response_has_security_headers_and_no_cross_origin_cors() -> None:
    headers = _get_headers(create_app(), origin="https://outside.invalid")

    assert headers["x-content-type-options"] == "nosniff"
    assert headers["x-frame-options"] == "SAMEORIGIN"
    assert headers["referrer-policy"] == "no-referrer"
    assert "frame-ancestors 'self'" in headers["content-security-policy"]
    assert "access-control-allow-origin" not in headers
