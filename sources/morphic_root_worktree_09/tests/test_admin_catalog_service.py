from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

import core.admin_catalog.store as store_module
from core.admin_catalog import (
    AdminCatalogService,
    CatalogContext,
    CatalogEntry,
    DraftConflictError,
    DraftNotFoundError,
    DraftValidationError,
    EntryType,
    PublishedDraftError,
    RevisionConflictError,
)
from core.admin_catalog.store import (
    CatalogStore,
    CatalogStoreError,
    ConcurrencyError,
    StoreAccessError,
)
from core.admin_catalog.validation_attestation import HmacValidationKeyProvider


def _catalog_store(path: Path) -> CatalogStore:
    return CatalogStore(
        path,
        validation_key_provider=HmacValidationKeyProvider(
            authority_id="admin-catalog-service-tests",
            active_key_id="test-v1",
            keys={"test-v1": b"K" * 32},
        ),
    )


def _context(suffix: str = "a") -> CatalogContext:
    return CatalogContext(
        operator_id=f"operator-{suffix}",
        workspace_id=f"workspace-{suffix}",
        tenant_id=f"tenant-{suffix}",
        scope="workspace",
    )


def _group(
    context: CatalogContext,
    entry_id: str,
    *,
    label: str | None = None,
) -> CatalogEntry:
    return CatalogEntry(
        entry_type=EntryType.GROUP,
        entry_id=entry_id,
        context=context,
        source_id="synthetic-fixture",
        provenance="f2-service-test",
        data={"label": label or entry_id, "enabled": True},
    )


def _profile(
    context: CatalogContext,
    entry_id: str,
    group_ids: list[str],
) -> CatalogEntry:
    return CatalogEntry(
        entry_type=EntryType.PROFILE,
        entry_id=entry_id,
        context=context,
        source_id="synthetic-fixture",
        provenance="f2-service-test",
        data={"label": entry_id, "group_ids": group_ids, "enabled": True},
    )


def _service(tmp_path: Path) -> AdminCatalogService:
    return AdminCatalogService(_catalog_store(tmp_path / "catalog.db"))


def test_draft_create_update_delete_mutates_no_revision_or_activation(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()

    created = service.create_draft(context, "draft-1", [_group(context, "group-a")])
    updated = service.update_draft(
        context,
        "draft-1",
        [_group(context, "group-b")],
        expected_version=1,
    )

    assert created.version == 1
    assert updated.version == 2
    assert updated.entry_ids == ("group-b",)
    assert service.store.list_revision_ids(context) == []
    assert service.store.current_revision_id(context) is None
    assert service.store.audit_event_count(context) == 0

    service.delete_draft(context, "draft-1", expected_version=2)

    assert service.store.get_draft(context, "draft-1") is None
    assert service.store.list_revision_ids(context) == []


def test_draft_updates_and_deletes_require_the_expected_version(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(context, "draft-1", [_group(context, "group-a")])

    with pytest.raises(DraftConflictError):
        service.update_draft(
            context,
            "draft-1",
            [_group(context, "group-b")],
            expected_version=2,
        )
    with pytest.raises(DraftConflictError):
        service.update_draft(
            context,
            "draft-1",
            [_group(context, "group-b")],
            expected_version=True,
        )
    with pytest.raises(DraftConflictError):
        service.delete_draft(context, "draft-1", expected_version=2)
    with pytest.raises(DraftConflictError):
        service.delete_draft(context, "draft-1", expected_version=True)

    assert service.get_draft(context, "draft-1").version == 1


def test_publish_requires_prior_successful_validation_and_exact_draft_version(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(context, "draft-1", [_group(context, "group-a")])

    with pytest.raises(DraftValidationError):
        service.publish_draft(
            context,
            "draft-1",
            "revision-1",
            expected_draft_version=1,
        )

    result = service.validate_draft(context, "draft-1")
    assert result.is_valid is True

    with pytest.raises(DraftConflictError):
        service.publish_draft(
            context,
            "draft-1",
            "revision-bool",
            expected_draft_version=True,
        )

    with pytest.raises(DraftConflictError):
        service.publish_draft(
            context,
            "draft-1",
            "revision-1",
            expected_draft_version=2,
        )

    published = AdminCatalogService(service.store).publish_draft(
        context,
        "draft-1",
        "revision-1",
        expected_draft_version=1,
    )

    assert published.revision_id == "revision-1"
    assert published.draft_version == 1
    assert service.store.list_revision_ids(context) == ["revision-1"]
    assert service.store.current_revision_id(context) is None


def test_duplicate_revision_id_is_a_domain_conflict_without_side_effects(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(context, "draft-1", [_group(context, "group-a")])
    service.validate_draft(context, "draft-1")
    service.publish_draft(
        context,
        "draft-1",
        "revision-1",
        expected_draft_version=1,
    )

    with pytest.raises(RevisionConflictError):
        service.publish_draft(
            context,
            "draft-1",
            "revision-1",
            expected_draft_version=1,
        )

    assert service.store.list_revision_ids(context) == ["revision-1"]
    assert service.store.current_revision_id(context) is None
    assert service.store.audit_event_count(context) == 0


def test_publish_does_not_misclassify_non_unique_integrity_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(context, "draft-1", [_group(context, "group-a")])
    service.validate_draft(context, "draft-1")

    def fail_with_non_unique_error(*args: object, **kwargs: object) -> str:
        raise sqlite3.IntegrityError("synthetic non-unique constraint")

    monkeypatch.setattr(
        service.store, "publish_validated_draft", fail_with_non_unique_error
    )

    with pytest.raises(sqlite3.IntegrityError, match="non-unique"):
        service.publish_draft(
            context,
            "draft-1",
            "revision-1",
            expected_draft_version=1,
        )


def test_invalid_draft_cannot_be_published(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(
        context,
        "draft-1",
        [_profile(context, "profile-a", ["missing-group"])],
    )

    validation = service.validate_draft(context, "draft-1")

    assert validation.is_valid is False
    assert validation.errors[0].code == "unknown_reference"
    with pytest.raises(DraftValidationError):
        service.publish_draft(
            context,
            "draft-1",
            "revision-1",
            expected_draft_version=1,
        )
    assert service.store.list_revision_ids(context) == []


def test_validation_marker_is_strict_persistent_and_invalidated_by_update(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "catalog.db"
    context = _context()
    service = AdminCatalogService(_catalog_store(database_path))
    state = service.create_draft(context, "draft-1", [_group(context, "group-a")])
    assert service.validate_draft(context, "draft-1").is_valid

    with pytest.raises(ConcurrencyError):
        service.store.mark_draft_validated(
            context,
            "draft-1",
            expected_version=True,
            expected_payload_hash=state.payload_hash,
        )

    reopened = AdminCatalogService(_catalog_store(database_path))
    persisted = reopened.store.get_draft(context, "draft-1")
    assert persisted is not None
    assert persisted["validated_version"] == 1
    reopened.update_draft(
        context,
        "draft-1",
        [_group(context, "group-b")],
        expected_version=1,
    )
    invalidated = reopened.store.get_draft(context, "draft-1")
    assert invalidated is not None
    assert invalidated["validated_version"] is None
    assert invalidated["validated_payload_hash"] is None
    with pytest.raises(DraftValidationError):
        reopened.publish_draft(
            context,
            "draft-1",
            "revision-1",
            expected_draft_version=2,
        )


def test_published_draft_delete_has_explicit_domain_error(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(context, "draft-1", [_group(context, "group-a")])
    service.validate_draft(context, "draft-1")
    service.publish_draft(
        context,
        "draft-1",
        "revision-1",
        expected_draft_version=1,
    )

    with pytest.raises(PublishedDraftError):
        service.delete_draft(context, "draft-1", expected_version=1)

    assert service.get_draft(context, "draft-1").version == 1
    assert service.store.list_revision_ids(context) == ["revision-1"]
    assert service.store.current_revision_id(context) is None
    assert service.store.audit_event_count(context) == 0


def test_delete_draft_does_not_misclassify_non_foreign_key_integrity_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(context, "draft-1", [_group(context, "group-a")])

    def fail_with_non_fk_error(*args: object, **kwargs: object) -> None:
        raise sqlite3.IntegrityError("synthetic non-foreign-key constraint")

    monkeypatch.setattr(service.store, "delete_draft", fail_with_non_fk_error)

    with pytest.raises(sqlite3.IntegrityError, match="non-foreign-key"):
        service.delete_draft(context, "draft-1", expected_version=1)


def test_revision_finalize_trigger_binds_source_snapshot_fields(tmp_path: Path) -> None:
    store = _catalog_store(tmp_path / "catalog.db")
    context = _context()
    store.create_draft(context, "draft-1", [_group(context, "group-a")])
    draft = store.get_draft(context, "draft-1")
    assert draft is not None
    with store_module._write_connection(store.db_path) as connection:
        connection.execute(
            """
            INSERT INTO catalog_revisions (
                operator_id, workspace_id, tenant_id, scope, revision_id,
                source_draft_id, source_draft_version,
                source_draft_payload_hash, payload_hash, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                context.operator_id,
                context.workspace_id,
                context.tenant_id,
                context.scope,
                "revision-unfinalized",
                "draft-1",
                1,
                draft["payload_hash"],
                "0" * 64,
                "2026-07-13T00:00:00+00:00",
            ),
        )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                UPDATE catalog_revisions
                SET finalized = 1, source_draft_version = 2
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND revision_id = ?
                """,
                (
                    context.operator_id,
                    context.workspace_id,
                    context.tenant_id,
                    context.scope,
                    "revision-unfinalized",
                ),
            )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                UPDATE catalog_revisions
                SET finalized = 1, source_draft_payload_hash = ?
                WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
                  AND scope = ? AND revision_id = ?
                """,
                (
                    "f" * 64,
                    context.operator_id,
                    context.workspace_id,
                    context.tenant_id,
                    context.scope,
                    "revision-unfinalized",
                ),
            )


def test_revision_persists_exact_mutable_draft_snapshot_provenance(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    first = service.create_draft(
        context, "draft-1", [_group(context, "group-a", label="First")]
    )
    service.validate_draft(context, "draft-1")
    service.publish_draft(
        context,
        "draft-1",
        "revision-1",
        expected_draft_version=1,
    )
    second = service.update_draft(
        context,
        "draft-1",
        [_group(context, "group-a", label="First")],
        expected_version=1,
    )
    assert second.payload_hash == first.payload_hash
    service.validate_draft(context, "draft-1")
    service.publish_draft(
        context,
        "draft-1",
        "revision-2",
        expected_draft_version=2,
    )

    assert service.store.get_revision_provenance(context, "revision-1") == {
        "source_draft_id": "draft-1",
        "source_draft_version": 1,
        "source_draft_payload_hash": first.payload_hash,
    }
    assert service.store.get_revision_provenance(context, "revision-2") == {
        "source_draft_id": "draft-1",
        "source_draft_version": 2,
        "source_draft_payload_hash": second.payload_hash,
    }
    with service.store.connect_readonly() as connection:
        revision_hashes = [
            str(row["payload_hash"])
            for row in connection.execute(
                "SELECT payload_hash FROM catalog_revisions ORDER BY revision_id"
            ).fetchall()
        ]
    assert len(set(revision_hashes)) == 2


def test_publish_failure_rolls_back_partial_revision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(context, "draft-1", [_group(context, "group-a")])
    service.validate_draft(context, "draft-1")
    original_connect = store_module._connect_database

    def connect_with_finalize_failure(path: Path) -> sqlite3.Connection:
        connection = original_connect(path)
        connection.execute(
            """
            CREATE TEMP TRIGGER synthetic_revision_finalize_failure
            BEFORE UPDATE OF finalized ON main.catalog_revisions
            WHEN NEW.revision_id = 'revision-partial'
            BEGIN
                SELECT RAISE(ABORT, 'synthetic finalize boundary failure');
            END
            """
        )
        return connection

    monkeypatch.setattr(store_module, "_connect_database", connect_with_finalize_failure)

    with pytest.raises(sqlite3.IntegrityError, match="synthetic finalize boundary failure"):
        service.publish_draft(
            context,
            "draft-1",
            "revision-partial",
            expected_draft_version=1,
        )

    assert service.store.list_revision_ids(context) == []
    assert service.store.get_revision_entries(context, "revision-partial") is None


def test_entry_roundtrip_preserves_every_type_and_structured_data(tmp_path: Path) -> None:
    store = _catalog_store(tmp_path / "catalog.db")
    context = _context()
    data_by_type: dict[EntryType, dict[str, object]] = {
        EntryType.PROFILE: {"label": "Profile", "group_ids": ["entry-1"]},
        EntryType.GROUP: {
            "label": "Group",
            "aliases": ["group-alias"],
            "enabled": True,
        },
        EntryType.REMEDY: {"label": "Remedy", "terminology_ids": ["entry-5"]},
        EntryType.PATHOGEN: {"label": "Pathogen", "description": "Synthetic"},
        EntryType.MULTIPLEX: {
            "label": "Multiplex",
            "group_ids": ["entry-1"],
            "remedy_ids": ["entry-2"],
        },
        EntryType.TERMINOLOGY: {
            "code": "TERM-A",
            "label": "Term",
            "scheme": "synthetic",
            "target_entry_id": "entry-0",
            "target_entry_type": "profile",
        },
        EntryType.RELATION: {
            "pathogen_id": "entry-3",
            "priority": 2,
            "relation_type": "remedy_pathogen",
            "remedy_id": "entry-2",
        },
    }
    entries = tuple(
        CatalogEntry(
            entry_type=entry_type,
            entry_id=f"entry-{index}",
            context=context,
            source_id="synthetic-roundtrip",
            provenance="f2-roundtrip",
            data=data_by_type[entry_type],
        )
        for index, entry_type in enumerate(EntryType)
    )
    expected = sorted(entry.canonical_json() for entry in entries)

    store.create_draft(context, "draft-roundtrip", entries)
    draft_entries = store.get_draft_entries(context, "draft-roundtrip")
    store.create_revision(context, "revision-roundtrip", entries)
    revision_entries = store.get_revision_entries(context, "revision-roundtrip")

    assert draft_entries is not None
    assert revision_entries is not None
    assert sorted(entry.canonical_json() for entry in draft_entries) == expected
    assert sorted(entry.canonical_json() for entry in revision_entries) == expected


def test_draft_diff_against_active_revision_is_deterministic(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(context, "draft-1", [_group(context, "group-a", label="A")])
    service.validate_draft(context, "draft-1")
    service.publish_draft(
        context,
        "draft-1",
        "revision-1",
        expected_draft_version=1,
    )
    service.activate_revision(
        context,
        "revision-1",
        expected_previous_revision_id=None,
        expected_activation_version=0,
        actor_id="operator-a",
        reason="approved baseline",
    )
    service.update_draft(
        context,
        "draft-1",
        [
            _group(context, "group-b", label="B"),
            _group(context, "group-a", label="A changed"),
        ],
        expected_version=1,
    )

    first = service.diff_draft(context, "draft-1")
    second = service.diff_draft(context, "draft-1")

    assert first == second
    assert first.added == ("group:group-b",)
    assert first.changed == ("group:group-a",)
    assert first.removed == ()


def test_activate_deactivate_and_rollback_are_separate_audited_operations(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(context, "draft-1", [_group(context, "group-a")])
    service.validate_draft(context, "draft-1")
    service.publish_draft(
        context,
        "draft-1",
        "revision-1",
        expected_draft_version=1,
    )

    assert service.activate_revision(
        context,
        "revision-1",
        expected_previous_revision_id=None,
        expected_activation_version=0,
        actor_id="operator-a",
        reason="activate",
    ) == 1
    with pytest.raises(CatalogStoreError):
        service.deactivate(
            context,
            expected_previous_revision_id="revision-1",
            expected_activation_version=True,
            actor_id="operator-a",
            reason="invalid boolean version",
        )
    assert service.deactivate(
        context,
        expected_previous_revision_id="revision-1",
        expected_activation_version=1,
        actor_id="operator-a",
        reason="maintenance",
    ) == 2
    assert service.store.current_revision_id(context) is None
    assert service.store.list_revision_ids(context) == ["revision-1"]

    with pytest.raises(ConcurrencyError):
        service.activate_revision(
            context,
            "revision-1",
            expected_previous_revision_id=None,
            expected_activation_version=0,
            actor_id="operator-a",
            reason="stale after deactivate",
        )

    assert service.activate_revision(
        context,
        "revision-1",
        expected_previous_revision_id=None,
        expected_activation_version=2,
        actor_id="operator-a",
        reason="reactivate",
    ) == 3
    service.update_draft(
        context,
        "draft-1",
        [_group(context, "group-b")],
        expected_version=1,
    )
    service.validate_draft(context, "draft-1")
    service.publish_draft(
        context,
        "draft-1",
        "revision-2",
        expected_draft_version=2,
    )
    assert service.activate_revision(
        context,
        "revision-2",
        expected_previous_revision_id="revision-1",
        expected_activation_version=3,
        actor_id="operator-a",
        reason="activate revision 2",
    ) == 4
    service.update_draft(
        context,
        "draft-1",
        [_group(context, "group-c")],
        expected_version=2,
    )
    service.validate_draft(context, "draft-1")
    service.publish_draft(
        context,
        "draft-1",
        "revision-never-active",
        expected_draft_version=3,
    )

    with pytest.raises(CatalogStoreError):
        service.rollback(
            context,
            target_revision_id="revision-2",
            expected_previous_revision_id="revision-2",
            expected_activation_version=4,
            actor_id="operator-a",
            reason="current revision is not a rollback target",
        )
    with pytest.raises(CatalogStoreError):
        service.rollback(
            context,
            target_revision_id="revision-never-active",
            expected_previous_revision_id="revision-2",
            expected_activation_version=4,
            actor_id="operator-a",
            reason="never active is not a rollback target",
        )
    assert service.store.current_activation(context) == ("revision-2", 4)
    assert service.store.audit_event_count(context) == 4

    assert service.rollback(
        context,
        target_revision_id="revision-1",
        expected_previous_revision_id="revision-2",
        expected_activation_version=4,
        actor_id="operator-a",
        reason="verified rollback",
    ) == 5
    assert service.store.current_revision_id(context) == "revision-1"
    assert service.store.audit_event_count(context) == 5
    assert service.store.verify_audit_chain(context) is True
    with service.store.connect_readonly() as connection:
        event_types = [
            str(row["event_type"])
            for row in connection.execute(
                "SELECT event_type FROM catalog_audit_events ORDER BY event_id"
            ).fetchall()
        ]
    assert event_types == [
        "activate",
        "deactivate",
        "activate",
        "activate",
        "rollback",
    ]


def test_foreign_context_cannot_read_update_publish_or_activate_draft(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    owner = _context("owner")
    foreign = _context("foreign")
    service.create_draft(owner, "draft-1", [_group(owner, "group-a")])
    service.validate_draft(owner, "draft-1")
    service.publish_draft(
        owner,
        "draft-1",
        "revision-1",
        expected_draft_version=1,
    )

    with pytest.raises(DraftNotFoundError):
        service.get_draft(foreign, "draft-1")
    with pytest.raises(DraftNotFoundError):
        service.update_draft(
            foreign,
            "draft-1",
            [_group(foreign, "group-a")],
            expected_version=1,
        )
    with pytest.raises(DraftNotFoundError):
        service.publish_draft(
            foreign,
            "draft-1",
            "revision-1",
            expected_draft_version=1,
        )
    with pytest.raises(StoreAccessError):
        service.activate_revision(
            foreign,
            "revision-1",
            expected_previous_revision_id=None,
            expected_activation_version=0,
            actor_id="operator-foreign",
            reason="must fail",
        )

    assert service.store.list_revision_ids(foreign) == []
    assert service.store.current_revision_id(foreign) is None
