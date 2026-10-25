from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class RealtimeEventLog:
    root: Path

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self._sequences: dict[Path, int] = {}

    def _path(self, job_id: str) -> Path:
        safe_job_id = "".join(
            ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in job_id
        )
        return self.root / f"{safe_job_id}.jsonl"

    def _next_sequence(self, path: Path) -> int:
        if path in self._sequences:
            self._sequences[path] += 1
            return self._sequences[path]
        if not path.exists():
            self._sequences[path] = 1
            return 1
        try:
            sequence = len(path.read_text(encoding="utf-8").splitlines()) + 1
        except OSError:
            sequence = 1
        self._sequences[path] = sequence
        return sequence

    def append(
        self, job_id: str, event_type: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        self.root.mkdir(parents=True, exist_ok=True)
        path = self._path(job_id)
        event = {
            "timestamp": datetime.now().isoformat(),
            "job_id": job_id,
            "event_type": event_type,
            "payload": payload,
            "sequence": self._next_sequence(path),
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        return event

    def append_best_effort(
        self, job_id: str, event_type: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        try:
            return self.append(job_id, event_type, payload)
        except Exception:
            return None
