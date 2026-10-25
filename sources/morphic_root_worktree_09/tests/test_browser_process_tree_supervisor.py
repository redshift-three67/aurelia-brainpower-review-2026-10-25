from __future__ import annotations

import errno
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import queue
import secrets
import signal
import subprocess
import sys
import threading
import time
from types import ModuleType
from typing import Any, Callable

import psutil
import pytest


SUPERVISOR = Path(__file__).parent / "browser" / "process_tree_supervisor.py"
TOKEN_ENV = "MORPHIC_BROWSER_PROCESS_TREE_TOKEN"
IDENTITY_SIDECAR_ENV = "MORPHIC_BROWSER_SUPERVISOR_IDENTITY_SIDECAR"
VALID_TOKEN = "a" * 32
READY_LINE = '{"event":"ready","schema_version":1}'


def _load_supervisor() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "browser_process_tree_supervisor",
        SUPERVISOR,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def supervisor_module() -> ModuleType:
    return _load_supervisor()


@pytest.fixture
def process_tree_token() -> str:
    return secrets.token_hex(16)


@pytest.fixture(autouse=True)
def _require_supervisor_implementation() -> None:
    assert SUPERVISOR.is_file(), "process tree supervisor implementation is missing"


def _supervisor_environment(
    token: str | None,
    *,
    identity_sidecar: Path | None = None,
) -> dict[str, str]:
    environment = dict(os.environ)
    environment["PYTHONUTF8"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"
    environment.pop(IDENTITY_SIDECAR_ENV, None)
    if token is None:
        environment.pop(TOKEN_ENV, None)
    else:
        environment[TOKEN_ENV] = token
    if identity_sidecar is not None:
        environment[IDENTITY_SIDECAR_ENV] = str(identity_sidecar)
    return environment


def _invoke(
    command: list[str],
    *,
    token: str | None,
    input_text: str = "",
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SUPERVISOR), "--", *command],
        input=input_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=_supervisor_environment(token),
        timeout=10,
        check=False,
    )


def _start(
    command: list[str],
    *,
    token: str,
    identity_sidecar: Path,
) -> subprocess.Popen[str]:
    return subprocess.Popen(
        [sys.executable, str(SUPERVISOR), "--", *command],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        env=_supervisor_environment(token, identity_sidecar=identity_sidecar),
    )


def _readline_with_timeout(stream: Any, timeout: float = 5.0) -> str:
    result: queue.Queue[str | BaseException] = queue.Queue(maxsize=1)

    def read() -> None:
        try:
            result.put(stream.readline())
        except BaseException as exc:  # pragma: no cover - defensive test cleanup
            result.put(exc)

    threading.Thread(target=read, daemon=True).start()
    try:
        value = result.get(timeout=timeout)
    except queue.Empty as exc:
        raise AssertionError("supervisor did not publish a bounded readiness line") from exc
    if isinstance(value, BaseException):
        raise value
    return value


def _wait_for(
    predicate: Callable[[], bool],
    *,
    timeout: float = 5.0,
    message: str,
) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.02)
    raise AssertionError(message)


def _read_identities(path: Path) -> list[tuple[int, float]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return [(int(item["pid"]), float(item["create_time"])) for item in raw]
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return []


def _read_supervisor_identity(
    path: Path, *, timeout: float = 5
) -> tuple[int, float]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(record, dict) or set(record) != {"pid", "create_time"}:
                raise ValueError
            pid = record["pid"]
            create_time = record["create_time"]
            if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
                raise ValueError
            if (
                isinstance(create_time, bool)
                or not isinstance(create_time, (int, float))
                or not math.isfinite(float(create_time))
                or float(create_time) <= 0
            ):
                raise ValueError
            return pid, float(create_time)
        except (
            FileNotFoundError,
            PermissionError,
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ):
            time.sleep(0.01)
    raise AssertionError("supervisor identity sidecar was not published")


def _identity_absent(identity: tuple[int, float]) -> bool:
    pid, create_time = identity
    try:
        process = psutil.Process(pid)
        if float(process.create_time()) != create_time:
            return True
        return not process.is_running() or process.status() == psutil.STATUS_ZOMBIE
    except (ProcessLookupError, psutil.NoSuchProcess):
        return True


def _kill_exact(identity: tuple[int, float]) -> None:
    pid, create_time = identity
    try:
        process = psutil.Process(pid)
        if float(process.create_time()) != create_time:
            return
        process.kill()
        process.wait(timeout=2)
    except (ProcessLookupError, psutil.NoSuchProcess, psutil.TimeoutExpired):
        pass


def _force_exact_exit(identity: tuple[int, float]) -> None:
    pid, create_time = identity
    process = psutil.Process(pid)
    assert float(process.create_time()) == create_time
    process.kill()


def _stop_exact_identity(identity: tuple[int, float], *, remaining: float) -> None:
    if remaining <= 0:
        return
    deadline = time.monotonic() + remaining
    pid, create_time = identity
    try:
        process = psutil.Process(pid)
        if float(process.create_time()) != create_time:
            return
        process.terminate()
        term_remaining = deadline - time.monotonic()
        if term_remaining <= 0:
            return
        try:
            process.wait(timeout=min(0.5, term_remaining / 2))
            return
        except psutil.TimeoutExpired:
            pass
        if deadline - time.monotonic() <= 0:
            return
        process = psutil.Process(pid)
        if float(process.create_time()) != create_time:
            return
        process.kill()
        kill_remaining = deadline - time.monotonic()
        if kill_remaining > 0:
            process.wait(timeout=kill_remaining)
    except (ProcessLookupError, psutil.NoSuchProcess):
        return


def _finish_owned_supervisor(
    process: subprocess.Popen[str],
    *,
    token: str,
    supervisor_identity: tuple[int, float] | None,
    primary_error: BaseException | None = None,
    cleanup_timeout: float = 8.0,
    monotonic: Callable[[], float] = time.monotonic,
    scanner: Callable[[str], list[tuple[int, float]]] | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> None:
    total_timeout = max(0.0, cleanup_timeout)
    deadline = monotonic() + total_timeout
    fallback_reserve = min(1.0, total_timeout / 2)
    cleanup_errors: list[BaseException] = []
    deadline_recorded = False
    known_token_identities: set[tuple[int, float]] = set()

    def default_scanner(value: str) -> list[tuple[int, float]]:
        identities = _token_owned_identities(value, known=known_token_identities)
        known_token_identities.update(identities)
        return identities

    scanner_fn = default_scanner if scanner is None else scanner

    def remaining() -> float:
        return max(0.0, deadline - monotonic())

    def record_deadline() -> None:
        nonlocal deadline_recorded
        if deadline_recorded:
            return
        deadline_recorded = True
        cleanup_errors.append(AssertionError("owned supervisor cleanup deadline expired"))

    if remaining() <= 0:
        record_deadline()
    else:
        try:
            if process.poll() is None:
                if process.stdin is not None and not process.stdin.closed:
                    process.stdin.write("stop\n")
                    process.stdin.flush()
                protocol_wait = max(0.0, remaining() - fallback_reserve)
                if protocol_wait > 0:
                    try:
                        process.wait(timeout=protocol_wait)
                    except subprocess.TimeoutExpired as error:
                        cleanup_errors.append(error)
        except BaseException as error:
            cleanup_errors.append(error)

    owned_identities: list[tuple[int, float]] = []
    attempted_identities: set[tuple[int, float]] = set()
    while remaining() > 0:
        try:
            active_identities = scanner_fn(token)
        except BaseException as error:
            cleanup_errors.append(error)
            break
        if remaining() <= 0:
            record_deadline()
            break
        if not active_identities:
            break
        new_identities = [
            identity
            for identity in active_identities
            if identity not in attempted_identities
        ]
        if not new_identities:
            cleanup_errors.append(
                AssertionError(
                    f"token-owned identities survived exact fallback: {active_identities}"
                )
            )
            break
        for identity in new_identities:
            stop_remaining = remaining()
            if stop_remaining <= 0:
                record_deadline()
                break
            attempted_identities.add(identity)
            owned_identities.append(identity)
            try:
                _stop_exact_identity(identity, remaining=stop_remaining)
            except BaseException as error:
                cleanup_errors.append(error)
        if remaining() <= 0:
            record_deadline()
            break

    if remaining() <= 0:
        record_deadline()
    else:
        try:
            supervisor_running = process.poll() is None
        except BaseException as error:
            cleanup_errors.append(error)
            supervisor_running = True
        if supervisor_running:
            if supervisor_identity is None:
                cleanup_errors.append(
                    AssertionError("live supervisor has no published exact identity")
                )
            else:
                stop_remaining = remaining()
                if stop_remaining <= 0:
                    record_deadline()
                else:
                    try:
                        _stop_exact_identity(
                            supervisor_identity,
                            remaining=stop_remaining,
                        )
                    except BaseException as error:
                        cleanup_errors.append(error)
            wait_remaining = remaining()
            if wait_remaining <= 0:
                record_deadline()
            else:
                try:
                    process.wait(timeout=wait_remaining)
                except subprocess.TimeoutExpired as error:
                    cleanup_errors.append(error)

    def verify_absence(identity: tuple[int, float]) -> None:
        while remaining() > 0:
            try:
                if _identity_absent(identity):
                    return
            except BaseException as error:
                cleanup_errors.append(error)
                return
            sleep(min(0.02, remaining()))
        record_deadline()

    if remaining() > 0:
        if supervisor_identity is not None:
            verify_absence(supervisor_identity)
        for identity in owned_identities:
            if remaining() <= 0:
                record_deadline()
                break
            verify_absence(identity)
    else:
        record_deadline()

    if remaining() <= 0:
        record_deadline()

    if primary_error is not None:
        if cleanup_errors:
            cleanup_group = BaseExceptionGroup(
                "owned supervisor cleanup failures", cleanup_errors
            )
            raise BaseExceptionGroup(
                "real supervisor primary and cleanup failures",
                [primary_error, cleanup_group],
            ) from primary_error
        raise primary_error
    if cleanup_errors:
        raise BaseExceptionGroup("owned supervisor cleanup failures", cleanup_errors)


def test_finish_owned_supervisor_requests_protocol_cleanup_before_any_fallback() -> None:
    class ProtocolProcess:
        pid = 43210

        def __init__(self) -> None:
            self.stdin = io.StringIO()
            self.returncode: int | None = None
            self.terminate_calls = 0
            self.kill_calls = 0

        def poll(self) -> int | None:
            return self.returncode

        def wait(self, timeout: float) -> int:
            assert timeout > 0
            assert self.stdin.getvalue() == "stop\n"
            self.returncode = 0
            return 0

        def terminate(self) -> None:
            self.terminate_calls += 1

        def kill(self) -> None:
            self.kill_calls += 1

    process = ProtocolProcess()

    _finish_owned_supervisor(
        process,  # type: ignore[arg-type]
        token=VALID_TOKEN,
        supervisor_identity=(process.pid, 1.0),
        scanner=lambda _token: [],
    )

    assert process.terminate_calls == 0
    assert process.kill_calls == 0


def test_finish_owned_supervisor_never_kills_reused_numeric_pid_and_orders_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class TimedOutProcess:
        pid = 43211

        def __init__(self) -> None:
            self.stdin = io.StringIO()
            self.terminate_calls = 0
            self.kill_calls = 0

        def poll(self) -> None:
            return None

        def wait(self, timeout: float) -> int:
            raise subprocess.TimeoutExpired(["supervisor"], timeout)

        def terminate(self) -> None:
            self.terminate_calls += 1

        def kill(self) -> None:
            self.kill_calls += 1

    class Replacement:
        def create_time(self) -> float:
            return 99.0

    process = TimedOutProcess()
    primary = subprocess.TimeoutExpired(["node"], 1)
    monkeypatch.setattr(psutil, "Process", lambda _pid: Replacement())

    with pytest.raises(BaseExceptionGroup) as caught:
        _finish_owned_supervisor(
            process,  # type: ignore[arg-type]
            token=VALID_TOKEN,
            supervisor_identity=(process.pid, 1.0),
            primary_error=primary,
            scanner=lambda _token: [],
        )

    assert caught.value.exceptions[0] is primary
    assert isinstance(caught.value.exceptions[1], BaseExceptionGroup)
    assert process.stdin.getvalue() == "stop\n"
    assert process.terminate_calls == 0
    assert process.kill_calls == 0


def test_finish_owned_supervisor_converges_late_token_owned_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class ProtocolProcess:
        pid = 43212

        def __init__(self) -> None:
            self.stdin = io.StringIO()
            self.returncode: int | None = None

        def poll(self) -> int | None:
            return self.returncode

        def wait(self, timeout: float) -> int:
            assert timeout > 0
            self.returncode = 0
            return 0

    first = (51001, 1.0)
    late = (51002, 2.0)
    scans = iter(([first], [late], []))
    stopped: list[tuple[int, float]] = []
    monkeypatch.setattr(
        sys.modules[__name__],
        "_stop_exact_identity",
        lambda identity, *, remaining: stopped.append(identity),
    )
    monkeypatch.setattr(sys.modules[__name__], "_identity_absent", lambda _identity: True)

    _finish_owned_supervisor(
        ProtocolProcess(),  # type: ignore[arg-type]
        token=VALID_TOKEN,
        supervisor_identity=(43212, 1.0),
        scanner=lambda _token: next(scans),
    )

    assert stopped == [first, late]


def test_stop_exact_identity_does_no_work_without_remaining_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        psutil,
        "Process",
        lambda _pid: (_ for _ in ()).throw(AssertionError("PID touched after deadline")),
    )

    _stop_exact_identity((52001, 1.0), remaining=0)


def test_finish_owned_supervisor_bounds_endless_new_identities_by_one_deadline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Clock:
        def __init__(self) -> None:
            self.now = 10.0

        def monotonic(self) -> float:
            return self.now

        def advance(self, seconds: float) -> None:
            self.now += seconds

    class TimedOutProcess:
        pid = 43213

        def __init__(self, clock: Clock) -> None:
            self.clock = clock
            self.stdin = io.StringIO()
            self.wait_calls: list[float] = []

        def poll(self) -> None:
            return None

        def wait(self, timeout: float) -> int:
            self.wait_calls.append(timeout)
            self.clock.advance(0.5)
            raise subprocess.TimeoutExpired(["supervisor"], timeout)

    clock = Clock()
    process = TimedOutProcess(clock)
    primary = AssertionError("primary harness failure")
    scan_count = 0
    stop_budgets: list[float] = []

    def scan(_token: str) -> list[tuple[int, float]]:
        nonlocal scan_count
        scan_count += 1
        clock.advance(0.2)
        return [(53000 + scan_count, float(scan_count))]

    def stop(_identity: tuple[int, float], *, remaining: float) -> None:
        assert remaining > 0
        stop_budgets.append(remaining)
        clock.advance(min(0.4, remaining))

    monkeypatch.setattr(sys.modules[__name__], "_stop_exact_identity", stop)
    monkeypatch.setattr(
        sys.modules[__name__],
        "_identity_absent",
        lambda _identity: (_ for _ in ()).throw(
            AssertionError("absence check started after deadline")
        ),
    )

    with pytest.raises(BaseExceptionGroup) as caught:
        _finish_owned_supervisor(
            process,  # type: ignore[arg-type]
            token=VALID_TOKEN,
            supervisor_identity=(process.pid, 1.0),
            primary_error=primary,
            cleanup_timeout=2.0,
            monotonic=clock.monotonic,
            scanner=scan,
        )

    assert caught.value.exceptions[0] is primary
    cleanup_group = caught.value.exceptions[1]
    assert isinstance(cleanup_group, BaseExceptionGroup)
    assert any("deadline" in str(error).lower() for error in cleanup_group.exceptions)
    assert clock.now == pytest.approx(12.0)
    assert scan_count == 3
    assert process.wait_calls == [1.0]
    assert stop_budgets == pytest.approx([1.3, 0.7, 0.1])


def test_protocol_timeout_reserves_same_deadline_budget_for_exact_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Clock:
        def __init__(self) -> None:
            self.now = 10.0

        def monotonic(self) -> float:
            return self.now

        def advance(self, seconds: float) -> None:
            self.now += seconds

    class ProtocolTimeoutProcess:
        pid = 43214

        def __init__(self, clock: Clock) -> None:
            self.clock = clock
            self.stdin = io.StringIO()
            self.returncode: int | None = None
            self.wait_calls: list[float] = []

        def poll(self) -> int | None:
            return self.returncode

        def wait(self, timeout: float) -> int:
            self.wait_calls.append(timeout)
            if len(self.wait_calls) == 1:
                self.clock.advance(timeout)
                raise subprocess.TimeoutExpired(["supervisor"], timeout)
            self.returncode = 0
            return 0

    clock = Clock()
    process = ProtocolTimeoutProcess(clock)
    primary = AssertionError("primary harness failure")
    owned_identity = (54001, 1.0)
    supervisor_identity = (process.pid, 2.0)
    scans = iter(([owned_identity], []))
    scan_count = 0
    stopped: list[tuple[tuple[int, float], float]] = []
    absence_checks: list[tuple[int, float]] = []

    def scan(_token: str) -> list[tuple[int, float]]:
        nonlocal scan_count
        scan_count += 1
        return next(scans)

    def stop(identity: tuple[int, float], *, remaining: float) -> None:
        assert remaining > 0
        stopped.append((identity, remaining))
        if identity == supervisor_identity:
            process.returncode = 0

    def absent(identity: tuple[int, float]) -> bool:
        absence_checks.append(identity)
        return True

    monkeypatch.setattr(sys.modules[__name__], "_stop_exact_identity", stop)
    monkeypatch.setattr(sys.modules[__name__], "_identity_absent", absent)

    with pytest.raises(BaseExceptionGroup) as caught:
        _finish_owned_supervisor(
            process,  # type: ignore[arg-type]
            token=VALID_TOKEN,
            supervisor_identity=supervisor_identity,
            primary_error=primary,
            cleanup_timeout=4.0,
            monotonic=clock.monotonic,
            scanner=scan,
        )

    assert caught.value.exceptions[0] is primary
    cleanup_group = caught.value.exceptions[1]
    assert isinstance(cleanup_group, BaseExceptionGroup)
    assert any(
        isinstance(error, subprocess.TimeoutExpired)
        for error in cleanup_group.exceptions
    )
    assert not any("deadline" in str(error).lower() for error in cleanup_group.exceptions)
    assert process.wait_calls == [3.0, 1.0]
    assert scan_count == 2
    assert [identity for identity, _remaining in stopped] == [
        owned_identity,
        supervisor_identity,
    ]
    assert all(remaining > 0 for _identity, remaining in stopped)
    assert absence_checks == [supervisor_identity, owned_identity]
    assert clock.now == 13.0


def test_token_fallback_access_denied_is_ambiguous_for_new_or_known_same_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = _AuthorityProcess(54501, 4.0, owner="test-owner")
    candidate.environment_readable = False
    identity = (candidate.pid, candidate.create_time())
    monkeypatch.setattr(psutil, "process_iter", lambda _attrs: [candidate])

    with pytest.raises(AssertionError, match="ambiguous"):
        _token_owned_identities(
            VALID_TOKEN,
            owner="test-owner",
            baseline=set(),
            known=set(),
        )

    assert _token_owned_identities(
        VALID_TOKEN,
        owner="test-owner",
        baseline={identity},
        known=set(),
    ) == []
    with pytest.raises(AssertionError, match="ambiguous"):
        _token_owned_identities(
            VALID_TOKEN,
            owner="test-owner",
            baseline={identity},
            known={identity},
        )


def test_token_fallback_skips_unowned_candidate_but_not_known_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = _AuthorityProcess(54502, 5.0, owner=None)
    candidate.environment_readable = False
    identity = (candidate.pid, candidate.create_time())
    monkeypatch.setattr(psutil, "process_iter", lambda _attrs: [candidate])

    assert _token_owned_identities(
        VALID_TOKEN,
        owner="test-owner",
        baseline=set(),
        known=set(),
    ) == []
    with pytest.raises(AssertionError, match="ambiguous"):
        _token_owned_identities(
            VALID_TOKEN,
            owner="test-owner",
            baseline=set(),
            known={identity},
        )


def test_supervisor_identity_reader_retries_transient_access_denied(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sidecar = tmp_path / "supervisor-identity.json"
    sidecar.write_text(
        json.dumps({"pid": os.getpid(), "create_time": 1.25}),
        encoding="utf-8",
    )
    original_read_text = Path.read_text
    attempts = 0

    def transient_read(path: Path, *args: object, **kwargs: object) -> str:
        nonlocal attempts
        if path == sidecar and attempts == 0:
            attempts += 1
            raise PermissionError("temporarily locked")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", transient_read)

    assert _read_supervisor_identity(sidecar) == (os.getpid(), 1.25)
    assert attempts == 1


def _capture_fallback_baseline() -> tuple[str, set[tuple[int, float]]]:
    owner = psutil.Process().username()
    baseline: set[tuple[int, float]] = set()
    for process in psutil.process_iter(["pid", "create_time", "username"]):
        try:
            candidate_owner = process.info.get("username")
            if candidate_owner is not None and candidate_owner != owner:
                continue
            baseline.add(
                (int(process.info["pid"]), float(process.info["create_time"]))
            )
        except (ProcessLookupError, psutil.NoSuchProcess, KeyError, TypeError, ValueError):
            continue
    return owner, baseline


_FALLBACK_OWNER, _FALLBACK_BASELINE = _capture_fallback_baseline()


def _token_owned_identities(
    token: str,
    *,
    owner: str = _FALLBACK_OWNER,
    baseline: set[tuple[int, float]] = _FALLBACK_BASELINE,
    known: set[tuple[int, float]] | None = None,
) -> list[tuple[int, float]]:
    known_identities = set() if known is None else known
    identities: list[tuple[int, float]] = []
    for process in psutil.process_iter(["pid", "create_time", "username"]):
        try:
            candidate_owner = process.info.get("username")
            if candidate_owner is not None and candidate_owner != owner:
                continue
            identity = (
                int(process.info["pid"]),
                float(process.info["create_time"]),
            )
            if candidate_owner is None and identity not in known_identities:
                continue
            if process.environ().get(TOKEN_ENV) != token:
                continue
            identities.append(identity)
        except (ProcessLookupError, psutil.NoSuchProcess):
            continue
        except (PermissionError, psutil.AccessDenied) as error:
            if identity in baseline and identity not in known_identities:
                continue
            raise AssertionError(
                f"same-owner token authority is ambiguous: {identity}"
            ) from error
    return identities


def _start_windows_fault_supervisor(
    marker: Path,
    failure: str,
    *,
    token: str,
    identity_sidecar: Path,
) -> subprocess.Popen[str]:
    productive_code = (
        "import json,os,pathlib,psutil,time;"
        f"pathlib.Path({str(marker)!r}).write_text("
        "json.dumps({'pid':os.getpid(),'create_time':psutil.Process().create_time()}),"
        "encoding='utf-8');"
        "time.sleep(60)"
    )
    harness = f"""
import importlib.util
import os
import pathlib
import sys

path = pathlib.Path({str(SUPERVISOR)!r})
spec = importlib.util.spec_from_file_location("faulted_browser_supervisor", path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
NativeApi = module._NativeWindowsJobApi

class FaultApi:
    def __init__(self):
        self.delegate = NativeApi()

    def create_kill_on_close_job(self):
        return self.delegate.create_kill_on_close_job()

    def assign(self, handle, process_handle):
        if {failure!r} == "assign":
            raise OSError("injected assign failure")
        return self.delegate.assign(handle, process_handle)

    def terminate(self, handle, exit_code):
        if {failure!r} == "terminate":
            raise OSError("injected terminate failure")
        return self.delegate.terminate(handle, exit_code)

    def active_processes(self, handle):
        if {failure!r} == "query":
            raise OSError("injected query failure")
        return self.delegate.active_processes(handle)

    def close(self, handle):
        return self.delegate.close(handle)

module._NativeWindowsJobApi = FaultApi
sys.argv = [str(path), "--", sys.executable, "-c", {productive_code!r}]
raise SystemExit(module.main())
"""
    return subprocess.Popen(
        [sys.executable, "-c", harness],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        env=_supervisor_environment(token, identity_sidecar=identity_sidecar),
    )


def _tree_command(
    identity_path: Path,
    *,
    leader_exits: bool,
    escape_descendant: bool = False,
) -> list[str]:
    descendant_code = (
        "import signal,time;"
        "signal.signal(signal.SIGTERM, signal.SIG_IGN);"
        "time.sleep(60)"
    )
    root_code = (
        "import json,os,pathlib,psutil,subprocess,sys,time;"
        f"child=subprocess.Popen([sys.executable,'-c',{descendant_code!r}],"
        f"start_new_session={escape_descendant!r});"
        "records=["
        "{'pid':os.getpid(),'create_time':psutil.Process().create_time(),"
        "'pgid':os.getpgid(os.getpid()) if hasattr(os,'getpgid') else None},"
        "{'pid':child.pid,'create_time':psutil.Process(child.pid).create_time(),"
        "'pgid':os.getpgid(child.pid) if hasattr(os,'getpgid') else None}];"
        f"pathlib.Path({str(identity_path)!r}).write_text(json.dumps(records),encoding='utf-8');"
        + ("raise SystemExit(6)" if leader_exits else "time.sleep(60)")
    )
    return [sys.executable, "-c", root_code]


def test_posix_real_tree_fixture_uses_new_session_for_escaped_descendant(
    tmp_path: Path,
) -> None:
    command = _tree_command(
        tmp_path / "identities.json",
        leader_exits=True,
        escape_descendant=True,
    )

    assert "start_new_session=True" in command[-1]


def test_supervisor_source_contains_no_numeric_posix_group_signaling() -> None:
    source = SUPERVISOR.read_text(encoding="utf-8")

    assert "os.killpg" not in source
    assert "_signal_group" not in source
    assert "def _group_exists" not in source
    assert "self.root.terminate()" not in source
    assert "self.root.kill()" not in source
    assert "_strict_authority" not in source


def test_parallel_real_supervisors_have_disjoint_random_token_authority(
    tmp_path: Path,
) -> None:
    tokens = [secrets.token_hex(16), secrets.token_hex(16)]
    markers = [tmp_path / "first-token", tmp_path / "second-token"]
    sidecars = [tmp_path / "first-supervisor.json", tmp_path / "second-supervisor.json"]
    processes: list[subprocess.Popen[str]] = []
    supervisor_identities: list[tuple[int, float]] = []
    owned: dict[str, list[tuple[int, float]]] = {}
    primary_error: BaseException | None = None
    try:
        for token, marker, sidecar in zip(tokens, markers, sidecars, strict=True):
            command = [
                sys.executable,
                "-c",
                (
                    "import os,pathlib,time;"
                    f"pathlib.Path({str(marker)!r}).write_text("
                    f"os.environ[{TOKEN_ENV!r}],encoding='ascii');"
                    "time.sleep(60)"
                ),
            ]
            processes.append(
                _start(command, token=token, identity_sidecar=sidecar)
            )
            supervisor_identities.append(_read_supervisor_identity(sidecar))
        for process in processes:
            assert process.stdout is not None
            assert _readline_with_timeout(process.stdout).rstrip("\r\n") == READY_LINE
        for marker in markers:
            _wait_for(marker.exists, message="parallel productive token was not published")

        assert tokens[0] != tokens[1]
        assert [marker.read_text(encoding="ascii") for marker in markers] == tokens
        owned = {token: _token_owned_identities(token) for token in tokens}
        assert all(owned[token] for token in tokens)
        assert {pid for pid, _ in owned[tokens[0]]}.isdisjoint(
            {pid for pid, _ in owned[tokens[1]]}
        )

        for process in processes:
            assert process.stdin is not None
            process.stdin.write("stop\n")
            process.stdin.flush()
        assert [process.wait(timeout=10) for process in processes] == [0, 0]
        assert all(_token_owned_identities(token) == [] for token in tokens)
    except BaseException as error:
        primary_error = error
    finally:
        cleanup_errors: list[BaseException] = []
        for index, process in enumerate(processes):
            try:
                _finish_owned_supervisor(
                    process,
                    token=tokens[index],
                    supervisor_identity=(
                        supervisor_identities[index]
                        if index < len(supervisor_identities)
                        else None
                    ),
                )
            except BaseException as error:
                cleanup_errors.append(error)
        for identities in owned.values():
            for identity in identities:
                _kill_exact(identity)
        if primary_error is not None:
            if cleanup_errors:
                raise BaseExceptionGroup(
                    "parallel supervisor primary and cleanup failures",
                    [
                        primary_error,
                        BaseExceptionGroup("parallel cleanup failures", cleanup_errors),
                    ],
                ) from primary_error
            raise primary_error
        if cleanup_errors:
            raise BaseExceptionGroup("parallel cleanup failures", cleanup_errors)


def test_supervisor_publishes_one_ready_record_then_forwards_and_propagates_exit(
    tmp_path: Path,
    process_tree_token: str,
) -> None:
    sidecar = tmp_path / "supervisor-identity.json"
    command = [
        sys.executable,
        "-c",
        "import sys;print('productive-out');print('productive-err',file=sys.stderr);raise SystemExit(7)",
    ]
    process = _start(
        command,
        token=process_tree_token,
        identity_sidecar=sidecar,
    )
    supervisor_identity: tuple[int, float] | None = None
    primary_error: BaseException | None = None
    assert process.stdin is not None
    assert process.stdout is not None
    assert process.stderr is not None
    try:
        supervisor_identity = _read_supervisor_identity(sidecar)
        assert _readline_with_timeout(process.stdout).rstrip("\r\n") == READY_LINE
        assert process.wait(timeout=10) == 7
        stdout = process.stdout.read()
        stderr = process.stderr.read()
    except BaseException as error:
        primary_error = error
    finally:
        _finish_owned_supervisor(
            process,
            token=process_tree_token,
            supervisor_identity=supervisor_identity,
            primary_error=primary_error,
        )

    assert stdout == "productive-out\n"
    assert stderr == "productive-err\n"
    assert READY_LINE not in stdout
    assert TOKEN_ENV not in stdout + stderr
    assert process_tree_token not in stdout + stderr


def test_productive_child_receives_token_only_via_environment(
    tmp_path: Path,
    process_tree_token: str,
) -> None:
    observed = tmp_path / "environment.json"
    command = [
        sys.executable,
        "-c",
        (
            "import json,os,pathlib;"
            f"pathlib.Path({str(observed)!r}).write_text("
            f"json.dumps({{'token':os.environ.get({TOKEN_ENV!r})}}),encoding='utf-8')"
        ),
    ]
    completed = _invoke(command, token=process_tree_token)

    assert completed.returncode == 0
    assert json.loads(observed.read_text(encoding="utf-8")) == {
        "token": process_tree_token
    }
    assert TOKEN_ENV not in completed.stdout + completed.stderr
    assert process_tree_token not in completed.stdout + completed.stderr
    assert process_tree_token not in " ".join(command)


def test_optional_identity_sidecar_is_atomic_exact_private_and_keeps_readiness_exact(
    tmp_path: Path,
    process_tree_token: str,
) -> None:
    sidecar = tmp_path / "supervisor-identity.json"
    observed = tmp_path / "productive-environment.json"
    environment = _supervisor_environment(process_tree_token)
    environment[IDENTITY_SIDECAR_ENV] = str(sidecar)
    command = [
        sys.executable,
        "-c",
        (
            "import json,os,pathlib;"
            f"pathlib.Path({str(observed)!r}).write_text("
            f"json.dumps({{'sidecar':os.environ.get({IDENTITY_SIDECAR_ENV!r})}}),"
            "encoding='utf-8')"
        ),
    ]
    process = subprocess.Popen(
        [sys.executable, str(SUPERVISOR), "--", *command],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        env=environment,
    )
    assert process.stdin is not None
    assert process.stdout is not None
    try:
        assert _readline_with_timeout(process.stdout).rstrip("\r\n") == READY_LINE
        _wait_for(sidecar.exists, message="supervisor identity sidecar was not published")
        identity = json.loads(sidecar.read_text(encoding="utf-8"))
        assert set(identity) == {"pid", "create_time"}
        published_supervisor = psutil.Process(identity["pid"])
        assert published_supervisor.create_time() == identity["create_time"]
        assert str(SUPERVISOR) in " ".join(published_supervisor.cmdline())
        _wait_for(observed.exists, message="productive environment was not published")
        assert json.loads(observed.read_text(encoding="utf-8")) == {"sidecar": None}
        assert list(tmp_path.glob(".supervisor-identity.json.*.tmp")) == []
        process.stdin.write("stop\n")
        process.stdin.flush()
        assert process.wait(timeout=10) == 0
        assert process.stdout.read() == ""
    finally:
        if process.poll() is None:
            process.stdin.write("stop\n")
            process.stdin.flush()
            process.wait(timeout=10)


def test_existing_malformed_identity_sidecar_fails_closed_before_readiness_or_child(
    tmp_path: Path,
    process_tree_token: str,
) -> None:
    sidecar = tmp_path / "supervisor-identity.json"
    sidecar.write_text('{"pid":"malformed"}', encoding="utf-8")
    marker = tmp_path / "productive-started"
    environment = _supervisor_environment(process_tree_token)
    environment[IDENTITY_SIDECAR_ENV] = str(sidecar)

    completed = subprocess.run(
        [
            sys.executable,
            str(SUPERVISOR),
            "--",
            sys.executable,
            "-c",
            f"from pathlib import Path;Path({str(marker)!r}).write_text('started')",
        ],
        input="stop\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
        timeout=10,
        check=False,
    )

    assert completed.returncode != 0
    assert completed.stdout == ""
    assert not marker.exists()
    assert sidecar.read_text(encoding="utf-8") == '{"pid":"malformed"}'
    assert IDENTITY_SIDECAR_ENV not in completed.stderr
    assert str(sidecar) not in completed.stderr


@pytest.mark.parametrize(
    "token",
    [None, "", "A" * 32, "a" * 31, "a" * 33, "g" * 32, "0" * 31 + "-"],
)
def test_missing_or_malformed_token_fails_closed_without_child(
    tmp_path: Path,
    token: str | None,
) -> None:
    marker = tmp_path / "started"
    completed = _invoke(
        [
            sys.executable,
            "-c",
            f"from pathlib import Path;Path({str(marker)!r}).write_text('started')",
        ],
        token=token,
    )

    assert completed.returncode != 0
    assert not marker.exists()
    assert READY_LINE not in completed.stdout
    assert TOKEN_ENV not in completed.stdout + completed.stderr
    if token:
        assert token not in completed.stdout + completed.stderr


@pytest.mark.parametrize(
    "arguments",
    [[], ["--"], ["not-the-separator", sys.executable, "-c", "raise SystemExit(0)"]],
)
def test_missing_or_malformed_command_fails_closed(
    arguments: list[str],
    process_tree_token: str,
) -> None:
    completed = subprocess.run(
        [sys.executable, str(SUPERVISOR), *arguments],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=_supervisor_environment(process_tree_token),
        timeout=10,
        check=False,
    )

    assert completed.returncode != 0
    assert READY_LINE not in completed.stdout
    assert TOKEN_ENV not in completed.stdout + completed.stderr
    assert process_tree_token not in completed.stdout + completed.stderr


def test_token_is_consumed_from_supervisor_environment(
    supervisor_module: ModuleType,
) -> None:
    environment = {TOKEN_ENV: VALID_TOKEN, "KEPT": "yes"}

    token = supervisor_module._consume_token(environment)

    assert token == VALID_TOKEN
    assert environment == {"KEPT": "yes"}


def test_ready_fd_invocation_is_optional_and_not_part_of_productive_command(
    supervisor_module: ModuleType,
) -> None:
    command = ["productive", "argument"]

    assert supervisor_module._parse_invocation(["--", *command]) == (
        False,
        None,
        command,
    )
    assert supervisor_module._parse_invocation(
        ["--ready-fd", "3", "--", *command]
    ) == (False, 3, command)


@pytest.mark.parametrize(
    "arguments",
    [
        ["--ready-fd", "not-a-fd", "--", "productive"],
        ["--ready-fd", "-1", "--", "productive"],
        ["--ready-fd", "2", "--", "productive"],
        ["--ready-fd", "3", "--ready-fd", "4", "--", "productive"],
    ],
)
def test_ready_fd_invocation_rejects_malformed_authority_channel(
    supervisor_module: ModuleType,
    arguments: list[str],
) -> None:
    with pytest.raises(supervisor_module.AuthorityError, match="invocation"):
        supervisor_module._parse_invocation(arguments)


def test_ready_record_uses_and_closes_dedicated_fd_without_touching_stdout(
    supervisor_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    writes: list[str] = []
    closed: list[bool] = []

    class ReadyStream:
        def write(self, value: str) -> int:
            writes.append(value)
            return len(value)

        def flush(self) -> None:
            pass

        def close(self) -> None:
            closed.append(True)

    stdout = io.StringIO()
    monkeypatch.setattr(supervisor_module.sys, "stdout", stdout)
    monkeypatch.setattr(
        supervisor_module.os,
        "fdopen",
        lambda fd, *args, **kwargs: ReadyStream()
        if fd == 3
        else pytest.fail(f"unexpected ready fd: {fd}"),
    )

    supervisor_module._publish_ready(3)

    assert "".join(writes) == READY_LINE + "\n"
    assert closed == [True]
    assert stdout.getvalue() == ""


def test_ready_fd_broken_pipe_cleans_unreleased_tree_and_returns_nonzero(
    supervisor_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Tree:
        released = False
        closed = False

        def release(self) -> None:
            self.released = True

        def close(self) -> None:
            self.closed = True

    tree = Tree()
    monkeypatch.setenv(TOKEN_ENV, VALID_TOKEN)
    monkeypatch.setattr(
        supervisor_module.sys,
        "argv",
        ["process_tree_supervisor.py", "--ready-fd", "3", "--", "productive"],
    )
    monkeypatch.setattr(supervisor_module.sys, "stderr", io.StringIO())
    monkeypatch.setattr(
        supervisor_module.ProcessTree,
        "start",
        lambda _command, *, token: tree,
    )
    monkeypatch.setattr(
        supervisor_module,
        "_publish_ready",
        lambda _ready_fd: (_ for _ in ()).throw(BrokenPipeError()),
    )

    result = supervisor_module.main()

    assert result != 0
    assert tree.released is False
    assert tree.closed is True


def test_productive_spawn_failure_is_bounded_and_non_disclosing(
    tmp_path: Path,
    process_tree_token: str,
) -> None:
    missing = tmp_path / "definitely-missing-command"
    completed = _invoke([str(missing)], token=process_tree_token)

    assert completed.returncode != 0
    assert completed.stdout.splitlines() in ([], [READY_LINE])
    assert str(missing) not in completed.stdout + completed.stderr
    assert TOKEN_ENV not in completed.stdout + completed.stderr
    assert process_tree_token not in completed.stdout + completed.stderr


@pytest.mark.parametrize("control", [None, "stop\n"])
def test_eof_and_stop_request_the_same_bounded_tree_cleanup(
    tmp_path: Path,
    control: str | None,
    process_tree_token: str,
) -> None:
    identities_path = tmp_path / "identities.json"
    sidecar = tmp_path / "supervisor-identity.json"
    identities: list[tuple[int, float]] = []
    supervisor_identity: tuple[int, float] | None = None
    primary_error: BaseException | None = None
    process = _start(
        _tree_command(identities_path, leader_exits=False),
        token=process_tree_token,
        identity_sidecar=sidecar,
    )
    assert process.stdin is not None
    assert process.stdout is not None
    try:
        supervisor_identity = _read_supervisor_identity(sidecar)
        assert _readline_with_timeout(process.stdout).rstrip("\r\n") == READY_LINE
        _wait_for(
            lambda: len(_read_identities(identities_path)) == 2,
            message="productive root and descendant identities were not published",
        )
        identities = _read_identities(identities_path)
        if control is None:
            process.stdin.close()
        else:
            process.stdin.write(control)
            process.stdin.flush()
        assert process.wait(timeout=10) == 0
        _wait_for(
            lambda: all(_identity_absent(identity) for identity in identities),
            message="supervisor exited before its exact productive identities were absent",
        )
    except BaseException as error:
        primary_error = error
    finally:
        _finish_owned_supervisor(
            process,
            token=process_tree_token,
            supervisor_identity=supervisor_identity,
            primary_error=primary_error,
        )
        for identity in identities:
            _kill_exact(identity)


def test_unknown_control_message_fails_closed_after_cleanup(
    tmp_path: Path,
    process_tree_token: str,
) -> None:
    identities_path = tmp_path / "identities.json"
    sidecar = tmp_path / "supervisor-identity.json"
    identities: list[tuple[int, float]] = []
    supervisor_identity: tuple[int, float] | None = None
    primary_error: BaseException | None = None
    process = _start(
        _tree_command(identities_path, leader_exits=False),
        token=process_tree_token,
        identity_sidecar=sidecar,
    )
    assert process.stdin is not None
    assert process.stdout is not None
    try:
        supervisor_identity = _read_supervisor_identity(sidecar)
        assert _readline_with_timeout(process.stdout).rstrip("\r\n") == READY_LINE
        _wait_for(
            lambda: len(_read_identities(identities_path)) == 2,
            message="productive identities were not published",
        )
        identities = _read_identities(identities_path)
        process.stdin.write("continue\n")
        process.stdin.flush()
        assert process.wait(timeout=10) != 0
        assert all(_identity_absent(identity) for identity in identities)
    except BaseException as error:
        primary_error = error
    finally:
        _finish_owned_supervisor(
            process,
            token=process_tree_token,
            supervisor_identity=supervisor_identity,
            primary_error=primary_error,
        )
        for identity in identities:
            _kill_exact(identity)


def test_control_listener_is_daemon_and_reports_invalid_input(
    supervisor_module: ModuleType,
) -> None:
    request = supervisor_module.ControlRequest()

    listener = supervisor_module._start_control_listener(
        io.StringIO("not-stop\n"),
        request,
    )

    listener.join(timeout=1)
    assert listener.daemon is True
    assert not listener.is_alive()
    assert request.requested.is_set()
    assert request.invalid is True


def test_private_entry_starts_nothing_before_exact_go_byte(
    tmp_path: Path,
    process_tree_token: str,
) -> None:
    marker = tmp_path / "started"
    process = subprocess.Popen(
        [
            sys.executable,
            str(SUPERVISOR),
            "--entry",
            "--",
            sys.executable,
            "-c",
            f"from pathlib import Path;Path({str(marker)!r}).write_text('started')",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=_supervisor_environment(process_tree_token),
    )
    assert process.stdin is not None
    try:
        time.sleep(0.15)
        assert not marker.exists()
        assert process.poll() is None
        process.stdin.write(b"g")
        process.stdin.close()
        assert process.wait(timeout=10) == 0
        assert marker.read_text(encoding="utf-8") == "started"
    finally:
        if process.poll() is None:
            if process.stdin is not None and not process.stdin.closed:
                process.stdin.close()
            process.wait(timeout=3)


@pytest.mark.parametrize("gate", [b"", b"x", b"gg"])
def test_private_entry_rejects_eof_or_any_non_exact_gate(
    tmp_path: Path,
    gate: bytes,
    process_tree_token: str,
) -> None:
    marker = tmp_path / "started"
    completed = subprocess.run(
        [
            sys.executable,
            str(SUPERVISOR),
            "--entry",
            "--",
            sys.executable,
            "-c",
            f"from pathlib import Path;Path({str(marker)!r}).write_text('started')",
        ],
        input=gate,
        capture_output=True,
        env=_supervisor_environment(process_tree_token),
        timeout=10,
        check=False,
    )

    assert completed.returncode != 0
    assert not marker.exists()
    assert TOKEN_ENV.encode() not in completed.stdout + completed.stderr
    assert process_tree_token.encode() not in completed.stdout + completed.stderr


def test_posix_private_entry_execs_productive_command_in_place(
    supervisor_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class BinaryInput:
        buffer = io.BytesIO(b"g")

    class ExecObserved(RuntimeError):
        pass

    calls: list[tuple[str, list[str], dict[str, str]]] = []

    def execvpe(
        executable: str,
        command: list[str],
        environment: dict[str, str],
    ) -> None:
        calls.append((executable, command, environment))
        raise ExecObserved

    monkeypatch.setattr(supervisor_module.sys, "platform", "linux")
    monkeypatch.setattr(supervisor_module.sys, "stdin", BinaryInput())
    monkeypatch.setattr(supervisor_module.os, "execvpe", execvpe)
    monkeypatch.setattr(
        supervisor_module.subprocess,
        "Popen",
        lambda *args, **kwargs: pytest.fail("POSIX entry must not spawn a second root"),
    )

    with pytest.raises(ExecObserved):
        supervisor_module._entry_main(["productive", "argument"], VALID_TOKEN)

    assert calls == [
        (
            "productive",
            ["productive", "argument"],
            {**os.environ, TOKEN_ENV: VALID_TOKEN},
        )
    ]


class _FakeWindowsApi:
    def __init__(self) -> None:
        self.handle = 101
        self.active = 0
        self.assigned: list[tuple[int, int]] = []
        self.terminated: list[tuple[int, int]] = []
        self.closed: list[int] = []
        self.fail_assign = False
        self.fail_query = False
        self.fail_terminate = False

    def create_kill_on_close_job(self) -> int:
        return self.handle

    def assign(self, handle: int, process_handle: int) -> None:
        if self.fail_assign:
            raise OSError("assign failed")
        self.assigned.append((handle, process_handle))

    def terminate(self, handle: int, exit_code: int) -> None:
        if self.fail_terminate:
            raise OSError("terminate failed")
        self.terminated.append((handle, exit_code))

    def active_processes(self, handle: int) -> int:
        if self.fail_query:
            raise OSError("query failed")
        return self.active

    def close(self, handle: int) -> None:
        self.closed.append(handle)


def test_windows_job_records_kill_on_close_identity_and_zero_active(
    supervisor_module: ModuleType,
) -> None:
    api = _FakeWindowsApi()
    identity = supervisor_module.ProcessIdentity(4321, 123.5)
    job = supervisor_module._WindowsJob(api=api)

    job.assign(999, identity)

    assert job.kill_on_close is True
    assert job.assigned_root_identity == identity
    assert job.active_processes() == 0
    assert api.assigned == [(api.handle, 999)]


@pytest.mark.parametrize("failure", ["assign", "query", "terminate"])
def test_windows_job_api_failures_are_fail_closed_and_never_signal_pid(
    supervisor_module: ModuleType,
    failure: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    api = _FakeWindowsApi()
    setattr(api, f"fail_{failure}", True)
    job = supervisor_module._WindowsJob(api=api)
    identity = supervisor_module.ProcessIdentity(5432, 44.0)
    signaled: list[tuple[Any, ...]] = []
    monkeypatch.setattr(os, "kill", lambda *args: signaled.append(args))

    with pytest.raises(OSError):
        if failure == "assign":
            job.assign(777, identity)
        elif failure == "query":
            job.active_processes()
        else:
            job.terminate()

    assert signaled == []
    assert job.assigned_root_identity is None


def test_windows_job_closes_its_handle_only_once(
    supervisor_module: ModuleType,
) -> None:
    api = _FakeWindowsApi()
    job = supervisor_module._WindowsJob(api=api)

    job.close()
    job.close()

    assert api.closed == [api.handle]


def test_windows_cleanup_soft_terminates_exact_root_before_stable_job_termination(
    supervisor_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []

    class Root:
        pid = 3699

    class ExactRoot:
        def create_time(self) -> float:
            return 7.5

        def terminate(self) -> None:
            events.append("root-term")

    class OrderedApi(_FakeWindowsApi):
        def terminate(self, handle: int, exit_code: int) -> None:
            events.append("job-term")
            super().terminate(handle, exit_code)

        def active_processes(self, handle: int) -> int:
            events.append("job-query")
            return 0

    monkeypatch.setattr(supervisor_module.psutil, "Process", lambda _pid: ExactRoot())
    api = OrderedApi()
    tree = supervisor_module._WindowsTree(
        Root(),
        supervisor_module.ProcessIdentity(Root.pid, 7.5),
        supervisor_module._WindowsJob(api=api),
    )

    tree.cleanup(deadline=time.monotonic() + 1)

    assert events == ["root-term", "job-term", "job-query"]


def test_windows_job_membership_remains_authority_without_descendant_token_reads(
    supervisor_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Root:
        pid = 3700

    class ExactRoot:
        def create_time(self) -> float:
            return 8.5

        def terminate(self) -> None:
            pass

    api = _FakeWindowsApi()
    api.active = 0
    monkeypatch.setattr(supervisor_module.psutil, "Process", lambda _pid: ExactRoot())
    monkeypatch.setattr(
        supervisor_module.psutil,
        "process_iter",
        lambda _attrs: pytest.fail("Job-contained descendants must not need token discovery"),
    )
    tree = supervisor_module._WindowsTree(
        Root(),
        supervisor_module.ProcessIdentity(Root.pid, 8.5),
        supervisor_module._WindowsJob(api=api),
    )

    tree.cleanup(deadline=time.monotonic() + 1)

    assert api.terminated == [(api.handle, 1)]


def test_windows_invalid_control_wins_over_simultaneous_natural_zero(
    supervisor_module: ModuleType,
) -> None:
    class ExitedRoot:
        pid = 3701

        @staticmethod
        def poll() -> int:
            return 0

    api = _FakeWindowsApi()
    job = supervisor_module._WindowsJob(api=api)
    tree = supervisor_module._WindowsTree(
        ExitedRoot(),
        supervisor_module.ProcessIdentity(ExitedRoot.pid, 1.0),
        job,
    )
    request = supervisor_module.ControlRequest()
    request.invalid = True
    request.requested.set()

    assert tree.run(request) != 0
    assert api.terminated == [(api.handle, 1)]


def test_windows_stop_arriving_with_exited_root_is_cleanup_success(
    supervisor_module: ModuleType,
) -> None:
    class ExitedRoot:
        pid = 3702

        @staticmethod
        def poll() -> int:
            return signal.SIGTERM

    class DeferredStop:
        def __init__(self) -> None:
            self.set = False

        def is_set(self) -> bool:
            return self.set

        def wait(self, _timeout: float) -> bool:
            self.set = True
            return True

    api = _FakeWindowsApi()
    job = supervisor_module._WindowsJob(api=api)
    tree = supervisor_module._WindowsTree(
        ExitedRoot(),
        supervisor_module.ProcessIdentity(ExitedRoot.pid, 1.0),
        job,
    )
    request = supervisor_module.ControlRequest()
    request.requested = DeferredStop()

    assert tree.run(request) == 0
    assert api.terminated == [(api.handle, 1)]


@pytest.mark.skipif(sys.platform != "win32", reason="requires Windows Job Objects")
def test_windows_assign_failure_subprocess_never_releases_gate_or_readies(
    tmp_path: Path,
    process_tree_token: str,
) -> None:
    marker = tmp_path / "productive.json"
    sidecar = tmp_path / "supervisor-identity.json"
    process = _start_windows_fault_supervisor(
        marker,
        "assign",
        token=process_tree_token,
        identity_sidecar=sidecar,
    )
    assert process.stdin is not None
    identities: list[tuple[int, float]] = []
    supervisor_identity: tuple[int, float] | None = None
    primary_error: BaseException | None = None
    try:
        supervisor_identity = _read_supervisor_identity(sidecar)
        stdout, stderr = process.communicate(input="stop\n", timeout=10)
        assert process.returncode != 0
        assert READY_LINE not in stdout
        assert not marker.exists()
        identities = _token_owned_identities(process_tree_token)
        assert identities == []
        assert TOKEN_ENV not in stdout + stderr
        assert process_tree_token not in stdout + stderr
        assert str(SUPERVISOR) not in stdout + stderr
        assert str(marker) not in stdout + stderr
    except BaseException as error:
        primary_error = error
    finally:
        _finish_owned_supervisor(
            process,
            token=process_tree_token,
            supervisor_identity=supervisor_identity,
            primary_error=primary_error,
        )
        for identity in identities:
            _kill_exact(identity)


@pytest.mark.skipif(sys.platform != "win32", reason="requires Windows Job Objects")
@pytest.mark.parametrize("failure", ["query", "terminate"])
def test_windows_cleanup_api_failure_subprocess_is_nonzero_and_tree_absent(
    tmp_path: Path,
    failure: str,
    process_tree_token: str,
) -> None:
    marker = tmp_path / "productive.json"
    sidecar = tmp_path / "supervisor-identity.json"
    process = _start_windows_fault_supervisor(
        marker,
        failure,
        token=process_tree_token,
        identity_sidecar=sidecar,
    )
    assert process.stdin is not None
    assert process.stdout is not None
    assert process.stderr is not None
    identities: list[tuple[int, float]] = []
    supervisor_identity: tuple[int, float] | None = None
    primary_error: BaseException | None = None
    try:
        supervisor_identity = _read_supervisor_identity(sidecar)
        assert _readline_with_timeout(process.stdout).rstrip("\r\n") == READY_LINE
        _wait_for(marker.exists, message="productive command did not start after assignment")
        identities = [
            (process.pid, psutil.Process(process.pid).create_time()),
            *_token_owned_identities(process_tree_token),
        ]
        process.stdin.write("stop\n")
        process.stdin.flush()
        assert process.wait(timeout=10) != 0
        stdout = process.stdout.read()
        stderr = process.stderr.read()
        assert READY_LINE not in stdout
        assert all(_identity_absent(identity) for identity in identities)
        assert _token_owned_identities(process_tree_token) == []
        assert TOKEN_ENV not in stdout + stderr
        assert process_tree_token not in stdout + stderr
        assert str(SUPERVISOR) not in stdout + stderr
        assert str(marker) not in stdout + stderr
    except BaseException as error:
        primary_error = error
    finally:
        _finish_owned_supervisor(
            process,
            token=process_tree_token,
            supervisor_identity=supervisor_identity,
            primary_error=primary_error,
        )
        for identity in identities:
            _kill_exact(identity)


@pytest.mark.skipif(sys.platform != "win32", reason="requires Windows Job Objects")
def test_windows_real_tree_converges_after_explicit_stop(
    tmp_path: Path,
    process_tree_token: str,
) -> None:
    identities_path = tmp_path / "identities.json"
    sidecar = tmp_path / "supervisor-identity.json"
    identities: list[tuple[int, float]] = []
    supervisor_identity: tuple[int, float] | None = None
    primary_error: BaseException | None = None
    process = _start(
        _tree_command(identities_path, leader_exits=False),
        token=process_tree_token,
        identity_sidecar=sidecar,
    )
    assert process.stdin is not None
    assert process.stdout is not None
    try:
        supervisor_identity = _read_supervisor_identity(sidecar)
        assert _readline_with_timeout(process.stdout).rstrip("\r\n") == READY_LINE
        _wait_for(
            lambda: len(_read_identities(identities_path)) == 2,
            message="real Windows tree identities were not published",
        )
        identities = _read_identities(identities_path)
        assert all(not _identity_absent(identity) for identity in identities)
        process.stdin.write("stop\n")
        process.stdin.flush()
        assert process.wait(timeout=10) == 0
        assert all(_identity_absent(identity) for identity in identities)
    except BaseException as error:
        primary_error = error
    finally:
        _finish_owned_supervisor(
            process,
            token=process_tree_token,
            supervisor_identity=supervisor_identity,
            primary_error=primary_error,
        )
        for identity in identities:
            _kill_exact(identity)


@pytest.mark.skipif(sys.platform != "win32", reason="requires Windows Job Objects")
def test_windows_leader_exit_cleans_resistant_descendant_and_propagates_exit(
    tmp_path: Path,
    process_tree_token: str,
) -> None:
    identities_path = tmp_path / "identities.json"
    sidecar = tmp_path / "supervisor-identity.json"
    identities: list[tuple[int, float]] = []
    supervisor_identity: tuple[int, float] | None = None
    primary_error: BaseException | None = None
    process = _start(
        _tree_command(identities_path, leader_exits=True),
        token=process_tree_token,
        identity_sidecar=sidecar,
    )
    assert process.stdin is not None
    assert process.stdout is not None
    try:
        supervisor_identity = _read_supervisor_identity(sidecar)
        assert _readline_with_timeout(process.stdout).rstrip("\r\n") == READY_LINE
        _wait_for(
            lambda: len(_read_identities(identities_path)) == 2,
            message="leader and descendant identities were not published",
        )
        identities = _read_identities(identities_path)
        assert process.wait(timeout=10) == 6
        assert all(_identity_absent(identity) for identity in identities)
    except BaseException as error:
        primary_error = error
    finally:
        _finish_owned_supervisor(
            process,
            token=process_tree_token,
            supervisor_identity=supervisor_identity,
            primary_error=primary_error,
        )
        for identity in identities:
            _kill_exact(identity)


def _assert_real_forced_leader_stop_converges(
    tmp_path: Path,
    process_tree_token: str,
    *,
    escape_descendant: bool,
    expected_exit_code: int,
) -> list[dict[str, Any]]:
    identities_path = tmp_path / "forced-leader-identities.json"
    sidecar = tmp_path / "forced-leader-supervisor.json"
    identities: list[tuple[int, float]] = []
    supervisor_identity: tuple[int, float] | None = None
    primary_error: BaseException | None = None
    process = _start(
        _tree_command(
            identities_path,
            leader_exits=False,
            escape_descendant=escape_descendant,
        ),
        token=process_tree_token,
        identity_sidecar=sidecar,
    )
    assert process.stdin is not None
    assert process.stdout is not None
    try:
        supervisor_identity = _read_supervisor_identity(sidecar)
        assert _readline_with_timeout(process.stdout).rstrip("\r\n") == READY_LINE
        _wait_for(
            lambda: len(_read_identities(identities_path)) == 2,
            message="forced-exit leader and resistant descendant were not published",
        )
        records = json.loads(identities_path.read_text(encoding="utf-8"))
        identities = _read_identities(identities_path)
        assert all(not _identity_absent(identity) for identity in identities)

        _force_exact_exit(identities[0])
        process.stdin.write("stop\n")
        process.stdin.flush()
        exit_code = process.wait(timeout=10)

        assert exit_code == expected_exit_code
        assert all(_identity_absent(identity) for identity in identities)
        assert _token_owned_identities(process_tree_token) == []
        return records
    except BaseException as error:
        primary_error = error
    finally:
        _finish_owned_supervisor(
            process,
            token=process_tree_token,
            supervisor_identity=supervisor_identity,
            primary_error=primary_error,
        )
        for identity in [*identities, *_token_owned_identities(process_tree_token)]:
            _kill_exact(identity)


@pytest.mark.skipif(sys.platform != "win32", reason="requires real Windows Job Objects")
def test_windows_real_job_converges_after_forced_leader_exit_then_stop(
    tmp_path: Path,
    process_tree_token: str,
) -> None:
    records = _assert_real_forced_leader_stop_converges(
        tmp_path,
        process_tree_token,
        escape_descendant=False,
        expected_exit_code=0,
    )

    assert records[0]["pgid"] is None
    assert records[1]["pgid"] is None


class _FakePosixRoot:
    def __init__(self) -> None:
        self.pid = 2468
        self.returncode: int | None = None
        self.calls: list[str] = []

    def poll(self) -> int | None:
        return self.returncode


class _AuthorityProcess:
    def __init__(
        self,
        pid: int,
        create_time: float,
        *,
        owner: str = "test-owner",
        parent_pid: int = 1,
        token: str | None = VALID_TOKEN,
    ) -> None:
        self.info = {
            "pid": pid,
            "ppid": parent_pid,
            "status": psutil.STATUS_RUNNING,
            "username": owner,
            "create_time": create_time,
        }
        self._owner = owner
        self._token = token
        self.environment_readable = True
        self.owner_readable = True
        self.signals: list[str] = []

    @property
    def pid(self) -> int:
        return int(self.info["pid"])

    def create_time(self) -> float:
        return float(self.info["create_time"])

    def username(self) -> str:
        if not self.owner_readable:
            raise psutil.AccessDenied(self.pid)
        return self._owner

    def status(self) -> str:
        return str(self.info["status"])

    def environ(self) -> dict[str, str]:
        if not self.environment_readable:
            raise psutil.AccessDenied(self.pid)
        return {} if self._token is None else {TOKEN_ENV: self._token}

    def terminate(self) -> None:
        self.signals.append("term")

    def kill(self) -> None:
        self.signals.append("kill")


class _FakePosixAuthority:
    def __init__(
        self,
        root: _FakePosixRoot,
        root_identity: Any,
        *,
        delegate: Any | None = None,
        root_signal: Callable[[bool], bool] | None = None,
    ) -> None:
        self.root = root
        self.root_identity = root_identity
        self.delegate = delegate
        self.root_signal = root_signal

    def scan(self) -> dict[Any, Any]:
        return {} if self.delegate is None else self.delegate.scan()

    def signal(self, target: Any, *, force: bool) -> bool:
        if target == self.root_identity:
            self.root.calls.append("root-kill" if force else "root-term")
            return True if self.root_signal is None else self.root_signal(force)
        if self.delegate is None:
            return False
        return bool(self.delegate.signal(target, force=force))


def test_null_posix_authority_fails_closed_for_root_signal(
    supervisor_module: ModuleType,
) -> None:
    identity = supervisor_module.ProcessIdentity(2468, 1.0)

    with pytest.raises(supervisor_module.AuthorityError, match="authority"):
        supervisor_module._NullPosixAuthority().signal(identity, force=False)


def test_posix_tree_routes_root_term_and_kill_through_identity_authority(
    supervisor_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _FakePosixRoot()
    identity = supervisor_module.ProcessIdentity(root.pid, 1.0)

    def direct_signal_forbidden() -> None:
        raise AssertionError("direct root signal bypassed authority")

    root.terminate = direct_signal_forbidden
    root.kill = direct_signal_forbidden

    class RootAuthority:
        def __init__(self) -> None:
            self.root_live = True
            self.signals: list[tuple[Any, bool]] = []

        def scan(self) -> dict[Any, Any]:
            return {identity: root} if self.root_live else {}

        def signal(self, target: Any, *, force: bool) -> bool:
            self.signals.append((target, force))
            if force:
                self.root_live = False
            return True

    authority = RootAuthority()
    tree = supervisor_module._PosixTree(root, identity, authority=authority)
    now = [10.0]
    monkeypatch.setattr(supervisor_module.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(
        supervisor_module.time,
        "sleep",
        lambda delay: now.__setitem__(0, now[0] + max(delay, 0.1)),
    )

    tree.cleanup(deadline=11.0, term_deadline=10.5)

    assert authority.signals == [(identity, False), (identity, True)]


def test_posix_authority_discovers_setsid_escape_and_retains_stable_identity(
    supervisor_module: ModuleType,
) -> None:
    escaped = _AuthorityProcess(3101, 41.5, parent_pid=1)
    authority = supervisor_module._PosixAuthority(
        token=VALID_TOKEN,
        owner="test-owner",
        baseline=set(),
        process_iter=lambda _attrs: [escaped],
        process_factory=lambda _pid: escaped,
    )
    identity = supervisor_module.ProcessIdentity(escaped.pid, escaped.create_time())

    assert authority.scan() == {identity: escaped}
    escaped.environment_readable = False
    with pytest.raises(supervisor_module.AuthorityError, match="token"):
        authority.scan()
    escaped.environment_readable = True

    authority.signal(identity, force=False)
    authority.signal(identity, force=True)
    assert escaped.signals == ["term", "kill"]


def test_posix_authority_ignores_baseline_but_fails_new_unreadable_candidate(
    supervisor_module: ModuleType,
) -> None:
    baseline_process = _AuthorityProcess(3201, 50.0)
    unknown = _AuthorityProcess(3202, 51.0)
    baseline_process.environment_readable = False
    unknown.environment_readable = False
    baseline_identity = supervisor_module.ProcessIdentity(3201, 50.0)
    authority = supervisor_module._PosixAuthority(
        token=VALID_TOKEN,
        owner="test-owner",
        baseline={baseline_identity},
        process_iter=lambda _attrs: [baseline_process, unknown],
        process_factory=lambda pid: {3201: baseline_process, 3202: unknown}[pid],
    )

    with pytest.raises(supervisor_module.AuthorityError, match="token"):
        authority.scan()

    baseline_only = supervisor_module._PosixAuthority(
        token=VALID_TOKEN,
        owner="test-owner",
        baseline={baseline_identity},
        process_iter=lambda _attrs: [baseline_process],
        process_factory=lambda _pid: baseline_process,
    )
    assert baseline_only.scan() == {}


def test_posix_owner_baseline_records_unreadable_owner_identity(
    supervisor_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    unreadable = _AuthorityProcess(3251, 55.0)
    unreadable.info["username"] = None
    monkeypatch.setattr(
        supervisor_module.psutil,
        "process_iter",
        lambda _attrs: [unreadable],
    )

    assert supervisor_module._owner_baseline("test-owner") == {
        supervisor_module.ProcessIdentity(3251, 55.0)
    }


def test_posix_authority_new_unreadable_owner_is_ambiguous(
    supervisor_module: ModuleType,
) -> None:
    unreadable = _AuthorityProcess(3252, 56.0)
    unreadable.info["username"] = None
    authority = supervisor_module._PosixAuthority(
        token=VALID_TOKEN,
        owner="test-owner",
        baseline=set(),
        process_iter=lambda _attrs: [unreadable],
        process_factory=lambda _pid: unreadable,
    )

    with pytest.raises(supervisor_module.AuthorityError, match="owner"):
        authority.scan()


def test_posix_authority_skips_proven_foreign_owner_before_identity_parsing(
    supervisor_module: ModuleType,
) -> None:
    foreign = _AuthorityProcess(3253, 57.0, owner="other-owner")
    foreign.info["create_time"] = "not-a-create-time"
    authority = supervisor_module._PosixAuthority(
        token=VALID_TOKEN,
        owner="test-owner",
        baseline=set(),
        process_iter=lambda _attrs: [foreign],
        process_factory=lambda _pid: foreign,
    )

    assert authority.scan() == {}


def test_posix_authority_fails_when_known_same_owner_identity_becomes_unreadable(
    supervisor_module: ModuleType,
) -> None:
    escaped = _AuthorityProcess(3301, 61.0)
    authority = supervisor_module._PosixAuthority(
        token=VALID_TOKEN,
        owner="test-owner",
        baseline=set(),
        process_iter=lambda _attrs: [escaped],
        process_factory=lambda _pid: escaped,
    )

    authority.scan()
    escaped.owner_readable = False

    with pytest.raises(supervisor_module.AuthorityError, match="owner"):
        authority.scan()


def test_posix_authority_never_signals_reused_or_foreign_identity(
    supervisor_module: ModuleType,
) -> None:
    replacement = _AuthorityProcess(3401, 72.0, token=None)
    foreign = _AuthorityProcess(3402, 73.0, owner="other-owner")
    original = supervisor_module.ProcessIdentity(3401, 71.0)
    authority = supervisor_module._PosixAuthority(
        token=VALID_TOKEN,
        owner="test-owner",
        baseline=set(),
        process_iter=lambda _attrs: [replacement, foreign],
        process_factory=lambda pid: {3401: replacement, 3402: foreign}[pid],
    )

    assert authority.scan() == {}
    assert authority.signal(original, force=True) is False
    assert replacement.signals == []
    assert foreign.signals == []


@pytest.mark.parametrize(
    ("mutation", "raises"),
    [
        ("create-time", False),
        ("token", True),
        ("owner", True),
        ("token-unreadable", True),
    ],
)
def test_posix_authority_revalidates_identity_owner_and_token_before_signal(
    supervisor_module: ModuleType,
    mutation: str,
    raises: bool,
) -> None:
    process = _AuthorityProcess(3451, 75.0)
    authority = supervisor_module._PosixAuthority(
        token=VALID_TOKEN,
        owner="test-owner",
        baseline=set(),
        process_iter=lambda _attrs: [process],
        process_factory=lambda _pid: process,
    )
    identity = supervisor_module.ProcessIdentity(process.pid, process.create_time())
    authority.scan()
    if mutation == "create-time":
        process.info["create_time"] = 76.0
    elif mutation == "token":
        process._token = "b" * 32
    elif mutation == "owner":
        process._owner = "other-owner"
    else:
        process.environment_readable = False

    if raises:
        with pytest.raises(supervisor_module.AuthorityError):
            authority.signal(identity, force=True)
    else:
        assert authority.signal(identity, force=True) is False
    assert process.signals == []


def test_posix_linked_descendant_without_exact_token_is_ambiguous(
    supervisor_module: ModuleType,
) -> None:
    root = _AuthorityProcess(3461, 77.0)
    descendant = _AuthorityProcess(
        3462,
        78.0,
        parent_pid=root.pid,
        token=None,
    )
    root_identity = supervisor_module.ProcessIdentity(root.pid, root.create_time())
    authority = supervisor_module._PosixAuthority(
        token=VALID_TOKEN,
        owner="test-owner",
        baseline=set(),
        known={root_identity},
        process_iter=lambda _attrs: [root, descendant],
        process_factory=lambda pid: {root.pid: root, descendant.pid: descendant}[pid],
    )

    with pytest.raises(supervisor_module.AuthorityError, match="token"):
        authority.scan()


def test_posix_reused_root_pid_is_not_signaled_after_identity_loss(
    supervisor_module: ModuleType,
) -> None:
    original = supervisor_module.ProcessIdentity(3471, 79.0)
    replacement = _AuthorityProcess(3471, 80.0, token=None)
    authority = supervisor_module._PosixAuthority(
        token=VALID_TOKEN,
        owner="test-owner",
        baseline=set(),
        known={original},
        process_iter=lambda _attrs: [replacement],
        process_factory=lambda _pid: replacement,
    )
    root = _FakePosixRoot()
    root.pid = original.pid
    tree = supervisor_module._PosixTree(root, original, authority=authority)
    tree.cleanup(
        deadline=time.monotonic() + 1,
        term_deadline=time.monotonic() + 0.5,
    )

    assert replacement.signals == []


def test_posix_root_signal_stops_when_root_token_changes(
    supervisor_module: ModuleType,
) -> None:
    root_process = _AuthorityProcess(3481, 82.0)
    root_identity = supervisor_module.ProcessIdentity(
        root_process.pid,
        root_process.create_time(),
    )
    authority = supervisor_module._PosixAuthority(
        token=VALID_TOKEN,
        owner="test-owner",
        baseline=set(),
        known={root_identity},
        process_iter=lambda _attrs: [root_process],
        process_factory=lambda _pid: root_process,
    )
    root = _FakePosixRoot()
    root.pid = root_process.pid
    tree = supervisor_module._PosixTree(root, root_identity, authority=authority)
    root_process._token = "b" * 32

    with pytest.raises(supervisor_module.AuthorityError, match="token|cleanup"):
        tree.cleanup(
            deadline=time.monotonic() + 0.1,
            term_deadline=time.monotonic() + 0.05,
        )

    assert root_process.signals == []


def test_posix_cleanup_never_signals_foreign_joiner(
    supervisor_module: ModuleType,
) -> None:
    class ResistantProcess(_AuthorityProcess):
        def kill(self) -> None:
            super().kill()
            self.info["status"] = psutil.STATUS_ZOMBIE

    root_process = ResistantProcess(3498, 90.0)
    descendant = ResistantProcess(3499, 91.0, parent_pid=root_process.pid)
    foreign_joiner = _AuthorityProcess(
        3500,
        92.0,
        owner="other-owner",
        token=None,
    )
    root_identity = supervisor_module.ProcessIdentity(
        root_process.pid,
        root_process.create_time(),
    )
    authority = supervisor_module._PosixAuthority(
        token=VALID_TOKEN,
        owner="test-owner",
        baseline=set(),
        known={root_identity},
        process_iter=lambda _attrs: [root_process, descendant, foreign_joiner],
        process_factory=lambda pid: {
            root_process.pid: root_process,
            descendant.pid: descendant,
        }[pid],
    )
    root = _FakePosixRoot()
    root.pid = root_process.pid
    tree = supervisor_module._PosixTree(root, root_identity, authority=authority)
    tree.cleanup(
        deadline=time.monotonic() + 1.5,
        term_deadline=time.monotonic() + 0.3,
    )

    assert foreign_joiner.signals == []
    assert root_process.signals == ["term", "kill"]
    assert descendant.signals == ["term", "kill"]


def test_posix_revalidate_treats_root_zombie_as_absent_before_token_read(
    supervisor_module: ModuleType,
) -> None:
    root = _AuthorityProcess(3493, 85.0)
    root.info["status"] = psutil.STATUS_ZOMBIE
    root.environment_readable = False
    identity = supervisor_module.ProcessIdentity(root.pid, root.create_time())
    authority = supervisor_module._PosixAuthority(
        token=VALID_TOKEN,
        owner="test-owner",
        baseline=set(),
        known={identity},
        process_iter=lambda _attrs: [root],
        process_factory=lambda _pid: root,
    )

    assert authority.scan() == {}
    assert authority.signal(identity, force=True) is False
    assert root.signals == []


@pytest.mark.parametrize(
    "exit_error",
    [psutil.NoSuchProcess(3494), OSError(errno.ESRCH, "member exited")],
)
def test_posix_group_member_exit_between_getpgid_and_environ_is_absent(
    supervisor_module: ModuleType,
    exit_error: BaseException,
) -> None:
    root = _AuthorityProcess(3494, 86.0)
    member = _AuthorityProcess(3495, 87.0, parent_pid=root.pid)
    root_identity = supervisor_module.ProcessIdentity(root.pid, root.create_time())

    def exited_environment() -> dict[str, str]:
        raise exit_error

    member.environ = exited_environment  # type: ignore[method-assign]
    authority = supervisor_module._PosixAuthority(
        token=VALID_TOKEN,
        owner="test-owner",
        baseline=set(),
        known={root_identity},
        process_iter=lambda _attrs: [root, member],
        process_factory=lambda pid: {root.pid: root, member.pid: member}[pid],
    )

    assert authority.scan() == {root_identity: root}
    assert member.signals == []


@pytest.mark.parametrize(
    "ambiguity",
    [psutil.AccessDenied(3495), OSError(errno.EPERM, "member denied")],
)
def test_posix_group_member_permission_failure_is_ambiguous(
    supervisor_module: ModuleType,
    ambiguity: BaseException,
) -> None:
    root = _AuthorityProcess(3496, 88.0)
    member = _AuthorityProcess(3497, 89.0, parent_pid=root.pid)
    root_identity = supervisor_module.ProcessIdentity(root.pid, root.create_time())

    def unreadable_environment() -> dict[str, str]:
        raise ambiguity

    member.environ = unreadable_environment  # type: ignore[method-assign]
    authority = supervisor_module._PosixAuthority(
        token=VALID_TOKEN,
        owner="test-owner",
        baseline=set(),
        known={root_identity},
        process_iter=lambda _attrs: [root, member],
        process_factory=lambda pid: {root.pid: root, member.pid: member}[pid],
    )

    with pytest.raises(supervisor_module.AuthorityError):
        authority.scan()


def test_posix_cleanup_requires_two_safe_empty_authority_scans(
    supervisor_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    escaped = _AuthorityProcess(3501, 81.0)
    identity = supervisor_module.ProcessIdentity(escaped.pid, escaped.create_time())

    class SequencedAuthority:
        def __init__(self) -> None:
            self.scan_count = 0
            self.empty_scans_after_kill = 0

        def scan(self) -> dict[Any, Any]:
            self.scan_count += 1
            if "kill" not in escaped.signals:
                return {identity: escaped}
            self.empty_scans_after_kill += 1
            return {}

        def signal(self, target: Any, *, force: bool) -> bool:
            escaped.kill() if force else escaped.terminate()
            return True

    root = _FakePosixRoot()
    root.returncode = 0
    root_identity = supervisor_module.ProcessIdentity(root.pid, 1.0)
    descendant_authority = SequencedAuthority()
    authority = _FakePosixAuthority(
        root,
        root_identity,
        delegate=descendant_authority,
    )
    tree = supervisor_module._PosixTree(
        root,
        root_identity,
        authority=authority,
    )
    now = [40.0]
    monkeypatch.setattr(supervisor_module.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(
        supervisor_module.time,
        "sleep",
        lambda delay: now.__setitem__(0, now[0] + max(delay, 0.1)),
    )

    tree.cleanup(deadline=42.0, term_deadline=40.5)

    assert descendant_authority.empty_scans_after_kill == 2
    assert escaped.signals == ["term", "kill"]


def test_posix_term_signal_order_is_productive_root_then_descendant(
    supervisor_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    order: list[str] = []
    escaped = _AuthorityProcess(3601, 91.0)
    identity = supervisor_module.ProcessIdentity(escaped.pid, escaped.create_time())

    root = _FakePosixRoot()
    root_identity = supervisor_module.ProcessIdentity(root.pid, 1.0)

    def signal_root(force: bool) -> bool:
        if not force:
            order.append("root-term")
            root.returncode = -signal.SIGTERM
        return True

    class OrderedAuthority:
        def scan(self) -> dict[Any, Any]:
            return {} if "descendant-term" in order else {identity: escaped}

        def signal(self, target: Any, *, force: bool) -> bool:
            order.append("descendant-kill" if force else "descendant-term")
            return True

    authority = _FakePosixAuthority(
        root,
        root_identity,
        delegate=OrderedAuthority(),
        root_signal=signal_root,
    )
    tree = supervisor_module._PosixTree(
        root,
        root_identity,
        authority=authority,
    )
    now = [50.0]
    monkeypatch.setattr(supervisor_module.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(
        supervisor_module.time,
        "sleep",
        lambda delay: now.__setitem__(0, now[0] + max(delay, 0.1)),
    )

    tree.cleanup(deadline=52.0, term_deadline=51.0)

    assert order[:2] == ["root-term", "descendant-term"]


def test_posix_invalid_control_wins_over_simultaneous_natural_zero(
    supervisor_module: ModuleType,
) -> None:
    root = _FakePosixRoot()
    root.returncode = 0
    identity = supervisor_module.ProcessIdentity(root.pid, 1.0)
    tree = supervisor_module._PosixTree(
        root,
        identity,
        authority=_FakePosixAuthority(root, identity),
    )
    request = supervisor_module.ControlRequest()
    request.invalid = True
    request.requested.set()
    assert tree.run(request) != 0
    assert tree._converged is True


def test_posix_stop_arriving_with_exited_root_is_cleanup_success(
    supervisor_module: ModuleType,
) -> None:
    class DeferredStop:
        def __init__(self) -> None:
            self.set = False

        def is_set(self) -> bool:
            return self.set

        def wait(self, _timeout: float) -> bool:
            self.set = True
            return True

    root = _FakePosixRoot()
    root.returncode = -signal.SIGKILL
    identity = supervisor_module.ProcessIdentity(root.pid, 1.0)
    tree = supervisor_module._PosixTree(
        root,
        identity,
        authority=_FakePosixAuthority(root, identity),
    )
    request = supervisor_module.ControlRequest()
    request.requested = DeferredStop()

    assert tree.run(request) == 0
    assert tree._converged is True


@pytest.mark.parametrize(("mode", "late_scan"), (("natural", 2), ("eof", 3)))
def test_posix_natural_and_eof_require_two_empty_scans_after_late_descendant(
    supervisor_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
    late_scan: int,
) -> None:
    escaped = _AuthorityProcess(3749, 110.0)
    escaped_identity = supervisor_module.ProcessIdentity(
        escaped.pid,
        escaped.create_time(),
    )

    class Root(_FakePosixRoot):
        def __init__(self) -> None:
            super().__init__()
            self.poll_count = 0

        def poll(self) -> int | None:
            self.poll_count += 1
            if mode == "eof" and self.poll_count == 1:
                return None
            return 0

    class LateAuthority:
        def __init__(self) -> None:
            self.scan_count = 0
            self.empty_after_signal = 0

        def scan(self) -> dict[Any, Any]:
            self.scan_count += 1
            if escaped.signals:
                self.empty_after_signal += 1
                return {}
            if self.scan_count == late_scan:
                return {escaped_identity: escaped}
            return {}

        def signal(self, target: Any, *, force: bool) -> bool:
            escaped.kill() if force else escaped.terminate()
            return True

    root = Root()
    root_identity = supervisor_module.ProcessIdentity(root.pid, 1.0)
    late_authority = LateAuthority()
    tree = supervisor_module._PosixTree(
        root,
        root_identity,
        authority=_FakePosixAuthority(
            root,
            root_identity,
            delegate=late_authority,
        ),
    )
    request = supervisor_module.ControlRequest()
    if mode == "eof":
        request.eof = True
        request.requested.set()
    now = [70.0]
    monkeypatch.setattr(supervisor_module.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(
        supervisor_module.time,
        "sleep",
        lambda delay: now.__setitem__(0, now[0] + max(delay, 0.1)),
    )

    assert tree.run(request) == 0

    assert escaped.signals == ["term"]
    assert late_authority.empty_after_signal == 2
    assert tree._converged is True


def test_posix_eof_natural_exit_still_cleans_known_escape(
    supervisor_module: ModuleType,
) -> None:
    escaped = _AuthorityProcess(3751, 111.0)
    identity = supervisor_module.ProcessIdentity(escaped.pid, escaped.create_time())

    class GraceExitRoot(_FakePosixRoot):
        def __init__(self) -> None:
            super().__init__()
            self.poll_count = 0

        def poll(self) -> int | None:
            self.poll_count += 1
            if self.poll_count < 2:
                return None
            return 0

    class EscapedAuthority:
        def scan(self) -> dict[Any, Any]:
            return {} if "kill" in escaped.signals else {identity: escaped}

        def signal(self, target: Any, *, force: bool) -> bool:
            escaped.kill() if force else escaped.terminate()
            return True

    root = GraceExitRoot()
    root_identity = supervisor_module.ProcessIdentity(root.pid, 1.0)
    tree = supervisor_module._PosixTree(
        root,
        root_identity,
        authority=_FakePosixAuthority(
            root,
            root_identity,
            delegate=EscapedAuthority(),
        ),
    )
    request = supervisor_module.ControlRequest()
    request.eof = True
    request.requested.set()
    assert tree.run(request) == 0
    assert escaped.signals == ["term", "kill"]
    assert tree._converged is True


def test_posix_close_converges_released_tree_instead_of_noop(
    supervisor_module: ModuleType,
) -> None:
    root = _FakePosixRoot()
    identity = supervisor_module.ProcessIdentity(root.pid, 1.0)
    tree = supervisor_module._PosixTree(
        root,
        identity,
        authority=_FakePosixAuthority(root, identity),
    )
    tree._released = True
    tree.close()

    assert root.calls == ["root-term"]
    assert tree._converged is True


def test_posix_poll_exception_runs_cleanup_before_reraising(
    supervisor_module: ModuleType,
) -> None:
    class PollFailureRoot(_FakePosixRoot):
        def __init__(self) -> None:
            super().__init__()
            self.poll_count = 0

        def poll(self) -> int | None:
            self.poll_count += 1
            if self.poll_count == 1:
                raise RuntimeError("poll failed")
            return self.returncode

    root = PollFailureRoot()
    identity = supervisor_module.ProcessIdentity(root.pid, 1.0)

    def signal_root(force: bool) -> bool:
        if not force:
            root.returncode = -signal.SIGTERM
        return True

    tree = supervisor_module._PosixTree(
        root,
        identity,
        authority=_FakePosixAuthority(
            root,
            identity,
            root_signal=signal_root,
        ),
    )
    tree._released = True
    with pytest.raises(RuntimeError, match="poll failed"):
        tree.run(supervisor_module.ControlRequest())

    assert root.calls == ["root-term"]
    assert tree._converged is True


def test_posix_discovery_exception_runs_cleanup_before_reraising(
    supervisor_module: ModuleType,
) -> None:
    class DiscoveryFailure:
        def __init__(self) -> None:
            self.calls = 0

        def scan(self) -> dict[Any, Any]:
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("discovery failed")
            return {}

        def signal(self, target: Any, *, force: bool) -> bool:
            return False

    root = _FakePosixRoot()
    authority = DiscoveryFailure()
    identity = supervisor_module.ProcessIdentity(root.pid, 1.0)
    tree = supervisor_module._PosixTree(
        root,
        identity,
        authority=_FakePosixAuthority(root, identity, delegate=authority),
    )
    tree._released = True
    with pytest.raises(RuntimeError, match="discovery failed"):
        tree.run(supervisor_module.ControlRequest())

    assert authority.calls >= 3
    assert root.calls == ["root-term"]
    assert tree._converged is True


def test_posix_run_orders_primary_then_close_cleanup_error(
    supervisor_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    primary = RuntimeError("primary failure")
    cleanup = supervisor_module.AuthorityError("cleanup failure")
    tree = supervisor_module._PosixTree(
        _FakePosixRoot(),
        supervisor_module.ProcessIdentity(2468, 1.0),
    )
    monkeypatch.setattr(
        tree,
        "_run",
        lambda _request: (_ for _ in ()).throw(primary),
    )
    monkeypatch.setattr(
        tree,
        "close",
        lambda: (_ for _ in ()).throw(cleanup),
    )

    with pytest.raises(BaseExceptionGroup) as captured:
        tree.run(supervisor_module.ControlRequest())

    assert captured.value.exceptions == (primary, cleanup)


@pytest.mark.parametrize("failure_kind", ["primary", "cleanup"])
def test_posix_run_preserves_single_error_identity(
    supervisor_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    failure_kind: str,
) -> None:
    failure = (
        RuntimeError("primary failure")
        if failure_kind == "primary"
        else supervisor_module.AuthorityError("cleanup failure")
    )
    tree = supervisor_module._PosixTree(
        _FakePosixRoot(),
        supervisor_module.ProcessIdentity(2468, 1.0),
    )
    monkeypatch.setattr(
        tree,
        "_run",
        lambda _request: (_ for _ in ()).throw(failure),
    )
    monkeypatch.setattr(tree, "close", lambda: None)

    with pytest.raises(type(failure)) as captured:
        tree.run(supervisor_module.ControlRequest())

    assert captured.value is failure


def test_posix_terminate_exception_retries_cleanup_under_same_deadline(
    supervisor_module: ModuleType,
) -> None:
    root = _FakePosixRoot()
    identity = supervisor_module.ProcessIdentity(root.pid, 1.0)

    def signal_root(force: bool) -> bool:
        if not force and root.calls.count("root-term") == 1:
            raise OSError(errno.EPERM, "term failed")
        if not force:
            root.returncode = -signal.SIGTERM
        return True

    tree = supervisor_module._PosixTree(
        root,
        identity,
        authority=_FakePosixAuthority(
            root,
            identity,
            root_signal=signal_root,
        ),
    )
    tree._released = True
    request = supervisor_module.ControlRequest()
    request.requested.set()
    with pytest.raises(supervisor_module.AuthorityError, match="cleanup"):
        tree.run(request)

    assert root.calls == ["root-term", "root-term"]
    assert tree._converged is True


def test_listener_start_exception_closes_released_posix_tree(
    supervisor_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _FakePosixRoot()
    root.stdin = io.BytesIO()
    identity = supervisor_module.ProcessIdentity(root.pid, 1.0)
    tree = supervisor_module._PosixTree(
        root,
        identity,
        authority=_FakePosixAuthority(root, identity),
    )
    monkeypatch.setenv(TOKEN_ENV, VALID_TOKEN)
    monkeypatch.setattr(
        supervisor_module.sys,
        "argv",
        [str(SUPERVISOR), "--", "productive"],
    )
    monkeypatch.setattr(supervisor_module.sys, "stdout", io.StringIO())
    monkeypatch.setattr(supervisor_module.sys, "stderr", io.StringIO())
    monkeypatch.setattr(
        supervisor_module.ProcessTree,
        "start",
        lambda command, *, token: tree,
    )
    monkeypatch.setattr(
        supervisor_module,
        "_start_control_listener",
        lambda stream, request: (_ for _ in ()).throw(RuntimeError("listener failed")),
    )
    assert supervisor_module.main() != 0
    assert root.calls == ["root-term"]
    assert tree._converged is True


def test_persistent_discovery_failure_still_signals_root_bounded(
    supervisor_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class BrokenDiscovery:
        def scan(self) -> dict[Any, Any]:
            raise supervisor_module.AuthorityError("discovery unavailable")

        def signal(self, target: Any, *, force: bool) -> bool:
            return False

    root = _FakePosixRoot()
    identity = supervisor_module.ProcessIdentity(root.pid, 1.0)
    tree = supervisor_module._PosixTree(
        root,
        identity,
        authority=_FakePosixAuthority(
            root,
            identity,
            delegate=BrokenDiscovery(),
        ),
    )
    tree._released = True
    now = [60.0]
    monkeypatch.setattr(supervisor_module.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(
        supervisor_module.time,
        "sleep",
        lambda delay: now.__setitem__(0, now[0] + max(delay, 0.1)),
    )

    with pytest.raises(supervisor_module.AuthorityError, match="discovery|cleanup"):
        tree.close()

    assert root.calls[:1] == ["root-term"]
    assert now[0] >= 65.0


def test_persistent_poll_and_root_term_failures_remain_bounded(
    supervisor_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class BrokenRoot(_FakePosixRoot):
        def poll(self) -> int | None:
            raise RuntimeError("poll unavailable")

    root = BrokenRoot()
    identity = supervisor_module.ProcessIdentity(root.pid, 1.0)

    def signal_root(_force: bool) -> bool:
        raise OSError(errno.EPERM, "term denied")

    tree = supervisor_module._PosixTree(
        root,
        identity,
        authority=_FakePosixAuthority(
            root,
            identity,
            root_signal=signal_root,
        ),
    )
    tree._released = True
    now = [70.0]
    monkeypatch.setattr(supervisor_module.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(
        supervisor_module.time,
        "sleep",
        lambda delay: now.__setitem__(0, now[0] + max(delay, 0.1)),
    )

    with pytest.raises(supervisor_module.AuthorityError, match="poll|root|cleanup"):
        tree.close()

    assert root.calls
    assert now[0] < 75.0


def test_persistent_individual_signal_failure_is_bounded(
    supervisor_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    escaped = _AuthorityProcess(3651, 101.0)
    identity = supervisor_module.ProcessIdentity(escaped.pid, escaped.create_time())

    class PersistentAuthority:
        def scan(self) -> dict[Any, Any]:
            return {identity: escaped}

        def signal(self, target: Any, *, force: bool) -> bool:
            raise supervisor_module.AuthorityError("individual signal denied")

    root = _FakePosixRoot()
    root_identity = supervisor_module.ProcessIdentity(root.pid, 1.0)
    tree = supervisor_module._PosixTree(
        root,
        root_identity,
        authority=_FakePosixAuthority(
            root,
            root_identity,
            delegate=PersistentAuthority(),
        ),
    )
    tree._released = True
    now = [80.0]
    monkeypatch.setattr(supervisor_module.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(
        supervisor_module.time,
        "sleep",
        lambda delay: now.__setitem__(0, now[0] + max(delay, 0.1)),
    )

    with pytest.raises(supervisor_module.AuthorityError, match="cleanup"):
        tree.close()

    assert escaped.signals == []
    assert now[0] >= 85.0


def test_posix_kill_escalation_is_single_across_cleanup_reentry(
    supervisor_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    escaped = _AuthorityProcess(3661, 102.0)
    identity = supervisor_module.ProcessIdentity(escaped.pid, escaped.create_time())

    class PersistentAuthority:
        def scan(self) -> dict[Any, Any]:
            return {identity: escaped}

        def signal(self, target: Any, *, force: bool) -> bool:
            escaped.kill() if force else escaped.terminate()
            return True

    root = _FakePosixRoot()
    root_identity = supervisor_module.ProcessIdentity(root.pid, 1.0)
    tree = supervisor_module._PosixTree(
        root,
        root_identity,
        authority=_FakePosixAuthority(
            root,
            root_identity,
            delegate=PersistentAuthority(),
        ),
    )
    tree._released = True
    now = [90.0]
    monkeypatch.setattr(supervisor_module.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(
        supervisor_module.time,
        "sleep",
        lambda delay: now.__setitem__(0, now[0] + max(delay, 0.1)),
    )

    with pytest.raises(supervisor_module.AuthorityError):
        tree.cleanup(deadline=90.6, term_deadline=90.2)
    with pytest.raises(supervisor_module.AuthorityError):
        tree.close()

    assert escaped.signals.count("kill") == 1


def test_posix_cleanup_reaps_terminated_leader_before_convergence(
    supervisor_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class ReapSensitiveRoot(_FakePosixRoot):
        def __init__(self) -> None:
            super().__init__()
            self.poll_count = 0
            self.reaped = False

        def poll(self) -> int | None:
            self.poll_count += 1
            if self.poll_count == 1:
                return None
            self.reaped = True
            return -signal.SIGTERM

    root = ReapSensitiveRoot()
    identity = supervisor_module.ProcessIdentity(root.pid, 1.0)
    tree = supervisor_module._PosixTree(
        root,
        identity,
        authority=_FakePosixAuthority(root, identity),
    )
    now = [30.0]
    monkeypatch.setattr(supervisor_module.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(
        supervisor_module.time,
        "sleep",
        lambda delay: now.__setitem__(0, now[0] + max(delay, 0.1)),
    )
    tree.cleanup(deadline=31.0, term_deadline=30.5)

    assert root.calls == ["root-term"]
    assert root.poll_count >= 2


@pytest.mark.skipif(sys.platform == "win32", reason="real POSIX process-group test")
def test_posix_real_resistant_group_is_absent_before_natural_exit_is_returned(
    tmp_path: Path,
    process_tree_token: str,
) -> None:
    identities_path = tmp_path / "identities.json"
    sidecar = tmp_path / "supervisor-identity.json"
    identities: list[tuple[int, float]] = []
    supervisor_identity: tuple[int, float] | None = None
    primary_error: BaseException | None = None
    process = _start(
        _tree_command(
            identities_path,
            leader_exits=True,
            escape_descendant=True,
        ),
        token=process_tree_token,
        identity_sidecar=sidecar,
    )
    assert process.stdin is not None
    assert process.stdout is not None
    try:
        supervisor_identity = _read_supervisor_identity(sidecar)
        assert _readline_with_timeout(process.stdout).rstrip("\r\n") == READY_LINE
        _wait_for(
            lambda: len(_read_identities(identities_path)) == 2,
            message="real POSIX tree identities were not published",
        )
        identities = _read_identities(identities_path)
        records = json.loads(identities_path.read_text(encoding="utf-8"))
        assert records[0]["pgid"] != records[1]["pgid"]
        assert process.wait(timeout=10) == 6
        assert all(_identity_absent(identity) for identity in identities)
    except BaseException as error:
        primary_error = error
    finally:
        _finish_owned_supervisor(
            process,
            token=process_tree_token,
            supervisor_identity=supervisor_identity,
            primary_error=primary_error,
        )
        for identity in identities:
            _kill_exact(identity)


@pytest.mark.skipif(sys.platform == "win32", reason="requires real POSIX setsid")
def test_posix_real_setsid_escape_converges_after_forced_leader_exit_then_stop(
    tmp_path: Path,
    process_tree_token: str,
) -> None:
    records = _assert_real_forced_leader_stop_converges(
        tmp_path,
        process_tree_token,
        escape_descendant=True,
        expected_exit_code=0,
    )

    assert records[0]["pgid"] != records[1]["pgid"]


@pytest.mark.skipif(sys.platform == "win32", reason="requires real POSIX process group")
def test_posix_real_shared_group_converges_after_forced_leader_exit_then_stop(
    tmp_path: Path,
    process_tree_token: str,
) -> None:
    records = _assert_real_forced_leader_stop_converges(
        tmp_path,
        process_tree_token,
        escape_descendant=False,
        expected_exit_code=0,
    )

    assert records[0]["pgid"] == records[1]["pgid"]
