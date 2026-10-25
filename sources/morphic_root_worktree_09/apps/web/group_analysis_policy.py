"""Default-safe local policy staging for future group analysis.

The policy can record an explicit bounded strength and expose the server-owned
kill switch. It never resolves identities, creates opt-ins, or starts scans.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, Field

from apps.web.security import verify_api_key


GROUP_ANALYSIS_POLICY_VERSION = "group-analysis-policy-v1"
_GROUP_ANALYSIS_FLAG = "MORPHIC_GROUP_ANALYSIS_ENABLED"
_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})


router = APIRouter(
    tags=["group-analysis-policy"], dependencies=[Depends(verify_api_key)]
)


def group_analysis_feature_enabled() -> bool:
    return os.getenv(_GROUP_ANALYSIS_FLAG, "").strip().casefold() in _TRUE_VALUES


class GroupAnalysisPolicyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strength: float = Field(ge=0.0, le=1.0)


@dataclass
class GroupAnalysisPolicyService:
    """Hold a local policy candidate without any productive effect."""

    strength: float | None = None

    def safe_summary(self) -> dict[str, object]:
        return {
            "policy_version": GROUP_ANALYSIS_POLICY_VERSION,
            "feature_enabled": group_analysis_feature_enabled(),
            "strength": self.strength,
            "strength_explicit": self.strength is not None,
            "analysis_ready": False,
            "productive_effect": False,
        }

    def set_strength(self, strength: float) -> dict[str, object]:
        value = float(strength)
        if not 0.0 <= value <= 1.0:
            raise ValueError("group analysis strength must be between 0 and 1")
        self.strength = value
        return self.safe_summary()


def _service(request: Request) -> GroupAnalysisPolicyService:
    service = request.app.state.group_analysis_policy
    if not isinstance(service, GroupAnalysisPolicyService):
        raise RuntimeError("group analysis policy is unavailable")
    return service


@router.get("/api/workbench/group-analysis-policy")
def get_group_analysis_policy(request: Request) -> dict[str, object]:
    return _service(request).safe_summary()


@router.put("/api/workbench/group-analysis-policy")
def set_group_analysis_policy(
    request: Request,
    payload: GroupAnalysisPolicyRequest,
) -> dict[str, object]:
    return _service(request).set_strength(payload.strength)
