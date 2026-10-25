from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pytest

from apps.web.group_drafts import build_group_draft_store
from apps.web.main import create_app
from core.compliance.local_vector_draft_store import LocalVectorDraftStore
from core.compliance.operator_context import OperatorContext
from core.profiles.group_vector import GroupAnalysisOptIn
from tests.test_web_shell import request


def _payload(**overrides: object) -> dict[str, object]:
    draft: dict[str, object] = {
        "group_label": "Morgenkreis",
        "members": [
            {"client_id": "cli-alpha", "consent_recorded": True},
            {"client_id": "cli-beta", "consent_recorded": True},
        ],
        "persistence_consent": True,
        "analysis_consent": False,
        "retention_days": 30,
    }
    draft.update(overrides)
    return {"draft_id": "group-draft-001", "draft": draft}


def _app(tmp_path: Path):
    app = create_app(runtime_dir=tmp_path)
    app.state.group_draft_store = LocalVectorDraftStore(tmp_path / "group-drafts")
    return app


def test_group_draft_store_namespace_is_workspace_and_tenant_bound(tmp_path: Path) -> None:
    first = OperatorContext(operator_id="op-local", workspace_id="ws-alpha", tenant_id="tenant-a")
    other_tenant = OperatorContext(operator_id="op-local", workspace_id="ws-alpha", tenant_id="tenant-b")
    other_workspace = OperatorContext(operator_id="op-local", workspace_id="ws-beta", tenant_id="tenant-a")
    other_operator = OperatorContext(operator_id="op-other", workspace_id="ws-alpha", tenant_id="tenant-a")

    first_store = build_group_draft_store(tmp_path, first)

    assert first_store.root == build_group_draft_store(tmp_path, first).root
    assert first_store.root != build_group_draft_store(tmp_path, other_tenant).root
    assert first_store.root != build_group_draft_store(tmp_path, other_workspace).root
    assert first_store.root != build_group_draft_store(tmp_path, other_operator).root
    assert "tenant-a" not in str(first_store.root)
    assert "ws-alpha" not in str(first_store.root)


def test_group_draft_api_stores_only_dpapi_protected_data_and_returns_safe_summaries(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path)

    empty = request(app, "GET", "/api/workbench/group-draft")
    saved = request(app, "PUT", "/api/workbench/group-draft", json_body=_payload())
    listed = request(app, "GET", "/api/workbench/group-draft")
    loaded = request(app, "GET", "/api/workbench/group-draft/group-draft-001")

    assert empty.status_code == 200
    assert empty.json() == {"drafts": []}
    assert saved.status_code == 200
    assert saved.json()["draft_id"] == "group-draft-001"
    assert saved.json()["vectors"][0]["analysis_enabled"] is False
    assert "Morgenkreis" not in str(saved.json())
    assert "cli-alpha" not in str(saved.json())
    assert listed.json() == {"drafts": [saved.json()]}
    assert loaded.status_code == 200
    assert loaded.json()["draft"]["group_label"] == "Morgenkreis"
    assert loaded.json()["draft"]["members"][0]["client_id"] == "cli-alpha"
    encrypted = (tmp_path / "group-drafts" / "group-draft-001.dpapi").read_bytes()
    assert b"Morgenkreis" not in encrypted
    assert b"cli-alpha" not in encrypted


def test_group_draft_api_fails_closed_for_invalid_drafts_and_wrong_erasure_confirmation(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path)

    invalid = request(
        app,
        "PUT",
        "/api/workbench/group-draft",
        json_body=_payload(persistence_consent=False),
    )
    unknown = request(
        app,
        "PUT",
        "/api/workbench/group-draft",
        json_body=_payload(unexpected="rejected"),
    )
    saved = request(app, "PUT", "/api/workbench/group-draft", json_body=_payload())
    wrong_delete = request(
        app,
        "DELETE",
        "/api/workbench/group-draft/group-draft-001",
        json_body={"confirmation_id": "group-draft-other"},
    )
    loaded = request(app, "GET", "/api/workbench/group-draft/group-draft-001")
    deleted = request(
        app,
        "DELETE",
        "/api/workbench/group-draft/group-draft-001",
        json_body={"confirmation_id": "group-draft-001"},
    )

    assert invalid.status_code == 422
    assert unknown.status_code == 422
    assert saved.status_code == 200
    assert wrong_delete.status_code == 422
    assert loaded.status_code == 200
    assert deleted.json() == {"deleted": True, "draft_id": "group-draft-001"}


def test_group_draft_erasure_invalidates_already_issued_activation_handles(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path)
    context = app.state.operator_context
    saved = request(app, "PUT", "/api/workbench/group-draft", json_body=_payload())
    issued = app.state.group_activation_handles.issue(
        GroupAnalysisOptIn(
            enabled=True,
            centroid_rates=np.asarray([1.0, 2.0, 3.0]),
            strength=0.25,
            consent_verified=True,
            activation_generation=app.state.group_activation_handles.authorization_generation(context),
        ),
        context=context,
        now=datetime.now(UTC),
    )

    deleted = request(
        app,
        "DELETE",
        "/api/workbench/group-draft/group-draft-001",
        json_body={"confirmation_id": "group-draft-001"},
    )

    assert saved.status_code == 200
    assert deleted.status_code == 200
    with pytest.raises(LookupError):
        app.state.group_activation_handles.consume(
            str(issued["activation_handle"]),
            context=context,
            now=datetime.now(UTC),
        )


def test_group_draft_erasure_does_not_delete_when_invalidation_fails(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path)
    request(app, "PUT", "/api/workbench/group-draft", json_body=_payload())

    def fail_invalidation(context: OperatorContext) -> None:
        raise OSError("synthetic invalidation failure")

    app.state.invalidate_group_analysis_context = fail_invalidation
    with pytest.raises(OSError, match="invalidation"):
        request(
            app,
            "DELETE",
            "/api/workbench/group-draft/group-draft-001",
            json_body={"confirmation_id": "group-draft-001"},
        )

    assert request(
        app, "GET", "/api/workbench/group-draft/group-draft-001"
    ).status_code == 200
