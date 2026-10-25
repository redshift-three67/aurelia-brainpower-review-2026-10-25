"""Tests fuer core.compliance.operator_context."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.compliance.operator_context import (
    OperatorContext,
    OwnershipError,
    assert_owner,
    resolve_operator_context,
)


def test_resolve_operator_context_persists_stable_workspace_id(tmp_path: Path) -> None:
    first = resolve_operator_context(tmp_path)
    second = resolve_operator_context(tmp_path)

    assert first.workspace_id == second.workspace_id
    assert first.workspace_id.startswith("ws-")
    assert first.operator_id


def test_resolve_operator_context_respects_env_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("MORPHIC_OPERATOR_ID", "operator-test")

    context = resolve_operator_context(tmp_path)

    assert context.operator_id == "operator-test"


def test_resolve_operator_context_uses_separate_workspace_per_root(tmp_path: Path) -> None:
    a = resolve_operator_context(tmp_path / "a")
    b = resolve_operator_context(tmp_path / "b")

    assert a.workspace_id != b.workspace_id


def test_assert_owner_allows_unowned_resource() -> None:
    context = OperatorContext(operator_id="op-1", workspace_id="ws-1")

    assert assert_owner(None, context) is None
    assert assert_owner("", context) is None


def test_assert_owner_allows_matching_owner() -> None:
    context = OperatorContext(operator_id="op-1", workspace_id="ws-1")

    assert assert_owner("op-1", context) is None
    assert assert_owner("ws-1", context) is None


def test_assert_owner_rejects_foreign_owner() -> None:
    context = OperatorContext(operator_id="op-1", workspace_id="ws-1")

    with pytest.raises(OwnershipError):
        assert_owner("someone-else", context)
