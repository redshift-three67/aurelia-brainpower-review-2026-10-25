from __future__ import annotations

import argparse
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

import psutil

if __package__ in {None, ""}:
    repository_root = str(Path(__file__).resolve().parents[1])
    sys.path[:] = [entry for entry in sys.path if entry != repository_root]
    sys.path.insert(0, repository_root)

from apps.web.durable_io import durable_mkdir_parents
from core.profile_sync import (
    SCAN_PROCESS_GATE_NONCE_ENV,
    SCAN_PROCESS_GATE_PROOF_ENV,
    SCAN_PROFILE_POOL_FINGERPRINT_ENV,
    build_scan_process_gate_proof,
)


_SPAWNED_TREE_CLEANUP_TIMEOUT = 5.0
_SPAWNED_TREE_TERM_GRACE = 1.0
_SPAWNED_TREE_POLL_INTERVAL = 0.02


def _publish_windows(source: Path, destination: Path) -> None:
    import ctypes
    from ctypes import wintypes

    move_file = ctypes.WinDLL("kernel32", use_last_error=True).MoveFileExW
    move_file.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD]
    move_file.restype = wintypes.BOOL
    deadline = time.monotonic() + 1.0
    while True:
        if move_file(
            str(source.resolve()),
            str(destination.resolve()),
            0x1 | 0x8,  # MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH
        ):
            return
        error = ctypes.get_last_error()
        if error not in {5, 32, 33} or time.monotonic() >= deadline:
            raise ctypes.WinError(error)
        time.sleep(0.01)


def _publish_result(path: Path, returncode: int) -> None:
    durable_mkdir_parents(path.parent, mode=0o700)
    os.chmod(path.parent, 0o700)
    temporary = path.with_suffix(path.suffix + f".tmp.{uuid4().hex[:8]}")
    try:
        descriptor = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.chmod(temporary, 0o600)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(f"{returncode}\n".encode("ascii"))
            handle.flush()
            os.fsync(handle.fileno())
        if os.name == "nt":
            _publish_windows(temporary, path)
        else:
            os.replace(temporary, path)
            parent = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                os.fsync(parent)
            finally:
                os.close(parent)
        os.chmod(path, 0o600)
    finally:
        temporary.unlink(missing_ok=True)


def _create_windows_job():
    if sys.platform != "win32":
        return None
    import ctypes
    from ctypes import wintypes

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_ulonglong),
            ("WriteOperationCount", ctypes.c_ulonglong),
            ("OtherOperationCount", ctypes.c_ulonglong),
            ("ReadTransferCount", ctypes.c_ulonglong),
            ("WriteTransferCount", ctypes.c_ulonglong),
            ("OtherTransferCount", ctypes.c_ulonglong),
        ]

    class BASIC_LIMITS(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_longlong),
            ("PerJobUserTimeLimit", ctypes.c_longlong),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class EXTENDED_LIMITS(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", BASIC_LIMITS),
            ("IoInfo", IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create_job = kernel32.CreateJobObjectW
    create_job.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    create_job.restype = wintypes.HANDLE
    set_information = kernel32.SetInformationJobObject
    set_information.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    set_information.restype = wintypes.BOOL
    assign_process = kernel32.AssignProcessToJobObject
    assign_process.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    assign_process.restype = wintypes.BOOL
    get_current_process = kernel32.GetCurrentProcess
    get_current_process.restype = wintypes.HANDLE
    handle = create_job(None, None)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    limits = EXTENDED_LIMITS()
    limits.BasicLimitInformation.LimitFlags = 0x00002000
    if not set_information(
        handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    if not assign_process(handle, get_current_process()):
        raise ctypes.WinError(ctypes.get_last_error())
    return handle


def _windows_job_active_processes(handle) -> int | None:
    if handle is None:
        return None
    import ctypes
    from ctypes import wintypes

    class BASIC_ACCOUNTING(ctypes.Structure):
        _fields_ = [
            ("TotalUserTime", ctypes.c_longlong),
            ("TotalKernelTime", ctypes.c_longlong),
            ("ThisPeriodTotalUserTime", ctypes.c_longlong),
            ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
            ("TotalPageFaultCount", wintypes.DWORD),
            ("TotalProcesses", wintypes.DWORD),
            ("ActiveProcesses", wintypes.DWORD),
            ("TotalTerminatedProcesses", wintypes.DWORD),
        ]

    info = BASIC_ACCOUNTING()
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    query_information = kernel32.QueryInformationJobObject
    query_information.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
    ]
    query_information.restype = wintypes.BOOL
    if not query_information(
        handle, 1, ctypes.byref(info), ctypes.sizeof(info), None
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    return int(info.ActiveProcesses)


def _live_descendants(process: psutil.Process) -> list[psutil.Process]:
    try:
        return [child for child in process.children(recursive=True) if child.is_running()]
    except psutil.Error:
        return []


def _posix_group_has_productive_members(process_group_id: int) -> bool:
    if sys.platform == "win32":
        return False
    supervisor_pid = os.getpid()
    for process in psutil.process_iter(["pid", "status"]):
        try:
            pid = int(process.info["pid"])
            if (
                pid != supervisor_pid
                and process.info["status"] != psutil.STATUS_ZOMBIE
                and os.getpgid(pid) == process_group_id
            ):
                return True
        except (ProcessLookupError, PermissionError, psutil.Error, OSError):
            continue
    return False


def _converge_spawned_tree(
    child: subprocess.Popen[object],
    token: str,
) -> list[BaseException]:
    failures: list[BaseException] = []
    deadline = time.monotonic() + _SPAWNED_TREE_CLEANUP_TIMEOUT

    def child_active() -> bool:
        try:
            return child.poll() is None
        except (ProcessLookupError, psutil.NoSuchProcess):
            return False
        except BaseException as exc:
            failures.append(exc)
            return True

    def discover() -> dict[int, psutil.Process]:
        targets: dict[int, psutil.Process] = {}
        if child_active():
            try:
                root = psutil.Process(child.pid)
                for process in root.children(recursive=True):
                    targets[process.pid] = process
            except (ProcessLookupError, psutil.NoSuchProcess):
                pass
            except BaseException as exc:
                failures.append(exc)
        for process in psutil.process_iter(["pid", "status"]):
            try:
                if process.info["status"] == psutil.STATUS_ZOMBIE:
                    continue
                if process.environ().get("MORPHIC_SCAN_GROUP_TOKEN") == token:
                    targets[process.pid] = process
            except (ProcessLookupError, psutil.AccessDenied, psutil.NoSuchProcess):
                continue
            except BaseException as exc:
                failures.append(exc)
        targets.pop(os.getpid(), None)
        targets.pop(child.pid, None)
        return targets

    known = discover()
    if child_active():
        try:
            child.terminate()
        except (ProcessLookupError, psutil.NoSuchProcess):
            pass
        except BaseException as exc:
            failures.append(exc)

    term_sent: set[int] = set()
    term_deadline = min(
        deadline,
        time.monotonic()
        + min(_SPAWNED_TREE_TERM_GRACE, _SPAWNED_TREE_CLEANUP_TIMEOUT / 2),
    )
    empty_scans = 0
    while time.monotonic() < term_deadline:
        known.update(discover())
        for pid, process in list(known.items()):
            if pid in term_sent:
                continue
            try:
                process.terminate()
            except (ProcessLookupError, psutil.NoSuchProcess):
                pass
            except BaseException as exc:
                failures.append(exc)
            term_sent.add(pid)
        active = discover()
        known.update(active)
        empty_scans = empty_scans + 1 if not active and not child_active() else 0
        if empty_scans >= 2:
            break
        time.sleep(
            min(
                _SPAWNED_TREE_POLL_INTERVAL,
                max(0.0, term_deadline - time.monotonic()),
            )
        )

    kill_sent: set[int] = set()
    if child_active():
        try:
            child.kill()
        except (ProcessLookupError, psutil.NoSuchProcess):
            pass
        except BaseException as exc:
            failures.append(exc)
    empty_scans = 0
    while time.monotonic() < deadline:
        active = discover()
        for pid, process in active.items():
            if pid in kill_sent:
                continue
            try:
                process.kill()
            except (ProcessLookupError, psutil.NoSuchProcess):
                pass
            except BaseException as exc:
                failures.append(exc)
            kill_sent.add(pid)
        empty_scans = empty_scans + 1 if not active and not child_active() else 0
        if empty_scans >= 2:
            break
        time.sleep(
            min(
                _SPAWNED_TREE_POLL_INTERVAL,
                max(0.0, deadline - time.monotonic()),
            )
        )

    survivors = discover()
    if child_active():
        failures.append(RuntimeError(f"productive root survived cleanup: {child.pid}"))
    if survivors:
        survivor_ids = ",".join(str(pid) for pid in sorted(survivors))
        failures.append(
            RuntimeError(f"authorized processes survived cleanup: {survivor_ids}")
        )
    return failures


def supervise(
    release_path: Path,
    started_path: Path,
    timeout: float,
    token: str,
    command: list[str],
) -> int:
    deadline = time.monotonic() + timeout
    while not release_path.exists():
        if time.monotonic() >= deadline:
            return 75
        time.sleep(0.02)

    durable_mkdir_parents(started_path.parent, mode=0o700)
    windows_job = _create_windows_job()
    fingerprint = os.environ.get(SCAN_PROFILE_POOL_FINGERPRINT_ENV, "")
    nonce = secrets.token_hex(32)
    proof = build_scan_process_gate_proof(nonce, fingerprint)
    child_environment = dict(os.environ)
    child_environment["MORPHIC_SCAN_GROUP_TOKEN"] = token
    child_environment[SCAN_PROCESS_GATE_NONCE_ENV] = nonce
    child_environment[SCAN_PROCESS_GATE_PROOF_ENV] = proof
    child = subprocess.Popen(
        command,
        shell=False,
        env=child_environment,
    )
    try:
        started_path.write_text(str(child.pid), encoding="ascii")
        supervisor = psutil.Process()
        process_group_id = os.getpgrp() if windows_job is None else None
        child_returncode: int | None = None
        while True:
            if child_returncode is None:
                child_returncode = child.poll()
            active_processes = _windows_job_active_processes(windows_job)
            descendants = _live_descendants(supervisor) if active_processes is None else []
            tree_finished = (
                active_processes <= 1
                if active_processes is not None
                else not descendants
                and not _posix_group_has_productive_members(process_group_id)
            )
            if child_returncode is not None and tree_finished:
                return int(child_returncode)
            time.sleep(0.05)
    except BaseException as primary_error:
        cleanup_failures = _converge_spawned_tree(child, token)
        if cleanup_failures:
            raise BaseExceptionGroup(
                "scan process gate failed and productive cleanup was incomplete",
                [primary_error, *cleanup_failures],
            )
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", required=True, type=Path)
    parser.add_argument("--started", required=True, type=Path)
    parser.add_argument("--result", required=True, type=Path)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = list(args.command)
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        parser.error("a productive command is required")
    token = os.environ.pop("MORPHIC_SCAN_GATE_TOKEN", "")
    if not token:
        parser.error("MORPHIC_SCAN_GATE_TOKEN is required")
    returncode = supervise(args.release, args.started, args.timeout, token, command)
    _publish_result(args.result, returncode)
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
