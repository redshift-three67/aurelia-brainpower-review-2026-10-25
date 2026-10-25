from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

_THIS_FILE = Path(__file__).resolve()
RADIALGO_ROOT = _THIS_FILE.parents[2]
ME_ROOT = _THIS_FILE.parents[1]

import sys
for p in (RADIALGO_ROOT, ME_ROOT):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)

from apps.cli.main import app


runner = CliRunner()


def test_analyze_smoke_runs_successfully() -> None:
    result = runner.invoke(
        app,
        [
            "analyze",
            "Mustermann",
            "Max",
            "--birth-date",
            "09031999",
            "--birth-place",
            "Muenchen",
            "--fixed-h",
            "0.33",
        ],
    )
    assert result.exit_code == 0
    out = result.stdout
    assert "Morphic Engine V1" in out
    assert "Top Resonances" in out
