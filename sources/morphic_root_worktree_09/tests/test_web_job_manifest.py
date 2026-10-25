from __future__ import annotations

import json
from pathlib import Path

from core.compliance.web_job_manifest import WebJobManifestStore


def test_web_job_manifest_writer_uses_shared_durable_parent_helper(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from core.compliance import web_job_manifest

    calls: list[Path] = []

    def parent(path: Path, *, mode: int = 0o777) -> None:
        calls.append(Path(path))
        Path(path).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(web_job_manifest, "durable_mkdir_parents", parent, raising=False)
    root = tmp_path / "nested" / "manifests"
    store = WebJobManifestStore(root)

    store.record({
        "job_id": "scan-parent", "status": "completed", "returncode": 0,
        "owner_id": "owner", "tenant_id": "tenant",
        "created_at": "2026-07-24T00:00:00Z", "updated_at": "2026-07-24T00:01:00Z",
    })

    assert calls == [root]


def test_web_job_manifest_redacts_command_and_recovers_read_only(tmp_path: Path) -> None:
    root = tmp_path / "manifests"
    store = WebJobManifestStore(root)
    entry = store.record({
        "job_id": "scan-1", "status": "completed", "returncode": 0,
        "command": ["python", "-m", "apps.cli.main", "scan", "top3-scan", "Mustermann", "Max"],
        "owner_id": "operator-synthetic", "tenant_id": "ws-synthetic",
        "created_at": "2026-07-10T20:00:00Z", "updated_at": "2026-07-10T20:01:00Z",
        "stdout_path": "scan-1.stdout.log", "stderr_path": "scan-1.stderr.log",
    })

    before = (root / "web_job_manifests.json").read_bytes()
    recovered = WebJobManifestStore(root).recover_read_only()

    assert entry["command"] == ["python", "-m", "apps.cli.main", "scan", "top3-scan", "[REDACTED]", "[REDACTED]"]
    assert recovered == [entry]
    assert (root / "web_job_manifests.json").read_bytes() == before
    assert "Mustermann" not in json.dumps(entry)
    assert "Max" not in json.dumps(entry)
