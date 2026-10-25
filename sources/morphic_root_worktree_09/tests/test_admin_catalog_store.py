from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from core.admin_catalog.contracts import CatalogContext, CatalogEntry, EntryType
from core.admin_catalog.store import (
    CatalogStore,
    CatalogStoreError,
    ConcurrencyError,
    StoreAccessError,
    _connect_database,
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
    entry_id: str = "group-a",
    *,
    source_id: str = "fixture",
    provenance: str = "synthetic-test",
) -> CatalogEntry:
    return CatalogEntry(
        entry_type=EntryType.GROUP,
        entry_id=entry_id,
        context=context,
        source_id=source_id,
        provenance=provenance,
        data={"label": entry_id, "enabled": True},
    )


def _store(tmp_path: Path, name: str = "catalog.db") -> CatalogStore:
    return CatalogStore(tmp_path / name)


def test_store_requires_an_explicit_database_path() -> None:
    with pytest.raises(TypeError):
        CatalogStore()  # type: ignore[call-arg]


def test_store_closes_write_connections_after_each_operation(tmp_path: Path) -> None:
    store = _store(tmp_path)
    context = _context()
    store.create_draft(context, "draft-1", [_entry(context)])
    store.create_revision(context, "revision-1", [_entry(context)])
    store.activate_revision(
        context,
        "revision-1",
        expected_previous_revision_id=None,
        expected_activation_version=0,
        actor_id="operator-a",
        reason="close contract",
    )

    store.db_path.unlink()

    assert store.db_path.exists() is False


def test_schema_enables_foreign_keys_and_creates_only_f1_tables(tmp_path: Path) -> None:
    store = _store(tmp_path)

    with store.connect_readonly() as connection:
        foreign_keys = connection.execute("PRAGMA foreign_keys").fetchone()[0]
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE 'catalog_%'"
            )
        }

    assert foreign_keys == 1
    assert tables == {
        "catalog_activations",
        "catalog_audit_events",
        "catalog_draft_managed_tombstones",
        "catalog_draft_profile_tombstones",
        "catalog_draft_source_imports",
        "catalog_draft_validation_attestations",
        "catalog_drafts",
        "catalog_revision_entries",
        "catalog_revisions",
    }


def test_drafts_are_context_isolated_even_with_same_id(tmp_path: Path) -> None:
    store = _store(tmp_path)
    context_a = _context("a")
    context_b = _context("b")

    store.create_draft(context_a, "draft-1", [_entry(context_a, "group-a")])
    store.create_draft(context_b, "draft-1", [_entry(context_b, "group-b")])

    assert store.get_draft(context_a, "draft-1")["entry_ids"] == ["group-a"]
    assert store.get_draft(context_b, "draft-1")["entry_ids"] == ["group-b"]
    assert store.get_draft(_context("foreign"), "draft-1") is None


def test_revision_hash_is_order_independent_and_binds_context_source_and_provenance(
    tmp_path: Path,
) -> None:
    context = _context()
    entries = [_entry(context, "group-b"), _entry(context, "group-a")]
    first = _store(tmp_path, "first.db").create_revision(context, "revision-1", entries)
    second = _store(tmp_path, "second.db").create_revision(
        context, "revision-1", list(reversed(entries))
    )
    changed_source = _store(tmp_path, "source.db").create_revision(
        context,
        "revision-1",
        [_entry(context, "group-a", source_id="other"), _entry(context, "group-b")],
    )
    changed_provenance = _store(tmp_path, "provenance.db").create_revision(
        context,
        "revision-1",
        [_entry(context, "group-a", provenance="other"), _entry(context, "group-b")],
    )
    other_context = _context("other")
    changed_context = _store(tmp_path, "context.db").create_revision(
        other_context,
        "revision-1",
        [_entry(other_context, "group-a"), _entry(other_context, "group-b")],
    )

    assert first == second
    assert len({first, changed_source, changed_provenance, changed_context}) == 4


def test_revision_and_revision_entries_are_sql_immutable(tmp_path: Path) -> None:
    store = _store(tmp_path)
    context = _context()
    store.create_revision(context, "revision-1", [_entry(context)])

    with sqlite3.connect(store.db_path) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                "UPDATE catalog_revisions SET payload_hash = ? WHERE revision_id = ?",
                ("changed", "revision-1"),
            )
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                "DELETE FROM catalog_revision_entries WHERE revision_id = ?",
                ("revision-1",),
            )


def test_activation_is_atomic_and_rejects_lost_updates(tmp_path: Path) -> None:
    store = _store(tmp_path)
    context = _context()
    store.create_revision(context, "revision-1", [_entry(context, "group-a")])
    store.create_revision(context, "revision-2", [_entry(context, "group-b")])

    version_1 = store.activate_revision(
        context,
        "revision-1",
        expected_previous_revision_id=None,
        expected_activation_version=0,
        actor_id="operator-a",
        reason="initial activation",
    )
    with pytest.raises(ConcurrencyError):
        store.activate_revision(
            context,
            "revision-2",
            expected_previous_revision_id=None,
            expected_activation_version=0,
            actor_id="operator-a",
            reason="stale activation",
        )

    assert version_1 == 1
    assert store.current_revision_id(context) == "revision-1"
    assert store.audit_event_count(context) == 1

    version_2 = store.activate_revision(
        context,
        "revision-2",
        expected_previous_revision_id="revision-1",
        expected_activation_version=1,
        actor_id="operator-a",
        reason="approved update",
    )
    assert version_2 == 2
    assert store.current_revision_id(context) == "revision-2"
    assert store.audit_event_count(context) == 2


def test_context_cannot_activate_a_foreign_revision(tmp_path: Path) -> None:
    store = _store(tmp_path)
    owner = _context("owner")
    store.create_revision(owner, "revision-1", [_entry(owner)])

    with pytest.raises(StoreAccessError):
        store.activate_revision(
            _context("foreign"),
            "revision-1",
            expected_previous_revision_id=None,
            expected_activation_version=0,
            actor_id="operator-foreign",
            reason="must fail",
        )


def test_rollback_reactivates_without_deleting_revisions(tmp_path: Path) -> None:
    store = _store(tmp_path)
    context = _context()
    store.create_revision(context, "revision-1", [_entry(context, "group-a")])
    store.create_revision(context, "revision-2", [_entry(context, "group-b")])
    store.activate_revision(
        context,
        "revision-1",
        expected_previous_revision_id=None,
        expected_activation_version=0,
        actor_id="operator-a",
        reason="initial",
    )
    store.activate_revision(
        context,
        "revision-2",
        expected_previous_revision_id="revision-1",
        expected_activation_version=1,
        actor_id="operator-a",
        reason="update",
    )

    store.rollback(
        context,
        target_revision_id="revision-1",
        expected_previous_revision_id="revision-2",
        expected_activation_version=2,
        actor_id="operator-a",
        reason="verified rollback",
    )

    assert store.current_revision_id(context) == "revision-1"
    assert store.list_revision_ids(context) == ["revision-1", "revision-2"]
    assert store.audit_event_count(context) == 3


def test_audit_chain_detects_an_unintended_row_change(tmp_path: Path) -> None:
    store = _store(tmp_path)
    context = _context()
    store.create_revision(context, "revision-1", [_entry(context)])
    store.activate_revision(
        context,
        "revision-1",
        expected_previous_revision_id=None,
        expected_activation_version=0,
        actor_id="operator-a",
        reason="initial",
    )
    assert store.verify_audit_chain(context) is True

    with sqlite3.connect(store.db_path) as connection:
        connection.execute(
            "UPDATE catalog_audit_events SET reason = ? WHERE event_id = 1",
            ("tampered",),
        )
        connection.commit()

    assert store.verify_audit_chain(context) is False


def test_foreign_trigger_blocks_activation_without_audit_fragment(tmp_path: Path) -> None:
    store = _store(tmp_path)
    context = _context()
    store.create_revision(context, "revision-1", [_entry(context)])
    with sqlite3.connect(store.db_path) as connection:
        connection.execute(
            """
            CREATE TRIGGER reject_audit_insert
            BEFORE INSERT ON catalog_audit_events
            BEGIN
                SELECT RAISE(ABORT, 'synthetic audit failure');
            END
            """
        )
        connection.commit()

    with pytest.raises(CatalogStoreError, match="schema fingerprint"):
        store.activate_revision(
            context,
            "revision-1",
            expected_previous_revision_id=None,
            expected_activation_version=0,
            actor_id="operator-a",
            reason="must roll back",
        )

    assert store.current_revision_id(context) is None
    assert store.audit_event_count(context) == 0


def test_readonly_connection_handles_uri_reserved_path_characters(tmp_path: Path) -> None:
    store = _store(tmp_path, "catalog%23fixture.db")

    with store.connect_readonly() as connection:
        assert connection.execute("SELECT 1").fetchone()[0] == 1


def test_revision_hash_binds_an_existing_context_local_source_draft(tmp_path: Path) -> None:
    context = _context()
    entry = _entry(context)
    first_store = _store(tmp_path, "draft-a.db")
    first_store.create_draft(context, "draft-a", [entry])
    second_store = _store(tmp_path, "draft-b.db")
    second_store.create_draft(context, "draft-b", [entry])

    first = first_store.create_revision(
        context, "revision-1", [entry], source_draft_id="draft-a"
    )
    second = second_store.create_revision(
        context, "revision-1", [entry], source_draft_id="draft-b"
    )

    assert first != second


def test_revision_rejects_missing_or_foreign_source_drafts(tmp_path: Path) -> None:
    store = _store(tmp_path)
    owner = _context("owner")
    foreign = _context("foreign")
    store.create_draft(owner, "draft-1", [_entry(owner)])

    with pytest.raises(sqlite3.IntegrityError):
        store.create_revision(
            owner,
            "revision-missing",
            [_entry(owner)],
            source_draft_id="missing-draft",
        )
    with pytest.raises(sqlite3.IntegrityError):
        store.create_revision(
            foreign,
            "revision-foreign",
            [_entry(foreign)],
            source_draft_id="draft-1",
        )


def test_finalized_revision_rejects_appended_entries(tmp_path: Path) -> None:
    store = _store(tmp_path)
    context = _context()
    original = _entry(context, "group-a")
    appended = _entry(context, "group-b")
    payload_hash = store.create_revision(context, "revision-1", [original])

    with sqlite3.connect(store.db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                """
                INSERT INTO catalog_revision_entries (
                    operator_id, workspace_id, tenant_id, scope,
                    revision_id, entry_type, entry_id, payload_json, payload_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    context.operator_id,
                    context.workspace_id,
                    context.tenant_id,
                    context.scope,
                    "revision-1",
                    appended.entry_type.value,
                    appended.entry_id,
                    appended.canonical_json(),
                    appended.payload_hash,
                ),
            )

    with store.connect_readonly() as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM catalog_revision_entries WHERE revision_id = ?",
            ("revision-1",),
        ).fetchone()[0]
        stored_hash = connection.execute(
            "SELECT payload_hash FROM catalog_revisions WHERE revision_id = ?",
            ("revision-1",),
        ).fetchone()[0]
    assert count == 1
    assert stored_hash == payload_hash


def test_activation_version_blocks_aba_and_same_pointer_lost_updates(tmp_path: Path) -> None:
    store = _store(tmp_path)
    context = _context()
    store.create_revision(context, "revision-a", [_entry(context, "group-a")])
    store.create_revision(context, "revision-b", [_entry(context, "group-b")])
    store.activate_revision(
        context,
        "revision-a",
        expected_previous_revision_id=None,
        expected_activation_version=0,
        actor_id="operator-a",
        reason="A",
    )
    store.activate_revision(
        context,
        "revision-b",
        expected_previous_revision_id="revision-a",
        expected_activation_version=1,
        actor_id="operator-a",
        reason="B",
    )
    store.activate_revision(
        context,
        "revision-a",
        expected_previous_revision_id="revision-b",
        expected_activation_version=2,
        actor_id="operator-a",
        reason="A again",
    )

    with pytest.raises(ConcurrencyError):
        store.activate_revision(
            context,
            "revision-b",
            expected_previous_revision_id="revision-a",
            expected_activation_version=1,
            actor_id="operator-a",
            reason="stale ABA request",
        )
    with pytest.raises(ConcurrencyError):
        store.activate_revision(
            context,
            "revision-a",
            expected_previous_revision_id="revision-a",
            expected_activation_version=2,
            actor_id="operator-a",
            reason="stale same-pointer request",
        )

    assert store.current_revision_id(context) == "revision-a"
    assert store.audit_event_count(context) == 3


@pytest.mark.parametrize("readonly", [False, True])
def test_connection_is_closed_when_pragma_setup_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, readonly: bool
) -> None:
    store = _store(tmp_path)

    class FailingSetupConnection:
        row_factory: object | None = None
        closed = False

        def execute(self, _statement: str) -> None:
            raise RuntimeError("synthetic pragma failure")

        def close(self) -> None:
            self.closed = True

    connection = FailingSetupConnection()
    monkeypatch.setattr(
        "core.admin_catalog.store.sqlite3.connect",
        lambda *_args, **_kwargs: connection,
    )

    with pytest.raises(RuntimeError, match="synthetic pragma failure"):
        if readonly:
            with store.connect_readonly():
                pass
        else:
            _connect_database(store.db_path)

    assert connection.closed is True


def test_draft_hashes_order_collisions_but_revisions_require_valid_snapshot(
    tmp_path: Path,
) -> None:
    context = _context()
    entries = [_entry(context, "Group-A"), _entry(context, "group-a")]
    first_store = _store(tmp_path, "collision-first.db")
    second_store = _store(tmp_path, "collision-second.db")

    first_draft = first_store.create_draft(context, "draft-1", entries)
    second_draft = second_store.create_draft(
        context, "draft-1", list(reversed(entries))
    )
    assert first_draft == second_draft
    with pytest.raises(CatalogStoreError, match="normalized_id_collision"):
        first_store.create_revision(
            context, "revision-1", entries, source_draft_id="draft-1"
        )
    with pytest.raises(CatalogStoreError, match="normalized_id_collision"):
        second_store.create_revision(
            context,
            "revision-1",
            list(reversed(entries)),
            source_draft_id="draft-1",
        )
    assert first_store.list_revision_ids(context) == []
    assert second_store.list_revision_ids(context) == []


def test_revision_read_detects_entry_hash_tampering(tmp_path: Path) -> None:
    store = _store(tmp_path, "entry-hash-tamper.db")
    context = _context()
    store.create_revision(context, "revision-1", [_entry(context)])
    with sqlite3.connect(store.db_path) as connection:
        connection.execute("DROP TRIGGER catalog_revision_entries_no_update")
        connection.execute(
            "UPDATE catalog_revision_entries SET payload_hash = ? WHERE revision_id = ?",
            ("0" * 64, "revision-1"),
        )
        connection.commit()

    with pytest.raises(StoreAccessError, match="entry payload hash"):
        store.get_revision_entries(context, "revision-1")


def test_revision_read_requires_exact_canonical_entry_json(tmp_path: Path) -> None:
    store = _store(tmp_path, "entry-json-tamper.db")
    context = _context()
    store.create_revision(context, "revision-1", [_entry(context)])
    with sqlite3.connect(store.db_path) as connection:
        connection.execute("DROP TRIGGER catalog_revision_entries_no_update")
        connection.execute(
            """
            UPDATE catalog_revision_entries
            SET payload_json = payload_json || ' '
            WHERE revision_id = ?
            """,
            ("revision-1",),
        )
        connection.commit()

    with pytest.raises(StoreAccessError, match="canonical JSON"):
        store.get_revision_entries(context, "revision-1")


def test_revision_read_detects_embedded_context_and_bundle_tampering(
    tmp_path: Path,
) -> None:
    context = _context()
    foreign = _context("foreign")

    context_store = _store(tmp_path, "context-tamper.db")
    context_store.create_revision(context, "revision-1", [_entry(context)])
    foreign_entry = _entry(foreign)
    with sqlite3.connect(context_store.db_path) as connection:
        connection.execute("DROP TRIGGER catalog_revision_entries_no_update")
        connection.execute(
            """
            UPDATE catalog_revision_entries
            SET payload_json = ?, payload_hash = ?
            WHERE revision_id = ?
            """,
            (foreign_entry.canonical_json(), foreign_entry.payload_hash, "revision-1"),
        )
        connection.commit()
    with pytest.raises(StoreAccessError, match="embedded context"):
        context_store.get_revision_entries(context, "revision-1")

    bundle_store = _store(tmp_path, "bundle-tamper.db")
    original = _entry(context)
    bundle_store.create_revision(context, "revision-1", [original])
    changed = CatalogEntry(
        entry_type=EntryType.GROUP,
        entry_id=original.entry_id,
        context=context,
        source_id=original.source_id,
        provenance=original.provenance,
        data={"label": "changed-label", "enabled": True},
    )
    with sqlite3.connect(bundle_store.db_path) as connection:
        connection.execute("DROP TRIGGER catalog_revision_entries_no_update")
        connection.execute(
            """
            UPDATE catalog_revision_entries
            SET payload_json = ?, payload_hash = ?
            WHERE revision_id = ?
            """,
            (changed.canonical_json(), changed.payload_hash, "revision-1"),
        )
        connection.commit()
    with pytest.raises(StoreAccessError, match="revision payload hash"):
        bundle_store.get_revision_entries(context, "revision-1")


def test_current_revision_snapshot_returns_activation_and_entries_together(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path, "active-snapshot.db")
    context = _context()
    entry = _entry(context)
    store.create_revision(context, "revision-1", [entry])
    store.activate_revision(
        context,
        "revision-1",
        expected_previous_revision_id=None,
        expected_activation_version=0,
        actor_id="reviewer",
        reason="synthetic active snapshot",
    )

    snapshot = store.current_revision_snapshot(context)

    assert snapshot is not None
    revision_id, entries = snapshot
    assert revision_id == "revision-1"
    assert entries == (entry,)
