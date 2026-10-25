"""Explicit, transactional Admin Catalog schema migrations."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .backup import (
    _CATALOG_SCHEMA_FINGERPRINT,
    _V7_CATALOG_SCHEMA_FINGERPRINT,
    _assert_catalog_schema_connection,
    _catalog_schema_fingerprint,
)
from .store import _VALIDATION_ATTESTATION_STATEMENTS, _connect_database


def _migration_checkpoint(connection: sqlite3.Connection, phase: str) -> None:
    """Fault-injection seam for transaction-bound migration contracts."""


def _assert_integrity(connection: sqlite3.Connection) -> None:
    foreign_key_rows = connection.execute("PRAGMA foreign_key_check").fetchall()
    if foreign_key_rows:
        raise ValueError("catalog migration foreign-key check failed")
    integrity_row = connection.execute("PRAGMA integrity_check").fetchone()
    if integrity_row is None or str(integrity_row[0]).casefold() != "ok":
        raise ValueError("catalog migration integrity check failed")


def migrate_catalog_v7_to_v8(db_path: str | Path) -> bool:
    """Migrate one exact v7 Catalog database to the current exact v8 schema.

    Returns ``True`` after a committed v7-to-v8 migration and ``False`` for an
    already exact current-v8 database. Every other input schema fails closed.
    """

    database_path = Path(db_path)
    if not database_path.exists():
        raise FileNotFoundError(f"catalog database does not exist: {database_path}")
    if not database_path.is_file() or database_path.stat().st_size == 0:
        raise ValueError("catalog migration requires a non-empty database file")

    connection = _connect_database(database_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        input_fingerprint = _catalog_schema_fingerprint(connection)
        if input_fingerprint == _CATALOG_SCHEMA_FINGERPRINT:
            connection.rollback()
            return False
        if input_fingerprint != _V7_CATALOG_SCHEMA_FINGERPRINT:
            raise ValueError("catalog migration input schema is unsupported")

        _migration_checkpoint(connection, "before_ddl")
        for statement in _VALIDATION_ATTESTATION_STATEMENTS:
            connection.execute(statement)
        _migration_checkpoint(connection, "after_ddl")

        connection.execute(
            "UPDATE catalog_drafts "
            "SET validated_version = NULL, validated_payload_hash = NULL"
        )
        _assert_integrity(connection)
        _assert_catalog_schema_connection(connection)
        _migration_checkpoint(connection, "before_commit")
        connection.commit()
        return True
    except BaseException:
        if connection.in_transaction:
            connection.rollback()
        raise
    finally:
        connection.close()
