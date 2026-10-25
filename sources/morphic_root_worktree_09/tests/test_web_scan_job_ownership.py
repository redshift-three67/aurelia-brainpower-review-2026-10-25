"""Tests fuer die additive Ownership-Pruefung am Scan-Job-Results-Endpoint.

Verifiziert das Verhalten aus Task 2 Schritt 4 des
morphic-v1-radiquant4-alignment-Plans:
- Jobs ohne owner_id bleiben fail-closed, bis eine belegte Migration Ownership setzt.
- Jobs mit owner_id koennen nur vom zugehoerigen Operator abgerufen werden.
- Der Operator-Kontext wird beim Start eines Jobs aufgezeichnet.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from apps.web import scan_jobs as scan_jobs_module
from apps.web.main import create_app
from apps.web.scan_jobs import (
    LocalScanJobService,
    ProcessAuthorityAmbiguousError,
    ScanJobOwnershipError,
    ScanJobReplayOwnershipError,
    _LocalScanJob,
)
from apps.web.workbench import current_scan_profile_pool_fingerprint
from tests.test_web_shell import AsgiResponse, request


class OwnershipScanJobs:
    """Scan-Job-Store-Stub mit explizitem owner_id-Tracking fuer Ownership-Tests."""

    def __init__(self, owner_id: str | None = None) -> None:
        self.owner_id = owner_id
        self.started_commands: list[list[str]] = []
        self.stopped: list[str] = []

    def start(
        self,
        command: list[str],
        owner_id: str | None = None,
        env_overrides: dict[str, str] | None = None,
        job_id: str | None = None,
    ) -> dict[str, Any]:
        self.started_commands.append(command)
        self.owner_id = owner_id
        return {
            "executes": True,
            "job_id": job_id,
            "status": "running",
            "command": command,
            "progress_percent": 0.0,
            "current_phase": None,
            "current_substep": None,
            "completed_substeps": [],
            "owner_id": owner_id,
        }

    def get(self, job_id: str) -> dict[str, Any]:
        return {
            "job_id": job_id,
            "status": "completed",
            "returncode": 0,
            "command": self.started_commands[-1] if self.started_commands else [],
            "stdout_tail": "",
            "stderr_tail": "",
            "progress_percent": 100.0,
            "current_phase": None,
            "current_substep": None,
            "completed_substeps": [],
            "owner_id": self.owner_id,
        }

    def get_owned(
        self,
        job_id: str,
        *,
        expected_owner_id: str,
    ) -> dict[str, Any]:
        payload = self.get(job_id)
        if payload.get("owner_id") != expected_owner_id:
            raise ScanJobOwnershipError("scan job owner identity mismatch")
        return payload

    def stop(self, job_id: str) -> dict[str, Any]:
        self.stopped.append(job_id)
        payload = self.get(job_id)
        payload["status"] = "stopped"
        return payload

    def stop_owned(
        self,
        job_id: str,
        *,
        expected_owner_id: str,
    ) -> dict[str, Any]:
        self.get_owned(job_id, expected_owner_id=expected_owner_id)
        return self.stop(job_id)


_SCAN_BODY = {
    "last_name": "Test",
    "first_name": "Klaus",
    "birth_date": "09041966",
    "birth_place": "Augsburg",
    "focus": "Bronchien",
    "scan_profile_pool_fingerprint": current_scan_profile_pool_fingerprint(3),
    "consent_local": True,
    "consent_safety": True,
}


def _owner_scope(tenant_id: str, operator_id: str) -> str:
    canonical = json.dumps(
        [tenant_id, operator_id],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return "owner-v1-" + hashlib.sha256(canonical).hexdigest()


_UNTRUSTED_OWNER_CASES = ("foreign", "blank", "bare-legacy")


class _BoundaryProcess:
    pid = 43210

    def __init__(self) -> None:
        self.returncode: int | None = None

    def poll(self) -> int | None:
        return self.returncode

    def wait(self, timeout: int) -> int:
        return int(self.returncode or 0)


def _owner_for_case(owner_case: str, tenant_id: str, operator_id: str) -> str:
    if owner_case == "foreign":
        return _owner_scope("foreign-tenant", operator_id)
    if owner_case == "blank":
        return "   "
    if owner_case == "bare-legacy":
        return operator_id
    if owner_case == "owned":
        return _owner_scope(tenant_id, operator_id)
    raise AssertionError(f"unknown owner case: {owner_case}")


def _real_unreleased_job_app(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    owner_case: str,
) -> SimpleNamespace:
    tenant_id = "boundary-tenant"
    operator_id = "boundary-operator"
    expected_owner = _owner_scope(tenant_id, operator_id)
    owner_id = _owner_for_case(owner_case, tenant_id, operator_id)

    monkeypatch.setenv("MORPHIC_TENANT_ID", tenant_id)
    monkeypatch.setenv("MORPHIC_OPERATOR_ID", operator_id)
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    process = _BoundaryProcess()
    job_id = "scan-op-owner-boundary-1234"
    stdout_path = service._stdout_path(job_id)
    stderr_path = service._stderr_path(job_id)
    stdout_path.write_text("", encoding="utf-8")
    stderr_path.write_text("", encoding="utf-8")
    job = _LocalScanJob(
        job_id=job_id,
        command=["python", "-m", "apps.cli.main", "scan", "top3-scan"],
        process=process,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        created_at="2026-07-23T12:00:00+00:00",
        updated_at="2026-07-23T12:00:00+00:00",
        owner_id=owner_id,
        process_create_time=1.0,
        process_group_id=process.pid,
        process_group_token="a" * 32,
        start_released=False,
    )
    service._jobs[job_id] = job
    service._persist_job(job)
    state_path = service._state_path(job_id)
    release_path = service._start_release_path(job_id, job.process_group_token)
    started_path = service._start_started_path(job_id, job.process_group_token)
    converge_calls: list[str] = []
    original_durable_write = scan_jobs_module.durable_write_bytes

    def publish_gate_start(path: Path, data: bytes) -> None:
        original_durable_write(path, data)
        if path == release_path:
            started_path.write_text(str(process.pid), encoding="ascii")

    def converge(active_job: _LocalScanJob) -> None:
        converge_calls.append(active_job.job_id)
        process.returncode = -15

    monkeypatch.setattr(scan_jobs_module, "_job_runtime_active", lambda _job: True)
    monkeypatch.setattr(scan_jobs_module, "_windows_job_active", lambda _job: True)
    monkeypatch.setattr(scan_jobs_module, "_process_group_alive", lambda *_args: True)
    monkeypatch.setattr(
        scan_jobs_module,
        "_strict_process_identity_matches",
        lambda *_args: True,
    )
    monkeypatch.setattr(scan_jobs_module, "_converge_windows_authority", converge)
    monkeypatch.setattr(scan_jobs_module, "_converge_posix_authority", converge)
    monkeypatch.setattr(scan_jobs_module, "durable_write_bytes", publish_gate_start)
    app = create_app(scan_jobs=service, runtime_dir=tmp_path / "runtime")
    app.state.workbench_store.ensure_run_trace(job_id, {"status": "running"})
    return SimpleNamespace(
        app=app,
        service=service,
        job=job,
        job_id=job_id,
        process=process,
        expected_owner=expected_owner,
        state_path=state_path,
        state_bytes=state_path.read_bytes(),
        release_path=release_path,
        started_path=started_path,
        converge_calls=converge_calls,
    )


def _assert_unreleased_owner_rejection_was_side_effect_free(
    case: SimpleNamespace,
) -> None:
    assert case.state_path.read_bytes() == case.state_bytes
    assert not case.release_path.exists()
    assert not case.started_path.exists()
    assert case.process.returncode is None
    assert case.job.start_released is False
    assert case.converge_calls == []


def _reject_observe_owned_side_effects(
    case: SimpleNamespace,
    monkeypatch: pytest.MonkeyPatch,
) -> list[str]:
    calls: list[str] = []

    def reject(name: str):
        def rejected(*_args: Any, **_kwargs: Any) -> None:
            calls.append(name)
            raise AssertionError(f"observe_owned called {name}")

        return rejected

    for name in (
        "_recover_jobs",
        "_snapshot",
        "_persist_job",
        "_release_registered_start",
    ):
        monkeypatch.setattr(case.service, name, reject(name))
    return calls


def test_observe_owned_reads_real_unreleased_job_without_productive_helpers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _real_unreleased_job_app(tmp_path, monkeypatch, "owned")
    calls = _reject_observe_owned_side_effects(case, monkeypatch)

    observed = case.service.observe_owned(
        case.job_id,
        expected_owner_id=case.expected_owner,
    )

    assert observed == {"job_id": case.job_id, "status": "starting"}
    assert calls == []
    _assert_unreleased_owner_rejection_was_side_effect_free(case)


def test_observe_owned_rejects_real_foreign_owner_before_authority_probe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _real_unreleased_job_app(tmp_path, monkeypatch, "foreign")
    calls = _reject_observe_owned_side_effects(case, monkeypatch)
    authority_calls: list[str] = []

    def reject_authority_probe(_job: _LocalScanJob) -> bool:
        authority_calls.append("probe")
        raise AssertionError("foreign owner reached process authority")

    monkeypatch.setattr(scan_jobs_module, "_job_runtime_active", reject_authority_probe)

    with pytest.raises(ScanJobOwnershipError):
        case.service.observe_owned(
            case.job_id,
            expected_owner_id=case.expected_owner,
        )

    assert calls == []
    assert authority_calls == []
    _assert_unreleased_owner_rejection_was_side_effect_free(case)


@pytest.mark.parametrize(
    "corruption",
    ["invalid-json", "process-token", "authority-namespace"],
)
def test_observe_owned_normalizes_real_corrupt_state_without_mutation_or_release(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    corruption: str,
) -> None:
    case = _real_unreleased_job_app(tmp_path, monkeypatch, "owned")
    if corruption == "invalid-json":
        corrupt_bytes = b"{private-corrupt-state"
    else:
        payload = json.loads(case.state_path.read_text(encoding="utf-8"))
        if corruption == "process-token":
            payload["process_group_token"] = ["private-corrupt-token"]
        else:
            payload["authority_namespace"] = "private-corrupt-namespace"
        corrupt_bytes = json.dumps(payload).encode("utf-8")
    case.state_path.write_bytes(corrupt_bytes)
    calls = _reject_observe_owned_side_effects(case, monkeypatch)

    with pytest.raises(ProcessAuthorityAmbiguousError):
        case.service.observe_owned(
            case.job_id,
            expected_owner_id=case.expected_owner,
        )

    assert case.state_path.read_bytes() == corrupt_bytes
    assert not case.release_path.exists()
    assert not case.started_path.exists()
    assert case.job.start_released is False
    assert case.process.returncode is None
    assert calls == []


def _persist_recovery_record(
    tmp_path: Path,
    owner_case: str,
) -> SimpleNamespace:
    tenant_id = "recovery-tenant"
    operator_id = "recovery-operator"
    expected_owner = _owner_scope(tenant_id, operator_id)
    root = tmp_path / "recovery-jobs"
    writer = LocalScanJobService(root, cwd=tmp_path)
    process = _BoundaryProcess()
    job_id = "scan-op-recovery-owner-1234"
    stdout_path = writer._stdout_path(job_id)
    stderr_path = writer._stderr_path(job_id)
    stdout_path.write_text("", encoding="utf-8")
    stderr_path.write_text("", encoding="utf-8")
    job = _LocalScanJob(
        job_id=job_id,
        command=["python", "-m", "apps.cli.main", "scan", "top3-scan"],
        process=process,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        created_at="2026-07-23T13:00:00+00:00",
        updated_at="2026-07-23T13:00:00+00:00",
        owner_id=_owner_for_case(owner_case, tenant_id, operator_id),
        process_create_time=1.0,
        process_group_id=process.pid,
        process_group_token="b" * 32,
        start_released=False,
    )
    writer._jobs[job_id] = job
    writer._persist_job(job)
    state_path = writer._state_path(job_id)
    return SimpleNamespace(
        root=root,
        writer=writer,
        job=job,
        job_id=job_id,
        process=process,
        expected_owner=expected_owner,
        state_path=state_path,
        state_bytes=state_path.read_bytes(),
        release_path=writer._start_release_path(job_id, job.process_group_token),
        started_path=writer._start_started_path(job_id, job.process_group_token),
    )


def _force_recovery_authority_probe_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        scan_jobs_module,
        "_job_runtime_active",
        lambda _job: (_ for _ in ()).throw(OSError("authority probe failed")),
    )


def _assert_recovery_bytes_and_authority_are_unchanged(
    case: SimpleNamespace,
) -> None:
    assert case.state_path.read_bytes() == case.state_bytes
    assert not case.release_path.exists()
    assert not case.started_path.exists()
    assert case.process.returncode is None
    assert json.loads(case.state_path.read_text(encoding="utf-8"))[
        "forced_status"
    ] is None


@pytest.mark.parametrize("owner_case", _UNTRUSTED_OWNER_CASES)
def test_startup_recovery_probe_failure_is_read_only_for_untrusted_owner(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    owner_case: str,
) -> None:
    case = _persist_recovery_record(tmp_path, owner_case)
    _force_recovery_authority_probe_failure(monkeypatch)

    recovered = LocalScanJobService(case.root, cwd=tmp_path)

    assert recovered._jobs[case.job_id].forced_status == "authority_ambiguous"
    _assert_recovery_bytes_and_authority_are_unchanged(case)


@pytest.mark.parametrize("owner_case", _UNTRUSTED_OWNER_CASES)
@pytest.mark.parametrize("operation", ["get_owned", "stop_owned"])
def test_uncached_owned_recovery_rejects_before_authority_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    owner_case: str,
    operation: str,
) -> None:
    root = tmp_path / "recovery-jobs"
    observer = LocalScanJobService(root, cwd=tmp_path)
    case = _persist_recovery_record(tmp_path, owner_case)
    _force_recovery_authority_probe_failure(monkeypatch)

    with pytest.raises(ScanJobOwnershipError):
        getattr(observer, operation)(
            case.job_id,
            expected_owner_id=case.expected_owner,
        )

    assert observer._jobs[case.job_id].forced_status == "authority_ambiguous"
    _assert_recovery_bytes_and_authority_are_unchanged(case)


@pytest.mark.parametrize("owner_case", _UNTRUSTED_OWNER_CASES)
def test_uncached_replay_recovery_rejects_before_authority_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    owner_case: str,
) -> None:
    root = tmp_path / "recovery-jobs"
    observer = LocalScanJobService(root, cwd=tmp_path)
    case = _persist_recovery_record(tmp_path, owner_case)
    _force_recovery_authority_probe_failure(monkeypatch)

    with pytest.raises(ScanJobReplayOwnershipError):
        observer.get_for_replay(
            case.job_id,
            expected_command=case.job.command,
            expected_owner_id=case.expected_owner,
        )

    assert observer._jobs[case.job_id].forced_status == "authority_ambiguous"
    _assert_recovery_bytes_and_authority_are_unchanged(case)


def test_startup_recovery_publishes_ambiguity_only_after_exact_owner_auth(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _persist_recovery_record(tmp_path, "owned")
    _force_recovery_authority_probe_failure(monkeypatch)
    recovered = LocalScanJobService(case.root, cwd=tmp_path)

    _assert_recovery_bytes_and_authority_are_unchanged(case)
    snapshot = recovered.get_owned(
        case.job_id,
        expected_owner_id=case.expected_owner,
    )

    assert snapshot["status"] == "authority_ambiguous"
    assert json.loads(case.state_path.read_text(encoding="utf-8"))[
        "forced_status"
    ] == "authority_ambiguous"


def test_replay_recovery_publishes_ambiguity_only_after_exact_owner_auth(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _persist_recovery_record(tmp_path, "owned")
    _force_recovery_authority_probe_failure(monkeypatch)
    recovered = LocalScanJobService(case.root, cwd=tmp_path)

    _assert_recovery_bytes_and_authority_are_unchanged(case)
    snapshot = recovered.get_for_replay(
        case.job_id,
        expected_command=case.job.command,
        expected_owner_id=case.expected_owner,
    )

    assert snapshot["status"] == "authority_ambiguous"
    assert json.loads(case.state_path.read_text(encoding="utf-8"))[
        "forced_status"
    ] == "authority_ambiguous"


def test_unowned_get_preserves_recovered_ambiguity_without_publishing_it(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _persist_recovery_record(tmp_path, "bare-legacy")
    _force_recovery_authority_probe_failure(monkeypatch)
    recovered = LocalScanJobService(case.root, cwd=tmp_path)

    snapshot = recovered.get(case.job_id)

    assert snapshot["status"] == "authority_ambiguous"
    _assert_recovery_bytes_and_authority_are_unchanged(case)


@pytest.mark.parametrize("owner_case", _UNTRUSTED_OWNER_CASES)
@pytest.mark.parametrize(
    ("method", "path_template"),
    [
        pytest.param("GET", "/api/scan/jobs/{job_id}", id="status"),
        pytest.param("GET", "/api/scan/jobs/{job_id}/results", id="results"),
        pytest.param("POST", "/api/scan/jobs/{job_id}/sync-trace", id="sync-trace"),
        pytest.param("GET", "/api/workbench/run-trace/{job_id}", id="run-trace"),
        pytest.param("POST", "/api/scan/jobs/{job_id}/stop", id="stop"),
    ],
)
def test_unreleased_owner_rejection_is_side_effect_free_for_web_routes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    owner_case: str,
    method: str,
    path_template: str,
) -> None:
    case = _real_unreleased_job_app(tmp_path, monkeypatch, owner_case)

    response = request(
        case.app,
        method,
        path_template.format(job_id=case.job_id),
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "resource access forbidden"}
    _assert_unreleased_owner_rejection_was_side_effect_free(case)


def test_owner_change_before_stop_cannot_cross_atomic_store_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _real_unreleased_job_app(tmp_path, monkeypatch, "foreign")

    def stale_owned_snapshot(job_id: str) -> dict[str, object]:
        return {
            "job_id": job_id,
            "owner_id": case.expected_owner,
            "status": "running",
        }

    monkeypatch.setattr(case.service, "get", stale_owned_snapshot)

    response = request(case.app, "POST", f"/api/scan/jobs/{case.job_id}/stop")

    assert response.status_code == 403
    assert response.json() == {"detail": "resource access forbidden"}
    _assert_unreleased_owner_rejection_was_side_effect_free(case)


@pytest.mark.parametrize("owner_id", [None, "", "   ", "some-other-operator"])
def test_scan_job_without_owner_id_is_fail_closed(
    tmp_path: Path, monkeypatch, owner_id: str | None
) -> None:
    """Legacy-Jobs ohne belegten Owner duerfen nicht operatoruebergreifend lecken."""
    monkeypatch.setenv("MORPHIC_OPERATOR_ID", "some-other-operator")
    app = create_app(scan_jobs=OwnershipScanJobs(owner_id=owner_id), runtime_dir=tmp_path)
    results = request(app, "GET", "/api/scan/jobs/job-own/results")
    status = request(app, "GET", "/api/scan/jobs/job-own")
    stopped = request(app, "POST", "/api/scan/jobs/job-own/stop")
    synced = request(app, "POST", "/api/scan/jobs/job-own/sync-trace")

    assert results.status_code == 403
    assert results.json() == {"detail": "resource access forbidden"}
    assert status.status_code == 403
    assert status.json() == {"detail": "resource access forbidden"}
    assert stopped.status_code == 403
    assert stopped.json() == {"detail": "resource access forbidden"}
    assert synced.status_code == 403
    assert synced.json() == {"detail": "resource access forbidden"}


def test_scan_job_start_records_owner_id(tmp_path: Path, monkeypatch) -> None:
    """Beim Starten eines Scan-Jobs wird der aktuelle Operator-Kontext als owner_id aufgezeichnet."""
    monkeypatch.setenv("MORPHIC_OPERATOR_ID", "operator-test-123")
    monkeypatch.setenv("MORPHIC_TENANT_ID", "tenant-test-456")
    scan_jobs = OwnershipScanJobs()
    app = create_app(scan_jobs=scan_jobs, runtime_dir=tmp_path)
    resp = request(app, "POST", "/api/scan/jobs", json_body=_SCAN_BODY)

    assert resp.status_code == 200
    assert resp.json().get("job_id", "").startswith("scan-op-")
    for forbidden in (
        "command", "focus", "image_path", "notes", "parallel_export_plan",
        "parallel_export_client_id", "launcher",
    ):
        assert forbidden not in resp.json()
    assert scan_jobs.owner_id == _owner_scope(
        "tenant-test-456",
        "operator-test-123",
    )


def test_scan_job_results_forbidden_for_foreign_owner(tmp_path: Path, monkeypatch) -> None:
    """Ein Job mit owner_id='operator-A' darf nicht von 'operator-B' abgerufen werden."""
    monkeypatch.setenv("MORPHIC_OPERATOR_ID", "operator-A")
    scan_jobs = OwnershipScanJobs()
    app = create_app(scan_jobs=scan_jobs, runtime_dir=tmp_path)
    started = request(app, "POST", "/api/scan/jobs", json_body=_SCAN_BODY)
    job_id = started.json()["job_id"]
    scan_jobs.owner_id = _owner_scope(
        app.state.operator_context.tenant_id,
        "operator-B",
    )

    resp = request(app, "GET", f"/api/scan/jobs/{job_id}/results")
    status = request(app, "GET", f"/api/scan/jobs/{job_id}")
    stopped = request(app, "POST", f"/api/scan/jobs/{job_id}/stop")
    synced = request(app, "POST", f"/api/scan/jobs/{job_id}/sync-trace")

    assert resp.status_code == 403, f"Foreign owner should be forbidden, got {resp.status_code}"
    assert resp.json() == {"detail": "resource access forbidden"}
    assert status.status_code == 403
    assert status.json() == {"detail": "resource access forbidden"}
    assert stopped.status_code == 403
    assert stopped.json() == {"detail": "resource access forbidden"}
    assert synced.status_code == 403
    assert synced.json() == {"detail": "resource access forbidden"}
    assert scan_jobs.stopped == []


def test_scan_job_results_allowed_for_matching_owner(tmp_path: Path, monkeypatch) -> None:
    """Ein Job mit owner_id='operator-A' darf von 'operator-A' abgerufen werden."""
    monkeypatch.setenv("MORPHIC_OPERATOR_ID", "operator-A")
    scan_jobs = OwnershipScanJobs()
    app = create_app(scan_jobs=scan_jobs, runtime_dir=tmp_path)
    started = request(app, "POST", "/api/scan/jobs", json_body=_SCAN_BODY)
    job_id = started.json()["job_id"]
    assert scan_jobs.owner_id == _owner_scope(
        app.state.operator_context.tenant_id,
        "operator-A",
    )
    app.state.workbench_store.ensure_run_trace(job_id, {"status": "running"})
    resp = request(app, "GET", f"/api/scan/jobs/{job_id}/results")
    status = request(app, "GET", f"/api/scan/jobs/{job_id}")
    stopped = request(app, "POST", f"/api/scan/jobs/{job_id}/stop")
    synced = request(app, "POST", f"/api/scan/jobs/{job_id}/sync-trace")

    assert resp.status_code == 200
    assert resp.json() == {
        "job_id": job_id,
        "status": "completed",
        "top_profiles": [],
        "top_resonances": [],
        "export_paths": {},
        "report_session_id": None,
    }
    assert status.status_code == 200
    assert status.json() == {
        "job_id": job_id,
        "status": "completed",
        "returncode": 0,
        "progress_percent": 100.0,
        "current_phase": None,
        "current_substep": None,
        "completed_substeps": [],
        "diagnostics": [],
    }
    assert stopped.status_code == 200
    assert stopped.json() == {
        "job_id": job_id,
        "status": "stopped",
        "returncode": 0,
        "progress_percent": 100.0,
        "current_phase": None,
        "current_substep": None,
        "completed_substeps": [],
        "diagnostics": [],
    }
    assert synced.status_code == 200
    assert synced.json() == {
        "status": "completed",
        "returncode": 0,
        "progress_percent": 100.0,
        "current_phase": None,
        "current_substep": None,
    }


def test_same_operator_in_another_tenant_cannot_access_any_scan_surface(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jobs = OwnershipScanJobs()
    monkeypatch.setenv("MORPHIC_OPERATOR_ID", "shared-operator")
    monkeypatch.setenv("MORPHIC_TENANT_ID", "tenant-a")
    app_a = create_app(scan_jobs=jobs, runtime_dir=tmp_path)
    started = request(app_a, "POST", "/api/scan/jobs", json_body=_SCAN_BODY)
    job_id = started.json()["job_id"]
    assert jobs.owner_id == _owner_scope("tenant-a", "shared-operator")

    monkeypatch.setenv("MORPHIC_TENANT_ID", "tenant-b")
    app_b = create_app(scan_jobs=jobs, runtime_dir=tmp_path)
    responses = [
        request(app_b, "GET", f"/api/scan/jobs/{job_id}"),
        request(app_b, "GET", f"/api/scan/jobs/{job_id}/results"),
        request(app_b, "POST", f"/api/scan/jobs/{job_id}/sync-trace"),
        request(app_b, "GET", f"/api/workbench/run-trace/{job_id}"),
        request(app_b, "POST", f"/api/scan/jobs/{job_id}/stop"),
    ]

    assert [response.status_code for response in responses] == [403] * 5
    assert all(
        response.json() == {"detail": "resource access forbidden"}
        for response in responses
    )
    assert jobs.stopped == []


def test_scan_status_and_results_require_configured_api_key(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MORPHIC_API_KEY", "configured-secret")
    app = create_app(scan_jobs=OwnershipScanJobs(owner_id=None), runtime_dir=tmp_path)

    assert request(app, "GET", "/api/scan/jobs/job-own").status_code == 401
    assert request(app, "GET", "/api/scan/jobs/job-own/results").status_code == 401
    assert request(app, "POST", "/api/scan/jobs/job-own/stop").status_code == 401
