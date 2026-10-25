"""Additive, post-success persistence for already-built run manifests."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping
from uuid import uuid4

from apps.web.durable_io import durable_mkdir_parents


def persist_successful_run_manifest(
    run_snapshot: Mapping[str, object], manifest: Mapping[str, object], target: str | Path
) -> Path | None:
    """Atomically persist only a completed zero-exit snapshot; otherwise do nothing."""
    if run_snapshot.get("status") != "completed" or run_snapshot.get("returncode") != 0:
        return None
    path = Path(target)
    if path.exists():
        raise FileExistsError(f"run manifest already exists: {path}")
    durable_mkdir_parents(path.parent, mode=0o700)
    temporary = path.with_suffix(path.suffix + f".tmp.{uuid4().hex[:8]}")
    temporary.write_text(
        json.dumps(dict(manifest), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    temporary.replace(path)
    return path
