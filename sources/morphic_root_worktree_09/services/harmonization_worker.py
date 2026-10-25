"""
Harmonisierungs-Worker Service für Morphic Engine V1

Ermöglicht persistente Harmonisierungen als Background-Jobs,
die auch nach Schließen der PowerShell weiterlaufen.

Features:
- Job-Management (JSON-basiert)
- Worker-Prozesse mit stabiler Prozessbaum-Autoritaet
- Hardware-Modulation (CPU, GPU, WebSocket)
- Status-Tracking
"""

import time
import hashlib
import json
import math
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import MISSING, asdict, dataclass, fields
import os
import sys
import threading
from contextlib import contextmanager

import psutil

from apps.web.durable_io import durable_mkdir_parents, durable_write_bytes
from apps.web.emf_authority import EmfTelemetryAuthority
from apps.web.authority_ids import (
    AuthorityIdError,
    HARMONIZATION_AUTHORITY_PREFIX,
    validate_authority_id,
    validate_harmonization_job_id_for_creation,
    validate_scan_job_id_for_creation,
)
from apps.web.scan_jobs import LocalScanJobService, ProcessAuthorityAmbiguousError
from core.compliance.operator_context import OperatorContext, operator_owner_scope


# Pfade. Tests and isolated deployments can redirect all runtime authority files.
JOBS_DIR = Path(
    os.environ.get(
        "MORPHIC_HARMONIZATION_JOBS_DIR",
        str(Path(__file__).parent.parent / "data" / "harmonization_jobs"),
    )
)
durable_mkdir_parents(JOBS_DIR, mode=0o700)
EVENTS_DIR = JOBS_DIR / "events"
_ACTIVE_REGISTRY_LOCK_ID = "__active_registry__"
_ACTIVE_REGISTRY_LOCK_FILE = f".{_ACTIVE_REGISTRY_LOCK_ID}.lock"

_HARMONIZATION_INTENTIONS = {
    "analysis",
    "regulation",
    "healing",
    "clearing",
    "protection",
    "transformation",
    "harmonization",
    "activation",
}


class HarmonizationStartOwnershipError(RuntimeError):
    pass


class HarmonizationJobOwnershipError(RuntimeError):
    pass


class HarmonizationStartIdentityError(RuntimeError):
    pass


class HarmonizationProcessAuthorityError(RuntimeError):
    pass


def normalize_harmonization_intention(value: object) -> str:
    if type(value) is not str:
        return "harmonization"
    cleaned = value.strip().lower()
    return cleaned if cleaned in _HARMONIZATION_INTENTIONS else "harmonization"


def _process_authority_service() -> LocalScanJobService:
    return LocalScanJobService(
        JOBS_DIR / ".process-authority",
        cwd=Path(__file__).resolve().parents[1],
        authority_namespace="harmonization",
    )


def _stop_marker_path(job_id: str) -> Path:
    job_id = validate_authority_id(job_id)
    return JOBS_DIR / f"{job_id}.stop"


@contextmanager
def _path_lock(lock_path: Path):
    durable_mkdir_parents(lock_path.parent, mode=0o700)
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(descriptor, b"0")
        os.fsync(descriptor)
        os.close(descriptor)
    except FileExistsError:
        pass
    with lock_path.open("r+b") as handle:
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


@contextmanager
def _job_lock(job_id: str):
    """Serialize stop markers and snapshots across worker/API processes."""
    job_id = validate_authority_id(job_id)
    with _path_lock(JOBS_DIR / f"{job_id}.lock"):
        yield


@contextmanager
def _active_registry_lock():
    with _path_lock(JOBS_DIR / _ACTIVE_REGISTRY_LOCK_FILE):
        yield


def _persisted_harmonization_id(job_id: object) -> str:
    try:
        return validate_authority_id(job_id)
    except AuthorityIdError as exc:
        raise RuntimeError("harmonization job record is unreadable") from exc


def _validate_persisted_authority_id(job: "HarmonizationJob") -> None:
    if job.authority_job_id is None:
        return
    try:
        authority_job_id = validate_scan_job_id_for_creation(job.authority_job_id)
        expected = validate_scan_job_id_for_creation(
            f"{HARMONIZATION_AUTHORITY_PREFIX}{job.job_id}"
        )
    except AuthorityIdError as exc:
        raise ValueError("harmonization process authority id is invalid") from exc
    if authority_job_id != expected:
        raise ValueError("harmonization process authority identity mismatch")


def _atomic_write_text(path: Path, content: str) -> None:
    durable_write_bytes(path, content.encode("utf-8"))

try:
    from core.hardware.snapshots import (
        build_hardware_snapshot_service,
        snapshot_sensor_entropy_probe,
    )
    from core.realtime.emf_profile import EMFProfileService
except Exception:  # pragma: no cover - optional realtime layer safety net
    build_hardware_snapshot_service = None
    snapshot_sensor_entropy_probe = None
    EMFProfileService = None


@dataclass
class HarmonizationJob:
    """Repräsentiert einen Harmonisierungs-Job."""
    
    job_id: str
    target_frequency: float
    duration_minutes: int
    intention: str
    hardware_config: Dict[str, object]

    # Status-Felder
    status: str = "pending"  # pending, running, completed, stopped, error
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    progress_percent: float = 0.0
    error_message: Optional[str] = None
    
    # Statistiken
    cycles_completed: int = 0
    total_cycles: int = 0

    # Impuls/Pause/Solfeggio-Zyklus (Task 7)
    pulse_seconds: float = 3.0
    pause_seconds: float = 2.0
    duration_factor: int = 1
    solfeggio_base: float = 432.0

    # Persistente Workbench-Bindung fuer Ownership und Report-Nachvollziehbarkeit.
    report_id: Optional[str] = None
    workbench_mode: str = "standard"
    tenant_id: Optional[str] = None
    operator_id: Optional[str] = None

    # Lease: enables conservative post-restart diagnosis without auto-resuming work.
    worker_pid: Optional[int] = None
    worker_create_time: Optional[float] = None
    heartbeat_at: Optional[str] = None
    current_phase: str = "pending"
    schema_version: int = 2
    authority_job_id: Optional[str] = None
    forced_status: Optional[str] = None

    def to_dict(self) -> Dict:
        """Konvertiert Job zu Dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HarmonizationJob':
        """Erstellt Job aus Dictionary."""
        return parse_harmonization_job_record(data)
    
    def save(self):
        """Speichert Job in JSON-Datei."""
        _persisted_harmonization_id(self.job_id)
        _validate_persisted_authority_id(self)
        with _job_lock(self.job_id):
            self._save_locked()

    def _save_locked(self) -> None:
        job_id = _persisted_harmonization_id(self.job_id)
        _validate_persisted_authority_id(self)
        job_file = JOBS_DIR / f"{job_id}.json"
        stop_marker = _stop_marker_path(job_id)
        if stop_marker.exists() and job_file.exists() and self.status != "stopped":
            persisted = HarmonizationJob.load(job_id)
            if persisted is not None and persisted.status == "stopped":
                self.status = "stopped"
                self.current_phase = "stopped"
                self.end_time = persisted.end_time or self.end_time
        normalized = _normalized_harmonization_job_for_save(self)
        for field in fields(HarmonizationJob):
            setattr(self, field.name, getattr(normalized, field.name))
        _atomic_write_text(
            job_file,
            json.dumps(
                normalized.to_dict(),
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            ),
        )
    
    @classmethod
    def load(cls, job_id: str) -> Optional['HarmonizationJob']:
        """Lädt Job aus JSON-Datei."""
        job_id = _persisted_harmonization_id(job_id)
        job_file = JOBS_DIR / f"{job_id}.json"
        
        if not job_file.exists():
            return None
        
        try:
            with open(job_file, "r", encoding="utf-8") as f:
                data = json.load(f, object_pairs_hook=_strict_json_object)
            return parse_harmonization_job_record(data, expected_job_id=job_id)
        except Exception as exc:
            raise RuntimeError("harmonization job record is unreadable") from exc
    
    def delete(self):
        """Löscht Job-Datei."""
        job_id = _persisted_harmonization_id(self.job_id)
        job_file = JOBS_DIR / f"{job_id}.json"
        
        if job_file.exists():
            job_file.unlink()
        stop_marker = _stop_marker_path(job_id)
        if stop_marker.exists():
            stop_marker.unlink()
        event_file = EVENTS_DIR / f"{job_id}.jsonl"
        try:
            if event_file.exists():
                event_file.unlink()
        except OSError:
            pass


_HARMONIZATION_STATUSES = {
    "pending",
    "starting",
    "running",
    "completed",
    "stopped",
    "error",
    "interrupted",
    "authority_ambiguous",
}
_HARMONIZATION_PHASES_BY_STATUS = {
    "pending": {"pending", "preparing"},
    "starting": {"pending", "preparing", "starting", "initializing"},
    "running": {
        "pending",
        "starting",
        "initializing",
        "running",
        "harmonizing",
        "impulse",
        "pause",
        "finalizing",
    },
    "completed": {"completed"},
    "stopped": {"stopped"},
    "error": {"error"},
    "interrupted": {"interrupted"},
    "authority_ambiguous": {"authority_ambiguous"},
}
_LEGACY_ACTIVE_PHASES = {
    "pending",
    "preparing",
    "starting",
    "initializing",
    "running",
    "harmonizing",
    "impulse",
    "pause",
    "finalizing",
}
_LEGACY_REQUIRED_FIELDS = {
    "job_id",
    "target_frequency",
    "duration_minutes",
    "intention",
    "hardware_config",
    "status",
    "start_time",
    "end_time",
    "progress_percent",
    "error_message",
    "cycles_completed",
    "total_cycles",
}
_LEGACY_OPTIONAL_FIELDS = {
    "pulse_seconds",
    "pause_seconds",
    "duration_factor",
    "solfeggio_base",
    "report_id",
    "workbench_mode",
    "tenant_id",
    "operator_id",
    "worker_pid",
    "worker_create_time",
    "heartbeat_at",
    "current_phase",
    "authority_job_id",
    "forced_status",
}
_MISSING_SCHEMA = object()


def _strict_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate harmonization record field")
        result[key] = value
    return result


def _validate_json_safe(value: object) -> None:
    if value is None or type(value) in {str, bool, int}:
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("non-finite harmonization hardware value")
        return
    if type(value) is list:
        for item in value:
            _validate_json_safe(item)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise TypeError("harmonization hardware keys must be strings")
            _validate_json_safe(item)
        return
    raise TypeError("harmonization hardware configuration is not JSON-safe")


def _require_string(value: object, field_name: str, *, optional: bool = False) -> None:
    if value is None and optional:
        return
    if type(value) is not str:
        raise TypeError(f"harmonization {field_name} must be a string")


def _require_real(value: object, field_name: str, *, positive: bool = False) -> None:
    if type(value) not in {int, float}:
        raise TypeError(f"harmonization {field_name} must be a finite number")
    try:
        finite = math.isfinite(value)
    except OverflowError as exc:
        raise ValueError(f"harmonization {field_name} is out of range") from exc
    if not finite:
        raise TypeError(f"harmonization {field_name} must be a finite number")
    if (positive and value <= 0) or (not positive and value < 0):
        raise ValueError(f"harmonization {field_name} is out of range")


def _require_nonnegative_int(value: object, field_name: str) -> None:
    if type(value) is not int:
        raise TypeError(f"harmonization {field_name} must be an integer")
    if value < 0:
        raise ValueError(f"harmonization {field_name} is out of range")


def _parse_optional_timestamp(value: object, field_name: str) -> Optional[datetime]:
    if value is None:
        return None
    if type(value) is not str or not value.strip():
        raise TypeError(f"harmonization {field_name} must be an ISO timestamp")
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"harmonization {field_name} must be an ISO timestamp") from exc


def _legacy_defaults(data: dict[str, object]) -> dict[str, object]:
    normalized = dict(data)
    normalized.pop("schema_version", None)
    for field in fields(HarmonizationJob):
        if field.name in normalized:
            continue
        if field.default is not MISSING:
            normalized[field.name] = field.default
        elif field.default_factory is not MISSING:
            normalized[field.name] = field.default_factory()
        else:
            raise ValueError(f"missing harmonization field {field.name}")
    normalized["schema_version"] = 2
    return normalized


def parse_harmonization_job_record(
    data: object,
    *,
    expected_job_id: Optional[str] = None,
) -> HarmonizationJob:
    """Parse one persisted job shape without coercion or ownership inference."""
    if type(data) is not dict:
        raise TypeError("harmonization record must be an object")
    raw = dict(data)
    schema_version = raw.get("schema_version", _MISSING_SCHEMA)
    legacy = schema_version is _MISSING_SCHEMA or (
        type(schema_version) is int and schema_version == 1
    )
    if legacy:
        allowed = _LEGACY_REQUIRED_FIELDS | _LEGACY_OPTIONAL_FIELDS
        if schema_version is not _MISSING_SCHEMA:
            allowed = allowed | {"schema_version"}
        if not _LEGACY_REQUIRED_FIELDS.issubset(raw) or not set(raw).issubset(allowed):
            raise ValueError("invalid legacy harmonization record fields")
        phase_was_missing = "current_phase" not in raw
        normalized = _legacy_defaults(raw)
    else:
        if type(schema_version) is not int or schema_version != 2:
            raise ValueError("unsupported harmonization schema version")
        expected_fields = {field.name for field in fields(HarmonizationJob)}
        if set(raw) != expected_fields:
            raise ValueError("invalid v2 harmonization record fields")
        phase_was_missing = False
        normalized = raw

    job_id = _persisted_harmonization_id(normalized["job_id"])
    if expected_job_id is not None and job_id != expected_job_id:
        raise ValueError("harmonization job identity mismatch")
    _require_real(normalized["target_frequency"], "target_frequency", positive=True)
    _require_nonnegative_int(normalized["duration_minutes"], "duration_minutes")
    _require_string(normalized["intention"], "intention")
    if not normalized["intention"].strip():
        raise ValueError("harmonization intention is empty")
    if type(normalized["hardware_config"]) is not dict:
        raise TypeError("harmonization hardware_config must be an object")
    _validate_json_safe(normalized["hardware_config"])
    _require_string(normalized["status"], "status")
    status = normalized["status"]
    if status not in _HARMONIZATION_STATUSES:
        raise ValueError("invalid harmonization status")
    start_time = _parse_optional_timestamp(normalized["start_time"], "start_time")
    end_time = _parse_optional_timestamp(normalized["end_time"], "end_time")
    _require_real(normalized["progress_percent"], "progress_percent")
    if normalized["progress_percent"] > 100:
        raise ValueError("harmonization progress_percent is out of range")
    _require_string(normalized["error_message"], "error_message", optional=True)
    _require_nonnegative_int(normalized["cycles_completed"], "cycles_completed")
    _require_nonnegative_int(normalized["total_cycles"], "total_cycles")
    if normalized["cycles_completed"] > normalized["total_cycles"]:
        raise ValueError("harmonization cycles exceed total")
    _require_real(normalized["pulse_seconds"], "pulse_seconds", positive=True)
    _require_real(normalized["pause_seconds"], "pause_seconds", positive=True)
    _require_nonnegative_int(normalized["duration_factor"], "duration_factor")
    _require_real(normalized["solfeggio_base"], "solfeggio_base", positive=True)
    _require_string(normalized["report_id"], "report_id", optional=True)
    _require_string(normalized["workbench_mode"], "workbench_mode")
    _require_string(normalized["tenant_id"], "tenant_id", optional=True)
    _require_string(normalized["operator_id"], "operator_id", optional=True)
    worker_pid = normalized["worker_pid"]
    if worker_pid is not None:
        if type(worker_pid) is not int or worker_pid <= 0:
            raise TypeError("harmonization worker_pid must be a positive integer")
    worker_create_time = normalized["worker_create_time"]
    if worker_create_time is not None:
        _require_real(worker_create_time, "worker_create_time", positive=True)
    _parse_optional_timestamp(normalized["heartbeat_at"], "heartbeat_at")
    _require_string(normalized["current_phase"], "current_phase")
    phase = normalized["current_phase"]
    _require_string(normalized["authority_job_id"], "authority_job_id", optional=True)
    _require_string(normalized["forced_status"], "forced_status", optional=True)
    forced_status = normalized["forced_status"]
    if forced_status not in {None, "authority_ambiguous"}:
        raise ValueError("invalid harmonization forced_status")
    if status == "authority_ambiguous":
        if forced_status != "authority_ambiguous" or phase != "authority_ambiguous":
            raise ValueError("invalid authority-ambiguous harmonization state")
    elif forced_status is not None:
        raise ValueError("forced harmonization status does not match public status")
    if (
        legacy
        and not phase_was_missing
        and status in {"completed", "error", "stopped"}
        and phase in _LEGACY_ACTIVE_PHASES
    ):
        normalized["current_phase"] = status
        phase = status
    if not phase_was_missing and phase not in _HARMONIZATION_PHASES_BY_STATUS[status]:
        raise ValueError("harmonization phase does not match status")

    terminal = status in {"completed", "stopped", "error", "interrupted"}
    if terminal and end_time is None:
        raise ValueError("terminal harmonization record has no end_time")
    if status in {"pending", "starting", "running"} and end_time is not None:
        raise ValueError("active harmonization record has end_time")
    if start_time is not None and end_time is not None:
        try:
            if end_time < start_time:
                raise ValueError("harmonization end_time precedes start_time")
        except TypeError as exc:
            raise ValueError("harmonization timestamps use incompatible offsets") from exc
    if status == "completed":
        if normalized["progress_percent"] != 100 or normalized["error_message"] is not None:
            raise ValueError("invalid completed harmonization state")
    elif status == "error":
        if not normalized["error_message"]:
            raise ValueError("error harmonization record has no error_message")
    elif status == "interrupted":
        if not normalized["error_message"]:
            raise ValueError("interrupted harmonization record has no error_message")
    elif status == "authority_ambiguous":
        if not normalized["error_message"]:
            raise ValueError("ambiguous harmonization record has no error_message")
    elif normalized["error_message"] is not None:
        raise ValueError("non-error harmonization record has error_message")

    if status != "completed":
        total_cycles = normalized["total_cycles"]
        expected_progress = (
            normalized["cycles_completed"] / total_cycles * 100.0
            if total_cycles
            else 0.0
        )
        if not math.isclose(
            normalized["progress_percent"],
            expected_progress,
            rel_tol=1e-9,
            abs_tol=1e-9,
        ):
            raise ValueError("harmonization progress contradicts cycles")

    job = HarmonizationJob(**normalized)
    _validate_persisted_authority_id(job)
    return job


def _normalized_harmonization_job_for_save(job: HarmonizationJob) -> HarmonizationJob:
    data = job.to_dict()
    data["schema_version"] = 2
    now = _harmonization_now_iso(job)
    if job.status == "completed":
        data.update(
            current_phase="completed",
            end_time=job.end_time or now,
            progress_percent=100.0,
            error_message=None,
            forced_status=None,
        )
    elif job.status == "stopped":
        data.update(
            current_phase="stopped",
            end_time=job.end_time or now,
            error_message=None,
            forced_status=None,
        )
    elif job.status == "error":
        data.update(
            current_phase="error",
            end_time=job.end_time or now,
            error_message=job.error_message or "Harmonization failed.",
            forced_status=None,
        )
    elif job.status == "interrupted":
        data.update(
            current_phase="interrupted",
            end_time=job.end_time or now,
            error_message=(
                job.error_message
                or "Worker lease ended after confirmed process-tree exit."
            ),
            forced_status=None,
        )
    elif job.status == "authority_ambiguous":
        data.update(
            current_phase="authority_ambiguous",
            forced_status="authority_ambiguous",
            error_message=job.error_message or "Worker authority requires manual recovery.",
        )
    return parse_harmonization_job_record(data, expected_job_id=job.job_id)


def _harmonization_now_iso(job: HarmonizationJob) -> str:
    reference_value = job.start_time or job.heartbeat_at
    if reference_value is None:
        return datetime.now().isoformat()
    reference = datetime.fromisoformat(reference_value)
    if reference.tzinfo is None:
        return datetime.now().isoformat()
    return datetime.now(reference.tzinfo).isoformat()


def _canonical_harmonization_record_bytes(job: HarmonizationJob) -> bytes:
    return json.dumps(
        job.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _harmonization_record_revision(job: HarmonizationJob) -> str:
    return hashlib.sha256(_canonical_harmonization_record_bytes(job)).hexdigest()


def assert_harmonization_start_identity(
    job: HarmonizationJob,
    *,
    job_id: str,
    authority_job_id: str,
    target_frequency: float,
    duration_minutes: int,
    intention: str,
    hardware_config: Dict[str, object],
    pulse_seconds: float,
    pause_seconds: float,
    duration_factor: int,
    solfeggio_base: float,
    report_id: Optional[str],
    workbench_mode: str,
    tenant_id: Optional[str],
    operator_id: Optional[str],
) -> None:
    if job.tenant_id != tenant_id or job.operator_id != operator_id:
        raise HarmonizationStartOwnershipError(
            "harmonization job ownership mismatch"
        )
    if (
        job.job_id != job_id
        or job.authority_job_id != authority_job_id
        or job.report_id != report_id
        or job.workbench_mode != workbench_mode
        or type(job.intention) is not str
        or type(intention) is not str
        or normalize_harmonization_intention(job.intention)
        != normalize_harmonization_intention(intention)
        ):
        raise HarmonizationStartIdentityError(
            "harmonization start identity mismatch"
        )
    numeric_fields = (
        (job.target_frequency, target_frequency),
        (job.pulse_seconds, pulse_seconds),
        (job.pause_seconds, pause_seconds),
        (job.solfeggio_base, solfeggio_base),
    )
    if any(
        type(actual) not in {int, float}
        or type(actual) is not type(expected)
        or actual != expected
        for actual, expected in numeric_fields
        ):
        raise HarmonizationStartIdentityError(
            "harmonization start identity mismatch"
        )
    if (
        type(job.duration_minutes) is not int
        or type(duration_minutes) is not int
        or job.duration_minutes != duration_minutes
        or type(job.duration_factor) is not int
        or type(duration_factor) is not int
        or job.duration_factor != duration_factor
    ):
        raise HarmonizationStartIdentityError(
            "harmonization start identity mismatch"
        )
    if (
        type(job.hardware_config) is not dict
        or type(hardware_config) is not dict
        or set(job.hardware_config) != set(hardware_config)
        or any(
            type(job.hardware_config[key]) is not type(expected)
            or job.hardware_config[key] != expected
            for key, expected in hardware_config.items()
        )
    ):
        raise HarmonizationStartIdentityError(
            "harmonization start identity mismatch"
        )


def _harmonization_process_owner_id(
    tenant_id: Optional[str], operator_id: Optional[str]
) -> str | None:
    if (
        isinstance(tenant_id, str)
        and tenant_id.strip()
        and isinstance(operator_id, str)
        and operator_id.strip()
    ):
        return operator_owner_scope(
            OperatorContext(
                operator_id=operator_id,
                workspace_id="",
                tenant_id=tenant_id,
            )
        )
    if isinstance(operator_id, str) and operator_id.strip():
        return operator_id
    return None


def list_all_jobs() -> List[HarmonizationJob]:
    """
    Listet alle Jobs auf.
    
    Returns:
        Liste aller Jobs, sortiert nach Erstellungszeit
    """
    jobs = []
    
    for job_file in JOBS_DIR.glob("*.json"):
        job_id = job_file.stem
        job = HarmonizationJob.load(job_id)
        
        if job:
            jobs.append(job)
    
    # Sortiere nach Start-Zeit (neueste zuerst)
    jobs.sort(
        key=lambda j: j.start_time or "0000-00-00",
        reverse=True
    )
    
    return jobs


def get_active_jobs() -> List[HarmonizationJob]:
    """
    Gibt alle aktiven Jobs zurück.
    
    Returns:
        Liste der Jobs mit Status 'pending' oder 'running'
    """
    all_jobs = list_all_jobs()
    return [
        job
        for job in all_jobs
        if job.status in {"pending", "running", "starting", "authority_ambiguous"}
        or job.forced_status == "authority_ambiguous"
    ]


def cleanup_old_jobs(days: int = 7):
    """
    Löscht alte abgeschlossene Jobs.
    
    Args:
        days: Jobs älter als X Tage werden gelöscht
    """
    from datetime import timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for job in list_all_jobs():
        if job.status in ["completed", "stopped", "error"]:
            if job.end_time:
                try:
                    end_dt = datetime.fromisoformat(job.end_time)
                    if end_dt < cutoff_date:
                        job.delete()
                except:
                    pass


def _event_log():
    from core.realtime.event_log import RealtimeEventLog

    return RealtimeEventLog(EVENTS_DIR)


def _append_event(job_id: str, event_type: str, payload: Dict[str, object]) -> None:
    job_id = validate_authority_id(job_id)
    try:
        _event_log().append_best_effort(job_id, event_type, payload)
    except Exception:
        pass


def _commit_completed_job(job_id: str) -> Optional[HarmonizationJob]:
    """Persist and publish completion under the same stop-aware authority lock."""
    with _job_lock(job_id):
        current_job = HarmonizationJob.load(job_id)
        if (
            current_job is None
            or current_job.status not in {"pending", "running"}
            or _stop_marker_path(job_id).exists()
        ):
            return None
        current_job.status = "completed"
        current_job.current_phase = "completed"
        current_job.end_time = _harmonization_now_iso(current_job)
        current_job.progress_percent = 100.0
        current_job.error_message = None
        current_job.forced_status = None
        current_job._save_locked()
        if current_job.status != "completed":
            return None
        _append_event(
            job_id,
            "completed",
            {
                "cycles_completed": current_job.cycles_completed,
                "total_cycles": current_job.total_cycles,
                "progress_percent": current_job.progress_percent,
            },
        )
        return current_job


def _commit_error_job(job_id: str, error_message: str) -> Optional[HarmonizationJob]:
    """Persist and publish an error only when stop did not win the terminal race."""
    with _job_lock(job_id):
        current_job = HarmonizationJob.load(job_id)
        if (
            current_job is None
            or current_job.status not in {"pending", "running"}
            or _stop_marker_path(job_id).exists()
        ):
            return None
        current_job.status = "error"
        current_job.current_phase = "error"
        current_job.end_time = _harmonization_now_iso(current_job)
        current_job.error_message = error_message
        current_job.forced_status = None
        current_job._save_locked()
        if current_job.status != "error":
            return None
        _append_event(job_id, "error", {"error_message": error_message})
        return current_job


def _publish_stopped_locked(
    job: HarmonizationJob,
    *,
    stopped_at: Optional[str] = None,
) -> HarmonizationJob:
    job.status = "stopped"
    job.current_phase = "stopped"
    job.end_time = stopped_at or job.end_time or _harmonization_now_iso(job)
    job.error_message = None
    job.forced_status = None
    job._save_locked()
    return job


def _publish_interrupted_locked(job: HarmonizationJob) -> HarmonizationJob:
    job.status = "interrupted"
    job.current_phase = "interrupted"
    job.end_time = job.end_time or _harmonization_now_iso(job)
    job.error_message = "Worker lease ended after confirmed process-tree exit."
    job.forced_status = None
    job._save_locked()
    return job


def _publish_authority_ambiguous_locked(
    job: HarmonizationJob,
    message: str = "Worker authority requires manual recovery.",
) -> HarmonizationJob:
    job.status = "authority_ambiguous"
    job.current_phase = "authority_ambiguous"
    job.forced_status = "authority_ambiguous"
    job.error_message = message
    job._save_locked()
    return job


def _cancel_for_stop_marker(job_id: str) -> bool:
    return _stop_marker_path(job_id).exists()


def validate_harmonization_authority_snapshot(
    job: HarmonizationJob,
    authority_snapshot: object,
    *,
    reconcile_nonterminal: bool,
) -> tuple[str, str]:
    if not isinstance(authority_snapshot, dict):
        raise HarmonizationProcessAuthorityError(
            "harmonization process authority status is invalid"
        )
    authority_status = authority_snapshot.get("status")
    if type(authority_status) is not str or job.forced_status is not None:
        raise HarmonizationProcessAuthorityError(
            "harmonization process authority status is invalid"
        )
    raw_status = job.status
    if type(raw_status) is not str:
        raise HarmonizationProcessAuthorityError(
            "harmonization process authority status is invalid"
        )
    if authority_status in {"starting", "running"}:
        if raw_status in {"pending", "starting", "running"}:
            return raw_status, str(job.current_phase or raw_status)
        if authority_status == "running" and raw_status == "completed":
            return "running", "finalizing"
        if authority_status == "running" and raw_status == "error":
            if job.current_phase != "error":
                job.current_phase = "error"
                job._save_locked()
            return "error", "error"
        if (
            authority_status == "running"
            and raw_status == "stopped"
            and _stop_marker_path(job.job_id).exists()
        ):
            if (
                job.current_phase != "stopped"
                or job.forced_status is not None
                or not job.end_time
                or job.error_message is not None
            ):
                _publish_stopped_locked(job)
            return "stopped", "stopped"
        raise HarmonizationProcessAuthorityError(
            "harmonization process authority status is invalid"
        )
    if authority_status not in {"completed", "failed", "stopped"}:
        raise HarmonizationProcessAuthorityError(
            "harmonization process authority status is invalid"
        )
    if raw_status in {"pending", "starting", "running"}:
        if not reconcile_nonterminal:
            raise HarmonizationProcessAuthorityError(
                "harmonization process authority status is invalid"
            )
        if _stop_marker_path(job.job_id).exists():
            _publish_stopped_locked(job)
        else:
            _publish_interrupted_locked(job)
        raw_status = job.status
    if raw_status == "completed" and authority_status == "completed":
        if job.current_phase != "completed":
            job.current_phase = "completed"
            job._save_locked()
        return "completed", "completed"
    if raw_status == "error" and authority_status == "failed":
        if job.current_phase != "error":
            job.current_phase = "error"
            job._save_locked()
        return "error", "error"
    if (
        raw_status == "stopped"
        and _stop_marker_path(job.job_id).exists()
        and authority_status in {"completed", "failed", "stopped"}
    ):
        if (
            job.current_phase != "stopped"
            or job.forced_status is not None
            or not job.end_time
            or job.error_message is not None
        ):
            _publish_stopped_locked(job)
        return "stopped", "stopped"
    if raw_status == "interrupted" and authority_status in {
        "completed",
        "failed",
        "stopped",
    }:
        if (
            job.current_phase != "interrupted"
            or job.forced_status is not None
            or not job.end_time
            or not job.error_message
        ):
            _publish_interrupted_locked(job)
        return "interrupted", "interrupted"
    raise HarmonizationProcessAuthorityError(
        "harmonization process authority status is invalid"
    )


def _harmonization_lease_expired(
    job: HarmonizationJob,
    *,
    lease_seconds: int,
) -> bool:
    if job.heartbeat_at is None:
        return True
    heartbeat = datetime.fromisoformat(job.heartbeat_at)
    now = datetime.now(heartbeat.tzinfo) if heartbeat.tzinfo is not None else datetime.now()
    return (now - heartbeat).total_seconds() > lease_seconds


def reconcile_expired_harmonization_job_on_get(
    job_id: str,
    *,
    lease_seconds: int = 30,
    expected_tenant_id: Optional[str] = None,
    expected_operator_id: Optional[str] = None,
) -> HarmonizationJob:
    """Reconcile one expired active lease without holding its lock during I/O."""
    job_id = validate_authority_id(job_id)
    preflight = HarmonizationJob.load(job_id)
    if preflight is None:
        raise KeyError(job_id)
    with _job_lock(job_id):
        captured = HarmonizationJob.load(job_id)
        if captured is None:
            raise KeyError(job_id)
        if (
            expected_tenant_id is not None
            or expected_operator_id is not None
        ) and (
            captured.tenant_id != expected_tenant_id
            or captured.operator_id != expected_operator_id
        ):
            raise HarmonizationJobOwnershipError(
                "harmonization job ownership mismatch"
            )
        if (
            captured.status not in {"pending", "starting", "running"}
            or captured.forced_status is not None
            or not _harmonization_lease_expired(
                captured,
                lease_seconds=lease_seconds,
            )
        ):
            return captured
        captured_revision = _harmonization_record_revision(captured)
        authority_job_id = captured.authority_job_id
        if authority_job_id is None:
            return _publish_authority_ambiguous_locked(captured)

    authority_snapshot: object = None
    authority_error: Optional[BaseException] = None
    try:
        authority_snapshot = _process_authority_service().observe(authority_job_id)
    except BaseException as exc:
        authority_error = exc

    with _job_lock(job_id):
        current = HarmonizationJob.load(job_id)
        if current is None:
            raise KeyError(job_id)
        if (
            expected_tenant_id is not None
            or expected_operator_id is not None
        ) and (
            current.tenant_id != expected_tenant_id
            or current.operator_id != expected_operator_id
        ):
            raise HarmonizationJobOwnershipError(
                "harmonization job ownership mismatch"
            )
        if _harmonization_record_revision(current) != captured_revision:
            return current
        if current.status == "stopped":
            return current
        if authority_error is not None:
            return _publish_authority_ambiguous_locked(current)
        try:
            validate_harmonization_authority_snapshot(
                current,
                authority_snapshot,
                reconcile_nonterminal=True,
            )
        except BaseException:
            return _publish_authority_ambiguous_locked(current)
        return current


def measure_realtime_emf_profile(
    hardware_config: Optional[Dict[str, object]] = None,
) -> dict[str, object]:
    service_cls = EMFProfileService
    if service_cls is None:
        from core.realtime.emf_profile import EMFProfileService as service_cls

    return service_cls().measure().to_dict()


def _driver_provider_ids(config: Dict[str, object]) -> List[str]:
    raw_provider_ids = config.get("driver_provider_ids")
    if raw_provider_ids is None:
        return ["cpu_timing"]
    if isinstance(raw_provider_ids, str):
        return [raw_provider_ids]
    try:
        return [str(provider_id) for provider_id in raw_provider_ids]
    except TypeError:
        return ["cpu_timing"]


def capture_realtime_context(
    hardware_config: Optional[Dict[str, object]] = None,
) -> Dict[str, object]:
    config = hardware_config or {}
    authority_path = config.get("_emf_authority_path")
    if authority_path is None:
        return {}
    authority = EmfTelemetryAuthority(Path(str(authority_path)))
    measurement_generation = authority.begin_measurement()
    if measurement_generation is None:
        return {}
    if config.get("use_driver_layer") is not True:
        result = {"emf_profile": measure_realtime_emf_profile()}
        return result if authority.measurement_is_current(measurement_generation) else {}

    try:
        builder = build_hardware_snapshot_service
        probe_adapter = snapshot_sensor_entropy_probe
        service_cls = EMFProfileService
        if builder is None or probe_adapter is None or service_cls is None:
            from core.hardware.snapshots import (
                build_hardware_snapshot_service as builder,
                snapshot_sensor_entropy_probe as probe_adapter,
            )
            from core.realtime.emf_profile import EMFProfileService as service_cls

        service = builder(allow_device_open=False)
        snapshot = service.capture(provider_ids=_driver_provider_ids(config))
        emf_profile = service_cls(
            sensor_entropy_probe=lambda: probe_adapter(snapshot),
            sensor_source="hardware_snapshot",
        ).measure().to_dict()
        result = {
            "emf_profile": emf_profile,
            "hardware_snapshot": snapshot.to_dict(),
        }
        return result if authority.measurement_is_current(measurement_generation) else {}
    except Exception:
        profile = measure_realtime_emf_profile()
        result = {
            "emf_profile": profile,
            "hardware_snapshot": {
                "summary": {"health": "fallback"},
                "samples": [],
                "replay": {
                    "algorithm": "hardware-snapshot-v2",
                    "error": "hardware snapshot unavailable",
                },
            },
        }
        return result if authority.measurement_is_current(measurement_generation) else {}


# ============================================================================
# HARDWARE-MODULATION
# ============================================================================

def modulate_cpu_timing(
    frequency: float, duration_seconds: float = 1.0, should_continue=None
):
    """
    Moduliert CPU-Timing basierend auf Ziel-Frequenz.
    
    Args:
        frequency: Ziel-Frequenz in Hz
        duration_seconds: Dauer der Modulation
    """
    if frequency <= 0:
        return
    
    # Berechne Periode (Zeit pro Zyklus)
    period = 1.0 / frequency
    
    # Anzahl der Zyklen in der Dauer
    cycles = int(duration_seconds / period)
    
    start_time = time.perf_counter()
    
    completed_cycles = 0
    for _ in range(cycles):
        if should_continue is not None and not should_continue():
            break
        cycle_start = time.perf_counter()
        
        # Minimale CPU-Operation (um Timing-Jitter zu erzeugen)
        _ = sum(range(100))
        
        # Warte bis zum Ende der Periode
        elapsed = time.perf_counter() - cycle_start
        sleep_time = period - elapsed
        
        while sleep_time > 0:
            if should_continue is not None and not should_continue():
                break
            chunk = min(0.05, sleep_time)
            time.sleep(chunk)
            sleep_time -= chunk
        else:
            completed_cycles += 1
    
    actual_duration = time.perf_counter() - start_time
    actual_frequency = completed_cycles / actual_duration if actual_duration > 0 else 0
    
    return actual_frequency


def modulate_hardware(
    frequency: float,
    intention: str,
    config: Dict[str, bool],
    duration_seconds: float = 1.0,
    should_continue=None,
) -> Dict[str, float]:
    """
    Moduliert Hardware basierend auf Frequenz und Intention.
    
    Args:
        frequency: Ziel-Frequenz in Hz
        intention: Intention (healing, clearing, etc.)
        config: Hardware-Konfiguration
    
    Returns:
        Dictionary mit Modulations-Metriken
    """
    # Verwende erweiterte Hardware-Modulation
    try:
        from services.hardware_modulation import modulate_all_hardware
        
        metrics = modulate_all_hardware(
            frequency=frequency,
            intention=intention,
            config=config,
            duration_seconds=duration_seconds,
            should_continue=should_continue,
        )
        
        return metrics
    
    except ImportError:
        # Fallback: Nur CPU-Modulation
        metrics = {}
        
        if config.get("use_cpu", True):
            actual_freq = modulate_cpu_timing(
                frequency,
                duration_seconds=duration_seconds,
                should_continue=should_continue,
            )
            metrics["cpu_frequency"] = actual_freq
        
        return metrics


def execute_pulse_pause_cycle(
    *, pulse_seconds: float, pause_seconds: float, impulse, sleep=time.sleep, should_continue=None
) -> bool:
    """Run one observable impulse segment followed by a hardware-idle pause."""
    if should_continue is not None and not should_continue():
        return False
    impulse(pulse_seconds)
    if should_continue is not None and not should_continue():
        return False
    sleep(pause_seconds)
    return should_continue is None or should_continue()


# ============================================================================
# WORKER-PROZESS
# ============================================================================

def run_harmonization_worker(job_id: str) -> str:
    """
    Worker-Prozess für Harmonisierung.
    Läuft im Hintergrund, auch nach PowerShell-Schließung.
    
    Args:
        job_id: ID des Jobs
    """
    job_id = validate_authority_id(job_id)
    job = HarmonizationJob.load(job_id)
    if not job:
        print(f"[{job_id}] Job nicht gefunden", file=sys.stderr)
        return "error"
    with _job_lock(job_id):
        job = HarmonizationJob.load(job_id)
        if not job:
            print(f"[{job_id}] Job nicht gefunden", file=sys.stderr)
            return "error"
        if job.status == "stopped":
            return "stopped"
        if _stop_marker_path(job_id).exists():
            _append_event(
                job_id,
                "stop_requested",
                {
                    "cycles_completed": job.cycles_completed,
                    "progress_percent": job.progress_percent,
                },
            )
            return "stopped"
        job.status = "running"
        job.start_time = datetime.now().isoformat()
        job.worker_pid = os.getpid()
        job.worker_create_time = float(psutil.Process(job.worker_pid).create_time())
        job.heartbeat_at = job.start_time
        job.current_phase = "initializing"
        job._save_locked()
    _append_event(
        job_id,
        "job_started",
        {
            "target_frequency": job.target_frequency,
            "duration_minutes": job.duration_minutes,
            "intention": job.intention,
            "hardware_config": job.hardware_config,
        },
    )
    
    print(f"[{job_id}] Harmonisierung gestartet")
    print(f"  Frequenz: {job.target_frequency} Hz")
    print(f"  Dauer: {job.duration_minutes} Minuten")
    print(f"  Intention: {job.intention}")
    
    try:
        # Historische Semantik: Dauerfaktor × 21 Minuten; ein Zyklus ist Impuls + Pause.
        total_seconds = job.duration_factor * 21 * 60
        job.total_cycles = int(total_seconds / (job.pulse_seconds + job.pause_seconds))
        job.save()
        end_time = time.time() + total_seconds

        while time.time() < end_time:
            current_job = HarmonizationJob.load(job_id)
            marker_exists = _stop_marker_path(job_id).exists()
            if marker_exists or (
                current_job and current_job.status == "stopped"
            ):
                _append_event(
                    job_id,
                    "stop_requested",
                    {
                        "cycles_completed": current_job.cycles_completed,
                        "progress_percent": current_job.progress_percent,
                    },
                )
                print(f"[{job_id}] Harmonisierung gestoppt")
                return "stopped"

            cycle_start = time.time()
            metrics: Dict[str, float] = {}
            impulse_completed = True

            def run_impulse(duration: float) -> None:
                nonlocal metrics, impulse_completed
                _append_event(job_id, "harmonization_phase", {"phase": "impulse", "duration_seconds": duration})
                job.current_phase = "impulse"
                job.heartbeat_at = datetime.now().isoformat()
                job.save()
                if job.status == "stopped" or _cancel_for_stop_marker(job_id):
                    impulse_completed = False
                    return
                impulse_deadline = time.monotonic() + duration

                def impulse_may_continue() -> bool:
                    return time.monotonic() <= impulse_deadline and may_continue()

                metrics = modulate_hardware(
                    frequency=job.target_frequency,
                    intention=job.intention,
                    config=job.hardware_config,
                    duration_seconds=duration,
                    should_continue=impulse_may_continue,
                )
                if time.monotonic() > impulse_deadline + 0.1:
                    impulse_completed = False

            def may_continue() -> bool:
                current = HarmonizationJob.load(job_id)
                return not _stop_marker_path(job_id).exists() and (
                    current is None or current.status != "stopped"
                )

            def cycle_may_continue() -> bool:
                return impulse_completed and may_continue()

            def run_pause(duration: float) -> None:
                _append_event(job_id, "harmonization_phase", {"phase": "pause", "duration_seconds": duration})
                job.current_phase = "pause"
                job.heartbeat_at = datetime.now().isoformat()
                job.save()
                if job.status == "stopped":
                    return
                deadline = time.monotonic() + duration
                while time.monotonic() < deadline and may_continue():
                    remaining = max(0.0, deadline - time.monotonic())
                    time.sleep(min(0.1, remaining))

            cycle_finished = execute_pulse_pause_cycle(
                pulse_seconds=job.pulse_seconds,
                pause_seconds=job.pause_seconds,
                impulse=run_impulse,
                sleep=run_pause,
                should_continue=cycle_may_continue,
            )
            if not cycle_finished:
                current_job = HarmonizationJob.load(job_id)
                if _stop_marker_path(job_id).exists() or (
                    current_job and current_job.status == "stopped"
                ):
                    _append_event(
                        job_id,
                        "stop_requested",
                        {"cycles_completed": current_job.cycles_completed, "phase": job.current_phase},
                    )
                    return "stopped"
                continue

            cycle_number = job.cycles_completed + 1
            cycle_payload: Dict[str, object] = {
                "cycle": cycle_number,
                "metrics": metrics,
            }
            if cycle_number == 1 or cycle_number % 10 == 0:
                cycle_payload.update(capture_realtime_context(job.hardware_config))

            cycle_committed = False
            with _job_lock(job_id):
                current_job = HarmonizationJob.load(job_id)
                if (
                    current_job
                    and current_job.status != "stopped"
                    and not _stop_marker_path(job_id).exists()
                ):
                    cycle_number = current_job.cycles_completed + 1
                    cycle_payload["cycle"] = cycle_number
                    current_job.cycles_completed = cycle_number
                    current_job.progress_percent = (
                        current_job.cycles_completed / current_job.total_cycles
                    ) * 100
                    current_job.heartbeat_at = datetime.now().isoformat()
                    current_job._save_locked()
                    _append_event(job_id, "cycle_metrics", cycle_payload)
                    job = current_job
                    cycle_committed = True

            if not cycle_committed:
                current_job = HarmonizationJob.load(job_id)
                _append_event(
                    job_id,
                    "stop_requested",
                    {
                        "cycles_completed": current_job.cycles_completed if current_job else job.cycles_completed,
                        "progress_percent": current_job.progress_percent if current_job else job.progress_percent,
                    },
                )
                print(f"[{job_id}] Harmonisierung gestoppt")
                return "stopped"

            # Fortschritt ist jetzt je abgeschlossenem Impuls-/Pause-Zyklus persistent.
            
            # Impuls und Pause haben die gesamte Zyklusdauer bereits abgebildet.

        current_job = HarmonizationJob.load(job_id)
        marker_exists = _stop_marker_path(job_id).exists()
        if marker_exists or (
            current_job and current_job.status == "stopped"
        ):
            _append_event(
                job_id,
                "stop_requested",
                {
                    "cycles_completed": current_job.cycles_completed,
                    "progress_percent": current_job.progress_percent,
                },
            )
            print(f"[{job_id}] Harmonisierung gestoppt")
            return "stopped"
        
        committed_job = _commit_completed_job(job_id)
        if committed_job is None:
            print(f"[{job_id}] Harmonisierung vor Abschluss gestoppt")
            current_job = HarmonizationJob.load(job_id)
            if _stop_marker_path(job_id).exists() or (
                current_job and current_job.status == "stopped"
            ):
                return "stopped"
            return str(current_job.status if current_job else "error")
        job = committed_job

        print(f"[{job_id}] Harmonisierung abgeschlossen")
        print(f"  Zyklen: {job.cycles_completed}/{job.total_cycles}")
        return "completed"
    
    except Exception as e:
        committed_error = _commit_error_job(job_id, str(e))
        print(f"[{job_id}] Fehler: {e}", file=sys.stderr)
        if committed_error is not None:
            return "error"
        current_job = HarmonizationJob.load(job_id)
        if _stop_marker_path(job_id).exists() or (
            current_job and current_job.status == "stopped"
        ):
            return "stopped"
        return str(current_job.status if current_job else "error")


def _active_harmonization_jobs(
    jobs: List[HarmonizationJob],
) -> List[HarmonizationJob]:
    return [
        job
        for job in jobs
        if job.status in {"pending", "running", "starting", "authority_ambiguous"}
        or job.forced_status == "authority_ambiguous"
    ]


def _harmonization_reservation_blockers(
    jobs: List[HarmonizationJob],
    *,
    target_job_id: str,
    tenant_id: Optional[str],
    operator_id: Optional[str],
) -> List[HarmonizationJob]:
    requested_owner_complete = bool(
        isinstance(tenant_id, str)
        and tenant_id.strip()
        and isinstance(operator_id, str)
        and operator_id.strip()
    )
    return [
        job
        for job in _active_harmonization_jobs(jobs)
        if job.job_id != target_job_id
        and (
            job.status == "authority_ambiguous"
            or job.forced_status == "authority_ambiguous"
            or not requested_owner_complete
            or not (
                isinstance(job.tenant_id, str)
                and job.tenant_id.strip()
                and isinstance(job.operator_id, str)
                and job.operator_id.strip()
            )
            or (job.tenant_id == tenant_id and job.operator_id == operator_id)
        )
    ]


def _assert_harmonization_reservation_available(
    jobs: List[HarmonizationJob],
    *,
    target_job_id: str,
    tenant_id: Optional[str],
    operator_id: Optional[str],
) -> None:
    if _harmonization_reservation_blockers(
        jobs,
        target_job_id=target_job_id,
        tenant_id=tenant_id,
        operator_id=operator_id,
    ):
        raise RuntimeError(
            "active harmonization job exists or authority is ambiguous"
        )


def reconcile_harmonization_start(
    job_id: str,
    *,
    target_frequency: float,
    duration_minutes: int,
    intention: str,
    hardware_config: Dict[str, object],
    pulse_seconds: float,
    pause_seconds: float,
    duration_factor: int,
    solfeggio_base: float,
    report_id: Optional[str],
    workbench_mode: str,
    tenant_id: Optional[str],
    operator_id: Optional[str],
) -> tuple[HarmonizationJob, dict[str, object], tuple[str, str]]:
    with _active_registry_lock():
        return _reconcile_harmonization_start_locked(
            job_id,
            target_frequency=target_frequency,
            duration_minutes=duration_minutes,
            intention=intention,
            hardware_config=hardware_config,
            pulse_seconds=pulse_seconds,
            pause_seconds=pause_seconds,
            duration_factor=duration_factor,
            solfeggio_base=solfeggio_base,
            report_id=report_id,
            workbench_mode=workbench_mode,
            tenant_id=tenant_id,
            operator_id=operator_id,
        )


def _reconcile_harmonization_start_locked(
    job_id: str,
    *,
    target_frequency: float,
    duration_minutes: int,
    intention: str,
    hardware_config: Dict[str, object],
    pulse_seconds: float,
    pause_seconds: float,
    duration_factor: int,
    solfeggio_base: float,
    report_id: Optional[str],
    workbench_mode: str,
    tenant_id: Optional[str],
    operator_id: Optional[str],
) -> tuple[HarmonizationJob, dict[str, object], tuple[str, str]]:
    job_id = validate_authority_id(job_id)
    authority_job_id = validate_scan_job_id_for_creation(
        f"{HARMONIZATION_AUTHORITY_PREFIX}{job_id}"
    )
    authority_command = [
        sys.executable,
        "-m",
        "services.harmonization_process_entry",
        job_id,
    ]
    authority_owner_id = _harmonization_process_owner_id(tenant_id, operator_id)
    _assert_harmonization_reservation_available(
        list_all_jobs(),
        target_job_id=job_id,
        tenant_id=tenant_id,
        operator_id=operator_id,
    )
    authority_service = None
    newly_created = False
    try:
        with _job_lock(job_id):
            job = HarmonizationJob.load(job_id)
            if job is None:
                raise KeyError(job_id)
            assert_harmonization_start_identity(
                job,
                job_id=job_id,
                authority_job_id=authority_job_id,
                target_frequency=target_frequency,
                duration_minutes=duration_minutes,
                intention=intention,
                hardware_config=hardware_config,
                pulse_seconds=pulse_seconds,
                pause_seconds=pause_seconds,
                duration_factor=duration_factor,
                solfeggio_base=solfeggio_base,
                report_id=report_id,
                workbench_mode=workbench_mode,
                tenant_id=tenant_id,
                operator_id=operator_id,
            )
            pristine_pending = (
                job.status == "pending"
                and job.current_phase == "pending"
                and job.worker_pid is None
                and job.forced_status is None
            )
            authority_service = _process_authority_service()
            try:
                authority_snapshot = authority_service.get_for_replay(
                    authority_job_id,
                    expected_command=authority_command,
                    expected_owner_id=authority_owner_id,
                )
            except KeyError as exc:
                if not pristine_pending:
                    raise HarmonizationProcessAuthorityError(
                        "harmonization process authority is missing"
                    ) from exc
                if _stop_marker_path(job_id).exists():
                    _publish_stopped_locked(job)
                    snapshot = {"job_id": authority_job_id, "status": "stopped"}
                    return job, snapshot, ("stopped", "stopped")
                try:
                    authority_snapshot = authority_service.start(
                        authority_command,
                        owner_id=authority_owner_id,
                        env_overrides={
                            "MORPHIC_HARMONIZATION_JOBS_DIR": str(JOBS_DIR),
                        },
                        job_id=authority_job_id,
                    )
                except BaseException as start_error:
                    _publish_authority_ambiguous_locked(
                        job,
                        "worker process authority failed to start",
                    )
                    raise HarmonizationProcessAuthorityError(
                        "harmonization process authority failed to start"
                    ) from start_error
                newly_created = True
            except (OSError, RuntimeError, ValueError) as exc:
                raise HarmonizationProcessAuthorityError(
                    "harmonization process authority identity mismatch"
                ) from exc

            current = HarmonizationJob.load(job_id)
            if current is None:
                raise HarmonizationProcessAuthorityError(
                    "harmonization job authority disappeared"
                )
            assert_harmonization_start_identity(
                current,
                job_id=job_id,
                authority_job_id=authority_job_id,
                target_frequency=target_frequency,
                duration_minutes=duration_minutes,
                intention=intention,
                hardware_config=hardware_config,
                pulse_seconds=pulse_seconds,
                pause_seconds=pause_seconds,
                duration_factor=duration_factor,
                solfeggio_base=solfeggio_base,
                report_id=report_id,
                workbench_mode=workbench_mode,
                tenant_id=tenant_id,
                operator_id=operator_id,
            )
            status_phase = validate_harmonization_authority_snapshot(
                current,
                authority_snapshot,
                reconcile_nonterminal=not newly_created,
            )
            return current, authority_snapshot, status_phase
    except BaseException:
        if newly_created and authority_service is not None:
            try:
                converged = authority_service.stop(authority_job_id)
                if converged.get("status") not in {"stopped", "completed", "failed"}:
                    raise ProcessAuthorityAmbiguousError(
                        "new process authority did not converge"
                    )
            except BaseException as convergence_error:
                with _job_lock(job_id):
                    current = HarmonizationJob.load(job_id)
                    if current is not None:
                        _publish_authority_ambiguous_locked(
                            current,
                            "new process authority requires manual recovery",
                        )
                raise HarmonizationProcessAuthorityError(
                    "harmonization process authority cleanup is ambiguous"
                ) from convergence_error
        raise


def start_harmonization_job(
    target_frequency: float,
    duration_minutes: int,
    intention: str = "harmonization",
    hardware_config: Optional[Dict[str, object]] = None,
    pulse_seconds: float = 3.0,
    pause_seconds: float = 2.0,
    duration_factor: int = 1,
    solfeggio_base: float = 432.0,
    report_id: Optional[str] = None,
    workbench_mode: str = "standard",
    tenant_id: Optional[str] = None,
    operator_id: Optional[str] = None,
    job_id: Optional[str] = None,
) -> str:
    """
    Startet einen Harmonisierungs-Job im Hintergrund.

    Args:
        target_frequency: Ziel-Frequenz in Hz
        duration_minutes: Dauer in Minuten
        intention: Intention (healing, clearing, etc.)
        hardware_config: Hardware-Konfiguration
        pulse_seconds: Dauer eines Impuls-Segments in Sekunden
        pause_seconds: Dauer eines Pause-Segments in Sekunden
        duration_factor: Vielfaches von 21 Minuten (1 = 21 Min, 7 = 147 Min, ...)
        solfeggio_base: Solfeggio-Basisfrequenz in Hz

    Returns:
        Job-ID
    """
    job_id = validate_harmonization_job_id_for_creation(
        f"harm_{uuid.uuid4().hex[:8]}" if job_id is None else job_id
    )
    authority_job_id = validate_scan_job_id_for_creation(
        f"{HARMONIZATION_AUTHORITY_PREFIX}{job_id}"
    )
    with _active_registry_lock():
        if hardware_config is None:
            hardware_config = {
                "use_cpu": True,
                "use_gpu": False,
                "use_ram": False,
                "use_websocket": False,
                "use_quartz": False,
            }
        with _job_lock(job_id):
            existing_job = HarmonizationJob.load(job_id)
        if existing_job is not None:
            _reconcile_harmonization_start_locked(
                job_id,
                target_frequency=target_frequency,
                duration_minutes=duration_minutes,
                intention=intention,
                hardware_config=hardware_config,
                pulse_seconds=pulse_seconds,
                pause_seconds=pause_seconds,
                duration_factor=duration_factor,
                solfeggio_base=solfeggio_base,
                report_id=report_id,
                workbench_mode=workbench_mode,
                tenant_id=tenant_id,
                operator_id=operator_id,
            )
            return job_id
        recover_interrupted_harmonization_jobs()
        _assert_harmonization_reservation_available(
            list_all_jobs(),
            target_job_id=job_id,
            tenant_id=tenant_id,
            operator_id=operator_id,
        )

        job = HarmonizationJob(
            job_id=job_id,
            target_frequency=target_frequency,
            duration_minutes=duration_minutes,
            intention=intention,
            hardware_config=hardware_config,
            pulse_seconds=pulse_seconds,
            pause_seconds=pause_seconds,
            duration_factor=duration_factor,
            solfeggio_base=solfeggio_base,
            report_id=report_id,
            workbench_mode=workbench_mode,
            tenant_id=tenant_id,
            operator_id=operator_id,
            total_cycles=int(duration_factor * 21 * 60 / (pulse_seconds + pause_seconds)),
        )
        job.start_time = datetime.now().isoformat()
        job.heartbeat_at = job.start_time

        job.authority_job_id = authority_job_id
        stop_marker = _stop_marker_path(job_id)
        if stop_marker.exists():
            stop_marker.unlink()
        job.save()

        _reconcile_harmonization_start_locked(
            job_id,
            target_frequency=target_frequency,
            duration_minutes=duration_minutes,
            intention=intention,
            hardware_config=hardware_config,
            pulse_seconds=pulse_seconds,
            pause_seconds=pause_seconds,
            duration_factor=duration_factor,
            solfeggio_base=solfeggio_base,
            report_id=report_id,
            workbench_mode=workbench_mode,
            tenant_id=tenant_id,
            operator_id=operator_id,
        )

        return job_id


def _converge_harmonization_worker(job: HarmonizationJob) -> None:
    if not job.authority_job_id:
        if job.status == "pending" and job.worker_pid is None:
            return
        raise ProcessAuthorityAmbiguousError(
            "harmonization process-tree authority is unavailable"
        )
    authority_job_id = validate_authority_id(job.authority_job_id)
    service = _process_authority_service()
    try:
        result = service.stop(authority_job_id)
    except KeyError as exc:
        if (
            job.status == "pending"
            and job.current_phase == "pending"
            and job.worker_pid is None
            and job.forced_status is None
        ):
            return
        raise ProcessAuthorityAmbiguousError(
            "harmonization process-tree authority is missing"
        ) from exc
    status = str(result.get("status") or "")
    if status not in {"stopped", "completed", "failed"}:
        raise ProcessAuthorityAmbiguousError(
            "harmonization process-tree convergence was not confirmed"
        )


def stop_harmonization_job(
    job_id: str,
    *,
    expected_tenant_id: Optional[str] = None,
    expected_operator_id: Optional[str] = None,
) -> bool:
    """
    Stoppt einen laufenden Harmonisierungs-Job.
    
    Args:
        job_id: ID des Jobs
    
    Returns:
        True wenn erfolgreich gestoppt, False sonst
    """
    job_id = validate_authority_id(job_id)
    with _job_lock(job_id):
        job = HarmonizationJob.load(job_id)
        if not job:
            return False
        if (
            expected_tenant_id is not None
            or expected_operator_id is not None
        ) and (
            job.tenant_id != expected_tenant_id
            or job.operator_id != expected_operator_id
        ):
            raise HarmonizationJobOwnershipError(
                "harmonization job ownership mismatch"
            )
        if job.status not in {"pending", "starting", "running"}:
            return False
        stopped_at = _harmonization_now_iso(job)
        _atomic_write_text(_stop_marker_path(job_id), stopped_at)

    try:
        _converge_harmonization_worker(job)
    except BaseException:
        with _job_lock(job_id):
            current_job = HarmonizationJob.load(job_id)
            if current_job is not None:
                if (
                    expected_tenant_id is not None
                    or expected_operator_id is not None
                ) and (
                    current_job.tenant_id != expected_tenant_id
                    or current_job.operator_id != expected_operator_id
                ):
                    raise HarmonizationJobOwnershipError(
                        "harmonization job ownership mismatch"
                    )
                current_job.status = "authority_ambiguous"
                current_job.current_phase = "authority_ambiguous"
                current_job.forced_status = "authority_ambiguous"
                current_job.error_message = "process-tree convergence requires manual recovery"
                current_job._save_locked()
        raise

    with _job_lock(job_id):
        current_job = HarmonizationJob.load(job_id)
        if current_job is None:
            raise RuntimeError("harmonization job disappeared during stop")
        if (
            expected_tenant_id is not None
            or expected_operator_id is not None
        ) and (
            current_job.tenant_id != expected_tenant_id
            or current_job.operator_id != expected_operator_id
        ):
            raise HarmonizationJobOwnershipError(
                "harmonization job ownership mismatch"
            )
        _publish_stopped_locked(current_job, stopped_at=stopped_at)
    return True


def recover_interrupted_harmonization_jobs(*, lease_seconds: int = 30) -> List[str]:
    """Inspect expired leases through stable process-tree authority; fail closed."""
    recovered: List[str] = []
    for job in get_active_jobs():
        if job.status not in {"pending", "starting", "running"}:
            continue
        if not _harmonization_lease_expired(job, lease_seconds=lease_seconds):
            continue
        current = reconcile_expired_harmonization_job_on_get(
            job.job_id,
            lease_seconds=lease_seconds,
        )
        if current.status in {"pending", "starting", "running"}:
            continue
        reason = (
            "lease_authority_unreadable"
            if current.status == "authority_ambiguous"
            else "confirmed_process_tree_exit"
        )
        _append_event(
            job.job_id,
            str(current.forced_status or current.status),
            {"reason": reason},
        )
        recovered.append(job.job_id)
    return recovered


def authoritative_public_status(job: HarmonizationJob) -> tuple[str, str]:
    status = str(job.forced_status or job.status)
    phase = str(job.current_phase or status)
    return status, phase


# ============================================================================
# HELPER-FUNKTIONEN
# ============================================================================

def format_job_status(job: HarmonizationJob) -> str:
    """
    Formatiert Job-Status als Text.
    
    Args:
        job: Harmonisierungs-Job
    
    Returns:
        Formatierter Status-String
    """
    lines = []
    
    # Status-Symbol
    status_symbols = {
        "pending": "⏳",
        "running": "🔄",
        "completed": "✅",
        "stopped": "⏹️",
        "error": "❌"
    }
    
    symbol = status_symbols.get(job.status, "❓")
    
    lines.append(f"\n{symbol} Job: {job.job_id}")
    lines.append(f"   Status: {job.status}")
    lines.append(f"   Frequenz: {job.target_frequency} Hz")
    lines.append(f"   Dauer: {job.duration_minutes} Minuten")
    lines.append(f"   Intention: {job.intention}")
    
    if job.start_time:
        lines.append(f"   Gestartet: {job.start_time}")
    
    if job.status == "running":
        lines.append(f"   Fortschritt: {job.progress_percent:.1f}% ({job.cycles_completed}/{job.total_cycles} Zyklen)")
    
    if job.end_time:
        lines.append(f"   Beendet: {job.end_time}")
    
    if job.error_message:
        lines.append(f"   Fehler: {job.error_message}")
    
    # Hardware-Config
    active_hw = [k.replace("use_", "").upper() for k, v in job.hardware_config.items() if v]
    if active_hw:
        lines.append(f"   Hardware: {', '.join(active_hw)}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Test
    print("Harmonisierungs-Worker Service")
    print("=" * 70)
    
    # Teste Job-Erstellung
    print("\nTest: Job erstellen...")
    job_id = start_harmonization_job(
        target_frequency=432.0,
        duration_minutes=1,  # 1 Minute für Test
        intention="healing"
    )
    
    print(f"✅ Job erstellt: {job_id}")
    
    # Warte kurz
    time.sleep(2)
    
    # Lade Job und zeige Status
    job = HarmonizationJob.load(job_id)
    if job:
        print(format_job_status(job))
    
    print("\n" + "=" * 70)
    print("Test abgeschlossen")
