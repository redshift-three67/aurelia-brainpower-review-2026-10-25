from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from core.compliance.synthetic_backup import (
    create_synthetic_backup,
    restore_synthetic_backup,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_synthetic_backup_and_restore_preserve_sources_and_verify_contents(tmp_path: Path) -> None:
    source_root = tmp_path / "synthetic-runtime"
    source_root.mkdir()
    first = source_root / "runtime.json"
    nested = source_root / "workbench" / "run_traces.json"
    nested.parent.mkdir()
    first.write_text('{"synthetic": true}\n', encoding="utf-8")
    nested.write_text('{"run_traces": []}\n', encoding="utf-8")
    source_hashes = {path.relative_to(source_root).as_posix(): _sha256(path) for path in (first, nested)}

    backup_root = tmp_path / "backup"
    manifest = create_synthetic_backup(source_root, backup_root)
    restore_root = tmp_path / "restored"
    restored = restore_synthetic_backup(backup_root, restore_root)

    assert manifest["schema_version"] == 1
    assert manifest["source_file_count"] == 2
    assert manifest["no_productive_activation"] is True
    assert {entry["path"]: entry["sha256"] for entry in manifest["files"]} == source_hashes
    assert {path.relative_to(source_root).as_posix(): _sha256(path) for path in (first, nested)} == source_hashes
    assert restored == restore_root
    assert {path.relative_to(restore_root).as_posix(): _sha256(path) for path in restore_root.rglob("*") if path.is_file()} == source_hashes
    persisted_manifest = json.loads((backup_root / "manifest.json").read_text(encoding="utf-8"))
    assert persisted_manifest == manifest


def test_synthetic_backup_refuses_project_paths_before_copy_or_restore(tmp_path: Path) -> None:
    source_root = tmp_path / "synthetic-runtime"
    source_root.mkdir()
    (source_root / "runtime.json").write_text("{}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="temporary"):
        create_synthetic_backup(Path.cwd(), tmp_path / "backup")

    backup_root = tmp_path / "backup"
    create_synthetic_backup(source_root, backup_root)
    with pytest.raises(ValueError, match="temporary"):
        restore_synthetic_backup(backup_root, Path.cwd() / "restored")
