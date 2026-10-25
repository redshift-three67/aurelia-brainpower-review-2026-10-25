from __future__ import annotations

import threading
import time
import os
from datetime import datetime

import pytest
import psutil

from apps.web.harmonization import WorkerHarmonizationService
from services import hardware_modulation
from services import harmonization_worker as worker
from services.harmonization_worker import HarmonizationJob


@pytest.fixture(autouse=True)
def _direct_worker_stop_authority(monkeypatch):
    """These unit tests execute the worker in-process; external tree authority is separate."""
    monkeypatch.setattr(worker, "_converge_harmonization_worker", lambda job: None)


def _blocking_hardware_process(stop_event):
    while True:
        time.sleep(0.05)


def _cooperative_hardware_process(name: str, stop_event):
    started_at = time.monotonic()
    while stop_event.is_set():
        time.sleep(0.005)
    return {f"{name}_started_at": started_at, f"{name}_pid": os.getpid()}


def test_worker_uses_persisted_impulse_duration_before_checking_for_stop(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    now = [0.0]
    sleeps: list[float] = []

    def fake_time() -> float:
        return now[0]

    def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)
        now[0] += seconds
        job = HarmonizationJob.load("harm_pulse_duration")
        assert job is not None
        job.status = "stopped"
        job.save()

    job = HarmonizationJob(
        job_id="harm_pulse_duration",
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        pulse_seconds=3.0,
        pause_seconds=2.0,
    )
    job.save()

    monkeypatch.setattr(worker.time, "time", fake_time)
    monkeypatch.setattr(worker.time, "sleep", fake_sleep)
    calls: list[dict[str, object]] = []

    def fake_modulate_hardware(**kwargs):
        calls.append(kwargs)
        job = HarmonizationJob.load("harm_pulse_duration")
        assert job is not None
        job.status = "stopped"
        job.save()
        return {}

    monkeypatch.setattr(worker, "modulate_hardware", fake_modulate_hardware)
    monkeypatch.setattr(worker, "capture_realtime_context", lambda config=None: {})

    worker.run_harmonization_worker("harm_pulse_duration")
    assert sleeps == []
    assert len(calls) == 1
    assert calls[0]["frequency"] == 432.0
    assert calls[0]["intention"] == "harmonization"
    assert calls[0]["config"] == {"use_cpu": False}
    assert calls[0]["duration_seconds"] == 3.0
    assert callable(calls[0]["should_continue"])
    stopped = HarmonizationJob.load("harm_pulse_duration")
    assert stopped.status == "stopped"
    assert stopped.total_cycles == 252
    events = (tmp_path / "events" / "harm_pulse_duration.jsonl").read_text(encoding="utf-8")
    assert '"event_type": "harmonization_phase"' in events
    assert '"phase": "impulse"' in events


def test_worker_interrupts_pause_in_bounded_slices_without_completing_cycle(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    now = [0.0]
    sleeps: list[float] = []

    job = HarmonizationJob(
        job_id="harm_pause_interrupt",
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        pulse_seconds=3.0,
        pause_seconds=2.0,
    )
    job.save()

    monkeypatch.setattr(worker.time, "time", lambda: now[0])

    def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)
        now[0] += seconds
        assert worker.stop_harmonization_job(job.job_id) is True

    monkeypatch.setattr(worker.time, "sleep", fake_sleep)
    monkeypatch.setattr(worker, "modulate_hardware", lambda **kwargs: {})
    monkeypatch.setattr(worker, "capture_realtime_context", lambda config=None: {})

    worker.run_harmonization_worker(job.job_id)

    stopped = HarmonizationJob.load(job.job_id)
    assert stopped is not None
    assert stopped.status == "stopped"
    assert stopped.cycles_completed == 0
    assert sleeps == [0.1]
    events = (tmp_path / "events" / f"{job.job_id}.jsonl").read_text(encoding="utf-8")
    assert '"phase": "pause"' in events
    assert '"event_type": "cycle_metrics"' not in events


def test_worker_impulse_receives_a_stop_and_deadline_predicate(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    monotonic = [100.0]
    observed = []
    job = HarmonizationJob(
        job_id="harm_impulse_deadline",
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={"use_cpu": True},
        pulse_seconds=3.0,
        pause_seconds=2.0,
    )
    job.save()
    monkeypatch.setattr(worker.time, "monotonic", lambda: monotonic[0])

    def overrun_modulator(**kwargs):
        predicate = kwargs["should_continue"]
        observed.append(predicate())
        monotonic[0] += 3.2
        observed.append(predicate())
        assert worker.stop_harmonization_job(job.job_id) is True
        return {}

    monkeypatch.setattr(worker, "modulate_hardware", overrun_modulator)
    monkeypatch.setattr(worker, "capture_realtime_context", lambda config=None: {})

    worker.run_harmonization_worker(job.job_id)

    assert observed == [True, False]
    stopped = HarmonizationJob.load(job.job_id)
    assert stopped is not None
    assert stopped.status == "stopped"
    assert stopped.cycles_completed == 0


def test_stop_wins_before_cycle_commit_and_suppresses_cycle_metrics(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_stop_before_commit",
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        pulse_seconds=3.0,
        pause_seconds=2.0,
    )
    job.save()
    monkeypatch.setattr(worker, "execute_pulse_pause_cycle", lambda **kwargs: True)

    def stop_before_commit(config=None):
        assert worker.stop_harmonization_job(job.job_id) is True
        return {}

    monkeypatch.setattr(worker, "capture_realtime_context", stop_before_commit)

    worker.run_harmonization_worker(job.job_id)

    stopped = HarmonizationJob.load(job.job_id)
    assert stopped is not None
    assert stopped.status == "stopped"
    assert stopped.cycles_completed == 0
    events = (tmp_path / "events" / f"{job.job_id}.jsonl").read_text(encoding="utf-8")
    assert '"event_type": "cycle_metrics"' not in events


def test_selected_hardware_processes_enter_one_shared_pulse_window() -> None:
    metrics = hardware_modulation._run_killable_tasks(
        {
            name: (_cooperative_hardware_process, (name,))
            for name in ("cpu", "gpu", "ram")
        },
        duration_seconds=0.05,
        should_continue=lambda: True,
    )

    starts = [metrics[f"{name}_started_at"] for name in ("cpu", "gpu", "ram")]
    assert max(starts) - min(starts) < 0.1
    assert len({metrics[f"{name}_pid"] for name in ("cpu", "gpu", "ram")}) == 3


def test_noncooperative_hardware_process_is_physically_terminated_after_grace() -> None:
    observed_pids: list[int] = []
    started = time.monotonic()

    with pytest.raises(hardware_modulation.HardwareModulationOverrunError) as error:
        hardware_modulation._run_killable_tasks(
            {"blocked": (_blocking_hardware_process, ())},
            duration_seconds=0.01,
            should_continue=lambda: True,
        )
    observed_pids.extend(error.value.terminated_pids)

    assert time.monotonic() - started < 3.0
    assert observed_pids
    assert all(not psutil.pid_exists(pid) for pid in observed_pids)


def test_partial_hardware_spawn_failure_converges_started_child(monkeypatch) -> None:
    real_context = hardware_modulation.multiprocessing.get_context("spawn")
    created = []

    class FailingProcess:
        pid = None

        def start(self) -> None:
            raise OSError("injected second spawn failure")

    class TrackingProcess:
        def __init__(self, process) -> None:
            self.process = process
            self.pid_at_start = None

        def start(self) -> None:
            self.process.start()
            self.pid_at_start = self.process.pid

        def __getattr__(self, name):
            return getattr(self.process, name)

    class InjectedContext:
        def Event(self):
            return real_context.Event()

        def Queue(self):
            return real_context.Queue()

        def Process(self, *args, **kwargs):
            if created:
                process = FailingProcess()
            else:
                process = TrackingProcess(real_context.Process(*args, **kwargs))
            created.append(process)
            return process

    monkeypatch.setattr(
        hardware_modulation.multiprocessing,
        "get_context",
        lambda method: InjectedContext(),
    )

    try:
        with pytest.raises(OSError, match="second spawn failure"):
            hardware_modulation._run_killable_tasks(
                {
                    "first": (_blocking_hardware_process, ()),
                    "second": (_blocking_hardware_process, ()),
                },
                duration_seconds=1.0,
                should_continue=lambda: True,
            )

        first_pid = created[0].pid_at_start
        assert first_pid is not None
        assert not psutil.pid_exists(first_pid)
    finally:
        first = created[0] if created else None
        if first is not None:
            try:
                alive = first.is_alive()
            except ValueError:
                alive = False
            if alive:
                first.terminate()
                first.join(timeout=2)


def test_hardware_cleanup_reports_survivor_and_continues_after_cleanup_error() -> None:
    class Event:
        def clear(self) -> None:
            pass

        def set(self) -> None:
            pass

    class Process:
        def __init__(self, pid: int, *, fail_terminate: bool = False) -> None:
            self.pid = pid
            self.alive = True
            self.fail_terminate = fail_terminate
            self.terminate_calls = 0

        def join(self, timeout=None) -> None:
            pass

        def is_alive(self) -> bool:
            return self.alive

        def terminate(self) -> None:
            self.terminate_calls += 1
            if self.fail_terminate:
                raise OSError("terminate failed")
            self.alive = False

        def kill(self) -> None:
            pass

    survivor = Process(101, fail_terminate=True)
    later = Process(102)

    with pytest.raises(BaseExceptionGroup) as error:
        hardware_modulation._converge_started_processes([survivor, later], Event(), Event())

    assert [type(exc) for exc in error.value.exceptions] == [
        OSError,
        hardware_modulation.HardwareModulationOverrunError,
    ]
    overrun = error.value.exceptions[1]
    assert overrun.terminated_pids == [101]
    assert later.terminate_calls == 1


def test_stop_predicate_converges_cpu_gpu_and_ram_processes_within_grace() -> None:
    continue_flag = threading.Event()
    continue_flag.set()
    controller = threading.Thread(
        target=lambda: (time.sleep(0.1), continue_flag.clear()),
        daemon=True,
    )
    controller.start()

    metrics = hardware_modulation._run_killable_tasks(
        {
            name: (_cooperative_hardware_process, (name,))
            for name in ("cpu", "gpu", "ram")
        },
        duration_seconds=1.0,
        should_continue=continue_flag.is_set,
    )
    controller.join(timeout=2)

    assert not controller.is_alive()
    assert all(
        not psutil.pid_exists(metrics[f"{name}_pid"])
        for name in ("cpu", "gpu", "ram")
    )


def test_modulate_all_hardware_uses_isolated_production_paths() -> None:
    metrics = hardware_modulation.modulate_all_hardware(
        frequency=432.0,
        intention="harmonization",
        config={"use_cpu": False, "use_gpu": True, "use_ram": True},
        duration_seconds=0.02,
        should_continue=lambda: True,
    )

    assert metrics["frequency"] == 432.0
    assert "gpu_cycles" in metrics
    assert "ram_cycles" in metrics


def test_terminal_commit_does_not_publish_completed_after_stop(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_terminal_stop",
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        total_cycles=0,
    )
    job.save()
    assert worker.stop_harmonization_job(job.job_id) is True
    events = []
    monkeypatch.setattr(worker, "_append_event", lambda *args: events.append(args))

    committed = worker._commit_completed_job(job.job_id)

    assert committed is None
    persisted = HarmonizationJob.load(job.job_id)
    assert persisted is not None
    assert persisted.status == "stopped"
    assert not any(event[1] == "completed" for event in events)


def test_completed_commit_normalizes_terminal_phase_and_snapshot(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_completed_phase",
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        status="running",
        current_phase="pause",
        authority_job_id="harm-auth-harm_completed_phase",
    )
    job.save()

    committed = worker._commit_completed_job(job.job_id)

    assert committed is not None
    assert committed.status == "completed"
    assert committed.current_phase == "completed"
    assert committed.progress_percent == 100.0
    assert committed.error_message is None
    assert committed.forced_status is None

    class CompletedAuthority:
        def get(self, authority_job_id: str) -> dict[str, object]:
            return {"job_id": authority_job_id, "status": "completed"}

    monkeypatch.setattr(worker, "_process_authority_service", CompletedAuthority)
    snapshot = WorkerHarmonizationService()._snapshot(committed)
    assert snapshot["status"] == "completed"
    assert snapshot["phase"] == "completed"


def test_worker_startup_stop_marker_prevents_hardware_modulation(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_startup_marker",
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": True},
    )
    job.save()
    worker._atomic_write_text(
        worker._stop_marker_path(job.job_id),
        "2026-07-22T10:00:00",
    )
    modulation_calls: list[str] = []
    events: list[str] = []

    def reject_modulation(**kwargs):
        modulation_calls.append("modulate")
        raise AssertionError("startup marker reached hardware modulation")

    monkeypatch.setattr(worker, "modulate_hardware", reject_modulation)
    monkeypatch.setattr(
        worker,
        "_append_event",
        lambda job_id, event_type, payload: events.append(event_type),
    )

    outcome = worker.run_harmonization_worker(job.job_id)

    persisted = HarmonizationJob.load(job.job_id)
    assert outcome == "stopped"
    assert persisted is not None
    assert persisted.status == "pending"
    assert persisted.current_phase == "pending"
    assert persisted.end_time is None
    assert modulation_calls == []
    assert events == ["stop_requested"]


def test_worker_runtime_stop_marker_exits_without_terminal_commit(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_runtime_marker",
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        pulse_seconds=0.01,
        pause_seconds=0.01,
    )
    job.save()
    modulation_calls: list[str] = []

    def write_marker(**kwargs):
        modulation_calls.append("modulate")
        worker._atomic_write_text(
            worker._stop_marker_path(job.job_id),
            "2026-07-22T12:30:00",
        )
        return {}

    monkeypatch.setattr(worker, "modulate_hardware", write_marker)

    outcome = worker.run_harmonization_worker(job.job_id)

    persisted = HarmonizationJob.load(job.job_id)
    assert outcome == "stopped"
    assert persisted is not None
    assert persisted.status == "running"
    assert persisted.current_phase == "impulse"
    assert persisted.end_time is None
    assert persisted.cycles_completed == 0
    assert modulation_calls == ["modulate"]


def test_stop_marker_after_phase_save_prevents_modulation_entry(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_marker_before_modulation",
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        pulse_seconds=0.01,
        pause_seconds=0.01,
    )
    job.save()
    original_save = HarmonizationJob.save
    marker_written = False

    def save_then_mark(self: HarmonizationJob) -> None:
        nonlocal marker_written
        original_save(self)
        if (
            self.job_id == job.job_id
            and self.current_phase == "impulse"
            and not marker_written
        ):
            marker_written = True
            worker._atomic_write_text(
                worker._stop_marker_path(job.job_id),
                "2026-07-22T12:45:00",
            )

    modulation_calls: list[str] = []

    def reject_modulation(**kwargs):
        modulation_calls.append("modulate")
        return {}

    monkeypatch.setattr(HarmonizationJob, "save", save_then_mark)
    monkeypatch.setattr(worker, "modulate_hardware", reject_modulation)

    outcome = worker.run_harmonization_worker(job.job_id)

    persisted = HarmonizationJob.load(job.job_id)
    assert marker_written is True
    assert modulation_calls == []
    assert outcome == "stopped"
    assert persisted is not None
    assert persisted.status == "running"
    assert persisted.current_phase == "impulse"
    assert persisted.end_time is None
    assert persisted.cycles_completed == 0


def test_stop_marker_during_pause_exits_without_cycle_or_terminal_commit(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_marker_during_pause",
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        pulse_seconds=0.01,
        pause_seconds=0.01,
    )
    job.save()
    modulation_calls: list[str] = []
    pause_calls: list[float] = []

    def modulate(**kwargs):
        modulation_calls.append("modulate")
        return {}

    def mark_during_pause(seconds: float) -> None:
        pause_calls.append(seconds)
        worker._atomic_write_text(
            worker._stop_marker_path(job.job_id),
            "2026-07-22T12:50:00",
        )

    monkeypatch.setattr(worker, "modulate_hardware", modulate)
    monkeypatch.setattr(worker.time, "sleep", mark_during_pause)

    outcome = worker.run_harmonization_worker(job.job_id)

    persisted = HarmonizationJob.load(job.job_id)
    assert outcome == "stopped"
    assert persisted is not None
    assert persisted.status == "running"
    assert persisted.current_phase == "pause"
    assert persisted.end_time is None
    assert persisted.cycles_completed == 0
    assert modulation_calls == ["modulate"]
    assert len(pause_calls) == 1


def test_marker_before_completion_returns_stopped_without_terminal_commit(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_marker_before_completion",
        target_frequency=432.0,
        duration_minutes=0,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        duration_factor=0,
    )
    job.save()
    original_commit = worker._commit_completed_job

    def mark_then_commit(job_id: str):
        worker._atomic_write_text(
            worker._stop_marker_path(job_id),
            "2026-07-22T13:00:00",
        )
        return original_commit(job_id)

    monkeypatch.setattr(worker, "_commit_completed_job", mark_then_commit)

    outcome = worker.run_harmonization_worker(job.job_id)

    persisted = HarmonizationJob.load(job.job_id)
    assert outcome == "stopped"
    assert persisted is not None
    assert persisted.status == "running"
    assert persisted.current_phase == "initializing"
    assert persisted.end_time is None
    assert persisted.progress_percent == 0.0


def test_marker_before_error_commit_returns_stopped_without_error_terminal(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_marker_before_error",
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        pulse_seconds=0.01,
        pause_seconds=0.01,
    )
    job.save()

    def mark_then_fail(**kwargs):
        worker._atomic_write_text(
            worker._stop_marker_path(job.job_id),
            "2026-07-22T13:05:00",
        )
        raise RuntimeError("hardware failed after stop request")

    monkeypatch.setattr(worker, "modulate_hardware", mark_then_fail)

    outcome = worker.run_harmonization_worker(job.job_id)

    persisted = HarmonizationJob.load(job.job_id)
    assert outcome == "stopped"
    assert persisted is not None
    assert persisted.status == "running"
    assert persisted.current_phase == "impulse"
    assert persisted.end_time is None
    assert persisted.error_message is None
    assert persisted.cycles_completed == 0


def test_worker_respects_controller_stopped_record_without_marker(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_controller_stopped",
        target_frequency=432.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        status="stopped",
        current_phase="stopped",
        end_time="2026-07-22T13:10:00",
    )
    job.save()
    before = (tmp_path / f"{job.job_id}.json").read_bytes()
    modulation_calls: list[str] = []
    monkeypatch.setattr(
        worker,
        "modulate_hardware",
        lambda **kwargs: modulation_calls.append("modulate") or {},
    )

    outcome = worker.run_harmonization_worker(job.job_id)

    assert outcome == "stopped"
    assert (tmp_path / f"{job.job_id}.json").read_bytes() == before
    assert modulation_calls == []


def test_stop_injected_after_terminal_load_before_save_suppresses_completed_event(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_terminal_boundary",
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        status="running",
    )
    job.save()
    original_load = HarmonizationJob.load.__func__
    injected = False

    def load_then_inject_stop(cls, job_id):
        nonlocal injected
        loaded = original_load(cls, job_id)
        if not injected:
            injected = True
            worker._stop_marker_path(job_id).write_text(
                "2026-07-20T09:00:00",
                encoding="utf-8",
            )
        return loaded

    events = []
    monkeypatch.setattr(
        worker.HarmonizationJob,
        "load",
        classmethod(load_then_inject_stop),
    )
    monkeypatch.setattr(worker, "_append_event", lambda *args: events.append(args))

    committed = worker._commit_completed_job(job.job_id)

    assert committed is None
    persisted = original_load(HarmonizationJob, job.job_id)
    assert persisted is not None
    assert persisted.status == "running"
    assert worker._stop_marker_path(job.job_id).exists()
    assert events == []


def test_error_commit_does_not_publish_error_after_stop_wins(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_error_stop",
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        status="running",
    )
    job.save()
    original_load = worker.HarmonizationJob.load.__func__
    events: list[str] = []

    def load_then_stop(cls, job_id: str):
        loaded = original_load(cls, job_id)
        worker._atomic_write_text(worker._stop_marker_path(job_id), "2026-07-20T10:00:00")
        return loaded

    monkeypatch.setattr(worker.HarmonizationJob, "load", classmethod(load_then_stop))
    monkeypatch.setattr(
        worker,
        "_append_event",
        lambda job_id, event_type, payload: events.append(event_type),
    )

    assert worker._commit_error_job(job.job_id, "hardware failed") is None
    persisted = original_load(worker.HarmonizationJob, job.job_id)
    assert persisted is not None
    assert persisted.status == "running"
    assert worker._stop_marker_path(job.job_id).exists()
    assert events == []


def test_confirmed_error_commit_publishes_one_error_event(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    job = HarmonizationJob(
        job_id="harm_error_confirmed",
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        status="running",
    )
    job.save()
    events: list[str] = []
    monkeypatch.setattr(
        worker,
        "_append_event",
        lambda job_id, event_type, payload: events.append(event_type),
    )

    committed = worker._commit_error_job(job.job_id, "hardware failed")

    assert committed is not None
    assert committed.status == "error"
    assert HarmonizationJob.load(job.job_id).status == "error"
    assert events == ["error"]


@pytest.mark.parametrize("terminal_status", ["completed", "error"])
def test_terminal_commit_writes_offset_compatible_end_time(
    tmp_path,
    monkeypatch,
    terminal_status,
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    start_time = "2026-07-22T12:00:00+02:00"
    job = HarmonizationJob(
        job_id=f"harm_offset_{terminal_status}",
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        status="running",
        start_time=start_time,
        heartbeat_at=start_time,
        current_phase="running",
    )
    job.save()

    if terminal_status == "completed":
        committed = worker._commit_completed_job(job.job_id)
    else:
        committed = worker._commit_error_job(job.job_id, "hardware failed")

    assert committed is not None and committed.end_time is not None
    started = datetime.fromisoformat(start_time)
    ended = datetime.fromisoformat(committed.end_time)
    assert committed.status == terminal_status
    assert ended.utcoffset() == started.utcoffset()
    assert ended >= started
