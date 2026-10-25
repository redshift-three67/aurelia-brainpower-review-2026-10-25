"""Read-only profile shadow adapter for Admin Catalog F3.3.

The selected runtime source always remains the legacy profile authority. Catalog
profiles are read only for an explicit shadow comparison and never replace the
profiles returned for productive use.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Sequence

from core.profile_sync import ProfileDefinition, get_all_profiles

from .contracts import CatalogContext, CatalogEntry, EntryType, normalize_catalog_id
from .store import CatalogStore
from .validation import validate_entries


ADMIN_CATALOG_ENABLED_ENV = "MORPHIC_ADMIN_CATALOG_ENABLED"
_CATALOG_ENABLED_VALUES = frozenset({"1", "on", "true"})
_CATALOG_DISABLED_VALUES = frozenset({"", "0", "false", "off"})


@dataclass(frozen=True, slots=True)
class ShadowProfileDifference:
    kind: str
    profile_name: str
    fields: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ShadowProfileError:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class RuntimeProfileResult:
    mode: str
    selected_source: str
    selected_profiles: tuple[ProfileDefinition, ...]
    catalog_profiles: tuple[ProfileDefinition, ...]
    active_revision_id: str | None
    differences: tuple[ShadowProfileDifference, ...]
    errors: tuple[ShadowProfileError, ...]
    used_legacy_fallback: bool
    productive_mutation: bool = False


class CatalogRuntimeError(RuntimeError):
    """F8.2 catalog runtime consumption failed before any fallback decision."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        active_revision_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.active_revision_id = active_revision_id


class CatalogRuntimeConfigError(CatalogRuntimeError):
    """The explicit F8.3 runtime switch has an unsupported configuration."""


@dataclass(frozen=True, slots=True)
class CatalogRuntimeGroup:
    entry_id: str
    label: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class CatalogRuntimeRemedy:
    entry_id: str
    label: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class CatalogRuntimePathogen:
    entry_id: str
    label: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class CatalogRuntimeRelation:
    entry_id: str
    remedy_id: str
    pathogen_id: str
    priority: int


@dataclass(frozen=True, slots=True)
class CatalogRuntimeMultiplex:
    entry_id: str
    label: str
    group_ids: tuple[str, ...]
    remedy_ids: tuple[str, ...]
    description: str = ""


@dataclass(frozen=True, slots=True)
class CatalogResolvedMultiplex:
    entry_id: str
    label: str
    groups: tuple[CatalogRuntimeGroup, ...]
    remedies: tuple[CatalogRuntimeRemedy, ...]
    description: str = ""


@dataclass(frozen=True, slots=True)
class CatalogRuntimeSnapshot:
    mode: str
    selected_source: str
    active_revision_id: str
    profiles: tuple[ProfileDefinition, ...]
    groups: Mapping[str, CatalogRuntimeGroup]
    remedies: Mapping[str, CatalogRuntimeRemedy]
    pathogens: Mapping[str, CatalogRuntimePathogen]
    remedy_relations: tuple[CatalogRuntimeRelation, ...]
    multiplexes: Mapping[str, CatalogRuntimeMultiplex]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "groups",
            MappingProxyType(dict(sorted(self.groups.items()))),
        )
        object.__setattr__(
            self,
            "remedies",
            MappingProxyType(dict(sorted(self.remedies.items()))),
        )
        object.__setattr__(
            self,
            "pathogens",
            MappingProxyType(dict(sorted(self.pathogens.items()))),
        )
        object.__setattr__(
            self,
            "multiplexes",
            MappingProxyType(dict(sorted(self.multiplexes.items()))),
        )

    def list_groups(self) -> list[str]:
        return sorted(self.groups)

    def generate_group_candidates(
        self,
        group: str,
        seed: str,
        k: int = 32,
    ) -> list[dict[str, object]]:
        selected = _lookup_runtime_record(self.groups, group, "group")
        if k <= 0:
            return []
        return [
            {
                "group": selected.entry_id,
                "label": selected.label,
                "rates": [_catalog_rate(seed, selected.entry_id, index)],
                "source": "catalog_runtime",
            }
            for index in range(k)
        ]

    def generate_fullbody_candidates(
        self,
        groups: list[str],
        seed: str,
        k_total: int = 64,
    ) -> list[dict[str, object]]:
        selected_groups = groups or self.list_groups()
        if k_total <= 0 or not selected_groups:
            return []
        per_group = max(1, k_total // len(selected_groups))
        remainder = max(0, k_total - per_group * len(selected_groups))
        candidates: list[dict[str, object]] = []
        for index, group_id in enumerate(selected_groups):
            extra = 1 if index < remainder else 0
            candidates.extend(
                self.generate_group_candidates(group_id, seed, k=per_group + extra)
            )
        return candidates[:k_total]

    def find_remedies_for_pathogen(
        self,
        pathogen_id: str,
        max_results: int = 5,
    ) -> list[tuple[str, str]]:
        selected_pathogen = _lookup_runtime_record(
            self.pathogens,
            pathogen_id,
            "pathogen",
        )
        normalized_pathogen = normalize_catalog_id(selected_pathogen.entry_id)
        relations = [
            relation
            for relation in self.remedy_relations
            if normalize_catalog_id(relation.pathogen_id) == normalized_pathogen
        ]
        relations.sort(
            key=lambda item: (
                -item.priority,
                self.remedies[item.remedy_id].label,
                item.entry_id,
            )
        )
        return [
            (self.remedies[relation.remedy_id].label, self.remedies[relation.remedy_id].description)
            for relation in relations[:max_results]
        ]

    def find_remedies_for_group(
        self,
        group_name: str,
        max_results: int = 3,
    ) -> list[tuple[str, str]]:
        remedy_ids: list[str] = []
        try:
            multiplex = _lookup_runtime_record(self.multiplexes, group_name, "multiplex")
            remedy_ids.extend(multiplex.remedy_ids)
        except CatalogRuntimeError:
            selected_group = _lookup_runtime_record(self.groups, group_name, "group")
            normalized_group = normalize_catalog_id(selected_group.entry_id)
            for multiplex in self.multiplexes.values():
                if normalized_group in {
                    normalize_catalog_id(group_id) for group_id in multiplex.group_ids
                }:
                    remedy_ids.extend(multiplex.remedy_ids)
        unique_remedy_ids = []
        seen: set[str] = set()
        for remedy_id in remedy_ids:
            normalized = normalize_catalog_id(remedy_id)
            if normalized in seen:
                continue
            seen.add(normalized)
            unique_remedy_ids.append(remedy_id)
        return [
            (self.remedies[remedy_id].label, self.remedies[remedy_id].description)
            for remedy_id in unique_remedy_ids[:max_results]
        ]

    def resolve_multiplex(self, multiplex_id: str) -> CatalogResolvedMultiplex:
        multiplex = _lookup_runtime_record(self.multiplexes, multiplex_id, "multiplex")
        return CatalogResolvedMultiplex(
            entry_id=multiplex.entry_id,
            label=multiplex.label,
            groups=tuple(
                _lookup_runtime_record(self.groups, group_id, "group")
                for group_id in multiplex.group_ids
            ),
            remedies=tuple(
                _lookup_runtime_record(self.remedies, remedy_id, "remedy")
                for remedy_id in multiplex.remedy_ids
            ),
            description=multiplex.description,
        )


@dataclass(frozen=True, slots=True)
class ConfiguredRuntime:
    mode: str
    selected_source: str
    catalog_enabled: bool
    profiles: tuple[ProfileDefinition, ...]
    active_revision_id: str | None
    catalog_snapshot: CatalogRuntimeSnapshot | None
    subgroup_provider: CatalogRuntimeSnapshot | None


def _copy_profile(profile: ProfileDefinition) -> ProfileDefinition:
    return ProfileDefinition(
        name=profile.name,
        display_name=profile.display_name,
        groups=list(profile.groups),
        category=profile.category,
        level=profile.level,
        aliases=list(profile.aliases or ()),
        enabled=profile.enabled,
    )


def _legacy_profiles() -> tuple[ProfileDefinition, ...]:
    return tuple(
        _copy_profile(profile)
        for profile in sorted(get_all_profiles(), key=lambda item: item.name)
    )


def _require_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"profile {field} must be non-empty text")
    return value


def _require_string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, (list, tuple)) or not all(
        isinstance(item, str) and item for item in value
    ):
        raise ValueError(f"profile {field} must be a list of identifiers")
    return list(value)


def _catalog_profile(entry: CatalogEntry) -> ProfileDefinition:
    data = entry.data
    level = data.get("level", 2)
    if isinstance(level, bool) or not isinstance(level, int) or level <= 0:
        raise ValueError("profile level must be a positive integer")
    enabled = data.get("enabled", True)
    if not isinstance(enabled, bool):
        raise ValueError("profile enabled must be boolean")
    return ProfileDefinition(
        name=entry.entry_id,
        display_name=_require_text(data.get("label"), "label"),
        groups=_require_string_list(data.get("group_ids"), "group_ids"),
        category=_require_text(data.get("category"), "category"),
        level=level,
        aliases=_require_string_list(data.get("aliases", ()), "aliases"),
        enabled=enabled,
    )


def _catalog_profiles(
    entries: Sequence[CatalogEntry],
) -> tuple[ProfileDefinition, ...]:
    profiles = []
    for entry in entries:
        if entry.entry_type is not EntryType.PROFILE:
            continue
        if entry.data.get("tombstoned", False) is True:
            continue
        if entry.data.get("enabled", True) is not True:
            continue
        profiles.append(_catalog_profile(entry))
    return tuple(sorted(profiles, key=lambda item: item.name))


def _optional_text(entry: CatalogEntry, field: str) -> str:
    value = entry.data.get(field, "")
    if value == "":
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{entry.entry_type.value} {field} must be text")
    return value


def _runtime_groups(
    entries: Sequence[CatalogEntry],
) -> dict[str, CatalogRuntimeGroup]:
    groups: dict[str, CatalogRuntimeGroup] = {}
    for entry in entries:
        if entry.entry_type is not EntryType.GROUP:
            continue
        if entry.data.get("enabled", True) is not True:
            continue
        groups[entry.entry_id] = CatalogRuntimeGroup(
            entry_id=entry.entry_id,
            label=_require_text(entry.data.get("label"), "label"),
            description=_optional_text(entry, "description"),
        )
    return dict(sorted(groups.items()))


def _runtime_remedies(
    entries: Sequence[CatalogEntry],
) -> dict[str, CatalogRuntimeRemedy]:
    remedies: dict[str, CatalogRuntimeRemedy] = {}
    for entry in entries:
        if entry.entry_type is not EntryType.REMEDY:
            continue
        if entry.data.get("tombstoned", False) is True:
            continue
        if entry.data.get("enabled", True) is not True:
            continue
        remedies[entry.entry_id] = CatalogRuntimeRemedy(
            entry_id=entry.entry_id,
            label=_require_text(entry.data.get("label"), "label"),
            description=_optional_text(entry, "description"),
        )
    return dict(sorted(remedies.items()))


def _runtime_pathogens(
    entries: Sequence[CatalogEntry],
) -> dict[str, CatalogRuntimePathogen]:
    pathogens: dict[str, CatalogRuntimePathogen] = {}
    for entry in entries:
        if entry.entry_type is not EntryType.PATHOGEN:
            continue
        if entry.data.get("enabled", True) is not True:
            continue
        pathogens[entry.entry_id] = CatalogRuntimePathogen(
            entry_id=entry.entry_id,
            label=_require_text(entry.data.get("label"), "label"),
            description=_optional_text(entry, "description"),
        )
    return dict(sorted(pathogens.items()))


def _runtime_relations(
    entries: Sequence[CatalogEntry],
) -> tuple[CatalogRuntimeRelation, ...]:
    relations: list[CatalogRuntimeRelation] = []
    for entry in entries:
        if entry.entry_type is not EntryType.RELATION:
            continue
        if entry.data.get("enabled", True) is not True:
            continue
        relations.append(
            CatalogRuntimeRelation(
                entry_id=entry.entry_id,
                remedy_id=str(entry.data["remedy_id"]),
                pathogen_id=str(entry.data["pathogen_id"]),
                priority=int(entry.data["priority"]),
            )
        )
    return tuple(sorted(relations, key=lambda item: item.entry_id))


def _runtime_multiplexes(
    entries: Sequence[CatalogEntry],
) -> dict[str, CatalogRuntimeMultiplex]:
    multiplexes: dict[str, CatalogRuntimeMultiplex] = {}
    for entry in entries:
        if entry.entry_type is not EntryType.MULTIPLEX:
            continue
        if entry.data.get("tombstoned", False) is True:
            continue
        if entry.data.get("enabled", True) is not True:
            continue
        multiplexes[entry.entry_id] = CatalogRuntimeMultiplex(
            entry_id=entry.entry_id,
            label=_require_text(entry.data.get("label"), "label"),
            group_ids=tuple(str(item) for item in entry.data["group_ids"]),
            remedy_ids=tuple(str(item) for item in entry.data["remedy_ids"]),
            description=_optional_text(entry, "description"),
        )
    return dict(sorted(multiplexes.items()))


def _lookup_runtime_record(
    records: Mapping[str, object],
    record_id: str,
    record_type: str,
):
    normalized = normalize_catalog_id(record_id)
    for candidate_id, record in records.items():
        if normalize_catalog_id(candidate_id) == normalized:
            return record
    raise CatalogRuntimeError(
        "runtime_reference_missing",
        f"{record_type} is not present in the active catalog revision",
    )


def _catalog_rate(seed: str, group_id: str, index: int) -> float:
    digest = hashlib.sha256(f"{seed}|{group_id}|{index}".encode("utf-8")).digest()
    return float(int.from_bytes(digest[:8], "big") % 10_000) / 100.0


def _runtime_snapshot_from_entries(
    active_revision_id: str,
    entries: Sequence[CatalogEntry],
) -> CatalogRuntimeSnapshot:
    return CatalogRuntimeSnapshot(
        mode="catalog_runtime",
        selected_source="catalog",
        active_revision_id=active_revision_id,
        profiles=_catalog_profiles(entries),
        groups=_runtime_groups(entries),
        remedies=_runtime_remedies(entries),
        pathogens=_runtime_pathogens(entries),
        remedy_relations=_runtime_relations(entries),
        multiplexes=_runtime_multiplexes(entries),
    )


def parse_admin_catalog_enabled(
    environ: Mapping[str, str] | None = None,
) -> bool:
    source = os.environ if environ is None else environ
    value = str(source.get(ADMIN_CATALOG_ENABLED_ENV, "")).strip().casefold()
    if value in _CATALOG_DISABLED_VALUES:
        return False
    if value in _CATALOG_ENABLED_VALUES:
        return True
    raise CatalogRuntimeConfigError(
        "invalid_catalog_enabled_value",
        f"{ADMIN_CATALOG_ENABLED_ENV} has an unsupported value",
    )


def _profile_fields(profile: ProfileDefinition) -> dict[str, object]:
    return {
        "aliases": tuple(profile.aliases or ()),
        "category": profile.category,
        "display_name": profile.display_name,
        "enabled": profile.enabled,
        "groups": tuple(profile.groups),
        "level": profile.level,
    }


def _differences(
    legacy_profiles: Sequence[ProfileDefinition],
    catalog_profiles: Sequence[ProfileDefinition],
) -> tuple[ShadowProfileDifference, ...]:
    def index(
        profiles: Sequence[ProfileDefinition],
    ) -> dict[str, ProfileDefinition]:
        indexed: dict[str, ProfileDefinition] = {}
        for profile in profiles:
            normalized_name = normalize_catalog_id(profile.name)
            if normalized_name in indexed:
                raise ValueError("normalized profile identity collision")
            indexed[normalized_name] = profile
        return indexed

    legacy = index(legacy_profiles)
    catalog = index(catalog_profiles)
    differences: list[ShadowProfileDifference] = []
    for normalized_name in sorted(legacy.keys() | catalog.keys()):
        if normalized_name not in legacy:
            profile_name = catalog[normalized_name].name
            differences.append(
                ShadowProfileDifference("catalog_only", profile_name)
            )
            continue
        profile_name = legacy[normalized_name].name
        if normalized_name not in catalog:
            differences.append(ShadowProfileDifference("legacy_only", profile_name))
            continue
        legacy_fields = _profile_fields(legacy[normalized_name])
        catalog_fields = _profile_fields(catalog[normalized_name])
        changed_fields = tuple(
            field
            for field in sorted(legacy_fields)
            if legacy_fields[field] != catalog_fields[field]
        )
        if changed_fields:
            differences.append(
                ShadowProfileDifference("changed", profile_name, changed_fields)
            )
    return tuple(differences)


def _fallback_result(
    legacy_profiles: tuple[ProfileDefinition, ...],
    *,
    active_revision_id: str | None,
    code: str,
    message: str,
) -> RuntimeProfileResult:
    return RuntimeProfileResult(
        mode="shadow",
        selected_source="legacy",
        selected_profiles=legacy_profiles,
        catalog_profiles=(),
        active_revision_id=active_revision_id,
        differences=(),
        errors=(ShadowProfileError(code, message),),
        used_legacy_fallback=True,
    )


def load_runtime_profiles(
    store: CatalogStore,
    context: CatalogContext,
    *,
    shadow_mode: bool = False,
) -> RuntimeProfileResult:
    """Return legacy runtime profiles and optionally compare an active catalog revision."""

    if not isinstance(shadow_mode, bool):
        raise TypeError("shadow_mode must be boolean")
    legacy_profiles = _legacy_profiles()
    if not shadow_mode:
        return RuntimeProfileResult(
            mode="legacy_default",
            selected_source="legacy",
            selected_profiles=legacy_profiles,
            catalog_profiles=(),
            active_revision_id=None,
            differences=(),
            errors=(),
            used_legacy_fallback=False,
        )

    try:
        snapshot = store.current_revision_snapshot(context)
    except Exception:
        return _fallback_result(
            legacy_profiles,
            active_revision_id=None,
            code="catalog_read_failed",
            message="active catalog snapshot could not be read",
        )
    if snapshot is None:
        return _fallback_result(
            legacy_profiles,
            active_revision_id=None,
            code="active_revision_missing",
            message="no active catalog revision exists in the requested context",
        )
    active_revision_id, entries = snapshot
    try:
        if any(entry.context != context for entry in entries):
            raise ValueError("active revision has a foreign embedded context")
        validation = validate_entries(entries)
        if not validation.is_valid:
            raise ValueError("active revision has invalid cross-references")
        catalog_profiles = _catalog_profiles(entries)
    except Exception:
        return _fallback_result(
            legacy_profiles,
            active_revision_id=active_revision_id,
            code="active_revision_invalid",
            message="active catalog revision failed validation",
        )
    try:
        differences = _differences(legacy_profiles, catalog_profiles)
    except Exception:
        return _fallback_result(
            legacy_profiles,
            active_revision_id=active_revision_id,
            code="legacy_diff_invalid",
            message="legacy profile identities cannot be compared safely",
        )
    return RuntimeProfileResult(
        mode="shadow",
        selected_source="legacy",
        selected_profiles=legacy_profiles,
        catalog_profiles=catalog_profiles,
        active_revision_id=active_revision_id,
        differences=differences,
        errors=(),
        used_legacy_fallback=False,
    )


def load_catalog_runtime_snapshot(
    store: CatalogStore,
    context: CatalogContext,
) -> CatalogRuntimeSnapshot:
    """Load the F8.2 catalog runtime view from one active revision.

    This is the first explicit catalog-consumption boundary. It does not choose
    a fallback source. Callers that opt into this function must treat any error
    as fail-closed.
    """

    try:
        snapshot = store.current_revision_snapshot(context)
    except Exception as exc:
        raise CatalogRuntimeError(
            "catalog_read_failed",
            "active catalog snapshot could not be read",
        ) from exc
    if snapshot is None:
        raise CatalogRuntimeError(
            "active_revision_missing",
            "no active catalog revision exists in the requested context",
        )
    active_revision_id, entries = snapshot
    try:
        if any(entry.context != context for entry in entries):
            raise ValueError("active catalog revision has a foreign context")
        validation = validate_entries(entries)
        if not validation.is_valid:
            raise ValueError("active catalog revision has invalid references")
        return _runtime_snapshot_from_entries(str(active_revision_id), entries)
    except CatalogRuntimeError:
        raise
    except Exception as exc:
        raise CatalogRuntimeError(
            "active_revision_invalid",
            "active catalog revision failed validation",
            active_revision_id=str(active_revision_id),
        ) from exc


def load_configured_runtime(
    store: CatalogStore,
    context: CatalogContext,
    *,
    environ: Mapping[str, str] | None = None,
) -> ConfiguredRuntime:
    """Apply the explicit F8.3 kill switch and return one runtime choice."""

    if not parse_admin_catalog_enabled(environ):
        return ConfiguredRuntime(
            mode="legacy_default",
            selected_source="legacy",
            catalog_enabled=False,
            profiles=_legacy_profiles(),
            active_revision_id=None,
            catalog_snapshot=None,
            subgroup_provider=None,
        )
    catalog_snapshot = load_catalog_runtime_snapshot(store, context)
    return ConfiguredRuntime(
        mode="catalog_runtime",
        selected_source="catalog",
        catalog_enabled=True,
        profiles=tuple(_copy_profile(profile) for profile in catalog_snapshot.profiles),
        active_revision_id=catalog_snapshot.active_revision_id,
        catalog_snapshot=catalog_snapshot,
        subgroup_provider=catalog_snapshot,
    )


__all__ = [
    "ADMIN_CATALOG_ENABLED_ENV",
    "CatalogResolvedMultiplex",
    "CatalogRuntimeConfigError",
    "CatalogRuntimeError",
    "CatalogRuntimeGroup",
    "CatalogRuntimeMultiplex",
    "CatalogRuntimePathogen",
    "CatalogRuntimeRelation",
    "CatalogRuntimeRemedy",
    "CatalogRuntimeSnapshot",
    "RuntimeProfileResult",
    "ShadowProfileDifference",
    "ShadowProfileError",
    "load_configured_runtime",
    "load_catalog_runtime_snapshot",
    "load_runtime_profiles",
    "parse_admin_catalog_enabled",
]
