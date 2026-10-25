from __future__ import annotations

import json

import pytest

from services import harmonization_worker as worker
from services.harmonization_worker import HarmonizationJob


class _FakeAuthority:
    def __init__(self) -> None:
        self.started: list[str] = []
        self.replayed: list[str] = []
        self.commands: dict[str, list[str]] = {}
        self.owners: dict[str, str | None] = {}

    def start(self, command, **kwargs):
        self.started.append(kwargs["job_id"])
        self.commands[kwargs["job_id"]] = list(command)
        self.owners[kwargs["job_id"]] = kwargs.get("owner_id")
        return {"job_id": kwargs["job_id"], "status": "running"}

    def get(self, job_id: str):
        return {"job_id": job_id, "status": "running"}

    def get_for_replay(
        self,
        job_id: str,
        *,
        expected_command: list[str],
        expected_owner_id: str | None,
    ):
        self.replayed.append(job_id)
        if self.commands[job_id] != expected_command:
            raise RuntimeError("authority command mismatch")
        if self.owners[job_id] != expected_owner_id:
            raise RuntimeError("authority owner mismatch")
        return {"job_id": job_id, "status": "running"}


@pytest.fixture(autouse=True)
def _stable_authority(monkeypatch):
    authority = _FakeAuthority()
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)
    return authority


def test_start_harmonization_job_stores_pulse_pause_solfeggio_fields(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")

    job_id = worker.start_harmonization_job(
        target_frequency=432.0,
        duration_minutes=1,
        pulse_seconds=3,
        pause_seconds=2,
        duration_factor=1,
        solfeggio_base=432.0,
    )

    job = HarmonizationJob.load(job_id)
    assert job is not None
    assert job.pulse_seconds == 3
    assert job.pause_seconds == 2
    assert job.duration_factor == 1
    assert job.solfeggio_base == 432.0
    assert job.total_cycles == int(1 * 21 * 60 / (3 + 2))
    assert job.authority_job_id == f"harm-auth-{job_id}"


def test_start_harmonization_job_defaults_are_backwards_compatible(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")

    job_id = worker.start_harmonization_job(
        target_frequency=528.0,
        duration_minutes=3,
    )

    job = HarmonizationJob.load(job_id)
    assert job is not None
    assert job.pulse_seconds == 3.0
    assert job.pause_seconds == 2.0
    assert job.duration_factor == 1
    assert job.solfeggio_base == 432.0


def test_start_harmonization_job_rejects_second_active_owner_job(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")

    first_id = worker.start_harmonization_job(
        target_frequency=432.0,
        duration_minutes=21,
        tenant_id="tenant-a",
        operator_id="operator-a",
    )

    with pytest.raises(RuntimeError, match="active harmonization job"):
        worker.start_harmonization_job(
            target_frequency=528.0,
            duration_minutes=21,
            tenant_id="tenant-a",
            operator_id="operator-a",
        )

    assert worker.HarmonizationJob.load(first_id) is not None
    assert len(worker.list_all_jobs()) == 1


def test_start_harmonization_job_replays_preallocated_job_id_without_duplicate(
    tmp_path,
    monkeypatch,
    _stable_authority,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job_id = "harm_0123456789abcdef01234567"

    first = worker.start_harmonization_job(
        target_frequency=432.0,
        duration_minutes=21,
        tenant_id="tenant-a",
        operator_id="operator-a",
        job_id=job_id,
    )
    replay = worker.start_harmonization_job(
        target_frequency=432.0,
        duration_minutes=21,
        tenant_id="tenant-a",
        operator_id="operator-a",
        job_id=job_id,
    )

    assert first == replay == job_id
    assert _stable_authority.started == [f"harm-auth-{job_id}"]
    assert _stable_authority.replayed == [
        f"harm-auth-{job_id}",
        f"harm-auth-{job_id}",
    ]
    assert len(worker.list_all_jobs()) == 1


def test_start_harmonization_job_rejects_preallocated_id_cross_owner_replay(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job_id = "harm_abcdef0123456789abcdef01"
    worker.start_harmonization_job(
        target_frequency=432.0,
        duration_minutes=21,
        tenant_id="tenant-a",
        operator_id="operator-a",
        job_id=job_id,
    )

    with pytest.raises(RuntimeError, match="ownership mismatch"):
        worker.start_harmonization_job(
            target_frequency=432.0,
            duration_minutes=21,
            tenant_id="tenant-b",
            operator_id="operator-b",
            job_id=job_id,
        )


@pytest.mark.parametrize(
    "mismatch",
    [
        "report_id",
        "workbench_mode",
        "intention",
        "target_frequency",
        "target_frequency_type",
        "duration_minutes",
        "pulse_seconds",
        "pause_seconds",
        "duration_factor",
        "solfeggio_base",
        "hardware_private",
        "hardware_bool_type",
        "authority_job_id",
        "authority_command",
        "authority_owner",
    ],
)
def test_existing_deterministic_start_rejects_exact_identity_or_authority_mismatch(
    tmp_path,
    monkeypatch,
    _stable_authority,
    mismatch: str,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job_id = "harm_exact_identity"
    base = {
        "target_frequency": 432.0,
        "duration_minutes": 21,
        "intention": "Clearing",
        "hardware_config": {
            "use_cpu": False,
            "use_gpu": False,
            "_emf_authority_path": "C:/private/emf.json",
        },
        "pulse_seconds": 3.0,
        "pause_seconds": 2.0,
        "duration_factor": 1,
        "solfeggio_base": 432.0,
        "report_id": "report-a",
        "workbench_mode": "standard",
        "tenant_id": "tenant-a",
        "operator_id": "operator-a",
        "job_id": job_id,
    }
    worker.start_harmonization_job(**base)
    replay = {**base, "intention": "clearing"}
    if mismatch == "report_id":
        replay["report_id"] = "report-b"
    elif mismatch == "workbench_mode":
        replay["workbench_mode"] = "group"
    elif mismatch == "intention":
        replay["intention"] = "healing"
    elif mismatch == "target_frequency":
        replay["target_frequency"] = 528.0
    elif mismatch == "target_frequency_type":
        replay["target_frequency"] = 432
    elif mismatch == "duration_minutes":
        replay["duration_minutes"] = 42
    elif mismatch == "pulse_seconds":
        replay["pulse_seconds"] = 4.0
    elif mismatch == "pause_seconds":
        replay["pause_seconds"] = 1.0
    elif mismatch == "duration_factor":
        replay["duration_factor"] = 2
    elif mismatch == "solfeggio_base":
        replay["solfeggio_base"] = 528.0
    elif mismatch == "hardware_private":
        replay["hardware_config"] = {
            **base["hardware_config"],
            "_emf_authority_path": "C:/other/emf.json",
        }
    elif mismatch == "hardware_bool_type":
        replay["hardware_config"] = {
            **base["hardware_config"],
            "use_cpu": 0,
        }
    elif mismatch == "authority_job_id":
        persisted = HarmonizationJob.load(job_id)
        assert persisted is not None
        path = worker.JOBS_DIR / f"{job_id}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["authority_job_id"] = "harm-auth-foreign"
        path.write_text(json.dumps(payload), encoding="utf-8")
    elif mismatch == "authority_command":
        _stable_authority.commands[f"harm-auth-{job_id}"] = ["foreign-command"]
    elif mismatch == "authority_owner":
        _stable_authority.owners[f"harm-auth-{job_id}"] = "foreign-owner"
    started_before = list(_stable_authority.started)
    replayed_before = list(_stable_authority.replayed)

    expected_error = (
        "record is unreadable" if mismatch == "authority_job_id" else "identity|authority"
    )
    with pytest.raises(RuntimeError, match=expected_error):
        worker.start_harmonization_job(**replay)

    assert _stable_authority.started == started_before
    if mismatch not in {"authority_command", "authority_owner"}:
        assert _stable_authority.replayed == replayed_before


def test_new_authority_terminal_snapshot_is_converged_before_start_fails(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")

    class EarlyFailedAuthority:
        def __init__(self) -> None:
            self.started: list[str] = []
            self.stopped: list[str] = []

        def get_for_replay(self, job_id: str, **kwargs):
            raise KeyError(job_id)

        def start(self, command, **kwargs):
            self.started.append(kwargs["job_id"])
            return {"job_id": kwargs["job_id"], "status": "failed"}

        def stop(self, job_id: str):
            self.stopped.append(job_id)
            return {"job_id": job_id, "status": "stopped"}

    authority = EarlyFailedAuthority()
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)

    with pytest.raises(
        worker.HarmonizationProcessAuthorityError,
        match="status is invalid",
    ):
        worker.start_harmonization_job(
            target_frequency=432.0,
            duration_minutes=21,
            hardware_config={"use_cpu": False},
            tenant_id="tenant-a",
            operator_id="operator-a",
            job_id="harm_early_terminal",
        )

    authority_job_id = "harm-auth-harm_early_terminal"
    assert authority.started == [authority_job_id]
    assert authority.stopped == [authority_job_id]
    persisted = HarmonizationJob.load("harm_early_terminal")
    assert persisted is not None
    assert persisted.status == "pending"
    assert persisted.forced_status is None
