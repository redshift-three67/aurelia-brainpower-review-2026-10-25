from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import pytest

from core.compliance.group_activation_handle_store import GroupActivationHandleStore
from core.compliance.operator_context import OperatorContext, OwnershipError
from core.profiles.group_vector import GroupAnalysisOptIn


CONTEXT = OperatorContext(operator_id="operator-a", workspace_id="ws-a", tenant_id="tenant-a")
NOW = datetime(2026, 7, 12, 22, 30, tzinfo=UTC)


def test_activation_handle_writers_use_shared_durable_parent_helper(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from core.compliance import group_activation_handle_store as handle_store_module

    calls: list[Path] = []

    def parent(path: Path, *, mode: int = 0o777) -> None:
        calls.append(Path(path))
        Path(path).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(
        handle_store_module,
        "durable_mkdir_parents",
        parent,
        raising=False,
    )
    store = GroupActivationHandleStore(tmp_path / "nested" / "handles")

    _issue(store, _opt_in(), context=CONTEXT, now=NOW)

    assert len(calls) >= 3
    assert set(calls) == {store.root}


def _opt_in(*, strength: float = 0.25) -> GroupAnalysisOptIn:
    return GroupAnalysisOptIn(
        enabled=True,
        centroid_rates=np.asarray([10.25, 20.5, 30.75]),
        strength=strength,
        consent_verified=True,
    )


def _issue(
    store: GroupActivationHandleStore,
    opt_in: GroupAnalysisOptIn,
    *,
    context: OperatorContext,
    **kwargs: object,
) -> dict[str, object]:
    if not opt_in.activation_generation:
        opt_in = replace(
            opt_in,
            activation_generation=store.authorization_generation(context),
        )
    return GroupActivationHandleStore.issue(store, opt_in, context=context, **kwargs)


def test_activation_handle_rejects_unbound_root_authorization(tmp_path: Path) -> None:
    store = GroupActivationHandleStore(tmp_path / "handles")

    with pytest.raises(LookupError, match="generation is required"):
        GroupActivationHandleStore.issue(store, _opt_in(), context=CONTEXT, now=NOW)


def test_activation_handle_is_short_lived_redacted_and_encrypted_at_rest(tmp_path: Path) -> None:
    store = GroupActivationHandleStore(tmp_path / "handles")

    summary = _issue(store, _opt_in(), context=CONTEXT, now=NOW, ttl_seconds=60)

    assert set(summary) == {
        "activation_handle",
        "policy_version",
        "status",
        "expires_at",
        "one_time",
    }
    assert summary["activation_handle"].startswith("gah-")
    assert summary["policy_version"] == "group-activation-handle-v1"
    assert summary["status"] == "ready"
    assert summary["one_time"] is True
    safe_text = str(summary)
    assert "operator-a" not in safe_text
    assert "tenant-a" not in safe_text
    assert "10.25" not in safe_text
    protected = next(store.root.glob("gah-*.dpapi")).read_bytes()
    assert b"operator-a" not in protected
    assert b"tenant-a" not in protected
    assert b"10.25" not in protected


def test_activation_handle_is_one_time_and_reconstructs_only_in_memory(tmp_path: Path) -> None:
    store = GroupActivationHandleStore(tmp_path / "handles")
    issued = _issue(store, _opt_in(), context=CONTEXT, now=NOW, ttl_seconds=60)

    consumed = store.consume(
        str(issued["activation_handle"]),
        context=CONTEXT,
        now=NOW + timedelta(seconds=30),
    )

    assert consumed.enabled is True
    assert consumed.consent_verified is True
    assert consumed.strength == 0.25
    np.testing.assert_array_equal(consumed.centroid_rates, np.asarray([10.25, 20.5, 30.75]))
    with pytest.raises(LookupError):
        store.consume(
            str(issued["activation_handle"]),
            context=CONTEXT,
            now=NOW + timedelta(seconds=31),
        )


def test_activation_handle_fails_closed_for_foreign_context_without_consuming(tmp_path: Path) -> None:
    store = GroupActivationHandleStore(tmp_path / "handles")
    issued = _issue(store, _opt_in(), context=CONTEXT, now=NOW, ttl_seconds=60)
    handle = str(issued["activation_handle"])
    foreign = OperatorContext(operator_id="operator-b", workspace_id="ws-b", tenant_id="tenant-b")

    with pytest.raises(OwnershipError):
        store.consume(handle, context=foreign, now=NOW + timedelta(seconds=10))

    assert store.consume(handle, context=CONTEXT, now=NOW + timedelta(seconds=11)).enabled is True


def test_context_invalidation_revokes_issued_handles_and_stale_fanout(
    tmp_path: Path,
) -> None:
    store = GroupActivationHandleStore(tmp_path / "handles")
    root = _issue(store, _opt_in(), context=CONTEXT, now=NOW)
    stale_opt_in = store.consume(
        str(root["activation_handle"]), context=CONTEXT, now=NOW
    )
    child = _issue(store, stale_opt_in, context=CONTEXT, now=NOW)

    summary = store.invalidate_context(CONTEXT, now=NOW + timedelta(seconds=1))

    assert summary == {"invalidated_count": 1}
    with pytest.raises(LookupError):
        store.consume(
            str(child["activation_handle"]),
            context=CONTEXT,
            now=NOW + timedelta(seconds=2),
        )
    with pytest.raises(LookupError, match="invalidated"):
        _issue(store, stale_opt_in, context=CONTEXT, now=NOW + timedelta(seconds=2))


def test_context_invalidation_does_not_revoke_foreign_context_handles(
    tmp_path: Path,
) -> None:
    store = GroupActivationHandleStore(tmp_path / "handles")
    foreign = OperatorContext("operator-b", "ws-b", "tenant-b")
    issued = _issue(store, _opt_in(), context=foreign, now=NOW)

    assert store.invalidate_context(CONTEXT, now=NOW) == {"invalidated_count": 0}
    assert store.consume(
        str(issued["activation_handle"]), context=foreign, now=NOW
    ).enabled is True


def test_context_generation_key_is_unambiguous_for_separator_characters(
    tmp_path: Path,
) -> None:
    store = GroupActivationHandleStore(tmp_path / "handles")
    first = OperatorContext("a|b", "c", "d")
    second = OperatorContext("a", "b|c", "d")

    assert store._generation_path(first) != store._generation_path(second)


def test_activation_handle_expires_at_exact_boundary_and_is_removed(tmp_path: Path) -> None:
    store = GroupActivationHandleStore(tmp_path / "handles")
    issued = _issue(store, _opt_in(), context=CONTEXT, now=NOW, ttl_seconds=30)
    handle = str(issued["activation_handle"])

    with pytest.raises(TimeoutError, match="expired"):
        store.consume(handle, context=CONTEXT, now=NOW + timedelta(seconds=30))
    with pytest.raises(LookupError):
        store.consume(handle, context=CONTEXT, now=NOW + timedelta(seconds=31))


def test_activation_handle_ttl_and_opt_in_must_be_explicitly_safe(tmp_path: Path) -> None:
    store = GroupActivationHandleStore(tmp_path / "handles")

    for ttl in (0, 301, True):
        with pytest.raises(ValueError, match="ttl"):
            _issue(store, _opt_in(), context=CONTEXT, now=NOW, ttl_seconds=ttl)
    with pytest.raises(ValueError, match="enabled"):
        _issue(store, GroupAnalysisOptIn(enabled=False), context=CONTEXT, now=NOW)
    with pytest.raises(ValueError, match="consent"):
        _issue(store,
            GroupAnalysisOptIn(
                enabled=True,
                centroid_rates=np.asarray([1.0, 2.0]),
                strength=0.2,
                consent_verified=False,
            ),
            context=CONTEXT,
            now=NOW,
        )
    with pytest.raises(ValueError, match="strength"):
        _issue(store, _opt_in(strength=float("nan")), context=CONTEXT, now=NOW)


def test_activation_handle_explicit_erasure_requires_exact_confirmation_and_context(tmp_path: Path) -> None:
    store = GroupActivationHandleStore(tmp_path / "handles")
    issued = _issue(store, _opt_in(), context=CONTEXT, now=NOW)
    handle = str(issued["activation_handle"])

    with pytest.raises(ValueError, match="confirmation"):
        store.erase(handle, confirmation_handle="gah-00000000000000000000000000000000", context=CONTEXT)
    with pytest.raises(OwnershipError):
        store.erase(
            handle,
            confirmation_handle=handle,
            context=OperatorContext("operator-b", "ws-b", "tenant-b"),
        )
    assert store.erase(handle, confirmation_handle=handle, context=CONTEXT) is True
    assert store.erase(handle, confirmation_handle=handle, context=CONTEXT) is False


def test_activation_handle_purge_expired_is_redacted(tmp_path: Path) -> None:
    store = GroupActivationHandleStore(tmp_path / "handles")
    _issue(store, _opt_in(), context=CONTEXT, now=NOW, ttl_seconds=10)
    _issue(store, _opt_in(), context=CONTEXT, now=NOW, ttl_seconds=60)

    dry_run = store.purge_expired(now=NOW + timedelta(seconds=10), dry_run=True)
    actual = store.purge_expired(now=NOW + timedelta(seconds=10), dry_run=False)

    assert dry_run == {"expired_count": 1, "deleted_count": 0}
    assert actual == {"expired_count": 1, "deleted_count": 1}
    assert len(list(store.root.glob("gah-*.dpapi"))) == 1


def test_activation_handle_tamper_fails_closed_without_raw_error_details(tmp_path: Path) -> None:
    store = GroupActivationHandleStore(tmp_path / "handles")
    issued = _issue(store, _opt_in(), context=CONTEXT, now=NOW)
    target = store._path_for(str(issued["activation_handle"]))
    target.write_bytes(b"tampered")

    with pytest.raises(ValueError, match="activation handle payload is invalid"):
        store.consume(str(issued["activation_handle"]), context=CONTEXT, now=NOW)


def test_activation_handle_rejects_noncanonical_and_path_like_identifiers(tmp_path: Path) -> None:
    store = GroupActivationHandleStore(tmp_path / "handles")

    for invalid in (
        "../gah-00000000000000000000000000000000",
        "gah-00000000000000000000000000000000/..",
        "C:\\temp\\gah-00000000000000000000000000000000",
        "gah-short",
        "gah-0000000000000000000000000000000G",
    ):
        with pytest.raises(ValueError, match="canonical"):
            store.worker_payload(invalid)


def test_activation_handle_failed_atomic_replace_cleans_temp_and_preserves_existing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = GroupActivationHandleStore(tmp_path / "handles")
    first = _issue(store, _opt_in(), context=CONTEXT, now=NOW)
    before = store._path_for(str(first["activation_handle"])).read_bytes()

    def fail_replace(self: Path, target: Path) -> Path:
        raise OSError("synthetic replace failure")

    monkeypatch.setattr(Path, "replace", fail_replace)
    with pytest.raises(OSError, match="synthetic replace failure"):
        _issue(store, _opt_in(), context=CONTEXT, now=NOW)

    assert store._path_for(str(first["activation_handle"])).read_bytes() == before
    assert list(store.root.glob("*.tmp.*")) == []


def test_worker_payload_contains_only_handle_and_rejects_raw_or_extra_fields(tmp_path: Path) -> None:
    store = GroupActivationHandleStore(tmp_path / "handles")
    issued = _issue(store, _opt_in(), context=CONTEXT, now=NOW)
    handle = str(issued["activation_handle"])

    payload = store.worker_payload(handle)

    assert payload == {"activation_handle": handle}
    assert "10.25" not in str(payload)
    consumed = store.consume_worker_payload(payload, context=CONTEXT, now=NOW)
    assert consumed.enabled is True

    second = _issue(store, _opt_in(), context=CONTEXT, now=NOW)
    second_handle = str(second["activation_handle"])
    with pytest.raises(ValueError, match="only activation_handle"):
        store.consume_worker_payload(
            {"activation_handle": second_handle, "group_member_rates": [1.0, 2.0]},
            context=CONTEXT,
            now=NOW,
        )
    with pytest.raises(ValueError, match="only activation_handle"):
        store.consume_worker_payload(
            {"activation_handle": second_handle, "subject_id": "cli-secret"},
            context=CONTEXT,
            now=NOW,
        )


def test_concurrent_consumers_cannot_reuse_one_time_handle(tmp_path: Path) -> None:
    from concurrent.futures import ThreadPoolExecutor

    store = GroupActivationHandleStore(tmp_path / "handles")
    issued = _issue(store, _opt_in(), context=CONTEXT, now=NOW)
    handle = str(issued["activation_handle"])

    def consume() -> str:
        try:
            store.consume(handle, context=CONTEXT, now=NOW)
            return "consumed"
        except LookupError:
            return "missing"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = sorted(pool.map(lambda _: consume(), range(2)))

    assert outcomes == ["consumed", "missing"]


def test_activation_handle_audit_is_redacted_and_productive_paths_do_not_import_store(
    tmp_path: Path,
) -> None:
    store = GroupActivationHandleStore(tmp_path / "handles")
    issued = _issue(store, _opt_in(), context=CONTEXT, now=NOW)
    store.consume(str(issued["activation_handle"]), context=CONTEXT, now=NOW)

    audit = store.audit_events()
    assert [event["event"] for event in audit] == ["issued", "consumed"]
    audit_text = str(audit)
    for forbidden in ("gah-", "operator-a", "ws-a", "tenant-a", "10.25", "20.5", "30.75"):
        assert forbidden not in audit_text

    root = Path(__file__).resolve().parents[1]
    protected_paths = (
        root / "apps" / "web" / "contracts.py",
        root / "apps" / "web" / "launcher.py",
        root / "apps" / "web" / "group_drafts.py",
        root / "apps" / "cli" / "commands" / "field.py",
        root / "core" / "compliance" / "run_manifest.py",
    )
    for path in protected_paths:
        source = path.read_text(encoding="utf-8")
        assert "GroupActivationHandleStore" not in source
        assert "group_activation_handle_store" not in source
        assert "activation_handle" not in source
