from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_module_help_exits_successfully_without_encoding_env() -> None:
    env = os.environ.copy()
    env.pop("PYTHONIOENCODING", None)
    env.pop("PYTHONUTF8", None)

    result = subprocess.run(
        [sys.executable, "-m", "apps.cli.main", "--help"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        timeout=20,
    )

    output = result.stdout.decode("utf-8", errors="replace")
    errors = result.stderr.decode("utf-8", errors="replace")

    assert result.returncode == 0, output + errors
    assert "health" in output
    assert "scan" in output
