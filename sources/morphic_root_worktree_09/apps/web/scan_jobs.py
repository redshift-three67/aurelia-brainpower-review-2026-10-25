from __future__ import annotations

import codecs
import errno
import hashlib
import json
import math
import os
import subprocess
import sys
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import re
import signal
import stat
from typing import Mapping, NoReturn, Protocol, cast

if not hasattr(signal, "SIGKILL"):
    signal.SIGKILL = 9  # type: ignore[attr-defined]

import psutil

from apps.web.durable_io import (
    _is_link_or_reparse,
    durable_mkdir_parents,
    durable_write_bytes,
)
from apps.web.authority_ids import (
    AuthorityIdError,
    validate_authority_id,
    validate_scan_job_id_for_creation,
)

# Windows: niedrige Prozess-Prioritaet, damit der Scan den Browser nicht einfriert
_CREATION_FLAGS = 0
if sys.platform == "win32":
    _CREATION_FLAGS = (
        subprocess.BELOW_NORMAL_PRIORITY_CLASS | subprocess.CREATE_NEW_PROCESS_GROUP
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


MAX_COMPLETED_SUBSTEPS = 8
_MAX_PROCESS_ID = (1 << 31) - 1
_MAX_CURSOR_POSITION = (1 << 63) - 1
_MAX_PROCESS_CREATE_TIME = 253_402_300_799.0
_SCAN_SERVICE_SHUTDOWN_TIMEOUT = 1.0
_IS_WINDOWS = os.name == "nt"

_RATIO_RE = re.compile(r"\[(\d+)/(\d+)\]")
_LEADING_MARKERS_RE = re.compile(r"^(?:\[[^\]]+\]\s*)+")
_MULTIPLEX_EXPORT_PREFIX = "MORPHIC_MULTIPLEX_EXPORT_V1 "
_MULTIPLEX_EXPORT_KEYS = {
    "version",
    "profile",
    "session_id",
    "json_path",
    "html_path",
}
_MAX_REPORT_SESSION_IDS = 2

_STAGE_DEFINITIONS = (
    ("phase1", "Phase 1", ("screening aller haupt-profile", "screening:")),
    ("top_profiles", "Phase 1", ("relevante profile", "top-profile", "top profile")),
    (
        "phase2",
        "Phase 2",
        ("phase 2", "vollstaendige analyse", "vollstandige analyse"),
    ),
    (
        "export",
        "Nachbereitung",
        (
            "export ",
            "export gespeichert",
            "export-basis",
            "export-pfade",
            "html-report",
            "html geschrieben",
            "export-ziel",
            "export ziel",
        ),
    ),
    ("synergy", "Nachbereitung", ("synergy",)),
    ("remedy", "Nachbereitung", ("remedy",)),
    ("interpretation", "Nachbereitung", ("deutungsbericht", "interpretation report")),
    ("trend", "Nachbereitung", ("trendbericht", "trend report")),
)


def _read_text(path: Path, limit: int | None = None) -> str:
    if not path.exists():
        return ""
    data = path.read_bytes()
    if limit is not None and len(data) > limit:
        data = data[-limit:]
    return data.decode("utf-8", errors="replace")


def _tail(path: Path, limit: int = 4000) -> str:
    return _read_text(path, limit=limit)


def _execution_command(command: list[str]) -> list[str]:
    if command and command[0].lower() in {"python", "python.exe"}:
        return [sys.executable, *command[1:]]
    return command


def _normalize_substep_label(line: str) -> str:
    cleaned = _LEADING_MARKERS_RE.sub("", line.strip())
    cleaned = cleaned.replace("...", "").strip(" -:")
    if ":" in cleaned and cleaned.lower().startswith("export"):
        return cleaned.split(":", 1)[0].strip()
    return cleaned


def _stage_details(line: str) -> tuple[int, str, str] | None:
    lowered = line.lower()
    for index, (stage_id, phase, markers) in enumerate(_STAGE_DEFINITIONS):
        if any(marker in lowered for marker in markers):
            return index, stage_id, phase
    return None


def _update_progress_state(
    lines: list[str],
    *,
    status: str,
    labels: list[str],
    seen_labels: set[str],
    current_substep: str | None,
    current_phase: str | None,
    progress_percent: float | None,
    stage_ids: list[str] | None = None,
    seen_stage_ids: set[str] | None = None,
    current_stage_id: str | None = None,
    phase2_profiles_started: bool = False,
    phase2_profiles_complete: bool = False,
) -> dict[str, object]:
    stage_ids = stage_ids if stage_ids is not None else []
    seen_stage_ids = seen_stage_ids if seen_stage_ids is not None else set()
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        lowered = line.lower()

        details = _stage_details(line)
        if details is None:
            if "harmonisierung" in line.lower():
                label = _normalize_substep_label(line)
                current_phase = "Nachbereitung"
                current_substep = label
                if label and label not in seen_labels:
                    labels.append(label)
                    seen_labels.add(label)
            continue

        stage_index, stage_id, phase = details
        ratio_match = _RATIO_RE.search(line)
        if (
            stage_id == "phase2"
            and ratio_match is not None
            and "vollstaendige analyse:" in lowered
        ):
            phase2_profiles_started = True
            phase2_profiles_complete = int(ratio_match.group(1)) >= int(ratio_match.group(2))
        export_index = next(
            index for index, definition in enumerate(_STAGE_DEFINITIONS)
            if definition[0] == "export"
        )
        if (
            stage_index >= export_index
            and phase2_profiles_started
            and not phase2_profiles_complete
        ):
            continue
        if current_stage_id:
            current_index = next(
                index for index, definition in enumerate(_STAGE_DEFINITIONS)
                if definition[0] == current_stage_id
            )
            if stage_index < current_index:
                continue
        label = _normalize_substep_label(line)
        if not label:
            continue

        if current_stage_id and current_stage_id != stage_id and current_stage_id not in seen_stage_ids:
            stage_ids.append(current_stage_id)
            seen_stage_ids.add(current_stage_id)
        current_phase = phase
        current_substep = label
        current_stage_id = stage_id

        ratio_progress = 0.0
        if ratio_match is not None and not label.lower().startswith("phase "):
            numerator = int(ratio_match.group(1))
            denominator = int(ratio_match.group(2))
            if denominator > 0:
                ratio_progress = min(max(numerator / denominator, 0.0), 1.0)
        progress_percent = max(
            progress_percent or 0.0,
            round(((stage_index + ratio_progress) / len(_STAGE_DEFINITIONS)) * 100, 1),
        )

        if label not in seen_labels:
            labels.append(label)
            seen_labels.add(label)

    if status == "completed":
        if current_stage_id and current_stage_id not in seen_stage_ids:
            stage_ids.append(current_stage_id)
            seen_stage_ids.add(current_stage_id)
        progress_percent = 100.0

    completed = labels[-MAX_COMPLETED_SUBSTEPS:]
    if status == "running" and current_substep in completed:
        completed = [label for label in completed if label != current_substep]

    return {
        "progress_percent": progress_percent,
        "current_phase": current_phase,
        "current_substep": current_substep,
        "current_stage_id": current_stage_id,
        "completed_substeps": completed,
        "completed_stage_ids": list(stage_ids),
        "_all_labels": labels,
        "_seen_labels": seen_labels,
        "_all_stage_ids": stage_ids,
        "_seen_stage_ids": seen_stage_ids,
        "_phase2_profiles_started": phase2_profiles_started,
        "_phase2_profiles_complete": phase2_profiles_complete,
    }


def _read_incremental(path: Path, start: int) -> tuple[str, int]:
    if not path.exists():
        return "", start
    with path.open("rb") as handle:
        handle.seek(start)
        data = handle.read()
        end = handle.tell()
    decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
    decoded = decoder.decode(data, final=False)
    pending, _ = decoder.getstate()
    return decoded, end - len(pending)


def _consume_lines(buffer: str, chunk: str) -> tuple[list[str], str]:
    merged = buffer + chunk
    if not merged:
        return [], ""
    complete = merged.endswith("\n") or merged.endswith("\r")
    lines = merged.splitlines()
    if complete:
        return lines, ""
    if not lines:
        return [], merged
    trailing = lines[-1]
    normalized = trailing.strip().lower()
    looks_complete = normalized.endswith(
        (
            "...",
            ":",
            "erstellt",
            "gespeichert",
            "abgeschlossen",
            "vorbereiten",
        )
    )
    if looks_complete and _stage_details(normalized) is not None:
        return lines, ""
    return lines[:-1], trailing


def _update_report_session_authority(
    lines: list[str],
    *,
    session_ids: set[str],
    invalid: bool,
) -> tuple[set[str], bool]:
    updated = set(session_ids)
    invalid_record = invalid
    for line in lines:
        if not line.startswith(_MULTIPLEX_EXPORT_PREFIX):
            continue
        try:
            payload = json.loads(line[len(_MULTIPLEX_EXPORT_PREFIX) :])
        except (json.JSONDecodeError, TypeError):
            invalid_record = True
            continue
        if (
            type(payload) is not dict
            or set(payload) != _MULTIPLEX_EXPORT_KEYS
            or type(payload.get("version")) is not int
            or payload["version"] != 1
            or type(payload.get("profile")) is not str
            or not payload["profile"]
            or type(payload.get("session_id")) is not str
            or not payload["session_id"]
            or type(payload.get("json_path")) is not str
            or not payload["json_path"]
            or type(payload.get("html_path")) is not str
            or not payload["html_path"]
        ):
            invalid_record = True
            continue
        try:
            for key in ("profile", "session_id", "json_path", "html_path"):
                payload[key].encode("utf-8")
        except UnicodeEncodeError:
            invalid_record = True
            continue
        session_id = payload["session_id"]
        if session_id in updated or len(updated) < _MAX_REPORT_SESSION_IDS:
            updated.add(session_id)
    return updated, invalid_record


def _resolved_report_session_id(
    session_ids: set[str], invalid: bool
) -> str | None:
    if invalid or len(session_ids) != 1:
        return None
    return next(iter(session_ids))


class ScanJobStore(Protocol):
    def start(
        self,
        command: list[str],
        owner_id: str | None = ...,
        env_overrides: Mapping[str, str] | None = ...,
        job_id: str | None = ...,
    ) -> dict[str, object]: ...

    def get(self, job_id: str) -> dict[str, object]: ...

    def observe(self, job_id: str) -> dict[str, object]: ...

    def observe_owned(
        self,
        job_id: str,
        *,
        expected_owner_id: str,
    ) -> dict[str, object]: ...

    def get_owned(
        self,
        job_id: str,
        *,
        expected_owner_id: str,
    ) -> dict[str, object]: ...

    def get_for_replay(
        self,
        job_id: str,
        *,
        expected_command: list[str],
        expected_owner_id: str | None,
    ) -> dict[str, object]: ...

    def stop(self, job_id: str) -> dict[str, object]: ...

    def stop_owned(
        self,
        job_id: str,
        *,
        expected_owner_id: str,
    ) -> dict[str, object]: ...


def _process_create_time(pid: int) -> float | None:
    try:
        return float(psutil.Process(pid).create_time())
    except (psutil.Error, OSError):
        return None


def _process_identity_matches(pid: int, expected_create_time: float | None) -> bool:
    if expected_create_time is None:
        return False
    actual = _process_create_time(pid)
    return actual is not None and abs(actual - expected_create_time) < 1e-6


def _strict_process_identity_matches(
    pid: int,
    expected_create_time: float | None,
) -> bool | None:
    """Return None only for confirmed exit; propagate unreadable-identity errors."""
    try:
        actual = float(psutil.Process(pid).create_time())
    except (ProcessLookupError, psutil.NoSuchProcess):
        return None
    except OSError as exc:
        if exc.errno == errno.ESRCH:
            return None
        raise
    if expected_create_time is None:
        return False
    return abs(actual - expected_create_time) < 1e-6


class ProcessAuthorityAmbiguousError(RuntimeError):
    pass


class ScanJobReplayAuthorityError(ProcessAuthorityAmbiguousError):
    pass


class ScanJobReplayOwnershipError(RuntimeError):
    pass


class ScanJobOwnershipError(RuntimeError):
    pass


class ScanJobReplayIdentityError(RuntimeError):
    pass


_OWNER_VALIDATION_NOT_REQUIRED = object()


def _raise_with_cleanup(
    message: str,
    primary: BaseException | None,
    cleanup_errors: list[BaseException],
) -> NoReturn:
    if primary is not None:
        if cleanup_errors:
            raise BaseExceptionGroup(message, [primary, *cleanup_errors]) from None
        raise primary.with_traceback(primary.__traceback__)
    if len(cleanup_errors) == 1:
        error = cleanup_errors[0]
        raise error.with_traceback(error.__traceback__)
    raise BaseExceptionGroup(message, cleanup_errors)


def _process_group_alive(
    process_group_id: int | None,
    process_group_token: str | None,
) -> bool:
    if process_group_id is None:
        return False
    if not process_group_token:
        raise ProcessAuthorityAmbiguousError("process group provenance token is missing")
    try:
        current_username = psutil.Process(os.getpid()).username()
    except psutil.Error as exc:
        raise ProcessAuthorityAmbiguousError("process owner could not be determined") from exc
    found_valid = False
    for process in psutil.process_iter(["pid", "status", "username"]):
        try:
            if process.info["status"] == psutil.STATUS_ZOMBIE:
                continue
            if process.info.get("username") not in {None, current_username}:
                continue
            pid = int(process.info["pid"])
            try:
                token = process.environ().get("MORPHIC_SCAN_GROUP_TOKEN")
            except (PermissionError, psutil.AccessDenied) as exc:
                raise ProcessAuthorityAmbiguousError(
                    f"same-owner process provenance is unreadable for pid {pid}"
                ) from exc
            if token == process_group_token:
                found_valid = True
                continue
            if (
                process_group_id is not None
                and process_group_id > 0
                and os.getpgid(pid) == process_group_id
            ):
                raise ProcessAuthorityAmbiguousError(
                    f"process-group provenance does not match for pid {pid}"
                )
        except ProcessAuthorityAmbiguousError:
            raise
        except (ProcessLookupError, psutil.NoSuchProcess):
            continue
        except OSError as exc:
            if exc.errno == errno.ESRCH:
                continue
            raise ProcessAuthorityAmbiguousError(
                "process authority could not be determined"
            ) from exc
        except psutil.Error as exc:
            raise ProcessAuthorityAmbiguousError(
                "process authority could not be determined"
            ) from exc
    return found_valid


def _job_runtime_active(job: "_LocalScanJob") -> bool:
    if sys.platform == "win32":
        return _windows_job_active(job)
    return job.process.poll() is None or _process_group_alive(
        job.process_group_id,
        job.process_group_token,
    )


def _scan_stop_authority_active(
    job: "_LocalScanJob",
    *,
    require_full_tree: bool,
) -> bool:
    supervisor_active = job.process.poll() is None
    if (
        supervisor_active
        and sys.platform != "win32"
        and job.process_create_time is not None
    ):
        supervisor_active = _strict_process_identity_matches(
            job.process.pid,
            job.process_create_time,
        ) is True
    if sys.platform == "win32":
        tree_active = _windows_job_active(job)
    elif require_full_tree or not supervisor_active:
        tree_active = _process_group_alive(
            job.process_group_id,
            job.process_group_token,
        )
    else:
        tree_active = False
    return supervisor_active or tree_active


def _build_gate_launch(
    *,
    gate_script: Path,
    release_path: Path,
    started_path: Path,
    result_path: Path,
    exec_command: list[str],
    process_environment: Mapping[str, str],
    process_group_token: str,
) -> tuple[list[str], dict[str, str]]:
    command = [
        sys.executable,
        str(gate_script),
        "--release",
        str(release_path),
        "--started",
        str(started_path),
        "--result",
        str(result_path),
        "--timeout",
        "30",
        "--",
        *exec_command,
    ]
    environment = dict(process_environment)
    environment["MORPHIC_SCAN_GATE_TOKEN"] = process_group_token
    return command, environment


class _RecoveredProcess:
    def __init__(
        self,
        pid: int,
        expected_create_time: float,
        result_path: Path,
    ) -> None:
        self.pid = pid
        self.expected_create_time = expected_create_time
        self.result_path = result_path

    def _result(self) -> int | None:
        try:
            data = self.result_path.read_bytes()
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise ProcessAuthorityAmbiguousError(
                "persisted scan process result is unreadable"
            ) from exc
        if re.fullmatch(rb"(?:0|[1-9][0-9]*|-[1-9][0-9]*)\n", data) is None:
            raise ProcessAuthorityAmbiguousError(
                "persisted scan process result is malformed"
            )
        return int(data)

    def poll(self) -> int | None:
        result = self._result()
        if result is not None:
            return result
        return None if _process_identity_matches(self.pid, self.expected_create_time) else 1

    def wait(self, timeout: float | None = None) -> int:
        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            result = self.poll()
            if result is not None:
                return result
            if deadline is not None and time.monotonic() >= deadline:
                raise subprocess.TimeoutExpired(str(self.pid), timeout)
            time.sleep(0.02)


@dataclass
class _LocalScanJob:
    job_id: str
    command: list[str]
    process: object
    stdout_path: Path
    stderr_path: Path
    created_at: str
    updated_at: str
    stdout_pos: int = 0
    stderr_pos: int = 0
    progress_percent: float | None = None
    current_phase: str | None = None
    current_substep: str | None = None
    completed_labels: list[str] = field(default_factory=list)
    seen_labels: set[str] = field(default_factory=set)
    completed_stage_ids: list[str] = field(default_factory=list)
    seen_stage_ids: set[str] = field(default_factory=set)
    current_stage_id: str | None = None
    stdout_buffer: str = ""
    stderr_buffer: str = ""
    owner_id: str | None = None
    artifact_paths: list[str] = field(default_factory=list)
    report_session_ids: set[str] = field(default_factory=set)
    report_session_invalid: bool = False
    forced_status: str | None = None
    phase2_profiles_started: bool = False
    phase2_profiles_complete: bool = False
    process_create_time: float | None = None
    process_group_id: int | None = None
    process_group_token: str | None = None
    start_released: bool = True
    windows_job_handle: int | None = None
    windows_job_lock: object = field(default_factory=threading.RLock, repr=False)
    windows_reaper_stop: threading.Event = field(
        default_factory=threading.Event,
        repr=False,
    )
    windows_reaper: threading.Thread | None = field(default=None, repr=False)
    windows_reaper_error: BaseException | None = field(default=None, repr=False)
    authority_namespace: str = "scan"
    recovered_authority_state_pending: bool = False


def _parse_persisted_job_payload(
    raw_payload: object,
    *,
    expected_authority_namespace: str,
) -> dict[str, object]:
    if not isinstance(raw_payload, dict):
        raise TypeError("persisted scan job state must be an object")
    payload = cast(dict[object, object], raw_payload)

    def value(name: str) -> object:
        if name not in payload:
            raise ValueError(f"persisted scan job field {name!r} is missing")
        return payload[name]

    def integer(
        name: str,
        *,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> int:
        raw = value(name)
        if isinstance(raw, bool) or not isinstance(raw, int):
            raise TypeError(f"persisted scan job field {name!r} must be an integer")
        if minimum is not None and raw < minimum:
            raise ValueError(f"persisted scan job field {name!r} is out of range")
        if maximum is not None and raw > maximum:
            raise ValueError(f"persisted scan job field {name!r} is out of range")
        return raw

    def number(name: str) -> float:
        raw = value(name)
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise TypeError(f"persisted scan job field {name!r} must be numeric")
        try:
            parsed = float(raw)
        except OverflowError as exc:
            raise ValueError(
                f"persisted scan job field {name!r} is out of range"
            ) from exc
        if not math.isfinite(parsed):
            raise ValueError(f"persisted scan job field {name!r} must be finite")
        return parsed

    def string(name: str, *, nonempty: bool = False) -> str:
        raw = value(name)
        if not isinstance(raw, str):
            raise TypeError(f"persisted scan job field {name!r} must be a string")
        if nonempty and not raw:
            raise ValueError(f"persisted scan job field {name!r} must not be empty")
        return raw

    def optional_string(name: str) -> str | None:
        raw = value(name)
        if raw is not None and not isinstance(raw, str):
            raise TypeError(
                f"persisted scan job field {name!r} must be a string or null"
            )
        return raw

    def string_list(name: str) -> list[str]:
        raw = value(name)
        if not isinstance(raw, list):
            raise TypeError(f"persisted scan job field {name!r} must be a list")
        if any(not isinstance(item, str) for item in raw):
            raise TypeError(
                f"persisted scan job field {name!r} must contain only strings"
            )
        return list(raw)

    def boolean(name: str) -> bool:
        raw = value(name)
        if not isinstance(raw, bool):
            raise TypeError(f"persisted scan job field {name!r} must be a boolean")
        return raw

    schema_version = integer("schema_version")
    if schema_version != 1:
        raise ValueError("persisted scan job schema version is unsupported")
    pid = integer("pid", minimum=1, maximum=_MAX_PROCESS_ID)
    process_group_id = integer(
        "process_group_id",
        minimum=1,
        maximum=_MAX_PROCESS_ID,
    )
    process_create_time = number("process_create_time")
    if not 0.0 < process_create_time <= _MAX_PROCESS_CREATE_TIME:
        raise ValueError("persisted scan job process creation time is out of range")
    stdout_pos = integer(
        "stdout_pos",
        minimum=0,
        maximum=_MAX_CURSOR_POSITION,
    )
    stderr_pos = integer(
        "stderr_pos",
        minimum=0,
        maximum=_MAX_CURSOR_POSITION,
    )
    progress_raw = value("progress_percent")
    progress_percent = None
    if progress_raw is not None:
        progress_percent = number("progress_percent")
        if not 0.0 <= progress_percent <= 100.0:
            raise ValueError("persisted scan job progress is out of range")
    forced_status = optional_string("forced_status")
    if forced_status not in {
        None,
        "completed",
        "failed",
        "stopped",
        "authority_ambiguous",
        "rollback_failed",
    }:
        raise ValueError("persisted scan job status is invalid")
    process_group_token = string("process_group_token", nonempty=True)
    if len(process_group_token) != 32 or any(
        character not in "0123456789abcdefABCDEF"
        for character in process_group_token
    ):
        raise ValueError("persisted scan job process token is invalid")
    authority_namespace = string("authority_namespace", nonempty=True)
    if authority_namespace != expected_authority_namespace:
        raise ValueError("persisted scan job authority namespace is invalid")
    raw_report_session_ids = payload.get("report_session_ids", [])
    if type(raw_report_session_ids) is not list or any(
        type(item) is not str or not item for item in raw_report_session_ids
    ):
        raise TypeError("persisted scan job report session ids are invalid")
    try:
        for item in raw_report_session_ids:
            item.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise TypeError("persisted scan job report session ids are invalid") from exc
    if len(set(raw_report_session_ids)) > _MAX_REPORT_SESSION_IDS:
        raise TypeError("persisted scan job report session ids are invalid")
    raw_report_session_invalid = payload.get("report_session_invalid", False)
    if type(raw_report_session_invalid) is not bool:
        raise TypeError("persisted scan job report session state is invalid")

    persisted_job_id = value("job_id")
    try:
        validate_authority_id(persisted_job_id)
    except AuthorityIdError as exc:
        raise ProcessAuthorityAmbiguousError(
            "persisted scan job authority is unreadable"
        ) from exc

    return {
        "job_id": cast(str, persisted_job_id),
        "command": string_list("command"),
        "pid": pid,
        "process_create_time": process_create_time,
        "process_group_id": process_group_id,
        "process_group_token": process_group_token,
        "stdout_path": string("stdout_path", nonempty=True),
        "stderr_path": string("stderr_path", nonempty=True),
        "created_at": string("created_at", nonempty=True),
        "updated_at": string("updated_at", nonempty=True),
        "stdout_pos": stdout_pos,
        "stderr_pos": stderr_pos,
        "progress_percent": progress_percent,
        "current_phase": optional_string("current_phase"),
        "current_substep": optional_string("current_substep"),
        "completed_labels": string_list("completed_labels"),
        "completed_stage_ids": string_list("completed_stage_ids"),
        "current_stage_id": optional_string("current_stage_id"),
        "stdout_buffer": string("stdout_buffer"),
        "stderr_buffer": string("stderr_buffer"),
        "owner_id": optional_string("owner_id"),
        "artifact_paths": string_list("artifact_paths"),
        "report_session_ids": set(raw_report_session_ids),
        "report_session_invalid": raw_report_session_invalid,
        "forced_status": forced_status,
        "phase2_profiles_started": boolean("phase2_profiles_started"),
        "phase2_profiles_complete": boolean("phase2_profiles_complete"),
        "start_released": boolean("start_released"),
        "authority_namespace": authority_namespace,
    }


def _windows_job_name(
    process_group_token: str | None,
    authority_namespace: str = "scan",
) -> str:
    if not process_group_token:
        raise ProcessAuthorityAmbiguousError("Windows job authority token is missing")
    digest = hashlib.sha256(process_group_token.encode("utf-8")).hexdigest()[:32]
    prefix = (
        "MorphicHarmonization"
        if authority_namespace == "harmonization"
        else "MorphicScan"
    )
    return f"Local\\{prefix}-{digest}"


def _create_windows_job(
    process: object,
    process_group_token: str | None,
    authority_namespace: str = "scan",
) -> int:
    import ctypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
    kernel32.CreateJobObjectW.restype = ctypes.c_void_p
    kernel32.AssignProcessToJobObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    kernel32.AssignProcessToJobObject.restype = ctypes.c_int
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel32.CloseHandle.restype = ctypes.c_int
    handle = kernel32.CreateJobObjectW(
        None,
        _windows_job_name(process_group_token, authority_namespace),
    )
    if not handle:
        raise OSError(ctypes.get_last_error(), "Windows job object could not be created")
    process_handle = getattr(process, "_handle", None)
    if process_handle is None or not kernel32.AssignProcessToJobObject(
        handle, ctypes.c_void_p(int(process_handle))
    ):
        error = ctypes.get_last_error()
        primary_error = OSError(
            error, "scan supervisor could not be assigned to Windows job"
        )
        if not kernel32.CloseHandle(handle):
            close_error = OSError(
                ctypes.get_last_error(), "Windows job handle could not be closed"
            )
            raise ExceptionGroup(
                "Windows job assignment and handle cleanup failed",
                [primary_error, close_error],
            )
        raise primary_error
    kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    kernel32.DuplicateHandle.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_uint,
        ctypes.c_int,
        ctypes.c_uint,
    ]
    kernel32.DuplicateHandle.restype = ctypes.c_int
    retained_handle = ctypes.c_void_p()
    if not kernel32.DuplicateHandle(
        kernel32.GetCurrentProcess(),
        ctypes.c_void_p(int(handle)),
        ctypes.c_void_p(int(process_handle)),
        ctypes.byref(retained_handle),
        0,
        False,
        0x00000002,
    ):
        error = ctypes.get_last_error()
        primary_error = OSError(
            error, "Windows job authority could not be retained by supervisor"
        )
        if not kernel32.CloseHandle(handle):
            raise ExceptionGroup(
                "Windows job retention and handle cleanup failed",
                [
                    primary_error,
                    OSError(
                        ctypes.get_last_error(),
                        "Windows job handle could not be closed",
                    ),
                ],
            )
        raise primary_error
    return int(handle)


def _close_windows_job_handle(job: _LocalScanJob) -> None:
    with job.windows_job_lock:  # type: ignore[attr-defined]
        if job.windows_job_handle is None:
            return
        import ctypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
        kernel32.CloseHandle.restype = ctypes.c_int
        if not kernel32.CloseHandle(ctypes.c_void_p(int(job.windows_job_handle))):
            raise OSError(ctypes.get_last_error(), "Windows job handle could not be closed")
        job.windows_job_handle = None
        job.windows_reaper_stop.set()


def _terminate_windows_job(job: _LocalScanJob) -> None:
    import ctypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenJobObjectW.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.c_wchar_p]
    kernel32.OpenJobObjectW.restype = ctypes.c_void_p
    kernel32.TerminateJobObject.argtypes = [ctypes.c_void_p, ctypes.c_uint]
    kernel32.TerminateJobObject.restype = ctypes.c_int
    with job.windows_job_lock:  # type: ignore[attr-defined]
        handle = job.windows_job_handle
        if handle is None:
            handle = kernel32.OpenJobObjectW(
                0x000C,  # JOB_OBJECT_QUERY | JOB_OBJECT_TERMINATE
                False,
                _windows_job_name(job.process_group_token, job.authority_namespace),
            )
            if handle:
                job.windows_job_handle = int(handle)
        if not handle:
            raise ProcessAuthorityAmbiguousError(
                "stable Windows job authority is unavailable"
            )
        if not kernel32.TerminateJobObject(ctypes.c_void_p(int(handle)), 1):
            raise OSError(ctypes.get_last_error(), "Windows job termination failed")


def _converge_windows_authority(job: _LocalScanJob) -> None:
    failures: list[BaseException] = []
    try:
        _terminate_windows_job(job)
    except BaseException as exc:
        failures.append(exc)
    if job.process.poll() is None:
        try:
            job.process.wait(timeout=5)
        except BaseException as exc:
            failures.append(exc)
    deadline = time.monotonic() + 5.0
    while True:
        try:
            active = _windows_job_active(job)
        except BaseException as exc:
            failures.append(exc)
            break
        if not active:
            break
        if time.monotonic() >= deadline:
            failures.append(RuntimeError("Windows process tree stop was not confirmed"))
            break
        time.sleep(0.05)
    if job.windows_job_handle is not None:
        try:
            _close_windows_job_handle(job)
        except BaseException as exc:
            failures.append(exc)
    reaper = job.windows_reaper
    if reaper is not None and reaper is not threading.current_thread():
        reaper.join(timeout=1)
        if reaper.is_alive():
            failures.append(RuntimeError("Windows job reaper did not stop"))
    if failures:
        raise BaseExceptionGroup("Windows process tree convergence failed", failures)


def _windows_job_active(job: _LocalScanJob) -> bool:
    with job.windows_job_lock:  # type: ignore[attr-defined]
        return _windows_job_active_locked(job)


def _windows_job_active_locked(job: _LocalScanJob) -> bool:
    import ctypes

    class BasicAccountingInformation(ctypes.Structure):
        _fields_ = [
            ("TotalUserTime", ctypes.c_longlong),
            ("TotalKernelTime", ctypes.c_longlong),
            ("ThisPeriodTotalUserTime", ctypes.c_longlong),
            ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
            ("TotalPageFaultCount", ctypes.c_uint),
            ("TotalProcesses", ctypes.c_uint),
            ("ActiveProcesses", ctypes.c_uint),
            ("TotalTerminatedProcesses", ctypes.c_uint),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenJobObjectW.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.c_wchar_p]
    kernel32.OpenJobObjectW.restype = ctypes.c_void_p
    kernel32.QueryInformationJobObject.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.c_void_p,
        ctypes.c_uint,
        ctypes.c_void_p,
    ]
    kernel32.QueryInformationJobObject.restype = ctypes.c_int
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel32.CloseHandle.restype = ctypes.c_int
    handle = job.windows_job_handle
    opened_here = False
    if handle is None:
        handle = kernel32.OpenJobObjectW(
            0x0004,  # JOB_OBJECT_QUERY
            False,
            _windows_job_name(job.process_group_token, job.authority_namespace),
        )
        if not handle:
            error = ctypes.get_last_error()
            if error == 2 and job.process.poll() is not None:
                return False
            raise ProcessAuthorityAmbiguousError(
                f"Windows job activity is unavailable ({error})"
            )
        opened_here = True
    information = BasicAccountingInformation()
    queried = bool(
        kernel32.QueryInformationJobObject(
            ctypes.c_void_p(int(handle)),
            1,
            ctypes.byref(information),
            ctypes.sizeof(information),
            None,
        )
    )
    error = ctypes.get_last_error()
    primary_error = None if queried else ProcessAuthorityAmbiguousError(
        f"Windows job activity could not be queried ({error})"
    )
    if opened_here:
        if not kernel32.CloseHandle(ctypes.c_void_p(int(handle))):
            close_error = OSError(
                ctypes.get_last_error(), "Windows job handle could not be closed"
            )
            if primary_error is not None:
                raise BaseExceptionGroup(
                    "Windows job query and handle cleanup failed",
                    [primary_error, close_error],
                )
            raise close_error
    if primary_error is not None:
        raise primary_error
    active = information.ActiveProcesses > 0
    if not active and not opened_here:
        _close_windows_job_handle(job)
    return active


def _start_windows_job_reaper(job: _LocalScanJob) -> None:
    if sys.platform != "win32" or job.windows_job_handle is None:
        return
    with job.windows_job_lock:  # type: ignore[attr-defined]
        if job.windows_reaper is not None and job.windows_reaper.is_alive():
            return
        job.windows_reaper_stop.clear()
        stop_event = job.windows_reaper_stop
        job_id = job.job_id

        def reap() -> None:
            while not stop_event.wait(0.05):
                try:
                    if not _windows_job_active(job):
                        return
                except BaseException as exc:
                    if _windows_reaper_query_error_is_retryable(exc):
                        continue
                    with job.windows_job_lock:  # type: ignore[attr-defined]
                        if job.windows_reaper_error is None:
                            job.windows_reaper_error = exc
                    stop_event.wait()
                    return

        job.windows_reaper = threading.Thread(
            target=reap,
            name=f"scan-job-reaper-{job_id}",
            daemon=True,
        )
        job.windows_reaper.start()


def _windows_reaper_query_error_is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, BaseExceptionGroup):
        return all(
            _windows_reaper_query_error_is_retryable(child)
            for child in exc.exceptions
        )
    return isinstance(
        exc,
        (ProcessAuthorityAmbiguousError, OSError, psutil.Error),
    )


def _remaining_time(deadline: float) -> float:
    return max(0.0, deadline - time.monotonic())


def _acquire_before(lock: object, deadline: float) -> bool:
    return bool(lock.acquire(timeout=_remaining_time(deadline)))  # type: ignore[attr-defined]


def _cleanup_windows_jobs(
    jobs: list[_LocalScanJob],
    deadline: float,
) -> list[BaseException]:
    failures: list[BaseException] = []
    for job in jobs:
        job.windows_reaper_stop.set()

    for job in jobs:
        if job.windows_job_handle is None:
            continue
        if not _acquire_before(job.windows_job_lock, deadline):
            failures.append(RuntimeError("Windows job handle cleanup timed out"))
            continue
        try:
            _close_windows_job_handle(job)
        except BaseException as exc:
            failures.append(exc)
        finally:
            job.windows_job_lock.release()  # type: ignore[attr-defined]

    for job in jobs:
        reaper = job.windows_reaper
        if reaper is None or reaper is threading.current_thread():
            continue
        try:
            reaper.join(timeout=_remaining_time(deadline))
        except BaseException as exc:
            failures.append(exc)
            continue
        if reaper.is_alive():
            failures.append(RuntimeError("Windows job reaper did not stop"))

    for job in jobs:
        if not _acquire_before(job.windows_job_lock, deadline):
            failures.append(RuntimeError("Windows job reaper error cleanup timed out"))
            continue
        try:
            if job.windows_reaper_error is not None:
                failures.append(job.windows_reaper_error)
                job.windows_reaper_error = None
        finally:
            job.windows_job_lock.release()  # type: ignore[attr-defined]
    return failures


def _open_pidfd(pid: int) -> int:
    opener = getattr(os, "pidfd_open", None)
    sender = getattr(signal, "pidfd_send_signal", None)
    if opener is None or sender is None:
        raise RuntimeError("stable POSIX process handles are unavailable")
    return int(opener(pid, 0))


def _close_process_handles(handles: list[int]) -> list[BaseException]:
    failures: list[BaseException] = []
    for descriptor in handles:
        try:
            os.close(descriptor)
        except BaseException as exc:
            failures.append(exc)
    return failures


def _raise_unreleased_start_failure(
    process: object,
    descriptor: int,
    primary_error: BaseException,
) -> NoReturn:
    cleanup_errors: list[BaseException] = []
    try:
        signal.pidfd_send_signal(descriptor, signal.SIGKILL, None, 0)
    except BaseException as exc:
        cleanup_errors.append(exc)
    finally:
        cleanup_errors.extend(_close_process_handles([descriptor]))
    try:
        process.wait(timeout=35)
    except BaseException as exc:
        cleanup_errors.append(exc)
    if cleanup_errors:
        raise BaseExceptionGroup(
            "scan startup failed and stable cleanup was incomplete",
            [primary_error, *cleanup_errors],
        )
    raise primary_error


def _token_process_pidfds(
    process_group_id: int | None,
    process_group_token: str | None,
    trusted_supervisor_identity: tuple[int, float | None] | None = None,
) -> list[int]:
    if not process_group_token:
        return []
    try:
        current_username = psutil.Process(os.getpid()).username()
    except psutil.Error as exc:
        raise ProcessAuthorityAmbiguousError("process owner could not be determined") from exc
    handles: list[int] = []
    try:
        for process in psutil.process_iter(["pid", "status", "username"]):
            descriptor: int | None = None
            try:
                pid = int(process.info["pid"])
                if process.info["status"] == psutil.STATUS_ZOMBIE:
                    continue
                if process.info.get("username") not in {None, current_username}:
                    continue
                if trusted_supervisor_identity is not None and pid == trusted_supervisor_identity[0]:
                    supervisor_state = _strict_process_identity_matches(
                        pid, trusted_supervisor_identity[1]
                    )
                    if supervisor_state is not False:
                        continue
                try:
                    token = process.environ().get("MORPHIC_SCAN_GROUP_TOKEN")
                except (PermissionError, psutil.AccessDenied) as exc:
                    raise ProcessAuthorityAmbiguousError(
                        f"same-owner process provenance is unreadable for pid {pid}"
                    ) from exc
                if token != process_group_token:
                    if (
                        process_group_id is not None
                        and process_group_id > 0
                        and os.getpgid(pid) == process_group_id
                    ):
                        raise ProcessAuthorityAmbiguousError(
                            f"process-group provenance does not match for pid {pid}"
                        )
                    continue
                try:
                    descriptor = _open_pidfd(pid)
                except ProcessLookupError:
                    continue
                except OSError as exc:
                    if exc.errno == errno.ESRCH:
                        continue
                    raise ProcessAuthorityAmbiguousError(
                        f"stable process handle could not be acquired for pid {pid}"
                    ) from exc
                except Exception as exc:
                    raise ProcessAuthorityAmbiguousError(
                        f"stable process handle could not be acquired for pid {pid}"
                    ) from exc
                try:
                    stable_token = process.environ().get("MORPHIC_SCAN_GROUP_TOKEN")
                except (PermissionError, psutil.AccessDenied) as exc:
                    raise ProcessAuthorityAmbiguousError(
                        f"stable process provenance is unreadable for pid {pid}"
                    ) from exc
                if stable_token != process_group_token:
                    raise ProcessAuthorityAmbiguousError(
                        f"stable process provenance does not match for pid {pid}"
                    )
                handles.append(descriptor)
                descriptor = None
            except ProcessAuthorityAmbiguousError:
                raise
            except (ProcessLookupError, psutil.NoSuchProcess):
                continue
            except OSError as exc:
                if exc.errno == errno.ESRCH:
                    continue
                raise ProcessAuthorityAmbiguousError(
                    "process authority could not be determined"
                ) from exc
            except psutil.Error as exc:
                raise ProcessAuthorityAmbiguousError(
                    "process authority could not be determined"
                ) from exc
            except Exception as exc:
                raise ProcessAuthorityAmbiguousError(
                    "process authority could not be determined"
                ) from exc
            finally:
                if descriptor is not None:
                    close_failures = _close_process_handles([descriptor])
                    active_error = sys.exception()
                    if close_failures and active_error is not None:
                        raise BaseExceptionGroup(
                            "process authority validation and handle cleanup failed",
                            [active_error, *close_failures],
                        )
                    if close_failures:
                        raise BaseExceptionGroup(
                            "stable process handle cleanup failed",
                            close_failures,
                        )
        return handles
    except BaseException as primary_error:
        close_failures = _close_process_handles(handles)
        if close_failures:
            raise BaseExceptionGroup(
                "process authority discovery and handle cleanup failed",
                [primary_error, *close_failures],
            )
        raise


def _signal_posix_authority(job: _LocalScanJob, sent_signal: int) -> int:
    handles: list[int] = []
    supervisor_descriptor: int | None = None
    trusted_supervisor_identity: tuple[int, float | None] | None = None
    try:
        if job.process.poll() is None:
            try:
                supervisor_descriptor = _open_pidfd(job.process.pid)
            except ProcessLookupError:
                supervisor_descriptor = None
            except OSError as exc:
                if exc.errno != errno.ESRCH:
                    raise ProcessAuthorityAmbiguousError(
                        "stable supervisor handle could not be acquired"
                    ) from exc
            except Exception as exc:
                raise ProcessAuthorityAmbiguousError(
                    "stable supervisor handle could not be acquired"
                ) from exc
            supervisor_valid = False
            if supervisor_descriptor is not None:
                try:
                    identity_matches = _strict_process_identity_matches(
                        job.process.pid,
                        job.process_create_time,
                    )
                    supervisor_valid = bool(identity_matches) and (
                        os.getpgid(job.process.pid) == job.process_group_id
                    )
                except ProcessLookupError:
                    supervisor_valid = False
                except OSError as exc:
                    if exc.errno == errno.ESRCH:
                        supervisor_valid = False
                    else:
                        raise ProcessAuthorityAmbiguousError(
                            "stable supervisor identity could not be revalidated"
                        ) from exc
                except Exception as exc:
                    raise ProcessAuthorityAmbiguousError(
                        "stable supervisor identity could not be revalidated"
                    ) from exc
            if supervisor_valid:
                handles.append(supervisor_descriptor)
                trusted_supervisor_identity = (
                    job.process.pid,
                    job.process_create_time,
                )
                supervisor_descriptor = None
        handles.extend(
            _token_process_pidfds(
                job.process_group_id,
                job.process_group_token,
                trusted_supervisor_identity,
            )
        )
        sender = getattr(signal, "pidfd_send_signal", None)
        if sender is None:
            raise RuntimeError("stable POSIX process signalling is unavailable")
        failures: list[OSError] = []
        for descriptor in handles:
            try:
                sender(descriptor, sent_signal, None, 0)
            except ProcessLookupError:
                continue
            except OSError as exc:
                if exc.errno == errno.ESRCH:
                    continue
                failures.append(exc)
        if failures:
            raise BaseExceptionGroup(
                "stable POSIX process signalling failed",
                failures,
            )
        return len(handles)
    finally:
        closing = list(handles)
        if supervisor_descriptor is not None:
            closing.append(supervisor_descriptor)
        close_failures = _close_process_handles(closing)
        active_error = sys.exception()
        if close_failures:
            if active_error is not None:
                raise BaseExceptionGroup(
                    "stable POSIX signalling and handle cleanup failed",
                    [active_error, *close_failures],
                )
            raise BaseExceptionGroup(
                "stable process handle cleanup failed",
                close_failures,
            )


def _posix_authority_active(job: _LocalScanJob) -> bool:
    return job.process.poll() is None or _process_group_alive(
        job.process_group_id,
        job.process_group_token,
    )


def _contains_authority_ambiguity(exc: BaseException) -> bool:
    if isinstance(exc, ProcessAuthorityAmbiguousError):
        return True
    if isinstance(exc, BaseExceptionGroup):
        return any(_contains_authority_ambiguity(child) for child in exc.exceptions)
    return False


def _converge_posix_authority(job: _LocalScanJob) -> None:
    failures: list[BaseException] = []
    may_signal = True
    try:
        if _signal_posix_authority(job, signal.SIGTERM) == 0:
            failures.append(RuntimeError("no stable POSIX process authority was found"))
            may_signal = False
    except ProcessAuthorityAmbiguousError as exc:
        failures.append(exc)
        may_signal = False
    except BaseException as exc:
        failures.append(exc)
        if _contains_authority_ambiguity(exc):
            may_signal = False
    deadline = time.monotonic() + 1.0
    try:
        active = _posix_authority_active(job)
    except BaseException as exc:
        failures.append(exc)
        active = True
        may_signal = False
    while active and time.monotonic() < deadline:
        time.sleep(0.02)
        try:
            active = _posix_authority_active(job)
        except BaseException as exc:
            failures.append(exc)
            active = True
            may_signal = False
            break
    deadline = time.monotonic() + 5.0
    kill_attempts = 0
    while active and may_signal and time.monotonic() < deadline and kill_attempts < 3:
        kill_attempts += 1
        try:
            if _signal_posix_authority(job, signal.SIGKILL) == 0:
                failures.append(
                    RuntimeError("remaining POSIX process authority could not be acquired")
                )
                break
        except ProcessAuthorityAmbiguousError as exc:
            failures.append(exc)
            may_signal = False
            break
        except BaseException as exc:
            failures.append(exc)
            if _contains_authority_ambiguity(exc):
                may_signal = False
                break
            time.sleep(0.02)
            continue
        time.sleep(0.02)
        try:
            active = _posix_authority_active(job)
        except BaseException as exc:
            failures.append(exc)
            active = True
            may_signal = False
            break
    try:
        active = _posix_authority_active(job)
    except BaseException as exc:
        failures.append(exc)
        active = True
    if active:
        failures.append(RuntimeError("scan process authority stop was not confirmed"))
    if failures:
        raise BaseExceptionGroup("POSIX process tree convergence failed", failures)


def _rollback_scan_authority(job: _LocalScanJob) -> None:
    process = job.process
    if sys.platform == "win32":
        _converge_windows_authority(job)
        return
    if process.poll() is not None and not _process_group_alive(
        job.process_group_id,
        job.process_group_token,
    ):
        return
    if process.poll() is None and not _process_identity_matches(
        process.pid,
        job.process_create_time,
    ):
        raise RuntimeError("scan rollback refused mismatched supervisor identity")
    if job.process_group_id is None:
        raise RuntimeError("scan rollback has no process-group authority")
    _converge_posix_authority(job)
    try:
        process.wait(timeout=5)
    except (subprocess.TimeoutExpired, psutil.TimeoutExpired):
        pass


class LocalScanJobService:
    """Durable local process authority.

    On Windows, ``root`` must be provisioned with an owner-restricted ACL by the
    deployment environment. This service validates the durable directory chain
    and rejects reparse points; POSIX modes are not treated as Windows DACLs.
    """

    def __init__(
        self,
        root: Path,
        cwd: Path | None = None,
        *,
        authority_namespace: str = "scan",
    ) -> None:
        self.root = root
        self.cwd = cwd or Path(__file__).resolve().parents[2]
        self.authority_namespace = authority_namespace
        self._jobs: dict[str, _LocalScanJob] = {}
        self._lock = threading.Lock()
        self._start_lock = threading.Lock()
        self._start_condition = threading.Condition(threading.Lock())
        self._active_starts = 0
        self._process_lock_state = threading.local()
        self._close_lock = threading.Lock()
        self._starts_closed = False
        self._shutdown_complete = False
        self._ensure_authority_root()
        self._recover_jobs()

    def _ensure_authority_root(self) -> None:
        durable_mkdir_parents(self.root, mode=0o700)
        root_attributes = os.lstat(self.root)
        if _is_link_or_reparse(root_attributes):
            raise ProcessAuthorityAmbiguousError(
                "scan process authority root is a reparse point"
            )
        if not stat.S_ISDIR(root_attributes.st_mode):
            raise ProcessAuthorityAmbiguousError(
                "scan process authority root is not a directory"
            )
        if _IS_WINDOWS:
            return
        os.chmod(self.root, 0o700)
        verified_attributes = os.stat(self.root, follow_symlinks=False)
        if _is_link_or_reparse(verified_attributes):
            raise ProcessAuthorityAmbiguousError(
                "scan process authority root is a reparse point"
            )
        if not stat.S_ISDIR(verified_attributes.st_mode):
            raise ProcessAuthorityAmbiguousError(
                "scan process authority root is not a directory"
            )
        if stat.S_IMODE(verified_attributes.st_mode) != 0o700:
            raise ProcessAuthorityAmbiguousError(
                "scan process authority root permissions are not 0700"
            )

    def close(self) -> None:
        deadline = time.monotonic() + _SCAN_SERVICE_SHUTDOWN_TIMEOUT
        failures: list[BaseException] = []
        if not _acquire_before(self._start_condition, deadline):
            raise BaseExceptionGroup(
                "scan job service shutdown failed",
                [RuntimeError("scan start admission shutdown timed out")],
            )
        try:
            self._starts_closed = True
            self._start_condition.notify_all()
        finally:
            self._start_condition.release()

        if not _acquire_before(self._close_lock, deadline):
            raise BaseExceptionGroup(
                "scan job service shutdown failed",
                [RuntimeError("scan job cleanup lock timed out")],
            )
        try:
            if self._shutdown_complete:
                return

            starts_converged = False
            if not _acquire_before(self._start_condition, deadline):
                failures.append(RuntimeError("accepted scan start wait timed out"))
            else:
                try:
                    while self._active_starts > 0:
                        remaining = _remaining_time(deadline)
                        if remaining <= 0 or not self._start_condition.wait(remaining):
                            break
                    starts_converged = self._active_starts == 0
                    if not starts_converged:
                        failures.append(RuntimeError("accepted scan starts did not stop"))
                finally:
                    self._start_condition.release()

            jobs: list[_LocalScanJob] = []
            snapshot_complete = _acquire_before(self._lock, deadline)
            if snapshot_complete:
                try:
                    jobs = list(self._jobs.values())
                finally:
                    self._lock.release()
            else:
                failures.append(RuntimeError("scan job cleanup snapshot timed out"))

            failures.extend(_cleanup_windows_jobs(jobs, deadline))
            self._shutdown_complete = (
                starts_converged
                and snapshot_complete
                and not any(
                    job.windows_job_handle is not None
                    or job.windows_reaper_error is not None
                    or (
                        job.windows_reaper is not None
                        and job.windows_reaper.is_alive()
                    )
                    for job in jobs
                )
            )
            if failures:
                raise BaseExceptionGroup("scan job service shutdown failed", failures)
        finally:
            self._close_lock.release()

    def shutdown(self) -> None:
        self.close()

    def _accept_start(self) -> None:
        with self._start_condition:
            if self._starts_closed:
                raise RuntimeError("scan job service is closed")
            self._active_starts += 1

    def _finish_start(self) -> None:
        with self._start_condition:
            self._active_starts -= 1
            self._start_condition.notify_all()

    def _handoff_start_during_shutdown(self, job_id: str) -> None:
        with self._start_condition:
            if not self._starts_closed:
                return
        deadline = time.monotonic() + _SCAN_SERVICE_SHUTDOWN_TIMEOUT
        if not _acquire_before(self._lock, deadline):
            raise BaseExceptionGroup(
                "scan start shutdown handoff failed",
                [RuntimeError("scan job handoff snapshot timed out")],
            )
        try:
            job = self._jobs.get(job_id)
        finally:
            self._lock.release()
        if job is None:
            return
        failures = _cleanup_windows_jobs([job], deadline)
        if failures:
            raise BaseExceptionGroup("scan start shutdown handoff failed", failures)

    def _state_path(self, job_id: str) -> Path:
        job_id = validate_authority_id(job_id)
        return self.root / f"{job_id}.state.json"

    def _process_lock_path(self, job_id: str) -> Path:
        job_id = validate_authority_id(job_id)
        return self.root / f".{job_id}.lock"

    def _stdout_path(self, job_id: str) -> Path:
        job_id = validate_authority_id(job_id)
        return self.root / f"{job_id}.stdout.log"

    def _stderr_path(self, job_id: str) -> Path:
        job_id = validate_authority_id(job_id)
        return self.root / f"{job_id}.stderr.log"

    def _expected_log_paths(self, job_id: str) -> tuple[Path, Path]:
        job_id = validate_authority_id(job_id)
        return self._stdout_path(job_id).resolve(), self._stderr_path(job_id).resolve()

    def _start_artifact_path(
        self,
        job_id: str,
        process_group_token: str | None,
        suffix: str,
    ) -> Path:
        job_id = validate_authority_id(job_id)
        if (
            process_group_token is None
            or len(process_group_token) != 32
            or any(
                character not in "0123456789abcdefABCDEF"
                for character in process_group_token
            )
        ):
            raise ProcessAuthorityAmbiguousError(
                "persisted scan job authority is unreadable"
            )
        attempt_id = hashlib.sha256(
            process_group_token.encode("ascii")
        ).hexdigest()
        return self.root / f".{job_id}.{attempt_id}.{suffix}"

    def _start_release_path(
        self,
        job_id: str,
        process_group_token: str | None,
    ) -> Path:
        return self._start_artifact_path(job_id, process_group_token, "release")

    def _start_started_path(
        self,
        job_id: str,
        process_group_token: str | None,
    ) -> Path:
        return self._start_artifact_path(job_id, process_group_token, "started")

    def _start_result_path(
        self,
        job_id: str,
        process_group_token: str | None,
    ) -> Path:
        job_id = validate_authority_id(job_id)
        self._start_artifact_path(job_id, process_group_token, "result")
        assert process_group_token is not None
        attempt_id = hashlib.sha256(
            f"{job_id}\0{process_group_token}".encode("ascii")
        ).hexdigest()
        return self.root / f".{attempt_id}.result"

    def _open_existing_process_lock(self, lock_path: Path):
        flags = os.O_RDWR | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        try:
            descriptor = os.open(lock_path, flags)
        except OSError as exc:
            raise ProcessAuthorityAmbiguousError(
                "scan process lock authority is unavailable"
            ) from exc
        try:
            handle = os.fdopen(descriptor, "r+b")
        except BaseException as primary_error:
            cleanup_errors: list[BaseException] = []
            try:
                os.close(descriptor)
            except BaseException as exc:
                cleanup_errors.append(exc)
            _raise_with_cleanup(
                "scan process lock open and descriptor cleanup failed",
                primary_error,
                cleanup_errors,
            )
        try:
            self._validate_open_process_lock_identity(lock_path, handle)
            return handle
        except BaseException as primary_error:
            cleanup_errors = []
            try:
                handle.close()
            except BaseException as exc:
                cleanup_errors.append(exc)
            _raise_with_cleanup(
                "scan process lock validation and handle cleanup failed",
                primary_error,
                cleanup_errors,
            )

    def _validate_open_process_lock_identity(
        self,
        lock_path: Path,
        handle: object,
    ) -> None:
        try:
            opened = os.fstat(handle.fileno())  # type: ignore[attr-defined]
            current = os.stat(lock_path, follow_symlinks=False)
        except OSError as exc:
            raise ProcessAuthorityAmbiguousError(
                "scan process lock authority is unreadable"
            ) from exc
        if (
            not stat.S_ISREG(opened.st_mode)
            or not stat.S_ISREG(current.st_mode)
            or _is_link_or_reparse(opened)
            or _is_link_or_reparse(current)
            or not os.path.samestat(opened, current)
        ):
            message = (
                "scan process lock authority is a reparse point"
                if _is_link_or_reparse(opened) or _is_link_or_reparse(current)
                else "scan process lock authority changed or is malformed"
            )
            raise ProcessAuthorityAmbiguousError(message)

    def _validate_open_process_lock(self, lock_path: Path, handle: object) -> None:
        self._validate_open_process_lock_identity(lock_path, handle)
        try:
            handle.seek(0)  # type: ignore[attr-defined]
            marker = handle.read(2)  # type: ignore[attr-defined]
            handle.seek(0)  # type: ignore[attr-defined]
        except OSError as exc:
            raise ProcessAuthorityAmbiguousError(
                "scan process lock authority is unreadable"
            ) from exc
        if marker != b"0":
            raise ProcessAuthorityAmbiguousError(
                "scan process lock authority changed or is malformed"
            )

    def _publish_initialized_process_lock(
        self,
        job_id: str,
    ) -> tuple[Path, os.stat_result | None]:
        """Install one initialized lock via same-filesystem atomic hardlink.

        Hardlink support is a required authority capability. Unsupported
        filesystems fail closed; there is deliberately no non-atomic fallback.
        """
        self._ensure_authority_root()
        lock_path = self._process_lock_path(job_id)
        temporary = lock_path.with_name(
            f"{lock_path.name}.tmp.{uuid.uuid4().hex[:8]}"
        )
        installed = False
        temporary_identity: os.stat_result | None = None
        descriptor: int | None = None
        temporary_created = False
        primary_error: BaseException | None = None
        try:
            descriptor = os.open(
                temporary,
                os.O_CREAT
                | os.O_EXCL
                | os.O_WRONLY
                | getattr(os, "O_BINARY", 0)
                | getattr(os, "O_NOFOLLOW", 0),
                0o600,
            )
            temporary_created = True
            temporary_attributes = os.lstat(temporary)
            if _is_link_or_reparse(temporary_attributes):
                raise ProcessAuthorityAmbiguousError(
                    "scan process lock temporary is a reparse point"
                )
            if not stat.S_ISREG(temporary_attributes.st_mode):
                raise ProcessAuthorityAmbiguousError(
                    "scan process lock temporary is not a regular file"
                )
            if os.name != "nt":
                os.chmod(temporary, 0o600)
            lock_file = os.fdopen(descriptor, "wb")
            descriptor = None
            with lock_file:
                lock_file.write(b"0")
                lock_file.flush()
                os.fsync(lock_file.fileno())
                temporary_identity = os.fstat(lock_file.fileno())
            try:
                os.link(temporary, lock_path)
            except FileExistsError:
                pass
            except OSError as exc:
                unsupported_errnos = {
                    errno.EPERM,
                    getattr(errno, "ENOTSUP", errno.EPERM),
                    getattr(errno, "EOPNOTSUPP", errno.EPERM),
                }
                if exc.errno in unsupported_errnos or getattr(
                    exc, "winerror", None
                ) in {1, 50, 87}:
                    raise ProcessAuthorityAmbiguousError(
                        "atomic process lock hardlink authority is unsupported"
                    ) from exc
                raise
            else:
                installed = True
        except BaseException as exc:
            primary_error = exc

        cleanup_errors: list[BaseException] = []
        if descriptor is not None:
            try:
                os.close(descriptor)
            except BaseException as exc:
                cleanup_errors.append(exc)
        if temporary_created:
            try:
                temporary.unlink(missing_ok=True)
            except BaseException as exc:
                cleanup_errors.append(exc)
            try:
                durable_mkdir_parents(lock_path.parent, mode=0o700)
            except BaseException as exc:
                cleanup_errors.append(exc)
        if primary_error is not None or cleanup_errors:
            _raise_with_cleanup(
                "scan process lock initialization and cleanup failed",
                primary_error,
                cleanup_errors,
            )
        return lock_path, temporary_identity if installed else None

    def _held_process_locks(self) -> dict[Path, object]:
        handles = getattr(self._process_lock_state, "handles", None)
        if handles is None:
            handles = {}
            self._process_lock_state.handles = handles
        return cast(dict[Path, object], handles)

    @contextmanager
    def _locked_process_lock(
        self,
        lock_path: Path,
        *,
        expected_identity: os.stat_result | None = None,
    ):
        handle = self._open_existing_process_lock(lock_path)
        locked = False
        held = self._held_process_locks()
        acquisition_error: BaseException | None = None
        try:
            handle.seek(0)
            if expected_identity is not None and not os.path.samestat(
                expected_identity,
                os.fstat(handle.fileno()),
            ):
                raise ProcessAuthorityAmbiguousError(
                    "scan process lock authority changed during initialization"
                )
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            locked = True
            self._validate_open_process_lock(lock_path, handle)
            if lock_path in held:
                raise RuntimeError("scan process lock is already held by this thread")
            held[lock_path] = handle
        except ProcessAuthorityAmbiguousError as exc:
            acquisition_error = exc
        except OSError as exc:
            acquisition_error = ProcessAuthorityAmbiguousError(
                "scan process lock authority could not be acquired"
            )
            acquisition_error.__cause__ = exc
        except BaseException as exc:
            acquisition_error = exc

        if acquisition_error is not None:
            cleanup_errors: list[BaseException] = []
            if locked:
                try:
                    handle.seek(0)
                    if os.name == "nt":
                        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                    else:
                        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
                except BaseException as exc:
                    cleanup_errors.append(exc)
            try:
                handle.close()
            except BaseException as exc:
                cleanup_errors.append(exc)
            _raise_with_cleanup(
                "scan process lock acquisition and cleanup failed",
                acquisition_error,
                cleanup_errors,
            )

        body_error: BaseException | None = None
        try:
            yield
        except BaseException as exc:
            body_error = exc

        cleanup_errors = []
        try:
            self._validate_open_process_lock(lock_path, handle)
        except BaseException as exc:
            if body_error is None:
                body_error = exc
            else:
                cleanup_errors.append(exc)
        held.pop(lock_path, None)
        try:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        except BaseException as exc:
            cleanup_errors.append(exc)
        try:
            handle.close()
        except BaseException as exc:
            cleanup_errors.append(exc)
        if body_error is not None or cleanup_errors:
            _raise_with_cleanup(
                "scan process lock operation and cleanup failed",
                body_error,
                cleanup_errors,
            )

    @contextmanager
    def _initialize_process_lock(self, job_id: str):
        lock_path = self._process_lock_path(job_id)
        held_handle = self._held_process_locks().get(lock_path)
        if held_handle is not None:
            self._validate_open_process_lock(lock_path, held_handle)
            body_error: BaseException | None = None
            try:
                yield
            except BaseException as exc:
                body_error = exc
            cleanup_errors: list[BaseException] = []
            try:
                self._validate_open_process_lock(lock_path, held_handle)
            except BaseException as exc:
                if body_error is None:
                    body_error = exc
                else:
                    cleanup_errors.append(exc)
            if body_error is not None or cleanup_errors:
                _raise_with_cleanup(
                    "nested scan process lock operation failed",
                    body_error,
                    cleanup_errors,
                )
            return
        lock_path, installed_identity = self._publish_initialized_process_lock(job_id)
        with self._locked_process_lock(
            lock_path,
            expected_identity=installed_identity,
        ):
            yield

    @contextmanager
    def _process_lock(self, job_id: str):
        with self._initialize_process_lock(job_id):
            yield

    @contextmanager
    def _existing_process_lock(self, job_id: str):
        lock_path = self._process_lock_path(job_id)
        held_handle = self._held_process_locks().get(lock_path)
        if held_handle is None:
            with self._locked_process_lock(lock_path):
                yield
            return
        self._validate_open_process_lock(lock_path, held_handle)
        body_error: BaseException | None = None
        try:
            yield
        except BaseException as exc:
            body_error = exc
        cleanup_errors: list[BaseException] = []
        try:
            self._validate_open_process_lock(lock_path, held_handle)
        except BaseException as exc:
            if body_error is None:
                body_error = exc
            else:
                cleanup_errors.append(exc)
        if body_error is not None or cleanup_errors:
            _raise_with_cleanup(
                "nested scan process lock operation failed",
                body_error,
                cleanup_errors,
            )

    @contextmanager
    def _start_process_lock(self, job_id: str):
        job_id = validate_authority_id(job_id)
        self._ensure_authority_root()
        lock_path = self.root / f".{job_id}.start.lock"
        try:
            descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(descriptor, "wb") as lock_file:
                lock_file.write(b"0")
                lock_file.flush()
                os.fsync(lock_file.fileno())
        except FileExistsError:
            pass
        with lock_path.open("r+b") as handle:
            if os.name == "nt":
                import msvcrt

                while True:
                    handle.seek(0)
                    try:
                        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                        break
                    except OSError as exc:
                        if exc.errno not in {errno.EACCES, errno.EAGAIN}:
                            raise
                        time.sleep(0.05)
            else:
                import fcntl

                handle.seek(0)
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                handle.seek(0)
                if os.name == "nt":
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def _refresh_job(
        self,
        job: _LocalScanJob,
        *,
        require_state: bool = True,
    ) -> None:
        validate_authority_id(job.job_id)
        path = self._state_path(job.job_id)
        if not path.exists():
            if not require_state:
                return
            raise ProcessAuthorityAmbiguousError(
                "persisted scan job authority is missing"
            )
        payload = _parse_persisted_job_payload(
            json.loads(path.read_text(encoding="utf-8")),
            expected_authority_namespace=self.authority_namespace,
        )
        persisted_job_id = cast(str, payload["job_id"])
        if persisted_job_id != job.job_id:
            raise ValueError("persisted scan job authority identity changed")
        expected_stdout_path, expected_stderr_path = self._expected_log_paths(
            job.job_id
        )
        if (
            payload["stdout_path"] != str(expected_stdout_path)
            or payload["stderr_path"] != str(expected_stderr_path)
        ):
            raise ValueError("persisted scan job authority identity changed")
        persisted_identity = (
            persisted_job_id,
            payload["pid"],
            payload["process_create_time"],
            payload["process_group_id"],
            payload["process_group_token"],
            expected_stdout_path,
            expected_stderr_path,
            payload["created_at"],
            payload["authority_namespace"],
        )
        cached_identity = (
            job.job_id,
            int(getattr(job.process, "pid")),
            job.process_create_time,
            job.process_group_id,
            job.process_group_token,
            job.stdout_path.resolve(),
            job.stderr_path.resolve(),
            job.created_at,
            job.authority_namespace,
        )
        if persisted_identity != cached_identity:
            raise ValueError("persisted scan job authority identity changed")

        recovered_authority_state_pending = job.recovered_authority_state_pending
        job.command = list(cast(list[str], payload["command"]))
        job.updated_at = cast(str, payload["updated_at"])
        job.stdout_pos = cast(int, payload["stdout_pos"])
        job.stderr_pos = cast(int, payload["stderr_pos"])
        job.progress_percent = cast(float | None, payload["progress_percent"])
        job.current_phase = cast(str | None, payload["current_phase"])
        job.current_substep = cast(str | None, payload["current_substep"])
        job.completed_labels = list(cast(list[str], payload["completed_labels"]))
        job.seen_labels = set(job.completed_labels)
        job.completed_stage_ids = list(
            cast(list[str], payload["completed_stage_ids"])
        )
        job.seen_stage_ids = set(job.completed_stage_ids)
        job.current_stage_id = cast(str | None, payload["current_stage_id"])
        job.stdout_buffer = cast(str, payload["stdout_buffer"])
        job.stderr_buffer = cast(str, payload["stderr_buffer"])
        job.owner_id = cast(str | None, payload["owner_id"])
        job.artifact_paths = list(cast(list[str], payload["artifact_paths"]))
        job.report_session_ids = set(cast(set[str], payload["report_session_ids"]))
        job.report_session_invalid = cast(bool, payload["report_session_invalid"])
        persisted_forced_status = cast(str | None, payload["forced_status"])
        if recovered_authority_state_pending and persisted_forced_status is None:
            job.forced_status = "authority_ambiguous"
        else:
            job.forced_status = persisted_forced_status
            job.recovered_authority_state_pending = False
        job.phase2_profiles_started = cast(bool, payload["phase2_profiles_started"])
        job.phase2_profiles_complete = cast(bool, payload["phase2_profiles_complete"])
        job.start_released = cast(bool, payload["start_released"])

    def _persist_job(self, job: _LocalScanJob) -> None:
        validate_authority_id(job.job_id)
        process = job.process
        payload = {
            "schema_version": 1,
            "job_id": job.job_id,
            "command": list(job.command),
            "pid": int(process.pid),
            "process_create_time": job.process_create_time,
            "process_group_id": job.process_group_id,
            "process_group_token": job.process_group_token,
            "stdout_path": str(job.stdout_path.resolve()),
            "stderr_path": str(job.stderr_path.resolve()),
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "stdout_pos": job.stdout_pos,
            "stderr_pos": job.stderr_pos,
            "progress_percent": job.progress_percent,
            "current_phase": job.current_phase,
            "current_substep": job.current_substep,
            "completed_labels": list(job.completed_labels),
            "completed_stage_ids": list(job.completed_stage_ids),
            "current_stage_id": job.current_stage_id,
            "stdout_buffer": job.stdout_buffer,
            "stderr_buffer": job.stderr_buffer,
            "owner_id": job.owner_id,
            "artifact_paths": list(job.artifact_paths),
            "report_session_ids": sorted(job.report_session_ids),
            "report_session_invalid": job.report_session_invalid,
            "forced_status": job.forced_status,
            "phase2_profiles_started": job.phase2_profiles_started,
            "phase2_profiles_complete": job.phase2_profiles_complete,
            "start_released": job.start_released,
            "authority_namespace": job.authority_namespace,
        }
        path = self._state_path(job.job_id)
        serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        lock_context = (
            self._existing_process_lock
            if path.exists()
            else self._initialize_process_lock
        )
        with lock_context(job.job_id):
            durable_write_bytes(path, serialized.encode("utf-8"))

    def _publish_recovered_authority_state(self, job: _LocalScanJob) -> None:
        if not job.recovered_authority_state_pending:
            return
        self._persist_job(job)
        job.recovered_authority_state_pending = False

    def _raise_start_failure(
        self,
        job: _LocalScanJob,
        primary_error: BaseException,
    ) -> NoReturn:
        cleanup_errors: list[BaseException] = []
        try:
            _rollback_scan_authority(job)
        except BaseException as exc:
            cleanup_errors.append(exc)
        job.forced_status = "rollback_failed" if cleanup_errors else "failed"
        try:
            self._persist_job(job)
        except BaseException as exc:
            cleanup_errors.append(exc)
        if cleanup_errors:
            raise BaseExceptionGroup(
                "scan start failed and cleanup was incomplete",
                [primary_error, *cleanup_errors],
            )
        raise primary_error.with_traceback(primary_error.__traceback__)

    def _recover_jobs(
        self,
        job_id: str | None = None,
        *,
        _process_lock_held: bool = False,
    ) -> None:
        if job_id is not None:
            job_id = validate_authority_id(job_id)
        state_paths = (
            [self._state_path(job_id)]
            if job_id is not None
            else list(self.root.glob("*.state.json"))
        )
        for state_path in state_paths:
            filename_job_id = state_path.name.removesuffix(".state.json")
            try:
                validate_authority_id(filename_job_id)
            except AuthorityIdError as exc:
                raise ProcessAuthorityAmbiguousError(
                    "persisted scan job authority is unreadable"
                ) from exc
            if not state_path.exists():
                continue
            try:
                payload = _parse_persisted_job_payload(
                    json.loads(state_path.read_text(encoding="utf-8")),
                    expected_authority_namespace=self.authority_namespace,
                )
                recovered_job_id = cast(str, payload["job_id"])
                if recovered_job_id != filename_job_id:
                    raise ProcessAuthorityAmbiguousError(
                        "persisted scan job authority is unreadable"
                    )
                pid = cast(int, payload["pid"])
                create_time = cast(float, payload["process_create_time"])
                process_group_id = cast(int, payload["process_group_id"])
                process_group_token = cast(str, payload["process_group_token"])
                stdout_path, stderr_path = self._expected_log_paths(
                    recovered_job_id
                )
                if (
                    payload["stdout_path"] != str(stdout_path)
                    or payload["stderr_path"] != str(stderr_path)
                ):
                    if job_id is not None:
                        raise ValueError(
                            "persisted scan job log identity is invalid"
                        )
                    continue
                if not _process_lock_held:
                    with self._existing_process_lock(filename_job_id):
                        self._recover_jobs(
                            filename_job_id,
                            _process_lock_held=True,
                        )
                    continue
                result_path = self._start_result_path(
                    recovered_job_id,
                    process_group_token,
                )
                process = _RecoveredProcess(pid, create_time, result_path)
                forced_status = cast(str | None, payload["forced_status"])
                job = _LocalScanJob(
                    job_id=recovered_job_id,
                    command=list(cast(list[str], payload["command"])),
                    process=process,
                    stdout_path=stdout_path,
                    stderr_path=stderr_path,
                    created_at=cast(str, payload["created_at"]),
                    updated_at=cast(str, payload["updated_at"]),
                    stdout_pos=cast(int, payload["stdout_pos"]),
                    stderr_pos=cast(int, payload["stderr_pos"]),
                    progress_percent=cast(float | None, payload["progress_percent"]),
                    current_phase=cast(str | None, payload["current_phase"]),
                    current_substep=cast(str | None, payload["current_substep"]),
                    completed_labels=list(cast(list[str], payload["completed_labels"])),
                    seen_labels=set(cast(list[str], payload["completed_labels"])),
                    completed_stage_ids=list(
                        cast(list[str], payload["completed_stage_ids"])
                    ),
                    seen_stage_ids=set(cast(list[str], payload["completed_stage_ids"])),
                    current_stage_id=cast(str | None, payload["current_stage_id"]),
                    stdout_buffer=cast(str, payload["stdout_buffer"]),
                    stderr_buffer=cast(str, payload["stderr_buffer"]),
                    owner_id=cast(str | None, payload["owner_id"]),
                    artifact_paths=list(cast(list[str], payload["artifact_paths"])),
                    report_session_ids=set(
                        cast(set[str], payload["report_session_ids"])
                    ),
                    report_session_invalid=cast(
                        bool, payload["report_session_invalid"]
                    ),
                    forced_status=forced_status,
                    phase2_profiles_started=cast(bool, payload["phase2_profiles_started"]),
                    phase2_profiles_complete=cast(bool, payload["phase2_profiles_complete"]),
                    process_create_time=create_time,
                    process_group_id=process_group_id,
                    process_group_token=process_group_token,
                    start_released=cast(bool, payload["start_released"]),
                    authority_namespace=cast(str, payload["authority_namespace"]),
                )
                if forced_status is None:
                    try:
                        _job_runtime_active(job)
                    except Exception:
                        job.forced_status = "authority_ambiguous"
                        job.recovered_authority_state_pending = True
                self._jobs[recovered_job_id] = job
            except json.JSONDecodeError as exc:
                if job_id is not None:
                    raise ProcessAuthorityAmbiguousError(
                        "persisted scan job authority is unreadable"
                    ) from exc
                continue
            except (TypeError, ValueError):
                if job_id is not None:
                    raise
                continue
            except (KeyError, OSError) as exc:
                if job_id is not None:
                    raise ProcessAuthorityAmbiguousError(
                        "persisted scan job authority is unreadable"
                    ) from exc
                continue

    def _release_registered_start(
        self,
        job: _LocalScanJob,
    ) -> dict[str, object]:
        validate_authority_id(job.job_id)
        if job.start_released or job.forced_status is not None:
            return self._snapshot(job)
        release_path = self._start_release_path(
            job.job_id,
            job.process_group_token,
        )
        started_path = self._start_started_path(
            job.job_id,
            job.process_group_token,
        )
        try:
            runtime_active = _job_runtime_active(job)
        except Exception as exc:
            job.forced_status = "authority_ambiguous"
            self._persist_job(job)
            raise ProcessAuthorityAmbiguousError(
                "scan process authority is ambiguous"
            ) from exc
        if not runtime_active:
            return self._snapshot(job)

        durable_write_bytes(release_path, b"release\n")
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and not started_path.exists():
            if job.process.poll() is not None:
                break
            time.sleep(0.02)
        job.start_released = started_path.exists()
        return self._snapshot(job)

    def start(
        self,
        command: list[str],
        owner_id: str | None = None,
        env_overrides: Mapping[str, str] | None = None,
        job_id: str | None = None,
    ) -> dict[str, object]:
        requested_command = list(command)
        resolved_job_id = job_id if job_id is not None else (
            f"scan-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
        )
        resolved_job_id = validate_scan_job_id_for_creation(resolved_job_id)
        self._accept_start()
        try:
            with self._start_lock:
                with self._start_process_lock(resolved_job_id):
                    try:
                        return self.get_for_replay(
                            resolved_job_id,
                            expected_command=requested_command,
                            expected_owner_id=owner_id,
                        )
                    except KeyError:
                        with self._process_lock(resolved_job_id):
                            pass
                        return self._start_new_job(
                            requested_command,
                            owner_id,
                            env_overrides,
                            resolved_job_id,
                        )
        finally:
            primary_error = sys.exception()
            cleanup_error: BaseException | None = None
            try:
                self._handoff_start_during_shutdown(resolved_job_id)
            except BaseException as exc:
                cleanup_error = exc
            finally:
                self._finish_start()
            if primary_error is not None and cleanup_error is not None:
                raise BaseExceptionGroup(
                    "scan start and shutdown handoff failed",
                    [primary_error, cleanup_error],
                ) from None
            if cleanup_error is not None:
                raise cleanup_error.with_traceback(cleanup_error.__traceback__)

    def _start_new_job(
        self,
        command: list[str],
        owner_id: str | None,
        env_overrides: Mapping[str, str] | None,
        job_id: str,
    ) -> dict[str, object]:
        job_id = validate_scan_job_id_for_creation(job_id)
        stdout_path = self._stdout_path(job_id)
        stderr_path = self._stderr_path(job_id)
        created_at = _utc_now()
        exec_command = _execution_command(command)
        process_group_token = uuid.uuid4().hex
        release_path = self._start_release_path(job_id, process_group_token)
        started_path = self._start_started_path(job_id, process_group_token)
        result_path = self._start_result_path(job_id, process_group_token)
        release_path.unlink(missing_ok=True)
        started_path.unlink(missing_ok=True)
        result_path.unlink(missing_ok=True)
        gate_script = (
            Path(__file__).resolve().parents[2] / "services" / "scan_process_gate.py"
        )
        process_environment = {
            **os.environ,
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUTF8": "1",
        }
        if env_overrides is not None:
            process_environment.update(
                {str(key): str(value) for key, value in env_overrides.items()}
            )
        gate_command, process_environment = _build_gate_launch(
            gate_script=gate_script,
            release_path=release_path,
            started_path=started_path,
            result_path=result_path,
            exec_command=exec_command,
            process_environment=process_environment,
            process_group_token=process_group_token,
        )

        with (
            stdout_path.open("ab") as stdout_file,
            stderr_path.open("ab") as stderr_file,
        ):
            process = subprocess.Popen(
                gate_command,
                cwd=self.cwd,
                env=process_environment,
                stdout=stdout_file,
                stderr=stderr_file,
                shell=False,
                creationflags=_CREATION_FLAGS,
                start_new_session=sys.platform != "win32",
            )

        startup_descriptor: int | None = None
        if sys.platform != "win32":
            try:
                startup_descriptor = _open_pidfd(process.pid)
            except BaseException as exc:
                primary_error = ProcessAuthorityAmbiguousError(
                    "stable startup supervisor authority could not be acquired"
                )
                try:
                    process.wait(timeout=35)
                except BaseException as wait_error:
                    raise BaseExceptionGroup(
                        "stable startup authority and gate reaping failed",
                        [primary_error, wait_error],
                    ) from exc
                raise primary_error from exc
        try:
            process_create_time = _process_create_time(process.pid)
        except BaseException as identity_error:
            if startup_descriptor is not None:
                descriptor = startup_descriptor
                startup_descriptor = None
                _raise_unreleased_start_failure(process, descriptor, identity_error)
            cleanup_errors: list[BaseException] = []
            try:
                process.kill()
            except BaseException as exc:
                cleanup_errors.append(exc)
            try:
                process.wait(timeout=5)
            except BaseException as exc:
                cleanup_errors.append(exc)
            if cleanup_errors:
                raise BaseExceptionGroup(
                    "scan identity lookup and Windows cleanup failed",
                    [identity_error, *cleanup_errors],
                )
            raise
        if process_create_time is None:
            primary_error = RuntimeError("scan process identity could not be established")
            if startup_descriptor is not None:
                descriptor = startup_descriptor
                startup_descriptor = None
                _raise_unreleased_start_failure(process, descriptor, primary_error)
            cleanup_errors: list[BaseException] = []
            try:
                process.kill()
            except BaseException as exc:
                cleanup_errors.append(exc)
            try:
                process.wait(timeout=5)
            except BaseException as exc:
                cleanup_errors.append(exc)
            if cleanup_errors:
                raise BaseExceptionGroup(
                    "scan identity failure and Windows cleanup failed",
                    [primary_error, *cleanup_errors],
                )
            raise primary_error
        if startup_descriptor is not None:
            close_failures = _close_process_handles([startup_descriptor])
            startup_descriptor = None
            if close_failures:
                primary_error = RuntimeError(
                    "stable startup supervisor handle cleanup failed"
                )
                try:
                    process.wait(timeout=35)
                except BaseException as wait_error:
                    raise BaseExceptionGroup(
                        "startup handle cleanup and gate reaping failed",
                        [primary_error, *close_failures, wait_error],
                    )
                raise primary_error from close_failures[0]

        job = _LocalScanJob(
            job_id=job_id,
            command=list(command),
            process=process,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            created_at=created_at,
            updated_at=created_at,
            owner_id=owner_id,
            process_create_time=process_create_time,
            process_group_id=process.pid,
            process_group_token=process_group_token,
            start_released=False,
            authority_namespace=self.authority_namespace,
        )
        if sys.platform == "win32":
            try:
                if self.authority_namespace == "scan":
                    job.windows_job_handle = _create_windows_job(
                        process,
                        process_group_token,
                    )
                else:
                    job.windows_job_handle = _create_windows_job(
                        process,
                        process_group_token,
                        self.authority_namespace,
                    )
            except BaseException as primary_error:
                cleanup_errors: list[BaseException] = []
                try:
                    process.kill()
                except BaseException as exc:
                    cleanup_errors.append(exc)
                try:
                    process.wait(timeout=5)
                except BaseException as exc:
                    cleanup_errors.append(exc)
                if cleanup_errors:
                    raise BaseExceptionGroup(
                        "Windows job setup and supervisor cleanup failed",
                        [primary_error, *cleanup_errors],
                    )
                raise
        with self._lock, self._existing_process_lock(job_id):
            self._jobs[job_id] = job
            try:
                self._snapshot(job)
                snapshot = self._release_registered_start(job)
                _start_windows_job_reaper(job)
                return snapshot
            except BaseException as primary_error:
                self._raise_start_failure(job, primary_error)

    def get(self, job_id: str) -> dict[str, object]:
        return self._get(job_id, _OWNER_VALIDATION_NOT_REQUIRED)

    def observe(self, job_id: str) -> dict[str, object]:
        """Inspect process authority without releasing or persisting job state."""
        return self._observe(job_id, _OWNER_VALIDATION_NOT_REQUIRED)

    def observe_owned(
        self,
        job_id: str,
        *,
        expected_owner_id: str,
    ) -> dict[str, object]:
        """Inspect owner-bound authority without releasing or persisting state."""
        return self._observe(job_id, expected_owner_id)

    def _observe(
        self,
        job_id: str,
        expected_owner_id: object,
    ) -> dict[str, object]:
        job_id = validate_authority_id(job_id)
        state_path = self._state_path(job_id)
        with self._lock:
            if not state_path.exists():
                raise KeyError(job_id)
        with self._lock, self._existing_process_lock(job_id):
            if not state_path.exists():
                raise KeyError(job_id)
            try:
                payload = _parse_persisted_job_payload(
                    json.loads(state_path.read_text(encoding="utf-8")),
                    expected_authority_namespace=self.authority_namespace,
                )
                if payload["job_id"] != job_id:
                    raise ProcessAuthorityAmbiguousError(
                        "persisted scan job authority is unreadable"
                    )
                stdout_path, stderr_path = self._expected_log_paths(job_id)
                if (
                    payload["stdout_path"] != str(stdout_path)
                    or payload["stderr_path"] != str(stderr_path)
                ):
                    raise ProcessAuthorityAmbiguousError(
                        "persisted scan job authority is unreadable"
                    )
                if (
                    expected_owner_id is not _OWNER_VALIDATION_NOT_REQUIRED
                    and payload["owner_id"] != expected_owner_id
                ):
                    raise ScanJobOwnershipError("scan job owner identity mismatch")
                token = cast(str, payload["process_group_token"])
                process = _RecoveredProcess(
                    cast(int, payload["pid"]),
                    cast(float, payload["process_create_time"]),
                    self._start_result_path(job_id, token),
                )
                job = _LocalScanJob(
                    job_id=job_id,
                    command=list(cast(list[str], payload["command"])),
                    process=process,
                    stdout_path=stdout_path,
                    stderr_path=stderr_path,
                    created_at=cast(str, payload["created_at"]),
                    updated_at=cast(str, payload["updated_at"]),
                    owner_id=cast(str | None, payload["owner_id"]),
                    report_session_ids=set(
                        cast(set[str], payload["report_session_ids"])
                    ),
                    report_session_invalid=cast(
                        bool, payload["report_session_invalid"]
                    ),
                    forced_status=cast(str | None, payload["forced_status"]),
                    process_create_time=cast(float, payload["process_create_time"]),
                    process_group_id=cast(int, payload["process_group_id"]),
                    process_group_token=token,
                    start_released=cast(bool, payload["start_released"]),
                    authority_namespace=cast(str, payload["authority_namespace"]),
                )
                runtime_active = _job_runtime_active(job)
                returncode = process.poll()
                start_released = job.start_released or self._start_started_path(
                    job_id,
                    token,
                ).exists()
                if job.forced_status is not None:
                    status = job.forced_status
                elif runtime_active and not start_released:
                    status = "starting"
                elif runtime_active:
                    status = "running"
                elif returncode == 0:
                    status = "completed"
                else:
                    status = "failed"
                return {"job_id": job_id, "status": status}
            except KeyError:
                raise
            except (ProcessAuthorityAmbiguousError, ScanJobOwnershipError):
                raise
            except (TypeError, ValueError, json.JSONDecodeError, OSError) as exc:
                raise ProcessAuthorityAmbiguousError(
                    "persisted scan job authority is unreadable"
                ) from exc

    def get_owned(
        self,
        job_id: str,
        *,
        expected_owner_id: str,
    ) -> dict[str, object]:
        return self._get(job_id, expected_owner_id)

    def _get(
        self,
        job_id: str,
        expected_owner_id: object,
    ) -> dict[str, object]:
        job_id = validate_authority_id(job_id)
        with self._lock:
            if job_id not in self._jobs and not self._state_path(job_id).exists():
                raise KeyError(job_id)
        with self._lock, self._existing_process_lock(job_id):
            if job_id not in self._jobs:
                self._recover_jobs(job_id, _process_lock_held=True)
            job = self._jobs[job_id]
            self._refresh_job(job)
            if (
                expected_owner_id is not _OWNER_VALIDATION_NOT_REQUIRED
                and job.owner_id != expected_owner_id
            ):
                raise ScanJobOwnershipError("scan job owner identity mismatch")
            if expected_owner_id is not _OWNER_VALIDATION_NOT_REQUIRED:
                self._publish_recovered_authority_state(job)
            if not job.start_released:
                return self._release_registered_start(job)
            return self._snapshot(job)

    def get_for_replay(
        self,
        job_id: str,
        *,
        expected_command: list[str],
        expected_owner_id: str | None,
    ) -> dict[str, object]:
        job_id = validate_authority_id(job_id)
        requested_command = list(expected_command)
        with self._lock:
            if job_id not in self._jobs and not self._state_path(job_id).exists():
                raise KeyError(job_id)
        try:
            with self._lock, self._existing_process_lock(job_id):
                if job_id not in self._jobs:
                    self._recover_jobs(job_id, _process_lock_held=True)
                job = self._jobs[job_id]
                self._refresh_job(job)
                if job.owner_id != expected_owner_id:
                    raise ScanJobReplayOwnershipError(
                        "scan replay owner identity mismatch"
                    )
                self._publish_recovered_authority_state(job)
                if job.command != requested_command:
                    raise ScanJobReplayIdentityError(
                        "scan replay command identity mismatch"
                    )
                if not job.start_released:
                    return self._release_registered_start(job)
                return self._snapshot(job)
        except KeyError:
            raise
        except ScanJobReplayAuthorityError:
            raise
        except (
            ProcessAuthorityAmbiguousError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
            OSError,
        ) as exc:
            raise ScanJobReplayAuthorityError(
                str(exc)
                if isinstance(exc, ProcessAuthorityAmbiguousError)
                else "scan replay authority mismatch"
            ) from exc

    def stop(self, job_id: str) -> dict[str, object]:
        return self._stop(job_id, _OWNER_VALIDATION_NOT_REQUIRED)

    def stop_owned(
        self,
        job_id: str,
        *,
        expected_owner_id: str,
    ) -> dict[str, object]:
        return self._stop(job_id, expected_owner_id)

    def _stop(
        self,
        job_id: str,
        expected_owner_id: object,
    ) -> dict[str, object]:
        job_id = validate_authority_id(job_id)
        with self._lock:
            if job_id not in self._jobs and not self._state_path(job_id).exists():
                raise KeyError(job_id)
        with self._lock, self._existing_process_lock(job_id):
            if job_id not in self._jobs:
                self._recover_jobs(job_id, _process_lock_held=True)
            job = self._jobs[job_id]
            self._refresh_job(job, require_state=False)
            if (
                expected_owner_id is not _OWNER_VALIDATION_NOT_REQUIRED
                and job.owner_id != expected_owner_id
            ):
                raise ScanJobOwnershipError("scan job owner identity mismatch")
            self._publish_recovered_authority_state(job)
            if job.forced_status in {"completed", "failed", "stopped"}:
                return self._snapshot(job)

            def retain_unresolved_authority() -> None:
                if job.forced_status != "rollback_failed":
                    job.forced_status = "authority_ambiguous"
                self._persist_job(job)

            try:
                authority_active = _scan_stop_authority_active(
                    job,
                    require_full_tree=False,
                )
            except BaseException as exc:
                retain_unresolved_authority()
                if sys.platform == "win32" and isinstance(
                    exc, ProcessAuthorityAmbiguousError
                ):
                    raise
                raise RuntimeError("scan process authority is ambiguous") from exc

            if not authority_active:
                if job.forced_status in {"authority_ambiguous", "rollback_failed"}:
                    job.forced_status = "stopped"
                    self._persist_job(job)
                return self._snapshot(job)

            try:
                if sys.platform == "win32":
                    _converge_windows_authority(job)
                else:
                    _converge_posix_authority(job)
                    try:
                        job.process.wait(timeout=1)
                    except (subprocess.TimeoutExpired, psutil.TimeoutExpired):
                        pass
            except BaseException as exc:
                retain_unresolved_authority()
                message = (
                    "scan process tree stop was not confirmed"
                    if sys.platform == "win32"
                    else "scan process authority is ambiguous"
                )
                raise RuntimeError(message) from exc

            try:
                authority_active = _scan_stop_authority_active(
                    job,
                    require_full_tree=True,
                )
            except BaseException as exc:
                retain_unresolved_authority()
                raise RuntimeError("scan process authority is ambiguous") from exc
            if authority_active:
                retain_unresolved_authority()
                raise RuntimeError("scan process tree stop was not confirmed")

            job.forced_status = "stopped"
            self._persist_job(job)
            return self._snapshot(job)

    def _snapshot(self, job: _LocalScanJob) -> dict[str, object]:
        validate_authority_id(job.job_id)
        if not job.start_released:
            started_path = self._start_started_path(
                job.job_id,
                job.process_group_token,
            )
            if started_path.exists():
                job.start_released = True
        returncode = job.process.poll()
        try:
            if (
                sys.platform == "win32"
                and job.process_group_token
                and job.forced_status not in {"completed", "failed", "stopped"}
            ):
                runtime_active = _windows_job_active(job)
            else:
                runtime_active = returncode is None or (
                    job.forced_status is None
                    and _process_group_alive(job.process_group_id, job.process_group_token)
                )
        except ProcessAuthorityAmbiguousError:
            if job.forced_status not in {
                "completed",
                "failed",
                "stopped",
                "rollback_failed",
            }:
                job.forced_status = "authority_ambiguous"
            runtime_active = True
        if not runtime_active:
            returncode = job.process.poll()
        if job.forced_status is not None:
            status = job.forced_status
        elif runtime_active and not job.start_released:
            status = "starting"
        elif runtime_active:
            status = "running"
        elif returncode == 0:
            status = "completed"
        else:
            status = "failed"

        job.updated_at = _utc_now()
        stdout_tail = _tail(job.stdout_path)
        stderr_tail = _tail(job.stderr_path)
        stdout_chunk, job.stdout_pos = _read_incremental(
            job.stdout_path, job.stdout_pos
        )
        stderr_chunk, job.stderr_pos = _read_incremental(
            job.stderr_path, job.stderr_pos
        )
        stdout_lines, job.stdout_buffer = _consume_lines(
            job.stdout_buffer, stdout_chunk
        )
        stderr_lines, job.stderr_buffer = _consume_lines(
            job.stderr_buffer, stderr_chunk
        )
        if status not in {"starting", "running"}:
            if job.stdout_buffer.strip():
                stdout_lines.append(job.stdout_buffer.strip())
            if job.stderr_buffer.strip():
                stderr_lines.append(job.stderr_buffer.strip())
            job.stdout_buffer = ""
            job.stderr_buffer = ""
        job.report_session_ids, job.report_session_invalid = (
            _update_report_session_authority(
                stdout_lines,
                session_ids=job.report_session_ids,
                invalid=job.report_session_invalid,
            )
        )
        for line in [*stdout_lines, *stderr_lines]:
            if ":" not in line:
                continue
            marker, raw_path = line.split(":", 1)
            if marker.strip().lower() not in {
                "export gespeichert",
                "html-report gespeichert",
                "pdf-report gespeichert",
            }:
                continue
            artifact = raw_path.strip()
            if artifact and artifact not in job.artifact_paths:
                job.artifact_paths.append(artifact)
        progress = _update_progress_state(
            [*stdout_lines, *stderr_lines],
            status=status,
            labels=job.completed_labels,
            seen_labels=job.seen_labels,
            current_substep=job.current_substep,
            current_phase=job.current_phase,
            progress_percent=job.progress_percent,
            stage_ids=job.completed_stage_ids,
            seen_stage_ids=job.seen_stage_ids,
            current_stage_id=job.current_stage_id,
            phase2_profiles_started=job.phase2_profiles_started,
            phase2_profiles_complete=job.phase2_profiles_complete,
        )
        job.progress_percent = cast(float | None, progress["progress_percent"])
        job.current_phase = cast(str | None, progress["current_phase"])
        job.current_substep = cast(str | None, progress["current_substep"])
        job.current_stage_id = cast(str | None, progress["current_stage_id"])
        job.completed_labels = list(cast(list[str], progress["_all_labels"]))
        job.seen_labels = set(cast(set[str], progress["_seen_labels"]))
        job.completed_stage_ids = list(cast(list[str], progress["_all_stage_ids"]))
        job.seen_stage_ids = set(cast(set[str], progress["_seen_stage_ids"]))
        job.phase2_profiles_started = bool(progress["_phase2_profiles_started"])
        job.phase2_profiles_complete = bool(progress["_phase2_profiles_complete"])
        if status not in {"starting", "running"} and job.forced_status is None:
            job.forced_status = status
        if (
            self._jobs.get(job.job_id) is job
            and not job.recovered_authority_state_pending
        ):
            self._persist_job(job)
        return {
            "executes": True,
            "job_id": job.job_id,
            "status": status,
            "returncode": returncode,
            "command": list(job.command),
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "stdout_tail": stdout_tail,
            "stderr_tail": stderr_tail,
            "progress_percent": job.progress_percent,
            "current_phase": job.current_phase,
            "current_substep": job.current_substep,
            "current_stage_id": job.current_stage_id,
            "completed_substeps": progress["completed_substeps"],
            "completed_stage_ids": progress["completed_stage_ids"],
            "owner_id": job.owner_id,
            "artifact_paths": list(job.artifact_paths),
            "report_session_id": _resolved_report_session_id(
                job.report_session_ids,
                job.report_session_invalid,
            ),
        }
