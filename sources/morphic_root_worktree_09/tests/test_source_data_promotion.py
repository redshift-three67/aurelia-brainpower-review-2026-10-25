from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import core.source_data_promotion as promotion_module
import core.source_registry as registry_module
from core.source_data_promotion import (
    SourceDataPromotionError,
    promote_staged_source_data,
    stage_source_data_batch,
)
from core.source_registry import SourceRegistry, SourceRegistryError


def _write_registry(
    path: Path,
    *,
    enabled: bool = True,
    status: str = "active",
    import_policy: str = "manual_review",
    return_status_on_disable: str = "",
) -> None:
    source: dict[str, object] = {
        "id": "admin_terms",
        "label": "Admin Terms",
        "source_type": "local_import",
        "local_path": str(path.parent / "terms"),
        "license": "admin-provided",
        "trust_level": "admin_curated",
        "import_policy": import_policy,
        "scopes": ["terminology"],
        "enabled": enabled,
        "status": status,
    }
    if return_status_on_disable:
        source["return_status_on_disable"] = return_status_on_disable
    path.write_text(
        json.dumps(
            {"schema_version": 1, "revision": 0, "rollback_history": [], "sources": [source]}
        ),
        encoding="utf-8",
    )


def _write_batch(path: Path, *, source_id: str = "admin_terms") -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_id": source_id,
                "source_version": "2026-07-14",
                "data_type": "terminology",
                "license": "admin-provided",
                "retrieval_metadata": {
                    "retrieved_at": "2026-07-14T20:00:00+00:00",
                    "method": "local_admin_import",
                },
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


def _directory_identity(path: Path) -> tuple[int, int]:
    attributes = os.lstat(path)
    return attributes.st_dev, attributes.st_ino


def _capture_security_failure(operation: object) -> BaseException | None:
    try:
        operation()
    except (SourceDataPromotionError, SourceRegistryError) as exc:
        return exc
    return None


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


def test_source_data_stage_rejects_parent_substitution_before_publish(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_parent = tmp_path / "registry-authority"
    staging_root = tmp_path / "stage-authority"
    displaced_root = tmp_path / "stage-authority-displaced"
    registry_parent.mkdir()
    staging_root.mkdir()
    sentinel = staging_root / "sentinel.txt"
    sentinel.write_bytes(b"original-stage-parent\n")
    sentinel_before = sentinel.read_bytes()
    original_identity = _directory_identity(staging_root)
    registry_path = registry_parent / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    real_publish = promotion_module._atomic_publish_json
    injected = 0
    swap_succeeded = False
    recreated_identity: tuple[int, int] | None = None

    def swap_parent_then_publish(
        target: Path,
        payload: object,
        *args: object,
        **kwargs: object,
    ) -> None:
        nonlocal injected, recreated_identity, swap_succeeded
        if target.parent == staging_root and target.name.endswith(".batch.json"):
            injected += 1
            os.replace(staging_root, displaced_root)
            swap_succeeded = True
            staging_root.mkdir()
            recreated_identity = _directory_identity(staging_root)
        real_publish(target, payload, *args, **kwargs)

    monkeypatch.setattr(
        promotion_module, "_atomic_publish_json", swap_parent_then_publish
    )
    failure = _capture_security_failure(
        lambda: stage_source_data_batch(
            batch_path,
            staging_root,
            SourceRegistry.load(registry_path),
        )
    )

    assert injected == 1
    assert swap_succeeded is True
    assert recreated_identity is not None
    assert recreated_identity != original_identity
    assert failure is not None
    assert "authority" in str(failure).lower()
    assert (displaced_root / sentinel.name).read_bytes() == sentinel_before
    assert not list(displaced_root.glob("*.batch.json"))
    assert list(staging_root.iterdir()) == []


def test_stage_registration_failure_retains_unregistered_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_path = tmp_path / "sources.json"
    staging_root = tmp_path / "staging"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    real_register = promotion_module._register_staged_artifact

    def fail_registration(*args: object, **kwargs: object) -> None:
        raise SourceDataPromotionError("synthetic stage registration failure")

    monkeypatch.setattr(
        promotion_module,
        "_register_staged_artifact",
        fail_registration,
    )

    with pytest.raises(SourceDataPromotionError, match="registration failure"):
        stage_source_data_batch(
            batch_path,
            staging_root,
            SourceRegistry.load(registry_path),
        )

    staged_files = list(staging_root.glob("*.batch.json"))
    assert len(staged_files) == 1
    assert not (staging_root / promotion_module._STAGE_INDEX_FILENAME).exists()

    monkeypatch.setattr(
        promotion_module,
        "_register_staged_artifact",
        real_register,
    )
    recovered = stage_source_data_batch(
        batch_path,
        staging_root,
        SourceRegistry.load(registry_path),
    )
    assert recovered == staged_files[0]
    assert (staging_root / promotion_module._STAGE_INDEX_FILENAME).exists()
    with pytest.raises(SourceDataPromotionError, match="duplicate|replay|registered"):
        stage_source_data_batch(
            batch_path,
            staging_root,
            SourceRegistry.load(registry_path),
        )


def test_unbound_registry_rejects_stage_before_creating_target_directory(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_root = tmp_path / "missing-stage-root"
    _write_registry(registry_path)
    _write_batch(batch_path)
    loaded = SourceRegistry.load(registry_path)
    unbound = SourceRegistry(
        registry_path,
        loaded.list_sources(),
        schema_version=loaded.schema_version,
        revision=loaded.revision,
        rollback_history=loaded.rollback_history,
    )
    batch = promotion_module._validate_batch(
        json.loads(batch_path.read_text(encoding="utf-8"))
    )

    with pytest.raises(SourceDataPromotionError, match="parent identity"):
        promotion_module._stage_source_data_batch_locked(
            batch,
            staging_root,
            unbound,
            quarantine_dir=None,
        )

    assert not staging_root.exists()


def test_stage_index_registration_rejects_parent_substitution_after_stage_publish(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_parent = tmp_path / "registry-authority"
    staging_root = tmp_path / "stage-authority"
    displaced_root = tmp_path / "stage-authority-displaced"
    registry_parent.mkdir()
    staging_root.mkdir()
    original_identity = _directory_identity(staging_root)
    registry_path = registry_parent / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    real_register = promotion_module._register_staged_artifact
    injected = 0
    staged_name = ""
    staged_bytes = b""
    recreated_identity: tuple[int, int] | None = None

    def swap_parent_before_registration(
        root: Path,
        staged_path: Path,
        staged: object,
        registry_authority: Path,
        *args: object,
        **kwargs: object,
    ) -> None:
        nonlocal injected, staged_name, staged_bytes, recreated_identity
        injected += 1
        staged_name = staged_path.name
        staged_bytes = staged_path.read_bytes()
        os.replace(staging_root, displaced_root)
        staging_root.mkdir()
        recreated_identity = _directory_identity(staging_root)
        (staging_root / staged_name).write_bytes(staged_bytes)
        real_register(
            root,
            staged_path,
            staged,
            registry_authority,
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        promotion_module,
        "_register_staged_artifact",
        swap_parent_before_registration,
    )
    failure = _capture_security_failure(
        lambda: stage_source_data_batch(
            batch_path,
            staging_root,
            SourceRegistry.load(registry_path),
        )
    )

    assert injected == 1
    assert recreated_identity is not None
    assert recreated_identity != original_identity
    assert failure is not None
    assert staged_name
    assert (displaced_root / staged_name).read_bytes() == staged_bytes
    assert not (displaced_root / promotion_module._STAGE_INDEX_FILENAME).exists()
    assert not (staging_root / promotion_module._STAGE_INDEX_FILENAME).exists()


def test_stage_index_registration_rejects_parent_substitution_after_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_parent = tmp_path / "registry-authority"
    staging_root = tmp_path / "stage-authority"
    displaced_root = tmp_path / "stage-authority-displaced"
    registry_parent.mkdir()
    registry_path = registry_parent / "sources.json"
    first_batch_path = tmp_path / "batch-1.json"
    second_batch_path = tmp_path / "batch-2.json"
    _write_registry(registry_path)
    _write_batch(first_batch_path)
    registry = SourceRegistry.load(registry_path)
    stage_source_data_batch(first_batch_path, staging_root, registry)
    index_path = staging_root / promotion_module._STAGE_INDEX_FILENAME
    index_before = index_path.read_bytes()
    original_identity = _directory_identity(staging_root)
    _write_batch(second_batch_path)
    second_payload = json.loads(second_batch_path.read_text(encoding="utf-8"))
    second_payload["records"][0]["id"] = "lunge"
    second_batch_path.write_text(json.dumps(second_payload), encoding="utf-8")
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
        if target == index_path:
            injected += 1
            os.replace(staging_root, displaced_root)
            swap_succeeded = True
            staging_root.mkdir()
            recreated_identity = _directory_identity(staging_root)
        real_replace(target, payload, *args, **kwargs)

    monkeypatch.setattr(
        promotion_module, "_atomic_replace_json", swap_parent_then_replace
    )
    monkeypatch.setattr(promotion_module, "_registry_lock", relocated_index_lock)
    failure = _capture_security_failure(
        lambda: stage_source_data_batch(second_batch_path, staging_root, registry)
    )

    assert injected == 1
    assert swap_succeeded is True
    assert recreated_identity is not None
    assert recreated_identity != original_identity
    assert failure is not None
    assert (displaced_root / index_path.name).read_bytes() == index_before
    assert list(staging_root.iterdir()) == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("id", None),
        ("id", 7),
        ("label", False),
        ("label", {"text": "invalid"}),
    ],
)
def test_source_data_records_require_real_nonempty_strings(
    tmp_path: Path,
    field: str,
    value: object,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    payload = json.loads(batch_path.read_text(encoding="utf-8"))
    payload["records"][0][field] = value
    batch_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(SourceDataPromotionError, match="non-empty string"):
        stage_source_data_batch(
            batch_path,
            tmp_path / "staging",
            SourceRegistry.load(registry_path),
        )


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
    ledger_path = tmp_path / "missing-ledger-parent" / "ledger.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    staged_path = stage_source_data_batch(batch_path, tmp_path / "staging", SourceRegistry.load(registry_path))
    registry_lock = registry_path.with_name(f".{registry_path.name}.lock")
    registry_lock.unlink(missing_ok=True)

    plan = promote_staged_source_data(
        staged_path,
        ledger_path,
        registry=SourceRegistry.load(registry_path),
        dry_run=True,
    )

    assert plan["source_id"] == "admin_terms"
    assert plan["record_count"] == 1
    assert plan["dry_run"] is True
    assert not ledger_path.exists()
    assert not ledger_path.parent.exists()
    assert not registry_lock.exists()


def test_source_data_dry_run_validates_existing_ledger_and_replay(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    ledger_path = tmp_path / "ledger.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, tmp_path / "staging", registry)
    ledger_path.write_text(
        json.dumps({"schema": "legacy", "schema_version": 1, "promotions": []}),
        encoding="utf-8",
    )

    with pytest.raises(SourceDataPromotionError, match="ledger|schema"):
        promote_staged_source_data(
            staged_path,
            ledger_path,
            registry=registry,
            dry_run=True,
        )

    ledger_path.unlink()
    promote_staged_source_data(staged_path, ledger_path, registry=registry)
    before = ledger_path.read_bytes()
    with pytest.raises(SourceDataPromotionError, match="replay|Duplicate"):
        promote_staged_source_data(
            staged_path,
            ledger_path,
            registry=registry,
            dry_run=True,
        )
    assert ledger_path.read_bytes() == before


def test_source_data_promotion_writes_consistency_ledger(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    ledger_path = tmp_path / "ledger.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    staged_path = stage_source_data_batch(batch_path, tmp_path / "staging", SourceRegistry.load(registry_path))

    result = promote_staged_source_data(
        staged_path,
        ledger_path,
        registry=SourceRegistry.load(registry_path),
    )

    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert result["dry_run"] is False
    assert ledger["schema"] == "morphic_source_data_consistency_ledger"
    assert ledger["schema_version"] == 3
    assert len(ledger["entries"]) == 1
    assert ledger["entries"][0]["source_id"] == "admin_terms"
    assert ledger["entries"][0]["record_count"] == 1
    assert "recorded_at" in ledger["entries"][0]
    assert all("promot" not in field.lower() for field in ledger)
    assert all("promot" not in field.lower() for field in ledger["entries"][0])


def test_consistency_ledger_rejects_parent_substitution_after_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_parent = tmp_path / "registry-authority"
    ledger_parent = tmp_path / "ledger-authority"
    displaced_parent = tmp_path / "ledger-authority-displaced"
    registry_parent.mkdir()
    ledger_parent.mkdir()
    registry_path = registry_parent / "sources.json"
    ledger_path = ledger_parent / "ledger.json"
    first_batch_path = tmp_path / "batch-1.json"
    second_batch_path = tmp_path / "batch-2.json"
    _write_registry(registry_path)
    _write_batch(first_batch_path)
    registry = SourceRegistry.load(registry_path)
    first_staged = stage_source_data_batch(
        first_batch_path, tmp_path / "staging-1", registry
    )
    promote_staged_source_data(first_staged, ledger_path, registry=registry)
    ledger_before = ledger_path.read_bytes()
    original_identity = _directory_identity(ledger_parent)
    _write_batch(second_batch_path)
    second_payload = json.loads(second_batch_path.read_text(encoding="utf-8"))
    second_payload["records"][0]["id"] = "lunge"
    second_batch_path.write_text(json.dumps(second_payload), encoding="utf-8")
    second_staged = stage_source_data_batch(
        second_batch_path, tmp_path / "staging-2", registry
    )
    lock_root = tmp_path / "synthetic-lock-authority"
    lock_root.mkdir()
    real_lock = promotion_module._registry_lock
    real_replace = promotion_module._atomic_replace_json
    injected = 0
    swap_succeeded = False
    recreated_identity: tuple[int, int] | None = None

    def relocated_ledger_lock(
        path: Path,
        *args: object,
        **kwargs: object,
    ) -> object:
        if path == ledger_path:
            return real_lock(lock_root / "ledger", *args, **kwargs)
        return real_lock(path, *args, **kwargs)

    def swap_parent_then_replace(
        target: Path,
        payload: object,
        *args: object,
        **kwargs: object,
    ) -> None:
        nonlocal injected, recreated_identity, swap_succeeded
        if target == ledger_path:
            injected += 1
            os.replace(ledger_parent, displaced_parent)
            swap_succeeded = True
            ledger_parent.mkdir()
            recreated_identity = _directory_identity(ledger_parent)
        real_replace(target, payload, *args, **kwargs)

    monkeypatch.setattr(
        promotion_module, "_atomic_replace_json", swap_parent_then_replace
    )
    monkeypatch.setattr(promotion_module, "_registry_lock", relocated_ledger_lock)
    failure = _capture_security_failure(
        lambda: promote_staged_source_data(
            second_staged,
            ledger_path,
            registry=registry,
        )
    )

    assert injected == 1
    assert swap_succeeded is True
    assert recreated_identity is not None
    assert recreated_identity != original_identity
    assert failure is not None
    assert (displaced_parent / ledger_path.name).read_bytes() == ledger_before
    assert list(ledger_parent.iterdir()) == []


def test_stage_key_rejects_parent_substitution_before_publish(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    key_parent = tmp_path / "key-authority"
    displaced_parent = tmp_path / "key-authority-displaced"
    staging_root = tmp_path / "stage-authority"
    key_parent.mkdir()
    staging_root.mkdir()
    registry_path = key_parent / "sources.json"
    _write_registry(registry_path)
    registry_before = registry_path.read_bytes()
    original_identity = _directory_identity(key_parent)
    key_path = registry_path.with_name(f"{registry_path.name}.stage-key")
    real_publish = promotion_module._atomic_publish_bytes
    injected = 0
    swap_succeeded = False
    recreated_identity: tuple[int, int] | None = None

    def swap_parent_then_publish(
        target: Path,
        payload: bytes,
        *args: object,
        **kwargs: object,
    ) -> None:
        nonlocal injected, recreated_identity, swap_succeeded
        if target == key_path:
            injected += 1
            os.replace(key_parent, displaced_parent)
            swap_succeeded = True
            key_parent.mkdir()
            recreated_identity = _directory_identity(key_parent)
        real_publish(target, payload, *args, **kwargs)

    monkeypatch.setattr(
        promotion_module, "_atomic_publish_bytes", swap_parent_then_publish
    )
    failure = _capture_security_failure(
        lambda: promotion_module._stage_hmac_key(
            registry_path,
            staging_root=staging_root,
            create=True,
            expected_parent_identity=original_identity,
        )
    )

    assert injected == 1
    assert swap_succeeded is True
    assert recreated_identity is not None
    assert recreated_identity != original_identity
    assert failure is not None
    assert (displaced_parent / registry_path.name).read_bytes() == registry_before
    assert not (displaced_parent / key_path.name).exists()
    assert list(key_parent.iterdir()) == []


def test_stage_key_rejects_parent_substitution_after_missing_key_check(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    key_parent = tmp_path / "key-authority"
    displaced_parent = tmp_path / "key-authority-displaced"
    staging_root = tmp_path / "stage-authority"
    lock_root = tmp_path / "synthetic-lock-authority"
    key_parent.mkdir()
    staging_root.mkdir()
    lock_root.mkdir()
    original_identity = _directory_identity(key_parent)
    registry_path = key_parent / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry_bytes = registry_path.read_bytes()
    key_path = registry_path.with_name(f"{registry_path.name}.stage-key")
    real_exists = Path.exists
    real_lock = promotion_module._registry_lock
    injected = 0
    recreated_identity: tuple[int, int] | None = None

    def relocated_registry_lock(
        path: Path,
        *args: object,
        **kwargs: object,
    ) -> object:
        if path == registry_path:
            return real_lock(lock_root / "registry", *args, **kwargs)
        return real_lock(path, *args, **kwargs)

    def swap_after_missing_key_check(path: Path) -> bool:
        nonlocal injected, recreated_identity
        exists = real_exists(path)
        if path == key_path and not exists and injected == 0:
            os.replace(key_parent, displaced_parent)
            key_parent.mkdir()
            (key_parent / registry_path.name).write_bytes(registry_bytes)
            recreated_identity = _directory_identity(key_parent)
            injected += 1
        return exists

    monkeypatch.setattr(promotion_module, "_registry_lock", relocated_registry_lock)
    monkeypatch.setattr(Path, "exists", swap_after_missing_key_check)
    failure = _capture_security_failure(
        lambda: stage_source_data_batch(
            batch_path,
            staging_root,
            SourceRegistry.load(registry_path),
        )
    )

    assert injected == 1
    assert recreated_identity is not None
    assert recreated_identity != original_identity
    assert failure is not None
    assert (displaced_parent / registry_path.name).read_bytes() == registry_bytes
    assert not (displaced_parent / key_path.name).exists()
    assert not (key_parent / key_path.name).exists()


def test_existing_stage_key_rejects_registry_parent_substitution(
    tmp_path: Path,
) -> None:
    key_parent = tmp_path / "key-authority"
    displaced_parent = tmp_path / "key-authority-displaced"
    staging_root = tmp_path / "stage-authority"
    key_parent.mkdir()
    staging_root.mkdir()
    registry_path = key_parent / "sources.json"
    _write_registry(registry_path)
    registry = SourceRegistry.load(registry_path)
    assert registry._baseline_parent_identity is not None
    registry_bytes = registry_path.read_bytes()
    key_path = registry_path.with_name(f"{registry_path.name}.stage-key")
    original_key = b"O" * 32
    replacement_key = b"R" * 32
    key_path.write_bytes(original_key)
    original_identity = _directory_identity(key_parent)

    os.replace(key_parent, displaced_parent)
    key_parent.mkdir()
    (key_parent / registry_path.name).write_bytes(registry_bytes)
    (key_parent / key_path.name).write_bytes(replacement_key)
    recreated_identity = _directory_identity(key_parent)
    failure = _capture_security_failure(
        lambda: promotion_module._stage_hmac_key(
            registry_path,
            staging_root=staging_root,
            create=True,
            expected_parent_identity=registry._baseline_parent_identity,
        )
    )

    assert recreated_identity != original_identity
    assert failure is not None
    assert (displaced_parent / key_path.name).read_bytes() == original_key
    assert (key_parent / key_path.name).read_bytes() == replacement_key


def test_legacy_promotion_ledger_v2_is_rejected_without_silent_relabeling(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    ledger_path = tmp_path / "ledger.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged = stage_source_data_batch(batch_path, tmp_path / "staging", registry)
    ledger_path.write_text(
        json.dumps(
            {
                "schema": "morphic_source_data_promotion_ledger",
                "schema_version": 2,
                "promotions": [],
            }
        ),
        encoding="utf-8",
    )
    before = ledger_path.read_bytes()

    with pytest.raises(SourceDataPromotionError, match="unsupported schema"):
        promote_staged_source_data(staged, ledger_path, registry=registry)
    assert ledger_path.read_bytes() == before


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("schema_version", 2),
        ("source_id", "other-source"),
        ("source_version", "2026-07-15"),
        ("data_type", "group"),
        ("license", "source-specific"),
        ("retrieval_metadata", {"retrieved_at": "changed", "method": "changed"}),
        ("source_manifest_sha256", "f" * 64),
        ("source_registry_revision", 99),
        ("analysis_only", True),
        ("rights", {"draft": True, "publish": False, "activate": False}),
        ("records", [{"id": "other", "label": "Other"}]),
        ("record_count", 99),
        ("record_count", True),
        ("staged_at", {"tampered": True}),
    ],
)
def test_staged_batch_hash_binds_complete_contract(
    tmp_path: Path,
    field: str,
    replacement: object,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    staged_path = stage_source_data_batch(
        batch_path,
        tmp_path / "staging",
        SourceRegistry.load(registry_path),
    )
    staged = json.loads(staged_path.read_text(encoding="utf-8"))
    staged[field] = replacement
    staged_path.write_text(json.dumps(staged), encoding="utf-8")

    with pytest.raises(
        SourceDataPromotionError,
        match="hash|schema|source|license|data_type|rights|analysis|record_count|timestamp|staged_at",
    ):
        promote_staged_source_data(
            staged_path,
            tmp_path / "ledger.json",
            registry=SourceRegistry.load(registry_path),
            dry_run=True,
        )


def test_legacy_registry_rejects_staging_and_promotion_plan_without_sidecars(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_dir = tmp_path / "staging"
    ledger_path = tmp_path / "ledger.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    current = SourceRegistry.load(registry_path)
    staged_path = stage_source_data_batch(batch_path, staging_dir, current)
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    payload.pop("revision")
    payload.pop("rollback_history")
    registry_path.write_text(json.dumps(payload), encoding="utf-8")
    legacy = SourceRegistry.load(registry_path)
    registry_lock = registry_path.with_name(f".{registry_path.name}.lock")
    registry_lock.unlink(missing_ok=True)

    with pytest.raises(SourceDataPromotionError, match="read-only|migrate"):
        stage_source_data_batch(batch_path, tmp_path / "second-stage", legacy)
    assert not registry_lock.exists()

    with pytest.raises(SourceDataPromotionError, match="read-only|migrate"):
        promote_staged_source_data(
            staged_path,
            ledger_path,
            registry=legacy,
            dry_run=True,
        )
    assert not registry_lock.exists()
    with pytest.raises(SourceDataPromotionError, match="read-only|migrate"):
        promote_staged_source_data(staged_path, ledger_path, registry=legacy)
    assert not ledger_path.exists()


def test_disabled_source_cannot_stage_data(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path, enabled=False, status="disabled")
    _write_batch(batch_path)

    with pytest.raises(SourceDataPromotionError, match="disabled|active"):
        stage_source_data_batch(
            batch_path,
            tmp_path / "staging",
            SourceRegistry.load(registry_path),
        )


def test_quarantined_source_is_analysis_only_in_separate_root(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    quarantine_root = tmp_path / "quarantine"
    _write_registry(registry_path, enabled=False, status="quarantined")
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)

    with pytest.raises(SourceDataPromotionError, match="quarantine|analysis"):
        stage_source_data_batch(batch_path, tmp_path / "staging", registry)

    staged_path = stage_source_data_batch(
        batch_path,
        tmp_path / "staging",
        registry,
        quarantine_dir=quarantine_root,
    )
    staged = json.loads(staged_path.read_text(encoding="utf-8"))
    assert staged_path.is_relative_to(quarantine_root)
    assert staged["analysis_only"] is True
    assert staged["rights"] == {"draft": False, "publish": False, "activate": False}


@pytest.mark.parametrize("quarantine_relative", ["staging", "staging/quarantine"])
def test_quarantine_root_must_be_disjoint_from_normal_staging(
    tmp_path: Path,
    quarantine_relative: str,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_dir = tmp_path / "staging"
    _write_registry(registry_path, enabled=False, status="quarantined")
    _write_batch(batch_path)

    with pytest.raises(SourceDataPromotionError, match="separate|disjoint|quarantine"):
        stage_source_data_batch(
            batch_path,
            staging_dir,
            SourceRegistry.load(registry_path),
            quarantine_dir=tmp_path / quarantine_relative,
        )


def test_previously_quarantined_source_remains_analysis_only(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(
        registry_path,
        enabled=True,
        status="active",
        return_status_on_disable="quarantined",
    )
    _write_batch(batch_path)

    with pytest.raises(SourceDataPromotionError, match="quarantine|analysis"):
        stage_source_data_batch(
            batch_path,
            tmp_path / "staging",
            SourceRegistry.load(registry_path),
        )


def test_reference_only_source_cannot_stage_import_data(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path, import_policy="reference_only")
    _write_batch(batch_path)

    with pytest.raises(SourceDataPromotionError, match="reference_only|policy"):
        stage_source_data_batch(
            batch_path,
            tmp_path / "staging",
            SourceRegistry.load(registry_path),
        )


def test_batch_and_staged_artifact_reject_unbound_extra_fields(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    raw = json.loads(batch_path.read_text(encoding="utf-8"))
    raw["unbound"] = "forbidden"
    batch_path.write_text(json.dumps(raw), encoding="utf-8")
    registry = SourceRegistry.load(registry_path)

    with pytest.raises(SourceDataPromotionError, match="fields"):
        stage_source_data_batch(batch_path, tmp_path / "staging", registry)

    raw.pop("unbound")
    batch_path.write_text(json.dumps(raw), encoding="utf-8")
    staged = stage_source_data_batch(batch_path, tmp_path / "staging", registry)
    artifact = json.loads(staged.read_text(encoding="utf-8"))
    artifact["unbound_privilege_claim"] = True
    staged.write_text(json.dumps(artifact), encoding="utf-8")
    with pytest.raises(SourceDataPromotionError, match="fields"):
        promote_staged_source_data(staged, tmp_path / "ledger.json", registry=registry)


def test_registry_and_ledger_paths_must_be_distinct(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged = stage_source_data_batch(batch_path, tmp_path / "staging", registry)

    with pytest.raises(SourceDataPromotionError, match="different files"):
        promote_staged_source_data(staged, registry_path, registry=registry)


def test_duplicate_staging_and_promotion_replay_are_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import core.source_data_promotion as promotion_module

    timestamps = iter(
        (
            "2026-07-15T07:00:00+00:00",
            "2026-07-15T07:00:01+00:00",
            "2026-07-15T07:00:02+00:00",
            "2026-07-15T07:00:03+00:00",
        )
    )
    monkeypatch.setattr(promotion_module, "_utc_now", lambda: next(timestamps))
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    staging_dir = tmp_path / "staging"
    ledger_path = tmp_path / "ledger.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)

    staged_path = stage_source_data_batch(batch_path, staging_dir, registry)
    with pytest.raises(SourceDataPromotionError, match="duplicate|replay|exists"):
        stage_source_data_batch(batch_path, staging_dir, registry)

    promote_staged_source_data(staged_path, ledger_path, registry=registry)
    before = ledger_path.read_bytes()
    with pytest.raises(SourceDataPromotionError, match="duplicate|replay"):
        promote_staged_source_data(staged_path, ledger_path, registry=registry)
    assert ledger_path.read_bytes() == before


def test_consistency_ledger_rejects_hardlink_alias_before_forking(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    second_batch_path = tmp_path / "batch-2.json"
    ledger_path = tmp_path / "ledger.json"
    alias_path = tmp_path / "ledger-alias.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged = stage_source_data_batch(batch_path, tmp_path / "staging-1", registry)
    promote_staged_source_data(staged, ledger_path, registry=registry)
    before = ledger_path.read_bytes()

    try:
        os.link(ledger_path, alias_path)
    except OSError:
        pytest.skip("Host filesystem does not permit hardlink creation")

    _write_batch(second_batch_path)
    second_payload = json.loads(second_batch_path.read_text(encoding="utf-8"))
    second_payload["records"][0]["id"] = "lunge"
    second_batch_path.write_text(json.dumps(second_payload), encoding="utf-8")
    second_staged = stage_source_data_batch(
        second_batch_path,
        tmp_path / "staging-2",
        registry,
    )

    with pytest.raises(SourceDataPromotionError, match="hard link|authority"):
        promote_staged_source_data(second_staged, alias_path, registry=registry)

    assert ledger_path.read_bytes() == before
    assert alias_path.read_bytes() == before


def test_consistency_ledger_revalidates_hardlinks_after_temp_write_before_replace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_path = tmp_path / "sources.json"
    first_batch_path = tmp_path / "batch-1.json"
    second_batch_path = tmp_path / "batch-2.json"
    ledger_path = tmp_path / "ledger.json"
    alias_path = tmp_path / "late-ledger-alias.json"
    _write_registry(registry_path)
    _write_batch(first_batch_path)
    registry = SourceRegistry.load(registry_path)
    first_staged = stage_source_data_batch(
        first_batch_path,
        tmp_path / "staging-1",
        registry,
    )
    promote_staged_source_data(first_staged, ledger_path, registry=registry)
    before = ledger_path.read_bytes()

    _write_batch(second_batch_path)
    second_payload = json.loads(second_batch_path.read_text(encoding="utf-8"))
    second_payload["records"][0]["id"] = "lunge"
    second_batch_path.write_text(json.dumps(second_payload), encoding="utf-8")
    second_staged = stage_source_data_batch(
        second_batch_path,
        tmp_path / "staging-2",
        registry,
    )
    original_write = registry_module._write_temporary_bytes

    def write_then_alias(target: Path, payload: object) -> Path:
        temporary = original_write(target, payload)
        try:
            os.link(target, alias_path)
        except OSError:
            temporary.unlink(missing_ok=True)
            pytest.skip("Host filesystem does not permit hardlink creation")
        return temporary

    monkeypatch.setattr(registry_module, "_write_temporary_bytes", write_then_alias)

    with pytest.raises(SourceDataPromotionError, match="hard link|authority"):
        promote_staged_source_data(second_staged, ledger_path, registry=registry)

    assert ledger_path.read_bytes() == before
    assert alias_path.read_bytes() == before
    assert not list(tmp_path.glob(".ledger.json.tmp-*"))


def test_replay_identity_survives_unrelated_registry_revisions(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    ledger_path = tmp_path / "ledger.json"
    _write_registry(registry_path)
    _write_batch(batch_path)

    first_registry = SourceRegistry.load(registry_path)
    first = stage_source_data_batch(batch_path, tmp_path / "staging-1", first_registry)
    promote_staged_source_data(first, ledger_path, registry=first_registry)

    changed = SourceRegistry.load(registry_path)
    changed.disable_source("admin_terms")
    changed.enable_source("admin_terms")
    current = SourceRegistry.load(registry_path)
    second = stage_source_data_batch(batch_path, tmp_path / "staging-2", current)
    first_payload = json.loads(first.read_text(encoding="utf-8"))
    second_payload = json.loads(second.read_text(encoding="utf-8"))
    assert first_payload["sha256"] != second_payload["sha256"]
    assert first_payload["batch_identity_sha256"] == second_payload["batch_identity_sha256"]

    before = ledger_path.read_bytes()
    with pytest.raises(SourceDataPromotionError, match="duplicate|replay"):
        promote_staged_source_data(second, ledger_path, registry=current)
    assert ledger_path.read_bytes() == before


def test_staged_batch_binds_full_registry_baseline_not_only_source_and_revision(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    staged = stage_source_data_batch(
        batch_path,
        tmp_path / "staging",
        SourceRegistry.load(registry_path),
    )
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    unrelated = dict(payload["sources"][0])
    unrelated["id"] = "unrelated_terms"
    unrelated["label"] = "Unrelated Terms"
    unrelated["local_path"] = str(tmp_path / "unrelated")
    payload["sources"].append(unrelated)
    registry_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(SourceDataPromotionError, match="baseline|changed|stale"):
        promote_staged_source_data(
            staged,
            tmp_path / "ledger.json",
            registry=SourceRegistry.load(registry_path),
            dry_run=True,
        )

    assert not (tmp_path / "ledger.json").exists()


def test_staging_revalidates_current_registry_state_from_disk(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    stale = SourceRegistry.load(registry_path)
    SourceRegistry.load(registry_path).disable_source("admin_terms")

    with pytest.raises(SourceDataPromotionError, match="disabled|active|stale"):
        stage_source_data_batch(batch_path, tmp_path / "staging", stale)


def test_promotion_revalidates_current_registry_state_from_disk(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    ledger_path = tmp_path / "ledger.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged = stage_source_data_batch(batch_path, tmp_path / "staging", registry)
    SourceRegistry.load(registry_path).disable_source("admin_terms")

    with pytest.raises(SourceDataPromotionError, match="disabled|active|revision|manifest"):
        promote_staged_source_data(staged, ledger_path, registry=registry)
    assert not ledger_path.exists()


@pytest.mark.parametrize(
    "invalid_json",
    [
        '{"schema_version":1,"source_id":"admin_terms","source_id":"other",'
        '"source_version":"1","data_type":"terminology","license":"public-domain",'
        '"retrieval_metadata":{"method":"test"},"records":[{"id":"x","label":"X"}]}',
        '{"schema_version":1,"source_id":"admin_terms","source_version":"1",'
        '"data_type":"terminology","license":"public-domain",'
        '"retrieval_metadata":{"score":NaN},"records":[{"id":"x","label":"X"}]}',
    ],
)
def test_batch_loader_rejects_ambiguous_or_non_finite_json(
    tmp_path: Path,
    invalid_json: str,
) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    _write_registry(registry_path)
    batch_path.write_text(invalid_json, encoding="utf-8")

    with pytest.raises(SourceDataPromotionError, match="Duplicate|Non-finite"):
        stage_source_data_batch(
            batch_path,
            tmp_path / "staging",
            SourceRegistry.load(registry_path),
        )


def test_corrupt_v3_consistency_ledger_is_rejected_before_append(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    ledger_path = tmp_path / "ledger.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged = stage_source_data_batch(batch_path, tmp_path / "staging", registry)
    ledger_path.write_text(
        json.dumps(
            {
                "schema": "morphic_source_data_consistency_ledger",
                "schema_version": 3,
                "entries": [{"sha256": "a" * 64}],
            }
        ),
        encoding="utf-8",
    )
    before = ledger_path.read_bytes()

    with pytest.raises(SourceDataPromotionError, match="entry fields"):
        promote_staged_source_data(staged, ledger_path, registry=registry)
    assert ledger_path.read_bytes() == before


def test_legacy_v1_ledger_is_rejected_without_silent_relabeling(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    ledger_path = tmp_path / "ledger.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    registry = SourceRegistry.load(registry_path)
    staged = stage_source_data_batch(batch_path, tmp_path / "staging", registry)
    ledger_path.write_text(
        json.dumps(
            {
                "schema": "morphic_source_data_promotion_ledger",
                "schema_version": 1,
                "promotions": [{"source_id": "legacy", "sha256": "a" * 64}],
            }
        ),
        encoding="utf-8",
    )
    before = ledger_path.read_bytes()

    with pytest.raises(SourceDataPromotionError, match="unsupported schema"):
        promote_staged_source_data(staged, ledger_path, registry=registry)
    assert ledger_path.read_bytes() == before


def test_failed_atomic_ledger_write_preserves_previous_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import core.source_data_promotion as promotion_module

    registry_path = tmp_path / "sources.json"
    batch_path = tmp_path / "batch.json"
    ledger_path = tmp_path / "ledger.json"
    _write_registry(registry_path)
    _write_batch(batch_path)
    staged_path = stage_source_data_batch(
        batch_path,
        tmp_path / "staging",
        SourceRegistry.load(registry_path),
    )
    ledger_path.write_text(
        json.dumps(
            {
                "schema": "morphic_source_data_consistency_ledger",
                "schema_version": 3,
                "entries": [],
            }
        ),
        encoding="utf-8",
    )
    before = ledger_path.read_bytes()

    def fail_write(path: Path, payload: object, **kwargs: object) -> None:
        raise OSError("simulated ledger replace failure")

    monkeypatch.setattr(promotion_module, "_atomic_replace_json", fail_write)
    with pytest.raises(OSError, match="replace failure"):
        promote_staged_source_data(
            staged_path,
            ledger_path,
            registry=SourceRegistry.load(registry_path),
        )

    assert ledger_path.read_bytes() == before
