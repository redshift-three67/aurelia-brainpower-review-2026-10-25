from __future__ import annotations

import hashlib
import importlib
from pathlib import Path

import pytest

from core.admin_catalog.contracts import CatalogContext, CatalogEntry, EntryType
from core.admin_catalog.shadow_comparison import (
    ShadowDiffExpectation,
    ShadowLegacySnapshot,
    ShadowRecord,
    compare_catalog_shadow_to_legacy,
    legacy_shadow_snapshot_from_exports,
)
from core.admin_catalog.store import CatalogStore


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
) -> CatalogEntry:
    return CatalogEntry(
        entry_type=entry_type,
        entry_id=entry_id,
        context=context,
        source_id="synthetic-shadow-comparison",
        provenance="f8.1-test",
        data=data,
    )


def _group(context: CatalogContext, entry_id: str = "group-a") -> CatalogEntry:
    return _entry(context, EntryType.GROUP, entry_id, {"label": "Group A"})


def _profile(context: CatalogContext, entry_id: str = "profile-a") -> CatalogEntry:
    return _entry(
        context,
        EntryType.PROFILE,
        entry_id,
        {
            "aliases": ["profile-alias"],
            "category": "test-category",
            "enabled": True,
            "group_ids": ["group-a"],
            "label": "Profile A",
            "level": 2,
        },
    )


def _remedy(context: CatalogContext, entry_id: str = "remedy-a") -> CatalogEntry:
    return _entry(context, EntryType.REMEDY, entry_id, {"label": "Remedy A"})


def _pathogen(context: CatalogContext, entry_id: str = "pathogen-a") -> CatalogEntry:
    return _entry(context, EntryType.PATHOGEN, entry_id, {"label": "Pathogen A"})


def _relation(context: CatalogContext, priority: int = 1) -> CatalogEntry:
    return _entry(
        context,
        EntryType.RELATION,
        "relation-a",
        {
            "enabled": True,
            "pathogen_id": "pathogen-a",
            "priority": priority,
            "relation_type": "remedy_pathogen",
            "remedy_id": "remedy-a",
        },
    )


def _multiplex(context: CatalogContext, entry_id: str = "multiplex-a") -> CatalogEntry:
    return _entry(
        context,
        EntryType.MULTIPLEX,
        entry_id,
        {
            "enabled": True,
            "group_ids": ["group-a"],
            "label": "Multiplex A",
            "remedy_ids": ["remedy-a"],
        },
    )


def _active_revision(
    store: CatalogStore,
    context: CatalogContext,
    entries: list[CatalogEntry],
    revision_id: str = "revision-a",
) -> None:
    store.create_revision(context, revision_id, entries)
    store.activate_revision(
        context,
        revision_id,
        expected_previous_revision_id=None,
        expected_activation_version=0,
        actor_id="shadow-reviewer",
        reason="F8.1 shadow comparison activation fixture",
    )


def _legacy_snapshot() -> ShadowLegacySnapshot:
    return ShadowLegacySnapshot.from_records(
        profiles=[
            ShadowRecord(
                "profile-a",
                {
                    "aliases": ("profile-alias",),
                    "category": "test-category",
                    "enabled": True,
                    "group_ids": ("group-a",),
                    "label": "Profile A",
                    "level": 2,
                },
            )
        ],
        groups=[ShadowRecord("group-a", {"label": "Group A"})],
        remedies=[ShadowRecord("remedy-a", {"label": "Remedy A"})],
        pathogens=[ShadowRecord("pathogen-a", {"label": "Pathogen A"})],
        remedy_relations=[
            ShadowRecord(
                "relation-a",
                {
                    "enabled": True,
                    "pathogen_id": "pathogen-a",
                    "priority": 1,
                    "relation_type": "remedy_pathogen",
                    "remedy_id": "remedy-a",
                },
            )
        ],
        multiplexes=[
            ShadowRecord(
                "multiplex-a",
                {
                    "enabled": True,
                    "group_ids": ("group-a",),
                    "label": "Multiplex A",
                    "remedy_ids": ("remedy-a",),
                },
            )
        ],
    )


def test_shadow_comparison_is_read_only_and_keeps_legacy_selected(tmp_path: Path) -> None:
    context = _context()
    database_path = tmp_path / "catalog.db"
    store = CatalogStore(database_path)
    _active_revision(
        store,
        context,
        [
            _group(context),
            _profile(context),
            _remedy(context),
            _pathogen(context),
            _relation(context),
            _multiplex(context),
        ],
    )
    database_hash_before = hashlib.sha256(database_path.read_bytes()).hexdigest()

    report = compare_catalog_shadow_to_legacy(store, context, _legacy_snapshot())

    assert report.mode == "shadow_compare"
    assert report.selected_source == "legacy"
    assert report.active_revision_id == "revision-a"
    assert report.productive_runtime_effect is False
    assert report.no_publish is True
    assert report.no_activate is True
    assert report.used_legacy_fallback is False
    assert report.errors == ()
    assert report.differences == ()
    assert report.summary == {
        "blocker": 0,
        "expected": 0,
        "warning": 0,
    }
    assert hashlib.sha256(database_path.read_bytes()).hexdigest() == database_hash_before


def test_shadow_comparison_classifies_all_domain_diffs_deterministically(
    tmp_path: Path,
) -> None:
    context = _context()
    store = CatalogStore(tmp_path / "catalog.db")
    changed_profile = _entry(
        context,
        EntryType.PROFILE,
        "profile-a",
        {
            "aliases": ["profile-alias"],
            "category": "test-category",
            "enabled": True,
            "group_ids": ["group-a"],
            "label": "Profile A changed",
            "level": 2,
        },
    )
    catalog_only_group = _entry(
        context,
        EntryType.GROUP,
        "group-extra",
        {"label": "Group Extra"},
    )
    changed_relation = _relation(context, priority=5)
    _active_revision(
        store,
        context,
        [
            _group(context),
            catalog_only_group,
            changed_profile,
            _remedy(context),
            _pathogen(context),
            changed_relation,
            _multiplex(context),
        ],
    )

    first = compare_catalog_shadow_to_legacy(
        store,
        context,
        _legacy_snapshot(),
        expectations=(
            ShadowDiffExpectation(
                domain="profiles",
                record_id="profile-a",
                kind="changed",
                fields=("label",),
                classification="warning",
                reason="label drift accepted for F8.1 fixture",
            ),
            ShadowDiffExpectation(
                domain="groups",
                record_id="group-extra",
                kind="catalog_only",
                classification="expected",
                reason="catalog-only fixture group",
            ),
        ),
    )
    second = compare_catalog_shadow_to_legacy(
        store,
        context,
        _legacy_snapshot(),
        expectations=first.expectations,
    )

    assert first.differences == second.differences
    assert [(item.domain, item.record_id, item.kind) for item in first.differences] == [
        ("groups", "group-extra", "catalog_only"),
        ("profiles", "profile-a", "changed"),
        ("remedy_relations", "relation-a", "changed"),
    ]
    assert [item.classification for item in first.differences] == [
        "expected",
        "warning",
        "blocker",
    ]
    assert first.differences[1].fields == ("label",)
    assert first.differences[2].fields == ("priority",)
    assert first.summary == {"blocker": 1, "expected": 1, "warning": 1}


def test_shadow_comparison_missing_active_revision_fails_closed(tmp_path: Path) -> None:
    report = compare_catalog_shadow_to_legacy(
        CatalogStore(tmp_path / "catalog.db"),
        _context(),
        _legacy_snapshot(),
    )

    assert report.selected_source == "legacy"
    assert report.active_revision_id is None
    assert report.used_legacy_fallback is True
    assert report.productive_runtime_effect is False
    assert report.differences == ()
    assert tuple(error.code for error in report.errors) == ("active_revision_missing",)


def test_shadow_comparison_rejects_invalid_snapshot_without_diffing() -> None:
    requested = _context()
    foreign = _context("foreign")

    class ForeignSnapshotStore:
        def current_revision_snapshot(
            self, context: CatalogContext
        ) -> tuple[str, tuple[CatalogEntry, ...]]:
            return "revision-foreign", (_group(foreign),)

    report = compare_catalog_shadow_to_legacy(
        ForeignSnapshotStore(),  # type: ignore[arg-type]
        requested,
        _legacy_snapshot(),
    )

    assert report.selected_source == "legacy"
    assert report.active_revision_id == "revision-foreign"
    assert report.used_legacy_fallback is True
    assert report.differences == ()
    assert tuple(error.code for error in report.errors) == ("active_revision_invalid",)
    assert "foreign" not in report.errors[0].message


def test_shadow_comparison_uses_one_atomic_active_snapshot_read() -> None:
    context = _context()
    entries = (
        _group(context),
        _profile(context),
        _remedy(context),
        _pathogen(context),
        _relation(context),
        _multiplex(context),
    )

    class AtomicSnapshotStore:
        def current_revision_snapshot(
            self, requested: CatalogContext
        ) -> tuple[str, tuple[CatalogEntry, ...]]:
            assert requested == context
            return "revision-atomic", entries

        def current_revision_id(self, requested: CatalogContext) -> str | None:
            raise AssertionError("split activation read is forbidden")

        def get_revision_entries(
            self, requested: CatalogContext, revision_id: str
        ) -> tuple[CatalogEntry, ...] | None:
            raise AssertionError("split revision read is forbidden")

    report = compare_catalog_shadow_to_legacy(
        AtomicSnapshotStore(),  # type: ignore[arg-type]
        context,
        _legacy_snapshot(),
    )

    assert report.active_revision_id == "revision-atomic"
    assert report.errors == ()
    assert report.differences == ()


def test_legacy_snapshot_from_exports_projects_all_f8_1_domains() -> None:
    profile_module = importlib.import_module(
        ".".join(("core", "admin_catalog", "legacy_" + "profile_adapter"))
    )
    remedy_module = importlib.import_module(
        ".".join(("core", "admin_catalog", "legacy_" + "remedy_adapter"))
    )
    multiplex_module = importlib.import_module(
        ".".join(("core", "admin_catalog", "legacy_" + "multiplex_adapter"))
    )

    profile_export = profile_module.LegacyProfileExport(
        schema_version=1,
        authority="profile-fixture",
        profiles=(
            profile_module.LegacyProfile(
                name="profile-a",
                display_name="Profile A",
                groups=("group-a",),
                category="test-category",
                level=2,
                aliases=("profile-alias",),
                enabled=True,
            ),
        ),
        aliases=(("profile-alias", "profile-a"),),
        referenced_groups=("group-a",),
        unresolved_groups=(),
    )
    remedy_export = remedy_module.LegacyRemedyExport(
        schema_version=1,
        authority="remedy-fixture",
        source_status="legacy_unprovenanced",
        database_sha256="0" * 64,
        remedies=(
            remedy_module.LegacyRemedy(
                legacy_id=1,
                catalog_id="remedy-a",
                name="Remedy A",
                potency=None,
                category=None,
                indication=None,
                created_at=None,
                legacy_source=None,
                oorep_id=None,
                abbrev=None,
            ),
        ),
        pathogens=(
            remedy_module.LegacyPathogen(
                legacy_id=1,
                catalog_id="pathogen-a",
                name="Pathogen A",
                pathogen_type="virus",
                category=None,
                indication=None,
                created_at=None,
            ),
        ),
        relations=(
            remedy_module.LegacyRemedyPathogenRelation(
                legacy_id=1,
                catalog_id="relation-a",
                pathogen_catalog_id="pathogen-a",
                remedy_catalog_id="remedy-a",
                priority=1,
            ),
        ),
    )
    multiplex_export = multiplex_module.LegacyMultiplexExport(
        schema_version=1,
        authority="multiplex-fixture",
        source_status="legacy_unprovenanced",
        runtime_snapshot_sha256="1" * 64,
        remedy_registry_snapshot_sha256="2" * 64,
        runtime_multiplexes=(
            multiplex_module.LegacyRuntimeMultiplex(
                name="multiplex-a",
                labels=("Group A",),
                label_source="fixture",
                explicit_remedy_group=True,
                heuristic_remedy_group=False,
            ),
        ),
        explicit_remedy_groups=(),
        relation_model=multiplex_module.LegacyRelationModel(
            model_type="remedy_pathogen",
            relation_count=1,
            relation_catalog_ids=("relation-a",),
            remedy_export_sha256=remedy_export.sha256,
        ),
        custom_config=multiplex_module.LegacyCustomConfig(
            configured=False,
            source_sha256=None,
            version=None,
            last_modified=None,
            custom_groups=(),
            group_descriptions=(),
            multiplexes=(),
        ),
        bat_fallback=multiplex_module.LegacyBatFallback(
            keyword_entries=(),
            default_remedies=(),
            source_sha256="3" * 64,
            matcher_sha256="4" * 64,
        ),
        conflicts=(),
    )

    snapshot = legacy_shadow_snapshot_from_exports(
        profiles=profile_export,
        remedies=remedy_export,
        multiplexes=multiplex_export,
    )

    assert snapshot.domain_counts == {
        "groups": 1,
        "multiplexes": 1,
        "pathogens": 1,
        "profiles": 1,
        "remedies": 1,
        "remedy_relations": 1,
    }
    assert snapshot.records_by_domain["profiles"]["profile-a"].payload["label"] == (
        "Profile A"
    )
    assert snapshot.records_by_domain["multiplexes"]["multiplex-a"].payload == {
        "explicit_remedy_group": True,
        "heuristic_remedy_group": False,
        "labels": ("Group A",),
        "label_source": "fixture",
    }


def test_shadow_comparison_module_has_no_productive_consumer_wiring() -> None:
    root = Path(__file__).resolve().parents[1]
    consumers = []
    marker = "shadow_comparison"
    for path in root.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        relative = path.relative_to(root).as_posix()
        if relative in {
            "core/admin_catalog/shadow_comparison.py",
            "tests/test_admin_catalog_shadow_comparison.py",
        }:
            continue
        if marker in path.read_text(encoding="utf-8", errors="ignore"):
            consumers.append(relative)

    assert consumers == []
