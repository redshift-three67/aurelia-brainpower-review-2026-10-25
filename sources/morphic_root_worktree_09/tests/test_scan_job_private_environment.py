from __future__ import annotations

from pathlib import Path

from core.profile_sync import SCAN_PROFILE_POOL_FINGERPRINT_ENV


def test_scan_job_environment_overrides_are_process_only_and_never_snapshotted(
    tmp_path: Path, monkeypatch
) -> None:
    import apps.web.scan_jobs as scan_jobs_module
    from apps.web.scan_jobs import LocalScanJobService

    captured: dict[str, object] = {}

    class FakeProcess:
        pid = 4242

        def poll(self):
            return None

    def fake_popen(command, **kwargs):
        captured["command"] = command
        captured["env"] = kwargs["env"]
        return FakeProcess()

    monkeypatch.setattr(scan_jobs_module.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(scan_jobs_module, "_process_create_time", lambda pid: 123.0)
    monkeypatch.setattr(scan_jobs_module, "_create_windows_job", lambda process, token: 700)
    monkeypatch.setattr(
        scan_jobs_module,
        "_close_windows_job_handle",
        lambda job: setattr(job, "windows_job_handle", None),
    )
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)

    snapshot = service.start(
        ["python", "-V"],
        owner_id="operator-local",
        env_overrides={
            "MORPHIC_GROUP_ACTIVATION_RUNTIME": "1",
            "MORPHIC_GROUP_ACTIVATION_ROOT": "C:/private/handles",
            "MORPHIC_GROUP_ACTIVATION_HANDLE": "gah-00000000000000000000000000000000",
            SCAN_PROFILE_POOL_FINGERPRINT_ENV: "a" * 64,
        },
    )

    environment = captured["env"]
    assert isinstance(environment, dict)
    assert environment["MORPHIC_GROUP_ACTIVATION_RUNTIME"] == "1"
    assert environment["MORPHIC_GROUP_ACTIVATION_HANDLE"].startswith("gah-")
    assert environment[SCAN_PROFILE_POOL_FINGERPRINT_ENV] == "a" * 64
    assert "env" not in snapshot
    assert "environment" not in snapshot
    snapshot_text = str(snapshot)
    assert "gah-" not in snapshot_text
    assert "C:/private/handles" not in snapshot_text
    assert "a" * 64 not in snapshot_text
    assert "a" * 64 not in str(captured["command"])
    for path in (tmp_path / "jobs").glob("*.json"):
        persisted = path.read_text(encoding="utf-8")
        assert "a" * 64 not in persisted
        assert SCAN_PROFILE_POOL_FINGERPRINT_ENV not in persisted


def test_scan_job_default_start_does_not_add_activation_environment(
    tmp_path: Path, monkeypatch
) -> None:
    import apps.web.scan_jobs as scan_jobs_module
    from apps.web.scan_jobs import LocalScanJobService

    captured: dict[str, object] = {}

    class FakeProcess:
        pid = 4242

        def poll(self):
            return None

    def fake_popen(command, **kwargs):
        captured["env"] = kwargs["env"]
        return FakeProcess()

    monkeypatch.setattr(scan_jobs_module.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(scan_jobs_module, "_process_create_time", lambda pid: 123.0)
    monkeypatch.setattr(scan_jobs_module, "_create_windows_job", lambda process, token: 700)
    monkeypatch.setattr(
        scan_jobs_module,
        "_close_windows_job_handle",
        lambda job: setattr(job, "windows_job_handle", None),
    )
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)

    service.start(["python", "-V"])

    environment = captured["env"]
    assert isinstance(environment, dict)
    assert "MORPHIC_GROUP_ACTIVATION_RUNTIME" not in environment
    assert "MORPHIC_GROUP_ACTIVATION_ROOT" not in environment
    assert "MORPHIC_GROUP_ACTIVATION_HANDLE" not in environment
