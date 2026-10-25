from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from core.admin_catalog.contracts import CatalogContext, CatalogEntry, EntryType
from core.admin_catalog.store import CatalogStore
from core.profile_sync import ProfileDefinition
from services.subgroup_service import SubgroupService


def _runtime_module():
    return importlib.import_module(
        ".".join(("core", "admin_catalog", "runtime" + "_adapter"))
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
) -> CatalogEntry:
    return CatalogEntry(
        entry_type=entry_type,
        entry_id=entry_id,
        context=context,
        source_id="synthetic-runtime-consumption",
        provenance="f8.2-test",
        data=data,
    )


def _group(
    context: CatalogContext,
    entry_id: str = "group-a",
    *,
    enabled: bool = True,
) -> CatalogEntry:
    return _entry(
        context,
        EntryType.GROUP,
        entry_id,
        {"description": "Group A runtime description", "enabled": enabled, "label": "Group A"},
    )


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
            "label": "Catalog Profile",
            "level": 2,
        },
    )


def _remedy(context: CatalogContext, entry_id: str = "remedy-a") -> CatalogEntry:
    return _entry(
        context,
        EntryType.REMEDY,
        entry_id,
        {
            "description": "Remedy A indication",
            "enabled": True,
            "label": "Remedy A",
        },
    )


def _pathogen(context: CatalogContext, entry_id: str = "pathogen-a") -> CatalogEntry:
    return _entry(
        context,
        EntryType.PATHOGEN,
        entry_id,
        {
            "description": "Pathogen A indication",
            "enabled": True,
            "label": "Pathogen A",
        },
    )


def _relation(
    context: CatalogContext,
    entry_id: str = "relation-a",
    *,
    priority: int = 7,
    remedy_id: str = "remedy-a",
    pathogen_id: str = "pathogen-a",
) -> CatalogEntry:
    return _entry(
        context,
        EntryType.RELATION,
        entry_id,
        {
            "enabled": True,
            "pathogen_id": pathogen_id,
            "priority": priority,
            "relation_type": "remedy_pathogen",
            "remedy_id": remedy_id,
        },
    )


def _multiplex(context: CatalogContext, entry_id: str = "multiplex-a") -> CatalogEntry:
    return _entry(
        context,
        EntryType.MULTIPLEX,
        entry_id,
        {
            "description": "Multiplex A runtime description",
            "enabled": True,
            "group_ids": ["group-a"],
            "label": "Multiplex A",
            "remedy_ids": ["remedy-a"],
        },
    )


def _runtime_entries(context: CatalogContext) -> list[CatalogEntry]:
    return [
        _group(context),
        _profile(context),
        _remedy(context),
        _pathogen(context),
        _relation(context),
        _multiplex(context),
    ]


def _activate(
    store: CatalogStore,
    context: CatalogContext,
    revision_id: str,
    entries: list[CatalogEntry],
    *,
    expected_previous_revision_id: str | None = None,
    expected_activation_version: int = 0,
) -> None:
    store.create_revision(context, revision_id, entries)
    store.activate_revision(
        context,
        revision_id,
        expected_previous_revision_id=expected_previous_revision_id,
        expected_activation_version=expected_activation_version,
        actor_id="runtime-consumption-test",
        reason=f"activate {revision_id} for F8.2 runtime consumption",
    )


def test_catalog_runtime_snapshot_projects_all_domains_from_one_active_revision(
    tmp_path: Path,
) -> None:
    runtime = _runtime_module()
    context = _context()
    store = CatalogStore(tmp_path / "catalog.db")
    _activate(store, context, "revision-a", _runtime_entries(context))

    snapshot = runtime.load_catalog_runtime_snapshot(store, context)

    assert snapshot.mode == "catalog_runtime"
    assert snapshot.selected_source == "catalog"
    assert snapshot.active_revision_id == "revision-a"
    assert tuple(profile.name for profile in snapshot.profiles) == ("profile-a",)
    assert snapshot.profiles[0].groups == ["group-a"]
    assert tuple(snapshot.list_groups()) == ("group-a",)
    assert snapshot.groups["group-a"].label == "Group A"
    assert snapshot.remedies["remedy-a"].label == "Remedy A"
    assert snapshot.pathogens["pathogen-a"].label == "Pathogen A"
    assert snapshot.remedy_relations[0].remedy_id == "remedy-a"
    assert snapshot.multiplexes["multiplex-a"].group_ids == ("group-a",)
    assert snapshot.multiplexes["multiplex-a"].remedy_ids == ("remedy-a",)


def test_catalog_runtime_snapshot_resolves_remedies_and_multiplexes_from_revision(
    tmp_path: Path,
) -> None:
    runtime = _runtime_module()
    context = _context()
    store = CatalogStore(tmp_path / "catalog.db")
    _activate(store, context, "revision-a", _runtime_entries(context))

    snapshot = runtime.load_catalog_runtime_snapshot(store, context)

    assert snapshot.find_remedies_for_pathogen("pathogen-a", max_results=3) == [
        ("Remedy A", "Remedy A indication")
    ]
    assert snapshot.find_remedies_for_group("multiplex-a", max_results=3) == [
        ("Remedy A", "Remedy A indication")
    ]
    assert snapshot.resolve_multiplex("multiplex-a").label == "Multiplex A"
    assert snapshot.resolve_multiplex("multiplex-a").groups[0].label == "Group A"
    assert snapshot.resolve_multiplex("multiplex-a").remedies[0].label == "Remedy A"


def test_catalog_runtime_snapshot_fails_closed_without_active_revision(
    tmp_path: Path,
) -> None:
    runtime = _runtime_module()

    with pytest.raises(runtime.CatalogRuntimeError) as caught:
        runtime.load_catalog_runtime_snapshot(
            CatalogStore(tmp_path / "catalog.db"),
            _context(),
        )

    assert caught.value.code == "active_revision_missing"
    assert caught.value.active_revision_id is None


def test_catalog_runtime_snapshot_rejects_invalid_revision_without_legacy_fallback() -> None:
    runtime = _runtime_module()
    context = _context()

    class InvalidSnapshotStore:
        def current_revision_snapshot(
            self, requested: CatalogContext
        ) -> tuple[str, tuple[CatalogEntry, ...]]:
            assert requested == context
            return "revision-invalid", (_group(context, enabled=False), _profile(context))

    with pytest.raises(runtime.CatalogRuntimeError) as caught:
        runtime.load_catalog_runtime_snapshot(
            InvalidSnapshotStore(),  # type: ignore[arg-type]
            context,
        )

    assert caught.value.code == "active_revision_invalid"
    assert caught.value.active_revision_id == "revision-invalid"
    assert "legacy" not in str(caught.value).casefold()


def test_catalog_runtime_snapshot_uses_one_atomic_active_snapshot_read() -> None:
    runtime = _runtime_module()
    context = _context()
    entries = tuple(_runtime_entries(context))

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

    snapshot = runtime.load_catalog_runtime_snapshot(
        AtomicSnapshotStore(),  # type: ignore[arg-type]
        context,
    )

    assert snapshot.active_revision_id == "revision-atomic"
    assert tuple(snapshot.list_groups()) == ("group-a",)


def test_catalog_runtime_snapshot_keeps_process_snapshots_revision_stable(
    tmp_path: Path,
) -> None:
    runtime = _runtime_module()
    context = _context()
    store = CatalogStore(tmp_path / "catalog.db")
    _activate(store, context, "revision-a", _runtime_entries(context))
    first = runtime.load_catalog_runtime_snapshot(store, context)

    changed_entries = [
        _group(context),
        _profile(context),
        _remedy(context),
        _remedy(context, "remedy-b"),
        _pathogen(context),
        _relation(context, remedy_id="remedy-b"),
        _multiplex(context),
    ]
    changed_entries[-1] = _entry(
        context,
        EntryType.MULTIPLEX,
        "multiplex-a",
        {
            "enabled": True,
            "group_ids": ["group-a"],
            "label": "Multiplex A",
            "remedy_ids": ["remedy-b"],
        },
    )
    _activate(
        store,
        context,
        "revision-b",
        changed_entries,
        expected_previous_revision_id="revision-a",
        expected_activation_version=1,
    )
    second = runtime.load_catalog_runtime_snapshot(store, context)

    assert first.active_revision_id == "revision-a"
    assert tuple(first.remedies) == ("remedy-a",)
    assert second.active_revision_id == "revision-b"
    assert tuple(second.remedies) == ("remedy-a", "remedy-b")
    assert second.multiplexes["multiplex-a"].remedy_ids == ("remedy-b",)


def test_subgroup_service_uses_injected_catalog_provider_for_groups_and_candidates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class CatalogProvider:
        def list_groups(self) -> list[str]:
            return ["catalog-group"]

        def generate_group_candidates(
            self, group: str, seed: str, k: int = 32
        ) -> list[dict[str, object]]:
            return [{"group": group, "label": seed, "rates": [float(k)]}]

        def generate_fullbody_candidates(
            self, groups: list[str], seed: str, k_total: int = 64
        ) -> list[dict[str, object]]:
            return [{"groups": tuple(groups), "label": seed, "rates": [float(k_total)]}]

    monkeypatch.setattr(
        "services.subgroup_service.procedural_groups.list_groups",
        lambda: (_ for _ in ()).throw(AssertionError("legacy group list used")),
    )
    monkeypatch.setattr(
        "services.subgroup_service.procedural_groups.generate_candidates_for_group",
        lambda group, seed, k=32: (_ for _ in ()).throw(
            AssertionError("legacy candidates used")
        ),
    )

    service = SubgroupService(catalog_provider=CatalogProvider())

    assert service.list_groups() == ["catalog-group"]
    assert service.generate_group_candidates("catalog-group", "seed", k=2) == [
        {"group": "catalog-group", "label": "seed", "rates": [2.0]}
    ]
    assert service.generate_fullbody_candidates(["catalog-group"], "seed", k_total=5) == [
        {"groups": ("catalog-group",), "label": "seed", "rates": [5.0]}
    ]


@pytest.mark.parametrize("raw_value", [None, "", "0", "false", "off", " FALSE "])
def test_catalog_kill_switch_disabled_values_keep_legacy_without_catalog_read(
    monkeypatch: pytest.MonkeyPatch,
    raw_value: str | None,
) -> None:
    runtime = _runtime_module()
    context = _context()
    environ = {} if raw_value is None else {"MORPHIC_ADMIN_CATALOG_ENABLED": raw_value}
    monkeypatch.setattr(
        runtime,
        "get_all_profiles",
        lambda: [
            ProfileDefinition(
                name="legacy-a",
                display_name="Legacy A",
                groups=["legacy-group"],
                category="legacy",
                level=1,
                aliases=[],
                enabled=True,
            )
        ],
    )

    class ExplodingStore:
        def current_revision_snapshot(self, requested: CatalogContext) -> None:
            raise AssertionError("disabled catalog switch must not read catalog")

    selected = runtime.load_configured_runtime(
        ExplodingStore(),  # type: ignore[arg-type]
        context,
        environ=environ,
    )

    assert selected.mode == "legacy_default"
    assert selected.selected_source == "legacy"
    assert selected.catalog_enabled is False
    assert selected.active_revision_id is None
    assert selected.catalog_snapshot is None
    assert selected.subgroup_provider is None
    assert tuple(profile.name for profile in selected.profiles) == ("legacy-a",)


@pytest.mark.parametrize("raw_value", ["1", "true", "on", " TRUE "])
def test_catalog_kill_switch_enabled_values_load_catalog_runtime_snapshot(
    raw_value: str,
    tmp_path: Path,
) -> None:
    runtime = _runtime_module()
    context = _context()
    store = CatalogStore(tmp_path / "catalog.db")
    _activate(store, context, "revision-a", _runtime_entries(context))

    selected = runtime.load_configured_runtime(
        store,
        context,
        environ={"MORPHIC_ADMIN_CATALOG_ENABLED": raw_value},
    )

    assert selected.mode == "catalog_runtime"
    assert selected.selected_source == "catalog"
    assert selected.catalog_enabled is True
    assert selected.active_revision_id == "revision-a"
    assert selected.catalog_snapshot is selected.subgroup_provider
    assert tuple(profile.name for profile in selected.profiles) == ("profile-a",)
    assert selected.subgroup_provider.list_groups() == ["group-a"]


@pytest.mark.parametrize("raw_value", ["yes", "2", "maybe", "falsey"])
def test_catalog_kill_switch_rejects_unknown_values_before_runtime_access(
    monkeypatch: pytest.MonkeyPatch,
    raw_value: str,
) -> None:
    runtime = _runtime_module()
    monkeypatch.setattr(
        runtime,
        "get_all_profiles",
        lambda: (_ for _ in ()).throw(AssertionError("legacy fallback used")),
    )

    class ExplodingStore:
        def current_revision_snapshot(self, requested: CatalogContext) -> None:
            raise AssertionError("invalid catalog switch must not read catalog")

    with pytest.raises(runtime.CatalogRuntimeConfigError) as caught:
        runtime.load_configured_runtime(
            ExplodingStore(),  # type: ignore[arg-type]
            _context(),
            environ={"MORPHIC_ADMIN_CATALOG_ENABLED": raw_value},
        )

    assert caught.value.code == "invalid_catalog_enabled_value"
    assert raw_value not in str(caught.value)


def test_enabled_catalog_missing_revision_fails_closed_without_legacy_fallback(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    runtime = _runtime_module()
    monkeypatch.setattr(
        runtime,
        "get_all_profiles",
        lambda: (_ for _ in ()).throw(AssertionError("legacy fallback used")),
    )

    with pytest.raises(runtime.CatalogRuntimeError) as caught:
        runtime.load_configured_runtime(
            CatalogStore(tmp_path / "catalog.db"),
            _context(),
            environ={"MORPHIC_ADMIN_CATALOG_ENABLED": "on"},
        )

    assert caught.value.code == "active_revision_missing"
    assert "legacy" not in str(caught.value).casefold()


def test_catalog_kill_switch_returns_one_snapshot_for_profiles_and_subgroups(
    tmp_path: Path,
) -> None:
    runtime = _runtime_module()
    context = _context()
    store = CatalogStore(tmp_path / "catalog.db")
    _activate(store, context, "revision-a", _runtime_entries(context))
    selected = runtime.load_configured_runtime(
        store,
        context,
        environ={"MORPHIC_ADMIN_CATALOG_ENABLED": "on"},
    )

    changed_entries = _runtime_entries(context) + [
        _group(context, "group-b"),
        _entry(
            context,
            EntryType.PROFILE,
            "profile-b",
            {
                "category": "test-category",
                "enabled": True,
                "group_ids": ["group-b"],
                "label": "Catalog Profile B",
                "level": 2,
            },
        ),
    ]
    _activate(
        store,
        context,
        "revision-b",
        changed_entries,
        expected_previous_revision_id="revision-a",
        expected_activation_version=1,
    )

    assert selected.active_revision_id == "revision-a"
    assert tuple(profile.name for profile in selected.profiles) == ("profile-a",)
    assert selected.subgroup_provider.list_groups() == ["group-a"]
