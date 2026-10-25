from __future__ import annotations

import ast
from pathlib import Path


MAIN_PATH = Path(__file__).resolve().parents[1] / "apps" / "cli" / "main.py"


def _is_typer_app_assignment(node: ast.AST) -> bool:
    if not isinstance(node, ast.Assign):
        return False
    if not any(isinstance(target, ast.Name) and target.id == "app" for target in node.targets):
        return False
    call = node.value
    return (
        isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr == "Typer"
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "typer"
    )


def _is_main_guard(node: ast.AST) -> bool:
    if not isinstance(node, ast.If):
        return False
    compare = node.test
    return (
        isinstance(compare, ast.Compare)
        and isinstance(compare.left, ast.Name)
        and compare.left.id == "__name__"
        and len(compare.ops) == 1
        and isinstance(compare.ops[0], ast.Eq)
        and len(compare.comparators) == 1
        and isinstance(compare.comparators[0], ast.Constant)
        and compare.comparators[0].value == "__main__"
    )


def test_cli_main_has_one_root_app_and_one_entrypoint() -> None:
    tree = ast.parse(MAIN_PATH.read_text(encoding="utf-8-sig"))

    app_assignments = [node for node in tree.body if _is_typer_app_assignment(node)]
    main_guards = [node for node in tree.body if _is_main_guard(node)]

    assert len(app_assignments) == 1
    assert len(main_guards) == 1
    assert main_guards[0].lineno > app_assignments[0].lineno
