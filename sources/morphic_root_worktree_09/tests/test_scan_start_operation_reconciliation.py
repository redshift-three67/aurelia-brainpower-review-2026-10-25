from __future__ import annotations

import hashlib
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from apps.web import main as web_main
from apps.web import scan_jobs as scan_jobs_module
from apps.web.main import create_app
from apps.web.scan_jobs import (
    LocalScanJobService,
    ProcessAuthorityAmbiguousError,
    ScanJobOwnershipError,
    ScanJobReplayIdentityError,
    ScanJobReplayOwnershipError,
)
from core.compliance.operator_context import operator_owner_scope
from tests.test_web_shell import request


RECONCILE_PATH = "/api/scan/start-operation/reconcile"


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _scan_body(fingerprint: str) -> dict[str, Any]:
    return {
        "last_name": "Gate",
        "first_name": "Drei",
        "birth_date": "09041966",
        "birth_place": "Augsburg",
        "focus": "synthetischer Fokus",
        "profile_level": 3,
        "top_n": 5,
        "scan_profile_pool_fingerprint": fingerprint,
        "consent_local": True,
        "consent_safety": True,
    }


class ReconciliationScanJobs:
    def __init__(self) -> None:
        self.jobs: dict[str, dict[str, Any]] = {}
        self.started: list[str] = []
        self.start_env_overrides: list[dict[str, str] | None] = []
        self.get_owned_calls: list[str] = []
        self.observe_owned_calls: list[str] = []
        self.authority_error: BaseException | None = None

    def start(
        self,
        command: list[str],
        owner_id: str | None = None,
        env_overrides: dict[str, str] | None = None,
        job_id: str | None = None,
    ) -> dict[str, Any]:
        assert job_id is not None
        self.started.append(job_id)
        self.start_env_overrides.append(
            None if env_overrides is None else dict(env_overrides)
        )
        job = {
            "executes": True,
            "job_id": job_id,
            "status": "running",
            "command": list(command),
            "progress_percent": 7.5,
            "current_phase": "Phase 1",
            "current_substep": "Screening",
            "completed_substeps": [],
            "owner_id": owner_id,
            "updated_at": "2026-07-27T12:00:00+00:00",
        }
        self.jobs[job_id] = job
        return dict(job)

    def get_owned(
        self,
        job_id: str,
        *,
        expected_owner_id: str,
    ) -> dict[str, Any]:
        self.get_owned_calls.append(job_id)
        if self.authority_error is not None:
            raise self.authority_error
        if job_id not in self.jobs:
            raise KeyError(job_id)
        job = self.jobs[job_id]
        if job.get("owner_id") != expected_owner_id:
            raise ScanJobOwnershipError("private foreign owner detail")
        return dict(job)

    def observe_owned(
        self,
        job_id: str,
        *,
        expected_owner_id: str,
    ) -> dict[str, Any]:
        self.observe_owned_calls.append(job_id)
        if self.authority_error is not None:
            raise self.authority_error
        if job_id not in self.jobs:
            raise KeyError(job_id)
        job = self.jobs[job_id]
        if job.get("owner_id") != expected_owner_id:
            raise ScanJobOwnershipError("private foreign owner detail")
        return dict(job)

    def get_for_replay(
        self,
        job_id: str,
        *,
        expected_command: list[str],
        expected_owner_id: str | None,
    ) -> dict[str, Any]:
        if job_id not in self.jobs:
            raise KeyError(job_id)
        job = self.jobs[job_id]
        if job.get("owner_id") != expected_owner_id:
            raise ScanJobReplayOwnershipError("foreign")
        if job.get("command") != expected_command:
            raise ScanJobReplayIdentityError("command")
        return dict(job)

    def stop_owned(
        self,
        job_id: str,
        *,
        expected_owner_id: str,
    ) -> dict[str, Any]:
        job = self.get_owned(job_id, expected_owner_id=expected_owner_id)
        job["status"] = "stopped"
        self.jobs[job_id] = job
        return dict(job)


def _operation_owner(app: Any) -> str:
    return operator_owner_scope(app.state.operator_context)


def _create_operation(app: Any, key: str, state: str = "pending") -> str:
    with app.state.start_operations.operation(
        kind="scan",
        key=key,
        owner_id=_operation_owner(app),
        request_sha256=_hash("request"),
    ) as claim:
        job_id = claim.job_id
        if state == "failed":
            claim.fail_before_creation()
        elif state == "completed":
            claim.complete(job_id)
        elif state != "pending":
            raise AssertionError(f"unsupported state {state}")
    return job_id


def _reconcile(app: Any, key: str):
    return request(
        app,
        "POST",
        RECONCILE_PATH,
        request_headers={"Idempotency-Key": key},
    )


def test_reconcile_absent_operation_retains_key_without_creating_record(
    tmp_path: Path,
) -> None:
    jobs = ReconciliationScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)

    response = _reconcile(app, "scan-reconcile-absent-12345678")

    assert response.status_code == 200
    assert response.json() == {"disposition": "retry-same-key"}
    assert "x-morphic-start-operation" not in response.headers
    assert list(app.state.start_operations.root.glob("*.json")) == []
    assert jobs.started == []
    assert jobs.observe_owned_calls == []


def test_reconcile_failed_operation_is_safe_to_replace(tmp_path: Path) -> None:
    jobs = ReconciliationScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)
    key = "scan-reconcile-failed-12345678"
    _create_operation(app, key, "failed")

    response = _reconcile(app, key)

    assert response.status_code == 200
    assert response.json() == {"disposition": "safe-to-replace"}
    assert response.headers["x-morphic-start-operation"] == "safe-to-replace"
    assert jobs.started == []
    assert jobs.observe_owned_calls == []


def test_scan_start_passes_emf_authority_path_to_productive_process_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jobs = ReconciliationScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)
    app.state.emf_telemetry_authority.set_enabled(True)
    key = "scan-emf-authority-12345678"
    headers = {"Idempotency-Key": key}
    pool = {"fingerprint": "c" * 64}

    def authority(_profile_level: int) -> SimpleNamespace:
        return SimpleNamespace(fingerprint=pool["fingerprint"], count=9)

    monkeypatch.setattr(web_main, "current_scan_profile_pool_authority", authority)

    response = request(app, "POST", "/api/scan/jobs", _scan_body(pool["fingerprint"]), headers)

    assert response.status_code == 200
    assert jobs.started == [response.json()["job_id"]]
    assert jobs.start_env_overrides == [
        {
            "MORPHIC_EXPECTED_SCAN_PROFILE_POOL_FINGERPRINT": pool["fingerprint"],
            "MORPHIC_EMF_AUTHORITY_PATH": str(app.state.emf_telemetry_authority.path),
        }
    ]


@pytest.mark.parametrize("initial_state", ["pending", "completed"])
def test_reconcile_existing_owned_job_returns_redacted_job_and_completes_pending_claim(
    tmp_path: Path,
    initial_state: str,
) -> None:
    jobs = ReconciliationScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)
    key = f"scan-reconcile-job-{initial_state}-12345678"
    job_id = _create_operation(app, key, initial_state)
    jobs.jobs[job_id] = {
        "job_id": job_id,
        "status": "running",
        "progress_percent": 12.5,
        "current_phase": "Phase 1",
        "current_substep": "Screening",
        "completed_substeps": [],
        "command": ["private", "command"],
        "owner_id": _operation_owner(app),
        "focus": "private focus",
        "request_sha256": "private hash",
        "updated_at": "2026-07-27T12:00:00+00:00",
    }

    response = _reconcile(app, key)

    assert response.status_code == 200
    payload = response.json()
    assert payload["disposition"] == "job"
    assert payload["job_id"] == job_id
    assert payload["status"] == "running"
    for forbidden in (
        "command",
        "owner_id",
        "focus",
        "request_sha256",
        "created_at",
        "updated_at",
    ):
        assert forbidden not in payload
    with app.state.start_operations.inspect(
        kind="scan",
        key=key,
        owner_id=_operation_owner(app),
    ) as claim:
        assert claim is not None
        assert claim.state == "completed"
    assert jobs.started == []
    assert jobs.observe_owned_calls == [job_id]


def test_reconcile_pending_without_job_marks_failed_and_allows_replacement(
    tmp_path: Path,
) -> None:
    jobs = ReconciliationScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)
    key = "scan-reconcile-pending-missing-12345678"
    job_id = _create_operation(app, key, "pending")

    response = _reconcile(app, key)

    assert response.status_code == 200
    assert response.json() == {"disposition": "safe-to-replace"}
    assert response.headers["x-morphic-start-operation"] == "safe-to-replace"
    with app.state.start_operations.inspect(
        kind="scan",
        key=key,
        owner_id=_operation_owner(app),
    ) as claim:
        assert claim is not None
        assert claim.state == "failed"
    assert jobs.started == []
    assert jobs.observe_owned_calls == [job_id]


def test_reconcile_completed_without_job_fails_closed(tmp_path: Path) -> None:
    jobs = ReconciliationScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)
    key = "scan-reconcile-completed-missing-12345678"
    job_id = _create_operation(app, key, "completed")

    response = _reconcile(app, key)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "completed scan operation lost job authority"
    }
    assert "x-morphic-start-operation" not in response.headers
    assert jobs.started == []
    assert jobs.observe_owned_calls == [job_id]


@pytest.mark.parametrize(
    ("initial_state", "expected_status", "expected_disposition"),
    [
        ("pending", 200, "safe-to-replace"),
        ("completed", 409, None),
    ],
)
def test_reconcile_uses_local_job_authority_without_starting_a_job(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    initial_state: str,
    expected_status: int,
    expected_disposition: str | None,
) -> None:
    app = create_app(runtime_dir=tmp_path / "runtime")
    key = f"scan-reconcile-local-{initial_state}-12345678"
    _create_operation(app, key, initial_state)
    start_calls: list[str] = []
    monkeypatch.setattr(
        app.state.scan_jobs,
        "start",
        lambda *args, **kwargs: start_calls.append("start"),
    )

    response = _reconcile(app, key)

    assert response.status_code == expected_status
    if expected_disposition is not None:
        assert response.json() == {"disposition": expected_disposition}
    assert start_calls == []


def test_reconcile_observes_unreleased_local_job_without_release_or_state_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=service)
    key = "scan-reconcile-unreleased-local-12345678"
    job_id = _create_operation(app, key, "pending")
    marker = tmp_path / "productive-command-ran.txt"
    command = [
        sys.executable,
        "-c",
        (
            "from pathlib import Path; "
            f"Path({str(marker)!r}).write_text('released', encoding='utf-8')"
        ),
    ]

    with monkeypatch.context() as setup:
        setup.setattr(
            service,
            "_release_registered_start",
            lambda job: {"job_id": job.job_id, "status": "starting"},
        )
        service.start(command, owner_id=_operation_owner(app), job_id=job_id)

    job = service._jobs[job_id]
    process = job.process
    state_path = service._state_path(job_id)
    state_before = state_path.read_bytes()
    release_path = service._start_release_path(job_id, job.process_group_token)
    started_path = service._start_started_path(job_id, job.process_group_token)
    spawn_calls: list[str] = []

    def reject_spawn(*_args: Any, **_kwargs: Any) -> None:
        spawn_calls.append("spawn")
        raise AssertionError("reconcile attempted to spawn a process")

    monkeypatch.setattr(scan_jobs_module.subprocess, "Popen", reject_spawn)
    try:
        response = _reconcile(app, key)

        assert not release_path.exists()
        assert not started_path.exists()
        assert not marker.exists()
        assert spawn_calls == []
        assert state_path.read_bytes() == state_before
        assert job.start_released is False
        assert response.status_code == 200
        assert response.json() == {
            "disposition": "job",
            "job_id": job_id,
            "status": "starting",
        }
    finally:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=5)


def test_reconcile_waits_for_claim_commit_and_never_reports_safe_to_replace(
    tmp_path: Path,
) -> None:
    jobs = ReconciliationScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)
    key = "scan-reconcile-lock-commit-12345678"
    request_started = threading.Event()

    def reconcile_in_thread():
        request_started.set()
        return _reconcile(app, key)

    with ThreadPoolExecutor(max_workers=1) as pool:
        with app.state.start_operations.operation(
            kind="scan",
            key=key,
            owner_id=_operation_owner(app),
            request_sha256=_hash("request"),
        ) as claim:
            job_id = claim.job_id
            jobs.jobs[job_id] = {
                "job_id": job_id,
                "status": "running",
                "owner_id": _operation_owner(app),
            }
            pending = pool.submit(reconcile_in_thread)
            assert request_started.wait(timeout=2)
            time.sleep(0.2)
            assert not pending.done()
            assert jobs.observe_owned_calls == []
            claim.complete(job_id)

        response = pending.result(timeout=5)

    assert response.status_code == 200
    assert response.json() == {
        "disposition": "job",
        "job_id": job_id,
        "status": "running",
    }
    assert "x-morphic-start-operation" not in response.headers
    assert jobs.observe_owned_calls == [job_id]
    with app.state.start_operations.inspect(
        kind="scan",
        key=key,
        owner_id=_operation_owner(app),
    ) as committed:
        assert committed is not None
        assert committed.state == "completed"


def test_reconcile_maps_job_owner_mismatch_to_redacted_forbidden(
    tmp_path: Path,
) -> None:
    jobs = ReconciliationScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)
    key = "scan-reconcile-job-owner-mismatch-12345678"
    job_id = _create_operation(app, key)
    jobs.jobs[job_id] = {
        "job_id": job_id,
        "status": "running",
        "owner_id": "foreign-private-owner",
    }

    response = _reconcile(app, key)

    assert response.status_code == 403
    assert response.json() == {"detail": "resource access forbidden"}
    assert "x-morphic-start-operation" not in response.headers
    assert "foreign" not in response.text
    assert jobs.started == []


def test_reconcile_record_owner_mismatch_is_forbidden_without_leak(
    tmp_path: Path,
) -> None:
    jobs = ReconciliationScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)
    key = "scan-reconcile-record-owner-mismatch-12345678"
    _create_operation(app, key)
    path, _, _ = app.state.start_operations._path(
        "scan", key, _operation_owner(app)
    )
    record = json.loads(path.read_text(encoding="utf-8"))
    record["owner_id"] = "foreign-private-owner"
    path.write_text(json.dumps(record), encoding="utf-8")

    response = _reconcile(app, key)

    assert response.status_code == 403
    assert response.json() == {"detail": "resource access forbidden"}
    assert "foreign" not in response.text
    assert jobs.started == []
    assert jobs.observe_owned_calls == []


@pytest.mark.parametrize("corruption", ["unreadable", "key-hash"])
def test_reconcile_corrupt_record_fails_closed_without_detail_leak(
    tmp_path: Path,
    corruption: str,
) -> None:
    jobs = ReconciliationScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)
    key = f"scan-reconcile-corrupt-{corruption}-12345678"
    _create_operation(app, key)
    path, _, _ = app.state.start_operations._path(
        "scan", key, _operation_owner(app)
    )
    if corruption == "unreadable":
        path.write_text("{private-corruption", encoding="utf-8")
    else:
        record = json.loads(path.read_text(encoding="utf-8"))
        record["key_sha256"] = "private-corruption"
        path.write_text(json.dumps(record), encoding="utf-8")

    response = _reconcile(app, key)

    assert response.status_code == 409
    assert response.json() == {"detail": "scan start operation authority mismatch"}
    assert "x-morphic-start-operation" not in response.headers
    assert "private" not in response.text
    assert jobs.started == []
    assert jobs.observe_owned_calls == []


@pytest.mark.parametrize(
    ("field", "corrupt_value"),
    [
        pytest.param("kind", ["private-kind"], id="list-kind"),
        pytest.param("kind", {"private-kind": True}, id="dict-kind"),
        pytest.param("state", ["private-state"], id="list-state"),
        pytest.param("state", {"private-state": True}, id="dict-state"),
    ],
)
def test_reconcile_unhashable_record_fields_fail_closed_without_detail_leak(
    tmp_path: Path,
    field: str,
    corrupt_value: object,
) -> None:
    jobs = ReconciliationScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)
    key = f"scan-reconcile-unhashable-{field}-12345678"
    _create_operation(app, key)
    path, _, _ = app.state.start_operations._path(
        "scan", key, _operation_owner(app)
    )
    record = json.loads(path.read_text(encoding="utf-8"))
    record[field] = corrupt_value
    path.write_text(json.dumps(record), encoding="utf-8")

    response = _reconcile(app, key)

    assert response.status_code == 409
    assert response.json() == {"detail": "scan start operation authority mismatch"}
    assert "x-morphic-start-operation" not in response.headers
    assert "private" not in response.text
    assert jobs.started == []
    assert jobs.observe_owned_calls == []


def test_reconcile_ambiguous_job_authority_is_generic_and_retains_claim(
    tmp_path: Path,
) -> None:
    jobs = ReconciliationScanJobs()
    jobs.authority_error = ProcessAuthorityAmbiguousError("private authority path")
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)
    key = "scan-reconcile-ambiguous-job-12345678"
    _create_operation(app, key)

    response = _reconcile(app, key)

    assert response.status_code == 503
    assert response.json() == {"detail": "scan job authority unavailable"}
    assert "x-morphic-start-operation" not in response.headers
    assert "private" not in response.text
    with app.state.start_operations.inspect(
        kind="scan",
        key=key,
        owner_id=_operation_owner(app),
    ) as claim:
        assert claim is not None
        assert claim.state == "pending"
    assert jobs.started == []


@pytest.mark.parametrize("failure_boundary", ["operation-lock", "job-authority"])
def test_reconcile_io_failure_is_generic_without_clear_disposition(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_boundary: str,
) -> None:
    jobs = ReconciliationScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)
    key = f"scan-reconcile-io-{failure_boundary}-12345678"
    if failure_boundary == "job-authority":
        _create_operation(app, key)
        jobs.authority_error = OSError("C:\\private\\job-authority.json")
    else:
        @contextmanager
        def unavailable_inspection(**_kwargs: Any):
            raise OSError("C:\\private\\start-operation.lock")
            yield

        monkeypatch.setattr(
            app.state.start_operations,
            "inspect",
            unavailable_inspection,
        )

    response = _reconcile(app, key)

    assert response.status_code == 503
    assert response.json() == {"detail": "scan start operation authority unavailable"}
    assert "x-morphic-start-operation" not in response.headers
    assert "private" not in response.text
    assert jobs.started == []


@pytest.mark.parametrize(
    ("foreign_tenant", "foreign_operator"),
    [
        pytest.param("tenant-a", "operator-b", id="same-tenant-foreign-operator"),
        pytest.param("tenant-b", "operator-a", id="foreign-tenant-same-operator"),
    ],
)
def test_same_key_for_foreign_authority_dimension_is_absent_without_job_lookup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    foreign_tenant: str,
    foreign_operator: str,
) -> None:
    runtime = tmp_path / "runtime"
    jobs = ReconciliationScanJobs()
    key = "scan-reconcile-cross-owner-12345678"
    monkeypatch.setenv("MORPHIC_TENANT_ID", "tenant-a")
    monkeypatch.setenv("MORPHIC_OPERATOR_ID", "operator-a")
    app_a = create_app(runtime_dir=runtime, scan_jobs=jobs)
    job_id = _create_operation(app_a, key, "completed")
    jobs.jobs[job_id] = {
        "job_id": job_id,
        "status": "running",
        "owner_id": _operation_owner(app_a),
    }

    monkeypatch.setenv("MORPHIC_TENANT_ID", foreign_tenant)
    monkeypatch.setenv("MORPHIC_OPERATOR_ID", foreign_operator)
    app_b = create_app(runtime_dir=runtime, scan_jobs=jobs)
    foreign = _reconcile(app_b, key)

    assert foreign.status_code == 200
    assert foreign.json() == {"disposition": "retry-same-key"}
    assert jobs.observe_owned_calls == []
    assert job_id not in foreign.text

    owned = _reconcile(app_a, key)
    assert owned.status_code == 200
    assert owned.json()["job_id"] == job_id
    assert jobs.observe_owned_calls == [job_id]
    assert jobs.started == []


def test_reconcile_requires_api_authentication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MORPHIC_API_KEY", "configured-secret")
    jobs = ReconciliationScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)

    response = _reconcile(app, "scan-reconcile-protected-12345678")

    assert response.status_code == 401
    assert jobs.started == []
    assert jobs.observe_owned_calls == []


def test_pool_drift_retry_can_reconcile_original_committed_job_without_request_body(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jobs = ReconciliationScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)
    key = "scan-reconcile-pool-drift-12345678"
    headers = {"Idempotency-Key": key}
    pool = {"fingerprint": "a" * 64}

    def authority(_profile_level: int) -> SimpleNamespace:
        return SimpleNamespace(fingerprint=pool["fingerprint"], count=9)

    monkeypatch.setattr(web_main, "current_scan_profile_pool_authority", authority)
    body = _scan_body(pool["fingerprint"])
    committed = request(app, "POST", "/api/scan/jobs", body, headers)
    assert committed.status_code == 200
    job_id = committed.json()["job_id"]

    pool["fingerprint"] = "b" * 64
    stale_retry = request(app, "POST", "/api/scan/jobs", body, headers)
    reconciled = _reconcile(app, key)

    assert stale_retry.status_code == 409
    assert stale_retry.headers["x-morphic-scan-profile-pool"] == "stale"
    assert reconciled.status_code == 200
    assert reconciled.json()["disposition"] == "job"
    assert reconciled.json()["job_id"] == job_id
    assert jobs.started == [job_id]
    assert len(jobs.jobs) == 1
