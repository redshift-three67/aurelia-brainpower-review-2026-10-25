from __future__ import annotations

import ast
from pathlib import Path


COMMANDS_PATH = Path(__file__).resolve().parents[1] / "apps" / "cli" / "commands"
FORBIDDEN_HELPER_MODULES = {"apps.cli.main", "cli.main"}


def test_command_modules_do_not_import_helpers_from_cli_main() -> None:
    offenders: list[str] = []

    for path in sorted(COMMANDS_PATH.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module in FORBIDDEN_HELPER_MODULES:
                offenders.append(f"{path.name}:{node.lineno}:{node.module}")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in FORBIDDEN_HELPER_MODULES:
                        offenders.append(f"{path.name}:{node.lineno}:{alias.name}")

    assert offenders == []
