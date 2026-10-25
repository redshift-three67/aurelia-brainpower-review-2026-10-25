"""Local owner- and consent-bound authorization for in-memory group analysis.

This module deliberately has no web, CLI, persistence, report, trace, job, or
manifest dependency. It turns no raw group data into an external payload.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from core.compliance.operator_context import OperatorContext, OwnershipError
from core.profiles.group_vector import GroupAnalysisOptIn


_SUBJECT_ID = re.compile(r"^cli-[A-Za-z0-9_-]{1,124}$")
_PURPOSE = "group-analysis-v1"


@dataclass(frozen=True)
class GroupAnalysisAuthorization:
    subject_id: str
    owner_id: str
    member_count: int
    member_consent_verified: bool
    purpose: str

    def safe_summary(self) -> dict[str, object]:
        return {
            "vector": "group",
            "purpose": self.purpose,
            "member_count": self.member_count,
            "activation_requested": True,
        }


def _validate_authorization(authorization: GroupAnalysisAuthorization) -> None:
    if not _SUBJECT_ID.fullmatch(str(authorization.subject_id or "").strip()):
        raise ValueError("subject_id must be a canonical pseudonymous client ID")
    if not str(authorization.owner_id or "").strip():
        raise ValueError("owner_id is required")
    if authorization.purpose != _PURPOSE:
        raise ValueError(f"purpose must be {_PURPOSE}")
    if authorization.member_count < 2:
        raise ValueError("member_count must be at least two")
    if authorization.member_consent_verified is not True:
        raise ValueError("member consent must be verified")


def authorize_group_opt_in(
    group_opt_in: GroupAnalysisOptIn,
    authorization: GroupAnalysisAuthorization | None,
    *,
    context: OperatorContext,
) -> GroupAnalysisOptIn:
    """Return only a locally owner-bound, consented enabled opt-in.

    Disabled configurations intentionally stay default-equivalent and require no
    authorization. Enabled configurations fail closed before reaching analysis.
    """

    if group_opt_in.enabled is not True:
        return group_opt_in
    if authorization is None:
        raise ValueError("enabled group analysis requires authorization")
    _validate_authorization(authorization)
    if authorization.owner_id not in (context.operator_id, context.workspace_id):
        raise OwnershipError("group analysis authorization belongs to another operator/workspace")
    if group_opt_in.consent_verified is not True:
        raise ValueError("group opt-in consent must be verified")
    return group_opt_in
