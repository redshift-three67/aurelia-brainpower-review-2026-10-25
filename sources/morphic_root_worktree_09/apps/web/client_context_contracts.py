"""Local-only, consent-bound group and geo draft contracts.

These models are intentionally not imported by scan, report, job, trace, or
manifest code. They define the E4.2 design boundary only; they do not persist
or activate an analysis vector.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


_SCHEMA_VERSION = 1


class _LocalDraftModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class GroupMemberReference(_LocalDraftModel):
    client_id: str = Field(pattern=r"^cli-[A-Za-z0-9_-]{1,124}$")
    consent_recorded: bool

    @field_validator("consent_recorded")
    @classmethod
    def require_member_consent(cls, value: bool) -> bool:
        if value is not True:
            raise ValueError("consent_recorded must be accepted for every group member")
        return value


class GroupContextDraft(_LocalDraftModel):
    group_label: str = Field(min_length=1, max_length=120)
    members: list[GroupMemberReference] = Field(min_length=1, max_length=100)
    persistence_consent: bool
    analysis_consent: bool = False
    retention_days: int = Field(ge=1, le=365)

    @field_validator("persistence_consent")
    @classmethod
    def require_persistence_consent(cls, value: bool) -> bool:
        if value is not True:
            raise ValueError("persistence_consent must be accepted")
        return value

    def safe_summary(self) -> dict[str, object]:
        return {
            "schema_version": _SCHEMA_VERSION,
            "vector": "group",
            "persistence": "local_opt_in",
            "retention_days": self.retention_days,
            "member_count": len(self.members),
            "analysis_enabled": False,
        }


class GeoContextDraft(_LocalDraftModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    radius_meters: int = Field(ge=1, le=500_000)
    coordinate_precision: Literal["coarse", "precise"]
    source: Literal["manual"]
    persistence_consent: bool
    retention_days: int = Field(ge=1, le=365)

    @field_validator("persistence_consent")
    @classmethod
    def require_persistence_consent(cls, value: bool) -> bool:
        if value is not True:
            raise ValueError("persistence_consent must be accepted")
        return value

    def safe_summary(self) -> dict[str, object]:
        return {
            "schema_version": _SCHEMA_VERSION,
            "vector": "geo",
            "persistence": "local_opt_in",
            "source": self.source,
            "coordinate_precision": self.coordinate_precision,
            "retention_days": self.retention_days,
            "analysis_enabled": False,
        }


class LocalVectorDraftEnvelope(_LocalDraftModel):
    group: GroupContextDraft | None = None
    geo: GeoContextDraft | None = None

    def safe_summary(self) -> dict[str, object]:
        vectors: list[dict[str, object]] = []
        if self.group is not None:
            vectors.append(self.group.safe_summary())
        if self.geo is not None:
            vectors.append(self.geo.safe_summary())
        return {"schema_version": _SCHEMA_VERSION, "vectors": vectors}
