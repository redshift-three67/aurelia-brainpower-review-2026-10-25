from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import pytest

from core.compliance.group_activation_handle_store import GroupActivationHandleStore
from core.compliance.group_member_identity_source import LocalClientIdentitySource
from core.compliance.local_client_identity_store import LocalClientIdentityStore
from core.compliance.operator_context import OperatorContext
from core.compliance.runtime_manifest import (
    DEFAULT_ERASURE_GATE_TOKEN,
    RuntimeManifestService,
)
from core.profiles.group_member_rate_resolver import GROUP_MEMBER_CONSENT_VERSION
from core.profiles.group_vector import GroupAnalysisOptIn


CONTEXT = OperatorContext(
    operator_id="operator-local",
    workspace_id="ws-local",
    tenant_id="tenant-local",
)
NOW = datetime.now(UTC)


def _register(service: LocalClientIdentityStore, suffix: str = "Alpha") -> str:
    return service.register(
        {
            "first_name": f"Anna{suffix}",
            "last_name": suffix,
            "birth_date": "01011980",
            "birth_place": "Berlin",
        },
        context=CONTEXT,
    )["client_id"]


def _consent(
    service: LocalClientIdentityStore,
    client_id: str,
    *,
    enabled: bool = True,
    valid_until: datetime,
) -> None:
    service.record_group_analysis_consent(
        client_id,
        context=CONTEXT,
        enabled=enabled,
        consent_version=GROUP_MEMBER_CONSENT_VERSION,
        valid_until=valid_until,
    )


def test_expired_group_consent_fails_closed_without_mutating_client(tmp_path: Path) -> None:
    service = LocalClientIdentityStore(tmp_path / "client-identities")
    client_id = _register(service)
    _consent(service, client_id, valid_until=NOW + timedelta(days=1))
    before = service.resolve(client_id, context=CONTEXT)

    source = LocalClientIdentitySource(
        service,
        context=CONTEXT,
        clock=lambda: NOW + timedelta(days=2),
    )
    with pytest.raises(ValueError, match="expired"):
        source.resolve(client_id)

    assert service.resolve(client_id, context=CONTEXT) == before


def test_revocation_immediately_removes_resolver_eligibility(tmp_path: Path) -> None:
    service = LocalClientIdentityStore(tmp_path / "client-identities")
    client_id = _register(service)
    _consent(service, client_id, valid_until=datetime.now(UTC) + timedelta(days=30))
    source = LocalClientIdentitySource(service, context=CONTEXT)

    assert source.resolve(client_id).analysis_consent is True

    _consent(
        service,
        client_id,
        enabled=False,
        valid_until=datetime.now(UTC) + timedelta(days=30),
    )
    with pytest.raises(ValueError, match="consent"):
        source.resolve(client_id)


def test_client_erasure_immediately_removes_resolver_eligibility(tmp_path: Path) -> None:
    runtime = RuntimeManifestService(tmp_path / "runtime")
    identity_store = LocalClientIdentityStore(tmp_path / "runtime" / "client-identities")
    client_id = _register(identity_store)
    _consent(identity_store, client_id, valid_until=datetime.now(UTC) + timedelta(days=30))
    source = LocalClientIdentitySource(identity_store, context=CONTEXT)

    result = runtime.execute_erasure(
        client_id,
        gate_token=DEFAULT_ERASURE_GATE_TOKEN,
        actor="operator-local",
        identity_store=identity_store,
        context=CONTEXT,
    )

    assert result["removed_hardened_identity"] is True
    with pytest.raises(LookupError):
        source.resolve(client_id)


def test_client_erasure_invalidates_already_issued_activation_handles(
    tmp_path: Path,
) -> None:
    runtime = RuntimeManifestService(tmp_path / "runtime")
    identity_store = LocalClientIdentityStore(tmp_path / "runtime" / "client-identities")
    handle_store = GroupActivationHandleStore(
        tmp_path / "runtime" / "group-activation-handles"
    )
    client_id = _register(identity_store)
    issued = handle_store.issue(
        GroupAnalysisOptIn(
            enabled=True,
            centroid_rates=np.asarray([1.0, 2.0, 3.0]),
            strength=0.25,
            consent_verified=True,
            activation_generation=handle_store.authorization_generation(CONTEXT),
        ),
        context=CONTEXT,
        now=NOW,
    )

    runtime.execute_erasure(
        client_id,
        gate_token=DEFAULT_ERASURE_GATE_TOKEN,
        identity_store=identity_store,
        context=CONTEXT,
    )

    with pytest.raises(LookupError):
        handle_store.consume(
            str(issued["activation_handle"]), context=CONTEXT, now=NOW
        )


def test_client_erasure_keeps_identity_when_invalidation_fails(
    tmp_path: Path,
) -> None:
    runtime = RuntimeManifestService(tmp_path / "runtime")
    identity_store = LocalClientIdentityStore(tmp_path / "runtime" / "client-identities")
    client_id = _register(identity_store)

    class FailingHandleStore:
        def invalidate_context(self, context: OperatorContext) -> None:
            raise OSError("synthetic invalidation failure")

    with pytest.raises(OSError, match="invalidation"):
        runtime.execute_erasure(
            client_id,
            gate_token=DEFAULT_ERASURE_GATE_TOKEN,
            identity_store=identity_store,
            activation_handle_store=FailingHandleStore(),
            context=CONTEXT,
        )

    assert identity_store.resolve(client_id, context=CONTEXT)["client_id"] == client_id


def test_enabled_consent_requires_aware_future_expiry(tmp_path: Path) -> None:
    service = LocalClientIdentityStore(tmp_path / "client-identities")
    client_id = _register(service)

    with pytest.raises(ValueError, match="timezone-aware"):
        _consent(
            service,
            client_id,
            valid_until=datetime.now() + timedelta(days=1),
        )

    with pytest.raises(ValueError, match="future"):
        _consent(
            service,
            client_id,
            valid_until=datetime.now(UTC) - timedelta(seconds=1),
        )


def test_erasure_and_consent_audit_never_expose_group_membership(tmp_path: Path) -> None:
    runtime = RuntimeManifestService(tmp_path / "runtime")
    identity_store = LocalClientIdentityStore(tmp_path / "runtime" / "client-identities")
    alpha_id = _register(identity_store, "Alpha")
    beta_id = _register(identity_store, "Beta")
    _consent(identity_store, alpha_id, valid_until=datetime.now(UTC) + timedelta(days=30))
    _consent(identity_store, beta_id, valid_until=datetime.now(UTC) + timedelta(days=30))

    manifest = runtime.erasure_manifest(
        alpha_id,
        identity_store=identity_store,
        context=CONTEXT,
    )
    audit = runtime.audit_for_client(alpha_id)
    text = str({"manifest": manifest, "audit": audit})

    assert beta_id not in text
    assert "AnnaBeta" not in text
    assert "member_ids" not in text
    assert "group_label" not in text
    assert "rates" not in text
