from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import pytest

from apps.web.main import create_app
from core.compliance.local_client_identity_store import LocalClientIdentityStore
from core.compliance.operator_context import OperatorContext
from core.profiles.group_member_rate_resolver import GROUP_MEMBER_CONSENT_VERSION
from core.profiles.group_vector import GroupAnalysisOptIn
from tests.test_web_shell import request


CONTEXT = OperatorContext("operator-local", "ws-local", "tenant-local")


def _app(tmp_path: Path):
    app = create_app(runtime_dir=tmp_path / "runtime")
    app.state.client_identity_store = LocalClientIdentityStore(
        tmp_path / "runtime" / "client-identities"
    )
    app.state.operator_context = CONTEXT
    return app


def _registration(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "first_name": "Anna",
        "last_name": "Alpha",
        "birth_date": "01011980",
        "birth_place": "Berlin",
        "persistence_consent": True,
        "retention_days": 365,
    }
    payload.update(overrides)
    return payload


def test_group_consent_registration_is_explicit_dpapi_protected_and_redacted(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path)

    empty = request(app, "GET", "/api/workbench/group-consent")
    registered = request(
        app,
        "POST",
        "/api/workbench/group-consent/identity",
        json_body=_registration(),
    )
    listed = request(app, "GET", "/api/workbench/group-consent")

    assert empty.status_code == 200
    assert empty.json() == {"identities": []}
    assert registered.status_code == 200
    body = registered.json()
    assert body["client_id"].startswith("cli-")
    assert body["consent_enabled"] is False
    assert body["consent_version"] == ""
    assert "Anna" not in str(body)
    assert "Berlin" not in str(body)
    assert listed.json() == {"identities": [body]}
    protected = (
        app.state.client_identity_store.root / f"{body['client_id']}.dpapi"
    ).read_bytes()
    assert b"Anna" not in protected
    assert b"Berlin" not in protected


def test_group_consent_registration_requires_explicit_persistence_consent(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path)

    rejected = request(
        app,
        "POST",
        "/api/workbench/group-consent/identity",
        json_body=_registration(persistence_consent=False),
    )

    assert rejected.status_code == 422
    assert app.state.client_identity_store.list_safe(context=CONTEXT) == []


def test_group_consent_enrollment_and_revocation_are_explicit_and_versioned(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path)
    registered = request(
        app,
        "POST",
        "/api/workbench/group-consent/identity",
        json_body=_registration(),
    ).json()
    client_id = registered["client_id"]
    valid_until = datetime.now(UTC) + timedelta(days=30)

    enrolled = request(
        app,
        "PUT",
        f"/api/workbench/group-consent/{client_id}",
        json_body={
            "confirmation_id": client_id,
            "enabled": True,
            "valid_until": valid_until.isoformat(),
        },
    )
    revoked = request(
        app,
        "PUT",
        f"/api/workbench/group-consent/{client_id}",
        json_body={
            "confirmation_id": client_id,
            "enabled": False,
            "valid_until": None,
        },
    )

    assert enrolled.status_code == 200
    assert enrolled.json()["consent_enabled"] is True
    assert enrolled.json()["consent_version"] == GROUP_MEMBER_CONSENT_VERSION
    assert revoked.status_code == 200
    assert revoked.json()["consent_enabled"] is False
    assert revoked.json()["consent_version"] == GROUP_MEMBER_CONSENT_VERSION


def test_group_consent_revocation_invalidates_already_issued_activation_handles(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path)
    registered = request(
        app,
        "POST",
        "/api/workbench/group-consent/identity",
        json_body=_registration(),
    ).json()
    client_id = registered["client_id"]
    issued = app.state.group_activation_handles.issue(
        GroupAnalysisOptIn(
            enabled=True,
            centroid_rates=np.asarray([1.0, 2.0, 3.0]),
            strength=0.25,
            consent_verified=True,
            activation_generation=app.state.group_activation_handles.authorization_generation(CONTEXT),
        ),
        context=CONTEXT,
        now=datetime.now(UTC),
    )

    revoked = request(
        app,
        "PUT",
        f"/api/workbench/group-consent/{client_id}",
        json_body={
            "confirmation_id": client_id,
            "enabled": False,
            "valid_until": None,
        },
    )

    assert revoked.status_code == 200
    with pytest.raises(LookupError):
        app.state.group_activation_handles.consume(
            str(issued["activation_handle"]),
            context=CONTEXT,
            now=datetime.now(UTC),
        )


def test_group_consent_revocation_keeps_consent_when_invalidation_fails(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path)
    registered = request(
        app,
        "POST",
        "/api/workbench/group-consent/identity",
        json_body=_registration(),
    ).json()
    client_id = registered["client_id"]
    request(
        app,
        "PUT",
        f"/api/workbench/group-consent/{client_id}",
        json_body={
            "confirmation_id": client_id,
            "enabled": True,
            "valid_until": (datetime.now(UTC) + timedelta(days=30)).isoformat(),
        },
    )

    def fail_invalidation(context: OperatorContext) -> None:
        raise OSError("synthetic invalidation failure")

    app.state.invalidate_group_analysis_context = fail_invalidation
    with pytest.raises(OSError, match="invalidation"):
        request(
            app,
            "PUT",
            f"/api/workbench/group-consent/{client_id}",
            json_body={
                "confirmation_id": client_id,
                "enabled": False,
                "valid_until": None,
            },
        )

    record = app.state.client_identity_store.resolve(client_id, context=CONTEXT)
    assert record["group_analysis"]["enabled"] is True


def test_group_consent_enrollment_fails_closed_for_wrong_confirmation_and_tenant(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path)
    registered = request(
        app,
        "POST",
        "/api/workbench/group-consent/identity",
        json_body=_registration(),
    ).json()
    client_id = registered["client_id"]
    expiry = (datetime.now(UTC) + timedelta(days=30)).isoformat()

    wrong_confirmation = request(
        app,
        "PUT",
        f"/api/workbench/group-consent/{client_id}",
        json_body={
            "confirmation_id": "cli-00000000000000000000",
            "enabled": True,
            "valid_until": expiry,
        },
    )
    app.state.operator_context = OperatorContext(
        "operator-local", "ws-local", "tenant-foreign"
    )
    foreign_tenant = request(
        app,
        "PUT",
        f"/api/workbench/group-consent/{client_id}",
        json_body={
            "confirmation_id": client_id,
            "enabled": True,
            "valid_until": expiry,
        },
    )

    assert wrong_confirmation.status_code == 422
    assert foreign_tenant.status_code == 403


def test_group_consent_router_has_no_scan_activation_imports() -> None:
    source = (Path(__file__).resolve().parents[1] / "apps" / "web" / "group_consents.py")
    text = source.read_text(encoding="utf-8")

    assert "group_analysis_activation" not in text
    assert "AnalysisService" not in text
    assert "Phase1ScanRequest" not in text
    assert "build_resolved_group_draft_opt_in" not in text
