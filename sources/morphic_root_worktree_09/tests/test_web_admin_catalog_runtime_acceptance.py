from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Sequence

import pytest

from apps.web.admin_security import ADMIN_TOKEN_HEADER, AdminSecurity
from apps.web.main import create_app
from core.admin_catalog import AdminCatalogService, CatalogContext
from core.admin_catalog.store import CatalogStore
from core.admin_catalog.validation_attestation import HmacValidationKeyProvider


EXPECTED_ORIGIN = "http://127.0.0.1:8000"
EXPECTED_HOST = "127.0.0.1:8000"
FORBIDDEN_EVIDENCE_FRAGMENTS = (
    "birth_date",
    "email",
    "nonce",
    "patient",
    "person_name",
    "phone",
    "token",
)


class AsgiResponse:
    def __init__(self, status_code: int, body: bytes):
        self.status_code = status_code
        self.body = body
        self.text = body.decode("utf-8")

    def json(self) -> dict[str, Any]:
        return json.loads(self.text)


def request(
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
                item for item in request_headers if item[0] != b"host"
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
        response_body = b"".join(
            event.get("body", b"")
            for event in events
            if event["type"] == "http.response.body"
        )
        return AsgiResponse(status, response_body)

    return asyncio.run(run())


def catalog_context(suffix: str) -> CatalogContext:
    return CatalogContext(
        operator_id=f"operator-option-b-{suffix}",
        workspace_id=f"workspace-option-b-{suffix}",
        tenant_id=f"tenant-option-b-{suffix}",
        scope="workspace",
    )


def catalog_service(db_path: Path) -> AdminCatalogService:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return AdminCatalogService(
        CatalogStore(
            db_path,
            validation_key_provider=HmacValidationKeyProvider(
                authority_id="option-b-live-runtime-acceptance-tests",
                active_key_id="test-v1",
                keys={"test-v1": b"K" * 32},
            ),
        )
    )


def app_for_catalog(
    tmp_path: Path,
    db_path: Path,
    context: CatalogContext,
    *,
    suffix: str,
) -> Any:
    return create_app(
        runtime_dir=tmp_path / f"runtime-{suffix}",
        admin_catalog_service_factory=lambda _context: catalog_service(db_path),
        admin_catalog_context_factory=lambda _operator_context: context,
    )


def admin_headers(app: Any) -> dict[str, str]:
    security = AdminSecurity.create(
        expected_origin=EXPECTED_ORIGIN,
        expected_host=EXPECTED_HOST,
    )
    nonce = security.create_bootstrap_nonce()
    app.state.admin_security = security
    exchange = request(
        app,
        "POST",
        "/api/admin/bootstrap/exchange",
        json_body={"nonce": nonce},
        headers={"Origin": EXPECTED_ORIGIN, "Host": EXPECTED_HOST},
    )
    assert exchange.status_code == 200
    payload = exchange.json()
    return {
        ADMIN_TOKEN_HEADER: str(payload["token"]),
        "Origin": EXPECTED_ORIGIN,
        "Host": EXPECTED_HOST,
    }


def entry_payload(
    entry_type: str,
    entry_id: str,
    data: dict[str, object],
) -> dict[str, object]:
    return {
        "entry_type": entry_type,
        "entry_id": entry_id,
        "source_id": "option-b-live-runtime-acceptance",
        "provenance": "option-b-live-runtime-acceptance-test",
        "data": data,
    }


def revision_entries(
    suffix: str,
    *,
    stable_managed_ids: bool = False,
) -> tuple[dict[str, object], ...]:
    group_id = f"group-{suffix}"
    profile_id = "profile-a" if stable_managed_ids else f"profile-{suffix}"
    remedy_id = "remedy-a" if stable_managed_ids else f"remedy-{suffix}"
    pathogen_id = "pathogen-a" if stable_managed_ids else f"pathogen-{suffix}"
    relation_id = "relation-a" if stable_managed_ids else f"relation-{suffix}"
    multiplex_id = "multiplex-a" if stable_managed_ids else f"multiplex-{suffix}"
    return (
        entry_payload(
            "group",
            group_id,
            {
                "description": f"Group {suffix} runtime description",
                "enabled": True,
                "label": f"Group {suffix.upper()}",
            },
        ),
        entry_payload(
            "profile",
            profile_id,
            {
                "aliases": [f"profile-{suffix}-alias"],
                "category": "acceptance",
                "enabled": True,
                "group_ids": [group_id],
                "label": f"Profile {suffix.upper()}",
                "level": 2,
            },
        ),
        entry_payload(
            "remedy",
            remedy_id,
            {
                "description": f"Remedy {suffix} indication",
                "enabled": True,
                "label": f"Remedy {suffix.upper()}",
            },
        ),
        entry_payload(
            "pathogen",
            pathogen_id,
            {
                "description": f"Pathogen {suffix} indication",
                "enabled": True,
                "label": f"Pathogen {suffix.upper()}",
            },
        ),
        entry_payload(
            "relation",
            relation_id,
            {
                "enabled": True,
                "pathogen_id": pathogen_id,
                "priority": 7,
                "relation_type": "remedy_pathogen",
                "remedy_id": remedy_id,
            },
        ),
        entry_payload(
            "multiplex",
            multiplex_id,
            {
                "description": f"Multiplex {suffix} runtime description",
                "enabled": True,
                "group_ids": [group_id],
                "label": f"Multiplex {suffix.upper()}",
                "remedy_ids": [remedy_id],
            },
        ),
    )


def activate_revision_via_api(
    app: Any,
    headers: dict[str, str],
    draft_id: str,
    revision_id: str,
    entries: Sequence[dict[str, object]],
    expected_previous_revision_id: str | None,
    expected_activation_version: int,
    expected_new_activation_version: int,
) -> None:
    created = request(
        app,
        "POST",
        "/api/admin/catalog/drafts",
        json_body={
            "draft_id": draft_id,
            "expected_version": 0,
            "reason": f"option b create {draft_id}",
            "entries": list(entries),
        },
        headers=headers,
    )
    assert created.status_code == 200, created.text
    assert created.json()["version"] == 1

    validated = request(
        app,
        "POST",
        f"/api/admin/catalog/drafts/{draft_id}/validate",
        json_body={
            "expected_version": 1,
            "reason": f"option b validate {draft_id}",
        },
        headers=headers,
    )
    assert validated.status_code == 200, validated.text
    assert validated.json()["is_valid"] is True

    diff = request(
        app,
        "GET",
        f"/api/admin/catalog/drafts/{draft_id}/diff",
        headers=headers,
    )
    assert diff.status_code == 200, diff.text

    published = request(
        app,
        "POST",
        f"/api/admin/catalog/drafts/{draft_id}/publish",
        json_body={
            "revision_id": revision_id,
            "expected_draft_version": 1,
            "reason": f"option b publish {revision_id}",
        },
        headers=headers,
    )
    assert published.status_code == 200, published.text
    assert published.json()["revision_id"] == revision_id

    activated = request(
        app,
        "POST",
        f"/api/admin/catalog/revisions/{revision_id}/activate",
        json_body={
            "expected_previous_revision_id": expected_previous_revision_id,
            "expected_activation_version": expected_activation_version,
            "reason": f"option b activate {revision_id}",
        },
        headers=headers,
    )
    assert activated.status_code == 200, activated.text
    assert activated.json()["activation_version"] == expected_new_activation_version


def test_admin_catalog_transport_runtime_acceptance_survives_app_reload_and_rollback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MORPHIC_ADMIN_CATALOG_ENABLED", "on")
    context = catalog_context("live")
    db_path = tmp_path / "catalog.sqlite3"

    app = app_for_catalog(tmp_path, db_path, context, suffix="one")
    headers = admin_headers(app)
    activate_revision_via_api(
        app,
        headers,
        "draft-a",
        "revision-a",
        revision_entries("a"),
        None,
        0,
        1,
    )

    reloaded = app_for_catalog(tmp_path, db_path, context, suffix="two")
    reloaded_headers = admin_headers(reloaded)
    runtime = request(
        reloaded,
        "GET",
        "/api/admin/catalog/runtime",
        headers=reloaded_headers,
    )
    assert runtime.status_code == 200
    assert runtime.json()["selected_source"] == "catalog"
    assert runtime.json()["active_revision_id"] == "revision-a"
    assert runtime.json()["group_ids"] == ["group-a"]
    assert runtime.json()["redacted"] is True

    activate_revision_via_api(
        reloaded,
        reloaded_headers,
        "draft-b",
        "revision-b",
        revision_entries("b", stable_managed_ids=True),
        "revision-a",
        1,
        2,
    )

    after_second = app_for_catalog(tmp_path, db_path, context, suffix="three")
    after_second_headers = admin_headers(after_second)
    second_runtime = request(
        after_second,
        "GET",
        "/api/admin/catalog/runtime",
        headers=after_second_headers,
    )
    assert second_runtime.status_code == 200
    assert second_runtime.json()["active_revision_id"] == "revision-b"
    assert second_runtime.json()["group_ids"] == ["group-b"]
    assert second_runtime.json()["profile_ids"] == ["profile-a"]
    assert second_runtime.json()["remedy_ids"] == ["remedy-a"]
    assert second_runtime.json()["pathogen_ids"] == ["pathogen-a"]
    assert second_runtime.json()["relation_ids"] == ["relation-a"]
    assert second_runtime.json()["multiplex_ids"] == ["multiplex-a"]

    rollback = request(
        after_second,
        "POST",
        "/api/admin/catalog/revisions/revision-a/rollback",
        json_body={
            "expected_previous_revision_id": "revision-b",
            "expected_activation_version": 2,
            "reason": "option b rollback to revision a",
        },
        headers=after_second_headers,
    )
    assert rollback.status_code == 200, rollback.text
    assert rollback.json()["activation_version"] == 3

    after_rollback = app_for_catalog(tmp_path, db_path, context, suffix="four")
    after_rollback_headers = admin_headers(after_rollback)
    rollback_runtime = request(
        after_rollback,
        "GET",
        "/api/admin/catalog/runtime",
        headers=after_rollback_headers,
    )
    assert rollback_runtime.status_code == 200
    assert rollback_runtime.json()["active_revision_id"] == "revision-a"
    assert rollback_runtime.json()["group_ids"] == ["group-a"]

    foreign = app_for_catalog(
        tmp_path,
        db_path,
        catalog_context("foreign"),
        suffix="foreign",
    )
    foreign_runtime = request(
        foreign,
        "GET",
        "/api/admin/catalog/runtime",
        headers=admin_headers(foreign),
    )
    assert foreign_runtime.status_code == 409
    assert foreign_runtime.json()["detail"]["code"] == "active_revision_missing"

    monkeypatch.setenv("MORPHIC_ADMIN_CATALOG_ENABLED", "off")
    disabled = request(
        after_rollback,
        "GET",
        "/api/admin/catalog/runtime",
        headers=after_rollback_headers,
    )
    assert disabled.status_code == 200
    assert disabled.json()["selected_source"] == "legacy"
    assert disabled.json()["catalog_enabled"] is False
    assert disabled.json()["active_revision_id"] is None
    assert disabled.json()["group_ids"] == []


def test_admin_catalog_runtime_endpoint_requires_admin_security(
    tmp_path: Path,
) -> None:
    context = catalog_context("security")
    db_path = tmp_path / "catalog.sqlite3"
    app = app_for_catalog(tmp_path, db_path, context, suffix="security")

    response = request(app, "GET", "/api/admin/catalog/runtime")

    assert response.status_code == 503
    assert response.json()["detail"] == "admin security not configured"


def test_admin_catalog_runtime_endpoint_rejects_invalid_switch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MORPHIC_ADMIN_CATALOG_ENABLED", "invalid")
    context = catalog_context("invalid")
    db_path = tmp_path / "catalog.sqlite3"
    app = app_for_catalog(tmp_path, db_path, context, suffix="invalid")

    response = request(
        app,
        "GET",
        "/api/admin/catalog/runtime",
        headers=admin_headers(app),
    )

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "invalid_catalog_enabled_value"


def test_admin_catalog_runtime_response_does_not_expose_admin_secret_fragments(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MORPHIC_ADMIN_CATALOG_ENABLED", "on")
    context = catalog_context("redacted")
    db_path = tmp_path / "catalog.sqlite3"
    app = app_for_catalog(tmp_path, db_path, context, suffix="redacted")
    headers = admin_headers(app)
    activate_revision_via_api(
        app,
        headers,
        "draft-redacted",
        "revision-redacted",
        revision_entries("redacted"),
        None,
        0,
        1,
    )

    response = request(app, "GET", "/api/admin/catalog/runtime", headers=headers)
    encoded = json.dumps(response.json(), sort_keys=True).casefold()

    assert response.status_code == 200
    assert response.json()["redacted"] is True
    for forbidden in FORBIDDEN_EVIDENCE_FRAGMENTS:
        assert forbidden not in encoded
