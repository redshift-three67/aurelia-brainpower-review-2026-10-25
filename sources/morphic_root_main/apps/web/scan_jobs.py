from __future__ import annotations

import subprocess
import sys
import threading
import uuid
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Protocol, cast

# Windows: niedrige Prozess-Prioritaet, damit der Scan den Browser nicht einfriert
_CREATION_FLAGS = 0
if sys.platform == "win32":
    _CREATION_FLAGS = subprocess.BELOW_NORMAL_PRIORITY_CLASS


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


MAX_COMPLETED_SUBSTEPS = 8

_RATIO_RE = re.compile(r"\[(\d+)/(\d+)\]")
_LEADING_MARKERS_RE = re.compile(r"^(?:\[[^\]]+\]\s*)+")

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
    ("harmonization", "Nachbereitung", ("harmonisierung",)),
    ("trend", "Nachbereitung", ("trendbericht",)),
    ("interpretation", "Nachbereitung", ("deutungsbericht",)),
    ("remedy", "Nachbereitung", ("remedy",)),
    ("synergy", "Nachbereitung", ("synergy",)),
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


def _stage_details(line: str) -> tuple[int, str] | None:
    lowered = line.lower()
    for index, (_, phase, markers) in enumerate(_STAGE_DEFINITIONS):
        if any(marker in lowered for marker in markers):
            return index, phase
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
) -> dict[str, object]:
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        details = _stage_details(line)
        if details is None:
            continue

        stage_index, phase = details
        label = _normalize_substep_label(line)
        if not label:
            continue

        current_phase = phase
        current_substep = label

        ratio_match = _RATIO_RE.search(line)
        ratio_progress = 0.0
        if ratio_match is not None and not label.lower().startswith("phase "):
            numerator = int(ratio_match.group(1))
            denominator = int(ratio_match.group(2))
            if denominator > 0:
                ratio_progress = min(max(numerator / denominator, 0.0), 1.0)
        progress_percent = round(
            ((stage_index + ratio_progress) / len(_STAGE_DEFINITIONS)) * 100,
            1,
        )

        if label not in seen_labels:
            labels.append(label)
            seen_labels.add(label)

    if status == "completed":
        progress_percent = 100.0

    completed = labels[-MAX_COMPLETED_SUBSTEPS:]
    if status == "running" and current_substep in completed:
        completed = [label for label in completed if label != current_substep]

    return {
        "progress_percent": progress_percent,
        "current_phase": current_phase,
        "current_substep": current_substep,
        "completed_substeps": completed,
        "_all_labels": labels,
        "_seen_labels": seen_labels,
    }


def _read_incremental(path: Path, start: int) -> tuple[str, int]:
    if not path.exists():
        return "", start
    with path.open("rb") as handle:
        handle.seek(start)
        data = handle.read()
        end = handle.tell()
    return data.decode("utf-8", errors="replace"), end


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


class ScanJobStore(Protocol):
    def start(self, command: list[str], owner_id: str | None = ...) -> dict[str, object]: ...

    def get(self, job_id: str) -> dict[str, object]: ...


@dataclass
class _LocalScanJob:
    job_id: str
    command: list[str]
    process: subprocess.Popen[bytes]
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
    stdout_buffer: str = ""
    stderr_buffer: str = ""
    owner_id: str | None = None


class LocalScanJobService:
    def __init__(self, root: Path, cwd: Path | None = None) -> None:
        self.root = root
        self.cwd = cwd or Path(__file__).resolve().parents[2]
        self._jobs: dict[str, _LocalScanJob] = {}
        self._lock = threading.Lock()
        self.root.mkdir(parents=True, exist_ok=True)

    def start(self, command: list[str], owner_id: str | None = None) -> dict[str, object]:
        job_id = (
            f"scan-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
        )
        stdout_path = self.root / f"{job_id}.stdout.log"
        stderr_path = self.root / f"{job_id}.stderr.log"
        created_at = _utc_now()
        exec_command = _execution_command(command)

        with (
            stdout_path.open("ab") as stdout_file,
            stderr_path.open("ab") as stderr_file,
        ):
            process = subprocess.Popen(
                exec_command,
                cwd=self.cwd,
                env={
                    **os.environ,
                    "PYTHONIOENCODING": "utf-8",
                    "PYTHONUTF8": "1",
                },
                stdout=stdout_file,
                stderr=stderr_file,
                shell=False,
                creationflags=_CREATION_FLAGS,
            )

        job = _LocalScanJob(
            job_id=job_id,
            command=command,
            process=process,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            created_at=created_at,
            updated_at=created_at,
            owner_id=owner_id,
        )
        with self._lock:
            self._jobs[job_id] = job
        return self._snapshot(job)

    def get(self, job_id: str) -> dict[str, object]:
        with self._lock:
            job = self._jobs[job_id]
        return self._snapshot(job)

    def _snapshot(self, job: _LocalScanJob) -> dict[str, object]:
        returncode = job.process.poll()
        if returncode is None:
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
        progress = _update_progress_state(
            [*stdout_lines, *stderr_lines],
            status=status,
            labels=job.completed_labels,
            seen_labels=job.seen_labels,
            current_substep=job.current_substep,
            current_phase=job.current_phase,
            progress_percent=job.progress_percent,
        )
        job.progress_percent = cast(float | None, progress["progress_percent"])
        job.current_phase = cast(str | None, progress["current_phase"])
        job.current_substep = cast(str | None, progress["current_substep"])
        job.completed_labels = list(cast(list[str], progress["_all_labels"]))
        job.seen_labels = set(cast(set[str], progress["_seen_labels"]))
        return {
            "executes": True,
            "job_id": job.job_id,
            "status": status,
            "returncode": returncode,
            "command": job.command,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "stdout_tail": stdout_tail,
            "stderr_tail": stderr_tail,
            "progress_percent": job.progress_percent,
            "current_phase": job.current_phase,
            "current_substep": job.current_substep,
            "completed_substeps": progress["completed_substeps"],
            "owner_id": job.owner_id,
        }
