from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class Phase1ScanRequest(BaseModel):
    last_name: str = Field(min_length=1)
    first_name: str = Field(min_length=1)
    birth_date: str = Field(min_length=1)
    birth_place: str = Field(min_length=1)
    focus: str = Field(min_length=1)
    profile_level: int = 3
    top_n: int = 5
    profile_template: str = Field(default="phase1-default", min_length=1)
    entropy_mode: str = "legacy"
    image_path: str | None = None
    adaptive_limits: bool = False
    consent_local: bool
    consent_safety: bool

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

    @field_validator("image_path")
    @classmethod
    def normalize_image_path(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("consent_local", "consent_safety")
    @classmethod
    def validate_consent(cls, value: bool, info: Any) -> bool:
        if value is not True:
            raise ValueError(f"{info.field_name} must be accepted")
        return value


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


class Phase1LauncherMetadata(BaseModel):
    mode: str
    script_path: str
    ps1_reference_entrypoint: str
    cli_entrypoint: str
    unsupported_request_fields: list[str]
