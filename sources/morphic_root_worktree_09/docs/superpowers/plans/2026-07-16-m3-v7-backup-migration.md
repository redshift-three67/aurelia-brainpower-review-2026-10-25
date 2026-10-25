# M3 v7 Backup Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert one fully verified v7 Admin Catalog backup bundle into a new complete v8 backup bundle without mutating or publishing the v7 input.

**Architecture:** Add a dedicated backup-migration API in `core/admin_catalog/backup.py`. It verifies a v7 source manifest and exact v7 schema, copies the source DB to an owned temporary snapshot, delegates the schema change to M2, and creates the new bundle through the existing v8 backup creator. The normal restore API remains v8-only.

**Tech Stack:** Python 3.12, SQLite `backup` API, pytest, Ruff.

---

## File Map

- Modify: `core/admin_catalog/backup.py`
  - Bind the exact v7 input fingerprint, make the private manifest parser version-aware, and add the explicit M3 API.
- Modify: `core/admin_catalog/migration.py`
  - Reuse the one historical v7 fingerprint authority from `backup.py`.
- Modify: `tests/admin_catalog_v7_fixture.py`
  - Add a deterministic two-file v7 backup-bundle fixture without importing current production schema constants.
- Create: `tests/test_admin_catalog_v7_backup_migration_contract.py`
  - Cover success, source immutability, malformed sources, schema rejection, interruption, normal-restore boundaries and target conflicts.

No commit is part of this plan. The active worktree has unrelated uncommitted work, and commits require explicit user approval.

### Task 1: Write The Complete M3 Contract Suite First

**Files:**
- Modify: `tests/admin_catalog_v7_fixture.py:11-18,390-552`
- Create: `tests/test_admin_catalog_v7_backup_migration_contract.py`

- [ ] **Step 1: Add a deterministic v7 backup-bundle fixture**

Append this code to `tests/admin_catalog_v7_fixture.py`. It keeps v7 manifest values local to the historical fixture and does not import any current production schema constant.

```python
V7_BACKUP_DATABASE_FILENAME = "catalog.sqlite3"
V7_BACKUP_MANIFEST_FILENAME = "manifest.json"


def create_v7_known_answer_backup(root: Path) -> V7KnownAnswer:
    if root.exists():
        raise FileExistsError(f"v7 known-answer backup already exists: {root}")
    if not root.parent.is_dir():
        raise FileNotFoundError(f"v7 known-answer backup parent does not exist: {root.parent}")
    root.mkdir()
    try:
        seed = root / ".v7-known-answer-seed.sqlite3"
        known_answer = create_v7_known_answer_database(seed)
        database = root / V7_BACKUP_DATABASE_FILENAME
        source_connection = sqlite3.connect(seed)
        target_connection = sqlite3.connect(database)
        try:
            source_connection.backup(target_connection)
            journal_mode = target_connection.execute(
                "PRAGMA journal_mode=DELETE"
            ).fetchone()
            if journal_mode is None or str(journal_mode[0]).casefold() != "delete":
                raise AssertionError("v7 known-answer backup is not self-contained")
            target_connection.commit()
        finally:
            target_connection.close()
            source_connection.close()
        seed.unlink()
        verify_v7_known_answer_database(database)
        manifest = {
            "backup_manifest_schema_version": 1,
            "catalog_schema_version": 7,
            "database": {
                "bytes": database.stat().st_size,
                "filename": V7_BACKUP_DATABASE_FILENAME,
                "sha256": hashlib.sha256(database.read_bytes()).hexdigest(),
            },
            "no_productive_activation": True,
        }
        (root / V7_BACKUP_MANIFEST_FILENAME).write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return V7KnownAnswer(
            database_path=database,
            schema_fingerprint=known_answer.schema_fingerprint,
            draft_id=known_answer.draft_id,
            receipt_sha256=known_answer.receipt_sha256,
            revision_id=known_answer.revision_id,
            activation_version=known_answer.activation_version,
            audit_event_id=known_answer.audit_event_id,
        )
    except BaseException:
        for child in root.iterdir():
            child.unlink()
        root.rmdir()
        raise
```

- [ ] **Step 2: Write every M3 contract before adding production code**

Create `tests/test_admin_catalog_v7_backup_migration_contract.py` with the imports and helpers below. The first import deliberately fails until the public API exists.

```python
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
```

Add the successful migration, source immutability and normal-restore boundary:

```python
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
```

Add malformed-source and non-v7-schema contracts:

```python
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
```

Add interruption and non-overwrite contracts:

```python
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
```

- [ ] **Step 3: Run the full M3 suite and verify RED**

Run:

```powershell
& "C:\morphic_v1\.venv\Scripts\python.exe" -X utf8 -m pytest tests/test_admin_catalog_v7_backup_migration_contract.py -q -p no:cacheprovider
```

Expected: collection fails with `ImportError: cannot import name 'migrate_catalog_backup_v7_to_v8'`. This proves that every M3 behavior is specified before production implementation.

### Task 2: Implement The Complete M3 Boundary

**Files:**
- Modify: `core/admin_catalog/backup.py:14-23,97-109,236-322`
- Modify: `core/admin_catalog/migration.py:8-13`
- Test: `tests/test_admin_catalog_v7_backup_migration_contract.py`

- [ ] **Step 1: Centralize the historical v7 production authority**

In `core/admin_catalog/backup.py`, add the v7 fingerprint directly after the
current v8 fingerprint:

```python
_V7_CATALOG_SCHEMA_FINGERPRINT = (
    "e8bcf21ff2317c82e8fd142abf46b6ca9ac1169c7738767c2553ede06e6e0d21"
)
```

In `core/admin_catalog/migration.py`, import
`_V7_CATALOG_SCHEMA_FINGERPRINT` from `.backup` and compare
`input_fingerprint` to it. Delete the local `_V7_SCHEMA_FINGERPRINT` literal.
This is not a cycle because the M3 API imports the migration function only
inside its function body, after `backup.py` has loaded.

- [ ] **Step 2: Replace `_load_manifest()` with the explicit version-aware implementation**

Replace the full function at `core/admin_catalog/backup.py:236-263` with:

```python
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
```

Do not change the `restore_catalog_backup()` call site. Its default remains the
current v8 schema version.

- [ ] **Step 3: Add exact-v7 attestation and the M3 API**

Add this helper directly after `_assert_catalog_schema()`:

```python
def _assert_v7_catalog_schema(path: Path) -> None:
    connection: sqlite3.Connection | None = None
    try:
        connection = _readonly_connection(path)
        if _catalog_schema_fingerprint(connection) != _V7_CATALOG_SCHEMA_FINGERPRINT:
            raise ValueError("catalog v7 schema validation failed")
    finally:
        if connection is not None:
            connection.close()
```

Append this API after `restore_catalog_backup()`:

```python
def migrate_catalog_backup_v7_to_v8(
    source_backup_root: str | Path,
    target_backup_root: str | Path,
) -> Path:
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
    if {item.name for item in source_root.iterdir()} != {
        BACKUP_DATABASE_FILENAME,
        BACKUP_MANIFEST_FILENAME,
    }:
        raise ValueError("backup bundle contains unmanifested or missing files")
    manifest = _load_manifest(
        source_root,
        expected_catalog_schema_version=7,
    )
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
```

The function never calls `_cleanup_new_directory(target_root)` or unlinks a
target. The only cleanup target is the exclusively reserved UUID-named snapshot
it created.

- [ ] **Step 4: Run the full M3 suite and verify GREEN**

Run:

```powershell
& "C:\morphic_v1\.venv\Scripts\python.exe" -X utf8 -m pytest tests/test_admin_catalog_v7_backup_migration_contract.py -q -p no:cacheprovider
```

Expected: every M3 contract passes with zero failures.

### Task 3: Run Required Regression And Static Verification

**Files:**
- Verify only. Do not modify code unless a failing test proves a production defect.

- [ ] **Step 1: Run focused migration and backup suites**

Run:

```powershell
& "C:\morphic_v1\.venv\Scripts\python.exe" -X utf8 -m pytest tests/test_admin_catalog_v7_backup_migration_contract.py tests/test_admin_catalog_v7_migration_contract.py tests/test_admin_catalog_backup.py -q -p no:cacheprovider
```

Expected: zero failures. Record pass and skip counts exactly.

- [ ] **Step 2: Run the complete Admin Catalog matrix**

Run:

```powershell
& "C:\morphic_v1\.venv\Scripts\python.exe" -X utf8 -m pytest tests/test_admin_catalog_validation.py tests/test_admin_catalog_v7_backup_migration_contract.py tests/test_admin_catalog_v7_migration_contract.py tests/test_admin_catalog_store.py tests/test_admin_catalog_service.py tests/test_admin_catalog_runtime_adapter.py tests/test_admin_catalog_paths.py tests/test_admin_catalog_legacy_remedies.py tests/test_admin_catalog_legacy_profiles.py tests/test_admin_catalog_legacy_multiplexes.py tests/test_admin_catalog_contracts.py tests/test_admin_catalog_backup.py tests/test_admin_catalog_audit_integrity.py -q -p no:cacheprovider
```

Expected: zero failures. Document any skips verbatim.

- [ ] **Step 3: Run static checks**

Run:

```powershell
& "C:\morphic_v1\.venv\Scripts\python.exe" -X utf8 -m py_compile core/admin_catalog/backup.py core/admin_catalog/migration.py tests/admin_catalog_v7_fixture.py tests/test_admin_catalog_v7_backup_migration_contract.py
& "C:\Users\Hubert111\AppData\Local\Programs\Python\Python312\Scripts\ruff.exe" check core/admin_catalog/backup.py core/admin_catalog/migration.py tests/admin_catalog_v7_fixture.py tests/test_admin_catalog_v7_backup_migration_contract.py
git diff --check
```

Expected: `py_compile` and Ruff exit 0. `git diff --check` may emit the known
LF-to-CRLF warnings from unrelated WIP files but must exit 0 with no whitespace
errors.

## Plan Self-Review

- Spec coverage: Task 1 specifies exact v7-only acceptance, source validation,
  v8 output, immutability, ordinary restore rejection, interruption, temporary
  cleanup and target non-overwrite. Task 2 implements every named boundary.
  Task 3 provides focused, adjacent and static evidence.
- Placeholder scan: no `TODO`, `TBD`, ellipsis, deferred behavior or unnamed
  validation remains. Every production function and test helper has a concrete
  signature and body.
- Type consistency: the only new public API is
  `migrate_catalog_backup_v7_to_v8(source_backup_root, target_backup_root) -> Path`.
  Its two arguments are bundle-root directories. `restore_catalog_backup()`
  remains a v8-only API that publishes a single database `Path`.
