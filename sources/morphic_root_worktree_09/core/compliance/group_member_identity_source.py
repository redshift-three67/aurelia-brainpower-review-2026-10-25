"""Owner-/tenant-bound adapter from protected local identities to group rates."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Callable

from core.compliance.local_client_identity_store import LocalClientIdentityStore
from core.compliance.operator_context import OperatorContext
from core.profiles.group_member_rate_resolver import (
    GROUP_MEMBER_CONSENT_VERSION,
    GroupMemberIdentity,
)


class LocalClientIdentitySource:
    """Resolve group identities exclusively from the DPAPI-protected store."""

    def __init__(
        self,
        store: LocalClientIdentityStore,
        *,
        context: OperatorContext,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._store = store
        self._context = context
        self._clock = clock or (lambda: datetime.now(UTC))

    def resolve(self, client_id: str) -> GroupMemberIdentity:
        requested = str(client_id or "").strip()
        entry = self._store.resolve(requested, context=self._context)
        consent = entry.get("group_analysis")
        if not isinstance(consent, dict) or not consent.get("enabled"):
            raise ValueError("group analysis consent is required")
        consent_version = str(consent.get("consent_version") or "").strip()
        if consent_version != GROUP_MEMBER_CONSENT_VERSION:
            raise ValueError("group analysis consent version is not current")
        valid_until_text = str(consent.get("valid_until") or "").strip()
        try:
            valid_until = datetime.fromisoformat(valid_until_text.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("group analysis consent expiry is invalid") from exc
        if valid_until.tzinfo is None or valid_until.utcoffset() is None:
            raise ValueError("group analysis consent expiry is not timezone-aware")
        reference = self._clock()
        if reference.tzinfo is None or reference.utcoffset() is None:
            raise ValueError("identity source clock must be timezone-aware")
        if reference.astimezone(UTC) >= valid_until.astimezone(UTC):
            raise ValueError("group analysis consent has expired")

        return GroupMemberIdentity(
            client_id=requested,
            owner_id=str(entry.get("owner_id") or "").strip(),
            tenant_id=str(entry.get("tenant_id") or "").strip(),
            first_name=str(entry.get("first_name") or "").strip(),
            last_name=str(entry.get("last_name") or entry.get("name") or "").strip(),
            birth_date=str(entry.get("birth_date") or "").strip(),
            birth_place=str(entry.get("birth_place") or "").strip(),
            analysis_consent=True,
            consent_version=consent_version,
        )
