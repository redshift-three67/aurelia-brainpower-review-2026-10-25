from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from radiworks.main import create_app


def test_same_runtime_home_rejects_second_engine_and_releases_after_shutdown(tmp_path: Path):
    first = create_app(base_dir=tmp_path)
    second = create_app(base_dir=tmp_path)
    with TestClient(first) as active:
        assert active.get("/ping").status_code == 200
        with pytest.raises(RuntimeError, match="bereits von einer Engine verwendet"):
            with TestClient(second):
                pass
    with TestClient(second) as restarted:
        assert restarted.get("/ping").status_code == 200


def test_different_runtime_homes_can_run_together(tmp_path: Path):
    first = create_app(base_dir=tmp_path / "a")
    second = create_app(base_dir=tmp_path / "b")
    with TestClient(first) as active, TestClient(second) as other:
        assert active.get("/ping").status_code == 200
        assert other.get("/ping").status_code == 200


def test_runtime_home_lock_is_cross_process_and_survives_crash(tmp_path: Path):
    import subprocess
    import sys
    import time

    ready = tmp_path / "child-ready"
    child_code = "\n".join([
        "import sys, time",
        "from pathlib import Path",
        "from fastapi.testclient import TestClient",
        "from radiworks.main import create_app",
        "with TestClient(create_app(base_dir=Path(sys.argv[1]))):",
        "    Path(sys.argv[2]).write_text('ready', encoding='utf-8')",
        "    time.sleep(30)",
    ])
    child = subprocess.Popen(
        [sys.executable, "-c", child_code, str(tmp_path), str(ready)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        deadline = time.monotonic() + 10
        while not ready.exists() and child.poll() is None and time.monotonic() < deadline:
            time.sleep(0.05)
        assert ready.exists(), "child engine did not become ready"
        with pytest.raises(RuntimeError, match="bereits von einer Engine verwendet"):
            with TestClient(create_app(base_dir=tmp_path)):
                pass
    finally:
        child.kill()
        child.wait(timeout=10)
        child.stdout.close()
        child.stderr.close()
    with TestClient(create_app(base_dir=tmp_path)) as restarted:
        assert restarted.get("/ping").status_code == 200
