from __future__ import annotations

import hashlib
import inspect
import json
import sqlite3
import threading
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

import pytest
from typer.testing import CliRunner

from apps.cli.main import app
import core.source_data_promotion as promotion_module
import core.source_registry as source_registry_module
import core.admin_catalog.store as store_module
from core.admin_catalog import (
    AdminCatalogService,
    CatalogContext,
    CatalogEntry,
    DraftValidationError,
    EntryType,
    normalize_source_records,
)
from core.admin_catalog.store import CatalogStore, CatalogStoreError
from core.admin_catalog.validation_attestation import HmacValidationKeyProvider
from core.source_data_promotion import (
    SourceDataPromotionError,
    import_staged_source_data_to_draft,
    stage_source_data_batch,
    validate_staged_source_artifact,
)
from core.source_registry import SourceRegistry, SourceRegistryError


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


def _context() -> CatalogContext:
    return CatalogContext(
        operator_id="operator-f5b-review",
        workspace_id="workspace-f5b-review",
        tenant_id="tenant-f5b-review",
        scope="workspace",
    )


def _validation_provider() -> HmacValidationKeyProvider:
    return HmacValidationKeyProvider(
        authority_id="f5b-review-catalog",
        active_key_id="test-key-v1",
        keys={"test-key-v1": b"K" * 32},
    )


def _write_registry(path: Path, *, scopes: list[str] | None = None) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 0,
                "rollback_history": [],
                "sources": [
                    {
                        "id": "admin_source",
                        "label": "Admin Source",
                        "source_type": "local_import",
                        "local_path": str(path.parent / "source"),
                        "license": "admin-provided",
                        "trust_level": "admin_curated",
                        "import_policy": "manual_review",
                        "scopes": scopes or ["group"],
                        "enabled": True,
                        "status": "active",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def _write_batch(path: Path, *, data_type: str = "group") -> None:
    records: list[dict[str, object]]
    if data_type == "group":
        records = [{"id": "group-a", "label": "Group A"}]
    else:
        records = [{"id": "term-a", "code": "A", "label": "A", "scheme": "fixture", "target_entry_id": "group-a", "target_entry_type": "group"}]
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_id": "admin_source",
                "source_version": "2026-07-15",
                "data_type": data_type,
                "license": "admin-provided",
                "retrieval_metadata": {
                    "retrieved_at": "2026-07-15T08:00:00+00:00",
                    "method": "local_fixture",
                },
                "records": records,
            }
        ),
        encoding="utf-8",
    )


def _imported_service(tmp_path: Path) -> tuple[AdminCatalogService, SourceRegistry, Path]:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_root = tmp_path / "staging"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, staging_root, registry)
    service = AdminCatalogService(CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        ))
    import_staged_source_data_to_draft(
        staged_path,
        staging_root=staged_path.parent,
        registry=registry,
        service=service,
        context=_context(),
        draft_id="source-draft",
        actor_id="operator-f5b-review",
        reason="review regression",
    )
    assert service.validate_draft(_context(), "source-draft").is_valid
    return service, registry, staged_path


def test_stage_rejects_data_type_outside_source_scope(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path, scopes=["terminology"])
    _write_batch(batch_path, data_type="group")

    with pytest.raises(SourceDataPromotionError, match="scope|data_type"):
        stage_source_data_batch(
            batch_path, tmp_path / "staging", SourceRegistry.load(registry_path)
        )


def test_import_requires_registered_artifact_under_explicit_staging_root(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_root = tmp_path / "staging"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, staging_root, registry)
    replacement = tmp_path / "replacement.batch.json"
    replacement.write_bytes(staged_path.read_bytes())
    service = AdminCatalogService(CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        ))

    with pytest.raises(SourceDataPromotionError, match="artifact|stage|registered"):
        import_staged_source_data_to_draft(
            replacement,
            staging_root=staging_root,
            registry=registry,
            service=service,
            context=_context(),
            draft_id="replacement-draft",
            actor_id="operator-f5b-review",
            reason="must fail",
        )

    assert service.store.get_draft(_context(), "replacement-draft") is None


def test_public_store_publish_rejects_source_imported_draft(tmp_path: Path) -> None:
    service, _registry, _staged_path = _imported_service(tmp_path)

    with pytest.raises(CatalogStoreError, match="source|receipt|dedicated"):
        service.store.publish_validated_draft(
            _context(),
            "source-draft",
            "revision-bypass",
            expected_draft_version=1,
        )

    assert service.store.list_revision_ids(_context()) == []


def test_generic_service_publish_rejects_noop_receipt_validator(tmp_path: Path) -> None:
    service, _registry, _staged_path = _imported_service(tmp_path)

    with pytest.raises(DraftValidationError, match="dedicated|source"):
        service.publish_draft(
            _context(),
            "source-draft",
            "revision-noop",
            expected_draft_version=1,
        )

    assert service.store.list_revision_ids(_context()) == []


def test_direct_revision_cannot_claim_source_draft_provenance(tmp_path: Path) -> None:
    store = CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        )
    entry = CatalogEntry(
        entry_type=EntryType.GROUP,
        entry_id="group-a",
        context=_context(),
        source_id="fixture",
        provenance="fixture",
        data={"label": "Group A"},
    )
    store.create_draft(_context(), "draft-a", [entry])

    replacement = CatalogEntry(
        entry_type=EntryType.GROUP,
        entry_id="group-b",
        context=_context(),
        source_id="fixture",
        provenance="fixture",
        data={"label": "Group B"},
    )
    with pytest.raises(CatalogStoreError, match="source_draft_id|differ"):
        store.create_revision(
            _context(),
            "revision-a",
            [replacement],
            source_draft_id="draft-a",
        )


def test_reference_quarantine_is_transitively_closed() -> None:
    result = normalize_source_records(
        source_id="admin_source",
        data_type="terminology",
        records=[
            {
                "id": "term-invalid",
                "code": "BAD",
                "label": "Invalid",
                "scheme": "fixture",
                "target_entry_id": "missing-group",
                "target_entry_type": "group",
            },
            {
                "id": "term-dependent",
                "code": "DEP",
                "label": "Dependent",
                "scheme": "fixture",
                "target_entry_id": "term-invalid",
                "target_entry_type": "terminology",
            },
        ],
        context=_context(),
    )

    assert result.normalized == ()
    assert {item.source_record_id for item in result.quarantined} == {
        "term-dependent",
        "term-invalid",
    }
    assert all(
        item.reason_codes == ("unknown_reference",)
        for item in result.quarantined
    )


def test_data_import_draft_requires_explicit_registry_and_staging_root(
    tmp_path: Path,
) -> None:
    common = [
        "sources",
        "data-import-draft",
        str(tmp_path / "missing.batch.json"),
        "--catalog-db",
        str(tmp_path / "catalog.db"),
        "--draft-id",
        "draft-a",
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
        "missing explicit authorities",
    ]
    missing_registry = runner.invoke(
        app,
        [*common, "--staging-root", str(tmp_path / "staging")],
    )
    missing_staging_root = runner.invoke(
        app,
        [*common, "--registry", str(tmp_path / "sources.json")],
    )

    assert missing_registry.exit_code == 2
    assert "--registry" in missing_registry.output
    assert missing_staging_root.exit_code == 2
    assert "--staging-root" in missing_staging_root.output
    assert not (tmp_path / "catalog.db").exists()


def test_store_open_rejects_drifted_receipt_trigger(tmp_path: Path) -> None:
    db_path = tmp_path / "catalog.db"
    CatalogStore(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.execute("DROP TRIGGER catalog_draft_source_imports_no_update")
        connection.execute(
            """
            CREATE TRIGGER catalog_draft_source_imports_no_update
            BEFORE UPDATE ON catalog_draft_source_imports
            BEGIN
                SELECT 1;
            END
            """
        )

    with pytest.raises(ValueError, match="schema"):
        CatalogStore(db_path)


def test_invalid_cli_import_does_not_create_catalog_database(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    catalog_db = tmp_path / "catalog.db"
    _write_registry(registry_path)

    result = runner.invoke(
        app,
        [
            "sources",
            "data-import-draft",
            str(tmp_path / "missing.batch.json"),
            "--staging-root",
            str(tmp_path / "staging"),
            "--catalog-db",
            str(catalog_db),
            "--registry",
            str(registry_path),
            "--draft-id",
            "draft-a",
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
            "invalid stage",
        ],
    )

    assert result.exit_code == 1
    assert not catalog_db.exists()


def test_quarantine_never_exposes_raw_invalid_record_id() -> None:
    raw_id = "<script>alert(1)</script>"
    result = normalize_source_records(
        source_id="admin_source",
        data_type="group",
        records=[{"id": raw_id, "label": "Unsafe"}],
        context=_context(),
    )

    assert result.normalized == ()
    assert len(result.quarantined) == 1
    quarantined = result.quarantined[0]
    assert quarantined.reason_codes == ("invalid_record_id",)
    assert raw_id not in quarantined.source_record_id
    assert raw_id not in result.canonical_json()


def test_receipt_binds_explicit_base_revision_identity_and_hash(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_root = tmp_path / "staging"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, staging_root, registry)
    service = AdminCatalogService(CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        ))
    base = CatalogEntry(
        entry_type=EntryType.GROUP,
        entry_id="group-base",
        context=_context(),
        source_id="fixture",
        provenance="base",
        data={"label": "Base"},
    )
    base_hash = service.store.create_revision(
        _context(), "revision-base", [base]
    )

    result = import_staged_source_data_to_draft(
        staged_path,
        staging_root=staging_root,
        registry=registry,
        service=service,
        context=_context(),
        draft_id="source-draft",
        actor_id="operator-f5b-review",
        reason="base binding",
        base_revision_id="revision-base",
    )

    assert result.receipt.base_revision_id == "revision-base"
    assert result.receipt.base_revision_payload_hash == base_hash
    assert result.receipt.has_valid_hash()


def test_public_store_publish_rejects_self_supplied_receipt_hashes(
    tmp_path: Path,
) -> None:
    service, _registry, _staged_path = _imported_service(tmp_path)
    receipt = service.store.source_import_receipts(_context(), "source-draft")[0]

    with pytest.raises((TypeError, CatalogStoreError)):
        service.store.publish_validated_draft(
            _context(),
            "source-draft",
            "revision-forged-capability",
            expected_draft_version=1,
            _revalidated_source_receipt_hashes=(receipt.receipt_sha256,),
        )


def test_direct_revision_rejects_exact_source_imported_draft_snapshot(
    tmp_path: Path,
) -> None:
    service, _registry, _staged_path = _imported_service(tmp_path)
    entries = service.store.get_draft_entries(_context(), "source-draft")
    assert entries is not None

    with pytest.raises(CatalogStoreError, match="source|receipt|dedicated"):
        service.store.create_revision(
            _context(),
            "revision-direct-source-draft",
            entries,
            source_draft_id="source-draft",
        )


def test_direct_revision_rejects_known_source_import_snapshot_without_draft_id(
    tmp_path: Path,
) -> None:
    service, _registry, _staged_path = _imported_service(tmp_path)
    entries = service.store.get_draft_entries(_context(), "source-draft")
    assert entries is not None

    with pytest.raises(CatalogStoreError, match="source|receipt|dedicated"):
        service.store.create_revision(
            _context(),
            "revision-direct-source-snapshot",
            entries,
        )


def test_stage_artifact_cannot_replay_into_another_catalog_context(
    tmp_path: Path,
) -> None:
    service, registry, staged_path = _imported_service(tmp_path)
    other_context = CatalogContext(
        operator_id="operator-other",
        workspace_id="workspace-other",
        tenant_id="tenant-other",
        scope="workspace",
    )

    with pytest.raises(SourceDataPromotionError, match="replay|already|consumed"):
        import_staged_source_data_to_draft(
            staged_path,
            staging_root=staged_path.parent,
            registry=registry,
            service=service,
            context=other_context,
            draft_id="other-draft",
            actor_id="operator-other",
            reason="cross-context replay must fail",
        )


def test_store_open_rejects_missing_schema_object_without_repair(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "catalog.db"
    CatalogStore(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.execute("DROP TRIGGER catalog_draft_source_imports_no_update")
    before = hashlib.sha256(db_path.read_bytes()).hexdigest()

    with pytest.raises(ValueError, match="schema"):
        CatalogStore(db_path)

    assert hashlib.sha256(db_path.read_bytes()).hexdigest() == before


def test_missing_base_revision_cli_preflight_does_not_create_catalog_database(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_root = tmp_path / "staging"
    catalog_db = tmp_path / "catalog.db"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, staging_root, registry)

    result = runner.invoke(
        app,
        [
            "sources", "data-import-draft", str(staged_path),
            "--staging-root", str(staging_root),
            "--catalog-db", str(catalog_db),
            "--registry", str(registry_path),
            "--base-revision-id", "missing-revision",
            "--draft-id", "draft-a",
            "--operator-id", "operator-a",
            "--workspace-id", "workspace-a",
            "--tenant-id", "tenant-a",
            "--scope", "workspace",
            "--actor-id", "operator-a",
            "--reason", "missing base",
        ],
    )

    assert result.exit_code == 1
    assert not catalog_db.exists()


def test_semantically_invalid_cli_preflight_does_not_create_catalog_database(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_root = tmp_path / "staging"
    catalog_db = tmp_path / "catalog.db"
    _write_registry(registry_path)
    _write_batch(batch_path)
    payload = json.loads(batch_path.read_text(encoding="utf-8"))
    payload["records"] = [
        {"id": "group-a", "label": "Group A", "medical_claim": "cures all"}
    ]
    batch_path.write_text(json.dumps(payload), encoding="utf-8")
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, staging_root, registry)

    result = runner.invoke(
        app,
        [
            "sources", "data-import-draft", str(staged_path),
            "--staging-root", str(staging_root),
            "--catalog-db", str(catalog_db),
            "--registry", str(registry_path),
            "--draft-id", "draft-a",
            "--operator-id", "operator-a",
            "--workspace-id", "workspace-a",
            "--tenant-id", "tenant-a",
            "--scope", "workspace",
            "--actor-id", "operator-a",
            "--reason", "semantic failure",
        ],
    )

    assert result.exit_code == 1
    assert not catalog_db.exists()


def test_stage_index_tamper_without_authority_key_is_rejected(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_root = tmp_path / "staging"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, staging_root, registry)
    index_path = staging_root / ".morphic-stage-index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["entries"][0]["relative_path"] = "forged.batch.json"
    index_path.write_text(json.dumps(index), encoding="utf-8")

    with pytest.raises(SourceDataPromotionError, match="HMAC|authority|index"):
        import_staged_source_data_to_draft(
            staged_path,
            staging_root=staging_root,
            registry=registry,
            service=AdminCatalogService(CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        )),
            context=_context(),
            draft_id="forged-index-draft",
            actor_id="operator-f5b-review",
            reason="tampered index",
        )


def test_raw_source_receipt_creation_is_not_public(tmp_path: Path) -> None:
    store = CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        )
    service = AdminCatalogService(store)

    assert not hasattr(store, "create_source_import_draft")
    assert not hasattr(service, "create_source_import_draft")


def test_internal_publish_cannot_accept_caller_supplied_receipt_hashes(
    tmp_path: Path,
) -> None:
    service, _registry, _staged_path = _imported_service(tmp_path)
    service.validate_draft(_context(), "source-draft")

    assert not hasattr(service.store, "_publish_validated_draft")
    with pytest.raises(CatalogStoreError, match="registry|receipt|source"):
        service.store.publish_validated_draft(
            _context(),
            "source-draft",
            "forged-internal-publish",
            expected_draft_version=1,
        )


def test_source_import_boundary_rejects_caller_supplied_entries_and_receipt(
    tmp_path: Path,
) -> None:
    store = CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        )
    service = AdminCatalogService(store)

    assert not hasattr(store, "_create_source_import_draft")
    assert not hasattr(service, "_create_source_import_draft")
    assert not hasattr(store, "_connect")
    assert not hasattr(store, "_write_connection")
    common = {
        "staging_root": tmp_path / "staging",
        "registry": object(),
        "context": _context(),
        "draft_id": "forged-source-draft",
        "actor_id": "operator-f5b-review",
        "reason": "forged receipt",
    }
    with pytest.raises(TypeError, match="entries"):
        store.import_staged_source_draft(
            tmp_path / "never-read.json",
            **common,
            entries=(),
        )
    with pytest.raises(TypeError, match="receipt"):
        store.import_staged_source_draft(
            tmp_path / "never-read.json",
            **common,
            receipt=object(),
        )


def test_import_uses_only_stage_bytes_attested_under_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_root = tmp_path / "staging"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, staging_root, registry)
    real_load_json_bytes = promotion_module._load_json_bytes
    staged_reads = 0

    def swapping_load_json(raw: bytes):
        nonlocal staged_reads
        loaded = real_load_json_bytes(raw)
        if loaded.get("schema") == promotion_module._BATCH_SCHEMA:
            staged_reads += 1
            if staged_reads == 2:
                payload = dict(loaded)
                records = [dict(item) for item in payload["records"]]
                records[0]["label"] = "FORGED AFTER LOCK"
                payload["records"] = records
                payload["batch_identity_sha256"] = promotion_module._canonical_sha256(
                    {
                        "source_id": payload["source_id"],
                        "source_version": payload["source_version"],
                        "data_type": payload["data_type"],
                        "license": payload["license"],
                        "retrieval_metadata": payload["retrieval_metadata"],
                        "records": records,
                    }
                )
                payload["sha256"] = promotion_module._canonical_sha256(
                    {key: value for key, value in payload.items() if key != "sha256"}
                )
                staged_path.write_text(json.dumps(payload), encoding="utf-8")
        return loaded

    monkeypatch.setattr(promotion_module, "_load_json_bytes", swapping_load_json)
    service = AdminCatalogService(CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        ))
    with pytest.raises((SourceDataPromotionError, OSError)):
        import_staged_source_data_to_draft(
            staged_path,
            staging_root=staging_root,
            registry=registry,
            service=service,
            context=_context(),
            draft_id="locked-bytes-draft",
            actor_id="operator-f5b-review",
            reason="stage swap regression",
        )

    assert staged_reads == 2
    assert service.store.get_draft(_context(), "locked-bytes-draft") is None


def test_schema_drift_after_store_open_blocks_next_write_without_mutation(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "catalog.db"
    store = CatalogStore(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.execute("DROP TRIGGER catalog_draft_source_imports_no_delete")
    before = hashlib.sha256(db_path.read_bytes()).hexdigest()
    entry = CatalogEntry(
        entry_id="group-after-drift",
        entry_type=EntryType.GROUP,
        context=_context(),
        source_id="fixture",
        provenance="fixture",
        data={"label": "Group after drift"},
    )

    with pytest.raises(CatalogStoreError, match="schema|fingerprint"):
        store.create_draft(_context(), "draft-after-drift", [entry])

    assert hashlib.sha256(db_path.read_bytes()).hexdigest() == before


def test_stage_authority_key_must_be_outside_staging_root(tmp_path: Path) -> None:
    staging_root = tmp_path / "staging"
    staging_root.mkdir()
    registry_path = staging_root / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_batch(batch_path)

    with pytest.raises(SourceDataPromotionError, match="key|staging|authority"):
        stage_source_data_batch(
            batch_path, staging_root, SourceRegistry.load(registry_path)
        )


def test_stage_key_creation_failure_leaves_no_final_authority_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_batch(batch_path)

    class PartialWrite:
        def __init__(self, context_manager: object) -> None:
            self.context_manager = context_manager
            self.handle: object | None = None

        def __enter__(self):
            self.handle = self.context_manager.__enter__()
            return self

        def write(self, data: bytes) -> None:
            assert self.handle is not None
            self.handle.write(data[:1])
            raise OSError("injected partial key write")

        def __exit__(self, *args: object) -> object:
            return self.context_manager.__exit__(*args)

    real_open = Path.open

    def partial_key_open(path: Path, mode: str = "r", *args: object, **kwargs: object):
        opened = real_open(path, mode, *args, **kwargs)
        if mode == "xb" and "stage-key" in path.name:
            return PartialWrite(opened)
        return opened

    monkeypatch.setattr(Path, "open", partial_key_open)
    with pytest.raises((OSError, SourceDataPromotionError)):
        stage_source_data_batch(
            batch_path, tmp_path / "staging", SourceRegistry.load(registry_path)
        )

    assert not registry_path.with_name(f"{registry_path.name}.stage-key").exists()


def test_direct_revision_rejects_mutated_source_entry_identity(
    tmp_path: Path,
) -> None:
    service, _registry, _staged_path = _imported_service(tmp_path)
    entries = service.store.get_draft_entries(_context(), "source-draft")
    assert entries is not None
    mutated = tuple(
        replace(
            entry,
            data={**entry.data, "label": f"{entry.data['label']} mutated"},
        )
        if index == 0
        else entry
        for index, entry in enumerate(entries)
    )

    with pytest.raises(CatalogStoreError, match="source|receipt|dedicated"):
        service.store.create_revision(
            _context(), "mutated-source-revision", mutated
        )


def test_schema_drift_blocks_delete_draft_without_mutation(tmp_path: Path) -> None:
    db_path = tmp_path / "catalog.db"
    store = CatalogStore(db_path)
    entry = CatalogEntry(
        entry_id="group-delete-drift",
        entry_type=EntryType.GROUP,
        context=_context(),
        source_id="fixture",
        provenance="fixture",
        data={"label": "Delete drift"},
    )
    store.create_draft(_context(), "draft-delete-drift", [entry])
    with sqlite3.connect(db_path) as connection:
        connection.execute("DROP TRIGGER catalog_draft_source_imports_no_delete")
    before = hashlib.sha256(db_path.read_bytes()).hexdigest()

    with pytest.raises(CatalogStoreError, match="schema|fingerprint"):
        store.delete_draft(_context(), "draft-delete-drift", expected_version=1)

    assert hashlib.sha256(db_path.read_bytes()).hexdigest() == before


def test_stage_key_lost_initialization_race_keeps_first_published_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry_path = tmp_path / "sources.json"
    staging_root = tmp_path / "staging"
    staging_root.mkdir()
    _write_registry(registry_path)
    registry = SourceRegistry.load(registry_path)
    assert registry._baseline_parent_identity is not None
    first_published_key = b"F" * 32

    def publish_competing_key(
        _guard: object, _source: object, destination: object
    ) -> None:
        Path(destination).write_bytes(first_published_key)
        raise FileExistsError("competing initializer won")

    monkeypatch.setattr(
        source_registry_module, "_link_in_guard", publish_competing_key
    )
    key = promotion_module._stage_hmac_key(
        registry_path,
        staging_root=staging_root,
        create=True,
        expected_parent_identity=registry._baseline_parent_identity,
    )

    assert key == first_published_key
    assert registry_path.with_name(f"{registry_path.name}.stage-key").read_bytes() == key


def test_direct_revision_rejects_case_variant_source_entry_identity(
    tmp_path: Path,
) -> None:
    service, _registry, _staged_path = _imported_service(tmp_path)
    entries = service.store.get_draft_entries(_context(), "source-draft")
    assert entries is not None
    mutated = tuple(
        replace(
            entry,
            entry_id=entry.entry_id.swapcase(),
            source_id="stripped-source",
            provenance="stripped-provenance",
            data={**entry.data, "label": f"{entry.data['label']} stripped"},
        )
        if index == 0
        else entry
        for index, entry in enumerate(entries)
    )

    with pytest.raises(CatalogStoreError, match="source|receipt|dedicated"):
        service.store.create_revision(
            _context(), "case-variant-source-revision", mutated
        )


def test_publish_rejects_byte_identical_registry_copy_as_wrong_authority(
    tmp_path: Path,
) -> None:
    service, registry, _staged_path = _imported_service(tmp_path)
    assert service.validate_draft(_context(), "source-draft").is_valid
    copied_registry = tmp_path / "copied-sources.json"
    copied_registry.write_bytes(registry.path.read_bytes())

    with pytest.raises(CatalogStoreError, match="registry|authority|path"):
        service.store.publish_validated_draft(
            _context(),
            "source-draft",
            "copied-registry-revision",
            expected_draft_version=1,
            source_registry_path=copied_registry,
        )

    assert service.store.list_revision_ids(_context()) == []


def test_source_import_boundaries_do_not_accept_caller_base_entries(
    tmp_path: Path,
) -> None:
    store = CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        )

    assert "base_entries" not in inspect.signature(
        store.import_staged_source_draft
    ).parameters
    assert "base_entries" not in inspect.signature(
        promotion_module.import_staged_source_data_to_draft
    ).parameters


def test_stage_artifact_cannot_replay_into_another_catalog_database(
    tmp_path: Path,
) -> None:
    _first_service, registry, staged_path = _imported_service(tmp_path)
    second_service = AdminCatalogService(CatalogStore(tmp_path / "catalog-second.db"))

    with pytest.raises(SourceDataPromotionError, match="replay|consumed|already"):
        import_staged_source_data_to_draft(
            staged_path,
            staging_root=staged_path.parent,
            registry=registry,
            service=second_service,
            context=_context(),
            draft_id="cross-db-replay",
            actor_id="operator-f5b-review",
            reason="cross database replay",
        )

    assert second_service.store.get_draft(_context(), "cross-db-replay") is None


@pytest.mark.parametrize("authority_name", ["stage", "index"])
def test_stage_authority_files_reject_hardlinks(
    tmp_path: Path, authority_name: str
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_root = tmp_path / "staging"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, staging_root, registry)
    authority_path = (
        staged_path
        if authority_name == "stage"
        else staging_root / promotion_module._STAGE_INDEX_FILENAME
    )
    authority_alias = tmp_path / f"{authority_name}-authority-hardlink.json"
    promotion_module.os.link(authority_path, authority_alias)
    service = AdminCatalogService(CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        ))

    with pytest.raises(SourceDataPromotionError, match="single-link|authority"):
        import_staged_source_data_to_draft(
            staged_path,
            staging_root=staging_root,
            registry=registry,
            service=service,
            context=_context(),
            draft_id=f"hardlink-{authority_name}",
            actor_id="operator-f5b-review",
            reason="hardlink authority regression",
        )

    assert service.store.get_draft(_context(), f"hardlink-{authority_name}") is None


def test_generic_publish_cannot_launder_source_imported_identity(
    tmp_path: Path,
) -> None:
    service, _registry, _staged_path = _imported_service(tmp_path)
    imported = service.store.get_draft_entries(_context(), "source-draft")
    assert imported is not None
    laundered = tuple(
        replace(
            entry,
            entry_id=entry.entry_id.swapcase(),
            source_id="manual-source",
            provenance="caller-laundered",
        )
        for entry in imported
    )
    service.create_draft(_context(), "generic-laundered", laundered)
    assert service.validate_draft(_context(), "generic-laundered").is_valid

    with pytest.raises(DraftValidationError, match="source|receipt|provenance"):
        service.publish_draft(
            _context(),
            "generic-laundered",
            "revision-laundered",
            expected_draft_version=1,
        )

    assert service.store.list_revision_ids(_context()) == []


def test_import_rejects_caller_selected_registry_after_authority_revocation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authority_path = tmp_path / "configured-authority.json"
    attacker_path = tmp_path / "attacker-registry.json"
    batch_path = tmp_path / "batch.json"
    staging_root = tmp_path / "staging"
    _write_registry(authority_path)
    _write_registry(attacker_path)
    SourceRegistry.load(authority_path).disable_source("admin_source")
    _write_batch(batch_path)
    attacker_registry = SourceRegistry.load(attacker_path)
    staged_path = stage_source_data_batch(
        batch_path,
        staging_root,
        attacker_registry,
    )
    monkeypatch.setattr(
        "core.source_registry.DEFAULT_SOURCE_REGISTRY_PATH",
        authority_path,
    )
    service = AdminCatalogService(CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        ))

    with pytest.raises(SourceDataPromotionError, match="authority|configured registry"):
        import_staged_source_data_to_draft(
            staged_path,
            staging_root=staging_root,
            registry=attacker_registry,
            service=service,
            context=_context(),
            draft_id="attacker-draft",
            actor_id="operator-f5b-review",
            reason="caller-selected registry regression",
        )

    assert service.store.get_draft(_context(), "attacker-draft") is None


def test_pending_stage_recovers_after_catalog_commit_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_root = tmp_path / "staging"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, staging_root, registry)
    service = AdminCatalogService(CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        ))
    real_write_connection = store_module._write_connection

    class CommitFailingConnection:
        def __init__(self, connection: sqlite3.Connection):
            self.connection = connection

        def __getattr__(self, name: str):
            return getattr(self.connection, name)

        def commit(self) -> None:
            raise RuntimeError("synthetic catalog commit failure")

    @contextmanager
    def failing_write_connection(path: Path):
        with real_write_connection(path) as connection:
            yield CommitFailingConnection(connection)

    monkeypatch.setattr(store_module, "_write_connection", failing_write_connection)
    with pytest.raises(RuntimeError, match="synthetic catalog commit failure"):
        import_staged_source_data_to_draft(
            staged_path,
            staging_root=staging_root,
            registry=registry,
            service=service,
            context=_context(),
            draft_id="recover-commit",
            actor_id="operator-f5b-review",
            reason="commit recovery regression",
        )
    assert service.store.get_draft(_context(), "recover-commit") is None
    monkeypatch.setattr(store_module, "_write_connection", real_write_connection)

    result = import_staged_source_data_to_draft(
        staged_path,
        staging_root=staging_root,
        registry=registry,
        service=service,
        context=_context(),
        draft_id="recover-commit",
        actor_id="operator-f5b-review",
        reason="commit recovery regression",
    )

    assert result.draft.draft_id == "recover-commit"
    assert len(service.store.source_import_receipts(_context(), "recover-commit")) == 1


def test_pending_stage_reconciles_commit_before_index_finalize(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_root = tmp_path / "staging"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, staging_root, registry)
    service = AdminCatalogService(CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        ))
    real_commit_stage = promotion_module._commit_registered_stage
    injected = 0

    def fail_stage_commit(*args: object, **kwargs: object) -> None:
        nonlocal injected
        injected += 1
        raise SourceDataPromotionError("synthetic post-commit index failure")

    monkeypatch.setattr(
        promotion_module,
        "_commit_registered_stage",
        fail_stage_commit,
    )
    with pytest.raises(SourceDataPromotionError, match="post-commit index failure"):
        import_staged_source_data_to_draft(
            staged_path,
            staging_root=staging_root,
            registry=registry,
            service=service,
            context=_context(),
            draft_id="recover-finalize",
            actor_id="operator-f5b-review",
            reason="index finalize recovery regression",
        )
    assert injected == 1
    assert service.store.get_draft(_context(), "recover-finalize") is not None
    stored_receipt = service.store.source_import_receipts(
        _context(), "recover-finalize"
    )[0]
    monkeypatch.setattr(
        promotion_module,
        "_commit_registered_stage",
        real_commit_stage,
    )

    result = import_staged_source_data_to_draft(
        staged_path,
        staging_root=staging_root,
        registry=registry,
        service=service,
        context=_context(),
        draft_id="recover-finalize",
        actor_id="operator-f5b-review",
        reason="index finalize recovery regression",
    )

    assert result.receipt.receipt_sha256 == stored_receipt.receipt_sha256
    assert len(service.store.source_import_receipts(_context(), "recover-finalize")) == 1


def test_parallel_first_stage_key_initializers_converge(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_path = tmp_path / "sources.json"
    _write_registry(registry_path)
    first_batch = tmp_path / "batch-a.json"
    second_batch = tmp_path / "batch-b.json"
    _write_batch(first_batch)
    _write_batch(second_batch)
    second_payload = json.loads(second_batch.read_text(encoding="utf-8"))
    second_payload["records"] = [{"id": "group-b", "label": "Group B"}]
    second_batch.write_text(json.dumps(second_payload), encoding="utf-8")
    registry = SourceRegistry.load(registry_path)
    staging_root = tmp_path / "staging"
    staging_root.mkdir()
    real_link = source_registry_module._link_in_guard
    key_barrier = threading.Barrier(2)
    key_link_calls = 0
    call_lock = threading.Lock()

    def synchronized_link(
        guard: object, source: Path | str, target: Path | str
    ) -> None:
        nonlocal key_link_calls
        if str(target).endswith(".stage-key"):
            with call_lock:
                key_link_calls += 1
            key_barrier.wait(timeout=5)
        real_link(guard, Path(source), Path(target))

    monkeypatch.setattr(source_registry_module, "_link_in_guard", synchronized_link)
    with ThreadPoolExecutor(max_workers=2) as executor:
        keys = tuple(
            executor.map(
                lambda _index: promotion_module._stage_hmac_key(
                    registry_path,
                    staging_root=staging_root,
                    create=True,
                    expected_parent_identity=registry._baseline_parent_identity,
                ),
                range(2),
            )
        )

    assert key_link_calls == 2
    assert keys[0] == keys[1]
    staged_paths = tuple(
        stage_source_data_batch(batch, staging_root, registry)
        for batch in (first_batch, second_batch)
    )
    assert len(set(staged_paths)) == 2
    assert registry_path.with_name("sources.json.stage-key").stat().st_size == 32
    for staged_path in staged_paths:
        validate_staged_source_artifact(
            staged_path,
            staging_root=staging_root,
            registry=registry,
        )


def test_stage_index_swap_during_authority_read_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_root = tmp_path / "staging"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, staging_root, registry)
    service = AdminCatalogService(CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        ))
    index_path = staging_root / promotion_module._STAGE_INDEX_FILENAME
    real_load_json_bytes = promotion_module._load_json_bytes
    injected = 0

    def swapping_index_load(raw: bytes):
        nonlocal injected
        payload = real_load_json_bytes(raw)
        if payload.get("schema") == promotion_module._STAGE_INDEX_SCHEMA and injected == 0:
            injected += 1
            replacement = index_path.with_name("replacement-index.json")
            replacement.write_text(json.dumps(payload), encoding="utf-8")
            promotion_module.os.replace(replacement, index_path)
        return payload

    monkeypatch.setattr(promotion_module, "_load_json_bytes", swapping_index_load)
    with pytest.raises((SourceDataPromotionError, OSError)):
        import_staged_source_data_to_draft(
            staged_path,
            staging_root=staging_root,
            registry=registry,
            service=service,
            context=_context(),
            draft_id="index-swap",
            actor_id="operator-f5b-review",
            reason="index swap regression",
        )

    assert injected == 1
    assert service.store.get_draft(_context(), "index-swap") is None


def test_stage_index_transition_rejects_parent_substitution_after_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_parent = tmp_path / "registry-authority"
    staging_root = tmp_path / "stage-authority"
    displaced_root = tmp_path / "stage-authority-displaced"
    registry_parent.mkdir()
    registry_path = registry_parent / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    monkeypatch.setattr(
        source_registry_module,
        "DEFAULT_SOURCE_REGISTRY_PATH",
        registry_path,
    )
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, staging_root, registry)
    service = AdminCatalogService(
        CatalogStore(
            tmp_path / "catalog.db",
            validation_key_provider=_validation_provider(),
        )
    )
    index_path = staging_root / promotion_module._STAGE_INDEX_FILENAME
    index_before = index_path.read_bytes()
    initial_attributes = promotion_module.os.lstat(staging_root)
    original_identity = initial_attributes.st_dev, initial_attributes.st_ino
    lock_root = tmp_path / "synthetic-lock-authority"
    lock_root.mkdir()
    real_lock = promotion_module._registry_lock
    real_replace = promotion_module._atomic_replace_json
    injected = 0
    swap_succeeded = False
    recreated_identity: tuple[int, int] | None = None

    def relocated_index_lock(
        path: Path,
        *args: object,
        **kwargs: object,
    ) -> object:
        if path == index_path:
            return real_lock(lock_root / "stage-index", *args, **kwargs)
        return real_lock(path, *args, **kwargs)

    def swap_parent_then_replace(
        target: Path,
        payload: object,
        *args: object,
        **kwargs: object,
    ) -> None:
        nonlocal injected, recreated_identity, swap_succeeded
        if target == index_path and injected == 0:
            injected += 1
            promotion_module.os.replace(staging_root, displaced_root)
            swap_succeeded = True
            staging_root.mkdir()
            recreated_attributes = promotion_module.os.lstat(staging_root)
            recreated_identity = (
                recreated_attributes.st_dev,
                recreated_attributes.st_ino,
            )
        real_replace(target, payload, *args, **kwargs)

    monkeypatch.setattr(
        promotion_module, "_atomic_replace_json", swap_parent_then_replace
    )
    monkeypatch.setattr(promotion_module, "_registry_lock", relocated_index_lock)
    failure: BaseException | None = None
    try:
        import_staged_source_data_to_draft(
            staged_path,
            staging_root=staging_root,
            registry=registry,
            service=service,
            context=_context(),
            draft_id="parent-swap-draft",
            actor_id="operator-f5b-review",
            reason="stage index parent substitution",
        )
    except (SourceDataPromotionError, SourceRegistryError) as exc:
        failure = exc

    assert injected == 1
    assert swap_succeeded is True
    assert recreated_identity is not None
    assert recreated_identity != original_identity
    assert failure is not None
    assert (displaced_root / index_path.name).read_bytes() == index_before
    assert list(staging_root.iterdir()) == []
    assert service.store.get_draft(_context(), "parent-swap-draft") is None


def test_stage_index_commit_rejects_parent_substitution_and_retry_recovers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_parent = tmp_path / "registry-authority"
    staging_root = tmp_path / "stage-authority"
    displaced_root = tmp_path / "stage-authority-displaced"
    registry_parent.mkdir()
    registry_path = registry_parent / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    monkeypatch.setattr(
        source_registry_module,
        "DEFAULT_SOURCE_REGISTRY_PATH",
        registry_path,
    )
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, staging_root, registry)
    service = AdminCatalogService(
        CatalogStore(
            tmp_path / "catalog.db",
            validation_key_provider=_validation_provider(),
        )
    )
    index_path = staging_root / promotion_module._STAGE_INDEX_FILENAME
    original_attributes = promotion_module.os.lstat(staging_root)
    original_identity = original_attributes.st_dev, original_attributes.st_ino
    lock_root = tmp_path / "synthetic-lock-authority"
    lock_root.mkdir()
    real_lock = promotion_module._registry_lock
    real_replace = promotion_module._atomic_replace_json
    transition_writes = 0
    injected = 0
    pending_index_bytes = b""
    recreated_identity: tuple[int, int] | None = None

    def relocated_index_lock(
        path: Path,
        *args: object,
        **kwargs: object,
    ) -> object:
        if path == index_path:
            return real_lock(lock_root / "stage-index", *args, **kwargs)
        return real_lock(path, *args, **kwargs)

    def swap_parent_on_commit(
        target: Path,
        payload: object,
        *args: object,
        **kwargs: object,
    ) -> None:
        nonlocal transition_writes, injected, pending_index_bytes, recreated_identity
        if target == index_path:
            transition_writes += 1
            if transition_writes == 2:
                pending_index_bytes = index_path.read_bytes()
                promotion_module.os.replace(staging_root, displaced_root)
                staging_root.mkdir()
                recreated_attributes = promotion_module.os.lstat(staging_root)
                recreated_identity = (
                    recreated_attributes.st_dev,
                    recreated_attributes.st_ino,
                )
                injected += 1
        real_replace(target, payload, *args, **kwargs)

    monkeypatch.setattr(
        promotion_module,
        "_atomic_replace_json",
        swap_parent_on_commit,
    )
    monkeypatch.setattr(promotion_module, "_registry_lock", relocated_index_lock)

    with pytest.raises((SourceDataPromotionError, SourceRegistryError)):
        import_staged_source_data_to_draft(
            staged_path,
            staging_root=staging_root,
            registry=registry,
            service=service,
            context=_context(),
            draft_id="commit-parent-swap",
            actor_id="operator-f5b-review",
            reason="stage index commit parent substitution",
        )

    assert transition_writes == 2
    assert injected == 1
    assert recreated_identity is not None
    assert recreated_identity != original_identity
    assert pending_index_bytes
    assert (displaced_root / index_path.name).read_bytes() == pending_index_bytes
    assert list(staging_root.iterdir()) == []
    assert service.store.get_draft(_context(), "commit-parent-swap") is not None

    monkeypatch.setattr(promotion_module, "_atomic_replace_json", real_replace)
    staging_root.rmdir()
    promotion_module.os.replace(displaced_root, staging_root)
    result = import_staged_source_data_to_draft(
        staged_path,
        staging_root=staging_root,
        registry=registry,
        service=service,
        context=_context(),
        draft_id="commit-parent-swap",
        actor_id="operator-f5b-review",
        reason="stage index commit parent substitution",
    )

    assert result.draft.draft_id == "commit-parent-swap"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    entry = next(
        item for item in index["entries"] if item["artifact_id"] == result.receipt.artifact_id
    )
    assert entry["consumption_state"] == "committed"


def test_registry_swap_during_json_parse_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry_path = tmp_path / "sources.json"
    revoked_path = tmp_path / "revoked-sources.json"
    _write_registry(registry_path)
    active_bytes = registry_path.read_bytes()
    SourceRegistry.load(registry_path).disable_source("admin_source")
    promotion_module.os.replace(registry_path, revoked_path)
    registry_path.write_bytes(active_bytes)
    real_loads = source_registry_module.json.loads
    injected = 0

    def restore_revoked_registry(*args: object, **kwargs: object):
        nonlocal injected
        payload = real_loads(*args, **kwargs)
        if injected == 0:
            injected += 1
            promotion_module.os.replace(revoked_path, registry_path)
        return payload

    monkeypatch.setattr(source_registry_module.json, "loads", restore_revoked_registry)
    with pytest.raises(SourceRegistryError, match="identity|changed|authority"):
        SourceRegistry.load(registry_path)

    assert injected == 1


def test_stage_key_swap_after_read_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_root = tmp_path / "staging"
    _write_registry(registry_path)
    _write_batch(batch_path)
    stage_source_data_batch(
        batch_path, staging_root, SourceRegistry.load(registry_path)
    )
    key_path = registry_path.with_name("sources.json.stage-key")
    original_key_path = tmp_path / "original.stage-key"
    promotion_module.os.replace(key_path, original_key_path)
    key_path.write_bytes(b"A" * 32)
    real_open = promotion_module.os.open
    injected = 0

    def swapping_open(path: object, flags: int, *args: object) -> int:
        nonlocal injected
        if Path(path) == key_path and injected == 0:
            injected += 1
            descriptor = real_open(path, flags, *args)
            promotion_module.os.replace(original_key_path, key_path)
            return descriptor
        return real_open(path, flags, *args)

    monkeypatch.setattr(promotion_module.os, "open", swapping_open)
    with pytest.raises(SourceDataPromotionError, match="identity|changed|authority"):
        promotion_module._stage_hmac_key(
            registry_path,
            staging_root=staging_root,
            create=False,
            expected_parent_identity=None,
        )

    assert injected == 1


def test_pending_stage_cannot_move_to_same_draft_id_in_other_context(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_root = tmp_path / "staging"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, staging_root, registry)
    service = AdminCatalogService(CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        ))
    original_context = _context()
    other_context = CatalogContext(
        operator_id="operator-other",
        workspace_id=original_context.workspace_id,
        tenant_id=original_context.tenant_id,
        scope=original_context.scope,
    )
    with promotion_module._prepare_source_data_draft_import(
        staged_path,
        staging_root=staging_root,
        registry=registry,
        service=service,
        context=original_context,
        draft_id="shared-draft",
        actor_id=original_context.operator_id,
        reason="reserve original context",
        catalog_authority_path=service.store.db_path,
    ) as prepared:
        promotion_module._reserve_registered_stage(
            staged_path,
            staging_root,
            prepared.receipt,
            registry.path,
            service.store.db_path,
            prepared.stage_parent_identity,
            prepared.registry_parent_identity,
        )

    with pytest.raises(SourceDataPromotionError, match="context|reserved|authority"):
        import_staged_source_data_to_draft(
            staged_path,
            staging_root=staging_root,
            registry=registry,
            service=service,
            context=other_context,
            draft_id="shared-draft",
            actor_id=other_context.operator_id,
            reason="cross-context pending takeover",
        )

    assert service.store.get_draft(other_context, "shared-draft") is None


def test_module_raw_connection_and_revision_insert_are_not_composable(
    tmp_path: Path,
) -> None:
    service, _registry, _staged_path = _imported_service(tmp_path)
    imported = service.store.get_draft_entries(_context(), "source-draft")
    assert imported is not None
    laundered = tuple(
        replace(entry, source_id="manual", provenance="stripped")
        for entry in imported
    )
    write_connection = getattr(store_module, "_write_connection", None)
    insert_revision = getattr(store_module, "_insert_revision", None)

    if callable(write_connection) and callable(insert_revision):
        with write_connection(service.store.db_path) as connection:
            insert_revision(
                connection,
                _context(),
                "raw-helper-bypass",
                laundered,
                source_draft_id=None,
            )

    assert not (callable(write_connection) and callable(insert_revision))
    assert "raw-helper-bypass" not in service.store.list_revision_ids(_context())


def test_base_revision_identity_is_not_poisoned_by_source_import(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_root = tmp_path / "staging"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, staging_root, registry)
    service = AdminCatalogService(CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        ))
    base = CatalogEntry(
        entry_type=EntryType.GROUP,
        entry_id="group-base",
        context=_context(),
        source_id="manual",
        provenance="manual-base",
        data={"label": "Manual Base"},
    )
    service.store.create_revision(_context(), "base-revision", [base])
    import_staged_source_data_to_draft(
        staged_path,
        staging_root=staging_root,
        registry=registry,
        service=service,
        context=_context(),
        draft_id="source-with-base",
        actor_id=_context().operator_id,
        reason="source import over manual base",
        base_revision_id="base-revision",
    )
    service.create_draft(_context(), "manual-base-only", [base])
    assert service.validate_draft(_context(), "manual-base-only").is_valid

    published = service.publish_draft(
        _context(),
        "manual-base-only",
        "manual-base-republished",
        expected_draft_version=1,
    )

    assert published.revision_id == "manual-base-republished"
    assert service.store.get_revision_entries(
        _context(), "manual-base-republished"
    ) == (base,)


def test_registry_and_key_reject_authority_substitution_during_resolution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry_path = tmp_path / "sources.json"
    foreign_registry_path = tmp_path / "foreign-sources.json"
    _write_registry(registry_path)
    _write_registry(foreign_registry_path)
    key_path = registry_path.with_name(f"{registry_path.name}.stage-key")
    foreign_key_path = tmp_path / "foreign.stage-key"
    key_path.write_bytes(b"K" * 32)
    foreign_key_path.write_bytes(b"F" * 32)
    real_resolve = Path.resolve
    registry_injections = 0
    key_injections = 0

    def substitute_resolution(path: Path, *args: object, **kwargs: object) -> Path:
        nonlocal registry_injections, key_injections
        if path == registry_path:
            registry_injections += 1
            return foreign_registry_path
        if path == key_path:
            key_injections += 1
            return foreign_key_path
        return real_resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", substitute_resolution)
    with pytest.raises(SourceRegistryError, match="authority|path|identity|resolved"):
        SourceRegistry.load(registry_path)
    with pytest.raises(SourceDataPromotionError, match="authority|key|path|identity"):
        promotion_module._stage_hmac_key(
            registry_path,
            staging_root=tmp_path / "staging",
            create=False,
            expected_parent_identity=None,
        )

    assert registry_injections >= 1
    assert key_injections >= 1


def test_stage_authority_read_binds_open_handle_to_original_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_root = tmp_path / "staging"
    _write_registry(registry_path)
    _write_batch(batch_path)
    staged_path = stage_source_data_batch(
        batch_path, staging_root, SourceRegistry.load(registry_path)
    )
    original_path = tmp_path / "original.batch.json"
    foreign_path = tmp_path / "foreign.batch.json"
    foreign_path.write_bytes(staged_path.read_bytes())
    real_open = promotion_module.os.open
    injected = 0

    def swap_around_open(path: object, flags: int, *args: object) -> int:
        nonlocal injected
        if Path(path) == staged_path and injected == 0:
            injected += 1
            promotion_module.os.replace(staged_path, original_path)
            promotion_module.os.replace(foreign_path, staged_path)
            descriptor = real_open(path, flags, *args)
            promotion_module.os.replace(staged_path, foreign_path)
            promotion_module.os.replace(original_path, staged_path)
            return descriptor
        return real_open(path, flags, *args)

    monkeypatch.setattr(promotion_module.os, "open", swap_around_open)
    with pytest.raises(SourceDataPromotionError, match="identity|authority|changed"):
        promotion_module._load_stage_authority_json(staged_path)

    assert injected == 1


def test_generic_publish_rejects_live_draft_payload_hash_mismatch(
    tmp_path: Path,
) -> None:
    service = AdminCatalogService(CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        ))
    context = _context()
    original = CatalogEntry(
        entry_type=EntryType.GROUP,
        entry_id="group-a",
        context=context,
        source_id="manual",
        provenance="manual",
        data={"label": "Original"},
    )
    altered = replace(original, data={"label": "Altered"})
    service.create_draft(context, "generic-tamper", [original])
    assert service.validate_draft(context, "generic-tamper").is_valid
    altered_payload_json = store_module._entries_payload(context, (altered,))[2]
    with sqlite3.connect(service.store.db_path) as connection:
        connection.execute(
            """
            UPDATE catalog_drafts SET payload_json = ?
            WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
              AND scope = ? AND draft_id = ?
            """,
            (altered_payload_json, *store_module._context_values(context), "generic-tamper"),
        )

    with pytest.raises(DraftValidationError, match="payload|hash|integrity"):
        service.publish_draft(
            context,
            "generic-tamper",
            "generic-tamper-revision",
            expected_draft_version=1,
        )
    assert service.store.list_revision_ids(context) == []


def test_source_publish_rejects_live_draft_payload_outside_receipt(
    tmp_path: Path,
) -> None:
    service, registry, _staged_path = _imported_service(tmp_path)
    context = _context()
    original = service.store.get_draft_entries(context, "source-draft")
    assert original is not None
    altered = replace(original[0], data={**original[0].data, "label": "Altered"})
    altered_payload_json = store_module._entries_payload(context, (altered,))[2]
    with sqlite3.connect(service.store.db_path) as connection:
        connection.execute(
            """
            UPDATE catalog_drafts SET payload_json = ?
            WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
              AND scope = ? AND draft_id = ?
            """,
            (altered_payload_json, *store_module._context_values(context), "source-draft"),
        )

    with pytest.raises(SourceDataPromotionError, match="payload|hash|receipt|integrity"):
        promotion_module.publish_source_imported_draft(
            registry=registry,
            service=service,
            context=context,
            draft_id="source-draft",
            revision_id="source-tamper-revision",
            expected_draft_version=1,
        )
    assert service.store.list_revision_ids(context) == []


def test_publish_rejects_coherent_draft_validation_marker_tampering(
    tmp_path: Path,
) -> None:
    context = _context()
    service = AdminCatalogService(CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        ))
    original = CatalogEntry(
        entry_id="original-group",
        entry_type=EntryType.GROUP,
        context=context,
        source_id="manual",
        provenance="manual",
        data={"label": "Original"},
    )
    replacement = CatalogEntry(
        entry_id="replacement-group",
        entry_type=EntryType.GROUP,
        context=context,
        source_id="manual",
        provenance="manual",
        data={"label": "Never validated"},
    )
    service.create_draft(context, "coherent-tamper", [original])
    assert service.validate_draft(context, "coherent-tamper").is_valid
    replacement_json = store_module._entries_payload(context, (replacement,))[2]
    replacement_hash = hashlib.sha256(replacement_json.encode("utf-8")).hexdigest()
    with sqlite3.connect(service.store.db_path) as connection:
        connection.execute(
            """
            UPDATE catalog_drafts
            SET payload_json = ?, payload_hash = ?, validated_payload_hash = ?
            WHERE operator_id = ? AND workspace_id = ? AND tenant_id = ?
              AND scope = ? AND draft_id = ?
            """,
            (
                replacement_json,
                replacement_hash,
                replacement_hash,
                *store_module._context_values(context),
                "coherent-tamper",
            ),
        )

    with pytest.raises(DraftValidationError, match="validation|attestation|payload"):
        service.publish_draft(
            context,
            "coherent-tamper",
            "coherent-tamper-revision",
            expected_draft_version=1,
        )
    assert service.store.list_revision_ids(context) == []


def test_validation_attestation_rows_are_append_only(tmp_path: Path) -> None:
    context = _context()
    service = AdminCatalogService(CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        ))
    entry = CatalogEntry(
        entry_id="attested-group",
        entry_type=EntryType.GROUP,
        context=context,
        source_id="manual",
        provenance="manual",
        data={"label": "Attested"},
    )
    service.create_draft(context, "attestation-immutable", [entry])
    assert service.validate_draft(context, "attestation-immutable").is_valid

    with sqlite3.connect(service.store.db_path) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="attestation is immutable"):
            connection.execute(
                """
                UPDATE catalog_draft_validation_attestations
                SET payload_hash = ? WHERE draft_id = ?
                """,
                ("f" * 64, "attestation-immutable"),
            )
        with pytest.raises(sqlite3.IntegrityError, match="attestation is immutable"):
            connection.execute(
                "DELETE FROM catalog_draft_validation_attestations WHERE draft_id = ?",
                ("attestation-immutable",),
            )


def test_publish_rejects_directly_inserted_forged_validation_attestation(
    tmp_path: Path,
) -> None:
    context = _context()
    provider = _validation_provider()
    service = AdminCatalogService(
        CatalogStore(tmp_path / "catalog-forged.db", validation_key_provider=provider)
    )
    original = CatalogEntry(
        entry_id="original-attested-group",
        entry_type=EntryType.GROUP,
        context=context,
        source_id="manual",
        provenance="manual",
        data={"label": "Original"},
    )
    replacement = CatalogEntry(
        entry_id="forged-attested-group",
        entry_type=EntryType.GROUP,
        context=context,
        source_id="manual",
        provenance="manual",
        data={"label": "Forged"},
    )
    service.create_draft(context, "forged-attestation", [original])
    assert service.validate_draft(context, "forged-attestation").is_valid
    replacement_json = store_module._entries_payload(context, (replacement,))[2]
    replacement_hash = hashlib.sha256(replacement_json.encode("utf-8")).hexdigest()
    with sqlite3.connect(service.store.db_path) as connection:
        connection.execute(
            """
            UPDATE catalog_drafts
            SET payload_json = ?, payload_hash = ?, validated_payload_hash = ?
            WHERE draft_id = ?
            """,
            (
                replacement_json,
                replacement_hash,
                replacement_hash,
                "forged-attestation",
            ),
        )
        connection.execute(
            """
            INSERT INTO catalog_draft_validation_attestations (
                operator_id, workspace_id, tenant_id, scope,
                draft_id, draft_version, payload_hash, policy_version,
                catalog_schema_version, attestation_format_version,
                authority_id, key_id, algorithm, validated_at, attestation_hmac
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                context.operator_id,
                context.workspace_id,
                context.tenant_id,
                context.scope,
                "forged-attestation",
                1,
                replacement_hash,
                "catalog-validation-v1",
                8,
                1,
                provider.authority_id,
                provider.active_key_id(),
                "HMAC-SHA256",
                "2026-07-15T23:00:00+00:00",
                "00" * 32,
            ),
        )

    with pytest.raises(CatalogStoreError, match="authenticated validation attestation"):
        service.store.publish_validated_draft(
            context,
            "forged-attestation",
            "revision-forged-attestation",
            expected_draft_version=1,
        )

    assert service.store.list_revision_ids(context) == []


def test_draft_validation_fails_closed_without_external_key_provider(
    tmp_path: Path,
) -> None:
    service = AdminCatalogService(CatalogStore(tmp_path / "catalog.db"))
    context = _context()
    entry = CatalogEntry(
        entry_id="provider-required-group",
        entry_type=EntryType.GROUP,
        context=context,
        source_id="manual",
        provenance="manual",
        data={"label": "Provider required"},
    )
    draft = service.create_draft(context, "provider-required", [entry])
    payload_json = store_module._entries_payload(context, (entry,))[2]
    payload_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

    with pytest.raises(CatalogStoreError, match="validation key provider"):
        service.store.mark_draft_validated(
            context,
            draft.draft_id,
            expected_version=draft.version,
            expected_payload_hash=payload_hash,
        )

    assert service.store.get_draft(context, draft.draft_id)["validated_version"] is None


def test_pending_reservation_rejects_changed_approval_semantics(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_root = tmp_path / "staging"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, staging_root, registry)
    service = AdminCatalogService(CatalogStore(
            tmp_path / "catalog.db", validation_key_provider=_validation_provider()
        ))
    context = _context()
    with promotion_module._prepare_source_data_draft_import(
        staged_path,
        staging_root=staging_root,
        registry=registry,
        service=service,
        context=context,
        draft_id="approval-bound",
        actor_id="operator-original",
        reason="original approval",
        catalog_authority_path=service.store.db_path,
    ) as prepared:
        promotion_module._reserve_registered_stage(
            staged_path,
            staging_root,
            prepared.receipt,
            registry.path,
            service.store.db_path,
            prepared.stage_parent_identity,
            prepared.registry_parent_identity,
        )
    index_path = staging_root / promotion_module._STAGE_INDEX_FILENAME
    reserved_bytes = index_path.read_bytes()

    with pytest.raises(SourceDataPromotionError, match="approval|receipt|reserved|identity"):
        import_staged_source_data_to_draft(
            staged_path,
            staging_root=staging_root,
            registry=registry,
            service=service,
            context=context,
            draft_id="approval-bound",
            actor_id="operator-changed",
            reason="changed approval",
        )

    assert index_path.read_bytes() == reserved_bytes
    assert service.store.get_draft(context, "approval-bound") is None
