"""Synthetic, opt-in-ready web-job manifest store; not wired into web runtime."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from apps.web.durable_io import durable_mkdir_parents


class WebJobManifestStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.path = self.root / "web_job_manifests.json"

    @staticmethod
    def _redact(command: object) -> list[str]:
        values = [str(item) for item in (command if isinstance(command, list) else [])]
        try:
            index = values.index("top3-scan")
        except ValueError:
            return ["[REDACTED]"] * len(values)
        return [*values[: index + 1], *(["[REDACTED]"] * (len(values) - index - 1))]

    def record(self, snapshot: Mapping[str, object]) -> dict[str, Any]:
        required = ("job_id", "status", "returncode", "owner_id", "tenant_id", "created_at", "updated_at")
        if any(not snapshot.get(key) for key in required if key != "returncode"):
            raise ValueError("incomplete web-job snapshot")
        entry = {key: snapshot.get(key) for key in required}
        entry["command"] = self._redact(snapshot.get("command"))
        entry["stdout_path"] = str(snapshot.get("stdout_path", ""))
        entry["stderr_path"] = str(snapshot.get("stderr_path", ""))
        entries = self.recover_read_only()
        entries = [item for item in entries if item.get("job_id") != entry["job_id"]]
        entries.insert(0, entry)
        durable_mkdir_parents(self.root, mode=0o700)
        tmp = self.path.with_suffix(self.path.suffix + f".tmp.{uuid4().hex[:8]}")
        tmp.write_text(json.dumps({"jobs": entries}, indent=2) + "\n", encoding="utf-8")
        tmp.replace(self.path)
        return entry

    def recover_read_only(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return list(payload.get("jobs", [])) if isinstance(payload, dict) else []
