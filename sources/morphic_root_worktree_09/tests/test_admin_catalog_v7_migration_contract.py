from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

import pytest

from core.admin_catalog.backup import _CATALOG_SCHEMA_FINGERPRINT, _catalog_schema_fingerprint
import core.admin_catalog.migration as migration_module
from core.admin_catalog.migration import migrate_catalog_v7_to_v8
from core.admin_catalog.contracts import CatalogContext
from core.admin_catalog.store import CatalogStore, CatalogStoreError
from core.admin_catalog.validation_attestation import HmacValidationKeyProvider
import tests.admin_catalog_v7_fixture as v7_fixture
from tests.admin_catalog_v7_fixture import (
    V7_SCHEMA_FINGERPRINT,
    add_synthetic_preview_v8_attestation_shape,
    add_unknown_schema_object,
    create_v7_known_answer_database,
    verify_v7_known_answer_database,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v7_known_answer_database_has_historical_fingerprint_and_rows(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "catalog-v7.sqlite3"

    known_answer = create_v7_known_answer_database(database_path)

    assert known_answer.schema_fingerprint == V7_SCHEMA_FINGERPRINT
    verify_v7_known_answer_database(database_path)
    with sqlite3.connect(database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table' AND name LIKE 'catalog_%'"
            )
        }
        assert connection.execute("SELECT COUNT(*) FROM catalog_drafts").fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM catalog_draft_source_imports"
        ).fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM catalog_revisions").fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM catalog_revision_entries"
        ).fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM catalog_activations").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM catalog_audit_events").fetchone()[0] == 1

    assert "catalog_draft_validation_attestations" not in tables


def test_current_store_rejects_v7_known_answer_database_without_mutation(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "catalog-v7.sqlite3"
    create_v7_known_answer_database(database_path)
    before = _sha256(database_path)

    with pytest.raises(ValueError, match="catalog schema validation failed"):
        CatalogStore(database_path)

    assert _sha256(database_path) == before
    assert not database_path.with_name(f"{database_path.name}-wal").exists()
    assert not database_path.with_name(f"{database_path.name}-shm").exists()
    assert not database_path.with_name(f"{database_path.name}-journal").exists()


def test_migrate_v7_to_current_v8_invalidates_legacy_validation_markers(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "catalog-v7.sqlite3"
    create_v7_known_answer_database(database_path)
    with sqlite3.connect(database_path) as connection:
        before_rows = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in (
                "catalog_drafts",
                "catalog_draft_source_imports",
                "catalog_revisions",
                "catalog_revision_entries",
                "catalog_activations",
                "catalog_audit_events",
            )
        }
        legacy_marker = connection.execute(
            "SELECT validated_version, validated_payload_hash FROM catalog_drafts"
        ).fetchone()
    assert legacy_marker is not None
    assert legacy_marker[0] == 1
    assert legacy_marker[1] is not None

    assert migrate_catalog_v7_to_v8(database_path) is True

    CatalogStore(database_path)
    with sqlite3.connect(database_path) as connection:
        after_rows = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in before_rows
        }
        marker = connection.execute(
            "SELECT validated_version, validated_payload_hash FROM catalog_drafts"
        ).fetchone()
        attestation_rows = connection.execute(
            "SELECT COUNT(*) FROM catalog_draft_validation_attestations"
        ).fetchone()[0]
        fingerprint = _catalog_schema_fingerprint(connection)
        foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
        integrity = connection.execute("PRAGMA integrity_check").fetchone()

    assert after_rows == before_rows
    assert marker == (None, None)
    assert attestation_rows == 0
    assert fingerprint == _CATALOG_SCHEMA_FINGERPRINT
    assert foreign_keys == []
    assert integrity == ("ok",)


def test_migrate_current_v8_is_idempotent_without_rewriting_database(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "catalog-v7.sqlite3"
    create_v7_known_answer_database(database_path)

    assert migrate_catalog_v7_to_v8(database_path) is True
    before = _sha256(database_path)
    checkpoints: list[str] = []
    monkeypatch.setattr(
        migration_module,
        "_migration_checkpoint",
        lambda _connection, phase: checkpoints.append(phase),
    )

    assert migrate_catalog_v7_to_v8(database_path) is False
    assert _sha256(database_path) == before
    assert checkpoints == []


@pytest.mark.parametrize(
    "schema_mutator",
    [add_unknown_schema_object, add_synthetic_preview_v8_attestation_shape],
    ids=["unknown-fingerprint", "synthetic-preview-v8"],
)
def test_migration_rejects_unknown_or_preview_schema_without_mutation(
    tmp_path: Path,
    schema_mutator: object,
) -> None:
    database_path = tmp_path / "catalog-unsupported.sqlite3"
    create_v7_known_answer_database(database_path)
    assert callable(schema_mutator)
    schema_mutator(database_path)
    before = _sha256(database_path)

    with pytest.raises(ValueError, match="input schema is unsupported"):
        migrate_catalog_v7_to_v8(database_path)

    assert _sha256(database_path) == before


@pytest.mark.parametrize("phase", ["before_ddl", "after_ddl", "before_commit"])
def test_migration_faults_roll_back_to_complete_v7(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    phase: str,
) -> None:
    database_path = tmp_path / "catalog-v7.sqlite3"
    create_v7_known_answer_database(database_path)
    observed: list[str] = []

    def fail_at_checkpoint(connection: sqlite3.Connection, current_phase: str) -> None:
        if current_phase != phase:
            return
        observed.append(current_phase)
        marker = connection.execute(
            "SELECT validated_version, validated_payload_hash FROM catalog_drafts"
        ).fetchone()
        if current_phase == "before_ddl":
            assert _catalog_schema_fingerprint(connection) == V7_SCHEMA_FINGERPRINT
            assert marker is not None and marker[0] == 1 and marker[1] is not None
        elif current_phase == "after_ddl":
            assert connection.execute(
                "SELECT COUNT(*) FROM catalog_draft_validation_attestations"
            ).fetchone()[0] == 0
            assert marker is not None and marker[0] == 1 and marker[1] is not None
        else:
            assert _catalog_schema_fingerprint(connection) == _CATALOG_SCHEMA_FINGERPRINT
            assert marker is not None and tuple(marker) == (None, None)
        raise RuntimeError(f"synthetic migration fault at {current_phase}")

    monkeypatch.setattr(migration_module, "_migration_checkpoint", fail_at_checkpoint)

    with pytest.raises(RuntimeError, match=phase):
        migrate_catalog_v7_to_v8(database_path)

    assert observed == [phase]
    verify_v7_known_answer_database(database_path)


def test_migration_integrity_check_failure_rolls_back_to_complete_v7(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "catalog-v7.sqlite3"
    create_v7_known_answer_database(database_path)
    monkeypatch.setattr(
        migration_module,
        "_assert_integrity",
        lambda _connection: (_ for _ in ()).throw(
            ValueError("catalog migration foreign-key check failed")
        ),
    )

    with pytest.raises(ValueError, match="foreign-key"):
        migrate_catalog_v7_to_v8(database_path)

    verify_v7_known_answer_database(database_path)


def test_migrated_draft_requires_external_revalidation(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "catalog-v7.sqlite3"
    create_v7_known_answer_database(database_path)
    assert migrate_catalog_v7_to_v8(database_path) is True
    context = CatalogContext(
        operator_id="operator-v7",
        workspace_id="workspace-v7",
        tenant_id="tenant-v7",
        scope="workspace",
    )
    with sqlite3.connect(database_path) as connection:
        draft = connection.execute(
            "SELECT version, payload_hash FROM catalog_drafts WHERE draft_id = 'draft-v7'"
        ).fetchone()
    assert draft is not None

    with pytest.raises(CatalogStoreError, match="validation key provider"):
        CatalogStore(database_path).mark_draft_validated(
            context,
            "draft-v7",
            expected_version=draft[0],
            expected_payload_hash=draft[1],
        )

    provider = HmacValidationKeyProvider(
        authority_id="m2-test-authority",
        active_key_id="m2-test-key",
        keys={"m2-test-key": b"M" * 32},
    )
    CatalogStore(database_path, validation_key_provider=provider).mark_draft_validated(
        context,
        "draft-v7",
        expected_version=draft[0],
        expected_payload_hash=draft[1],
    )
    with sqlite3.connect(database_path) as connection:
        marker = connection.execute(
            "SELECT validated_version, validated_payload_hash FROM catalog_drafts"
        ).fetchone()
        attestation_count = connection.execute(
            "SELECT COUNT(*) FROM catalog_draft_validation_attestations"
        ).fetchone()[0]

    assert marker == draft
    assert attestation_count == 1


@pytest.mark.parametrize(
    "schema_mutator",
    [add_unknown_schema_object, add_synthetic_preview_v8_attestation_shape],
    ids=["unknown-fingerprint", "synthetic-preview-v8"],
)
def test_current_store_rejects_unknown_or_preview_schema_without_mutation(
    tmp_path: Path,
    schema_mutator: object,
) -> None:
    database_path = tmp_path / "catalog-unsupported.sqlite3"
    create_v7_known_answer_database(database_path)
    assert callable(schema_mutator)
    schema_mutator(database_path)
    before = _sha256(database_path)

    with pytest.raises(ValueError, match="catalog schema validation failed"):
        CatalogStore(database_path)

    assert _sha256(database_path) == before
    assert not database_path.with_name(f"{database_path.name}-wal").exists()
    assert not database_path.with_name(f"{database_path.name}-shm").exists()
    assert not database_path.with_name(f"{database_path.name}-journal").exists()


def test_v7_known_answer_verifier_rejects_revision_bundle_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "catalog-v7.sqlite3"
    create_v7_known_answer_database(database_path)
    with sqlite3.connect(database_path) as connection:
        connection.execute("DROP TRIGGER catalog_revisions_no_update")
        connection.execute(
            "UPDATE catalog_revisions SET source_draft_id = NULL, "
            "source_draft_version = NULL, source_draft_payload_hash = NULL"
        )
    monkeypatch.setattr(
        v7_fixture,
        "fingerprint_v7_database",
        lambda _path: V7_SCHEMA_FINGERPRINT,
    )

    with pytest.raises(AssertionError, match="revision"):
        verify_v7_known_answer_database(database_path)
