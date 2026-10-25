"""Dedicated local-only API for DPAPI-protected group drafts.

The router never creates scan, launcher, job, report, trace, or manifest data.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from apps.web.client_context_contracts import GroupContextDraft, LocalVectorDraftEnvelope
from apps.web.security import verify_api_key
from core.compliance.local_vector_draft_store import LocalVectorDraftStore
from core.compliance.operator_context import OperatorContext


router = APIRouter(tags=["group-drafts"], dependencies=[Depends(verify_api_key)])


class GroupDraftSaveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    draft_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
    draft: GroupContextDraft


class GroupDraftDeleteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    confirmation_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")


def build_group_draft_store(
    runtime_dir: str | Path | None,
    context: OperatorContext,
) -> LocalVectorDraftStore:
    runtime_source = str(Path(runtime_dir).resolve()) if runtime_dir is not None else str(Path.cwd().resolve())
    namespace_source = json.dumps(
        (runtime_source, context.operator_id, context.workspace_id, context.tenant_id),
        ensure_ascii=False,
        separators=(",", ":"),
    )
    namespace = hashlib.sha256(namespace_source.encode("utf-8")).hexdigest()[:16]
    root = Path(tempfile.gettempdir()) / "morphic-workbench-local-vector-drafts" / namespace
    return LocalVectorDraftStore(root)


def _store(request: Request) -> LocalVectorDraftStore:
    store = request.app.state.group_draft_store
    if not isinstance(store, LocalVectorDraftStore):
        raise RuntimeError("group draft store is unavailable")
    return store


def _invalidate_activation_context(request: Request) -> None:
    invalidate = getattr(request.app.state, "invalidate_group_analysis_context", None)
    if not callable(invalidate):
        raise RuntimeError("group activation handle store is unavailable")
    invalidate(_context(request))


def _context(request: Request) -> OperatorContext:
    context = request.app.state.operator_context
    if not isinstance(context, OperatorContext):
        raise RuntimeError("operator context is unavailable")
    return context


def _safe_list(store: LocalVectorDraftStore) -> dict[str, object]:
    return {"drafts": store.list_safe()}


@router.get("/api/workbench/group-draft")
def list_group_drafts(request: Request) -> dict[str, object]:
    return _safe_list(_store(request))


@router.put("/api/workbench/group-draft")
def save_group_draft(
    request: Request,
    payload: GroupDraftSaveRequest,
) -> dict[str, object]:
    envelope = LocalVectorDraftEnvelope(group=payload.draft)
    return _store(request).save(payload.draft_id, envelope)


@router.get("/api/workbench/group-draft/erasure-dry-run")
def group_draft_erasure_dry_run(request: Request) -> dict[str, object]:
    return {"drafts": _store(request).erasure_dry_run(now=datetime.now(UTC))}


@router.get("/api/workbench/group-draft/{draft_id}")
def load_group_draft(draft_id: str, request: Request) -> dict[str, object]:
    try:
        envelope = _store(request).load(draft_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="group draft not found") from exc
    if envelope.group is None:
        raise HTTPException(status_code=404, detail="group draft not found")
    return {"draft_id": draft_id, "draft": envelope.group.model_dump(mode="json")}


@router.delete("/api/workbench/group-draft/{draft_id}")
def delete_group_draft(
    draft_id: str,
    request: Request,
    payload: GroupDraftDeleteRequest,
) -> dict[str, object]:
    if payload.confirmation_id != draft_id:
        raise HTTPException(
            status_code=422,
            detail="confirmation_id must exactly match draft_id",
        )
    try:
        _store(request).load(draft_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="group draft not found") from exc
    _invalidate_activation_context(request)
    try:
        deleted = _store(request).erase(draft_id, confirmation_id=payload.confirmation_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="group draft not found")
    return {"deleted": True, "draft_id": draft_id}
