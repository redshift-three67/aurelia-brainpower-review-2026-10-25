from __future__ import annotations

from collections import Counter, defaultdict
from html.parser import HTMLParser
import json
import math
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import time
from typing import Callable

import psutil
import pytest


ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "apps" / "web" / "static" / "index.html"
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"
RENDER_JS = ROOT / "apps" / "web" / "static" / "workbench-render.js"
BROWSER_DIR = ROOT / "tests" / "browser"
TREE_TOKEN_ENV = "MORPHIC_BROWSER_PROCESS_TREE_TOKEN"


def _read_published_process_identities(path: Path) -> list[tuple[int, float]]:
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
        return [(int(item["pid"]), float(item["create_time"])) for item in records]
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return []


def _published_identity_absent(identity: tuple[int, float]) -> bool:
    pid, create_time = identity
    try:
        process = psutil.Process(pid)
        if float(process.create_time()) != create_time:
            return True
        return not process.is_running() or process.status() == psutil.STATUS_ZOMBIE
    except (ProcessLookupError, psutil.NoSuchProcess):
        return True


def _wait_for_published_supervisor_identity(
    path: Path, timeout: float = 5
) -> tuple[int, float]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(record, dict) or set(record) != {"pid", "create_time"}:
                raise ValueError("malformed supervisor identity")
            pid = record["pid"]
            create_time = record["create_time"]
            if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
                raise ValueError("malformed supervisor pid")
            if (
                isinstance(create_time, bool)
                or not isinstance(create_time, (int, float))
                or not math.isfinite(float(create_time))
                or float(create_time) <= 0
            ):
                raise ValueError("malformed supervisor create time")
            return pid, float(create_time)
        except (
            FileNotFoundError,
            PermissionError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ):
            time.sleep(0.01)
    raise AssertionError(f"supervisor identity was not published within {timeout}s: {path}")


def _wait_for_published_tree_token(path: Path, timeout: float = 5) -> str:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            token = path.read_text(encoding="ascii")
            if re.fullmatch(r"[0-9a-f]{32}", token) is None:
                raise ValueError("malformed tree token")
            return token
        except (FileNotFoundError, UnicodeError, ValueError):
            time.sleep(0.01)
    raise AssertionError(f"tree token was not published within {timeout}s: {path}")


def _capture_harness_process_baseline() -> tuple[str, set[tuple[int, float]]]:
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


def _scan_harness_token_identities(
    token: str | None,
    *,
    owner: str,
    baseline: set[tuple[int, float]],
    known: set[tuple[int, float]],
) -> list[tuple[int, float]]:
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
            if candidate_owner is None and identity not in known:
                continue
            if process.environ().get(TREE_TOKEN_ENV) == token:
                identities.append(identity)
        except (ProcessLookupError, psutil.NoSuchProcess):
            continue
        except (PermissionError, psutil.AccessDenied) as error:
            if identity in baseline and identity not in known:
                continue
            raise AssertionError(
                f"same-owner harness token authority is ambiguous: {identity}"
            ) from error
    return identities


def _stop_harness_identity(
    identity: tuple[int, float],
    *,
    remaining: float,
) -> None:
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
        process = psutil.Process(pid)
        if float(process.create_time()) != create_time:
            return
        kill_remaining = deadline - time.monotonic()
        if kill_remaining <= 0:
            return
        process.kill()
        process.wait(timeout=kill_remaining)
    except (ProcessLookupError, psutil.NoSuchProcess):
        return


class CleanupAmbiguityError(BaseExceptionGroup):
    """Process absence is unproven, so forensic state must remain intact."""


def _finish_real_node_harness(
    node_process: subprocess.Popen[str] | None,
    *,
    supervisor_identity: tuple[int, float] | None,
    token: str | None,
    owner: str,
    baseline: set[tuple[int, float]],
    primary_error: BaseException | None,
    known_identities: list[tuple[int, float]] | None = None,
    cleanup_timeout: float = 8.0,
    monotonic: Callable[[], float] = time.monotonic,
    scanner: Callable[[str], list[tuple[int, float]]] | None = None,
    stopper: Callable[..., None] = _stop_harness_identity,
    sleeper: Callable[[float], None] = time.sleep,
) -> None:
    total_timeout = max(0.0, cleanup_timeout)
    deadline = monotonic() + total_timeout
    fallback_reserve = min(1.0, total_timeout / 2)
    cleanup_errors: list[BaseException] = []
    deadline_recorded = False
    known = set(known_identities or [])
    seen = set(known)

    def remaining() -> float:
        return max(0.0, deadline - monotonic())

    def record_deadline() -> None:
        nonlocal deadline_recorded
        if deadline_recorded:
            return
        deadline_recorded = True
        cleanup_errors.append(AssertionError("real harness cleanup deadline expired"))

    def scan(value: str) -> list[tuple[int, float]]:
        if scanner is not None:
            return scanner(value)
        identities = _scan_harness_token_identities(
            value,
            owner=owner,
            baseline=baseline,
            known=known,
        )
        known.update(identities)
        return identities

    if node_process is not None and remaining() > 0:
        try:
            if node_process.poll() is None:
                node_process.kill()
                parent_wait = max(0.0, remaining() - fallback_reserve)
                if parent_wait > 0:
                    node_process.wait(timeout=parent_wait)
        except BaseException as error:
            cleanup_errors.append(error)

    empty_scans = 0
    if token is None:
        cleanup_errors.append(AssertionError("real harness tree token is unavailable"))
    while token is not None and remaining() > 0 and empty_scans < 2:
        try:
            active = scan(token)
        except BaseException as error:
            cleanup_errors.append(error)
            break
        if remaining() <= 0:
            record_deadline()
            break
        if not active:
            empty_scans += 1
            if empty_scans < 2:
                sleeper(min(0.01, remaining()))
            continue
        empty_scans = 0
        for identity in active:
            seen.add(identity)
            stop_remaining = remaining()
            if stop_remaining <= 0:
                record_deadline()
                break
            try:
                stopper(identity, remaining=stop_remaining)
            except BaseException as error:
                cleanup_errors.append(error)

    if empty_scans < 2 and remaining() <= 0:
        record_deadline()
    if supervisor_identity is not None and remaining() > 0:
        try:
            stopper(supervisor_identity, remaining=remaining())
        except BaseException as error:
            cleanup_errors.append(error)

    for identity in [supervisor_identity, *seen]:
        if identity is None:
            continue
        while remaining() > 0:
            try:
                if _published_identity_absent(identity):
                    break
            except BaseException as error:
                cleanup_errors.append(error)
                break
            sleeper(min(0.01, remaining()))
        else:
            record_deadline()

    if remaining() <= 0:
        record_deadline()
    if primary_error is not None:
        if cleanup_errors:
            cleanup_group = BaseExceptionGroup(
                "real harness cleanup failures", cleanup_errors
            )
            raise CleanupAmbiguityError(
                "real harness primary and cleanup failures",
                [primary_error, cleanup_group],
            ) from primary_error
        raise primary_error
    if cleanup_errors:
        raise CleanupAmbiguityError("real harness cleanup failures", cleanup_errors)


def _record_forensic_runtime_evidence(
    runtime_root: Path,
    error: BaseException,
) -> None:
    if not runtime_root.is_dir():
        raise AssertionError(
            f"forensic runtime was not preserved before outer teardown: {runtime_root}"
        )
    error.add_note(f"forensic runtime observed before outer teardown: {runtime_root}")


def _finish_real_node_harness_in_sandbox(
    finalizer: Callable[[], None],
    *,
    sandbox_root: Path,
    runtime_root: Path | None,
    primary_error: BaseException | None,
) -> None:
    def preserve(ambiguity: CleanupAmbiguityError) -> None:
        evidence_errors: list[BaseException] = []
        candidates = (
            [runtime_root]
            if runtime_root is not None
            else list(sandbox_root.glob("morphic-browser-*"))
        )
        if not candidates:
            evidence_errors.append(
                AssertionError("cleanup ambiguity produced no observable forensic runtime")
            )
        for candidate in candidates:
            try:
                _record_forensic_runtime_evidence(candidate, ambiguity)
            except BaseException as evidence_error:
                evidence_errors.append(evidence_error)
        if evidence_errors:
            raise CleanupAmbiguityError(
                "real harness cleanup ambiguity and forensic evidence failures",
                [ambiguity, *evidence_errors],
            ) from ambiguity
        raise ambiguity

    try:
        finalizer()
    except CleanupAmbiguityError as ambiguity:
        return preserve(ambiguity)
    except BaseException as error:
        if error is not primary_error:
            return preserve(
                CleanupAmbiguityError(
                    "real harness finalization ended without proven process absence",
                    [error],
                )
            )
        try:
            shutil.rmtree(sandbox_root)
        except FileNotFoundError:
            pass
        except BaseException as teardown_error:
            raise BaseExceptionGroup(
                "real harness primary and outer teardown failures",
                [error, teardown_error],
            ) from error
        raise
    try:
        shutil.rmtree(sandbox_root)
    except FileNotFoundError:
        pass
    except BaseException as teardown_error:
        raise BaseExceptionGroup(
            "real harness outer teardown failures",
            [teardown_error],
        ) from teardown_error


def test_supervisor_identity_reader_uses_published_pair_without_pid_lookup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sidecar = tmp_path / "supervisor-identity.json"
    sidecar.write_text(
        json.dumps({"pid": os.getpid(), "create_time": 1.25}),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        psutil,
        "Process",
        lambda _pid: (_ for _ in ()).throw(AssertionError("numeric PID lookup used")),
    )

    assert _wait_for_published_supervisor_identity(sidecar) == (os.getpid(), 1.25)


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

    assert _wait_for_published_supervisor_identity(sidecar) == (os.getpid(), 1.25)
    assert attempts == 1


def test_harness_token_scan_skips_unowned_candidate_but_not_known_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    identity = (54321, 1.25)

    class UnownedProcess:
        info = {"pid": identity[0], "create_time": identity[1], "username": None}

        def environ(self) -> dict[str, str]:
            raise psutil.AccessDenied(identity[0])

    monkeypatch.setattr(psutil, "process_iter", lambda _attrs: [UnownedProcess()])

    assert _scan_harness_token_identities(
        "0" * 32,
        owner="test-owner",
        baseline=set(),
        known=set(),
    ) == []
    with pytest.raises(AssertionError, match="ambiguous"):
        _scan_harness_token_identities(
            "0" * 32,
            owner="test-owner",
            baseline=set(),
            known={identity},
        )


@pytest.mark.parametrize(
    "record",
    (
        {},
        {"pid": 1},
        {"pid": "1", "create_time": 1.0},
        {"pid": 1, "create_time": "1.0"},
        {"pid": 0, "create_time": 1.0},
        {"pid": 1, "create_time": 0.0},
        {"pid": 1, "create_time": float("inf")},
        {"pid": 1, "create_time": float("nan")},
        {"pid": 1, "create_time": 1.0, "token": "leak"},
    ),
)
def test_supervisor_identity_reader_rejects_malformed_sidecar(
    tmp_path: Path,
    record: dict[str, object],
) -> None:
    sidecar = tmp_path / "supervisor-identity.json"
    sidecar.write_text(json.dumps(record), encoding="utf-8")

    with pytest.raises(AssertionError, match="identity"):
        _wait_for_published_supervisor_identity(sidecar, timeout=0.03)


def test_supervisor_identity_reader_fails_closed_when_sidecar_is_missing(
    tmp_path: Path,
) -> None:
    with pytest.raises(AssertionError, match="identity"):
        _wait_for_published_supervisor_identity(
            tmp_path / "missing-supervisor-identity.json",
            timeout=0.03,
        )


def test_real_harness_finalizer_bounds_continuous_token_descendants_and_orders_primary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Clock:
        def __init__(self) -> None:
            self.now = 20.0

        def monotonic(self) -> float:
            return self.now

        def advance(self, value: float) -> None:
            self.now += value

    class NodeProcess:
        def __init__(self) -> None:
            self.returncode: int | None = None
            self.kill_calls = 0

        def poll(self) -> int | None:
            return self.returncode

        def kill(self) -> None:
            self.kill_calls += 1
            self.returncode = -9

        def wait(self, timeout: float) -> int:
            assert timeout > 0
            return -9

    clock = Clock()
    node = NodeProcess()
    primary = subprocess.TimeoutExpired(["node"], 1)
    scan_count = 0
    stop_budgets: list[float] = []

    def scan(_token: str) -> list[tuple[int, float]]:
        nonlocal scan_count
        scan_count += 1
        clock.advance(0.3)
        return [(55000 + scan_count, float(scan_count))]

    def stop(_identity: tuple[int, float], *, remaining: float) -> None:
        assert remaining > 0
        stop_budgets.append(remaining)
        clock.advance(min(0.2, remaining))

    monkeypatch.setattr(
        sys.modules[__name__],
        "_published_identity_absent",
        lambda _identity: (_ for _ in ()).throw(
            AssertionError("absence check started after deadline")
        ),
    )

    with pytest.raises(BaseExceptionGroup) as caught:
        _finish_real_node_harness(
            node,  # type: ignore[arg-type]
            supervisor_identity=(55999, 9.0),
            token="a" * 32,
            owner="test-owner",
            baseline=set(),
            primary_error=primary,
            cleanup_timeout=1.5,
            monotonic=clock.monotonic,
            scanner=scan,
            stopper=stop,
        )

    assert caught.value.exceptions[0] is primary
    cleanup_group = caught.value.exceptions[1]
    assert isinstance(cleanup_group, BaseExceptionGroup)
    assert any("deadline" in str(error).lower() for error in cleanup_group.exceptions)
    assert node.kill_calls == 1
    assert scan_count == 3
    assert all(remaining > 0 for remaining in stop_budgets)
    assert clock.now == pytest.approx(21.5)


def test_real_harness_sandbox_preserves_forensics_on_cleanup_ambiguity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sandbox_root = tmp_path / "outer-sandbox"
    runtime_root = sandbox_root / "morphic-browser-forensic"
    runtime_root.mkdir(parents=True)
    primary = subprocess.TimeoutExpired(["node"], 1)
    cleanup = AssertionError("controlled cleanup ambiguity")
    cleanup_group = BaseExceptionGroup("real harness cleanup failures", [cleanup])
    finalizer_error = CleanupAmbiguityError(
        "real harness primary and cleanup failures",
        [primary, cleanup_group],
    )
    observations: list[tuple[Path, bool, bool, BaseException]] = []

    def observe(path: Path, error: BaseException) -> None:
        observations.append((path, path.exists(), sandbox_root.exists(), error))

    monkeypatch.setattr(
        sys.modules[__name__],
        "_record_forensic_runtime_evidence",
        observe,
    )

    with pytest.raises(BaseExceptionGroup) as caught:
        _finish_real_node_harness_in_sandbox(
            lambda: (_ for _ in ()).throw(finalizer_error),
            sandbox_root=sandbox_root,
            runtime_root=runtime_root,
            primary_error=primary,
        )

    assert caught.value is finalizer_error
    assert caught.value.exceptions == (primary, cleanup_group)
    assert observations == [(runtime_root, True, True, finalizer_error)]
    assert sandbox_root.exists()
    assert runtime_root.exists()


def test_real_harness_cleanup_failure_has_typed_ambiguity() -> None:
    with pytest.raises(CleanupAmbiguityError) as caught:
        _finish_real_node_harness(
            None,
            supervisor_identity=None,
            token=None,
            owner="test-owner",
            baseline=set(),
            primary_error=None,
            cleanup_timeout=0,
        )

    assert isinstance(caught.value, CleanupAmbiguityError)


class OptionHelpParser(HTMLParser):
    VOID_TAGS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[tuple[str, dict[str, str | None]]] = []
        self.id_counts: Counter[str] = Counter()
        self.text_parts: dict[str, list[str]] = defaultdict(list)
        self._tags: list[str] = []
        self._open_ids: list[tuple[str, int]] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        self.elements.append((tag, attributes))
        element_id = attributes.get("id")
        if element_id:
            self.id_counts[element_id] += 1
        if tag not in self.VOID_TAGS:
            self._tags.append(tag)
            if element_id:
                self._open_ids.append((element_id, len(self._tags)))

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        self.elements.append((tag, attributes))
        element_id = attributes.get("id")
        if element_id:
            self.id_counts[element_id] += 1

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if not text:
            return
        for element_id, _depth in self._open_ids:
            self.text_parts[element_id].append(text)

    def handle_endtag(self, tag: str) -> None:
        self._open_ids = [
            item for item in self._open_ids if item[1] != len(self._tags)
        ]
        if self._tags:
            self._tags.pop()

    def by_id(self, element_id: str) -> dict[str, str | None]:
        for _tag, attributes in self.elements:
            if attributes.get("id") == element_id:
                return attributes
        raise AssertionError(f"missing element id: {element_id}")

    def by_name(self, name: str) -> dict[str, str | None]:
        for _tag, attributes in self.elements:
            if attributes.get("name") == name:
                return attributes
        raise AssertionError(f"missing element name: {name}")

    def text_by_id(self, element_id: str) -> str:
        return " ".join(self.text_parts[element_id])


HELP_LINKS = {
    "focus-history-help": [
        ("id", "focus-history-consent"),
        ("id", "clear-focus-history"),
    ],
    "main-symptom-help": [("name", "main_symptom")],
    "client-context-help": [
        ("name", "birth_time"),
        ("name", "email"),
        ("name", "notes"),
        ("id", "context-persistence-consent"),
        ("id", "save-client-context-button"),
    ],
    "group-draft-help": [
        ("id", "group-draft-label"),
        ("id", "group-draft-members"),
        ("id", "group-members-consent"),
        ("id", "group-persistence-consent"),
        ("id", "group-analysis-consent"),
        ("id", "save-group-draft-button"),
        ("id", "group-erasure-dry-run-button"),
        ("id", "delete-group-draft-button"),
        ("id", "group-delete-confirmation"),
    ],
    "group-consent-help": [
        ("id", "group-identity-first-name"),
        ("id", "group-identity-last-name"),
        ("id", "group-identity-birth-date"),
        ("id", "group-identity-birth-place"),
        ("id", "group-identity-retention-days"),
        ("id", "group-identity-persistence-consent"),
        ("id", "register-group-identity-button"),
        ("id", "group-consent-client-id"),
        ("id", "group-consent-valid-until"),
        ("id", "group-consent-confirmation"),
        ("id", "enable-group-consent-button"),
        ("id", "revoke-group-consent-button"),
    ],
    "group-policy-help": [
        ("id", "group-analysis-strength"),
        ("id", "save-group-analysis-policy-button"),
    ],
    "group-activation-help": [
        ("id", "group-scan-activation-enabled"),
        ("id", "group-scan-draft-id"),
    ],
    "reference-image-help": [
        ("id", "image-file-input"),
        ("id", "image-path-input"),
    ],
    "planetary-vector-help": [
        ("name", "planetary_vector_enabled"),
        ("name", "planet_type"),
    ],
    "profile-template-help": [("id", "profile-template-choices")],
    "entropy-mode-help": [("id", "entropy-mode-choices")],
    "adaptive-limits-help": [("name", "adaptive_limits")],
    "workbench-mode-help": [("id", "workbench-mode")],
    "emf-help": [("id", "realtime-calibration")],
    "harmonization-intention-help": [("name", "intention")],
    "harmonization-frequency-help": [
        ("name", "target_frequency"),
        ("id", "solfeggio-base-choices"),
    ],
    "harmonization-cycle-help": [
        ("name", "pulse_seconds"),
        ("name", "pause_seconds"),
    ],
    "harmonization-duration-help": [("name", "duration_factor")],
    "harmonization-hardware-help": [
        ("name", "use_cpu"),
        ("name", "use_gpu"),
        ("name", "use_ram"),
        ("name", "use_websocket"),
        ("name", "use_driver_layer"),
    ],
    "template-persistence-help": [
        ("id", "template-sensitive-consent"),
        ("id", "save-template-button"),
    ],
}


def _parser() -> OptionHelpParser:
    parser = OptionHelpParser()
    parser.feed(INDEX_HTML.read_text(encoding="utf-8"))
    return parser


def test_static_option_controls_have_complete_linked_explanations() -> None:
    parser = _parser()
    markers = (
        "Zweck:",
        "Standard:",
        "Auswirkung:",
        "Keine Auswirkung:",
        "Datenschutz-/Hardwaregrenze:",
    )

    for help_id, controls in HELP_LINKS.items():
        assert parser.id_counts[help_id] == 1
        help_attributes = parser.by_id(help_id)
        assert "hidden" not in help_attributes
        assert help_attributes.get("aria-hidden") != "true"
        help_text = parser.text_by_id(help_id)
        for marker in markers:
            assert marker in help_text, f"{help_id}: missing {marker}"

        for kind, value in controls:
            attributes = (
                parser.by_id(value) if kind == "id" else parser.by_name(value)
            )
            described_by = str(attributes.get("aria-describedby") or "").split()
            assert help_id in described_by, f"{kind}={value} not linked to {help_id}"


def test_local_options_explain_storage_retention_deletion_and_scan_effect() -> None:
    parser = _parser()
    for help_id in (
        "focus-history-help",
        "client-context-help",
        "group-draft-help",
        "group-consent-help",
        "group-policy-help",
        "group-activation-help",
        "template-persistence-help",
    ):
        text = parser.text_by_id(help_id)
        for marker in (
            "Speicherort:",
            "Aufbewahrung:",
            "Löschweg:",
            "Aktueller Scan:",
        ):
            assert marker in text, f"{help_id}: missing {marker}"

    draft_text = parser.text_by_id("group-draft-help")
    assert "DPAPI" in draft_text
    assert "an dieses Windows-Benutzerkonto gebundene Verschlüsselung" in draft_text

    policy_text = parser.text_by_id("group-policy-help")
    assert "Kill-Switch" in policy_text
    assert "serverseitiger Not-Aus-Schalter" in policy_text
    assert "Policy-Kandidat" in policy_text
    assert "nur vorgemerkter Vorschlag" in policy_text
    assert "0 = keine Gruppenwirkung" in policy_text
    assert "1 = volle angeforderte Gruppenwirkung" in policy_text


def test_local_ai_opt_in_is_removed_only_from_template_save_payload() -> None:
    source = APP_JS.read_text(encoding="utf-8")
    template_handler = source.split(
        'const saveTemplate = $("#save-template-button")', 1
    )[1].split('const newCase = $("#new-case-button")', 1)[0]

    fresh_payload = "const payload = formScanPayload();"
    remove_local_ai = "delete payload.local_ai_enabled;"
    save_template = "MorphicWorkbenchApi.saveTemplate"
    assert fresh_payload in template_handler
    assert remove_local_ai in template_handler
    assert save_template in template_handler
    assert template_handler.index(fresh_payload) < template_handler.index(remove_local_ai)
    assert template_handler.index(remove_local_ai) < template_handler.index(save_template)


def test_future_optional_features_are_explained_without_premature_controls() -> None:
    parser = _parser()
    local_ai = parser.text_by_id("local-ai-help")
    profile_context = parser.text_by_id("profile-context-help")

    local_ai_controls = [
        attributes
        for _, attributes in parser.elements
        if attributes.get("name") == "local_ai_enabled"
    ]
    assert len(local_ai_controls) == 1
    local_ai_control = local_ai_controls[0]
    assert local_ai_control.get("id") == "local-ai-enabled"
    assert local_ai_control.get("type") == "checkbox"
    assert local_ai_control.get("aria-describedby") == "local-ai-help"
    assert "checked" not in local_ai_control
    assert "Standard: aus" in local_ai
    assert "Loopback" in local_ai
    assert "regelbasierter Fallback" in local_ai
    assert "Profilpool" in local_ai
    assert "nicht gespeichert" in local_ai
    assert "derzeit nicht auswählbar" in profile_context
    assert "Gate 12" in profile_context

    assert not any(
        attributes.get("name") == "profile_context"
        for _, attributes in parser.elements
    )


def test_generated_choice_cards_have_separate_names_and_descriptions() -> None:
    script = f"""
const fs = require("fs");
const vm = require("vm");

function element(tagName) {{
  return {{
    tagName,
    id: "",
    className: "",
    dataset: {{}},
    children: [],
    attributes: {{}},
    _text: "",
    appendChild(child) {{ this.children.push(child); }},
    replaceChildren() {{ this.children = []; this._text = ""; }},
    setAttribute(name, value) {{ this.attributes[name] = String(value); }},
    getAttribute(name) {{ return this.attributes[name] ?? null; }},
    addEventListener() {{}},
    querySelectorAll(selector) {{
      if (selector === ".choice-card") {{
        return this.children.filter((child) => child.className.includes("choice-card"));
      }}
      return [];
    }},
    get textContent() {{
      return this._text + this.children.map((child) => child.textContent).join("");
    }},
    set textContent(value) {{ this._text = String(value); this.children = []; }},
  }};
}}

const container = element("div");
container.id = "profile-template-choices";
container.setAttribute("aria-describedby", "profile-template-help");
const help = element("p");
help.id = "profile-template-help";

function findById(node, id) {{
  if (node.id === id) return node;
  for (const child of node.children || []) {{
    const found = findById(child, id);
    if (found) return found;
  }}
  return null;
}}

global.window = {{}};
global.document = {{
  querySelector(selector) {{
    return selector === "#profile-template-choices" ? container : null;
  }},
  createElement(tagName) {{ return element(tagName); }},
  getElementById(id) {{ return findById(container, id) || findById(help, id); }},
}};

vm.runInThisContext(fs.readFileSync({str(RENDER_JS)!r}, "utf8"));
window.MorphicWorkbenchRender.renderChoiceCards(
  "#profile-template-choices",
  [
    {{value: "phase1-default", label: "Phase-1 Standard", hint: "Neutraler Ausgangspunkt"}},
    {{value: "personal-balanced", label: "Persoenlich ausgewogen", hint: "Breitere Gewichtung"}},
  ],
  "phase1-default",
  () => {{}},
);

const ids = new Set();
for (const card of container.children) {{
  const labelledBy = card.getAttribute("aria-labelledby");
  const describedBy = String(card.getAttribute("aria-describedby") || "")
    .split(/\\s+/)
    .filter(Boolean);
  if (!labelledBy) throw new Error("missing aria-labelledby");
  if (!describedBy.includes("profile-template-help")) throw new Error("missing group help");
  if (!describedBy.some((id) => id.endsWith("-hint"))) throw new Error("missing option hint");
  if (!document.getElementById(labelledBy)) throw new Error("broken accessible label");
  for (const id of [labelledBy, ...describedBy]) {{
    if (!document.getElementById(id)) throw new Error(`broken reference: ${{id}}`);
    if (ids.has(id) && id !== "profile-template-help") throw new Error(`duplicate id: ${{id}}`);
    ids.add(id);
  }}
}}
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_maximum_harmonization_duration_requires_confirmation_before_start() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    app = APP_JS.read_text(encoding="utf-8")
    form = html.split('<form id="harmonization-form"', 1)[1].split(
        "</form>", 1
    )[0]
    assert 'id="harmonization-max-duration-confirmation"' in form
    assert "441 Minuten" in form
    assert 'id="harmonization-confirmation-state"' in html

    start = app.split("async function startHarmonizationJob", 1)[1].split(
        "async function pollHarmonizationJob", 1
    )[0]
    assert "body.duration_factor === 21" in start
    assert "harmonization-max-duration-confirmation" in start
    assert start.index("harmonization-max-duration-confirmation") < start.index(
        "MorphicWorkbenchApi.startHarmonization"
    )


def test_adaptive_limits_copy_matches_detail_limit_behavior() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")

    assert "Adaptive Limits begrenzen den Detailumfang" in html
    assert "Screening-Umfang selbst" not in html
    assert "Profile werden vollstaendig durchsucht" not in html




def test_browser_runner_drops_parent_morphic_configuration() -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const path = require("path");
process.env.MORPHIC_API_KEY = "production-secret";
process.env.MORPHIC_TENANT_ID = "production-tenant";
process.env.mOrPhIc_AdMiN_bOoTsTrAp_NoNcE = "mixed-case-secret";
const runner = require({str(runner_path)!r});
const root = path.resolve("isolated-runtime");
const env = runner.buildServerEnv(root, 43123, "health-token");
const testEnv = runner.buildTestEnv("http://127.0.0.1:43123", null);

if (env.MORPHIC_API_KEY !== undefined) throw new Error("API key leaked");
if (env.MORPHIC_TENANT_ID === "production-tenant") throw new Error("tenant leaked");
if (testEnv.MORPHIC_API_KEY !== undefined) throw new Error("API key leaked to Playwright");
if (testEnv.MORPHIC_TENANT_ID !== undefined) throw new Error("tenant leaked to Playwright");
for (const candidate of [env, testEnv]) {{
  if (Object.keys(candidate).some(name => name.toUpperCase().startsWith("MORPHIC_") &&
      !["MORPHIC_BROWSER_PORT", "MORPHIC_BROWSER_RUNTIME_ROOT", "MORPHIC_BROWSER_HEALTH_TOKEN",
        "MORPHIC_RUNTIME_DIR", "MORPHIC_HARMONIZATION_JOBS_DIR", "MORPHIC_PARALLEL_EXPORT_ROOT",
        "MORPHIC_OPERATOR_ID", "MORPHIC_TENANT_ID", "MORPHIC_GROUP_ANALYSIS_ENABLED",
        "MORPHIC_ADMIN_CATALOG_ENABLED"].includes(name))) {{
    throw new Error("mixed-case MORPHIC variable leaked");
  }}
}}
if (env.MORPHIC_RUNTIME_DIR !== path.join(root, "runtime")) throw new Error("runtime not isolated");
if (env.MORPHIC_HARMONIZATION_JOBS_DIR !== path.join(root, "harmonization-jobs")) {{
  throw new Error("harmonization jobs not isolated");
}}
if (env.MORPHIC_BROWSER_HEALTH_TOKEN !== "health-token") throw new Error("health token missing");
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_browser_runner_preserves_runtime_when_any_tree_cleanup_fails() -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const fs = require("fs");
const os = require("os");
const path = require("path");
const runner = require({str(runner_path)!r});
const root = fs.mkdtempSync(path.join(os.tmpdir(), "morphic-cleanup-contract-"));
let attempts = 0;

runner.cleanupGroup([{{pid: 1}}, {{pid: 2}}], root, async child => {{
  attempts += 1;
  if (child.pid === 1) throw new Error("synthetic stop failure");
}}).then(() => {{
  throw new Error("cleanup unexpectedly succeeded");
}}).catch(error => {{
  if (attempts !== 2) throw new Error(`only ${{attempts}} trees were stopped`);
  if (!fs.existsSync(root)) throw new Error("runtime removed after failed cleanup");
  fs.rmSync(root, {{recursive: true, force: true}});
  if (!(error instanceof AggregateError)) throw error;
}});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


































def test_browser_runner_supervisor_wraps_server_and_playwright_with_isolated_authority() -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});
const ready = '{{"event":"ready","schema_version":1}}\\n';
const calls = [];
const supervisors = [];
let healthObserved = false;

function supervisor(label) {{
  const child = new EventEmitter();
  child.exitCode = null;
  child.signalCode = null;
  child.stdout = new EventEmitter();
  child.stderr = new EventEmitter();
  child.ready = new EventEmitter();
  child.stopWrites = [];
  child.stdin = {{
    destroyed: false,
    writableEnded: false,
    write(value, callback) {{
      child.stopWrites.push(String(value));
      if (String(value) === "stop\\n" && child.exitCode === null) {{
        setImmediate(() => {{
          child.exitCode = 0;
          child.emit("exit", 0);
          child.emit("close", 0);
        }});
      }}
      callback?.();
      return true;
    }},
  }};
  child.stdio = [child.stdin, child.stdout, child.stderr, child.ready];
  child.label = label;
  return child;
}}

function injectedSpawn(command, args, options) {{
  const child = supervisor(calls.length === 0 ? "server" : "playwright");
  if (child.label === "playwright") {{
    child.stdout = null;
    child.stderr = null;
    child.stdio = [child.stdin, null, null, child.ready];
  }}
  calls.push({{command, args, options}});
  supervisors.push(child);
  setImmediate(() => {{
    child.ready.emit("data", Buffer.from(ready));
    child.ready.emit("end");
    if (child.label === "server") child.stdout.emit("data", Buffer.from("server-log\\n"));
    if (child.label === "playwright") {{
      setImmediate(() => {{
        child.exitCode = 0;
        child.emit("exit", 0);
        child.emit("close", 0);
      }});
    }}
  }});
  return child;
}}

async function main() {{
  await runner.runGroup(null, [], {{
    spawn: injectedSpawn,
    freePort: async () => 43171,
    waitForHealth: async (_url, _token, _server, logs) => {{
      healthObserved = true;
      if (logs.text !== "server-log\\n") {{
        throw new Error(`server framing garbled logs: ${{JSON.stringify(logs.text)}}`);
      }}
    }},
  }});

  if (!healthObserved) throw new Error("health check was not reached");
  if (calls.length !== 2) throw new Error(`spawn count was ${{calls.length}}`);
  const [serverCall, playwrightCall] = calls;
  if (serverCall.command !== playwrightCall.command) throw new Error("supervisors used different Python owners");
  for (const call of calls) {{
    if (!String(call.args[0]).endsWith("process_tree_supervisor.py")) {{
      throw new Error(`wrong supervisor: ${{JSON.stringify(call.args)}}`);
    }}
    if (JSON.stringify(call.args.slice(1, 4)) !== JSON.stringify(["--ready-fd", "3", "--"])) {{
      throw new Error(`supervisor readiness arguments were ${{JSON.stringify(call.args)}}`);
    }}
    if (call.options.detached !== false) throw new Error("supervisor was detached");
  }}
  if (JSON.stringify(serverCall.options.stdio) !== JSON.stringify(["pipe", "pipe", "pipe", "pipe"])) {{
    throw new Error(`server supervisor stdio was ${{JSON.stringify(serverCall.options.stdio)}}`);
  }}
  if (JSON.stringify(playwrightCall.options.stdio) !== JSON.stringify(["pipe", "inherit", "inherit", "pipe"])) {{
    throw new Error(`Playwright supervisor stdio was ${{JSON.stringify(playwrightCall.options.stdio)}}`);
  }}
  if (!serverCall.args.some(value => String(value).endsWith("isolated_server.py"))) {{
    throw new Error("server productive command missing");
  }}
  if (!playwrightCall.args.some(value => String(value).includes("@playwright"))) {{
    throw new Error("Playwright productive command missing");
  }}
  const tokens = calls.map(call => call.options.env.MORPHIC_BROWSER_PROCESS_TREE_TOKEN);
  if (!tokens.every(token => /^[0-9a-f]{{32}}$/.test(token)) || tokens[0] === tokens[1]) {{
    throw new Error(`tree authorities were not isolated: ${{JSON.stringify(tokens)}}`);
  }}
  for (const [call, token] of calls.map((call, index) => [call, tokens[index]])) {{
    if (call.args.some(value => String(value).includes(token))) throw new Error("tree token leaked to argv");
  }}
  if (JSON.stringify(runner.runnerState()).includes(tokens[0])
      || JSON.stringify(runner.runnerState()).includes(tokens[1])) {{
    throw new Error("tree token leaked to runner state");
  }}
  if (supervisors[0].stopWrites.join("") !== "stop\\n") {{
    throw new Error(`server stop writes were ${{JSON.stringify(supervisors[0].stopWrites)}}`);
  }}
  if (runner.runnerState().activeSupervisorCount !== 0) throw new Error("supervisors remained tracked");
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_browser_runner_supervisor_readiness_is_exact_bounded_and_preserves_output() -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});
const ready = '{{"event":"ready","schema_version":1}}\\n';

function child() {{
  const value = new EventEmitter();
  value.exitCode = null;
  value.signalCode = null;
  value.stdout = new EventEmitter();
  value.stderr = new EventEmitter();
  value.ready = new EventEmitter();
  value.stdin = {{write(_value, callback) {{ callback?.(); return true; }}}};
  value.stdio = [value.stdin, value.stdout, value.stderr, value.ready];
  return value;
}}

async function rejectedReadiness(label, payload, timeoutMs = 50) {{
  const value = child();
  const supervised = runner.spawnSupervised("productive", [label], {{
    env: {{}},
    readinessTimeoutMs: timeoutMs,
  }}, {{spawn: () => value}});
  const pending = runner.waitForSupervisorReady(supervised);
  if (payload !== null) setImmediate(() => {{
    value.ready.emit("data", Buffer.from(payload));
    value.ready.emit("end");
  }});
  let actual = null;
  try {{ await pending; }} catch (error) {{ actual = error; }}
  if (!actual || !String(actual.message).toLowerCase().includes("readiness")) {{
    throw actual || new Error(`${{label}} readiness unexpectedly resolved`);
  }}
  if (label === "oversized") {{
    value.ready.emit("data", Buffer.alloc(1024 * 1024, 120));
    if (value.ready.listenerCount("data") !== 0) {{
      throw new Error("oversized readiness kept buffering protocol bytes");
    }}
  }}
  value.exitCode = 1;
  value.emit("exit", 1);
  value.emit("close", 1);
  if (value.listenerCount("error") !== 0 || value.listenerCount("exit") !== 0
      || value.listenerCount("close") !== 0 || value.ready.listenerCount("data") !== 0
      || value.ready.listenerCount("end") !== 0) {{
    throw new Error(`${{label}} retained protocol listeners`);
  }}
}}

async function main() {{
  if (typeof runner.spawnSupervised !== "function"
      || typeof runner.waitForSupervisorReady !== "function") {{
    throw new Error("supervisor readiness API is not behavior-testable");
  }}
  await rejectedReadiness("malformed", "not-json\\n");
  await rejectedReadiness("token-bearing", '{{"event":"ready","schema_version":1,"token":"secret"}}\\n');
  await rejectedReadiness("padded-duplicate", ready + " " + ready);
  await rejectedReadiness("oversized", "x".repeat(1025));
  await rejectedReadiness("timeout", null, 10);

  const forwarded = [];
  const value = child();
  const supervised = runner.spawnSupervised("productive", [], {{
    env: {{}},
    onStdout: chunk => forwarded.push(chunk),
    readinessTimeoutMs: 50,
  }}, {{spawn: () => value}});
  const pending = runner.waitForSupervisorReady(supervised);
  value.ready.emit("data", Buffer.from(ready));
  await pending;
  value.ready.emit("end");
  const productive = Buffer.from("productive-out\\n" + "x".repeat(4096));
  value.stdout.emit("data", productive);
  if (forwarded.length !== 1 || forwarded[0] !== productive) {{
    throw new Error("productive stdout was parsed or re-encoded");
  }}
  const naturalExit = runner.waitForSupervisorExit(value, 50, "natural productive result");
  value.exitCode = 7;
  value.emit("exit", 7);
  value.emit("close", 7);
  if (await naturalExit !== 7) throw new Error("productive result code was not propagated");

  const duplicate = child();
  const duplicateSupervisor = runner.spawnSupervised("productive", [], {{env: {{}}}}, {{
    spawn: () => duplicate,
  }});
  duplicate.ready.emit("data", Buffer.from(ready));
  await runner.waitForSupervisorReady(duplicateSupervisor);
  duplicate.ready.emit("data", Buffer.from(ready));
  const duplicateError = await runner.waitForSupervisorExit(
    duplicateSupervisor,
    50,
    "delayed duplicate readiness",
  ).then(() => null, error => error);
  if (!String(duplicateError?.message || "").toLowerCase().includes("readiness")) {{
    throw duplicateError || new Error("delayed duplicate readiness was accepted");
  }}
  duplicate.exitCode = 1;
  duplicate.emit("exit", 1);
  duplicate.emit("close", 1);
  if (runner.runnerState().activeSupervisorCount !== 0) throw new Error("readiness test retained supervisor");
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_browser_runner_delayed_duplicate_during_cleanup_preserves_runtime(
    tmp_path: Path,
) -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    runtime_root = tmp_path / "delayed-duplicate-runtime"
    script = f"""
const fs = require("fs");
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});
const ready = Buffer.from('{{"event":"ready","schema_version":1}}\\n');
const runtimeRoot = {json.dumps(str(runtime_root))};
const supervisors = [];
let spawnCalls = 0;

function supervisor(label) {{
  const value = new EventEmitter();
  value.label = label;
  value.exitCode = null;
  value.signalCode = null;
  value.stdout = new EventEmitter();
  value.stderr = new EventEmitter();
  value.ready = new EventEmitter();
  value.stdin = new EventEmitter();
  value.stdin.destroyed = false;
  value.stdin.destroy = () => {{ value.stdin.destroyed = true; }};
  value.stdin.write = (_data, callback) => {{
    callback?.();
    if (label === "server") {{
      setImmediate(() => value.ready.emit("data", ready));
    }}
    return true;
  }};
  value.stdio = [value.stdin, value.stdout, value.stderr, value.ready];
  supervisors.push(value);
  setImmediate(() => {{
    value.ready.emit("data", ready);
    if (label === "playwright") value.ready.emit("end");
  }});
  return value;
}}

async function main() {{
  fs.mkdirSync(runtimeRoot, {{recursive: true}});
  let actual = null;
  try {{
    actual = await runner.runGroup(null, [], {{
      freePort: async () => 0,
      spawn() {{
        spawnCalls += 1;
        return supervisor(spawnCalls === 1 ? "server" : "playwright");
      }},
      waitForHealth: async () => {{}},
      waitForExit: async () => 0,
      stopTimeoutMs: 100,
    }}).then(() => null, error => error);
    await new Promise(resolve => setImmediate(resolve));
    if (!(actual instanceof AggregateError)) {{
      throw actual || new Error("delayed duplicate cleanup unexpectedly succeeded");
    }}
    const messages = JSON.stringify(actual, Object.getOwnPropertyNames(actual));
    if (!messages.toLowerCase().includes("readiness")) {{
      throw actual;
    }}
    if (!fs.existsSync(runtimeRoot)) {{
      throw new Error("delayed duplicate cleanup removed forensic runtime");
    }}
  }} finally {{
    for (const value of supervisors) {{
      if (value.exitCode === null) {{
        value.exitCode = 1;
        value.emit("exit", 1);
        value.emit("close", 1);
      }}
    }}
    fs.rmSync(runtimeRoot, {{recursive: true, force: true}});
  }}
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_browser_runner_supervisor_readiness_stream_errors_are_bounded_and_listener_free() -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});

function child() {{
  const value = new EventEmitter();
  value.exitCode = null;
  value.signalCode = null;
  value.stdout = new EventEmitter();
  value.stderr = new EventEmitter();
  value.ready = new EventEmitter();
  value.ready.removals = {{data: 0, end: 0, error: 0}};
  const removeListener = value.ready.removeListener.bind(value.ready);
  value.ready.removeListener = (event, listener) => {{
    if (Object.hasOwn(value.ready.removals, event)) value.ready.removals[event] += 1;
    return removeListener(event, listener);
  }};
  value.ready.destroy = () => {{
    value.ready.destroyed = true;
    setImmediate(() => value.ready.emit("close"));
  }};
  value.stdin = {{write(_data, callback) {{ callback?.(); return true; }}}};
  value.stdio = [value.stdin, value.stdout, value.stderr, value.ready];
  return value;
}}

async function scenario(label, emitBeforeWait) {{
  const expected = new Error(label);
  const value = child();
  const supervised = runner.spawnSupervised("productive", [], {{
    env: {{}},
    readinessTimeoutMs: 100,
  }}, {{spawn: () => value}});
  const readyClosed = new Promise(resolve => value.ready.once("close", resolve));
  let pending;
  if (emitBeforeWait) {{
    value.ready.emit("error", expected);
    pending = runner.waitForSupervisorReady(supervised);
  }} else {{
    pending = runner.waitForSupervisorReady(supervised);
    setImmediate(() => value.ready.emit("error", expected));
  }}
  const result = await Promise.race([
    pending.then(() => null, error => error),
    new Promise(resolve => setTimeout(() => resolve(null), 50)),
  ]);
  if (!String(result?.message || "").toLowerCase().includes("readiness")) {{
    throw result || new Error(`${{label}} stream error was not bounded`);
  }}
  if (result.cause !== expected) throw new Error(`${{label}} stream cause was not retained`);
  if (value.ready.listenerCount("data") !== 0 || value.ready.listenerCount("end") !== 0
      || value.ready.listenerCount("error") !== 1 || value.ready.destroyed !== true) {{
    throw new Error(`${{label}} protocol listeners remained after stream error`);
  }}
  value.ready.emit("error", new Error(`${{label}}-after-rejection`));
  await readyClosed;
  if (value.ready.listenerCount("error") !== 0 || value.ready.listenerCount("close") !== 0) {{
    throw new Error(`${{label}} protocol guard remained after fd close`);
  }}
  if (runner.runnerState().activeSupervisorCount !== 1) {{
    throw new Error(`${{label}} tracker released before child close`);
  }}
  value.emit("close", null);
  if (JSON.stringify(value.ready.removals) !== JSON.stringify({{data: 1, end: 1, error: 1}})) {{
    throw new Error(`${{label}} protocol cleanup was ${{JSON.stringify(value.ready.removals)}}`);
  }}
  if (runner.runnerState().activeSupervisorCount !== 0) {{
    throw new Error(`${{label}} tracker remained after close`);
  }}
}}

(async () => {{
  await scenario("stream-error-before-wait", true);
  await scenario("stream-error-after-wait", false);
}})().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_browser_runner_real_readiness_pipe_failure_breaks_writer_without_leak() -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const {{spawn}} = require("child_process");
const runner = require({str(runner_path)!r});
const malicious = `
const fs = require("fs");
const mode = process.argv[1];
const ready = fs.createWriteStream(null, {{fd: 3, autoClose: false}});
ready.on("error", () => process.exit(23));
ready.write(mode === "malformed" ? Buffer.from("not-json\\n") : Buffer.alloc(2048, 120));
const block = Buffer.alloc(65536, 121);
function flood() {{
  while (ready.write(block)) {{}}
  ready.once("drain", flood);
}}
flood();
setInterval(() => {{}}, 1000);
`;

async function scenario(mode) {{
  let child;
  try {{
    const supervised = runner.spawnSupervised("ignored", [], {{
      env: {{}},
      readinessTimeoutMs: 200,
    }}, {{
      spawn() {{
        child = spawn(process.execPath, ["-e", malicious, mode], {{
          stdio: ["pipe", "pipe", "pipe", "pipe"],
          windowsHide: true,
        }});
        return child;
      }},
      stopTimeoutMs: 500,
    }});
    const readiness = await runner.waitForSupervisorReady(supervised).catch(error => error);
    if (!String(readiness?.message || "").toLowerCase().includes("readiness")) {{
      throw readiness || new Error(`${{mode}} readiness did not reject`);
    }}
    const stopError = await runner.stopSupervisor(supervised).then(() => null, error => error);
    const stopFailures = [];
    const visit = error => {{
      if (error instanceof AggregateError) error.errors.forEach(visit);
      else if (error) stopFailures.push(error);
    }};
    visit(stopError);
    if (stopError) {{
      if (!stopFailures.some(error => ["EPIPE", "ERR_STREAM_DESTROYED"].includes(error.code))) {{
        throw stopError;
      }}
      if (!stopFailures.some(error => String(error.message).includes("Supervisor exited with code"))) {{
        throw stopError;
      }}
      if (!stopFailures.some(error => String(error.message).toLowerCase().includes("readiness"))) {{
        throw stopError;
      }}
    }}
    if (!(child.exitCode > 0)) throw new Error(`${{mode}} writer exit was ${{child.exitCode}}`);
    if (runner.runnerState().activeSupervisorCount !== 0) {{
      throw new Error(`${{mode}} retained real supervisor tracker`);
    }}
  }} finally {{
    if (child?.exitCode === null) {{
      const closed = new Promise(resolve => child.once("close", resolve));
      child.kill();
      await closed;
    }}
  }}
}}

(async () => {{
  await scenario("malformed");
  await scenario("oversized");
}})().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_browser_runner_supervisor_settles_on_close_after_unicode_stream_drainage() -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});
const ready = Buffer.from('{{"event":"ready","schema_version":1}}\\n');

function child() {{
  const value = new EventEmitter();
  value.exitCode = null;
  value.signalCode = null;
  value.stdout = new EventEmitter();
  value.stderr = new EventEmitter();
  value.ready = new EventEmitter();
  value.stdin = {{write(_data, callback) {{ callback?.(); return true; }}}};
  value.stdio = [value.stdin, value.stdout, value.stderr, value.ready];
  return value;
}}

async function main() {{
  const value = child();
  const stdoutChunks = [];
  const stderrChunks = [];
  const supervised = runner.spawnSupervised("productive", [], {{
    env: {{}},
    onStdout: chunk => stdoutChunks.push(chunk),
    onStderr: chunk => stderrChunks.push(chunk),
    readinessTimeoutMs: 100,
  }}, {{spawn: () => value}});
  value.ready.emit("data", ready.subarray(0, 7));
  value.ready.emit("data", ready.subarray(7));
  value.ready.emit("end");
  await runner.waitForSupervisorReady(supervised);

  const stdout = Buffer.from("vor-€-nach\\n", "utf8");
  const stderr = Buffer.from("fehler-漢字\\n", "utf8");
  let settled = false;
  const completion = runner.waitForSupervisorExit(
    supervised,
    100,
    "fast natural supervisor",
  ).then(code => {{ settled = true; return code; }});
  value.stdout.emit("data", stdout.subarray(0, 5));
  value.stderr.emit("data", stderr.subarray(0, 9));
  value.exitCode = 7;
  value.emit("exit", 7);
  await Promise.resolve();
  if (settled) throw new Error("supervisor settled on exit before stdio close");
  if (runner.runnerState().activeSupervisorCount !== 1) {{
    throw new Error("supervisor tracker released before close");
  }}
  value.stdout.emit("data", stdout.subarray(5));
  value.stderr.emit("data", stderr.subarray(9));
  if (!Buffer.concat(stdoutChunks).equals(stdout)) throw new Error("split stdout bytes changed");
  if (!Buffer.concat(stderrChunks).equals(stderr)) throw new Error("split stderr bytes changed");
  value.emit("close", 7);
  if (await completion !== 7) throw new Error("natural exit code changed at close");
  if (runner.runnerState().activeSupervisorCount !== 0) throw new Error("close retained tracker");
  if (value.listenerCount("error") !== 0 || value.listenerCount("exit") !== 0
      || value.listenerCount("close") !== 0 || value.stdout.listenerCount("data") !== 0
      || value.stderr.listenerCount("data") !== 0) {{
    throw new Error("close retained supervisor listeners");
  }}
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_browser_runner_supervisor_stop_is_deduplicated_across_cleanup_and_shutdown(
    tmp_path: Path,
) -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    runtime_root = tmp_path / "supervisor-dedup-runtime"
    runtime_root.mkdir()
    script = f"""
const fs = require("fs");
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});
const ready = '{{"event":"ready","schema_version":1}}\\n';
const value = new EventEmitter();
value.exitCode = null;
value.signalCode = null;
value.stdout = new EventEmitter();
value.stderr = new EventEmitter();
value.ready = new EventEmitter();
let stopWrites = 0;
let waits = 0;
let exits = 0;
let removals = 0;
const originalRmSync = fs.rmSync;
value.stdin = {{
  write(data, callback) {{
    if (String(data) !== "stop\\n") throw new Error(`unexpected control: ${{String(data)}}`);
    stopWrites += 1;
    callback?.();
    return true;
  }},
}};
value.stdio = [value.stdin, value.stdout, value.stderr, value.ready];

async function main() {{
  fs.rmSync = function(target, options) {{
    if (target === {str(runtime_root)!r}) removals += 1;
    return originalRmSync.call(this, target, options);
  }};
  try {{
    const supervised = runner.spawnSupervised("productive", [], {{env: {{}}}}, {{
      spawn: () => value,
      waitForExit: async child => {{
        waits += 1;
        await new Promise(resolve => setImmediate(resolve));
        child.exitCode = 0;
        exits += 1;
        child.emit("exit", 0);
        child.emit("close", 0);
        return 0;
      }},
      stopTimeoutMs: 100,
    }});
    value.ready.emit("data", Buffer.from(ready));
    value.ready.emit("end");
    await runner.waitForSupervisorReady(supervised);
    const cleanup = runner.cleanupGroup([supervised], {str(runtime_root)!r});
    const ending = runner.shutdown("SIGTERM", {{
      exitProcess() {{}},
      shutdownTimeoutMs: 100,
    }});
    await Promise.all([cleanup, ending]);
    if (stopWrites !== 1 || waits !== 1 || exits !== 1 || removals !== 1) {{
      throw new Error(`dedup was writes=${{stopWrites}} waits=${{waits}} exits=${{exits}} removals=${{removals}}`);
    }}
    if (value.listenerCount("error") !== 0 || value.listenerCount("exit") !== 0
        || value.listenerCount("close") !== 0 || value.ready.listenerCount("data") !== 0) {{
      throw new Error("supervisor listeners were retained");
    }}
    const state = runner.runnerState();
    if (state.activeSupervisorCount !== 0 || state.activeRuntimeRoots.length !== 0) {{
      throw new Error(`tracker did not converge: ${{JSON.stringify(state)}}`);
    }}
  }} finally {{
    fs.rmSync = originalRmSync;
  }}
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_browser_runner_supervisor_stop_promise_survives_exit_and_rejection() -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});
const ready = Buffer.from('{{"event":"ready","schema_version":1}}\\n');

function child() {{
  const value = new EventEmitter();
  value.exitCode = null;
  value.signalCode = null;
  value.stdout = new EventEmitter();
  value.stderr = new EventEmitter();
  value.ready = new EventEmitter();
  value.stopWrites = 0;
  value.stdin = {{
    write(data, callback) {{
      if (String(data) !== "stop\\n") throw new Error("unexpected stop control");
      value.stopWrites += 1;
      callback?.();
      return true;
    }},
  }};
  value.stdio = [value.stdin, value.stdout, value.stderr, value.ready];
  return value;
}}

async function scenario(rejectWait) {{
  const value = child();
  const expected = new Error("synthetic stop rejection");
  let resolveWait;
  let rejectWaitOperation;
  const supervised = runner.spawnSupervised("productive", [], {{env: {{}}}}, {{
    spawn: () => value,
    stopTimeoutMs: 100,
    waitForExit: () => new Promise((resolve, reject) => {{
      resolveWait = resolve;
      rejectWaitOperation = reject;
    }}),
  }});
  value.ready.emit("data", ready);
  value.ready.emit("end");
  await runner.waitForSupervisorReady(supervised);

  const first = runner.stopSupervisor(supervised);
  await new Promise(resolve => setImmediate(resolve));
  value.exitCode = rejectWait ? 1 : 0;
  value.emit("exit", value.exitCode);
  const second = runner.stopSupervisor(supervised);
  if (second !== first) throw new Error("post-exit caller received a different stop promise");
  value.emit("close", value.exitCode);
  if (rejectWait) rejectWaitOperation(expected);
  else resolveWait(0);

  let firstResult = null;
  try {{ await first; }} catch (error) {{ firstResult = error; }}
  const third = runner.stopSupervisor(supervised);
  if (third !== first) throw new Error("settled stop promise identity changed");
  let thirdResult = null;
  try {{ await third; }} catch (error) {{ thirdResult = error; }}
  if (rejectWait) {{
    if (firstResult !== expected || thirdResult !== expected) {{
      throw firstResult || thirdResult || new Error("stop rejection was not shared");
    }}
  }} else if (firstResult || thirdResult) {{
    throw firstResult || thirdResult;
  }}
  if (value.stopWrites !== 1) throw new Error(`stop was written ${{value.stopWrites}} times`);
}}

(async () => {{
  await scenario(false);
  await scenario(true);
}})().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_browser_runner_first_stop_after_exit_or_spawn_error_waits_for_close_bounded() -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});
const ready = Buffer.from('{{"event":"ready","schema_version":1}}\\n');

function child() {{
  const value = new EventEmitter();
  value.exitCode = null;
  value.signalCode = null;
  value.stdout = new EventEmitter();
  value.stderr = new EventEmitter();
  value.ready = new EventEmitter();
  value.stopWrites = 0;
  value.stdin = {{
    write(_data, callback) {{ value.stopWrites += 1; callback?.(); return true; }},
  }};
  value.stdio = [value.stdin, value.stdout, value.stderr, value.ready];
  return value;
}}

function spawn(value, stopTimeoutMs = 100) {{
  return runner.spawnSupervised("productive", [], {{env: {{}}}}, {{
    spawn: () => value,
    stopTimeoutMs,
  }});
}}

async function assertPending(promise, label) {{
  const settled = await Promise.race([
    promise.then(() => true, () => true),
    new Promise(resolve => setTimeout(() => resolve(false), 10)),
  ]);
  if (settled) throw new Error(`${{label}} settled before close`);
}}

function assertReleased(value, label) {{
  if (runner.runnerState().activeSupervisorCount !== 0) {{
    throw new Error(`${{label}} retained tracker`);
  }}
  if (value.listenerCount("error") !== 0 || value.listenerCount("exit") !== 0
      || value.listenerCount("close") !== 0 || value.ready.listenerCount("data") !== 0
      || value.ready.listenerCount("end") !== 0 || value.ready.listenerCount("error") !== 0) {{
    throw new Error(`${{label}} retained listeners`);
  }}
}}

async function exitBeforeClose() {{
  const value = child();
  const supervised = spawn(value);
  value.ready.emit("data", ready);
  value.ready.emit("end");
  await runner.waitForSupervisorReady(supervised);
  value.exitCode = 0;
  value.emit("exit", 0);
  const first = runner.stopSupervisor(supervised);
  const second = runner.stopSupervisor(supervised);
  if (first !== second) throw new Error("exit-before-close stop promise was not canonical");
  if (value.stopWrites !== 0) throw new Error("stop was written after supervisor exit");
  if (runner.runnerState().activeSupervisorCount !== 1) throw new Error("exit released tracker early");
  await assertPending(first, "exit-before-close stop");
  value.emit("close", 0);
  await first;
  assertReleased(value, "exit-before-close stop");
}}

async function spawnErrorBeforeClose() {{
  const value = child();
  value.pid = 49301;
  const supervised = spawn(value);
  const expected = new Error("synthetic supervisor spawn error");
  value.emit("error", expected);
  const readiness = await runner.waitForSupervisorReady(supervised).catch(error => error);
  if (readiness !== expected) throw readiness || new Error("spawn error was not preserved");
  const first = runner.stopSupervisor(supervised);
  const second = runner.stopSupervisor(supervised);
  if (first !== second) throw new Error("spawn-error stop promise was not canonical");
  if (runner.runnerState().activeSupervisorCount !== 1) throw new Error("spawn error released tracker early");
  await assertPending(first, "spawn-error stop");
  value.emit("close", null);
  const firstError = await first.then(() => null, error => error);
  if (firstError !== expected) throw firstError || new Error("spawn-error stop did not share settlement");
  assertReleased(value, "spawn-error stop");
}}

async function spawnErrorWithoutCloseTimesOut() {{
  const value = child();
  value.pid = 49302;
  const supervised = spawn(value, 15);
  const expected = new Error("spawn error without close");
  value.emit("error", expected);
  await runner.waitForSupervisorReady(supervised).catch(() => {{}});
  const first = runner.stopSupervisor(supervised);
  const second = runner.stopSupervisor(supervised);
  if (first !== second) throw new Error("timeout stop promise was not canonical");
  const timeout = await first.then(() => null, error => error);
  if (!String(timeout?.message || "").includes("timed out")) {{
    throw timeout || new Error("missing close did not fail bounded");
  }}
  const third = runner.stopSupervisor(supervised);
  if (third !== first) throw new Error("rejected timeout promise identity changed");
  const repeated = await third.then(() => null, error => error);
  if (repeated !== timeout) throw new Error("timeout rejection was not shared");
  if (runner.runnerState().activeSupervisorCount !== 1) {{
    throw new Error("timeout released unresolved supervisor authority");
  }}
  if (value.listenerCount("close") !== 1) throw new Error("timeout removed close authority listener");
  value.emit("close", null);
  assertReleased(value, "spawn-error timeout");
}}

(async () => {{
  await exitBeforeClose();
  await spawnErrorBeforeClose();
  await spawnErrorWithoutCloseTimesOut();
}})().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_browser_runner_real_stop_write_failure_waits_for_delayed_close() -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const {{spawn}} = require("child_process");
const runner = require({str(runner_path)!r});
const controlled = `
const fs = require("fs");
const {{spawn}} = require("child_process");
fs.closeSync(0);
fs.writeSync(3, Buffer.from('{{"event":"ready","schema_version":1}}\\\\n'));
fs.closeSync(3);
spawn(process.execPath, ["-e", "setTimeout(() => {{}}, 450)"], {{
  stdio: ["ignore", 1, 2],
  windowsHide: true,
}});
setTimeout(() => process.exit(0), 300);
`;

async function main() {{
  let child;
  const supervised = runner.spawnSupervised("ignored", [], {{
    env: {{}},
    readinessTimeoutMs: 500,
  }}, {{
    spawn() {{
      child = spawn(process.execPath, ["-e", controlled], {{
        stdio: ["pipe", "pipe", "pipe", "pipe"],
        windowsHide: true,
      }});
      return child;
    }},
    stopTimeoutMs: 700,
  }});
  try {{
    await runner.waitForSupervisorReady(supervised);
    await new Promise(resolve => setTimeout(resolve, 150));
    if (!child.stdin.destroyed) {{
      const stdinClosed = new Promise(resolve => child.stdin.once("close", resolve));
      child.stdin.destroy();
      await stdinClosed;
    }}
    const started = Date.now();
    const stopError = await runner.stopSupervisor(supervised).then(() => null, error => error);
    const elapsed = Date.now() - started;
    if (!stopError || !["EPIPE", "ERR_STREAM_DESTROYED"].includes(stopError.code)) {{
      throw stopError || new Error("real control-pipe failure was hidden");
    }}
    if (elapsed < 100 || elapsed >= 700) {{
      throw new Error(`stop did not share delayed close deadline: ${{elapsed}}ms`);
    }}
    if (child.exitCode !== 0) throw new Error(`real delayed child exit was ${{child.exitCode}}`);
    if (runner.runnerState().activeSupervisorCount !== 0) {{
      throw new Error("real delayed close retained tracker");
    }}
  }} finally {{
    if (child?.exitCode === null) {{
      const closed = new Promise(resolve => child.once("close", resolve));
      child.kill();
      await closed;
    }}
  }}
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_browser_runner_stop_write_timeout_closes_control_and_uses_remaining_deadline() -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});
const ready = Buffer.from('{{"event":"ready","schema_version":1}}\\n');
const child = new EventEmitter();
child.exitCode = null;
child.signalCode = null;
child.stdout = new EventEmitter();
child.stderr = new EventEmitter();
child.ready = new EventEmitter();
child.stdin = new EventEmitter();
child.stdin.destroyed = false;
child.stdin.write = () => false;
child.stdin.destroy = () => {{
  if (child.stdin.destroyed) return;
  child.stdin.destroyed = true;
  setTimeout(() => {{ child.exitCode = 0; child.emit("exit", 0); }}, 5);
  setTimeout(() => child.emit("close", 0), 15);
}};
child.stdio = [child.stdin, child.stdout, child.stderr, child.ready];

async function main() {{
  const supervised = runner.spawnSupervised("productive", [], {{env: {{}}}}, {{
    spawn: () => child,
    stopTimeoutMs: 100,
  }});
  child.ready.emit("data", ready);
  child.ready.emit("end");
  await runner.waitForSupervisorReady(supervised);
  const started = Date.now();
  const error = await runner.stopSupervisor(supervised).then(() => null, failure => failure);
  const elapsed = Date.now() - started;
  if (error?.code !== "ETIMEDOUT" || !error.message.includes("stop request")) {{
    throw error || new Error("write timeout was hidden");
  }}
  if (!child.stdin.destroyed) throw new Error("timed-out control pipe was not destroyed");
  if (elapsed < 25 || elapsed >= 200) throw new Error(`bounded stop completion was ${{elapsed}}ms`);
  if (runner.runnerState().activeSupervisorCount !== 0) throw new Error("close retained tracker");
  if (child.stdin.listenerCount("error") !== 0) throw new Error("stdin error guard remained");
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_browser_runner_supervisor_spawn_errors_are_bounded_and_tracker_clean() -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});

function child() {{
  const value = new EventEmitter();
  value.exitCode = null;
  value.signalCode = null;
  value.stdout = new EventEmitter();
  value.stderr = new EventEmitter();
  value.ready = new EventEmitter();
  value.stdin = {{write(_data, callback) {{ callback?.(); return true; }}}};
  value.stdio = [value.stdin, value.stdout, value.stderr, value.ready];
  return value;
}}

async function asynchronous(label, emitBeforeWait) {{
  const expected = new Error(label);
  const value = child();
  const supervised = runner.spawnSupervised("productive", [], {{
    env: {{}},
    readinessTimeoutMs: 100,
  }}, {{spawn: () => value}});
  let pending;
  if (emitBeforeWait) {{
    value.emit("error", expected);
    pending = runner.waitForSupervisorReady(supervised);
  }} else {{
    pending = runner.waitForSupervisorReady(supervised);
    setImmediate(() => value.emit("error", expected));
  }}
  let actual = null;
  try {{ await pending; }} catch (error) {{ actual = error; }}
  if (actual !== expected) throw actual || new Error(`${{label}} was not preserved`);
  value.emit("close", null);
  if (value.listenerCount("error") !== 0 || value.listenerCount("exit") !== 0
      || value.listenerCount("close") !== 0 || value.ready.listenerCount("data") !== 0) {{
    throw new Error(`${{label}} retained listeners`);
  }}
}}

async function main() {{
  const synchronous = new Error("synchronous-supervisor-spawn");
  let actual = null;
  try {{
    runner.spawnSupervised("productive", [], {{env: {{}}}}, {{spawn() {{ throw synchronous; }}}});
  }} catch (error) {{
    actual = error;
  }}
  if (actual !== synchronous) throw actual || new Error("synchronous spawn was not preserved");
  await asynchronous("async-before-wait", true);
  await asynchronous("async-after-wait", false);
  if (runner.runnerState().activeSupervisorCount !== 0) throw new Error("spawn errors retained trackers");
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("failure_stage", ("server", "playwright"))
def test_run_group_distinguishes_productive_server_and_playwright_spawn_failure(
    failure_stage: str,
) -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const {{EventEmitter}} = require("events");
const fs = require("fs");
const runner = require({str(runner_path)!r});
const failureStage = process.argv[1];
const ready = Buffer.from('{{"event":"ready","schema_version":1}}\\n');
let calls = 0;
let healthCalls = 0;
let runtimeRoot = null;

function supervisor(label, failProductiveSpawn) {{
  const value = new EventEmitter();
  value.label = label;
  value.exitCode = null;
  value.signalCode = null;
  value.stdout = new EventEmitter();
  value.stderr = new EventEmitter();
  value.ready = new EventEmitter();
  value.stdin = new EventEmitter();
  value.stdin.write = (_data, callback) => {{
    callback?.();
    if (value.exitCode === null) setImmediate(() => {{
      value.exitCode = 0;
      value.emit("exit", 0);
      value.emit("close", 0);
    }});
    return true;
  }};
  value.stdio = [value.stdin, value.stdout, value.stderr, value.ready];
  setImmediate(() => {{
    if (failProductiveSpawn) {{
      value.exitCode = 71;
      value.emit("exit", 71);
      value.emit("close", 71);
      return;
    }}
    value.ready.emit("data", ready);
    value.ready.emit("end");
  }});
  return value;
}}

async function main() {{
  const actual = await runner.runGroup(null, [], {{
    freePort: async () => 43188,
    spawn(_command, _args, options) {{
      calls += 1;
      runtimeRoot ||= options.env.MORPHIC_BROWSER_RUNTIME_ROOT;
      fs.mkdirSync(runtimeRoot, {{recursive: true}});
      const label = calls === 1 ? "server" : "playwright";
      return supervisor(label, label === failureStage);
    }},
    waitForHealth: async () => {{ healthCalls += 1; }},
    stopTimeoutMs: 100,
  }}).then(() => null, error => error);

  const messages = [String(actual?.message || actual),
    ...Array.from(actual?.errors || [], error => String(error?.message || error))];
  if (!messages.some(message => message.includes("71") || message.toLowerCase().includes("readiness"))) {{
    throw actual || new Error(`${{failureStage}} productive spawn failure was hidden`);
  }}
  const expectedCalls = failureStage === "server" ? 1 : 2;
  const expectedHealth = failureStage === "server" ? 0 : 1;
  if (calls !== expectedCalls || healthCalls !== expectedHealth) {{
    throw new Error(`${{failureStage}} routing was calls=${{calls}} health=${{healthCalls}}`);
  }}
  const state = runner.runnerState();
  if (state.activeSupervisorCount !== 0 || state.activeRunCount !== 0) {{
    throw new Error(`${{failureStage}} retained trackers: ${{JSON.stringify(state)}}`);
  }}
  if (fs.existsSync(runtimeRoot)) fs.rmSync(runtimeRoot, {{recursive: true, force: true}});
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script, "--", failure_stage],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_run_group_child_error_emitted_inside_spawn_before_registration_is_primary() -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});
const expected = new Error("child-error-before-registration");

async function main() {{
  const actual = await runner.runGroup(null, [], {{
    freePort: async () => 43189,
    spawn() {{
      const value = new EventEmitter();
      value.emit("error", expected);
      return value;
    }},
  }}).then(() => null, error => error);
  if (actual !== expected) throw actual || new Error("pre-registration child error changed");
  const state = runner.runnerState();
  if (state.activeSupervisorCount !== 0 || state.activeRunCount !== 0) {{
    throw new Error(`pre-registration error retained trackers: ${{JSON.stringify(state)}}`);
  }}
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("authority", ("none", "pid", "ready"))
def test_browser_runner_async_spawn_error_removes_only_proven_unused_runtime(
    authority: str,
) -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const fs = require("fs");
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});
const authority = process.argv[1];
const expected = new Error(`async-spawn-${{authority}}`);
const ready = Buffer.from('{{"event":"ready","schema_version":1}}\\n');
let runtimeRoot = null;

function failedSupervisor() {{
  const value = new EventEmitter();
  value.exitCode = null;
  value.signalCode = null;
  value.pid = authority === "pid" ? 49101 : undefined;
  value.stdout = new EventEmitter();
  value.stderr = new EventEmitter();
  value.ready = new EventEmitter();
  value.stdin = new EventEmitter();
  value.stdin.write = () => {{ throw new Error("spawn failure must not receive stop control"); }};
  value.stdio = [value.stdin, value.stdout, value.stderr, value.ready];
  setImmediate(() => {{
    if (authority === "ready") {{
      value.ready.emit("data", ready);
      value.ready.emit("end");
    }}
    setImmediate(() => {{
      value.emit("error", expected);
      value.emit("close", null);
    }});
  }});
  return value;
}}

async function main() {{
  const actual = await runner.runGroup(null, [], {{
    freePort: async () => 43178,
    spawn(_command, _args, options) {{
      runtimeRoot = options.env.MORPHIC_BROWSER_RUNTIME_ROOT;
      fs.mkdirSync(runtimeRoot, {{recursive: true}});
      return failedSupervisor();
    }},
    waitForHealth: async () => {{
      await new Promise(resolve => setImmediate(resolve));
      throw expected;
    }},
    stopTimeoutMs: 50,
  }}).catch(error => error);

  const state = runner.runnerState();
  if (authority === "none") {{
    if (actual !== expected) throw actual || new Error("proven spawn error was wrapped as cleanup ambiguity");
    if (fs.existsSync(runtimeRoot) || state.activeRuntimeRoots.includes(runtimeRoot)) {{
      throw new Error("proven unused runtime was preserved");
    }}
  }} else {{
    if (!(actual instanceof AggregateError) || actual.errors[0] !== expected) {{
      throw actual || new Error(`${{authority}} ambiguity lost primary ordering`);
    }}
    if (!fs.existsSync(runtimeRoot) || !state.activeRuntimeRoots.includes(runtimeRoot)) {{
      throw new Error(`${{authority}} ambiguity removed forensic runtime`);
    }}
    fs.rmSync(runtimeRoot, {{recursive: true, force: true}});
  }}
  if (state.activeSupervisorCount !== 0 || state.activeRunCount !== 0) {{
    throw new Error(`spawn error retained process trackers: ${{JSON.stringify(state)}}`);
  }}
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script, authority],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "scenario",
    ("after-allocation", "after-health", "readiness-pending", "finally-owns-stop"),
)
def test_browser_runner_shutdown_closes_every_spawn_gate_and_shares_stop(
    scenario: str,
) -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});
const scenario = process.argv[1];
const ready = Buffer.from('{{"event":"ready","schema_version":1}}\\n');
let spawnCalls = 0;
let stopWrites = 0;
let waits = 0;
let exitCode = null;
let shutdownOperation = null;
let observedRunCount = null;
let resolveSpawned;
let resolveStopStarted;
const spawned = new Promise(resolve => {{ resolveSpawned = resolve; }});
const stopStarted = new Promise(resolve => {{ resolveStopStarted = resolve; }});

function supervisor() {{
  const value = new EventEmitter();
  value.exitCode = null;
  value.signalCode = null;
  value.stdout = new EventEmitter();
  value.stderr = new EventEmitter();
  value.ready = new EventEmitter();
  let resolveClosed;
  value.closed = new Promise(resolve => {{ resolveClosed = resolve; }});
  value.closeNow = (code = 0) => {{
    if (value.exitCode !== null) return;
    value.exitCode = code;
    value.emit("exit", code);
    value.emit("close", code);
    resolveClosed(code);
  }};
  value.stdin = new EventEmitter();
  value.stdin.destroyed = false;
  value.stdin.write = (data, callback) => {{
    if (String(data) !== "stop\\n") throw new Error("unexpected supervisor control");
    stopWrites += 1;
    callback?.();
    resolveStopStarted();
    if (scenario !== "finally-owns-stop") setImmediate(() => value.closeNow(0));
    return true;
  }};
  value.stdin.destroy = () => {{ value.stdin.destroyed = true; }};
  value.stdio = [value.stdin, value.stdout, value.stderr, value.ready];
  return value;
}}

function shutdown() {{
  shutdownOperation ||= runner.shutdown("SIGTERM", {{
    exitProcess(code) {{ exitCode = code; }},
    shutdownTimeoutMs: 80,
  }});
  return shutdownOperation;
}}

async function main() {{
  let active = null;
  const dependencies = {{
    freePort: async () => {{
      observedRunCount = runner.runnerState().activeRunCount;
      if (scenario === "after-allocation") shutdown();
      return 43173;
    }},
    spawn() {{
      spawnCalls += 1;
      active = supervisor();
      resolveSpawned();
      if (scenario !== "readiness-pending") {{
        setImmediate(() => {{
          active.ready.emit("data", ready);
          active.ready.emit("end");
        }});
      }}
      return active;
    }},
    waitForExit: async value => {{ waits += 1; return value.closed; }},
    waitForHealth: async () => {{
      if (scenario === "after-health") shutdown();
      if (scenario === "finally-owns-stop") throw new Error("primary-health-failure");
    }},
    stopTimeoutMs: 80,
  }};

  const run = runner.runGroup(null, [], dependencies).catch(error => error);
  if (scenario === "readiness-pending") {{
    await spawned;
    shutdown();
  }} else if (scenario === "finally-owns-stop") {{
    await stopStarted;
    shutdown();
    setImmediate(() => active.closeNow(0));
  }}
  const runResult = await run;
  await shutdownOperation;
  const runMessages = [];
  const visit = error => {{
    runMessages.push(String(error?.message || error));
    if (error instanceof AggregateError) error.errors.forEach(visit);
  }};
  visit(runResult);

  if (observedRunCount !== 1) {{
    throw new Error(`run was not registered before allocation: ${{observedRunCount}}`);
  }}
  if (!runMessages.some(message => message.includes(
      scenario === "finally-owns-stop" ? "primary-health-failure" :
      scenario === "readiness-pending" ? "readiness" : "shutdown"))) {{
    throw runResult || new Error(`wrong ${{scenario}} run result`);
  }}
  const expectedSpawns = scenario === "after-allocation" ? 0 : 1;
  if (spawnCalls !== expectedSpawns) {{
    throw new Error(`${{scenario}} spawned ${{spawnCalls}} supervisors`);
  }}
  if (expectedSpawns && (stopWrites !== 1 || waits !== 1)) {{
    throw new Error(`${{scenario}} stop was writes=${{stopWrites}} waits=${{waits}}`);
  }}
  if (exitCode !== 143) throw new Error(`${{scenario}} exit code was ${{exitCode}}`);
  const state = runner.runnerState();
  if (state.activeSupervisorCount !== 0 || state.activeRunCount !== 0) {{
    throw new Error(`${{scenario}} did not quiesce: ${{JSON.stringify(state)}}`);
  }}
  let lateSpawns = 0;
  const late = await runner.runGroup(null, [], {{
    freePort: async () => 43174,
    spawn() {{ lateSpawns += 1; throw new Error("late spawn"); }},
  }}).catch(error => error);
  if (!String(late?.message || "").includes("shutdown") || lateSpawns !== 0) {{
    throw late || new Error("shutdown admission reopened");
  }}
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script, scenario],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_browser_runner_shutdown_uses_one_monotonic_deadline_for_both_phases() -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});
const ready = Buffer.from('{{"event":"ready","schema_version":1}}\\n');
let clock = 1000;
const budgets = [];
let exitCode = null;
let releaseAllocation;

function supervisor() {{
  const value = new EventEmitter();
  value.exitCode = null;
  value.signalCode = null;
  value.stdout = new EventEmitter();
  value.stderr = new EventEmitter();
  value.ready = new EventEmitter();
  value.stdin = new EventEmitter();
  value.stdin.write = (_data, callback) => {{
    callback?.();
    value.exitCode = 0;
    value.emit("exit", 0);
    value.emit("close", 0);
    return true;
  }};
  value.stdio = [value.stdin, value.stdout, value.stderr, value.ready];
  return value;
}}

async function main() {{
  const owned = supervisor();
  runner.spawnSupervised("productive", [], {{env: {{}}}}, {{spawn: () => owned}});
  owned.ready.emit("data", ready);
  owned.ready.emit("end");
  const allocation = new Promise(resolve => {{ releaseAllocation = resolve; }});
  const run = runner.runGroup(null, [], {{freePort: () => allocation}}).catch(error => error);
  await Promise.resolve();
  if (runner.runnerState().activeRunCount !== 1) throw new Error("pending run was not admitted");

  await runner.shutdown("SIGINT", {{
    exitProcess(code) {{ exitCode = code; }},
    shutdownTimeoutMs: 100,
    now: () => clock,
    async waitForOperations(operations, timeoutMs, label) {{
      budgets.push([label, timeoutMs]);
      if (budgets.length === 1) {{
        const results = await Promise.allSettled(operations);
        clock += 70;
        return results;
      }}
      clock += timeoutMs;
      return [];
    }},
  }});
  if (JSON.stringify(budgets.map(([, value]) => value)) !== JSON.stringify([100, 30])) {{
    throw new Error(`shutdown budgets were ${{JSON.stringify(budgets)}}`);
  }}
  if (exitCode !== 130) throw new Error(`SIGINT exit code was ${{exitCode}}`);
  releaseAllocation(43175);
  const result = await run;
  if (!String(result?.message || "").includes("shutdown")) throw result;
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_browser_runner_shutdown_reports_run_primary_before_supervisor_cleanup() -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});
const ready = Buffer.from('{{"event":"ready","schema_version":1}}\\n');
const primary = new Error("active-run-primary");
const cleanup = new Error("supervisor-cleanup");
const execution = [];
const reported = [];
let rejectHealth;
let resolveHealthEntered;
const healthEntered = new Promise(resolve => {{ resolveHealthEntered = resolve; }});
const value = new EventEmitter();
value.exitCode = null;
value.signalCode = null;
value.pid = 49303;
value.stdout = new EventEmitter();
value.stderr = new EventEmitter();
value.ready = new EventEmitter();
value.stdin = new EventEmitter();
value.stdin.destroyed = false;
value.stdin.write = (_data, callback) => {{ callback?.(); return true; }};
value.stdin.destroy = () => {{ value.stdin.destroyed = true; }};
value.stdio = [value.stdin, value.stdout, value.stderr, value.ready];

async function main() {{
  const run = runner.runGroup(null, [], {{
    freePort: async () => 43179,
    spawn: () => {{
      setImmediate(() => {{ value.ready.emit("data", ready); value.ready.emit("end"); }});
      return value;
    }},
    waitForHealth: () => new Promise((_resolve, reject) => {{
      rejectHealth = reject;
      resolveHealthEntered();
    }}),
    waitForExit: async () => {{
      execution.push("cleanup");
      rejectHealth(primary);
      throw cleanup;
    }},
    stopTimeoutMs: 50,
  }}).catch(error => error);
  await healthEntered;

  const originalError = console.error;
  console.error = error => reported.push(error);
  try {{
    await runner.shutdown("SIGTERM", {{
      exitProcess() {{}},
      shutdownTimeoutMs: 80,
    }});
  }} finally {{
    console.error = originalError;
  }}
  const runError = await run;
  if (execution.join(",") !== "cleanup") {{
    throw new Error(`cleanup execution order changed: ${{execution}}`);
  }}
  if (!(runError instanceof AggregateError) || runError.errors[0] !== primary) throw runError;
  if (reported.length !== 2 || reported[0] !== primary || reported[1] !== cleanup) {{
    throw new Error(`shutdown report order was ${{reported.map(error => error.message).join(",")}}`);
  }}
  value.exitCode = 1;
  value.emit("exit", 1);
  value.emit("close", 1);
  const state = runner.runnerState();
  if (state.activeSupervisorCount !== 0 || state.activeRunCount !== 0) {{
    throw new Error(`ordered shutdown retained trackers: ${{JSON.stringify(state)}}`);
  }}
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("remaining_ms", (0, -1))
def test_browser_runner_expired_stop_deadline_starts_no_new_work(
    remaining_ms: int,
) -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});
const remaining = Number(process.argv[1]);
const ready = Buffer.from('{{"event":"ready","schema_version":1}}\\n');
const value = new EventEmitter();
value.exitCode = null;
value.signalCode = null;
value.pid = 49304;
value.stdout = new EventEmitter();
value.stderr = new EventEmitter();
value.ready = new EventEmitter();
value.stdin = new EventEmitter();
let writes = 0;
let waits = 0;
let timers = 0;
value.stdin.write = () => {{ writes += 1; return false; }};
value.stdio = [value.stdin, value.stdout, value.stderr, value.ready];

async function main() {{
  const supervised = runner.spawnSupervised("productive", [], {{env: {{}}}}, {{
    spawn: () => value,
    waitForExit: async () => {{ waits += 1; return 0; }},
    stopTimeoutMs: 100,
  }});
  value.ready.emit("data", ready);
  value.ready.emit("end");
  await runner.waitForSupervisorReady(supervised);

  const originalSetTimeout = global.setTimeout;
  global.setTimeout = (...args) => {{ timers += 1; return originalSetTimeout(...args); }};
  let first;
  let second;
  let actual;
  try {{
    first = runner.stopSupervisor(supervised, {{
      deadline: 100 + remaining,
      now: () => 100,
    }});
    second = runner.stopSupervisor(supervised);
    actual = await first.then(() => null, error => error);
  }} finally {{
    global.setTimeout = originalSetTimeout;
  }}
  if (second !== first) throw new Error("expired stop promise was not canonical");
  if (actual?.code !== "ETIMEDOUT" || !actual.message.includes("deadline")) {{
    throw actual || new Error("expired deadline did not fail explicitly");
  }}
  if (writes !== 0 || waits !== 0 || timers !== 0) {{
    throw new Error(`expired deadline started writes=${{writes}} waits=${{waits}} timers=${{timers}}`);
  }}
  if (value.stdin.listenerCount("error") !== 0) {{
    throw new Error("expired deadline installed a control listener");
  }}
  value.exitCode = 0;
  value.emit("exit", 0);
  value.emit("close", 0);
  if (runner.runnerState().activeSupervisorCount !== 0) {{
    throw new Error("expired deadline retained tracker after close");
  }}
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script, "--", str(remaining_ms)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_browser_runner_control_budget_expiry_starts_no_side_effects() -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});
const ready = Buffer.from('{{"event":"ready","schema_version":1}}\\n');
const value = new EventEmitter();
value.exitCode = null;
value.signalCode = null;
value.pid = 49305;
value.stdout = new EventEmitter();
value.stderr = new EventEmitter();
value.ready = new EventEmitter();
value.stdin = new EventEmitter();
let writes = 0;
let waits = 0;
let timers = 0;
let clockReads = 0;
value.stdin.write = () => {{ writes += 1; return false; }};
value.stdio = [value.stdin, value.stdout, value.stderr, value.ready];

async function main() {{
  const supervised = runner.spawnSupervised("productive", [], {{env: {{}}}}, {{
    spawn: () => value,
    waitForExit: async () => {{ waits += 1; return 0; }},
    stopTimeoutMs: 100,
  }});
  value.ready.emit("data", ready);
  value.ready.emit("end");
  await runner.waitForSupervisorReady(supervised);

  const clock = [0, 99, 100];
  const originalSetTimeout = global.setTimeout;
  global.setTimeout = (...args) => {{ timers += 1; return originalSetTimeout(...args); }};
  let actual;
  try {{
    actual = await runner.stopSupervisor(supervised, {{
      deadline: 100,
      now: () => clock[Math.min(clockReads++, clock.length - 1)],
    }}).then(() => null, error => error);
  }} finally {{
    global.setTimeout = originalSetTimeout;
  }}
  if (!actual) throw new Error("expired control budget resolved");
  if (clockReads < 3) throw new Error(`control budget was not sampled: ${{clockReads}}`);
  if (writes !== 0 || waits !== 0 || timers !== 0) {{
    throw new Error(`control boundary started writes=${{writes}} waits=${{waits}} timers=${{timers}}`);
  }}
  if (value.stdin.listenerCount("error") !== 0) {{
    throw new Error("expired control budget installed a listener");
  }}
  value.exitCode = 0;
  value.emit("exit", 0);
  value.emit("close", 0);
  if (runner.runnerState().activeSupervisorCount !== 0) {{
    throw new Error("control-budget test retained tracker after close");
  }}
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "scenario",
    ("sync-spawn", "malformed-readiness", "control-write", "nonzero", "timeout"),
)
def test_browser_runner_supervisor_failures_order_errors_and_preserve_runtime(
    scenario: str,
) -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const fs = require("fs");
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});
const scenario = process.argv[1];
const ready = Buffer.from('{{"event":"ready","schema_version":1}}\\n');
const primary = new Error("primary-health-failure");
const control = Object.assign(new Error("control-write-failure"), {{code: "EPIPE"}});
let calls = 0;
let runtimeRoot = null;
const supervisors = [];

function close(value, code) {{
  value.exitCode = code;
  value.emit("exit", code);
  value.emit("close", code);
}}

function supervisor(label) {{
  const value = new EventEmitter();
  value.label = label;
  value.exitCode = null;
  value.signalCode = null;
  value.stdout = new EventEmitter();
  value.stderr = new EventEmitter();
  value.ready = new EventEmitter();
  value.stdin = new EventEmitter();
  value.stdin.destroyed = false;
  value.stdin.destroy = () => {{ value.stdin.destroyed = true; }};
  value.stdin.write = (_data, callback) => {{
    if (scenario === "control-write" && label === "server") {{
      callback?.(control);
      setImmediate(() => close(value, 0));
      return false;
    }}
    callback?.();
    if (scenario !== "timeout") setImmediate(() => close(value, 0));
    return true;
  }};
  value.stdio = [value.stdin, value.stdout, value.stderr, value.ready];
  supervisors.push(value);
  return value;
}}

function messages(error) {{
  return [String(error?.message || error), ...Array.from(error?.errors || [], messages).flat()];
}}

async function main() {{
  const actual = await runner.runGroup(null, [], {{
    freePort: async () => 43176,
    stopTimeoutMs: 25,
    spawn(_command, _args, options) {{
      calls += 1;
      runtimeRoot ||= options.env.MORPHIC_BROWSER_RUNTIME_ROOT;
      fs.mkdirSync(runtimeRoot, {{recursive: true}});
      if (scenario === "sync-spawn") throw new Error("synchronous-supervisor-spawn");
      const value = supervisor(calls === 1 ? "server" : "playwright");
      setImmediate(() => {{
        if (scenario === "malformed-readiness" && calls === 1) {{
          value.ready.emit("data", Buffer.from("not-ready\\n"));
          value.ready.emit("end");
          return;
        }}
        value.ready.emit("data", ready);
        value.ready.emit("end");
        if (value.label === "playwright") setImmediate(() => close(value, 7));
      }});
      return value;
    }},
    waitForHealth: async () => {{
      if (["control-write", "timeout"].includes(scenario)) throw primary;
    }},
  }}).catch(error => error);

  const allMessages = messages(actual);
  if (scenario === "sync-spawn") {{
    if (!allMessages.some(value => value.includes("synchronous-supervisor-spawn"))) throw actual;
    if (fs.existsSync(runtimeRoot)) throw new Error("unused runtime survived synchronous spawn failure");
  }} else if (scenario === "malformed-readiness") {{
    if (!allMessages.some(value => value.toLowerCase().includes("readiness"))) throw actual;
    if (!fs.existsSync(runtimeRoot)) throw new Error("malformed protocol removed forensic runtime");
  }} else {{
    if (!(actual instanceof AggregateError)) throw actual || new Error("cleanup aggregate missing");
    const expectedPrimary = scenario === "nonzero" ? "Playwright group focus failed with exit 7" : primary.message;
    if (!String(actual.errors[0]?.message || actual.errors[0]).includes(expectedPrimary)) {{
      throw new Error(`primary error was not first: ${{JSON.stringify(allMessages)}}`);
    }}
    if (!fs.existsSync(runtimeRoot)) throw new Error(`${{scenario}} removed forensic runtime`);
  }}
  const state = runner.runnerState();
  if (state.activeRunCount !== 0) throw new Error(`${{scenario}} retained run tracker`);
  if (scenario !== "timeout" && state.activeSupervisorCount !== 0) {{
    throw new Error(`${{scenario}} retained supervisor tracker`);
  }}
  if (scenario === "timeout") {{
    if (state.activeSupervisorCount !== 1) throw new Error("timeout released stable authority");
    close(supervisors[0], 0);
  }}
  for (const value of supervisors) {{
    if (value.exitCode !== null && (value.listenerCount("error") !== 0
        || value.listenerCount("exit") !== 0 || value.listenerCount("close") !== 0)) {{
      throw new Error(`${{scenario}} retained settled supervisor listeners`);
    }}
  }}
  if (fs.existsSync(runtimeRoot)) fs.rmSync(runtimeRoot, {{recursive: true, force: true}});
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script, scenario],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_browser_runner_shutdown_timeout_makes_a_bounded_exit_decision() -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const fs = require("fs");
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});
let runtimeRoot = null;
let exitCode = null;
let stopWrites = 0;
let resolveSpawned;
const spawned = new Promise(resolve => {{ resolveSpawned = resolve; }});
const value = new EventEmitter();
value.exitCode = null;
value.signalCode = null;
value.stdout = new EventEmitter();
value.stderr = new EventEmitter();
value.ready = new EventEmitter();
value.stdin = new EventEmitter();
value.stdin.destroyed = false;
value.stdin.write = (_data, callback) => {{ stopWrites += 1; callback?.(); return true; }};
value.stdin.destroy = () => {{ value.stdin.destroyed = true; }};
value.stdio = [value.stdin, value.stdout, value.stderr, value.ready];

async function main() {{
  const run = runner.runGroup(null, [], {{
    freePort: async () => 43177,
    stopTimeoutMs: 20,
    spawn(_command, _args, options) {{
      runtimeRoot = options.env.MORPHIC_BROWSER_RUNTIME_ROOT;
      fs.mkdirSync(runtimeRoot, {{recursive: true}});
      resolveSpawned();
      return value;
    }},
    waitForHealth: async () => {{}},
  }}).catch(error => error);
  await spawned;
  const started = Date.now();
  await runner.shutdown("SIGTERM", {{
    exitProcess(code) {{ exitCode = code; }},
    shutdownTimeoutMs: 30,
  }});
  const elapsed = Date.now() - started;
  if (elapsed >= 250) throw new Error(`shutdown exit decision took ${{elapsed}}ms`);
  if (exitCode !== 143 || stopWrites !== 1) {{
    throw new Error(`shutdown decision was exit=${{exitCode}} writes=${{stopWrites}}`);
  }}
  if (!value.stdin.destroyed) throw new Error("final shutdown did not close stable control authority");
  if (!fs.existsSync(runtimeRoot)) throw new Error("ambiguous shutdown removed forensic runtime");
  const runResult = await Promise.race([
    run,
    new Promise(resolve => setTimeout(() => resolve(null), 100)),
  ]);
  if (!(runResult instanceof AggregateError)) {{
    throw runResult || new Error("active run remained pending after final exit decision");
  }}
  if (runner.runnerState().activeRunCount !== 0) throw new Error("final exit retained run operation");
  if (runner.runnerState().activeSupervisorCount !== 1) {{
    throw new Error("final exit discarded unresolved supervisor authority");
  }}
  value.exitCode = 0;
  value.emit("exit", 0);
  value.emit("close", 0);
  if (runner.runnerState().activeSupervisorCount !== 0) throw new Error("late close retained authority");
  fs.rmSync(runtimeRoot, {{recursive: true, force: true}});
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=3,
    )
    assert result.returncode == 0, result.stderr


def test_browser_runner_parallel_same_group_same_millisecond_uses_unique_runtime_roots() -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    script = f"""
const {{EventEmitter}} = require("events");
const runner = require({str(runner_path)!r});
const ready = Buffer.from('{{"event":"ready","schema_version":1}}\\n');
const roots = [];
const originalNow = Date.now;

function supervisor(exitAfterReady) {{
  const value = new EventEmitter();
  value.exitCode = null;
  value.signalCode = null;
  value.stdout = new EventEmitter();
  value.stderr = new EventEmitter();
  value.ready = new EventEmitter();
  value.stdin = new EventEmitter();
  value.stdin.destroyed = false;
  value.stdin.write = (_data, callback) => {{
    callback?.();
    setImmediate(() => {{
      value.exitCode = 0;
      value.emit("exit", 0);
      value.emit("close", 0);
    }});
    return true;
  }};
  value.stdin.destroy = () => {{ value.stdin.destroyed = true; }};
  value.stdio = [value.stdin, value.stdout, value.stderr, value.ready];
  setImmediate(() => {{
    value.ready.emit("data", ready);
    value.ready.emit("end");
    if (exitAfterReady) setImmediate(() => {{
      value.exitCode = 0;
      value.emit("exit", 0);
      value.emit("close", 0);
    }});
  }});
  return value;
}}

function dependencies(label) {{
  let calls = 0;
  return {{
    freePort: async () => label === "first" ? 43181 : 43182,
    spawn(_command, _args, options) {{
      calls += 1;
      if (calls === 1) roots.push(options.env.MORPHIC_BROWSER_RUNTIME_ROOT);
      return supervisor(calls === 2);
    }},
    waitForHealth: async () => {{}},
    stopTimeoutMs: 100,
  }};
}}

async function main() {{
  Date.now = () => 1234567890;
  try {{
    await Promise.all([
      runner.runGroup(1, [], dependencies("first")),
      runner.runGroup(1, [], dependencies("second")),
    ]);
  }} finally {{
    Date.now = originalNow;
  }}
  if (roots.length !== 2 || new Set(roots).size !== 2) {{
    throw new Error(`parallel runtime roots collided: ${{JSON.stringify(roots)}}`);
  }}
  const state = runner.runnerState();
  if (state.activeSupervisorCount !== 0 || state.activeRunCount !== 0
      || state.activeRuntimeRoots.length !== 0) {{
    throw new Error(`parallel runs retained state: ${{JSON.stringify(state)}}`);
  }}
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_real_node_python_supervisor_harnesses_hold_authority_in_finally() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    for test_name in (
        "test_browser_runner_real_node_python_supervisor_controls_tree_and_forwards_output",
        "test_real_node_python_harness_early_assertion_cleans_tree_and_runtime",
        "test_run_group_real_delayed_duplicate_rejects_and_preserves_runtime",
        "test_browser_runner_real_supervisor_failure_preserves_runtime_after_tree_absence",
    ):
        block = source.split(f"\ndef {test_name}(\n", 1)[1].split(
            "\ndef test_", 1
        )[0]
        spawn_marker = "node_process = subprocess.Popen("
        assert spawn_marker in block, f"{test_name}: Python Popen authority missing"
        popen_index = block.index(spawn_marker)
        assert block.rfind("try:", 0, popen_index) >= 0, (
            f"{test_name}: Python spawn is outside try"
        )
        assert block.find("finally:", popen_index) >= 0, (
            f"{test_name}: Python cleanup finally missing"
        )
        assert "_finish_real_node_harness_in_sandbox(" in block, (
            f"{test_name}: forensic sandbox finalizer missing"
        )
        node_main = block.split("async function main() {{", 1)[1].split(
            "main().catch", 1
        )[0]
        assert "try {{" in node_main, f"{test_name}: Node spawn is outside try"
        assert "finally {{" in node_main, f"{test_name}: Node cleanup finally missing"


def test_real_node_python_harnesses_publish_exact_supervisor_identity() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    for test_name in (
        "test_browser_runner_real_node_python_supervisor_controls_tree_and_forwards_output",
        "test_real_node_python_harness_early_assertion_cleans_tree_and_runtime",
        "test_run_group_real_delayed_duplicate_rejects_and_preserves_runtime",
        "test_browser_runner_real_supervisor_failure_preserves_runtime_after_tree_absence",
    ):
        block = source.split(f"\ndef {test_name}(\n", 1)[1].split(
            "\ndef test_", 1
        )[0]
        assert "supervisor_probe_path = tmp_path /" in block, (
            f"{test_name}: test-owned supervisor identity sidecar missing"
        )
        assert "const supervisorProbePath =" in block
        assert (
            'const supervisorIdentitySidecarEnv = '
            '"MORPHIC_BROWSER_SUPERVISOR_IDENTITY_SIDECAR";'
        ) in block
        spawn_index = block.index("supervisor = spawn(")
        return_index = block.index("return supervisor;", spawn_index)
        sidecar_index = block.index(
            "[supervisorIdentitySidecarEnv]: supervisorProbePath",
            spawn_index,
        )
        assert spawn_index < sidecar_index < return_index, (
            f"{test_name}: test-owned identity sidecar was not passed at spawn"
        )
        assert "fs.writeFileSync(supervisorProbePath" not in block
        capture_index = block.index(
            "supervisor_identity = _wait_for_published_supervisor_identity("
        )
        communicate_index = block.index("node_process.communicate(")
        assert capture_index < communicate_index, (
            f"{test_name}: PID/create-time capture must precede communicate"
        )
        finalizer_index = block.index("_finish_real_node_harness(", communicate_index)
        assert block.index("finally:", communicate_index) < finalizer_index
        assert "token=tree_token" in block[finalizer_index:]
        assert "baseline=fallback_baseline" in block[finalizer_index:]


def test_delayed_readiness_harness_owns_all_node_temp_paths() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    block = source.split(
        "\ndef test_run_group_real_delayed_duplicate_rejects_and_preserves_runtime(\n",
        1,
    )[1].split("\ndef test_", 1)[0]

    assert 'test_temp_root = tmp_path / "delayed-readiness-temp"' in block
    for variable in ("TMP", "TEMP", "TMPDIR"):
        assert f'"{variable}": str(test_temp_root)' in block
    popen = block.split("node_process = subprocess.Popen(", 1)[1].split(")\n", 1)[0]
    assert "env=node_environment" in popen
    finally_block = block.rsplit("finally:", 1)[1]
    assert "sandbox_root=test_temp_root" in finally_block
    assert "shutil.rmtree(test_temp_root" not in finally_block


def test_failure_preservation_harness_owns_all_node_temp_paths() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    block = source.split(
        "\ndef test_browser_runner_real_supervisor_failure_preserves_runtime_after_tree_absence(\n",
        1,
    )[1].split("\ndef test_", 1)[0]

    assert 'test_temp_root = tmp_path / "failure-preservation-temp"' in block
    for variable in ("TMP", "TEMP", "TMPDIR"):
        assert f'"{variable}": str(test_temp_root)' in block
    popen = block.split("node_process = subprocess.Popen(", 1)[1].split(")\n", 1)[0]
    assert "env=node_environment" in popen
    finally_block = block.split("finally:", 1)[1]
    assert "sandbox_root=test_temp_root" in finally_block
    assert "shutil.rmtree(test_temp_root" not in finally_block


@pytest.mark.parametrize(
    "mode", ("timeout", "timeout-cleanup-failure", "early-exit")
)
def test_failure_preservation_harness_retains_forensics_only_on_cleanup_ambiguity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
) -> None:
    host_temp_root = Path(os.environ.get("TEMP") or os.environ.get("TMP") or tmp_path)
    outside_before = set(host_temp_root.glob("morphic-browser-*"))
    observed_environments: list[dict[str, str]] = []
    created_runtime: Path | None = None

    class ControlledNodeProcess:
        def __init__(self, args: list[str], **kwargs: object) -> None:
            nonlocal created_runtime
            self.args = args
            self.returncode: int | None = None
            environment = dict(kwargs.get("env") or {})
            observed_environments.append(environment)
            created_runtime = Path(environment.get("TMP", str(host_temp_root))) / (
                f"morphic-browser-{secrets.token_hex(8)}"
            )
            created_runtime.mkdir(parents=True)

        def communicate(self, timeout: float) -> tuple[str, str]:
            if mode.startswith("timeout"):
                raise subprocess.TimeoutExpired(self.args, timeout)
            self.returncode = 99
            return "", "controlled early exit"

        def poll(self) -> int | None:
            return self.returncode

        def kill(self) -> None:
            self.returncode = -9

        def wait(self, timeout: float) -> int:
            del timeout
            assert self.returncode is not None
            return self.returncode

    monkeypatch.setattr(subprocess, "Popen", ControlledNodeProcess)
    monkeypatch.setattr(
        sys.modules[__name__],
        "_wait_for_published_supervisor_identity",
        lambda _path: (os.getpid(), 0.0),
    )
    monkeypatch.setattr(
        sys.modules[__name__],
        "_wait_for_published_tree_token",
        lambda _path: "a" * 32,
    )
    cleanup_wait_calls = 0
    forensic_observations: list[tuple[Path, bool, bool, BaseException]] = []

    def wait_for_cleanup(_identity: tuple[int, float]) -> bool:
        nonlocal cleanup_wait_calls
        cleanup_wait_calls += 1
        if mode == "timeout-cleanup-failure" and cleanup_wait_calls == 1:
            raise AssertionError("controlled parent cleanup failure")
        return True

    monkeypatch.setattr(
        sys.modules[__name__], "_published_identity_absent", wait_for_cleanup
    )
    original_evidence_recorder = _record_forensic_runtime_evidence

    def record_evidence(path: Path, error: BaseException) -> None:
        forensic_observations.append(
            (path, path.exists(), (tmp_path / "failure-preservation-temp").exists(), error)
        )
        original_evidence_recorder(path, error)

    monkeypatch.setattr(
        sys.modules[__name__],
        "_record_forensic_runtime_evidence",
        record_evidence,
    )
    try:
        if mode == "timeout-cleanup-failure":
            with pytest.raises(CleanupAmbiguityError) as caught:
                test_browser_runner_real_supervisor_failure_preserves_runtime_after_tree_absence(
                    tmp_path
                )
            assert isinstance(caught.value.exceptions[0], subprocess.TimeoutExpired)
            cleanup_group = caught.value.exceptions[1]
            assert isinstance(cleanup_group, BaseExceptionGroup)
            assert isinstance(cleanup_group.exceptions[0], AssertionError)
            assert str(cleanup_group.exceptions[0]) == "controlled parent cleanup failure"
            assert cleanup_wait_calls == 1
            assert forensic_observations == [
                (created_runtime, True, True, caught.value)
            ]
        else:
            expected_error = (
                subprocess.TimeoutExpired if mode == "timeout" else AssertionError
            )
            with pytest.raises(expected_error):
                test_browser_runner_real_supervisor_failure_preserves_runtime_after_tree_absence(
                    tmp_path
                )
            assert forensic_observations == []

        assert len(observed_environments) == 1
        environment = observed_environments[0]
        owned_root = tmp_path / "failure-preservation-temp"
        assert {environment[name] for name in ("TMP", "TEMP", "TMPDIR")} == {
            str(owned_root)
        }
        assert created_runtime is not None
        assert created_runtime.is_relative_to(owned_root)
        if mode == "timeout-cleanup-failure":
            assert owned_root.exists()
            assert created_runtime.exists()
        else:
            assert not owned_root.exists()
            assert not created_runtime.exists()
        assert set(host_temp_root.glob("morphic-browser-*")) == outside_before
    finally:
        if mode == "timeout-cleanup-failure" and created_runtime is not None:
            assert created_runtime.exists()


def test_browser_runner_real_node_python_supervisor_controls_tree_and_forwards_output(
    tmp_path: Path,
) -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    identities_path = tmp_path / "real-boundary-identities.json"
    supervisor_probe_path = tmp_path / "real-boundary-supervisor.json"
    token_probe_path = tmp_path / "real-boundary-token"
    report_path = tmp_path / "real-boundary-report.json"
    test_temp_root = tmp_path / "real-boundary-temp"
    test_temp_root.mkdir()
    runtime_root = test_temp_root / "real-boundary-runtime"
    descendant_code = (
        "import signal,time;"
        "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
        "time.sleep(60)"
    )
    productive_code = (
        "import json,os,pathlib,psutil,signal,subprocess,sys,time;"
        f"child=subprocess.Popen([sys.executable,'-c',{descendant_code!r}],"
        "env=dict(os.environ),stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,"
        "stderr=subprocess.DEVNULL,start_new_session=sys.platform!='win32');"
        "records=["
        "{'pid':os.getpid(),'create_time':psutil.Process().create_time()},"
        "{'pid':child.pid,'create_time':psutil.Process(child.pid).create_time()}];"
        f"pathlib.Path({str(identities_path)!r}).write_text("
        "json.dumps(records),encoding='utf-8');"
        "print('real-productive-out',flush=True);"
        "print('real-productive-err',file=sys.stderr,flush=True);"
        "time.sleep(60)"
    )
    script = f"""
const fs = require("fs");
const {{spawn}} = require("child_process");
const runner = require({str(runner_path)!r});
const identitiesPath = {json.dumps(str(identities_path))};
const supervisorProbePath = {json.dumps(str(supervisor_probe_path))};
const tokenProbePath = {json.dumps(str(token_probe_path))};
const supervisorIdentitySidecarEnv = "MORPHIC_BROWSER_SUPERVISOR_IDENTITY_SIDECAR";
const reportPath = {json.dumps(str(report_path))};
const runtimeRoot = {json.dumps(str(runtime_root))};
const cleanEnv = Object.fromEntries(
  Object.entries(process.env).filter(([name]) => !name.toUpperCase().startsWith("MORPHIC_")),
);
const stdout = [];
const stderr = [];
let treeToken = null;
let supervised = null;
let supervisor = null;

async function waitFor(predicate, label) {{
  const deadline = Date.now() + 3000;
  while (!predicate()) {{
    if (Date.now() >= deadline) throw new Error(`${{label}} timed out`);
    await new Promise(resolve => setTimeout(resolve, 10));
  }}
}}

async function main() {{
  let primaryError = null;
  try {{
    fs.mkdirSync(runtimeRoot, {{recursive: true}});
    supervised = runner.spawnSupervised(
      {json.dumps(sys.executable)},
      ["-c", {json.dumps(productive_code)}],
      {{
        env: cleanEnv,
        onStdout: chunk => stdout.push(chunk),
        onStderr: chunk => stderr.push(chunk),
        readinessTimeoutMs: 3000,
      }},
      {{
        spawn(command, args, options) {{
          treeToken = options.env.{TREE_TOKEN_ENV};
          fs.writeFileSync(tokenProbePath, treeToken, {{flag: "wx", mode: 0o600}});
          supervisor = spawn(command, args, {{
            ...options,
            env: {{
              ...options.env,
              [supervisorIdentitySidecarEnv]: supervisorProbePath,
            }},
          }});
          return supervisor;
        }},
        stopTimeoutMs: 7000,
      }},
    );
    await runner.waitForSupervisorReady(supervised);
    await waitFor(() => fs.existsSync(identitiesPath), "productive identity publication");
    await waitFor(
      () => Buffer.concat(stdout).toString("utf8").includes("real-productive-out")
        && Buffer.concat(stderr).toString("utf8").includes("real-productive-err"),
      "productive output forwarding",
    );
  }} catch (error) {{
    primaryError = error;
    throw error;
  }} finally {{
    try {{
      await Promise.all([
        runner.cleanupGroup([supervised], runtimeRoot),
        supervised ? runner.stopSupervisor(supervised) : Promise.resolve(),
      ]);
    }} catch (cleanupError) {{
      throw runner.combinePrimaryAndCleanup(primaryError, cleanupError);
    }}
  }}
  const output = Buffer.concat(stdout).toString("utf8");
  const errors = Buffer.concat(stderr).toString("utf8");
  const state = runner.runnerState();
  fs.writeFileSync(reportPath, JSON.stringify({{
    output,
    errors,
    tokenLeaked: output.includes(treeToken)
      || errors.includes(treeToken)
      || JSON.stringify(state).includes(treeToken),
    runtimeExists: fs.existsSync(runtimeRoot),
    state,
  }}));
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    node_process: subprocess.Popen[str] | None = None
    supervisor_identity: tuple[int, float] | None = None
    tree_token: str | None = None
    identities: list[tuple[int, float]] = []
    primary_error: BaseException | None = None
    fallback_owner, fallback_baseline = _capture_harness_process_baseline()
    try:
        node_process = subprocess.Popen(
            ["node", "-e", script],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        supervisor_identity = _wait_for_published_supervisor_identity(
            supervisor_probe_path
        )
        tree_token = _wait_for_published_tree_token(token_probe_path)
        stdout_text, stderr_text = node_process.communicate(timeout=15)
        identities = _read_published_process_identities(identities_path)
        assert node_process.returncode == 0, stderr_text or stdout_text
        assert len(identities) == 2
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert report["output"].splitlines() == ["real-productive-out"]
        assert report["errors"].splitlines() == ["real-productive-err"]
        assert report["tokenLeaked"] is False
        assert report["runtimeExists"] is False
        assert report["state"] == {
            "activeSupervisorCount": 0,
            "activeRunCount": 0,
            "activeRuntimeRoots": [],
        }
        assert all(_published_identity_absent(identity) for identity in identities)
    except BaseException as error:
        primary_error = error
    finally:
        _finish_real_node_harness_in_sandbox(
            lambda: _finish_real_node_harness(
                node_process,
                supervisor_identity=supervisor_identity,
                token=tree_token,
                owner=fallback_owner,
                baseline=fallback_baseline,
                primary_error=primary_error,
                known_identities=(
                    identities or _read_published_process_identities(identities_path)
                ),
            ),
            sandbox_root=test_temp_root,
            runtime_root=runtime_root,
            primary_error=primary_error,
        )


def test_real_node_python_harness_early_assertion_cleans_tree_and_runtime(
    tmp_path: Path,
) -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    identities_path = tmp_path / "early-assertion-identities.json"
    supervisor_probe_path = tmp_path / "early-assertion-supervisor.json"
    token_probe_path = tmp_path / "early-assertion-token"
    report_path = tmp_path / "early-assertion-report.json"
    test_temp_root = tmp_path / "early-assertion-temp"
    test_temp_root.mkdir()
    runtime_root = test_temp_root / "early-assertion-runtime"
    descendant_code = (
        "import signal,time;"
        "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
        "time.sleep(60)"
    )
    productive_code = (
        "import json,os,pathlib,psutil,subprocess,sys,time;"
        f"child=subprocess.Popen([sys.executable,'-c',{descendant_code!r}],"
        "env=dict(os.environ),stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,"
        "stderr=subprocess.DEVNULL,start_new_session=sys.platform!='win32');"
        "records=["
        "{'pid':os.getpid(),'create_time':psutil.Process().create_time()},"
        "{'pid':child.pid,'create_time':psutil.Process(child.pid).create_time()}];"
        f"pathlib.Path({str(identities_path)!r}).write_text("
        "json.dumps(records),encoding='utf-8');"
        "time.sleep(60)"
    )
    script = f"""
const fs = require("fs");
const {{spawn}} = require("child_process");
const runner = require({str(runner_path)!r});
const identitiesPath = {json.dumps(str(identities_path))};
const supervisorProbePath = {json.dumps(str(supervisor_probe_path))};
const tokenProbePath = {json.dumps(str(token_probe_path))};
const supervisorIdentitySidecarEnv = "MORPHIC_BROWSER_SUPERVISOR_IDENTITY_SIDECAR";
const reportPath = {json.dumps(str(report_path))};
const runtimeRoot = {json.dumps(str(runtime_root))};
const cleanEnv = Object.fromEntries(
  Object.entries(process.env).filter(([name]) => !name.toUpperCase().startsWith("MORPHIC_")),
);
let supervised = null;
let supervisor = null;
let primaryError = null;

async function waitForIdentities() {{
  const deadline = Date.now() + 3000;
  while (!fs.existsSync(identitiesPath)) {{
    if (Date.now() >= deadline) throw new Error("identity publication timed out");
    await new Promise(resolve => setTimeout(resolve, 10));
  }}
}}

async function main() {{
  try {{
    fs.mkdirSync(runtimeRoot, {{recursive: true}});
    supervised = runner.spawnSupervised(
      {json.dumps(sys.executable)},
      ["-c", {json.dumps(productive_code)}],
      {{env: cleanEnv, readinessTimeoutMs: 3000}},
      {{
        spawn(command, args, options) {{
          fs.writeFileSync(
            tokenProbePath,
            options.env.{TREE_TOKEN_ENV},
            {{flag: "wx", mode: 0o600}},
          );
          supervisor = spawn(command, args, {{
            ...options,
            env: {{
              ...options.env,
              [supervisorIdentitySidecarEnv]: supervisorProbePath,
            }},
          }});
          return supervisor;
        }},
        stopTimeoutMs: 7000,
      }},
    );
    await runner.waitForSupervisorReady(supervised);
    await waitForIdentities();
    throw new Error("injected early harness assertion");
  }} catch (error) {{
    primaryError = error;
  }} finally {{
    await runner.cleanupGroup([supervised], runtimeRoot);
  }}
  if (primaryError?.message !== "injected early harness assertion") {{
    throw primaryError || new Error("early assertion was not observed");
  }}
  const state = runner.runnerState();
  fs.writeFileSync(reportPath, JSON.stringify({{
    runtimeExists: fs.existsSync(runtimeRoot),
    state,
  }}));
  process.exitCode = 29;
}}

main().catch(error => {{ console.error(error); process.exitCode = 99; }});
"""
    node_process: subprocess.Popen[str] | None = None
    supervisor_identity: tuple[int, float] | None = None
    tree_token: str | None = None
    identities: list[tuple[int, float]] = []
    primary_error: BaseException | None = None
    fallback_owner, fallback_baseline = _capture_harness_process_baseline()
    try:
        node_process = subprocess.Popen(
            ["node", "-e", script],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        supervisor_identity = _wait_for_published_supervisor_identity(
            supervisor_probe_path
        )
        tree_token = _wait_for_published_tree_token(token_probe_path)
        stdout_text, stderr_text = node_process.communicate(timeout=15)
        identities = _read_published_process_identities(identities_path)
        assert node_process.returncode == 29, stderr_text or stdout_text
        assert len(identities) == 2
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert report == {
            "runtimeExists": False,
            "state": {
                "activeSupervisorCount": 0,
                "activeRunCount": 0,
                "activeRuntimeRoots": [],
            },
        }
        assert all(_published_identity_absent(identity) for identity in identities)
    except BaseException as error:
        primary_error = error
    finally:
        _finish_real_node_harness_in_sandbox(
            lambda: _finish_real_node_harness(
                node_process,
                supervisor_identity=supervisor_identity,
                token=tree_token,
                owner=fallback_owner,
                baseline=fallback_baseline,
                primary_error=primary_error,
                known_identities=(
                    identities or _read_published_process_identities(identities_path)
                ),
            ),
            sandbox_root=test_temp_root,
            runtime_root=runtime_root,
            primary_error=primary_error,
        )


def test_run_group_real_delayed_duplicate_rejects_and_preserves_runtime(
    tmp_path: Path,
) -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    supervisor_path = BROWSER_DIR / "process_tree_supervisor.py"
    identities_path = tmp_path / "real-duplicate-identities.json"
    supervisor_probe_path = tmp_path / "real-duplicate-supervisor.json"
    token_probe_path = tmp_path / "real-duplicate-token"
    report_path = tmp_path / "real-duplicate-report.json"
    test_temp_root = tmp_path / "delayed-readiness-temp"
    test_temp_root.mkdir()
    node_environment = {
        **os.environ,
        "TMP": str(test_temp_root),
        "TEMP": str(test_temp_root),
        "TMPDIR": str(test_temp_root),
    }
    descendant_code = (
        "import signal,time;"
        "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
        "time.sleep(60)"
    )
    productive_code = (
        "import json,os,pathlib,psutil,subprocess,sys,time;"
        f"child=subprocess.Popen([sys.executable,'-c',{descendant_code!r}],"
        "env=dict(os.environ),stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,"
        "stderr=subprocess.DEVNULL,start_new_session=sys.platform!='win32');"
        "records=["
        "{'pid':os.getpid(),'create_time':psutil.Process().create_time()},"
        "{'pid':child.pid,'create_time':psutil.Process(child.pid).create_time()}];"
        f"pathlib.Path({str(identities_path)!r}).write_text("
        "json.dumps(records),encoding='utf-8');"
        "time.sleep(60)"
    )
    wrapper_code = f"""
import importlib.util
import os
import pathlib
import sys

path = pathlib.Path({str(supervisor_path)!r})
spec = importlib.util.spec_from_file_location("duplicate_ready_supervisor", path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
original_read_control = module._read_control
ready_stream = None

def publish_ready(ready_fd):
    global ready_stream
    ready_stream = os.fdopen(ready_fd, "w", encoding="utf-8", newline="\\n", closefd=True)
    ready_stream.write(module.READY_LINE + "\\n")
    ready_stream.flush()

def read_control(stream, request):
    original_read_control(stream, request)
    if request.requested.is_set() and ready_stream is not None:
        ready_stream.write(module.READY_LINE + "\\n")
        ready_stream.flush()
        ready_stream.close()

module._publish_ready = publish_ready
module._read_control = read_control
sys.argv = [
    str(path),
    "--ready-fd",
    "3",
    "--",
    sys.executable,
    "-c",
    {productive_code!r},
]
try:
    raise SystemExit(module.main())
finally:
    if ready_stream is not None and not ready_stream.closed:
        ready_stream.close()
"""
    script = f"""
const fs = require("fs");
const {{spawn}} = require("child_process");
const runner = require({str(runner_path)!r});
const identitiesPath = {json.dumps(str(identities_path))};
const supervisorProbePath = {json.dumps(str(supervisor_probe_path))};
const tokenProbePath = {json.dumps(str(token_probe_path))};
const supervisorIdentitySidecarEnv = "MORPHIC_BROWSER_SUPERVISOR_IDENTITY_SIDECAR";
const reportPath = {json.dumps(str(report_path))};
const wrapper = {json.dumps(wrapper_code)};
const primary = new Error("real duplicate cleanup primary");
let runtimeRoot = null;
let supervisor = null;
let treeToken = null;

function messages(error) {{
  return [String(error?.message || error), ...Array.from(error?.errors || [], messages).flat()];
}}

async function waitForIdentities() {{
  const deadline = Date.now() + 3000;
  while (!fs.existsSync(identitiesPath)) {{
    if (Date.now() >= deadline) throw new Error("identity publication timed out");
    await new Promise(resolve => setTimeout(resolve, 10));
  }}
}}

async function main() {{
  try {{
    const actual = await runner.runGroup(null, [], {{
      freePort: async () => 0,
      stopTimeoutMs: 7000,
      spawn(command, _args, options) {{
        runtimeRoot = options.env.MORPHIC_BROWSER_RUNTIME_ROOT;
        fs.mkdirSync(runtimeRoot, {{recursive: true}});
        treeToken = options.env.{TREE_TOKEN_ENV};
        fs.writeFileSync(tokenProbePath, treeToken, {{flag: "wx", mode: 0o600}});
        supervisor = spawn(command, ["-c", wrapper], {{
          ...options,
          env: {{
            ...options.env,
            [supervisorIdentitySidecarEnv]: supervisorProbePath,
          }},
        }});
        return supervisor;
      }},
      waitForHealth: async () => {{
        await waitForIdentities();
        throw primary;
      }},
    }}).catch(error => error);
    const allMessages = messages(actual);
    const state = runner.runnerState();
    if (!(actual instanceof AggregateError) || actual.errors[0] !== primary) throw actual;
    if (!allMessages.some(message => message.toLowerCase().includes("readiness"))) {{
      throw new Error(`delayed duplicate was not retained: ${{JSON.stringify(allMessages)}}`);
    }}
    if (!fs.existsSync(runtimeRoot)) throw new Error("real duplicate removed forensic runtime");
    if (supervisor.exitCode !== 0) throw new Error(`supervisor exit was ${{supervisor.exitCode}}`);
    if (allMessages.some(message => message.includes(treeToken))
        || JSON.stringify(state).includes(treeToken)) {{
      throw new Error("tree token leaked");
    }}
    fs.writeFileSync(reportPath, JSON.stringify({{runtimeRoot, state}}));
  }} finally {{
    if (supervisor?.exitCode === null) await runner.stopSupervisor(supervisor).catch(() => {{}});
  }}
}}

main().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    node_process: subprocess.Popen[str] | None = None
    supervisor_identity: tuple[int, float] | None = None
    tree_token: str | None = None
    identities: list[tuple[int, float]] = []
    runtime_root: Path | None = None
    primary_error: BaseException | None = None
    fallback_owner, fallback_baseline = _capture_harness_process_baseline()
    try:
        node_process = subprocess.Popen(
            ["node", "-e", script],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            env=node_environment,
        )
        supervisor_identity = _wait_for_published_supervisor_identity(
            supervisor_probe_path
        )
        tree_token = _wait_for_published_tree_token(token_probe_path)
        stdout_text, stderr_text = node_process.communicate(timeout=15)
        identities = _read_published_process_identities(identities_path)
        assert node_process.returncode == 0, stderr_text or stdout_text
        assert len(identities) == 2
        report = json.loads(report_path.read_text(encoding="utf-8"))
        runtime_root = Path(report["runtimeRoot"])
        assert report["state"]["activeSupervisorCount"] == 0
        assert report["state"]["activeRunCount"] == 0
        assert report["state"]["activeRuntimeRoots"] == [str(runtime_root)]
        assert runtime_root.exists()
        assert all(_published_identity_absent(identity) for identity in identities)
    except BaseException as error:
        primary_error = error
    finally:
        _finish_real_node_harness_in_sandbox(
            lambda: _finish_real_node_harness(
                node_process,
                supervisor_identity=supervisor_identity,
                token=tree_token,
                owner=fallback_owner,
                baseline=fallback_baseline,
                primary_error=primary_error,
                known_identities=(
                    identities or _read_published_process_identities(identities_path)
                ),
            ),
            sandbox_root=test_temp_root,
            runtime_root=runtime_root,
            primary_error=primary_error,
        )


def test_browser_runner_real_supervisor_failure_preserves_runtime_after_tree_absence(
    tmp_path: Path,
) -> None:
    runner_path = BROWSER_DIR / "run-isolated-tests.js"
    supervisor_path = BROWSER_DIR / "process_tree_supervisor.py"
    identities_path = tmp_path / "real-failure-identities.json"
    supervisor_probe_path = tmp_path / "real-failure-supervisor.json"
    token_probe_path = tmp_path / "real-failure-token"
    report_path = tmp_path / "real-failure-report.json"
    test_temp_root = tmp_path / "failure-preservation-temp"
    test_temp_root.mkdir()
    node_environment = {
        **os.environ,
        "TMP": str(test_temp_root),
        "TEMP": str(test_temp_root),
        "TMPDIR": str(test_temp_root),
    }
    descendant_code = (
        "import signal,time;"
        "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
        "time.sleep(60)"
    )
    productive_code = (
        "import json,os,pathlib,psutil,subprocess,sys,time;"
        f"child=subprocess.Popen([sys.executable,'-c',{descendant_code!r}],"
        "env=dict(os.environ),stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,"
        "stderr=subprocess.DEVNULL,start_new_session=sys.platform!='win32');"
        "records=["
        "{'pid':os.getpid(),'create_time':psutil.Process().create_time()},"
        "{'pid':child.pid,'create_time':psutil.Process(child.pid).create_time()}];"
        f"pathlib.Path({str(identities_path)!r}).write_text("
        "json.dumps(records),encoding='utf-8');"
        "time.sleep(60)"
    )
    wrapper_code = f"""
import importlib.util
import pathlib
import sys

path = pathlib.Path({str(supervisor_path)!r})
spec = importlib.util.spec_from_file_location("controlled_failure_supervisor", path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
tree_class = module._WindowsTree if sys.platform == "win32" else module._PosixTree
original_cleanup = tree_class.cleanup

def cleanup_then_fail(self, *, deadline, term_deadline=None):
    original_cleanup(self, deadline=deadline, term_deadline=term_deadline)
    raise module.AuthorityError("injected post-convergence cleanup failure")

tree_class.cleanup = cleanup_then_fail
sys.argv = [
    str(path),
    "--ready-fd",
    "3",
    "--",
    sys.executable,
    "-c",
    {productive_code!r},
]
raise SystemExit(module.main())
"""
    script = f"""
const fs = require("fs");
const {{spawn}} = require("child_process");
const runner = require({str(runner_path)!r});
const identitiesPath = {json.dumps(str(identities_path))};
const supervisorProbePath = {json.dumps(str(supervisor_probe_path))};
const tokenProbePath = {json.dumps(str(token_probe_path))};
const supervisorIdentitySidecarEnv = "MORPHIC_BROWSER_SUPERVISOR_IDENTITY_SIDECAR";
const reportPath = {json.dumps(str(report_path))};
const wrapper = {json.dumps(wrapper_code)};
const primary = new Error("controlled-primary-after-productive-start");
let runtimeRoot = null;
let supervisor = null;
let treeToken = null;
let spawnCalls = 0;

function serialize(error) {{
  return {{
    name: error?.name || "Error",
    message: String(error?.message || error),
    code: error?.code || null,
    errors: Array.from(error?.errors || [], serialize),
  }};
}}

async function waitForIdentityPublication() {{
  const deadline = Date.now() + 3000;
  while (!fs.existsSync(identitiesPath)) {{
    if (Date.now() >= deadline) throw new Error("productive identity publication timed out");
    await new Promise(resolve => setTimeout(resolve, 10));
  }}
}}

async function main() {{
  let actual = null;
  try {{
    actual = await runner.runGroup(null, [], {{
      freePort: async () => 0,
      stopTimeoutMs: 7000,
      spawn(command, _args, options) {{
        spawnCalls += 1;
        if (spawnCalls !== 1) throw new Error("Playwright must not start after primary failure");
        runtimeRoot = options.env.MORPHIC_BROWSER_RUNTIME_ROOT;
        fs.mkdirSync(runtimeRoot, {{recursive: true}});
        treeToken = options.env.{TREE_TOKEN_ENV};
        fs.writeFileSync(tokenProbePath, treeToken, {{flag: "wx", mode: 0o600}});
        supervisor = spawn(command, ["-c", wrapper], {{
          ...options,
          env: {{
            ...options.env,
            [supervisorIdentitySidecarEnv]: supervisorProbePath,
          }},
        }});
        return supervisor;
      }},
      waitForHealth: async () => {{
        await waitForIdentityPublication();
        throw primary;
      }},
    }}).catch(error => error);

    const serialized = serialize(actual);
    const state = runner.runnerState();
    fs.writeFileSync(reportPath, JSON.stringify({{
      error: serialized,
      primaryFirst: actual instanceof AggregateError && actual.errors[0] === primary,
      runtimeRoot,
      runtimeExists: fs.existsSync(runtimeRoot),
      supervisorExitCode: supervisor?.exitCode ?? null,
      state,
      tokenLeaked: JSON.stringify(serialized).includes(treeToken)
        || JSON.stringify(state).includes(treeToken),
    }}));
    process.exitCode = 23;
  }} finally {{
    if (supervisor?.exitCode === null) {{
      await runner.stopSupervisor(supervisor).catch(() => {{}});
    }}
  }}
}}

main().catch(error => {{ console.error("CONTROLLED_HARNESS_FAILURE", error); process.exitCode = 99; }});
"""
    started = time.monotonic()
    node_process: subprocess.Popen[str] | None = None
    supervisor_identity: tuple[int, float] | None = None
    tree_token: str | None = None
    identities: list[tuple[int, float]] = []
    runtime_root: Path | None = None
    primary_error: BaseException | None = None
    fallback_owner, fallback_baseline = _capture_harness_process_baseline()
    try:
        node_process = subprocess.Popen(
            ["node", "-e", script],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            env=node_environment,
        )
        supervisor_identity = _wait_for_published_supervisor_identity(
            supervisor_probe_path
        )
        tree_token = _wait_for_published_tree_token(token_probe_path)
        stdout_text, stderr_text = node_process.communicate(timeout=15)
        elapsed = time.monotonic() - started
        identities = _read_published_process_identities(identities_path)
        assert node_process.returncode == 23, stderr_text or stdout_text
        assert elapsed < 10
        assert "Unhandled" not in stderr_text
        assert "ERR_UNHANDLED_ERROR" not in stderr_text
        assert "CONTROLLED_HARNESS_FAILURE" not in stderr_text
        assert len(identities) == 2
        report = json.loads(report_path.read_text(encoding="utf-8"))
        runtime_root = Path(report["runtimeRoot"])
        assert runtime_root.is_relative_to(test_temp_root)
        assert report["error"]["name"] == "AggregateError"
        assert report["primaryFirst"] is True
        assert report["error"]["errors"][0]["message"] == (
            "controlled-primary-after-productive-start"
        )
        nested_messages = json.dumps(report["error"]["errors"][1])
        assert "Supervisor exited with code 1" in nested_messages
        assert report["supervisorExitCode"] == 1
        assert report["runtimeExists"] is True
        assert report["state"]["activeSupervisorCount"] == 0
        assert report["state"]["activeRunCount"] == 0
        assert report["state"]["activeRuntimeRoots"] == [str(runtime_root)]
        assert report["tokenLeaked"] is False
        assert all(_published_identity_absent(identity) for identity in identities)
    except BaseException as error:
        primary_error = error
    finally:
        _finish_real_node_harness_in_sandbox(
            lambda: _finish_real_node_harness(
                node_process,
                supervisor_identity=supervisor_identity,
                token=tree_token,
                owner=fallback_owner,
                baseline=fallback_baseline,
                primary_error=primary_error,
                known_identities=(
                    identities or _read_published_process_identities(identities_path)
                ),
            ),
            sandbox_root=test_temp_root,
            runtime_root=runtime_root,
            primary_error=primary_error,
        )


def test_browser_route_gates_use_central_deferred_finally_cleanup() -> None:
    source = (BROWSER_DIR / "workbench.spec.js").read_text(encoding="utf-8")
    manual_waits = re.findall(
        r"await\s+new Promise\(resolve\s*=>\s*\{\s*"
        r"release[A-Z]\w*\s*=\s*resolve;\s*\}\);",
        source,
    )
    manual_signals = re.findall(
        r"const\s+[A-Za-z_$]\w*\s*=\s*new Promise\(resolve\s*=>\s*\{\s*"
        r"[A-Za-z_$]\w*\s*=\s*resolve;\s*\}\);",
        source,
    )
    assert not manual_waits, f"manual blocking route gates remain: {len(manual_waits)}"
    assert not manual_signals, f"manual route signal promises remain: {len(manual_signals)}"
    assert "function createDeferred()" in source
    assert "async function releaseDeferredRoutes(page, ...deferreds)" in source

    deferred_test_titles = (
        "late registry hydration preserves the authoritative wizard step",
        "sources hydrate independently while the health read is delayed",
        "scan start is single-flight and cannot create competing poll loops",
        "New Case is blocked until a delayed scan start returns authoritative job id",
        "harmonization start is single-flight and keeps one active poll authority",
        "latest report selection wins when preview responses complete out of order",
        "failed New Case teardown preserves generation and authoritative polling",
        "stale bootstrap response cannot rehydrate a reset case",
        "stale health, sources and hardware loaders cannot rehydrate a reset case",
        "old completion cannot overwrite a newer scan in the same case generation",
    )
    for title in deferred_test_titles:
        marker = f"test('{title}'"
        assert marker in source, f"missing browser test: {title}"
        block = source.split(marker, 1)[1].split("\ntest(", 1)[0]
        assert "createDeferred()" in block, f"{title}: central deferred missing"
        assert "finally {" in block, f"{title}: finally cleanup missing"
        compact_block = "".join(block.split())
        assert "releaseDeferredRoutes(page," in compact_block, (
            f"{title}: central route cleanup missing"
        )
