from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from core.compliance.group_activation_handle_store import GroupActivationHandleStore
from core.compliance.group_activation_runtime import build_group_activation_environment
from core.compliance.operator_context import OperatorContext
from core.profiles.group_vector import GroupAnalysisOptIn


CONTEXT = OperatorContext("operator-field", "ws-field", "tenant-field")
NOW = datetime(2026, 7, 13, 9, 0, tzinfo=UTC)


def test_field_activation_runtime_is_none_without_internal_environment() -> None:
    from apps.cli.commands.field import resolve_field_group_opt_in

    assert resolve_field_group_opt_in(
        environment={}, context=CONTEXT, now=NOW
    ) is None


def test_field_activation_runtime_consumes_child_handle_once(tmp_path: Path) -> None:
    from apps.cli.commands.field import resolve_field_group_opt_in

    store = GroupActivationHandleStore(tmp_path / "handles")
    issued = store.issue(
        GroupAnalysisOptIn(
            enabled=True,
            centroid_rates=np.asarray([11.0, 22.0, 33.0]),
            strength=0.4,
            consent_verified=True,
            activation_generation=store.authorization_generation(CONTEXT),
        ),
        context=CONTEXT,
        now=NOW,
    )
    environment = build_group_activation_environment(
        store=store,
        activation_handle=str(issued["activation_handle"]),
    )

    opt_in = resolve_field_group_opt_in(
        environment=environment, context=CONTEXT, now=NOW
    )

    assert opt_in is not None
    assert opt_in.strength == 0.4
    np.testing.assert_array_equal(opt_in.centroid_rates, np.asarray([11.0, 22.0, 33.0]))


def test_multiplex_analysis_passes_only_in_memory_group_opt_in_to_analysis_service() -> None:
    source = (
        Path(__file__).resolve().parents[1]
        / "apps"
        / "cli"
        / "commands"
        / "field.py"
    ).read_text(encoding="utf-8")

    assert "group_opt_in = resolve_field_group_opt_in()" in source
    assert "analysis.encode_profile(profile_obj, group_opt_in=group_opt_in)" in source
    assert '"activation_handle"' not in source
    assert "MORPHIC_GROUP_ACTIVATION_HANDLE" not in source
