from __future__ import annotations

from typer.testing import CliRunner

from apps.cli.main import app


runner = CliRunner()


def test_health_command_reports_runtime_and_database_status() -> None:
    result = runner.invoke(app, ["health"])

    assert result.exit_code == 0, result.output
    assert "Morphic Engine Health" in result.output
    assert "Python:" in result.output
    assert "Profiles:" in result.output
    assert "remedies.db" in result.output
    assert "descriptions.db" in result.output
