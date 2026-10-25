from __future__ import annotations

import pytest

from apps.web.hardware_truth import build_hardware_truth_snapshot


def hardware_status_payload(*, has_gpu: bool) -> dict[str, object]:
    return {
        "profile": "test",
        "os": {"system": "Windows"},
        "cpu": {"logical_cores": 16},
        "gpu": {
            "has_gpu": has_gpu,
            "backend": "cupy" if has_gpu else "numpy",
            "device_name": "GPU" if has_gpu else "CPU fallback",
            "note": "test-gpu-note",
        },
        "sensors": {
            "count": 0,
            "devices": [],
            "note": "Keine externe Sensor-Hardware erkannt",
        },
        "emf_measurement_source": "software",
        "driver_layer": {
            "providers": [
                {
                    "provider_id": "cpu_timing",
                    "provider_type": "system",
                    "display_name": "CPU Timing",
                    "available": True,
                    "default_timeout_ms": 50,
                },
                {
                    "provider_id": "hid_sensor",
                    "provider_type": "hid",
                    "display_name": "HID Sensor",
                    "available": False,
                    "default_timeout_ms": 75,
                },
            ],
            "note": "status does not open devices",
        },
    }


def realtime_calibration(*, sensor_entropy_status: str) -> dict[str, object]:
    return {
        "timestamp": "2026-07-05T10:00:00",
        "sensor_entropy": 0.5,
        "source_health": {
            "rng": "ok",
            "cpu_timing": "ok",
            "system_load": "ok",
            "sensor_entropy": sensor_entropy_status,
        },
        "replay": {
            "algorithm": "emf-profile-v2",
            "sensor_source": "fallback",
        },
    }


@pytest.mark.parametrize(
    ("has_gpu", "expected_gpu_status"),
    [
        (False, "software_fallback"),
        (True, "real_available_not_used"),
    ],
)
def test_build_hardware_truth_snapshot_classifies_components_without_sampling(
    has_gpu: bool,
    expected_gpu_status: str,
) -> None:
    payload = build_hardware_truth_snapshot(
        hardware_status_payload(has_gpu=has_gpu),
        mode="standard",
        calibration=realtime_calibration(sensor_entropy_status="ok"),
    )

    assert payload["mode"] == "standard"
    assert payload["components"]["cpu"]["status"] == "real_active"
    assert payload["components"]["gpu"]["status"] == expected_gpu_status
    assert payload["components"]["quartz"]["status"] == "not_implemented"
    assert payload["gate_warnings"] == []


def test_build_hardware_truth_snapshot_adds_expert_gate_warning_for_sensor_fallback() -> None:
    payload = build_hardware_truth_snapshot(
        hardware_status_payload(has_gpu=False),
        mode="expert",
        calibration=realtime_calibration(sensor_entropy_status="fallback"),
    )

    assert payload["mode"] == "expert"
    assert payload["realtime_calibration"]["source_health"]["sensor_entropy"] == "fallback"
    assert any("fallback" in warning.lower() for warning in payload["gate_warnings"])


def test_build_hardware_truth_snapshot_never_measures_implicitly(monkeypatch) -> None:
    monkeypatch.setattr(
        "apps.web.hardware_truth.measure_realtime_calibration",
        lambda: (_ for _ in ()).throw(AssertionError("implicit measurement forbidden")),
    )

    payload = build_hardware_truth_snapshot(
        hardware_status_payload(has_gpu=False),
        mode="standard",
    )

    assert payload["realtime_calibration"]["status"] == "disabled"
