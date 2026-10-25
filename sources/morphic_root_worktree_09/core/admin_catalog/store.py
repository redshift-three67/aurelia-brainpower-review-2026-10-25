"""Expliziter, isolierter SQLite-Store fuer Admin-Catalog F1.

Der Store besitzt absichtlich keinen Defaultpfad und ist an keinen Runtimepfad,
Web-Endpunkt oder Engine-Consumer angebunden.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterator, Sequence

from .contracts import CatalogContext, CatalogEntry, EntryType, normalize_catalog_id
from .validation import validate_entries
from .validation_attestation import ValidationKeyProvider


class CatalogStoreError(RuntimeError):
    """Basisklasse fuer Store-Vertragsverletzungen."""


class ConcurrencyError(CatalogStoreError):
    """Der erwartete Aktivierungspointer ist veraltet."""


class StoreAccessError(CatalogStoreError):
    """Eine Ressource gehoert nicht zum angefragten Catalog-Kontext."""


class ProfileRemovalError(CatalogStoreError):
    """Ein atomarer Draft-Write wuerde ein bestehendes Profil entfernen."""


class ManagedEntryRemovalError(CatalogStoreError):
    """Ein Draft-/Revisionswrite wuerde Remedy oder Multiplex hart entfernen."""


class TombstoneMutationError(CatalogStoreError):
    """Ein atomarer Draft-Write wuerde einen Tombstone veraendern."""


class ManagedEntryTombstoneError(TombstoneMutationError):
    """Der Remedy-/Multiplex-Tombstone-Vertrag wurde verletzt."""


class ManagedEntryReferenceError(CatalogStoreError):
    """Ein Remedy ist noch durch nicht tombstonierte Catalogeintraege gebunden."""

    def __init__(self, references: Sequence[str]) -> None:
        self.references = tuple(sorted(references))
        super().__init__("remedy is still referenced: " + ", ".join(self.references))


@dataclass(frozen=True)
class EntryPublicationState:
    published: bool
    entry_type: EntryType | None
    revision_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DraftSourceImportReceipt:
    draft_id: str
    draft_version: int
    draft_payload_hash: str
    source_id: str
    artifact_id: str
    batch_identity_sha256: str
    staged_batch_sha256: str
    source_manifest_sha256: str
    source_registry_revision: int
    source_registry_path: str
    source_registry_sha256: str
    normalization_sha256: str
    base_revision_id: str
    base_revision_payload_hash: str
    operator_id: str
    workspace_id: str
    tenant_id: str
    scope: str
    actor_id: str
    reason: str
    imported_at: str
    receipt_sha256: str

    def unsigned_mapping(self) -> dict[str, object]:
        return {
            "actor_id": self.actor_id,
            "artifact_id": self.artifact_id,
            "base_revision_id": self.base_revision_id,
            "base_revision_payload_hash": self.base_revision_payload_hash,
            "batch_identity_sha256": self.batch_identity_sha256,
            "draft_id": self.draft_id,
            "draft_payload_hash": self.draft_payload_hash,
            "draft_version": self.draft_version,
            "imported_at": self.imported_at,
            "normalization_sha256": self.normalization_sha256,
            "operator_id": self.operator_id,
            "reason": self.reason,
            "scope": self.scope,
            "source_id": self.source_id,
            "source_manifest_sha256": self.source_manifest_sha256,
            "source_registry_revision": self.source_registry_revision,
            "source_registry_path": self.source_registry_path,
            "source_registry_sha256": self.source_registry_sha256,
            "staged_batch_sha256": self.staged_batch_sha256,
            "tenant_id": self.tenant_id,
            "workspace_id": self.workspace_id,
        }

    def has_valid_hash(self) -> bool:
        return self.receipt_sha256 == _sha256(
            _canonical_json(self.unsigned_mapping())
        )


_ZERO_HASH = "0" * 64
_MANAGED_ENTRY_TYPES = frozenset({EntryType.REMEDY, EntryType.MULTIPLEX})
_VALIDATION_POLICY_VERSION = "catalog-validation-v1"
_VALIDATION_ATTESTATION_FORMAT = "morphic.admin-catalog.validation-attestation"
_VALIDATION_ATTESTATION_FORMAT_VERSION = 1
_CATALOG_SCHEMA_VERSION = 8


_VALIDATION_ATTESTATION_STATEMENTS = (
    """CREATE TABLE IF NOT EXISTS catalog_draft_validation_attestations (
    operator_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    scope TEXT NOT NULL,
    draft_id TEXT NOT NULL,
    draft_version INTEGER NOT NULL CHECK (draft_version > 0),
    payload_hash TEXT NOT NULL,
    policy_version TEXT NOT NULL,
    catalog_schema_version INTEGER NOT NULL CHECK (catalog_schema_version = 8),
    attestation_format_version INTEGER NOT NULL CHECK (attestation_format_version = 1),
    authority_id TEXT NOT NULL,
    key_id TEXT NOT NULL,
    algorithm TEXT NOT NULL CHECK (algorithm = 'HMAC-SHA256'),
    validated_at TEXT NOT NULL,
    attestation_hmac TEXT NOT NULL,
    PRIMARY KEY (
        operator_id, workspace_id, tenant_id, scope,
        draft_id, draft_version, payload_hash, policy_version,
        authority_id, key_id
    )
);""",

    """CREATE TRIGGER IF NOT EXISTS catalog_draft_validation_attestations_no_update
BEFORE UPDATE ON catalog_draft_validation_attestations
BEGIN
    SELECT RAISE(ABORT, 'catalog draft validation attestation is immutable');
END;""",

    """CREATE TRIGGER IF NOT EXISTS catalog_draft_validation_attestations_no_delete
BEFORE DELETE ON catalog_draft_validation_attestations
BEGIN
    SELECT RAISE(ABORT, 'catalog draft validation attestation is immutable');
END;""",
)
_VALIDATION_ATTESTATION_SCHEMA = "\n\n".join(_VALIDATION_ATTESTATION_STATEMENTS)


_SCHEMA = f"""
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

{_VALIDATION_ATTESTATION_SCHEMA}

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


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _context_values(context: CatalogContext) -> tuple[str, str, str, str]:
    return (
        context.operator_id,
        context.workspace_id,
        context.tenant_id,
        context.scope,
    )


def _validation_attestation_message(
    context: CatalogContext,
    *,
    draft_id: str,
    draft_version: int,
    payload_hash: str,
    validated_at: str,
    authority_id: str,
    key_id: str,
) -> bytes:
    return _canonical_json(
        {
            "algorithm": "HMAC-SHA256",
            "attestation_format": _VALIDATION_ATTESTATION_FORMAT,
            "attestation_format_version": _VALIDATION_ATTESTATION_FORMAT_VERSION,
            "authority_id": authority_id,
            "catalog_schema_version": _CATALOG_SCHEMA_VERSION,
            "context": context.canonical_mapping(),
            "draft_id": draft_id,
            "draft_version": draft_version,
            "key_id": key_id,
            "payload_hash": payload_hash,
            "policy_version": _VALIDATION_POLICY_VERSION,
            "validated_at": validated_at,
        }
    ).encode("utf-8")


def _begin_attested_write(connection: sqlite3.Connection) -> None:
    from .backup import _assert_catalog_schema_connection

    connection.execute("BEGIN IMMEDIATE")
    try:
        _assert_catalog_schema_connection(connection)
    except ValueError as exc:
        connection.rollback()
        raise CatalogStoreError("catalog schema fingerprint mismatch") from exc


def _validate_entries_context(
    context: CatalogContext, entries: Sequence[CatalogEntry]
) -> None:
    for entry in entries:
        if entry.context != context:
            raise StoreAccessError(
                f"entry {entry.entry_id!r} belongs to a different catalog context"
            )


def _sorted_entries(entries: Sequence[CatalogEntry]) -> list[CatalogEntry]:
    return sorted(
        entries,
        key=lambda item: (
            item.entry_type.value,
            normalize_catalog_id(item.entry_id),
            item.canonical_json(),
        ),
    )


def _entries_payload(
    context: CatalogContext, entries: Sequence[CatalogEntry]
) -> tuple[list[CatalogEntry], dict[str, object], str]:
    _validate_entries_context(context, entries)
    ordered = _sorted_entries(entries)
    payload = {
        "context": context.canonical_mapping(),
        "entries": [entry.canonical_mapping() for entry in ordered],
    }
    payload_json = _canonical_json(payload)
    return ordered, payload, payload_json


def _entry_from_mapping(value: dict[str, object]) -> CatalogEntry:
    context_data = dict(value["context"])  # type: ignore[arg-type]
    return CatalogEntry(
        entry_type=EntryType(str(value["entry_type"])),
        entry_id=str(value["entry_id"]),
        context=CatalogContext(
            operator_id=str(context_data["operator_id"]),
            workspace_id=str(context_data["workspace_id"]),
            tenant_id=str(context_data["tenant_id"]),
            scope=str(context_data["scope"]),
        ),
        source_id=str(value["source_id"]),
        provenance=str(value["provenance"]),
        data=dict(value["data"]),  # type: ignore[arg-type]
    )


def _entries_from_payload_json(payload_json: str) -> tuple[CatalogEntry, ...]:
    payload = json.loads(payload_json)
    return tuple(_entry_from_mapping(dict(value)) for value in payload["entries"])


def _verified_revision_entries(
    connection: sqlite3.Connection,
    context: CatalogContext,
    revision_id: str,
) -> tuple[CatalogEntry, ...] | None:
    revision = connection.execute(
        """
        SELECT source_draft_id, source_draft_version,
               source_draft_payload_hash, payload_hash, finalized
        FROM catalog_revisions
        WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
          AND scope = ? AND revision_id = ?
        """,
        (*_context_values(context), revision_id),
    ).fetchone()
    if revision is None:
        return None
    if int(revision["finalized"]) != 1:
        raise StoreAccessError("revision payload is not finalized")
    rows = connection.execute(
        """
        SELECT entry_type, entry_id, payload_json, payload_hash
        FROM catalog_revision_entries
        WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
          AND scope = ? AND revision_id = ?
        ORDER BY entry_type, entry_id, payload_json
        """,
        (*_context_values(context), revision_id),
    ).fetchall()
    entries: list[CatalogEntry] = []
    for row in rows:
        try:
            entry = _entry_from_mapping(json.loads(str(row["payload_json"])))
        except Exception as exc:
            raise StoreAccessError("revision entry payload is invalid") from exc
        if str(row["payload_json"]) != entry.canonical_json():
            raise StoreAccessError("revision entry canonical JSON mismatch")
        if entry.context != context:
            raise StoreAccessError("revision entry embedded context mismatch")
        if (
            entry.entry_type.value != str(row["entry_type"])
            or entry.entry_id != str(row["entry_id"])
        ):
            raise StoreAccessError("revision entry identity mismatch")
        if entry.payload_hash != str(row["payload_hash"]):
            raise StoreAccessError("revision entry payload hash mismatch")
        entries.append(entry)
    try:
        ordered, payload, _payload_json = _entries_payload(context, entries)
    except Exception as exc:
        raise StoreAccessError("revision payload context is invalid") from exc
    bundle = {
        **payload,
        "source_draft_id": revision["source_draft_id"],
        "source_draft_payload_hash": revision["source_draft_payload_hash"],
        "source_draft_version": revision["source_draft_version"],
    }
    if _sha256(_canonical_json(bundle)) != str(revision["payload_hash"]):
        raise StoreAccessError("revision payload hash mismatch")
    return tuple(ordered)


def _published_profile_hashes(
    connection: sqlite3.Connection, context: CatalogContext
) -> dict[str, set[str]]:
    rows = connection.execute(
        """
        SELECT e.entry_id, e.payload_hash
        FROM catalog_revision_entries AS e
        JOIN catalog_revisions AS r
          ON r.operator_id = e.operator_id
         AND r.workspace_id = e.workspace_id
         AND r.tenant_id = e.tenant_id
         AND r.scope = e.scope
         AND r.revision_id = e.revision_id
        WHERE e.operator_id = ? AND e.workspace_id = ?
          AND e.tenant_id = ? AND e.scope = ?
          AND e.entry_type = ? AND r.finalized = 1
        """,
        (*_context_values(context), EntryType.PROFILE.value),
    ).fetchall()
    result: dict[str, set[str]] = {}
    for row in rows:
        result.setdefault(normalize_catalog_id(str(row["entry_id"])), set()).add(
            str(row["payload_hash"])
        )
    return result


def _published_profile_tombstone_hashes(
    connection: sqlite3.Connection, context: CatalogContext
) -> dict[str, set[str]]:
    rows = connection.execute(
        """
        SELECT e.entry_id, e.payload_hash, e.payload_json
        FROM catalog_revision_entries AS e
        JOIN catalog_revisions AS r
          ON r.operator_id = e.operator_id
         AND r.workspace_id = e.workspace_id
         AND r.tenant_id = e.tenant_id
         AND r.scope = e.scope
         AND r.revision_id = e.revision_id
        WHERE e.operator_id = ? AND e.workspace_id = ?
          AND e.tenant_id = ? AND e.scope = ?
          AND e.entry_type = ? AND r.finalized = 1
        """,
        (*_context_values(context), EntryType.PROFILE.value),
    ).fetchall()
    result: dict[str, set[str]] = {}
    for row in rows:
        entry = _entry_from_mapping(json.loads(str(row["payload_json"])))
        if entry.data.get("tombstoned", False) is True:
            result.setdefault(normalize_catalog_id(str(row["entry_id"])), set()).add(
                str(row["payload_hash"])
            )
    return result


def _managed_key(entry: CatalogEntry) -> tuple[EntryType, str]:
    return entry.entry_type, normalize_catalog_id(entry.entry_id)


def _published_managed_hashes(
    connection: sqlite3.Connection, context: CatalogContext
) -> dict[tuple[EntryType, str], set[str]]:
    rows = connection.execute(
        """
        SELECT e.entry_type, e.entry_id, e.payload_hash
        FROM catalog_revision_entries AS e
        JOIN catalog_revisions AS r
          ON r.operator_id = e.operator_id
         AND r.workspace_id = e.workspace_id
         AND r.tenant_id = e.tenant_id
         AND r.scope = e.scope
         AND r.revision_id = e.revision_id
        WHERE e.operator_id = ? AND e.workspace_id = ?
          AND e.tenant_id = ? AND e.scope = ?
          AND e.entry_type IN (?, ?) AND r.finalized = 1
        """,
        (
            *_context_values(context),
            EntryType.REMEDY.value,
            EntryType.MULTIPLEX.value,
        ),
    ).fetchall()
    result: dict[tuple[EntryType, str], set[str]] = {}
    for row in rows:
        key = (
            EntryType(str(row["entry_type"])),
            normalize_catalog_id(str(row["entry_id"])),
        )
        result.setdefault(key, set()).add(str(row["payload_hash"]))
    return result


def _published_managed_tombstone_hashes(
    connection: sqlite3.Connection, context: CatalogContext
) -> dict[tuple[EntryType, str], set[str]]:
    rows = connection.execute(
        """
        SELECT e.entry_type, e.entry_id, e.payload_hash, e.payload_json
        FROM catalog_revision_entries AS e
        JOIN catalog_revisions AS r
          ON r.operator_id = e.operator_id
         AND r.workspace_id = e.workspace_id
         AND r.tenant_id = e.tenant_id
         AND r.scope = e.scope
         AND r.revision_id = e.revision_id
        WHERE e.operator_id = ? AND e.workspace_id = ?
          AND e.tenant_id = ? AND e.scope = ?
          AND e.entry_type IN (?, ?) AND r.finalized = 1
        """,
        (
            *_context_values(context),
            EntryType.REMEDY.value,
            EntryType.MULTIPLEX.value,
        ),
    ).fetchall()
    result: dict[tuple[EntryType, str], set[str]] = {}
    for row in rows:
        entry = _entry_from_mapping(json.loads(str(row["payload_json"])))
        if entry.data.get("tombstoned", False) is True:
            result.setdefault(_managed_key(entry), set()).add(str(row["payload_hash"]))
    return result


def _published_managed_tombstone_entries(
    connection: sqlite3.Connection, context: CatalogContext
) -> dict[tuple[EntryType, str], tuple[CatalogEntry, ...]]:
    rows = connection.execute(
        """
        SELECT e.payload_json
        FROM catalog_revision_entries AS e
        JOIN catalog_revisions AS r
          ON r.operator_id = e.operator_id
         AND r.workspace_id = e.workspace_id
         AND r.tenant_id = e.tenant_id
         AND r.scope = e.scope
         AND r.revision_id = e.revision_id
        WHERE e.operator_id = ? AND e.workspace_id = ?
          AND e.tenant_id = ? AND e.scope = ?
          AND e.entry_type IN (?, ?) AND r.finalized = 1
        """,
        (
            *_context_values(context),
            EntryType.REMEDY.value,
            EntryType.MULTIPLEX.value,
        ),
    ).fetchall()
    grouped: dict[tuple[EntryType, str], dict[str, CatalogEntry]] = {}
    for row in rows:
        entry = _entry_from_mapping(json.loads(str(row["payload_json"])))
        if entry.data.get("tombstoned", False) is True:
            grouped.setdefault(_managed_key(entry), {})[entry.payload_hash] = entry
    return {
        key: tuple(value[item] for item in sorted(value))
        for key, value in grouped.items()
    }


def _require_initial_managed_policy(
    connection: sqlite3.Connection,
    context: CatalogContext,
    entries: Sequence[CatalogEntry],
) -> None:
    published = _published_managed_hashes(connection, context)
    terminal = _published_managed_tombstone_hashes(connection, context)
    terminal_entries = _published_managed_tombstone_entries(connection, context)
    for entry in entries:
        if entry.entry_type not in _MANAGED_ENTRY_TYPES:
            continue
        key = _managed_key(entry)
        if key in terminal and entry.payload_hash not in terminal[key]:
            raise ManagedEntryTombstoneError(
                f"published {entry.entry_type.value} tombstone is terminal"
            )
        if (
            entry.data.get("tombstoned", False) is True
            and entry.payload_hash not in published.get(key, set())
        ):
            raise ManagedEntryTombstoneError(
                f"use delete_{entry.entry_type.value} to create a tombstone"
            )

    terminal_ids = {key[1] for key in terminal_entries}
    reserved_aliases = {
        normalize_catalog_id(str(alias))
        for values in terminal_entries.values()
        for tombstone in values
        for alias in tombstone.data.get("aliases", ())
    }
    for entry in entries:
        entry_id = normalize_catalog_id(entry.entry_id)
        key = _managed_key(entry) if entry.entry_type in _MANAGED_ENTRY_TYPES else None
        exact_terminal = (
            key is not None
            and key in terminal
            and entry.payload_hash in terminal[key]
        )
        if entry_id in terminal_ids and not exact_terminal:
            raise ManagedEntryTombstoneError(
                "published managed tombstone identity is reserved"
            )
        if entry_id in reserved_aliases:
            raise ManagedEntryTombstoneError(
                "published managed tombstone alias is reserved"
            )
        aliases = {
            normalize_catalog_id(str(alias)) for alias in entry.data.get("aliases", ())
        }
        if not exact_terminal and (aliases & terminal_ids or aliases & reserved_aliases):
            raise ManagedEntryTombstoneError(
                "published managed tombstone identity or alias is reserved"
            )


def _require_direct_revision_managed_policy(
    connection: sqlite3.Connection,
    context: CatalogContext,
    entries: Sequence[CatalogEntry],
) -> None:
    published = _published_managed_hashes(connection, context)
    terminal = _published_managed_tombstone_hashes(connection, context)
    candidates = {
        _managed_key(entry): entry
        for entry in entries
        if entry.entry_type in _MANAGED_ENTRY_TYPES
    }
    if published.keys() - candidates.keys():
        raise ManagedEntryRemovalError(
            "published remedies and multiplexes must be retained as disabled tombstones"
        )
    for key, entry in candidates.items():
        if key in terminal and entry.payload_hash not in terminal[key]:
            raise ManagedEntryTombstoneError(
                f"published {entry.entry_type.value} tombstone is terminal"
            )
        if (
            entry.data.get("tombstoned", False) is True
            and entry.payload_hash not in published.get(key, set())
        ):
            raise ManagedEntryTombstoneError(
                f"use delete_{entry.entry_type.value} to create a tombstone"
            )

    terminal_entries = {
        key: entry
        for key, entry in candidates.items()
        if key in terminal and entry.payload_hash in terminal[key]
    }
    terminal_ids = {key[1] for key in terminal_entries}
    reserved_aliases = {
        normalize_catalog_id(str(alias))
        for entry in terminal_entries.values()
        for alias in entry.data.get("aliases", ())
    }
    for entry in entries:
        entry_id = normalize_catalog_id(entry.entry_id)
        key = _managed_key(entry) if entry.entry_type in _MANAGED_ENTRY_TYPES else None
        if entry_id in terminal_ids and key not in terminal_entries:
            raise CatalogStoreError(
                "revision snapshot validation failed: normalized_id_collision"
            )
        if entry_id in reserved_aliases:
            raise CatalogStoreError(
                "revision snapshot validation failed: alias_canonical_collision"
            )
        aliases = {
            normalize_catalog_id(str(alias)) for alias in entry.data.get("aliases", ())
        }
        if aliases & terminal_ids:
            raise CatalogStoreError(
                "revision snapshot validation failed: alias_canonical_collision"
            )
        if aliases & reserved_aliases and key not in terminal_entries:
            raise CatalogStoreError(
                "revision snapshot validation failed: duplicate_alias"
            )


def _require_initial_tombstones_published(
    connection: sqlite3.Connection,
    context: CatalogContext,
    entries: Sequence[CatalogEntry],
) -> None:
    published = _published_profile_hashes(connection, context)
    terminal = _published_profile_tombstone_hashes(connection, context)
    for entry in entries:
        profile_id = normalize_catalog_id(entry.entry_id)
        if (
            entry.entry_type is EntryType.PROFILE
            and profile_id in terminal
            and entry.payload_hash not in terminal[profile_id]
        ):
            raise TombstoneMutationError("published profile tombstone is terminal")
        if (
            entry.entry_type is EntryType.PROFILE
            and entry.data.get("tombstoned", False) is True
            and entry.payload_hash
            not in published.get(profile_id, set())
        ):
            raise TombstoneMutationError("use delete_profile to create a tombstone")


def _require_no_source_identity_bypass(
    connection: sqlite3.Connection,
    context: CatalogContext,
    candidate_entries: Sequence[CatalogEntry],
    candidate_payload_hash: str,
) -> None:
    known_source_snapshot = connection.execute(
        """
        SELECT 1
        FROM catalog_drafts AS d
        JOIN catalog_draft_source_imports AS receipt
          ON receipt.operator_id = d.operator_id
         AND receipt.workspace_id = d.workspace_id
         AND receipt.tenant_id = d.tenant_id
         AND receipt.scope = d.scope
         AND receipt.draft_id = d.draft_id
        WHERE d.operator_id = ? AND d.workspace_id = ?
          AND d.tenant_id = ? AND d.scope = ? AND d.payload_hash = ?
        LIMIT 1
        """,
        (*_context_values(context), candidate_payload_hash),
    ).fetchone()
    if known_source_snapshot is not None:
        raise CatalogStoreError(
            "source-imported snapshot requires dedicated receipt publication"
        )
    source_payload_rows = connection.execute(
        """
        SELECT d.payload_json, receipt.base_revision_id
        FROM catalog_drafts AS d
        JOIN catalog_draft_source_imports AS receipt
          ON receipt.operator_id = d.operator_id
         AND receipt.workspace_id = d.workspace_id
         AND receipt.tenant_id = d.tenant_id
         AND receipt.scope = d.scope
         AND receipt.draft_id = d.draft_id
        WHERE d.operator_id = ? AND d.workspace_id = ?
          AND d.tenant_id = ? AND d.scope = ?
        """,
        _context_values(context),
    ).fetchall()
    protected_source_identities: set[tuple[EntryType, str]] = set()
    for row in source_payload_rows:
        source_entries = _entries_from_payload_json(str(row["payload_json"]))
        base_revision_id = str(row["base_revision_id"])
        base_identities: set[tuple[EntryType, str]] = set()
        if base_revision_id:
            base_entries = _verified_revision_entries(
                connection, context, base_revision_id
            )
            if base_entries is None:
                raise CatalogStoreError(
                    "source receipt base revision is unavailable"
                )
            base_identities = {
                (entry.entry_type, normalize_catalog_id(entry.entry_id))
                for entry in base_entries
            }
        protected_source_identities.update(
            (entry.entry_type, normalize_catalog_id(entry.entry_id))
            for entry in source_entries
            if (entry.entry_type, normalize_catalog_id(entry.entry_id))
            not in base_identities
        )
    if protected_source_identities.intersection(
        (entry.entry_type, normalize_catalog_id(entry.entry_id))
        for entry in candidate_entries
    ):
        raise CatalogStoreError(
            "source-imported entry identity requires dedicated receipt publication"
        )


def _require_direct_revision_profile_policy(
    connection: sqlite3.Connection,
    context: CatalogContext,
    entries: Sequence[CatalogEntry],
) -> None:
    published = _published_profile_hashes(connection, context)
    terminal = _published_profile_tombstone_hashes(connection, context)
    candidates = {
        normalize_catalog_id(entry.entry_id): entry
        for entry in entries
        if entry.entry_type is EntryType.PROFILE
    }
    if published.keys() - candidates.keys():
        raise ProfileRemovalError(
            "published profiles must be retained as disabled tombstones"
        )
    for profile_id, profile in candidates.items():
        if profile_id in terminal and profile.payload_hash not in terminal[profile_id]:
            raise TombstoneMutationError("published profile tombstone is terminal")
        if (
            profile.data.get("tombstoned", False) is True
            and profile.payload_hash not in published.get(profile_id, set())
        ):
            raise TombstoneMutationError("use delete_profile to create a tombstone")
    reserved_aliases = {
        normalize_catalog_id(str(alias))
        for profile_id, profile in candidates.items()
        if profile_id in terminal and profile.payload_hash in terminal[profile_id]
        for alias in profile.data.get("aliases", ())
    }
    terminal_ids = {
        profile_id
        for profile_id, profile in candidates.items()
        if profile_id in terminal and profile.payload_hash in terminal[profile_id]
    }
    for entry in entries:
        entry_id = normalize_catalog_id(entry.entry_id)
        if entry_id in terminal_ids:
            if (
                entry.entry_type is EntryType.PROFILE
                and entry.payload_hash in terminal[entry_id]
            ):
                continue
            raise CatalogStoreError(
                "revision snapshot validation failed: normalized_id_collision"
            )
        if entry_id in reserved_aliases:
            raise CatalogStoreError(
                "revision snapshot validation failed: alias_canonical_collision"
            )
        if any(
            normalize_catalog_id(str(alias)) in terminal_ids
            for alias in entry.data.get("aliases", ())
        ):
            raise CatalogStoreError(
                "revision snapshot validation failed: alias_canonical_collision"
            )
        if any(
            normalize_catalog_id(str(alias)) in reserved_aliases
            for alias in entry.data.get("aliases", ())
        ):
            raise CatalogStoreError(
                "revision snapshot validation failed: duplicate_alias"
            )


def _tombstone_entry(entry: CatalogEntry) -> CatalogEntry:
    mapping = entry.canonical_mapping()
    data = dict(mapping["data"])
    data["enabled"] = False
    data["tombstoned"] = True
    return CatalogEntry(
        entry_type=entry.entry_type,
        entry_id=entry.entry_id,
        context=entry.context,
        source_id=entry.source_id,
        provenance=entry.provenance,
        data=data,
    )


def _incoming_remedy_references(
    entries: Sequence[CatalogEntry], remedy_id: str
) -> tuple[str, ...]:
    normalized_remedy_id = normalize_catalog_id(remedy_id)
    references: list[str] = []
    for entry in entries:
        if (
            entry.entry_type is EntryType.MULTIPLEX
            and entry.data.get("tombstoned", False) is not True
            and normalized_remedy_id
            in {
                normalize_catalog_id(str(item))
                for item in entry.data.get("remedy_ids", ())
            }
        ):
            references.append(f"multiplex:{entry.entry_id}:remedy_ids")
        elif (
            entry.entry_type is EntryType.RELATION
            and normalize_catalog_id(str(entry.data["remedy_id"]))
            == normalized_remedy_id
        ):
            references.append(f"relation:{entry.entry_id}:remedy_id")
        elif (
            entry.entry_type is EntryType.TERMINOLOGY
            and entry.data.get("target_entry_type") == "remedy"
            and normalize_catalog_id(str(entry.data["target_entry_id"]))
            == normalized_remedy_id
        ):
            references.append(f"terminology:{entry.entry_id}:target_entry_id")
    return tuple(sorted(references))


def _require_valid_snapshot(entries: Sequence[CatalogEntry]) -> None:
    validation = validate_entries(entries)
    if validation.is_valid:
        return
    codes = ", ".join(issue.code for issue in validation.errors)
    raise CatalogStoreError(f"snapshot validation failed: {codes}")


@dataclass(frozen=True, slots=True)
class _RevisionInsertPlan:
    payload_hash: str
    revision_values: tuple[object, ...]
    entry_values: tuple[tuple[object, ...], ...]
    finalization_values: tuple[object, ...]


def _revision_insert_plan(
    context: CatalogContext,
    revision_id: str,
    entries: Sequence[CatalogEntry],
    *,
    source_draft_id: str | None,
    source_draft_version: int | None,
    source_draft_payload_hash: str | None,
) -> _RevisionInsertPlan:
    ordered, payload, _payload_json = _entries_payload(context, entries)
    if (source_draft_id is None) != (
        source_draft_version is None and source_draft_payload_hash is None
    ):
        raise CatalogStoreError("revision source draft identity is incomplete")
    bundle = {
        **payload,
        "source_draft_id": source_draft_id,
        "source_draft_payload_hash": source_draft_payload_hash,
        "source_draft_version": source_draft_version,
    }
    payload_hash = _sha256(_canonical_json(bundle))
    return _RevisionInsertPlan(
        payload_hash=payload_hash,
        revision_values=(
            *_context_values(context),
            revision_id,
            source_draft_id,
            source_draft_version,
            source_draft_payload_hash,
            payload_hash,
            datetime.now(UTC).isoformat(),
        ),
        entry_values=tuple(
            (
                *_context_values(context),
                revision_id,
                entry.entry_type.value,
                entry.entry_id,
                entry.canonical_json(),
                entry.payload_hash,
            )
            for entry in ordered
        ),
        finalization_values=(*_context_values(context), revision_id),
    )


def _audit_payload(
    *,
    context: CatalogContext,
    event_type: str,
    revision_id: str,
    previous_revision_id: str | None,
    activation_version: int,
    actor_id: str,
    reason: str,
    occurred_at: str,
    previous_hash: str,
) -> dict[str, object]:
    return {
        "activation_version": activation_version,
        "actor_id": actor_id,
        "context": context.canonical_mapping(),
        "event_type": event_type,
        "occurred_at": occurred_at,
        "previous_hash": previous_hash,
        "previous_revision_id": previous_revision_id,
        "reason": reason,
        "revision_id": revision_id,
    }


def _connect_database(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    try:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
    except BaseException:
        connection.close()
        raise


@contextmanager
def _write_connection(db_path: Path) -> Iterator[sqlite3.Connection]:
    connection = _connect_database(db_path)
    try:
        with connection:
            yield connection
    finally:
        connection.close()


class CatalogStore:
    """Small F1 persistence boundary with an explicit caller-owned path."""

    def __init__(
        self,
        db_path: str | Path,
        *,
        validation_key_provider: ValidationKeyProvider | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.validation_key_provider = validation_key_provider
        if not self.db_path.parent.exists():
            raise FileNotFoundError(
                f"catalog database parent does not exist: {self.db_path.parent}"
            )
        from .backup import _assert_catalog_schema

        if self.db_path.exists() and self.db_path.stat().st_size > 0:
            _assert_catalog_schema(self.db_path)
            return
        with _write_connection(self.db_path) as connection:
            connection.executescript(_SCHEMA)
        _assert_catalog_schema(self.db_path)


    @contextmanager
    def connect_readonly(self) -> Iterator[sqlite3.Connection]:
        uri = f"{self.db_path.resolve().as_uri()}?mode=ro"
        connection = sqlite3.connect(uri, uri=True)
        try:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            yield connection
        finally:
            connection.close()

    def create_draft(
        self,
        context: CatalogContext,
        draft_id: str,
        entries: Sequence[CatalogEntry],
    ) -> str:
        normalize_catalog_id(draft_id)
        candidate_entries = tuple(entries)
        ordered, _payload, payload_json = _entries_payload(
            context, candidate_entries
        )
        payload_hash = _sha256(payload_json)
        with _write_connection(self.db_path) as connection:
            _begin_attested_write(connection)
            _require_initial_tombstones_published(connection, context, ordered)
            _require_initial_managed_policy(connection, context, ordered)
            connection.execute(
                """
                INSERT INTO catalog_drafts (
                    operator_id, workspace_id, tenant_id, scope,
                    draft_id, payload_json, payload_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (*_context_values(context), draft_id, payload_json, payload_hash),
            )
        return payload_hash

    def import_staged_source_draft(
        self,
        staged_path: str | Path,
        *,
        staging_root: str | Path,
        registry: object,
        context: CatalogContext,
        draft_id: str,
        actor_id: str,
        reason: str,
        base_revision_id: str = "",
    ) -> tuple[str, object]:
        from .service import AdminCatalogService
        from core.source_registry import (
            DEFAULT_SOURCE_REGISTRY_PATH,
            _canonical_registry_path,
        )
        from core.source_data_promotion import (
            _commit_registered_stage,
            _prepare_source_data_draft_import,
            _replace_pending_registered_stage,
            _reserve_registered_stage,
        )

        configured_registry_path = _canonical_registry_path(
            Path(DEFAULT_SOURCE_REGISTRY_PATH)
        )
        provided_registry_path = _canonical_registry_path(Path(registry.path))
        if provided_registry_path != configured_registry_path:
            raise CatalogStoreError(
                "source registry does not match the configured registry authority"
            )
        service = AdminCatalogService(self)
        base_entries: tuple[CatalogEntry, ...] = ()
        if base_revision_id:
            stored_base = self.get_revision_entries(context, base_revision_id)
            if stored_base is None:
                raise CatalogStoreError(
                    "Explicit base revision does not exist in the requested context."
                )
            base_entries = stored_base
        with _prepare_source_data_draft_import(
            staged_path,
            staging_root=staging_root,
            registry=registry,
            service=service,
            context=context,
            draft_id=draft_id,
            actor_id=actor_id,
            reason=reason,
            catalog_authority_path=self.db_path,
            base_entries=tuple(base_entries),
            base_revision_id=base_revision_id,
        ) as prepared:
            receipt = prepared.receipt
            entries = prepared.entries
            normalize_catalog_id(draft_id)
            normalize_catalog_id(receipt.source_id)
            normalize_catalog_id(receipt.actor_id)
            if receipt.draft_id != draft_id or receipt.draft_version != 1:
                raise CatalogStoreError("source import receipt draft identity is invalid")
            if not receipt.reason.strip() or not receipt.imported_at.strip():
                raise CatalogStoreError("source import receipt audit fields are required")
            if (
                receipt.operator_id,
                receipt.workspace_id,
                receipt.tenant_id,
                receipt.scope,
            ) != _context_values(context):
                raise CatalogStoreError("source import receipt context mismatch")
            if receipt.receipt_sha256 != _sha256(
                _canonical_json(receipt.unsigned_mapping())
            ):
                raise CatalogStoreError("source import receipt hash mismatch")
            ordered, _payload, payload_json = _entries_payload(context, entries)
            payload_hash = _sha256(payload_json)
            if receipt.draft_payload_hash != payload_hash:
                raise CatalogStoreError("source import receipt draft hash mismatch")
            previous_receipt_hash = _reserve_registered_stage(
                Path(staged_path),
                staging_root,
                receipt,
                Path(receipt.source_registry_path),
                self.db_path,
                prepared.stage_parent_identity,
                prepared.registry_parent_identity,
            )
            if previous_receipt_hash:
                stored_receipt = next(
                    (
                        item
                        for item in self.source_import_receipts(context, draft_id)
                        if item.receipt_sha256 == previous_receipt_hash
                    ),
                    None,
                )
                if stored_receipt is not None:
                    stored_entries = self.get_draft_entries(context, draft_id)
                    if stored_entries != tuple(entries):
                        raise CatalogStoreError(
                            "pending stage receipt does not match the stored draft"
                        )
                    _commit_registered_stage(
                        Path(staged_path),
                        staging_root,
                        stored_receipt,
                        Path(stored_receipt.source_registry_path),
                        self.db_path,
                        prepared.stage_parent_identity,
                        prepared.registry_parent_identity,
                    )
                    return payload_hash, replace(prepared, receipt=stored_receipt)
                _replace_pending_registered_stage(
                    Path(staged_path),
                    staging_root,
                    receipt,
                    Path(receipt.source_registry_path),
                    self.db_path,
                    prepared.stage_parent_identity,
                    prepared.registry_parent_identity,
                )
            with _write_connection(self.db_path) as connection:
                _begin_attested_write(connection)
                _require_initial_tombstones_published(connection, context, ordered)
                _require_initial_managed_policy(connection, context, ordered)
                connection.execute(
                    """
                    INSERT INTO catalog_drafts (
                        operator_id, workspace_id, tenant_id, scope,
                        draft_id, payload_json, payload_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (*_context_values(context), draft_id, payload_json, payload_hash),
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
                        receipt.receipt_sha256,
                        *_context_values(context),
                        receipt.draft_id,
                        receipt.draft_version,
                        receipt.draft_payload_hash,
                        receipt.source_id,
                        receipt.artifact_id,
                        receipt.batch_identity_sha256,
                        receipt.staged_batch_sha256,
                        receipt.source_manifest_sha256,
                        receipt.source_registry_revision,
                        receipt.source_registry_path,
                        receipt.source_registry_sha256,
                        receipt.normalization_sha256,
                        receipt.base_revision_id,
                        receipt.base_revision_payload_hash,
                        receipt.actor_id,
                        receipt.reason,
                        receipt.imported_at,
                    ),
                )
                connection.commit()
            _commit_registered_stage(
                Path(staged_path),
                staging_root,
                receipt,
                Path(receipt.source_registry_path),
                self.db_path,
                prepared.stage_parent_identity,
                prepared.registry_parent_identity,
            )
        return payload_hash, prepared

    def preview_draft_payload_hash(
        self, context: CatalogContext, entries: Sequence[CatalogEntry]
    ) -> str:
        _ordered, _payload, payload_json = _entries_payload(context, tuple(entries))
        return _sha256(payload_json)

    def source_import_receipts(
        self, context: CatalogContext, draft_id: str
    ) -> tuple[DraftSourceImportReceipt, ...]:
        with self.connect_readonly() as connection:
            rows = connection.execute(
                """
                SELECT draft_id, draft_version, draft_payload_hash,
                       source_id, artifact_id, batch_identity_sha256, staged_batch_sha256,
                       source_manifest_sha256, source_registry_revision,
                       source_registry_path, source_registry_sha256, normalization_sha256,
                       base_revision_id, base_revision_payload_hash,
                       actor_id, reason, imported_at, receipt_sha256
                FROM catalog_draft_source_imports
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND draft_id = ?
                ORDER BY receipt_sha256
                """,
                (*_context_values(context), draft_id),
            ).fetchall()
        return tuple(
            DraftSourceImportReceipt(
                draft_id=str(row["draft_id"]),
                draft_version=int(row["draft_version"]),
                draft_payload_hash=str(row["draft_payload_hash"]),
                source_id=str(row["source_id"]),
                artifact_id=str(row["artifact_id"]),
                batch_identity_sha256=str(row["batch_identity_sha256"]),
                staged_batch_sha256=str(row["staged_batch_sha256"]),
                source_manifest_sha256=str(row["source_manifest_sha256"]),
                source_registry_revision=int(row["source_registry_revision"]),
                source_registry_path=str(row["source_registry_path"]),
                source_registry_sha256=str(row["source_registry_sha256"]),
                normalization_sha256=str(row["normalization_sha256"]),
                base_revision_id=str(row["base_revision_id"]),
                base_revision_payload_hash=str(row["base_revision_payload_hash"]),
                operator_id=context.operator_id,
                workspace_id=context.workspace_id,
                tenant_id=context.tenant_id,
                scope=context.scope,
                actor_id=str(row["actor_id"]),
                reason=str(row["reason"]),
                imported_at=str(row["imported_at"]),
                receipt_sha256=str(row["receipt_sha256"]),
            )
            for row in rows
        )

    def get_draft(self, context: CatalogContext, draft_id: str) -> dict[str, object] | None:
        with self.connect_readonly() as connection:
            row = connection.execute(
                """
                SELECT payload_json, payload_hash, version,
                       validated_version, validated_payload_hash
                FROM catalog_drafts
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND draft_id = ?
                """,
                (*_context_values(context), draft_id),
            ).fetchone()
        if row is None:
            return None
        payload = json.loads(row["payload_json"])
        return {
            "draft_id": draft_id,
            "entry_ids": [entry["entry_id"] for entry in payload["entries"]],
            "payload_hash": row["payload_hash"],
            "version": row["version"],
            "validated_version": row["validated_version"],
            "validated_payload_hash": row["validated_payload_hash"],
        }

    def get_draft_entries(
        self, context: CatalogContext, draft_id: str
    ) -> tuple[CatalogEntry, ...] | None:
        with self.connect_readonly() as connection:
            row = connection.execute(
                """
                SELECT payload_json FROM catalog_drafts
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND draft_id = ?
                """,
                (*_context_values(context), draft_id),
            ).fetchone()
        return None if row is None else _entries_from_payload_json(str(row["payload_json"]))

    def update_draft(
        self,
        context: CatalogContext,
        draft_id: str,
        entries: Sequence[CatalogEntry],
        *,
        expected_version: int,
    ) -> tuple[int, str]:
        return self._update_draft(
            context,
            draft_id,
            entries,
            expected_version=expected_version,
            authorized_profile_tombstone_id=None,
            authorized_managed_tombstone=None,
        )

    def _tombstone_profile(
        self,
        context: CatalogContext,
        draft_id: str,
        *,
        profile_id: str,
        expected_version: int,
    ) -> tuple[int, str]:
        return self._update_draft(
            context,
            draft_id,
            None,
            expected_version=expected_version,
            authorized_profile_tombstone_id=normalize_catalog_id(profile_id),
            authorized_managed_tombstone=None,
        )

    def _tombstone_managed_entry(
        self,
        context: CatalogContext,
        draft_id: str,
        *,
        entry_type: EntryType,
        entry_id: str,
        expected_version: int,
    ) -> tuple[int, str]:
        if entry_type not in _MANAGED_ENTRY_TYPES:
            raise ManagedEntryTombstoneError("unsupported managed tombstone type")
        return self._update_draft(
            context,
            draft_id,
            None,
            expected_version=expected_version,
            authorized_profile_tombstone_id=None,
            authorized_managed_tombstone=(
                entry_type,
                normalize_catalog_id(entry_id),
            ),
        )

    def _update_draft(
        self,
        context: CatalogContext,
        draft_id: str,
        entries: Sequence[CatalogEntry] | None,
        *,
        expected_version: int,
        authorized_profile_tombstone_id: str | None,
        authorized_managed_tombstone: tuple[EntryType, str] | None,
    ) -> tuple[int, str]:
        normalize_catalog_id(draft_id)
        if isinstance(expected_version, bool) or not isinstance(expected_version, int):
            raise CatalogStoreError("expected_version must be an integer")
        with _write_connection(self.db_path) as connection:
            _begin_attested_write(connection)
            source_receipt = connection.execute(
                """
                SELECT 1 FROM catalog_draft_source_imports
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND draft_id = ?
                LIMIT 1
                """,
                (*_context_values(context), draft_id),
            ).fetchone()
            if source_receipt is not None:
                raise CatalogStoreError(
                    "source-imported draft is immutable after receipt binding"
                )
            current_row = connection.execute(
                """
                SELECT version, payload_json FROM catalog_drafts
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND draft_id = ?
                """,
                (*_context_values(context), draft_id),
            ).fetchone()
            if current_row is None:
                raise StoreAccessError("draft does not exist in the requested context")
            if int(current_row["version"]) != expected_version:
                raise ConcurrencyError("draft version changed")
            current_entries = _entries_from_payload_json(
                str(current_row["payload_json"])
            )
            if (
                authorized_profile_tombstone_id is not None
                and authorized_managed_tombstone is not None
            ):
                raise CatalogStoreError("only one tombstone transition is permitted")
            if authorized_profile_tombstone_id is not None:
                matches = [
                    (index, entry)
                    for index, entry in enumerate(current_entries)
                    if normalize_catalog_id(entry.entry_id)
                    == authorized_profile_tombstone_id
                ]
                if (
                    len(matches) != 1
                    or matches[0][1].entry_type is not EntryType.PROFILE
                    or matches[0][1].data.get("tombstoned", False) is True
                ):
                    raise TombstoneMutationError(
                        "delete_profile requires exactly one existing live profile"
                    )
                index, current_profile = matches[0]
                candidate_entries = list(current_entries)
                candidate_entries[index] = _tombstone_entry(current_profile)
            elif authorized_managed_tombstone is not None:
                managed_type, managed_id = authorized_managed_tombstone
                matches = [
                    (index, entry)
                    for index, entry in enumerate(current_entries)
                    if normalize_catalog_id(entry.entry_id) == managed_id
                ]
                if (
                    len(matches) != 1
                    or matches[0][1].entry_type is not managed_type
                    or matches[0][1].data.get("tombstoned", False) is True
                ):
                    raise ManagedEntryTombstoneError(
                        f"delete_{managed_type.value} requires exactly one existing live {managed_type.value}"
                    )
                if managed_type is EntryType.REMEDY:
                    references = _incoming_remedy_references(
                        current_entries, managed_id
                    )
                    if references:
                        raise ManagedEntryReferenceError(references)
                index, current_managed = matches[0]
                candidate_entries = list(current_entries)
                candidate_entries[index] = _tombstone_entry(current_managed)
            else:
                if entries is None:
                    raise CatalogStoreError("draft entries are required")
                candidate_entries = list(entries)
            ordered, _payload, payload_json = _entries_payload(
                context, candidate_entries
            )
            payload_hash = _sha256(payload_json)
            candidate_profiles = {
                normalize_catalog_id(entry.entry_id): entry
                for entry in ordered
                if entry.entry_type is EntryType.PROFILE
            }
            current_profiles = {
                normalize_catalog_id(entry.entry_id): entry
                for entry in current_entries
                if entry.entry_type is EntryType.PROFILE
            }
            for current in current_entries:
                if current.entry_type is not EntryType.PROFILE:
                    continue
                candidate = candidate_profiles.get(
                    normalize_catalog_id(current.entry_id)
                )
                if candidate is None:
                    raise ProfileRemovalError(
                        "profiles must be retained as disabled tombstones"
                    )
                if (
                    current.data.get("tombstoned", False) is True
                    and candidate.payload_hash != current.payload_hash
                ):
                    raise TombstoneMutationError(
                        "tombstoned profile is immutable"
                    )
            tombstone_transitions: list[str] = []
            for profile_id, candidate in candidate_profiles.items():
                current = current_profiles.get(profile_id)
                if (
                    candidate.data.get("tombstoned", False) is True
                    and (
                        current is None
                        or current.data.get("tombstoned", False) is not True
                    )
                ):
                    tombstone_transitions.append(profile_id)
            expected_transitions = (
                []
                if authorized_profile_tombstone_id is None
                else [authorized_profile_tombstone_id]
            )
            if tombstone_transitions != expected_transitions:
                raise TombstoneMutationError(
                    "use delete_profile to create exactly one existing profile tombstone"
                )
            candidate_managed = {
                _managed_key(entry): entry
                for entry in ordered
                if entry.entry_type in _MANAGED_ENTRY_TYPES
            }
            current_managed = {
                _managed_key(entry): entry
                for entry in current_entries
                if entry.entry_type in _MANAGED_ENTRY_TYPES
            }
            for key, current in current_managed.items():
                candidate = candidate_managed.get(key)
                if candidate is None:
                    raise ManagedEntryRemovalError(
                        "remedies and multiplexes must be retained as disabled tombstones"
                    )
                if (
                    current.data.get("tombstoned", False) is True
                    and candidate.payload_hash != current.payload_hash
                ):
                    raise ManagedEntryTombstoneError(
                        f"tombstoned {current.entry_type.value} is immutable"
                    )
                if (
                    current.entry_type is EntryType.REMEDY
                    and current.data.get("enabled", True) is True
                    and candidate.data.get("enabled", True) is False
                    and candidate.data.get("tombstoned", False) is not True
                ):
                    references = _incoming_remedy_references(
                        ordered, current.entry_id
                    )
                    if references:
                        raise ManagedEntryReferenceError(references)
            managed_transitions = sorted(
                (
                    key
                    for key, candidate in candidate_managed.items()
                    if candidate.data.get("tombstoned", False) is True
                    and (
                        key not in current_managed
                        or current_managed[key].data.get("tombstoned", False) is not True
                    )
                ),
                key=lambda item: (item[0].value, item[1]),
            )
            expected_managed_transitions = (
                []
                if authorized_managed_tombstone is None
                else [authorized_managed_tombstone]
            )
            if managed_transitions != expected_managed_transitions:
                type_name = (
                    "managed_entry"
                    if not managed_transitions
                    else managed_transitions[0][0].value
                )
                raise ManagedEntryTombstoneError(
                    f"use delete_{type_name} to create exactly one existing managed tombstone"
                )
            cursor = connection.execute(
                """
                UPDATE catalog_drafts
                SET payload_json = ?, payload_hash = ?, version = version + 1,
                    validated_version = NULL, validated_payload_hash = NULL
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND draft_id = ? AND version = ?
                """,
                (
                    payload_json,
                    payload_hash,
                    *_context_values(context),
                    draft_id,
                    expected_version,
                ),
            )
            if cursor.rowcount != 1:
                raise ConcurrencyError("draft version changed")
            if authorized_profile_tombstone_id is not None:
                tombstone = candidate_profiles[authorized_profile_tombstone_id]
                connection.execute(
                    """
                    INSERT INTO catalog_draft_profile_tombstones (
                        operator_id, workspace_id, tenant_id, scope,
                        draft_id, profile_id, payload_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (
                        operator_id, workspace_id, tenant_id, scope,
                        draft_id, profile_id
                    ) DO UPDATE SET payload_hash = excluded.payload_hash
                    """,
                    (
                        *_context_values(context),
                        draft_id,
                        tombstone.entry_id,
                        tombstone.payload_hash,
                    ),
                )
            if authorized_managed_tombstone is not None:
                tombstone = candidate_managed[authorized_managed_tombstone]
                connection.execute(
                    """
                    INSERT INTO catalog_draft_managed_tombstones (
                        operator_id, workspace_id, tenant_id, scope,
                        draft_id, entry_type, entry_id, payload_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (
                        operator_id, workspace_id, tenant_id, scope,
                        draft_id, entry_type, entry_id
                    ) DO UPDATE SET payload_hash = excluded.payload_hash
                    """,
                    (
                        *_context_values(context),
                        draft_id,
                        tombstone.entry_type.value,
                        tombstone.entry_id,
                        tombstone.payload_hash,
                    ),
                )
        return expected_version + 1, payload_hash

    def delete_draft(
        self, context: CatalogContext, draft_id: str, *, expected_version: int
    ) -> None:
        if (
            isinstance(expected_version, bool)
            or not isinstance(expected_version, int)
            or expected_version < 1
        ):
            raise ConcurrencyError("expected draft version must be a positive integer")
        with _write_connection(self.db_path) as connection:
            _begin_attested_write(connection)
            source_receipt = connection.execute(
                """
                SELECT 1 FROM catalog_draft_source_imports
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND draft_id = ?
                LIMIT 1
                """,
                (*_context_values(context), draft_id),
            ).fetchone()
            if source_receipt is not None:
                raise CatalogStoreError(
                    "source-imported draft with immutable receipt cannot be deleted"
                )
            cursor = connection.execute(
                """
                DELETE FROM catalog_drafts
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND draft_id = ? AND version = ?
                """,
                (*_context_values(context), draft_id, expected_version),
            )
            if cursor.rowcount != 1:
                exists = connection.execute(
                    """
                    SELECT 1 FROM catalog_drafts
                    WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                      AND scope = ? AND draft_id = ?
                    """,
                    (*_context_values(context), draft_id),
                ).fetchone()
                if exists is None:
                    raise StoreAccessError("draft does not exist in the requested context")
                raise ConcurrencyError("draft version changed")

    def mark_draft_validated(
        self,
        context: CatalogContext,
        draft_id: str,
        *,
        expected_version: int,
        expected_payload_hash: str,
    ) -> None:
        if (
            isinstance(expected_version, bool)
            or not isinstance(expected_version, int)
            or expected_version < 1
        ):
            raise ConcurrencyError("expected draft version must be a positive integer")
        provider = self.validation_key_provider
        if provider is None:
            raise CatalogStoreError("validation key provider is required")
        with _write_connection(self.db_path) as connection:
            _begin_attested_write(connection)
            row = connection.execute(
                """
                SELECT payload_json, payload_hash, version
                FROM catalog_drafts
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND draft_id = ?
                """,
                (*_context_values(context), draft_id),
            ).fetchone()
            if (
                row is None
                or int(row["version"]) != expected_version
                or str(row["payload_hash"]) != expected_payload_hash
            ):
                raise ConcurrencyError("draft changed during validation")
            candidate_entries = _entries_from_payload_json(str(row["payload_json"]))
            _require_valid_snapshot(candidate_entries)
            validated_at = datetime.now(UTC).isoformat()
            authority_id = provider.authority_id
            key_id = provider.active_key_id()
            message = _validation_attestation_message(
                context,
                draft_id=draft_id,
                draft_version=expected_version,
                payload_hash=expected_payload_hash,
                validated_at=validated_at,
                authority_id=authority_id,
                key_id=key_id,
            )
            signature = provider.sign_hmac_sha256(key_id, message).hex()
            connection.execute(
                """
                INSERT OR IGNORE INTO catalog_draft_validation_attestations (
                    operator_id, workspace_id, tenant_id, scope,
                    draft_id, draft_version, payload_hash, policy_version,
                    catalog_schema_version, attestation_format_version,
                    authority_id, key_id, algorithm, validated_at, attestation_hmac
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    *_context_values(context),
                    draft_id,
                    expected_version,
                    expected_payload_hash,
                    _VALIDATION_POLICY_VERSION,
                    _CATALOG_SCHEMA_VERSION,
                    _VALIDATION_ATTESTATION_FORMAT_VERSION,
                    authority_id,
                    key_id,
                    "HMAC-SHA256",
                    validated_at,
                    signature,
                ),
            )
            attestation = connection.execute(
                """
                SELECT validated_at, attestation_hmac
                FROM catalog_draft_validation_attestations
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND draft_id = ? AND draft_version = ?
                  AND payload_hash = ? AND policy_version = ?
                  AND authority_id = ? AND key_id = ?
                """,
                (
                    *_context_values(context),
                    draft_id,
                    expected_version,
                    expected_payload_hash,
                    _VALIDATION_POLICY_VERSION,
                    authority_id,
                    key_id,
                ),
            ).fetchone()
            if attestation is None:
                raise CatalogStoreError("validation attestation was not persisted")
            persisted_message = _validation_attestation_message(
                context,
                draft_id=draft_id,
                draft_version=expected_version,
                payload_hash=expected_payload_hash,
                validated_at=str(attestation["validated_at"]),
                authority_id=authority_id,
                key_id=key_id,
            )
            try:
                persisted_signature = bytes.fromhex(str(attestation["attestation_hmac"]))
            except ValueError as exc:
                raise CatalogStoreError("validation attestation is malformed") from exc
            if not provider.verify_hmac_sha256(
                key_id, persisted_message, persisted_signature
            ):
                raise CatalogStoreError("validation attestation authentication failed")
            cursor = connection.execute(
                """
                UPDATE catalog_drafts
                SET validated_version = version, validated_payload_hash = payload_hash
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND draft_id = ? AND version = ? AND payload_hash = ?
                """,
                (
                    *_context_values(context),
                    draft_id,
                    expected_version,
                    expected_payload_hash,
                ),
            )
            if cursor.rowcount != 1:
                raise ConcurrencyError("draft changed during validation")

    def publish_validated_draft(
        self,
        context: CatalogContext,
        draft_id: str,
        revision_id: str,
        *,
        expected_draft_version: int,
        source_registry_path: str | Path | None = None,
    ) -> str:
        normalize_catalog_id(draft_id)
        normalize_catalog_id(revision_id)
        if (
            isinstance(expected_draft_version, bool)
            or not isinstance(expected_draft_version, int)
            or expected_draft_version < 1
        ):
            raise ConcurrencyError(
                "expected draft version must be a positive integer"
            )
        provider = self.validation_key_provider
        if provider is None:
            raise CatalogStoreError("validation key provider is required")
        authority_stack = ExitStack()
        authorized_receipts: tuple[DraftSourceImportReceipt, ...] = ()
        if source_registry_path is not None:
            from core.source_data_promotion import (
                _registry_lock,
                _revalidate_source_import_receipt_against_registry,
            )
            from core.source_registry import SourceRegistry, _canonical_registry_path

            registry_path = _canonical_registry_path(Path(source_registry_path))
            authority_stack.enter_context(_registry_lock(registry_path))
            try:
                authorized_receipts = self.source_import_receipts(context, draft_id)
                if any(
                    receipt.source_registry_path != str(registry_path)
                    for receipt in authorized_receipts
                ):
                    raise CatalogStoreError(
                        "source receipt registry authority path mismatch"
                    )
                current_registry = SourceRegistry.load(registry_path)
                for receipt in authorized_receipts:
                    _revalidate_source_import_receipt_against_registry(
                        receipt, current_registry
                    )
            except Exception:
                authority_stack.close()
                raise
        try:
            connection = _connect_database(self.db_path)
        except Exception:
            authority_stack.close()
            raise
        try:
            _begin_attested_write(connection)
            receipt_rows = connection.execute(
                """
                SELECT receipt_sha256 FROM catalog_draft_source_imports
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND draft_id = ?
                ORDER BY receipt_sha256
                """,
                (*_context_values(context), draft_id),
            ).fetchall()
            receipt_hashes = tuple(str(item["receipt_sha256"]) for item in receipt_rows)
            authorized_hashes = tuple(
                sorted(receipt.receipt_sha256 for receipt in authorized_receipts)
            )
            if receipt_hashes and receipt_hashes != authorized_hashes:
                raise CatalogStoreError(
                    "source-imported draft requires dedicated receipt revalidation"
                )
            row = connection.execute(
                """
                SELECT payload_json, payload_hash, version,
                       validated_version, validated_payload_hash
                FROM catalog_drafts
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND draft_id = ?
                """,
                (*_context_values(context), draft_id),
            ).fetchone()
            if row is None:
                raise StoreAccessError("draft does not exist in the requested context")
            if int(row["version"]) != expected_draft_version:
                raise ConcurrencyError("draft version changed")
            if (
                row["validated_version"] != row["version"]
                or row["validated_payload_hash"] != row["payload_hash"]
            ):
                raise CatalogStoreError("draft has no successful current validation")
            validation_attestations = connection.execute(
                """
                SELECT catalog_schema_version, attestation_format_version,
                       authority_id, key_id, algorithm, validated_at,
                       attestation_hmac
                FROM catalog_draft_validation_attestations
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND draft_id = ? AND draft_version = ?
                  AND payload_hash = ? AND policy_version = ?
                  AND authority_id = ?
                """,
                (
                    *_context_values(context),
                    draft_id,
                    int(row["version"]),
                    str(row["payload_hash"]),
                    _VALIDATION_POLICY_VERSION,
                    provider.authority_id,
                ),
            ).fetchall()
            valid_attestation = False
            for attestation in validation_attestations:
                if (
                    int(attestation["catalog_schema_version"])
                    != _CATALOG_SCHEMA_VERSION
                    or int(attestation["attestation_format_version"])
                    != _VALIDATION_ATTESTATION_FORMAT_VERSION
                    or str(attestation["algorithm"]) != "HMAC-SHA256"
                ):
                    continue
                key_id = str(attestation["key_id"])
                message = _validation_attestation_message(
                    context,
                    draft_id=draft_id,
                    draft_version=int(row["version"]),
                    payload_hash=str(row["payload_hash"]),
                    validated_at=str(attestation["validated_at"]),
                    authority_id=str(attestation["authority_id"]),
                    key_id=key_id,
                )
                try:
                    signature = bytes.fromhex(str(attestation["attestation_hmac"]))
                except ValueError:
                    continue
                if provider.verify_hmac_sha256(key_id, message, signature):
                    valid_attestation = True
                    break
            if not valid_attestation:
                raise CatalogStoreError(
                    "draft has no authenticated validation attestation for live payload"
                )
            live_payload_json = str(row["payload_json"])
            live_payload_hash = _sha256(live_payload_json)
            if live_payload_hash != str(row["payload_hash"]):
                raise CatalogStoreError("draft payload hash integrity mismatch")
            candidate_entries = _entries_from_payload_json(live_payload_json)
            _ordered, _payload, canonical_payload_json = _entries_payload(
                context, candidate_entries
            )
            if canonical_payload_json != live_payload_json:
                raise CatalogStoreError("draft payload canonical integrity mismatch")
            for receipt in authorized_receipts:
                if (
                    receipt.draft_id != draft_id
                    or receipt.draft_version != int(row["version"])
                    or receipt.draft_payload_hash != live_payload_hash
                    or (
                        receipt.operator_id,
                        receipt.workspace_id,
                        receipt.tenant_id,
                        receipt.scope,
                    )
                    != _context_values(context)
                ):
                    raise CatalogStoreError(
                        "source receipt does not attest the live draft payload"
                    )
            _require_valid_snapshot(candidate_entries)
            if not receipt_hashes:
                _require_no_source_identity_bypass(
                    connection,
                    context,
                    candidate_entries,
                    str(row["payload_hash"]),
                )
            candidate_profiles = {
                normalize_catalog_id(entry.entry_id): entry
                for entry in candidate_entries
                if entry.entry_type is EntryType.PROFILE
            }
            published_profiles = _published_profile_hashes(connection, context)
            terminal_profiles = _published_profile_tombstone_hashes(
                connection, context
            )
            if published_profiles.keys() - candidate_profiles.keys():
                raise ProfileRemovalError(
                    "published profiles must be retained as disabled tombstones"
                )
            authorized_rows = connection.execute(
                """
                SELECT profile_id, payload_hash
                FROM catalog_draft_profile_tombstones
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND draft_id = ?
                """,
                (*_context_values(context), draft_id),
            ).fetchall()
            authorized_tombstones = {
                normalize_catalog_id(str(item["profile_id"])): str(item["payload_hash"])
                for item in authorized_rows
            }
            for profile_id, profile in candidate_profiles.items():
                if (
                    profile_id in terminal_profiles
                    and profile.payload_hash not in terminal_profiles[profile_id]
                ):
                    raise TombstoneMutationError(
                        "published profile tombstone is terminal"
                    )
                if profile.data.get("tombstoned", False) is not True:
                    continue
                previously_published = (
                    profile.payload_hash in published_profiles.get(profile_id, set())
                )
                authorized_here = (
                    authorized_tombstones.get(profile_id) == profile.payload_hash
                )
                if not previously_published and not authorized_here:
                    raise TombstoneMutationError(
                        "profile tombstone was not created by delete_profile"
                    )
            candidate_managed = {
                _managed_key(entry): entry
                for entry in candidate_entries
                if entry.entry_type in _MANAGED_ENTRY_TYPES
            }
            published_managed = _published_managed_hashes(connection, context)
            terminal_managed = _published_managed_tombstone_hashes(
                connection, context
            )
            if published_managed.keys() - candidate_managed.keys():
                raise ManagedEntryRemovalError(
                    "published remedies and multiplexes must be retained as disabled tombstones"
                )
            managed_rows = connection.execute(
                """
                SELECT entry_type, entry_id, payload_hash
                FROM catalog_draft_managed_tombstones
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND draft_id = ?
                """,
                (*_context_values(context), draft_id),
            ).fetchall()
            authorized_managed = {
                (
                    EntryType(str(item["entry_type"])),
                    normalize_catalog_id(str(item["entry_id"])),
                ): str(item["payload_hash"])
                for item in managed_rows
            }
            for key, entry in candidate_managed.items():
                if key in terminal_managed and entry.payload_hash not in terminal_managed[key]:
                    raise ManagedEntryTombstoneError(
                        f"published {entry.entry_type.value} tombstone is terminal"
                    )
                if entry.data.get("tombstoned", False) is not True:
                    continue
                previously_published = entry.payload_hash in published_managed.get(
                    key, set()
                )
                authorized_here = authorized_managed.get(key) == entry.payload_hash
                if not previously_published and not authorized_here:
                    raise ManagedEntryTombstoneError(
                        f"{entry.entry_type.value} tombstone was not created by delete_{entry.entry_type.value}"
                    )
            insert_plan = _revision_insert_plan(
                context,
                revision_id,
                candidate_entries,
                source_draft_id=draft_id,
                source_draft_version=int(row["version"]),
                source_draft_payload_hash=str(row["payload_hash"]),
            )
            connection.execute(
                """
                INSERT INTO catalog_revisions (
                    operator_id, workspace_id, tenant_id, scope,
                    revision_id, source_draft_id, source_draft_version,
                    source_draft_payload_hash, payload_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                insert_plan.revision_values,
            )
            connection.executemany(
                """
                INSERT INTO catalog_revision_entries (
                    operator_id, workspace_id, tenant_id, scope,
                    revision_id, entry_type, entry_id, payload_json, payload_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                insert_plan.entry_values,
            )
            connection.execute(
                """
                UPDATE catalog_revisions
                SET finalized = 1
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND revision_id = ? AND finalized = 0
                """,
                insert_plan.finalization_values,
            )
            connection.commit()
            return insert_plan.payload_hash
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
            authority_stack.close()

    def create_revision(
        self,
        context: CatalogContext,
        revision_id: str,
        entries: Sequence[CatalogEntry],
        *,
        source_draft_id: str | None = None,
    ) -> str:
        normalize_catalog_id(revision_id)
        if source_draft_id is not None:
            normalize_catalog_id(source_draft_id)
        candidate_entries = tuple(entries)
        candidate_draft_hash = self.preview_draft_payload_hash(
            context, candidate_entries
        )
        connection = _connect_database(self.db_path)
        try:
            _begin_attested_write(connection)
            source_draft_version: int | None = None
            source_draft_payload_hash: str | None = None
            if source_draft_id is not None:
                source_row = connection.execute(
                    """
                    SELECT d.payload_json, d.version, d.payload_hash,
                           EXISTS (
                               SELECT 1 FROM catalog_draft_source_imports AS receipt
                               WHERE receipt.operator_id = d.operator_id
                                 AND receipt.workspace_id = d.workspace_id
                                 AND receipt.tenant_id = d.tenant_id
                                 AND receipt.scope = d.scope
                                 AND receipt.draft_id = d.draft_id
                           ) AS has_source_receipt
                    FROM catalog_drafts AS d
                    WHERE d.operator_id = ? AND d.workspace_id = ?
                      AND d.tenant_id = ? AND d.scope = ? AND d.draft_id = ?
                    """,
                    (*_context_values(context), source_draft_id),
                ).fetchone()
                if source_row is None:
                    raise sqlite3.IntegrityError(
                        "source draft does not exist in the requested context"
                    )
                if source_row is not None and int(source_row["has_source_receipt"]):
                    raise CatalogStoreError(
                        "source-imported draft requires dedicated receipt publication"
                    )
                if source_row is not None:
                    source_draft_version = int(source_row["version"])
                    source_draft_payload_hash = str(source_row["payload_hash"])
                    source_entries = _entries_from_payload_json(
                        str(source_row["payload_json"])
                    )
                    if self.preview_draft_payload_hash(
                        context, source_entries
                    ) != candidate_draft_hash:
                        raise CatalogStoreError(
                            "source_draft_id entries differ from the revision snapshot"
                        )
            _require_no_source_identity_bypass(
                connection,
                context,
                candidate_entries,
                candidate_draft_hash,
            )
            _require_valid_snapshot(candidate_entries)
            _require_direct_revision_profile_policy(
                connection, context, candidate_entries
            )
            _require_direct_revision_managed_policy(
                connection, context, candidate_entries
            )
            insert_plan = _revision_insert_plan(
                context,
                revision_id,
                candidate_entries,
                source_draft_id=source_draft_id,
                source_draft_version=source_draft_version,
                source_draft_payload_hash=source_draft_payload_hash,
            )
            connection.execute(
                """
                INSERT INTO catalog_revisions (
                    operator_id, workspace_id, tenant_id, scope,
                    revision_id, source_draft_id, source_draft_version,
                    source_draft_payload_hash, payload_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                insert_plan.revision_values,
            )
            connection.executemany(
                """
                INSERT INTO catalog_revision_entries (
                    operator_id, workspace_id, tenant_id, scope,
                    revision_id, entry_type, entry_id, payload_json, payload_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                insert_plan.entry_values,
            )
            connection.execute(
                """
                UPDATE catalog_revisions
                SET finalized = 1
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND revision_id = ? AND finalized = 0
                """,
                insert_plan.finalization_values,
            )
            connection.commit()
            return insert_plan.payload_hash
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def list_revision_ids(self, context: CatalogContext) -> list[str]:
        with self.connect_readonly() as connection:
            rows = connection.execute(
                """
                SELECT revision_id FROM catalog_revisions
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ? AND scope = ?
                ORDER BY revision_id
                """,
                _context_values(context),
            ).fetchall()
        return [str(row["revision_id"]) for row in rows]

    def get_revision_entries(
        self, context: CatalogContext, revision_id: str
    ) -> tuple[CatalogEntry, ...] | None:
        with self.connect_readonly() as connection:
            connection.execute("BEGIN")
            return _verified_revision_entries(connection, context, revision_id)

    def revision_payload_hash(
        self, context: CatalogContext, revision_id: str
    ) -> str | None:
        with self.connect_readonly() as connection:
            row = connection.execute(
                """
                SELECT payload_hash FROM catalog_revisions
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND revision_id = ? AND finalized = 1
                """,
                (*_context_values(context), revision_id),
            ).fetchone()
        return None if row is None else str(row["payload_hash"])

    def entry_publication_state(
        self, context: CatalogContext, entry_id: str
    ) -> EntryPublicationState:
        normalize_catalog_id(entry_id)
        with self.connect_readonly() as connection:
            rows = connection.execute(
                """
                SELECT e.entry_type, e.revision_id
                FROM catalog_revision_entries AS e
                JOIN catalog_revisions AS r
                  ON r.operator_id = e.operator_id
                 AND r.workspace_id = e.workspace_id
                 AND r.tenant_id = e.tenant_id
                 AND r.scope = e.scope
                 AND r.revision_id = e.revision_id
                WHERE e.operator_id = ? AND e.workspace_id = ?
                  AND e.tenant_id = ? AND e.scope = ?
                  AND e.entry_id = ? COLLATE NOCASE
                  AND r.finalized = 1
                ORDER BY e.revision_id, e.entry_type
                """,
                (*_context_values(context), entry_id),
            ).fetchall()
        if not rows:
            return EntryPublicationState(False, None, ())
        entry_types = {EntryType(str(row["entry_type"])) for row in rows}
        if len(entry_types) != 1:
            raise StoreAccessError(
                f"published entry {entry_id!r} has conflicting entry types"
            )
        return EntryPublicationState(
            True,
            next(iter(entry_types)),
            tuple(sorted({str(row["revision_id"]) for row in rows})),
        )

    def get_revision_provenance(
        self, context: CatalogContext, revision_id: str
    ) -> dict[str, object] | None:
        with self.connect_readonly() as connection:
            row = connection.execute(
                """
                SELECT source_draft_id, source_draft_version,
                       source_draft_payload_hash
                FROM catalog_revisions
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND revision_id = ?
                """,
                (*_context_values(context), revision_id),
            ).fetchone()
        if row is None:
            return None
        return {
            "source_draft_id": row["source_draft_id"],
            "source_draft_version": row["source_draft_version"],
            "source_draft_payload_hash": row["source_draft_payload_hash"],
        }

    def current_activation(self, context: CatalogContext) -> tuple[str | None, int]:
        with self.connect_readonly() as connection:
            row = connection.execute(
                """
                SELECT revision_id, version FROM catalog_activations
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ? AND scope = ?
                """,
                _context_values(context),
            ).fetchone()
        if row is None:
            return None, 0
        revision_id = None if row["revision_id"] is None else str(row["revision_id"])
        return revision_id, int(row["version"])

    def current_revision_id(self, context: CatalogContext) -> str | None:
        return self.current_activation(context)[0]

    def current_revision_snapshot(
        self, context: CatalogContext
    ) -> tuple[str, tuple[CatalogEntry, ...]] | None:
        """Read the active pointer and its verified payload in one SQLite snapshot."""

        with self.connect_readonly() as connection:
            connection.execute("BEGIN")
            row = connection.execute(
                """
                SELECT revision_id FROM catalog_activations
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ?
                """,
                _context_values(context),
            ).fetchone()
            if row is None or row["revision_id"] is None:
                return None
            revision_id = str(row["revision_id"])
            entries = _verified_revision_entries(connection, context, revision_id)
            if entries is None:
                raise StoreAccessError("active revision payload is missing")
            return revision_id, entries

    def activate_revision(
        self,
        context: CatalogContext,
        revision_id: str,
        *,
        expected_previous_revision_id: str | None,
        expected_activation_version: int,
        actor_id: str,
        reason: str,
        event_type: str = "activate",
    ) -> int:
        normalize_catalog_id(revision_id)
        normalize_catalog_id(actor_id)
        if expected_previous_revision_id is not None:
            normalize_catalog_id(expected_previous_revision_id)
        if (
            isinstance(expected_activation_version, bool)
            or not isinstance(expected_activation_version, int)
            or expected_activation_version < 0
        ):
            raise CatalogStoreError("expected_activation_version must be non-negative")
        if event_type not in {"activate", "rollback"}:
            raise CatalogStoreError(f"unsupported activation event: {event_type!r}")
        if not isinstance(reason, str) or not reason.strip():
            raise CatalogStoreError("activation reason must be non-empty")

        connection = _connect_database(self.db_path)
        try:
            _begin_attested_write(connection)
            revision = connection.execute(
                """
                SELECT 1 FROM catalog_revisions
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND revision_id = ? AND finalized = 1
                """,
                (*_context_values(context), revision_id),
            ).fetchone()
            if revision is None:
                raise StoreAccessError(
                    f"revision {revision_id!r} does not exist in the requested context"
                )

            active = connection.execute(
                """
                SELECT revision_id, version FROM catalog_activations
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ? AND scope = ?
                """,
                _context_values(context),
            ).fetchone()
            actual_previous = (
                None
                if active is None or active["revision_id"] is None
                else str(active["revision_id"])
            )
            actual_version = 0 if active is None else int(active["version"])
            if (
                actual_previous != expected_previous_revision_id
                or actual_version != expected_activation_version
            ):
                raise ConcurrencyError(
                    "activation state changed: "
                    f"expected ({expected_previous_revision_id!r}, "
                    f"v{expected_activation_version}), found "
                    f"({actual_previous!r}, v{actual_version})"
                )
            if event_type == "rollback":
                if revision_id == actual_previous:
                    raise CatalogStoreError(
                        "rollback target must differ from the active revision"
                    )
                prior_activation = connection.execute(
                    """
                    SELECT 1 FROM catalog_audit_events
                    WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                      AND scope = ? AND revision_id = ?
                      AND event_type IN ('activate', 'rollback')
                      AND activation_version < ?
                    LIMIT 1
                    """,
                    (*_context_values(context), revision_id, actual_version),
                ).fetchone()
                if prior_activation is None:
                    raise CatalogStoreError(
                        "rollback target was never active earlier in this context"
                    )
            version = actual_version + 1
            occurred_at = datetime.now(UTC).isoformat()
            connection.execute(
                """
                INSERT INTO catalog_activations (
                    operator_id, workspace_id, tenant_id, scope,
                    revision_id, version, activated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (operator_id, workspace_id, tenant_id, scope)
                DO UPDATE SET
                    revision_id = excluded.revision_id,
                    version = excluded.version,
                    activated_at = excluded.activated_at
                """,
                (*_context_values(context), revision_id, version, occurred_at),
            )

            previous_event = connection.execute(
                """
                SELECT event_hash FROM catalog_audit_events
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ? AND scope = ?
                ORDER BY event_id DESC LIMIT 1
                """,
                _context_values(context),
            ).fetchone()
            previous_hash = (
                _ZERO_HASH if previous_event is None else str(previous_event["event_hash"])
            )
            audit_payload = _audit_payload(
                context=context,
                event_type=event_type,
                revision_id=revision_id,
                previous_revision_id=actual_previous,
                activation_version=version,
                actor_id=actor_id,
                reason=reason,
                occurred_at=occurred_at,
                previous_hash=previous_hash,
            )
            event_hash = _sha256(_canonical_json(audit_payload))
            connection.execute(
                """
                INSERT INTO catalog_audit_events (
                    operator_id, workspace_id, tenant_id, scope,
                    event_type, revision_id, previous_revision_id,
                    activation_version, actor_id, reason, occurred_at,
                    previous_hash, event_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    *_context_values(context),
                    event_type,
                    revision_id,
                    actual_previous,
                    version,
                    actor_id,
                    reason,
                    occurred_at,
                    previous_hash,
                    event_hash,
                ),
            )
            connection.commit()
            return version
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def deactivate_revision(
        self,
        context: CatalogContext,
        *,
        expected_previous_revision_id: str,
        expected_activation_version: int,
        actor_id: str,
        reason: str,
    ) -> int:
        normalize_catalog_id(expected_previous_revision_id)
        normalize_catalog_id(actor_id)
        if (
            isinstance(expected_activation_version, bool)
            or not isinstance(expected_activation_version, int)
            or expected_activation_version < 1
        ):
            raise CatalogStoreError(
                "expected_activation_version must be a positive integer"
            )
        if not isinstance(reason, str) or not reason.strip():
            raise CatalogStoreError("deactivation reason must be non-empty")
        connection = _connect_database(self.db_path)
        try:
            _begin_attested_write(connection)
            active = connection.execute(
                """
                SELECT revision_id, version FROM catalog_activations
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ? AND scope = ?
                """,
                _context_values(context),
            ).fetchone()
            actual_previous = (
                None
                if active is None or active["revision_id"] is None
                else str(active["revision_id"])
            )
            actual_version = 0 if active is None else int(active["version"])
            if (
                actual_previous != expected_previous_revision_id
                or actual_version != expected_activation_version
            ):
                raise ConcurrencyError("activation state changed before deactivation")
            version = actual_version + 1
            occurred_at = datetime.now(UTC).isoformat()
            connection.execute(
                """
                UPDATE catalog_activations
                SET revision_id = NULL, version = ?, activated_at = ?
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ? AND scope = ?
                """,
                (version, occurred_at, *_context_values(context)),
            )
            previous_event = connection.execute(
                """
                SELECT event_hash FROM catalog_audit_events
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ? AND scope = ?
                ORDER BY event_id DESC LIMIT 1
                """,
                _context_values(context),
            ).fetchone()
            previous_hash = (
                _ZERO_HASH if previous_event is None else str(previous_event["event_hash"])
            )
            audit_payload = _audit_payload(
                context=context,
                event_type="deactivate",
                revision_id=expected_previous_revision_id,
                previous_revision_id=actual_previous,
                activation_version=version,
                actor_id=actor_id,
                reason=reason,
                occurred_at=occurred_at,
                previous_hash=previous_hash,
            )
            event_hash = _sha256(_canonical_json(audit_payload))
            connection.execute(
                """
                INSERT INTO catalog_audit_events (
                    operator_id, workspace_id, tenant_id, scope,
                    event_type, revision_id, previous_revision_id,
                    activation_version, actor_id, reason, occurred_at,
                    previous_hash, event_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    *_context_values(context),
                    "deactivate",
                    expected_previous_revision_id,
                    actual_previous,
                    version,
                    actor_id,
                    reason,
                    occurred_at,
                    previous_hash,
                    event_hash,
                ),
            )
            connection.commit()
            return version
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def rollback(
        self,
        context: CatalogContext,
        *,
        target_revision_id: str,
        expected_previous_revision_id: str,
        expected_activation_version: int,
        actor_id: str,
        reason: str,
    ) -> int:
        return self.activate_revision(
            context,
            target_revision_id,
            expected_previous_revision_id=expected_previous_revision_id,
            expected_activation_version=expected_activation_version,
            actor_id=actor_id,
            reason=reason,
            event_type="rollback",
        )

    def audit_event_count(self, context: CatalogContext) -> int:
        with self.connect_readonly() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS count FROM catalog_audit_events
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ? AND scope = ?
                """,
                _context_values(context),
            ).fetchone()
        return int(row["count"])

    def verify_audit_chain(self, context: CatalogContext) -> bool:
        with self.connect_readonly() as connection:
            rows = connection.execute(
                """
                SELECT event_type, revision_id, previous_revision_id,
                       activation_version, actor_id, reason, occurred_at,
                       previous_hash, event_hash
                FROM catalog_audit_events
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ? AND scope = ?
                ORDER BY event_id
                """,
                _context_values(context),
            ).fetchall()
        expected_previous_hash = _ZERO_HASH
        for row in rows:
            if row["previous_hash"] != expected_previous_hash:
                return False
            payload = _audit_payload(
                context=context,
                event_type=str(row["event_type"]),
                revision_id=str(row["revision_id"]),
                previous_revision_id=(
                    None
                    if row["previous_revision_id"] is None
                    else str(row["previous_revision_id"])
                ),
                activation_version=int(row["activation_version"]),
                actor_id=str(row["actor_id"]),
                reason=str(row["reason"]),
                occurred_at=str(row["occurred_at"]),
                previous_hash=str(row["previous_hash"]),
            )
            calculated = _sha256(_canonical_json(payload))
            if calculated != row["event_hash"]:
                return False
            expected_previous_hash = calculated
        return True


__all__ = [
    "CatalogStore",
    "CatalogStoreError",
    "ConcurrencyError",
    "DraftSourceImportReceipt",
    "EntryPublicationState",
    "ProfileRemovalError",
    "StoreAccessError",
    "TombstoneMutationError",
]
