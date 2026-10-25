from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import core.source_registry as registry_module
from core.source_registry import SourceRegistry, SourceRegistryError


def _source(source_id: str, *, enabled: bool = False, label: str | None = None) -> dict[str, object]:
    return {
        "id": source_id,
        "label": label or f"Source {source_id}",
        "description": "Synthetic source",
        "source_type": "online_download",
        "homepage": "https://example.org",
        "download_url": "https://example.org/data.json",
        "license": "source-specific",
        "trust_level": "experimental_unverified",
        "import_policy": "reference_only",
        "scopes": ["terminology"],
        "enabled": enabled,
        "status": "active" if enabled else "disabled",
    }


def _write_registry(path: Path, sources: list[dict[str, object]]) -> None:
    path.write_text(
        json.dumps(
            {"schema_version": 1, "revision": 0, "rollback_history": [], "sources": sources}
        ),
        encoding="utf-8",
    )


def _write_manifest(path: Path, source: dict[str, object]) -> None:
    path.write_text(
        json.dumps({"schema_version": 1, "source": source}),
        encoding="utf-8",
    )


def _stage_approved(
    registry: SourceRegistry,
    manifest_path: Path,
    root: Path,
    *,
    replace: bool = False,
    approval_id: str = "approval-001",
) -> Path:
    return registry.stage_manifest(
        manifest_path,
        root / "staging",
        replace=replace,
        approval_id=approval_id,
    )


def _directory_identity(path: Path) -> tuple[int, int]:
    attributes = os.lstat(path)
    return attributes.st_dev, attributes.st_ino


def _capture_registry_failure(operation: object) -> BaseException | None:
    try:
        operation()
    except SourceRegistryError as exc:
        return exc
    return None


@pytest.mark.parametrize("operation_name", ("_replace_in_guard", "_link_in_guard"))
@pytest.mark.parametrize("misplaced_path", ("source", "target"))
def test_guarded_publish_requires_source_and_target_under_bound_parent(
    tmp_path: Path,
    operation_name: str,
    misplaced_path: str,
) -> None:
    authority_parent = tmp_path / "authority"
    outside_parent = tmp_path / "outside"
    authority_parent.mkdir()
    outside_parent.mkdir()
    source = authority_parent / "temporary.json"
    target = authority_parent / "published.json"
    if misplaced_path == "source":
        source = outside_parent / "temporary.json"
    else:
        target = outside_parent / "published.json"
    source.write_bytes(b'{"authority":true}\n')
    operation = getattr(registry_module, operation_name)

    with registry_module._directory_commit_guard(
        authority_parent,
        expected_identity=_directory_identity(authority_parent),
    ) as (guard, _flush_directory):
        with registry_module._held_file_identity(source):
            with pytest.raises(SourceRegistryError, match="authority parent"):
                operation(guard, source, target)

    assert not target.exists()
    assert source.exists()


@pytest.mark.parametrize("operation_name", ("_replace_in_guard", "_link_in_guard"))
def test_posix_guarded_publish_fails_closed_without_dir_fd_support(
    tmp_path: Path,
    operation_name: str,
) -> None:
    authority_parent = tmp_path / "authority"
    authority_parent.mkdir()
    source = authority_parent / "temporary.json"
    target = authority_parent / "published.json"
    source.write_bytes(b'{"authority":true}\n')
    guard = {"parent": authority_parent, "fd": 123}
    operation = getattr(registry_module, operation_name)
    original_os_name = registry_module.os.name
    original_supports_dir_fd = registry_module.os.supports_dir_fd
    try:
        registry_module.os.name = "posix"
        registry_module.os.supports_dir_fd = set()
        with pytest.raises(SourceRegistryError, match="POSIX.*dir_fd"):
            operation(guard, source, target)
    finally:
        registry_module.os.name = original_os_name
        registry_module.os.supports_dir_fd = original_supports_dir_fd

    assert source.exists()
    assert not target.exists()


@pytest.mark.parametrize("operation_name", ("_replace_in_guard", "_link_in_guard"))
def test_posix_guarded_publish_fails_closed_even_with_dir_fd_support(
    tmp_path: Path,
    operation_name: str,
) -> None:
    authority_parent = tmp_path / "authority"
    authority_parent.mkdir()
    source = authority_parent / "temporary.json"
    target = authority_parent / "published.json"
    source.write_bytes(b'{"authority":true}\n')
    target_before: bytes | None = None
    if operation_name == "_replace_in_guard":
        target.write_bytes(b'{"before":true}\n')
        target_before = target.read_bytes()
    operation = getattr(registry_module, operation_name)
    original_os_name = registry_module.os.name
    original_supports_dir_fd = registry_module.os.supports_dir_fd
    original_replace = registry_module.os.replace
    original_link = registry_module.os.link
    original_path = registry_module.Path
    attempted_publish = 0

    def fake_replace(
        _source_name: str,
        _target_name: str,
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
    ) -> None:
        nonlocal attempted_publish
        attempted_publish += 1
        target.write_bytes(b'{"attacker":true}\n')

    def fake_link(
        _source_name: str,
        _target_name: str,
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
        follow_symlinks: bool = True,
    ) -> None:
        nonlocal attempted_publish
        attempted_publish += 1
        target.write_bytes(b'{"attacker":true}\n')

    try:
        registry_module.os.name = "posix"
        registry_module.Path = type(authority_parent)
        if operation_name == "_replace_in_guard":
            registry_module.os.replace = fake_replace
            registry_module.os.supports_dir_fd = {fake_replace}
        else:
            registry_module.os.link = fake_link
            registry_module.os.supports_dir_fd = {fake_link}
        with pytest.raises(SourceRegistryError, match="POSIX.*source-inode-bound"):
            operation({"parent": authority_parent, "fd": 123}, source, target)
    finally:
        registry_module.os.name = original_os_name
        registry_module.os.supports_dir_fd = original_supports_dir_fd
        registry_module.os.replace = original_replace
        registry_module.os.link = original_link
        registry_module.Path = original_path

    assert attempted_publish == 0
    if target_before is None:
        assert not target.exists()
    else:
        assert target.read_bytes() == target_before
    assert source.exists()


def test_atomic_registry_replace_failure_preserves_previous_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_path = tmp_path / "sources.json"
    _write_registry(registry_path, [_source("alpha")])
    before = registry_path.read_bytes()
    registry = SourceRegistry.load(registry_path)

    def fail_replace(_guard: object, source: Path, target: Path) -> None:
        raise OSError("simulated replace failure")

    monkeypatch.setattr(registry_module, "_replace_in_guard", fail_replace)
    with pytest.raises(OSError, match="replace failure"):
        registry.enable_source("alpha")

    assert registry_path.read_bytes() == before
    assert not list(tmp_path.glob(".sources.json.tmp-*"))


def test_registry_rejects_hardlink_alias_authority(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    alias_path = tmp_path / "alias.json"
    _write_registry(registry_path, [_source("alpha")])
    try:
        os.link(registry_path, alias_path)
    except OSError:
        pytest.skip("Host filesystem does not permit hardlink creation")

    with pytest.raises(SourceRegistryError, match="hard link"):
        SourceRegistry.load(alias_path)


def test_registry_revalidates_hardlinks_after_temp_write_before_replace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_path = tmp_path / "sources.json"
    alias_path = tmp_path / "late-alias.json"
    _write_registry(registry_path, [_source("alpha")])
    registry = SourceRegistry.load(registry_path)
    before = registry_path.read_bytes()
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

    with pytest.raises(SourceRegistryError, match="hard link"):
        registry.enable_source("alpha")

    assert registry_path.read_bytes() == before
    assert alias_path.read_bytes() == before
    assert not list(tmp_path.glob(".sources.json.tmp-*"))


@pytest.mark.skipif(os.name != "nt", reason="Windows parent-handle semantics")
def test_registry_commit_guard_blocks_parent_namespace_replacement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_path = tmp_path / "sources.json"
    displaced_parent = tmp_path.with_name(f"{tmp_path.name}-displaced")
    _write_registry(registry_path, [_source("alpha")])
    registry = SourceRegistry.load(registry_path)
    real_replace = registry_module._replace_in_guard
    attempted = 0

    def attack_parent_then_replace(
        guard: object, source: Path, target: Path
    ) -> None:
        nonlocal attempted
        attempted += 1
        with pytest.raises(PermissionError):
            os.replace(tmp_path, displaced_parent)
        real_replace(guard, source, target)

    monkeypatch.setattr(
        registry_module, "_replace_in_guard", attack_parent_then_replace
    )
    registry.enable_source("alpha")

    assert attempted == 1
    assert SourceRegistry.load(registry_path).get("alpha").enabled is True
    assert not displaced_parent.exists()


@pytest.mark.skipif(os.name != "nt", reason="Windows handle-publish semantics")
def test_registry_temp_name_swap_cannot_mutate_authority(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_path = tmp_path / "sources.json"
    displaced_temp = tmp_path / "displaced-temp.json"
    _write_registry(registry_path, [_source("alpha")])
    before = registry_path.read_bytes()
    registry = SourceRegistry.load(registry_path)
    real_replace = registry_module._replace_in_guard
    injected = 0

    def swap_temp_name_then_replace(
        guard: object, source: Path, target: Path
    ) -> None:
        nonlocal injected
        injected += 1
        os.replace(source, displaced_temp)
        source.write_bytes(b'{"attacker":true}\n')
        real_replace(guard, source, target)

    monkeypatch.setattr(
        registry_module, "_replace_in_guard", swap_temp_name_then_replace
    )
    with pytest.raises(SourceRegistryError, match="changed before commit"):
        registry.enable_source("alpha")

    assert injected == 1
    assert registry_path.read_bytes() == before


@pytest.mark.skipif(os.name != "nt", reason="Windows authority-parent semantics")
def test_loaded_registry_rejects_parent_substitution_before_commit(
    tmp_path: Path,
) -> None:
    authority_parent = tmp_path / "authority"
    displaced_parent = tmp_path / "authority-displaced"
    authority_parent.mkdir()
    registry_path = authority_parent / "sources.json"
    _write_registry(registry_path, [_source("alpha")])
    before = registry_path.read_bytes()
    registry = SourceRegistry.load(registry_path)

    os.replace(authority_parent, displaced_parent)
    authority_parent.mkdir()
    registry_path.write_bytes(before)

    with pytest.raises(SourceRegistryError, match="parent identity"):
        registry.enable_source("alpha")

    assert registry_path.read_bytes() == before
    assert (displaced_parent / "sources.json").read_bytes() == before


def test_loaded_revision_zero_registry_is_not_recreated_after_deletion(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    _write_registry(registry_path, [_source("alpha")])
    loaded = SourceRegistry.load(registry_path)
    registry_path.unlink()

    with pytest.raises(SourceRegistryError, match="disappeared|conflict"):
        loaded.enable_source("alpha")

    assert not registry_path.exists()


def test_same_revision_legacy_swap_is_rejected_without_rewrite(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    source = _source("alpha")
    _write_registry(registry_path, [source])
    loaded = SourceRegistry.load(registry_path)
    legacy_bytes = json.dumps(
        {"schema_version": 1, "sources": [source]},
        sort_keys=True,
    ).encode("utf-8")
    registry_path.write_bytes(legacy_bytes)

    with pytest.raises(SourceRegistryError, match="read-only|state conflict"):
        loaded.enable_source("alpha")

    assert registry_path.read_bytes() == legacy_bytes


def test_stale_registry_write_is_rejected(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    _write_registry(registry_path, [_source("alpha"), _source("beta")])
    first = SourceRegistry.load(registry_path)
    stale = SourceRegistry.load(registry_path)

    first.enable_source("alpha")
    with pytest.raises(SourceRegistryError, match="revision|concurrent|stale"):
        stale.enable_source("beta")

    current = SourceRegistry.load(registry_path)
    assert current.get("alpha").enabled is True
    assert current.get("beta").enabled is False


def test_process_lock_rejects_a_second_writer(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    _write_registry(registry_path, [_source("alpha")])

    with registry_module._registry_lock(registry_path):
        with pytest.raises(SourceRegistryError, match="process lock|Timed out"):
            with registry_module._registry_lock(registry_path, timeout_seconds=0.02):
                pytest.fail("second writer unexpectedly acquired the registry lock")


def test_staging_is_immutable_and_never_overwrites_existing_artifact(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "source.json"
    _write_registry(registry_path, [])
    _write_manifest(manifest_path, _source("alpha"))
    registry = SourceRegistry.load(registry_path)

    staged = _stage_approved(registry, manifest_path, tmp_path)
    before = staged.read_bytes()
    with pytest.raises(SourceRegistryError, match="already exists|immutable"):
        _stage_approved(registry, manifest_path, tmp_path)

    assert staged.read_bytes() == before
    assert not list((tmp_path / "staging").glob(".*.tmp-*"))


def test_source_manifest_stage_rejects_parent_substitution_before_publish(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_parent = tmp_path / "registry-authority"
    staging_root = tmp_path / "stage-authority"
    displaced_root = tmp_path / "stage-authority-displaced"
    registry_parent.mkdir()
    staging_root.mkdir()
    sentinel = staging_root / "sentinel.txt"
    sentinel.write_bytes(b"original-manifest-stage-parent\n")
    sentinel_before = sentinel.read_bytes()
    original_identity = _directory_identity(staging_root)
    registry_path = registry_parent / "sources.json"
    manifest_path = tmp_path / "source.json"
    _write_registry(registry_path, [])
    _write_manifest(manifest_path, _source("alpha"))
    registry = SourceRegistry.load(registry_path)
    real_publish = registry_module._atomic_publish_json
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
        if target.parent == staging_root:
            injected += 1
            os.replace(staging_root, displaced_root)
            swap_succeeded = True
            staging_root.mkdir()
            recreated_identity = _directory_identity(staging_root)
        real_publish(target, payload, *args, **kwargs)

    monkeypatch.setattr(
        registry_module, "_atomic_publish_json", swap_parent_then_publish
    )
    failure = _capture_registry_failure(
        lambda: registry.stage_manifest(
            manifest_path,
            staging_root,
            approval_id="approval-001",
        )
    )

    assert injected == 1
    assert swap_succeeded is True
    assert recreated_identity is not None
    assert recreated_identity != original_identity
    assert failure is not None
    assert (displaced_root / sentinel.name).read_bytes() == sentinel_before
    assert not list(displaced_root.glob("*.source-stage.json"))
    assert list(staging_root.iterdir()) == []


def test_import_requires_hash_bound_staged_artifact_and_approval_receipt(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "source.json"
    rollback_dir = tmp_path / "rollbacks"
    _write_registry(registry_path, [])
    _write_manifest(manifest_path, _source("alpha"))
    registry = SourceRegistry.load(registry_path)

    with pytest.raises(SourceRegistryError, match="staged|approval"):
        registry.import_manifest(manifest_path)

    staged = _stage_approved(registry, manifest_path, tmp_path)
    artifact = json.loads(staged.read_text(encoding="utf-8"))
    assert artifact["schema"] == "morphic_source_manifest_stage"
    assert artifact["approval_receipt"]["approval_id"] == "approval-001"
    assert artifact["approval_receipt"]["artifact_sha256"] == artifact["artifact_sha256"]

    imported = registry.import_manifest(
        staged,
        rollback_dir=rollback_dir,
        batch_id="batch-001",
    )
    assert imported.id == "alpha"


def test_tampered_staged_manifest_is_rejected_before_registry_mutation(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "source.json"
    _write_registry(registry_path, [])
    _write_manifest(manifest_path, _source("alpha"))
    registry = SourceRegistry.load(registry_path)
    staged = _stage_approved(registry, manifest_path, tmp_path)
    before = registry_path.read_bytes()

    artifact = json.loads(staged.read_text(encoding="utf-8"))
    artifact["source"]["label"] = "Tampered"
    staged.write_text(json.dumps(artifact), encoding="utf-8")

    with pytest.raises(SourceRegistryError, match="hash|artifact"):
        registry.import_manifest(staged, rollback_dir=tmp_path / "rollbacks", batch_id="batch-001")
    assert registry_path.read_bytes() == before


def test_rollback_snapshot_has_integrity_hash_and_single_use_marker(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "source.json"
    rollback_dir = tmp_path / "rollbacks"
    _write_registry(registry_path, [_source("alpha", label="Before")])
    _write_manifest(manifest_path, _source("alpha", label="After"))
    registry = SourceRegistry.load(registry_path)
    staged = _stage_approved(registry, manifest_path, tmp_path, replace=True)

    registry.import_manifest(staged, rollback_dir=rollback_dir, batch_id="batch-001")
    snapshot_path = rollback_dir / "batch-001.source-registry-rollback.json"
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert len(snapshot["snapshot_sha256"]) == 64
    expected_revision = SourceRegistry.load(registry_path).revision

    SourceRegistry.load(registry_path).rollback_import(
        "batch-001",
        rollback_dir=rollback_dir,
        expected_revision=expected_revision,
    )
    marker = rollback_dir / "batch-001.source-registry-rollback.consumed.json"
    assert marker.exists()
    assert json.loads(marker.read_text(encoding="utf-8"))["snapshot_sha256"] == snapshot["snapshot_sha256"]

    with pytest.raises(SourceRegistryError, match="consumed|already reverted"):
        SourceRegistry.load(registry_path).rollback_import(
            "batch-001",
            rollback_dir=rollback_dir,
            expected_revision=SourceRegistry.load(registry_path).revision,
        )


def test_rollback_snapshot_rejects_parent_substitution_before_publish(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_parent = tmp_path / "registry-authority"
    rollback_root = tmp_path / "rollback-authority"
    displaced_root = tmp_path / "rollback-authority-displaced"
    registry_parent.mkdir()
    rollback_root.mkdir()
    sentinel = rollback_root / "sentinel.txt"
    sentinel.write_bytes(b"original-rollback-parent\n")
    sentinel_before = sentinel.read_bytes()
    original_identity = _directory_identity(rollback_root)
    registry_path = registry_parent / "sources.json"
    manifest_path = tmp_path / "source.json"
    _write_registry(registry_path, [_source("alpha", label="Before")])
    _write_manifest(manifest_path, _source("alpha", label="After"))
    registry = SourceRegistry.load(registry_path)
    staged = registry.stage_manifest(
        manifest_path,
        tmp_path / "staging",
        replace=True,
        approval_id="approval-001",
    )
    registry_before = registry_path.read_bytes()
    snapshot_name = "batch-001.source-registry-rollback.json"
    real_publish = registry_module._atomic_publish_json
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
        if target.name == snapshot_name:
            injected += 1
            os.replace(rollback_root, displaced_root)
            swap_succeeded = True
            rollback_root.mkdir()
            recreated_identity = _directory_identity(rollback_root)
        real_publish(target, payload, *args, **kwargs)

    monkeypatch.setattr(
        registry_module, "_atomic_publish_json", swap_parent_then_publish
    )
    failure = _capture_registry_failure(
        lambda: registry.import_manifest(
            staged,
            rollback_dir=rollback_root,
            batch_id="batch-001",
        )
    )

    assert injected == 1
    assert swap_succeeded is True
    assert recreated_identity is not None
    assert recreated_identity != original_identity
    assert failure is not None
    assert registry_path.read_bytes() == registry_before
    assert (displaced_root / sentinel.name).read_bytes() == sentinel_before
    assert not (displaced_root / snapshot_name).exists()
    assert list(rollback_root.iterdir()) == []


def test_supplementary_consumed_marker_cannot_veto_authoritative_rollback(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "source.json"
    rollback_dir = tmp_path / "rollbacks"
    _write_registry(registry_path, [_source("alpha", label="Before")])
    _write_manifest(manifest_path, _source("alpha", label="After"))
    registry = SourceRegistry.load(registry_path)
    staged = _stage_approved(registry, manifest_path, tmp_path, replace=True)
    registry.import_manifest(staged, rollback_dir=rollback_dir, batch_id="batch-001")
    marker = rollback_dir / "batch-001.source-registry-rollback.consumed.json"
    marker.write_text('{"untrusted":true}', encoding="utf-8")

    current = SourceRegistry.load(registry_path)
    current.rollback_import(
        "batch-001",
        rollback_dir=rollback_dir,
        expected_revision=current.revision,
    )

    restored = SourceRegistry.load(registry_path)
    assert restored.get("alpha").label == "Before"
    assert restored.rollback_history[-1]["batch_id"] == "batch-001"


def test_rollback_rejects_later_legitimate_revision_without_overwrite(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "source.json"
    rollback_dir = tmp_path / "rollbacks"
    _write_registry(registry_path, [_source("alpha", label="Before"), _source("beta")])
    _write_manifest(manifest_path, _source("alpha", label="After"))
    registry = SourceRegistry.load(registry_path)
    staged = _stage_approved(registry, manifest_path, tmp_path, replace=True)
    registry.import_manifest(staged, rollback_dir=rollback_dir, batch_id="batch-001")

    current = SourceRegistry.load(registry_path)
    imported_revision = current.revision
    current.enable_source("beta")
    before_rollback = registry_path.read_bytes()

    with pytest.raises(SourceRegistryError, match="revision|conflict"):
        SourceRegistry.load(registry_path).rollback_import(
            "batch-001",
            rollback_dir=rollback_dir,
            expected_revision=imported_revision,
        )
    assert registry_path.read_bytes() == before_rollback


def test_staged_manifest_binds_full_registry_baseline_not_only_revision(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "source.json"
    rollback_dir = tmp_path / "rollbacks"
    _write_registry(registry_path, [_source("alpha", label="Before")])
    _write_manifest(manifest_path, _source("alpha", label="After"))
    staged = _stage_approved(
        SourceRegistry.load(registry_path),
        manifest_path,
        tmp_path,
        replace=True,
    )
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    payload["sources"][0]["description"] = "same-revision external change"
    registry_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(SourceRegistryError, match="baseline|stale|concurrent"):
        SourceRegistry.load(registry_path).import_manifest(
            staged,
            rollback_dir=rollback_dir,
            batch_id="batch-001",
        )

    assert not rollback_dir.exists()
    assert json.loads(registry_path.read_text(encoding="utf-8")) == payload


def test_manifest_staging_reloads_current_lifecycle_and_rejects_stale_transition(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "source.json"
    _write_registry(registry_path, [_source("alpha", label="Before")])
    _write_manifest(manifest_path, _source("alpha", label="After"))
    stale = SourceRegistry.load(registry_path)
    SourceRegistry.load(registry_path).enable_source("alpha")

    with pytest.raises(SourceRegistryError, match="enabled/status|lifecycle"):
        stale.stage_manifest(
            manifest_path,
            tmp_path / "staging",
            replace=True,
            approval_id="approval-001",
        )


def test_legacy_import_rejection_leaves_no_rollback_directory(tmp_path: Path) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "source.json"
    rollback_dir = tmp_path / "rollbacks"
    _write_registry(registry_path, [_source("alpha", label="Before")])
    _write_manifest(manifest_path, _source("alpha", label="After"))
    current = SourceRegistry.load(registry_path)
    staged = _stage_approved(current, manifest_path, tmp_path, replace=True)
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    payload.pop("revision")
    payload.pop("rollback_history")
    registry_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(SourceRegistryError, match="read-only|migrate"):
        SourceRegistry.load(registry_path).import_manifest(
            staged,
            rollback_dir=rollback_dir,
            batch_id="batch-001",
        )

    assert not rollback_dir.exists()


def test_post_replace_error_retains_snapshot_for_committed_import(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "source.json"
    rollback_dir = tmp_path / "rollbacks"
    _write_registry(registry_path, [_source("alpha", label="Before")])
    _write_manifest(manifest_path, _source("alpha", label="After"))
    registry = SourceRegistry.load(registry_path)
    staged = _stage_approved(registry, manifest_path, tmp_path, replace=True)
    original_replace = registry_module._atomic_replace_json

    def commit_then_raise(
        target: Path,
        payload: dict[str, object],
        **kwargs: object,
    ) -> None:
        original_replace(target, payload, **kwargs)
        if target == registry_path:
            raise OSError("synthetic post-commit interruption")

    monkeypatch.setattr(registry_module, "_atomic_replace_json", commit_then_raise)

    with pytest.raises(SourceRegistryError, match="committed|retained"):
        registry.import_manifest(
            staged,
            rollback_dir=rollback_dir,
            batch_id="batch-001",
        )

    committed = SourceRegistry.load(registry_path)
    assert committed.revision == 1
    assert committed.get("alpha").label == "After"
    assert (rollback_dir / "batch-001.source-registry-rollback.json").is_file()


def test_post_replace_error_classifies_committed_rollback_and_publishes_marker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "source.json"
    rollback_dir = tmp_path / "rollbacks"
    _write_registry(registry_path, [_source("alpha", label="Before")])
    _write_manifest(manifest_path, _source("alpha", label="After"))
    registry = SourceRegistry.load(registry_path)
    staged = _stage_approved(registry, manifest_path, tmp_path, replace=True)
    registry.import_manifest(staged, rollback_dir=rollback_dir, batch_id="batch-001")
    current = SourceRegistry.load(registry_path)
    original_replace = registry_module._atomic_replace_json

    def commit_then_raise(
        target: Path,
        payload: dict[str, object],
        **kwargs: object,
    ) -> None:
        original_replace(target, payload, **kwargs)
        if target == registry_path:
            raise OSError("synthetic post-commit rollback interruption")

    monkeypatch.setattr(registry_module, "_atomic_replace_json", commit_then_raise)

    current.rollback_import(
        "batch-001",
        rollback_dir=rollback_dir,
        expected_revision=current.revision,
    )

    restored = SourceRegistry.load(registry_path)
    assert restored.get("alpha").label == "Before"
    assert restored.rollback_history[-1]["batch_id"] == "batch-001"
    assert (rollback_dir / "batch-001.source-registry-rollback.consumed.json").is_file()


def test_marker_failure_cannot_leave_committed_rollback_unconsumed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "source.json"
    rollback_dir = tmp_path / "rollbacks"
    _write_registry(registry_path, [_source("alpha", label="Before")])
    _write_manifest(manifest_path, _source("alpha", label="After"))
    registry = SourceRegistry.load(registry_path)
    staged = _stage_approved(registry, manifest_path, tmp_path, replace=True)
    registry.import_manifest(staged, rollback_dir=rollback_dir, batch_id="batch-001")

    current = SourceRegistry.load(registry_path)
    original_publish = registry_module._atomic_publish_json

    def fail_consumed_marker(
        path: Path,
        payload: object,
        *args: object,
        **kwargs: object,
    ) -> None:
        if path.name.endswith(".consumed.json"):
            raise OSError("simulated consumed marker failure")
        original_publish(path, payload, *args, **kwargs)

    monkeypatch.setattr(registry_module, "_atomic_publish_json", fail_consumed_marker)
    current.rollback_import(
        "batch-001",
        rollback_dir=rollback_dir,
        expected_revision=current.revision,
    )

    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    assert payload["sources"][0]["label"] == "Before"
    assert payload["rollback_history"][0]["batch_id"] == "batch-001"
    assert not (rollback_dir / "batch-001.source-registry-rollback.consumed.json").exists()
    with pytest.raises(SourceRegistryError, match="reverted|consumed"):
        SourceRegistry.load(registry_path).rollback_import(
            "batch-001",
            rollback_dir=rollback_dir,
            expected_revision=payload["revision"],
        )


def test_failed_import_retains_uncommitted_snapshot_and_preserves_registry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "replacement.json"
    rollback_dir = tmp_path / "rollbacks"
    _write_registry(registry_path, [_source("alpha", label="Alpha")])
    _write_manifest(manifest_path, _source("alpha", label="Alpha Changed"))
    before = registry_path.read_bytes()
    registry = SourceRegistry.load(registry_path)
    staged_path = _stage_approved(registry, manifest_path, tmp_path, replace=True)

    def fail_save() -> None:
        raise OSError("simulated registry save failure")

    monkeypatch.setattr(registry, "save", fail_save)
    with pytest.raises(OSError, match="save failure"):
        registry.import_manifest(
            staged_path,
            rollback_dir=rollback_dir,
            batch_id="batch-failed",
        )

    assert registry_path.read_bytes() == before
    assert (rollback_dir / "batch-failed.source-registry-rollback.json").exists()
    assert rollback_dir.is_dir()
