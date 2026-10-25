from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from apps.web.contracts import (
    WorkbenchDraftEnvelope,
    WorkbenchTemplateRequest,
    _normalize_workbench_mode,
)
from apps.web.authority_ids import AuthorityIdError, validate_authority_id
from apps.web.scan_jobs import ScanJobOwnershipError
from apps.web.workbench_registry import build_workbench_registry
from apps.web.security import (
    capture_authenticated_request_generation,
    register_measurement_publish_permit,
    revalidate_authenticated_request_generation,
    verify_api_key,
)
from apps.web.hardware_truth import disabled_realtime_calibration
from core.compliance.operator_context import operator_owner_scope
from core.profile_sync import (
    ProfileAuthorityError,
    SCAN_PROFILE_POOL_SCHEMA_VERSION,
    build_scan_profile_pool_fingerprint as _build_scan_profile_pool_fingerprint,
    get_top_n_analysis_profiles_by_level,
    validate_scan_profile_pool,
)
from core.source_registry import SourceRegistry, SourceRegistryError

router = APIRouter(tags=["workbench"])
_SCAN_PROFILE_POOL_FINGERPRINT_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_SENSITIVE_DRAFT_KEYS = frozenset({
    "first_name", "last_name", "birth_date", "birth_place", "focus",
    "main_symptom", "birth_time", "email", "notes", "image_path",
})


@dataclass(frozen=True, slots=True)
class ScanProfilePoolAuthority:
    profiles: tuple[tuple[str, str], ...]
    count: int
    fingerprint: str


def _validate_scan_profile_level(profile_level: object) -> None:
    if type(profile_level) is not int or not 1 <= profile_level <= 5:
        raise ValueError("profile_level must be between 1 and 5")


def build_scan_profile_pool_fingerprint(
    profile_level: int,
    internal_profiles: list[tuple[str, str]],
) -> str:
    _validate_scan_profile_level(profile_level)
    return _build_scan_profile_pool_fingerprint(
        profile_level,
        internal_profiles,
    )


def current_scan_profile_pool_authority(
    profile_level: int,
) -> ScanProfilePoolAuthority:
    _validate_scan_profile_level(profile_level)
    profiles = tuple(get_top_n_analysis_profiles_by_level(profile_level))
    fingerprint = build_scan_profile_pool_fingerprint(
        profile_level,
        list(profiles),
    )
    return ScanProfilePoolAuthority(
        profiles=profiles,
        count=len(profiles),
        fingerprint=fingerprint,
    )


def current_scan_profile_pool_fingerprint(profile_level: int) -> str:
    return current_scan_profile_pool_authority(profile_level).fingerprint


def _build_scan_profile_catalog_payload(
    *,
    profile_level: int,
    internal_profiles: tuple[tuple[str, str], ...] | list[tuple[str, str]],
    registry_sources: list[Any],
    fingerprint: str,
) -> dict[str, Any]:
    internal = [
        {"id": profile_id, "label": label}
        for profile_id, label in internal_profiles
    ]
    active_sources = [
        {
            "id": str(source.id),
            "label": str(source.label),
            "scan_effect": False,
            "reason_code": "registry_metadata_only",
        }
        for source in registry_sources
        if bool(source.active)
    ]
    return {
        "schema_version": SCAN_PROFILE_POOL_SCHEMA_VERSION,
        "profile_level": profile_level,
        "pool_authority": {
            "source": "legacy",
            "label": "Legacy",
            "revision": None,
            "revision_short": None,
            "fingerprint": fingerprint,
            "fingerprint_short": fingerprint[:12],
        },
        "internal": {"count": len(internal), "profiles": internal},
        "external": {
            "count": 0,
            "profiles": [],
            "integration_status": "registry_only",
            "scan_effect": False,
            "activation_available": False,
            "activation_gate": "gate_14",
            "active_source_count": len(active_sources),
            "active_sources": active_sources,
        },
        "total_scan_profiles": len(internal),
    }


def build_scan_profile_catalog(
    *,
    profile_level: int,
    internal_profiles: list[tuple[str, str]],
    registry_sources: list[Any],
    _validated_fingerprint: str | None = None,
) -> dict[str, Any]:
    """Describe the actual Top-N screening pool without implying source integration."""
    _validate_scan_profile_level(profile_level)
    validated_profiles = validate_scan_profile_pool(profile_level, internal_profiles)
    if _validated_fingerprint is None:
        fingerprint = build_scan_profile_pool_fingerprint(
            profile_level,
            validated_profiles,
        )
    elif (
        type(_validated_fingerprint) is not str
        or _SCAN_PROFILE_POOL_FINGERPRINT_PATTERN.fullmatch(_validated_fingerprint)
        is None
    ):
        raise ProfileAuthorityError("Profile authority returned an invalid pool.")
    else:
        fingerprint = _validated_fingerprint
    return _build_scan_profile_catalog_payload(
        profile_level=profile_level,
        internal_profiles=validated_profiles,
        registry_sources=registry_sources,
        fingerprint=fingerprint,
    )


def _contains_sensitive_draft_data(value: object) -> bool:
    if isinstance(value, dict):
        return any(
            (key in _SENSITIVE_DRAFT_KEYS and str(nested or "").strip())
            or _contains_sensitive_draft_data(nested)
            for key, nested in value.items()
        )
    if isinstance(value, list):
        return any(_contains_sensitive_draft_data(nested) for nested in value)
    return False


def _require_sensitive_persistence_consent(draft: dict[str, Any], allowed: bool) -> None:
    if _contains_sensitive_draft_data(draft) and not allowed:
        raise HTTPException(
            status_code=422,
            detail="Sensible Klientendaten erfordern eine explizite Persistenzfreigabe.",
        )


@router.get("/api/workbench/registry")
def workbench_registry(
    _api_key: str | None = Depends(verify_api_key),
) -> dict[str, object]:
    return build_workbench_registry()


@router.get("/api/workbench/scan-profile-catalog")
def scan_profile_catalog(
    profile_level: int = 3,
    _api_key: str | None = Depends(verify_api_key),
) -> dict[str, Any]:
    try:
        _validate_scan_profile_level(profile_level)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail="profile_level must be between 1 and 5",
        ) from exc
    try:
        authority = current_scan_profile_pool_authority(profile_level)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Scanprofil-Pool nicht verfügbar.",
        ) from exc
    try:
        sources = SourceRegistry.load_default().list_sources()
    except (SourceRegistryError, OSError, ValueError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Lokaler Quellenkatalog nicht verfügbar.",
        ) from exc
    return _build_scan_profile_catalog_payload(
        profile_level=profile_level,
        internal_profiles=authority.profiles,
        registry_sources=sources,
        fingerprint=authority.fingerprint,
    )


@router.get("/api/workbench/hardware")
async def workbench_hardware(
    request: Request,
    mode: str = "standard",
    _api_key: str | None = Depends(verify_api_key),
) -> dict[str, Any]:
    try:
        normalized_mode = _normalize_workbench_mode(mode)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    authority = request.app.state.emf_telemetry_authority
    authentication_generation = capture_authenticated_request_generation(request)
    measurement_generation = await asyncio.to_thread(authority.begin_measurement)
    hardware_status = request.app.state.build_hardware_status_payload()
    calibration = disabled_realtime_calibration()
    if measurement_generation is not None:
        calibration = request.app.state.measure_realtime_calibration()
    snapshot = request.app.state.build_hardware_truth_snapshot(
        hardware_status,
        mode=normalized_mode,
        calibration=calibration,
    )
    revalidate_authenticated_request_generation(
        request, authentication_generation
    )
    if measurement_generation is not None:
        if not await asyncio.to_thread(
            authority.measurement_is_current,
            measurement_generation,
        ):
            snapshot = request.app.state.build_hardware_truth_snapshot(
                hardware_status,
                mode=normalized_mode,
                calibration=disabled_realtime_calibration(),
            )
        else:
            register_measurement_publish_permit(
                request,
                authority,
                measurement_generation,
            )
    return snapshot


@router.get("/api/workbench/draft", response_model=WorkbenchDraftEnvelope)
def load_workbench_draft(
    request: Request,
    _api_key: str | None = Depends(verify_api_key),
) -> WorkbenchDraftEnvelope:
    return WorkbenchDraftEnvelope.model_validate(
        request.app.state.workbench_store.load_draft()
    )


@router.put("/api/workbench/draft", response_model=WorkbenchDraftEnvelope)
def save_workbench_draft(
    request: Request,
    draft: WorkbenchDraftEnvelope,
    _api_key: str | None = Depends(verify_api_key),
) -> WorkbenchDraftEnvelope:
    _require_sensitive_persistence_consent(draft.draft, draft.persist_sensitive_data)
    return WorkbenchDraftEnvelope.model_validate(
        request.app.state.workbench_store.save_draft(draft.draft)
    )


@router.get("/api/workbench/templates")
def list_workbench_templates(
    request: Request,
    _api_key: str | None = Depends(verify_api_key),
) -> dict[str, object]:
    return {"templates": request.app.state.workbench_store.list_templates()}


@router.post("/api/workbench/templates")
def save_workbench_template(
    request: Request,
    template: WorkbenchTemplateRequest,
    _api_key: str | None = Depends(verify_api_key),
) -> dict[str, Any]:
    _require_sensitive_persistence_consent(
        template.draft, template.persist_sensitive_data
    )
    return request.app.state.workbench_store.save_template(
        name=template.name,
        draft=template.draft,
    )


@router.delete("/api/workbench/templates/{template_id}")
def delete_workbench_template(
    template_id: str,
    request: Request,
    _api_key: str | None = Depends(verify_api_key),
) -> dict[str, Any]:
    deleted = request.app.state.workbench_store.delete_template(template_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="template not found")
    return {"deleted": True, "template_id": template_id}


@router.get("/api/workbench/run-trace/{run_id}")
def get_workbench_run_trace(
    run_id: str,
    request: Request,
    _api_key: str | None = Depends(verify_api_key),
) -> dict[str, Any]:
    try:
        run_id = validate_authority_id(run_id)
    except AuthorityIdError as exc:
        raise HTTPException(status_code=422, detail="invalid authority id") from exc
    try:
        request.app.state.scan_jobs.get_owned(
            run_id,
            expected_owner_id=operator_owner_scope(
                request.app.state.operator_context
            ),
        )
        return request.app.state.workbench_store.get_run_trace(run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="run trace not found") from exc
    except ScanJobOwnershipError as exc:
        raise HTTPException(status_code=403, detail="resource access forbidden") from exc
