import json
from pathlib import Path

import pytest
import core.source_registry as source_registry_module
from typer.testing import CliRunner

from apps.cli.main import app
from core.admin_catalog import CatalogContext
from core.admin_catalog.store import CatalogStore
from core.source_data_promotion import stage_source_data_batch
from core.source_registry import SourceRegistry


runner = CliRunner()


@pytest.fixture(autouse=True)
def _configured_source_registry_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        source_registry_module,
        "DEFAULT_SOURCE_REGISTRY_PATH",
        tmp_path / "sources.json",
    )


def _write_registry(path: Path, *, enabled: bool = False) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 0,
                "rollback_history": [],
                "sources": [
                    {
                        "id": "nlm_mesh",
                        "label": "NLM MeSH",
                        "source_type": "online_download",
                        "homepage": "https://www.nlm.nih.gov/mesh/meshhome.html",
                        "download_url": "https://www.nlm.nih.gov/databases/download/mesh.html",
                        "license": "source-specific",
                        "trust_level": "official",
                        "import_policy": "manual_review",
                        "scopes": ["group", "terminology"],
                        "enabled": enabled,
                        "status": "active" if enabled else "disabled",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def _write_manifest(path: Path, source_id: str = "admin_notes", **overrides: object) -> None:
    data: dict[str, object] = {
        "id": source_id,
        "label": "Admin Notes",
        "description": "Curated admin notes",
        "source_type": "local_import",
        "local_path": str(path.parent / "notes"),
        "license": "admin-provided",
        "trust_level": "experimental_unverified",
        "import_policy": "reference_only",
        "scopes": ["terminology"],
        "enabled": False,
        "status": "disabled",
    }
    data.update(overrides)
    path.write_text(json.dumps(data), encoding="utf-8")


def _write_validation_keyring(path: Path) -> Path:
    path.write_text(
        json.dumps(
            {
                "purpose": "morphic_admin_catalog_validation_hmac_v1",
                "authority_id": "source-cli-validation-tests",
                "active_key_id": "validation-v1",
                "keys": {"validation-v1": "cd" * 32},
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return path


def test_sources_cli_imports_stage_to_new_draft_without_publish_or_activation(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    catalog_db = tmp_path / "catalog.db"
    _write_registry(registry_path, enabled=True)
    batch_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_id": "nlm_mesh",
                "source_version": "2026-07-15",
                "data_type": "group",
                "license": "source-specific",
                "retrieval_metadata": {
                    "retrieved_at": "2026-07-15T07:30:00+00:00",
                    "method": "local_fixture",
                },
                "records": [{"id": "group-a", "label": "Group A"}],
            }
        ),
        encoding="utf-8",
    )
    staged_path = stage_source_data_batch(
        batch_path,
        tmp_path / "staging",
        SourceRegistry.load(registry_path),
    )

    result = runner.invoke(
        app,
        [
            "sources",
            "data-import-draft",
            str(staged_path),
            "--catalog-db",
            str(catalog_db),
            "--staging-root",
            str(tmp_path / "staging"),
            "--registry",
            str(registry_path),
            "--draft-id",
            "source-draft-a",
            "--operator-id",
            "operator-a",
            "--workspace-id",
            "workspace-a",
            "--tenant-id",
            "tenant-a",
            "--scope",
            "workspace",
            "--actor-id",
            "operator-a",
            "--reason",
            "reviewed source import",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Source-Draft erstellt" in result.output
    assert "Kein Catalog-Publish" in result.output
    context = CatalogContext(
        operator_id="operator-a",
        workspace_id="workspace-a",
        tenant_id="tenant-a",
        scope="workspace",
    )
    store = CatalogStore(catalog_db)
    assert store.get_draft(context, "source-draft-a") is not None
    assert len(store.source_import_receipts(context, "source-draft-a")) == 1
    assert store.list_revision_ids(context) == []
    assert store.current_revision_id(context) is None


def test_sources_cli_data_import_draft_injects_explicit_validation_keyring(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import apps.cli.commands.sources as sources_command_module

    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    catalog_db = tmp_path / "catalog.db"
    validation_keyring = _write_validation_keyring(tmp_path / "validation-keyring.json")
    _write_registry(registry_path, enabled=True)
    batch_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_id": "nlm_mesh",
                "source_version": "2026-07-15",
                "data_type": "group",
                "license": "source-specific",
                "retrieval_metadata": {
                    "retrieved_at": "2026-07-15T07:30:00+00:00",
                    "method": "local_fixture",
                },
                "records": [{"id": "group-a", "label": "Group A"}],
            }
        ),
        encoding="utf-8",
    )
    staged_path = stage_source_data_batch(
        batch_path,
        tmp_path / "staging",
        SourceRegistry.load(registry_path),
    )
    captured_providers: list[object] = []

    class CapturingCatalogStore(CatalogStore):
        def __init__(self, *args: object, **kwargs: object) -> None:
            captured_providers.append(kwargs.get("validation_key_provider"))
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(
        sources_command_module,
        "CatalogStore",
        CapturingCatalogStore,
    )

    result = runner.invoke(
        app,
        [
            "sources",
            "data-import-draft",
            str(staged_path),
            "--catalog-db",
            str(catalog_db),
            "--staging-root",
            str(tmp_path / "staging"),
            "--registry",
            str(registry_path),
            "--draft-id",
            "source-draft-a",
            "--operator-id",
            "operator-a",
            "--workspace-id",
            "workspace-a",
            "--tenant-id",
            "tenant-a",
            "--scope",
            "workspace",
            "--actor-id",
            "operator-a",
            "--reason",
            "reviewed source import",
            "--validation-keyring",
            str(validation_keyring),
        ],
    )

    assert result.exit_code == 0, result.output
    assert captured_providers
    provider = captured_providers[-1]
    assert provider is not None
    assert getattr(provider, "authority_id") == "source-cli-validation-tests"
    assert "cd" * 32 not in result.output


def test_sources_cli_is_discoverable() -> None:
    result = runner.invoke(app, ["sources", "--help"])

    assert result.exit_code == 0, result.output
    assert "list" in result.output
    assert "enable" in result.output
    assert "disable" in result.output
    assert "import" in result.output
    assert "data-import-draft" in result.output


def test_sources_cli_reports_corrupt_registry_without_traceback(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    registry_path.write_text("{", encoding="utf-8")

    result = runner.invoke(
        app,
        ["sources", "list", "--registry", str(registry_path)],
    )

    assert result.exit_code == 1
    assert "[FEHLER]" in result.output
    assert "Traceback" not in result.output


def test_sources_cli_reports_invalid_utf8_batch_without_traceback(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path, enabled=True)
    batch_path.write_bytes(b"\xff")

    result = runner.invoke(
        app,
        [
            "sources",
            "data-stage",
            str(batch_path),
            "--staging-dir",
            str(tmp_path / "staging"),
            "--registry",
            str(registry_path),
        ],
    )

    assert result.exit_code == 1
    assert "[FEHLER]" in result.output
    assert "Traceback" not in result.output


def test_sources_cli_enable_normalizes_write_time_oserror(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_path = tmp_path / "sources.json"
    _write_registry(registry_path)

    def fail_enable(*args: object, **kwargs: object) -> None:
        raise OSError("synthetic write failure")

    monkeypatch.setattr(SourceRegistry, "enable_source", fail_enable)
    result = runner.invoke(
        app,
        ["sources", "enable", "nlm_mesh", "--registry", str(registry_path)],
    )

    assert result.exit_code == 1
    assert "synthetic write failure" in result.output
    assert "Traceback" not in result.output


def test_sources_cli_validate_rejects_unknown_wrapper_schema(tmp_path: Path) -> None:
    manifest_path = tmp_path / "admin_notes.json"
    _write_manifest(manifest_path)
    source = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_path.write_text(
        json.dumps({"schema_version": 999, "source": source}),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "sources",
            "validate",
            str(manifest_path),
            "--import-root",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 1
    assert "schema_version" in result.output


def test_sources_cli_lists_and_toggles_registry(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    _write_registry(registry_path)

    listed = runner.invoke(app, ["sources", "list", "--registry", str(registry_path), "--json"])
    assert listed.exit_code == 0, listed.output
    assert json.loads(listed.output)[0]["id"] == "nlm_mesh"

    enabled = runner.invoke(app, ["sources", "enable", "nlm_mesh", "--registry", str(registry_path)])
    assert enabled.exit_code == 0, enabled.output
    assert json.loads(registry_path.read_text(encoding="utf-8"))["sources"][0]["enabled"] is True

    disabled = runner.invoke(app, ["sources", "disable", "nlm_mesh", "--registry", str(registry_path)])
    assert disabled.exit_code == 0, disabled.output
    assert json.loads(registry_path.read_text(encoding="utf-8"))["sources"][0]["enabled"] is False


def test_sources_cli_import_dry_run_does_not_modify_registry(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "admin_notes.json"
    _write_registry(registry_path)
    _write_manifest(manifest_path)
    (tmp_path / "notes").mkdir()

    result = runner.invoke(
        app,
        [
            "sources",
            "import-plan",
            str(manifest_path),
            "--registry",
            str(registry_path),
            "--import-root",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "PLAN" in result.output
    assert "admin_notes" in result.output
    source_ids = [source["id"] for source in json.loads(registry_path.read_text(encoding="utf-8"))["sources"]]
    assert source_ids == ["nlm_mesh"]


def test_sources_cli_stages_manifest_without_importing(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "admin_notes.json"
    staging_dir = tmp_path / "staging"
    _write_registry(registry_path)
    _write_manifest(manifest_path)
    (tmp_path / "notes").mkdir()

    result = runner.invoke(
        app,
        [
            "sources",
            "stage",
            str(manifest_path),
            "--registry",
            str(registry_path),
            "--staging-dir",
            str(staging_dir),
            "--import-root",
            str(tmp_path),
            "--approval-id",
            "approval-001",
        ],
    )

    assert result.exit_code == 0, result.output
    staged_paths = list(staging_dir.glob("admin_notes.*.source-stage.json"))
    assert len(staged_paths) == 1
    staged_path = staged_paths[0]
    assert staged_path.exists()
    assert json.loads(staged_path.read_text(encoding="utf-8"))["source"]["id"] == "admin_notes"
    source_ids = [source["id"] for source in json.loads(registry_path.read_text(encoding="utf-8"))["sources"]]
    assert source_ids == ["nlm_mesh"]


def test_sources_cli_rolls_back_import_batch(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "nlm_mesh.json"
    staging_dir = tmp_path / "staging"
    rollback_dir = tmp_path / "rollbacks"
    _write_registry(registry_path)
    _write_manifest(
        manifest_path,
        source_id="nlm_mesh",
        label="NLM MeSH Updated",
        source_type="online_download",
        homepage="https://www.nlm.nih.gov/mesh/meshhome.html",
        download_url="https://www.nlm.nih.gov/databases/download/mesh.html",
        local_path="",
        license="source-specific",
        trust_level="official",
        import_policy="manual_review",
    )

    staged = runner.invoke(
        app,
        [
            "sources",
            "stage",
            str(manifest_path),
            "--registry",
            str(registry_path),
            "--replace",
            "--staging-dir",
            str(staging_dir),
            "--approval-id",
            "approval-001",
        ],
    )
    assert staged.exit_code == 0, staged.output
    staged_paths = list(staging_dir.glob("nlm_mesh.*.source-stage.json"))
    assert len(staged_paths) == 1

    imported = runner.invoke(
        app,
        [
            "sources",
            "import",
            str(staged_paths[0]),
            "--registry",
            str(registry_path),
            "--rollback-dir",
            str(rollback_dir),
            "--batch-id",
            "batch-001",
        ],
    )
    assert imported.exit_code == 0, imported.output
    assert json.loads(registry_path.read_text(encoding="utf-8"))["sources"][0]["label"] == "NLM MeSH Updated"
    expected_revision = json.loads(registry_path.read_text(encoding="utf-8"))["revision"]

    rolled_back = runner.invoke(
        app,
        [
            "sources",
            "rollback",
            "batch-001",
            "--registry",
            str(registry_path),
            "--rollback-dir",
            str(rollback_dir),
            "--expected-revision",
            str(expected_revision),
        ],
    )

    assert rolled_back.exit_code == 0, rolled_back.output
    assert json.loads(registry_path.read_text(encoding="utf-8"))["sources"][0]["label"] == "NLM MeSH"


def test_sources_cli_stages_and_records_source_data_consistency(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_dir = tmp_path / "data-staging"
    ledger_path = tmp_path / "ledger.json"
    _write_registry(registry_path, enabled=True)
    batch_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_id": "nlm_mesh",
                "source_version": "2026-07-14",
                "data_type": "terminology",
                "license": "source-specific",
                "retrieval_metadata": {
                    "retrieved_at": "2026-07-14T20:00:00+00:00",
                    "method": "synthetic_cli_test",
                },
                "records": [{"id": "bronchien", "label": "Bronchien"}],
            }
        ),
        encoding="utf-8",
    )

    staged = runner.invoke(
        app,
        [
            "sources",
            "data-stage",
            str(batch_path),
            "--registry",
            str(registry_path),
            "--staging-dir",
            str(staging_dir),
        ],
    )
    assert staged.exit_code == 0, staged.output
    staged_paths = list(staging_dir.glob("nlm_mesh.terminology.*.batch.json"))
    assert len(staged_paths) == 1
    staged_path = staged_paths[0]

    dry_run = runner.invoke(
        app,
        [
            "sources",
            "data-record-consistency",
            str(staged_path),
            "--ledger",
            str(ledger_path),
            "--registry",
            str(registry_path),
            "--dry-run",
        ],
    )
    assert dry_run.exit_code == 0, dry_run.output
    assert "DRY-RUN" in dry_run.output
    assert not ledger_path.exists()

    promoted = runner.invoke(
        app,
        [
            "sources",
            "data-record-consistency",
            str(staged_path),
            "--ledger",
            str(ledger_path),
            "--registry",
            str(registry_path),
        ],
    )
    assert promoted.exit_code == 0, promoted.output
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert ledger["entries"][0]["source_id"] == "nlm_mesh"
    assert "promot" not in json.dumps(ledger).lower()


def test_sources_cli_data_promote_is_explicitly_deprecated_alias(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_dir = tmp_path / "staging"
    ledger_path = tmp_path / "ledger.json"
    _write_registry(registry_path, enabled=True)
    batch_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_id": "nlm_mesh",
                "source_version": "2026-07-14",
                "data_type": "terminology",
                "license": "source-specific",
                "retrieval_metadata": {
                    "retrieved_at": "2026-07-14T20:00:00+00:00",
                    "method": "synthetic_cli_test",
                },
                "records": [{"id": "bronchien", "label": "Bronchien"}],
            }
        ),
        encoding="utf-8",
    )
    staged = runner.invoke(
        app,
        [
            "sources",
            "data-stage",
            str(batch_path),
            "--registry",
            str(registry_path),
            "--staging-dir",
            str(staging_dir),
        ],
    )
    assert staged.exit_code == 0, staged.output
    staged_path = next(staging_dir.glob("nlm_mesh.terminology.*.batch.json"))

    result = runner.invoke(
        app,
        [
            "sources",
            "data-promote",
            str(staged_path),
            "--ledger",
            str(ledger_path),
            "--registry",
            str(registry_path),
            "--dry-run",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "DEPRECATED" in result.output
    assert "data-record-consistency" in result.output
    assert "kein Catalog-Publish" in result.output
    assert not ledger_path.exists()
