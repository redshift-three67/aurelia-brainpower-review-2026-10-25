from __future__ import annotations

from datetime import datetime, timedelta

from apps.web.harmonization import WorkerHarmonizationService
from services import harmonization_worker as worker
from services.harmonization_worker import HarmonizationJob


def test_worker_harmonization_snapshot_exposes_persisted_phase_and_lease(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_phase", target_frequency=432.0, duration_minutes=1,
        intention="harmonization", hardware_config={"use_cpu": False},
        status="interrupted", current_phase="interrupted", worker_pid=123,
        heartbeat_at="2026-07-11T10:00:00", end_time="2026-07-11T10:01:00",
        error_message="Worker lease ended after confirmed process-tree exit.",
        authority_job_id="harm-auth-harm_phase",
    )
    job.save()

    class TerminalAuthority:
        def get(self, authority_job_id: str) -> dict[str, object]:
            return {"job_id": authority_job_id, "status": "completed"}

    monkeypatch.setattr(worker, "_process_authority_service", TerminalAuthority)

    snapshot = WorkerHarmonizationService()._snapshot(job)

    assert snapshot["status"] == "interrupted"
    assert snapshot["phase"] == "interrupted"
    assert snapshot["lease"] == {"worker_pid": 123, "heartbeat_at": "2026-07-11T10:00:00"}
    assert snapshot["manual_action_required"] is True


def test_worker_get_snapshots_terminal_authority_as_interrupted_without_second_read(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    expired = (datetime.now() - timedelta(minutes=10)).isoformat()
    job = HarmonizationJob(
        job_id="harm_phase_reconcile",
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        status="running",
        start_time=expired,
        heartbeat_at=expired,
        current_phase="impulse",
        authority_job_id="harm-auth-harm_phase_reconcile",
    )
    job.save()

    class TerminalAuthority:
        def __init__(self) -> None:
            self.calls: list[str] = []

        def get(self, authority_job_id: str) -> dict[str, object]:
            self.calls.append(authority_job_id)
            return {"job_id": authority_job_id, "status": "completed"}

        def observe(self, authority_job_id: str) -> dict[str, object]:
            return self.get(authority_job_id)

        def start(self, *args, **kwargs):
            raise AssertionError("ordinary get attempted worker start")

    authority = TerminalAuthority()
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)

    snapshot = WorkerHarmonizationService().get(job.job_id)

    assert snapshot["status"] == "interrupted"
    assert snapshot["phase"] == "interrupted"
    assert snapshot["manual_action_required"] is True
    assert authority.calls == [job.authority_job_id]
