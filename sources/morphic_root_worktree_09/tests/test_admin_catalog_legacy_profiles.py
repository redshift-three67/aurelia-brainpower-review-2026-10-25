from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from core.admin_catalog.legacy_profile_adapter import (
    _load_cli_fallback,
    export_legacy_profiles,
    inventory_cli_legacy_fallback,
)
from core.profile_sync import MASTER_PROFILES, get_all_profiles


EXPECTED_ALIASES = {
    "emf_stoerfelder_detailliert": "strahlung_detailliert",
    "meridiane_tcm_detailliert": "chakren_meridiane",
    "psyche_emotion_detailliert": "psyche_detailliert",
    "urogenital_detailliert": "niere_detailliert",
    "zaehne_kiefer_detailliert": "zahn_detailliert",
}
EXPECTED_FALLBACK_MISSING = ("homeopathy_classical", "hormone_stoffwechsel_detailliert")
EXPECTED_FALLBACK_MATCHING = ("bindegewebe_faszien",)
EXPECTED_FALLBACK_DRIFT = (
    "emf_stoerfelder_detailliert",
    "gehirn_detailliert",
    "immunsystem_detailliert",
    "lymphsystem_detailliert",
    "medikamenten_toxizitaet",
    "meridiane_tcm_detailliert",
    "mitochondrien_dysfunktion",
    "nahrungsmittel_intoleranzen",
    "pestizide_herbizide",
    "psyche_emotion_detailliert",
    "vergiftung_komplett",
    "zaehne_kiefer_detailliert",
)


def _master_snapshot() -> tuple[tuple[str, int, str], ...]:
    return tuple(
        sorted(
            (
                key,
                id(profile),
                json.dumps(
                    {
                        "aliases": list(profile.aliases or []),
                        "category": profile.category,
                        "display_name": profile.display_name,
                        "enabled": profile.enabled,
                        "groups": list(profile.groups),
                        "level": profile.level,
                        "name": profile.name,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            )
            for key, profile in MASTER_PROFILES.items()
        )
    )


def test_export_contains_all_active_profiles_aliases_and_resolved_groups() -> None:
    exported = export_legacy_profiles()

    assert exported.schema_version == 1
    assert exported.authority == "core.profile_sync.MASTER_PROFILES"
    assert len(exported.profiles) == 502
    assert dict(exported.aliases) == EXPECTED_ALIASES
    assert len(exported.referenced_groups) == 449
    assert exported.unresolved_groups == ()
    assert all(profile.enabled is True for profile in exported.profiles)


def test_export_is_sorted_and_repeated_exports_are_byte_and_hash_stable() -> None:
    first = export_legacy_profiles()
    second = export_legacy_profiles()
    first_bytes = first.canonical_json().encode("utf-8")
    second_bytes = second.canonical_json().encode("utf-8")

    assert tuple(profile.name for profile in first.profiles) == tuple(
        sorted(profile.name for profile in first.profiles)
    )
    assert first_bytes == second_bytes
    assert first.sha256 == hashlib.sha256(first_bytes).hexdigest()
    assert first.sha256 == second.sha256


def test_export_preserves_profile_fields_and_alias_relationships() -> None:
    exported = export_legacy_profiles()
    by_name = {profile.name: profile for profile in exported.profiles}

    canonical = by_name["strahlung_detailliert"]
    assert canonical.display_name
    assert canonical.category
    assert canonical.level >= 1
    assert canonical.groups
    assert canonical.aliases == ("emf_stoerfelder_detailliert",)
    assert dict(exported.aliases)["emf_stoerfelder_detailliert"] == canonical.name


def test_export_is_field_exact_for_every_active_profile() -> None:
    exported = export_legacy_profiles()
    aliases_by_profile: dict[str, list[str]] = {}
    for alias, canonical_name in sorted(
        (key, profile.name)
        for key, profile in MASTER_PROFILES.items()
        if key != profile.name
    ):
        aliases_by_profile.setdefault(canonical_name, []).append(alias)
    source_profiles = sorted(get_all_profiles(), key=lambda profile: profile.name)

    assert len(exported.profiles) == len(source_profiles) == 502
    for normalized, source in zip(exported.profiles, source_profiles, strict=True):
        assert normalized.name == source.name
        assert normalized.display_name == source.display_name
        assert normalized.groups == tuple(source.groups)
        assert normalized.category == source.category
        assert normalized.level == source.level
        assert normalized.aliases == tuple(aliases_by_profile.get(source.name, []))
        assert normalized.enabled is source.enabled


def test_export_does_not_mutate_master_profiles() -> None:
    before = _master_snapshot()

    export_legacy_profiles()
    export_legacy_profiles()

    assert _master_snapshot() == before


def test_cli_fallback_is_separate_non_authoritative_drift_inventory() -> None:
    inventory = inventory_cli_legacy_fallback()

    assert inventory.source_path == "apps/cli/profiles/registry.py"
    assert inventory.authority == "cli_legacy_fallback"
    assert inventory.authoritative is False
    assert inventory.profile_count == 15
    assert inventory.referenced_group_count == 146
    assert inventory.missing_from_master == EXPECTED_FALLBACK_MISSING
    assert inventory.matching_master == EXPECTED_FALLBACK_MATCHING
    assert tuple(item.profile_name for item in inventory.drift) == EXPECTED_FALLBACK_DRIFT
    assert all(item.fallback_groups != item.master_groups for item in inventory.drift)


def test_fallback_inventory_is_deterministic_and_does_not_mutate_sources() -> None:
    registry_path = Path("apps/cli/profiles/registry.py")
    registry_hash_before = hashlib.sha256(registry_path.read_bytes()).hexdigest()
    master_before = _master_snapshot()

    first = inventory_cli_legacy_fallback()
    second = inventory_cli_legacy_fallback()

    assert first.canonical_json() == second.canonical_json()
    assert first.sha256 == second.sha256
    assert hashlib.sha256(registry_path.read_bytes()).hexdigest() == registry_hash_before
    assert _master_snapshot() == master_before


def test_cli_fallback_ast_loader_never_executes_registry_module(tmp_path: Path) -> None:
    module_name = "apps.cli.profiles.registry"
    module_before = sys.modules.get(module_name)
    sentinel = tmp_path / "executed.txt"
    registry = tmp_path / "registry.py"
    registry.write_text(
        "from pathlib import Path\n"
        f"Path({str(sentinel)!r}).write_text('executed', encoding='utf-8')\n"
        "raise RuntimeError('registry module must never execute')\n"
        "_PROFILES_DATA: dict[str, list[str]] = {'safe': ['group-a']}\n",
        encoding="utf-8",
    )

    loaded = _load_cli_fallback(registry)

    assert loaded == {"safe": ["group-a"]}
    assert sentinel.exists() is False
    assert sys.modules.get(module_name) is module_before


def test_adapter_has_no_productive_runtime_cli_or_engine_wiring() -> None:
    root = Path(__file__).resolve().parents[1]
    consumers = []
    import_marker = "core.admin_catalog.legacy_profile_adapter"
    for path in root.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        if import_marker in path.read_text(encoding="utf-8", errors="ignore"):
            consumers.append(path.relative_to(root).as_posix())

    assert consumers == ["tests/test_admin_catalog_legacy_profiles.py"]
