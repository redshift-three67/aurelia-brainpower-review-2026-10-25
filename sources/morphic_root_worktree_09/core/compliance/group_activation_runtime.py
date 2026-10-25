"""Internal one-time handle transport for local group-analysis workers.

The environment carries only an opaque handle and its local DPAPI store root.
Callers must never persist or expose the environment values in job snapshots,
commands, traces, reports, or manifests.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Mapping

from core.compliance.group_activation_handle_store import GroupActivationHandleStore
from core.compliance.operator_context import OperatorContext
from core.profiles.group_vector import GroupAnalysisOptIn


GROUP_ACTIVATION_RUNTIME_ENV = "MORPHIC_GROUP_ACTIVATION_RUNTIME"
GROUP_ACTIVATION_ROOT_ENV = "MORPHIC_GROUP_ACTIVATION_ROOT"
GROUP_ACTIVATION_HANDLE_ENV = "MORPHIC_GROUP_ACTIVATION_HANDLE"
_ENV_KEYS = frozenset(
    {
        GROUP_ACTIVATION_RUNTIME_ENV,
        GROUP_ACTIVATION_ROOT_ENV,
        GROUP_ACTIVATION_HANDLE_ENV,
    }
)


def build_group_activation_environment(
    *,
    store: GroupActivationHandleStore,
    activation_handle: str,
) -> dict[str, str]:
    """Build the private process environment for one activation consume."""

    handle = store._handle(activation_handle)
    return {
        GROUP_ACTIVATION_RUNTIME_ENV: "1",
        GROUP_ACTIVATION_ROOT_ENV: str(store.root),
        GROUP_ACTIVATION_HANDLE_ENV: handle,
    }


def safe_group_activation_environment_summary(
    environment: Mapping[str, str],
) -> dict[str, object]:
    """Describe activation intent without returning handles, paths, or context."""

    requested = any(str(environment.get(key, "")).strip() for key in _ENV_KEYS)
    return {
        "activation_requested": requested,
        "transport": "one-time-handle" if requested else "none",
    }


def consume_group_activation_from_environment(
    environment: Mapping[str, str],
    *,
    context: OperatorContext,
    now: datetime,
) -> GroupAnalysisOptIn | None:
    """Consume an explicitly complete internal activation environment once."""

    values = {key: str(environment.get(key, "")).strip() for key in _ENV_KEYS}
    present = {key for key, value in values.items() if value}
    if not present:
        return None
    if present != _ENV_KEYS:
        raise ValueError("group activation runtime environment is incomplete")
    if values[GROUP_ACTIVATION_RUNTIME_ENV] != "1":
        raise ValueError("group activation runtime marker is invalid")

    root = Path(values[GROUP_ACTIVATION_ROOT_ENV]).expanduser().resolve()
    store = GroupActivationHandleStore(root)
    return store.consume(
        values[GROUP_ACTIVATION_HANDLE_ENV],
        context=context,
        now=now,
    )


def issue_child_group_activation_environment(
    opt_in: GroupAnalysisOptIn,
    *,
    parent_environment: Mapping[str, str],
    context: OperatorContext,
    now: datetime,
    ttl_seconds: int = 60,
) -> dict[str, str]:
    """Reissue an in-memory candidate as a fresh one-time child-worker handle."""

    values = {key: str(parent_environment.get(key, "")).strip() for key in _ENV_KEYS}
    if {key for key, value in values.items() if value} != _ENV_KEYS:
        raise ValueError("group activation runtime environment is incomplete")
    if values[GROUP_ACTIVATION_RUNTIME_ENV] != "1":
        raise ValueError("group activation runtime marker is invalid")
    store = GroupActivationHandleStore(
        Path(values[GROUP_ACTIVATION_ROOT_ENV]).expanduser().resolve()
    )
    issued = store.issue(
        opt_in,
        context=context,
        now=now,
        ttl_seconds=ttl_seconds,
    )
    return build_group_activation_environment(
        store=store,
        activation_handle=str(issued["activation_handle"]),
    )
