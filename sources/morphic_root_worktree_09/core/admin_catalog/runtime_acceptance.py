"""Synthetic F8.4 acceptance harness for explicit Catalog runtime activation.

The harness is intentionally small: it owns no persistence primitive and no
runtime selection logic. It only exercises existing AdminCatalogService,
CatalogStore, and runtime_adapter boundaries with synthetic data supplied by
the caller.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Sequence

from .contracts import CatalogContext, CatalogEntry
from .runtime_adapter import (
    ADMIN_CATALOG_ENABLED_ENV,
    CatalogRuntimeError,
    load_configured_runtime,
)
from .service import AdminCatalogService
from .store import CatalogStore


class RuntimeAcceptanceError(RuntimeError):
    """F8.4 acceptance could not complete through the expected public boundary."""


@dataclass(frozen=True, slots=True)
class RuntimeAcceptanceEvidence:
    status: str
    activation_versions: tuple[int, int, int]
    revision_after_reload: str
    revision_after_second_activation: str
    revision_after_rollback: str
    group_ids_after_reload: tuple[str, ...]
    group_ids_after_second_activation: tuple[str, ...]
    group_ids_after_rollback: tuple[str, ...]
    foreign_context_error_code: str
    kill_switch_disabled_selected_source: str
    audit_chain_valid: bool
    redacted: bool

    def redacted_mapping(self) -> dict[str, object]:
        return asdict(self)


_CATALOG_ON = {ADMIN_CATALOG_ENABLED_ENV: "on"}
_CATALOG_OFF = {ADMIN_CATALOG_ENABLED_ENV: "off"}
_FORBIDDEN_EVIDENCE_FRAGMENTS = (
    "birth_date",
    "email",
    "nonce",
    "patient",
    "person_name",
    "phone",
    "token",
)


def _publish_and_activate(
    service: AdminCatalogService,
    context: CatalogContext,
    *,
    draft_id: str,
    revision_id: str,
    entries: Sequence[CatalogEntry],
    expected_previous_revision_id: str | None,
    expected_activation_version: int,
) -> int:
    state = service.create_draft(context, draft_id, tuple(entries))
    validation = service.validate_draft(context, draft_id)
    if not validation.is_valid:
        codes = ", ".join(issue.code for issue in validation.errors)
        raise RuntimeAcceptanceError(f"synthetic draft validation failed: {codes}")
    service.diff_draft(context, draft_id)
    service.publish_draft(
        context,
        draft_id,
        revision_id,
        expected_draft_version=state.version,
    )
    return service.activate_revision(
        context,
        revision_id,
        expected_previous_revision_id=expected_previous_revision_id,
        expected_activation_version=expected_activation_version,
        actor_id=context.operator_id,
        reason=f"F8.4 synthetic acceptance activate {revision_id}",
    )


def _reload_store(service: AdminCatalogService) -> CatalogStore:
    return CatalogStore(service.store.db_path)


def _catalog_group_ids(store: CatalogStore, context: CatalogContext) -> tuple[str, ...]:
    selected = load_configured_runtime(store, context, environ=_CATALOG_ON)
    if selected.catalog_snapshot is None:
        raise RuntimeAcceptanceError("catalog runtime did not return a snapshot")
    return tuple(selected.subgroup_provider.list_groups())  # type: ignore[union-attr]


def _foreign_context_error_code(
    store: CatalogStore,
    context: CatalogContext,
) -> str:
    foreign = CatalogContext(
        operator_id=f"{context.operator_id}-foreign",
        workspace_id=context.workspace_id,
        tenant_id=context.tenant_id,
        scope=context.scope,
    )
    try:
        load_configured_runtime(store, foreign, environ=_CATALOG_ON)
    except CatalogRuntimeError as exc:
        return exc.code
    raise RuntimeAcceptanceError("foreign context unexpectedly loaded Catalog runtime")


def _disabled_selected_source(store: CatalogStore, context: CatalogContext) -> str:
    selected = load_configured_runtime(store, context, environ=_CATALOG_OFF)
    return selected.selected_source


def _is_redacted(evidence: RuntimeAcceptanceEvidence) -> bool:
    encoded = json.dumps(evidence.redacted_mapping(), sort_keys=True).casefold()
    return not any(fragment in encoded for fragment in _FORBIDDEN_EVIDENCE_FRAGMENTS)


def run_synthetic_runtime_acceptance(
    service: AdminCatalogService,
    context: CatalogContext,
    revision_one_entries: Sequence[CatalogEntry],
    revision_two_entries: Sequence[CatalogEntry],
) -> RuntimeAcceptanceEvidence:
    """Run the isolated F8.4 lifecycle and return sanitized evidence."""

    if not isinstance(service, AdminCatalogService):
        raise TypeError("service must be AdminCatalogService")
    if not isinstance(context, CatalogContext):
        raise TypeError("context must be CatalogContext")

    activation_v1 = _publish_and_activate(
        service,
        context,
        draft_id="draft-a",
        revision_id="revision-a",
        entries=revision_one_entries,
        expected_previous_revision_id=None,
        expected_activation_version=0,
    )
    reloaded_after_first = _reload_store(service)
    first_groups = _catalog_group_ids(reloaded_after_first, context)
    first_revision = load_configured_runtime(
        reloaded_after_first,
        context,
        environ=_CATALOG_ON,
    ).active_revision_id

    activation_v2 = _publish_and_activate(
        service,
        context,
        draft_id="draft-b",
        revision_id="revision-b",
        entries=revision_two_entries,
        expected_previous_revision_id="revision-a",
        expected_activation_version=activation_v1,
    )
    second_store = _reload_store(service)
    second_groups = _catalog_group_ids(second_store, context)
    second_revision = load_configured_runtime(
        second_store,
        context,
        environ=_CATALOG_ON,
    ).active_revision_id

    activation_v3 = service.rollback(
        context,
        target_revision_id="revision-a",
        expected_previous_revision_id="revision-b",
        expected_activation_version=activation_v2,
        actor_id=context.operator_id,
        reason="F8.4 synthetic acceptance rollback to revision-a",
    )
    rollback_store = _reload_store(service)
    rollback_groups = _catalog_group_ids(rollback_store, context)
    rollback_revision = load_configured_runtime(
        rollback_store,
        context,
        environ=_CATALOG_ON,
    ).active_revision_id

    evidence = RuntimeAcceptanceEvidence(
        status="passed",
        activation_versions=(activation_v1, activation_v2, activation_v3),
        revision_after_reload=str(first_revision),
        revision_after_second_activation=str(second_revision),
        revision_after_rollback=str(rollback_revision),
        group_ids_after_reload=first_groups,
        group_ids_after_second_activation=second_groups,
        group_ids_after_rollback=rollback_groups,
        foreign_context_error_code=_foreign_context_error_code(rollback_store, context),
        kill_switch_disabled_selected_source=_disabled_selected_source(
            rollback_store,
            context,
        ),
        audit_chain_valid=service.store.verify_audit_chain(context),
        redacted=False,
    )
    return RuntimeAcceptanceEvidence(
        **{**evidence.redacted_mapping(), "redacted": _is_redacted(evidence)}
    )


__all__ = [
    "RuntimeAcceptanceError",
    "RuntimeAcceptanceEvidence",
    "run_synthetic_runtime_acceptance",
]
