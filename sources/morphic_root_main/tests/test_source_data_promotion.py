from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.source_data_promotion import (
    SourceDataPromotionError,
    promote_staged_source_data,
    stage_source_data_batch,
)
from core.source_registry import SourceRegistry


def _write_registry(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "sources": [
                    {
                        "id": "admin_terms",
                        "label": "Admin Terms",
                        "source_type": "local_import",
                        "local_path": str(path.parent / "terms"),
                        "license": "admin",
                        "trust_level": "admin_curated",
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


def _write_batch(path: Path, *, source_id: str = "admin_terms") -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_id": source_id,
                "data_type": "terminology",
                "records": [
                    {
                        "id": "bronchien",
                        "label": "Bronchien",
                        "payload": {"group": "atmung_lunge_detailliert"},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_source_data_batch_is_staged_with_hash_and_provenance(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_dir = tmp_path / "staging"
    _write_registry(registry_path)
    _write_batch(batch_path)

    staged_path = stage_source_data_batch(batch_path, staging_dir, SourceRegistry.load(registry_path))

    staged = json.loads(staged_path.read_text(encoding="utf-8"))
    assert staged["schema"] == "morphic_source_data_batch"
    assert staged["source_id"] == "admin_terms"
    assert staged["data_type"] == "terminology"
    assert staged["record_count"] == 1
    assert len(staged["sha256"]) == 64
    assert staged["records"][0]["id"] == "bronchien"


def test_source_data_batch_rejects_unknown_source(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_batch(batch_path, source_id="missing_source")

    with pytest.raises(SourceDataPromotionError, match="Unknown source"):
        stage_source_data_batch(batch_path, tmp_path / "staging", SourceRegistry.load(registry_path))


def test_source_data_promotion_dry_run_does_not_write_ledger(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    ledger_path = tmp_path / "ledger.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    staged_path = stage_source_data_batch(batch_path, tmp_path / "staging", SourceRegistry.load(registry_path))

    plan = promote_staged_source_data(staged_path, ledger_path, dry_run=True)

    assert plan["source_id"] == "admin_terms"
    assert plan["record_count"] == 1
    assert plan["dry_run"] is True
    assert not ledger_path.exists()


def test_source_data_promotion_writes_append_only_ledger(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    ledger_path = tmp_path / "ledger.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    staged_path = stage_source_data_batch(batch_path, tmp_path / "staging", SourceRegistry.load(registry_path))

    result = promote_staged_source_data(staged_path, ledger_path)

    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert result["dry_run"] is False
    assert ledger["schema"] == "morphic_source_data_promotion_ledger"
    assert len(ledger["promotions"]) == 1
    assert ledger["promotions"][0]["source_id"] == "admin_terms"
    assert ledger["promotions"][0]["record_count"] == 1
