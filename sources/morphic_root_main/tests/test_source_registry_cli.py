import json
from pathlib import Path

from typer.testing import CliRunner

from apps.cli.main import app


runner = CliRunner()


def _write_registry(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
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
                        "scopes": ["terminology"],
                        "enabled": False,
                        "status": "disabled",
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
        "license": "admin",
        "trust_level": "admin_curated",
        "import_policy": "manual_review",
        "scopes": ["terminology"],
        "enabled": False,
        "status": "disabled",
    }
    data.update(overrides)
    path.write_text(json.dumps(data), encoding="utf-8")


def test_sources_cli_is_discoverable() -> None:
    result = runner.invoke(app, ["sources", "--help"])

    assert result.exit_code == 0, result.output
    assert "list" in result.output
    assert "enable" in result.output
    assert "disable" in result.output
    assert "import" in result.output


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

    result = runner.invoke(
        app,
        ["sources", "import", str(manifest_path), "--registry", str(registry_path), "--dry-run"],
    )

    assert result.exit_code == 0, result.output
    assert "DRY-RUN" in result.output
    assert "admin_notes" in result.output
    source_ids = [source["id"] for source in json.loads(registry_path.read_text(encoding="utf-8"))["sources"]]
    assert source_ids == ["nlm_mesh"]


def test_sources_cli_stages_manifest_without_importing(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "admin_notes.json"
    staging_dir = tmp_path / "staging"
    _write_registry(registry_path)
    _write_manifest(manifest_path)

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
        ],
    )

    assert result.exit_code == 0, result.output
    staged_path = staging_dir / "admin_notes.source.json"
    assert staged_path.exists()
    assert json.loads(staged_path.read_text(encoding="utf-8"))["source"]["id"] == "admin_notes"
    source_ids = [source["id"] for source in json.loads(registry_path.read_text(encoding="utf-8"))["sources"]]
    assert source_ids == ["nlm_mesh"]


def test_sources_cli_rolls_back_import_batch(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "nlm_mesh.json"
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
    )

    imported = runner.invoke(
        app,
        [
            "sources",
            "import",
            str(manifest_path),
            "--registry",
            str(registry_path),
            "--replace",
            "--rollback-dir",
            str(rollback_dir),
            "--batch-id",
            "batch-001",
        ],
    )
    assert imported.exit_code == 0, imported.output
    assert json.loads(registry_path.read_text(encoding="utf-8"))["sources"][0]["label"] == "NLM MeSH Updated"

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
        ],
    )

    assert rolled_back.exit_code == 0, rolled_back.output
    assert json.loads(registry_path.read_text(encoding="utf-8"))["sources"][0]["label"] == "NLM MeSH"


def test_sources_cli_stages_and_promotes_source_data_batch(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_dir = tmp_path / "data-staging"
    ledger_path = tmp_path / "ledger.json"
    _write_registry(registry_path)
    batch_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_id": "nlm_mesh",
                "data_type": "terminology",
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
    staged_path = staging_dir / "nlm_mesh.terminology.batch.json"
    assert staged_path.exists()

    dry_run = runner.invoke(
        app,
        [
            "sources",
            "data-promote",
            str(staged_path),
            "--ledger",
            str(ledger_path),
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
            "data-promote",
            str(staged_path),
            "--ledger",
            str(ledger_path),
        ],
    )
    assert promoted.exit_code == 0, promoted.output
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert ledger["promotions"][0]["source_id"] == "nlm_mesh"
