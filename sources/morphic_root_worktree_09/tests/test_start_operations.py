from __future__ import annotations

import hashlib
import json
import multiprocessing
import time
from pathlib import Path

import pytest

from apps.web.start_operations import (
    StartOperationConflictError,
    StartOperationError,
    StartOperationStore,
)


def test_start_operation_root_and_lock_use_shared_durable_parent_helper(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps.web import start_operations

    calls: list[Path] = []

    def parent(path: Path, *, mode: int = 0o777) -> None:
        calls.append(Path(path))
        Path(path).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(start_operations, "durable_mkdir_parents", parent, raising=False)
    root = tmp_path / "nested" / "start-operations"
    store = StartOperationStore(root)

    store.begin(
        kind="scan",
        key="scan-parent-helper-12345678",
        owner_id="tenant:operator",
        request_sha256=_hash("request"),
    )

    assert calls.count(root) >= 2


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _hold_cross_process_claim(root, ready, release, results) -> None:
    store = StartOperationStore(root)
    with store.operation(
        kind="scan",
        key="scan-cross-process-12345678",
        owner_id="tenant:operator",
        request_sha256=_hash("same-request"),
    ) as claim:
        results.put(claim.is_new)
        ready.set()
        release.wait(5)


def _wait_cross_process_claim(root, started, results) -> None:
    started.set()
    store = StartOperationStore(root)
    with store.operation(
        kind="scan",
        key="scan-cross-process-12345678",
        owner_id="tenant:operator",
        request_sha256=_hash("same-request"),
    ) as claim:
        results.put(claim.is_new)


def _hold_cross_process_inspection_claim(root, ready, release) -> None:
    store = StartOperationStore(root)
    with store.operation(
        kind="scan",
        key="scan-inspection-lock-12345678",
        owner_id="tenant:operator",
        request_sha256=_hash("same-request"),
    ) as claim:
        ready.set()
        release.wait(5)
        claim.complete(claim.job_id)


def _wait_cross_process_inspection(root, started, results) -> None:
    started.set()
    store = StartOperationStore(root)
    with store.inspect(
        kind="scan",
        key="scan-inspection-lock-12345678",
        owner_id="tenant:operator",
    ) as claim:
        results.put(None if claim is None else claim.state)


def test_pending_start_operation_survives_restart_and_blocks_second_claim(tmp_path) -> None:
    root = tmp_path / "start-operations"
    first = StartOperationStore(root)

    assert first.begin(
        kind="scan",
        key="scan-qa-12345678",
        owner_id="operator-local",
        request_sha256=_hash("request-a"),
    ) is None

    restarted = StartOperationStore(root)
    existing = restarted.begin(
        kind="scan",
        key="scan-qa-12345678",
        owner_id="operator-local",
        request_sha256=_hash("request-a"),
    )

    assert existing is not None
    assert existing["state"] == "pending"
    assert existing["job_id"].startswith("scan-op-")


def test_start_operation_claim_is_exclusive_across_processes(tmp_path) -> None:
    context = multiprocessing.get_context("spawn")
    ready = context.Event()
    release = context.Event()
    second_started = context.Event()
    results = context.Queue()
    root = tmp_path / "start-operations"
    first = context.Process(
        target=_hold_cross_process_claim,
        args=(root, ready, release, results),
    )
    second = context.Process(
        target=_wait_cross_process_claim,
        args=(root, second_started, results),
    )
    first.start()
    assert ready.wait(5)
    second.start()
    assert second_started.wait(5)
    time.sleep(0.25)
    assert second.is_alive(), "second process must wait for the durable claim lock"
    release.set()
    first.join(5)
    second.join(5)

    assert first.exitcode == 0
    assert second.exitcode == 0
    assert sorted([results.get(timeout=1), results.get(timeout=1)]) == [False, True]


def test_inspect_absent_operation_does_not_create_a_record(tmp_path: Path) -> None:
    root = tmp_path / "start-operations"
    store = StartOperationStore(root)

    with store.inspect(
        kind="scan",
        key="scan-inspect-absent-12345678",
        owner_id="tenant:operator",
    ) as claim:
        assert claim is None

    assert list(root.glob("*.json")) == []


def test_inspect_is_owner_bound_without_requiring_request_hash(tmp_path: Path) -> None:
    store = StartOperationStore(tmp_path / "start-operations")
    key = "scan-inspect-owner-12345678"
    with store.operation(
        kind="scan",
        key=key,
        owner_id="tenant:operator-a",
        request_sha256=_hash("request-a"),
    ) as created:
        created.complete(created.job_id)

    with store.inspect(
        kind="scan",
        key=key,
        owner_id="tenant:operator-b",
    ) as foreign:
        assert foreign is None
    with store.inspect(
        kind="scan",
        key=key,
        owner_id="tenant:operator-a",
    ) as owned:
        assert owned is not None
        assert owned.state == "completed"
        assert owned.job_id.startswith("scan-op-")


@pytest.mark.parametrize("field", ["kind", "owner_id", "key_sha256"])
def test_inspect_rejects_corrupt_record_identity(
    tmp_path: Path,
    field: str,
) -> None:
    store = StartOperationStore(tmp_path / "start-operations")
    key = "scan-inspect-corrupt-12345678"
    owner = "tenant:operator"
    with store.operation(
        kind="scan",
        key=key,
        owner_id=owner,
        request_sha256=_hash("request"),
    ):
        pass
    path, _, _ = store._path("scan", key, owner)
    record = json.loads(path.read_text(encoding="utf-8"))
    record[field] = "corrupt"
    path.write_text(json.dumps(record), encoding="utf-8")

    with pytest.raises(StartOperationConflictError):
        with store.inspect(kind="scan", key=key, owner_id=owner):
            pass


@pytest.mark.parametrize(
    ("field", "corrupt_value"),
    [
        pytest.param("schema_version", True, id="bool-schema-version"),
        pytest.param("kind", [], id="list-kind"),
        pytest.param("kind", {}, id="dict-kind"),
        pytest.param("state", [], id="list-state"),
        pytest.param("state", {}, id="dict-state"),
        pytest.param("owner_id", [], id="list-owner"),
        pytest.param("key_sha256", {}, id="dict-key-hash"),
        pytest.param("request_sha256", [], id="list-request-hash"),
        pytest.param("created_at", {}, id="dict-created-at"),
        pytest.param("updated_at", [], id="list-updated-at"),
    ],
)
def test_inspect_normalizes_typed_record_corruption_to_conflict(
    tmp_path: Path,
    field: str,
    corrupt_value: object,
) -> None:
    store = StartOperationStore(tmp_path / "start-operations")
    key = "scan-inspect-typed-corrupt-12345678"
    owner = "tenant:operator"
    with store.operation(
        kind="scan",
        key=key,
        owner_id=owner,
        request_sha256=_hash("request"),
    ):
        pass
    path, _, _ = store._path("scan", key, owner)
    record = json.loads(path.read_text(encoding="utf-8"))
    record[field] = corrupt_value
    path.write_text(json.dumps(record), encoding="utf-8")

    with pytest.raises(StartOperationConflictError):
        with store.inspect(kind="scan", key=key, owner_id=owner):
            pass


def test_inspect_waits_for_claim_owner_and_observes_completed_commit(
    tmp_path: Path,
) -> None:
    context = multiprocessing.get_context("spawn")
    ready = context.Event()
    release = context.Event()
    inspection_started = context.Event()
    results = context.Queue()
    root = tmp_path / "start-operations"
    owner = context.Process(
        target=_hold_cross_process_inspection_claim,
        args=(root, ready, release),
    )
    inspector = context.Process(
        target=_wait_cross_process_inspection,
        args=(root, inspection_started, results),
    )
    owner.start()
    assert ready.wait(5)
    inspector.start()
    assert inspection_started.wait(5)
    time.sleep(0.25)
    assert inspector.is_alive(), "inspection must wait for the claim-owning operation"
    release.set()
    owner.join(5)
    inspector.join(5)

    assert owner.exitcode == 0
    assert inspector.exitcode == 0
    assert results.get(timeout=1) == "completed"


def test_completed_start_operation_replays_job_and_rejects_payload_change(tmp_path) -> None:
    store = StartOperationStore(tmp_path / "start-operations")
    key = "harm-qa-12345678"
    owner_id = "operator-local"
    request_hash = _hash("request-a")
    assert store.begin(
        kind="harmonization",
        key=key,
        owner_id=owner_id,
        request_sha256=request_hash,
    ) is None
    pending = store.begin(
        kind="harmonization",
        key=key,
        owner_id=owner_id,
        request_sha256=request_hash,
    )
    assert pending is not None
    job_id = pending["job_id"]
    assert job_id.startswith("harm_")
    store.complete(
        kind="harmonization",
        key=key,
        owner_id=owner_id,
        job_id=job_id,
    )

    replay = StartOperationStore(store.root).begin(
        kind="harmonization",
        key=key,
        owner_id=owner_id,
        request_sha256=request_hash,
    )

    assert replay is not None
    assert replay["state"] == "completed"
    assert replay["job_id"] == job_id
    with pytest.raises(StartOperationError, match="identity mismatch"):
        store.begin(
            kind="harmonization",
            key=key,
            owner_id=owner_id,
            request_sha256=_hash("request-b"),
        )


def test_completed_operation_cannot_be_downgraded_to_failed(tmp_path) -> None:
    store = StartOperationStore(tmp_path / "start-operations")
    key = "scan-completed-immutable-12345678"
    request_hash = _hash("request")
    assert store.begin(
        kind="scan",
        key=key,
        owner_id="tenant:operator",
        request_sha256=request_hash,
    ) is None
    record = store.begin(
        kind="scan",
        key=key,
        owner_id="tenant:operator",
        request_sha256=request_hash,
    )
    assert record is not None
    store.complete(
        kind="scan",
        key=key,
        owner_id="tenant:operator",
        job_id=record["job_id"],
    )

    with pytest.raises(StartOperationError, match="completed"):
        store.fail(
            kind="scan",
            key=key,
            owner_id="tenant:operator",
        )
