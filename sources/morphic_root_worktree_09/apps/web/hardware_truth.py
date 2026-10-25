from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from apps.web.contracts import _normalize_workbench_mode
from core.realtime.emf_profile import EMFProfileService


def _component(
    component_id: str,
    *,
    label: str,
    status: str,
    note: str,
    evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": component_id,
        "label": label,
        "status": status,
        "note": note,
        "evidence": dict(evidence or {}),
    }


def disabled_realtime_calibration() -> dict[str, Any]:
    return {
        "status": "disabled",
        "sensor_entropy": None,
        "source_health": {
            "rng": "disabled",
            "cpu_timing": "disabled",
            "system_load": "disabled",
            "sensor_entropy": "disabled",
        },
        "replay": {
            "algorithm": "emf-profile-v2",
            "sensor_source": "disabled",
        },
    }


def measure_realtime_calibration() -> dict[str, Any]:
    try:
        return EMFProfileService().measure().to_dict()
    except Exception:  # pragma: no cover - defensive
        return {
            "timestamp": datetime.now().isoformat(),
            "sensor_entropy": 0.5,
            "source_health": {
                "rng": "fallback",
                "cpu_timing": "fallback",
                "system_load": "fallback",
                "sensor_entropy": "fallback",
            },
            "replay": {
                "algorithm": "emf-profile-v2",
                "sensor_source": "fallback",
            },
            "error": "realtime calibration unavailable",
        }


def build_hardware_truth_snapshot(
    hardware_status: Mapping[str, Any],
    *,
    mode: str = "standard",
    calibration: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    normalized_mode = _normalize_workbench_mode(mode)
    gpu = hardware_status.get("gpu", {}) or {}
    sensors = hardware_status.get("sensors", {}) or {}
    driver_layer = hardware_status.get("driver_layer", {}) or {}
    calibration_payload = dict(calibration or disabled_realtime_calibration())
    source_health = calibration_payload.get("source_health", {}) or {}
    sensor_entropy_status = str(source_health.get("sensor_entropy") or "fallback")
    available_providers = [
        provider
        for provider in driver_layer.get("providers", []) or []
        if provider.get("available")
    ]
    external_sensor_count = int(sensors.get("count") or len(sensors.get("devices", []) or []))
    components = {
        "cpu": _component(
            "cpu",
            label="CPU",
            status="real_active",
            note="CPU execution is the active realtime path.",
            evidence=hardware_status.get("cpu", {}) or {},
        ),
        "gpu": _component(
            "gpu",
            label="GPU",
            status=(
                "real_available_not_used"
                if gpu.get("has_gpu")
                else "software_fallback"
            ),
            note=str(gpu.get("note") or "GPU acceleration is not part of this path."),
            evidence=gpu,
        ),
        "sensors": _component(
            "sensors",
            label="Sensors",
            status=(
                "real_available_not_used"
                if external_sensor_count > 0
                else "software_fallback"
            ),
            note=str(sensors.get("note") or "No external sensor signal is in the active path."),
            evidence={
                "count": external_sensor_count,
                "devices": sensors.get("devices", []) or [],
            },
        ),
        "driver_layer": _component(
            "driver_layer",
            label="Driver Layer",
            status=(
                "real_available_not_used"
                if available_providers
                else "software_fallback"
            ),
            note=str(
                driver_layer.get("note")
                or "Driver layer status is visible without opening devices."
            ),
            evidence={
                "provider_count": len(driver_layer.get("providers", []) or []),
                "available_provider_count": len(available_providers),
                "providers": driver_layer.get("providers", []) or [],
            },
        ),
        "quartz": _component(
            "quartz",
            label="Quartz",
            status="not_implemented",
            note="Quartz-backed realtime control is not implemented in the web workbench yet.",
        ),
    }
    gate_warnings: list[str] = []
    if normalized_mode == "expert" and sensor_entropy_status != "ok":
        gate_warnings.append(
            "Expert mode gate warning: sensor entropy is in fallback mode, so the realtime calibration is not backed by a confirmed hardware entropy path."
        )
    return {
        "mode": normalized_mode,
        "profile": hardware_status.get("profile"),
        "components": components,
        "realtime_calibration": calibration_payload,
        "gate_warnings": gate_warnings,
    }
