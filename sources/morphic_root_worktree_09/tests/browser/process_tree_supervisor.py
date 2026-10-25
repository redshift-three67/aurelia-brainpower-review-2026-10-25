from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass, field
import errno
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
from typing import Any, Callable, MutableMapping, TextIO

import psutil


TOKEN_ENV = "MORPHIC_BROWSER_PROCESS_TREE_TOKEN"
IDENTITY_SIDECAR_ENV = "MORPHIC_BROWSER_SUPERVISOR_IDENTITY_SIDECAR"
TOKEN_PATTERN = re.compile(r"^[0-9a-f]{32}$")
READY_RECORD = {"event": "ready", "schema_version": 1}
READY_LINE = json.dumps(READY_RECORD, separators=(",", ":"))

POLL_SECONDS = 0.02
CLEANUP_SECONDS = 5.0
TERM_GRACE_SECONDS = 0.5
EOF_NATURAL_EXIT_GRACE_SECONDS = 1.0


class AuthorityError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProcessIdentity:
    pid: int
    create_time: float


@dataclass
class ControlRequest:
    requested: threading.Event = field(default_factory=threading.Event)
    invalid: bool = False
    eof: bool = False


def _consume_token(environment: MutableMapping[str, str]) -> str:
    token = environment.pop(TOKEN_ENV, "")
    if TOKEN_PATTERN.fullmatch(token) is None:
        raise AuthorityError("invalid isolated browser process authority")
    return token


def _consume_identity_sidecar(
    environment: MutableMapping[str, str],
) -> Path | None:
    raw_path = environment.pop(IDENTITY_SIDECAR_ENV, None)
    if raw_path is None:
        return None
    try:
        path = Path(raw_path)
    except (TypeError, ValueError) as exc:
        raise AuthorityError("invalid supervisor identity sidecar") from exc
    if not raw_path or not path.is_absolute() or not path.parent.is_dir() or path.exists():
        raise AuthorityError("invalid supervisor identity sidecar")
    return path


def _publish_identity_sidecar(path: Path) -> None:
    identity = _process_identity(os.getpid())
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    payload = json.dumps(
        {"pid": identity.pid, "create_time": identity.create_time},
        separators=(",", ":"),
    )
    descriptor: int | None = None
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            descriptor = None
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if path.exists():
            raise AuthorityError("supervisor identity sidecar already exists")
        os.replace(temporary, path)
    except BaseException:
        if descriptor is not None:
            os.close(descriptor)
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise


def _parse_invocation(arguments: list[str]) -> tuple[bool, int | None, list[str]]:
    entry = arguments[:1] == ["--entry"]
    offset = 1 if entry else 0
    ready_fd: int | None = None
    if not entry and arguments[:1] == ["--ready-fd"]:
        try:
            ready_fd = int(arguments[1])
        except (IndexError, TypeError, ValueError) as exc:
            raise AuthorityError("invalid isolated browser process invocation") from exc
        if ready_fd < 3:
            raise AuthorityError("invalid isolated browser process invocation")
        offset = 2
    if arguments[offset : offset + 1] != ["--"]:
        raise AuthorityError("invalid isolated browser process invocation")
    command = arguments[offset + 1 :]
    if not command:
        raise AuthorityError("invalid isolated browser process invocation")
    return entry, ready_fd, command


def _publish_ready(ready_fd: int | None) -> None:
    if ready_fd is None:
        print(READY_LINE, flush=True)
        return
    stream = os.fdopen(
        ready_fd,
        "w",
        encoding="utf-8",
        newline="\n",
        closefd=True,
    )
    try:
        stream.write(READY_LINE + "\n")
        stream.flush()
    finally:
        stream.close()


def _read_control(stream: TextIO, request: ControlRequest) -> None:
    try:
        line = stream.readline()
        request.eof = line == ""
        request.invalid = line not in {"", "stop\n"}
    except BaseException:
        request.invalid = True
    finally:
        request.requested.set()


def _start_control_listener(
    stream: TextIO,
    request: ControlRequest,
) -> threading.Thread:
    listener = threading.Thread(
        target=_read_control,
        args=(stream, request),
        daemon=True,
        name="browser-process-tree-control",
    )
    listener.start()
    return listener


def _explicit_control_arrived(request: ControlRequest) -> bool:
    if not request.requested.is_set():
        request.requested.wait(POLL_SECONDS)
    return request.requested.is_set() and not request.eof


class _IO_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_ulonglong),
        ("WriteOperationCount", ctypes.c_ulonglong),
        ("OtherOperationCount", ctypes.c_ulonglong),
        ("ReadTransferCount", ctypes.c_ulonglong),
        ("WriteTransferCount", ctypes.c_ulonglong),
        ("OtherTransferCount", ctypes.c_ulonglong),
    ]


class _BASIC_LIMITS(ctypes.Structure):
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


class _EXTENDED_LIMITS(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _BASIC_LIMITS),
        ("IoInfo", _IO_COUNTERS),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


class _BASIC_ACCOUNTING(ctypes.Structure):
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


class _NativeWindowsJobApi:
    _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    _JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION = 1
    _JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9

    def __init__(self) -> None:
        if sys.platform != "win32":
            raise OSError("Windows Job Objects are unavailable")
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._create = kernel32.CreateJobObjectW
        self._create.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self._create.restype = wintypes.HANDLE
        self._set = kernel32.SetInformationJobObject
        self._set.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            wintypes.DWORD,
        ]
        self._set.restype = wintypes.BOOL
        self._assign = kernel32.AssignProcessToJobObject
        self._assign.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self._assign.restype = wintypes.BOOL
        self._terminate = kernel32.TerminateJobObject
        self._terminate.argtypes = [wintypes.HANDLE, wintypes.UINT]
        self._terminate.restype = wintypes.BOOL
        self._query = kernel32.QueryInformationJobObject
        self._query.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
        ]
        self._query.restype = wintypes.BOOL
        self._close = kernel32.CloseHandle
        self._close.argtypes = [wintypes.HANDLE]
        self._close.restype = wintypes.BOOL

    @staticmethod
    def _raise_last_error(message: str) -> None:
        error = ctypes.get_last_error()
        raise OSError(error, message)

    def create_kill_on_close_job(self) -> int:
        handle = self._create(None, None)
        if not handle:
            self._raise_last_error("CreateJobObjectW failed")
        numeric_handle = int(handle)
        limits = _EXTENDED_LIMITS()
        limits.BasicLimitInformation.LimitFlags = (
            self._JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        )
        if not self._set(
            numeric_handle,
            self._JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(limits),
            ctypes.sizeof(limits),
        ):
            error = ctypes.get_last_error()
            self._close(numeric_handle)
            raise OSError(error, "SetInformationJobObject failed")
        return numeric_handle

    def assign(self, handle: int, process_handle: int) -> None:
        if not self._assign(handle, process_handle):
            self._raise_last_error("AssignProcessToJobObject failed")

    def terminate(self, handle: int, exit_code: int) -> None:
        if not self._terminate(handle, exit_code):
            self._raise_last_error("TerminateJobObject failed")

    def active_processes(self, handle: int) -> int:
        information = _BASIC_ACCOUNTING()
        if not self._query(
            handle,
            self._JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION,
            ctypes.byref(information),
            ctypes.sizeof(information),
            None,
        ):
            self._raise_last_error("QueryInformationJobObject failed")
        return int(information.ActiveProcesses)

    def close(self, handle: int) -> None:
        if not self._close(handle):
            self._raise_last_error("CloseHandle failed")


class _WindowsJob:
    def __init__(self, *, api: Any | None = None) -> None:
        self._api = api if api is not None else _NativeWindowsJobApi()
        self._handle = self._api.create_kill_on_close_job()
        self._closed = False
        self.kill_on_close = True
        self.assigned_root_identity: ProcessIdentity | None = None

    def assign(
        self,
        process_handle: int,
        identity: ProcessIdentity,
    ) -> None:
        self._api.assign(self._handle, process_handle)
        self.assigned_root_identity = identity

    def terminate(self, exit_code: int = 1) -> None:
        self._api.terminate(self._handle, exit_code)

    def active_processes(self) -> int:
        return self._api.active_processes(self._handle)

    def close(self) -> None:
        if self._closed:
            return
        self._api.close(self._handle)
        self._closed = True


def _process_identity(pid: int) -> ProcessIdentity:
    try:
        return ProcessIdentity(pid, float(psutil.Process(pid).create_time()))
    except (ProcessLookupError, psutil.NoSuchProcess, psutil.Error, OSError, ValueError) as exc:
        raise AuthorityError("productive process identity is unavailable") from exc


def _entry_arguments(command: list[str]) -> list[str]:
    return [sys.executable, str(Path(__file__).resolve()), "--entry", "--", *command]


def _entry_environment(token: str) -> dict[str, str]:
    environment = dict(os.environ)
    environment[TOKEN_ENV] = token
    return environment


def _close_gate(process: subprocess.Popen[Any]) -> None:
    if process.stdin is None or process.stdin.closed:
        return
    process.stdin.close()


def _discard_blocked_entry(process: subprocess.Popen[Any]) -> None:
    _close_gate(process)
    try:
        process.wait(timeout=1)
        return
    except subprocess.TimeoutExpired:
        pass
    process.terminate()
    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=1)


def _wait_for_natural_exit(
    process: subprocess.Popen[Any],
    timeout: float,
) -> int | None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        returncode = process.poll()
        if returncode is not None:
            return int(returncode)
        time.sleep(POLL_SECONDS)
    return None


class _WindowsTree:
    def __init__(
        self,
        root: subprocess.Popen[Any],
        identity: ProcessIdentity,
        job: _WindowsJob,
    ) -> None:
        self.root = root
        self.identity = identity
        self.job = job
        self._released = False
        self._closed = False

    @classmethod
    def start(cls, command: list[str], token: str) -> _WindowsTree:
        job = _WindowsJob()
        try:
            entry = subprocess.Popen(
                _entry_arguments(command),
                stdin=subprocess.PIPE,
                shell=False,
                env=_entry_environment(token),
            )
        except BaseException:
            job.close()
            raise
        try:
            identity = _process_identity(entry.pid)
            job.assign(int(entry._handle), identity)
        except BaseException:
            _discard_blocked_entry(entry)
            job.close()
            raise
        return cls(entry, identity, job)

    def release(self) -> None:
        if self._released:
            raise AuthorityError("productive entry was already released")
        if self.root.stdin is None:
            raise AuthorityError("productive entry gate is unavailable")
        try:
            self.root.stdin.write(b"g")
            self.root.stdin.flush()
            self.root.stdin.close()
        except (BrokenPipeError, OSError, ValueError) as exc:
            raise AuthorityError("productive entry could not be released") from exc
        self._released = True

    def cleanup(
        self,
        *,
        deadline: float,
        term_deadline: float | None = None,
    ) -> None:
        del term_deadline
        root_failure: BaseException | None = None
        try:
            process = psutil.Process(self.identity.pid)
            if float(process.create_time()) == self.identity.create_time:
                process.terminate()
        except (ProcessLookupError, psutil.NoSuchProcess):
            pass
        except BaseException as exc:
            root_failure = exc
        self.job.terminate()
        while True:
            if self.job.active_processes() == 0:
                if root_failure is not None:
                    raise AuthorityError(
                        "exact productive root soft termination failed"
                    ) from root_failure
                return
            now = time.monotonic()
            if now >= deadline:
                raise AuthorityError("productive Job Object cleanup deadline expired")
            time.sleep(min(POLL_SECONDS, max(0.0, deadline - now)))

    def run(self, request: ControlRequest) -> int:
        while True:
            if request.requested.is_set() and request.invalid:
                self.cleanup(deadline=time.monotonic() + CLEANUP_SECONDS)
                return 1
            returncode = self.root.poll()
            if returncode is not None:
                if _explicit_control_arrived(request):
                    self.cleanup(deadline=time.monotonic() + CLEANUP_SECONDS)
                    return 1 if request.invalid else 0
                if self.job.active_processes() != 0:
                    self.cleanup(deadline=time.monotonic() + CLEANUP_SECONDS)
                return int(returncode)
            if request.requested.is_set():
                deadline = time.monotonic() + CLEANUP_SECONDS
                if request.eof:
                    returncode = _wait_for_natural_exit(
                        self.root,
                        min(
                            EOF_NATURAL_EXIT_GRACE_SECONDS,
                            max(0.0, deadline - time.monotonic()),
                        ),
                    )
                    if returncode is not None:
                        if self.job.active_processes() != 0:
                            self.cleanup(deadline=deadline)
                        return returncode
                self.cleanup(deadline=deadline)
                return 1 if request.invalid else 0
            time.sleep(POLL_SECONDS)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            if self.job.active_processes() == 0:
                self.job.close()
                return
        except BaseException:
            pass
        # Closing a still-active kill-on-close job is the last fail-closed action.
        self.job.close()


class _NullPosixAuthority:
    def scan(self) -> dict[ProcessIdentity, psutil.Process]:
        return {}

    def signal(self, identity: ProcessIdentity, *, force: bool) -> bool:
        del identity, force
        raise AuthorityError("POSIX process authority is unavailable")


class _PosixAuthority:
    def __init__(
        self,
        *,
        token: str,
        owner: str,
        baseline: set[ProcessIdentity],
        known: set[ProcessIdentity] | None = None,
        process_iter: Callable[[list[str]], Any] = psutil.process_iter,
        process_factory: Callable[[int], psutil.Process] = psutil.Process,
    ) -> None:
        self._token = token
        self._owner = owner
        self._baseline = set(baseline)
        self._known = set() if known is None else set(known)
        self._process_iter = process_iter
        self._process_factory = process_factory

    def _revalidate(self, identity: ProcessIdentity) -> psutil.Process | None:
        try:
            process = self._process_factory(identity.pid)
            if float(process.create_time()) != identity.create_time:
                self._known.discard(identity)
                return None
            if process.status() == psutil.STATUS_ZOMBIE:
                self._known.discard(identity)
                return None
            if process.username() != self._owner:
                raise AuthorityError("known productive process owner changed")
            try:
                token = process.environ().get(TOKEN_ENV)
            except (PermissionError, psutil.AccessDenied) as exc:
                raise AuthorityError("known productive process token is unreadable") from exc
            if token != self._token:
                raise AuthorityError("known productive process token changed")
            return process
        except (ProcessLookupError, psutil.NoSuchProcess):
            self._known.discard(identity)
            return None
        except (PermissionError, psutil.AccessDenied) as exc:
            raise AuthorityError("known productive process owner is unreadable") from exc
        except AuthorityError:
            raise
        except OSError as exc:
            if exc.errno == errno.ESRCH:
                self._known.discard(identity)
                return None
            raise AuthorityError("known productive process identity is unreadable") from exc
        except (psutil.Error, TypeError, ValueError) as exc:
            raise AuthorityError("known productive process identity is unreadable") from exc

    def scan(self) -> dict[ProcessIdentity, psutil.Process]:
        active: dict[ProcessIdentity, psutil.Process] = {}
        for identity in tuple(self._known):
            process = self._revalidate(identity)
            if process is not None:
                active[identity] = process

        candidates: dict[int, tuple[ProcessIdentity, psutil.Process, int]] = {}
        try:
            iterator = self._process_iter(
                ["pid", "ppid", "status", "username", "create_time"]
            )
            for process in iterator:
                try:
                    pid = int(process.info["pid"])
                    if pid == os.getpid() or process.info["status"] == psutil.STATUS_ZOMBIE:
                        continue
                    owner = process.info.get("username")
                    if owner is not None and owner != self._owner:
                        continue
                    identity = ProcessIdentity(
                        pid,
                        float(process.info["create_time"]),
                    )
                    parent_pid = int(process.info.get("ppid") or 0)
                except (ProcessLookupError, psutil.NoSuchProcess):
                    continue
                except (KeyError, TypeError, ValueError, psutil.Error, OSError) as exc:
                    raise AuthorityError("process discovery identity is unreadable") from exc
                if identity in self._known:
                    continue
                if owner is None:
                    if identity in self._baseline:
                        continue
                    raise AuthorityError("new process owner is unreadable")
                candidates[pid] = (identity, process, parent_pid)
        except AuthorityError:
            raise
        except (psutil.Error, OSError) as exc:
            raise AuthorityError("process discovery failed") from exc

        known_pids = {identity.pid for identity in self._known}

        def linked_to_known(parent_pid: int) -> bool:
            visited: set[int] = set()
            while parent_pid and parent_pid not in visited:
                if parent_pid in known_pids:
                    return True
                visited.add(parent_pid)
                candidate = candidates.get(parent_pid)
                if candidate is None:
                    return False
                parent_pid = candidate[2]
            return False

        for identity, process, parent_pid in candidates.values():
            linked = linked_to_known(parent_pid)
            if identity in self._baseline and not linked:
                continue
            try:
                candidate_token = process.environ().get(TOKEN_ENV)
            except (ProcessLookupError, psutil.NoSuchProcess):
                continue
            except (PermissionError, psutil.AccessDenied) as exc:
                raise AuthorityError(
                    "new same-owner process token is unreadable"
                ) from exc
            except (psutil.Error, OSError, TypeError) as exc:
                raise AuthorityError("process token discovery failed") from exc
            if candidate_token != self._token:
                if linked:
                    raise AuthorityError("linked productive process token changed")
                continue
            self._known.add(identity)
            active[identity] = process
            known_pids.add(identity.pid)
        return active

    def signal(self, identity: ProcessIdentity, *, force: bool) -> bool:
        if identity not in self._known:
            return False
        process = self._revalidate(identity)
        if process is None:
            return False
        try:
            process.kill() if force else process.terminate()
            return True
        except (ProcessLookupError, psutil.NoSuchProcess):
            self._known.discard(identity)
            return False
        except (PermissionError, psutil.AccessDenied, psutil.Error, OSError) as exc:
            raise AuthorityError("authorized productive process could not be signaled") from exc

def _current_owner() -> str:
    try:
        return psutil.Process(os.getpid()).username()
    except (psutil.Error, OSError) as exc:
        raise AuthorityError("supervisor process owner is unreadable") from exc


def _owner_baseline(owner: str) -> set[ProcessIdentity]:
    baseline: set[ProcessIdentity] = set()
    try:
        for process in psutil.process_iter(["pid", "username", "create_time"]):
            try:
                candidate_owner = process.info.get("username")
                if candidate_owner is not None and candidate_owner != owner:
                    continue
                baseline.add(
                    ProcessIdentity(
                        int(process.info["pid"]),
                        float(process.info["create_time"]),
                    )
                )
            except (ProcessLookupError, psutil.NoSuchProcess):
                continue
            except (KeyError, TypeError, ValueError, psutil.Error, OSError):
                continue
    except (psutil.Error, OSError) as exc:
        raise AuthorityError("process baseline could not be captured") from exc
    return baseline


class _PosixTree:
    def __init__(
        self,
        root: subprocess.Popen[Any],
        identity: ProcessIdentity,
        *,
        authority: Any | None = None,
    ) -> None:
        self.root = root
        self.identity = identity
        self.authority = authority if authority is not None else _NullPosixAuthority()
        self._released = False
        self._converged = False
        self._cleanup_deadline: float | None = None
        self._closed = False
        self._root_kill_attempted = False
        self._kill_signaled: set[ProcessIdentity] = set()

    @classmethod
    def start(cls, command: list[str], token: str) -> _PosixTree:
        owner = _current_owner()
        baseline = _owner_baseline(owner)
        entry = subprocess.Popen(
            _entry_arguments(command),
            stdin=subprocess.PIPE,
            shell=False,
            env=_entry_environment(token),
            start_new_session=True,
        )
        try:
            identity = _process_identity(entry.pid)
        except BaseException:
            _discard_blocked_entry(entry)
            raise
        authority = _PosixAuthority(
            token=token,
            owner=owner,
            baseline=baseline,
            known={identity},
        )
        return cls(entry, identity, authority=authority)

    def release(self) -> None:
        if self._released:
            raise AuthorityError("productive entry was already released")
        if self.root.stdin is None:
            raise AuthorityError("productive entry gate is unavailable")
        try:
            self.root.stdin.write(b"g")
            self.root.stdin.flush()
            self.root.stdin.close()
        except (BrokenPipeError, OSError, ValueError) as exc:
            raise AuthorityError("productive entry could not be released") from exc
        self._released = True

    def cleanup(
        self,
        *,
        deadline: float,
        term_deadline: float | None = None,
    ) -> None:
        if self._cleanup_deadline is None:
            self._cleanup_deadline = deadline
        else:
            self._cleanup_deadline = min(self._cleanup_deadline, deadline)
        deadline = self._cleanup_deadline
        term_deadline = (
            min(deadline, time.monotonic() + TERM_GRACE_SECONDS)
            if term_deadline is None
            else min(deadline, term_deadline)
        )
        first_failure: BaseException | None = None
        last_targets: dict[ProcessIdentity, psutil.Process] = {}

        def record_failure(exc: BaseException) -> None:
            nonlocal first_failure
            if first_failure is None:
                first_failure = exc

        def scan() -> tuple[dict[ProcessIdentity, psutil.Process], bool]:
            nonlocal last_targets
            try:
                last_targets = self.authority.scan()
                return last_targets, True
            except BaseException as exc:
                record_failure(exc)
                return last_targets, False

        def poll_root() -> None:
            try:
                self.root.poll()
            except BaseException as exc:
                record_failure(exc)

        root_term_complete = False

        def terminate_root() -> None:
            nonlocal root_term_complete
            if root_term_complete:
                return
            try:
                self.authority.signal(self.identity, force=False)
                root_term_complete = True
            except (ProcessLookupError, psutil.NoSuchProcess):
                root_term_complete = True
            except OSError as exc:
                if exc.errno == errno.ESRCH:
                    root_term_complete = True
                else:
                    record_failure(
                        AuthorityError("productive root could not be terminated")
                    )
            except BaseException as exc:
                record_failure(exc)

        def signal_targets(
            targets: dict[ProcessIdentity, psutil.Process],
            *,
            force: bool,
            signaled: set[ProcessIdentity],
        ) -> None:
            for identity in targets:
                if identity == self.identity or identity in signaled:
                    continue
                try:
                    if force:
                        signaled.add(identity)
                    if self.authority.signal(identity, force=force) and not force:
                        signaled.add(identity)
                except BaseException as exc:
                    record_failure(exc)

        targets, scan_safe = scan()
        poll_root()
        terminate_root()
        term_signaled: set[ProcessIdentity] = set()
        signal_targets(targets, force=False, signaled=term_signaled)

        empty_scans = 0
        while time.monotonic() < term_deadline:
            terminate_root()
            poll_root()
            targets, scan_safe = scan()
            signal_targets(targets, force=False, signaled=term_signaled)
            empty_scans = (
                empty_scans + 1
                if scan_safe and not targets
                else 0
            )
            if empty_scans >= 2:
                self._converged = True
                if first_failure is not None:
                    raise AuthorityError("productive process tree cleanup encountered errors") from first_failure
                return
            time.sleep(POLL_SECONDS)

        poll_root()
        if not self._root_kill_attempted:
            self._root_kill_attempted = True
            try:
                self.authority.signal(self.identity, force=True)
            except (ProcessLookupError, psutil.NoSuchProcess):
                pass
            except OSError as exc:
                if exc.errno != errno.ESRCH:
                    record_failure(exc)
            except BaseException as exc:
                record_failure(exc)
        kill_signaled = self._kill_signaled
        empty_scans = 0
        while time.monotonic() < deadline:
            poll_root()
            targets, scan_safe = scan()
            signal_targets(targets, force=True, signaled=kill_signaled)
            empty_scans = (
                empty_scans + 1
                if scan_safe and not targets
                else 0
            )
            if empty_scans >= 2:
                self._converged = True
                if first_failure is not None:
                    raise AuthorityError("productive process tree cleanup encountered errors") from first_failure
                return
            time.sleep(POLL_SECONDS)
        if first_failure is not None:
            raise AuthorityError("productive process tree cleanup failed before deadline") from first_failure
        raise AuthorityError("productive process tree cleanup deadline expired")

    def _run(self, request: ControlRequest) -> int:
        while True:
            if request.requested.is_set() and request.invalid:
                self.cleanup(deadline=time.monotonic() + CLEANUP_SECONDS)
                return 1
            self.authority.scan()
            returncode = self.root.poll()
            if returncode is not None:
                if _explicit_control_arrived(request):
                    self.cleanup(deadline=time.monotonic() + CLEANUP_SECONDS)
                    return 1 if request.invalid else 0
                self.cleanup(deadline=time.monotonic() + CLEANUP_SECONDS)
                return int(returncode)
            if request.requested.is_set():
                deadline = time.monotonic() + CLEANUP_SECONDS
                if request.eof:
                    returncode = _wait_for_natural_exit(
                        self.root,
                        min(
                            EOF_NATURAL_EXIT_GRACE_SECONDS,
                            max(0.0, deadline - time.monotonic()),
                        ),
                    )
                    if returncode is not None:
                        self.cleanup(deadline=deadline)
                        return returncode
                self.cleanup(
                    deadline=deadline,
                    term_deadline=min(deadline, time.monotonic() + TERM_GRACE_SECONDS),
                )
                return 1 if request.invalid else 0
            time.sleep(POLL_SECONDS)

    def run(self, request: ControlRequest) -> int:
        try:
            return self._run(request)
        except BaseException as primary:
            try:
                self.close()
            except BaseException as cleanup:
                raise BaseExceptionGroup(
                    "productive process failed and cleanup also failed",
                    [primary, cleanup],
                ) from primary
            raise

    def close(self) -> None:
        if self._closed:
            return
        try:
            if not self._converged:
                deadline = self._cleanup_deadline
                if deadline is None:
                    deadline = time.monotonic() + CLEANUP_SECONDS
                self.cleanup(deadline=deadline)
        finally:
            if self._converged:
                self._closed = True


class ProcessTree:
    @staticmethod
    def start(command: list[str], *, token: str) -> _WindowsTree | _PosixTree:
        if sys.platform == "win32":
            return _WindowsTree.start(command, token)
        return _PosixTree.start(command, token)


def _entry_main(command: list[str], token: str) -> int:
    gate = sys.stdin.buffer.read(2)
    if gate != b"g":
        return 64
    child_environment = dict(os.environ)
    child_environment[TOKEN_ENV] = token
    if sys.platform != "win32":
        try:
            os.execvpe(command[0], command, child_environment)
        except (OSError, ValueError):
            print("isolated browser process start failed", file=sys.stderr)
            return 71
        raise AssertionError("os.execvpe returned unexpectedly")
    try:
        productive = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            shell=False,
            env=child_environment,
        )
    except (OSError, ValueError):
        print("isolated browser process start failed", file=sys.stderr)
        return 71
    return int(productive.wait())


def _report_failure(stream: TextIO) -> None:
    print("isolated browser process supervision failed", file=stream, flush=True)


def main() -> int:
    try:
        token = _consume_token(os.environ)
        identity_sidecar = _consume_identity_sidecar(os.environ)
        entry_mode, ready_fd, command = _parse_invocation(sys.argv[1:])
    except BaseException:
        _report_failure(sys.stderr)
        return 64

    if entry_mode:
        if identity_sidecar is not None:
            _report_failure(sys.stderr)
            return 64
        return _entry_main(command, token)

    tree: _WindowsTree | _PosixTree | None = None
    try:
        if identity_sidecar is not None:
            _publish_identity_sidecar(identity_sidecar)
        tree = ProcessTree.start(command, token=token)
        _publish_ready(ready_fd)
        tree.release()
        request = ControlRequest()
        _start_control_listener(sys.stdin, request)
        return tree.run(request)
    except BaseException:
        _report_failure(sys.stderr)
        return 1
    finally:
        if tree is not None:
            try:
                tree.close()
            except BaseException:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
