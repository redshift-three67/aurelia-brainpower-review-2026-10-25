from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pytest

from core.compliance.group_activation_handle_store import GroupActivationHandleStore
from core.compliance.operator_context import OperatorContext
from core.profiles.group_vector import GroupAnalysisOptIn


CONTEXT = OperatorContext("operator-local", "ws-local", "tenant-local")
NOW = datetime(2026, 7, 13, 8, 0, tzinfo=UTC)


def _issued(tmp_path: Path) -> tuple[GroupActivationHandleStore, str]:
    store = GroupActivationHandleStore(tmp_path / "handles")
    summary = store.issue(
        GroupAnalysisOptIn(
            enabled=True,
            centroid_rates=np.asarray([1.0, 2.0, 3.0]),
            strength=0.25,
            consent_verified=True,
            activation_generation=store.authorization_generation(CONTEXT),
        ),
        context=CONTEXT,
        now=NOW,
    )
    return store, str(summary["activation_handle"])


def test_runtime_environment_is_absent_by_default_without_opening_a_store(monkeypatch) -> None:
    from core.compliance import group_activation_runtime as runtime

    class ForbiddenStore:
        def __init__(self, root: object) -> None:
            raise AssertionError("default path must not open an activation store")

    monkeypatch.setattr(runtime, "GroupActivationHandleStore", ForbiddenStore)

    assert runtime.consume_group_activation_from_environment(
        {}, context=CONTEXT, now=NOW
    ) is None


def test_runtime_environment_requires_complete_internal_transport(tmp_path: Path) -> None:
    from core.compliance.group_activation_runtime import (
        GROUP_ACTIVATION_HANDLE_ENV,
        GROUP_ACTIVATION_ROOT_ENV,
        GROUP_ACTIVATION_RUNTIME_ENV,
        consume_group_activation_from_environment,
    )

    incomplete = (
        {GROUP_ACTIVATION_RUNTIME_ENV: "1"},
        {
            GROUP_ACTIVATION_RUNTIME_ENV: "1",
            GROUP_ACTIVATION_ROOT_ENV: str(tmp_path / "handles"),
        },
        {
            GROUP_ACTIVATION_RUNTIME_ENV: "1",
            GROUP_ACTIVATION_HANDLE_ENV: "gah-00000000000000000000000000000000",
        },
    )

    for environment in incomplete:
        with pytest.raises(ValueError, match="incomplete"):
            consume_group_activation_from_environment(
                environment, context=CONTEXT, now=NOW
            )


def test_runtime_environment_consumes_one_time_handle_and_redacts_summary(
    tmp_path: Path,
) -> None:
    from core.compliance.group_activation_runtime import (
        build_group_activation_environment,
        consume_group_activation_from_environment,
        safe_group_activation_environment_summary,
    )

    store, handle = _issued(tmp_path)
    environment = build_group_activation_environment(store=store, activation_handle=handle)

    assert set(environment) == {
        "MORPHIC_GROUP_ACTIVATION_RUNTIME",
        "MORPHIC_GROUP_ACTIVATION_ROOT",
        "MORPHIC_GROUP_ACTIVATION_HANDLE",
    }
    assert safe_group_activation_environment_summary(environment) == {
        "activation_requested": True,
        "transport": "one-time-handle",
    }
    summary_text = str(safe_group_activation_environment_summary(environment))
    assert handle not in summary_text
    assert str(store.root) not in summary_text
    assert "operator-local" not in summary_text

    opt_in = consume_group_activation_from_environment(
        environment, context=CONTEXT, now=NOW
    )

    assert opt_in is not None
    assert opt_in.enabled is True
    assert opt_in.strength == 0.25
    np.testing.assert_array_equal(opt_in.centroid_rates, np.asarray([1.0, 2.0, 3.0]))
    with pytest.raises(LookupError):
        consume_group_activation_from_environment(
            environment, context=CONTEXT, now=NOW
        )


def test_runtime_environment_rejects_unknown_activation_marker(tmp_path: Path) -> None:
    from core.compliance.group_activation_runtime import (
        GROUP_ACTIVATION_HANDLE_ENV,
        GROUP_ACTIVATION_ROOT_ENV,
        GROUP_ACTIVATION_RUNTIME_ENV,
        consume_group_activation_from_environment,
    )

    with pytest.raises(ValueError, match="marker"):
        consume_group_activation_from_environment(
            {
                GROUP_ACTIVATION_RUNTIME_ENV: "true",
                GROUP_ACTIVATION_ROOT_ENV: str(tmp_path / "handles"),
                GROUP_ACTIVATION_HANDLE_ENV: "gah-00000000000000000000000000000000",
            },
            context=CONTEXT,
            now=NOW,
        )


def test_runtime_reissues_a_distinct_child_handle_without_exposing_candidate(
    tmp_path: Path,
) -> None:
    from core.compliance.group_activation_runtime import (
        build_group_activation_environment,
        consume_group_activation_from_environment,
        issue_child_group_activation_environment,
    )

    store, root_handle = _issued(tmp_path)
    root_environment = build_group_activation_environment(
        store=store, activation_handle=root_handle
    )
    opt_in = consume_group_activation_from_environment(
        root_environment, context=CONTEXT, now=NOW
    )
    assert opt_in is not None

    child_environment = issue_child_group_activation_environment(
        opt_in,
        parent_environment=root_environment,
        context=CONTEXT,
        now=NOW,
    )

    assert child_environment["MORPHIC_GROUP_ACTIVATION_HANDLE"] != root_handle
    assert child_environment["MORPHIC_GROUP_ACTIVATION_ROOT"] == str(store.root)
    assert "1.0" not in str(child_environment)
    child = consume_group_activation_from_environment(
        child_environment, context=CONTEXT, now=NOW
    )
    assert child is not None
    np.testing.assert_array_equal(child.centroid_rates, opt_in.centroid_rates)
