import json
from pathlib import Path

import pytest

from core.source_registry import SourceRegistry, SourceRegistryError, _sha256_json


def _write_registry(path: Path, sources: list[dict[str, object]]) -> None:
    path.write_text(
        json.dumps(
            {"schema_version": 1, "revision": 0, "rollback_history": [], "sources": sources},
            indent=2,
        ),
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
        "license": "source-specific",
        "trust_level": "official",
        "import_policy": "manual_review",
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


def test_registry_rejects_non_mapping_source_entries_with_registry_error(
    tmp_path: Path,
) -> None:
    path = tmp_path / "sources.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 0,
                "rollback_history": [],
                "sources": [1],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(SourceRegistryError, match="must be an object"):
        SourceRegistry.load(path)


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


def test_deprecated_source_state_is_terminal(tmp_path: Path) -> None:
    path = tmp_path / "sources.json"
    _write_registry(
        path,
        [_source("old_source", enabled=False, status="deprecated")],
    )
    registry = SourceRegistry.load(path)

    with pytest.raises(SourceRegistryError, match="deprecated"):
        registry.enable_source("old_source")
    with pytest.raises(SourceRegistryError, match="deprecated|terminal"):
        registry.disable_source("old_source")

    reloaded = SourceRegistry.load(path).get("old_source")
    assert reloaded.status == "deprecated"
    assert reloaded.enabled is False


@pytest.mark.parametrize(
    ("current_state", "incoming_state", "extra", "match"),
    [
        (
            {"enabled": False, "status": "deprecated"},
            {"enabled": True, "status": "active"},
            {},
            "deprecated",
        ),
        (
            {"enabled": False, "status": "quarantined"},
            {"enabled": True, "status": "active"},
            {"return_status_on_disable": "quarantined"},
            "enabled/status|lifecycle",
        ),
    ],
)
def test_manifest_replacement_cannot_bypass_lifecycle_state(
    tmp_path: Path,
    current_state: dict[str, object],
    incoming_state: dict[str, object],
    extra: dict[str, object],
    match: str,
) -> None:
    path = tmp_path / "sources.json"
    manifest_path = tmp_path / "source.json"
    current = _source("guarded", **current_state, **extra)
    incoming = _source("guarded", **incoming_state)
    _write_registry(path, [current])
    manifest_path.write_text(json.dumps(incoming), encoding="utf-8")

    with pytest.raises(SourceRegistryError, match=match):
        SourceRegistry.load(path).plan_import_manifest(manifest_path, replace=True)


def test_registry_rejects_disabled_active_lifecycle_contradiction(tmp_path: Path) -> None:
    path = tmp_path / "sources.json"
    _write_registry(path, [_source("contradictory", enabled=False, status="active")])

    with pytest.raises(SourceRegistryError, match="enabled/status|true/active"):
        SourceRegistry.load(path)


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
    import_root = tmp_path / "imports"
    (import_root / "tcm_notes").mkdir(parents=True)
    manifest_path.write_text(
        json.dumps(
            {
                "id": "admin_tcm_notes",
                "label": "Admin TCM Notes",
                "description": "Curated local notes",
                "source_type": "local_import",
                "local_path": "tcm_notes",
                "license": "admin-provided",
                "trust_level": "experimental_unverified",
                "import_policy": "reference_only",
                "scopes": ["tcm", "acupuncture"],
                "enabled": False,
                "status": "disabled",
            }
        ),
        encoding="utf-8",
    )

    registry = SourceRegistry.load(registry_path)
    staged_path = registry.stage_manifest(
        manifest_path,
        tmp_path / "staging",
        import_root=import_root,
        approval_id="approval-001",
    )
    imported = registry.import_manifest(staged_path)

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


def test_new_source_manifest_cannot_self_assign_importable_policy(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "self-promoted.json"
    _write_registry(registry_path, [])
    manifest_path.write_text(json.dumps(_source("self_promoted")), encoding="utf-8")

    with pytest.raises(SourceRegistryError, match="server-owned|least-privilege|policy"):
        SourceRegistry.load(registry_path).plan_import_manifest(manifest_path)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("source_type", "online_download"),
        ("license", "admin-provided"),
        ("trust_level", "experimental_unverified"),
        ("import_policy", "reference_only"),
    ),
)
def test_replacement_manifest_cannot_change_server_owned_policy(
    tmp_path: Path,
    field: str,
    value: str,
) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "replacement.json"
    _write_registry(registry_path, [_source("nlm_mesh")])
    incoming = _source("nlm_mesh")
    incoming[field] = value
    manifest_path.write_text(json.dumps(incoming), encoding="utf-8")

    with pytest.raises(SourceRegistryError, match="server-owned|policy"):
        SourceRegistry.load(registry_path).plan_import_manifest(manifest_path, replace=True)


def test_final_import_rechecks_server_owned_policy_against_forged_stage(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "least-privilege.json"
    _write_registry(registry_path, [])
    manifest_path.write_text(
        json.dumps(
            _source(
                "new_reference",
                trust_level="experimental_unverified",
                import_policy="reference_only",
            )
        ),
        encoding="utf-8",
    )
    registry = SourceRegistry.load(registry_path)
    staged_path = registry.stage_manifest(
        manifest_path,
        tmp_path / "staging",
        approval_id="approval-001",
    )
    artifact = json.loads(staged_path.read_text(encoding="utf-8"))
    artifact["source"]["trust_level"] = "official"
    artifact["source"]["import_policy"] = "manual_review"
    manifest_sha256 = _sha256_json(artifact["source"])
    artifact["manifest_sha256"] = manifest_sha256
    artifact["approval_receipt"]["manifest_sha256"] = manifest_sha256
    unsigned = dict(artifact)
    unsigned.pop("artifact_sha256")
    unsigned["approval_receipt"] = dict(artifact["approval_receipt"])
    unsigned["approval_receipt"].pop("artifact_sha256")
    artifact_sha256 = _sha256_json(unsigned)
    artifact["artifact_sha256"] = artifact_sha256
    artifact["approval_receipt"]["artifact_sha256"] = artifact_sha256
    staged_path.write_text(json.dumps(artifact), encoding="utf-8")

    with pytest.raises(SourceRegistryError, match="server-owned|least-privilege|policy"):
        registry.import_manifest(staged_path)


def test_registry_stages_normalized_manifest_without_promoting(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    _write_registry(registry_path, [])
    manifest_path = tmp_path / "admin_source.json"
    import_root = tmp_path / "imports"
    (import_root / "notes").mkdir(parents=True)
    manifest_path.write_text(
        json.dumps(
            _source(
                "admin_notes",
                source_type="local_import",
                local_path="notes",
                endpoint="",
                license="admin-provided",
                trust_level="experimental_unverified",
                import_policy="reference_only",
            )
        ),
        encoding="utf-8",
    )

    registry = SourceRegistry.load(registry_path)
    staged_path = registry.stage_manifest(
        manifest_path,
        tmp_path / "staging",
        import_root=import_root,
        approval_id="approval-001",
    )

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
    staged_path = registry.stage_manifest(
        manifest_path,
        tmp_path / "staging",
        replace=True,
        approval_id="approval-001",
    )
    registry.import_manifest(
        staged_path,
        rollback_dir=rollback_dir,
        batch_id="batch-001",
    )
    assert SourceRegistry.load(registry_path).get("nlm_mesh").label == "NLM MeSH Updated"

    current = SourceRegistry.load(registry_path)
    current.rollback_import(
        "batch-001",
        rollback_dir=rollback_dir,
        expected_revision=current.revision,
    )

    restored = SourceRegistry.load(registry_path)
    assert restored.get("nlm_mesh").label == "NLM MeSH"


def test_source_registry_authority_directories_and_lock_use_shared_parent_helper(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import core.source_registry as source_registry_module

    calls: list[Path] = []

    def parent(path: Path, *, mode: int = 0o777) -> None:
        calls.append(Path(path))
        Path(path).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(
        source_registry_module,
        "durable_mkdir_parents",
        parent,
        raising=False,
    )
    registry_path = tmp_path / "registry" / "sources.json"
    registry_path.parent.mkdir(parents=True)
    _write_registry(registry_path, [_source("nlm_mesh", label="NLM MeSH")])
    manifest_path = tmp_path / "incoming.json"
    manifest_path.write_text(
        json.dumps(_source("nlm_mesh", label="NLM MeSH Updated")),
        encoding="utf-8",
    )
    staging_dir = tmp_path / "authority" / "staging"
    rollback_dir = tmp_path / "authority" / "rollback"
    registry = SourceRegistry.load(registry_path)
    staged_path = registry.stage_manifest(
        manifest_path,
        staging_dir,
        replace=True,
        approval_id="approval-parent-helper",
    )

    registry.import_manifest(
        staged_path,
        rollback_dir=rollback_dir,
        batch_id="batch-parent-helper",
    )

    assert staging_dir in calls
    assert rollback_dir in calls
    assert registry_path.parent in calls
