from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from core.hardware.drivers import (
    CachedHardwareSampler,
    HardwareDriverRegistry,
    HardwareSignalSample,
    clamp,
    json_safe,
)


@dataclass(frozen=True)
class HardwareSnapshotSummary:
    total_count: int
    ok_count: int
    fallback_count: int
    error_count: int
    entropy_mean: float
    quality_mean: float
    health: str

    def to_dict(self) -> dict[str, Any]:
        return json_safe(asdict(self))


@dataclass(frozen=True)
class HardwareSnapshot:
    timestamp: str
    samples: list[dict[str, Any]]
    summary: HardwareSnapshotSummary
    replay: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return json_safe(
            {
                "timestamp": self.timestamp,
                "samples": self.samples,
                "summary": self.summary.to_dict(),
                "replay": self.replay,
            }
        )


def _finite_float(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _summary(samples: list[HardwareSignalSample]) -> HardwareSnapshotSummary:
    total = len(samples)
    ok_values = [
        value
        for sample in samples
        if sample.status == "ok"
        for value in [_finite_float(sample.value)]
        if value is not None
    ]
    quality_values = [
        value
        for sample in samples
        for value in [_finite_float(sample.quality)]
        if value is not None
    ]
    ok_count = sum(1 for sample in samples if sample.status == "ok")
    fallback_count = sum(
        1
        for sample in samples
        if sample.status in {"fallback", "unavailable", "timeout"}
    )
    error_count = sum(1 for sample in samples if sample.status == "error")
    if total == 0:
        health = "fallback"
    elif ok_count == total:
        health = "ok"
    elif ok_count > 0:
        health = "partial"
    else:
        health = "fallback"
    return HardwareSnapshotSummary(
        total_count=total,
        ok_count=ok_count,
        fallback_count=fallback_count,
        error_count=error_count,
        entropy_mean=(
            round(sum(ok_values) / len(ok_values), 4) if ok_values else 0.5
        ),
        quality_mean=(
            round(sum(quality_values) / len(quality_values), 4)
            if quality_values
            else 0.0
        ),
        health=health,
    )


class HardwareSnapshotService:
    def __init__(self, sampler: object) -> None:
        self.sampler = sampler

    def capture(self, provider_ids: list[str] | None = None) -> HardwareSnapshot:
        try:
            samples = list(self.sampler.sample(provider_ids))
        except Exception as exc:
            samples = [
                HardwareSignalSample(
                    source_id="snapshot",
                    source_type="snapshot",
                    status="fallback",
                    value=0.5,
                    quality=0.0,
                    metadata={"provider": "HardwareSnapshotService"},
                    error=str(exc),
                )
            ]
        summary = _summary(samples)
        replay = {
            "algorithm": "hardware-snapshot-v2",
            "provider_ids": list(provider_ids) if provider_ids is not None else None,
            "sampler_ttl_seconds": getattr(self.sampler, "ttl_seconds", None),
            "timeout_ms": getattr(self.sampler, "timeout_ms", None),
        }
        return HardwareSnapshot(
            timestamp=datetime.now().isoformat(),
            samples=[sample.to_dict() for sample in samples],
            summary=summary,
            replay=replay,
        )


def snapshot_sensor_entropy_probe(snapshot: HardwareSnapshot) -> tuple[float, str]:
    return clamp(snapshot.summary.entropy_mean), snapshot.summary.health


def build_hardware_snapshot_service(
    *,
    allow_device_open: bool = False,
    ttl_seconds: float = 2.0,
    timeout_ms: int = 75,
) -> HardwareSnapshotService:
    registry = HardwareDriverRegistry.default(allow_device_open=allow_device_open)
    sampler = CachedHardwareSampler(
        registry,
        ttl_seconds=ttl_seconds,
        timeout_ms=timeout_ms,
    )
    return HardwareSnapshotService(sampler=sampler)
