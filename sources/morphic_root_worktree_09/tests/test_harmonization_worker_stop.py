from __future__ import annotations

from datetime import datetime, timedelta
import threading

from typer.testing import CliRunner
import pytest

from apps.cli.main import app
from apps.web.harmonization import WorkerHarmonizationService
from apps.web.scan_jobs import ProcessAuthorityAmbiguousError
from apps.web.emf_authority import EmfTelemetryAuthority
from services import harmonization_worker as worker
from services.harmonization_worker import HarmonizationJob


runner = CliRunner()


def test_worker_stops_when_job_file_is_marked_stopped(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    now = [0.0]

    def fake_time() -> float:
        return now[0]

    def fake_sleep(seconds: float) -> None:
        now[0] += max(seconds, 1.0)

    job = HarmonizationJob(
        job_id="harm_stop_check",
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={"use_cpu": False},
    )
    job.save()

    calls = {"count": 0}

    def fake_modulate_hardware(*args, **kwargs) -> dict[str, float]:
        calls["count"] += 1
        now[0] += 0.01
        if calls["count"] == 1:
            stopped = HarmonizationJob.load("harm_stop_check")
            assert stopped is not None
            stopped.status = "stopped"
            stopped.end_time = datetime.now().isoformat()
            stopped.save()
        return {}

    monkeypatch.setattr(worker.time, "time", fake_time)
    monkeypatch.setattr(worker.time, "sleep", fake_sleep)
    monkeypatch.setattr(worker, "modulate_hardware", fake_modulate_hardware)

    worker.run_harmonization_worker("harm_stop_check")

    stopped = HarmonizationJob.load("harm_stop_check")
    assert stopped is not None
    assert stopped.status == "stopped"
    assert stopped.progress_percent < 100.0
    assert calls["count"] == 1


def test_stop_converges_stable_process_tree_before_publishing_stopped(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_converge",
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        status="running",
        current_phase="harmonizing",
        authority_job_id="harm-auth-harm_converge",
    )
    job.save()
    calls: list[str] = []

    class Authority:
        def stop(self, authority_job_id: str) -> dict[str, object]:
            persisted = HarmonizationJob.load(job.job_id)
            assert persisted is not None and persisted.status == "running"
            calls.append(authority_job_id)
            return {"job_id": authority_job_id, "status": "stopped"}

    monkeypatch.setattr(worker, "_process_authority_service", Authority)

    assert worker.stop_harmonization_job(job.job_id) is True

    stopped = HarmonizationJob.load(job.job_id)
    assert stopped is not None and stopped.status == "stopped"
    assert calls == ["harm-auth-harm_converge"]


def test_stop_writes_offset_compatible_terminal_time(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    start_time = "2026-07-22T12:00:00+05:30"
    job = HarmonizationJob(
        job_id="harm_offset_stop",
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        status="running",
        start_time=start_time,
        heartbeat_at=start_time,
        current_phase="running",
        authority_job_id="harm-auth-harm_offset_stop",
    )
    job.save()

    class Authority:
        def stop(self, authority_job_id: str) -> dict[str, object]:
            assert authority_job_id == job.authority_job_id
            return {"job_id": authority_job_id, "status": "stopped"}

    monkeypatch.setattr(worker, "_process_authority_service", Authority)

    assert worker.stop_harmonization_job(job.job_id) is True

    persisted = HarmonizationJob.load(job.job_id)
    assert persisted is not None and persisted.end_time is not None
    started = datetime.fromisoformat(start_time)
    ended = datetime.fromisoformat(persisted.end_time)
    marker = datetime.fromisoformat(
        worker._stop_marker_path(job.job_id).read_text(encoding="utf-8")
    )
    assert ended.utcoffset() == started.utcoffset()
    assert marker.utcoffset() == started.utcoffset()
    assert ended >= started


def test_stop_failure_persists_ambiguity_and_never_publishes_stopped(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_stop_ambiguous",
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        status="running",
        authority_job_id="harm-auth-harm_stop_ambiguous",
    )
    job.save()

    class Authority:
        def stop(self, authority_job_id: str) -> dict[str, object]:
            raise ProcessAuthorityAmbiguousError("unreadable stable authority")

    monkeypatch.setattr(worker, "_process_authority_service", Authority)

    with pytest.raises(ProcessAuthorityAmbiguousError):
        worker.stop_harmonization_job(job.job_id)

    persisted = HarmonizationJob.load(job.job_id)
    assert persisted is not None
    assert persisted.status == "authority_ambiguous"
    assert persisted.forced_status == "authority_ambiguous"


def test_stop_pristine_pending_without_authority_publishes_stopped(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_pending_no_authority",
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        authority_job_id="harm-auth-harm_pending_no_authority",
    )
    job.save()

    class MissingAuthority:
        def get(self, authority_job_id: str) -> dict[str, object]:
            raise KeyError(authority_job_id)

        def stop(self, authority_job_id: str) -> dict[str, object]:
            raise KeyError(authority_job_id)

    monkeypatch.setattr(worker, "_process_authority_service", MissingAuthority)

    snapshot = WorkerHarmonizationService().stop(job.job_id)
    assert snapshot["status"] == "stopped"
    assert snapshot["phase"] == "stopped"
    persisted = HarmonizationJob.load(job.job_id)
    assert persisted is not None
    assert persisted.status == "stopped"
    assert persisted.current_phase == "stopped"
    assert persisted.forced_status is None
    assert worker._stop_marker_path(job.job_id).exists()


def test_completed_poll_followed_by_stop_remains_completed(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_completed_immutable",
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        status="completed",
        current_phase="completed",
        end_time="2026-07-22T13:00:00",
        progress_percent=100.0,
        authority_job_id="harm-auth-harm_completed_immutable",
    )
    job.save()

    class CompletedAuthority:
        def get(self, authority_job_id: str) -> dict[str, object]:
            return {"job_id": authority_job_id, "status": "completed"}

    monkeypatch.setattr(worker, "_process_authority_service", CompletedAuthority)
    service = WorkerHarmonizationService()

    assert service.get(job.job_id)["status"] == "completed"
    stopped = service.stop(job.job_id)

    assert stopped["status"] == "completed"
    assert stopped["phase"] == "completed"
    persisted = HarmonizationJob.load(job.job_id)
    assert persisted is not None
    assert persisted.status == "completed"
    assert not worker._stop_marker_path(job.job_id).exists()


@pytest.mark.parametrize("active_status", ["running", "starting"])
def test_ordinary_get_revision_race_never_overwrites_concurrent_stop(
    tmp_path,
    monkeypatch,
    active_status,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    expired = (datetime.now() - timedelta(minutes=10)).isoformat()
    job = HarmonizationJob(
        job_id=f"harm_get_stop_race_{active_status}",
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        status=active_status,
        start_time=expired,
        heartbeat_at=expired,
        current_phase=active_status,
        authority_job_id=f"harm-auth-harm_get_stop_race_{active_status}",
    )
    job.save()
    get_entered = threading.Event()
    release_get = threading.Event()

    class Authority:
        def __init__(self) -> None:
            self.get_calls: list[str] = []
            self.stop_calls: list[str] = []
            self.start_calls: list[str] = []

        def get(self, authority_job_id: str) -> dict[str, object]:
            self.get_calls.append(authority_job_id)
            get_entered.set()
            assert release_get.wait(timeout=5)
            return {"job_id": authority_job_id, "status": "completed"}

        def observe(self, authority_job_id: str) -> dict[str, object]:
            return self.get(authority_job_id)

        def stop(self, authority_job_id: str) -> dict[str, object]:
            self.stop_calls.append(authority_job_id)
            return {"job_id": authority_job_id, "status": "stopped"}

        def start(self, *args, **kwargs):
            self.start_calls.append("start")
            raise AssertionError("ordinary get attempted worker start")

    authority = Authority()
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)
    snapshots: list[dict[str, object]] = []
    errors: list[BaseException] = []

    def get_snapshot() -> None:
        try:
            snapshots.append(WorkerHarmonizationService().get(job.job_id))
        except BaseException as exc:
            errors.append(exc)

    get_thread = threading.Thread(target=get_snapshot)
    get_thread.start()
    assert get_entered.wait(timeout=5)
    stopped = worker.stop_harmonization_job(job.job_id)
    release_get.set()
    get_thread.join(timeout=10)

    assert not get_thread.is_alive()
    assert stopped is True
    assert errors == []
    assert len(snapshots) == 1
    assert snapshots[0]["status"] == "stopped"
    assert snapshots[0]["phase"] == "stopped"
    persisted = HarmonizationJob.load(job.job_id)
    assert persisted is not None
    assert persisted.status == "stopped"
    assert persisted.current_phase == "stopped"
    assert authority.get_calls == [job.authority_job_id]
    assert authority.stop_calls == [job.authority_job_id]
    assert authority.start_calls == []


@pytest.mark.parametrize("active_status", ["running", "starting"])
def test_stop_marker_keeps_active_authority_reserved_until_convergence(
    tmp_path,
    monkeypatch,
    active_status,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    expired = (datetime.now() - timedelta(minutes=10)).isoformat()
    job = HarmonizationJob(
        job_id=f"harm_stop_pending_{active_status}",
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        status=active_status,
        start_time=expired,
        heartbeat_at=expired,
        current_phase=active_status,
        authority_job_id=f"harm-auth-harm_stop_pending_{active_status}",
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    job.save()
    stop_entered = threading.Event()
    release_stop = threading.Event()

    class Authority:
        def __init__(self) -> None:
            self.statuses = {job.authority_job_id: active_status}
            self.observe_calls: list[str] = []
            self.replay_calls: list[str] = []
            self.stop_calls: list[str] = []
            self.start_calls: list[str] = []

        def observe(self, authority_job_id: str) -> dict[str, object]:
            self.observe_calls.append(authority_job_id)
            return {
                "job_id": authority_job_id,
                "status": self.statuses[authority_job_id],
            }

        def get_for_replay(
            self,
            authority_job_id: str,
            **kwargs,
        ) -> dict[str, object]:
            self.replay_calls.append(authority_job_id)
            if authority_job_id not in self.statuses:
                raise KeyError(authority_job_id)
            return {
                "job_id": authority_job_id,
                "status": self.statuses[authority_job_id],
            }

        def start(self, command, **kwargs) -> dict[str, object]:
            authority_job_id = str(kwargs["job_id"])
            self.start_calls.append(authority_job_id)
            self.statuses[authority_job_id] = "running"
            return {"job_id": authority_job_id, "status": "running"}

        def stop(self, authority_job_id: str) -> dict[str, object]:
            self.stop_calls.append(authority_job_id)
            stop_entered.set()
            assert release_stop.wait(timeout=5)
            self.statuses[authority_job_id] = "stopped"
            return {"job_id": authority_job_id, "status": "stopped"}

    authority = Authority()
    monkeypatch.setattr(worker, "_process_authority_service", lambda: authority)
    stop_results: list[bool] = []
    stop_errors: list[BaseException] = []

    def stop() -> None:
        try:
            stop_results.append(
                worker.stop_harmonization_job(
                    job.job_id,
                    expected_tenant_id="tenant-a",
                    expected_operator_id="operator-a",
                )
            )
        except BaseException as exc:
            stop_errors.append(exc)

    stop_thread = threading.Thread(target=stop)
    stop_thread.start()
    assert stop_entered.wait(timeout=5)
    snapshot: dict[str, object] | None = None
    same_owner_error: RuntimeError | None = None
    pre_convergence: HarmonizationJob | None = None
    marker_exists = False
    worker_outcome: str | None = None
    try:
        worker_outcome = worker.run_harmonization_worker(job.job_id)
        snapshot = WorkerHarmonizationService().get_owned(
            job.job_id,
            tenant_id="tenant-a",
            operator_id="operator-a",
        )
        pre_convergence = HarmonizationJob.load(job.job_id)
        marker_exists = worker._stop_marker_path(job.job_id).exists()
        try:
            worker.start_harmonization_job(
                target_frequency=528.0,
                duration_minutes=21,
                hardware_config={"use_cpu": False},
                tenant_id="tenant-a",
                operator_id="operator-a",
                job_id=f"harm_second_{active_status}",
            )
        except RuntimeError as exc:
            same_owner_error = exc
    finally:
        release_stop.set()
        stop_thread.join(timeout=10)

    assert not stop_thread.is_alive()
    assert stop_errors == []
    assert stop_results == [True]
    assert marker_exists is True
    assert worker_outcome == "stopped"
    assert snapshot is not None and snapshot["status"] == active_status
    assert pre_convergence is not None
    assert pre_convergence.status == active_status
    assert pre_convergence.current_phase == active_status
    assert same_owner_error is not None
    assert "active harmonization job" in str(same_owner_error)
    assert authority.observe_calls == [job.authority_job_id, job.authority_job_id]
    assert authority.replay_calls == []
    assert authority.start_calls == []
    assert authority.stop_calls == [job.authority_job_id]
    persisted = HarmonizationJob.load(job.job_id)
    assert persisted is not None
    assert persisted.status == "stopped"
    assert persisted.current_phase == "stopped"
    assert persisted.forced_status is None


def test_harmonize_cli_delegates_start_status_and_stop(monkeypatch) -> None:
    started: list[dict[str, object]] = []
    stopped: list[str] = []
    job = HarmonizationJob(
        job_id="harm_cli_test",
        target_frequency=528.0,
        duration_minutes=3,
        intention="healing",
        hardware_config={"use_cpu": False, "use_gpu": True},
        status="running",
        progress_percent=10.0,
        cycles_completed=6,
        total_cycles=60,
    )

    def fake_start_harmonization_job(
        target_frequency: float,
        duration_minutes: int,
        intention: str,
        hardware_config: dict[str, bool],
    ) -> str:
        started.append(
            {
                "target_frequency": target_frequency,
                "duration_minutes": duration_minutes,
                "intention": intention,
                "hardware_config": hardware_config,
            }
        )
        return "harm_cli_test"

    monkeypatch.setattr(worker, "start_harmonization_job", fake_start_harmonization_job)
    monkeypatch.setattr(worker, "list_all_jobs", lambda: [job])
    monkeypatch.setattr(worker, "get_active_jobs", lambda: [job])
    monkeypatch.setattr(worker.HarmonizationJob, "load", classmethod(lambda cls, job_id: job))
    monkeypatch.setattr(worker, "stop_harmonization_job", lambda job_id: stopped.append(job_id) or True)

    start = runner.invoke(
        app,
        [
            "harmonize",
            "harmonize",
            "528",
            "3",
            "--intention",
            "healing",
            "--no-cpu",
            "--gpu",
            "--driver-layer",
        ],
    )
    assert start.exit_code == 0, start.output
    assert "harm_cli_test" in start.output
    assert started == [
        {
            "target_frequency": 528.0,
            "duration_minutes": 3,
            "intention": "healing",
            "hardware_config": {
                "use_cpu": False,
                "use_gpu": True,
                "use_ram": False,
                "use_websocket": False,
                "use_quartz": False,
                "use_driver_layer": True,
            },
        }
    ]

    status = runner.invoke(app, ["harmonize", "harmonize-status", "--active"])
    assert status.exit_code == 0, status.output
    assert "harm_cli_test" in status.output
    assert "running" in status.output

    stop = runner.invoke(app, ["harmonize", "harmonize-stop", "harm_cli_test"])
    assert stop.exit_code == 0, stop.output
    assert "gestoppt" in stop.output.lower()
    assert stopped == ["harm_cli_test"]


def test_worker_appends_realtime_trace_events(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    now = [0.0]

    def fake_time() -> float:
        return now[0]

    def fake_sleep(seconds: float) -> None:
        now[0] += max(seconds, 1.0)

    job = HarmonizationJob(
        job_id="harm_trace_check",
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={"use_cpu": False},
    )
    job.save()

    calls = {"count": 0}

    def fake_modulate_hardware(*args, **kwargs) -> dict[str, float]:
        calls["count"] += 1
        now[0] += 0.01
        stopped = HarmonizationJob.load("harm_trace_check")
        assert stopped is not None
        stopped.status = "stopped"
        stopped.end_time = datetime.now().isoformat()
        stopped.save()
        return {"cpu_frequency": 431.9}

    monkeypatch.setattr(worker.time, "time", fake_time)
    monkeypatch.setattr(worker.time, "sleep", fake_sleep)
    monkeypatch.setattr(worker, "modulate_hardware", fake_modulate_hardware)
    monkeypatch.setattr(
        worker,
        "capture_realtime_context",
        lambda hardware_config=None: {
            "emf_profile": {
                "emf_index": 0.2,
                "replay": {"algorithm": "emf-profile-v2"},
            },
            "hardware_snapshot": {"summary": {"health": "ok"}},
        },
    )

    worker.run_harmonization_worker("harm_trace_check")

    events = (tmp_path / "events" / "harm_trace_check.jsonl").read_text(
        encoding="utf-8"
    )
    assert '"event_type": "job_started"' in events
    assert '"event_type": "cycle_metrics"' not in events
    assert '"event_type": "stop_requested"' in events
    assert '"cycles_completed": 0' in events


def test_realtime_context_does_not_measure_when_durable_emf_authority_is_disabled(
    tmp_path,
    monkeypatch,
) -> None:
    authority_path = tmp_path / "emf-authority.json"
    authority_path.write_text('{"enabled": false}', encoding="utf-8")
    monkeypatch.setattr(
        worker,
        "measure_realtime_emf_profile",
        lambda hardware_config=None: (_ for _ in ()).throw(
            AssertionError("disabled authority must not measure")
        ),
    )

    context = worker.capture_realtime_context(
        {"use_cpu": False, "_emf_authority_path": str(authority_path)}
    )

    assert context == {}


def test_realtime_context_default_does_not_build_snapshot_service(tmp_path, monkeypatch) -> None:
    built: list[bool] = []

    def fake_build_snapshot_service(*args, **kwargs):
        built.append(True)
        raise AssertionError("snapshot service should not be built")

    monkeypatch.setattr(
        worker,
        "build_hardware_snapshot_service",
        fake_build_snapshot_service,
        raising=False,
    )
    monkeypatch.setattr(
        worker,
        "measure_realtime_emf_profile",
        lambda hardware_config=None: {
            "emf_index": 0.2,
            "replay": {"sensor_source": "fallback"},
        },
    )

    authority_path = tmp_path / "emf.json"
    EmfTelemetryAuthority(authority_path).set_enabled(True)
    context = worker.capture_realtime_context(
        {"use_cpu": False, "_emf_authority_path": str(authority_path)}
    )

    assert context == {
        "emf_profile": {"emf_index": 0.2, "replay": {"sensor_source": "fallback"}}
    }
    assert built == []


def test_realtime_context_discards_measurement_after_authority_revocation(
    tmp_path,
    monkeypatch,
) -> None:
    authority_path = tmp_path / "emf.json"
    authority = EmfTelemetryAuthority(authority_path)
    authority.set_enabled(True)

    def revoke_during_measurement():
        authority.set_enabled(False)
        return {"emf_index": 0.9}

    monkeypatch.setattr(worker, "measure_realtime_emf_profile", revoke_during_measurement)

    assert worker.capture_realtime_context(
        {"_emf_authority_path": str(authority_path)}
    ) == {}


def test_realtime_context_string_false_does_not_opt_in(tmp_path, monkeypatch) -> None:
    built: list[bool] = []

    def fake_build_snapshot_service(*args, **kwargs):
        built.append(True)
        raise AssertionError("snapshot service should not be built")

    monkeypatch.setattr(
        worker,
        "build_hardware_snapshot_service",
        fake_build_snapshot_service,
        raising=False,
    )
    monkeypatch.setattr(
        worker,
        "measure_realtime_emf_profile",
        lambda: {
            "emf_index": 0.2,
            "replay": {"sensor_source": "fallback"},
        },
    )

    authority_path = tmp_path / "emf.json"
    EmfTelemetryAuthority(authority_path).set_enabled(True)
    context = worker.capture_realtime_context(
        {"use_driver_layer": "false", "_emf_authority_path": str(authority_path)}
    )

    assert context["emf_profile"]["replay"]["sensor_source"] == "fallback"
    assert built == []


def test_realtime_context_opt_in_adds_hardware_snapshot(tmp_path, monkeypatch) -> None:
    class FakeSummary:
        entropy_mean = 0.8
        health = "ok"

    class FakeSnapshot:
        summary = FakeSummary()

        def to_dict(self):
            return {
                "summary": {"entropy_mean": 0.8, "health": "ok"},
                "samples": [{"source_id": "mock", "status": "ok", "value": 0.8}],
                "replay": {"algorithm": "hardware-snapshot-v2"},
            }

    class FakeSnapshotService:
        def capture(self, provider_ids=None):
            assert provider_ids == ["cpu_timing"]
            return FakeSnapshot()

    captured_sources: list[str] = []

    class FakeProfile:
        def to_dict(self):
            return {
                "emf_index": 0.31,
                "sensor_entropy": 0.8,
                "source_health": {"sensor_entropy": "ok"},
                "replay": {"sensor_source": captured_sources[-1]},
            }

    class FakeProfileService:
        def __init__(self, **kwargs):
            captured_sources.append(kwargs["sensor_source"])
            value, status = kwargs["sensor_entropy_probe"]()
            assert value == 0.8
            assert status == "ok"

        def measure(self):
            return FakeProfile()

    monkeypatch.setattr(
        worker,
        "build_hardware_snapshot_service",
        lambda **kwargs: FakeSnapshotService(),
        raising=False,
    )
    monkeypatch.setattr(worker, "EMFProfileService", FakeProfileService, raising=False)

    authority_path = tmp_path / "emf.json"
    EmfTelemetryAuthority(authority_path).set_enabled(True)
    context = worker.capture_realtime_context(
        {"use_driver_layer": True, "_emf_authority_path": str(authority_path)}
    )

    assert context["emf_profile"]["sensor_entropy"] == 0.8
    assert context["emf_profile"]["replay"]["sensor_source"] == "hardware_snapshot"
    assert context["hardware_snapshot"]["summary"]["health"] == "ok"


def test_worker_ignores_event_log_root_failures(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    event_root_file = tmp_path / "events"
    event_root_file.write_text("not a directory", encoding="utf-8")
    monkeypatch.setattr(worker, "EVENTS_DIR", event_root_file)
    now = [0.0]

    def fake_time() -> float:
        return now[0]

    def fake_sleep(seconds: float) -> None:
        now[0] += max(seconds, 1.0)

    job = HarmonizationJob(
        job_id="harm_event_failure_check",
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={"use_cpu": False},
    )
    job.save()

    def fake_modulate_hardware(*args, **kwargs) -> dict[str, float]:
        now[0] += 0.01
        stopped = HarmonizationJob.load("harm_event_failure_check")
        assert stopped is not None
        stopped.status = "stopped"
        stopped.end_time = datetime.now().isoformat()
        stopped.save()
        return {"cpu_frequency": 432.0}

    monkeypatch.setattr(worker.time, "time", fake_time)
    monkeypatch.setattr(worker.time, "sleep", fake_sleep)
    monkeypatch.setattr(worker, "modulate_hardware", fake_modulate_hardware)
    monkeypatch.setattr(
        worker,
        "measure_realtime_emf_profile",
        lambda: {"emf_index": 0.2, "replay": {"algorithm": "emf-profile-v2"}},
    )

    worker.run_harmonization_worker("harm_event_failure_check")

    stopped = HarmonizationJob.load("harm_event_failure_check")
    assert stopped is not None
    assert stopped.status == "stopped"
