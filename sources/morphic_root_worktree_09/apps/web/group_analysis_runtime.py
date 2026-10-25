"""Server-side preparation for explicitly requested local group scan activation."""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Protocol

from apps.web.contracts import Phase1ScanRequest
from apps.web.group_analysis_activation import build_resolved_group_draft_opt_in
from apps.web.group_analysis_policy import (
    GroupAnalysisPolicyService,
    group_analysis_feature_enabled,
)
from core.compliance.group_activation_handle_store import GroupActivationHandleStore
from core.compliance.group_activation_runtime import build_group_activation_environment
from core.compliance.group_member_identity_source import LocalClientIdentitySource
from core.compliance.local_client_identity_store import LocalClientIdentityStore
from core.compliance.operator_context import OperatorContext
from core.compliance.runtime_manifest import stable_client_id


class _DraftStore(Protocol):
    def load(self, draft_id: str): ...


def prepare_group_scan_activation(
    request: Phase1ScanRequest,
    *,
    policy: GroupAnalysisPolicyService,
    draft_store: _DraftStore,
    identity_store: LocalClientIdentityStore,
    handle_store: GroupActivationHandleStore,
    context: OperatorContext,
    now: datetime,
) -> dict[str, str] | None:
    """Prepare a root worker handle, or preserve exact default inactivity."""

    draft_id = request.group_draft_id.strip()
    if not draft_id or not group_analysis_feature_enabled():
        return None
    strength = policy.strength
    if strength is None or strength == 0.0:
        return None

    authorization_generation = handle_store.authorization_generation(context)
    envelope = draft_store.load(draft_id)
    draft = getattr(envelope, "group", None)
    if draft is None:
        raise LookupError("group draft not found")
    subject_id = stable_client_id(
        {
            "last_name": request.last_name,
            "first_name": request.first_name,
            "birth_date": request.birth_date,
            "birth_place": request.birth_place,
        }
    )
    source = LocalClientIdentitySource(identity_store, context=context)
    opt_in = build_resolved_group_draft_opt_in(
        draft,
        subject_id=subject_id,
        context=context,
        source=source,
        strength=strength,
    )
    opt_in = replace(opt_in, activation_generation=authorization_generation)
    issued = handle_store.issue(opt_in, context=context, now=now)
    return build_group_activation_environment(
        store=handle_store,
        activation_handle=str(issued["activation_handle"]),
    )
