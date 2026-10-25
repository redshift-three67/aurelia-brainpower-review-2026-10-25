"""Local-only bridge from a consented group draft to an in-memory authorization.

This module is not a FastAPI route and is deliberately not imported by scan,
launcher, report, trace, job, manifest, or persistence code.
"""
from __future__ import annotations

from typing import Mapping

import numpy as np

from apps.web.client_context_contracts import GroupContextDraft
from core.compliance.group_analysis_authorization import (
    GroupAnalysisAuthorization,
    authorize_group_opt_in,
)
from core.compliance.operator_context import OperatorContext
from core.profiles.group_vector import (
    GroupAnalysisOptIn,
    GroupMemberRates,
    build_group_centroid,
)
from core.profiles.group_member_rate_resolver import (
    GroupMemberIdentitySource,
    resolve_group_member_rates,
)


_PURPOSE = "group-analysis-v1"


def build_group_draft_authorization(
    draft: GroupContextDraft,
    *,
    subject_id: str,
    context: OperatorContext,
) -> GroupAnalysisAuthorization:
    """Bind a separately consented local group draft to an enrolled subject."""

    if draft.analysis_consent is not True:
        raise ValueError("group analysis consent must be accepted")
    enrolled_member_ids = {member.client_id for member in draft.members}
    if subject_id not in enrolled_member_ids:
        raise ValueError("subject must be enrolled in the consented group")
    if not all(member.consent_recorded is True for member in draft.members):
        raise ValueError("all group member consents must be verified")
    return GroupAnalysisAuthorization(
        subject_id=subject_id,
        owner_id=context.operator_id,
        member_count=len(draft.members),
        member_consent_verified=True,
        purpose=_PURPOSE,
    )


def build_group_draft_opt_in(
    draft: GroupContextDraft,
    *,
    subject_id: str,
    context: OperatorContext,
    member_rates: Mapping[str, np.ndarray],
    strength: float,
) -> GroupAnalysisOptIn:
    """Build a fully consented, local in-memory group-analysis candidate.

    The function performs no I/O and returns no raw group data outside the
    in-memory centroid held by the returned opt-in object.
    """

    authorization = build_group_draft_authorization(
        draft,
        subject_id=subject_id,
        context=context,
    )
    enrolled_member_ids = {member.client_id for member in draft.members}
    if set(member_rates) != enrolled_member_ids:
        raise ValueError("member rates must match exactly the consented group membership")
    centroid = build_group_centroid(
        GroupMemberRates(
            client_id=member.client_id,
            rates=np.asarray(member_rates[member.client_id], dtype=float),
            consent_recorded=member.consent_recorded,
        )
        for member in draft.members
    )
    return authorize_group_opt_in(
        GroupAnalysisOptIn(
            enabled=True,
            centroid_rates=centroid,
            strength=strength,
            consent_verified=True,
        ),
        authorization,
        context=context,
    )


def build_resolved_group_draft_opt_in(
    draft: GroupContextDraft,
    *,
    subject_id: str,
    context: OperatorContext,
    source: GroupMemberIdentitySource,
    strength: float,
) -> GroupAnalysisOptIn:
    """Resolve the exact consented membership and build an in-memory opt-in.

    Draft-level consent is checked before the identity source is accessed. The
    resolved identities and rates are never serialized or returned separately.
    """

    build_group_draft_authorization(
        draft,
        subject_id=subject_id,
        context=context,
    )
    resolution = resolve_group_member_rates(
        [member.client_id for member in draft.members],
        source=source,
        context=context,
    )
    return build_group_draft_opt_in(
        draft,
        subject_id=subject_id,
        context=context,
        member_rates=resolution.member_rates,
        strength=strength,
    )
