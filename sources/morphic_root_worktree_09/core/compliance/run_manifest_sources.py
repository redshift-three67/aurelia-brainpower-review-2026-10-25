"""Explicit read-only source hashes for a future Run-Manifest integration."""
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path
from typing import Mapping


_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
_COMMIT = re.compile(r"^[0-9a-f]{40}$")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _hash_source_map(sources: Mapping[str, str | Path] | None) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_name, raw_path in sorted((sources or {}).items()):
        name = str(raw_name or "").strip()
        if not _NAME.fullmatch(name):
            raise ValueError("source name must be canonical")
        path = Path(raw_path)
        if not path.is_file() or path.is_symlink():
            raise FileNotFoundError(f"source file is missing or unsafe: {name}")
        result[name] = _sha256_file(path)
    return result


def collect_source_hashes(
    *,
    profile_sources: Mapping[str, str | Path] | None = None,
    data_sources: Mapping[str, str | Path] | None = None,
) -> dict[str, dict[str, str]]:
    """Read only explicit source files; no production path is inferred."""
    return {
        "profile_hashes": _hash_source_map(profile_sources),
        "data_hashes": _hash_source_map(data_sources),
    }


def resolve_git_commit(project_root: str | Path) -> str:
    """Return the current full Git commit without reading application data."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=Path(project_root),
        capture_output=True,
        text=True,
        check=False,
    )
    commit = result.stdout.strip().lower()
    if result.returncode != 0 or not _COMMIT.fullmatch(commit):
        raise RuntimeError("unable to resolve a full git commit")
    return commit
