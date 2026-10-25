from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from core.admin_catalog.contracts import CatalogContext, CatalogEntry, EntryType
from core.admin_catalog.runtime_adapter import load_runtime_profiles
from core.admin_catalog.store import CatalogStore
from core.profile_sync import MASTER_PROFILES, ProfileDefinition, get_all_profiles


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
        source_id="synthetic-runtime-adapter",
        provenance="f3.3-test",
        data=data,
    )


def _group(context: CatalogContext, entry_id: str = "group-a") -> CatalogEntry:
    return _entry(
        context,
        EntryType.GROUP,
        entry_id,
        {"label": entry_id, "enabled": True},
    )


def _profile(
    context: CatalogContext,
    entry_id: str = "catalog-profile",
    *,
    level: object = 3,
    enabled: bool = True,
    tombstoned: bool = False,
) -> CatalogEntry:
    data: dict[str, object] = {
        "aliases": [f"{entry_id}-alias"],
        "category": "synthetic-category",
        "enabled": enabled,
        "group_ids": ["group-a"],
        "label": "Catalog Profile",
        "level": level,
    }
    if tombstoned:
        data["tombstoned"] = True
    return _entry(context, EntryType.PROFILE, entry_id, data)


def _activate(
    store: CatalogStore,
    context: CatalogContext,
    revision_id: str,
    entries: list[CatalogEntry],
) -> None:
    store.create_revision(context, revision_id, entries)
    store.activate_revision(
        context,
        revision_id,
        expected_previous_revision_id=None,
        expected_activation_version=0,
        actor_id="synthetic-reviewer",
        reason="F3.3 synthetic activation",
    )


def _legacy_signature() -> tuple[tuple[object, ...], ...]:
    return tuple(
        (
            profile.name,
            profile.display_name,
            tuple(profile.groups),
            profile.category,
            profile.level,
            tuple(profile.aliases or ()),
            profile.enabled,
        )
        for profile in sorted(get_all_profiles(), key=lambda item: item.name)
    )


def _master_identity_snapshot() -> tuple[tuple[str, int], ...]:
    return tuple(sorted((key, id(value)) for key, value in MASTER_PROFILES.items()))


def test_shadow_mode_requires_an_explicit_boolean() -> None:
    with pytest.raises(TypeError, match="shadow_mode must be boolean"):
        load_runtime_profiles(
            object(),  # type: ignore[arg-type]
            _context(),
            shadow_mode=1,  # type: ignore[arg-type]
        )


def test_default_mode_is_legacy_and_does_not_read_catalog() -> None:
    class ExplodingStore:
        def current_revision_id(self, context: CatalogContext) -> str | None:
            raise AssertionError("default mode must not inspect the catalog")

    before = _master_identity_snapshot()
    result = load_runtime_profiles(
        ExplodingStore(),  # type: ignore[arg-type]
        _context(),
    )

    assert result.mode == "legacy_default"
    assert result.selected_source == "legacy"
    assert result.active_revision_id is None
    assert result.catalog_profiles == ()
    assert result.differences == ()
    assert result.errors == ()
    assert result.used_legacy_fallback is False
    assert result.productive_mutation is False
    assert tuple(
        (
            profile.name,
            profile.display_name,
            tuple(profile.groups),
            profile.category,
            profile.level,
            tuple(profile.aliases or ()),
            profile.enabled,
        )
        for profile in result.selected_profiles
    ) == _legacy_signature()
    authorities = sorted(get_all_profiles(), key=lambda item: item.name)
    assert len(result.selected_profiles) == len(authorities)
    for selected, authority in zip(result.selected_profiles, authorities, strict=True):
        assert selected is not authority
        assert selected.groups is not authority.groups
        if authority.aliases is not None:
            assert selected.aliases is not authority.aliases
    legacy_before_mutating_result = _legacy_signature()
    result.selected_profiles[0].groups.append("synthetic-detachment-check")
    if result.selected_profiles[0].aliases is not None:
        result.selected_profiles[0].aliases.append("synthetic-detachment-alias")
    assert _legacy_signature() == legacy_before_mutating_result
    assert _master_identity_snapshot() == before


def test_shadow_mode_maps_active_profiles_but_keeps_legacy_selected(tmp_path: Path) -> None:
    context = _context()
    database_path = tmp_path / "catalog.db"
    store = CatalogStore(database_path)
    _activate(
        store,
        context,
        "revision-a",
        [
            _group(context),
            _profile(context),
            _profile(context, "disabled-profile", enabled=False),
        ],
    )
    database_hash_before = hashlib.sha256(database_path.read_bytes()).hexdigest()
    master_before = _master_identity_snapshot()
    legacy_before = _legacy_signature()

    result = load_runtime_profiles(store, context, shadow_mode=True)

    assert result.mode == "shadow"
    assert result.selected_source == "legacy"
    assert result.active_revision_id == "revision-a"
    assert result.used_legacy_fallback is False
    assert result.errors == ()
    assert result.productive_mutation is False
    assert tuple(profile.name for profile in result.catalog_profiles) == (
        "catalog-profile",
    )
    mapped = result.catalog_profiles[0]
    assert mapped.display_name == "Catalog Profile"
    assert mapped.groups == ["group-a"]
    assert mapped.category == "synthetic-category"
    assert mapped.level == 3
    assert mapped.aliases == ["catalog-profile-alias"]
    assert mapped.enabled is True
    assert any(
        difference.kind == "catalog_only"
        and difference.profile_name == "catalog-profile"
        for difference in result.differences
    )
    assert tuple(profile.name for profile in result.selected_profiles) == tuple(
        profile.name for profile in sorted(get_all_profiles(), key=lambda item: item.name)
    )
    assert hashlib.sha256(database_path.read_bytes()).hexdigest() == database_hash_before
    assert _master_identity_snapshot() == master_before
    assert _legacy_signature() == legacy_before


def test_shadow_mode_missing_active_revision_falls_back_visibly(tmp_path: Path) -> None:
    result = load_runtime_profiles(
        CatalogStore(tmp_path / "catalog.db"),
        _context(),
        shadow_mode=True,
    )

    assert result.selected_source == "legacy"
    assert result.catalog_profiles == ()
    assert result.used_legacy_fallback is True
    assert tuple(error.code for error in result.errors) == ("active_revision_missing",)
    assert result.differences == ()


def test_shadow_mode_defective_active_revision_falls_back_visibly(tmp_path: Path) -> None:
    class DefectiveStore:
        def current_revision_snapshot(
            self, context: CatalogContext
        ) -> tuple[str, tuple[CatalogEntry, ...]] | None:
            raise ValueError("corrupt revision payload")

    result = load_runtime_profiles(
        DefectiveStore(),  # type: ignore[arg-type]
        _context(),
        shadow_mode=True,
    )

    assert result.selected_source == "legacy"
    assert result.active_revision_id is None
    assert result.catalog_profiles == ()
    assert result.used_legacy_fallback is True
    assert tuple(error.code for error in result.errors) == (
        "catalog_read_failed",
    )
    assert result.errors[0].message == "active catalog snapshot could not be read"
    assert "corrupt revision payload" not in result.errors[0].message
    assert result.differences == ()


def test_shadow_differences_are_deterministic_and_field_specific(tmp_path: Path) -> None:
    context = _context()
    store = CatalogStore(tmp_path / "catalog.db")
    legacy = next(
        profile
        for profile in sorted(get_all_profiles(), key=lambda item: item.name)
        if (
            profile.groups
            and not profile.aliases
            and profile.name.casefold()
            not in {group_id.casefold() for group_id in profile.groups}
        )
    )
    changed = _entry(
        context,
        EntryType.PROFILE,
        legacy.name.swapcase(),
        {
            "aliases": list(legacy.aliases or ()),
            "category": legacy.category,
            "enabled": True,
            "group_ids": list(legacy.groups),
            "label": f"{legacy.display_name} changed",
            "level": legacy.level,
        },
    )
    _activate(
        store,
        context,
        "revision-diff",
        [_group(context, group_id) for group_id in legacy.groups] + [changed],
    )

    first = load_runtime_profiles(store, context, shadow_mode=True)
    second = load_runtime_profiles(store, context, shadow_mode=True)

    assert first.differences == second.differences
    changed_diff = next(
        item
        for item in first.differences
        if item.kind == "changed" and item.profile_name == legacy.name
    )
    assert changed_diff.fields == ("display_name",)
    assert not any(
        item.profile_name.casefold() == legacy.name.casefold()
        and item.kind in {"catalog_only", "legacy_only"}
        for item in first.differences
    )
    assert first.selected_source == "legacy"


@pytest.mark.parametrize("defect", ["foreign_context", "unknown_reference"])
def test_shadow_mode_rejects_context_and_cross_reference_defects(defect: str) -> None:
    requested = _context()
    foreign = _context("foreign")
    if defect == "foreign_context":
        entries = (_group(foreign), _profile(foreign))
    else:
        entries = (_profile(requested),)

    class DefectiveSnapshotStore:
        def current_revision_snapshot(
            self, context: CatalogContext
        ) -> tuple[str, tuple[CatalogEntry, ...]] | None:
            return "revision-defective", entries

    result = load_runtime_profiles(
        DefectiveSnapshotStore(),  # type: ignore[arg-type]
        requested,
        shadow_mode=True,
    )

    assert result.selected_source == "legacy"
    assert result.catalog_profiles == ()
    assert result.used_legacy_fallback is True
    assert tuple(error.code for error in result.errors) == (
        "active_revision_invalid",
    )
    assert result.errors[0].message == "active catalog revision failed validation"


def test_shadow_mode_uses_one_atomic_active_snapshot_read() -> None:
    context = _context()
    entries = (_group(context), _profile(context))

    class AtomicSnapshotStore:
        def current_revision_snapshot(
            self, requested: CatalogContext
        ) -> tuple[str, tuple[CatalogEntry, ...]] | None:
            assert requested == context
            return "revision-atomic", entries

        def current_revision_id(self, requested: CatalogContext) -> str | None:
            raise AssertionError("split activation read is forbidden")

        def get_revision_entries(
            self, requested: CatalogContext, revision_id: str
        ) -> tuple[CatalogEntry, ...] | None:
            raise AssertionError("split revision read is forbidden")

    result = load_runtime_profiles(
        AtomicSnapshotStore(),  # type: ignore[arg-type]
        context,
        shadow_mode=True,
    )

    assert result.active_revision_id == "revision-atomic"
    assert tuple(profile.name for profile in result.catalog_profiles) == (
        "catalog-profile",
    )
    assert result.errors == ()


def test_shadow_mode_excludes_a_valid_tombstone_snapshot() -> None:
    context = _context()
    tombstone = _profile(context, enabled=False, tombstoned=True)

    class TombstoneSnapshotStore:
        def current_revision_snapshot(
            self, requested: CatalogContext
        ) -> tuple[str, tuple[CatalogEntry, ...]] | None:
            return "revision-tombstone", (_group(context), tombstone)

    result = load_runtime_profiles(
        TombstoneSnapshotStore(),  # type: ignore[arg-type]
        context,
        shadow_mode=True,
    )

    assert result.active_revision_id == "revision-tombstone"
    assert result.catalog_profiles == ()
    assert result.used_legacy_fallback is False
    assert result.errors == ()


@pytest.mark.parametrize("legacy_defect", ["invalid_id", "normalized_collision"])
def test_shadow_diff_legacy_identity_defects_fall_back_safely(
    monkeypatch: pytest.MonkeyPatch,
    legacy_defect: str,
) -> None:
    context = _context()
    if legacy_defect == "invalid_id":
        profiles = [
            ProfileDefinition(
                name="legacy profile",
                display_name="Legacy Profile",
                groups=["group-a"],
                category="synthetic",
                level=1,
                aliases=[],
                enabled=True,
            )
        ]
    else:
        profiles = [
            ProfileDefinition(
                name=name,
                display_name=name,
                groups=["group-a"],
                category="synthetic",
                level=1,
                aliases=[],
                enabled=True,
            )
            for name in ("Legacy-A", "legacy-a")
        ]
    monkeypatch.setattr(
        "core.admin_catalog.runtime_adapter.get_all_profiles",
        lambda: profiles,
    )

    class SnapshotStore:
        def current_revision_snapshot(
            self, requested: CatalogContext
        ) -> tuple[str, tuple[CatalogEntry, ...]] | None:
            return "revision-a", (_group(context), _profile(context))

    result = load_runtime_profiles(
        SnapshotStore(),  # type: ignore[arg-type]
        context,
        shadow_mode=True,
    )

    assert result.selected_source == "legacy"
    assert tuple(profile.name for profile in result.selected_profiles) == tuple(
        sorted(profile.name for profile in profiles)
    )
    assert result.catalog_profiles == ()
    assert result.differences == ()
    assert result.used_legacy_fallback is True
    assert tuple(error.code for error in result.errors) == (
        "legacy_diff_invalid",
    )
    assert (
        result.errors[0].message
        == "legacy profile identities cannot be compared safely"
    )


def test_runtime_adapter_has_only_approved_consumer_wiring() -> None:
    root = Path(__file__).resolve().parents[1]
    consumers = []
    import_marker = "runtime_adapter"
    approved_consumers = {
        "core/admin_catalog/runtime_acceptance.py",
        "apps/web/admin_catalog.py",
        "tests/test_web_admin_catalog_runtime_acceptance.py",
    }
    for path in root.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        relative = path.relative_to(root).as_posix()
        if relative in {
            "core/admin_catalog/runtime_adapter.py",
            "tests/test_admin_catalog_runtime_adapter.py",
            *approved_consumers,
        }:
            continue
        if import_marker in path.read_text(encoding="utf-8", errors="ignore"):
            consumers.append(relative)

    assert consumers == []
