"""Immutable identity for an original rate in a promoted analysis draft."""

from __future__ import annotations

import hmac
import re
import uuid
from dataclasses import dataclass
from typing import Any, ClassVar

from ..persistence import document_digest
from ..scope import ScopeContext


_HEX_64 = re.compile(r"[0-9a-f]{64}\Z")
_HEX_32 = re.compile(r"[0-9a-f]{32}\Z")
_PAYLOAD_FIELDS = frozenset(
    {
        "schemaVersion",
        "scope",
        "caseRef",
        "sessionId",
        "draftId",
        "sessionRevision",
        "rateIndex",
        "analysisDigest",
    }
)
_SCOPE_FIELDS = frozenset({"tenant_id", "client_id", "job_id"})


def _canonical_uuid(value: object) -> bool:
    if type(value) is not str:
        return False
    try:
        return str(uuid.UUID(value)) == value
    except (ValueError, AttributeError):
        return False


def _nonnegative_int(value: object) -> bool:
    return type(value) is int and value >= 0


@dataclass(frozen=True, slots=True)
class ObservationBinding:
    """Detached, strict identity of one rate in a pinned analysis result."""

    scope: ScopeContext
    case_ref: str
    session_id: str
    draft_id: str
    session_revision: int
    rate_index: int
    analysis_digest: str

    SCHEMA_VERSION: ClassVar[int] = 1

    def __post_init__(self) -> None:
        if not isinstance(self.scope, ScopeContext):
            raise TypeError("scope must be a ScopeContext")
        if type(self.case_ref) is not str or not _HEX_64.fullmatch(self.case_ref):
            raise ValueError("case_ref must be 64 lowercase hexadecimal characters")
        if type(self.session_id) is not str or not _HEX_32.fullmatch(self.session_id):
            raise ValueError("session_id must be 32 lowercase hexadecimal characters")
        if not _canonical_uuid(self.draft_id):
            raise ValueError("draft_id must be a canonical UUID string")
        if not _nonnegative_int(self.session_revision):
            raise ValueError("session_revision must be a nonnegative integer")
        if not _nonnegative_int(self.rate_index):
            raise ValueError("rate_index must be a nonnegative integer")
        if type(self.analysis_digest) is not str or not _HEX_64.fullmatch(self.analysis_digest):
            raise ValueError("analysis_digest must be 64 lowercase hexadecimal characters")

    def payload(self) -> dict[str, Any]:
        """Return a fresh JSON-shaped value with no mutable aliases."""
        return {
            "schemaVersion": self.SCHEMA_VERSION,
            "scope": self.scope.to_dict(),
            "caseRef": self.case_ref,
            "sessionId": self.session_id,
            "draftId": self.draft_id,
            "sessionRevision": self.session_revision,
            "rateIndex": self.rate_index,
            "analysisDigest": self.analysis_digest,
        }

    @classmethod
    def from_payload(cls, payload: object) -> ObservationBinding:
        """Parse only the exact v1 JSON contract; reject aliases and extensions."""
        if type(payload) is not dict:
            raise TypeError("observation binding payload must be an object")
        if set(payload) != _PAYLOAD_FIELDS:
            raise ValueError("observation binding payload fields do not match schema v1")
        if type(payload["schemaVersion"]) is not int or payload["schemaVersion"] != cls.SCHEMA_VERSION:
            raise ValueError("unsupported observation binding schema version")

        scope_value = payload["scope"]
        if type(scope_value) is not dict or set(scope_value) != _SCOPE_FIELDS:
            raise ValueError("observation binding scope fields do not match")
        if any(type(scope_value[field]) is not str for field in _SCOPE_FIELDS):
            raise TypeError("observation binding scope values must be strings")

        return cls(
            scope=ScopeContext(
                tenant_id=scope_value["tenant_id"],
                client_id=scope_value["client_id"],
                job_id=scope_value["job_id"],
            ),
            case_ref=payload["caseRef"],
            session_id=payload["sessionId"],
            draft_id=payload["draftId"],
            session_revision=payload["sessionRevision"],
            rate_index=payload["rateIndex"],
            analysis_digest=payload["analysisDigest"],
        )


def _valid_analysis_rates(analysis: object) -> list[dict[str, Any]] | None:
    if type(analysis) is not dict:
        return None
    rates = analysis.get("rateObjects")
    if type(rates) is not list:
        return None
    case_gv = analysis.get("generalVitality")
    if case_gv is not None and type(case_gv) is not int:
        return None
    for rate in rates:
        if type(rate) is not dict:
            return None
        if type(rate.get("nameOrRate")) is not str:
            return None
        if type(rate.get("energeticValue")) is not int:
            return None
        if "gv" in rate and type(rate["gv"]) is not int:
            return None
        if rate.get("potency") is not None and type(rate["potency"]) is not str:
            return None
    return rates


def bind_promoted_rates(
    draft: dict[str, Any] | None,
    case: dict[str, Any] | None,
    *,
    scope: ScopeContext,
    case_ref: str,
    source_case_ref: str | None = None,
) -> dict[int, ObservationBinding]:
    """Bind original rate-array indices to the draft's exact stored session.

    This helper is intentionally read-only and fail-closed. Promotion may later
    sort or filter rates; the returned keys always refer to their source order.
    """
    if not isinstance(scope, ScopeContext):
        return {}
    if type(case_ref) is not str or not _HEX_64.fullmatch(case_ref):
        return {}
    if (
        type(source_case_ref) is not str
        or not _HEX_64.fullmatch(source_case_ref)
        or not hmac.compare_digest(source_case_ref, case_ref)
    ):
        return {}
    if type(draft) is not dict or type(case) is not dict:
        return {}

    expected_scope = scope.to_dict()
    if type(draft.get("scope")) is not dict or draft["scope"] != expected_scope:
        return {}
    if type(case.get("scope")) is not dict or case["scope"] != expected_scope:
        return {}

    draft_id = draft.get("id")
    session_id = draft.get("sessionId")
    revision = draft.get("sessionRevision")
    if not _canonical_uuid(draft_id):
        return {}
    if type(session_id) is not str or not _HEX_32.fullmatch(session_id):
        return {}
    if not _nonnegative_int(revision):
        return {}

    sessions = case.get("sessionList")
    if type(sessions) is not list or any(type(item) is not dict for item in sessions):
        return {}
    matches = [item for item in sessions if item.get("sessionId") == session_id]
    if len(matches) != 1:
        return {}
    session = matches[0]
    if session.get("draftId") != draft_id:
        return {}
    if not _nonnegative_int(session.get("revision")) or session["revision"] != revision:
        return {}

    draft_payload = draft.get("payload")
    analysis = session.get("analysisResult")
    if type(draft_payload) is not dict or type(analysis) is not dict:
        return {}
    try:
        if draft_payload != analysis:
            return {}
        rates = _valid_analysis_rates(analysis)
        if rates is None:
            return {}
        analysis_digest = document_digest(analysis)
    except (TypeError, ValueError, RecursionError):
        return {}
    if type(analysis_digest) is not str or not _HEX_64.fullmatch(analysis_digest):
        return {}

    try:
        return {
            index: ObservationBinding(
                scope=scope,
                case_ref=case_ref,
                session_id=session_id,
                draft_id=draft_id,
                session_revision=revision,
                rate_index=index,
                analysis_digest=analysis_digest,
            )
            for index in range(len(rates))
        }
    except (TypeError, ValueError):
        return {}
