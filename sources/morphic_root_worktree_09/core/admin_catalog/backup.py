"""Offline, hash-verified SQLite backup and non-overwriting recovery helpers."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import stat
from pathlib import Path
from uuid import uuid4


BACKUP_MANIFEST_SCHEMA_VERSION = 1
BACKUP_COMPLETION_SCHEMA_VERSION = 1
CATALOG_SCHEMA_VERSION = 8
BACKUP_DATABASE_FILENAME = "catalog.sqlite3"
BACKUP_MANIFEST_FILENAME = "manifest.json"
BACKUP_COMPLETION_FILENAME = "completion.json"
_WINDOWS_REPARSE_ATTRIBUTE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
# SHA-256 over sorted ``type\0name\0normalized sqlite_master.sql`` records.
# This value and CATALOG_SCHEMA_VERSION must change together when store schema changes.
_CATALOG_SCHEMA_FINGERPRINT = (
    "3dde32b404989c89c392a272c086d09b8b9ac2cb7e2f61372b6d5f41fa5385c5"
)
_V7_CATALOG_SCHEMA_FINGERPRINT = (
    "e8bcf21ff2317c82e8fd142abf46b6ca9ac1169c7738767c2553ede06e6e0d21"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _file_snapshot(path: Path) -> tuple[int, str]:
    return path.stat().st_size, _sha256(path)


def _assert_expected_file_snapshot(
    path: Path,
    *,
    expected_size: int | None,
    expected_sha256: str | None,
) -> None:
    if expected_size is not None and path.stat().st_size != expected_size:
        raise ValueError("backup artifact size changed during publish")
    if expected_sha256 is not None and _sha256(path) != expected_sha256:
        raise ValueError("backup artifact hash changed during publish")


def _has_reparse_component(path: Path) -> bool:
    current = path
    while True:
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            pass
        except OSError as exc:
            raise ValueError("backup path cannot be inspected safely") from exc
        else:
            attributes = getattr(metadata, "st_file_attributes", 0)
            if stat.S_ISLNK(metadata.st_mode) or attributes & _WINDOWS_REPARSE_ATTRIBUTE:
                return True
        if current == current.parent:
            return False
        current = current.parent


def _require_absolute(path: str | Path, label: str) -> Path:
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        raise ValueError(f"{label} must be an absolute path")
    if any(part == ".." for part in candidate.parts):
        raise ValueError(f"{label} must not contain path traversal")
    return candidate


def _path_identity(path: Path) -> tuple[int, int]:
    attributes = path.lstat()
    return attributes.st_dev, attributes.st_ino


def _readonly_connection(path: Path) -> sqlite3.Connection:
    uri = f"{path.resolve().as_uri()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def _assert_sqlite_integrity(path: Path) -> None:
    connection: sqlite3.Connection | None = None
    try:
        connection = _readonly_connection(path)
        row = connection.execute("PRAGMA integrity_check").fetchone()
    except sqlite3.DatabaseError as exc:
        raise ValueError("SQLite backup integrity check failed") from exc
    finally:
        if connection is not None:
            connection.close()
    if row is None or str(row[0]).casefold() != "ok":
        raise ValueError("SQLite backup integrity check failed")


def _catalog_schema_fingerprint(connection: sqlite3.Connection) -> str:
    try:
        rows = connection.execute(
            "SELECT type, name, sql FROM sqlite_master "
            "WHERE type IN ('table', 'trigger', 'index', 'view') "
            "AND NOT (type = 'index' AND name LIKE 'sqlite_autoindex_%' AND sql IS NULL) "
            "ORDER BY type, name"
        ).fetchall()
        normalized = "\n".join(
            f"{object_type}\0{name}\0{' '.join(str(sql).split())}"
            for object_type, name, sql in rows
        )
    except sqlite3.DatabaseError as exc:
        raise ValueError("catalog schema validation failed") from exc
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _assert_catalog_schema_connection(connection: sqlite3.Connection) -> None:
    if _catalog_schema_fingerprint(connection) != _CATALOG_SCHEMA_FINGERPRINT:
        raise ValueError("catalog schema validation failed")


def _assert_catalog_schema(path: Path) -> None:
    connection: sqlite3.Connection | None = None
    try:
        connection = _readonly_connection(path)
        _assert_catalog_schema_connection(connection)
    finally:
        if connection is not None:
            connection.close()


def _assert_v7_catalog_schema(path: Path) -> None:
    connection: sqlite3.Connection | None = None
    try:
        connection = _readonly_connection(path)
        if _catalog_schema_fingerprint(connection) != _V7_CATALOG_SCHEMA_FINGERPRINT:
            raise ValueError("catalog v7 schema validation failed")
    finally:
        if connection is not None:
            connection.close()


def _backup_database(source: Path, target: Path) -> None:
    source_connection: sqlite3.Connection | None = None
    target_connection: sqlite3.Connection | None = None
    try:
        source_connection = _readonly_connection(source)
        target_connection = sqlite3.connect(target)
        source_connection.backup(target_connection)
        journal_mode = target_connection.execute("PRAGMA journal_mode=DELETE").fetchone()
        if journal_mode is None or str(journal_mode[0]).casefold() != "delete":
            raise ValueError("temporary SQLite snapshot journal mode is not self-contained")
        target_connection.commit()
    finally:
        try:
            if target_connection is not None:
                target_connection.close()
        finally:
            if source_connection is not None:
                source_connection.close()
    _assert_sqlite_integrity(target)


def _publish_without_overwrite(
    source: Path,
    target: Path,
    *,
    expected_parent_identity: tuple[int, int] | None = None,
    expected_size: int | None = None,
    expected_sha256: str | None = None,
) -> None:
    from core.source_registry import (
        _directory_commit_guard,
        _held_file_identity,
        _link_in_guard,
    )

    try:
        _assert_expected_file_snapshot(
            source,
            expected_size=expected_size,
            expected_sha256=expected_sha256,
        )
        with _directory_commit_guard(
            target.parent,
            expected_identity=expected_parent_identity,
        ) as (guard, flush_directory):
            with _held_file_identity(source) as temporary_identity:
                _link_in_guard(guard, source, target)
                try:
                    os.unlink(source)
                except FileNotFoundError:
                    pass
                flush_directory()
                target_stat = target.lstat()
                if (
                    target_stat.st_dev,
                    target_stat.st_ino,
                    target_stat.st_size,
                ) != temporary_identity:
                    raise ValueError("published backup artifact identity changed")
                _assert_expected_file_snapshot(
                    target,
                    expected_size=expected_size,
                    expected_sha256=expected_sha256,
                )
    finally:
        try:
            os.unlink(source)
        except FileNotFoundError:
            pass


def _sqlite_sidecars(database: Path) -> tuple[Path, ...]:
    return tuple(
        database.with_name(f"{database.name}{suffix}")
        for suffix in ("-wal", "-shm", "-journal")
    )


def _assert_no_sqlite_sidecars(database: Path) -> None:
    for sidecar in _sqlite_sidecars(database):
        try:
            sidecar.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise ValueError("SQLite sidecar state cannot be inspected safely") from exc
        raise ValueError("SQLite WAL or journal sidecar state is not part of the manifest")


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _completion_payload(
    *,
    manifest_sha256: str,
    database_sha256: str,
    catalog_schema_version: int,
) -> dict[str, object]:
    return {
        "backup_completion_schema_version": BACKUP_COMPLETION_SCHEMA_VERSION,
        "catalog_schema_version": catalog_schema_version,
        "database": {
            "filename": BACKUP_DATABASE_FILENAME,
            "sha256": database_sha256,
        },
        "manifest": {
            "filename": BACKUP_MANIFEST_FILENAME,
            "sha256": manifest_sha256,
        },
        "no_productive_activation": True,
    }


def _validate_sha256(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"backup completion {label} hash is invalid")
    return value


def _load_completion(
    backup_root: Path,
    manifest: dict[str, object],
    *,
    expected_catalog_schema_version: int = CATALOG_SCHEMA_VERSION,
) -> dict[str, object]:
    completion_path = backup_root / BACKUP_COMPLETION_FILENAME
    if not completion_path.is_file() or _has_reparse_component(completion_path):
        raise ValueError("backup completion record is missing or unsafe")
    try:
        payload = json.loads(completion_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("backup completion record is missing or invalid") from exc
    if not isinstance(payload, dict):
        raise ValueError("backup completion record must be an object")
    if payload.get("backup_completion_schema_version") != BACKUP_COMPLETION_SCHEMA_VERSION:
        raise ValueError("backup completion schema is unsupported")
    if payload.get("catalog_schema_version") != expected_catalog_schema_version:
        raise ValueError("backup completion catalog schema is unsupported")
    if payload.get("no_productive_activation") is not True:
        raise ValueError("backup completion activation boundary is invalid")
    manifest_entry = payload.get("manifest")
    database_entry = payload.get("database")
    if not isinstance(manifest_entry, dict) or not isinstance(database_entry, dict):
        raise ValueError("backup completion record entries are invalid")
    if manifest_entry.get("filename") != BACKUP_MANIFEST_FILENAME:
        raise ValueError("backup completion manifest filename is invalid")
    if database_entry.get("filename") != BACKUP_DATABASE_FILENAME:
        raise ValueError("backup completion database filename is invalid")
    manifest_hash = _validate_sha256(manifest_entry.get("sha256"), "manifest")
    database_hash = _validate_sha256(database_entry.get("sha256"), "database")
    manifest_path = backup_root / BACKUP_MANIFEST_FILENAME
    if _sha256(manifest_path) != manifest_hash:
        raise ValueError("backup completion manifest hash does not match")
    manifest_database = manifest.get("database")
    if not isinstance(manifest_database, dict):
        raise ValueError("backup manifest database entry is invalid")
    if manifest_database.get("sha256") != database_hash:
        raise ValueError("backup completion database hash does not match manifest")
    return payload


def _cleanup_sqlite_bundle(database: Path) -> None:
    for artifact in (database, *_sqlite_sidecars(database)):
        try:
            artifact.unlink()
        except FileNotFoundError:
            pass


def _cleanup_new_directory(root: Path) -> None:
    if not root.exists():
        return
    for child in root.iterdir():
        if child.is_file() or child.is_symlink():
            child.unlink()
    root.rmdir()


def create_catalog_backup(
    source_db: str | Path,
    backup_root: str | Path,
) -> dict[str, object]:
    """Create a consistent SQLite backup plus deterministic hash manifest."""

    source = _require_absolute(source_db, "source_db")
    destination = _require_absolute(backup_root, "backup_root")
    if not source.exists():
        raise FileNotFoundError(f"catalog source database does not exist: {source}")
    if not source.is_file():
        raise ValueError("catalog source database must be a file")
    if _has_reparse_component(source):
        raise ValueError("catalog source database must not use a symlink or reparse point")
    if _has_reparse_component(destination):
        raise ValueError("backup_root must not use a symlink or reparse point")
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"backup_root already exists: {destination}")
    if not destination.parent.is_dir():
        raise FileNotFoundError(f"backup_root parent does not exist: {destination.parent}")
    if _has_reparse_component(destination.parent):
        raise ValueError("backup_root parent must not use a symlink or reparse point")
    _assert_catalog_schema(source)

    destination.mkdir()
    temporary_db = destination / f".{BACKUP_DATABASE_FILENAME}.tmp-{uuid4().hex}"
    backup_db = destination / BACKUP_DATABASE_FILENAME
    manifest_path = destination / BACKUP_MANIFEST_FILENAME
    completion_path = destination / BACKUP_COMPLETION_FILENAME
    try:
        _backup_database(source, temporary_db)
        _assert_no_sqlite_sidecars(temporary_db)
        _assert_catalog_schema(temporary_db)
        temporary_db_size, temporary_db_sha256 = _file_snapshot(temporary_db)
        destination_identity = _path_identity(destination)
        _publish_without_overwrite(
            temporary_db,
            backup_db,
            expected_parent_identity=destination_identity,
            expected_size=temporary_db_size,
            expected_sha256=temporary_db_sha256,
        )
        manifest: dict[str, object] = {
            "backup_manifest_schema_version": BACKUP_MANIFEST_SCHEMA_VERSION,
            "catalog_schema_version": CATALOG_SCHEMA_VERSION,
            "database": {
                "bytes": temporary_db_size,
                "filename": BACKUP_DATABASE_FILENAME,
                "sha256": temporary_db_sha256,
            },
            "no_productive_activation": True,
        }
        temporary_manifest = destination / f".{BACKUP_MANIFEST_FILENAME}.tmp-{uuid4().hex}"
        _write_json(temporary_manifest, manifest)
        temporary_manifest_size, temporary_manifest_sha256 = _file_snapshot(
            temporary_manifest
        )
        _publish_without_overwrite(
            temporary_manifest,
            manifest_path,
            expected_parent_identity=destination_identity,
            expected_size=temporary_manifest_size,
            expected_sha256=temporary_manifest_sha256,
        )
        completion = _completion_payload(
            manifest_sha256=temporary_manifest_sha256,
            database_sha256=temporary_db_sha256,
            catalog_schema_version=CATALOG_SCHEMA_VERSION,
        )
        temporary_completion = destination / f".{BACKUP_COMPLETION_FILENAME}.tmp-{uuid4().hex}"
        _write_json(temporary_completion, completion)
        temporary_completion_size, temporary_completion_sha256 = _file_snapshot(
            temporary_completion
        )
        _publish_without_overwrite(
            temporary_completion,
            completion_path,
            expected_parent_identity=destination_identity,
            expected_size=temporary_completion_size,
            expected_sha256=temporary_completion_sha256,
        )
        return manifest
    except BaseException:
        _cleanup_new_directory(destination)
        raise


def _load_manifest(
    backup_root: Path,
    *,
    expected_catalog_schema_version: int = CATALOG_SCHEMA_VERSION,
) -> dict[str, object]:
    manifest_path = backup_root / BACKUP_MANIFEST_FILENAME
    if not manifest_path.is_file() or _has_reparse_component(manifest_path):
        raise ValueError("backup manifest is missing or unsafe")
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("backup manifest is missing or invalid") from exc
    if not isinstance(payload, dict):
        raise ValueError("backup manifest must be an object")
    if payload.get("backup_manifest_schema_version") != BACKUP_MANIFEST_SCHEMA_VERSION:
        raise ValueError("backup manifest schema is unsupported")
    if payload.get("catalog_schema_version") != expected_catalog_schema_version:
        raise ValueError("catalog schema is unsupported")
    if payload.get("no_productive_activation") is not True:
        raise ValueError("backup manifest activation boundary is invalid")
    database = payload.get("database")
    if not isinstance(database, dict):
        raise ValueError("backup manifest database entry is invalid")
    if database.get("filename") != BACKUP_DATABASE_FILENAME:
        raise ValueError("backup manifest database filename is invalid")
    size = database.get("bytes")
    digest = database.get("sha256")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise ValueError("backup manifest database size is invalid")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError("backup manifest database hash is invalid")
    return payload


def restore_catalog_backup(backup_root: str | Path, target_db: str | Path) -> Path:
    """Verify and restore into a new database path without overwriting anything."""

    backup = _require_absolute(backup_root, "backup_root")
    target = _require_absolute(target_db, "target_db")
    if not backup.is_dir():
        raise FileNotFoundError(f"backup_root does not exist: {backup}")
    if _has_reparse_component(backup):
        raise ValueError("backup_root must not use a symlink or reparse point")
    if _has_reparse_component(target):
        raise ValueError("restore target must not use a symlink or reparse point")
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"restore target already exists: {target}")
    if not target.parent.is_dir():
        raise FileNotFoundError(f"restore target parent does not exist: {target.parent}")
    if _has_reparse_component(target.parent):
        raise ValueError("restore target parent must not use a symlink or reparse point")
    target_parent_identity = _path_identity(target.parent)

    manifest = _load_manifest(backup)
    expected_bundle = {
        BACKUP_DATABASE_FILENAME,
        BACKUP_MANIFEST_FILENAME,
        BACKUP_COMPLETION_FILENAME,
    }
    actual_bundle = {item.name for item in backup.iterdir()}
    if actual_bundle != expected_bundle:
        if BACKUP_COMPLETION_FILENAME not in actual_bundle:
            raise ValueError("backup completion record is missing")
        raise ValueError("backup bundle contains unmanifested or missing files")
    _load_completion(backup, manifest)
    database = manifest["database"]
    assert isinstance(database, dict)
    backup_db = backup / BACKUP_DATABASE_FILENAME
    if not backup_db.is_file() or _has_reparse_component(backup_db):
        raise ValueError("backup database is missing or unsafe")
    _assert_no_sqlite_sidecars(backup_db)
    if backup_db.stat().st_size != database["bytes"] or _sha256(backup_db) != database["sha256"]:
        raise ValueError("backup database size or hash integrity check failed")
    _assert_sqlite_integrity(backup_db)
    _assert_catalog_schema(backup_db)

    temporary_target = target.with_name(f".{target.name}.tmp-{uuid4().hex}")
    try:
        _backup_database(backup_db, temporary_target)
        _assert_no_sqlite_sidecars(temporary_target)
        if (
            temporary_target.stat().st_size != database["bytes"]
            or _sha256(temporary_target) != database["sha256"]
        ):
            raise ValueError("restored snapshot does not match manifest hash or size")
        _assert_catalog_schema(temporary_target)
        temporary_stat = temporary_target.lstat()
        checked_identity = (temporary_stat.st_dev, temporary_stat.st_ino)
        _publish_without_overwrite(
            temporary_target,
            target,
            expected_parent_identity=target_parent_identity,
        )
        target_stat = target.lstat()
        if (target_stat.st_dev, target_stat.st_ino) != checked_identity:
            raise ValueError("published restore target identity changed")
        _assert_no_sqlite_sidecars(target)
        if target.stat().st_size != database["bytes"] or _sha256(target) != database["sha256"]:
            raise ValueError("published restore target does not match manifest hash or size")
        _assert_catalog_schema(target)
    except BaseException:
        _cleanup_sqlite_bundle(temporary_target)
        raise
    return target.resolve()


def migrate_catalog_backup_v7_to_v8(
    source_backup_root: str | Path,
    target_backup_root: str | Path,
) -> Path:
    """Convert one verified v7 backup bundle into a new v8 backup bundle."""

    source_root = _require_absolute(source_backup_root, "source_backup_root")
    target_root = _require_absolute(target_backup_root, "target_backup_root")
    if not source_root.is_dir():
        raise FileNotFoundError(f"source_backup_root does not exist: {source_root}")
    if _has_reparse_component(source_root):
        raise ValueError("source_backup_root must not use a symlink or reparse point")
    if _has_reparse_component(target_root):
        raise ValueError("target_backup_root must not use a symlink or reparse point")
    if target_root.exists() or target_root.is_symlink():
        raise FileExistsError(f"target_backup_root already exists: {target_root}")
    if not target_root.parent.is_dir():
        raise FileNotFoundError(
            f"target_backup_root parent does not exist: {target_root.parent}"
        )
    if _has_reparse_component(target_root.parent):
        raise ValueError(
            "target_backup_root parent must not use a symlink or reparse point"
        )
    manifest = _load_manifest(source_root, expected_catalog_schema_version=7)
    if {item.name for item in source_root.iterdir()} != {
        BACKUP_DATABASE_FILENAME,
        BACKUP_MANIFEST_FILENAME,
    }:
        raise ValueError("backup bundle contains unmanifested or missing files")
    database = manifest["database"]
    assert isinstance(database, dict)
    source_db = source_root / BACKUP_DATABASE_FILENAME
    if not source_db.is_file() or _has_reparse_component(source_db):
        raise ValueError("backup database is missing or unsafe")
    _assert_no_sqlite_sidecars(source_db)
    if (
        source_db.stat().st_size != database["bytes"]
        or _sha256(source_db) != database["sha256"]
    ):
        raise ValueError("backup database size or hash integrity check failed")
    _assert_sqlite_integrity(source_db)
    _assert_v7_catalog_schema(source_db)

    temporary_snapshot = target_root.parent / (
        f".{target_root.name}.v7-migration-{uuid4().hex}.sqlite3"
    )
    owns_temporary_snapshot = False
    try:
        try:
            with temporary_snapshot.open("xb"):
                pass
        except FileExistsError as exc:
            raise FileExistsError("temporary migration snapshot already exists") from exc
        owns_temporary_snapshot = True
        _backup_database(source_db, temporary_snapshot)
        _assert_no_sqlite_sidecars(temporary_snapshot)
        if (
            temporary_snapshot.stat().st_size != database["bytes"]
            or _sha256(temporary_snapshot) != database["sha256"]
        ):
            raise ValueError("migration snapshot does not match v7 backup manifest")
        from .migration import migrate_catalog_v7_to_v8

        migrate_catalog_v7_to_v8(temporary_snapshot)
        _assert_no_sqlite_sidecars(temporary_snapshot)
        _assert_sqlite_integrity(temporary_snapshot)
        _assert_catalog_schema(temporary_snapshot)
        create_catalog_backup(temporary_snapshot, target_root)
    finally:
        if owns_temporary_snapshot:
            _cleanup_sqlite_bundle(temporary_snapshot)
    return target_root.resolve()
