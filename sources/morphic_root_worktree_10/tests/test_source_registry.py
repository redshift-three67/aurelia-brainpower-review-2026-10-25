import json
from pathlib import Path

import pytest

from core.source_registry import SourceRegistry, SourceRegistryError


def _write_registry(path: Path, sources: list[dict[str, object]]) -> None:
    path.write_text(
        json.dumps({"schema_version": 1, "sources": sources}, indent=2),
        encoding="utf-8",
    )


def _source(source_id: str, **overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "id": source_id,
        "label": f"Source {source_id}",
        "description": "Test source",
        "source_type": "online_api",
        "homepage": "https://example.org",
        "endpoint": "https://example.org/api",
        "license": "test",
        "trust_level": "official",
        "import_policy": "manual",
        "scopes": ["terminology"],
        "enabled": False,
        "status": "disabled",
    }
    data.update(overrides)
    return data


def test_default_registry_contains_safe_domain_sources() -> None:
    registry = SourceRegistry.load_default()
    sources = registry.list_sources()
    source_ids = {source.id for source in sources}

    assert "nlm_mesh" in source_ids
    assert "nccih_acupuncture" in source_ids
    assert "ema_hmpc_herbal_monographs" in source_ids
    assert "clark_frequencies_legacy" in source_ids

    assert registry.get("nlm_mesh").enabled is True
    assert registry.get("nlm_mesh").status == "active"
    assert registry.get("clark_frequencies_legacy").enabled is False
    assert registry.get("clark_frequencies_legacy").status == "quarantined"


def test_registry_can_enable_disable_active_safe_sources(tmp_path: Path) -> None:
    path = tmp_path / "sources.json"
    _write_registry(path, [_source("nlm_mesh")])

    registry = SourceRegistry.load(path)
    registry.enable_source("nlm_mesh")

    enabled = SourceRegistry.load(path).get("nlm_mesh")
    assert enabled.enabled is True
    assert enabled.status == "active"

    registry = SourceRegistry.load(path)
    registry.disable_source("nlm_mesh")

    disabled = SourceRegistry.load(path).get("nlm_mesh")
    assert disabled.enabled is False
    assert disabled.status == "disabled"


def test_registry_rejects_non_https_online_sources(tmp_path: Path) -> None:
    path = tmp_path / "sources.json"
    _write_registry(path, [_source("unsafe", endpoint="http://example.org/api")])

    with pytest.raises(SourceRegistryError, match="https"):
        SourceRegistry.load(path)


def test_quarantined_sources_require_explicit_override(tmp_path: Path) -> None:
    path = tmp_path / "sources.json"
    _write_registry(path, [_source("rife_legacy", status="quarantined")])

    registry = SourceRegistry.load(path)
    with pytest.raises(SourceRegistryError, match="quarantined"):
        registry.enable_source("rife_legacy")

    registry.enable_source("rife_legacy", allow_quarantined=True)
    enabled = SourceRegistry.load(path).get("rife_legacy")
    assert enabled.enabled is True
    assert enabled.status == "active"

    registry = SourceRegistry.load(path)
    registry.disable_source("rife_legacy")
    disabled = SourceRegistry.load(path).get("rife_legacy")
    assert disabled.enabled is False
    assert disabled.status == "quarantined"


def test_admin_can_import_local_repository_manifest(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    _write_registry(registry_path, [])
    manifest_path = tmp_path / "admin_source.json"
    manifest_path.write_text(
        json.dumps(
            {
                "id": "admin_tcm_notes",
                "label": "Admin TCM Notes",
                "description": "Curated local notes",
                "source_type": "local_import",
                "local_path": str(tmp_path / "tcm_notes"),
                "license": "admin",
                "trust_level": "admin_curated",
                "import_policy": "manual_review",
                "scopes": ["tcm", "acupuncture"],
                "enabled": False,
                "status": "disabled",
            }
        ),
        encoding="utf-8",
    )

    registry = SourceRegistry.load(registry_path)
    imported = registry.import_manifest(manifest_path)

    assert imported.id == "admin_tcm_notes"
    assert SourceRegistry.load(registry_path).get("admin_tcm_notes").source_type == "local_import"


def test_registry_plans_replace_import_without_writing(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    _write_registry(registry_path, [_source("nlm_mesh", label="NLM MeSH")])
    manifest_path = tmp_path / "nlm_mesh.json"
    manifest_path.write_text(
        json.dumps(_source("nlm_mesh", label="NLM MeSH Updated")),
        encoding="utf-8",
    )

    registry = SourceRegistry.load(registry_path)
    plan = registry.plan_import_manifest(manifest_path, replace=True)

    assert plan.action == "replace"
    assert plan.source.id == "nlm_mesh"
    assert plan.changed_fields["label"] == {
        "current": "NLM MeSH",
        "incoming": "NLM MeSH Updated",
    }
    assert SourceRegistry.load(registry_path).get("nlm_mesh").label == "NLM MeSH"


def test_registry_stages_normalized_manifest_without_promoting(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    _write_registry(registry_path, [])
    manifest_path = tmp_path / "admin_source.json"
    manifest_path.write_text(
        json.dumps(
            _source(
                "admin_notes",
                source_type="local_import",
                local_path=str(tmp_path / "notes"),
                endpoint="",
            )
        ),
        encoding="utf-8",
    )

    registry = SourceRegistry.load(registry_path)
    staged_path = registry.stage_manifest(manifest_path, tmp_path / "staging")

    staged = json.loads(staged_path.read_text(encoding="utf-8"))
    assert staged["source"]["id"] == "admin_notes"
    assert staged["source"]["source_type"] == "local_import"
    assert SourceRegistry.load(registry_path).list_sources() == []


def test_registry_import_can_be_rolled_back_by_batch_snapshot(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    rollback_dir = tmp_path / "rollbacks"
    _write_registry(registry_path, [_source("nlm_mesh", label="NLM MeSH")])
    manifest_path = tmp_path / "nlm_mesh.json"
    manifest_path.write_text(
        json.dumps(_source("nlm_mesh", label="NLM MeSH Updated")),
        encoding="utf-8",
    )

    registry = SourceRegistry.load(registry_path)
    registry.import_manifest(
        manifest_path,
        replace=True,
        rollback_dir=rollback_dir,
        batch_id="batch-001",
    )
    assert SourceRegistry.load(registry_path).get("nlm_mesh").label == "NLM MeSH Updated"

    SourceRegistry.load(registry_path).rollback_import("batch-001", rollback_dir=rollback_dir)

    restored = SourceRegistry.load(registry_path)
    assert restored.get("nlm_mesh").label == "NLM MeSH"
