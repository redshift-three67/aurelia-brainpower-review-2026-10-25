"""Read-only normalization of the legacy profile authority for Admin Catalog F3.1.

The adapter exports the already populated ``core.profile_sync`` registry without
mutating it. The duplicated CLI fallback is parsed as static Python data instead
of importing or executing the legacy CLI module.
"""

from __future__ import annotations

import ast
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from core.profile_sync import MASTER_PROFILES, get_all_profiles
from core.subgroups.procedural_groups import list_groups


_EXPORT_SCHEMA_VERSION = 1
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_CLI_FALLBACK_RELATIVE_PATH = Path("apps/cli/profiles/registry.py")


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


@dataclass(frozen=True, slots=True)
class LegacyProfile:
    name: str
    display_name: str
    groups: tuple[str, ...]
    category: str
    level: int
    aliases: tuple[str, ...]
    enabled: bool


@dataclass(frozen=True, slots=True)
class LegacyProfileExport:
    schema_version: int
    authority: str
    profiles: tuple[LegacyProfile, ...]
    aliases: tuple[tuple[str, str], ...]
    referenced_groups: tuple[str, ...]
    unresolved_groups: tuple[str, ...]

    def canonical_json(self) -> str:
        return _canonical_json(asdict(self))

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class LegacyFallbackDrift:
    profile_name: str
    fallback_groups: tuple[str, ...]
    master_groups: tuple[str, ...]
    fallback_only: tuple[str, ...]
    master_only: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class LegacyFallbackInventory:
    source_path: str
    authority: str
    authoritative: bool
    profile_count: int
    referenced_group_count: int
    missing_from_master: tuple[str, ...]
    matching_master: tuple[str, ...]
    drift: tuple[LegacyFallbackDrift, ...]

    def canonical_json(self) -> str:
        return _canonical_json(asdict(self))

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def export_legacy_profiles() -> LegacyProfileExport:
    """Return a deterministic snapshot of active canonical profiles and aliases."""

    aliases = tuple(
        sorted(
            (registry_name, profile.name)
            for registry_name, profile in MASTER_PROFILES.items()
            if registry_name != profile.name
        )
    )
    aliases_by_profile: dict[str, list[str]] = {}
    for alias, canonical_name in aliases:
        aliases_by_profile.setdefault(canonical_name, []).append(alias)

    profiles = tuple(
        LegacyProfile(
            name=profile.name,
            display_name=profile.display_name,
            groups=tuple(profile.groups),
            category=profile.category,
            level=profile.level,
            aliases=tuple(sorted(aliases_by_profile.get(profile.name, []))),
            enabled=profile.enabled,
        )
        for profile in sorted(get_all_profiles(), key=lambda item: item.name)
    )
    referenced_groups = tuple(
        sorted({group for profile in profiles for group in profile.groups})
    )
    available_groups = set(list_groups())
    unresolved_groups = tuple(
        group for group in referenced_groups if group not in available_groups
    )
    return LegacyProfileExport(
        schema_version=_EXPORT_SCHEMA_VERSION,
        authority="core.profile_sync.MASTER_PROFILES",
        profiles=profiles,
        aliases=aliases,
        referenced_groups=referenced_groups,
        unresolved_groups=unresolved_groups,
    )


def _load_cli_fallback(path: Path) -> dict[str, list[str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        value: ast.expr | None = None
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "_PROFILES_DATA"
        ):
            value = node.value
        elif (
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "_PROFILES_DATA"
                for target in node.targets
            )
        ):
            value = node.value
        if value is not None:
            parsed = ast.literal_eval(value)
            if not isinstance(parsed, dict):
                break
            result: dict[str, list[str]] = {}
            for name, groups in parsed.items():
                if not isinstance(name, str) or not isinstance(groups, list) or not all(
                    isinstance(group, str) for group in groups
                ):
                    raise ValueError("CLI legacy profile fallback has an invalid shape")
                result[name] = list(groups)
            return result
    raise ValueError("CLI legacy profile fallback _PROFILES_DATA was not found")


def inventory_cli_legacy_fallback() -> LegacyFallbackInventory:
    """Inventory the duplicate fallback as non-authoritative static source data."""

    fallback_path = _PROJECT_ROOT / _CLI_FALLBACK_RELATIVE_PATH
    fallback = _load_cli_fallback(fallback_path)
    missing: list[str] = []
    matching: list[str] = []
    drift: list[LegacyFallbackDrift] = []
    for profile_name, fallback_group_list in sorted(fallback.items()):
        master = MASTER_PROFILES.get(profile_name)
        if master is None:
            missing.append(profile_name)
            continue
        master_groups = tuple(master.groups)
        fallback_groups = tuple(fallback_group_list)
        if fallback_groups == master_groups:
            matching.append(profile_name)
            continue
        drift.append(
            LegacyFallbackDrift(
                profile_name=profile_name,
                fallback_groups=fallback_groups,
                master_groups=master_groups,
                fallback_only=tuple(sorted(set(fallback_groups) - set(master_groups))),
                master_only=tuple(sorted(set(master_groups) - set(fallback_groups))),
            )
        )
    return LegacyFallbackInventory(
        source_path=_CLI_FALLBACK_RELATIVE_PATH.as_posix(),
        authority="cli_legacy_fallback",
        authoritative=False,
        profile_count=len(fallback),
        referenced_group_count=len(
            {group for groups in fallback.values() for group in groups}
        ),
        missing_from_master=tuple(missing),
        matching_master=tuple(matching),
        drift=tuple(drift),
    )


__all__ = [
    "LegacyFallbackDrift",
    "LegacyFallbackInventory",
    "LegacyProfile",
    "LegacyProfileExport",
    "export_legacy_profiles",
    "inventory_cli_legacy_fallback",
]
