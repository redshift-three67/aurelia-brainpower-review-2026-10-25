from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

import core.admin_catalog.backup as backup_module
import core.admin_catalog.migration as migration_module
from core.admin_catalog.backup import (
    BACKUP_DATABASE_FILENAME,
    BACKUP_MANIFEST_FILENAME,
    CATALOG_SCHEMA_VERSION,
    create_catalog_backup,
    migrate_catalog_backup_v7_to_v8,
    restore_catalog_backup,
)
from core.admin_catalog.store import CatalogStore
from tests.admin_catalog_v7_fixture import (
    add_synthetic_preview_v8_attestation_shape,
    add_unknown_schema_object,
    create_v7_known_answer_backup,
)


def _bundle_hashes(root: Path) -> dict[str, str]:
    return {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in (BACKUP_DATABASE_FILENAME, BACKUP_MANIFEST_FILENAME)
    }


def _rewrite_v7_manifest_database(root: Path) -> None:
    database = root / BACKUP_DATABASE_FILENAME
    manifest_path = root / BACKUP_MANIFEST_FILENAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    database_entry = manifest["database"]
    assert isinstance(database_entry, dict)
    database_entry["bytes"] = database.stat().st_size
    database_entry["sha256"] = hashlib.sha256(database.read_bytes()).hexdigest()
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _assert_no_m3_snapshot(parent: Path, target_name: str) -> None:
    assert not list(parent.glob(f".{target_name}.v7-migration-*.sqlite3*"))


def test_migrate_exact_v7_backup_to_new_consumable_v8_bundle(tmp_path: Path) -> None:
    source = tmp_path / "v7-backup"
    create_v7_known_answer_backup(source)
    before = _bundle_hashes(source)
    target = tmp_path / "v8-backup"

    assert migrate_catalog_backup_v7_to_v8(source, target) == target.resolve()

    assert _bundle_hashes(source) == before
    manifest = json.loads((target / BACKUP_MANIFEST_FILENAME).read_text("utf-8"))
    assert manifest["catalog_schema_version"] == CATALOG_SCHEMA_VERSION
    restored = restore_catalog_backup(target, tmp_path / "restored-v8.sqlite3")
    assert restored.exists()
    _assert_no_m3_snapshot(tmp_path, target.name)


def test_normal_restore_rejects_v7_bundle_without_creating_database(tmp_path: Path) -> None:
    source = tmp_path / "v7-backup"
    create_v7_known_answer_backup(source)
    target = tmp_path / "v7-restore.sqlite3"

    with pytest.raises(ValueError, match="schema"):
        restore_catalog_backup(source, target)

    assert target.exists() is False


@pytest.mark.parametrize("tamper", ["manifest", "database", "sidecar"])
def test_migration_rejects_tampered_v7_bundle_without_target(
    tmp_path: Path, tamper: str
) -> None:
    source = tmp_path / "v7-backup"
    create_v7_known_answer_backup(source)
    target = tmp_path / "v8-backup"
    if tamper == "manifest":
        (source / BACKUP_MANIFEST_FILENAME).write_text("{}", encoding="utf-8")
    elif tamper == "database":
        database = source / BACKUP_DATABASE_FILENAME
        database.write_bytes(database.read_bytes() + b"tamper")
    else:
        (source / f"{BACKUP_DATABASE_FILENAME}-wal").write_bytes(b"tamper")

    with pytest.raises(ValueError):
        migrate_catalog_backup_v7_to_v8(source, target)

    assert target.exists() is False
    _assert_no_m3_snapshot(tmp_path, target.name)


@pytest.mark.parametrize(
    "mutator", [add_unknown_schema_object, add_synthetic_preview_v8_attestation_shape]
)
def test_migration_rejects_unknown_v7_lookalike_without_target(
    tmp_path: Path, mutator: object
) -> None:
    source = tmp_path / "v7-backup"
    create_v7_known_answer_backup(source)
    database = source / BACKUP_DATABASE_FILENAME
    assert callable(mutator)
    mutator(database)
    _rewrite_v7_manifest_database(source)

    with pytest.raises(ValueError, match="schema"):
        migrate_catalog_backup_v7_to_v8(source, tmp_path / "v8-backup")

    assert not (tmp_path / "v8-backup").exists()


def test_migration_rejects_current_v8_bundle_without_target(tmp_path: Path) -> None:
    source_database = tmp_path / "source-v8.sqlite3"
    CatalogStore(source_database)
    source = tmp_path / "v8-backup"
    create_catalog_backup(source_database, source)

    with pytest.raises(ValueError, match="schema"):
        migrate_catalog_backup_v7_to_v8(source, tmp_path / "migration-target")

    assert not (tmp_path / "migration-target").exists()


@pytest.mark.parametrize("phase", ["before_ddl", "after_ddl", "before_commit"])
def test_migration_fault_leaves_source_and_target_untouched(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, phase: str
) -> None:
    source = tmp_path / "v7-backup"
    create_v7_known_answer_backup(source)
    before = _bundle_hashes(source)
    target = tmp_path / "v8-backup"

    def fail_at_phase(_connection: sqlite3.Connection, current_phase: str) -> None:
        if current_phase == phase:
            raise RuntimeError(f"synthetic M3 migration fault at {phase}")

    monkeypatch.setattr(migration_module, "_migration_checkpoint", fail_at_phase)

    with pytest.raises(RuntimeError, match=phase):
        migrate_catalog_backup_v7_to_v8(source, target)

    assert _bundle_hashes(source) == before
    assert target.exists() is False
    _assert_no_m3_snapshot(tmp_path, target.name)


def test_migration_never_overwrites_existing_bundle_root(tmp_path: Path) -> None:
    source = tmp_path / "v7-backup"
    create_v7_known_answer_backup(source)
    target = tmp_path / "v8-backup"
    target.mkdir()
    marker = target / "foreign-owner"
    marker.write_bytes(b"foreign-owner")

    with pytest.raises(FileExistsError):
        migrate_catalog_backup_v7_to_v8(source, target)

    assert marker.read_bytes() == b"foreign-owner"
    _assert_no_m3_snapshot(tmp_path, target.name)


def test_migration_never_claims_a_preexisting_temporary_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "v7-backup"
    create_v7_known_answer_backup(source)
    target = tmp_path / "v8-backup"

    class KnownUuid:
        hex = "known"

    monkeypatch.setattr(backup_module, "uuid4", lambda: KnownUuid())
    temporary_snapshot = tmp_path / ".v8-backup.v7-migration-known.sqlite3"
    temporary_snapshot.write_bytes(b"foreign-owner")

    with pytest.raises(FileExistsError, match="temporary migration snapshot"):
        migrate_catalog_backup_v7_to_v8(source, target)

    assert temporary_snapshot.read_bytes() == b"foreign-owner"
    assert target.exists() is False


def test_migration_preserves_target_created_during_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "v7-backup"
    create_v7_known_answer_backup(source)
    target = tmp_path / "v8-backup"
    real_create = backup_module.create_catalog_backup

    def concurrent_create(source_db: Path, target_root: Path) -> dict[str, object]:
        target_root.mkdir()
        (target_root / "foreign-owner").write_bytes(b"foreign-owner")
        return real_create(source_db, target_root)

    monkeypatch.setattr(backup_module, "create_catalog_backup", concurrent_create)

    with pytest.raises(FileExistsError):
        migrate_catalog_backup_v7_to_v8(source, target)

    assert (target / "foreign-owner").read_bytes() == b"foreign-owner"
    _assert_no_m3_snapshot(tmp_path, target.name)
