from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta
import os
from pathlib import Path
import sys
from contextlib import contextmanager

import pytest

from apps.web.main import create_app
from apps.web.harmonization import WorkerHarmonizationService
from apps.web import scan_jobs as scan_jobs_module
from apps.web.scan_jobs import LocalScanJobService
from core.compliance.operator_context import OperatorContext, operator_owner_scope
from services import harmonization_worker as worker
from services.harmonization_worker import HarmonizationJob
from tests.test_web_authority_ids import INVALID_AUTHORITY_IDS


class FakeAuthorityService:
    def __init__(self, snapshots=None, failure: BaseException | None = None) -> None:
        self.snapshots = dict(snapshots or {})
        self.failure = failure
        self.get_calls: list[str] = []
        self.started: list[dict[str, object]] = []

    def get(self, job_id: str) -> dict[str, object]:
        self.get_calls.append(job_id)
        if self.failure is not None:
            raise self.failure
        return dict(self.snapshots[job_id])

    def observe(self, job_id: str) -> dict[str, object]:
        return self.get(job_id)

    def start(self, command, **kwargs):
        self.started.append({"command": list(command), **kwargs})
        snapshot = {"job_id": kwargs["job_id"], "status": "running"}
        self.snapshots[kwargs["job_id"]] = snapshot
        return dict(snapshot)

    def get_for_replay(
        self,
        job_id: str,
        *,
        expected_command: list[str],
        expected_owner_id: str | None,
    ) -> dict[str, object]:
        if job_id not in self.snapshots:
            raise KeyError(job_id)
        return self.get(job_id)


def _expired_job(job_id: str, authority_job_id: str, **overrides) -> HarmonizationJob:
    values = {
        "job_id": job_id,
        "target_frequency": 432.0,
        "duration_minutes": 1,
        "intention": "harmonization",
        "hardware_config": {"use_cpu": False},
        "status": "running",
        "start_time": (datetime.now() - timedelta(minutes=10)).isoformat(),
        "heartbeat_at": (datetime.now() - timedelta(minutes=10)).isoformat(),
        "current_phase": "running",
        "authority_job_id": authority_job_id,
    }
    values.update(overrides)
    return HarmonizationJob(**values)


@pytest.mark.parametrize("invalid_id", INVALID_AUTHORITY_IDS)
def test_harmonization_ids_reject_before_path_lock_or_process_authority(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    invalid_id: str,
) -> None:
    lock_calls: list[str] = []
    process_calls: list[str] = []
    path_accesses: list[str] = []

    class GuardRoot:
        def __truediv__(self, name: str):
            path_accesses.append(name)
            raise AssertionError("invalid harmonization ID reached a filesystem path")

    monkeypatch.setattr(worker, "JOBS_DIR", GuardRoot())
    monkeypatch.setattr(worker, "EVENTS_DIR", GuardRoot())

    @contextmanager
    def unexpected_lock(job_id: str):
        lock_calls.append(job_id)
        raise AssertionError("invalid harmonization ID reached a lock")
        yield  # pragma: no cover

    monkeypatch.setattr(worker, "_job_lock", unexpected_lock)
    monkeypatch.setattr(
        worker,
        "_process_authority_service",
        lambda: process_calls.append("process") or FakeAuthorityService(),
    )
    job = HarmonizationJob(
        job_id=invalid_id,
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={},
    )

    with pytest.raises(ValueError):
        worker._stop_marker_path(invalid_id)
    with pytest.raises((ValueError, RuntimeError)):
        HarmonizationJob.load(invalid_id)
    with pytest.raises((ValueError, RuntimeError)):
        job.save()
    with pytest.raises((ValueError, RuntimeError)):
        job.delete()
    with pytest.raises(ValueError):
        worker.stop_harmonization_job(invalid_id)
    with pytest.raises(ValueError):
        worker.run_harmonization_worker(invalid_id)

    assert lock_calls == []
    assert path_accesses == []
    assert process_calls == []
    assert not (tmp_path / "outside.json").exists()
    assert not (tmp_path / "jobs").exists()


@pytest.mark.parametrize(
    ("authority_job_id", "error"),
    [
        pytest.param("job-valid", "id is invalid", id="invalid-authority-kind"),
        pytest.param(
            "harm-auth-foreign",
            "identity mismatch",
            id="foreign-authority-identity",
        ),
    ],
)
def test_harmonization_save_rejects_invalid_authority_before_lock_or_path(
    monkeypatch: pytest.MonkeyPatch,
    authority_job_id: str,
    error: str,
) -> None:
    lock_calls: list[str] = []
    path_calls: list[str] = []

    class GuardRoot:
        def __truediv__(self, name: str):
            path_calls.append(name)
            raise AssertionError("invalid process authority reached a path")

    @contextmanager
    def unexpected_lock(job_id: str):
        lock_calls.append(job_id)
        raise AssertionError("invalid process authority reached a lock")
        yield  # pragma: no cover

    monkeypatch.setattr(worker, "JOBS_DIR", GuardRoot())
    monkeypatch.setattr(worker, "EVENTS_DIR", GuardRoot())
    monkeypatch.setattr(worker, "_job_lock", unexpected_lock)
    job = HarmonizationJob(
        job_id="harm_save_guard",
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={},
        authority_job_id=authority_job_id,
    )

    with pytest.raises(ValueError, match=error):
        job.save()

    assert lock_calls == []
    assert path_calls == []


def test_explicit_empty_harmonization_creation_id_rejects_before_side_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jobs_root = tmp_path / "jobs"
    lock_calls: list[str] = []
    authority_calls: list[str] = []

    @contextmanager
    def unexpected_registry_lock():
        lock_calls.append("registry")
        raise AssertionError("empty creation ID reached the active registry")
        yield  # pragma: no cover

    monkeypatch.setattr(worker, "JOBS_DIR", jobs_root)
    monkeypatch.setattr(worker, "EVENTS_DIR", jobs_root / "events")
    monkeypatch.setattr(worker, "_active_registry_lock", unexpected_registry_lock)
    monkeypatch.setattr(
        worker,
        "_process_authority_service",
        lambda: authority_calls.append("process") or FakeAuthorityService(),
    )

    with pytest.raises(ValueError):
        worker.start_harmonization_job(
            target_frequency=432.0,
            duration_minutes=21,
            hardware_config={"use_cpu": False},
            job_id="",
        )

    assert lock_calls == []
    assert authority_calls == []
    assert not jobs_root.exists()


def test_harmonization_service_rejects_first_oversized_creation_id_before_worker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    job_id = "harm_" + "a" * (119 - len("harm_"))
    worker_calls: list[str] = []

    monkeypatch.setattr(
        worker,
        "start_harmonization_job",
        lambda **kwargs: worker_calls.append(str(kwargs["job_id"])) or job_id,
    )
    monkeypatch.setattr(worker.HarmonizationJob, "load", lambda _job_id: None)

    with pytest.raises(ValueError):
        WorkerHarmonizationService().start(
            mode="harmonization",
            target_frequency=432.0,
            duration_minutes=21,
            intention="harmonization",
            hardware_config={"use_cpu": False},
            job_id=job_id,
        )

    assert worker_calls == []


def test_harmonization_worker_rejects_oversized_creation_before_side_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    job_id = "harm_" + "a" * (119 - len("harm_"))
    jobs_root = tmp_path / "jobs"
    authority_calls: list[str] = []
    monkeypatch.setattr(worker, "JOBS_DIR", jobs_root)
    monkeypatch.setattr(worker, "EVENTS_DIR", jobs_root / "events")
    monkeypatch.setattr(
        worker,
        "_process_authority_service",
        lambda: authority_calls.append("process") or FakeAuthorityService(),
    )

    with pytest.raises(ValueError):
        worker.start_harmonization_job(
            target_frequency=432.0,
            duration_minutes=21,
            hardware_config={"use_cpu": False},
            job_id=job_id,
        )

    assert authority_calls == []
    assert not jobs_root.exists()


def test_active_registry_uses_fixed_internal_lock_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    authority = FakeAuthorityService()
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)

    job_id = worker.start_harmonization_job(
        target_frequency=432.0,
        duration_minutes=1,
        hardware_config={"use_cpu": False},
        tenant_id="tenant-a",
        operator_id="operator-a",
        job_id="harm_registry",
    )

    assert job_id == "harm_registry"
    assert (tmp_path / ".__active_registry__.lock").exists()


@pytest.mark.parametrize("invalid_id", INVALID_AUTHORITY_IDS)
def test_harmonization_process_entry_rejects_invalid_argv_before_worker_lookup(
    monkeypatch: pytest.MonkeyPatch,
    invalid_id: str,
) -> None:
    from services import harmonization_process_entry

    calls: list[str] = []
    monkeypatch.setattr(sys, "argv", ["harmonization_process_entry", invalid_id])
    monkeypatch.setattr(
        worker,
        "run_harmonization_worker",
        lambda job_id: calls.append(job_id) or "completed",
    )
    monkeypatch.setattr(
        worker.HarmonizationJob,
        "load",
        lambda job_id: calls.append(job_id),
    )

    with pytest.raises(ValueError):
        harmonization_process_entry.main()
    assert calls == []


def test_process_entry_accepts_cooperative_stopped_with_active_record(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from services import harmonization_process_entry

    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_entry_cooperative_stop",
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
    )
    job.save()
    worker._atomic_write_text(
        worker._stop_marker_path(job.job_id),
        "2026-07-22T13:15:00",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["harmonization_process_entry", job.job_id],
    )

    exit_code = harmonization_process_entry.main()

    persisted = HarmonizationJob.load(job.job_id)
    assert exit_code == 0
    assert persisted is not None
    assert persisted.status == "pending"
    assert persisted.current_phase == "pending"
    assert persisted.end_time is None


def test_process_entry_rejects_unknown_worker_outcome(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from services import harmonization_process_entry

    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_entry_unknown_outcome",
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
    )
    job.save()
    monkeypatch.setattr(worker, "run_harmonization_worker", lambda job_id: "unknown")
    monkeypatch.setattr(
        sys,
        "argv",
        ["harmonization_process_entry", job.job_id],
    )

    assert harmonization_process_entry.main() == 1


def test_cooperative_stop_process_entry_completes_real_authority(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jobs_root = tmp_path / "harmonization-jobs"
    authority_root = jobs_root / ".process-authority"
    monkeypatch.setattr(worker, "JOBS_DIR", jobs_root)
    monkeypatch.setattr(worker, "EVENTS_DIR", jobs_root / "events")
    job_id = "harm_real_cooperative_stop"
    authority_job_id = f"harm-auth-{job_id}"
    job = HarmonizationJob(
        job_id=job_id,
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        authority_job_id=authority_job_id,
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    job.save()
    worker._atomic_write_text(
        worker._stop_marker_path(job_id),
        "2026-07-22T13:20:00",
    )
    authority = LocalScanJobService(
        authority_root,
        cwd=Path(worker.__file__).resolve().parents[1],
        authority_namespace="harmonization",
    )

    authority.start(
        [sys.executable, "-m", "services.harmonization_process_entry", job_id],
        owner_id="operator-a",
        env_overrides={"MORPHIC_HARMONIZATION_JOBS_DIR": str(jobs_root)},
        job_id=authority_job_id,
    )

    try:
        assert authority._jobs[authority_job_id].process.wait(timeout=10) == 0
        authority_snapshot = authority.get(authority_job_id)
        persisted = HarmonizationJob.load(job_id)
        assert authority_snapshot["status"] == "completed"
        assert persisted is not None
        assert persisted.status == "pending"
        assert persisted.current_phase == "pending"
        assert persisted.end_time is None
        assert worker._stop_marker_path(job_id).exists()
    finally:
        active = authority._jobs.get(authority_job_id)
        if active is not None and active.process.poll() is None:
            authority.stop(authority_job_id)


def test_worker_entry_rejects_persisted_authority_mismatch_before_job_lock(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jobs_root = tmp_path / "jobs"
    jobs_root.mkdir()
    monkeypatch.setattr(worker, "JOBS_DIR", jobs_root)
    monkeypatch.setattr(worker, "EVENTS_DIR", jobs_root / "events")
    job_id = "harm_worker_entry_guard"
    job = HarmonizationJob(
        job_id=job_id,
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={},
        authority_job_id=f"harm-auth-{job_id}",
    )
    payload = job.to_dict()
    payload["authority_job_id"] = "harm-auth-foreign"
    path = jobs_root / f"{job_id}.json"
    original = json.dumps(payload).encode("utf-8")
    path.write_bytes(original)
    process_calls: list[int] = []
    monkeypatch.setattr(
        worker.psutil,
        "Process",
        lambda pid: process_calls.append(pid) or pytest.fail(
            "corrupt worker entry reached process authority"
        ),
    )

    with pytest.raises(RuntimeError, match="record is unreadable"):
        worker.run_harmonization_worker(job_id)

    assert process_calls == []
    assert path.read_bytes() == original
    assert {entry.name for entry in jobs_root.iterdir()} == {f"{job_id}.json"}


@pytest.mark.parametrize("embedded_job_id", INVALID_AUTHORITY_IDS)
def test_harmonization_valid_filename_rejects_every_embedded_invalid_job_id(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    embedded_job_id: str,
) -> None:
    jobs_root = tmp_path / "jobs"
    jobs_root.mkdir()
    monkeypatch.setattr(worker, "JOBS_DIR", jobs_root)
    monkeypatch.setattr(worker, "EVENTS_DIR", jobs_root / "events")
    valid_job_id = "harm_container"
    job = HarmonizationJob(
        job_id=valid_job_id,
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={},
        status="completed",
        authority_job_id=f"harm-auth-{valid_job_id}",
    )
    payload = job.to_dict()
    payload["job_id"] = embedded_job_id
    path = jobs_root / f"{valid_job_id}.json"
    original = json.dumps(payload).encode("utf-8")
    path.write_bytes(original)
    process_calls: list[str] = []
    monkeypatch.setattr(
        worker,
        "_process_authority_service",
        lambda: process_calls.append("process"),
    )

    with pytest.raises(RuntimeError, match="record is unreadable"):
        WorkerHarmonizationService().get(valid_job_id)

    assert process_calls == []
    assert path.read_bytes() == original
    assert list(jobs_root.iterdir()) == [path]


@pytest.mark.parametrize(
    "authority_job_id",
    [*INVALID_AUTHORITY_IDS, "scan-valid", "harm-auth-other"],
)
def test_harmonization_load_rejects_corrupt_or_mismatched_authority_id(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    authority_job_id: str,
) -> None:
    jobs_root = tmp_path / "jobs"
    jobs_root.mkdir()
    monkeypatch.setattr(worker, "JOBS_DIR", jobs_root)
    monkeypatch.setattr(worker, "EVENTS_DIR", jobs_root / "events")
    job_id = "harm_authority_record"
    job = HarmonizationJob(
        job_id=job_id,
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={},
        status="completed",
        current_phase="completed",
        authority_job_id=authority_job_id,
    )
    path = jobs_root / f"{job_id}.json"
    original = json.dumps(job.to_dict()).encode("utf-8")
    path.write_bytes(original)
    process_calls: list[str] = []
    monkeypatch.setattr(
        worker,
        "_process_authority_service",
        lambda: process_calls.append("process"),
    )

    with pytest.raises(RuntimeError, match="record is unreadable"):
        WorkerHarmonizationService().get(job_id)

    assert process_calls == []
    assert path.read_bytes() == original
    assert list(jobs_root.glob("*.lock")) == []


def test_invalid_harmonization_ids_do_not_share_sanitized_authority_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jobs_root = tmp_path / "jobs"
    monkeypatch.setattr(worker, "JOBS_DIR", jobs_root)
    monkeypatch.setattr(worker, "EVENTS_DIR", jobs_root / "events")

    for invalid_id in ("name/child", "name\\child"):
        job = HarmonizationJob(
            job_id=invalid_id,
            target_frequency=432.0,
            duration_minutes=1,
            intention="harmonization",
            hardware_config={},
        )
        with pytest.raises(RuntimeError, match="record is unreadable"):
            job.save()

    assert not jobs_root.exists()


def test_recovery_uses_stable_tree_authority_not_worker_pid(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    stale = _expired_job("harm_stale", "harm-auth-harm_stale", worker_pid=991)
    alive = _expired_job("harm_alive", "harm-auth-harm_alive", worker_pid=992)
    stale.save()
    alive.save()
    authority = FakeAuthorityService(
        {
            "harm-auth-harm_stale": {"status": "completed"},
            "harm-auth-harm_alive": {"status": "running"},
        }
    )
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)

    recovered = worker.recover_interrupted_harmonization_jobs(lease_seconds=30)

    assert recovered == ["harm_stale"]
    assert HarmonizationJob.load("harm_stale").status == "interrupted"
    assert HarmonizationJob.load("harm_alive").status == "running"


def test_interrupted_reconciliation_writes_offset_compatible_terminal_time(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    start_time = "2026-07-22T12:00:00-04:00"
    job = _expired_job(
        "harm_offset_interrupted",
        "harm-auth-harm_offset_interrupted",
        start_time=start_time,
        heartbeat_at=start_time,
    )
    job.save()
    authority = FakeAuthorityService(
        {job.authority_job_id: {"status": "completed"}}
    )
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)

    reconciled = worker.reconcile_expired_harmonization_job_on_get(job.job_id)

    assert reconciled.status == "interrupted"
    assert reconciled.end_time is not None
    started = datetime.fromisoformat(start_time)
    ended = datetime.fromisoformat(reconciled.end_time)
    assert ended.utcoffset() == started.utcoffset()
    assert ended >= started


def test_recovery_treats_starting_process_authority_as_live(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = _expired_job("harm_starting", "harm-auth-harm_starting")
    job.save()
    authority = FakeAuthorityService(
        {"harm-auth-harm_starting": {"status": "starting"}}
    )
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)

    assert worker.recover_interrupted_harmonization_jobs(lease_seconds=30) == []
    persisted = HarmonizationJob.load(job.job_id)
    assert persisted is not None
    assert persisted.status == "running"
    assert persisted.forced_status is None


@pytest.mark.parametrize(
    ("authority_status", "expected_status"),
    [
        pytest.param("starting", "running", id="starting-remains-active"),
        pytest.param("running", "running", id="running-remains-active"),
        pytest.param("completed", "interrupted", id="completed-without-domain-commit"),
        pytest.param("failed", "interrupted", id="failed-without-domain-commit"),
        pytest.param("stopped", "interrupted", id="stopped-without-stop-marker"),
    ],
)
def test_ordinary_get_reconciles_expired_active_record_with_one_authority_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    authority_status: str,
    expected_status: str,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    requested = _expired_job(
        "harm_get_requested",
        "harm-auth-harm_get_requested",
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    unrelated = _expired_job(
        "harm_get_unrelated",
        "harm-auth-harm_get_unrelated",
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    requested.save()
    unrelated.save()
    authority = FakeAuthorityService(
        {
            requested.authority_job_id: {"status": authority_status},
            unrelated.authority_job_id: {"status": "completed"},
        }
    )
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)

    snapshot = WorkerHarmonizationService().get(requested.job_id)

    assert snapshot["status"] == expected_status
    assert authority.get_calls == [requested.authority_job_id]
    assert authority.started == []
    persisted = HarmonizationJob.load(requested.job_id)
    untouched = HarmonizationJob.load(unrelated.job_id)
    assert persisted is not None and persisted.status == expected_status
    assert untouched is not None and untouched.status == "running"


def test_ordinary_get_does_not_read_authority_for_live_lease(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = _expired_job(
        "harm_get_live_lease",
        "harm-auth-harm_get_live_lease",
        heartbeat_at=datetime.now().isoformat(),
    )
    job.save()
    authority = FakeAuthorityService(
        {job.authority_job_id: {"status": "completed"}}
    )
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)

    snapshot = WorkerHarmonizationService().get(job.job_id)

    assert snapshot["status"] == "running"
    assert authority.get_calls == []
    assert authority.started == []


def test_ordinary_get_persists_authority_uncertainty_without_starting_worker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = _expired_job(
        "harm_get_ambiguous",
        "harm-auth-harm_get_ambiguous",
    )
    job.save()
    authority = FakeAuthorityService(failure=PermissionError("authority unreadable"))
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)

    snapshot = WorkerHarmonizationService().get(job.job_id)

    assert snapshot["status"] == "authority_ambiguous"
    assert snapshot["phase"] == "authority_ambiguous"
    assert snapshot["manual_action_required"] is True
    assert authority.get_calls == [job.authority_job_id]
    assert authority.started == []
    persisted = HarmonizationJob.load(job.job_id)
    assert persisted is not None
    assert persisted.status == "authority_ambiguous"
    assert persisted.forced_status == "authority_ambiguous"


def test_ordinary_get_stop_marker_with_authority_failure_is_ambiguous(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = _expired_job(
        "harm_marker_authority_failure",
        "harm-auth-harm_marker_authority_failure",
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    job.save()
    worker._atomic_write_text(
        worker._stop_marker_path(job.job_id),
        "2026-07-22T12:00:00",
    )
    authority = FakeAuthorityService(failure=PermissionError("authority unreadable"))
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)

    snapshot = WorkerHarmonizationService().get_owned(
        job.job_id,
        tenant_id="tenant-a",
        operator_id="operator-a",
    )

    assert snapshot["status"] == "authority_ambiguous"
    assert snapshot["phase"] == "authority_ambiguous"
    assert snapshot["manual_action_required"] is True
    assert worker._stop_marker_path(job.job_id).exists()
    assert authority.get_calls == [job.authority_job_id]
    assert authority.started == []
    persisted = HarmonizationJob.load(job.job_id)
    assert persisted is not None
    assert persisted.status == "authority_ambiguous"
    assert persisted.forced_status == "authority_ambiguous"


def test_ordinary_get_never_reads_process_authority_while_job_lock_is_held(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = _expired_job(
        "harm_get_lock_order",
        "harm-auth-harm_get_lock_order",
    )
    job.save()
    original_lock = worker._job_lock
    lock_depth = 0

    @contextmanager
    def observed_lock(job_id: str):
        nonlocal lock_depth
        with original_lock(job_id):
            lock_depth += 1
            try:
                yield
            finally:
                lock_depth -= 1

    class Authority:
        def __init__(self) -> None:
            self.get_calls: list[str] = []
            self.start_calls: list[str] = []

        def get(self, authority_job_id: str) -> dict[str, object]:
            assert lock_depth == 0
            self.get_calls.append(authority_job_id)
            return {"job_id": authority_job_id, "status": "running"}

        def observe(self, authority_job_id: str) -> dict[str, object]:
            return self.get(authority_job_id)

        def start(self, *args, **kwargs):
            self.start_calls.append("start")
            raise AssertionError("ordinary get attempted worker start")

    authority = Authority()
    monkeypatch.setattr(worker, "_job_lock", observed_lock)
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)

    snapshot = WorkerHarmonizationService().get(job.job_id)

    assert snapshot["status"] == "running"
    assert authority.get_calls == [job.authority_job_id]
    assert authority.start_calls == []


def test_ordinary_get_observes_unreleased_real_authority_without_durable_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jobs_root = tmp_path / "harmonization-jobs"
    authority_root = jobs_root / ".process-authority"
    monkeypatch.setattr(worker, "JOBS_DIR", jobs_root)
    monkeypatch.setattr(worker, "EVENTS_DIR", jobs_root / "events")
    authority = LocalScanJobService(
        authority_root,
        cwd=tmp_path,
        authority_namespace="harmonization",
    )
    job_id = "harm_unreleased_observe"
    authority_job_id = f"harm-auth-{job_id}"
    token = "a" * 32

    class WaitingProcess:
        pid = os.getpid()

        def poll(self) -> None:
            return None

    process = WaitingProcess()
    stdout_path = authority._stdout_path(authority_job_id)
    stderr_path = authority._stderr_path(authority_job_id)
    stdout_path.write_bytes(b"")
    stderr_path.write_bytes(b"")
    authority_job = scan_jobs_module._LocalScanJob(
        job_id=authority_job_id,
        command=[sys.executable, "-m", "services.harmonization_process_entry", job_id],
        process=process,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        created_at="2026-07-22T12:00:00+00:00",
        updated_at="2026-07-22T12:00:00+00:00",
        owner_id="operator-a",
        process_create_time=float(worker.psutil.Process(process.pid).create_time()),
        process_group_id=process.pid,
        process_group_token=token,
        start_released=False,
        authority_namespace="harmonization",
    )
    authority._jobs[authority_job_id] = authority_job
    authority._persist_job(authority_job)
    lock_path = authority_root / f".{authority_job_id}.lock"
    assert lock_path.read_bytes() == b"0"
    release_path = authority._start_release_path(authority_job_id, token)
    started_path = authority._start_started_path(authority_job_id, token)
    result_path = authority._start_result_path(authority_job_id, token)
    monkeypatch.setattr(scan_jobs_module, "_job_runtime_active", lambda job: True)
    monkeypatch.setattr(scan_jobs_module, "_windows_job_active", lambda job: True)
    expired = (datetime.now() - timedelta(minutes=10)).isoformat()
    harmonization = _expired_job(
        job_id,
        authority_job_id,
        start_time=expired,
        heartbeat_at=expired,
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    harmonization.save()
    before = {
        path.name: path.read_bytes()
        for path in authority_root.iterdir()
        if path.is_file()
    }
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)

    snapshot = WorkerHarmonizationService().get(job_id)

    after = {
        path.name: path.read_bytes()
        for path in authority_root.iterdir()
        if path.is_file()
    }
    assert snapshot["status"] == "running"
    assert before == after
    assert not release_path.exists()
    assert not started_path.exists()
    assert not result_path.exists()
    assert authority_job.start_released is False


def test_recovery_persists_ambiguity_and_keeps_owner_reserved(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = _expired_job(
        "harm_ambiguous",
        "harm-auth-harm_ambiguous",
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    job.save()
    authority = FakeAuthorityService(failure=PermissionError("unreadable"))
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)

    assert worker.recover_interrupted_harmonization_jobs(lease_seconds=30) == [
        "harm_ambiguous"
    ]
    persisted = HarmonizationJob.load(job.job_id)
    assert persisted is not None
    assert persisted.status == "authority_ambiguous"
    assert persisted.forced_status == "authority_ambiguous"

    with pytest.raises(RuntimeError, match="active harmonization job"):
        worker.start_harmonization_job(
            target_frequency=432.0,
            duration_minutes=1,
            hardware_config={"use_cpu": False},
            tenant_id="tenant-a",
            operator_id="operator-a",
        )
    assert authority.started == []


def test_malformed_active_registry_fails_closed_before_new_worker_release(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    (tmp_path / "malformed.json").write_text("not-json", encoding="utf-8")
    authority = FakeAuthorityService()
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)

    with pytest.raises(RuntimeError, match="record is unreadable"):
        worker.start_harmonization_job(
            target_frequency=432.0,
            duration_minutes=1,
            hardware_config={"use_cpu": False},
            tenant_id="tenant-a",
            operator_id="operator-a",
        )

    assert authority.started == []


def test_ownerless_ambiguous_job_globally_reserves_start(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    ambiguous = worker.HarmonizationJob(
        job_id="ownerless-ambiguous",
        target_frequency=432.0,
        duration_minutes=1,
        intention="test",
        hardware_config={},
        status="authority_ambiguous",
        heartbeat_at=datetime.now().isoformat(),
        worker_pid=None,
        worker_create_time=None,
        authority_job_id="harm-auth-ownerless-ambiguous",
    )
    ambiguous.tenant_id = None
    ambiguous.operator_id = None
    ambiguous.forced_status = "authority_ambiguous"
    ambiguous.save()
    authority = FakeAuthorityService(
        {"harm-auth-ownerless-ambiguous": {"status": "authority_ambiguous"}}
    )
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)

    with pytest.raises(RuntimeError, match="authority is ambiguous"):
        worker.start_harmonization_job(
            target_frequency=432.0,
            duration_minutes=1,
            tenant_id="tenant-a",
            operator_id="operator-a",
        )

    assert authority.started == []


@pytest.mark.parametrize(
    ("malformed_owner", "expected_error"),
    [
        pytest.param("   ", "active harmonization job", id="blank-owner-reserves"),
        pytest.param(123, "record is unreadable", id="integer-owner-rejected"),
        pytest.param(
            {"legacy": "owner"},
            "record is unreadable",
            id="object-owner-rejected",
        ),
    ],
)
def test_malformed_owner_active_job_fails_closed_before_start(
    tmp_path, monkeypatch, malformed_owner, expected_error
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    active = worker.HarmonizationJob(
        job_id="whitespace-owner",
        target_frequency=432.0,
        duration_minutes=1,
        intention="test",
        hardware_config={},
        status="running",
        heartbeat_at=datetime.now().isoformat(),
        authority_job_id="harm-auth-whitespace-owner",
        tenant_id=malformed_owner,
        operator_id="operator-legacy",
    )
    (tmp_path / f"{active.job_id}.json").write_text(
        json.dumps(active.to_dict()),
        encoding="utf-8",
    )
    authority = FakeAuthorityService(
        {"harm-auth-whitespace-owner": {"status": "running"}}
    )
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)

    with pytest.raises(RuntimeError, match=expected_error):
        worker.start_harmonization_job(
            target_frequency=432.0,
            duration_minutes=1,
            tenant_id="tenant-a",
            operator_id="operator-a",
        )

    assert authority.started == []


def test_owner_reservation_releases_only_after_confirmed_tree_exit(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    stale = _expired_job(
        "harm_owner_stale",
        "harm-auth-harm_owner_stale",
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    stale.save()
    authority = FakeAuthorityService(
        {"harm-auth-harm_owner_stale": {"status": "completed"}}
    )
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)

    job_id = worker.start_harmonization_job(
        target_frequency=432.0,
        duration_minutes=1,
        hardware_config={"use_cpu": False},
        tenant_id="tenant-a",
        operator_id="operator-a",
    )

    assert job_id != stale.job_id
    assert HarmonizationJob.load(stale.job_id).status == "interrupted"
    assert len(authority.started) == 1
    started = authority.started[0]
    assert started["job_id"] == f"harm-auth-{job_id}"
    assert "MORPHIC_HARMONIZATION_JOBS_DIR" in started["env_overrides"]
    assert all("token" not in str(part).lower() for part in started["command"])


def test_harmonization_process_authority_uses_collision_safe_owner_scope(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jobs_root = tmp_path / "harmonization-jobs"
    monkeypatch.setattr(worker, "JOBS_DIR", jobs_root)
    monkeypatch.setattr(worker, "EVENTS_DIR", jobs_root / "events")

    class RecordingAuthority(FakeAuthorityService):
        def __init__(self) -> None:
            super().__init__()
            self.replay_expected_owner_ids: list[str | None] = []

        def get_for_replay(
            self,
            job_id: str,
            *,
            expected_command: list[str],
            expected_owner_id: str | None,
        ) -> dict[str, object]:
            self.replay_expected_owner_ids.append(expected_owner_id)
            raise KeyError(job_id)

    authority = RecordingAuthority()
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)
    expected_owner = operator_owner_scope(
        OperatorContext(operator_id="c", workspace_id="", tenant_id="a:b")
    )

    job_id = worker.start_harmonization_job(
        target_frequency=432.0,
        duration_minutes=1,
        hardware_config={"use_cpu": False},
        tenant_id="a:b",
        operator_id="c",
        job_id="harm_owner_scope",
    )

    assert job_id == "harm_owner_scope"
    assert authority.replay_expected_owner_ids == [expected_owner]
    assert authority.started[0]["owner_id"] == expected_owner


def test_worker_service_recovers_interrupted_jobs_at_composition_start(
    tmp_path,
    monkeypatch,
) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        worker,
        "recover_interrupted_harmonization_jobs",
        lambda: calls.append("recover") or [],
    )

    app = create_app(runtime_dir=tmp_path / "runtime")

    async def run_lifespan() -> None:
        async with app.router.lifespan_context(app):
            pass

    asyncio.run(run_lifespan())

    assert calls == ["recover"]


def test_process_entry_failure_publishes_failed_process_authority(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jobs_root = tmp_path / "harmonization-jobs"
    authority_root = jobs_root / ".process-authority"
    monkeypatch.setattr(worker, "JOBS_DIR", jobs_root)
    monkeypatch.setattr(worker, "EVENTS_DIR", jobs_root / "events")

    class RegistrationAuthority:
        def __init__(self) -> None:
            self.started: list[dict[str, object]] = []

        def get_for_replay(self, authority_job_id: str, **kwargs):
            raise KeyError(authority_job_id)

        def start(self, command, **kwargs):
            self.started.append({"command": list(command), **kwargs})
            return {"job_id": kwargs["job_id"], "status": "running"}

    registration = RegistrationAuthority()
    monkeypatch.setattr(
        worker,
        "_process_authority_service",
        lambda: registration,
    )
    job_id = worker.start_harmonization_job(
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        pulse_seconds=0.01,
        pause_seconds=0.01,
        duration_factor=1,
        solfeggio_base=432.0,
        report_id="report-a",
        workbench_mode="standard",
        tenant_id="tenant-a",
        operator_id="operator-a",
        job_id="harm_process_failure",
    )
    persisted_start = HarmonizationJob.load(job_id)
    assert persisted_start is not None
    worker.assert_harmonization_start_identity(
        persisted_start,
        job_id=job_id,
        authority_job_id=f"harm-auth-{job_id}",
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        pulse_seconds=0.01,
        pause_seconds=0.01,
        duration_factor=1,
        solfeggio_base=432.0,
        report_id="report-a",
        workbench_mode="standard",
        tenant_id="tenant-a",
        operator_id="operator-a",
    )

    injection_root = tmp_path / "runtime-injection"
    injection_root.mkdir()
    (injection_root / "sitecustomize.py").write_text(
        "from services import harmonization_worker\n"
        "def fail_runtime(config=None):\n"
        "    raise RuntimeError('injected worker runtime failure')\n"
        "harmonization_worker.capture_realtime_context = fail_runtime\n",
        encoding="utf-8",
    )
    authority = LocalScanJobService(
        authority_root,
        cwd=Path(__file__).resolve().parents[1],
        authority_namespace="harmonization",
    )
    authority_job_id = f"harm-auth-{job_id}"
    authority.start(
        [
            sys.executable,
            "-m",
            "services.harmonization_process_entry",
            job_id,
        ],
        owner_id="operator-a",
        env_overrides={
            "MORPHIC_HARMONIZATION_JOBS_DIR": str(jobs_root),
            "PYTHONPATH": os.pathsep.join(
                (str(injection_root), str(Path(worker.__file__).resolve().parents[1]))
            ),
        },
        job_id=authority_job_id,
    )

    try:
        authority._jobs[authority_job_id].process.wait(timeout=10)
        authority_snapshot = authority.get(authority_job_id)
        persisted = HarmonizationJob.load(job_id)

        assert persisted is not None
        assert persisted.status == "error"
        assert persisted.current_phase == "error"
        assert authority_snapshot["status"] == "failed"
    finally:
        active = authority._jobs.get(authority_job_id)
        if active is not None and active.process.poll() is None:
            authority.stop(authority_job_id)


def test_completed_process_entry_replays_after_original_authority_is_discarded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jobs_root = tmp_path / "harmonization-jobs"
    authority_root = jobs_root / ".process-authority"
    project_root = Path(__file__).resolve().parents[1]
    monkeypatch.setattr(worker, "JOBS_DIR", jobs_root)
    monkeypatch.setattr(worker, "EVENTS_DIR", jobs_root / "events")
    original_authority = LocalScanJobService(
        authority_root,
        cwd=project_root,
        authority_namespace="harmonization",
    )
    cleanup_authority: LocalScanJobService | None = original_authority
    monkeypatch.setattr(
        worker,
        "_process_authority_service",
        lambda: original_authority,
    )
    job_id = "harm_completed_replay"
    authority_job_id = f"harm-auth-{job_id}"
    hardware_config = {"use_cpu": False}
    process = None

    try:
        started_job_id = worker.start_harmonization_job(
            target_frequency=432.0,
            duration_minutes=0,
            intention="harmonization",
            hardware_config=hardware_config,
            pulse_seconds=0.01,
            pause_seconds=0.01,
            duration_factor=0,
            solfeggio_base=432.0,
            report_id="report-completed",
            workbench_mode="standard",
            tenant_id="tenant-a",
            operator_id="operator-a",
            job_id=job_id,
        )
        assert started_job_id == job_id
        process = original_authority._jobs[authority_job_id].process
        assert process.wait(timeout=10) == 0
        persisted = HarmonizationJob.load(job_id)
        assert persisted is not None
        assert persisted.status == "completed"
        assert persisted.current_phase == "completed"

        original_authority._jobs.clear()
        del process
        process = None
        del original_authority
        cleanup_authority = None
        fresh_authority = LocalScanJobService(
            authority_root,
            cwd=project_root,
            authority_namespace="harmonization",
        )
        monkeypatch.setattr(
            worker,
            "_process_authority_service",
            lambda: fresh_authority,
        )

        replayed = WorkerHarmonizationService().get_for_replay(
            job_id,
            mode="harmonization",
            target_frequency=432.0,
            duration_minutes=0,
            intention="harmonization",
            hardware_config=hardware_config,
            pulse_seconds=0.01,
            pause_seconds=0.01,
            duration_factor=0,
            solfeggio_base=432.0,
            report_id="report-completed",
            workbench_mode="standard",
            tenant_id="tenant-a",
            operator_id="operator-a",
        )
        authority_snapshot = fresh_authority.get(authority_job_id)

        assert replayed["status"] == "completed"
        assert replayed["phase"] == "completed"
        assert authority_snapshot["status"] == "completed"
        assert authority_snapshot["returncode"] == 0
    finally:
        if (
            process is not None
            and process.poll() is None
            and cleanup_authority is not None
        ):
            cleanup_authority.stop(authority_job_id)
