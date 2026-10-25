from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI, HTTPException
from starlette.requests import Request

from apps.web.admin_security import (
    ADMIN_TOKEN_HEADER,
    AdminSecurity,
    AdminSecurityError,
    require_admin_request,
)
from apps.web.main import create_app


EXPECTED_ORIGIN = "http://127.0.0.1:8000"
EXPECTED_HOST = "127.0.0.1:8000"
ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "Run-WebUI.ps1"


class Clock:
    def __init__(self) -> None:
        self.value = datetime(2026, 7, 17, 12, 0, tzinfo=UTC)

    def now(self) -> datetime:
        return self.value

    def advance(self, seconds: int) -> None:
        self.value += timedelta(seconds=seconds)


class AsgiResponse:
    def __init__(self, status_code: int, body: bytes, headers: list[tuple[bytes, bytes]]):
        self.status_code = status_code
        self.body = body
        self.text = body.decode("utf-8")
        self.headers = {
            key.decode("latin1").lower(): value.decode("latin1")
            for key, value in headers
        }

    def json(self) -> dict[str, Any]:
        return json.loads(self.text)


def _request(app: FastAPI, headers: dict[str, str] | None = None) -> Request:
    raw_headers = [
        (key.lower().encode("ascii"), value.encode("ascii"))
        for key, value in (headers or {}).items()
    ]
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/admin/catalog/drafts",
        "raw_path": b"/api/admin/catalog/drafts",
        "query_string": b"",
        "headers": raw_headers,
        "client": ("127.0.0.1", 50000),
        "server": ("127.0.0.1", 8000),
        "app": app,
    }
    return Request(scope)


def _asgi_request(
    app: Any,
    method: str,
    path: str,
    *,
    json_body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> AsgiResponse:
    body = json.dumps(json_body or {}).encode("utf-8") if json_body is not None else b""
    request_headers = [(b"host", EXPECTED_HOST.encode("ascii"))]
    for key, value in (headers or {}).items():
        if key.lower() == "host":
            request_headers = [
                (existing_key, existing_value)
                for existing_key, existing_value in request_headers
                if existing_key != b"host"
            ]
        request_headers.append((key.lower().encode("ascii"), value.encode("ascii")))
    if json_body is not None:
        request_headers.extend(
            [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode("ascii")),
            ]
        )

    async def run() -> AsgiResponse:
        sent = False
        events: list[dict[str, Any]] = []

        async def receive() -> dict[str, Any]:
            nonlocal sent
            if sent:
                return {"type": "http.disconnect"}
            sent = True
            return {"type": "http.request", "body": body, "more_body": False}

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
            "headers": request_headers,
            "client": ("127.0.0.1", 50000),
            "server": ("127.0.0.1", 8000),
            "scheme": "http",
        }
        await app(scope, receive, send)
        status = next(
            event["status"]
            for event in events
            if event["type"] == "http.response.start"
        )
        response_headers = next(
            event["headers"]
            for event in events
            if event["type"] == "http.response.start"
        )
        response_body = b"".join(
            event.get("body", b"")
            for event in events
            if event["type"] == "http.response.body"
        )
        return AsgiResponse(status, response_body, response_headers)

    return asyncio.run(run())


def _security(clock: Clock | None = None) -> AdminSecurity:
    return AdminSecurity.create(
        expected_origin=EXPECTED_ORIGIN,
        expected_host=EXPECTED_HOST,
        now=clock.now if clock is not None else None,
    )


def _issue_admin_token(security: AdminSecurity, clock: Clock | None = None) -> str:
    now = clock.now if clock is not None else None
    nonce = security.create_bootstrap_nonce(now=now)
    issue = security.exchange_bootstrap_nonce(
        nonce,
        origin=EXPECTED_ORIGIN,
        host=EXPECTED_HOST,
        now=now,
        client_id="127.0.0.1",
    )
    return issue.token


def test_admin_mutation_dependency_fails_closed_without_explicit_admin_security() -> None:
    app = FastAPI()
    app.state.operator_context = object()
    request = _request(
        app,
        {
            ADMIN_TOKEN_HEADER: "not-enough",
            "Origin": EXPECTED_ORIGIN,
            "Host": EXPECTED_HOST,
        },
    )

    with pytest.raises(HTTPException) as exc_info:
        require_admin_request(request)

    assert exc_info.value.status_code == 503
    assert "admin security not configured" in exc_info.value.detail


def test_api_key_operator_context_and_entitlement_stub_do_not_authorize_admin() -> None:
    clock = Clock()
    security = _security(clock)
    token = _issue_admin_token(security, clock)
    app = FastAPI()
    app.state.admin_security = security
    app.state.operator_context = object()
    app.state.entitlements = {"admin": True}

    request = _request(
        app,
        {
            "X-API-Key": token,
            "Origin": EXPECTED_ORIGIN,
            "Host": EXPECTED_HOST,
        },
    )

    with pytest.raises(HTTPException) as exc_info:
        require_admin_request(request)

    assert exc_info.value.status_code == 401
    assert "X-Morphic-Admin-Token" in exc_info.value.detail


def test_admin_token_uses_separate_header_and_origin_host_gate() -> None:
    clock = Clock()
    security = _security(clock)
    token = _issue_admin_token(security, clock)
    app = FastAPI()
    app.state.admin_security = security

    authorized = require_admin_request(
        _request(
            app,
            {
                ADMIN_TOKEN_HEADER: token,
                "Origin": EXPECTED_ORIGIN,
                "Host": EXPECTED_HOST,
            },
        )
    )

    assert authorized is security

    wrong_origin = _request(
        app,
        {
            ADMIN_TOKEN_HEADER: token,
            "Origin": "http://localhost:8000",
            "Host": EXPECTED_HOST,
        },
    )
    with pytest.raises(HTTPException) as exc_info:
        require_admin_request(wrong_origin)
    assert exc_info.value.status_code == 403


def test_admin_token_accepts_same_origin_request_without_origin_header() -> None:
    clock = Clock()
    security = _security(clock)
    token = _issue_admin_token(security, clock)
    app = FastAPI()
    app.state.admin_security = security

    authorized = require_admin_request(
        _request(
            app,
            {
                ADMIN_TOKEN_HEADER: token,
                "Host": EXPECTED_HOST,
            },
        )
    )

    assert authorized is security


def test_bootstrap_nonce_is_single_use_bound_and_timeout_consumes_it() -> None:
    clock = Clock()
    security = _security(clock)
    nonce = security.create_bootstrap_nonce(now=clock.now)

    issue = security.exchange_bootstrap_nonce(
        nonce,
        origin=EXPECTED_ORIGIN,
        host=EXPECTED_HOST,
        now=clock.now,
        client_id="127.0.0.1",
    )

    assert issue.token_type == ADMIN_TOKEN_HEADER
    assert issue.token != nonce
    assert len(issue.token) >= 43

    with pytest.raises(AdminSecurityError):
        security.exchange_bootstrap_nonce(
            nonce,
            origin=EXPECTED_ORIGIN,
            host=EXPECTED_HOST,
            now=clock.now,
            client_id="127.0.0.1",
        )

    wrong_origin_nonce = security.create_bootstrap_nonce(now=clock.now)
    with pytest.raises(AdminSecurityError):
        security.exchange_bootstrap_nonce(
            wrong_origin_nonce,
            origin="http://localhost:8000",
            host=EXPECTED_HOST,
            now=clock.now,
            client_id="127.0.0.1",
        )
    with pytest.raises(AdminSecurityError):
        security.exchange_bootstrap_nonce(
            wrong_origin_nonce,
            origin=EXPECTED_ORIGIN,
            host=EXPECTED_HOST,
            now=clock.now,
            client_id="127.0.0.1",
        )

    expired_nonce = security.create_bootstrap_nonce(now=clock.now)
    clock.advance(31)
    with pytest.raises(AdminSecurityError):
        security.exchange_bootstrap_nonce(
            expired_nonce,
            origin=EXPECTED_ORIGIN,
            host=EXPECTED_HOST,
            now=clock.now,
            client_id="127.0.0.1",
        )


def test_admin_token_ttl_and_constant_time_compare_contract() -> None:
    clock = Clock()
    security = _security(clock)
    token = _issue_admin_token(security, clock)

    assert security.verify_admin_token(
        token, origin=EXPECTED_ORIGIN, host=EXPECTED_HOST, now=clock.now
    )
    assert not security.verify_admin_token(
        token, origin=EXPECTED_ORIGIN, host="localhost:8000", now=clock.now
    )

    clock.advance(901)
    assert not security.verify_admin_token(
        token, origin=EXPECTED_ORIGIN, host=EXPECTED_HOST, now=clock.now
    )

    source = (ROOT / "apps" / "web" / "admin_security.py").read_text(
        encoding="utf-8"
    )
    assert "secrets.compare_digest" in source
    assert "X-API-Key" not in source


def test_bootstrap_exchange_endpoint_is_fail_closed_without_pending_launch() -> None:
    app = create_app()

    response = _asgi_request(
        app,
        "POST",
        "/api/admin/bootstrap/exchange",
        json_body={"nonce": "x" * 43},
        headers={"Origin": EXPECTED_ORIGIN, "Host": EXPECTED_HOST},
    )

    assert response.status_code == 503
    assert "set-cookie" not in response.headers


def test_bootstrap_exchange_endpoint_returns_token_without_cookie() -> None:
    clock = Clock()
    security = _security(clock)
    nonce = security.create_bootstrap_nonce(now=clock.now)
    app = create_app()
    app.state.admin_security = security

    response = _asgi_request(
        app,
        "POST",
        "/api/admin/bootstrap/exchange",
        json_body={"nonce": nonce},
        headers={"Origin": EXPECTED_ORIGIN, "Host": EXPECTED_HOST},
    )

    payload = response.json()
    assert response.status_code == 200
    assert payload["token_type"] == ADMIN_TOKEN_HEADER
    assert payload["token"] != nonce
    assert "set-cookie" not in response.headers

    replay = _asgi_request(
        app,
        "POST",
        "/api/admin/bootstrap/exchange",
        json_body={"nonce": nonce},
        headers={"Origin": EXPECTED_ORIGIN, "Host": EXPECTED_HOST},
    )
    assert replay.status_code == 403


def test_launcher_bootstraps_nonce_in_fragment_without_token_or_terminal_output() -> None:
    source = LAUNCHER.read_text(encoding="utf-8")

    assert "New-MorphicAdminBootstrapNonce" in source
    assert "MORPHIC_ADMIN_BOOTSTRAP_NONCE" in source
    assert "#admin_nonce=$AdminBootstrapNonce" in source
    assert "X-Morphic-Admin-Token" not in source
    assert "Write-Host $AdminBootstrapNonce" not in source
    assert "Clipboard" not in source
    assert "localStorage" not in source
    assert "sessionStorage" not in source
