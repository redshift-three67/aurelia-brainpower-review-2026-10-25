from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
from pathlib import Path

import pytest

import core.admin_catalog.backup as backup_module
from core.admin_catalog.backup import (
    BACKUP_DATABASE_FILENAME,
    BACKUP_MANIFEST_FILENAME,
    BACKUP_MANIFEST_SCHEMA_VERSION,
    CATALOG_SCHEMA_VERSION,
    create_catalog_backup,
    restore_catalog_backup,
)
from core.admin_catalog.contracts import CatalogContext, CatalogEntry, EntryType
from core.admin_catalog.store import CatalogStore


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rewrite_completion_record(root: Path) -> None:
    backup_db = root / BACKUP_DATABASE_FILENAME
    manifest_path = root / BACKUP_MANIFEST_FILENAME
    completion = {
        "backup_completion_schema_version": 1,
        "catalog_schema_version": CATALOG_SCHEMA_VERSION,
        "database": {
            "filename": BACKUP_DATABASE_FILENAME,
            "sha256": _sha256(backup_db),
        },
        "manifest": {
            "filename": BACKUP_MANIFEST_FILENAME,
            "sha256": _sha256(manifest_path),
        },
        "no_productive_activation": True,
    }
    (root / "completion.json").write_text(
        json.dumps(completion, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _context() -> CatalogContext:
    return CatalogContext(
        operator_id="operator-backup",
        workspace_id="workspace-backup",
        tenant_id="tenant-backup",
        scope="workspace",
    )


def _catalog_database(tmp_path: Path, name: str = "catalog.sqlite3") -> Path:
    path = tmp_path / name
    store = CatalogStore(path)
    context = _context()
    store.create_draft(
        context,
        "draft-backup",
        [
            CatalogEntry(
                entry_type=EntryType.GROUP,
                entry_id="group-backup",
                context=context,
                source_id="synthetic-fixture",
                provenance="backup-test",
                data={"label": "Backup fixture", "enabled": True},
            )
        ],
    )
    return path


def _draft_count(path: Path) -> int:
    uri = f"{path.resolve().as_uri()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
        return int(connection.execute("SELECT COUNT(*) FROM catalog_drafts").fetchone()[0])


def test_backup_uses_hash_manifest_and_restores_logical_catalog(tmp_path: Path) -> None:
    source = _catalog_database(tmp_path)
    source_hash = _sha256(source)
    backup_root = tmp_path / "backup"

    manifest = create_catalog_backup(source, backup_root)

    backup_db = backup_root / BACKUP_DATABASE_FILENAME
    manifest_path = backup_root / BACKUP_MANIFEST_FILENAME
    assert manifest == {
        "backup_manifest_schema_version": BACKUP_MANIFEST_SCHEMA_VERSION,
        "catalog_schema_version": CATALOG_SCHEMA_VERSION,
        "database": {
            "bytes": backup_db.stat().st_size,
            "filename": BACKUP_DATABASE_FILENAME,
            "sha256": _sha256(backup_db),
        },
        "no_productive_activation": True,
    }
    assert json.loads(manifest_path.read_text(encoding="utf-8")) == manifest
    assert _sha256(source) == source_hash

    target = tmp_path / "restored.sqlite3"
    restored = restore_catalog_backup(backup_root, target)

    assert restored == target.resolve()
    assert _draft_count(restored) == 1
    assert _draft_count(source) == 1


def test_backup_writes_completion_record_as_final_bundle_authority(
    tmp_path: Path,
) -> None:
    source = _catalog_database(tmp_path)
    backup_root = tmp_path / "backup-completed"

    create_catalog_backup(source, backup_root)

    backup_db = backup_root / BACKUP_DATABASE_FILENAME
    manifest_path = backup_root / BACKUP_MANIFEST_FILENAME
    completion_path = backup_root / "completion.json"
    assert completion_path.is_file()
    assert json.loads(completion_path.read_text(encoding="utf-8")) == {
        "backup_completion_schema_version": 1,
        "catalog_schema_version": CATALOG_SCHEMA_VERSION,
        "database": {
            "filename": BACKUP_DATABASE_FILENAME,
            "sha256": _sha256(backup_db),
        },
        "manifest": {
            "filename": BACKUP_MANIFEST_FILENAME,
            "sha256": _sha256(manifest_path),
        },
        "no_productive_activation": True,
    }


def test_restore_requires_completion_record_before_creating_target(
    tmp_path: Path,
) -> None:
    source = _catalog_database(tmp_path)
    backup_root = tmp_path / "backup-incomplete"
    create_catalog_backup(source, backup_root)
    (backup_root / "completion.json").unlink(missing_ok=True)
    target = tmp_path / "restored.sqlite3"

    with pytest.raises(ValueError, match="completion"):
        restore_catalog_backup(backup_root, target)

    assert target.exists() is False


def test_backup_api_includes_committed_wal_state(tmp_path: Path) -> None:
    source = _catalog_database(tmp_path)
    writer = sqlite3.connect(source)
    try:
        assert writer.execute("PRAGMA journal_mode=WAL").fetchone()[0].lower() == "wal"
        writer.execute(
            "UPDATE catalog_drafts SET version = 7 WHERE draft_id = ?",
            ("draft-backup",),
        )
        writer.commit()
        assert source.with_name(f"{source.name}-wal").exists()

        backup_root = tmp_path / "backup-wal"
        create_catalog_backup(source, backup_root)
        with sqlite3.connect(backup_root / BACKUP_DATABASE_FILENAME) as connection:
            version = connection.execute(
                "SELECT version FROM catalog_drafts WHERE draft_id = ?",
                ("draft-backup",),
            ).fetchone()[0]
    finally:
        writer.close()

    assert version == 7


def test_backup_refuses_missing_non_file_and_existing_destination(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        create_catalog_backup(tmp_path / "missing.sqlite3", tmp_path / "backup-missing")

    directory = tmp_path / "directory.sqlite3"
    directory.mkdir()
    with pytest.raises(ValueError, match="file"):
        create_catalog_backup(directory, tmp_path / "backup-directory")

    source = _catalog_database(tmp_path, "source.sqlite3")
    backup_root = tmp_path / "existing-backup"
    backup_root.mkdir()
    with pytest.raises(FileExistsError):
        create_catalog_backup(source, backup_root)


def test_backup_refuses_source_symlink(tmp_path: Path) -> None:
    source = _catalog_database(tmp_path, "source.sqlite3")
    link = tmp_path / "source-link.sqlite3"
    try:
        link.symlink_to(source)
    except OSError as exc:
        pytest.skip(f"file symlinks unavailable: {exc}")
    with pytest.raises(ValueError, match="symlink|reparse"):
        create_catalog_backup(link, tmp_path / "backup-link")


def test_restore_detects_database_tampering_before_target_creation(tmp_path: Path) -> None:
    source = _catalog_database(tmp_path)
    backup_root = tmp_path / "backup"
    create_catalog_backup(source, backup_root)
    backup_db = backup_root / BACKUP_DATABASE_FILENAME
    backup_db.write_bytes(backup_db.read_bytes() + b"tamper")
    target = tmp_path / "restored.sqlite3"

    with pytest.raises(ValueError, match="integrity|hash|size"):
        restore_catalog_backup(backup_root, target)

    assert target.exists() is False


def test_restore_rejects_unsupported_or_malformed_manifest(tmp_path: Path) -> None:
    source = _catalog_database(tmp_path)
    backup_root = tmp_path / "backup"
    create_catalog_backup(source, backup_root)
    manifest_path = backup_root / BACKUP_MANIFEST_FILENAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["backup_manifest_schema_version"] = BACKUP_MANIFEST_SCHEMA_VERSION + 1
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="schema"):
        restore_catalog_backup(backup_root, tmp_path / "unsupported.sqlite3")

    manifest_path.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="manifest"):
        restore_catalog_backup(backup_root, tmp_path / "malformed.sqlite3")


def test_restore_never_overwrites_existing_target(tmp_path: Path) -> None:
    source = _catalog_database(tmp_path, "source.sqlite3")
    backup_root = tmp_path / "backup"
    create_catalog_backup(source, backup_root)

    existing_file = tmp_path / "existing.sqlite3"
    existing_file.write_bytes(b"")
    with pytest.raises(FileExistsError):
        restore_catalog_backup(backup_root, existing_file)
    assert existing_file.read_bytes() == b""

    active_store = _catalog_database(tmp_path, "active.sqlite3")
    active_hash = _sha256(active_store)
    with pytest.raises(FileExistsError):
        restore_catalog_backup(backup_root, active_store)
    assert _sha256(active_store) == active_hash


def test_restore_requires_existing_empty_parent_and_leaves_no_partial_target(
    tmp_path: Path,
) -> None:
    source = _catalog_database(tmp_path)
    backup_root = tmp_path / "backup"
    create_catalog_backup(source, backup_root)
    missing_parent_target = tmp_path / "missing-parent" / "restored.sqlite3"

    with pytest.raises(FileNotFoundError, match="parent"):
        restore_catalog_backup(backup_root, missing_parent_target)

    assert missing_parent_target.exists() is False
    assert missing_parent_target.parent.exists() is False


def test_restore_rejects_corrupt_sqlite_even_with_matching_manifest_hash(tmp_path: Path) -> None:
    source = _catalog_database(tmp_path)
    backup_root = tmp_path / "backup"
    create_catalog_backup(source, backup_root)
    backup_db = backup_root / BACKUP_DATABASE_FILENAME
    backup_db.write_bytes(b"not a sqlite database")
    manifest_path = backup_root / BACKUP_MANIFEST_FILENAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["database"]["bytes"] = backup_db.stat().st_size
    manifest["database"]["sha256"] = _sha256(backup_db)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    _rewrite_completion_record(backup_root)
    target = tmp_path / "restored.sqlite3"

    with pytest.raises(ValueError, match="SQLite|integrity"):
        restore_catalog_backup(backup_root, target)

    assert target.exists() is False


def test_restore_rejects_integral_non_catalog_sqlite_with_matching_manifest(
    tmp_path: Path,
) -> None:
    source = _catalog_database(tmp_path)
    backup_root = tmp_path / "backup"
    create_catalog_backup(source, backup_root)
    backup_db = backup_root / BACKUP_DATABASE_FILENAME
    backup_db.unlink()
    with sqlite3.connect(backup_db) as connection:
        connection.execute("CREATE TABLE unrelated(value TEXT)")
    manifest_path = backup_root / BACKUP_MANIFEST_FILENAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["database"]["bytes"] = backup_db.stat().st_size
    manifest["database"]["sha256"] = _sha256(backup_db)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    _rewrite_completion_record(backup_root)
    target = tmp_path / "restored.sqlite3"

    with pytest.raises(ValueError, match="catalog schema"):
        restore_catalog_backup(backup_root, target)

    assert target.exists() is False


def test_restore_rejects_noop_trigger_with_canonical_name(tmp_path: Path) -> None:
    source = _catalog_database(tmp_path)
    backup_root = tmp_path / "backup"
    create_catalog_backup(source, backup_root)
    backup_db = backup_root / BACKUP_DATABASE_FILENAME
    with sqlite3.connect(backup_db) as connection:
        connection.execute("DROP TRIGGER catalog_revisions_no_update")
        connection.execute(
            "CREATE TRIGGER catalog_revisions_no_update "
            "AFTER UPDATE ON catalog_revisions BEGIN SELECT 1; END"
        )
    manifest_path = backup_root / BACKUP_MANIFEST_FILENAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["database"]["bytes"] = backup_db.stat().st_size
    manifest["database"]["sha256"] = _sha256(backup_db)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    _rewrite_completion_record(backup_root)

    with pytest.raises(ValueError, match="catalog schema"):
        restore_catalog_backup(backup_root, tmp_path / "restored.sqlite3")


def test_restore_rejects_additional_semantic_schema_object(tmp_path: Path) -> None:
    source = _catalog_database(tmp_path)
    backup_root = tmp_path / "backup"
    create_catalog_backup(source, backup_root)
    backup_db = backup_root / BACKUP_DATABASE_FILENAME
    with sqlite3.connect(backup_db) as connection:
        connection.execute(
            "CREATE TRIGGER extra_catalog_mutation_guard "
            "BEFORE UPDATE ON catalog_drafts BEGIN SELECT RAISE(ABORT, 'extra'); END"
        )
    manifest_path = backup_root / BACKUP_MANIFEST_FILENAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["database"]["bytes"] = backup_db.stat().st_size
    manifest["database"]["sha256"] = _sha256(backup_db)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    _rewrite_completion_record(backup_root)

    with pytest.raises(ValueError, match="catalog schema"):
        restore_catalog_backup(backup_root, tmp_path / "restored.sqlite3")


def test_restore_rejects_unhashed_wal_sidecar_state(tmp_path: Path) -> None:
    source = _catalog_database(tmp_path)
    backup_root = tmp_path / "backup"
    create_catalog_backup(source, backup_root)
    backup_db = backup_root / BACKUP_DATABASE_FILENAME
    writer = sqlite3.connect(backup_db)
    try:
        assert writer.execute("PRAGMA journal_mode=WAL").fetchone()[0].lower() == "wal"
        manifest_path = backup_root / BACKUP_MANIFEST_FILENAME
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["database"]["bytes"] = backup_db.stat().st_size
        manifest["database"]["sha256"] = _sha256(backup_db)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        _rewrite_completion_record(backup_root)
        writer.execute(
            "UPDATE catalog_drafts SET version = 99 WHERE draft_id = ?",
            ("draft-backup",),
        )
        writer.commit()
        assert backup_db.with_name(f"{backup_db.name}-wal").exists()
        assert _sha256(backup_db) == manifest["database"]["sha256"]

        with pytest.raises(ValueError, match="sidecar|WAL|bundle|manifest"):
            restore_catalog_backup(backup_root, tmp_path / "restored.sqlite3")
    finally:
        writer.close()


def test_restore_revalidates_actual_temporary_snapshot_after_source_race(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = _catalog_database(tmp_path)
    backup_root = tmp_path / "backup"
    create_catalog_backup(source, backup_root)
    real_backup = backup_module._backup_database

    def inject_wal_before_copy(source_path: Path, target_path: Path) -> None:
        writer = sqlite3.connect(source_path)
        try:
            assert writer.execute("PRAGMA journal_mode=WAL").fetchone()[0].lower() == "wal"
            writer.execute(
                "UPDATE catalog_drafts SET version = 99 WHERE draft_id = ?",
                ("draft-backup",),
            )
            writer.commit()
            assert source_path.with_name(f"{source_path.name}-wal").exists()
            real_backup(source_path, target_path)
        finally:
            writer.close()

    monkeypatch.setattr(backup_module, "_backup_database", inject_wal_before_copy)
    target = tmp_path / "restored.sqlite3"

    with pytest.raises(ValueError, match="manifest|hash|size|schema|sidecar"):
        restore_catalog_backup(backup_root, target)

    assert target.exists() is False
    assert not list(tmp_path.glob(".restored.sqlite3.tmp-*"))


@pytest.mark.skipif(os.name != "nt", reason="Windows dangling junction contract")
def test_dangling_junction_cannot_be_backup_root_or_restore_target(tmp_path: Path) -> None:
    source = _catalog_database(tmp_path)
    missing_backup_target = tmp_path / "missing-backup-target"
    backup_junction = tmp_path / "backup-junction"
    created_backup = subprocess.run(
        ["cmd.exe", "/c", "mklink", "/J", str(backup_junction), str(missing_backup_target)],
        capture_output=True,
        check=False,
    )
    if created_backup.returncode != 0:
        pytest.skip("Windows dangling junction creation unavailable")
    try:
        with pytest.raises(ValueError, match="reparse|junction|symlink"):
            create_catalog_backup(source, backup_junction)
    finally:
        backup_junction.rmdir()

    backup_root = tmp_path / "backup"
    create_catalog_backup(source, backup_root)
    missing_restore_target = tmp_path / "missing-restore-target"
    restore_junction = tmp_path / "restore-junction.sqlite3"
    created_restore = subprocess.run(
        ["cmd.exe", "/c", "mklink", "/J", str(restore_junction), str(missing_restore_target)],
        capture_output=True,
        check=False,
    )
    if created_restore.returncode != 0:
        pytest.skip("Windows dangling junction creation unavailable")
    try:
        with pytest.raises(ValueError, match="reparse|junction|symlink"):
            restore_catalog_backup(backup_root, restore_junction)
        assert restore_junction.is_dir() is False
        assert restore_junction.lstat().st_file_attributes & 0x400
    finally:
        restore_junction.rmdir()


def test_restore_does_not_overwrite_target_created_during_restore(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = _catalog_database(tmp_path)
    backup_root = tmp_path / "backup"
    create_catalog_backup(source, backup_root)
    target = tmp_path / "concurrent.sqlite3"
    real_publish = backup_module._publish_without_overwrite

    def concurrent_publish(
        source_path: Path,
        target_path: Path,
        **kwargs: object,
    ) -> None:
        Path(target_path).write_bytes(b"concurrent-owner")
        real_publish(source_path, target_path, **kwargs)

    monkeypatch.setattr(backup_module, "_publish_without_overwrite", concurrent_publish)

    with pytest.raises(FileExistsError):
        restore_catalog_backup(backup_root, target)

    assert target.read_bytes() == b"concurrent-owner"
    assert not list(tmp_path.glob(".concurrent.sqlite3.tmp-*"))


def test_backup_closes_source_if_target_connection_open_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    class SourceConnection:
        closed = False

        def close(self) -> None:
            self.closed = True

    source_connection = SourceConnection()
    calls = 0

    def connect(*args: object, **kwargs: object) -> SourceConnection:
        nonlocal calls
        calls += 1
        if calls == 1:
            return source_connection
        raise sqlite3.OperationalError("synthetic target-open failure")

    monkeypatch.setattr(backup_module.sqlite3, "connect", connect)

    with pytest.raises(sqlite3.OperationalError, match="target-open"):
        backup_module._backup_database(
            tmp_path / "source.sqlite3",
            tmp_path / "target.sqlite3",
        )

    assert source_connection.closed is True


def test_backup_closes_both_connections_if_backup_api_raises(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    class Connection:
        def __init__(self, *, fail_backup: bool = False) -> None:
            self.closed = False
            self.fail_backup = fail_backup

        def backup(self, _target: object) -> None:
            if self.fail_backup:
                raise sqlite3.OperationalError("synthetic backup-api failure")

        def commit(self) -> None:
            pass

        def close(self) -> None:
            self.closed = True

    source_connection = Connection(fail_backup=True)
    target_connection = Connection()
    connections = iter((source_connection, target_connection))
    monkeypatch.setattr(
        backup_module.sqlite3,
        "connect",
        lambda *args, **kwargs: next(connections),
    )

    with pytest.raises(sqlite3.OperationalError, match="backup-api"):
        backup_module._backup_database(
            tmp_path / "source.sqlite3",
            tmp_path / "target.sqlite3",
        )

    assert source_connection.closed is True
    assert target_connection.closed is True


@pytest.mark.skipif(os.name != "nt", reason="Windows publication contract")
def test_windows_publication_does_not_depend_on_temp_unlink(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = tmp_path / "temporary.sqlite3"
    target = tmp_path / "restored.sqlite3"
    source.write_bytes(b"restored")
    real_unlink = Path.unlink

    def fail_source_unlink(path: Path, *args: object, **kwargs: object) -> None:
        if path == source:
            raise PermissionError("synthetic temp-unlink failure")
        real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", fail_source_unlink)

    backup_module._publish_without_overwrite(source, target)

    assert target.read_bytes() == b"restored"
    assert source.exists() is False


def test_backup_rejects_integral_non_catalog_sqlite_before_creating_destination(
    tmp_path: Path,
) -> None:
    source = tmp_path / "unrelated.sqlite3"
    with sqlite3.connect(source) as connection:
        connection.execute("CREATE TABLE unrelated(value TEXT)")
    backup_root = tmp_path / "backup"

    with pytest.raises(ValueError, match="catalog schema"):
        create_catalog_backup(source, backup_root)

    assert backup_root.exists() is False


def test_backup_rejects_lookalike_catalog_tables_with_wrong_structure(tmp_path: Path) -> None:
    source = tmp_path / "lookalike.sqlite3"
    with sqlite3.connect(source) as connection:
        for table in (
            "catalog_activations",
            "catalog_audit_events",
            "catalog_drafts",
            "catalog_revision_entries",
            "catalog_revisions",
        ):
            connection.execute(f"CREATE TABLE {table}(placeholder TEXT)")
    backup_root = tmp_path / "backup-lookalike"

    with pytest.raises(ValueError, match="catalog schema"):
        create_catalog_backup(source, backup_root)

    assert backup_root.exists() is False


def test_create_and_restore_failures_remove_owned_temporary_artifacts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = _catalog_database(tmp_path)
    failed_backup_root = tmp_path / "failed-backup"

    def fail_after_partial_write(_source: Path, target: Path) -> None:
        target.write_bytes(b"partial")
        raise RuntimeError("synthetic backup failure")

    monkeypatch.setattr(backup_module, "_backup_database", fail_after_partial_write)
    with pytest.raises(RuntimeError, match="synthetic backup"):
        create_catalog_backup(source, failed_backup_root)
    assert failed_backup_root.exists() is False

    monkeypatch.undo()
    backup_root = tmp_path / "backup"
    create_catalog_backup(source, backup_root)
    monkeypatch.setattr(backup_module, "_backup_database", fail_after_partial_write)
    target = tmp_path / "failed-restore.sqlite3"
    with pytest.raises(RuntimeError, match="synthetic backup"):
        restore_catalog_backup(backup_root, target)
    assert target.exists() is False
    assert not list(tmp_path.glob(".failed-restore.sqlite3.tmp-*"))


@pytest.mark.parametrize("value", ["relative/path", "../escape", "safe/../escape"])
def test_backup_and_restore_reject_relative_or_traversing_paths(
    tmp_path: Path,
    value: str,
) -> None:
    source = _catalog_database(tmp_path)

    with pytest.raises(ValueError, match="absolute|traversal"):
        create_catalog_backup(value, tmp_path / "backup-source")
    with pytest.raises(ValueError, match="absolute|traversal"):
        create_catalog_backup(source, value)
    with pytest.raises(ValueError, match="absolute|traversal"):
        restore_catalog_backup(value, tmp_path / "restore.sqlite3")
    with pytest.raises(ValueError, match="absolute|traversal"):
        restore_catalog_backup(tmp_path / "missing-backup", value)


def test_backup_rejects_sqlite_stat_schema_object(tmp_path: Path) -> None:
    source = _catalog_database(tmp_path)
    with sqlite3.connect(source) as connection:
        connection.execute("ANALYZE")
        assert connection.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE name = 'sqlite_stat1'"
        ).fetchone()[0] == 1
    backup_root = tmp_path / "backup-stat"

    with pytest.raises(ValueError, match="catalog schema"):
        create_catalog_backup(source, backup_root)

    assert backup_root.exists() is False


def test_create_revalidates_actual_snapshot_after_source_schema_race(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = _catalog_database(tmp_path)
    backup_root = tmp_path / "backup-race"
    real_backup = backup_module._backup_database

    def mutate_schema_before_copy(source_path: Path, target_path: Path) -> None:
        with sqlite3.connect(source_path) as connection:
            connection.execute("CREATE TABLE unexpected_after_precheck(value TEXT)")
        real_backup(source_path, target_path)

    monkeypatch.setattr(backup_module, "_backup_database", mutate_schema_before_copy)

    with pytest.raises(ValueError, match="catalog schema"):
        create_catalog_backup(source, backup_root)

    assert backup_root.exists() is False


def test_create_rejects_same_size_snapshot_mutation_before_publish(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = _catalog_database(tmp_path)
    backup_root = tmp_path / "backup-mutated-before-publish"
    real_publish = backup_module._publish_without_overwrite
    mutated = False

    def mutate_database_then_publish(
        source_path: Path,
        target_path: Path,
        **kwargs: object,
    ) -> None:
        nonlocal mutated
        if target_path.name == BACKUP_DATABASE_FILENAME:
            before_size = source_path.stat().st_size
            before_hash = _sha256(source_path)
            connection = sqlite3.connect(source_path)
            try:
                connection.execute(
                    "UPDATE catalog_drafts SET draft_id = ? WHERE draft_id = ?",
                    ("draft-tamper", "draft-backup"),
                )
                connection.commit()
            finally:
                connection.close()
            after_size = source_path.stat().st_size
            after_hash = _sha256(source_path)
            assert after_size == before_size
            assert after_hash != before_hash
            mutated = True
        real_publish(source_path, target_path, **kwargs)

    monkeypatch.setattr(
        backup_module, "_publish_without_overwrite", mutate_database_then_publish
    )

    with pytest.raises(ValueError, match="published|snapshot|hash|schema"):
        create_catalog_backup(source, backup_root)

    assert mutated is True
    assert backup_root.exists() is False


def test_restore_rechecks_published_target_without_unsafe_postpublish_delete(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = _catalog_database(tmp_path)
    backup_root = tmp_path / "backup"
    create_catalog_backup(source, backup_root)
    target = tmp_path / "restored.sqlite3"
    real_publish = backup_module._publish_without_overwrite

    def alter_then_publish(
        source_path: Path,
        target_path: Path,
        **kwargs: object,
    ) -> None:
        source_path.write_bytes(source_path.read_bytes() + b"changed-after-check")
        real_publish(source_path, target_path, **kwargs)

    monkeypatch.setattr(backup_module, "_publish_without_overwrite", alter_then_publish)

    with pytest.raises(ValueError, match="published|manifest|hash|size|integrity"):
        restore_catalog_backup(backup_root, target)

    assert target.exists() is True


def test_restore_rejects_unmanifested_backup_bundle_file(tmp_path: Path) -> None:
    source = _catalog_database(tmp_path)
    backup_root = tmp_path / "backup"
    create_catalog_backup(source, backup_root)
    (backup_root / "catalog.sqlite3-mj synthetic").write_bytes(b"extra")

    with pytest.raises(ValueError, match="manifest|bundle|extra"):
        restore_catalog_backup(backup_root, tmp_path / "restored.sqlite3")


def test_source_close_runs_even_when_target_close_raises(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    class SourceConnection:
        closed = False

        def backup(self, _target: object) -> None:
            pass

        def close(self) -> None:
            self.closed = True

    class TargetConnection:
        def execute(self, _sql: str) -> object:
            class Result:
                @staticmethod
                def fetchone() -> tuple[str]:
                    return ("delete",)

            return Result()

        def commit(self) -> None:
            pass

        def close(self) -> None:
            raise sqlite3.OperationalError("synthetic target-close failure")

    source_connection = SourceConnection()
    connections = iter((source_connection, TargetConnection()))
    monkeypatch.setattr(
        backup_module.sqlite3,
        "connect",
        lambda *args, **kwargs: next(connections),
    )

    with pytest.raises(sqlite3.OperationalError, match="target-close"):
        backup_module._backup_database(
            tmp_path / "source.sqlite3",
            tmp_path / "target.sqlite3",
        )

    assert source_connection.closed is True


def test_failed_postpublish_check_preserves_externally_created_sidecar(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = _catalog_database(tmp_path)
    backup_root = tmp_path / "backup"
    create_catalog_backup(source, backup_root)
    target = tmp_path / "restored.sqlite3"
    external_sidecar = target.with_name(f"{target.name}-wal")
    real_check = backup_module._assert_no_sqlite_sidecars

    def add_external_sidecar_before_target_check(database: Path) -> None:
        if database == target:
            external_sidecar.write_bytes(b"external-owner")
        real_check(database)

    monkeypatch.setattr(
        backup_module,
        "_assert_no_sqlite_sidecars",
        add_external_sidecar_before_target_check,
    )

    with pytest.raises(ValueError, match="sidecar|WAL|journal"):
        restore_catalog_backup(backup_root, target)

    assert target.exists() is True
    assert external_sidecar.read_bytes() == b"external-owner"


def test_postpublish_failure_never_unlinks_a_racing_replacement(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = _catalog_database(tmp_path)
    backup_root = tmp_path / "backup"
    create_catalog_backup(source, backup_root)
    target = tmp_path / "restored.sqlite3"
    external_sidecar = target.with_name(f"{target.name}-wal")
    real_check = backup_module._assert_no_sqlite_sidecars
    real_unlink = Path.unlink
    raced = False

    def fail_target_sidecar_check(database: Path) -> None:
        if database == target:
            external_sidecar.write_bytes(b"external-owner")
        real_check(database)

    def replace_target_during_unlink(path: Path, *args: object, **kwargs: object) -> None:
        nonlocal raced
        if path == target:
            raced = True
            replacement = target.with_name("foreign-replacement.sqlite3")
            replacement.write_bytes(b"foreign-owner")
            os.replace(replacement, target)
        real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(backup_module, "_assert_no_sqlite_sidecars", fail_target_sidecar_check)
    monkeypatch.setattr(Path, "unlink", replace_target_during_unlink)

    with pytest.raises(ValueError, match="sidecar|WAL|journal"):
        restore_catalog_backup(backup_root, target)

    assert target.exists() is True
    if raced:
        assert target.read_bytes() == b"foreign-owner"
