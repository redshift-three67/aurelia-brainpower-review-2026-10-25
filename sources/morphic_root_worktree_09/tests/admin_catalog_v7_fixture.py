"""Historical v7 Admin Catalog Known-Answer fixture for migration contracts.

The DDL is reconstructed from the last executable v7 scope (Freeze v8) by
removing only the later v8 validation-attestation table and its two triggers
from the preserved current schema. It deliberately does not import runtime
CatalogStore schema constants or helpers.
"""

from __future__ import annotations

import gc
import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path


V7_SCHEMA_FINGERPRINT = "e8bcf21ff2317c82e8fd142abf46b6ca9ac1169c7738767c2553ede06e6e0d21"
V7_BACKUP_DATABASE_FILENAME = "catalog.sqlite3"
V7_BACKUP_MANIFEST_FILENAME = "manifest.json"


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

_V7_SCHEMA = """
CREATE TABLE IF NOT EXISTS catalog_drafts (
    operator_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    scope TEXT NOT NULL,
    draft_id TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    validated_version INTEGER,
    validated_payload_hash TEXT,
    PRIMARY KEY (operator_id, workspace_id, tenant_id, scope, draft_id)
);

CREATE TABLE IF NOT EXISTS catalog_draft_source_imports (
    receipt_sha256 TEXT PRIMARY KEY,
    operator_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    scope TEXT NOT NULL,
    draft_id TEXT NOT NULL,
    draft_version INTEGER NOT NULL CHECK (draft_version > 0),
    draft_payload_hash TEXT NOT NULL,
    source_id TEXT NOT NULL,
    artifact_id TEXT NOT NULL,
    batch_identity_sha256 TEXT NOT NULL,
    staged_batch_sha256 TEXT NOT NULL,
    source_manifest_sha256 TEXT NOT NULL,
    source_registry_revision INTEGER NOT NULL CHECK (source_registry_revision >= 0),
    source_registry_path TEXT NOT NULL,
    source_registry_sha256 TEXT NOT NULL,
    normalization_sha256 TEXT NOT NULL,
    base_revision_id TEXT NOT NULL,
    base_revision_payload_hash TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    imported_at TEXT NOT NULL,
    UNIQUE (
        operator_id, workspace_id, tenant_id, scope, batch_identity_sha256
    )
);

CREATE TRIGGER IF NOT EXISTS catalog_draft_source_imports_no_update
BEFORE UPDATE ON catalog_draft_source_imports
BEGIN
    SELECT RAISE(ABORT, 'catalog source import receipt is immutable');
END;

CREATE TRIGGER IF NOT EXISTS catalog_draft_source_imports_no_delete
BEFORE DELETE ON catalog_draft_source_imports
BEGIN
    SELECT RAISE(ABORT, 'catalog source import receipt is immutable');
END;

CREATE UNIQUE INDEX IF NOT EXISTS catalog_draft_source_imports_global_batch_replay
ON catalog_draft_source_imports (batch_identity_sha256);

CREATE TABLE IF NOT EXISTS catalog_draft_profile_tombstones (
    operator_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    scope TEXT NOT NULL,
    draft_id TEXT NOT NULL,
    profile_id TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    PRIMARY KEY (
        operator_id, workspace_id, tenant_id, scope, draft_id, profile_id
    ),
    FOREIGN KEY (operator_id, workspace_id, tenant_id, scope, draft_id)
        REFERENCES catalog_drafts (
            operator_id, workspace_id, tenant_id, scope, draft_id
        ) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS catalog_draft_managed_tombstones (
    operator_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    scope TEXT NOT NULL,
    draft_id TEXT NOT NULL,
    entry_type TEXT NOT NULL CHECK (entry_type IN ('remedy', 'multiplex')),
    entry_id TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    PRIMARY KEY (
        operator_id, workspace_id, tenant_id, scope,
        draft_id, entry_type, entry_id
    ),
    FOREIGN KEY (operator_id, workspace_id, tenant_id, scope, draft_id)
        REFERENCES catalog_drafts (
            operator_id, workspace_id, tenant_id, scope, draft_id
        ) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS catalog_revisions (
    operator_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    scope TEXT NOT NULL,
    revision_id TEXT NOT NULL,
    source_draft_id TEXT,
    source_draft_version INTEGER,
    source_draft_payload_hash TEXT,
    payload_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    finalized INTEGER NOT NULL DEFAULT 0 CHECK (finalized IN (0, 1)),
    CHECK (
        (source_draft_id IS NULL AND source_draft_version IS NULL
            AND source_draft_payload_hash IS NULL)
        OR
        (source_draft_id IS NOT NULL AND source_draft_version > 0
            AND source_draft_payload_hash IS NOT NULL)
    ),
    PRIMARY KEY (operator_id, workspace_id, tenant_id, scope, revision_id),
    FOREIGN KEY (operator_id, workspace_id, tenant_id, scope, source_draft_id)
        REFERENCES catalog_drafts (
            operator_id, workspace_id, tenant_id, scope, draft_id
        )
);

CREATE TABLE IF NOT EXISTS catalog_revision_entries (
    operator_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    scope TEXT NOT NULL,
    revision_id TEXT NOT NULL,
    entry_type TEXT NOT NULL,
    entry_id TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    PRIMARY KEY (
        operator_id, workspace_id, tenant_id, scope,
        revision_id, entry_type, entry_id
    ),
    FOREIGN KEY (operator_id, workspace_id, tenant_id, scope, revision_id)
        REFERENCES catalog_revisions (
            operator_id, workspace_id, tenant_id, scope, revision_id
        )
);

CREATE TABLE IF NOT EXISTS catalog_activations (
    operator_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    scope TEXT NOT NULL,
    revision_id TEXT,
    version INTEGER NOT NULL CHECK (version > 0),
    activated_at TEXT NOT NULL,
    PRIMARY KEY (operator_id, workspace_id, tenant_id, scope),
    FOREIGN KEY (operator_id, workspace_id, tenant_id, scope, revision_id)
        REFERENCES catalog_revisions (
            operator_id, workspace_id, tenant_id, scope, revision_id
        )
);

CREATE TABLE IF NOT EXISTS catalog_audit_events (
    event_id INTEGER PRIMARY KEY,
    operator_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    scope TEXT NOT NULL,
    event_type TEXT NOT NULL,
    revision_id TEXT NOT NULL,
    previous_revision_id TEXT,
    activation_version INTEGER NOT NULL,
    actor_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    previous_hash TEXT NOT NULL,
    event_hash TEXT NOT NULL,
    FOREIGN KEY (operator_id, workspace_id, tenant_id, scope, revision_id)
        REFERENCES catalog_revisions (
            operator_id, workspace_id, tenant_id, scope, revision_id
        )
);

CREATE TRIGGER IF NOT EXISTS catalog_revisions_no_update
BEFORE UPDATE ON catalog_revisions
WHEN NOT (
    OLD.finalized = 0 AND NEW.finalized = 1
    AND NEW.operator_id IS OLD.operator_id
    AND NEW.workspace_id IS OLD.workspace_id
    AND NEW.tenant_id IS OLD.tenant_id
    AND NEW.scope IS OLD.scope
    AND NEW.revision_id IS OLD.revision_id
    AND NEW.source_draft_id IS OLD.source_draft_id
    AND NEW.source_draft_version IS OLD.source_draft_version
    AND NEW.source_draft_payload_hash IS OLD.source_draft_payload_hash
    AND NEW.payload_hash IS OLD.payload_hash
    AND NEW.created_at IS OLD.created_at
)
BEGIN
    SELECT RAISE(ABORT, 'catalog revision is immutable');
END;

CREATE TRIGGER IF NOT EXISTS catalog_revisions_no_delete
BEFORE DELETE ON catalog_revisions
BEGIN
    SELECT RAISE(ABORT, 'catalog revision is immutable');
END;

CREATE TRIGGER IF NOT EXISTS catalog_revision_entries_no_update
BEFORE UPDATE ON catalog_revision_entries
BEGIN
    SELECT RAISE(ABORT, 'catalog revision entry is immutable');
END;

CREATE TRIGGER IF NOT EXISTS catalog_revision_entries_no_delete
BEFORE DELETE ON catalog_revision_entries
BEGIN
    SELECT RAISE(ABORT, 'catalog revision entry is immutable');
END;

CREATE TRIGGER IF NOT EXISTS catalog_revision_entries_no_insert_after_finalize
BEFORE INSERT ON catalog_revision_entries
WHEN COALESCE((
    SELECT finalized
    FROM catalog_revisions
    WHERE operator_id = NEW.operator_id
      AND workspace_id = NEW.workspace_id
      AND tenant_id = NEW.tenant_id
      AND scope = NEW.scope
      AND revision_id = NEW.revision_id
), 1) = 1
BEGIN
    SELECT RAISE(ABORT, 'catalog revision entry is immutable');
END;
"""


@dataclass(frozen=True, slots=True)
class V7KnownAnswer:
    database_path: Path
    schema_fingerprint: str
    draft_id: str
    receipt_sha256: str
    revision_id: str
    activation_version: int
    audit_event_id: int


def fingerprint_v7_database(path: Path) -> str:
    with sqlite3.connect(path) as connection:
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
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _known_answer_values() -> dict[str, object]:
    context_mapping = {
        "operator_id": "operator-v7",
        "scope": "workspace",
        "tenant_id": "tenant-v7",
        "workspace_id": "workspace-v7",
    }
    context_values = (
        context_mapping["operator_id"],
        context_mapping["workspace_id"],
        context_mapping["tenant_id"],
        context_mapping["scope"],
    )
    draft_id = "draft-v7"
    revision_id = "revision-v7"
    occurred_at = "2026-07-15T12:24:53+00:00"
    entry = {
        "context": context_mapping,
        "data": {"enabled": True, "label": "Group V7"},
        "entry_id": "group-v7",
        "entry_type": "group",
        "provenance": "historical-v7-known-answer",
        "source_id": "source-v7",
    }
    entry_payload_json = _canonical_json(entry)
    entry_payload_hash = _sha256_text(entry_payload_json)
    draft_payload_json = _canonical_json(
        {"context": context_mapping, "entries": [entry]}
    )
    draft_payload_hash = _sha256_text(draft_payload_json)
    revision_payload_hash = _sha256_text(
        _canonical_json(
            {
                "context": context_mapping,
                "entries": [entry],
                "source_draft_id": draft_id,
                "source_draft_payload_hash": draft_payload_hash,
                "source_draft_version": 1,
            }
        )
    )
    receipt_unsigned = {
        "actor_id": "operator-v7",
        "artifact_id": "artifact-v7",
        "base_revision_id": "",
        "base_revision_payload_hash": "0" * 64,
        "batch_identity_sha256": _sha256_text("batch-v7"),
        "draft_id": draft_id,
        "draft_payload_hash": draft_payload_hash,
        "draft_version": 1,
        "imported_at": occurred_at,
        "normalization_sha256": _sha256_text("normalization-v7"),
        "operator_id": context_mapping["operator_id"],
        "reason": "historical v7 known answer",
        "scope": context_mapping["scope"],
        "source_id": "source-v7",
        "source_manifest_sha256": _sha256_text("source-manifest-v7"),
        "source_registry_path": "C:/synthetic/v7/source-registry.json",
        "source_registry_revision": 7,
        "source_registry_sha256": _sha256_text("source-registry-v7"),
        "staged_batch_sha256": _sha256_text("staged-batch-v7"),
        "tenant_id": context_mapping["tenant_id"],
        "workspace_id": context_mapping["workspace_id"],
    }
    receipt_sha256 = _sha256_text(_canonical_json(receipt_unsigned))
    previous_hash = "0" * 64
    audit_payload = {
        "activation_version": 1,
        "actor_id": "operator-v7",
        "context": context_mapping,
        "event_type": "activate",
        "occurred_at": occurred_at,
        "previous_hash": previous_hash,
        "previous_revision_id": None,
        "reason": "historical v7 known answer",
        "revision_id": revision_id,
    }
    return {
        "audit_event_id": 1,
        "audit_event_hash": _sha256_text(_canonical_json(audit_payload)),
        "audit_payload": audit_payload,
        "context_mapping": context_mapping,
        "context_values": context_values,
        "draft_id": draft_id,
        "draft_payload_hash": draft_payload_hash,
        "draft_payload_json": draft_payload_json,
        "entry": entry,
        "entry_payload_hash": entry_payload_hash,
        "entry_payload_json": entry_payload_json,
        "legacy_validated_payload_hash": draft_payload_hash,
        "legacy_validated_version": 1,
        "occurred_at": occurred_at,
        "previous_hash": previous_hash,
        "receipt_sha256": receipt_sha256,
        "receipt_unsigned": receipt_unsigned,
        "revision_id": revision_id,
        "revision_payload_hash": revision_payload_hash,
    }


def create_v7_known_answer_database(path: Path) -> V7KnownAnswer:
    database_path = Path(path)
    if database_path.exists():
        raise FileExistsError(f"v7 known-answer database already exists: {database_path}")
    if not database_path.parent.is_dir():
        raise FileNotFoundError(
            f"v7 known-answer database parent does not exist: {database_path.parent}"
        )

    values = _known_answer_values()
    try:
        connection = sqlite3.connect(database_path)
        with connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.executescript(_V7_SCHEMA)
            connection.execute(
                """
                INSERT INTO catalog_drafts (
                    operator_id, workspace_id, tenant_id, scope,
                    draft_id, payload_json, payload_hash,
                    validated_version, validated_payload_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    *values["context_values"],
                    values["draft_id"],
                    values["draft_payload_json"],
                    values["draft_payload_hash"],
                    values["legacy_validated_version"],
                    values["legacy_validated_payload_hash"],
                ),
            )
            connection.execute(
                """
                INSERT INTO catalog_draft_source_imports (
                    receipt_sha256,
                    operator_id, workspace_id, tenant_id, scope,
                    draft_id, draft_version, draft_payload_hash,
                    source_id, artifact_id, batch_identity_sha256, staged_batch_sha256,
                    source_manifest_sha256, source_registry_revision,
                    source_registry_path, source_registry_sha256, normalization_sha256,
                    base_revision_id, base_revision_payload_hash,
                    actor_id, reason, imported_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    values["receipt_sha256"],
                    *values["context_values"],
                    values["receipt_unsigned"]["draft_id"],
                    values["receipt_unsigned"]["draft_version"],
                    values["receipt_unsigned"]["draft_payload_hash"],
                    values["receipt_unsigned"]["source_id"],
                    values["receipt_unsigned"]["artifact_id"],
                    values["receipt_unsigned"]["batch_identity_sha256"],
                    values["receipt_unsigned"]["staged_batch_sha256"],
                    values["receipt_unsigned"]["source_manifest_sha256"],
                    values["receipt_unsigned"]["source_registry_revision"],
                    values["receipt_unsigned"]["source_registry_path"],
                    values["receipt_unsigned"]["source_registry_sha256"],
                    values["receipt_unsigned"]["normalization_sha256"],
                    values["receipt_unsigned"]["base_revision_id"],
                    values["receipt_unsigned"]["base_revision_payload_hash"],
                    values["receipt_unsigned"]["actor_id"],
                    values["receipt_unsigned"]["reason"],
                    values["receipt_unsigned"]["imported_at"],
                ),
            )
            connection.execute(
                """
                INSERT INTO catalog_revisions (
                    operator_id, workspace_id, tenant_id, scope,
                    revision_id, source_draft_id, source_draft_version,
                    source_draft_payload_hash, payload_hash, created_at, finalized
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (
                    *values["context_values"],
                    values["revision_id"],
                    values["draft_id"],
                    1,
                    values["draft_payload_hash"],
                    values["revision_payload_hash"],
                    values["occurred_at"],
                ),
            )
            connection.execute(
                """
                INSERT INTO catalog_revision_entries (
                    operator_id, workspace_id, tenant_id, scope,
                    revision_id, entry_type, entry_id, payload_json, payload_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    *values["context_values"],
                    values["revision_id"],
                    "group",
                    "group-v7",
                    values["entry_payload_json"],
                    values["entry_payload_hash"],
                ),
            )
            connection.execute(
                """
                UPDATE catalog_revisions
                SET finalized = 1
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ? AND scope = ?
                  AND revision_id = ?
                """,
                (*values["context_values"], values["revision_id"]),
            )
            connection.execute(
                """
                INSERT INTO catalog_activations (
                    operator_id, workspace_id, tenant_id, scope,
                    revision_id, version, activated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    *values["context_values"],
                    values["revision_id"],
                    1,
                    values["occurred_at"],
                ),
            )
            connection.execute(
                """
                INSERT INTO catalog_audit_events (
                    event_id, operator_id, workspace_id, tenant_id, scope,
                    event_type, revision_id, previous_revision_id, activation_version,
                    actor_id, reason, occurred_at, previous_hash, event_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    values["audit_event_id"],
                    *values["context_values"],
                    "activate",
                    values["revision_id"],
                    None,
                    1,
                    "operator-v7",
                    "historical v7 known answer",
                    values["occurred_at"],
                    values["previous_hash"],
                    values["audit_event_hash"],
                ),
            )
        schema_fingerprint = fingerprint_v7_database(database_path)
        if schema_fingerprint != V7_SCHEMA_FINGERPRINT:
            raise AssertionError(
                "reconstructed v7 schema fingerprint differs from the historical known answer"
            )
        verify_v7_known_answer_database(database_path)
        connection.close()
    except BaseException:
        database_path.unlink(missing_ok=True)
        raise
    return V7KnownAnswer(
        database_path=database_path,
        schema_fingerprint=schema_fingerprint,
        draft_id=str(values["draft_id"]),
        receipt_sha256=str(values["receipt_sha256"]),
        revision_id=str(values["revision_id"]),
        activation_version=1,
        audit_event_id=int(values["audit_event_id"]),
    )


def verify_v7_known_answer_database(path: Path) -> None:
    values = _known_answer_values()
    if fingerprint_v7_database(path) != V7_SCHEMA_FINGERPRINT:
        raise AssertionError("v7 known-answer schema fingerprint changed")
    connection = sqlite3.connect(path)
    try:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise AssertionError("v7 known-answer fixture has foreign-key violations")
        draft = connection.execute("SELECT * FROM catalog_drafts").fetchone()
        receipt = connection.execute(
            "SELECT * FROM catalog_draft_source_imports"
        ).fetchone()
        revision = connection.execute("SELECT * FROM catalog_revisions").fetchone()
        entry = connection.execute("SELECT * FROM catalog_revision_entries").fetchone()
        activation = connection.execute("SELECT * FROM catalog_activations").fetchone()
        audit = connection.execute("SELECT * FROM catalog_audit_events").fetchone()
    finally:
        connection.close()
    if any(item is None for item in (draft, receipt, revision, entry, activation, audit)):
        raise AssertionError("v7 known-answer fixture is incomplete")
    assert draft is not None
    assert receipt is not None
    assert revision is not None
    assert entry is not None
    assert activation is not None
    assert audit is not None
    if (
        str(draft["payload_json"]) != values["draft_payload_json"]
        or str(draft["payload_hash"]) != values["draft_payload_hash"]
        or int(draft["validated_version"])
        != values["legacy_validated_version"]
        or str(draft["validated_payload_hash"])
        != values["legacy_validated_payload_hash"]
    ):
        raise AssertionError("v7 known-answer draft payload is inconsistent")
    if str(entry["payload_json"]) != values["entry_payload_json"] or str(
        entry["payload_hash"]
    ) != values["entry_payload_hash"]:
        raise AssertionError("v7 known-answer revision entry is inconsistent")
    if (
        str(revision["payload_hash"]) != values["revision_payload_hash"]
        or int(revision["finalized"]) != 1
        or str(revision["source_draft_id"]) != values["draft_id"]
        or int(revision["source_draft_version"]) != 1
        or str(revision["source_draft_payload_hash"])
        != values["draft_payload_hash"]
    ):
        raise AssertionError("v7 known-answer revision is inconsistent")
    revision_bundle = {
        "context": values["context_mapping"],
        "entries": [json.loads(str(entry["payload_json"]))],
        "source_draft_id": revision["source_draft_id"],
        "source_draft_payload_hash": revision["source_draft_payload_hash"],
        "source_draft_version": revision["source_draft_version"],
    }
    if _sha256_text(_canonical_json(revision_bundle)) != revision["payload_hash"]:
        raise AssertionError("v7 known-answer revision bundle hash is inconsistent")
    receipt_unsigned = {
        "actor_id": receipt["actor_id"],
        "artifact_id": receipt["artifact_id"],
        "base_revision_id": receipt["base_revision_id"],
        "base_revision_payload_hash": receipt["base_revision_payload_hash"],
        "batch_identity_sha256": receipt["batch_identity_sha256"],
        "draft_id": receipt["draft_id"],
        "draft_payload_hash": receipt["draft_payload_hash"],
        "draft_version": receipt["draft_version"],
        "imported_at": receipt["imported_at"],
        "normalization_sha256": receipt["normalization_sha256"],
        "operator_id": receipt["operator_id"],
        "reason": receipt["reason"],
        "scope": receipt["scope"],
        "source_id": receipt["source_id"],
        "source_manifest_sha256": receipt["source_manifest_sha256"],
        "source_registry_path": receipt["source_registry_path"],
        "source_registry_revision": receipt["source_registry_revision"],
        "source_registry_sha256": receipt["source_registry_sha256"],
        "staged_batch_sha256": receipt["staged_batch_sha256"],
        "tenant_id": receipt["tenant_id"],
        "workspace_id": receipt["workspace_id"],
    }
    if _sha256_text(_canonical_json(receipt_unsigned)) != receipt["receipt_sha256"]:
        raise AssertionError("v7 known-answer source receipt hash is inconsistent")
    if (
        str(activation["revision_id"]) != values["revision_id"]
        or int(activation["version"]) != 1
    ):
        raise AssertionError("v7 known-answer activation is inconsistent")
    audit_payload = {
        "activation_version": audit["activation_version"],
        "actor_id": audit["actor_id"],
        "context": values["context_mapping"],
        "event_type": audit["event_type"],
        "occurred_at": audit["occurred_at"],
        "previous_hash": audit["previous_hash"],
        "previous_revision_id": audit["previous_revision_id"],
        "reason": audit["reason"],
        "revision_id": audit["revision_id"],
    }
    if _sha256_text(_canonical_json(audit_payload)) != audit["event_hash"]:
        raise AssertionError("v7 known-answer audit hash is inconsistent")


def create_v7_known_answer_backup(root: Path) -> V7KnownAnswer:
    if root.exists():
        raise FileExistsError(f"v7 known-answer backup already exists: {root}")
    if not root.parent.is_dir():
        raise FileNotFoundError(
            f"v7 known-answer backup parent does not exist: {root.parent}"
        )
    root.mkdir()
    try:
        seed = root / ".v7-known-answer-seed.sqlite3"
        known_answer = create_v7_known_answer_database(seed)
        database = root / V7_BACKUP_DATABASE_FILENAME
        source_connection = sqlite3.connect(seed)
        target_connection = sqlite3.connect(database)
        try:
            source_connection.backup(target_connection)
            journal_mode = target_connection.execute("PRAGMA journal_mode=DELETE").fetchone()
            if journal_mode is None or str(journal_mode[0]).casefold() != "delete":
                raise AssertionError("v7 known-answer backup is not self-contained")
            target_connection.commit()
        finally:
            target_connection.close()
            source_connection.close()
        gc.collect()
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


def add_unknown_schema_object(path: Path) -> None:
    """Create an explicitly unsupported object without changing v7 records."""

    with sqlite3.connect(path) as connection:
        connection.execute(
            "CREATE TABLE catalog_unknown_schema_marker (value TEXT NOT NULL)"
        )


def add_synthetic_preview_v8_attestation_shape(path: Path) -> None:
    """Create a non-authoritative preview-v8 shape for fail-closed testing.

    The exact initial v8 fingerprint was not preserved. This fixture must not
    be mistaken for historical v8 DDL; it represents an unsupported partial
    attestation addition to prove that only the current v8 fingerprint opens.
    """

    with sqlite3.connect(path) as connection:
        connection.executescript(
            """
            CREATE TABLE catalog_draft_validation_attestations (
                operator_id TEXT NOT NULL,
                workspace_id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                scope TEXT NOT NULL,
                draft_id TEXT NOT NULL,
                draft_version INTEGER NOT NULL,
                payload_hash TEXT NOT NULL,
                policy_version TEXT NOT NULL,
                validated_at TEXT NOT NULL,
                PRIMARY KEY (
                    operator_id, workspace_id, tenant_id, scope,
                    draft_id, draft_version, payload_hash, policy_version
                )
            );

            CREATE TRIGGER catalog_draft_validation_attestations_no_update
            BEFORE UPDATE ON catalog_draft_validation_attestations
            BEGIN
                SELECT RAISE(ABORT, 'catalog draft validation attestation is immutable');
            END;

            CREATE TRIGGER catalog_draft_validation_attestations_no_delete
            BEFORE DELETE ON catalog_draft_validation_attestations
            BEGIN
                SELECT RAISE(ABORT, 'catalog draft validation attestation is immutable');
            END;
            """
        )
