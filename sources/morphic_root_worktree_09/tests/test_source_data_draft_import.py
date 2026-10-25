from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
import core.source_registry as source_registry_module

from core.admin_catalog import (
    AdminCatalogService,
    CatalogContext,
    CatalogEntry,
    DraftConflictError,
    DraftValidationError,
    EntryType,
)
from core.admin_catalog.store import CatalogStore
from core.admin_catalog.validation_attestation import HmacValidationKeyProvider
from core.source_data_promotion import (
    SourceDataPromotionError,
    import_staged_source_data_to_draft as _import_staged_source_data_to_draft,
    publish_source_imported_draft,

    stage_source_data_batch,
)
from core.source_registry import SourceRegistry


def _catalog_store(path: Path) -> CatalogStore:
    return CatalogStore(
        path,
        validation_key_provider=HmacValidationKeyProvider(
            authority_id="source-draft-import-tests",
            active_key_id="test-v1",
            keys={"test-v1": b"K" * 32},
        ),
    )


@pytest.fixture(autouse=True)
def _configured_source_registry_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        source_registry_module,
        "DEFAULT_SOURCE_REGISTRY_PATH",
        tmp_path / "sources.json",
    )


def import_staged_source_data_to_draft(
    staged_path: Path,
    **kwargs: object,
):
    return _import_staged_source_data_to_draft(
        staged_path,
        staging_root=staged_path.parent,
        **kwargs,
    )


def _context() -> CatalogContext:
    return CatalogContext(
        operator_id="operator-f5b",
        workspace_id="workspace-f5b",
        tenant_id="tenant-f5b",
        scope="workspace",
    )


def _write_registry(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 0,
                "rollback_history": [],
                "sources": [
                    {
                        "id": "admin_groups",
                        "label": "Admin Groups",
                        "source_type": "local_import",
                        "local_path": str(path.parent / "groups"),
                        "license": "admin-provided",
                        "trust_level": "admin_curated",
                        "import_policy": "manual_review",
                        "scopes": ["group"],
                        "enabled": True,
                        "status": "active",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def _write_group_batch(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_id": "admin_groups",
                "source_version": "2026-07-15",
                "data_type": "group",
                "license": "admin-provided",
                "retrieval_metadata": {
                    "retrieved_at": "2026-07-15T07:30:00+00:00",
                    "method": "local_admin_import",
                },
                "records": [{"id": "group-a", "label": "Group A"}],
            }
        ),
        encoding="utf-8",
    )


def test_source_imported_draft_is_immutable_after_receipt_binding(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_group_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, tmp_path / "staging", registry)
    service = AdminCatalogService(_catalog_store(tmp_path / "catalog.db"))
    result = import_staged_source_data_to_draft(
        staged_path,
        registry=registry,
        service=service,
        context=_context(),
        draft_id="source-draft-a",
        actor_id="operator-f5b",
        reason="reviewed group import",
    )
    changed_entry = CatalogEntry(
        entry_type=EntryType.GROUP,
        entry_id="group-a",
        context=_context(),
        source_id="admin_groups",
        provenance="source-record:group-a",
        data={"label": "Changed"},
    )

    with pytest.raises(DraftConflictError, match="source|receipt|immutable"):
        service.update_draft(
            _context(),
            "source-draft-a",
            [changed_entry],
            expected_version=1,
        )

    assert service.get_draft(_context(), "source-draft-a") == result.draft


def test_source_imported_draft_cannot_be_hard_deleted_or_reused(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_group_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, tmp_path / "staging", registry)
    service = AdminCatalogService(_catalog_store(tmp_path / "catalog.db"))
    import_staged_source_data_to_draft(
        staged_path,
        registry=registry,
        service=service,
        context=_context(),
        draft_id="source-draft-a",
        actor_id="operator-f5b",
        reason="reviewed group import",
    )

    with pytest.raises(DraftConflictError, match="source|receipt|delete"):
        service.delete_draft(
            _context(), "source-draft-a", expected_version=1
        )

    assert service.store.get_draft(_context(), "source-draft-a") is not None
    assert len(service.store.source_import_receipts(_context(), "source-draft-a")) == 1


def test_source_import_receipt_rows_are_append_only(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    catalog_db = tmp_path / "catalog.db"
    _write_registry(registry_path)
    _write_group_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, tmp_path / "staging", registry)
    service = AdminCatalogService(_catalog_store(catalog_db))
    import_staged_source_data_to_draft(
        staged_path,
        registry=registry,
        service=service,
        context=_context(),
        draft_id="source-draft-a",
        actor_id="operator-f5b",
        reason="reviewed group import",
    )

    with sqlite3.connect(catalog_db) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                "UPDATE catalog_draft_source_imports SET reason = 'tampered'"
            )
        connection.rollback()
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute("DELETE FROM catalog_draft_source_imports")

    assert len(service.store.source_import_receipts(_context(), "source-draft-a")) == 1


def test_registry_drift_blocks_source_receipt_publish(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_group_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, tmp_path / "staging", registry)
    service = AdminCatalogService(_catalog_store(tmp_path / "catalog.db"))
    import_staged_source_data_to_draft(
        staged_path,
        registry=registry,
        service=service,
        context=_context(),
        draft_id="source-draft-a",
        actor_id="operator-f5b",
        reason="reviewed group import",
    )
    assert service.validate_draft(_context(), "source-draft-a").is_valid
    SourceRegistry.load(registry_path).disable_source("admin_groups")

    with pytest.raises(DraftValidationError, match="revalidation"):
        service.publish_draft(
            _context(),
            "source-draft-a",
            "revision-stale",
            expected_draft_version=1,
        )

    assert service.store.list_revision_ids(_context()) == []


def test_quarantined_normalization_leaves_no_draft_or_receipt(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_group_batch(batch_path)
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    batch["records"][0]["unverified_claim"] = "not allowed"
    batch_path.write_text(json.dumps(batch), encoding="utf-8")
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, tmp_path / "staging", registry)
    service = AdminCatalogService(_catalog_store(tmp_path / "catalog.db"))

    with pytest.raises(SourceDataPromotionError, match="quarantine"):
        import_staged_source_data_to_draft(
            staged_path,
            registry=registry,
            service=service,
            context=_context(),
            draft_id="quarantined-draft",
            actor_id="operator-f5b",
            reason="must not import",
        )

    assert service.store.get_draft(_context(), "quarantined-draft") is None
    assert service.store.source_import_receipts(_context(), "quarantined-draft") == ()


def test_cross_type_base_collision_rejects_entire_import_before_draft_write(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_group_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, tmp_path / "staging", registry)
    colliding_base = (
        CatalogEntry(
            entry_type=EntryType.REMEDY,
            entry_id="group-a",
            context=_context(),
            source_id="base-fixture",
            provenance="explicit-base",
            data={"label": "Colliding Remedy"},
        ),
    )
    service = AdminCatalogService(_catalog_store(tmp_path / "catalog.db"))
    service.store.create_revision(
        _context(), "base-collision", colliding_base
    )

    with pytest.raises(SourceDataPromotionError, match="snapshot|collision|invalid"):
        import_staged_source_data_to_draft(
            staged_path,
            registry=registry,
            service=service,
            context=_context(),
            draft_id="colliding-draft",
            actor_id="operator-f5b",
            reason="collision test",
            base_revision_id="base-collision",
        )

    assert service.store.get_draft(_context(), "colliding-draft") is None
    assert service.store.source_import_receipts(_context(), "colliding-draft") == ()


def test_relation_batch_without_label_imports_against_explicit_base_entries(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "relation-batch.json"
    _write_registry(registry_path)
    registry_payload = json.loads(registry_path.read_text(encoding="utf-8"))
    registry_payload["sources"][0]["scopes"] = ["relation"]
    registry_path.write_text(json.dumps(registry_payload), encoding="utf-8")
    batch_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_id": "admin_groups",
                "source_version": "2026-07-15",
                "data_type": "relation",
                "license": "admin-provided",
                "retrieval_metadata": {
                    "retrieved_at": "2026-07-15T07:30:00+00:00",
                    "method": "local_admin_import",
                },
                "records": [
                    {
                        "id": "relation-a",
                        "pathogen_id": "pathogen-a",
                        "priority": 1,
                        "relation_type": "remedy_pathogen",
                        "remedy_id": "remedy-a",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    registry = SourceRegistry.load(registry_path)
    base_entries = (
        CatalogEntry(
            entry_type=EntryType.PATHOGEN,
            entry_id="pathogen-a",
            context=_context(),
            source_id="base-fixture",
            provenance="explicit-base",
            data={"label": "Pathogen A"},
        ),
        CatalogEntry(
            entry_type=EntryType.REMEDY,
            entry_id="remedy-a",
            context=_context(),
            source_id="base-fixture",
            provenance="explicit-base",
            data={"label": "Remedy A"},
        ),
    )

    staged_path = stage_source_data_batch(
        batch_path, tmp_path / "staging", registry
    )
    service = AdminCatalogService(_catalog_store(tmp_path / "catalog.db"))
    service.store.create_revision(
        _context(), "base-relation", base_entries
    )
    result = import_staged_source_data_to_draft(
        staged_path,
        registry=registry,
        service=service,
        context=_context(),
        draft_id="relation-draft",
        actor_id="operator-f5b",
        reason="reviewed relation import",
        base_revision_id="base-relation",
    )

    assert result.draft.entry_ids == ("pathogen-a", "relation-a", "remedy-a")
    assert result.normalization.normalized[0].entry.entry_type is EntryType.RELATION


def test_replayed_stage_rolls_back_second_draft_and_receipt(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_group_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, tmp_path / "staging", registry)
    service = AdminCatalogService(_catalog_store(tmp_path / "catalog.db"))
    import_staged_source_data_to_draft(
        staged_path,
        registry=registry,
        service=service,
        context=_context(),
        draft_id="source-draft-a",
        actor_id="operator-f5b",
        reason="first import",
    )

    with pytest.raises(SourceDataPromotionError, match="replay|already|import"):
        import_staged_source_data_to_draft(
            staged_path,
            registry=registry,
            service=service,
            context=_context(),
            draft_id="source-draft-b",
            actor_id="operator-f5b",
            reason="replayed import",
        )

    assert service.store.get_draft(_context(), "source-draft-b") is None
    assert service.store.source_import_receipts(_context(), "source-draft-b") == ()


def test_current_registry_receipt_revalidation_allows_publish_not_activation(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_group_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, tmp_path / "staging", registry)
    service = AdminCatalogService(_catalog_store(tmp_path / "catalog.db"))
    import_staged_source_data_to_draft(
        staged_path,
        registry=registry,
        service=service,
        context=_context(),
        draft_id="source-draft-a",
        actor_id="operator-f5b",
        reason="reviewed group import",
    )
    assert service.validate_draft(_context(), "source-draft-a").is_valid

    published = publish_source_imported_draft(
        registry=registry,
        service=service,
        context=_context(),
        draft_id="source-draft-a",
        revision_id="revision-approved",
        expected_draft_version=1,
    )

    assert published.revision_id == "revision-approved"
    assert service.store.current_revision_id(_context()) is None
    assert service.store.audit_event_count(_context()) == 0


def test_source_imported_draft_cannot_publish_without_receipt_revalidation(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_group_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, tmp_path / "staging", registry)
    service = AdminCatalogService(_catalog_store(tmp_path / "catalog.db"))
    import_staged_source_data_to_draft(
        staged_path,
        registry=registry,
        service=service,
        context=_context(),
        draft_id="source-draft-a",
        actor_id="operator-f5b",
        reason="reviewed group import",
    )
    assert service.validate_draft(_context(), "source-draft-a").is_valid

    with pytest.raises(DraftValidationError, match="receipt|source"):
        service.publish_draft(
            _context(),
            "source-draft-a",
            "revision-forbidden",
            expected_draft_version=1,
        )

    assert service.store.list_revision_ids(_context()) == []


def test_staged_batch_creates_draft_and_approval_receipt_atomically(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_group_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, tmp_path / "staging", registry)
    staged_before = staged_path.read_bytes()
    service = AdminCatalogService(_catalog_store(tmp_path / "catalog.db"))

    result = import_staged_source_data_to_draft(
        staged_path,
        registry=registry,
        service=service,
        context=_context(),
        draft_id="source-draft-a",
        actor_id="operator-f5b",
        reason="reviewed group import",
    )

    assert result.draft.draft_id == "source-draft-a"
    assert result.draft.version == 1
    assert result.draft.entry_ids == ("group-a",)
    assert result.receipt.source_id == "admin_groups"
    assert result.receipt.draft_payload_hash == result.draft.payload_hash
    assert result.receipt.normalization_sha256 == result.normalization.sha256
    assert len(result.receipt.receipt_sha256) == 64
    assert service.store.source_import_receipts(_context(), "source-draft-a") == (
        result.receipt,
    )
    assert service.store.list_revision_ids(_context()) == []
    assert service.store.current_revision_id(_context()) is None
    assert service.store.audit_event_count(_context()) == 0
    assert staged_path.read_bytes() == staged_before
