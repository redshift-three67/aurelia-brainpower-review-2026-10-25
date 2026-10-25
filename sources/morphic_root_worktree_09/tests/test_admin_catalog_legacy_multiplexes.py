from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path

import pytest

import core.admin_catalog.legacy_multiplex_adapter as legacy_multiplex_adapter
from core.admin_catalog.legacy_multiplex_adapter import (
    LegacyMultiplexAdapterError,
    export_legacy_multiplexes,
)
from core.admin_catalog.legacy_remedy_adapter import export_legacy_remedies
from core.remedy_group_registry import EXPLICIT_REMEDY_GROUPS, is_remedy_group
from core.subgroups import procedural_groups


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REMEDY_DATABASE = PROJECT_ROOT / "data" / "remedies.db"
BAT_SOURCE = PROJECT_ROOT / "core" / "bat_report_aggregator.py"
DEFAULT_CUSTOM_CONFIG = PROJECT_ROOT / "config" / "groups_config.json"
EXPECTED_EXPORT_SHA256 = "ff714fe6f83c2f277248319dcfee7af2351c73d75c467298bb2fb1e869c46bb6"
_DYNAMIC_MULTIPLEX_CATEGORIES = {
    "heel_remedies_multiplex": "homotoxikologie_heel",
    "nutramedix_remedies_multiplex": "phytotherapie_nutramedix",
    "oorep_homeopathy_multiplex": "oorep_homeopathy_multiplex",
    "schuessler_remedies_multiplex": "Kohärente Harmonisierung mit Schüssler-Salzen",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _bat_literals() -> tuple[dict[str, list[tuple[str, str]]], tuple[tuple[str, str], ...]]:
    tree = ast.parse(BAT_SOURCE.read_text(encoding="utf-8"))
    mapping: dict[str, list[tuple[str, str]]] | None = None
    default: tuple[tuple[str, str], ...] | None = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "BAT_REMEDY_MAP"
            for target in node.targets
        ):
            mapping = ast.literal_eval(node.value)
        if isinstance(node, ast.FunctionDef) and node.name == "find_remedies_for_group":
            final_return = node.body[-1]
            assert isinstance(final_return, ast.Return)
            assert isinstance(final_return.value, ast.Subscript)
            default = tuple(tuple(item) for item in ast.literal_eval(final_return.value.value))
    assert mapping is not None
    assert default is not None
    return mapping, default


def _write_custom_config(path: Path, *, multiplexes: dict[str, object], groups: dict[str, object] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "custom_groups": groups or {},
                "custom_multiplexes": multiplexes,
                "group_descriptions": {
                    "spagyrik_multiplex": "Legacy-Laufzeitbeschreibung"
                },
                "last_modified": "2026-07-14T17:15:00",
                "version": "1.0",
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


@pytest.fixture(scope="module")
def production_export():
    return export_legacy_multiplexes(REMEDY_DATABASE)


@pytest.fixture(scope="module")
def remedy_export():
    return export_legacy_remedies(REMEDY_DATABASE)


def test_production_inventory_is_complete_deterministic_and_null_mutating(production_export) -> None:
    source_paths = (
        PROJECT_ROOT / "core" / "subgroups" / "procedural_groups.py",
        PROJECT_ROOT / "core" / "remedy_group_registry.py",
        BAT_SOURCE,
        REMEDY_DATABASE,
    )
    hashes_before = {path: _sha256(path) for path in source_paths}
    labels_before = {
        name: tuple(labels) for name, labels in procedural_groups._GROUP_LABELS.items()
    }
    dynamic_before = tuple(procedural_groups._DYNAMIC_GROUPS)
    explicit_before = frozenset(EXPLICIT_REMEDY_GROUPS)
    config_existed_before = DEFAULT_CUSTOM_CONFIG.exists()
    group_manager_before = sys.modules.get("tools.group_manager")
    bat_module_before = sys.modules.get("core.bat_report_aggregator")

    repeated = export_legacy_multiplexes(REMEDY_DATABASE)

    assert len(production_export.runtime_multiplexes) == 55
    assert len(production_export.explicit_remedy_groups) == 40
    assert production_export.relation_model.relation_count == 4_373
    assert len(production_export.relation_model.relation_catalog_ids) == 4_373
    assert len(production_export.bat_fallback.keyword_entries) == 16
    assert sum(len(item.remedies) for item in production_export.bat_fallback.keyword_entries) == 48
    assert production_export.custom_config.configured is False
    assert production_export.custom_config.multiplexes == ()
    assert production_export.custom_config.custom_group_names == ()
    assert production_export.custom_config.source_sha256 is None
    assert production_export.conflicts == ()
    assert production_export.canonical_json() == repeated.canonical_json()
    assert production_export.sha256 == repeated.sha256
    assert production_export.sha256 == EXPECTED_EXPORT_SHA256

    assert {path: _sha256(path) for path in source_paths} == hashes_before
    assert {
        name: tuple(labels) for name, labels in procedural_groups._GROUP_LABELS.items()
    } == labels_before
    assert tuple(procedural_groups._DYNAMIC_GROUPS) == dynamic_before
    assert frozenset(EXPLICIT_REMEDY_GROUPS) == explicit_before
    assert DEFAULT_CUSTOM_CONFIG.exists() is config_existed_before
    assert sys.modules.get("tools.group_manager") is group_manager_before
    assert sys.modules.get("core.bat_report_aggregator") is bat_module_before


def test_runtime_multiplexes_preserve_every_authority_label_and_classification(
    production_export,
    remedy_export,
) -> None:
    actual = {item.name: item for item in production_export.runtime_multiplexes}
    expected_names = sorted(
        name for name in procedural_groups.list_groups() if "multiplex" in name.casefold()
    )
    assert list(actual) == expected_names

    remedies_by_category: dict[str, list[str]] = {}
    for remedy in remedy_export.remedies:
        if remedy.category is not None:
            remedies_by_category.setdefault(remedy.category, []).append(remedy.name)

    for name in expected_names:
        item = actual[name]
        if name in _DYNAMIC_MULTIPLEX_CATEGORIES:
            expected_labels = tuple(
                sorted(remedies_by_category.get(_DYNAMIC_MULTIPLEX_CATEGORIES[name], []))
            )
            assert item.label_source == "legacy_remedy_database_category"
        else:
            expected_labels = tuple(procedural_groups._GROUP_LABELS[name])
            assert item.label_source == "procedural_group_labels"
        assert item.labels == expected_labels
        assert item.explicit_remedy_group is (name in EXPLICIT_REMEDY_GROUPS)
        assert item.heuristic_remedy_group is is_remedy_group(name)
        assert item.scan_effect == "active_runtime"
        assert item.source_status == "legacy_unprovenanced"


def test_explicit_remedy_and_relation_models_remain_separate_and_exact(
    production_export,
    remedy_export,
) -> None:
    expected_explicit = sorted(EXPLICIT_REMEDY_GROUPS)
    assert [item.name for item in production_export.explicit_remedy_groups] == expected_explicit
    for item in production_export.explicit_remedy_groups:
        assert item.runtime_available is True
        assert item.runtime_multiplex is ("multiplex" in item.name.casefold())
        assert item.source_status == "legacy_unprovenanced"

    relation_model = production_export.relation_model
    assert relation_model.model_type == "remedy_pathogen_relation"
    assert relation_model.scan_effect == "not_consumed_by_scan"
    assert relation_model.source_status == "legacy_unprovenanced"
    assert relation_model.remedy_export_sha256 == remedy_export.sha256
    assert relation_model.relation_catalog_ids == tuple(
        relation.catalog_id for relation in remedy_export.relations
    )


def test_bat_fallback_is_static_non_authoritative_inventory(production_export) -> None:
    expected_mapping, expected_default = _bat_literals()
    actual_mapping = {
        item.keyword: tuple(tuple(pair) for pair in item.remedies)
        for item in production_export.bat_fallback.keyword_entries
    }
    assert actual_mapping == {
        keyword: tuple(tuple(pair) for pair in remedies)
        for keyword, remedies in sorted(expected_mapping.items())
    }
    assert production_export.bat_fallback.default_remedies == expected_default
    assert production_export.bat_fallback.authoritative is False
    assert production_export.bat_fallback.scan_effect == "fallback_only"
    assert production_export.bat_fallback.source_status == "legacy_unprovenanced"
    assert production_export.bat_fallback.source_sha256 == (
        "6b6b9f2536bd838dfe26455460082fae3b1f513e077f7b015623b545e558b6a5"
    )
    assert production_export.bat_fallback.source_sha256 == _sha256(BAT_SOURCE)
    assert production_export.bat_fallback.matcher_sha256 == (
        "a41964d281421cb9f39416220691b0cfed288dd83c5c4ad01ca3bfd28f602c25"
    )


def test_custom_multiplex_is_preserved_but_never_claimed_scan_active(tmp_path: Path) -> None:
    config = tmp_path / "groups_config.json"
    _write_custom_config(
        config,
        groups={
            "custom_basis": {
                "labels": ["Äther", "Ω-Test"],
                "description": "Benutzerdefiniert",
                "created": "2026-07-14T17:10:00",
                "type": "custom",
            }
        },
        multiplexes={
            "Mein Multiplex": {
                "groups": ["custom_basis", "spagyrik_multiplex"],
                "description": "Nur Übersicht",
                "k_total": 512,
                "focus_areas": ["Fokus A"],
                "created": "2026-07-14T17:11:00",
                "type": "custom",
            }
        },
    )
    before = config.read_bytes()

    export = export_legacy_multiplexes(REMEDY_DATABASE, custom_config_path=config)

    assert config.read_bytes() == before
    assert export.custom_config.configured is True
    assert export.custom_config.source_sha256 == hashlib.sha256(before).hexdigest()
    assert export.custom_config.version == "1.0"
    assert export.custom_config.last_modified == "2026-07-14T17:15:00"
    assert export.custom_config.custom_group_names == ("custom_basis",)
    assert [asdict(group) for group in export.custom_config.custom_groups] == [
        {
            "name": "custom_basis",
            "labels": ("Äther", "Ω-Test"),
            "description": "Benutzerdefiniert",
            "created": "2026-07-14T17:10:00",
            "type": "custom",
            "source_status": "legacy_unprovenanced",
        }
    ]
    assert export.custom_config.group_descriptions == (
        ("spagyrik_multiplex", "Legacy-Laufzeitbeschreibung"),
    )
    assert len(export.custom_config.multiplexes) == 1
    item = export.custom_config.multiplexes[0]
    assert asdict(item) == {
        "name": "Mein Multiplex",
        "groups": ("custom_basis", "spagyrik_multiplex"),
        "description": "Nur Übersicht",
        "k_total": 512,
        "focus_areas": ("Fokus A",),
        "created": "2026-07-14T17:11:00",
        "type": "custom",
        "listed_in_groups_overview": True,
        "scan_effect": "no_runtime_effect",
        "source_status": "legacy_unprovenanced",
    }
    assert export.conflicts == ()


def test_custom_conflicts_are_reported_without_overwrite(tmp_path: Path) -> None:
    config = tmp_path / "groups_config.json"
    _write_custom_config(
        config,
        multiplexes={
            "spagyrik_multiplex": {
                "groups": ["missing_custom_group"],
                "description": "Konflikt",
                "k_total": 64,
                "focus_areas": [],
                "created": "2026-07-14T17:12:00",
                "type": "custom",
            },
            "SPAGYRIK_MULTIPLEX": {
                "groups": ["spagyrik_multiplex"],
                "description": "Casefold-Konflikt",
                "k_total": 64,
                "focus_areas": [],
                "created": "2026-07-14T17:13:00",
                "type": "custom",
            },
        },
    )

    export = export_legacy_multiplexes(REMEDY_DATABASE, custom_config_path=config)

    assert len(export.custom_config.multiplexes) == 2
    assert [(item.conflict_type, item.subject, item.reference) for item in export.conflicts] == [
        ("custom_casefold_collision", "spagyrik_multiplex", "SPAGYRIK_MULTIPLEX"),
        ("custom_name_collision", "SPAGYRIK_MULTIPLEX", "spagyrik_multiplex"),
        ("custom_name_collision", "spagyrik_multiplex", "spagyrik_multiplex"),
        ("unknown_group_reference", "spagyrik_multiplex", "missing_custom_group"),
    ]
    assert all(item.scan_effect == "no_runtime_effect" for item in export.custom_config.multiplexes)


def test_group_description_reference_conflicts_are_all_reported(tmp_path: Path) -> None:
    config = tmp_path / "groups_config.json"
    config.write_text(
        json.dumps(
            {
                "custom_groups": {
                    "spagyrik_multiplex": {
                        "labels": ["Custom"],
                        "description": "Kollision",
                        "created": "2026-07-14T17:20:00",
                        "type": "custom",
                    }
                },
                "custom_multiplexes": {},
                "group_descriptions": {
                    "SPAGYRIK_MULTIPLEX": "Case",
                    "missing_group": "Unbekannt",
                    "spagyrik_multiplex": "Exakt aber mehrdeutig",
                },
                "last_modified": "2026-07-14T17:21:00",
                "version": "1.0",
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    export = export_legacy_multiplexes(REMEDY_DATABASE, custom_config_path=config)

    description_conflicts = {
        (item.conflict_type, item.subject, item.reference)
        for item in export.conflicts
        if "description" in item.conflict_type
    }
    assert description_conflicts == {
        ("ambiguous_group_description_reference", "SPAGYRIK_MULTIPLEX", "spagyrik_multiplex|spagyrik_multiplex"),
        ("ambiguous_group_description_reference", "spagyrik_multiplex", "spagyrik_multiplex|spagyrik_multiplex"),
        ("group_description_case_mismatch", "SPAGYRIK_MULTIPLEX", "spagyrik_multiplex"),
        ("group_description_casefold_collision", "spagyrik_multiplex", "SPAGYRIK_MULTIPLEX"),
        ("unknown_group_description_reference", "missing_group", "missing_group"),
    }


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"custom_groups": {}, "custom_multiplexes": {}},
        {
            "custom_groups": {},
            "custom_multiplexes": [],
            "group_descriptions": {},
            "last_modified": "x",
            "version": "1.0",
        },
        {
            "custom_groups": {},
            "custom_multiplexes": {
                "bad": {
                    "groups": [],
                    "description": "",
                    "k_total": True,
                    "focus_areas": [],
                    "created": "x",
                    "type": "custom",
                }
            },
            "group_descriptions": {},
            "last_modified": "x",
            "version": "1.0",
        },
    ],
)
def test_malformed_custom_config_fails_closed_with_stable_redacted_error(
    tmp_path: Path,
    payload: object,
) -> None:
    config = tmp_path / "secret-client-name.json"
    config.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(LegacyMultiplexAdapterError) as caught:
        export_legacy_multiplexes(REMEDY_DATABASE, custom_config_path=config)

    assert str(caught.value) == "legacy custom multiplex config is invalid"
    assert caught.value.__cause__ is None
    assert str(config) not in str(caught.value)


def test_symlinked_custom_config_is_rejected(tmp_path: Path) -> None:
    target = tmp_path / "target.json"
    _write_custom_config(target, multiplexes={})
    link = tmp_path / "link.json"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("Symlinks are unavailable on this Windows host")

    with pytest.raises(
        LegacyMultiplexAdapterError,
        match="legacy custom multiplex config must not be a symlink",
    ):
        export_legacy_multiplexes(REMEDY_DATABASE, custom_config_path=link)


def test_path_swap_during_descriptor_bound_read_is_blocked_or_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "groups_config.json"
    replacement = tmp_path / "replacement.json"
    _write_custom_config(source, multiplexes={})
    _write_custom_config(
        replacement,
        multiplexes={
            "swapped": {
                "groups": ["spagyrik_multiplex"],
                "description": "Darf nicht unbemerkt gelesen werden",
                "k_total": 64,
                "focus_areas": [],
                "created": "2026-07-14T17:30:00",
                "type": "custom",
            }
        },
    )
    real_open = legacy_multiplex_adapter._open_binary_nofollow
    calls = 0
    swap_blocked = False

    @contextmanager
    def adversarial_open(path: Path):
        nonlocal calls, swap_blocked
        calls += 1
        if calls == 2:
            try:
                os.replace(replacement, source)
            except OSError:
                swap_blocked = True
        with real_open(path) as handle:
            yield handle

    monkeypatch.setattr(
        legacy_multiplex_adapter,
        "_open_binary_nofollow",
        adversarial_open,
    )
    rejected = False
    try:
        export_legacy_multiplexes(REMEDY_DATABASE, custom_config_path=source)
    except LegacyMultiplexAdapterError as exc:
        rejected = True
        assert str(exc) == "legacy custom multiplex config is invalid"
        assert exc.__cause__ is None

    assert calls >= 2
    assert swap_blocked or rejected


def test_optional_config_disappearing_after_first_open_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "groups_config.json"
    _write_custom_config(source, multiplexes={})
    real_open = legacy_multiplex_adapter._open_binary_nofollow
    calls = 0

    @contextmanager
    def disappearing_open(path: Path):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise FileNotFoundError("simulated concurrent removal")
        with real_open(path) as handle:
            yield handle

    monkeypatch.setattr(
        legacy_multiplex_adapter,
        "_open_binary_nofollow",
        disappearing_open,
    )
    with pytest.raises(
        LegacyMultiplexAdapterError,
        match="legacy custom multiplex config is invalid",
    ) as caught:
        export_legacy_multiplexes(REMEDY_DATABASE, custom_config_path=source)

    assert calls == 2
    assert caught.value.__cause__ is None


def test_oversized_custom_config_fails_closed(tmp_path: Path) -> None:
    source = tmp_path / "groups_config.json"
    source.write_bytes(b" " * 1_048_577)

    with pytest.raises(
        LegacyMultiplexAdapterError,
        match="legacy custom multiplex config is invalid",
    ) as caught:
        export_legacy_multiplexes(REMEDY_DATABASE, custom_config_path=source)

    assert caught.value.__cause__ is None


def test_symlinked_bat_source_is_rejected(tmp_path: Path) -> None:
    link = tmp_path / "bat-link.py"
    try:
        link.symlink_to(BAT_SOURCE)
    except OSError:
        pytest.skip("Symlinks are unavailable on this Windows host")

    with pytest.raises(
        LegacyMultiplexAdapterError,
        match="legacy BAT fallback source must not be a symlink",
    ):
        export_legacy_multiplexes(REMEDY_DATABASE, bat_source_path=link)


def test_duplicate_custom_json_keys_fail_closed(tmp_path: Path) -> None:
    config = tmp_path / "groups_config.json"
    config.write_text(
        '{"custom_groups":{},"custom_groups":{},"custom_multiplexes":{},'
        '"group_descriptions":{},"last_modified":"x","version":"1.0"}',
        encoding="utf-8",
    )

    with pytest.raises(
        LegacyMultiplexAdapterError,
        match="legacy custom multiplex config is invalid",
    ):
        export_legacy_multiplexes(REMEDY_DATABASE, custom_config_path=config)


def test_malformed_bat_source_fails_closed_without_executing_it(tmp_path: Path) -> None:
    source = tmp_path / "bat.py"
    marker = tmp_path / "executed.txt"
    source.write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('bad')\nBAT_REMEDY_MAP = {{}}\n",
        encoding="utf-8",
    )

    with pytest.raises(
        LegacyMultiplexAdapterError,
        match="legacy BAT fallback source is invalid",
    ) as caught:
        export_legacy_multiplexes(REMEDY_DATABASE, bat_source_path=source)

    assert caught.value.__cause__ is None
    assert not marker.exists()


def test_any_bat_authority_byte_change_fails_closed(tmp_path: Path) -> None:
    source = tmp_path / "bat.py"
    source.write_bytes(BAT_SOURCE.read_bytes() + b"\n# changed authority snapshot\n")

    with pytest.raises(
        LegacyMultiplexAdapterError,
        match="legacy BAT fallback source is invalid",
    ) as caught:
        export_legacy_multiplexes(REMEDY_DATABASE, bat_source_path=source)

    assert caught.value.__cause__ is None


def test_duplicate_bat_declarations_fail_closed(tmp_path: Path) -> None:
    source = tmp_path / "bat.py"
    source.write_text(
        "BAT_REMEDY_MAP = {'a': [('R1', 'D1')]}\n"
        "BAT_REMEDY_MAP = {'b': [('R2', 'D2')]}\n"
        "def find_remedies_for_group(group_name, max_remedies=3):\n"
        "    return [('R1', 'D1')][:max_remedies]\n"
        "def find_remedies_for_group(group_name, max_remedies=3):\n"
        "    return [('R2', 'D2')][:max_remedies]\n",
        encoding="utf-8",
    )

    with pytest.raises(
        LegacyMultiplexAdapterError,
        match="legacy BAT fallback source is invalid",
    ):
        export_legacy_multiplexes(REMEDY_DATABASE, bat_source_path=source)


@pytest.mark.parametrize(
    "extra_source",
    [
        "BAT_REMEDY_MAP: dict = {'b': [('R2', 'D2')]}\n",
        "BAT_REMEDY_MAP += {'b': [('R2', 'D2')]}\n",
        "async def find_remedies_for_group(group_name, max_remedies=3):\n    return []\n",
        "if True:\n    BAT_REMEDY_MAP = {'b': [('R2', 'D2')]}\n",
        "BAT_REMEDY_MAP['b'] = [('R2', 'D2')]\n",
        "def mutate_map():\n    global BAT_REMEDY_MAP\n    BAT_REMEDY_MAP = {}\n",
        "def mutate_map():\n    BAT_REMEDY_MAP['b'] = [('R2', 'D2')]\n",
        "def mutate_map():\n    BAT_REMEDY_MAP.update({'b': [('R2', 'D2')]})\n",
        "def mutate_map():\n    globals()['BAT_REMEDY_MAP'] = {}\n",
        "def decorator(function):\n    return function\n@decorator\ndef decorated():\n    return None\n",
        "def dynamic_default(value=globals()):\n    return value\n",
    ],
)
def test_ambiguous_bat_authority_shapes_fail_closed(
    tmp_path: Path,
    extra_source: str,
) -> None:
    source = tmp_path / "bat.py"
    source.write_text(
        "BAT_REMEDY_MAP = {'a': [('R1', 'D1')]}\n"
        "def find_remedies_for_group(group_name, max_remedies=3):\n"
        "    return [('R1', 'D1')][:max_remedies]\n"
        + extra_source,
        encoding="utf-8",
    )

    with pytest.raises(
        LegacyMultiplexAdapterError,
        match="legacy BAT fallback source is invalid",
    ):
        export_legacy_multiplexes(REMEDY_DATABASE, bat_source_path=source)


def test_adapter_has_no_productive_runtime_cli_engine_or_package_wiring() -> None:
    consumers: list[str] = []
    for path in PROJECT_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        relative = path.relative_to(PROJECT_ROOT).as_posix()
        if relative in {
            "core/admin_catalog/legacy_multiplex_adapter.py",
            "tests/test_admin_catalog_legacy_multiplexes.py",
            "tests/test_admin_catalog_legacy_remedies.py",
        }:
            continue
        if "legacy_multiplex_adapter" in path.read_text(
            encoding="utf-8",
            errors="ignore",
        ):
            consumers.append(relative)

    assert consumers == []
