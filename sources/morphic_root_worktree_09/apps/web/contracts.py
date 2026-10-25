from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _normalize_workbench_mode(value: str) -> str:
    cleaned = value.strip().lower()
    if cleaned not in {"standard", "expert"}:
        raise ValueError("workbench_mode must be one of standard or expert")
    return cleaned


class Phase1ScanRequest(BaseModel):
    last_name: str = Field(min_length=1)
    first_name: str = Field(min_length=1)
    birth_date: str = Field(min_length=1)
    birth_place: str = Field(min_length=1)
    focus: str = Field(min_length=1)
    profile_level: int = Field(default=3, strict=True)
    top_n: int = Field(default=5, strict=True)
    scan_profile_pool_fingerprint: str = Field(
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
    )
    profile_template: str = Field(default="phase1-default", min_length=1)
    entropy_mode: str = "legacy"
    workbench_mode: str = "standard"
    image_path: str | None = None
    adaptive_limits: bool = Field(default=False, strict=True)
    local_ai_enabled: bool = Field(default=False, strict=True)
    planetary_vector_enabled: bool = Field(default=False, strict=True)
    planet_type: str = ""
    main_symptom: str = ""
    notes: str = ""
    group_draft_id: str = Field(
        default="",
        pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$|^$",
    )
    consent_local: bool = Field(strict=True)
    consent_safety: bool = Field(strict=True)

    @field_validator("planet_type")
    @classmethod
    def validate_planet_type(cls, value: str) -> str:
        cleaned = value.strip().title()
        if cleaned and cleaned not in {"Mars", "Venus", "Sonne", "Saturn", "Neptun"}:
            raise ValueError("planet_type must be one of Mars, Venus, Sonne, Saturn or Neptun")
        return cleaned

    @field_validator("main_symptom", "notes", "group_draft_id")
    @classmethod
    def validate_optional_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("profile_template")
    @classmethod
    def validate_profile_template(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if cleaned not in {
            "phase1-default",
            "personal-balanced",
            "personal-focused",
        }:
            raise ValueError(
                "profile_template must be one of phase1-default, personal-balanced or personal-focused"
            )
        return cleaned

    @field_validator(
        "last_name",
        "first_name",
        "birth_date",
        "birth_place",
        "focus",
        "profile_template",
    )
    @classmethod
    def validate_required_text(cls, value: str, info: Any) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(f"{info.field_name} must not be blank")
        return cleaned

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date_format(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) != 8 or not cleaned.isdigit():
            raise ValueError("birth_date must use DDMMYYYY format")
        try:
            datetime.strptime(cleaned, "%d%m%Y")
        except ValueError as exc:
            raise ValueError("birth_date must be a valid calendar date") from exc
        return cleaned

    @field_validator("top_n")
    @classmethod
    def validate_top_n(cls, value: int) -> int:
        if value not in {3, 5, 7, 9}:
            raise ValueError("top_n must be one of 3, 5, 7 or 9")
        return value

    @field_validator("profile_level")
    @classmethod
    def validate_profile_level(cls, value: int) -> int:
        if value not in {1, 2, 3, 4}:
            raise ValueError("profile_level must be one of 1, 2, 3 or 4")
        return value

    @field_validator("entropy_mode")
    @classmethod
    def validate_entropy_mode(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if cleaned not in {"legacy", "enhanced", "hybrid"}:
            raise ValueError("entropy_mode must be one of legacy, enhanced or hybrid")
        return cleaned

    @field_validator("workbench_mode")
    @classmethod
    def validate_workbench_mode(cls, value: str) -> str:
        return _normalize_workbench_mode(value)

    @field_validator("image_path")
    @classmethod
    def normalize_image_path(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            return None
        if not cleaned.lower().endswith((".jpg", ".jpeg")):
            raise ValueError("image_path must be a .jpg/.jpeg file")
        return cleaned

    @field_validator("consent_local", "consent_safety")
    @classmethod
    def validate_consent(cls, value: bool, info: Any) -> bool:
        if value is not True:
            raise ValueError(f"{info.field_name} must be accepted")
        return value


class HarmonizationRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    intention: str = Field(
        default="harmonization",
        min_length=1,
        alias="harmonization_mode",
        serialization_alias="intention",
    )
    target_frequency: float = Field(default=432.0, gt=0, le=2000.0)
    use_cpu: bool = True
    use_gpu: bool = False
    use_ram: bool = False
    use_websocket: bool = False
    use_driver_layer: bool = False
    report_id: str = Field(min_length=1)
    workbench_mode: str = "standard"
    pulse_seconds: float = Field(default=3.0, gt=0, le=5.0)
    pause_seconds: float = Field(default=2.0, gt=0, le=5.0)
    duration_factor: int = Field(default=1, ge=1, le=21)

    @field_validator("workbench_mode")
    @classmethod
    def validate_workbench_mode(cls, value: str) -> str:
        return _normalize_workbench_mode(value)


class WorkbenchDraftEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    draft: dict[str, Any] = Field(default_factory=dict)
    updated_at: str | None = None
    persist_sensitive_data: bool = Field(default=False, exclude=True)


class WorkbenchTemplateRequest(BaseModel):
    name: str = Field(min_length=1)
    draft: dict[str, Any] = Field(default_factory=dict)
    persist_sensitive_data: bool = Field(default=False, exclude=True)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("name must not be blank")
        return cleaned


class Phase1ScanPreviewResponse(BaseModel):
    launcher: "Phase1LauncherMetadata"
    executes: bool
    command: list[str]
    profile_level: int
    top_n: int
    focus: str
    profile_template: str
    entropy_mode: str
    image_path: str | None = None
    image_enabled: bool = False
    adaptive_limits_requested: bool = False
    effective_result_limit: int
    notes: list[str] = Field(default_factory=list)


class Phase1ScanJobResponse(Phase1ScanPreviewResponse):
    job_id: str
    status: str
    progress_percent: float | None = None
    current_phase: str | None = None
    current_substep: str | None = None
    completed_substeps: list[str] = Field(default_factory=list)
    parallel_export_plan: str | None = None
    parallel_export_client_id: str | None = None


class Phase1ScanStartResponse(BaseModel):
    executes: bool
    job_id: str
    status: str
    progress_percent: float | None = None
    current_phase: str | None = None
    current_substep: str | None = None
    completed_substeps: list[str] = Field(default_factory=list)


class ScanStartOperationReconcileResponse(BaseModel):
    disposition: Literal["retry-same-key", "safe-to-replace", "job"]
    job_id: str | None = None
    status: str | None = None
    returncode: int | None = None
    progress_percent: float | None = None
    current_phase: str | None = None
    current_substep: str | None = None
    completed_substeps: list[str] = Field(default_factory=list)
    completed_stage_ids: list[str] = Field(default_factory=list)
    current_stage_id: str | None = None
    diagnostics: list[str] = Field(default_factory=list)


class Phase1LauncherMetadata(BaseModel):
    mode: str
    script_path: str
    ps1_reference_entrypoint: str
    cli_entrypoint: str
    unsupported_request_fields: list[str]
