from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

import pytest

from core.admin_catalog.backup import create_catalog_backup, restore_catalog_backup
from core.admin_catalog import (
    AdminCatalogService,
    CatalogContext,
    CatalogEntry,
    DraftConflictError,
    EntryType,
    ManagedEntryConflictError,
    ManagedEntryNotFoundError,
    ManagedEntryStateError,
    ManagedEntryTypeError,
    ManagedEntryValidationError,
    ReferencedRemedyError,
)
from core.admin_catalog.store import (
    CatalogStore,
    CatalogStoreError,
    ManagedEntryReferenceError,
    ManagedEntryRemovalError,
    TombstoneMutationError,
)
from core.admin_catalog.validation_attestation import HmacValidationKeyProvider


def _catalog_store(path: Path) -> CatalogStore:
    return CatalogStore(
        path,
        validation_key_provider=HmacValidationKeyProvider(
            authority_id="admin-remedy-tests",
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


def _entry(
    context: CatalogContext,
    entry_type: EntryType,
    entry_id: str,
    data: dict[str, object],
    *,
    provenance: str = "f4-3-test",
) -> CatalogEntry:
    return CatalogEntry(
        entry_type=entry_type,
        entry_id=entry_id,
        context=context,
        source_id="synthetic-fixture",
        provenance=provenance,
        data=data,
    )


def _group(context: CatalogContext, entry_id: str = "group-a") -> CatalogEntry:
    return _entry(
        context,
        EntryType.GROUP,
        entry_id,
        {"label": entry_id, "enabled": True},
    )


def _remedy(
    context: CatalogContext,
    entry_id: str = "remedy-a",
    *,
    enabled: bool = True,
    label: str | None = None,
    aliases: list[str] | None = None,
    tombstoned: bool = False,
) -> CatalogEntry:
    data: dict[str, object] = {
        "label": label or entry_id,
        "enabled": enabled,
    }
    if aliases is not None:
        data["aliases"] = aliases
    if tombstoned:
        data["tombstoned"] = True
    return _entry(context, EntryType.REMEDY, entry_id, data)


def _multiplex(
    context: CatalogContext,
    entry_id: str = "multiplex-a",
    *,
    group_ids: list[str] | None = None,
    remedy_ids: list[str] | None = None,
    enabled: bool = True,
    label: str | None = None,
    aliases: list[str] | None = None,
    tombstoned: bool = False,
) -> CatalogEntry:
    data: dict[str, object] = {
        "label": label or entry_id,
        "group_ids": ["group-a"] if group_ids is None else group_ids,
        "remedy_ids": ["remedy-a"] if remedy_ids is None else remedy_ids,
        "enabled": enabled,
    }
    if aliases is not None:
        data["aliases"] = aliases
    if tombstoned:
        data["tombstoned"] = True
    return _entry(context, EntryType.MULTIPLEX, entry_id, data)


def _pathogen(context: CatalogContext) -> CatalogEntry:
    return _entry(
        context,
        EntryType.PATHOGEN,
        "pathogen-a",
        {"label": "pathogen-a", "enabled": True},
    )


def _terminology(
    context: CatalogContext,
    entry_id: str = "terminology-a",
    *,
    target_entry_id: str = "remedy-a",
    target_entry_type: str = "remedy",
) -> CatalogEntry:
    return _entry(
        context,
        EntryType.TERMINOLOGY,
        entry_id,
        {
            "code": "TERM-A",
            "label": "Terminology A",
            "scheme": "synthetic",
            "target_entry_id": target_entry_id,
            "target_entry_type": target_entry_type,
        },
    )


def _relation(context: CatalogContext, *, enabled: bool = True) -> CatalogEntry:
    return _entry(
        context,
        EntryType.RELATION,
        "relation-a",
        {
            "relation_type": "remedy_pathogen",
            "remedy_id": "remedy-a",
            "pathogen_id": "pathogen-a",
            "priority": 7,
            "enabled": enabled,
        },
        provenance="curated-link-source",
    )


def _service(tmp_path: Path) -> AdminCatalogService:
    return AdminCatalogService(_catalog_store(tmp_path / "catalog.db"))


def _entries(
    service: AdminCatalogService,
    context: CatalogContext,
    draft_id: str = "draft-1",
) -> tuple[CatalogEntry, ...]:
    entries = service.store.get_draft_entries(context, draft_id)
    assert entries is not None
    return entries


def test_create_remedy_and_multiplex_are_versioned_draft_only(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(context, "draft-1", [_group(context)])

    remedy_state = service.create_remedy(
        context, "draft-1", _remedy(context), expected_version=1
    )
    multiplex_state = service.create_multiplex(
        context, "draft-1", _multiplex(context), expected_version=2
    )

    assert remedy_state.version == 2
    assert multiplex_state.version == 3
    assert service.get_remedy(context, "draft-1", "remedy-a").entry_type is EntryType.REMEDY
    assert (
        service.get_multiplex(context, "draft-1", "multiplex-a").entry_type
        is EntryType.MULTIPLEX
    )
    assert service.validate_draft(context, "draft-1").is_valid
    assert service.store.list_revision_ids(context) == []
    assert service.store.current_revision_id(context) is None
    assert service.store.audit_event_count(context) == 0


def test_update_disable_enable_preserve_identity_and_payload(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(
        context,
        "draft-1",
        [_group(context), _remedy(context, aliases=["remedy-alias"])],
    )

    updated = service.update_remedy(
        context,
        "draft-1",
        "remedy-a",
        _remedy(context, label="Updated", aliases=["remedy-alias"]),
        expected_version=1,
    )
    disabled = service.disable_remedy(
        context, "draft-1", "remedy-a", expected_version=2
    )
    enabled = service.enable_remedy(
        context, "draft-1", "remedy-a", expected_version=3
    )

    remedy = service.get_remedy(context, "draft-1", "remedy-a")
    assert (updated.version, disabled.version, enabled.version) == (2, 3, 4)
    assert remedy.data["label"] == "Updated"
    assert remedy.data["aliases"] == ("remedy-alias",)
    assert remedy.data["enabled"] is True


def test_managed_operations_reject_wrong_type_identity_context_and_cas(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    foreign = _context("foreign")
    service.create_draft(context, "draft-1", [_group(context), _remedy(context)])

    with pytest.raises(ManagedEntryTypeError):
        service.create_remedy(context, "draft-1", _group(context, "group-b"), expected_version=1)
    with pytest.raises(ManagedEntryConflictError, match="identity"):
        service.update_remedy(
            context,
            "draft-1",
            "remedy-a",
            _remedy(context, "remedy-renamed"),
            expected_version=1,
        )
    with pytest.raises(ManagedEntryValidationError):
        service.create_remedy(
            context,
            "draft-1",
            _remedy(foreign, "remedy-foreign"),
            expected_version=1,
        )
    with pytest.raises(DraftConflictError):
        service.disable_remedy(context, "draft-1", "remedy-a", expected_version=True)
    with pytest.raises(DraftConflictError):
        service.disable_remedy(context, "draft-1", "remedy-a", expected_version=2)
    with pytest.raises(ManagedEntryNotFoundError):
        service.get_multiplex(context, "draft-1", "missing")

    assert service.get_draft(context, "draft-1").version == 1


def test_invalid_multiplex_cross_references_fail_before_write(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(context, "draft-1", [_group(context), _remedy(context)])
    before = service.get_draft(context, "draft-1")

    with pytest.raises(ManagedEntryValidationError) as captured:
        service.create_multiplex(
            context,
            "draft-1",
            _multiplex(
                context,
                group_ids=["missing-group"],
                remedy_ids=["missing-remedy"],
            ),
            expected_version=1,
        )

    assert tuple(issue.code for issue in captured.value.result.errors) == (
        "unknown_reference",
        "unknown_reference",
    )
    assert service.get_draft(context, "draft-1") == before


@pytest.mark.parametrize("invalid_version", [True, 0, -1, "1", 1.5, None])
def test_managed_operations_reject_non_positive_non_integer_cas_without_mutation(
    tmp_path: Path,
    invalid_version: object,
) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(context, "draft-1", [_group(context)])
    before = service.get_draft(context, "draft-1")

    with pytest.raises(DraftConflictError):
        service.create_remedy(
            context,
            "draft-1",
            _remedy(context),
            expected_version=invalid_version,  # type: ignore[arg-type]
        )

    assert service.get_draft(context, "draft-1") == before


def test_referenced_remedy_tombstone_returns_deterministic_blockers(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(
        context,
        "draft-1",
        [
            _group(context),
            _remedy(context),
            _pathogen(context),
            _multiplex(context),
            _relation(context),
            _terminology(context),
        ],
    )
    before = service.get_draft(context, "draft-1")

    with pytest.raises(ReferencedRemedyError) as captured:
        service.delete_remedy(context, "draft-1", "remedy-a", expected_version=1)

    assert captured.value.references == (
        "multiplex:multiplex-a:remedy_ids",
        "relation:relation-a:remedy_id",
        "terminology:terminology-a:target_entry_id",
    )
    assert service.get_draft(context, "draft-1") == before


def test_relation_priority_and_provenance_are_versioned_without_implicit_cascade(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(
        context,
        "draft-1",
        [_remedy(context), _pathogen(context), _relation(context)],
    )
    updated_relation = _entry(
        context,
        EntryType.RELATION,
        "relation-a",
        {
            "relation_type": "remedy_pathogen",
            "remedy_id": "remedy-a",
            "pathogen_id": "pathogen-a",
            "priority": 3,
            "enabled": True,
        },
        provenance="operator-curated-link-v2",
    )

    state = service.update_draft(
        context,
        "draft-1",
        [_remedy(context), _pathogen(context), updated_relation],
        expected_version=1,
    )
    persisted = next(
        entry
        for entry in _entries(service, context)
        if entry.entry_type is EntryType.RELATION
    )

    assert state.version == 2
    assert persisted.data["priority"] == 3
    assert persisted.provenance == "operator-curated-link-v2"
    assert service.store.list_revision_ids(context) == []


def test_remedy_disable_is_blocked_by_terminology_reference(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(
        context,
        "draft-1",
        [_remedy(context), _terminology(context)],
    )
    before = service.get_draft(context, "draft-1")

    with pytest.raises(ManagedEntryValidationError) as captured:
        service.disable_remedy(context, "draft-1", "remedy-a", expected_version=1)

    assert "disabled_reference" in {
        issue.code for issue in captured.value.result.errors
    }
    assert service.get_draft(context, "draft-1") == before


def test_remedy_update_preserves_relation_identity_priority_and_provenance(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    relation = _relation(context)
    service.create_draft(
        context,
        "draft-1",
        [_remedy(context), _pathogen(context), relation],
    )

    service.update_remedy(
        context,
        "draft-1",
        "remedy-a",
        _remedy(context, label="Updated remedy"),
        expected_version=1,
    )
    persisted = next(
        entry
        for entry in _entries(service, context)
        if entry.entry_type is EntryType.RELATION
    )

    assert persisted.canonical_json() == relation.canonical_json()
    assert persisted.payload_hash == relation.payload_hash


def test_disabled_live_references_still_block_but_tombstoned_multiplex_does_not(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(
        context,
        "draft-1",
        [
            _group(context),
            _remedy(context),
            _pathogen(context),
            _multiplex(context, enabled=False),
            _relation(context, enabled=False),
        ],
    )

    with pytest.raises(ReferencedRemedyError):
        service.delete_remedy(context, "draft-1", "remedy-a", expected_version=1)

    service.delete_multiplex(context, "draft-1", "multiplex-a", expected_version=1)
    entries = tuple(
        entry for entry in _entries(service, context) if entry.entry_type is not EntryType.RELATION
    )
    service.update_draft(context, "draft-1", entries, expected_version=2)
    state = service.delete_remedy(context, "draft-1", "remedy-a", expected_version=3)

    assert state.version == 4
    assert service.get_remedy(context, "draft-1", "remedy-a").data["tombstoned"] is True


def test_remedy_and_multiplex_tombstones_are_retained_disabled_and_terminal(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    remedy = _remedy(context, aliases=["reserved-remedy-alias"])
    multiplex = _multiplex(
        context,
        aliases=["reserved-multiplex-alias"],
        remedy_ids=[],
    )
    service.create_draft(context, "draft-1", [_group(context), remedy, multiplex])

    service.delete_remedy(context, "draft-1", "remedy-a", expected_version=1)
    service.delete_multiplex(context, "draft-1", "multiplex-a", expected_version=2)

    remedy_tombstone = service.get_remedy(context, "draft-1", "remedy-a")
    multiplex_tombstone = service.get_multiplex(context, "draft-1", "multiplex-a")
    assert remedy_tombstone.data["enabled"] is False
    assert remedy_tombstone.data["tombstoned"] is True
    assert multiplex_tombstone.data["enabled"] is False
    assert multiplex_tombstone.data["tombstoned"] is True
    assert multiplex_tombstone.data["group_ids"] == ("group-a",)

    with pytest.raises(ManagedEntryStateError):
        service.enable_remedy(context, "draft-1", "remedy-a", expected_version=3)
    with pytest.raises(ManagedEntryStateError):
        service.update_multiplex(
            context,
            "draft-1",
            "multiplex-a",
            _multiplex(context, remedy_ids=[], label="resurrected"),
            expected_version=3,
        )


def test_generic_draft_write_cannot_omit_or_forge_managed_tombstones(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    group = _group(context)
    remedy = _remedy(context)
    multiplex = _multiplex(context)
    service.create_draft(context, "draft-live", [group, remedy, multiplex])
    service.create_draft(context, "draft-empty", [group])

    with pytest.raises(ManagedEntryConflictError, match="tombstone"):
        service.update_draft(context, "draft-live", [group], expected_version=1)
    with pytest.raises(ManagedEntryStateError, match="delete_"):
        service.update_draft(
            context,
            "draft-live",
            [
                group,
                _remedy(context, enabled=False, tombstoned=True),
                _multiplex(context, enabled=False, tombstoned=True),
            ],
            expected_version=1,
        )
    with pytest.raises(ManagedEntryStateError, match="delete_"):
        service.update_draft(
            context,
            "draft-empty",
            [group, _remedy(context, enabled=False, tombstoned=True)],
            expected_version=1,
        )

    assert service.get_draft(context, "draft-live").version == 1
    assert service.get_draft(context, "draft-empty").version == 1


def test_low_level_store_cannot_disable_referenced_remedy(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    entries = (
        _group(context),
        _remedy(context),
        _pathogen(context),
        _multiplex(context),
        _relation(context),
        _terminology(context),
    )
    service.create_draft(context, "draft-1", entries)
    candidate = tuple(
        _remedy(context, enabled=False)
        if entry.entry_type is EntryType.REMEDY
        else entry
        for entry in entries
    )

    with pytest.raises(ManagedEntryReferenceError) as captured:
        service.store.update_draft(
            context,
            "draft-1",
            candidate,
            expected_version=1,
        )

    assert captured.value.references == (
        "multiplex:multiplex-a:remedy_ids",
        "relation:relation-a:remedy_id",
        "terminology:terminology-a:target_entry_id",
    )
    assert service.get_draft(context, "draft-1").version == 1


def test_low_level_store_and_direct_revision_cannot_bypass_managed_policy(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    group = _group(context)
    remedy = _remedy(context)
    service.create_draft(context, "draft-1", [group, remedy])

    with pytest.raises(ManagedEntryRemovalError):
        service.store.update_draft(context, "draft-1", [group], expected_version=1)
    with pytest.raises(TombstoneMutationError, match="delete_remedy"):
        service.store.update_draft(
            context,
            "draft-1",
            [group, _remedy(context, enabled=False, tombstoned=True)],
            expected_version=1,
        )

    assert service.validate_draft(context, "draft-1").is_valid
    service.publish_draft(
        context, "draft-1", "revision-live", expected_draft_version=1
    )
    service.delete_remedy(context, "draft-1", "remedy-a", expected_version=1)
    assert service.validate_draft(context, "draft-1").is_valid
    service.publish_draft(
        context, "draft-1", "revision-tombstone", expected_draft_version=2
    )
    tombstone = service.get_remedy(context, "draft-1", "remedy-a")

    with pytest.raises(ManagedEntryRemovalError):
        service.store.create_revision(context, "revision-omit", [group])
    with pytest.raises(TombstoneMutationError, match="terminal"):
        service.store.create_revision(context, "revision-resurrect", [group, remedy])
    service.store.create_revision(context, "revision-carry", [group, tombstone])

    assert service.store.list_revision_ids(context) == [
        "revision-carry",
        "revision-live",
        "revision-tombstone",
    ]


def test_new_draft_cannot_forge_managed_tombstone_or_resurrect_published_one(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    group = _group(context)
    remedy = _remedy(context, aliases=["reserved-remedy-alias"])

    with pytest.raises(ManagedEntryStateError, match="delete_remedy"):
        service.create_draft(
            context,
            "draft-forged",
            [group, _remedy(context, enabled=False, tombstoned=True)],
        )

    service.create_draft(context, "draft-source", [group, remedy])
    service.create_draft(context, "draft-stale", [group, remedy])
    assert service.validate_draft(context, "draft-source").is_valid
    service.publish_draft(
        context, "draft-source", "revision-live", expected_draft_version=1
    )
    service.delete_remedy(
        context, "draft-source", "remedy-a", expected_version=1
    )
    assert service.validate_draft(context, "draft-source").is_valid
    service.publish_draft(
        context, "draft-source", "revision-tombstone", expected_draft_version=2
    )

    with pytest.raises(ManagedEntryStateError, match="terminal"):
        service.create_draft(context, "draft-resurrection", [group, remedy])
    assert service.validate_draft(context, "draft-stale").is_valid
    with pytest.raises(ManagedEntryStateError, match="terminal"):
        service.publish_draft(
            context,
            "draft-stale",
            "revision-stale",
            expected_draft_version=1,
        )

    with pytest.raises(ManagedEntryStateError, match="reserved"):
        service.create_draft(
            context,
            "draft-id-theft",
            [group, _group(context, "Remedy-A")],
        )
    with pytest.raises(ManagedEntryStateError, match="reserved"):
        service.create_draft(
            context,
            "draft-alias-theft",
            [group, _remedy(context, "remedy-b", aliases=["reserved-remedy-alias"])],
        )
    with pytest.raises(ManagedEntryStateError, match="reserved"):
        service.create_draft(
            context,
            "draft-id-to-alias-theft",
            [group, _remedy(context, "reserved-remedy-alias")],
        )
    with pytest.raises(ManagedEntryStateError, match="reserved"):
        service.create_draft(
            context,
            "draft-alias-to-id-theft",
            [group, _remedy(context, "remedy-c", aliases=["remedy-a"])],
        )


def test_cross_draft_publish_cannot_omit_a_published_managed_entry(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    group = _group(context)
    service.create_draft(context, "draft-source", [group, _remedy(context)])
    assert service.validate_draft(context, "draft-source").is_valid
    service.publish_draft(
        context, "draft-source", "revision-source", expected_draft_version=1
    )
    service.create_draft(context, "draft-omit", [group])
    assert service.validate_draft(context, "draft-omit").is_valid

    with pytest.raises(ManagedEntryConflictError, match="tombstone"):
        service.publish_draft(
            context, "draft-omit", "revision-omit", expected_draft_version=1
        )

    assert service.store.list_revision_ids(context) == ["revision-source"]


def test_direct_revision_validates_managed_cross_references(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()

    with pytest.raises(CatalogStoreError, match="unknown_reference"):
        service.store.create_revision(
            context,
            "revision-invalid",
            [
                _remedy(context),
                _multiplex(
                    context,
                    group_ids=["missing-group"],
                    remedy_ids=["remedy-a"],
                ),
            ],
        )

    assert service.store.list_revision_ids(context) == []


def test_direct_revision_rejects_relation_and_terminology_only_unknown_targets(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()

    for revision_id, entries in (
        ("revision-relation-only", [_relation(context)]),
        ("revision-terminology-only", [_terminology(context)]),
        (
            "revision-missing-terminology-id",
            [
                _entry(
                    context,
                    EntryType.REMEDY,
                    "remedy-a",
                    {
                        "label": "Remedy A",
                        "terminology_ids": ["missing-term"],
                    },
                )
            ],
        ),
    ):
        with pytest.raises(CatalogStoreError, match="unknown_reference"):
            service.store.create_revision(context, revision_id, entries)

    assert service.store.list_revision_ids(context) == []


def test_invalid_draft_cannot_be_attested_or_published_with_forged_marker(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    payload_hash = service.store.create_draft(
        context,
        "draft-invalid",
        [_relation(context)],
    )

    with pytest.raises(CatalogStoreError, match="unknown_reference"):
        service.store.mark_draft_validated(
            context,
            "draft-invalid",
            expected_version=1,
            expected_payload_hash=payload_hash,
        )

    with sqlite3.connect(service.store.db_path) as connection:
        connection.execute(
            """
            UPDATE catalog_drafts
            SET validated_version = version, validated_payload_hash = payload_hash
            WHERE draft_id = ?
            """,
            ("draft-invalid",),
        )

    with pytest.raises(
        CatalogStoreError, match="unknown_reference|validation attestation"
    ):
        service.store.publish_validated_draft(
            context,
            "draft-invalid",
            "revision-forged",
            expected_draft_version=1,
        )

    assert service.store.list_revision_ids(context) == []


def test_create_draft_materializes_stateful_input_exactly_once(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    local_group = _group(context)
    foreign_group = _group(_context("foreign"), "group-foreign")

    class StatefulEntries:
        def __init__(self) -> None:
            self.iterations = 0

        def __iter__(self):
            self.iterations += 1
            if self.iterations == 1:
                return iter((local_group,))
            return iter((foreign_group,))

    entries = StatefulEntries()
    service.store.create_draft(  # type: ignore[arg-type]
        context,
        "draft-stateful",
        entries,
    )

    assert entries.iterations == 1
    assert service.store.get_draft_entries(context, "draft-stateful") == (
        local_group,
    )


def test_direct_revision_materializes_stateful_input_exactly_once(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    group = _group(context)
    remedy = _remedy(context)

    class StatefulEntries:
        def __init__(self) -> None:
            self.iterations = 0

        def __iter__(self):
            self.iterations += 1
            if self.iterations == 1:
                return iter((group, remedy))
            return iter((group,))

    entries = StatefulEntries()
    revision_hash = service.store.create_revision(  # type: ignore[arg-type]
        context,
        "revision-stateful",
        entries,
    )

    assert entries.iterations == 1
    assert service.store.get_revision_entries(context, "revision-stateful") == (
        group,
        remedy,
    )
    assert len(revision_hash) == 64


def test_concurrent_reference_addition_wins_and_stale_delete_is_atomic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(
        context,
        "draft-1",
        [_group(context), _remedy(context), _pathogen(context)],
    )
    original = service.store._tombstone_managed_entry
    injected = False

    def interleaved(*args: object, **kwargs: object) -> tuple[int, str]:
        nonlocal injected
        if not injected:
            injected = True
            competing = AdminCatalogService(_catalog_store(service.store.db_path))
            competing.update_draft(
                context,
                "draft-1",
                (*_entries(competing, context), _relation(context)),
                expected_version=1,
            )
        return original(*args, **kwargs)

    monkeypatch.setattr(service.store, "_tombstone_managed_entry", interleaved)

    with pytest.raises(DraftConflictError):
        service.delete_remedy(context, "draft-1", "remedy-a", expected_version=1)

    assert service.get_draft(context, "draft-1").version == 2
    assert service.get_remedy(context, "draft-1", "remedy-a").data.get(
        "tombstoned", False
    ) is False


def test_backup_restore_preserves_unpublished_managed_tombstone_authorization(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "source.sqlite3"
    context = _context()
    service = AdminCatalogService(_catalog_store(source_path))
    service.create_draft(context, "draft-1", [_group(context), _remedy(context)])
    service.delete_remedy(context, "draft-1", "remedy-a", expected_version=1)
    backup_root = tmp_path / "backup"

    manifest = create_catalog_backup(source_path, backup_root)
    restored_path = restore_catalog_backup(backup_root, tmp_path / "restored.sqlite3")
    restored = AdminCatalogService(_catalog_store(restored_path))

    assert manifest["catalog_schema_version"] == 8
    assert restored.validate_draft(context, "draft-1").is_valid
    published = restored.publish_draft(
        context, "draft-1", "revision-tombstone", expected_draft_version=2
    )
    assert published.revision_id == "revision-tombstone"


def test_management_does_not_mutate_legacy_remedy_authority(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    authority = Path(__file__).resolve().parents[1] / "data" / "remedies.db"
    before_hash = hashlib.sha256(authority.read_bytes()).hexdigest()
    before_stat = authority.stat()
    service.create_draft(context, "draft-1", [_group(context)])
    service.create_remedy(context, "draft-1", _remedy(context), expected_version=1)
    service.disable_remedy(context, "draft-1", "remedy-a", expected_version=2)

    after_stat = authority.stat()
    assert hashlib.sha256(authority.read_bytes()).hexdigest() == before_hash
    assert (after_stat.st_size, after_stat.st_mtime_ns) == (
        before_stat.st_size,
        before_stat.st_mtime_ns,
    )
    assert service.store.current_revision_id(context) is None
