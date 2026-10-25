"""Local-only enrollment and revocation API for protected group identities.

This router never activates analysis and is not imported by scan, launcher,
worker, report, trace, or manifest-output paths.
"""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator

from apps.web.security import verify_api_key

from core.compliance.local_client_identity_store import LocalClientIdentityStore
from core.compliance.operator_context import OperatorContext, OwnershipError
from core.compliance.runtime_manifest import runtime_root
from core.profiles.group_member_rate_resolver import GROUP_MEMBER_CONSENT_VERSION


router = APIRouter(tags=["group-consents"], dependencies=[Depends(verify_api_key)])


class GroupIdentityRegistrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    first_name: str = Field(min_length=1, max_length=120)
    last_name: str = Field(min_length=1, max_length=120)
    birth_date: str = Field(min_length=4, max_length=32)
    birth_place: str = Field(min_length=1, max_length=160)
    persistence_consent: Literal[True]
    retention_days: int = Field(ge=1, le=3650)


class GroupConsentEnrollmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    confirmation_id: str = Field(pattern=r"^cli-[0-9a-f]{20}$")
    enabled: bool
    valid_until: datetime | None = None

    @field_validator("valid_until")
    @classmethod
    def require_aware_expiry(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("valid_until must be timezone-aware")
        return value


def build_client_identity_store(runtime_dir: str | Path | None) -> LocalClientIdentityStore:
    root = Path(runtime_dir) if runtime_dir is not None else runtime_root()
    return LocalClientIdentityStore(root / "client-identities")


def _store(request: Request) -> LocalClientIdentityStore:
    store = request.app.state.client_identity_store
    if not isinstance(store, LocalClientIdentityStore):
        raise RuntimeError("client identity store is unavailable")
    return store


def _context(request: Request) -> OperatorContext:
    context = request.app.state.operator_context
    if not isinstance(context, OperatorContext):
        raise RuntimeError("operator context is unavailable")
    return context


def _invalidate_activation_context(request: Request) -> None:
    invalidate = getattr(request.app.state, "invalidate_group_analysis_context", None)
    if not callable(invalidate):
        raise RuntimeError("group activation handle store is unavailable")
    invalidate(_context(request))


@router.get("/api/workbench/group-consent")
def list_group_consents(request: Request) -> dict[str, object]:
    return {"identities": _store(request).list_safe(context=_context(request))}


@router.post("/api/workbench/group-consent/identity")
def register_group_identity(
    request: Request,
    payload: GroupIdentityRegistrationRequest,
) -> dict[str, object]:
    identity = payload.model_dump(exclude={"persistence_consent", "retention_days"})
    try:
        return _store(request).register(
            identity,
            context=_context(request),
            retention_days=payload.retention_days,
        )
    except (ValueError, OwnershipError) as exc:
        status = 403 if isinstance(exc, OwnershipError) else 422
        raise HTTPException(status_code=status, detail=str(exc)) from exc


@router.put("/api/workbench/group-consent/{client_id}")
def set_group_consent(
    client_id: str,
    request: Request,
    payload: GroupConsentEnrollmentRequest,
) -> dict[str, object]:
    if payload.confirmation_id != client_id:
        raise HTTPException(
            status_code=422,
            detail="confirmation_id must exactly match client_id",
        )
    if payload.enabled and payload.valid_until is None:
        raise HTTPException(status_code=422, detail="enabled consent requires valid_until")
    valid_until = payload.valid_until or datetime.now(UTC)
    try:
        if payload.enabled is False:
            _store(request).resolve(client_id, context=_context(request))
            _invalidate_activation_context(request)
        result = _store(request).record_group_analysis_consent(
            client_id,
            context=_context(request),
            enabled=payload.enabled,
            consent_version=GROUP_MEMBER_CONSENT_VERSION,
            valid_until=valid_until,
        )
        return result
    except OwnershipError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="client identity not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
