from __future__ import annotations

import ast
from pathlib import Path

from apps.cli import main as cli_main
from apps.cli.commands import helpers


MAIN_PATH = Path(__file__).resolve().parents[1] / "apps" / "cli" / "main.py"


def test_cli_main_helper_exports_delegate_to_helpers_package() -> None:
    for name in helpers.__all__:
        if not name.startswith("_"):
            continue
        assert getattr(cli_main, name) is getattr(helpers, name), name


def test_cli_main_does_not_define_helper_copies() -> None:
    tree = ast.parse(MAIN_PATH.read_text(encoding="utf-8-sig"))
    helper_names = {name for name in helpers.__all__ if name.startswith("_")}

    local_helper_defs = [
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in helper_names
    ]

    assert local_helper_defs == []
