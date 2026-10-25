"""Tests fuer core.compliance.operator_context."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import core.compliance.operator_context as operator_context_module

from core.compliance.operator_context import (
    OperatorContext,
    OwnershipError,
    assert_owner,
    assert_strict_owner,
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


def test_operator_context_tenant_id_defaults_to_workspace_id(tmp_path: Path) -> None:
    context = resolve_operator_context(tmp_path)

    assert context.tenant_id == context.workspace_id


def test_operator_context_tenant_id_respects_env_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("MORPHIC_TENANT_ID", "tenant-test")

    context = resolve_operator_context(tmp_path)

    assert context.tenant_id == "tenant-test"
    assert context.tenant_id != context.workspace_id


def test_assert_owner_allows_unowned_resource() -> None:
    context = OperatorContext(operator_id="op-1", workspace_id="ws-1", tenant_id="ws-1")

    assert assert_owner(None, context) is None
    assert assert_owner("", context) is None


def test_assert_owner_allows_matching_owner() -> None:
    context = OperatorContext(operator_id="op-1", workspace_id="ws-1", tenant_id="ws-1")

    assert assert_owner("op-1", context) is None
    assert assert_owner("ws-1", context) is None


def test_assert_owner_rejects_foreign_owner() -> None:
    context = OperatorContext(operator_id="op-1", workspace_id="ws-1", tenant_id="ws-1")

    with pytest.raises(OwnershipError):
        assert_owner("someone-else", context)


def _expected_owner_scope(tenant_id: str, operator_id: str) -> str:
    canonical = json.dumps(
        [tenant_id, operator_id],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return "owner-v1-" + hashlib.sha256(canonical).hexdigest()


def test_operator_owner_scope_uses_collision_safe_canonical_json() -> None:
    first = OperatorContext(
        operator_id="c",
        workspace_id="workspace",
        tenant_id="a:b",
    )
    second = OperatorContext(
        operator_id="b:c",
        workspace_id="workspace",
        tenant_id="a",
    )

    first_scope = operator_context_module.operator_owner_scope(first)
    second_scope = operator_context_module.operator_owner_scope(second)

    assert first_scope == _expected_owner_scope("a:b", "c")
    assert second_scope == _expected_owner_scope("a", "b:c")
    assert first_scope != second_scope
    assert len(first_scope) == len("owner-v1-") + 64


@pytest.mark.parametrize(
    ("tenant_id", "operator_id"),
    [
        pytest.param(None, "operator", id="missing-tenant"),
        pytest.param("", "operator", id="empty-tenant"),
        pytest.param("   ", "operator", id="blank-tenant"),
        pytest.param("tenant", None, id="missing-operator"),
        pytest.param("tenant", "", id="empty-operator"),
        pytest.param("tenant", "   ", id="blank-operator"),
    ],
)
def test_operator_owner_scope_rejects_missing_or_blank_components(
    tenant_id: str | None,
    operator_id: str | None,
) -> None:
    context = OperatorContext(
        operator_id=operator_id,  # type: ignore[arg-type]
        workspace_id="workspace",
        tenant_id=tenant_id,  # type: ignore[arg-type]
    )

    with pytest.raises(ValueError):
        operator_context_module.operator_owner_scope(context)


@pytest.mark.parametrize(
    "legacy_owner",
    [None, "", "   ", "operator", "workspace", "tenant:operator"],
)
def test_assert_strict_owner_accepts_only_exact_owner_scope(
    legacy_owner: object,
) -> None:
    context = OperatorContext(
        operator_id="operator",
        workspace_id="workspace",
        tenant_id="tenant",
    )

    with pytest.raises(OwnershipError):
        assert_strict_owner(legacy_owner, context)

    assert_strict_owner(_expected_owner_scope("tenant", "operator"), context)
