from __future__ import annotations

from datetime import datetime

from typer.testing import CliRunner

from apps.cli.main import app
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
    assert '"event_type": "cycle_metrics"' in events
    assert '"event_type": "stop_requested"' in events
    assert '"cpu_frequency": 431.9' in events
    assert '"hardware_snapshot": {"summary": {"health": "ok"}}' in events


def test_realtime_context_default_does_not_build_snapshot_service(monkeypatch) -> None:
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

    context = worker.capture_realtime_context({"use_cpu": False})

    assert context == {
        "emf_profile": {"emf_index": 0.2, "replay": {"sensor_source": "fallback"}}
    }
    assert built == []


def test_realtime_context_string_false_does_not_opt_in(monkeypatch) -> None:
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

    context = worker.capture_realtime_context({"use_driver_layer": "false"})

    assert context["emf_profile"]["replay"]["sensor_source"] == "fallback"
    assert built == []


def test_realtime_context_opt_in_adds_hardware_snapshot(monkeypatch) -> None:
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

    context = worker.capture_realtime_context({"use_driver_layer": True})

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
