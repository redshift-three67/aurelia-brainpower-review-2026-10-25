from __future__ import annotations

import json
from pathlib import Path

from core.compliance.progress_events import append_progress_event


def test_progress_event_writer_uses_shared_durable_parent_helper(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from core.compliance import progress_events

    calls: list[Path] = []

    def parent(path: Path, *, mode: int = 0o777) -> None:
        calls.append(Path(path))
        Path(path).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(progress_events, "durable_mkdir_parents", parent, raising=False)
    target = tmp_path / "nested" / "events" / "progress.jsonl"

    append_progress_event(target, {"job_id": "scan-parent"}, occurred_at="2026-07-24T00:00:00Z")

    assert calls == [target.parent]


def test_append_progress_event_writes_only_safe_structured_fields(tmp_path: Path) -> None:
    event_path = tmp_path / "progress.jsonl"
    snapshot = {
        "job_id": "scan-synthetic",
        "status": "running",
        "returncode": None,
        "progress_percent": 42.0,
        "current_phase": "Phase 1",
        "current_substep": "Screening",
        "completed_substeps": ["Vorbereitung"],
        "command": ["python", "top3-scan", "Mustermann"],
        "stdout_tail": "Mustermann",
    }

    event = append_progress_event(event_path, snapshot, occurred_at="2026-07-11T00:00:00Z")

    assert json.loads(event_path.read_text(encoding="utf-8")) == event
    assert event == {
        "schema_version": 1,
        "occurred_at": "2026-07-11T00:00:00Z",
        "job_id": "scan-synthetic",
        "status": "running",
        "returncode": None,
        "progress_percent": 42.0,
        "current_phase": "Phase 1",
        "current_substep": "Screening",
        "completed_substeps": ["Vorbereitung"],
    }
    assert "Mustermann" not in event_path.read_text(encoding="utf-8")
