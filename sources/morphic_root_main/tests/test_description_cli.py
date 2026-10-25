from __future__ import annotations

from typer.testing import CliRunner

from apps.cli.main import app


runner = CliRunner()


def test_descriptions_status_detailed_renders_group_rows() -> None:
    result = runner.invoke(app, ["descriptions", "descriptions-status", "--detailed"])

    assert result.exit_code == 0, result.output
    assert "BESCHREIBUNGS" in result.output
    assert "Items" in result.output
