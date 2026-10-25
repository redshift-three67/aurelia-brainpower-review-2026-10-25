"""Offline staging and audit ledger for source data batches."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from core.source_registry import SourceRegistry, SourceRegistryError


ALLOWED_DATA_TYPES = {"terminology", "profile", "group", "remedy", "reference"}


class SourceDataPromotionError(ValueError):
    """Raised when a source data batch cannot be staged or promoted."""


def stage_source_data_batch(
    batch_path: Path | str,
    staging_dir: Path | str,
    registry: SourceRegistry,
) -> Path:
    path = Path(batch_path)
    payload = _load_json(path)
    batch = _validate_batch(payload)
    source_id = str(batch["source_id"])
    try:
        registry.get(source_id)
    except SourceRegistryError as exc:
        raise SourceDataPromotionError(f"Unknown source: {source_id}") from exc

    records = list(batch["records"])
    normalized = {
        "schema": "morphic_source_data_batch",
        "schema_version": 1,
        "source_id": source_id,
        "data_type": str(batch["data_type"]),
        "record_count": len(records),
        "sha256": _sha256_json(records),
        "staged_at": _utc_now(),
        "source_batch_path": str(path),
        "records": records,
    }

    target_dir = Path(staging_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    staged_path = target_dir / f"{source_id}.{normalized['data_type']}.batch.json"
    staged_path.write_text(json.dumps(normalized, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return staged_path


def promote_staged_source_data(
    staged_path: Path | str,
    ledger_path: Path | str,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    path = Path(staged_path)
    staged = _load_json(path)
    _validate_staged_batch(staged)
    entry = {
        "promoted_at": _utc_now(),
        "source_id": staged["source_id"],
        "data_type": staged["data_type"],
        "record_count": staged["record_count"],
        "sha256": staged["sha256"],
        "staged_path": str(path),
    }
    result = dict(entry)
    result["dry_run"] = dry_run
    if dry_run:
        return result

    ledger_file = Path(ledger_path)
    if ledger_file.exists():
        ledger = _load_json(ledger_file)
        if ledger.get("schema") != "morphic_source_data_promotion_ledger":
            raise SourceDataPromotionError("Promotion ledger has an unsupported schema.")
        promotions = ledger.setdefault("promotions", [])
        if not isinstance(promotions, list):
            raise SourceDataPromotionError("Promotion ledger field 'promotions' must be a list.")
    else:
        ledger = {
            "schema": "morphic_source_data_promotion_ledger",
            "schema_version": 1,
            "promotions": [],
        }
        promotions = ledger["promotions"]

    promotions.append(entry)
    ledger_file.parent.mkdir(parents=True, exist_ok=True)
    ledger_file.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def _validate_batch(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    required = ("source_id", "data_type", "records")
    missing = [field for field in required if field not in payload]
    if missing:
        raise SourceDataPromotionError(f"Missing source data batch fields: {', '.join(missing)}")
    source_id = str(payload["source_id"]).strip()
    if not source_id:
        raise SourceDataPromotionError("source_id must not be empty.")
    data_type = str(payload["data_type"]).strip()
    if data_type not in ALLOWED_DATA_TYPES:
        raise SourceDataPromotionError(f"Unsupported source data_type: {data_type}")
    records = payload["records"]
    if not isinstance(records, list) or not records:
        raise SourceDataPromotionError("records must be a non-empty list.")
    for index, record in enumerate(records, 1):
        if not isinstance(record, Mapping):
            raise SourceDataPromotionError(f"record {index} must be an object.")
        if not str(record.get("id", "")).strip() or not str(record.get("label", "")).strip():
            raise SourceDataPromotionError(f"record {index} requires id and label.")
    return payload


def _validate_staged_batch(payload: Mapping[str, Any]) -> None:
    if payload.get("schema") != "morphic_source_data_batch":
        raise SourceDataPromotionError("Staged batch has an unsupported schema.")
    _validate_batch(payload)
    records = payload["records"]
    expected_hash = _sha256_json(records)
    if payload.get("sha256") != expected_hash:
        raise SourceDataPromotionError("Staged batch hash mismatch.")
    if payload.get("record_count") != len(records):
        raise SourceDataPromotionError("Staged batch record_count mismatch.")


def _load_json(path: Path) -> Mapping[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise SourceDataPromotionError("JSON payload must be an object.")
    return payload


def _sha256_json(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
