"""Tests fuer core.compliance.entitlement_stub."""

from __future__ import annotations

from core.compliance.entitlement_stub import (
    is_module_available,
    set_entitlement_provider,
)
from core.compliance.operator_context import OperatorContext


def test_default_provider_allows_all_modules_in_standalone_mode() -> None:
    context = OperatorContext(operator_id="op-1", workspace_id="ws-1")

    assert is_module_available("radimorphic", context) is True
    assert is_module_available("anything-else", context) is True


def test_custom_provider_can_be_injected_and_reset() -> None:
    context = OperatorContext(operator_id="op-1", workspace_id="ws-1")
    set_entitlement_provider(lambda module, ctx: module == "radi144")
    try:
        assert is_module_available("radi144", context) is True
        assert is_module_available("radimorphic", context) is False
    finally:
        set_entitlement_provider(None)

    assert is_module_available("radimorphic", context) is True
