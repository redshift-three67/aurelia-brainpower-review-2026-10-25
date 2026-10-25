from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from core.admin_catalog.source_policy import (
    SourcePolicyError,
    resolve_local_import_path,
    validate_source_policy_fields,
)
from core.source_registry import SourceRegistry, SourceRegistryError, validate_manifest


def _local_source(local_path: str, **overrides: object) -> dict[str, object]:
    source: dict[str, object] = {
        "id": "admin_notes",
        "label": "Admin Notes",
        "source_type": "local_import",
        "local_path": local_path,
        "license": "admin-provided",
        "trust_level": "admin_curated",
        "import_policy": "manual_review",
        "scopes": ["terminology"],
        "enabled": False,
        "status": "disabled",
    }
    source.update(overrides)
    return source


def test_source_policy_accepts_only_server_defined_values() -> None:
    validate_source_policy_fields(
        {
            "license": "source-specific",
            "trust_level": "official",
            "import_policy": "manual_review",
        }
    )

    for field, value in (
        ("license", "manifest-says-trusted"),
        ("trust_level", "superuser"),
        ("import_policy", "auto_publish"),
    ):
        payload = {
            "license": "source-specific",
            "trust_level": "official",
            "import_policy": "manual_review",
            field: value,
        }
        with pytest.raises(SourcePolicyError, match=field):
            validate_source_policy_fields(payload)


@pytest.mark.parametrize("schema_version", [999, "1", True])
def test_registry_rejects_unknown_explicit_schema_version(
    tmp_path: Path,
    schema_version: object,
) -> None:
    registry_path = tmp_path / "sources.json"
    registry_path.write_text(
        json.dumps({"schema_version": schema_version, "sources": []}),
        encoding="utf-8",
    )

    with pytest.raises(SourceRegistryError, match="schema_version"):
        SourceRegistry.load(registry_path)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("id", 1),
        ("label", ["label"]),
        ("source_type", {"kind": "online_download"}),
        ("status", 1),
        ("scopes", [1]),
        ("warnings", [1]),
        ("endpoint", ["https://example.invalid"]),
    ],
)
def test_source_manifest_rejects_non_string_contract_values(
    tmp_path: Path,
    field: str,
    value: object,
) -> None:
    registry_path = tmp_path / "sources.json"
    source = _local_source(str(tmp_path / "terms"), id="strict-types")
    source[field] = value
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 0,
                "rollback_history": [],
                "sources": [source],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(SourceRegistryError, match="string|scopes|warnings"):
        SourceRegistry.load(registry_path)


def test_registry_rejects_unknown_wrapper_fields_and_duplicate_keys(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    registry_path.write_text("[]", encoding="utf-8")
    with pytest.raises(SourceRegistryError, match="versioned JSON object"):
        SourceRegistry.load(registry_path)

    registry_path.write_text(
        '{"schema_version":1,"sources":[]}',
        encoding="utf-8",
    )
    legacy = SourceRegistry.load(registry_path)
    with pytest.raises(SourceRegistryError, match="read-only|migration"):
        legacy.save()
    with pytest.raises(SourceRegistryError, match="read-only|migrate"):
        legacy.stage_manifest(
            tmp_path / "unused.json",
            tmp_path / "staging",
            approval_id="approval-001",
        )

    registry_path.write_text(
        '{"schema_version":1,"sources":[],"unexpected":true}',
        encoding="utf-8",
    )
    with pytest.raises(SourceRegistryError, match="wrapper fields"):
        SourceRegistry.load(registry_path)

    registry_path.write_text(
        '{"schema_version":1,"schema_version":1,"sources":[]}',
        encoding="utf-8",
    )
    with pytest.raises(SourceRegistryError, match="Duplicate JSON key"):
        SourceRegistry.load(registry_path)


def test_manifest_wrapper_rejects_unknown_fields(tmp_path: Path) -> None:
    payload = {
        "schema_version": 1,
        "source": _local_source("notes"),
        "unexpected": True,
    }
    (tmp_path / "notes").mkdir()
    with pytest.raises(SourceRegistryError, match="wrapper fields"):
        validate_manifest(payload, import_root=tmp_path)


def test_manifest_rejects_unknown_explicit_schema_version(tmp_path: Path) -> None:
    import_root = tmp_path / "imports"
    source_dir = import_root / "notes"
    source_dir.mkdir(parents=True)
    payload = {
        "schema_version": 999,
        "source": _local_source("notes"),
    }

    with pytest.raises(SourceRegistryError, match="schema_version"):
        validate_manifest(payload, import_root=import_root)


def test_manifest_enabled_must_be_a_real_boolean(tmp_path: Path) -> None:
    import_root = tmp_path / "imports"
    (import_root / "notes").mkdir(parents=True)
    payload = _local_source("notes", enabled="false", status="active")

    with pytest.raises(SourceRegistryError, match="enabled|boolean"):
        validate_manifest(payload, import_root=import_root)


def test_local_import_requires_explicit_absolute_existing_root(tmp_path: Path) -> None:
    relative_root = Path("relative-import-root")

    with pytest.raises(SourcePolicyError, match="absolute"):
        resolve_local_import_path("notes", import_root=relative_root)

    missing_root = tmp_path / "missing"
    with pytest.raises(SourcePolicyError, match="exist"):
        resolve_local_import_path("notes", import_root=missing_root)


def test_local_import_path_must_exist_below_configured_root(tmp_path: Path) -> None:
    import_root = tmp_path / "imports"
    source_dir = import_root / "notes"
    source_dir.mkdir(parents=True)

    assert resolve_local_import_path("notes", import_root=import_root) == source_dir.resolve()
    assert resolve_local_import_path(source_dir, import_root=import_root) == source_dir.resolve()

    with pytest.raises(SourcePolicyError, match="exist"):
        resolve_local_import_path("missing", import_root=import_root)

    outside = tmp_path / "outside"
    outside.mkdir()
    with pytest.raises(SourcePolicyError, match="escape|outside"):
        resolve_local_import_path(outside, import_root=import_root)


def test_local_import_rejects_parent_traversal(tmp_path: Path) -> None:
    import_root = tmp_path / "imports"
    import_root.mkdir()
    (tmp_path / "outside").mkdir()

    with pytest.raises(SourcePolicyError, match="traversal|escape"):
        resolve_local_import_path("../outside", import_root=import_root)


def test_local_import_rejects_symlink_escape(tmp_path: Path) -> None:
    import_root = tmp_path / "imports"
    outside = tmp_path / "outside"
    import_root.mkdir()
    outside.mkdir()
    link = import_root / "linked"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlinks unavailable: {exc}")

    with pytest.raises(SourcePolicyError, match="symlink|reparse|escape"):
        resolve_local_import_path("linked", import_root=import_root)


@pytest.mark.skipif(os.name != "nt", reason="Windows junction contract")
def test_local_import_rejects_windows_junction_escape(tmp_path: Path) -> None:
    import_root = tmp_path / "imports"
    outside = tmp_path / "outside"
    import_root.mkdir()
    outside.mkdir()
    junction = import_root / "junction"
    created = subprocess.run(
        ["cmd.exe", "/c", "mklink", "/J", str(junction), str(outside)],
        capture_output=True,
        check=False,
    )
    if created.returncode != 0:
        pytest.skip("Windows junction creation unavailable")
    try:
        with pytest.raises(SourcePolicyError, match="symlink|reparse|escape"):
            resolve_local_import_path("junction", import_root=import_root)
    finally:
        junction.rmdir()


def test_validate_local_manifest_returns_canonical_policy_bound_path(tmp_path: Path) -> None:
    import_root = tmp_path / "imports"
    source_dir = import_root / "notes"
    source_dir.mkdir(parents=True)

    source = validate_manifest(_local_source("notes"), import_root=import_root)

    assert source.local_path == str(source_dir.resolve())
