from __future__ import annotations

from typer.testing import CliRunner

from apps.cli.main import app
from apps.cli.commands.scan import scan_app


runner = CliRunner()


def test_root_help_loads() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0, result.output
    assert "scan" in result.output
    assert "field" in result.output
    assert "health" in result.output


def test_top3_scan_command_is_discoverable() -> None:
    result = runner.invoke(app, ["scan", "top3-scan", "--help"])

    assert result.exit_code == 0, result.output
    assert "--focus" in result.output
    assert "--top-n" in result.output


def test_top3_scan_command_is_registered_once() -> None:
    top3_commands = [
        command
        for command in scan_app.registered_commands
        if command.name == "top3-scan"
    ]

    assert len(top3_commands) == 1


def test_multiplex_scan_command_is_discoverable() -> None:
    result = runner.invoke(app, ["field", "multiplex-scan", "--help"])

    assert result.exit_code == 0, result.output
    assert "--profile" in result.output
    assert "--focus" in result.output
