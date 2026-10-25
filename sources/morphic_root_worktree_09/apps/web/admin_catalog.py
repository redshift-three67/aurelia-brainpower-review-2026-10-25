"""Protected Web API facade for the offline Admin Catalog."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field

from apps.web.admin_security import require_admin_request
from core.admin_catalog import (
    AdminCatalogService,
    CatalogContext,
    CatalogEntry,
    CatalogServiceError,
    ContractError,
    DraftConflictError,
    DraftNotFoundError,
    EntryType,
    RevisionConflictError,
)
from core.admin_catalog.paths import catalog_database_path
from core.admin_catalog.runtime_adapter import (
    CatalogRuntimeConfigError,
    CatalogRuntimeError,
    ConfiguredRuntime,
    load_configured_runtime,
)
from core.admin_catalog.validation import ValidationIssue, ValidationResult
from core.admin_catalog.validation_key_composition import (
    ValidationKeyCompositionError,
    build_admin_catalog_service,
)
from core.compliance.operator_context import OperatorContext


router = APIRouter(prefix="/api/admin/catalog", tags=["admin-catalog"])
_FORBIDDEN_RUNTIME_RESPONSE_FRAGMENTS = (
    "birth_date",
    "email",
    "nonce",
    "patient",
    "person_name",
    "phone",
    "token",
)


class CatalogEntryPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entry_type: EntryType
    entry_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    provenance: str = Field(min_length=1)
    data: dict[str, Any]


class DraftWriteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    draft_id: str = Field(min_length=1)
    expected_version: int = Field(ge=0)
    reason: str = Field(min_length=1)
    entries: list[CatalogEntryPayload]


class DraftUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    expected_version: int = Field(ge=1)
    reason: str = Field(min_length=1)
    entries: list[CatalogEntryPayload]


class DraftValidateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    expected_version: int = Field(ge=1)
    reason: str = Field(min_length=1)


class DraftPublishRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    revision_id: str = Field(min_length=1)
    expected_draft_version: int = Field(ge=1)
    reason: str = Field(min_length=1)


class ActivateRevisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    expected_previous_revision_id: str | None = None
    expected_activation_version: int = Field(ge=0)
    reason: str = Field(min_length=1)


class RollbackRevisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    expected_previous_revision_id: str = Field(min_length=1)
    expected_activation_version: int = Field(ge=1)
    reason: str = Field(min_length=1)


def admin_catalog_context_from_operator(
    operator_context: OperatorContext,
) -> CatalogContext:
    return CatalogContext(
        operator_id=operator_context.operator_id,
        workspace_id=operator_context.workspace_id,
        tenant_id=operator_context.tenant_id,
        scope="workspace",
    )


def default_admin_catalog_service_factory(
    context: CatalogContext,
) -> AdminCatalogService:
    db_path = catalog_database_path(context, writable=True)
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return build_admin_catalog_service(
        db_path,
        require_validation_key=True,
    )


def _catalog_context(request: Request) -> CatalogContext:
    factory = getattr(
        request.app.state,
        "admin_catalog_context_factory",
        admin_catalog_context_from_operator,
    )
    try:
        context = factory(request.app.state.operator_context)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="admin catalog context unavailable",
        ) from exc
    if not isinstance(context, CatalogContext):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="admin catalog context unavailable",
        )
    return context


def _catalog_service(request: Request, context: CatalogContext) -> AdminCatalogService:
    factory: Callable[[CatalogContext], AdminCatalogService] = getattr(
        request.app.state,
        "admin_catalog_service_factory",
        default_admin_catalog_service_factory,
    )
    try:
        service = factory(context)
    except (FileNotFoundError, OSError, RuntimeError, ValueError, PermissionError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="admin catalog service unavailable",
        ) from exc
    except ValidationKeyCompositionError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="admin catalog validation key unavailable",
        ) from exc
    if not isinstance(service, AdminCatalogService):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="admin catalog service unavailable",
        )
    return service


def _service_and_context(request: Request) -> tuple[AdminCatalogService, CatalogContext]:
    require_admin_request(request)
    context = _catalog_context(request)
    return _catalog_service(request, context), context


def _entry_from_payload(
    payload: CatalogEntryPayload,
    context: CatalogContext,
) -> CatalogEntry:
    return CatalogEntry(
        entry_type=payload.entry_type,
        entry_id=payload.entry_id,
        context=context,
        source_id=payload.source_id,
        provenance=payload.provenance,
        data=payload.data,
    )


def _entry_mapping(entry: CatalogEntry) -> dict[str, Any]:
    return entry.canonical_mapping()


def _draft_state_mapping(value: Any) -> dict[str, Any]:
    return {
        "draft_id": value.draft_id,
        "version": value.version,
        "payload_hash": value.payload_hash,
        "entry_ids": list(value.entry_ids),
    }


def _issue_mapping(issue: ValidationIssue) -> dict[str, Any]:
    return {
        "code": issue.code,
        "entry_id": issue.entry_id,
        "field": issue.field,
        "target_id": issue.target_id,
        "message": issue.message,
    }


def _validation_mapping(result: ValidationResult) -> dict[str, Any]:
    return {
        "is_valid": result.is_valid,
        "errors": [_issue_mapping(issue) for issue in result.errors],
        "warnings": [_issue_mapping(issue) for issue in result.warnings],
    }


def _map_service_error(exc: Exception) -> HTTPException:
    if isinstance(exc, DraftNotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, (DraftConflictError, RevisionConflictError)):
        return HTTPException(status_code=409, detail=str(exc))
    if isinstance(exc, (CatalogServiceError, ContractError, ValueError, TypeError)):
        return HTTPException(status_code=422, detail=str(exc))
    return HTTPException(status_code=500, detail="admin catalog operation failed")


def _runtime_error_detail(exc: CatalogRuntimeError) -> dict[str, Any]:
    return {
        "code": exc.code,
        "message": str(exc),
        "active_revision_id": exc.active_revision_id,
    }


def _runtime_response_is_redacted(payload: dict[str, Any]) -> bool:
    encoded = json.dumps(payload, sort_keys=True).casefold()
    return not any(
        fragment in encoded
        for fragment in _FORBIDDEN_RUNTIME_RESPONSE_FRAGMENTS
    )


def _runtime_mapping(
    selected: ConfiguredRuntime,
    context: CatalogContext,
) -> dict[str, Any]:
    snapshot = selected.catalog_snapshot
    payload: dict[str, Any] = {
        "context": context.canonical_mapping(),
        "mode": selected.mode,
        "selected_source": selected.selected_source,
        "catalog_enabled": selected.catalog_enabled,
        "active_revision_id": selected.active_revision_id,
        "profile_ids": (
            sorted(profile.name for profile in selected.profiles)
            if snapshot is not None
            else []
        ),
        "group_ids": snapshot.list_groups() if snapshot is not None else [],
        "remedy_ids": sorted(snapshot.remedies) if snapshot is not None else [],
        "pathogen_ids": sorted(snapshot.pathogens) if snapshot is not None else [],
        "relation_ids": (
            sorted(relation.entry_id for relation in snapshot.remedy_relations)
            if snapshot is not None
            else []
        ),
        "multiplex_ids": sorted(snapshot.multiplexes) if snapshot is not None else [],
    }
    payload["redacted"] = _runtime_response_is_redacted(payload)
    return payload


def _require_expected_draft_version(
    service: AdminCatalogService,
    context: CatalogContext,
    draft_id: str,
    expected_version: int,
) -> None:
    state = service.get_draft(context, draft_id)
    if state.version != expected_version:
        raise DraftConflictError(
            f"draft version changed: expected v{expected_version}, found v{state.version}"
        )


@router.get("/status")
def admin_catalog_status(request: Request) -> dict[str, Any]:
    service, context = _service_and_context(request)
    revision_id, activation_version = service.store.current_activation(context)
    revision_ids = service.store.list_revision_ids(context)
    return {
        "context": context.canonical_mapping(),
        "current_revision_id": revision_id,
        "activation_version": activation_version,
        "revision_count": len(revision_ids),
        "revision_ids": revision_ids,
    }


@router.get("/entries")
def admin_catalog_entries(request: Request) -> dict[str, Any]:
    service, context = _service_and_context(request)
    try:
        snapshot = service.store.current_revision_snapshot(context)
    except Exception as exc:
        raise _map_service_error(exc) from exc
    if snapshot is None:
        return {"revision_id": None, "count": 0, "entries": []}
    revision_id, entries = snapshot
    return {
        "revision_id": revision_id,
        "count": len(entries),
        "entries": [_entry_mapping(entry) for entry in entries],
    }


@router.get("/runtime")
def admin_catalog_runtime(request: Request) -> dict[str, Any]:
    service, context = _service_and_context(request)
    try:
        selected = load_configured_runtime(service.store, context)
    except CatalogRuntimeConfigError as exc:
        raise HTTPException(
            status_code=422,
            detail=_runtime_error_detail(exc),
        ) from exc
    except CatalogRuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_runtime_error_detail(exc),
        ) from exc
    return _runtime_mapping(selected, context)


@router.post("/drafts")
def create_draft(payload: DraftWriteRequest, request: Request) -> dict[str, Any]:
    service, context = _service_and_context(request)
    if payload.expected_version != 0:
        raise HTTPException(
            status_code=409,
            detail="draft creation requires expected_version 0",
        )
    try:
        state = service.create_draft(
            context,
            payload.draft_id,
            [_entry_from_payload(entry, context) for entry in payload.entries],
        )
    except Exception as exc:
        raise _map_service_error(exc) from exc
    return _draft_state_mapping(state)


@router.patch("/drafts/{draft_id}")
def update_draft(
    draft_id: str,
    payload: DraftUpdateRequest,
    request: Request,
) -> dict[str, Any]:
    service, context = _service_and_context(request)
    try:
        state = service.update_draft(
            context,
            draft_id,
            [_entry_from_payload(entry, context) for entry in payload.entries],
            expected_version=payload.expected_version,
        )
    except Exception as exc:
        raise _map_service_error(exc) from exc
    return _draft_state_mapping(state)


@router.post("/drafts/{draft_id}/validate")
def validate_draft(
    draft_id: str,
    payload: DraftValidateRequest,
    request: Request,
) -> dict[str, Any]:
    service, context = _service_and_context(request)
    try:
        _require_expected_draft_version(
            service,
            context,
            draft_id,
            payload.expected_version,
        )
        return _validation_mapping(service.validate_draft(context, draft_id))
    except Exception as exc:
        raise _map_service_error(exc) from exc


@router.get("/drafts/{draft_id}/diff")
def diff_draft(draft_id: str, request: Request) -> dict[str, Any]:
    service, context = _service_and_context(request)
    try:
        diff = service.diff_draft(context, draft_id)
    except Exception as exc:
        raise _map_service_error(exc) from exc
    return {
        "added": list(diff.added),
        "removed": list(diff.removed),
        "changed": list(diff.changed),
    }


@router.post("/drafts/{draft_id}/publish")
def publish_draft(
    draft_id: str,
    payload: DraftPublishRequest,
    request: Request,
) -> dict[str, Any]:
    service, context = _service_and_context(request)
    try:
        revision = service.publish_draft(
            context,
            draft_id,
            payload.revision_id,
            expected_draft_version=payload.expected_draft_version,
        )
    except Exception as exc:
        raise _map_service_error(exc) from exc
    return {
        "revision_id": revision.revision_id,
        "payload_hash": revision.payload_hash,
        "draft_id": revision.draft_id,
        "draft_version": revision.draft_version,
    }


@router.post("/revisions/{revision_id}/activate")
def activate_revision(
    revision_id: str,
    payload: ActivateRevisionRequest,
    request: Request,
) -> dict[str, Any]:
    service, context = _service_and_context(request)
    try:
        activation_version = service.activate_revision(
            context,
            revision_id,
            expected_previous_revision_id=payload.expected_previous_revision_id,
            expected_activation_version=payload.expected_activation_version,
            actor_id=context.operator_id,
            reason=payload.reason,
        )
    except Exception as exc:
        raise _map_service_error(exc) from exc
    return {
        "current_revision_id": revision_id,
        "activation_version": activation_version,
    }


@router.post("/revisions/{revision_id}/rollback")
def rollback_revision(
    revision_id: str,
    payload: RollbackRevisionRequest,
    request: Request,
) -> dict[str, Any]:
    service, context = _service_and_context(request)
    try:
        activation_version = service.rollback(
            context,
            target_revision_id=revision_id,
            expected_previous_revision_id=payload.expected_previous_revision_id,
            expected_activation_version=payload.expected_activation_version,
            actor_id=context.operator_id,
            reason=payload.reason,
        )
    except Exception as exc:
        raise _map_service_error(exc) from exc
    return {
        "current_revision_id": revision_id,
        "activation_version": activation_version,
    }
