from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import pytest

from apps.web.client_context_contracts import GroupContextDraft, LocalVectorDraftEnvelope
from apps.web.contracts import Phase1ScanRequest
from apps.web.group_analysis_policy import GroupAnalysisPolicyService
from apps.web.main import create_app
from apps.web.workbench import current_scan_profile_pool_fingerprint
from core.compliance.group_activation_handle_store import GroupActivationHandleStore
from core.compliance.group_activation_runtime import consume_group_activation_from_environment
from core.compliance.local_client_identity_store import LocalClientIdentityStore
from core.compliance.operator_context import OperatorContext
from core.compliance.runtime_manifest import stable_client_id
from core.profile_sync import SCAN_PROFILE_POOL_FINGERPRINT_ENV
from core.profiles.group_member_rate_resolver import GROUP_MEMBER_CONSENT_VERSION
from tests.test_web_shell import request as web_request


CONTEXT = OperatorContext("operator-web", "ws-web", "tenant-web")
NOW = datetime(2026, 7, 13, 11, 0, tzinfo=UTC)


def _request(**overrides: object) -> Phase1ScanRequest:
    payload: dict[str, object] = {
        "last_name": "Alpha",
        "first_name": "Anna",
        "birth_date": "01011980",
        "birth_place": "Berlin",
        "focus": "synthetic",
        "consent_local": True,
        "consent_safety": True,
    }
    payload.update(overrides)
    payload.setdefault(
        "scan_profile_pool_fingerprint",
        current_scan_profile_pool_fingerprint(payload.get("profile_level", 3)),
    )
    return Phase1ScanRequest.model_validate(payload)


def test_web_activation_is_default_inactive_without_touching_sensitive_stores(
    tmp_path: Path, monkeypatch
) -> None:
    from apps.web.group_analysis_runtime import prepare_group_scan_activation

    monkeypatch.delenv("MORPHIC_GROUP_ANALYSIS_ENABLED", raising=False)

    class ForbiddenStore:
        def __getattr__(self, name: str):
            raise AssertionError(f"default path must not access {name}")

    policy = GroupAnalysisPolicyService(strength=0.5)
    assert prepare_group_scan_activation(
        _request(group_draft_id="draft-safe"),
        policy=policy,
        draft_store=ForbiddenStore(),
        identity_store=ForbiddenStore(),
        handle_store=GroupActivationHandleStore(tmp_path / "handles"),
        context=CONTEXT,
        now=NOW,
    ) is None
    assert list((tmp_path / "handles").glob("gah-*.dpapi")) == []


def test_web_activation_requires_explicit_nonzero_strength_without_store_access(
    tmp_path: Path, monkeypatch
) -> None:
    from apps.web.group_analysis_runtime import prepare_group_scan_activation

    monkeypatch.setenv("MORPHIC_GROUP_ANALYSIS_ENABLED", "1")

    class ForbiddenStore:
        def __getattr__(self, name: str):
            raise AssertionError(f"zero-strength path must not access {name}")

    assert prepare_group_scan_activation(
        _request(group_draft_id="draft-safe"),
        policy=GroupAnalysisPolicyService(strength=0.0),
        draft_store=ForbiddenStore(),
        identity_store=ForbiddenStore(),
        handle_store=GroupActivationHandleStore(tmp_path / "handles"),
        context=CONTEXT,
        now=NOW,
    ) is None


def test_web_activation_builds_authorized_root_handle_server_side(
    tmp_path: Path, monkeypatch
) -> None:
    from apps.web.group_analysis_runtime import prepare_group_scan_activation

    monkeypatch.setenv("MORPHIC_GROUP_ANALYSIS_ENABLED", "1")
    identity_store = LocalClientIdentityStore(tmp_path / "identities")
    members = [
        {
            "first_name": "Anna",
            "last_name": "Alpha",
            "birth_date": "01011980",
            "birth_place": "Berlin",
        },
        {
            "first_name": "Berta",
            "last_name": "Beta",
            "birth_date": "02021982",
            "birth_place": "Bern",
        },
    ]
    member_ids: list[str] = []
    for identity in members:
        client_id = str(identity_store.register(identity, context=CONTEXT)["client_id"])
        identity_store.record_group_analysis_consent(
            client_id,
            context=CONTEXT,
            enabled=True,
            consent_version=GROUP_MEMBER_CONSENT_VERSION,
            valid_until=NOW + timedelta(days=30),
        )
        member_ids.append(client_id)

    draft = GroupContextDraft(
        group_label="Synthetic",
        members=[
            {"client_id": client_id, "consent_recorded": True}
            for client_id in member_ids
        ],
        persistence_consent=True,
        analysis_consent=True,
        retention_days=30,
    )

    class DraftStore:
        def load(self, draft_id: str) -> LocalVectorDraftEnvelope:
            assert draft_id == "draft-safe"
            return LocalVectorDraftEnvelope(group=draft)

    handle_store = GroupActivationHandleStore(tmp_path / "handles")
    environment = prepare_group_scan_activation(
        _request(group_draft_id="draft-safe"),
        policy=GroupAnalysisPolicyService(strength=0.25),
        draft_store=DraftStore(),
        identity_store=identity_store,
        handle_store=handle_store,
        context=CONTEXT,
        now=NOW,
    )

    assert environment is not None
    assert set(environment) == {
        "MORPHIC_GROUP_ACTIVATION_RUNTIME",
        "MORPHIC_GROUP_ACTIVATION_ROOT",
        "MORPHIC_GROUP_ACTIVATION_HANDLE",
    }
    text = str(environment)
    assert member_ids[0] not in text
    assert member_ids[1] not in text
    assert "Synthetic" not in text
    opt_in = consume_group_activation_from_environment(
        environment, context=CONTEXT, now=NOW
    )
    assert opt_in is not None
    assert opt_in.enabled is True
    assert opt_in.strength == 0.25
    assert opt_in.centroid_rates is not None
    assert np.isfinite(opt_in.centroid_rates).all()
    assert stable_client_id(members[0]) == member_ids[0]


def test_web_activation_fails_closed_when_context_is_invalidated_during_resolution(
    tmp_path: Path, monkeypatch
) -> None:
    from apps.web.group_analysis_runtime import prepare_group_scan_activation

    monkeypatch.setenv("MORPHIC_GROUP_ANALYSIS_ENABLED", "1")
    identity_store = LocalClientIdentityStore(tmp_path / "identities")
    identities = [
        {
            "first_name": "Anna",
            "last_name": "Alpha",
            "birth_date": "01011980",
            "birth_place": "Berlin",
        },
        {
            "first_name": "Berta",
            "last_name": "Beta",
            "birth_date": "02021982",
            "birth_place": "Bern",
        },
    ]
    member_ids: list[str] = []
    for identity in identities:
        client_id = str(identity_store.register(identity, context=CONTEXT)["client_id"])
        identity_store.record_group_analysis_consent(
            client_id,
            context=CONTEXT,
            enabled=True,
            consent_version=GROUP_MEMBER_CONSENT_VERSION,
            valid_until=NOW + timedelta(days=30),
        )
        member_ids.append(client_id)
    draft = GroupContextDraft(
        group_label="Synthetic",
        members=[
            {"client_id": client_id, "consent_recorded": True}
            for client_id in member_ids
        ],
        persistence_consent=True,
        analysis_consent=True,
        retention_days=30,
    )
    handle_store = GroupActivationHandleStore(tmp_path / "handles")

    class InvalidatingDraftStore:
        def load(self, draft_id: str) -> LocalVectorDraftEnvelope:
            assert draft_id == "draft-safe"
            handle_store.invalidate_context(CONTEXT, now=NOW)
            return LocalVectorDraftEnvelope(group=draft)

    with pytest.raises(LookupError, match="invalidated"):
        prepare_group_scan_activation(
            _request(group_draft_id="draft-safe"),
            policy=GroupAnalysisPolicyService(strength=0.25),
            draft_store=InvalidatingDraftStore(),
            identity_store=identity_store,
            handle_store=handle_store,
            context=CONTEXT,
            now=NOW,
        )
    assert list((tmp_path / "handles").glob("gah-*.dpapi")) == []


def test_scan_request_rejects_raw_group_activation_data() -> None:
    assert "group_draft_id" in Phase1ScanRequest.model_fields
    for forbidden in ("group_member_rates", "group_opt_in", "group_centroid", "group_subject_id"):
        assert forbidden not in Phase1ScanRequest.model_fields


def test_web_scan_start_passes_activation_only_in_private_job_environment(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("MORPHIC_GROUP_ANALYSIS_ENABLED", "1")

    class CapturingJobs:
        def __init__(self) -> None:
            self.environment: dict[str, str] | None = None

        def start(self, command, owner_id=None, env_overrides=None, job_id=None):
            self.environment = env_overrides
            return {
                "executes": True,
                "job_id": job_id,
                "status": "running",
                "command": command,
                "completed_substeps": [],
            }

        def get(self, job_id: str):
            raise AssertionError("not used")

    jobs = CapturingJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)
    context = app.state.operator_context
    identities = [
        {"first_name": "Anna", "last_name": "Alpha", "birth_date": "01011980", "birth_place": "Berlin"},
        {"first_name": "Berta", "last_name": "Beta", "birth_date": "02021982", "birth_place": "Bern"},
    ]
    member_ids = []
    for identity in identities:
        client_id = str(app.state.client_identity_store.register(identity, context=context)["client_id"])
        app.state.client_identity_store.record_group_analysis_consent(
            client_id,
            context=context,
            enabled=True,
            consent_version=GROUP_MEMBER_CONSENT_VERSION,
            valid_until=datetime.now(UTC) + timedelta(days=30),
        )
        member_ids.append(client_id)
    draft = GroupContextDraft(
        group_label="Private Group",
        members=[{"client_id": value, "consent_recorded": True} for value in member_ids],
        persistence_consent=True,
        analysis_consent=True,
        retention_days=30,
    )
    app.state.group_draft_store.save(
        "draft-productive",
        LocalVectorDraftEnvelope(group=draft),
    )
    app.state.group_analysis_policy.set_strength(0.25)

    response = web_request(
        app,
        "POST",
        "/api/scan/jobs",
        json_body=_request(group_draft_id="draft-productive").model_dump(),
    )

    assert response.status_code == 200
    assert jobs.environment is not None
    assert set(jobs.environment) == {
        "MORPHIC_GROUP_ACTIVATION_RUNTIME",
        "MORPHIC_GROUP_ACTIVATION_ROOT",
        "MORPHIC_GROUP_ACTIVATION_HANDLE",
        "MORPHIC_RUNTIME_DIR",
        "MORPHIC_EMF_AUTHORITY_PATH",
        SCAN_PROFILE_POOL_FINGERPRINT_ENV,
    }
    confirmed_fingerprint = current_scan_profile_pool_fingerprint(3)
    assert jobs.environment[SCAN_PROFILE_POOL_FINGERPRINT_ENV] == confirmed_fingerprint
    assert "gah-" not in response.text
    assert confirmed_fingerprint not in response.text
    assert "draft-productive" not in response.text
    assert "Private Group" not in response.text
    trace = app.state.workbench_store.get_run_trace(response.json()["job_id"])
    assert "gah-" not in str(trace)
    assert "draft-productive" not in str(trace)
    assert "Private Group" not in str(trace)
    assert confirmed_fingerprint not in str(trace)
