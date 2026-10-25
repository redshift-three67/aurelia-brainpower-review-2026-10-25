from __future__ import annotations

from pathlib import Path
import asyncio
import errno
import gc
import json
import multiprocessing
import os
import signal
import sys
import subprocess
import threading
import time
import weakref
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from types import SimpleNamespace

import pytest

from apps.web import main as web_main
from apps.web import scan_jobs
from services import scan_process_gate
from apps.web.scan_jobs import (
    LocalScanJobService,
    ProcessAuthorityAmbiguousError,
    _LocalScanJob,
)
import inspect

from tests.test_web_authority_ids import INVALID_AUTHORITY_IDS


def _poll_recovered_scan_process(root: str, cwd: str, job_id: str, output) -> None:
    try:
        output.put(("ok", LocalScanJobService(Path(root), cwd=Path(cwd)).get(job_id)))
    except BaseException as exc:
        output.put(("error", f"{type(exc).__name__}: {exc}"))


_TERMINAL_SCAN_STATUSES = {"completed", "failed", "stopped"}


def _cleanup_owned_scan_job(
    writer: LocalScanJobService,
    root: Path,
    cwd: Path,
    job_id: str,
    *,
    terminal: bool,
    prior_error: BaseException | None,
) -> None:
    if terminal:
        return
    failures: list[BaseException] = []
    for attempt in range(2):
        service = writer if attempt == 0 else LocalScanJobService(root, cwd=cwd)
        try:
            stopped = service.stop(job_id)
            if stopped["status"] in _TERMINAL_SCAN_STATUSES:
                return
            failures.append(
                RuntimeError(f"scan cleanup remained {stopped['status']!r}")
            )
        except BaseException as exc:
            failures.append(exc)
    job = writer._jobs.get(job_id)
    if job is not None:
        try:
            scan_jobs._rollback_scan_authority(job)
            return
        except BaseException as exc:
            failures.append(exc)
    cleanup_error = BaseExceptionGroup("scan test cleanup failed", failures)
    if prior_error is not None:
        prior_error.add_note(str(cleanup_error))
        return
    raise cleanup_error


class FakeProcess:
    def __init__(self, returncode: int | None = None) -> None:
        self.returncode = returncode

    def poll(self) -> int | None:
        return self.returncode


class StoppableProcess(FakeProcess):
    pid = 43210

    def __init__(self) -> None:
        super().__init__(None)
        self.terminate_calls = 0
        self.kill_calls = 0
        self.wait_calls: list[int] = []

    def terminate(self) -> None:
        self.terminate_calls += 1
        self.returncode = -15

    def kill(self) -> None:
        self.kill_calls += 1
        self.returncode = -9

    def wait(self, timeout: int) -> int:
        self.wait_calls.append(timeout)
        return int(self.returncode or 0)


def test_local_scan_job_service_start_accepts_owner_id_parameter() -> None:
    """Regression-Test: LocalScanJobService.start() muss owner_id akzeptieren.

    Verhindert den Bug vom 2026-07-06, bei dem die Protocol-Signatur
    aktualisiert wurde, die Implementierung aber nicht - was zu einem
    500-Error beim Scan-Start fuehrte.
    """
    sig = inspect.signature(LocalScanJobService.start)
    assert "owner_id" in sig.parameters, (
        "LocalScanJobService.start() muss owner_id akzeptieren "
        "(siehe main.py scan_job_start)"
    )


def _job(
    service: LocalScanJobService,
    tmp_path: Path,
    stdout: str,
    *,
    returncode: int | None = None,
) -> _LocalScanJob:
    stdout_path = tmp_path / "job.stdout.log"
    stderr_path = tmp_path / "job.stderr.log"
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text("", encoding="utf-8")
    job = _LocalScanJob(
        job_id="job-1",
        command=["python", "-m", "apps.cli.main", "scan", "top3-scan"],
        process=FakeProcess(returncode),
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:00+00:00",
    )
    with service._process_lock(job.job_id):
        pass
    return job


def _register_job(service: LocalScanJobService, job: _LocalScanJob) -> None:
    with service._process_lock(job.job_id):
        pass
    service._jobs[job.job_id] = job


def _report_session_record(session_id: str, *, profile: str = "P1") -> str:
    payload = {
        "version": 1,
        "profile": profile,
        "session_id": session_id,
        "json_path": f"C:/reports/{profile}.json",
        "html_path": f"C:/reports/{profile}.html",
    }
    return "MORPHIC_MULTIPLEX_EXPORT_V1 " + json.dumps(payload)


def test_scan_job_snapshot_exposes_progress_phase_and_substeps(tmp_path: Path) -> None:
    service = LocalScanJobService(tmp_path)
    job = _job(
        service,
        tmp_path,
        "\n".join(
            [
                "[1/2] PHASE 1: Screening aller Haupt-Profile...",
                "[OK] TOP-5 RELEVANTE PROFILE:",
                "[2/2] PHASE 2: Vollstaendige Analyse der Top-5 Profile...",
                "[1/5] [OK] Vollstaendige Analyse: regulation",
                "Export gespeichert: C:/exports/report.json",
                "Trendbericht erstellt",
            ]
        ),
    )

    snapshot = service._snapshot(job)

    assert snapshot["status"] == "running"
    assert snapshot["progress_percent"] is not None
    assert 0 < float(snapshot["progress_percent"]) < 100
    assert snapshot["current_phase"] == "Phase 2"
    assert snapshot["current_substep"] == "Vollstaendige Analyse: regulation"
    assert snapshot["completed_substeps"] == [
        "PHASE 1: Screening aller Haupt-Profile",
        "TOP-5 RELEVANTE PROFILE",
        "PHASE 2: Vollstaendige Analyse der Top-5 Profile",
    ]


def test_snapshot_repolls_returncode_after_authority_converges(tmp_path, monkeypatch) -> None:
    service = LocalScanJobService(tmp_path)
    job = _job(service, tmp_path, "", returncode=None)

    class CompletingProcess(FakeProcess):
        def __init__(self) -> None:
            super().__init__(None)
            self.polls = 0

        def poll(self):
            self.polls += 1
            return None if self.polls == 1 else 0

    job.process = CompletingProcess()
    job.process_group_token = "stable-job"
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(scan_jobs, "_windows_job_active", lambda current: False)

    snapshot = service._snapshot(job)

    assert snapshot["status"] == "completed"
    assert job.process.polls == 2


@pytest.mark.parametrize(
    ("forced_status", "expected_probes"),
    [("completed", 0), ("rollback_failed", 2)],
)
def test_windows_snapshot_preserves_durable_status_when_authority_is_ambiguous(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    forced_status: str,
    expected_probes: int,
) -> None:
    service = LocalScanJobService(tmp_path)
    job = _job(service, tmp_path, "", returncode=0)
    job.job_id = f"snapshot-{forced_status}"
    job.process = StoppableProcess()
    job.process.returncode = 0
    job.process_create_time = 1.0
    job.process_group_id = job.process.pid
    job.process_group_token = "a" * 32
    job.forced_status = forced_status
    job.progress_percent = 100.0 if forced_status == "completed" else None
    job.updated_at = "2026-07-23T00:00:00+00:00"
    _register_job(service, job)
    service._persist_job(job)
    state_path = service._state_path(job.job_id)
    persisted_bytes = state_path.read_bytes()
    probes: list[str] = []
    original_probe = scan_jobs._windows_job_active

    def ambiguous_probe(active_job: _LocalScanJob) -> bool:
        if active_job is not job:
            return original_probe(active_job)
        probes.append(active_job.job_id)
        raise ProcessAuthorityAmbiguousError("ambiguous Windows authority")

    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(scan_jobs, "_utc_now", lambda: job.updated_at)
    monkeypatch.setattr(scan_jobs, "_windows_job_active", ambiguous_probe)

    for _ in range(2):
        snapshot = service._snapshot(job)
        assert snapshot["status"] == forced_status
        assert job.forced_status == forced_status
        assert state_path.read_bytes() == persisted_bytes

    assert len(probes) == expected_probes


def test_scan_job_snapshot_bounds_completed_substeps_and_marks_completed(
    tmp_path: Path,
) -> None:
    service = LocalScanJobService(tmp_path)
    job = _job(
        service,
        tmp_path,
        "\n".join(
            [
                "[1/5] Export vorbereiten",
                "[2/5] Harmonisierung vorbereiten",
                "[3/5] Trendbericht erstellt",
                "[4/5] Deutungsbericht erstellt",
                "[5/5] Remedy und Synergy abgeschlossen",
            ]
        ),
        returncode=0,
    )

    snapshot = service._snapshot(job)

    assert snapshot["status"] == "completed"
    assert snapshot["progress_percent"] == 100.0
    assert snapshot["current_phase"] == "Nachbereitung"
    assert snapshot["current_substep"] == "Trendbericht erstellt"
    assert snapshot["completed_substeps"] == [
        "Export vorbereiten",
        "Harmonisierung vorbereiten",
        "Trendbericht erstellt",
    ]


def test_scan_job_snapshot_buffers_partial_lines_between_polls(tmp_path: Path) -> None:
    service = LocalScanJobService(tmp_path)
    stdout_path = tmp_path / "job.stdout.log"
    stderr_path = tmp_path / "job.stderr.log"
    stdout_path.write_text("[1/2] PHASE 1: Screen", encoding="utf-8")
    stderr_path.write_text("", encoding="utf-8")
    job = _LocalScanJob(
        job_id="job-2",
        command=["python", "-m", "apps.cli.main", "scan", "top3-scan"],
        process=FakeProcess(None),
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:00+00:00",
    )

    first = service._snapshot(job)
    assert first["current_phase"] is None
    assert first["current_substep"] is None

    stdout_path.write_text(
        "[1/2] PHASE 1: Screening aller Haupt-Profile...\n[OK] TOP-5 RELEVANTE PROFILE:\n",
        encoding="utf-8",
    )
    second = service._snapshot(job)

    assert second["current_phase"] == "Phase 1"
    assert second["current_substep"] == "TOP-5 RELEVANTE PROFILE"
    assert "PHASE 1: Screening aller Haupt-Profile" in second["completed_substeps"]


def test_report_session_authority_survives_incremental_completion_and_recovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    first_record = _report_session_record("session-a", profile="P1")
    second_record = _report_session_record("session-a", profile="P2")
    job = _job(service, root, "", returncode=None)
    job.process = StoppableProcess()
    job.process_create_time = 1.0
    job.process_group_id = job.process.pid
    job.process_group_token = "a" * 32
    job.stdout_path = service._stdout_path(job.job_id)
    job.stderr_path = service._stderr_path(job.job_id)
    job.stdout_path.write_text(first_record + "\n", encoding="utf-8")
    job.stderr_path.write_text("", encoding="utf-8")
    _register_job(service, job)
    monkeypatch.setattr(
        scan_jobs,
        "_windows_job_active",
        lambda active_job: active_job.process.poll() is None,
    )

    running = service._snapshot(job)
    assert running["report_session_id"] == "session-a"

    with job.stdout_path.open("a", encoding="utf-8", newline="") as handle:
        handle.write(second_record + "\n")
    job.process.returncode = 0
    completed = service._snapshot(job)
    recovered = LocalScanJobService(root, cwd=tmp_path).get(job.job_id)

    assert job.stdout_path.read_text(encoding="utf-8").splitlines() == [
        first_record,
        second_record,
    ]
    assert completed["report_session_id"] == "session-a"
    assert recovered["report_session_id"] == "session-a"


def test_conflicting_report_sessions_remain_unresolved_after_recovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    first_record = _report_session_record("session-a", profile="P1")
    second_record = _report_session_record("session-b", profile="P2")
    job = _job(service, root, "", returncode=None)
    job.process = StoppableProcess()
    job.process_create_time = 1.0
    job.process_group_id = job.process.pid
    job.process_group_token = "b" * 32
    job.stdout_path = service._stdout_path(job.job_id)
    job.stderr_path = service._stderr_path(job.job_id)
    job.stdout_path.write_text(first_record + "\n", encoding="utf-8")
    job.stderr_path.write_text("", encoding="utf-8")
    _register_job(service, job)
    monkeypatch.setattr(
        scan_jobs,
        "_windows_job_active",
        lambda active_job: active_job.process.poll() is None,
    )

    running = service._snapshot(job)
    assert running["report_session_id"] == "session-a"

    with job.stdout_path.open("a", encoding="utf-8", newline="") as handle:
        handle.write(second_record + "\n")
    job.process.returncode = 0
    completed = service._snapshot(job)
    recovered = LocalScanJobService(root, cwd=tmp_path).get(job.job_id)

    assert job.stdout_path.read_text(encoding="utf-8").splitlines() == [
        first_record,
        second_record,
    ]
    assert completed["report_session_id"] is None
    assert recovered["report_session_id"] is None


def test_terminal_report_session_marker_without_final_newline_is_recovered(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    terminal_record = _report_session_record("session-a")
    job = _job(service, root, "", returncode=None)
    job.process = StoppableProcess()
    job.process_create_time = 1.0
    job.process_group_id = job.process.pid
    job.process_group_token = "c" * 32
    job.stdout_path = service._stdout_path(job.job_id)
    job.stderr_path = service._stderr_path(job.job_id)
    job.stdout_path.write_text("Analyse gestartet\n", encoding="utf-8")
    job.stderr_path.write_text("", encoding="utf-8")
    _register_job(service, job)
    monkeypatch.setattr(
        scan_jobs,
        "_windows_job_active",
        lambda active_job: active_job.process.poll() is None,
    )

    running = service._snapshot(job)
    assert running["report_session_id"] is None

    with job.stdout_path.open("a", encoding="utf-8", newline="") as handle:
        handle.write(terminal_record)
    job.process.returncode = 0
    completed = service._snapshot(job)
    recovered = LocalScanJobService(root, cwd=tmp_path).get(job.job_id)

    assert job.stdout_path.read_text(encoding="utf-8").endswith(terminal_record)
    assert completed["report_session_id"] == "session-a"
    assert recovered["report_session_id"] == "session-a"


def test_report_session_marker_preserves_split_utf8_codepoint_across_polls(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    payload = {
        "version": 1,
        "profile": "P1",
        "session_id": "s€x",
        "json_path": "C:/reports/P1.json",
        "html_path": "C:/reports/P1.html",
    }
    record = "MORPHIC_MULTIPLEX_EXPORT_V1 " + json.dumps(
        payload,
        ensure_ascii=False,
    )
    encoded = (record + "\n").encode("utf-8")
    euro_start = encoded.index("€".encode("utf-8"))
    split_at = euro_start + 1
    job = _job(service, root, "", returncode=None)
    job.process = StoppableProcess()
    job.process_create_time = 1.0
    job.process_group_id = job.process.pid
    job.process_group_token = "d" * 32
    job.stdout_path = service._stdout_path(job.job_id)
    job.stderr_path = service._stderr_path(job.job_id)
    job.stdout_path.write_bytes(encoded[:split_at])
    job.stderr_path.write_text("", encoding="utf-8")
    _register_job(service, job)
    monkeypatch.setattr(
        scan_jobs,
        "_windows_job_active",
        lambda active_job: active_job.process.poll() is None,
    )

    running = service._snapshot(job)

    assert running["report_session_id"] is None
    assert job.stdout_pos == euro_start

    with job.stdout_path.open("ab") as handle:
        handle.write(encoded[split_at:])
    job.process.returncode = 0
    completed = service._snapshot(job)
    recovered = LocalScanJobService(root, cwd=tmp_path).get(job.job_id)

    assert job.report_session_ids == {"s€x"}
    assert all("\ufffd" not in session_id for session_id in job.report_session_ids)
    assert completed["report_session_id"] == "s€x"
    assert recovered["report_session_id"] == "s€x"


def test_surrogate_report_session_marker_is_invalid_and_job_state_persists(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    record = _report_session_record("\ud800")
    job = _job(service, root, "", returncode=None)
    job.process = StoppableProcess()
    job.process.returncode = 0
    job.process_create_time = 1.0
    job.process_group_id = job.process.pid
    job.process_group_token = "e" * 32
    job.stdout_path = service._stdout_path(job.job_id)
    job.stderr_path = service._stderr_path(job.job_id)
    job.stdout_path.write_text(record + "\n", encoding="utf-8")
    job.stderr_path.write_text("", encoding="utf-8")
    _register_job(service, job)
    monkeypatch.setattr(scan_jobs, "_windows_job_active", lambda _job: False)

    completed = service._snapshot(job)
    persisted = json.loads(service._state_path(job.job_id).read_text(encoding="utf-8"))

    assert completed["report_session_id"] is None
    assert job.report_session_ids == set()
    assert job.report_session_invalid is True
    assert persisted["report_session_ids"] == []
    assert persisted["report_session_invalid"] is True


def test_scan_job_snapshot_does_not_flush_recognizable_partial_marker(
    tmp_path: Path,
) -> None:
    service = LocalScanJobService(tmp_path)
    stdout_path = tmp_path / "job3.stdout.log"
    stderr_path = tmp_path / "job3.stderr.log"
    stdout_path.write_text("Trendbericht", encoding="utf-8")
    stderr_path.write_text("", encoding="utf-8")
    job = _LocalScanJob(
        job_id="job-3",
        command=["python", "-m", "apps.cli.main", "scan", "top3-scan"],
        process=FakeProcess(None),
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:00+00:00",
    )

    first = service._snapshot(job)
    assert first["current_substep"] is None

    stdout_path.write_text("Trendbericht erstellt\n", encoding="utf-8")
    second = service._snapshot(job)
    assert second["current_substep"] == "Trendbericht erstellt"


def test_scan_stop_does_not_report_success_when_windows_job_termination_fails(
    tmp_path: Path,
    monkeypatch,
) -> None:
    service = LocalScanJobService(tmp_path)
    process = StoppableProcess()
    job = _job(service, tmp_path, "")
    job.job_id = "tree-stop-win"
    job.process = process
    _register_job(service, job)
    calls: list[_LocalScanJob] = []

    def fail_job_termination(active_job: _LocalScanJob) -> None:
        calls.append(active_job)
        raise OSError("stable Windows job termination failed")

    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(scan_jobs, "_windows_job_active", lambda active_job: True)
    monkeypatch.setattr(scan_jobs, "_terminate_windows_job", fail_job_termination)
    monkeypatch.setattr(
        scan_jobs.subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("numeric taskkill must not be used")
        ),
    )

    with pytest.raises(RuntimeError, match="tree stop was not confirmed"):
        service.stop(job.job_id)

    assert calls == [job]
    assert process.terminate_calls == 0
    assert job.forced_status == "authority_ambiguous"


def test_windows_stop_and_rollback_use_stable_job_authority_not_numeric_pid(
    tmp_path: Path,
    monkeypatch,
) -> None:
    service = LocalScanJobService(tmp_path)
    process = StoppableProcess()
    job = _job(service, tmp_path, "", returncode=None)
    job.job_id = "stable-windows-job"
    job.process = process
    job.windows_job_handle = 700
    job.process_group_token = "expected-token"
    _register_job(service, job)
    calls: list[tuple[int | None, int]] = []

    def terminate_job(active_job: _LocalScanJob) -> None:
        calls.append((active_job.windows_job_handle, active_job.process.pid))
        active_job.process.pid = 99999  # simulate numeric PID reuse after authority capture
        active_job.process.returncode = 1

    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(
        scan_jobs,
        "_windows_job_active",
        lambda active_job: active_job.process.poll() is None,
    )
    monkeypatch.setattr(scan_jobs, "_terminate_windows_job", terminate_job)
    monkeypatch.setattr(
        scan_jobs,
        "_converge_windows_authority",
        lambda active_job: terminate_job(active_job),
    )
    monkeypatch.setattr(
        scan_jobs.subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("numeric taskkill must not be used")
        ),
    )

    snapshot = service.stop(job.job_id)
    assert snapshot["status"] == "stopped"
    assert calls == [(700, 43210)]

    rollback_process = StoppableProcess()
    rollback_process.returncode = 1
    rollback_job = _job(service, tmp_path, "", returncode=None)
    rollback_job.process = rollback_process
    rollback_job.windows_job_handle = 701
    rollback_job.process_group_token = "rollback-token"
    scan_jobs._rollback_scan_authority(rollback_job)
    assert calls[-1] == (701, 43210)


def test_windows_unreadable_job_authority_is_persisted_without_termination(
    tmp_path: Path,
    monkeypatch,
) -> None:
    service = LocalScanJobService(tmp_path)
    job = _job(service, tmp_path, "", returncode=1)
    job.job_id = "unreadable-windows-job"
    process = StoppableProcess()
    process.returncode = 1
    job.process = process
    job.process_group_token = "expected-token"
    _register_job(service, job)
    terminated: list[str] = []
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(
        scan_jobs,
        "_windows_job_active",
        lambda active_job: (_ for _ in ()).throw(
            scan_jobs.ProcessAuthorityAmbiguousError("unreadable")
        ),
    )
    monkeypatch.setattr(
        scan_jobs,
        "_terminate_windows_job",
        lambda active_job: terminated.append(active_job.job_id),
    )

    with pytest.raises(scan_jobs.ProcessAuthorityAmbiguousError):
        service.stop(job.job_id)
    assert terminated == []
    persisted = json.loads(service._state_path(job.job_id).read_text(encoding="utf-8"))
    assert persisted["forced_status"] == "authority_ambiguous"


def test_windows_job_assignment_preserves_primary_and_close_failures(monkeypatch) -> None:
    import ctypes

    class Function:
        def __init__(self, result: int) -> None:
            self.result = result
            self.argtypes = None
            self.restype = None

        def __call__(self, *args):
            return self.result

    class Kernel32:
        CreateJobObjectW = Function(700)
        AssignProcessToJobObject = Function(0)
        CloseHandle = Function(0)

    errors = iter([5, 6])
    monkeypatch.setattr(ctypes, "WinDLL", lambda *args, **kwargs: Kernel32())
    monkeypatch.setattr(ctypes, "get_last_error", lambda: next(errors))
    process = type("Process", (), {"_handle": 900})()

    with pytest.raises(ExceptionGroup) as captured:
        scan_jobs._create_windows_job(process, "expected-token")
    assert [error.errno for error in captured.value.exceptions] == [5, 6]


def test_windows_job_retention_uses_exact_duplicate_handle_contract(monkeypatch) -> None:
    import ctypes

    calls: list[tuple[object, ...]] = []

    class Function:
        argtypes = None
        restype = None

        def __init__(self, result=1, callback=None) -> None:
            self.result = result
            self.callback = callback

        def __call__(self, *args):
            if self.callback is not None:
                self.callback(*args)
            return self.result

    class Kernel32:
        CreateJobObjectW = Function(700)
        AssignProcessToJobObject = Function(1)
        CloseHandle = Function(1)
        GetCurrentProcess = Function(111)
        DuplicateHandle = Function(1, lambda *args: calls.append(args))

    monkeypatch.setattr(ctypes, "WinDLL", lambda *args, **kwargs: Kernel32())
    process = type("Process", (), {"_handle": 900})()

    assert scan_jobs._create_windows_job(process, "expected-token") == 700
    assert len(calls) == 1
    source_process, source_handle, target_process, _, access, inherit, options = calls[0]
    value = lambda item: item.value if hasattr(item, "value") else item
    assert value(source_process) == 111
    assert value(source_handle) == 700
    assert value(target_process) == 900
    assert access == 0
    assert inherit is False
    assert options == 0x00000002


def test_windows_job_retention_preserves_duplicate_and_close_failures(monkeypatch) -> None:
    import ctypes

    class Function:
        argtypes = None
        restype = None

        def __init__(self, result=1) -> None:
            self.result = result

        def __call__(self, *args):
            return self.result

    class Kernel32:
        CreateJobObjectW = Function(700)
        AssignProcessToJobObject = Function(1)
        CloseHandle = Function(0)
        GetCurrentProcess = Function(111)
        DuplicateHandle = Function(0)

    errors = iter([5, 6])
    monkeypatch.setattr(ctypes, "WinDLL", lambda *args, **kwargs: Kernel32())
    monkeypatch.setattr(ctypes, "get_last_error", lambda: next(errors))
    process = type("Process", (), {"_handle": 900})()

    with pytest.raises(ExceptionGroup) as captured:
        scan_jobs._create_windows_job(process, "expected-token")
    assert [error.errno for error in captured.value.exceptions] == [5, 6]


def test_windows_job_start_preserves_retention_kill_and_wait_failures(
    tmp_path: Path,
    monkeypatch,
) -> None:
    class Process:
        pid = 4242
        _handle = 900

        def kill(self) -> None:
            raise OSError("kill failed")

        def wait(self, timeout: int) -> int:
            raise subprocess.TimeoutExpired("gate", timeout)

    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(scan_jobs.subprocess, "Popen", lambda *args, **kwargs: Process())
    monkeypatch.setattr(scan_jobs, "_process_create_time", lambda pid: 1.0)
    monkeypatch.setattr(
        scan_jobs,
        "_create_windows_job",
        lambda *args: (_ for _ in ()).throw(RuntimeError("retention failed")),
    )

    with pytest.raises(BaseExceptionGroup) as captured:
        LocalScanJobService(tmp_path / "jobs", cwd=tmp_path).start(["python", "-V"])
    assert len(captured.value.exceptions) == 3
    assert str(captured.value.exceptions[0]) == "retention failed"
    assert str(captured.value.exceptions[1]) == "kill failed"
    assert isinstance(captured.value.exceptions[2], subprocess.TimeoutExpired)


def test_windows_missing_creation_time_preserves_kill_and_wait_failures(
    tmp_path: Path,
    monkeypatch,
) -> None:
    class Process:
        pid = 4242
        _handle = 900

        def kill(self) -> None:
            raise OSError("kill failed")

        def wait(self, timeout: int) -> int:
            raise subprocess.TimeoutExpired("gate", timeout)

    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(scan_jobs.subprocess, "Popen", lambda *args, **kwargs: Process())
    monkeypatch.setattr(scan_jobs, "_process_create_time", lambda pid: None)

    with pytest.raises(BaseExceptionGroup) as captured:
        LocalScanJobService(tmp_path / "jobs", cwd=tmp_path).start(["python", "-V"])
    assert len(captured.value.exceptions) == 3
    assert str(captured.value.exceptions[0]) == "scan process identity could not be established"
    assert str(captured.value.exceptions[1]) == "kill failed"
    assert isinstance(captured.value.exceptions[2], subprocess.TimeoutExpired)


def test_posix_start_identity_failure_uses_preopened_pidfd(
    tmp_path: Path,
    monkeypatch,
) -> None:
    class Process:
        pid = 4242

        def wait(self, timeout: int) -> int:
            return -9

        def kill(self) -> None:
            raise AssertionError("numeric Popen.kill must not be used")

    sent: list[tuple[int, int]] = []
    closed: list[int] = []
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(scan_jobs.signal, "SIGKILL", 9, raising=False)
    monkeypatch.setattr(scan_jobs.subprocess, "Popen", lambda *args, **kwargs: Process())
    monkeypatch.setattr(scan_jobs, "_open_pidfd", lambda pid: 117)
    monkeypatch.setattr(scan_jobs, "_process_create_time", lambda pid: None)
    monkeypatch.setattr(
        scan_jobs.signal,
        "pidfd_send_signal",
        lambda fd, sig, info, flags: sent.append((fd, sig)),
        raising=False,
    )
    monkeypatch.setattr(scan_jobs.os, "close", lambda fd: closed.append(fd))

    with pytest.raises(RuntimeError, match="identity could not be established"):
        LocalScanJobService(tmp_path / "jobs", cwd=tmp_path).start(["python", "-V"])
    assert sent == [(117, getattr(signal, "SIGKILL", 9))]
    assert closed == [117]


@pytest.mark.parametrize("failure_stage", ["signal", "close"])
def test_posix_start_identity_failure_always_closes_and_reaps(
    tmp_path: Path,
    monkeypatch,
    failure_stage: str,
) -> None:
    class Process:
        pid = 4242

        def __init__(self) -> None:
            self.waits: list[int] = []

        def wait(self, timeout: int) -> int:
            self.waits.append(timeout)
            return -9

    process = Process()
    closed: list[int] = []
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(scan_jobs.signal, "SIGKILL", 9, raising=False)
    monkeypatch.setattr(scan_jobs.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(scan_jobs, "_open_pidfd", lambda pid: 117)
    monkeypatch.setattr(scan_jobs, "_process_create_time", lambda pid: None)

    def send(fd, sig, info, flags) -> None:
        if failure_stage == "signal":
            raise OSError("signal failed")

    def close(fd: int) -> None:
        closed.append(fd)
        if failure_stage == "close":
            raise OSError("close failed")

    monkeypatch.setattr(scan_jobs.signal, "pidfd_send_signal", send, raising=False)
    monkeypatch.setattr(scan_jobs.os, "close", close)

    with pytest.raises(BaseExceptionGroup) as captured:
        LocalScanJobService(tmp_path / "jobs", cwd=tmp_path).start(["python", "-V"])
    assert isinstance(captured.value.exceptions[0], RuntimeError)
    assert closed == [117]
    assert process.waits == [35]


def test_posix_pidfd_acquisition_failure_preserves_wait_timeout(
    tmp_path: Path,
    monkeypatch,
) -> None:
    class Process:
        pid = 4242

        def wait(self, timeout: int) -> int:
            raise subprocess.TimeoutExpired("gate", timeout)

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(scan_jobs.subprocess, "Popen", lambda *args, **kwargs: Process())
    monkeypatch.setattr(scan_jobs, "_open_pidfd", lambda pid: (_ for _ in ()).throw(OSError("pidfd failed")))

    with pytest.raises(BaseExceptionGroup) as captured:
        LocalScanJobService(tmp_path / "jobs", cwd=tmp_path).start(["python", "-V"])
    assert isinstance(captured.value.exceptions[0], scan_jobs.ProcessAuthorityAmbiguousError)
    assert isinstance(captured.value.exceptions[1], subprocess.TimeoutExpired)


def test_posix_creation_time_exception_closes_and_reaps_startup_pidfd(
    tmp_path: Path,
    monkeypatch,
) -> None:
    class Process:
        pid = 4242

        def __init__(self) -> None:
            self.waited = False

        def wait(self, timeout: int) -> int:
            self.waited = True
            return -9

    process = Process()
    closed: list[int] = []
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(scan_jobs.signal, "SIGKILL", 9, raising=False)
    monkeypatch.setattr(scan_jobs.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(scan_jobs, "_open_pidfd", lambda pid: 117)
    monkeypatch.setattr(scan_jobs, "_process_create_time", lambda pid: (_ for _ in ()).throw(OSError("identity read failed")))
    monkeypatch.setattr(scan_jobs.signal, "pidfd_send_signal", lambda *args: None, raising=False)
    monkeypatch.setattr(scan_jobs.os, "close", lambda fd: closed.append(fd))

    with pytest.raises(OSError, match="identity read failed"):
        LocalScanJobService(tmp_path / "jobs", cwd=tmp_path).start(["python", "-V"])
    assert closed == [117]
    assert process.waited is True


def test_scan_stop_escalates_the_entire_posix_process_group(tmp_path: Path, monkeypatch) -> None:
    service = LocalScanJobService(tmp_path)
    process = StoppableProcess()
    job = _job(service, tmp_path, "")
    job.job_id = "tree-stop-posix"
    job.process = process
    job.process_group_id = process.pid + 1
    _register_job(service, job)
    signals: list[int] = []

    def signal_stable_authority(active_job, sent_signal: int) -> int:
        assert active_job is job
        signals.append(sent_signal)
        if sent_signal == 9:
            process.returncode = -sent_signal
        return 1

    def fake_wait(timeout: int) -> int:
        process.wait_calls.append(timeout)
        if process.returncode is None:
            raise scan_jobs.subprocess.TimeoutExpired("synthetic", timeout)
        return process.returncode

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(scan_jobs.signal, "SIGKILL", 9, raising=False)
    monkeypatch.setattr(scan_jobs, "_signal_posix_authority", signal_stable_authority)
    monkeypatch.setattr(scan_jobs, "_process_group_alive", lambda pgid, token: process.returncode is None)
    monkeypatch.setattr(process, "wait", fake_wait)

    snapshot = service.stop(job.job_id)

    assert signals == [15, 9]
    assert process.terminate_calls == 0
    assert snapshot["status"] == "stopped"


def test_recovered_scan_remains_running_when_supervisor_exited_but_posix_group_is_live(
    tmp_path: Path,
    monkeypatch,
) -> None:
    service = LocalScanJobService(tmp_path)
    job = _job(service, tmp_path, "", returncode=1)
    job.process_group_id = 4242
    job.process_group_token = "expected-token"
    job.start_released = True
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(
        scan_jobs,
        "_process_group_alive",
        lambda pgid, token: pgid == 4242 and token == "expected-token",
    )

    snapshot = service._snapshot(job)

    assert snapshot["status"] == "running"


def test_scan_stop_controls_live_posix_group_after_supervisor_exit(tmp_path: Path, monkeypatch) -> None:
    service = LocalScanJobService(tmp_path)
    job = _job(service, tmp_path, "", returncode=1)
    job.job_id = "recovered-group-stop"
    process = StoppableProcess()
    process.returncode = 1
    job.process = process
    job.process_group_id = 4242
    job.process_group_token = "expected-token"
    job.start_released = True
    _register_job(service, job)
    signals: list[int] = []
    group_active = {"value": True}
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(
        scan_jobs,
        "_process_group_alive",
        lambda pgid, token: group_active["value"] and token == "expected-token",
    )

    def signal_stable_authority(active_job, sent_signal: int) -> int:
        assert active_job is job
        signals.append(sent_signal)
        group_active["value"] = False
        return 1

    monkeypatch.setattr(
        scan_jobs,
        "_signal_posix_authority",
        signal_stable_authority,
        raising=False,
    )
    monkeypatch.setattr(
        scan_jobs.os,
        "killpg",
        lambda *args: pytest.fail("supervisor-less stop must never use numeric killpg"),
        raising=False,
    )

    snapshot = service.stop(job.job_id)

    assert signals == [signal.SIGTERM]
    assert snapshot["status"] == "stopped"


def test_foreign_reused_posix_group_is_not_adopted_or_killed(tmp_path: Path, monkeypatch) -> None:
    service = LocalScanJobService(tmp_path)
    job = _job(service, tmp_path, "", returncode=1)
    job.job_id = "foreign-group"
    process = StoppableProcess()
    process.returncode = 1
    job.process = process
    job.process_group_id = 4242
    job.process_group_token = "expected-token"
    job.start_released = True
    _register_job(service, job)
    signals = []
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(scan_jobs, "_process_group_alive", lambda pgid, token: False)
    monkeypatch.setattr(
        scan_jobs.os,
        "killpg",
        lambda pgid, sent_signal: signals.append((pgid, sent_signal)),
        raising=False,
    )

    snapshot = service.stop(job.job_id)

    assert snapshot["status"] == "failed"
    assert signals == []


def test_posix_environment_access_denied_is_fail_closed(tmp_path: Path, monkeypatch) -> None:
    class Process:
        info = {"pid": 17, "status": "running"}

        def environ(self):
            raise scan_jobs.psutil.AccessDenied(17)

    closed: list[int] = []
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(scan_jobs.psutil, "process_iter", lambda attrs: [Process()])
    monkeypatch.setattr(scan_jobs.os, "getpgid", lambda pid: 4242, raising=False)
    monkeypatch.setattr(scan_jobs, "_open_pidfd", lambda pid: 117)
    monkeypatch.setattr(scan_jobs.os, "close", lambda fd: closed.append(fd))

    with pytest.raises(scan_jobs.ProcessAuthorityAmbiguousError):
        scan_jobs._process_group_alive(4242, "expected-token")
    with pytest.raises(scan_jobs.ProcessAuthorityAmbiguousError):
        scan_jobs._token_process_pidfds(4242, "expected-token")
    assert closed == []


def test_supervisorless_posix_signal_rejects_mixed_token_population(
    tmp_path: Path,
    monkeypatch,
) -> None:
    class Process:
        def __init__(self, pid: int, token: str) -> None:
            self.info = {"pid": pid, "status": "running"}
            self._token = token

        def environ(self):
            return {"MORPHIC_SCAN_GROUP_TOKEN": self._token}

    job = _job(LocalScanJobService(tmp_path), tmp_path, "", returncode=1)
    job.process_group_id = 4242
    job.process_group_token = "expected-token"
    sent: list[tuple[int, int]] = []
    closed: list[int] = []
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(
        scan_jobs.psutil,
        "process_iter",
        lambda attrs: [Process(11, "expected-token"), Process(12, "foreign-token")],
    )
    monkeypatch.setattr(scan_jobs.os, "getpgid", lambda pid: 4242, raising=False)
    monkeypatch.setattr(scan_jobs, "_open_pidfd", lambda pid: pid + 100)
    monkeypatch.setattr(scan_jobs.os, "close", lambda fd: closed.append(fd))
    monkeypatch.setattr(
        scan_jobs.signal,
        "pidfd_send_signal",
        lambda fd, sig, info, flags: sent.append((fd, sig)),
        raising=False,
    )

    with pytest.raises(scan_jobs.ProcessAuthorityAmbiguousError):
        scan_jobs._signal_posix_authority(job, signal.SIGTERM)

    assert sent == []
    assert sorted(closed) == [111]


def test_posix_signal_and_close_failures_are_both_preserved(
    tmp_path: Path,
    monkeypatch,
) -> None:
    job = _job(LocalScanJobService(tmp_path), tmp_path, "")
    job.process_create_time = None
    job.process.returncode = 1
    job.process_group_token = "expected-token"
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(scan_jobs, "_token_process_pidfds", lambda *args: [117])
    monkeypatch.setattr(
        scan_jobs.signal,
        "pidfd_send_signal",
        lambda *args: (_ for _ in ()).throw(OSError(errno.EIO, "signal failed")),
        raising=False,
    )
    monkeypatch.setattr(
        scan_jobs.os,
        "close",
        lambda fd: (_ for _ in ()).throw(OSError(errno.EBADF, "close failed")),
    )

    with pytest.raises(BaseExceptionGroup) as captured:
        scan_jobs._signal_posix_authority(job, signal.SIGTERM)
    assert len(captured.value.exceptions) == 2
    assert isinstance(captured.value.exceptions[0], BaseExceptionGroup)
    assert isinstance(captured.value.exceptions[0].exceptions[0], OSError)
    assert isinstance(captured.value.exceptions[1], OSError)


def test_token_discovery_preserves_primary_and_prior_handle_close_failure(
    monkeypatch,
) -> None:
    class Current:
        def username(self) -> str:
            return "owner"

    class Candidate:
        def __init__(self, pid: int, *, denied: bool = False) -> None:
            self.info = {"pid": pid, "status": "running", "username": "owner"}
            self.denied = denied

        def environ(self) -> dict[str, str]:
            if self.denied:
                raise scan_jobs.psutil.AccessDenied(self.info["pid"])
            return {"MORPHIC_SCAN_GROUP_TOKEN": "expected-token"}

    monkeypatch.setattr(scan_jobs.psutil, "Process", lambda pid: Current())
    monkeypatch.setattr(
        scan_jobs.psutil,
        "process_iter",
        lambda attrs: [Candidate(11), Candidate(12, denied=True)],
    )
    monkeypatch.setattr(scan_jobs, "_open_pidfd", lambda pid: 111)
    monkeypatch.setattr(
        scan_jobs.os,
        "close",
        lambda fd: (_ for _ in ()).throw(OSError(errno.EBADF, "close failed")),
    )

    with pytest.raises(BaseExceptionGroup) as captured:
        scan_jobs._token_process_pidfds(None, "expected-token")
    assert isinstance(captured.value.exceptions[0], scan_jobs.ProcessAuthorityAmbiguousError)
    assert isinstance(captured.value.exceptions[1], OSError)


def test_target_group_access_denied_aborts_entire_signal_round(
    tmp_path: Path,
    monkeypatch,
) -> None:
    class Process:
        def __init__(self, pid: int, token: str | None) -> None:
            self.info = {"pid": pid, "status": "running"}
            self._token = token

        def environ(self):
            if self._token is None:
                raise scan_jobs.psutil.AccessDenied(self.info["pid"])
            return {"MORPHIC_SCAN_GROUP_TOKEN": self._token}

    job = _job(LocalScanJobService(tmp_path), tmp_path, "", returncode=1)
    job.process_group_id = 4242
    job.process_group_token = "expected-token"
    sent: list[int] = []
    closed: list[int] = []
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(
        scan_jobs.psutil,
        "process_iter",
        lambda attrs: [Process(11, "expected-token"), Process(12, None)],
    )
    monkeypatch.setattr(scan_jobs.os, "getpgid", lambda pid: 4242, raising=False)
    monkeypatch.setattr(scan_jobs, "_open_pidfd", lambda pid: pid + 100)
    monkeypatch.setattr(scan_jobs.os, "close", lambda fd: closed.append(fd))
    monkeypatch.setattr(
        scan_jobs.signal,
        "pidfd_send_signal",
        lambda fd, sig, info, flags: sent.append(fd),
        raising=False,
    )

    with pytest.raises(scan_jobs.ProcessAuthorityAmbiguousError):
        scan_jobs._signal_posix_authority(job, signal.SIGTERM)

    assert sent == []
    assert sorted(closed) == [111]


@pytest.mark.parametrize("later_token", [None, "wrong-token"])
def test_full_group_inspection_rejects_later_unproven_member(
    monkeypatch,
    later_token,
) -> None:
    class Process:
        def __init__(self, pid: int, token) -> None:
            self.info = {"pid": pid, "status": "running"}
            self.token = token

        def environ(self):
            if self.token is None:
                raise scan_jobs.psutil.AccessDenied(self.info["pid"])
            return {"MORPHIC_SCAN_GROUP_TOKEN": self.token}

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(scan_jobs.os, "getpgid", lambda pid: 4242, raising=False)
    monkeypatch.setattr(
        scan_jobs.psutil,
        "process_iter",
        lambda attrs: [Process(11, "expected-token"), Process(12, later_token)],
    )

    with pytest.raises(scan_jobs.ProcessAuthorityAmbiguousError):
        scan_jobs._process_group_alive(4242, "expected-token")


@pytest.mark.parametrize(
    ("actual", "expected", "result"),
    [(1.0, 1.0, True), (2.0, 1.0, False), (1.0, None, False)],
)
def test_strict_process_identity_readable_matrix(
    monkeypatch,
    actual: float,
    expected: float | None,
    result: bool,
) -> None:
    class Process:
        def create_time(self) -> float:
            return actual

    monkeypatch.setattr(scan_jobs.psutil, "Process", lambda pid: Process())
    assert scan_jobs._strict_process_identity_matches(11, expected) is result


@pytest.mark.parametrize("exit_kind", ["no-such", "lookup", "esrch"])
def test_strict_process_identity_confirmed_exit_matrix(monkeypatch, exit_kind: str) -> None:
    class Process:
        def create_time(self) -> float:
            if exit_kind == "no-such":
                raise scan_jobs.psutil.NoSuchProcess(11)
            if exit_kind == "lookup":
                raise ProcessLookupError("gone")
            raise OSError(errno.ESRCH, "gone")

    monkeypatch.setattr(scan_jobs.psutil, "Process", lambda pid: Process())
    assert scan_jobs._strict_process_identity_matches(11, 1.0) is None


@pytest.mark.parametrize("failure_kind", ["access-denied", "eio", "generic"])
def test_strict_process_identity_non_exit_errors_propagate(
    monkeypatch,
    failure_kind: str,
) -> None:
    class Process:
        def create_time(self) -> float:
            if failure_kind == "access-denied":
                raise scan_jobs.psutil.AccessDenied(11)
            if failure_kind == "eio":
                raise OSError(errno.EIO, "unreadable")
            raise ValueError("invalid identity")

    monkeypatch.setattr(scan_jobs.psutil, "Process", lambda pid: Process())
    with pytest.raises((scan_jobs.psutil.AccessDenied, OSError, ValueError)):
        scan_jobs._strict_process_identity_matches(11, 1.0)


@pytest.mark.parametrize("failure_errno", [errno.EACCES, errno.EPERM, errno.EMFILE])
def test_pidfd_acquisition_only_ignores_confirmed_exit(
    monkeypatch,
    failure_errno: int,
) -> None:
    class Process:
        info = {"pid": 11, "status": "running"}

        def environ(self):
            return {"MORPHIC_SCAN_GROUP_TOKEN": "expected-token"}

    monkeypatch.setattr(scan_jobs.psutil, "process_iter", lambda attrs: [Process()])
    monkeypatch.setattr(scan_jobs.os, "getpgid", lambda pid: 4242, raising=False)
    monkeypatch.setattr(
        scan_jobs,
        "_open_pidfd",
        lambda pid: (_ for _ in ()).throw(OSError(failure_errno, "denied")),
    )
    with pytest.raises(scan_jobs.ProcessAuthorityAmbiguousError):
        scan_jobs._token_process_pidfds(4242, "expected-token")

    monkeypatch.setattr(
        scan_jobs,
        "_open_pidfd",
        lambda pid: (_ for _ in ()).throw(ValueError("invalid pidfd result")),
    )
    with pytest.raises(scan_jobs.ProcessAuthorityAmbiguousError):
        scan_jobs._token_process_pidfds(4242, "expected-token")

    monkeypatch.setattr(
        scan_jobs,
        "_open_pidfd",
        lambda pid: (_ for _ in ()).throw(ProcessLookupError("exited")),
    )
    assert scan_jobs._token_process_pidfds(4242, "expected-token") == []


def test_pidfd_enumeration_filters_foreign_group_before_open(monkeypatch) -> None:
    class Process:
        def __init__(self, pid: int) -> None:
            self.info = {"pid": pid, "status": "running"}

        def environ(self):
            return {"MORPHIC_SCAN_GROUP_TOKEN": "expected-token"}

    opened: list[int] = []
    monkeypatch.setattr(
        scan_jobs.psutil, "process_iter", lambda attrs: [Process(10), Process(11)]
    )
    monkeypatch.setattr(
        scan_jobs.os, "getpgid", lambda pid: 9999 if pid == 10 else 4242, raising=False
    )

    def open_pidfd(pid: int) -> int:
        opened.append(pid)
        raise PermissionError("target denied")

    monkeypatch.setattr(scan_jobs, "_open_pidfd", open_pidfd)
    with pytest.raises(scan_jobs.ProcessAuthorityAmbiguousError):
        scan_jobs._token_process_pidfds(4242, "expected-token")
    assert opened == [10]


def test_pidfd_candidate_revalidates_group_after_open(monkeypatch) -> None:
    class Process:
        info = {"pid": 11, "status": "running"}

        def environ(self):
            raise AssertionError("foreign replacement provenance must not be read")

    pgids = iter([4242, 9999])
    closed: list[int] = []
    monkeypatch.setattr(scan_jobs.psutil, "process_iter", lambda attrs: [Process()])
    monkeypatch.setattr(scan_jobs.os, "getpgid", lambda pid: next(pgids), raising=False)
    monkeypatch.setattr(scan_jobs, "_open_pidfd", lambda pid: 111)
    monkeypatch.setattr(scan_jobs.os, "close", lambda fd: closed.append(fd))

    with pytest.raises(scan_jobs.ProcessAuthorityAmbiguousError):
        scan_jobs._token_process_pidfds(4242, "expected-token")
    assert closed == []


def test_pidfd_cleanup_preserves_system_exit_and_attempts_current_and_transferred(
    monkeypatch,
) -> None:
    class Process:
        def __init__(self, pid: int, exit_on_environ: bool) -> None:
            self.info = {"pid": pid, "status": "running"}
            self.exit_on_environ = exit_on_environ

        def environ(self):
            if self.exit_on_environ:
                raise SystemExit("primary")
            return {"MORPHIC_SCAN_GROUP_TOKEN": "expected-token"}

    handles = iter([101, 102])
    closed: list[int] = []
    monkeypatch.setattr(
        scan_jobs.psutil,
        "process_iter",
        lambda attrs: [Process(11, False), Process(12, True)],
    )
    monkeypatch.setattr(scan_jobs.os, "getpgid", lambda pid: 4242, raising=False)
    monkeypatch.setattr(scan_jobs, "_open_pidfd", lambda pid: next(handles))

    def close(fd: int) -> None:
        closed.append(fd)
        if fd == 102:
            raise OSError("current close failed")

    monkeypatch.setattr(scan_jobs.os, "close", close)

    with pytest.raises(SystemExit, match="primary"):
        scan_jobs._token_process_pidfds(4242, "expected-token")
    assert closed == [101]


def test_supervisor_exit_during_pidfd_open_still_signals_valid_member(
    tmp_path: Path,
    monkeypatch,
) -> None:
    class Member:
        info = {"pid": 11, "status": "running"}

        def environ(self):
            return {"MORPHIC_SCAN_GROUP_TOKEN": "expected-token"}

    process = StoppableProcess()
    process.pid = 10
    job = _job(LocalScanJobService(tmp_path), tmp_path, "", returncode=None)
    job.process = process
    job.process_group_id = 4242
    job.process_group_token = "expected-token"
    sent: list[int] = []
    monkeypatch.setattr(scan_jobs.psutil, "process_iter", lambda attrs: [Member()])
    monkeypatch.setattr(scan_jobs.os, "getpgid", lambda pid: 4242, raising=False)
    monkeypatch.setattr(
        scan_jobs,
        "_open_pidfd",
        lambda pid: (_ for _ in ()).throw(ProcessLookupError()) if pid == 10 else 111,
    )
    monkeypatch.setattr(scan_jobs.os, "close", lambda fd: None)
    monkeypatch.setattr(
        scan_jobs.signal,
        "pidfd_send_signal",
        lambda fd, sig, info, flags: sent.append(fd),
        raising=False,
    )

    assert scan_jobs._signal_posix_authority(job, signal.SIGTERM) == 1
    assert sent == [111]


def test_supervisor_runtime_acquisition_failure_is_ambiguous(
    tmp_path: Path,
    monkeypatch,
) -> None:
    process = StoppableProcess()
    process.pid = 10
    job = _job(LocalScanJobService(tmp_path), tmp_path, "", returncode=None)
    job.process = process
    job.process_group_id = 4242
    job.process_group_token = "expected-token"
    monkeypatch.setattr(
        scan_jobs,
        "_open_pidfd",
        lambda pid: (_ for _ in ()).throw(
            RuntimeError("stable POSIX process handles are unavailable")
        ),
    )

    with pytest.raises(scan_jobs.ProcessAuthorityAmbiguousError):
        scan_jobs._signal_posix_authority(job, signal.SIGTERM)


def test_stop_persists_ambiguity_for_generic_supervisor_acquisition_failure(
    tmp_path: Path,
    monkeypatch,
) -> None:
    service = LocalScanJobService(tmp_path)
    process = StoppableProcess()
    job = _job(service, tmp_path, "", returncode=None)
    job.job_id = "scan-generic-acquisition"
    job.process = process
    job.process_group_id = 4242
    job.process_group_token = "expected-token"
    _register_job(service, job)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(
        scan_jobs,
        "_open_pidfd",
        lambda pid: (_ for _ in ()).throw(ValueError("invalid pidfd result")),
    )

    with pytest.raises(RuntimeError, match="authority is ambiguous"):
        service.stop(job.job_id)

    assert job.forced_status == "authority_ambiguous"
    persisted = json.loads(service._state_path(job.job_id).read_text(encoding="utf-8"))
    assert persisted["forced_status"] == "authority_ambiguous"


def test_windows_recovery_retains_job_when_authority_close_fails(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = tmp_path / "jobs"
    writer = LocalScanJobService(root, cwd=tmp_path)
    job = _job(writer, root, "", returncode=None)
    job.job_id = "scan-job-1"
    job.process = StoppableProcess()
    job.process_create_time = 1.0
    job.process_group_id = job.process.pid
    job.process_group_token = "a" * 32
    job.owner_id = "operator-a"
    job.stdout_path = writer._stdout_path(job.job_id)
    job.stderr_path = writer._stderr_path(job.job_id)
    job.stdout_path.write_text("", encoding="utf-8")
    job.stderr_path.write_text("", encoding="utf-8")
    writer._persist_job(job)

    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(
        scan_jobs,
        "_job_runtime_active",
        lambda active_job: (_ for _ in ()).throw(OSError(errno.EBADF, "close failed")),
    )

    recovered = LocalScanJobService(root, cwd=tmp_path)

    assert recovered._jobs[job.job_id].forced_status == "authority_ambiguous"
    assert recovered.get(job.job_id)["status"] == "authority_ambiguous"


def test_windows_terminated_job_close_failure_still_attempts_bounded_wait(
    tmp_path: Path,
    monkeypatch,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job = _job(service, tmp_path, "")
    process = StoppableProcess()
    job.process = process
    job.windows_job_handle = 77
    wait_calls: list[float] = []

    def fail_wait(timeout):
        wait_calls.append(timeout)
        raise subprocess.TimeoutExpired("gate", timeout)

    process.wait = fail_wait
    monkeypatch.setattr(scan_jobs, "_terminate_windows_job", lambda active_job: None)
    monkeypatch.setattr(scan_jobs, "_windows_job_active", lambda active_job: False)
    monkeypatch.setattr(
        scan_jobs,
        "_close_windows_job_handle",
        lambda active_job: (_ for _ in ()).throw(OSError(errno.EBADF, "close failed")),
    )

    with pytest.raises(BaseExceptionGroup) as captured:
        scan_jobs._converge_windows_authority(job)

    assert [type(exc) for exc in captured.value.exceptions] == [
        subprocess.TimeoutExpired,
        OSError,
    ]
    assert wait_calls == [5]


def test_supervisor_post_open_exit_still_signals_valid_member(
    tmp_path: Path,
    monkeypatch,
) -> None:
    class Member:
        info = {"pid": 11, "status": "running"}

        def environ(self):
            return {"MORPHIC_SCAN_GROUP_TOKEN": "expected-token"}

    process = StoppableProcess()
    process.pid = 10
    job = _job(LocalScanJobService(tmp_path), tmp_path, "", returncode=None)
    job.process = process
    job.process_create_time = 1.0
    job.process_group_id = 4242
    job.process_group_token = "expected-token"
    handles = iter([100, 111])
    sent: list[int] = []
    closed: list[int] = []
    monkeypatch.setattr(
        scan_jobs, "_strict_process_identity_matches", lambda pid, created: True
    )
    monkeypatch.setattr(scan_jobs.psutil, "process_iter", lambda attrs: [Member()])

    def getpgid(pid: int) -> int:
        if pid == 10:
            raise ProcessLookupError("supervisor exited after open")
        return 4242

    monkeypatch.setattr(scan_jobs.os, "getpgid", getpgid, raising=False)
    monkeypatch.setattr(scan_jobs, "_open_pidfd", lambda pid: next(handles))
    monkeypatch.setattr(scan_jobs.os, "close", lambda fd: closed.append(fd))
    monkeypatch.setattr(
        scan_jobs.signal,
        "pidfd_send_signal",
        lambda fd, sig, info, flags: sent.append(fd),
        raising=False,
    )

    assert scan_jobs._signal_posix_authority(job, signal.SIGTERM) == 1
    assert sent == [111]
    assert closed == [111, 100]


def test_stop_persists_ambiguity_for_post_open_supervisor_revalidation_error(
    tmp_path: Path,
    monkeypatch,
) -> None:
    service = LocalScanJobService(tmp_path)
    process = StoppableProcess()
    job = _job(service, tmp_path, "", returncode=None)
    job.job_id = "scan-post-open-ambiguous"
    job.process = process
    job.process_create_time = 1.0
    job.process_group_id = 4242
    job.process_group_token = "expected-token"
    _register_job(service, job)
    closed: list[int] = []
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(scan_jobs, "_open_pidfd", lambda pid: 100)
    monkeypatch.setattr(
        scan_jobs, "_strict_process_identity_matches", lambda pid, created: True
    )
    monkeypatch.setattr(
        scan_jobs.os,
        "getpgid",
        lambda pid: (_ for _ in ()).throw(OSError(errno.EACCES, "denied")),
        raising=False,
    )
    monkeypatch.setattr(scan_jobs.os, "close", lambda fd: closed.append(fd))

    with pytest.raises(RuntimeError, match="authority is ambiguous"):
        service.stop(job.job_id)

    assert closed.count(100) == 1
    assert job.forced_status == "authority_ambiguous"
    persisted = json.loads(service._state_path(job.job_id).read_text(encoding="utf-8"))
    assert persisted["forced_status"] == "authority_ambiguous"


@pytest.mark.parametrize("failure_kind", ["access-denied", "eio"])
def test_stop_persists_creation_time_error_after_successful_supervisor_open(
    tmp_path: Path,
    monkeypatch,
    failure_kind: str,
) -> None:
    service = LocalScanJobService(tmp_path)
    process = StoppableProcess()
    job = _job(service, tmp_path, "", returncode=None)
    job.job_id = f"scan-create-time-{failure_kind}"
    job.process = process
    job.process_create_time = 1.0
    job.process_group_id = 4242
    job.process_group_token = "expected-token"
    _register_job(service, job)
    calls = 0
    closed: list[int] = []
    sent: list[int] = []

    class ProcessIdentity:
        def create_time(self) -> float:
            nonlocal calls
            calls += 1
            if calls == 1:
                return 1.0
            if failure_kind == "access-denied":
                raise scan_jobs.psutil.AccessDenied(process.pid)
            raise OSError(errno.EIO, "identity unreadable")

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(scan_jobs.psutil, "Process", lambda pid: ProcessIdentity())
    monkeypatch.setattr(scan_jobs, "_open_pidfd", lambda pid: 100)
    monkeypatch.setattr(scan_jobs.os, "close", lambda fd: closed.append(fd))
    monkeypatch.setattr(
        scan_jobs.signal,
        "pidfd_send_signal",
        lambda fd, sig, info, flags: sent.append(fd),
        raising=False,
    )

    with pytest.raises(RuntimeError, match="authority is ambiguous"):
        service.stop(job.job_id)

    assert calls == 2
    assert sent == []
    assert closed.count(100) == 1
    assert job.forced_status == "authority_ambiguous"
    persisted = json.loads(service._state_path(job.job_id).read_text(encoding="utf-8"))
    assert persisted["forced_status"] == "authority_ambiguous"


def test_start_failure_preserves_primary_when_rollback_also_fails(
    tmp_path: Path,
    monkeypatch,
) -> None:
    service = LocalScanJobService(tmp_path)
    process = StoppableProcess()
    job = _job(service, tmp_path, "", returncode=None)
    job.job_id = "scan-rollback-failure"
    job.process = process
    job.process_group_id = 4242
    job.process_group_token = "expected-token"
    def fail_primary() -> None:
        raise KeyboardInterrupt("primary snapshot failure")

    try:
        fail_primary()
    except BaseException as exc:
        primary = exc
    original_traceback = primary.__traceback__
    rollback = RuntimeError("rollback failed")
    monkeypatch.setattr(
        scan_jobs,
        "_rollback_scan_authority",
        lambda active_job: (_ for _ in ()).throw(rollback),
    )

    with pytest.raises(BaseExceptionGroup) as raised:
        service._raise_start_failure(job, primary)

    assert raised.value.exceptions[0] is primary
    assert raised.value.exceptions[0].__traceback__ is original_traceback
    assert original_traceback is not None
    assert original_traceback.tb_next is not None
    assert original_traceback.tb_next.tb_frame.f_code.co_name == "fail_primary"
    assert raised.value.exceptions[1] is rollback
    assert job.forced_status == "rollback_failed"
    persisted = json.loads(service._state_path(job.job_id).read_text(encoding="utf-8"))
    assert persisted["forced_status"] == "rollback_failed"


def _register_rollback_failed_job(
    service: LocalScanJobService,
    job_id: str,
) -> _LocalScanJob:
    process = StoppableProcess()
    process.returncode = 1
    stdout_path = service._stdout_path(job_id)
    stderr_path = service._stderr_path(job_id)
    stdout_path.write_text("", encoding="utf-8")
    stderr_path.write_text("", encoding="utf-8")
    job = _LocalScanJob(
        job_id=job_id,
        command=["python", "-V"],
        process=process,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        created_at="2026-07-22T00:00:00+00:00",
        updated_at="2026-07-22T00:00:00+00:00",
        forced_status="rollback_failed",
        process_create_time=1.0,
        process_group_id=4242,
        process_group_token="a" * 32,
        start_released=True,
    )
    service._jobs[job_id] = job
    service._persist_job(job)
    return job


@pytest.mark.parametrize(
    "probe_error",
    [
        ProcessAuthorityAmbiguousError("ambiguous authority"),
        OSError("authority probe failed"),
        RuntimeError("authority probe exception"),
    ],
    ids=["ambiguous", "failed", "exception"],
)
def test_rollback_failed_survives_every_uncertain_authority_probe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    probe_error: Exception,
) -> None:
    service = LocalScanJobService(tmp_path)
    job = _register_rollback_failed_job(service, f"rollback-{type(probe_error).__name__}")
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(
        scan_jobs,
        "_process_group_alive",
        lambda group_id, token: (_ for _ in ()).throw(probe_error),
    )

    with pytest.raises(Exception):
        service.stop(job.job_id)

    assert job.forced_status == "rollback_failed"
    persisted = json.loads(service._state_path(job.job_id).read_text(encoding="utf-8"))
    assert persisted["forced_status"] == "rollback_failed"


def test_rollback_failed_survives_convergence_exception_and_post_recheck_activity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = LocalScanJobService(tmp_path)
    job = _register_rollback_failed_job(service, "rollback-convergence")
    process = job.process
    process.returncode = None
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(scan_jobs, "_strict_process_identity_matches", lambda pid, created: True)
    monkeypatch.setattr(scan_jobs, "_process_group_alive", lambda group_id, token: False)
    monkeypatch.setattr(
        scan_jobs,
        "_converge_posix_authority",
        lambda active_job: (_ for _ in ()).throw(RuntimeError("convergence failed")),
    )

    with pytest.raises(RuntimeError, match="authority is ambiguous"):
        service.stop(job.job_id)
    assert job.forced_status == "rollback_failed"

    monkeypatch.setattr(scan_jobs, "_converge_posix_authority", lambda active_job: None)
    with pytest.raises(RuntimeError, match="stop was not confirmed"):
        service.stop(job.job_id)
    assert job.forced_status == "rollback_failed"
    persisted = json.loads(service._state_path(job.job_id).read_text(encoding="utf-8"))
    assert persisted["forced_status"] == "rollback_failed"


def test_rollback_failed_becomes_durably_stopped_after_stable_tree_converges(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root)
    job = _register_rollback_failed_job(service, "rollback-converged")
    process = job.process
    process.returncode = None
    group_active = {"value": True}
    probes: list[tuple[int | None, str | None]] = []
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(scan_jobs, "_strict_process_identity_matches", lambda pid, created: True)

    def probe(group_id: int | None, token: str | None) -> bool:
        probes.append((group_id, token))
        return group_active["value"]

    def converge(active_job: _LocalScanJob) -> None:
        assert active_job is job
        process.returncode = 1
        group_active["value"] = False

    monkeypatch.setattr(scan_jobs, "_process_group_alive", probe)
    monkeypatch.setattr(scan_jobs, "_converge_posix_authority", converge)

    stopped = service.stop(job.job_id)

    assert stopped["status"] == "stopped"
    assert len(probes) >= 1
    persisted = json.loads(service._state_path(job.job_id).read_text(encoding="utf-8"))
    assert persisted["forced_status"] == "stopped"
    recovered = LocalScanJobService(root)
    assert recovered.get(job.job_id)["status"] == "stopped"
    monkeypatch.setattr(
        scan_jobs,
        "_process_group_alive",
        lambda group_id, token: (_ for _ in ()).throw(
            ProcessAuthorityAmbiguousError("terminal authority must not regress")
        ),
    )
    assert recovered.stop(job.job_id)["status"] == "stopped"


def test_restart_keeps_rollback_failed_until_authoritative_inactivity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    writer = LocalScanJobService(root)
    job = _register_rollback_failed_job(writer, "rollback-restart")
    monkeypatch.setattr(sys, "platform", "linux")
    recovered = LocalScanJobService(root)
    assert recovered.get(job.job_id)["status"] == "rollback_failed"
    monkeypatch.setattr(scan_jobs, "_process_group_alive", lambda group_id, token: False)

    stopped = recovered.stop(job.job_id)

    assert stopped["status"] == "stopped"
    restarted = LocalScanJobService(root)
    assert restarted.get(job.job_id)["status"] == "stopped"


def test_descriptor_cleanup_attempts_every_handle_after_close_error(monkeypatch) -> None:
    attempted: list[int] = []

    def close(descriptor: int) -> None:
        attempted.append(descriptor)
        if descriptor == 1:
            raise OSError("first close failed")

    monkeypatch.setattr(scan_jobs.os, "close", close)
    failures = scan_jobs._close_process_handles([1, 2, 3])

    assert attempted == [1, 2, 3]
    assert len(failures) == 1


def test_authority_ambiguous_transitions_to_stopped_after_confirmed_absence(
    tmp_path: Path,
    monkeypatch,
) -> None:
    service = LocalScanJobService(tmp_path)
    process = StoppableProcess()
    process.returncode = 1
    job = _job(service, tmp_path, "", returncode=1)
    job.job_id = "ambiguity-cleared"
    job.process = process
    job.process_group_id = 4242
    job.process_group_token = "expected-token"
    job.forced_status = "authority_ambiguous"
    _register_job(service, job)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(scan_jobs, "_process_group_alive", lambda pgid, token: False)

    snapshot = service.stop(job.job_id)

    assert snapshot["status"] == "stopped"
    persisted = json.loads(service._state_path(job.job_id).read_text(encoding="utf-8"))
    assert persisted["forced_status"] == "stopped"


def test_snapshot_and_recovery_publish_ambiguous_for_mixed_group(
    tmp_path: Path,
    monkeypatch,
) -> None:
    service = LocalScanJobService(tmp_path)
    process = StoppableProcess()
    process.returncode = 1
    job = _job(service, tmp_path, "", returncode=1)
    job.job_id = "scan-mixed-recovery"
    job.process = process
    job.process_create_time = 1.0
    job.process_group_id = 4242
    job.process_group_token = "a" * 32
    job.stdout_path = service._stdout_path(job.job_id)
    job.stderr_path = service._stderr_path(job.job_id)
    job.stdout_path.write_text("", encoding="utf-8")
    job.stderr_path.write_text("", encoding="utf-8")
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(
        scan_jobs,
        "_process_group_alive",
        lambda pgid, token: (_ for _ in ()).throw(
            scan_jobs.ProcessAuthorityAmbiguousError("later unreadable member")
        ),
    )

    assert service._snapshot(job)["status"] == "authority_ambiguous"
    job.forced_status = None
    service._persist_job(job)
    monkeypatch.setattr(scan_jobs._RecoveredProcess, "poll", lambda self: 1)
    recovered = LocalScanJobService(tmp_path)

    assert recovered.get(job.job_id)["status"] == "authority_ambiguous"


def test_stale_pidfd_does_not_block_later_valid_handle(tmp_path: Path, monkeypatch) -> None:
    job = _job(LocalScanJobService(tmp_path), tmp_path, "", returncode=1)
    job.process_group_id = 4242
    job.process_group_token = "expected-token"
    sent: list[int] = []
    monkeypatch.setattr(
        scan_jobs,
        "_token_process_pidfds",
        lambda pgid, token, supervisor=None: [111, 112],
    )
    monkeypatch.setattr(scan_jobs.os, "close", lambda fd: None)

    def sender(fd, sig, info, flags) -> None:
        if fd == 111:
            raise ProcessLookupError("already exited")
        sent.append(fd)

    monkeypatch.setattr(scan_jobs.signal, "pidfd_send_signal", sender, raising=False)

    assert scan_jobs._signal_posix_authority(job, signal.SIGTERM) == 2
    assert sent == [112]


def test_stop_and_rollback_send_nothing_when_group_authority_is_ambiguous(
    tmp_path: Path,
    monkeypatch,
) -> None:
    service = LocalScanJobService(tmp_path)
    process = StoppableProcess()
    process.returncode = 1
    job = _job(service, tmp_path, "", returncode=None)
    job.job_id = "ambiguous-authority"
    job.process = process
    job.process_group_id = 4242
    job.process_group_token = "expected-token"
    _register_job(service, job)
    signals: list[int] = []
    original_signal_authority = scan_jobs._signal_posix_authority
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(
        scan_jobs,
        "_process_group_alive",
        lambda pgid, token: (_ for _ in ()).throw(
            scan_jobs.ProcessAuthorityAmbiguousError("unreadable member")
        ),
    )
    monkeypatch.setattr(
        scan_jobs,
        "_signal_posix_authority",
        lambda active_job, sent_signal: signals.append(sent_signal),
    )

    with pytest.raises(RuntimeError, match="authority is ambiguous"):
        service.stop(job.job_id)
    assert job.forced_status == "authority_ambiguous"
    assert signals == []

    job.forced_status = None
    process.returncode = 1
    monkeypatch.setattr(scan_jobs, "_signal_posix_authority", original_signal_authority)
    monkeypatch.setattr(scan_jobs, "_process_group_alive", lambda pgid, token: True)
    monkeypatch.setattr(scan_jobs, "_process_identity_matches", lambda pid, created: True)
    monkeypatch.setattr(
        scan_jobs,
        "_token_process_pidfds",
        lambda pgid, token, supervisor=None: (_ for _ in ()).throw(
            scan_jobs.ProcessAuthorityAmbiguousError("unreadable member")
        ),
    )
    with pytest.raises(BaseExceptionGroup):
        scan_jobs._rollback_scan_authority(job)
    assert signals == []


def test_stop_reenumerates_members_that_appear_between_signal_rounds(
    tmp_path: Path,
    monkeypatch,
) -> None:
    service = LocalScanJobService(tmp_path)
    job = _job(service, tmp_path, "", returncode=1)
    job.job_id = "fork-between-rounds"
    process = StoppableProcess()
    process.returncode = 1
    job.process = process
    job.process_group_id = 4242
    job.process_group_token = "expected-token"
    _register_job(service, job)
    signals: list[int] = []
    active = {"value": True, "kills": 0}
    clock = {"value": 0.0}
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(scan_jobs.signal, "SIGKILL", 9, raising=False)
    monkeypatch.setattr(scan_jobs, "_process_group_alive", lambda pgid, token: active["value"])

    def signal_round(active_job, sent_signal: int) -> int:
        signals.append(sent_signal)
        if sent_signal == 9:
            active["kills"] += 1
            if active["kills"] == 2:
                active["value"] = False
        return 1

    def monotonic() -> float:
        clock["value"] += 0.6
        return clock["value"]

    monkeypatch.setattr(scan_jobs, "_signal_posix_authority", signal_round)
    monkeypatch.setattr(scan_jobs.time, "monotonic", monotonic)
    monkeypatch.setattr(scan_jobs.time, "sleep", lambda seconds: None)

    snapshot = service.stop(job.job_id)

    assert signals == [signal.SIGTERM, 9, 9]
    assert snapshot["status"] == "stopped"


@pytest.mark.skipif(sys.platform != "win32", reason="Windows process-tree contract")
def test_running_windows_scan_retains_owned_job_handle_until_convergence(
    tmp_path: Path,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    started = service.start(
        [sys.executable, "-c", "import time; time.sleep(60)"]
    )
    job_id = str(started["job_id"])
    try:
        assert started["status"] == "running"
        assert service._jobs[job_id].windows_job_handle is not None
    finally:
        service.stop(job_id)

    assert service._jobs[job_id].windows_job_handle is None
    reaper = service._jobs[job_id].windows_reaper
    assert reaper is not None
    reaper.join(timeout=1)
    assert not reaper.is_alive()


@pytest.mark.skipif(sys.platform != "win32", reason="Windows process-tree contract")
def test_naturally_completed_windows_scan_closes_owned_job_handle(tmp_path: Path) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    started = service.start([sys.executable, "-c", "pass"])
    job_id = str(started["job_id"])
    deadline = time.monotonic() + 5
    snapshot = started
    while time.monotonic() < deadline and snapshot["status"] in {"starting", "running"}:
        time.sleep(0.05)
        snapshot = service.get(job_id)
    assert snapshot["status"] == "completed"
    assert service._jobs[job_id].windows_job_handle is None


@pytest.mark.skipif(sys.platform != "win32", reason="Windows process-tree contract")
def test_windows_scan_reaps_job_handle_after_natural_completion_without_poll(
    tmp_path: Path,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    started = service.start(
        [sys.executable, "-c", "import time; time.sleep(0.2)"]
    )
    job_id = str(started["job_id"])
    job = service._jobs[job_id]
    try:
        assert job.windows_job_handle is not None
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline and job.windows_job_handle is not None:
            time.sleep(0.02)
        assert job.windows_job_handle is None
        assert job.process.poll() is not None
        assert job.windows_reaper is not None
        job.windows_reaper.join(timeout=1)
        assert not job.windows_reaper.is_alive()
    finally:
        if job.process.poll() is None:
            service.stop(job_id)


@pytest.mark.skipif(sys.platform != "win32", reason="Windows process-tree contract")
def test_windows_job_handle_concurrent_close_calls_kernel_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ctypes

    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job = _job(service, tmp_path, "", returncode=0)
    job.windows_job_handle = 77
    entered = threading.Event()
    release = threading.Event()
    calls: list[int] = []
    errors: list[BaseException] = []

    class CloseHandle:
        argtypes = None
        restype = None

        @staticmethod
        def __call__(handle) -> int:
            calls.append(int(handle.value))
            entered.set()
            assert release.wait(timeout=2)
            return 1

    kernel32 = type("Kernel32", (), {})()
    kernel32.CloseHandle = CloseHandle()

    def close() -> None:
        try:
            scan_jobs._close_windows_job_handle(job)
        except BaseException as exc:
            errors.append(exc)

    monkeypatch.setattr(ctypes, "WinDLL", lambda *args, **kwargs: kernel32)
    first = threading.Thread(target=close)
    second = threading.Thread(target=close)
    first.start()
    assert entered.wait(timeout=2)
    second.start()
    time.sleep(0.05)
    release.set()
    first.join(timeout=2)
    second.join(timeout=2)

    assert not first.is_alive()
    assert not second.is_alive()
    assert errors == []
    assert calls == [77]
    assert job.windows_job_handle is None


@pytest.mark.skipif(sys.platform != "win32", reason="Windows process-tree contract")
def test_windows_reaper_retains_job_authority_after_outer_references_are_dropped(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job = _job(service, tmp_path, "", returncode=None)
    job.job_id = "reaper-strong-authority"
    job.windows_job_handle = 77
    _register_job(service, job)
    job_reference = weakref.ref(job)
    monkeypatch.setattr(scan_jobs, "_windows_job_active", lambda active_job: True)

    scan_jobs._start_windows_job_reaper(job)
    reaper = job.windows_reaper
    assert reaper is not None
    service._jobs.clear()
    del job
    del service
    deadline = time.monotonic() + 0.5
    while time.monotonic() < deadline:
        gc.collect()
        if job_reference() is None:
            break
        time.sleep(0.02)

    retained = job_reference()
    try:
        assert retained is not None
        assert retained.windows_job_handle == 77
        assert reaper.is_alive()
    finally:
        if retained is not None:
            retained.windows_reaper_stop.set()
        reaper.join(timeout=1)


@pytest.mark.skipif(sys.platform != "win32", reason="Windows process-tree contract")
def test_scan_service_close_is_idempotent_single_close_and_bounded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ctypes

    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job = _job(service, tmp_path, "", returncode=None)
    job.job_id = "service-close-authority"
    job.windows_job_handle = 77
    _register_job(service, job)
    calls: list[int] = []

    class CloseHandle:
        argtypes = None
        restype = None

        @staticmethod
        def __call__(handle) -> int:
            calls.append(int(handle.value))
            return 1

    kernel32 = type("Kernel32", (), {})()
    kernel32.CloseHandle = CloseHandle()
    monkeypatch.setattr(ctypes, "WinDLL", lambda *args, **kwargs: kernel32)
    reaper = threading.Thread(
        target=lambda: job.windows_reaper_stop.wait(60),
        daemon=True,
    )
    job.windows_reaper = reaper
    reaper.start()
    close = getattr(service, "close", None)
    try:
        assert callable(close), "LocalScanJobService.close is required"
        started = time.monotonic()
        close()
        service.shutdown()
        close()
        elapsed = time.monotonic() - started
        assert elapsed < 2
        assert calls == [77]
        assert job.windows_job_handle is None
        assert not reaper.is_alive()
        with pytest.raises(RuntimeError, match="service is closed"):
            service.start([sys.executable, "-c", "pass"])
    finally:
        job.windows_reaper_stop.set()
        reaper.join(timeout=1)


@pytest.mark.skipif(sys.platform != "win32", reason="Windows process-tree contract")
def test_scan_service_close_retries_transient_handle_failure_and_blocks_starts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ctypes

    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job = _job(service, tmp_path, "", returncode=None)
    job.job_id = "service-close-retry-handle"
    job.windows_job_handle = 77
    _register_job(service, job)
    calls: list[int] = []

    class CloseHandle:
        argtypes = None
        restype = None

        @staticmethod
        def __call__(handle) -> int:
            calls.append(int(handle.value))
            return int(len(calls) > 1)

    kernel32 = type("Kernel32", (), {})()
    kernel32.CloseHandle = CloseHandle()
    monkeypatch.setattr(ctypes, "WinDLL", lambda *args, **kwargs: kernel32)

    with pytest.raises(BaseExceptionGroup, match="shutdown failed"):
        service.close()
    assert job.windows_job_handle == 77
    assert calls == [77]
    with pytest.raises(RuntimeError, match="service is closed"):
        service.start([sys.executable, "-c", "pass"])

    service.shutdown()
    service.close()

    assert job.windows_job_handle is None
    assert calls == [77, 77]


@pytest.mark.skipif(sys.platform != "win32", reason="Windows process-tree contract")
def test_scan_service_close_retries_reaper_timeout_until_it_converges(
    tmp_path: Path,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job = _job(service, tmp_path, "", returncode=None)
    job.job_id = "service-close-retry-reaper"
    _register_job(service, job)

    class ControllableReaper:
        def __init__(self) -> None:
            self.alive = True
            self.join_timeouts: list[float | None] = []

        def join(self, timeout: float | None = None) -> None:
            self.join_timeouts.append(timeout)

        def is_alive(self) -> bool:
            return self.alive

    reaper = ControllableReaper()
    job.windows_reaper = reaper  # type: ignore[assignment]

    with pytest.raises(BaseExceptionGroup, match="shutdown failed"):
        service.close()
    assert len(reaper.join_timeouts) == 1
    assert reaper.join_timeouts[0] is not None
    assert reaper.join_timeouts[0] <= 1.0
    with pytest.raises(RuntimeError, match="service is closed"):
        service.start([sys.executable, "-c", "pass"])

    reaper.alive = False
    service.close()
    service.shutdown()

    assert len(reaper.join_timeouts) == 2


@pytest.mark.skipif(sys.platform != "win32", reason="Windows process-tree contract")
def test_scan_service_close_retries_transient_reaper_join_failure(
    tmp_path: Path,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job = _job(service, tmp_path, "", returncode=None)
    job.job_id = "service-close-retry-reaper-join"
    _register_job(service, job)

    class TransientJoinFailure:
        def __init__(self) -> None:
            self.alive = True
            self.join_calls = 0

        def join(self, timeout: float | None = None) -> None:
            self.join_calls += 1
            if self.join_calls == 1:
                raise RuntimeError("transient reaper join failure")
            self.alive = False

        def is_alive(self) -> bool:
            return self.alive

    reaper = TransientJoinFailure()
    job.windows_reaper = reaper  # type: ignore[assignment]

    with pytest.raises(BaseExceptionGroup, match="shutdown failed") as captured:
        service.close()
    assert isinstance(captured.value.exceptions[0], RuntimeError)
    assert "transient reaper join failure" in str(captured.value.exceptions[0])
    with pytest.raises(RuntimeError, match="service is closed"):
        service.start([sys.executable, "-c", "pass"])

    service.close()
    service.shutdown()

    assert reaper.join_calls == 2
    assert not reaper.is_alive()


def test_scan_service_close_bounds_accepted_start_and_late_start_hands_off(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    entered_process_lock = threading.Event()
    release_process_lock = threading.Event()
    close_done = threading.Event()
    process_lock_calls: list[str] = []
    close_calls: list[str] = []
    start_results: list[dict[str, object]] = []
    start_errors: list[BaseException] = []
    close_errors: list[BaseException] = []
    registered_jobs: list[_LocalScanJob] = []
    job_id = "scan-bounded-accepted-start"
    monkeypatch.setattr(
        scan_jobs,
        "_SCAN_SERVICE_SHUTDOWN_TIMEOUT",
        0.1,
        raising=False,
    )

    @contextmanager
    def blocked_process_lock(active_job_id: str):
        process_lock_calls.append(active_job_id)
        entered_process_lock.set()
        assert release_process_lock.wait(timeout=2)
        yield

    def register_job(
        command: list[str],
        owner_id: str | None,
        env_overrides,
        active_job_id: str,
    ) -> dict[str, object]:
        job = _job(service, tmp_path, "", returncode=None)
        job.job_id = active_job_id
        job.windows_job_handle = 77
        with service._lock:
            service._jobs[active_job_id] = job
        registered_jobs.append(job)
        return {"job_id": active_job_id, "status": "running"}

    def close_handle(
        active_job: _LocalScanJob,
        *,
        deadline: float | None = None,
    ) -> None:
        with active_job.windows_job_lock:  # type: ignore[attr-defined]
            if active_job.windows_job_handle is None:
                return
            close_calls.append(active_job.job_id)
            active_job.windows_job_handle = None
            active_job.windows_reaper_stop.set()

    def run_start() -> None:
        try:
            start_results.append(
                service.start([sys.executable, "-c", "pass"], job_id=job_id)
            )
        except BaseException as exc:
            start_errors.append(exc)

    def run_close() -> None:
        try:
            service.close()
        except BaseException as exc:
            close_errors.append(exc)
        finally:
            close_done.set()

    monkeypatch.setattr(service, "_start_process_lock", blocked_process_lock)
    monkeypatch.setattr(service, "_start_new_job", register_job)
    monkeypatch.setattr(scan_jobs, "_close_windows_job_handle", close_handle)
    start_thread = threading.Thread(target=run_start, daemon=True)
    close_thread = threading.Thread(target=run_close, daemon=True)
    start_thread.start()
    assert entered_process_lock.wait(timeout=1)
    started = time.monotonic()
    close_thread.start()

    try:
        assert close_done.wait(timeout=0.35)
        assert time.monotonic() - started < 0.35
        assert len(close_errors) == 1
        assert isinstance(close_errors[0], BaseExceptionGroup)
        assert "accepted scan start" in str(close_errors[0].exceptions[0]).lower()
        with pytest.raises(RuntimeError, match="service is closed"):
            service.start([sys.executable, "-c", "pass"], job_id="scan-rejected")
        assert process_lock_calls == [job_id]

        release_process_lock.set()
        start_thread.join(timeout=1)
        assert not start_thread.is_alive()
        assert start_errors == []
        assert start_results == [{"job_id": job_id, "status": "running"}]
        assert registered_jobs[0].windows_job_handle is None
        assert close_calls == [job_id]

        service.close()
        service.shutdown()
        assert close_calls == [job_id]
    finally:
        release_process_lock.set()
        start_thread.join(timeout=2)
        close_thread.join(timeout=2)
        for job in registered_jobs:
            job.windows_job_handle = None


def test_scan_service_close_bounds_cleanup_lock_and_closes_admission(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    close_done = threading.Event()
    close_errors: list[BaseException] = []
    monkeypatch.setattr(
        scan_jobs,
        "_SCAN_SERVICE_SHUTDOWN_TIMEOUT",
        0.1,
        raising=False,
    )

    def run_close() -> None:
        try:
            service.close()
        except BaseException as exc:
            close_errors.append(exc)
        finally:
            close_done.set()

    service._close_lock.acquire()
    close_thread = threading.Thread(target=run_close, daemon=True)
    started = time.monotonic()
    close_thread.start()
    try:
        assert close_done.wait(timeout=0.35)
        assert time.monotonic() - started < 0.35
        assert len(close_errors) == 1
        assert isinstance(close_errors[0], BaseExceptionGroup)
        with pytest.raises(RuntimeError, match="service is closed"):
            service.start([sys.executable, "-c", "pass"])
    finally:
        service._close_lock.release()
        close_thread.join(timeout=1)

    service.close()


def test_scan_start_registration_racing_shutdown_closes_handle_exactly_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    registered = threading.Event()
    release_start = threading.Event()
    close_done = threading.Event()
    start_results: list[dict[str, object]] = []
    start_errors: list[BaseException] = []
    close_errors: list[BaseException] = []
    close_calls: list[str] = []
    jobs: list[_LocalScanJob] = []
    job_id = "scan-shutdown-registration-race"
    monkeypatch.setattr(
        scan_jobs,
        "_SCAN_SERVICE_SHUTDOWN_TIMEOUT",
        0.5,
        raising=False,
    )

    def register_then_wait(
        command: list[str],
        owner_id: str | None,
        env_overrides,
        active_job_id: str,
    ) -> dict[str, object]:
        job = _job(service, tmp_path, "", returncode=None)
        job.job_id = active_job_id
        job.windows_job_handle = 77
        with service._lock:
            service._jobs[active_job_id] = job
        jobs.append(job)
        registered.set()
        assert release_start.wait(timeout=2)
        return {"job_id": active_job_id, "status": "running"}

    def close_handle(
        active_job: _LocalScanJob,
        *,
        deadline: float | None = None,
    ) -> None:
        with active_job.windows_job_lock:  # type: ignore[attr-defined]
            if active_job.windows_job_handle is None:
                return
            close_calls.append(active_job.job_id)
            active_job.windows_job_handle = None
            active_job.windows_reaper_stop.set()

    def run_start() -> None:
        try:
            start_results.append(
                service.start([sys.executable, "-c", "pass"], job_id=job_id)
            )
        except BaseException as exc:
            start_errors.append(exc)

    def run_close() -> None:
        try:
            service.close()
        except BaseException as exc:
            close_errors.append(exc)
        finally:
            close_done.set()

    monkeypatch.setattr(service, "_start_new_job", register_then_wait)
    monkeypatch.setattr(scan_jobs, "_close_windows_job_handle", close_handle)
    start_thread = threading.Thread(target=run_start, daemon=True)
    close_thread = threading.Thread(target=run_close, daemon=True)
    start_thread.start()
    assert registered.wait(timeout=1)
    close_thread.start()
    deadline = time.monotonic() + 0.3
    while time.monotonic() < deadline and not service._starts_closed:
        time.sleep(0.005)

    try:
        assert service._starts_closed
        release_start.set()
        start_thread.join(timeout=1)
        close_thread.join(timeout=1)
        assert not start_thread.is_alive()
        assert not close_thread.is_alive()
        assert start_errors == []
        assert close_errors == []
        assert start_results == [{"job_id": job_id, "status": "running"}]
        assert close_calls == [job_id]
        assert jobs[0].windows_job_handle is None

        service.close()
        assert close_calls == [job_id]
    finally:
        release_start.set()
        start_thread.join(timeout=2)
        close_thread.join(timeout=2)
        for job in jobs:
            job.windows_job_handle = None


def test_scan_service_close_retries_uncollected_reaper_error_after_lock_timeout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job = _job(service, tmp_path, "", returncode=1)
    job.job_id = "scan-reaper-error-lock-timeout"
    recorded = TypeError("recorded reaper defect")
    job.windows_reaper_error = recorded
    _register_job(service, job)
    close_done = threading.Event()
    first_errors: list[BaseException] = []
    monkeypatch.setattr(scan_jobs, "_SCAN_SERVICE_SHUTDOWN_TIMEOUT", 0.1)

    def run_close() -> None:
        try:
            service.close()
        except BaseException as exc:
            first_errors.append(exc)
        finally:
            close_done.set()

    job.windows_job_lock.acquire()  # type: ignore[attr-defined]
    close_thread = threading.Thread(target=run_close, daemon=True)
    close_thread.start()
    try:
        assert close_done.wait(timeout=0.35)
        assert len(first_errors) == 1
        assert isinstance(first_errors[0], BaseExceptionGroup)
        assert job.windows_reaper_error is recorded
    finally:
        job.windows_job_lock.release()  # type: ignore[attr-defined]
        close_thread.join(timeout=1)

    with pytest.raises(BaseExceptionGroup, match="shutdown failed") as captured:
        service.close()
    assert captured.value.exceptions == (recorded,)
    assert job.windows_reaper_error is None

    service.close()


@pytest.mark.skipif(sys.platform != "win32", reason="Windows process-tree contract")
def test_windows_reaper_query_failures_retain_handle_until_service_close(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job = _job(service, tmp_path, "", returncode=1)
    job.job_id = "reaper-query-failure"
    job.windows_job_handle = 77
    _register_job(service, job)
    clock = {"value": 0.0}
    closed: list[str] = []
    real_monotonic = time.monotonic

    def monotonic() -> float:
        clock["value"] += 1.1
        return clock["value"]

    def close_handle(active_job: _LocalScanJob) -> None:
        with active_job.windows_job_lock:  # type: ignore[attr-defined]
            closed.append(active_job.job_id)
            active_job.windows_job_handle = None
            active_job.windows_reaper_stop.set()

    monkeypatch.setattr(
        scan_jobs,
        "_windows_job_active",
        lambda active_job: (_ for _ in ()).throw(OSError("query unavailable")),
    )
    monkeypatch.setattr(scan_jobs.time, "monotonic", monotonic)
    monkeypatch.setattr(scan_jobs, "_close_windows_job_handle", close_handle)
    scan_jobs._start_windows_job_reaper(job)
    reaper = job.windows_reaper
    assert reaper is not None
    time.sleep(0.3)

    try:
        assert reaper.is_alive()
        assert job.windows_job_handle == 77
        close = getattr(service, "close", None)
        assert callable(close), "LocalScanJobService.close is required"
        monkeypatch.setattr(scan_jobs.time, "monotonic", real_monotonic)
        close()
        assert closed == [job.job_id]
        assert not reaper.is_alive()
    finally:
        job.windows_reaper_stop.set()
        reaper.join(timeout=1)


@pytest.mark.skipif(sys.platform != "win32", reason="Windows process-tree contract")
@pytest.mark.parametrize("error_type", [TypeError, AssertionError])
def test_windows_reaper_reports_unexpected_query_error_at_shutdown(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error_type: type[BaseException],
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job = _job(service, tmp_path, "", returncode=None)
    job.job_id = f"reaper-unexpected-{error_type.__name__.lower()}"
    job.windows_job_handle = 77
    _register_job(service, job)
    query_calls: list[str] = []
    original_query = scan_jobs._windows_job_active

    def fail_query(active_job: _LocalScanJob) -> bool:
        if active_job is not job:
            return original_query(active_job)
        query_calls.append(active_job.job_id)
        raise error_type("unexpected query defect")

    def close_handle(active_job: _LocalScanJob) -> None:
        with active_job.windows_job_lock:  # type: ignore[attr-defined]
            active_job.windows_job_handle = None
            active_job.windows_reaper_stop.set()

    monkeypatch.setattr(scan_jobs, "_windows_job_active", fail_query)
    monkeypatch.setattr(scan_jobs, "_close_windows_job_handle", close_handle)
    scan_jobs._start_windows_job_reaper(job)
    reaper = job.windows_reaper
    assert reaper is not None
    deadline = time.monotonic() + 0.5
    while (
        time.monotonic() < deadline
        and getattr(job, "windows_reaper_error", None) is None
    ):
        time.sleep(0.01)

    try:
        recorded = getattr(job, "windows_reaper_error", None)
        assert isinstance(recorded, error_type)
        time.sleep(0.1)
        assert query_calls == [job.job_id]
        assert reaper.is_alive()
        assert job.windows_job_handle == 77

        with pytest.raises(BaseExceptionGroup, match="shutdown failed") as captured:
            service.close()

        assert captured.value.exceptions == (recorded,)
        assert job.windows_job_handle is None
        assert not reaper.is_alive()
        service.shutdown()
    finally:
        job.windows_reaper_stop.set()
        reaper.join(timeout=1)


def test_app_lifespan_closes_app_owned_scan_service(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    closed: list[Path] = []

    class OwnedScanJobs:
        def __init__(self, root: Path) -> None:
            self.root = root

        def close(self) -> None:
            closed.append(self.root)

    monkeypatch.setattr(web_main, "LocalScanJobService", OwnedScanJobs)
    app = web_main.create_app(
        runtime_dir=tmp_path / "runtime",
        harmonization_jobs=object(),  # type: ignore[arg-type]
    )

    async def run_lifespan() -> None:
        async with app.router.lifespan_context(app):
            assert closed == []

    asyncio.run(run_lifespan())

    assert closed == [tmp_path / "runtime" / "web_jobs"]


def test_app_lifespan_does_not_close_injected_scan_service(tmp_path: Path) -> None:
    class InjectedScanJobs:
        def __init__(self) -> None:
            self.close_calls = 0

        def close(self) -> None:
            self.close_calls += 1

    injected = InjectedScanJobs()
    app = web_main.create_app(
        runtime_dir=tmp_path / "runtime",
        scan_jobs=injected,  # type: ignore[arg-type]
        harmonization_jobs=object(),  # type: ignore[arg-type]
    )

    async def run_lifespan() -> None:
        async with app.router.lifespan_context(app):
            pass

    asyncio.run(run_lifespan())

    assert injected.close_calls == 0


def test_app_lifespan_closes_owned_scan_service_when_startup_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    close_calls: list[None] = []

    class OwnedScanJobs:
        def __init__(self, root: Path) -> None:
            pass

        def close(self) -> None:
            close_calls.append(None)

    class FailingHarmonizationJobs:
        def recover_interrupted_jobs(self) -> None:
            raise RuntimeError("startup recovery failed")

    monkeypatch.setattr(web_main, "LocalScanJobService", OwnedScanJobs)
    monkeypatch.setattr(
        web_main,
        "WorkerHarmonizationService",
        FailingHarmonizationJobs,
    )
    app = web_main.create_app(runtime_dir=tmp_path / "runtime")

    async def run_lifespan() -> None:
        async with app.router.lifespan_context(app):
            pass

    with pytest.raises(RuntimeError, match="startup recovery failed"):
        asyncio.run(run_lifespan())

    assert close_calls == [None]


def test_app_lifespan_groups_startup_and_owned_scan_cleanup_failures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    primary = RuntimeError("startup recovery failed")
    cleanup = OSError("scan cleanup failed")

    class OwnedScanJobs:
        def __init__(self, root: Path) -> None:
            pass

        def close(self) -> None:
            raise cleanup

    class FailingHarmonizationJobs:
        def recover_interrupted_jobs(self) -> None:
            raise primary

    monkeypatch.setattr(web_main, "LocalScanJobService", OwnedScanJobs)
    monkeypatch.setattr(
        web_main,
        "WorkerHarmonizationService",
        FailingHarmonizationJobs,
    )
    app = web_main.create_app(runtime_dir=tmp_path / "runtime")

    async def run_lifespan() -> None:
        async with app.router.lifespan_context(app):
            pass

    with pytest.raises(BaseExceptionGroup) as captured:
        asyncio.run(run_lifespan())

    assert captured.value.exceptions == (primary, cleanup)


def test_app_lifespan_groups_body_and_owned_scan_cleanup_failures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    primary = LookupError("lifespan body failed")
    cleanup = OSError("scan cleanup failed")

    class OwnedScanJobs:
        def __init__(self, root: Path) -> None:
            pass

        def close(self) -> None:
            raise cleanup

    monkeypatch.setattr(web_main, "LocalScanJobService", OwnedScanJobs)
    app = web_main.create_app(
        runtime_dir=tmp_path / "runtime",
        harmonization_jobs=object(),  # type: ignore[arg-type]
    )

    async def run_lifespan() -> None:
        async with app.router.lifespan_context(app):
            raise primary

    with pytest.raises(BaseExceptionGroup) as captured:
        asyncio.run(run_lifespan())

    assert captured.value.exceptions == (primary, cleanup)


def test_app_lifespan_raises_owned_scan_cleanup_failure_directly(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cleanup = OSError("scan cleanup failed")

    class OwnedScanJobs:
        def __init__(self, root: Path) -> None:
            pass

        def close(self) -> None:
            raise cleanup

    monkeypatch.setattr(web_main, "LocalScanJobService", OwnedScanJobs)
    app = web_main.create_app(
        runtime_dir=tmp_path / "runtime",
        harmonization_jobs=object(),  # type: ignore[arg-type]
    )

    async def run_lifespan() -> None:
        async with app.router.lifespan_context(app):
            pass

    with pytest.raises(OSError) as captured:
        asyncio.run(run_lifespan())

    assert captured.value is cleanup


@pytest.mark.skipif(sys.platform != "win32", reason="Windows process-tree contract")
def test_scan_stop_terminates_a_real_windows_child_process(tmp_path: Path) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    child_pid_path = tmp_path / "child.pid"
    parent_script = (
        "import pathlib,subprocess,sys,time;"
        "child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']);"
        f"pathlib.Path({str(child_pid_path)!r}).write_text(str(child.pid),encoding='utf-8');"
        "time.sleep(60)"
    )

    def process_exists(pid: int) -> bool:
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            check=False,
            capture_output=True,
            timeout=5,
        )
        return f'"{pid}"'.encode("ascii") in (result.stdout or b"")

    snapshot = service.start(["python", "-c", parent_script])
    child_pid = 0
    try:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and not child_pid_path.exists():
            time.sleep(0.05)
        child_pid = int(child_pid_path.read_text(encoding="utf-8"))
        assert process_exists(child_pid)

        stopped = service.stop(str(snapshot["job_id"]))

        assert stopped["status"] == "stopped"
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and process_exists(child_pid):
            time.sleep(0.05)
        assert not process_exists(child_pid)
    finally:
        if child_pid and process_exists(child_pid):
            service.stop(str(snapshot["job_id"]))


@pytest.mark.skipif(sys.platform != "win32", reason="Windows restart/process-tree contract")
def test_scan_restart_recovers_and_stops_real_windows_process_tree(tmp_path: Path) -> None:
    root = tmp_path / "jobs"
    first_service = LocalScanJobService(root, cwd=tmp_path)
    child_pid_path = tmp_path / "restart-child.pid"
    parent_script = (
        "import pathlib,subprocess,sys,time;"
        "child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']);"
        f"pathlib.Path({str(child_pid_path)!r}).write_text(str(child.pid),encoding='utf-8');"
        "time.sleep(60)"
    )

    snapshot = first_service.start(["python", "-c", parent_script], owner_id="owner-restart")
    child_pid = 0
    try:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and not child_pid_path.exists():
            time.sleep(0.05)
        child_pid = int(child_pid_path.read_text(encoding="utf-8"))

        recovered_service = LocalScanJobService(root, cwd=tmp_path)
        recovered = recovered_service.get(str(snapshot["job_id"]))
        assert recovered["status"] == "running"
        assert recovered["owner_id"] == "owner-restart"

        stopped = recovered_service.stop(str(snapshot["job_id"]))
        assert stopped["status"] == "stopped"
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and scan_jobs.psutil.pid_exists(child_pid):
            time.sleep(0.05)
        assert not scan_jobs.psutil.pid_exists(child_pid)
    finally:
        if child_pid and scan_jobs.psutil.pid_exists(child_pid):
            first_service.stop(str(snapshot["job_id"]))


@pytest.mark.skipif(sys.platform != "win32", reason="Windows owner-process restart contract")
def test_windows_named_job_survives_original_service_process_exit(tmp_path: Path) -> None:
    root = tmp_path / "jobs"
    job_id_path = tmp_path / "job-id.txt"
    project_root = Path(scan_jobs.__file__).resolve().parents[2]
    holder_code = (
        "import os,sys; from pathlib import Path; "
        "from apps.web.scan_jobs import LocalScanJobService; "
        f"service=LocalScanJobService(Path({str(root)!r}),cwd=Path({str(tmp_path)!r})); "
        "snapshot=service.start([sys.executable,'-c','import time; time.sleep(60)']); "
        f"Path({str(job_id_path)!r}).write_text(str(snapshot['job_id']),encoding='utf-8'); "
        "os._exit(0)"
    )
    environment = {**os.environ, "PYTHONPATH": str(project_root)}
    result = subprocess.run(
        [sys.executable, "-c", holder_code],
        cwd=project_root,
        env=environment,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0
    job_id = job_id_path.read_text(encoding="utf-8")
    recovered = LocalScanJobService(root, cwd=tmp_path)
    try:
        assert recovered.get(job_id)["status"] == "running"
        assert recovered.stop(job_id)["status"] == "stopped"
    finally:
        if recovered.get(job_id)["status"] in {"starting", "running"}:
            recovered.stop(job_id)


def test_scan_restart_fails_closed_when_pid_identity_changed(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = tmp_path / "jobs"
    first_service = LocalScanJobService(root, cwd=tmp_path)
    snapshot = first_service.start(
        ["python", "-c", "import time; time.sleep(60)"], owner_id="owner-a"
    )
    job_id = str(snapshot["job_id"])
    state_path = root / f"{job_id}.state.json"
    try:
        persisted = json.loads(state_path.read_text(encoding="utf-8"))
        assert persisted["pid"] > 0
        assert persisted["process_create_time"] > 0
        assert persisted["process_group_id"] == persisted["pid"]
        assert len(persisted["process_group_token"]) == 32
        assert "process_group_token" not in snapshot
        assert persisted["owner_id"] == "owner-a"
        assert persisted["stdout_path"].endswith(".stdout.log")
        assert persisted["stderr_path"].endswith(".stderr.log")

        original_create_time = scan_jobs._process_create_time
        with monkeypatch.context() as scoped:
            scoped.setattr(
                scan_jobs,
                "_process_create_time",
                lambda pid: float(persisted["process_create_time"]) + 100.0,
            )
            recovered_service = LocalScanJobService(root, cwd=tmp_path)
            assert recovered_service.get(job_id)["status"] == "running"
            assert recovered_service.stop(job_id)["status"] == "stopped"
        assert scan_jobs._process_create_time is original_create_time
    finally:
        first_service.stop(job_id)


def test_service_created_before_job_adopts_later_persisted_job(tmp_path: Path) -> None:
    root = tmp_path / "jobs"
    observer = LocalScanJobService(root, cwd=tmp_path)
    writer = LocalScanJobService(root, cwd=tmp_path)
    command = [sys.executable, "-c", "import time; time.sleep(30)"]
    owner_id = "owner-late-adoption"
    job_id = "scan-op-late-adoption-1234"
    job_owned = False
    observer_terminal = False

    try:
        started = writer.start(command, owner_id=owner_id, job_id=job_id)
        job_owned = True

        observed = observer.get(job_id)

        assert observed["job_id"] == started["job_id"] == job_id
        assert observed["owner_id"] == started["owner_id"] == owner_id
        assert observed["command"] == started["command"] == command
        assert observed["status"] == started["status"]
        assert observed["status"] in {"starting", "running"}

        stopped = observer.stop(job_id)
        observer_terminal = stopped["status"] in _TERMINAL_SCAN_STATUSES
        assert stopped["status"] == "stopped"
    finally:
        job_owned = job_owned or job_id in writer._jobs
        if job_owned:
            _cleanup_owned_scan_job(
                writer,
                root,
                tmp_path,
                job_id,
                terminal=observer_terminal,
                prior_error=sys.exception(),
            )


def test_existing_deterministic_job_is_replayed_without_second_spawn(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = tmp_path / "jobs"
    observer = LocalScanJobService(root, cwd=tmp_path)
    writer = LocalScanJobService(root, cwd=tmp_path)
    command = [sys.executable, "-c", "import time; time.sleep(30)"]
    owner_id = "owner-a"
    job_id = "scan-op-single-spawn-1234"
    job_owned = False
    job_terminal = False
    spawn_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def reject_spawn(*args, **kwargs):
        spawn_calls.append((args, kwargs))
        raise AssertionError("existing deterministic job attempted a second spawn")

    try:
        started = writer.start(command, owner_id=owner_id, job_id=job_id)
        job_owned = True
        with monkeypatch.context() as scoped:
            scoped.setattr(scan_jobs.subprocess, "Popen", reject_spawn)

            replayed = observer.start(command, owner_id=owner_id, job_id=job_id)

        assert spawn_calls == []
        assert replayed["job_id"] == started["job_id"] == job_id
        assert replayed["owner_id"] == started["owner_id"] == owner_id
        assert replayed["command"] == started["command"] == command
    finally:
        job_owned = job_owned or job_id in writer._jobs
        if job_owned:
            _cleanup_owned_scan_job(
                writer,
                root,
                tmp_path,
                job_id,
                terminal=job_terminal,
                prior_error=sys.exception(),
            )


def test_start_replay_validates_identity_before_releasing_existing_job(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job = _job(service, tmp_path, "", returncode=None)
    job.job_id = "scan-op-start-replay-identity-1234"
    job.command = ["python", "-m", "expected.scan"]
    job.owner_id = "owner-a"
    job.start_released = False
    job.process = StoppableProcess()
    job.process_create_time = 1.0
    job.process_group_id = job.process.pid
    job.process_group_token = "a" * 32
    job.stdout_path = service._stdout_path(job.job_id)
    job.stderr_path = service._stderr_path(job.job_id)
    job.stdout_path.write_text("", encoding="utf-8")
    job.stderr_path.write_text("", encoding="utf-8")
    _register_job(service, job)
    service._persist_job(job)
    release_calls: list[str] = []

    def release(active_job: _LocalScanJob) -> dict[str, object]:
        release_calls.append(active_job.job_id)
        return {
            "executes": True,
            "job_id": active_job.job_id,
            "status": "starting",
            "command": list(active_job.command),
            "owner_id": active_job.owner_id,
        }

    monkeypatch.setattr(service, "_release_registered_start", release)

    with pytest.raises(scan_jobs.ScanJobReplayIdentityError):
        service.start(
            ["python", "-m", "different.scan"],
            owner_id="owner-a",
            job_id=job.job_id,
        )

    assert release_calls == []


def test_corrupt_persisted_deterministic_job_fails_closed_before_spawn(
    tmp_path: Path,
    monkeypatch,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job_id = "scan-op-corrupt-state-1234"
    with service._process_lock(job_id):
        pass
    service._state_path(job_id).write_text("{not-json", encoding="utf-8")
    spawn_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def reject_spawn(*args, **kwargs):
        spawn_calls.append((args, kwargs))
        raise AssertionError("corrupt durable authority attempted a spawn")

    with monkeypatch.context() as scoped:
        scoped.setattr(scan_jobs.subprocess, "Popen", reject_spawn)
        with pytest.raises(ProcessAuthorityAmbiguousError, match="unreadable"):
            service.start(
                [sys.executable, "-c", "pass"],
                owner_id="owner-a",
                job_id=job_id,
            )
    assert spawn_calls == []


def test_deterministic_job_command_identity_is_immutable_at_public_boundary(
    tmp_path: Path,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    command = [sys.executable, "-c", "import time; time.sleep(30)"]
    expected_command = list(command)
    owner_id = "owner-immutable-command"
    job_id = "scan-op-immutable-command-1234"
    started = service.start(command, owner_id=owner_id, job_id=job_id)

    try:
        command.append("caller-mutation")
        started["command"].append("snapshot-mutation")

        replayed = service.start(
            expected_command,
            owner_id=owner_id,
            job_id=job_id,
        )
        persisted = json.loads(service._state_path(job_id).read_text(encoding="utf-8"))

        assert replayed["command"] == expected_command
        assert service._jobs[job_id].command == expected_command
        assert persisted["command"] == expected_command
    finally:
        service.stop(job_id)


def test_start_release_is_scoped_to_the_registered_attempt(
    tmp_path: Path,
    monkeypatch,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job = _job(service, tmp_path, "", returncode=None)
    job.job_id = "scan-op-attempt-release-1234"
    job.process_group_token = "b" * 32
    job.start_released = False
    abandoned_token = "a" * 32
    abandoned_release = service._start_release_path(job.job_id, abandoned_token)
    current_release = service._start_release_path(
        job.job_id, job.process_group_token
    )
    current_started = service._start_started_path(
        job.job_id, job.process_group_token
    )
    current_started.write_text("43210", encoding="ascii")
    monkeypatch.setattr(scan_jobs, "_job_runtime_active", lambda active_job: True)
    monkeypatch.setattr(scan_jobs, "_windows_job_active", lambda active_job: True)

    snapshot = service._release_registered_start(job)

    assert abandoned_release != current_release
    assert job.process_group_token not in current_release.name
    assert not abandoned_release.exists()
    assert current_release.read_bytes() == b"release\n"
    assert snapshot["status"] == "running"


@pytest.mark.parametrize("invalid_id", INVALID_AUTHORITY_IDS)
def test_scan_id_helpers_reject_before_path_or_lock_access(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    invalid_id: str,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    token = "a" * 32
    process_lock_calls: list[str] = []
    start_lock_calls: list[str] = []

    @contextmanager
    def unexpected_process_lock(job_id: str):
        process_lock_calls.append(job_id)
        yield

    @contextmanager
    def unexpected_start_lock(job_id: str):
        start_lock_calls.append(job_id)
        yield

    monkeypatch.setattr(service, "_process_lock", unexpected_process_lock)
    monkeypatch.setattr(service, "_start_process_lock", unexpected_start_lock)

    helpers = [
        ("_state_path", (invalid_id,)),
        ("_stdout_path", (invalid_id,)),
        ("_stderr_path", (invalid_id,)),
        ("_start_artifact_path", (invalid_id, token, "release")),
        ("_start_release_path", (invalid_id, token)),
        ("_start_started_path", (invalid_id, token)),
        ("_start_result_path", (invalid_id, token)),
    ]
    for helper_name, arguments in helpers:
        helper = getattr(service, helper_name, None)
        assert callable(helper), f"missing scan path helper {helper_name}"
        with pytest.raises(ValueError):
            helper(*arguments)

    with pytest.raises(ValueError):
        service.get(invalid_id)
    with pytest.raises(ValueError):
        service.get_for_replay(
            invalid_id,
            expected_command=["python", "-V"],
            expected_owner_id="operator",
        )
    with pytest.raises(ValueError):
        service.stop(invalid_id)
    with pytest.raises(ValueError):
        service.start(["python", "-V"], job_id=invalid_id)

    assert process_lock_calls == []
    assert start_lock_calls == []
    assert list((tmp_path / "jobs").iterdir()) == []


@pytest.mark.parametrize("operation", ["get", "replay"])
def test_unknown_scan_reads_do_not_create_permanent_process_locks(
    tmp_path: Path,
    operation: str,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job_id = "scan-valid-looking-miss"

    with pytest.raises(KeyError):
        if operation == "get":
            service.get(job_id)
        else:
            service.get_for_replay(
                job_id,
                expected_command=["python", "-V"],
                expected_owner_id="operator-a",
            )

    assert list(root.iterdir()) == []


def _observation_job(
    service: LocalScanJobService,
    root: Path,
    job_id: str,
) -> _LocalScanJob:
    job = _job(service, root, "", returncode=None)
    job.job_id = job_id
    process = StoppableProcess()
    job.process = process
    job.process_create_time = 1.0
    job.process_group_id = process.pid
    job.process_group_token = "a" * 32
    job.owner_id = "owner-a"
    job.start_released = False
    job.stdout_path = service._stdout_path(job_id)
    job.stderr_path = service._stderr_path(job_id)
    job.stdout_path.write_text("", encoding="utf-8")
    job.stderr_path.write_text("", encoding="utf-8")
    service._jobs[job_id] = job
    return job


def test_persist_job_publishes_process_lock_before_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, "scan-persist-lock-order")
    state_path = service._state_path(job.job_id)
    lock_path = root / f".{job.job_id}.lock"
    original_write = scan_jobs.durable_write_bytes
    state_publications: list[Path] = []

    def observed_write(path: Path, data: bytes) -> None:
        if Path(path) == state_path:
            assert lock_path.stat().st_size == 1
            state_publications.append(Path(path))
        original_write(path, data)

    monkeypatch.setattr(scan_jobs, "durable_write_bytes", observed_write)

    service._persist_job(job)

    assert state_publications == [state_path]
    assert state_path.exists()
    assert lock_path.read_bytes() == b"0"


@pytest.mark.parametrize("owned", [False, True], ids=["observe", "observe-owned"])
def test_observe_legacy_state_without_process_lock_fails_closed_without_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    owned: bool,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, "scan-observe-legacy-lock")
    service._persist_job(job)
    lock_path = root / f".{job.job_id}.lock"
    lock_path.unlink(missing_ok=True)
    before = {
        path.name: path.read_bytes()
        for path in root.iterdir()
        if path.is_file()
    }
    monkeypatch.setattr(scan_jobs, "_job_runtime_active", lambda _job: True)

    with pytest.raises(ProcessAuthorityAmbiguousError, match="lock"):
        if owned:
            service.observe_owned(job.job_id, expected_owner_id="owner-a")
        else:
            service.observe(job.job_id)

    assert not lock_path.exists()
    assert {
        path.name: path.read_bytes()
        for path in root.iterdir()
        if path.is_file()
    } == before


def test_startup_recovery_rejects_legacy_state_without_lock_without_adoption(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    writer = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(writer, root, "scan-legacy-before-service-init")
    writer._persist_job(job)
    lock_path = root / f".{job.job_id}.lock"
    lock_path.unlink()
    state_path = writer._state_path(job.job_id)
    before = state_path.read_bytes()
    monkeypatch.setattr(scan_jobs, "_job_runtime_active", lambda _job: True)

    with pytest.raises(ProcessAuthorityAmbiguousError, match="lock"):
        LocalScanJobService(root, cwd=tmp_path)

    assert not lock_path.exists()
    assert state_path.read_bytes() == before


@pytest.mark.parametrize("operation", ["get", "replay", "stop"])
def test_existing_job_operations_reject_legacy_state_without_lock_without_synthesis(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, f"scan-legacy-{operation}-lock")
    service._persist_job(job)
    lock_path = root / f".{job.job_id}.lock"
    lock_path.unlink()
    state_path = service._state_path(job.job_id)
    before = state_path.read_bytes()
    service._jobs.pop(job.job_id)
    monkeypatch.setattr(scan_jobs, "_job_runtime_active", lambda _job: True)

    expected_error = (
        scan_jobs.ScanJobReplayAuthorityError
        if operation == "replay"
        else ProcessAuthorityAmbiguousError
    )
    with pytest.raises(expected_error, match="lock"):
        if operation == "get":
            service.get(job.job_id)
        elif operation == "replay":
            service.get_for_replay(
                job.job_id,
                expected_command=job.command,
                expected_owner_id=job.owner_id,
            )
        else:
            service.stop(job.job_id)

    assert job.job_id not in service._jobs
    assert not lock_path.exists()
    assert state_path.read_bytes() == before


def test_observe_process_lock_disappearance_fails_closed_without_recreation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, "scan-observe-lock-disappears")
    service._persist_job(job)
    lock_path = root / f".{job.job_id}.lock"
    if not lock_path.exists():
        lock_path.write_bytes(b"0")
    state_bytes = service._state_path(job.job_id).read_bytes()
    original_open = scan_jobs.os.open
    removed = False

    def racing_open(path, flags, *args, **kwargs):
        nonlocal removed
        if Path(path) == lock_path and not removed:
            removed = True
            lock_path.unlink()
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(scan_jobs.os, "open", racing_open)
    monkeypatch.setattr(scan_jobs, "_job_runtime_active", lambda _job: True)

    with pytest.raises(ProcessAuthorityAmbiguousError, match="lock"):
        service.observe(job.job_id)

    assert removed is True
    assert not lock_path.exists()
    assert service._state_path(job.job_id).read_bytes() == state_bytes


def test_observe_unreadable_process_lock_normalizes_permission_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, "scan-observe-lock-permission")
    service._persist_job(job)
    lock_path = root / f".{job.job_id}.lock"
    if not lock_path.exists():
        lock_path.write_bytes(b"0")
    before = lock_path.read_bytes()
    original_open = scan_jobs.os.open

    def denied_open(path, flags, *args, **kwargs):
        if Path(path) == lock_path and not flags & os.O_CREAT:
            raise PermissionError(errno.EACCES, "lock denied")
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(scan_jobs.os, "open", denied_open)
    monkeypatch.setattr(scan_jobs, "_job_runtime_active", lambda _job: True)

    with pytest.raises(ProcessAuthorityAmbiguousError, match="lock"):
        service.observe(job.job_id)

    assert lock_path.read_bytes() == before


def test_observe_replaced_process_lock_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, "scan-observe-lock-replaced")
    service._persist_job(job)
    lock_path = root / f".{job.job_id}.lock"
    if not lock_path.exists():
        lock_path.write_bytes(b"0")
    original_open = scan_jobs.os.open
    original_stat = scan_jobs.os.stat
    existing_lock_opened = False

    def observed_open(path, flags, *args, **kwargs):
        nonlocal existing_lock_opened
        descriptor = original_open(path, flags, *args, **kwargs)
        if Path(path) == lock_path and not flags & os.O_CREAT:
            existing_lock_opened = True
        return descriptor

    def replaced_stat(path, *args, **kwargs):
        result = original_stat(path, *args, **kwargs)
        if Path(path) != lock_path or not existing_lock_opened:
            return result
        values = list(result)
        values[1] += 1
        return os.stat_result(values)

    monkeypatch.setattr(scan_jobs.os, "open", observed_open)
    monkeypatch.setattr(scan_jobs.os, "stat", replaced_stat)
    monkeypatch.setattr(scan_jobs, "_job_runtime_active", lambda _job: True)

    with pytest.raises(ProcessAuthorityAmbiguousError, match="lock"):
        service.observe(job.job_id)

    assert existing_lock_opened is True


@pytest.mark.parametrize(
    "identity_index",
    [pytest.param(1, id="posix-inode"), pytest.param(2, id="windows-volume")],
)
def test_observe_revalidates_process_lock_identity_after_yield(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    identity_index: int,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, "scan-observe-post-yield-identity")
    service._persist_job(job)
    lock_path = root / f".{job.job_id}.lock"
    state_bytes = service._state_path(job.job_id).read_bytes()
    original_stat = scan_jobs.os.stat
    observation_yielded = False

    def active(_job: _LocalScanJob) -> bool:
        nonlocal observation_yielded
        observation_yielded = True
        return True

    def replaced_stat(path, *args, **kwargs):
        result = original_stat(path, *args, **kwargs)
        if Path(path) != lock_path or not observation_yielded:
            return result
        values = list(result)
        values[identity_index] += 1
        return os.stat_result(values)

    monkeypatch.setattr(scan_jobs, "_job_runtime_active", active)
    monkeypatch.setattr(scan_jobs.os, "stat", replaced_stat)

    with pytest.raises(ProcessAuthorityAmbiguousError, match="lock"):
        service.observe(job.job_id)

    assert observation_yielded is True
    assert service._state_path(job.job_id).read_bytes() == state_bytes


def test_observe_revalidates_process_lock_presence_after_yield(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, "scan-observe-post-yield-missing")
    service._persist_job(job)
    lock_path = root / f".{job.job_id}.lock"
    state_bytes = service._state_path(job.job_id).read_bytes()
    original_stat = scan_jobs.os.stat
    observation_yielded = False

    def active(_job: _LocalScanJob) -> bool:
        nonlocal observation_yielded
        observation_yielded = True
        return True

    def missing_stat(path, *args, **kwargs):
        if Path(path) == lock_path and observation_yielded:
            raise FileNotFoundError(lock_path)
        return original_stat(path, *args, **kwargs)

    monkeypatch.setattr(scan_jobs, "_job_runtime_active", active)
    monkeypatch.setattr(scan_jobs.os, "stat", missing_stat)

    with pytest.raises(ProcessAuthorityAmbiguousError, match="lock"):
        service.observe(job.job_id)

    assert observation_yielded is True
    assert service._state_path(job.job_id).read_bytes() == state_bytes


def test_observe_revalidates_process_lock_marker_after_yield(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, "scan-observe-post-yield-marker")
    service._persist_job(job)
    lock_path = root / f".{job.job_id}.lock"
    original_fdopen = scan_jobs.os.fdopen
    marker_reads = 0

    class ChangingMarkerHandle:
        def __init__(self, handle) -> None:
            self._handle = handle

        def __enter__(self):
            self._handle.__enter__()
            return self

        def __exit__(self, *args):
            return self._handle.__exit__(*args)

        def fileno(self) -> int:
            return self._handle.fileno()

        def close(self) -> None:
            self._handle.close()

        def seek(self, *args):
            return self._handle.seek(*args)

        def read(self, size: int = -1) -> bytes:
            nonlocal marker_reads
            marker_reads += 1
            marker = self._handle.read(size)
            return b"x" if marker_reads > 1 else marker

    def changing_fdopen(descriptor: int, *args, **kwargs):
        is_lock = os.path.samestat(
            os.fstat(descriptor),
            scan_jobs.os.stat(lock_path, follow_symlinks=False),
        )
        handle = original_fdopen(descriptor, *args, **kwargs)
        return ChangingMarkerHandle(handle) if is_lock else handle

    monkeypatch.setattr(scan_jobs.os, "fdopen", changing_fdopen)
    monkeypatch.setattr(scan_jobs, "_job_runtime_active", lambda _job: True)

    with pytest.raises(ProcessAuthorityAmbiguousError, match="lock"):
        service.observe(job.job_id)

    assert marker_reads == 2


@pytest.mark.parametrize(
    "existing_bytes",
    [
        pytest.param(b"", id="zero-length"),
        pytest.param(b"00", id="extra-byte"),
        pytest.param(b"x", id="wrong-marker"),
    ],
)
def test_persist_rejects_existing_malformed_process_lock_without_state_publication(
    tmp_path: Path,
    existing_bytes: bytes,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, "scan-persist-malformed-lock")
    lock_path = root / f".{job.job_id}.lock"
    lock_path.write_bytes(existing_bytes)

    with pytest.raises(ProcessAuthorityAmbiguousError, match="lock"):
        service._persist_job(job)

    assert lock_path.read_bytes() == existing_bytes
    assert not service._state_path(job.job_id).exists()
    assert list(root.glob(f"{lock_path.name}.tmp.*")) == []


def test_persist_rejects_existing_process_lock_symlink_without_state_publication(
    tmp_path: Path,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, "scan-persist-symlink-lock")
    lock_path = root / f".{job.job_id}.lock"
    target = root / "foreign-lock"
    target.write_bytes(b"0")
    try:
        lock_path.symlink_to(target)
    except OSError as exc:
        pytest.skip(f"file symlink unavailable: {exc}")

    with pytest.raises(ProcessAuthorityAmbiguousError, match="lock"):
        service._persist_job(job)

    assert lock_path.is_symlink()
    assert target.read_bytes() == b"0"
    assert not service._state_path(job.job_id).exists()


def test_posix_authority_root_is_tightened_before_process_lock_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job_id = "scan-posix-root-mode"
    lock_path = service._process_lock_path(job_id)
    root_mode = {"value": 0o777}
    events: list[str] = []
    original_lstat = scan_jobs.os.lstat
    original_stat = scan_jobs.os.stat
    original_chmod = scan_jobs.os.chmod
    original_link = scan_jobs.os.link

    def root_attributes() -> SimpleNamespace:
        return SimpleNamespace(
            st_mode=scan_jobs.stat.S_IFDIR | root_mode["value"],
            st_file_attributes=0,
        )

    def observed_lstat(path, *args, **kwargs):
        if Path(path) == root:
            events.append("lstat")
            return root_attributes()
        return original_lstat(path, *args, **kwargs)

    def observed_chmod(path, mode, *args, **kwargs) -> None:
        if Path(path) == root:
            events.append("chmod")
            assert mode == 0o700
            root_mode["value"] = mode
            return
        original_chmod(path, mode, *args, **kwargs)

    def observed_stat(path, *args, **kwargs):
        if Path(path) == root:
            events.append("stat")
            assert kwargs.get("follow_symlinks") is False
            return root_attributes()
        return original_stat(path, *args, **kwargs)

    def observed_link(source, destination, *args, **kwargs) -> None:
        if Path(destination) == lock_path:
            events.append("link")
            assert root_mode["value"] == 0o700
            assert events[-3:] == ["chmod", "stat", "link"]
        original_link(source, destination, *args, **kwargs)

    monkeypatch.setattr(scan_jobs, "_IS_WINDOWS", False, raising=False)
    monkeypatch.setattr(scan_jobs.os, "lstat", observed_lstat)
    monkeypatch.setattr(scan_jobs.os, "chmod", observed_chmod)
    monkeypatch.setattr(scan_jobs.os, "stat", observed_stat)
    monkeypatch.setattr(scan_jobs.os, "link", observed_link)

    service._publish_initialized_process_lock(job_id)

    assert root_mode["value"] == 0o700
    assert lock_path.read_bytes() == b"0"


def test_posix_authority_root_chmod_failure_publishes_nothing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job_id = "scan-posix-root-chmod-failure"
    lock_path = service._process_lock_path(job_id)
    state_path = service._state_path(job_id)
    original_chmod = scan_jobs.os.chmod

    def failing_chmod(path, mode, *args, **kwargs) -> None:
        if Path(path) == root:
            raise OSError("injected authority root chmod failure")
        original_chmod(path, mode, *args, **kwargs)

    monkeypatch.setattr(scan_jobs, "_IS_WINDOWS", False, raising=False)
    monkeypatch.setattr(scan_jobs.os, "chmod", failing_chmod)

    with pytest.raises(OSError, match="authority root chmod"):
        service._publish_initialized_process_lock(job_id)

    assert not lock_path.exists()
    assert not state_path.exists()
    assert list(root.glob(f"{lock_path.name}.tmp.*")) == []


def test_nested_persistence_reuses_held_lock_before_any_temp_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, "scan-nested-held-lock")
    lock_path = service._process_lock_path(job.job_id)
    lock_temp_prefix = f"{lock_path.name}.tmp."
    original_open = scan_jobs.os.open
    lifecycle_calls: list[str] = []

    def reject_lock_temp(path, flags, *args, **kwargs):
        if Path(path).name.startswith(lock_temp_prefix):
            lifecycle_calls.append("temp-open")
            raise OSError("injected nested lock temp failure")
        return original_open(path, flags, *args, **kwargs)

    def reject_lock_link(*args, **kwargs) -> None:
        lifecycle_calls.append("link")
        raise OSError("injected nested lock link failure")

    with service._process_lock(job.job_id):
        monkeypatch.setattr(scan_jobs.os, "open", reject_lock_temp)
        monkeypatch.setattr(scan_jobs.os, "link", reject_lock_link)
        service._persist_job(job)

    assert lifecycle_calls == []
    assert service._state_path(job.job_id).exists()
    assert list(root.glob(f"{lock_path.name}.tmp.*")) == []


def test_persist_never_exposes_incomplete_canonical_process_lock(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, "scan-persist-private-lock-temp")
    lock_path = root / f".{job.job_id}.lock"
    original_open = scan_jobs.os.open
    original_fsync = scan_jobs.os.fsync
    lock_descriptors: set[int] = set()

    def observed_open(path, flags, *args, **kwargs):
        descriptor = original_open(path, flags, *args, **kwargs)
        if Path(path) == lock_path or Path(path).name.startswith(f"{lock_path.name}.tmp."):
            lock_descriptors.add(descriptor)
        return descriptor

    def observed_fsync(descriptor: int) -> None:
        if descriptor in lock_descriptors:
            assert not lock_path.exists()
        original_fsync(descriptor)

    monkeypatch.setattr(scan_jobs.os, "open", observed_open)
    monkeypatch.setattr(scan_jobs.os, "fsync", observed_fsync)

    service._persist_job(job)

    assert lock_path.read_bytes() == b"0"
    assert list(root.glob(f"{lock_path.name}.tmp.*")) == []


@pytest.mark.parametrize(
    "failure_stage",
    [
        pytest.param(
            "chmod",
            marks=pytest.mark.skipif(
                os.name == "nt",
                reason="Windows lock authority is inherited from the root DACL",
            ),
        ),
        "fdopen",
    ],
)
def test_process_lock_temp_setup_failure_closes_descriptor_and_cleans_temp(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_stage: str,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, f"scan-lock-temp-{failure_stage}")
    lock_path = root / f".{job.job_id}.lock"
    original_open = scan_jobs.os.open
    original_chmod = scan_jobs.os.chmod
    original_fdopen = scan_jobs.os.fdopen
    temporary_descriptor: int | None = None

    def observed_open(path, flags, *args, **kwargs):
        nonlocal temporary_descriptor
        descriptor = original_open(path, flags, *args, **kwargs)
        if Path(path).name.startswith(f"{lock_path.name}.tmp."):
            temporary_descriptor = descriptor
        return descriptor

    def failing_chmod(path, mode) -> None:
        if failure_stage == "chmod" and Path(path).name.startswith(
            f"{lock_path.name}.tmp."
        ):
            raise OSError("injected lock temp chmod failure")
        original_chmod(path, mode)

    def failing_fdopen(descriptor: int, *args, **kwargs):
        if failure_stage == "fdopen" and descriptor == temporary_descriptor:
            raise OSError("injected lock temp fdopen failure")
        return original_fdopen(descriptor, *args, **kwargs)

    monkeypatch.setattr(scan_jobs.os, "open", observed_open)
    monkeypatch.setattr(scan_jobs.os, "chmod", failing_chmod)
    monkeypatch.setattr(scan_jobs.os, "fdopen", failing_fdopen)

    with pytest.raises(OSError, match="injected lock temp"):
        service._persist_job(job)

    assert temporary_descriptor is not None
    descriptor_closed = False
    try:
        os.fstat(temporary_descriptor)
    except OSError:
        descriptor_closed = True
    finally:
        if not descriptor_closed:
            os.close(temporary_descriptor)
    assert descriptor_closed is True
    assert not lock_path.exists()
    assert list(root.glob(f"{lock_path.name}.tmp.*")) == []
    assert not service._state_path(job.job_id).exists()


def test_locked_process_lock_preserves_body_then_validation_unlock_and_close_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    lock_path = service._process_lock_path("scan-lock-error-order")
    body_error = RuntimeError("body failed")
    validation_error = ProcessAuthorityAmbiguousError("post validation failed")
    unlock_error = OSError("unlock failed")
    close_error = OSError("close failed")
    validation_calls = 0
    lock_calls = 0

    class Handle:
        def fileno(self) -> int:
            return 123

        def seek(self, *_args) -> int:
            return 0

        def close(self) -> None:
            raise close_error

        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            self.close()

    def validate(_path: Path, _handle: object) -> None:
        nonlocal validation_calls
        validation_calls += 1
        if validation_calls > 1:
            raise validation_error

    def locking(*_args) -> None:
        nonlocal lock_calls
        lock_calls += 1
        if lock_calls > 1:
            raise unlock_error

    monkeypatch.setattr(service, "_open_existing_process_lock", lambda _path: Handle())
    monkeypatch.setattr(service, "_validate_open_process_lock", validate)
    if os.name == "nt":
        import msvcrt

        monkeypatch.setattr(msvcrt, "locking", locking)
    else:
        import fcntl

        monkeypatch.setattr(fcntl, "flock", locking)

    with pytest.raises(BaseExceptionGroup) as captured:
        with service._locked_process_lock(lock_path):
            raise body_error

    assert captured.value.exceptions == (
        body_error,
        validation_error,
        unlock_error,
        close_error,
    )


def test_open_existing_process_lock_preserves_validation_then_close_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    primary_error = ProcessAuthorityAmbiguousError("identity validation failed")
    close_error = OSError("handle close failed")

    class Handle:
        def close(self) -> None:
            raise close_error

    monkeypatch.setattr(scan_jobs.os, "open", lambda *_args, **_kwargs: 123)
    monkeypatch.setattr(scan_jobs.os, "fdopen", lambda *_args, **_kwargs: Handle())
    monkeypatch.setattr(
        service,
        "_validate_open_process_lock_identity",
        lambda *_args: (_ for _ in ()).throw(primary_error),
    )

    with pytest.raises(BaseExceptionGroup) as captured:
        service._open_existing_process_lock(
            service._process_lock_path("scan-existing-open-errors")
        )

    assert captured.value.exceptions == (primary_error, close_error)


def test_locked_process_lock_preserves_clean_body_exception_identity(
    tmp_path: Path,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    body_error = RuntimeError("body failed cleanly")

    with pytest.raises(RuntimeError) as captured:
        with service._process_lock("scan-clean-body-error"):
            raise body_error

    assert captured.value is body_error


def test_locked_process_lock_uses_post_validation_as_primary_after_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    post_error = ProcessAuthorityAmbiguousError("post validation failed")
    original_validate = service._validate_open_process_lock
    calls = 0

    def validate(path: Path, handle: object) -> None:
        nonlocal calls
        calls += 1
        if calls > 1:
            raise post_error
        original_validate(path, handle)

    monkeypatch.setattr(service, "_validate_open_process_lock", validate)

    with pytest.raises(ProcessAuthorityAmbiguousError) as captured:
        with service._process_lock("scan-post-validation-primary"):
            pass

    assert captured.value is post_error


def test_process_lock_initializer_attempts_all_cleanup_in_error_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, "scan-lock-cleanup-order")
    lock_path = root / f".{job.job_id}.lock"
    primary_error = OSError("initializer failed")
    close_error = OSError("close cleanup failed")
    unlink_error = OSError("unlink cleanup failed")
    directory_error = OSError("directory cleanup failed")
    original_open = scan_jobs.os.open
    original_lstat = scan_jobs.os.lstat
    original_close = scan_jobs.os.close
    original_unlink = Path.unlink
    original_durable_mkdir = scan_jobs.durable_mkdir_parents
    temporary_descriptor: int | None = None
    temporary_path: Path | None = None
    directory_calls = 0

    def observed_open(path, flags, *args, **kwargs):
        nonlocal temporary_descriptor, temporary_path
        descriptor = original_open(path, flags, *args, **kwargs)
        if Path(path).name.startswith(f"{lock_path.name}.tmp."):
            temporary_descriptor = descriptor
            temporary_path = Path(path)
        return descriptor

    def failing_lstat(path):
        if Path(path).name.startswith(f"{lock_path.name}.tmp."):
            raise primary_error
        return original_lstat(path)

    def failing_close(descriptor: int) -> None:
        original_close(descriptor)
        if descriptor == temporary_descriptor:
            raise close_error

    def failing_unlink(path: Path, *args, **kwargs) -> None:
        original_unlink(path, *args, **kwargs)
        if path == temporary_path:
            raise unlink_error

    def failing_directory(path: Path, *, mode: int = 0o777) -> None:
        nonlocal directory_calls
        directory_calls += 1
        if directory_calls > 1:
            raise directory_error
        original_durable_mkdir(path, mode=mode)

    monkeypatch.setattr(scan_jobs.os, "open", observed_open)
    monkeypatch.setattr(scan_jobs.os, "lstat", failing_lstat)
    monkeypatch.setattr(scan_jobs.os, "close", failing_close)
    monkeypatch.setattr(Path, "unlink", failing_unlink)
    monkeypatch.setattr(scan_jobs, "durable_mkdir_parents", failing_directory)

    with pytest.raises(BaseExceptionGroup) as captured:
        service._persist_job(job)

    assert captured.value.exceptions == (
        primary_error,
        close_error,
        unlink_error,
        directory_error,
    )
    assert temporary_descriptor is not None
    assert temporary_path is not None and not temporary_path.exists()
    assert list(root.glob(f"{lock_path.name}.tmp.*")) == []
    assert not lock_path.exists()
    assert not service._state_path(job.job_id).exists()


@pytest.mark.parametrize(
    "failure",
    [
        pytest.param(OSError(errno.ENOTSUP, "not supported"), id="enotsup"),
        pytest.param(OSError(errno.EPERM, "not permitted"), id="eperm"),
        pytest.param(SimpleNamespace(errno=None, winerror=50), id="windows-not-supported"),
    ],
)
def test_process_lock_hardlink_unsupported_fails_closed_without_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure: object,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, "scan-lock-hardlink-required")
    lock_path = root / f".{job.job_id}.lock"
    if not isinstance(failure, BaseException):
        error = OSError("Windows hardlink unsupported")
        error.winerror = failure.winerror  # type: ignore[attr-defined]
        failure = error

    monkeypatch.setattr(
        scan_jobs.os,
        "link",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(failure),
    )

    with pytest.raises(ProcessAuthorityAmbiguousError, match="hardlink"):
        service._persist_job(job)

    assert not lock_path.exists()
    assert not service._state_path(job.job_id).exists()
    assert list(root.glob(f"{lock_path.name}.tmp.*")) == []


def test_process_lock_rejects_windows_reparse_attribute_on_existing_lock(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, "scan-lock-reparse-existing")
    lock_path = root / f".{job.job_id}.lock"
    lock_path.write_bytes(b"0")
    original_stat = scan_jobs.os.stat

    def reparse_stat(path, *args, **kwargs):
        attributes = original_stat(path, *args, **kwargs)
        if Path(path) != lock_path:
            return attributes
        return SimpleNamespace(
            st_mode=attributes.st_mode,
            st_dev=attributes.st_dev,
            st_ino=attributes.st_ino,
            st_file_attributes=0x400,
        )

    monkeypatch.setattr(scan_jobs.os, "stat", reparse_stat)

    with pytest.raises(ProcessAuthorityAmbiguousError, match="reparse"):
        service._persist_job(job)

    assert not service._state_path(job.job_id).exists()


def test_process_lock_rejects_windows_reparse_attribute_on_private_temp(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, "scan-lock-reparse-temp")
    lock_path = root / f".{job.job_id}.lock"
    original_lstat = scan_jobs.os.lstat

    def reparse_lstat(path):
        attributes = original_lstat(path)
        if not Path(path).name.startswith(f"{lock_path.name}.tmp."):
            return attributes
        return SimpleNamespace(
            st_mode=attributes.st_mode,
            st_dev=attributes.st_dev,
            st_ino=attributes.st_ino,
            st_file_attributes=0x400,
        )

    monkeypatch.setattr(scan_jobs.os, "lstat", reparse_lstat)

    with pytest.raises(ProcessAuthorityAmbiguousError, match="reparse"):
        service._persist_job(job)

    assert not lock_path.exists()
    assert not service._state_path(job.job_id).exists()
    assert list(root.glob(f"{lock_path.name}.tmp.*")) == []


def test_scan_service_rejects_reparse_root_after_durable_provisioning(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    root.mkdir()
    original_lstat = scan_jobs.os.lstat

    def reparse_root(path):
        attributes = original_lstat(path)
        if Path(path) != root:
            return attributes
        return SimpleNamespace(
            st_mode=attributes.st_mode,
            st_dev=attributes.st_dev,
            st_ino=attributes.st_ino,
            st_file_attributes=0x400,
        )

    monkeypatch.setattr(scan_jobs, "durable_mkdir_parents", lambda *_a, **_k: None)
    monkeypatch.setattr(scan_jobs.os, "lstat", reparse_root)

    with pytest.raises(ProcessAuthorityAmbiguousError, match="root.*reparse"):
        LocalScanJobService(root, cwd=tmp_path)


def test_scan_service_documents_windows_root_acl_precondition() -> None:
    documentation = LocalScanJobService.__doc__ or ""

    assert "owner-restricted ACL" in documentation
    assert "not treated as Windows DACLs" in documentation


def test_persist_rejects_replacement_of_newly_installed_process_lock(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, "scan-persist-install-replaced")
    lock_path = root / f".{job.job_id}.lock"
    replacement = root / "replacement.lock"
    replacement.write_bytes(b"0")
    original_link = scan_jobs.os.link

    def replacing_link(source, destination, *args, **kwargs) -> None:
        original_link(source, destination, *args, **kwargs)
        lock_path.unlink()
        replacement.replace(lock_path)

    monkeypatch.setattr(scan_jobs.os, "link", replacing_link)

    with pytest.raises(ProcessAuthorityAmbiguousError, match="lock"):
        service._persist_job(job)

    assert lock_path.read_bytes() == b"0"
    assert not service._state_path(job.job_id).exists()


def test_persist_does_not_overwrite_existing_valid_process_lock(tmp_path: Path) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _observation_job(service, root, "scan-persist-existing-lock")
    lock_path = root / f".{job.job_id}.lock"
    lock_path.write_bytes(b"0")
    identity = lock_path.stat()

    service._persist_job(job)

    assert os.path.samestat(identity, lock_path.stat())
    assert lock_path.read_bytes() == b"0"


def test_concurrent_persist_initializers_never_publish_incomplete_lock(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    first = LocalScanJobService(root, cwd=tmp_path)
    second = LocalScanJobService(root, cwd=tmp_path)
    job_id = "scan-concurrent-lock-initializers"
    first_job = _observation_job(first, root, job_id)
    second_job = _observation_job(second, root, job_id)
    lock_path = root / f".{job_id}.lock"
    original_open = scan_jobs.os.open
    original_fdopen = scan_jobs.os.fdopen
    original_write = scan_jobs.durable_write_bytes
    descriptor_paths: dict[int, Path] = {}
    first_write_entered = threading.Event()
    release_first_write = threading.Event()
    blocked_once = False
    errors: list[BaseException] = []

    def observed_open(path, flags, *args, **kwargs):
        descriptor = original_open(path, flags, *args, **kwargs)
        descriptor_paths[descriptor] = Path(path)
        return descriptor

    class BlockingHandle:
        def __init__(self, handle) -> None:
            self._handle = handle

        def __enter__(self):
            self._handle.__enter__()
            return self

        def __exit__(self, *args):
            return self._handle.__exit__(*args)

        def __getattr__(self, name: str):
            return getattr(self._handle, name)

        def write(self, data: bytes) -> int:
            first_write_entered.set()
            assert release_first_write.wait(timeout=5)
            return self._handle.write(data)

    def observed_fdopen(descriptor: int, *args, **kwargs):
        nonlocal blocked_once
        handle = original_fdopen(descriptor, *args, **kwargs)
        path = descriptor_paths.get(descriptor)
        is_initializer = path == lock_path or (
            path is not None and path.name.startswith(f"{lock_path.name}.tmp.")
        )
        if is_initializer and not blocked_once:
            blocked_once = True
            return BlockingHandle(handle)
        return handle

    def observed_write(path: Path, data: bytes) -> None:
        if Path(path) == first._state_path(job_id):
            assert lock_path.stat().st_size == 1
        original_write(path, data)

    def persist_first() -> None:
        try:
            first._persist_job(first_job)
        except BaseException as exc:
            errors.append(exc)

    monkeypatch.setattr(scan_jobs.os, "open", observed_open)
    monkeypatch.setattr(scan_jobs.os, "fdopen", observed_fdopen)
    monkeypatch.setattr(scan_jobs, "durable_write_bytes", observed_write)
    thread = threading.Thread(target=persist_first)
    thread.start()
    assert first_write_entered.wait(timeout=5)

    try:
        second._persist_job(second_job)
    finally:
        release_first_write.set()
        thread.join(timeout=5)

    assert not thread.is_alive()
    assert errors == []
    assert lock_path.read_bytes() == b"0"
    assert list(root.glob(f"{lock_path.name}.tmp.*")) == []


def test_cached_refresh_rejects_persisted_id_before_unc_path_resolution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _job(service, root, "", returncode=1)
    job.job_id = "scan-cached-identity"
    process = StoppableProcess()
    process.returncode = 1
    job.process = process
    job.process_create_time = 1.0
    job.process_group_id = process.pid
    job.process_group_token = "a" * 32
    job.start_released = True
    _register_job(service, job)
    service._persist_job(job)
    state_path = service._state_path(job.job_id)
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    payload["job_id"] = "scan-foreign-identity"
    unc_sentinel = Path(r"\\review-sentinel\share\outside.log")
    payload["stdout_path"] = str(unc_sentinel)
    state_path.write_text(json.dumps(payload), encoding="utf-8")
    original_resolve = Path.resolve
    sentinel_resolves: list[Path] = []

    def guarded_resolve(path: Path, *args, **kwargs):
        if path == unc_sentinel:
            sentinel_resolves.append(path)
            raise AssertionError("foreign persisted identity reached UNC resolution")
        return original_resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", guarded_resolve)

    with pytest.raises(ValueError, match="authority identity changed"):
        service.get(job.job_id)

    assert sentinel_resolves == []
    assert state_path.exists()


@pytest.mark.parametrize("operation", ["get", "replay"])
def test_cached_missing_state_fails_closed_before_snapshot_or_release(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _job(service, root, "", returncode=None)
    job.job_id = f"scan-cached-missing-{operation}"
    process = StoppableProcess()
    job.process = process
    job.process_create_time = 1.0
    job.process_group_id = process.pid
    job.process_group_token = "a" * 32
    job.owner_id = "operator-a"
    job.start_released = operation == "get"
    job.stdout_path = service._stdout_path(job.job_id)
    job.stderr_path = service._stderr_path(job.job_id)
    job.stdout_path.write_text("", encoding="utf-8")
    job.stderr_path.write_text("", encoding="utf-8")
    _register_job(service, job)
    service._persist_job(job)
    state_path = service._state_path(job.job_id)
    state_path.unlink()
    productive_calls: list[str] = []

    monkeypatch.setattr(
        service,
        "_snapshot",
        lambda _job: productive_calls.append("snapshot") or {},
    )
    monkeypatch.setattr(
        service,
        "_release_registered_start",
        lambda _job: productive_calls.append("release") or {},
    )
    monkeypatch.setattr(
        service,
        "_persist_job",
        lambda _job: productive_calls.append("persist"),
    )

    expected_error = (
        ProcessAuthorityAmbiguousError
        if operation == "get"
        else scan_jobs.ScanJobReplayAuthorityError
    )
    with pytest.raises(expected_error):
        if operation == "get":
            service.get(job.job_id)
        else:
            service.get_for_replay(
                job.job_id,
                expected_command=job.command,
                expected_owner_id=job.owner_id,
            )

    assert productive_calls == []
    assert not state_path.exists()


@pytest.mark.parametrize("path_kind", ["unc", "alternate-job", "subdirectory"])
def test_cached_refresh_rejects_untrusted_log_identity_before_resolution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    path_kind: str,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _job(service, root, "", returncode=1)
    job.job_id = "scan-cached-log-identity"
    process = StoppableProcess()
    process.returncode = 1
    job.process = process
    job.process_create_time = 1.0
    job.process_group_id = process.pid
    job.process_group_token = "a" * 32
    job.start_released = True
    job.stdout_path = service._stdout_path(job.job_id)
    job.stderr_path = service._stderr_path(job.job_id)
    job.stdout_path.write_text("", encoding="utf-8")
    job.stderr_path.write_text("", encoding="utf-8")
    _register_job(service, job)
    service._persist_job(job)
    state_path = service._state_path(job.job_id)
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    if path_kind == "unc":
        untrusted = Path(r"\\review-sentinel\share\outside.log")
    elif path_kind == "alternate-job":
        untrusted = service._stdout_path("scan-other-log-identity").resolve()
    else:
        untrusted = (root / "subdir" / f"{job.job_id}.stdout.log").resolve()
    payload["stdout_path"] = str(untrusted)
    state_path.write_text(json.dumps(payload), encoding="utf-8")
    original_resolve = Path.resolve
    untrusted_resolves: list[Path] = []

    def guarded_resolve(path: Path, *args, **kwargs):
        if path == untrusted:
            untrusted_resolves.append(path)
            raise AssertionError("untrusted persisted log path was resolved")
        return original_resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", guarded_resolve)

    with pytest.raises(ValueError, match="authority identity changed"):
        service.get(job.job_id)

    assert untrusted_resolves == []
    assert state_path.exists()


@pytest.mark.parametrize("path_kind", ["unc", "alternate-job", "subdirectory"])
def test_startup_recovery_rejects_untrusted_log_identity_before_resolution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    path_kind: str,
) -> None:
    root = tmp_path / "jobs"
    writer = LocalScanJobService(root, cwd=tmp_path)
    job = _job(writer, root, "", returncode=1)
    job.job_id = "scan-recovery-log-identity"
    process = StoppableProcess()
    process.returncode = 1
    job.process = process
    job.process_create_time = 1.0
    job.process_group_id = process.pid
    job.process_group_token = "a" * 32
    job.start_released = True
    job.stdout_path = writer._stdout_path(job.job_id)
    job.stderr_path = writer._stderr_path(job.job_id)
    job.stdout_path.write_text("", encoding="utf-8")
    job.stderr_path.write_text("", encoding="utf-8")
    writer._persist_job(job)
    state_path = writer._state_path(job.job_id)
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    if path_kind == "unc":
        untrusted = Path(r"\\review-sentinel\share\outside.log")
    elif path_kind == "alternate-job":
        untrusted = writer._stdout_path("scan-other-log-identity").resolve()
    else:
        untrusted = (root / "subdir" / f"{job.job_id}.stdout.log").resolve()
    payload["stdout_path"] = str(untrusted)
    state_path.write_text(json.dumps(payload), encoding="utf-8")
    original_resolve = Path.resolve
    untrusted_resolves: list[Path] = []

    def guarded_resolve(path: Path, *args, **kwargs):
        if path == untrusted:
            untrusted_resolves.append(path)
            raise AssertionError("untrusted recovery log path was resolved")
        return original_resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", guarded_resolve)

    recovered = LocalScanJobService(root, cwd=tmp_path)

    assert untrusted_resolves == []
    assert job.job_id not in recovered._jobs
    assert state_path.exists()


def test_recovery_reloads_state_inside_process_lock_without_stale_overwrite(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    writer = LocalScanJobService(root, cwd=tmp_path)
    observer = LocalScanJobService(root, cwd=tmp_path)
    job = _job(writer, root, "", returncode=1)
    job.job_id = "scan-recovery-lock-order"
    process = StoppableProcess()
    process.returncode = 1
    job.process = process
    job.process_create_time = 1.0
    job.process_group_id = process.pid
    job.process_group_token = "a" * 32
    job.start_released = True
    job.stdout_path = writer._stdout_path(job.job_id)
    job.stderr_path = writer._stderr_path(job.job_id)
    job.stdout_path.write_text("", encoding="utf-8")
    job.stderr_path.write_text("", encoding="utf-8")
    writer._persist_job(job)
    state_path = writer._state_path(job.job_id)
    lock_calls: list[str] = []
    persist_lock_states: list[bool] = []
    inside_lock = False
    original_persist = observer._persist_job

    @contextmanager
    def controlled_lock(job_id: str):
        nonlocal inside_lock
        lock_calls.append(job_id)
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        payload["forced_status"] = "stopped"
        state_path.write_text(json.dumps(payload), encoding="utf-8")
        inside_lock = True
        try:
            yield
        finally:
            inside_lock = False

    def observed_persist(active_job: _LocalScanJob) -> None:
        persist_lock_states.append(inside_lock)
        original_persist(active_job)

    monkeypatch.setattr(observer, "_existing_process_lock", controlled_lock)
    monkeypatch.setattr(observer, "_persist_job", observed_persist)
    monkeypatch.setattr(
        scan_jobs,
        "_job_runtime_active",
        lambda _job: (_ for _ in ()).throw(OSError("stale authority read")),
    )

    observer._recover_jobs()

    assert lock_calls == [job.job_id]
    assert persist_lock_states == []
    assert observer._jobs[job.job_id].forced_status == "stopped"
    assert json.loads(state_path.read_text(encoding="utf-8"))["forced_status"] == "stopped"


@pytest.mark.parametrize(
    "persisted_job_id",
    [*INVALID_AUTHORITY_IDS, "scan-other"],
)
def test_scan_recovery_rejects_invalid_persisted_id_before_outside_path_access(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    persisted_job_id: str,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job = _job(service, root, "", returncode=1)
    job.job_id = "scan-safe"
    process = StoppableProcess()
    process.returncode = 1
    job.process = process
    job.process_create_time = 1.0
    job.process_group_id = process.pid
    job.process_group_token = "a" * 32
    service._persist_job(job)
    state_path = service._state_path(job.job_id)
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    payload["job_id"] = persisted_job_id
    outside = tmp_path / "outside.log"
    payload["stdout_path"] = str(outside)
    state_path.write_text(json.dumps(payload), encoding="utf-8")
    before = {
        path.name: path.read_bytes()
        for path in root.iterdir()
        if path.is_file()
    }
    original_resolve = Path.resolve
    outside_resolves: list[Path] = []

    def guarded_resolve(path: Path, *args, **kwargs):
        if path == outside:
            outside_resolves.append(path)
            raise AssertionError("invalid persisted ID reached an outside path")
        return original_resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", guarded_resolve)

    with pytest.raises(ProcessAuthorityAmbiguousError):
        LocalScanJobService(root, cwd=tmp_path)
    assert outside_resolves == []
    assert not outside.exists()
    assert {
        path.name: path.read_bytes()
        for path in root.iterdir()
        if path.is_file()
    } == before
    assert (root / f".{job.job_id}.lock").read_bytes() == b"0"


def test_scan_recovery_rejects_invalid_state_filename_before_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    root.mkdir()
    invalid_state = root / "n\N{LATIN SMALL LETTER A WITH DIAERESIS}me.state.json"
    invalid_state.write_text("{}", encoding="utf-8")
    reads: list[Path] = []
    original_read_text = Path.read_text

    def guarded_read_text(path: Path, *args, **kwargs):
        if path == invalid_state:
            reads.append(path)
            raise AssertionError("invalid state filename was read")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", guarded_read_text)

    with pytest.raises(ProcessAuthorityAmbiguousError):
        LocalScanJobService(root, cwd=tmp_path)
    assert reads == []


def test_invalid_scan_ids_that_previously_sanitized_to_one_name_do_not_collide(
    tmp_path: Path,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    colliding_ids = ("name/child", "name\\child")

    for invalid_id in colliding_ids:
        with pytest.raises(ValueError):
            service._state_path(invalid_id)
        with pytest.raises(ValueError):
            with service._process_lock(invalid_id):
                pass

    assert list((tmp_path / "jobs").iterdir()) == []


def test_targeted_adoption_releases_the_persisted_unreleased_attempt(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = tmp_path / "jobs"
    observer = LocalScanJobService(root, cwd=tmp_path)
    writer = LocalScanJobService(root, cwd=tmp_path)
    job = _job(writer, root, "", returncode=None)
    job.job_id = "scan-op-adopt-unreleased-1234"
    job.process = StoppableProcess()
    job.process_create_time = 1.0
    job.process_group_id = job.process.pid
    job.process_group_token = "c" * 32
    job.owner_id = "owner-unreleased"
    job.start_released = False
    job.stdout_path = writer._stdout_path(job.job_id)
    job.stderr_path = writer._stderr_path(job.job_id)
    job.stdout_path.write_text("", encoding="utf-8")
    job.stderr_path.write_text("", encoding="utf-8")
    writer._persist_job(job)
    release_path = observer._start_release_path(job.job_id, job.process_group_token)
    started_path = observer._start_started_path(job.job_id, job.process_group_token)
    original_durable_write = scan_jobs.durable_write_bytes
    spawn_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def publish_started(path: Path, data: bytes) -> None:
        original_durable_write(path, data)
        if path == release_path:
            started_path.write_text(str(job.process.pid), encoding="ascii")

    def reject_spawn(*args, **kwargs):
        spawn_calls.append((args, kwargs))
        raise AssertionError("persisted unreleased attempt attempted a second spawn")

    monkeypatch.setattr(scan_jobs, "_job_runtime_active", lambda active_job: True)
    monkeypatch.setattr(scan_jobs, "_windows_job_active", lambda active_job: True)
    monkeypatch.setattr(scan_jobs, "durable_write_bytes", publish_started)
    monkeypatch.setattr(scan_jobs.subprocess, "Popen", reject_spawn)

    adopted = observer.get(job.job_id)
    persisted = json.loads(observer._state_path(job.job_id).read_text(encoding="utf-8"))

    assert spawn_calls == []
    assert adopted["status"] == "running"
    assert release_path.read_bytes() == b"release\n"
    assert started_path.exists()
    assert persisted["start_released"] is True


def test_replay_lookup_validates_identity_before_releasing_unreleased_job(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job = _job(service, tmp_path, "", returncode=None)
    job.job_id = "scan-op-replay-identity-1234"
    job.command = ["python", "-m", "expected.scan"]
    job.owner_id = "owner-a"
    job.start_released = False
    job.process = StoppableProcess()
    job.process_create_time = 1.0
    job.process_group_id = job.process.pid
    job.process_group_token = "a" * 32
    job.stdout_path = service._stdout_path(job.job_id)
    job.stderr_path = service._stderr_path(job.job_id)
    job.stdout_path.write_text("", encoding="utf-8")
    job.stderr_path.write_text("", encoding="utf-8")
    _register_job(service, job)
    service._persist_job(job)
    release_calls: list[_LocalScanJob] = []

    def release(active_job: _LocalScanJob) -> dict[str, object]:
        release_calls.append(active_job)
        return {
            "executes": True,
            "job_id": active_job.job_id,
            "status": "running",
            "command": list(active_job.command),
            "owner_id": active_job.owner_id,
        }

    monkeypatch.setattr(service, "_release_registered_start", release)
    get_for_replay = getattr(service, "get_for_replay", None)
    assert callable(get_for_replay)
    identity_error = getattr(scan_jobs, "ScanJobReplayIdentityError", None)
    ownership_error = getattr(scan_jobs, "ScanJobReplayOwnershipError", None)
    assert isinstance(identity_error, type)
    assert isinstance(ownership_error, type)

    with pytest.raises(ownership_error):
        get_for_replay(
            job.job_id,
            expected_command=job.command,
            expected_owner_id="owner-b",
        )
    assert release_calls == []

    with pytest.raises(identity_error):
        get_for_replay(
            job.job_id,
            expected_command=["python", "-m", "different.scan"],
            expected_owner_id="owner-a",
        )

    assert release_calls == []
    replayed = get_for_replay(
        job.job_id,
        expected_command=job.command,
        expected_owner_id="owner-a",
    )
    assert release_calls == [job]
    assert replayed["job_id"] == job.job_id


def test_scan_replay_authority_error_is_process_authority_error() -> None:
    replay_authority_error = getattr(
        scan_jobs,
        "ScanJobReplayAuthorityError",
        None,
    )

    assert isinstance(replay_authority_error, type)
    assert issubclass(replay_authority_error, ProcessAuthorityAmbiguousError)


def test_replay_lookup_normalizes_targeted_corrupt_state_without_side_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job_id = "scan-op-replay-corrupt-targeted-1234"
    state_path = service._state_path(job_id)
    corrupt_bytes = b"{not-json"
    state_path.write_bytes(corrupt_bytes)
    calls: list[str] = []

    def reject_side_effect(*args, **kwargs):
        calls.append("side-effect")
        raise AssertionError("corrupt replay attempted a side effect")

    monkeypatch.setattr(service, "_release_registered_start", reject_side_effect)
    monkeypatch.setattr(service, "_snapshot", reject_side_effect)
    monkeypatch.setattr(service, "_persist_job", reject_side_effect)

    with pytest.raises(scan_jobs.ScanJobReplayAuthorityError) as captured:
        service.get_for_replay(
            job_id,
            expected_command=[sys.executable, "-c", "pass"],
            expected_owner_id="owner-a",
        )

    assert isinstance(captured.value.__cause__, ProcessAuthorityAmbiguousError)
    assert state_path.read_bytes() == corrupt_bytes
    assert job_id not in service._jobs
    assert calls == []


@pytest.mark.parametrize("refresh_failure", ["invalid-json", "eio"])
def test_replay_lookup_normalizes_cached_refresh_failure_without_side_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    refresh_failure: str,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job = _job(service, tmp_path, "", returncode=None)
    job.job_id = f"scan-op-replay-refresh-{refresh_failure}-1234"
    job.command = [sys.executable, "-m", "expected.scan"]
    job.owner_id = "owner-a"
    job.process_create_time = 123.0
    job.process_group_id = 456
    job.process_group_token = "a" * 32
    job.start_released = False
    _register_job(service, job)
    state_path = service._state_path(job.job_id)
    state_bytes = b"{not-json" if refresh_failure == "invalid-json" else b"{}"
    state_path.write_bytes(state_bytes)
    identity_before = (
        job.job_id,
        tuple(job.command),
        job.owner_id,
        id(job.process),
        job.process_create_time,
        job.process_group_id,
        job.process_group_token,
        job.start_released,
        job.authority_namespace,
    )
    calls: list[str] = []

    def reject_side_effect(*args, **kwargs):
        calls.append("side-effect")
        raise AssertionError("failed refresh attempted a side effect")

    if refresh_failure == "eio":
        original_read_text = Path.read_text

        def fail_state_read(path: Path, *args, **kwargs) -> str:
            if path == state_path:
                raise OSError(errno.EIO, "injected state read failure")
            return original_read_text(path, *args, **kwargs)

        monkeypatch.setattr(Path, "read_text", fail_state_read)
    monkeypatch.setattr(service, "_release_registered_start", reject_side_effect)
    monkeypatch.setattr(service, "_snapshot", reject_side_effect)
    monkeypatch.setattr(service, "_persist_job", reject_side_effect)

    with pytest.raises(scan_jobs.ScanJobReplayAuthorityError) as captured:
        service.get_for_replay(
            job.job_id,
            expected_command=job.command,
            expected_owner_id=job.owner_id,
        )

    if refresh_failure == "invalid-json":
        assert isinstance(captured.value.__cause__, json.JSONDecodeError)
    else:
        assert isinstance(captured.value.__cause__, OSError)
        assert captured.value.__cause__.errno == errno.EIO
    assert state_path.read_bytes() == state_bytes
    assert (
        job.job_id,
        tuple(job.command),
        job.owner_id,
        id(job.process),
        job.process_create_time,
        job.process_group_id,
        job.process_group_token,
        job.start_released,
        job.authority_namespace,
    ) == identity_before
    assert service._jobs[job.job_id] is job
    assert calls == []


def _persist_replay_validation_job(
    service: LocalScanJobService,
    job_id: str,
) -> _LocalScanJob:
    stdout_path = service.root / f"{job_id}.stdout.log"
    stderr_path = service.root / f"{job_id}.stderr.log"
    stdout_path.write_text("", encoding="utf-8")
    stderr_path.write_text("", encoding="utf-8")
    job = _LocalScanJob(
        job_id=job_id,
        command=[sys.executable, "-c", "pass"],
        process=StoppableProcess(),
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        created_at="2026-07-22T12:00:00+00:00",
        updated_at="2026-07-22T12:00:00+00:00",
        owner_id="owner-a",
        process_create_time=123.0,
        process_group_id=43210,
        process_group_token="a" * 32,
        start_released=True,
    )
    service._jobs[job_id] = job
    service._persist_job(job)
    return job


def test_schema_v1_job_without_report_session_fields_recovers_with_defaults(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    writer = LocalScanJobService(root, cwd=tmp_path)
    job_id = "scan-op-legacy-report-session-1234"
    job = _persist_replay_validation_job(writer, job_id)
    state_path = writer._state_path(job_id)
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    payload.pop("report_session_ids")
    payload.pop("report_session_invalid")
    state_path.write_text(json.dumps(payload), encoding="utf-8")
    writer._jobs.clear()
    monkeypatch.setattr(scan_jobs, "_job_runtime_active", lambda _job: True)

    recovered = LocalScanJobService(root, cwd=tmp_path)

    assert recovered._jobs[job_id].report_session_ids == set()
    assert recovered._jobs[job_id].report_session_invalid is False


@pytest.mark.parametrize(
    ("field", "invalid_value", "message"),
    [
        pytest.param(
            "report_session_ids",
            "session-a",
            "persisted scan job report session ids are invalid",
            id="ids-not-list",
        ),
        pytest.param(
            "report_session_ids",
            [""],
            "persisted scan job report session ids are invalid",
            id="ids-empty-item",
        ),
        pytest.param(
            "report_session_ids",
            [1],
            "persisted scan job report session ids are invalid",
            id="ids-non-string-item",
        ),
        pytest.param(
            "report_session_ids",
            ["\ud800"],
            "persisted scan job report session ids are invalid",
            id="ids-non-utf8-item",
        ),
        pytest.param(
            "report_session_ids",
            ["session-a", "session-b", "session-c"],
            "persisted scan job report session ids are invalid",
            id="ids-over-authority-limit",
        ),
        pytest.param(
            "report_session_invalid",
            0,
            "persisted scan job report session state is invalid",
            id="invalid-state-not-bool",
        ),
    ],
)
def test_report_session_state_corruption_fails_closed_during_targeted_recovery(
    tmp_path: Path,
    field: str,
    invalid_value: object,
    message: str,
) -> None:
    root = tmp_path / "jobs"
    writer = LocalScanJobService(root, cwd=tmp_path)
    job_id = f"scan-op-invalid-{field}-1234"
    _persist_replay_validation_job(writer, job_id)
    state_path = writer._state_path(job_id)
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    payload[field] = invalid_value
    state_path.write_text(json.dumps(payload), encoding="utf-8")
    writer._jobs.clear()
    recovered = LocalScanJobService(root, cwd=tmp_path)

    with pytest.raises(TypeError, match=message):
        recovered.get(job_id)

    assert job_id not in recovered._jobs


def test_report_session_ids_parser_rejects_list_subclasses(tmp_path: Path) -> None:
    class ReportSessionIdList(list[str]):
        pass

    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job = _persist_replay_validation_job(
        service,
        "scan-op-report-session-list-subclass-1234",
    )
    payload = json.loads(service._state_path(job.job_id).read_text(encoding="utf-8"))
    payload["report_session_ids"] = ReportSessionIdList(["session-a"])

    with pytest.raises(
        TypeError,
        match="persisted scan job report session ids are invalid",
    ):
        scan_jobs._parse_persisted_job_payload(
            payload,
            expected_authority_namespace=service.authority_namespace,
        )


def test_report_session_recovery_allows_duplicate_entries_with_two_unique_ids(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    writer = LocalScanJobService(root, cwd=tmp_path)
    job_id = "scan-op-duplicate-report-sessions-1234"
    job = _persist_replay_validation_job(writer, job_id)
    state_path = writer._state_path(job_id)
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    payload["report_session_ids"] = ["session-b", "s€x", "s€x"]
    state_path.write_text(json.dumps(payload), encoding="utf-8")
    writer._jobs.clear()
    monkeypatch.setattr(scan_jobs, "_job_runtime_active", lambda _job: True)

    recovered = LocalScanJobService(root, cwd=tmp_path)

    assert recovered._jobs[job_id].report_session_ids == {"s€x", "session-b"}


def test_report_session_ids_are_persisted_in_sorted_order(tmp_path: Path) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job = _persist_replay_validation_job(
        service,
        "scan-op-sorted-report-sessions-1234",
    )
    job.report_session_ids = {"session-b", "session-a"}

    service._persist_job(job)

    payload = json.loads(service._state_path(job.job_id).read_text(encoding="utf-8"))
    assert payload["report_session_ids"] == ["session-a", "session-b"]


def test_report_session_authority_persists_only_first_two_distinct_ids(
    tmp_path: Path,
) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job = _persist_replay_validation_job(
        service,
        "scan-op-bounded-report-sessions-1234",
    )
    job.report_session_ids, job.report_session_invalid = (
        scan_jobs._update_report_session_authority(
            [
                _report_session_record("session-a", profile="P1"),
                _report_session_record("session-b", profile="P2"),
                _report_session_record("session-c", profile="P3"),
            ],
            session_ids=set(),
            invalid=False,
        )
    )

    service._persist_job(job)

    payload = json.loads(service._state_path(job.job_id).read_text(encoding="utf-8"))
    assert job.report_session_ids == {"session-a", "session-b"}
    assert payload["report_session_ids"] == ["session-a", "session-b"]


def _replay_validation_state(job: _LocalScanJob) -> tuple[object, ...]:
    return (
        tuple(job.command),
        job.stdout_pos,
        job.stderr_pos,
        job.progress_percent,
        job.current_phase,
        job.current_substep,
        tuple(job.completed_labels),
        tuple(job.completed_stage_ids),
        job.current_stage_id,
        job.stdout_buffer,
        job.stderr_buffer,
        job.owner_id,
        tuple(job.artifact_paths),
        job.forced_status,
        job.phase2_profiles_started,
        job.phase2_profiles_complete,
        job.start_released,
    )


@pytest.mark.parametrize("lookup_kind", ["cached", "targeted"])
@pytest.mark.parametrize(
    ("field", "corrupt_value"),
    [
        pytest.param("schema_version", True, id="bool-schema-version"),
        pytest.param("pid", True, id="bool-pid"),
        pytest.param("pid", 2**31, id="oversized-pid"),
        pytest.param("process_group_id", 2**31, id="oversized-process-group-id"),
        pytest.param("process_create_time", True, id="bool-process-create-time"),
        pytest.param("process_create_time", -1.0, id="negative-process-create-time"),
        pytest.param(
            "process_create_time",
            float("inf"),
            id="non-finite-process-create-time",
        ),
        pytest.param(
            "process_create_time",
            10**1000,
            id="overflowing-process-create-time",
        ),
        pytest.param(
            "process_create_time",
            10**20,
            id="oversized-process-create-time",
        ),
        pytest.param("stdout_pos", True, id="bool-cursor"),
        pytest.param("stderr_pos", -1, id="negative-cursor"),
        pytest.param("stdout_pos", 2**63, id="oversized-stdout-cursor"),
        pytest.param("stderr_pos", 2**63, id="oversized-stderr-cursor"),
        pytest.param("progress_percent", float("nan"), id="non-finite-progress"),
        pytest.param("command", [sys.executable, 7], id="command-element"),
        pytest.param("completed_labels", ["valid", 7], id="list-element"),
        pytest.param("phase2_profiles_started", 1, id="malformed-boolean"),
        pytest.param("forced_status", "unknown", id="malformed-status"),
        pytest.param("current_phase", [], id="malformed-optional-string"),
    ],
)
def test_replay_lookup_rejects_typed_state_corruption_atomically(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    lookup_kind: str,
    field: str,
    corrupt_value: object,
) -> None:
    root = tmp_path / "jobs"
    writer = LocalScanJobService(root, cwd=tmp_path)
    job_id = f"scan-op-typed-{lookup_kind}-{field.replace('_', '-')}-1234"
    job = _persist_replay_validation_job(writer, job_id)
    state_path = writer._state_path(job_id)
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    payload["stdout_pos"] = 9
    payload[field] = corrupt_value
    corrupt_bytes = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode(
        "utf-8"
    )
    state_path.write_bytes(corrupt_bytes)
    before = _replay_validation_state(job)
    if lookup_kind == "targeted":
        writer._jobs.clear()
        service = LocalScanJobService(root, cwd=tmp_path)
    else:
        service = writer
    calls: list[str] = []

    def reject_side_effect(*args, **kwargs):
        calls.append("side-effect")
        raise AssertionError("typed corruption attempted a side effect")

    monkeypatch.setattr(service, "_release_registered_start", reject_side_effect)
    monkeypatch.setattr(service, "_snapshot", reject_side_effect)
    monkeypatch.setattr(service, "_persist_job", reject_side_effect)
    monkeypatch.setattr(scan_jobs.subprocess, "Popen", reject_side_effect)

    with pytest.raises(scan_jobs.ScanJobReplayAuthorityError) as captured:
        service.get_for_replay(
            job_id,
            expected_command=job.command,
            expected_owner_id=job.owner_id,
        )

    assert isinstance(captured.value.__cause__, (TypeError, ValueError))
    assert state_path.read_bytes() == corrupt_bytes
    if lookup_kind == "cached":
        assert service._jobs[job_id] is job
        assert _replay_validation_state(job) == before
    else:
        assert job_id not in service._jobs
    assert calls == []


@pytest.mark.skipif(os.name != "nt", reason="Windows start-lock contract")
def test_windows_start_lock_retries_contention_without_busy_spin(
    tmp_path: Path,
    monkeypatch,
) -> None:
    import msvcrt

    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    attempts = 0
    unlocks = 0
    sleeps: list[float] = []

    def contended_locking(descriptor: int, mode: int, size: int) -> None:
        nonlocal attempts, unlocks
        if mode == msvcrt.LK_NBLCK:
            attempts += 1
            if attempts <= 12:
                raise OSError(errno.EACCES, "lock is held")
            return
        if mode == msvcrt.LK_UNLCK:
            unlocks += 1
            return
        raise AssertionError("start lock used bounded LK_LOCK")

    monkeypatch.setattr(msvcrt, "locking", contended_locking)
    monkeypatch.setattr(scan_jobs.time, "sleep", lambda delay: sleeps.append(delay))

    with service._start_process_lock("scan-op-contended-start-1234"):
        pass

    assert attempts == 13
    assert unlocks == 1
    assert len(sleeps) == 12
    assert all(delay > 0 for delay in sleeps)

    def invalid_locking(descriptor: int, mode: int, size: int) -> None:
        raise OSError(errno.EIO, "lock device failed")

    monkeypatch.setattr(msvcrt, "locking", invalid_locking)
    sleep_count = len(sleeps)
    with pytest.raises(OSError, match="lock device failed"):
        with service._start_process_lock("scan-op-invalid-start-lock-1234"):
            pass
    assert len(sleeps) == sleep_count


def test_scan_gate_token_uses_environment_and_never_argv(tmp_path: Path) -> None:
    token = "private-token"
    result_path = tmp_path / "result"

    command, environment = scan_jobs._build_gate_launch(
        gate_script=tmp_path / "gate.py",
        release_path=tmp_path / "release",
        started_path=tmp_path / "started",
        result_path=result_path,
        exec_command=[sys.executable, "-c", "pass"],
        process_environment={"PATH": "test"},
        process_group_token=token,
    )

    assert token not in command
    assert "--token" not in command
    assert command[command.index("--result") + 1] == str(result_path)
    assert environment["MORPHIC_SCAN_GATE_TOKEN"] == token


@pytest.mark.parametrize("returncode", [0, 7])
def test_scan_gate_main_publishes_exact_result_before_return(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    returncode: int,
) -> None:
    release_path = tmp_path / "release"
    started_path = tmp_path / "started"
    result_path = tmp_path / "result"
    events: list[str] = []
    original_publish = scan_process_gate._publish_result

    def supervise(*args, **kwargs) -> int:
        events.append("supervise")
        return returncode

    def publish(path: Path, exact_returncode: int) -> None:
        events.append("publish")
        original_publish(path, exact_returncode)

    monkeypatch.setattr(scan_process_gate, "supervise", supervise)
    monkeypatch.setattr(scan_process_gate, "_publish_result", publish)
    monkeypatch.setenv("MORPHIC_SCAN_GATE_TOKEN", "a" * 32)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scan_process_gate.py",
            "--release",
            str(release_path),
            "--started",
            str(started_path),
            "--result",
            str(result_path),
            "--",
            sys.executable,
            "-c",
            "pass",
        ],
    )

    observed_returncode = scan_process_gate.main()

    assert events == ["supervise", "publish"]
    assert result_path.read_bytes() == f"{returncode}\n".encode("ascii")
    assert observed_returncode == returncode


def test_scan_result_path_is_opaque_and_attempt_specific(tmp_path: Path) -> None:
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    job_id = "scan-op-result-sidecar-1234"
    first_token = "a" * 32
    second_token = "b" * 32

    first = service._start_result_path(job_id, first_token)
    repeated = service._start_result_path(job_id, first_token)
    second = service._start_result_path(job_id, second_token)
    other_job = service._start_result_path("scan-op-result-sidecar-5678", first_token)

    assert first == repeated
    assert len(first.stem.removeprefix(".")) == 64
    assert first.suffix == ".result"
    assert job_id not in first.name
    assert first_token not in first.name
    assert len({first, second, other_job}) == 3


@pytest.mark.parametrize(
    ("exit_code", "expected_status"),
    [(0, "completed"), (7, "failed")],
)
def test_fresh_service_recovers_exact_gate_exit_code(
    tmp_path: Path,
    exit_code: int,
    expected_status: str,
) -> None:
    root = tmp_path / "jobs"
    job_id = f"scan-op-exact-exit-{exit_code}-1234"
    command = [sys.executable, "-c", f"raise SystemExit({exit_code})"]
    writer = LocalScanJobService(root, cwd=tmp_path)
    writer_reference = weakref.ref(writer)

    writer.start(command, owner_id="owner-a", job_id=job_id)
    process = writer._jobs[job_id].process
    process_reference = weakref.ref(process)
    try:
        assert process.wait(timeout=10) == exit_code
        process_group_token = writer._jobs[job_id].process_group_token
        result_path = writer._start_result_path(job_id, process_group_token)
        assert result_path.read_bytes() == f"{exit_code}\n".encode("ascii")

        writer.close()
        writer._jobs.clear()
        del process
        del writer
        gc.collect()
        assert writer_reference() is None
        assert process_reference() is None
        observer = LocalScanJobService(root, cwd=tmp_path)
        replayed = observer.get_for_replay(
            job_id,
            expected_command=command,
            expected_owner_id="owner-a",
        )

        assert replayed["status"] == expected_status
        assert replayed["returncode"] == exit_code
    finally:
        remaining_process = process_reference()
        if remaining_process is not None and remaining_process.poll() is None:
            remaining_process.kill()
            remaining_process.wait(timeout=5)


def test_recovered_process_rejects_malformed_result_before_pid_liveness(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result_path = tmp_path / "attempt.result"
    result_path.write_bytes(b"not-an-integer\n")
    identity_checks: list[int] = []

    def reject_identity_check(pid: int, expected_create_time: float | None) -> bool:
        identity_checks.append(pid)
        raise AssertionError("malformed result reached PID liveness")

    monkeypatch.setattr(scan_jobs, "_process_identity_matches", reject_identity_check)
    process = scan_jobs._RecoveredProcess(43210, 123.0, result_path)

    with pytest.raises(ProcessAuthorityAmbiguousError, match="result"):
        process.poll()

    assert identity_checks == []


def test_recovered_process_without_result_never_reports_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        scan_jobs,
        "_process_identity_matches",
        lambda pid, expected_create_time: False,
    )
    process = scan_jobs._RecoveredProcess(
        43210,
        123.0,
        tmp_path / "missing.result",
    )

    assert process.poll() == 1
    assert process.wait(timeout=0) == 1


def test_parallel_scan_polls_share_one_atomic_snapshot_boundary(
    tmp_path: Path,
    monkeypatch,
) -> None:
    service = LocalScanJobService(tmp_path)
    job = _job(
        service,
        tmp_path,
        "[1/2] PHASE 1: Screening aller Haupt-Profile\n",
    )
    job.process.pid = 424242
    job.process_create_time = 1.0
    job.process_group_id = job.process.pid
    job.process_group_token = "a" * 32
    job.stdout_path = service._stdout_path(job.job_id)
    job.stderr_path = service._stderr_path(job.job_id)
    job.stdout_path.write_text(
        "[1/2] PHASE 1: Screening aller Haupt-Profile\n",
        encoding="utf-8",
    )
    job.stderr_path.write_text("", encoding="utf-8")
    _register_job(service, job)
    service._persist_job(job)
    original_read = scan_jobs._read_incremental
    counter_lock = threading.Lock()
    active = 0
    maximum_active = 0

    def observed_read(path: Path, start: int) -> tuple[str, int]:
        nonlocal active, maximum_active
        with counter_lock:
            active += 1
            maximum_active = max(maximum_active, active)
        try:
            time.sleep(0.03)
            return original_read(path, start)
        finally:
            with counter_lock:
                active -= 1

    monkeypatch.setattr(scan_jobs, "_read_incremental", observed_read)
    monkeypatch.setattr(sys, "platform", "linux")
    with ThreadPoolExecutor(max_workers=2) as pool:
        snapshots = list(pool.map(lambda _: service.get(job.job_id), range(2)))

    assert maximum_active == 1
    assert {snapshot["job_id"] for snapshot in snapshots} == {job.job_id}
    assert snapshots[-1]["completed_substeps"] == snapshots[0]["completed_substeps"]


def test_parallel_recovered_services_never_regress_persisted_scan_cursor(tmp_path: Path) -> None:
    root = tmp_path / "jobs"
    first = LocalScanJobService(root, cwd=tmp_path)
    started = first.start(["python", "-c", "import time; time.sleep(60)"])
    job_id = str(started["job_id"])
    second = LocalScanJobService(root, cwd=tmp_path)
    stdout_path = root / f"{job_id}.stdout.log"
    marker = "[1/2] PHASE 1: Screening aller Haupt-Profile\n"
    stdout_path.write_text(marker, encoding="utf-8")

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            snapshots = list(pool.map(lambda service: service.get(job_id), [first, second]))

        persisted = json.loads(
            (root / f"{job_id}.state.json").read_text(encoding="utf-8")
        )
        assert persisted["stdout_pos"] == stdout_path.stat().st_size
        assert persisted["completed_labels"]
        assert {snapshot["job_id"] for snapshot in snapshots} == {job_id}
        final = LocalScanJobService(root, cwd=tmp_path).get(job_id)
        assert final["completed_substeps"] == snapshots[-1]["completed_substeps"]
    finally:
        LocalScanJobService(root, cwd=tmp_path).stop(job_id)


def test_independent_processes_poll_one_recovered_scan_without_state_drift(
    tmp_path: Path,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    started = service.start([sys.executable, "-c", "import time; time.sleep(30)"])
    job_id = str(started["job_id"])
    context = multiprocessing.get_context("spawn")
    output = context.Queue()
    processes = [
        context.Process(
            target=_poll_recovered_scan_process,
            args=(str(root), str(tmp_path), job_id, output),
        )
        for _ in range(2)
    ]

    try:
        for process in processes:
            process.start()
        for process in processes:
            process.join(timeout=10)
        messages = [output.get(timeout=2) for _ in processes]

        assert all(process.exitcode == 0 for process in processes)
        assert {message[0] for message in messages} == {"ok"}
        assert {message[1]["job_id"] for message in messages} == {job_id}
        persisted = json.loads((root / f"{job_id}.state.json").read_text(encoding="utf-8"))
        assert persisted["job_id"] == job_id
        assert persisted["forced_status"] is None
    finally:
        LocalScanJobService(root, cwd=tmp_path).stop(job_id)


def test_productive_scan_command_waits_for_durable_registration(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "jobs"
    marker = tmp_path / "productive-started.txt"
    service = LocalScanJobService(root, cwd=tmp_path)
    entered_persist = threading.Event()
    release_persist = threading.Event()
    original_persist = service._persist_job
    result: list[dict[str, object]] = []
    errors: list[BaseException] = []

    def blocked_persist(job) -> None:
        entered_persist.set()
        assert release_persist.wait(timeout=5)
        original_persist(job)

    monkeypatch.setattr(service, "_persist_job", blocked_persist)
    command = [
        sys.executable,
        "-c",
        (
            "from pathlib import Path; import time; "
            f"Path({str(marker)!r}).write_text('started', encoding='utf-8'); "
            "time.sleep(30)"
        ),
    ]

    def start() -> None:
        try:
            result.append(service.start(command))
        except BaseException as exc:  # pragma: no cover - surfaced below
            errors.append(exc)

    thread = threading.Thread(target=start)
    thread.start()
    assert entered_persist.wait(timeout=5)
    time.sleep(0.2)
    try:
        assert not marker.exists()
    finally:
        release_persist.set()
        thread.join(timeout=10)
        monkeypatch.setattr(service, "_persist_job", original_persist)
        if result:
            service.stop(str(result[0]["job_id"]))
    assert not thread.is_alive()
    assert errors == []


def test_recovered_scan_supervisor_controls_child_after_requested_leader_exits(
    tmp_path: Path,
) -> None:
    root = tmp_path / "jobs"
    child_pid_path = tmp_path / "child.pid"
    service = LocalScanJobService(root, cwd=tmp_path)
    child_code = "import time; time.sleep(60)"
    leader_code = (
        "import subprocess,sys; from pathlib import Path; "
        f"p=subprocess.Popen([sys.executable,'-c',{child_code!r}],start_new_session=sys.platform!='win32'); "
        f"Path({str(child_pid_path)!r}).write_text(str(p.pid), encoding='utf-8')"
    )
    started = service.start([sys.executable, "-c", leader_code])
    job_id = str(started["job_id"])
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and not child_pid_path.exists():
        time.sleep(0.05)
    assert child_pid_path.exists()
    child_pid = int(child_pid_path.read_text(encoding="utf-8"))

    try:
        time.sleep(0.3)
        recovered = LocalScanJobService(root, cwd=tmp_path)
        assert recovered.get(job_id)["status"] == "running"
        assert recovered.stop(job_id)["status"] == "stopped"
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and scan_jobs.psutil.pid_exists(child_pid):
            time.sleep(0.05)
        assert not scan_jobs.psutil.pid_exists(child_pid)
    finally:
        if scan_jobs.psutil.pid_exists(child_pid):
            service.stop(job_id)


def test_failed_initial_registration_never_releases_productive_scan(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = tmp_path / "jobs"
    marker = tmp_path / "must-not-run.txt"
    service = LocalScanJobService(root, cwd=tmp_path)
    command = [
        sys.executable,
        "-c",
        f"from pathlib import Path; Path({str(marker)!r}).write_text('ran', encoding='utf-8')",
    ]

    def fail_registration(job) -> None:
        raise OSError("simulated durable registration failure")

    monkeypatch.setattr(service, "_persist_job", fail_registration)

    with pytest.raises(BaseExceptionGroup) as raised:
        service.start(command)
    assert isinstance(raised.value.exceptions[0], OSError)
    assert "registration failure" in str(raised.value.exceptions[0])
    assert isinstance(raised.value.exceptions[1], OSError)
    time.sleep(0.3)

    assert not marker.exists()


def test_post_release_snapshot_failure_rolls_back_productive_descendant(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = tmp_path / "jobs"
    child_pid_path = tmp_path / "rollback-child.pid"
    service = LocalScanJobService(root, cwd=tmp_path)
    leader_code = (
        "import subprocess,sys,time; from pathlib import Path; "
        "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']); "
        f"Path({str(child_pid_path)!r}).write_text(str(p.pid),encoding='utf-8'); "
        "time.sleep(60)"
    )
    original_snapshot = service._snapshot
    snapshot_calls = 0

    def fail_second_snapshot(job):
        nonlocal snapshot_calls
        snapshot_calls += 1
        if snapshot_calls == 2:
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline and not child_pid_path.exists():
                time.sleep(0.02)
            raise OSError("post-release snapshot failure")
        return original_snapshot(job)

    monkeypatch.setattr(service, "_snapshot", fail_second_snapshot)

    with pytest.raises(OSError, match="post-release snapshot failure"):
        service.start([sys.executable, "-c", leader_code])

    assert child_pid_path.exists()
    child_pid = int(child_pid_path.read_text(encoding="utf-8"))
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and scan_jobs.psutil.pid_exists(child_pid):
        time.sleep(0.02)
    assert not scan_jobs.psutil.pid_exists(child_pid)
    assert all(job.process.poll() is not None for job in service._jobs.values())


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX process-group contract")
def test_posix_recovery_controls_group_after_leader_and_supervisor_exit(tmp_path: Path) -> None:
    root = tmp_path / "jobs"
    child_pid_path = tmp_path / "child.pid"
    leader_script = (
        "import pathlib,subprocess,sys;"
        "child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']);"
        f"pathlib.Path({str(child_pid_path)!r}).write_text(str(child.pid),encoding='utf-8')"
    )
    service = LocalScanJobService(root, cwd=tmp_path)
    snapshot = service.start(["python", "-c", leader_script])
    job_id = str(snapshot["job_id"])
    supervisor_pid = int(service._jobs[job_id].process.pid)
    child_pid = 0
    try:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and not child_pid_path.exists():
            time.sleep(0.02)
        assert child_pid_path.exists()
        child_pid = int(child_pid_path.read_text(encoding="utf-8"))
        assert scan_jobs.psutil.pid_exists(child_pid)

        supervisor_descriptor = scan_jobs._open_pidfd(supervisor_pid)
        try:
            scan_jobs.signal.pidfd_send_signal(
                supervisor_descriptor, signal.SIGKILL, None, 0
            )
        finally:
            scan_jobs.os.close(supervisor_descriptor)
        service._jobs[job_id].process.wait(timeout=5)
        assert not scan_jobs.psutil.pid_exists(supervisor_pid)

        recovered = LocalScanJobService(root, cwd=tmp_path)
        assert recovered.get(job_id)["status"] == "running"
        assert recovered.stop(job_id)["status"] == "stopped"

        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and scan_jobs.psutil.pid_exists(child_pid):
            time.sleep(0.02)
        assert not scan_jobs.psutil.pid_exists(child_pid)
    finally:
        if child_pid and scan_jobs.psutil.pid_exists(child_pid):
            service.stop(job_id)
