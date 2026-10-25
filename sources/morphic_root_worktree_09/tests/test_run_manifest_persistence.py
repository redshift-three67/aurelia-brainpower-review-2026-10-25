from __future__ import annotations

import json
from pathlib import Path

from core.compliance.run_manifest import build_run_manifest
from core.compliance.run_manifest_persistence import persist_successful_run_manifest


def test_run_manifest_writer_uses_shared_durable_parent_helper(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from core.compliance import run_manifest_persistence

    calls: list[Path] = []

    def parent(path: Path, *, mode: int = 0o777) -> None:
        calls.append(Path(path))
        Path(path).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(
        run_manifest_persistence,
        "durable_mkdir_parents",
        parent,
        raising=False,
    )
    target = tmp_path / "nested" / "manifests" / "run.json"

    persist_successful_run_manifest(
        {"status": "completed", "returncode": 0}, _manifest(), target
    )

    assert calls == [target.parent]


def _manifest() -> dict[str, object]:
    digest = "a" * 64
    return build_run_manifest(
        run_id="run-synthetic", created_at="2026-07-10T20:00:00Z",
        commit="619a1f5485a1", tenant_id="ws-synthetic", client_id="cli-synthetic",
        profile_hashes={"profile": digest}, data_hashes={"groups": digest},
        seed_mode="deterministic", parameter_version="v1",
    )


def test_successful_synthetic_run_persists_manifest_atomically(tmp_path: Path) -> None:
    target = tmp_path / "run-manifest.json"
    manifest = _manifest()

    result = persist_successful_run_manifest(
        {"status": "completed", "returncode": 0}, manifest, target
    )

    assert result == target
    assert json.loads(target.read_text(encoding="utf-8")) == manifest
    assert not list(tmp_path.glob("*.tmp.*"))


def test_failed_or_incomplete_run_does_not_write_manifest(tmp_path: Path) -> None:
    target = tmp_path / "run-manifest.json"

    assert persist_successful_run_manifest({"status": "failed", "returncode": 1}, _manifest(), target) is None
    assert persist_successful_run_manifest({"status": "running", "returncode": None}, _manifest(), target) is None
    assert not target.exists()
