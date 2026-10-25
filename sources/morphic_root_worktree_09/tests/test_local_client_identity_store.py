from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import pytest

import core.compliance.local_client_identity_store as identity_store_module
from core.compliance.group_activation_handle_store import GroupActivationHandleStore
from core.compliance.group_member_identity_source import LocalClientIdentitySource
from core.compliance.local_client_identity_store import LocalClientIdentityStore
from core.compliance.operator_context import OperatorContext, OwnershipError
from core.compliance.runtime_manifest import RuntimeManifestService, stable_client_id
from core.profiles.group_member_rate_resolver import GROUP_MEMBER_CONSENT_VERSION
from core.profiles.group_vector import GroupAnalysisOptIn


CONTEXT = OperatorContext(
    operator_id="operator-local",
    workspace_id="ws-local",
    tenant_id="tenant-local",
)


def test_identity_store_writer_uses_shared_durable_parent_helper(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[Path] = []

    def parent(path: Path, *, mode: int = 0o777) -> None:
        calls.append(Path(path))
        Path(path).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(
        identity_store_module,
        "durable_mkdir_parents",
        parent,
        raising=False,
    )
    store = LocalClientIdentityStore(tmp_path / "nested" / "identities")

    store.register(_client(), context=CONTEXT)

    assert calls == [store.root]


def _client() -> dict[str, str]:
    return {
        "first_name": "Anna",
        "last_name": "Alpha",
        "birth_date": "01011980",
        "birth_place": "Berlin",
    }


def test_identity_store_roundtrips_dpapi_payload_without_cleartext_at_rest(
    tmp_path: Path,
) -> None:
    store = LocalClientIdentityStore(tmp_path / "client-identities")

    registered = store.register(_client(), context=CONTEXT)
    protected = (store.root / f"{registered['client_id']}.dpapi").read_bytes()
    identity = store.resolve(registered["client_id"], context=CONTEXT)

    assert registered == {
        "client_id": stable_client_id(_client()),
        "owner_bound": True,
        "consent_enabled": False,
        "consent_version": "",
        "valid_until": "",
    }
    assert b"Anna" not in protected
    assert b"Alpha" not in protected
    assert b"01011980" not in protected
    assert b"Berlin" not in protected
    assert identity["first_name"] == "Anna"
    assert identity["last_name"] == "Alpha"
    assert identity["tenant_id"] == CONTEXT.tenant_id


def test_identity_store_fails_closed_for_foreign_workspace_and_tenant(tmp_path: Path) -> None:
    store = LocalClientIdentityStore(tmp_path / "client-identities")
    client_id = store.register(_client(), context=CONTEXT)["client_id"]

    with pytest.raises(OwnershipError, match="workspace"):
        store.resolve(
            client_id,
            context=OperatorContext("operator-local", "ws-foreign", "tenant-local"),
        )
    with pytest.raises(OwnershipError, match="tenant"):
        store.resolve(
            client_id,
            context=OperatorContext("operator-local", "ws-local", "tenant-foreign"),
        )


def test_identity_store_does_not_import_legacy_runtime_clients(tmp_path: Path) -> None:
    runtime = RuntimeManifestService(tmp_path / "runtime")
    legacy = runtime.get_or_create_client(_client())
    store = LocalClientIdentityStore(tmp_path / "runtime" / "client-identities")

    assert store.list_safe(context=CONTEXT) == []
    with pytest.raises(LookupError, match="identity"):
        store.resolve(legacy["client_id"], context=CONTEXT)
    assert runtime.get_client(legacy["client_id"])["first_name"] == "Anna"


def test_identity_store_safe_list_and_consent_are_redacted(tmp_path: Path) -> None:
    store = LocalClientIdentityStore(tmp_path / "client-identities")
    client_id = store.register(_client(), context=CONTEXT)["client_id"]
    valid_until = datetime.now(UTC) + timedelta(days=30)

    store.record_group_analysis_consent(
        client_id,
        context=CONTEXT,
        enabled=True,
        consent_version=GROUP_MEMBER_CONSENT_VERSION,
        valid_until=valid_until,
    )
    safe = store.list_safe(context=CONTEXT)

    assert safe == [
        {
            "client_id": client_id,
            "owner_bound": True,
            "consent_enabled": True,
            "consent_version": GROUP_MEMBER_CONSENT_VERSION,
            "valid_until": valid_until.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }
    ]
    safe_text = str(safe)
    assert "Anna" not in safe_text
    assert "Alpha" not in safe_text
    assert "Berlin" not in safe_text
    assert "ws-local" not in safe_text
    assert "tenant-local" not in safe_text
    assert str(store.root) not in safe_text


def test_group_member_identity_source_reads_only_hardened_store(tmp_path: Path) -> None:
    store = LocalClientIdentityStore(tmp_path / "client-identities")
    client_id = store.register(_client(), context=CONTEXT)["client_id"]
    store.record_group_analysis_consent(
        client_id,
        context=CONTEXT,
        enabled=True,
        consent_version=GROUP_MEMBER_CONSENT_VERSION,
        valid_until=datetime.now(UTC) + timedelta(days=30),
    )

    identity = LocalClientIdentitySource(store, context=CONTEXT).resolve(client_id)

    assert identity.client_id == client_id
    assert identity.first_name == "Anna"
    assert identity.analysis_consent is True


def test_identity_store_erasure_is_exact_idempotent_and_tenant_bound(tmp_path: Path) -> None:
    store = LocalClientIdentityStore(tmp_path / "client-identities")
    client_id = store.register(_client(), context=CONTEXT)["client_id"]

    dry_run = store.erasure_dry_run(client_id, context=CONTEXT)

    assert dry_run == {
        "client_id": client_id,
        "identity_entry_present": True,
        "dry_run": True,
    }
    with pytest.raises(ValueError, match="confirmation"):
        store.erase(client_id, context=CONTEXT, confirmation_id="cli-other")
    with pytest.raises(OwnershipError, match="tenant"):
        store.erase(
            client_id,
            context=OperatorContext("operator-local", "ws-local", "tenant-foreign"),
            confirmation_id=client_id,
        )
    assert store.erase(client_id, context=CONTEXT, confirmation_id=client_id) is True
    assert store.erase(client_id, context=CONTEXT, confirmation_id=client_id) is False


def test_identity_store_retention_is_redacted_and_non_destructive_in_dry_run(
    tmp_path: Path,
) -> None:
    store = LocalClientIdentityStore(tmp_path / "client-identities")
    client_id = store.register(
        _client(),
        context=CONTEXT,
        registered_at=datetime(2025, 1, 1, tzinfo=UTC),
    )["client_id"]

    candidates = store.retention_dry_run(
        retention_days=365,
        now=datetime(2026, 2, 1, tzinfo=UTC),
        context=CONTEXT,
    )

    assert candidates == [{"client_id": client_id, "reason": "retention_expired"}]
    assert store.resolve(client_id, context=CONTEXT)["first_name"] == "Anna"


def test_identity_store_uses_per_record_retention_and_purges_orphans(
    tmp_path: Path,
) -> None:
    store = LocalClientIdentityStore(tmp_path / "client-identities")
    client_id = store.register(
        _client(),
        context=CONTEXT,
        retention_days=30,
        registered_at=datetime(2026, 1, 1, tzinfo=UTC),
    )["client_id"]

    before_expiry = store.find_expired(
        context=CONTEXT,
        now=datetime(2026, 1, 30, 23, 59, 59, tzinfo=UTC),
    )
    at_expiry = store.find_expired(
        context=CONTEXT,
        now=datetime(2026, 1, 31, tzinfo=UTC),
    )

    assert before_expiry == []
    assert at_expiry == [client_id]
    assert store.purge_expired(
        context=CONTEXT,
        now=datetime(2026, 1, 31, tzinfo=UTC),
        dry_run=True,
    ) == [client_id]
    assert store.resolve(client_id, context=CONTEXT)["first_name"] == "Anna"
    assert store.purge_expired(
        context=CONTEXT,
        now=datetime(2026, 1, 31, tzinfo=UTC),
    ) == [client_id]
    with pytest.raises(LookupError):
        store.resolve(client_id, context=CONTEXT)


def test_identity_store_rejects_noncanonical_ids_and_corrupted_blobs(tmp_path: Path) -> None:
    store = LocalClientIdentityStore(tmp_path / "client-identities")
    client_id = store.register(_client(), context=CONTEXT)["client_id"]

    for invalid in ("../clients", "cli-alpha", "C:/absolute", f"{client_id}.dpapi"):
        with pytest.raises(ValueError, match="canonical"):
            store.resolve(invalid, context=CONTEXT)

    (store.root / f"{client_id}.dpapi").write_bytes(b"corrupted-dpapi-record")
    with pytest.raises(ValueError, match="payload"):
        store.resolve(client_id, context=CONTEXT)


def test_identity_store_failed_protection_preserves_existing_record(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = LocalClientIdentityStore(tmp_path / "client-identities")
    client_id = store.register(_client(), context=CONTEXT)["client_id"]
    target = store.root / f"{client_id}.dpapi"
    before = target.read_bytes()

    def fail_protection(payload: bytes, *, description: str = "") -> bytes:
        raise OSError("synthetic protection failure")

    monkeypatch.setattr(identity_store_module, "protect_for_current_user", fail_protection)
    with pytest.raises(OSError, match="synthetic"):
        store.record_group_analysis_consent(
            client_id,
            context=CONTEXT,
            enabled=True,
            consent_version=GROUP_MEMBER_CONSENT_VERSION,
            valid_until=datetime.now(UTC) + timedelta(days=30),
        )

    assert target.read_bytes() == before
    assert list(store.root.glob("*.tmp.*")) == []


def test_identity_store_failed_atomic_replace_preserves_record_and_cleans_temp(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = LocalClientIdentityStore(tmp_path / "client-identities")
    client_id = store.register(_client(), context=CONTEXT)["client_id"]
    target = store.root / f"{client_id}.dpapi"
    before = target.read_bytes()
    original_replace = Path.replace

    def fail_identity_replace(path: Path, destination: Path) -> Path:
        if path.name.startswith(f"{client_id}.dpapi.tmp."):
            raise OSError("synthetic replace failure")
        return original_replace(path, destination)

    monkeypatch.setattr(Path, "replace", fail_identity_replace)
    with pytest.raises(OSError, match="replace"):
        store.record_group_analysis_consent(
            client_id,
            context=CONTEXT,
            enabled=True,
            consent_version=GROUP_MEMBER_CONSENT_VERSION,
            valid_until=datetime.now(UTC) + timedelta(days=30),
        )

    assert target.read_bytes() == before
    assert list(store.root.glob("*.tmp.*")) == []


def test_runtime_erasure_explicitly_covers_hardened_identity_store(tmp_path: Path) -> None:
    runtime = RuntimeManifestService(tmp_path / "runtime")
    identity_store = LocalClientIdentityStore(tmp_path / "runtime" / "client-identities")
    client_id = identity_store.register(_client(), context=CONTEXT)["client_id"]

    manifest = runtime.erasure_manifest(
        client_id,
        identity_store=identity_store,
        context=CONTEXT,
    )

    assert manifest["hardened_identity"] == {
        "client_id": client_id,
        "identity_entry_present": True,
        "dry_run": True,
    }
    text = str(manifest["hardened_identity"])
    assert "Anna" not in text
    assert str(identity_store.root) not in text

    result = runtime.execute_erasure(
        client_id,
        gate_token="MORPHIC_ERASURE_ACKNOWLEDGED",
        identity_store=identity_store,
        context=CONTEXT,
    )

    assert result["removed_hardened_identity"] is True
    with pytest.raises(LookupError):
        identity_store.resolve(client_id, context=CONTEXT)


def test_runtime_retention_purge_explicitly_removes_matching_hardened_identity(
    tmp_path: Path,
) -> None:
    runtime = RuntimeManifestService(tmp_path / "runtime")
    identity_store = LocalClientIdentityStore(tmp_path / "runtime" / "client-identities")
    handle_store = GroupActivationHandleStore(
        tmp_path / "runtime" / "group-activation-handles"
    )
    legacy = runtime.get_or_create_client(_client())
    client_id = identity_store.register(_client(), context=CONTEXT)["client_id"]
    assert legacy["client_id"] == client_id
    runtime_clients = runtime.load_store("clients")
    stale = datetime(2025, 1, 1, tzinfo=UTC).isoformat().replace("+00:00", "Z")
    runtime_clients["clients"][0]["created_at"] = stale
    runtime_clients["clients"][0]["updated_at"] = stale
    runtime.save_store("clients", runtime_clients)
    now = datetime.now(UTC)
    issued = handle_store.issue(
        GroupAnalysisOptIn(
            enabled=True,
            centroid_rates=np.asarray([1.0, 2.0, 3.0]),
            strength=0.25,
            consent_verified=True,
            activation_generation=handle_store.authorization_generation(CONTEXT),
        ),
        context=CONTEXT,
        now=now,
    )

    purged = runtime.purge_expired(
        retention_days=365,
        identity_store=identity_store,
        activation_handle_store=handle_store,
        context=CONTEXT,
    )

    assert purged == [client_id]
    with pytest.raises(LookupError):
        identity_store.resolve(client_id, context=CONTEXT)
    with pytest.raises(LookupError):
        handle_store.consume(
            str(issued["activation_handle"]), context=CONTEXT, now=now
        )
