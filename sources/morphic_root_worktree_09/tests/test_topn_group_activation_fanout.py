from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from core.compliance.group_activation_handle_store import GroupActivationHandleStore
from core.compliance.group_activation_runtime import build_group_activation_environment
from core.compliance.operator_context import OperatorContext
from core.profiles.group_vector import GroupAnalysisOptIn


CONTEXT = OperatorContext("operator-topn", "ws-topn", "tenant-topn")
NOW = datetime(2026, 7, 13, 10, 0, tzinfo=UTC)


def _root_environment(tmp_path: Path) -> dict[str, str]:
    store = GroupActivationHandleStore(tmp_path / "handles")
    issued = store.issue(
        GroupAnalysisOptIn(
            enabled=True,
            centroid_rates=np.asarray([4.0, 5.0, 6.0]),
            strength=0.3,
            consent_verified=True,
            activation_generation=store.authorization_generation(CONTEXT),
        ),
        context=CONTEXT,
        now=NOW,
    )
    return build_group_activation_environment(
        store=store, activation_handle=str(issued["activation_handle"])
    )


def test_topn_runtime_is_exactly_inactive_without_internal_environment() -> None:
    from apps.cli.commands.scan import (
        build_topn_child_process_environment,
        resolve_topn_group_opt_in,
    )

    base = {"PYTHONUTF8": "1", "EXISTING": "kept"}
    assert resolve_topn_group_opt_in(
        environment={}, context=CONTEXT, now=NOW
    ) is None
    assert build_topn_child_process_environment(
        base_environment=base,
        parent_environment={},
        group_opt_in=None,
        context=CONTEXT,
        now=NOW,
    ) == base
    assert base == {"PYTHONUTF8": "1", "EXISTING": "kept"}


def test_topn_runtime_consumes_root_and_issues_distinct_child_handles(
    tmp_path: Path,
) -> None:
    from apps.cli.commands.scan import (
        build_topn_child_process_environment,
        resolve_topn_group_opt_in,
    )

    parent = _root_environment(tmp_path)
    opt_in = resolve_topn_group_opt_in(
        environment=parent, context=CONTEXT, now=NOW
    )
    assert opt_in is not None

    first = build_topn_child_process_environment(
        base_environment={"EXISTING": "kept"},
        parent_environment=parent,
        group_opt_in=opt_in,
        context=CONTEXT,
        now=NOW,
    )
    second = build_topn_child_process_environment(
        base_environment={"EXISTING": "kept"},
        parent_environment=parent,
        group_opt_in=opt_in,
        context=CONTEXT,
        now=NOW,
    )

    assert first["EXISTING"] == "kept"
    assert first["MORPHIC_GROUP_ACTIVATION_HANDLE"] != parent["MORPHIC_GROUP_ACTIVATION_HANDLE"]
    assert second["MORPHIC_GROUP_ACTIVATION_HANDLE"] != first["MORPHIC_GROUP_ACTIVATION_HANDLE"]
    for environment in (first, second):
        assert "4.0" not in str(environment)
        assert "operator-topn" not in str(environment)


def test_topn_scan_uses_child_activation_environment_for_screening_and_detail() -> None:
    source = (
        Path(__file__).resolve().parents[1]
        / "apps"
        / "cli"
        / "commands"
        / "scan.py"
    ).read_text(encoding="utf-8")

    assert "group_opt_in = resolve_topn_group_opt_in(context=group_context)" in source
    assert source.count("build_topn_child_process_environment(") >= 3
    assert '"--activation-handle"' not in source
    assert '"activation_handle"' not in source
