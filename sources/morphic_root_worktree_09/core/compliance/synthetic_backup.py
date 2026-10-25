"""Temporary-only synthetic backup/restore feasibility helper.

This additive Phase-3 helper is not connected to productive runtime, export, or
backup paths. It accepts only paths below the operating system temporary root
and refuses to overwrite a restore target.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any


MANIFEST_FILENAME = "manifest.json"


def _temporary_path(path: str | Path, *, must_exist: bool, label: str) -> Path:
    target = Path(path).resolve()
    temporary_root = Path(tempfile.gettempdir()).resolve()
    try:
        target.relative_to(temporary_root)
    except ValueError as exc:
        raise ValueError(f"{label} must be below the operating system temporary directory") from exc
    if must_exist and not target.is_dir():
        raise ValueError(f"{label} must be an existing directory")
    return target


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _source_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError("synthetic backup refuses symbolic links")
        if path.is_file():
            files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def _relative_path(value: object) -> PurePosixPath:
    candidate = PurePosixPath(str(value))
    if not candidate.parts or candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        raise ValueError("backup manifest contains an unsafe relative path")
    return candidate


def _target(root: Path, relative: PurePosixPath) -> Path:
    target = (root / Path(*relative.parts)).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError("backup path escapes its root") from exc
    return target


def create_synthetic_backup(source_root: str | Path, backup_root: str | Path) -> dict[str, Any]:
    """Copy a synthetic temporary tree and write a hash manifest beside it."""
    source = _temporary_path(source_root, must_exist=True, label="source_root")
    backup = _temporary_path(backup_root, must_exist=False, label="backup_root")
    if backup.exists():
        raise ValueError("backup_root must not already exist")

    files = _source_files(source)
    backup.mkdir(parents=True)
    manifest_files: list[dict[str, object]] = []
    for source_file in files:
        relative = source_file.relative_to(source)
        destination = _target(backup, PurePosixPath(relative.as_posix()))
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, destination)
        manifest_files.append(
            {
                "path": relative.as_posix(),
                "bytes": source_file.stat().st_size,
                "sha256": _sha256(source_file),
            }
        )

    manifest: dict[str, Any] = {
        "schema_version": 1,
        "source_file_count": len(manifest_files),
        "files": manifest_files,
        "no_productive_activation": True,
    }
    (backup / MANIFEST_FILENAME).write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def restore_synthetic_backup(backup_root: str | Path, restore_root: str | Path) -> Path:
    """Verify a synthetic temporary backup before restoring it to a new temp root."""
    backup = _temporary_path(backup_root, must_exist=True, label="backup_root")
    restore = _temporary_path(restore_root, must_exist=False, label="restore_root")
    if restore.exists():
        raise ValueError("restore_root must not already exist")

    try:
        manifest = json.loads((backup / MANIFEST_FILENAME).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("backup manifest is missing or invalid") from exc
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise ValueError("backup manifest schema is unsupported")
    files = manifest.get("files")
    if not isinstance(files, list) or manifest.get("source_file_count") != len(files):
        raise ValueError("backup manifest file inventory is invalid")

    verified: list[tuple[Path, PurePosixPath]] = []
    for entry in files:
        if not isinstance(entry, dict):
            raise ValueError("backup manifest contains an invalid file entry")
        relative = _relative_path(entry.get("path"))
        source = _target(backup, relative)
        if not source.is_file() or source.is_symlink():
            raise ValueError("backup artifact is missing or unsafe")
        if source.stat().st_size != entry.get("bytes") or _sha256(source) != entry.get("sha256"):
            raise ValueError("backup artifact integrity check failed")
        verified.append((source, relative))

    restore.mkdir(parents=True)
    for source, relative in verified:
        destination = _target(restore, relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    return restore
