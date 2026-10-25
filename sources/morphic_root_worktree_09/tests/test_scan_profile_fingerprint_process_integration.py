from __future__ import annotations

import hashlib
import hmac
import json
import os
import queue
import subprocess
import sys
import threading
import time
import uuid
from multiprocessing.connection import Client, Listener
from pathlib import Path

import psutil
import pytest

from apps.web import scan_jobs as scan_jobs_module
from apps.web.contracts import Phase1ScanRequest
from apps.web.launcher import build_phase1_scan_launcher
from apps.web.main import create_app
from apps.web.scan_jobs import LocalScanJobService
from apps.web.workbench import current_scan_profile_pool_authority
from core.profile_sync import (
    SCAN_PROCESS_GATE_NONCE_ENV,
    SCAN_PROCESS_GATE_PROOF_ENV,
    SCAN_PROFILE_POOL_FINGERPRINT_ENV,
    build_scan_process_gate_proof,
)
from tests.test_web_shell import request


PRIVATE_SCAN_ENV_NAMES = (
    SCAN_PROFILE_POOL_FINGERPRINT_ENV,
    SCAN_PROCESS_GATE_NONCE_ENV,
    SCAN_PROCESS_GATE_PROOF_ENV,
)
PROFILE_AUTHORITY_ERROR = (
    "Scanprofil-Pool stimmt nicht mit der bestätigten Autorität überein."
)
_PRIVATE_VALUE_LENGTH = 64
_DIRECT_PROCESS_CLEANUP_TIMEOUT = 5.0
_DIRECT_PROCESS_TERM_GRACE = 1.0
_DIRECT_PROCESS_POLL_INTERVAL = 0.02


def _start_private_value_verifier(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> dict[str, object]:
    family = "AF_PIPE" if sys.platform == "win32" else "AF_UNIX"
    socket_path: Path | None = None
    if family == "AF_PIPE":
        address = rf"\\.\pipe\morphic-scan-proof-{uuid.uuid4().hex}"
    else:
        socket_path = tmp_path / "proof-verifier.sock"
        address = str(socket_path)
    authkey = os.urandom(32)
    comparison_key = os.urandom(32)
    listener = Listener(address, family=family, authkey=authkey)
    outcomes: queue.Queue[object] = queue.Queue(maxsize=1)

    def receive() -> None:
        try:
            with listener.accept() as connection:
                outcomes.put(connection.recv())
        except BaseException as exc:
            outcomes.put(exc)
        finally:
            listener.close()

    receiver = threading.Thread(target=receive, daemon=True)
    receiver.start()
    monkeypatch.setenv("MORPHIC_TEST_SCAN_VERIFIER_ADDRESS", address)
    monkeypatch.setenv("MORPHIC_TEST_SCAN_VERIFIER_FAMILY", family)
    monkeypatch.setenv("MORPHIC_TEST_SCAN_VERIFIER_AUTHKEY", authkey.hex())
    monkeypatch.setenv("MORPHIC_TEST_SCAN_VERIFIER_KEY", comparison_key.hex())
    return {
        "address": address,
        "authkey": authkey,
        "comparison_key": comparison_key,
        "family": family,
        "listener": listener,
        "outcomes": outcomes,
        "receiver": receiver,
        "socket_path": socket_path,
    }


def _receive_private_value_tokens(
    verifier: dict[str, object],
    *,
    timeout: float = 10.0,
) -> tuple[str, str, str]:
    outcomes = verifier["outcomes"]
    assert isinstance(outcomes, queue.Queue)
    result = outcomes.get(timeout=timeout)
    if isinstance(result, BaseException):
        raise result
    assert isinstance(result, tuple)
    assert len(result) == 3
    assert all(
        isinstance(token, str)
        and len(token) == 64
        and all(character in "0123456789abcdef" for character in token)
        for token in result
    )
    receiver = verifier["receiver"]
    assert isinstance(receiver, threading.Thread)
    receiver.join(timeout=5)
    assert not receiver.is_alive(), "private-value verifier exceeded its deadline"
    return result


def _close_private_value_verifier(verifier: dict[str, object]) -> None:
    receiver = verifier["receiver"]
    assert isinstance(receiver, threading.Thread)
    if receiver.is_alive():
        try:
            with Client(
                verifier["address"],
                family=verifier["family"],
                authkey=verifier["authkey"],
            ) as connection:
                connection.send(None)
        except (OSError, EOFError):
            pass
    receiver.join(timeout=5)
    verifier["listener"].close()
    assert not receiver.is_alive(), "private-value verifier cleanup exceeded its deadline"
    socket_path = verifier["socket_path"]
    if isinstance(socket_path, Path):
        socket_path.unlink(missing_ok=True)


def _private_values_absent_from_surfaces(
    surfaces: list[bytes],
    *,
    comparison_key: bytes,
    private_tokens: tuple[str, str, str],
) -> bool:
    expected = set(private_tokens)
    for surface in surfaces:
        for offset in range(len(surface) - _PRIVATE_VALUE_LENGTH + 1):
            candidate = surface[offset : offset + _PRIVATE_VALUE_LENGTH]
            token = hmac.new(comparison_key, candidate, hashlib.sha256).hexdigest()
            if token in expected:
                return False
    return True


def _request_payload(fingerprint: str, export_root: Path) -> dict[str, object]:
    return {
        "last_name": "Gate",
        "first_name": "Prozess",
        "birth_date": "09041966",
        "birth_place": "Augsburg",
        "focus": "deterministischer Integrationstest",
        "profile_level": 1,
        "top_n": 3,
        "scan_profile_pool_fingerprint": fingerprint,
        "consent_local": True,
        "consent_safety": True,
        "adaptive_limits": True,
        "notes": str(export_root.name),
    }


def _install_cli_probe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    hold_at_entry: bool = False,
) -> tuple[Path, Path, Path, Path]:
    probe_root = tmp_path / "private-cli-probe"
    probe_root.mkdir()
    entry_marker = probe_root / "entry.json"
    activation_marker = probe_root / "activation.json"
    subscan_marker = probe_root / "first-subscan.json"
    exit_marker = probe_root / "exit.json"
    hook_root = probe_root / "hook"
    hook_root.mkdir()
    (hook_root / "sitecustomize.py").write_text(
        """from __future__ import annotations
import atexit
import hashlib
import hmac
import json
import os
import subprocess
import sys
import time
from multiprocessing.connection import Client
from pathlib import Path

repository_root = os.environ["MORPHIC_TEST_SCAN_PROBE_REPOSITORY_ROOT"]
if repository_root not in sys.path:
    sys.path.insert(0, repository_root)

is_gate = Path(sys.argv[0]).name == "scan_process_gate.py"
if "top3-scan" in sys.argv and not is_gate:
    from core.profile_sync import (
        SCAN_PROCESS_GATE_NONCE_ENV,
        SCAN_PROCESS_GATE_PROOF_ENV,
        SCAN_PROFILE_POOL_FINGERPRINT_ENV,
    )

    private_keys = (
        SCAN_PROFILE_POOL_FINGERPRINT_ENV,
        SCAN_PROCESS_GATE_NONCE_ENV,
        SCAN_PROCESS_GATE_PROOF_ENV,
    )
    private_values = tuple(os.environ.get(key) for key in private_keys)
    scan_root = Path(os.environ["MORPHIC_TEST_SCAN_PROBE_SCAN_ROOT"])

    verifier_address = os.environ.pop("MORPHIC_TEST_SCAN_VERIFIER_ADDRESS", None)
    verifier_family = os.environ.pop("MORPHIC_TEST_SCAN_VERIFIER_FAMILY", None)
    verifier_authkey = os.environ.pop("MORPHIC_TEST_SCAN_VERIFIER_AUTHKEY", None)
    verifier_key = os.environ.pop("MORPHIC_TEST_SCAN_VERIFIER_KEY", None)
    if verifier_address is not None:
        assert verifier_family and verifier_authkey and verifier_key
        comparison_key = bytes.fromhex(verifier_key)
        private_tokens = tuple(
            hmac.new(
                comparison_key,
                value.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            for value in private_values
            if value is not None
        )
        with Client(
            verifier_address,
            family=verifier_family,
            authkey=bytes.fromhex(verifier_authkey),
        ) as connection:
            connection.send(private_tokens)

    def publish(path_key, payload):
        assert payload and all(type(value) is bool for value in payload.values())
        serialized = json.dumps(payload, sort_keys=True)
        assert all(not value or value not in serialized for value in private_values)
        Path(os.environ[path_key]).write_text(serialized, encoding="ascii")

    def private_values_absent_from_files():
        encoded = [
            value.encode("utf-8") for value in private_values if value is not None
        ]
        for path in scan_root.rglob("*"):
            if not path.is_file():
                continue
            try:
                content = path.read_bytes()
            except OSError:
                return False
            if any(value in content for value in encoded):
                return False
        return True

    def argv_excludes_private(argv):
        private_items = (*private_keys, *(value for value in private_values if value))
        return all(
            private_item not in str(argument)
            for private_item in private_items
            for argument in argv
        )

    def environment_excludes_private(environment):
        return all(key not in environment for key in private_keys) and all(
            private_value not in str(candidate)
            for private_value in private_values
            if private_value
            for candidate in environment.values()
        )

    publish(
        "MORPHIC_TEST_SCAN_PROBE_ENTRY",
        {
            "fingerprint_present": private_values[0] is not None,
            "nonce_present": private_values[1] is not None,
            "proof_present": private_values[2] is not None,
        },
    )
    entry_release_value = os.environ.pop(
        "MORPHIC_TEST_SCAN_PROBE_ENTRY_RELEASE",
        None,
    )
    if entry_release_value is not None:
        entry_release_path = Path(entry_release_value)
        entry_deadline = time.monotonic() + 10
        while not entry_release_path.exists():
            if time.monotonic() >= entry_deadline:
                raise RuntimeError("entry probe release exceeded its deadline")
            time.sleep(0.02)

    def publish_exit():
        publish(
            "MORPHIC_TEST_SCAN_PROBE_EXIT",
            {
                "fingerprint_absent": private_keys[0] not in os.environ,
                "nonce_absent": private_keys[1] not in os.environ,
                "proof_absent": private_keys[2] not in os.environ,
            },
        )

    atexit.register(publish_exit)

    from apps.cli.commands import scan as scan_module

    original_context = scan_module.resolve_operator_context

    def observed_context(*args, **kwargs):
        publish(
            \"MORPHIC_TEST_SCAN_PROBE_ACTIVATION\",
            {
                \"private_values_absent_from_files\": private_values_absent_from_files(),
                \"triplet_absent_from_argv\": argv_excludes_private(sys.argv),
                \"triplet_absent_from_parent_env\": environment_excludes_private(
                    os.environ
                ),
            },
        )
        return original_context(*args, **kwargs)

    original_run = scan_module.subprocess.run

    def controlled_run(command, *args, **kwargs):
        captured = list(command)
        if \"field\" not in captured or \"multiplex-scan\" not in captured:
            return original_run(command, *args, **kwargs)
        child_environment = kwargs.get(\"env\") or {}
        publish(
            \"MORPHIC_TEST_SCAN_PROBE_SUBSCAN\",
            {
                \"actual_cli_subscan\": (
                    captured[:3] == [sys.executable, \"-m\", \"apps.cli.main\"]
                    and \"field\" in captured
                    and \"multiplex-scan\" in captured
                ),
                \"private_values_absent_from_files\": private_values_absent_from_files(),
                \"triplet_absent_from_argv\": argv_excludes_private(captured),
                \"triplet_absent_from_child_env\": environment_excludes_private(
                    child_environment
                ),
                \"triplet_absent_from_parent_env\": environment_excludes_private(
                    os.environ
                ),
            },
        )
        release_path = Path(os.environ["MORPHIC_TEST_SCAN_PROBE_SUBSCAN_RELEASE"])
        deadline = time.monotonic() + 10
        while not release_path.exists():
            if time.monotonic() >= deadline:
                raise RuntimeError("subscan probe release exceeded its deadline")
            time.sleep(0.02)
        return subprocess.CompletedProcess(captured, 23, stdout=\"\", stderr=\"\")

    scan_module.resolve_operator_context = observed_context
    scan_module.subprocess.run = controlled_run
""",
        encoding="ascii",
    )
    inherited_pythonpath = os.environ.get("PYTHONPATH")
    pythonpath = str(hook_root)
    if inherited_pythonpath:
        pythonpath += os.pathsep + inherited_pythonpath
    monkeypatch.setenv("PYTHONPATH", pythonpath)
    monkeypatch.setenv(
        "MORPHIC_TEST_SCAN_PROBE_REPOSITORY_ROOT",
        str(Path(__file__).resolve().parents[1]),
    )
    monkeypatch.setenv("MORPHIC_TEST_SCAN_PROBE_SCAN_ROOT", str(tmp_path))
    monkeypatch.setenv("MORPHIC_TEST_SCAN_PROBE_ENTRY", str(entry_marker))
    monkeypatch.setenv(
        "MORPHIC_TEST_SCAN_PROBE_ACTIVATION",
        str(activation_marker),
    )
    monkeypatch.setenv(
        "MORPHIC_TEST_SCAN_PROBE_SUBSCAN",
        str(subscan_marker),
    )
    monkeypatch.setenv(
        "MORPHIC_TEST_SCAN_PROBE_SUBSCAN_RELEASE",
        str(probe_root / "first-subscan.release"),
    )
    monkeypatch.setenv("MORPHIC_TEST_SCAN_PROBE_EXIT", str(exit_marker))
    if hold_at_entry:
        monkeypatch.setenv(
            "MORPHIC_TEST_SCAN_PROBE_ENTRY_RELEASE",
            str(probe_root / "entry.release"),
        )
    return entry_marker, activation_marker, subscan_marker, exit_marker


def _wait_for_terminal(
    service: LocalScanJobService,
    job_id: str,
    *,
    timeout: float = 20.0,
) -> dict[str, object]:
    deadline = time.monotonic() + timeout
    snapshot = service.get(job_id)
    while snapshot["status"] in {"starting", "running"}:
        if time.monotonic() >= deadline:
            raise AssertionError(f"scan job {job_id} did not become terminal")
        time.sleep(0.05)
        snapshot = service.get(job_id)
    return snapshot


def _wait_for_path(path: Path, *, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while not path.exists():
        if time.monotonic() >= deadline:
            raise AssertionError(f"expected path was not published: {path}")
        time.sleep(0.02)


def _read_productive_process_identity(
    started_path: Path,
) -> tuple[int, float | None]:
    pid = int(started_path.read_text(encoding="ascii").strip())
    assert pid > 0
    try:
        create_time = psutil.Process(pid).create_time()
    except psutil.NoSuchProcess:
        create_time = None
    return pid, create_time


def _assert_process_identity_finished(
    pid: int,
    create_time: float | None,
) -> None:
    try:
        process = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return
    if create_time is not None and process.create_time() != create_time:
        return
    assert not process.is_running() or process.status() == psutil.STATUS_ZOMBIE


def _assert_runtime_renameable(runtime_root: Path) -> None:
    """Prove Windows lock release; on POSIX this only proves path renameability."""
    assert runtime_root.is_dir()
    moved = runtime_root.with_name(f"{runtime_root.name}.release-check")
    assert not moved.exists()
    runtime_root.rename(moved)
    moved.rename(runtime_root)


def _surface_file_contents(root: Path) -> list[bytes]:
    contents: list[bytes] = []
    for path in root.rglob("*"):
        if path.is_file():
            contents.append(path.read_bytes())
    return contents


def _assert_no_file_leak(root: Path, *values: str) -> None:
    encoded = [value.encode("utf-8") for value in values if value]
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        content = path.read_bytes()
        assert all(value not in content for value in encoded), path


def _assert_boolean_probe(path: Path, expected: dict[str, bool]) -> None:
    payload = json.loads(path.read_text(encoding="ascii"))
    assert payload == expected
    assert all(type(value) is bool for value in payload.values())


def _assert_job_process_finished(service: LocalScanJobService, job_id: str) -> None:
    job = service._jobs[job_id]
    process = job.process
    assert process.poll() is not None
    _assert_process_identity_finished(process.pid, job.process_create_time)


def _cleanup_job(
    service: LocalScanJobService,
    job_id: str | None,
    *,
    timeout: float = 10.0,
) -> None:
    if job_id is None:
        return
    outcomes: queue.Queue[BaseException | None] = queue.Queue(maxsize=1)

    def stop_known_job() -> None:
        try:
            snapshot = service.get(job_id)
            if snapshot["status"] in {
                "starting",
                "running",
                "authority_ambiguous",
                "rollback_failed",
            }:
                service.stop(job_id)
        except KeyError:
            pass
        except BaseException as exc:
            outcomes.put(exc)
            return
        outcomes.put(None)

    cleanup = threading.Thread(target=stop_known_job, daemon=True)
    cleanup.start()
    cleanup.join(timeout=timeout)
    assert not cleanup.is_alive(), "scan job cleanup exceeded its hard deadline"
    error = outcomes.get_nowait()
    if error is not None:
        raise error


def _terminate_process_tree(
    process: subprocess.Popen[str],
    process_token: str,
) -> list[BaseException]:
    failures: list[BaseException] = []
    deadline = time.monotonic() + _DIRECT_PROCESS_CLEANUP_TIMEOUT

    def root_active() -> bool:
        try:
            return process.poll() is None
        except (ProcessLookupError, psutil.NoSuchProcess):
            return False
        except BaseException as exc:
            failures.append(exc)
            return True

    def discover() -> dict[int, psutil.Process]:
        targets: dict[int, psutil.Process] = {}
        if root_active():
            try:
                root = psutil.Process(process.pid)
                for candidate in root.children(recursive=True):
                    targets[candidate.pid] = candidate
            except psutil.NoSuchProcess:
                pass
            except BaseException as exc:
                failures.append(exc)
        for candidate in psutil.process_iter(["pid", "status"]):
            try:
                if candidate.info["status"] == psutil.STATUS_ZOMBIE:
                    continue
                if (
                    candidate.environ().get("MORPHIC_TEST_DIRECT_PROCESS_TOKEN")
                    == process_token
                ):
                    targets[candidate.pid] = candidate
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue
            except BaseException as exc:
                failures.append(exc)
        targets.pop(os.getpid(), None)
        targets.pop(process.pid, None)
        return targets

    known = discover()
    if root_active():
        try:
            process.terminate()
        except (ProcessLookupError, psutil.NoSuchProcess):
            pass
        except BaseException as exc:
            failures.append(exc)

    term_sent: set[int] = set()
    term_deadline = min(
        deadline,
        time.monotonic()
        + min(_DIRECT_PROCESS_TERM_GRACE, _DIRECT_PROCESS_CLEANUP_TIMEOUT / 2),
    )
    empty_scans = 0
    while time.monotonic() < term_deadline:
        known.update(discover())
        for pid, target in list(known.items()):
            if pid in term_sent:
                continue
            try:
                target.terminate()
            except psutil.NoSuchProcess:
                pass
            except BaseException as exc:
                failures.append(exc)
            term_sent.add(pid)
        active = discover()
        known.update(active)
        empty_scans = empty_scans + 1 if not active and not root_active() else 0
        if empty_scans >= 2:
            break
        time.sleep(
            min(
                _DIRECT_PROCESS_POLL_INTERVAL,
                max(0.0, term_deadline - time.monotonic()),
            )
        )

    if root_active():
        try:
            process.kill()
        except (ProcessLookupError, psutil.NoSuchProcess):
            pass
        except BaseException as exc:
            failures.append(exc)
    kill_sent: set[int] = set()
    empty_scans = 0
    while time.monotonic() < deadline:
        active = discover()
        for pid, target in active.items():
            if pid in kill_sent:
                continue
            try:
                target.kill()
            except psutil.NoSuchProcess:
                pass
            except BaseException as exc:
                failures.append(exc)
            kill_sent.add(pid)
        empty_scans = empty_scans + 1 if not active and not root_active() else 0
        if empty_scans >= 2:
            break
        time.sleep(
            min(
                _DIRECT_PROCESS_POLL_INTERVAL,
                max(0.0, deadline - time.monotonic()),
            )
        )

    survivors = discover()
    if root_active():
        failures.append(RuntimeError(f"direct root survived cleanup: {process.pid}"))
    if survivors:
        survivor_ids = ",".join(str(pid) for pid in sorted(survivors))
        failures.append(
            RuntimeError(f"authorized processes survived cleanup: {survivor_ids}")
        )
    return failures


def _run_direct_cli_child(
    command: list[str],
    environment: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    process_token = uuid.uuid4().hex
    child_environment = {
        **environment,
        "MORPHIC_TEST_DIRECT_PROCESS_TOKEN": process_token,
    }
    process = subprocess.Popen(
        command,
        cwd=Path(__file__).resolve().parents[1],
        env=child_environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
        creationflags=(
            subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        ),
        start_new_session=sys.platform != "win32",
    )
    try:
        stdout, stderr = process.communicate(timeout=20)
    except subprocess.TimeoutExpired:
        primary_error = AssertionError("direct CLI child exceeded its hard deadline")
        cleanup_failures = _terminate_process_tree(process, process_token)
        if cleanup_failures:
            raise BaseExceptionGroup(
                "direct CLI failed and cleanup was incomplete",
                [primary_error, *cleanup_failures],
            )
        raise primary_error from None
    except BaseException as primary_error:
        cleanup_failures = _terminate_process_tree(process, process_token)
        if cleanup_failures:
            raise BaseExceptionGroup(
                "direct CLI failed and cleanup was incomplete",
                [primary_error, *cleanup_failures],
            )
        raise
    cleanup_failures = _terminate_process_tree(process, process_token)
    if cleanup_failures:
        raise BaseExceptionGroup(
            "direct CLI completed but cleanup was incomplete",
            [RuntimeError("direct CLI cleanup was incomplete"), *cleanup_failures],
        )
    assert process.poll() is not None
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


@pytest.mark.parametrize("status", ["authority_ambiguous", "rollback_failed"])
def test_cleanup_converges_nonterminal_authority_states(status: str) -> None:
    stopped: list[str] = []

    class Service:
        @staticmethod
        def get(job_id: str) -> dict[str, str]:
            assert job_id == "scan-cleanup-authority"
            return {"status": status}

        @staticmethod
        def stop(job_id: str) -> None:
            stopped.append(job_id)

    _cleanup_job(Service(), "scan-cleanup-authority")  # type: ignore[arg-type]

    assert stopped == ["scan-cleanup-authority"]


def test_direct_cli_process_authority_converges_orphaned_descendant(
    tmp_path: Path,
) -> None:
    child_pid_path = tmp_path / "direct-child.pid"
    script = (
        "import pathlib,subprocess,sys;"
        "child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'],"
        "stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);"
        f"pathlib.Path({str(child_pid_path)!r}).write_text(str(child.pid),encoding='ascii')"
    )
    child_pid: int | None = None
    try:
        completed = _run_direct_cli_child(
            [sys.executable, "-c", script],
            os.environ.copy(),
        )
        assert completed.returncode == 0
        child_pid = int(child_pid_path.read_text(encoding="ascii"))
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and psutil.pid_exists(child_pid):
            time.sleep(0.02)
        assert not psutil.pid_exists(child_pid)
    finally:
        if child_pid is not None:
            try:
                descendant = psutil.Process(child_pid)
                descendant.kill()
                descendant.wait(timeout=5)
            except psutil.NoSuchProcess:
                pass


def test_direct_cleanup_rescans_for_process_spawned_during_term(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []
    late_visible = {"value": False}

    class TokenProcess:
        def __init__(self, pid: int, label: str) -> None:
            self.pid = pid
            self.info = {"pid": pid, "status": "running"}
            self.label = label
            self.alive = True

        @staticmethod
        def environ() -> dict[str, str]:
            return {"MORPHIC_TEST_DIRECT_PROCESS_TOKEN": "direct-token"}

        def terminate(self) -> None:
            events.append(f"{self.label}-terminate")
            self.alive = False
            if self.label == "first":
                late_visible["value"] = True

        def kill(self) -> None:
            events.append(f"{self.label}-kill")
            self.alive = False

    first = TokenProcess(7101, "first")
    late = TokenProcess(7102, "late")

    class RootAuthority:
        pid = 7100

        @staticmethod
        def children(*, recursive: bool) -> list[TokenProcess]:
            return []

        @staticmethod
        def terminate() -> None:
            events.append("root-authority-terminate")

        @staticmethod
        def kill() -> None:
            events.append("root-authority-kill")

    class RootProcess:
        pid = 7100
        returncode: int | None = None

        def poll(self) -> int | None:
            return self.returncode

        def terminate(self) -> None:
            events.append("root-terminate")
            self.returncode = 1

        def kill(self) -> None:
            events.append("root-kill")
            self.returncode = 1

        def wait(self, timeout: float) -> int:
            self.returncode = 1
            return 1

    scans = {"count": 0}

    def process_iter(attrs: list[str]) -> list[TokenProcess]:
        scans["count"] += 1
        return [
            candidate
            for candidate in (first, late)
            if candidate.alive
            and (candidate is first or late_visible["value"])
        ]

    monkeypatch.setattr(psutil, "Process", lambda pid: RootAuthority())
    monkeypatch.setattr(psutil, "process_iter", process_iter)
    monkeypatch.setattr(psutil, "wait_procs", lambda processes, timeout: (processes, []))

    failures = _terminate_process_tree(
        RootProcess(),  # type: ignore[arg-type]
        "direct-token",
    )

    assert failures == []
    assert next(event for event in events if event.endswith("terminate")) == (
        "root-terminate"
    )
    assert "first-terminate" in events
    assert "late-terminate" in events
    assert scans["count"] >= 2


def test_direct_cleanup_has_one_deadline_and_reports_final_survivor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    waits: list[float] = []

    class Survivor:
        pid = 7201
        info = {"pid": 7201, "status": "running"}

        @staticmethod
        def environ() -> dict[str, str]:
            return {"MORPHIC_TEST_DIRECT_PROCESS_TOKEN": "direct-token"}

        @staticmethod
        def terminate() -> None:
            pass

        @staticmethod
        def kill() -> None:
            pass

    class ExitedRoot:
        pid = 7200

        @staticmethod
        def poll() -> int:
            return 1

        @staticmethod
        def wait(timeout: float) -> int:
            return 1

    monkeypatch.setattr(
        sys.modules[__name__],
        "_DIRECT_PROCESS_CLEANUP_TIMEOUT",
        0.1,
        raising=False,
    )
    monkeypatch.setattr(psutil, "process_iter", lambda attrs: [Survivor()])
    monkeypatch.setattr(
        psutil,
        "wait_procs",
        lambda processes, timeout: waits.append(timeout) or ([], processes),
    )

    failures = _terminate_process_tree(
        ExitedRoot(),  # type: ignore[arg-type]
        "direct-token",
    )

    assert sum(waits) <= 0.1
    assert any("authorized processes survived cleanup: 7201" in str(exc) for exc in failures)


def test_direct_cleanup_failure_preserves_timeout_as_primary_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cleanup_error = RuntimeError("authorized processes survived cleanup: 7301")

    class TimedOutProcess:
        pid = 7300
        returncode = None

        @staticmethod
        def communicate(timeout: float):
            raise subprocess.TimeoutExpired("direct-cli", timeout)

    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: TimedOutProcess())
    monkeypatch.setattr(
        sys.modules[__name__],
        "_terminate_process_tree",
        lambda process, token: [cleanup_error],
    )

    with pytest.raises(BaseExceptionGroup) as raised:
        _run_direct_cli_child([sys.executable, "-V"], os.environ.copy())

    assert isinstance(raised.value.exceptions[0], AssertionError)
    assert str(raised.value.exceptions[0]) == "direct CLI child exceeded its hard deadline"
    assert raised.value.exceptions[1] is cleanup_error


def test_gate_process_completion_uses_recorded_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class GateProcess:
        pid = 4242

        @staticmethod
        def poll() -> int:
            return 1

    class ReusedProcess:
        @staticmethod
        def create_time() -> float:
            return 2.0

        @staticmethod
        def is_running() -> bool:
            return True

        @staticmethod
        def status() -> str:
            return psutil.STATUS_RUNNING

    job = type(
        "Job",
        (),
        {"process": GateProcess(), "process_create_time": 1.0},
    )()
    service = type("Service", (), {"_jobs": {"scan-identity": job}})()
    monkeypatch.setattr(psutil, "Process", lambda pid: ReusedProcess())

    _assert_job_process_finished(service, "scan-identity")  # type: ignore[arg-type]


def test_web_start_binds_private_fingerprint_through_real_gate_to_cli(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authority = current_scan_profile_pool_authority(1)
    runtime_root = tmp_path / "runtime"
    export_root = tmp_path / "exports"
    service = LocalScanJobService(runtime_root / "web_jobs")
    app = create_app(
        runtime_dir=runtime_root,
        scan_jobs=service,
        report_roots=[export_root],
    )
    verifier = _start_private_value_verifier(tmp_path, monkeypatch)
    entry_marker, activation_marker, subscan_marker, exit_marker = _install_cli_probe(
        tmp_path,
        monkeypatch,
    )
    late_disclosure_marker = tmp_path / "private-cli-probe" / "late-disclosure.json"
    subscan_release = tmp_path / "private-cli-probe" / "first-subscan.release"
    monkeypatch.setenv("MORPHIC_RUNTIME_DIR", str(runtime_root))
    for private_name in PRIVATE_SCAN_ENV_NAMES:
        monkeypatch.delenv(private_name, raising=False)

    release_entered = threading.Event()
    release_allowed = threading.Event()
    original_durable_write = scan_jobs_module.durable_write_bytes

    def controlled_release(path: Path, data: bytes) -> None:
        candidate = Path(path)
        if candidate.parent == service.root and candidate.suffix == ".release":
            release_entered.set()
            assert release_allowed.wait(timeout=10)
        original_durable_write(candidate, data)

    monkeypatch.setattr(scan_jobs_module, "durable_write_bytes", controlled_release)
    job_id: str | None = None
    productive_pid: int | None = None
    productive_create_time: float | None = None
    responses: queue.Queue[object] = queue.Queue(maxsize=1)

    def start_request() -> None:
        try:
            responses.put(
                request(
                    app,
                    "POST",
                    "/api/scan/jobs",
                    _request_payload(authority.fingerprint, export_root),
                )
            )
        except BaseException as exc:
            responses.put(exc)

    worker = threading.Thread(target=start_request, daemon=True)
    worker.start()
    try:
        assert release_entered.wait(timeout=10)
        assert len(service._jobs) == 1
        job = next(iter(service._jobs.values()))
        job_id = job.job_id
        started_path = service._start_started_path(
            job.job_id,
            job.process_group_token,
        )
        assert not started_path.exists()
        assert not entry_marker.exists()
        assert not activation_marker.exists()
        assert not subscan_marker.exists()

        release_allowed.set()
        worker.join(timeout=20)
        assert not worker.is_alive(), "scan start request exceeded its hard deadline"
        started = responses.get_nowait()
        if isinstance(started, BaseException):
            raise started

        assert started.status_code == 200, started.text
        assert job_id == started.json()["job_id"]
        private_tokens = _receive_private_value_tokens(verifier)
        _wait_for_path(subscan_marker)
        productive_pid, productive_create_time = _read_productive_process_identity(
            started_path
        )
        subscan_release.write_bytes(b"release\n")
        terminal = _wait_for_terminal(service, job_id)
        status_response = request(app, "GET", f"/api/scan/jobs/{job_id}")
        sync_response = request(app, "POST", f"/api/scan/jobs/{job_id}/sync-trace")

        assert status_response.status_code == 200
        assert sync_response.status_code == 200
        assert terminal["status"] == "failed"
        assert terminal["returncode"] != 0
        assert started_path.exists()
        assert entry_marker.exists()
        assert activation_marker.exists()
        assert subscan_marker.exists()
        assert exit_marker.exists()
        _assert_boolean_probe(
            entry_marker,
            {
                "fingerprint_present": True,
                "nonce_present": True,
                "proof_present": True,
            },
        )
        _assert_boolean_probe(
            activation_marker,
            {
                "private_values_absent_from_files": True,
                "triplet_absent_from_argv": True,
                "triplet_absent_from_parent_env": True,
            },
        )
        _assert_boolean_probe(
            subscan_marker,
            {
                "actual_cli_subscan": True,
                "private_values_absent_from_files": True,
                "triplet_absent_from_argv": True,
                "triplet_absent_from_child_env": True,
                "triplet_absent_from_parent_env": True,
            },
        )
        _assert_boolean_probe(
            exit_marker,
            {
                "fingerprint_absent": True,
                "nonce_absent": True,
                "proof_absent": True,
            },
        )
        run_trace = app.state.workbench_store.get_run_trace(job_id)
        public_values = (
            started.text,
            status_response.text,
            sync_response.text,
            json.dumps(terminal, sort_keys=True),
            json.dumps(run_trace, sort_keys=True),
        )
        for private_value in (authority.fingerprint, *PRIVATE_SCAN_ENV_NAMES):
            assert all(private_value not in value for value in public_values)
        assert all(
            private_name not in terminal["command"]
            for private_name in PRIVATE_SCAN_ENV_NAMES
        )
        assert authority.fingerprint not in terminal["command"]

        job = service._jobs[job_id]
        result_path = service._start_result_path(job_id, job.process_group_token)
        persisted_surfaces = (
            service._start_release_path(job_id, job.process_group_token),
            started_path,
            result_path,
            service._state_path(job_id),
            service._stdout_path(job_id),
            service._stderr_path(job_id),
            app.state.workbench_store._path_for("run_traces"),
            entry_marker,
            activation_marker,
            subscan_marker,
            exit_marker,
        )
        missing_surfaces = [str(path) for path in persisted_surfaces if not path.exists()]
        assert not missing_surfaces, missing_surfaces
        assert list((runtime_root / "start-operations").glob("*.json"))
        late_surfaces = [
            value.encode("utf-8") for value in public_values
        ] + _surface_file_contents(tmp_path)
        late_disclosure_marker.write_text(
            json.dumps(
                {
                    "private_values_absent_from_late_surfaces": (
                        _private_values_absent_from_surfaces(
                            late_surfaces,
                            comparison_key=verifier["comparison_key"],
                            private_tokens=private_tokens,
                        )
                    )
                },
                sort_keys=True,
            ),
            encoding="ascii",
        )
        _assert_boolean_probe(
            late_disclosure_marker,
            {"private_values_absent_from_late_surfaces": True},
        )
        _assert_no_file_leak(
            tmp_path,
            authority.fingerprint,
            *PRIVATE_SCAN_ENV_NAMES,
        )
        _assert_job_process_finished(service, job_id)
    finally:
        release_allowed.set()
        subscan_release.write_bytes(b"release\n")
        if job_id is None and len(service._jobs) == 1:
            job_id = next(iter(service._jobs))
        try:
            _cleanup_job(service, job_id)
        finally:
            worker.join(timeout=20)
            _close_private_value_verifier(verifier)
        assert not worker.is_alive(), (
            "scan start request remained alive after its cleanup deadline"
        )
        if productive_pid is not None:
            _assert_process_identity_finished(
                productive_pid,
                productive_create_time,
            )
        if runtime_root.exists():
            _assert_runtime_renameable(runtime_root)


@pytest.mark.parametrize("fingerprint_mode", ["mismatch", "missing"])
def test_process_bound_cli_rejects_untrusted_fingerprint_before_activation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fingerprint_mode: str,
) -> None:
    authority = current_scan_profile_pool_authority(1)
    runtime_root = tmp_path / "runtime"
    export_root = tmp_path / "exports"
    service = LocalScanJobService(runtime_root / "web_jobs")
    entry_marker, activation_marker, subscan_marker, exit_marker = _install_cli_probe(
        tmp_path,
        monkeypatch,
        hold_at_entry=True,
    )
    entry_release = tmp_path / "private-cli-probe" / "entry.release"
    monkeypatch.setenv("MORPHIC_RUNTIME_DIR", str(runtime_root))
    for private_name in PRIVATE_SCAN_ENV_NAMES:
        monkeypatch.delenv(private_name, raising=False)
    request_model = Phase1ScanRequest.model_validate(
        _request_payload(authority.fingerprint, export_root)
    )
    command = build_phase1_scan_launcher(
        request_model,
        executes=True,
        export_path=str(export_root),
    )["command"]
    mismatch = "0" * 64 if authority.fingerprint != "0" * 64 else "1" * 64
    environment = (
        {SCAN_PROFILE_POOL_FINGERPRINT_ENV: mismatch}
        if fingerprint_mode == "mismatch"
        else None
    )
    job_id: str | None = None
    productive_pid: int | None = None
    productive_create_time: float | None = None

    try:
        started = service.start(command, env_overrides=environment)
        job_id = str(started["job_id"])
        job = service._jobs[job_id]
        started_path = service._start_started_path(job_id, job.process_group_token)
        _wait_for_path(entry_marker)
        productive_pid, productive_create_time = _read_productive_process_identity(
            started_path
        )
        assert productive_create_time is not None
        entry_release.write_bytes(b"release\n")
        terminal = _wait_for_terminal(service, job_id)

        assert terminal["status"] == "failed"
        assert terminal["returncode"] not in {None, 0}
        assert terminal["stderr_tail"].strip() == PROFILE_AUTHORITY_ERROR
        assert "Traceback" not in terminal["stderr_tail"]
        assert entry_marker.exists()
        assert exit_marker.exists()
        assert not activation_marker.exists()
        assert not subscan_marker.exists()
        assert not export_root.exists()
        _assert_boolean_probe(
            entry_marker,
            {
                "fingerprint_present": fingerprint_mode == "mismatch",
                "nonce_present": True,
                "proof_present": True,
            },
        )
        _assert_boolean_probe(
            exit_marker,
            {
                "fingerprint_absent": True,
                "nonce_absent": True,
                "proof_absent": True,
            },
        )
        assert authority.fingerprint not in terminal["stdout_tail"]
        assert authority.fingerprint not in terminal["stderr_tail"]
        assert mismatch not in terminal["stdout_tail"]
        assert mismatch not in terminal["stderr_tail"]
        for private_name in PRIVATE_SCAN_ENV_NAMES:
            assert private_name not in terminal["stdout_tail"]
            assert private_name not in terminal["stderr_tail"]
        assert authority.fingerprint not in command
        assert mismatch not in command
        _assert_no_file_leak(
            tmp_path,
            authority.fingerprint,
            mismatch,
            *PRIVATE_SCAN_ENV_NAMES,
        )
        _assert_job_process_finished(service, job_id)
    finally:
        entry_release.write_bytes(b"release\n")
        _cleanup_job(service, job_id)
        if productive_pid is not None:
            _assert_process_identity_finished(
                productive_pid,
                productive_create_time,
            )
        if runtime_root.exists():
            _assert_runtime_renameable(runtime_root)


@pytest.mark.parametrize(
    "proof_mode",
    ["malformed-nonce", "malformed-proof", "partial-proof", "tampered-proof"],
)
def test_direct_real_cli_rejects_invalid_process_proof_before_side_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    proof_mode: str,
) -> None:
    authority = current_scan_profile_pool_authority(1)
    export_root = tmp_path / "exports"
    entry_marker, activation_marker, subscan_marker, exit_marker = _install_cli_probe(
        tmp_path,
        monkeypatch,
    )
    for private_name in PRIVATE_SCAN_ENV_NAMES:
        monkeypatch.delenv(private_name, raising=False)
    monkeypatch.setenv("MORPHIC_RUNTIME_DIR", str(tmp_path / "runtime"))
    request_model = Phase1ScanRequest.model_validate(
        _request_payload(authority.fingerprint, export_root)
    )
    command = build_phase1_scan_launcher(
        request_model,
        executes=True,
        export_path=str(export_root),
    )["command"]

    nonce: str | None = "a" * 64
    proof: str | None = build_scan_process_gate_proof(
        nonce,
        authority.fingerprint,
    )
    if proof_mode == "malformed-nonce":
        nonce = "malformed-nonce"
    elif proof_mode == "malformed-proof":
        proof = "malformed-proof"
    elif proof_mode == "partial-proof":
        proof = None
    else:
        assert proof_mode == "tampered-proof"
        proof = ("0" if proof[0] != "0" else "1") + proof[1:]

    environment = os.environ.copy()
    for private_name in PRIVATE_SCAN_ENV_NAMES:
        environment.pop(private_name, None)
    environment[SCAN_PROFILE_POOL_FINGERPRINT_ENV] = authority.fingerprint
    if nonce is not None:
        environment[SCAN_PROCESS_GATE_NONCE_ENV] = nonce
    if proof is not None:
        environment[SCAN_PROCESS_GATE_PROOF_ENV] = proof

    completed = _run_direct_cli_child(command, environment)

    assert completed.returncode not in {None, 0}
    assert completed.stderr.strip() == PROFILE_AUTHORITY_ERROR
    assert "Traceback" not in completed.stderr
    assert not activation_marker.exists()
    assert not subscan_marker.exists()
    assert not export_root.exists()
    _assert_boolean_probe(
        entry_marker,
        {
            "fingerprint_present": True,
            "nonce_present": True,
            "proof_present": proof is not None,
        },
    )
    _assert_boolean_probe(
        exit_marker,
        {
            "fingerprint_absent": True,
            "nonce_absent": True,
            "proof_absent": True,
        },
    )
    combined_output = completed.stdout + completed.stderr
    for private_value in (
        authority.fingerprint,
        nonce,
        proof,
        *PRIVATE_SCAN_ENV_NAMES,
    ):
        if private_value:
            assert private_value not in combined_output
    assert authority.fingerprint not in command
    assert all(private_name not in command for private_name in PRIVATE_SCAN_ENV_NAMES)
    _assert_no_file_leak(
        tmp_path,
        authority.fingerprint,
        nonce or "",
        proof or "",
        *PRIVATE_SCAN_ENV_NAMES,
    )
