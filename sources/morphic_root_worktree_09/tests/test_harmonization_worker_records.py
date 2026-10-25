from __future__ import annotations

import copy
import json
from dataclasses import fields
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from services import harmonization_worker as worker
from services.harmonization_worker import HarmonizationJob


LEGACY_ACTIVE_PHASES = (
    "pending",
    "preparing",
    "starting",
    "initializing",
    "running",
    "harmonizing",
    "impulse",
    "pause",
    "finalizing",
)


def _valid_v2_payload(job_id: str = "harm_record") -> dict[str, object]:
    now = datetime.now().isoformat()
    return HarmonizationJob(
        job_id=job_id,
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False, "nested": {"level": 1}},
        status="running",
        start_time=now,
        progress_percent=20.0,
        cycles_completed=2,
        total_cycles=10,
        heartbeat_at=now,
        current_phase="impulse",
        authority_job_id=f"harm-auth-{job_id}",
    ).to_dict()


def _write_payload(root: Path, job_id: str, payload: object) -> Path:
    path = root / f"{job_id}.json"
    path.write_text(json.dumps(payload, allow_nan=True), encoding="utf-8")
    return path


def _apply_case(payload: dict[str, object], case: dict[str, object]) -> None:
    for key, value in case.get("set", {}).items():
        payload[key] = value
    for key in case.get("remove", ()):
        payload.pop(key, None)
    for key, value in case.get("add", {}).items():
        payload[key] = value


@pytest.mark.parametrize(
    "case",
    [
        pytest.param({"add": {"unknown": True}}, id="unknown-v2-field"),
        pytest.param({"remove": ["intention"]}, id="missing-v2-field"),
        pytest.param({"set": {"schema_version": True}}, id="bool-schema-version"),
        pytest.param({"set": {"target_frequency": True}}, id="bool-target"),
        pytest.param({"set": {"duration_minutes": True}}, id="bool-duration"),
        pytest.param({"set": {"progress_percent": True}}, id="bool-progress"),
        pytest.param({"set": {"worker_pid": True}}, id="bool-worker-pid"),
        pytest.param({"set": {"target_frequency": float("nan")}}, id="nan-target"),
        pytest.param({"set": {"worker_create_time": float("inf")}}, id="infinite-create-time"),
        pytest.param({"set": {"target_frequency": 0}}, id="zero-target"),
        pytest.param({"set": {"pulse_seconds": 0}}, id="zero-pulse"),
        pytest.param({"set": {"pause_seconds": -1}}, id="negative-pause"),
        pytest.param({"set": {"solfeggio_base": 0}}, id="zero-solfeggio"),
        pytest.param({"set": {"duration_minutes": -1}}, id="negative-duration"),
        pytest.param({"set": {"duration_factor": -1}}, id="negative-factor"),
        pytest.param({"set": {"progress_percent": 101}}, id="progress-over-100"),
        pytest.param({"set": {"cycles_completed": -1}}, id="negative-cycles"),
        pytest.param(
            {"set": {"cycles_completed": 11, "progress_percent": 110.0}},
            id="completed-cycles-over-total",
        ),
        pytest.param(
            {"set": {"cycles_completed": 1, "progress_percent": 50.0}},
            id="cycle-progress-contradiction",
        ),
        pytest.param({"set": {"status": "unknown"}}, id="unknown-status"),
        pytest.param({"set": {"current_phase": "completed"}}, id="active-terminal-phase"),
        pytest.param(
            {
                "set": {
                    "status": "completed",
                    "current_phase": "running",
                    "end_time": datetime.now().isoformat(),
                    "progress_percent": 100.0,
                    "error_message": None,
                }
            },
            id="terminal-active-phase",
        ),
        pytest.param(
            {"set": {"status": "completed", "current_phase": "completed", "progress_percent": 100.0}},
            id="terminal-without-end-time",
        ),
        pytest.param(
            {"set": {"end_time": datetime.now().isoformat()}},
            id="active-with-end-time",
        ),
        pytest.param(
            {
                "set": {
                    "status": "authority_ambiguous",
                    "current_phase": "authority_ambiguous",
                    "error_message": "manual recovery required",
                }
            },
            id="ambiguous-without-forced-status",
        ),
        pytest.param(
            {"set": {"forced_status": "authority_ambiguous"}},
            id="forced-status-on-running",
        ),
        pytest.param({"set": {"forced_status": "stopped"}}, id="unknown-forced-status"),
        pytest.param({"set": {"heartbeat_at": "not-an-iso-timestamp"}}, id="malformed-heartbeat"),
        pytest.param({"set": {"tenant_id": 7}}, id="invalid-tenant-type"),
        pytest.param({"set": {"operator_id": {"legacy": "owner"}}}, id="invalid-operator-type"),
        pytest.param({"set": {"hardware_config": {"bad": float("nan")}}}, id="hardware-nan"),
    ],
)
def test_v2_records_fail_closed_for_invalid_shapes_and_values(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    case: dict[str, object],
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    payload = copy.deepcopy(_valid_v2_payload())
    _apply_case(payload, case)
    original = _write_payload(tmp_path, "harm_record", payload).read_bytes()

    with pytest.raises(RuntimeError, match="record is unreadable"):
        HarmonizationJob.load("harm_record")

    assert (tmp_path / "harm_record.json").read_bytes() == original


def test_in_memory_record_parser_rejects_non_string_hardware_keys() -> None:
    payload = _valid_v2_payload()
    payload["hardware_config"] = {1: "not-string-keyed"}

    with pytest.raises((TypeError, ValueError)):
        HarmonizationJob.from_dict(payload)


def test_record_filename_must_match_canonical_embedded_job_id(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    _write_payload(tmp_path, "harm_filename", _valid_v2_payload("harm_embedded"))

    with pytest.raises(RuntimeError, match="record is unreadable"):
        HarmonizationJob.load("harm_filename")


@pytest.mark.parametrize("schema_version", [None, 1])
def test_shipped_legacy_records_fill_only_dataclass_defaults_without_owner_inference(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    schema_version: int | None,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    payload: dict[str, object] = {
        "job_id": "harm_legacy",
        "target_frequency": 432.0,
        "duration_minutes": 5,
        "intention": "harmonization",
        "hardware_config": {"use_cpu": True},
        "status": "completed",
        "start_time": "2025-11-29T23:58:33.788108",
        "end_time": "2025-11-30T00:03:34.062556",
        "progress_percent": 100.0,
        "error_message": None,
        "cycles_completed": 8,
        "total_cycles": 10,
    }
    if schema_version is not None:
        payload["schema_version"] = schema_version
    _write_payload(tmp_path, "harm_legacy", payload)

    loaded = HarmonizationJob.load("harm_legacy")

    assert loaded is not None
    assert loaded.schema_version == 2
    assert loaded.pulse_seconds == 3.0
    assert loaded.current_phase == "pending"
    assert loaded.tenant_id is None
    assert loaded.operator_id is None
    loaded.save()
    saved = json.loads((tmp_path / "harm_legacy.json").read_text(encoding="utf-8"))
    assert set(saved) == {field.name for field in fields(HarmonizationJob)}
    assert saved["schema_version"] == 2
    assert saved["tenant_id"] is None
    assert saved["operator_id"] is None


@pytest.mark.parametrize(
    "case",
    [
        pytest.param({"remove": ["status"]}, id="missing-required"),
        pytest.param({"add": {"worker": {"pid": 3}}}, id="unknown-legacy-field"),
        pytest.param(
            {"set": {"schema_version": 1}, "add": {"v2_only_unknown": True}},
            id="mixed-legacy-shape",
        ),
    ],
)
def test_legacy_records_reject_missing_unknown_and_mixed_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    case: dict[str, object],
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    payload = {
        "job_id": "harm_legacy_bad",
        "target_frequency": 432.0,
        "duration_minutes": 5,
        "intention": "harmonization",
        "hardware_config": {},
        "status": "completed",
        "start_time": "2025-11-29T23:58:33",
        "end_time": "2025-11-30T00:03:34",
        "progress_percent": 100.0,
        "error_message": None,
        "cycles_completed": 8,
        "total_cycles": 10,
    }
    _apply_case(payload, case)
    _write_payload(tmp_path, "harm_legacy_bad", payload)

    with pytest.raises(RuntimeError, match="record is unreadable"):
        HarmonizationJob.load("harm_legacy_bad")


@pytest.mark.parametrize("schema_version", [None, 1], ids=["v0", "v1"])
@pytest.mark.parametrize("status", ["completed", "error", "stopped"])
@pytest.mark.parametrize("legacy_phase", LEGACY_ACTIVE_PHASES)
def test_shipped_legacy_terminal_phase_is_normalized_before_v2_save(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    schema_version: int | None,
    status: str,
    legacy_phase: str,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    payload: dict[str, object] = {
        "job_id": "harm_legacy_terminal",
        "target_frequency": 432.0,
        "duration_minutes": 21,
        "intention": "harmonization",
        "hardware_config": {"use_cpu": False},
        "status": status,
        "start_time": "2026-07-22T12:00:00",
        "end_time": "2026-07-22T12:01:00",
        "progress_percent": 100.0 if status == "completed" else 20.0,
        "error_message": "worker failed" if status == "error" else None,
        "cycles_completed": 2,
        "total_cycles": 10,
        "current_phase": legacy_phase,
    }
    if schema_version is not None:
        payload["schema_version"] = schema_version
    _write_payload(tmp_path, "harm_legacy_terminal", payload)

    loaded = HarmonizationJob.load("harm_legacy_terminal")

    assert loaded is not None
    assert loaded.current_phase == status
    loaded.save()
    saved = json.loads(
        (tmp_path / "harm_legacy_terminal.json").read_text(encoding="utf-8")
    )
    assert saved["schema_version"] == 2
    assert saved["status"] == status
    assert saved["current_phase"] == status
    assert HarmonizationJob.load("harm_legacy_terminal") is not None


@pytest.mark.parametrize("status", ["completed", "error", "stopped"])
@pytest.mark.parametrize("active_phase", LEGACY_ACTIVE_PHASES)
def test_v2_terminal_records_reject_historical_active_phases(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    status: str,
    active_phase: str,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    payload = _valid_v2_payload("harm_v2_terminal_phase")
    payload.update(
        {
            "status": status,
            "current_phase": active_phase,
            "end_time": "2026-07-22T12:01:00",
            "progress_percent": 100.0 if status == "completed" else 20.0,
            "error_message": "worker failed" if status == "error" else None,
        }
    )
    _write_payload(tmp_path, "harm_v2_terminal_phase", payload)

    with pytest.raises(RuntimeError, match="record is unreadable"):
        HarmonizationJob.load("harm_v2_terminal_phase")


@pytest.mark.parametrize("schema_version", [None, 1], ids=["v0", "v1"])
def test_legacy_terminal_record_rejects_unknown_phase(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    schema_version: int | None,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    payload: dict[str, object] = {
        "job_id": "harm_legacy_unknown_phase",
        "target_frequency": 432.0,
        "duration_minutes": 21,
        "intention": "harmonization",
        "hardware_config": {},
        "status": "completed",
        "start_time": "2026-07-22T12:00:00",
        "end_time": "2026-07-22T12:01:00",
        "progress_percent": 100.0,
        "error_message": None,
        "cycles_completed": 2,
        "total_cycles": 10,
        "current_phase": "legacy-unknown",
    }
    if schema_version is not None:
        payload["schema_version"] = schema_version
    _write_payload(tmp_path, "harm_legacy_unknown_phase", payload)

    with pytest.raises(RuntimeError, match="record is unreadable"):
        HarmonizationJob.load("harm_legacy_unknown_phase")


def test_malformed_registry_member_blocks_recovery_release_and_new_start(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    stale = HarmonizationJob(
        job_id="harm_stale_registry",
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        status="running",
        start_time=(datetime.now() - timedelta(minutes=10)).isoformat(),
        heartbeat_at=(datetime.now() - timedelta(minutes=10)).isoformat(),
        current_phase="running",
        authority_job_id="harm-auth-harm_stale_registry",
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    stale.save()
    malformed = _valid_v2_payload("harm_malformed_registry")
    malformed.update(
        {
            "target_frequency": True,
            "status": "completed",
            "current_phase": "completed",
            "end_time": datetime.now().isoformat(),
            "progress_percent": 100.0,
            "cycles_completed": 10,
        }
    )
    _write_payload(tmp_path, "harm_malformed_registry", malformed)
    authority_calls: list[tuple[str, str]] = []

    class Authority:
        def get(self, job_id: str) -> dict[str, object]:
            authority_calls.append(("get", job_id))
            return {"job_id": job_id, "status": "completed"}

        def get_for_replay(self, job_id: str, **kwargs: object) -> dict[str, object]:
            authority_calls.append(("replay", job_id))
            raise KeyError(job_id)

        def start(self, command: list[str], **kwargs: object) -> dict[str, object]:
            job_id = str(kwargs["job_id"])
            authority_calls.append(("start", job_id))
            return {"job_id": job_id, "status": "running"}

    monkeypatch.setattr(worker, "_process_authority_service", Authority)

    with pytest.raises(RuntimeError, match="record is unreadable"):
        worker.start_harmonization_job(
            target_frequency=432.0,
            duration_minutes=21,
            hardware_config={"use_cpu": False},
            tenant_id="tenant-a",
            operator_id="operator-a",
            job_id="harm_new_registry",
        )

    persisted = HarmonizationJob.load(stale.job_id)
    assert persisted is not None
    assert persisted.status == "running"
    assert authority_calls == []


def test_reconcile_existing_pending_validates_complete_registry_before_authority(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job_id = "harm_replay_registry"
    target = HarmonizationJob(
        job_id=job_id,
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        authority_job_id=f"harm-auth-{job_id}",
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    target.save()
    target_path = tmp_path / f"{job_id}.json"
    target_bytes = target_path.read_bytes()
    malformed = _valid_v2_payload("harm_foreign_malformed")
    malformed["target_frequency"] = True
    _write_payload(tmp_path, "harm_foreign_malformed", malformed)
    authority_calls: list[tuple[str, str]] = []

    class Authority:
        def get_for_replay(self, authority_job_id: str, **kwargs: object):
            authority_calls.append(("replay", authority_job_id))
            raise KeyError(authority_job_id)

        def start(self, command: list[str], **kwargs: object):
            authority_job_id = str(kwargs["job_id"])
            authority_calls.append(("start", authority_job_id))
            raise AssertionError("malformed registry reached authority start")

        def get(self, authority_job_id: str):
            authority_calls.append(("get", authority_job_id))
            raise AssertionError("malformed registry reached authority get")

    monkeypatch.setattr(worker, "_process_authority_service", Authority)

    with pytest.raises(RuntimeError, match="record is unreadable"):
        worker.reconcile_harmonization_start(
            job_id,
            target_frequency=432.0,
            duration_minutes=21,
            intention="harmonization",
            hardware_config={"use_cpu": False},
            pulse_seconds=3.0,
            pause_seconds=2.0,
            duration_factor=1,
            solfeggio_base=432.0,
            report_id=None,
            workbench_mode="standard",
            tenant_id="tenant-a",
            operator_id="operator-a",
        )

    assert authority_calls == []
    assert target_path.read_bytes() == target_bytes


@pytest.mark.parametrize(
    ("other_kind", "blocked"),
    [
        pytest.param("ownerless", True, id="ownerless-blocks-globally"),
        pytest.param("ambiguous", True, id="ambiguous-blocks-globally"),
        pytest.param("same-owner", True, id="same-owner-blocks"),
        pytest.param("different-owner", False, id="different-owner-does-not-block"),
    ],
)
def test_reconcile_pending_uses_global_reservation_policy_excluding_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    other_kind: str,
    blocked: bool,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job_id = "harm_replay_target"
    target = HarmonizationJob(
        job_id=job_id,
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        authority_job_id=f"harm-auth-{job_id}",
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    target.save()
    now = datetime.now().isoformat()
    other_id = f"harm_other_{other_kind.replace('-', '_')}"
    other = HarmonizationJob(
        job_id=other_id,
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        status="running",
        start_time=now,
        heartbeat_at=now,
        current_phase="running",
        authority_job_id=f"harm-auth-{other_id}",
        tenant_id=(
            None
            if other_kind == "ownerless"
            else "tenant-a" if other_kind == "same-owner" else "tenant-b"
        ),
        operator_id=(
            None
            if other_kind == "ownerless"
            else "operator-a" if other_kind == "same-owner" else "operator-b"
        ),
    )
    if other_kind == "ambiguous":
        other.status = "authority_ambiguous"
        other.current_phase = "authority_ambiguous"
        other.forced_status = "authority_ambiguous"
        other.error_message = "manual recovery required"
    other.save()
    authority_calls: list[tuple[str, str]] = []

    class Authority:
        def get_for_replay(self, authority_job_id: str, **kwargs: object):
            authority_calls.append(("replay", authority_job_id))
            return {"job_id": authority_job_id, "status": "running"}

        def start(self, command: list[str], **kwargs: object):
            authority_job_id = str(kwargs["job_id"])
            authority_calls.append(("start", authority_job_id))
            raise AssertionError("reservation policy reached authority start")

    monkeypatch.setattr(worker, "_process_authority_service", Authority)

    call = lambda: worker.reconcile_harmonization_start(
        job_id,
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        pulse_seconds=3.0,
        pause_seconds=2.0,
        duration_factor=1,
        solfeggio_base=432.0,
        report_id=None,
        workbench_mode="standard",
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    if blocked:
        with pytest.raises(RuntimeError, match="active harmonization job"):
            call()
        assert authority_calls == []
    else:
        current, _, status_phase = call()
        assert current.job_id == job_id
        assert status_phase == ("pending", "pending")
        assert authority_calls == [("replay", f"harm-auth-{job_id}")]
