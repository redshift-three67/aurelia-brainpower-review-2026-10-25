"""Pure in-memory resolution of consented pseudonymous group-member baselines."""
from __future__ import annotations

import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Protocol, Sequence

import numpy as np

from core.compliance.operator_context import OperatorContext, OwnershipError
from core.profiles.profile import ClientProfile


GROUP_MEMBER_RESOLVER_VERSION = "group-member-baseline-v1"
GROUP_MEMBER_CONSENT_VERSION = "group-analysis-v1"
_GROUP_PURPOSE = "group-analysis-v1"
_CLIENT_ID = re.compile(r"^cli-[A-Za-z0-9][A-Za-z0-9_-]{0,123}$")


@dataclass(frozen=True)
class GroupMemberIdentity:
    client_id: str
    owner_id: str
    tenant_id: str
    first_name: str
    last_name: str
    birth_date: str
    birth_place: str
    analysis_consent: bool
    consent_version: str


class GroupMemberIdentitySource(Protocol):
    def resolve(self, client_id: str) -> GroupMemberIdentity: ...


@dataclass(frozen=True)
class GroupMemberRateResolution:
    member_rates: Mapping[str, np.ndarray]
    resolver_version: str = GROUP_MEMBER_RESOLVER_VERSION

    def safe_summary(self) -> dict[str, object]:
        return {
            "resolver_version": self.resolver_version,
            "member_count": len(self.member_rates),
            "purpose": _GROUP_PURPOSE,
        }


def _canonical_member_ids(client_ids: Sequence[str]) -> list[str]:
    resolved = [str(client_id or "").strip() for client_id in client_ids]
    if len(resolved) < 2:
        raise ValueError("group member resolver requires at least two members")
    if len(set(resolved)) != len(resolved):
        raise ValueError("group member client_id must be unique")
    if any(not _CLIENT_ID.fullmatch(client_id) for client_id in resolved):
        raise ValueError("group member client_id must be pseudonymous and canonical")
    return sorted(resolved)


def _validate_identity(
    identity: GroupMemberIdentity,
    *,
    requested_client_id: str,
    context: OperatorContext,
) -> None:
    if identity.client_id != requested_client_id:
        raise ValueError("identity source returned a different requested client_id")
    if identity.owner_id not in (context.operator_id, context.workspace_id):
        raise OwnershipError("group member identity belongs to another owner")
    if identity.tenant_id != context.tenant_id:
        raise OwnershipError("group member identity belongs to another tenant")
    if not identity.analysis_consent:
        raise ValueError("group member analysis consent is required")
    if identity.consent_version != GROUP_MEMBER_CONSENT_VERSION:
        raise ValueError("group member consent version is not current")
    required_identity = (
        identity.first_name,
        identity.last_name,
        identity.birth_date,
        identity.birth_place,
    )
    if any(not str(value or "").strip() for value in required_identity):
        raise ValueError("group member identity fields must be complete")


def resolve_group_member_rates(
    client_ids: Sequence[str],
    *,
    source: GroupMemberIdentitySource,
    context: OperatorContext,
) -> GroupMemberRateResolution:
    """Resolve deterministic default profile rates without serialization or I/O."""

    # Local import keeps the domain contract free from service initialization and I/O.
    from services.analysis_service import AnalysisService

    service = AnalysisService(rate_database={}, h_level=0.0)
    rates: dict[str, np.ndarray] = {}
    for client_id in _canonical_member_ids(client_ids):
        identity = source.resolve(client_id)
        _validate_identity(identity, requested_client_id=client_id, context=context)
        profile = ClientProfile(
            name=identity.last_name,
            first_name=identity.first_name,
            birth_date=identity.birth_date,
            birth_place=identity.birth_place,
            image_signature=None,
            personal_profile=None,
            planet_type="",
        )
        member_rates = np.asarray(service.encode_profile(profile), dtype=float).copy()
        if member_rates.ndim != 1 or member_rates.size == 0 or not np.all(np.isfinite(member_rates)):
            raise ValueError("resolved group member rates must be finite and one-dimensional")
        member_rates.setflags(write=False)
        rates[client_id] = member_rates

    return GroupMemberRateResolution(member_rates=MappingProxyType(rates))
