"""Additive structured progress events; not wired into the web job runtime."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from apps.web.durable_io import durable_mkdir_parents


_SAFE_FIELDS = (
    "job_id",
    "status",
    "returncode",
    "progress_percent",
    "current_phase",
    "current_substep",
    "completed_substeps",
)


def append_progress_event(
    path: str | Path, snapshot: Mapping[str, object], *, occurred_at: str
) -> dict[str, Any]:
    """Append a JSONL event from a strict allow-list; never serialize command/output."""
    event: dict[str, Any] = {"schema_version": 1, "occurred_at": occurred_at}
    event.update({field: snapshot.get(field) for field in _SAFE_FIELDS})
    target = Path(path)
    durable_mkdir_parents(target.parent, mode=0o700)
    with target.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
    return event
