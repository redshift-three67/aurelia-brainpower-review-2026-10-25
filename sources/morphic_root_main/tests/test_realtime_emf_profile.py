from __future__ import annotations

import math
import numpy as np

from apps.cli.workflow.state import WorkflowState
from core.hardware.drivers import (
    CachedHardwareSampler,
    HardwareDriverRegistry,
    MockSignalProvider,
)
from core.realtime.emf_profile import (
    EMFProfileService,
    default_sensor_entropy_probe,
    hardware_sampler_entropy_probe,
    histogram_entropy_score,
)


def test_histogram_entropy_score_rates_varied_bytes_above_flat_bytes() -> None:
    flat = bytes([7]) * 2048
    varied = bytes(range(256)) * 8

    assert histogram_entropy_score(varied) > 0.95
    assert histogram_entropy_score(flat) < 0.05


def test_profile_service_returns_bounded_json_safe_profile() -> None:
    service = EMFProfileService(
        rng_bytes=lambda size: bytes(range(256)) * (size // 256),
        timing_probe=lambda iterations: [0.01 for _ in range(iterations)],
        system_load_probe=lambda: 0.25,
        sensor_entropy_probe=lambda: (0.75, "ok"),
    )

    profile = service.measure()
    data = profile.to_dict()

    assert 0.0 <= data["emf_index"] <= 1.0
    assert 0.0 <= data["entropy_score"] <= 1.0
    assert data["timing_jitter_ms"] == 0.0
    assert data["system_load"] == 0.25
    assert data["sensor_entropy"] == 0.75
    assert data["source_health"]["sensor_entropy"] == "ok"
    assert data["replay"]["algorithm"] == "emf-profile-v2"
    assert data["counter_frequencies"] == [528.0]


def test_profile_service_records_sensor_source_in_replay() -> None:
    service = EMFProfileService(
        rng_bytes=lambda size: bytes(range(256)) * (size // 256),
        timing_probe=lambda iterations: [0.01 for _ in range(iterations)],
        system_load_probe=lambda: 0.25,
        sensor_entropy_probe=lambda: (0.75, "ok"),
        sensor_source="hardware_snapshot",
    )

    profile = service.measure().to_dict()

    assert profile["replay"]["sensor_source"] == "hardware_snapshot"


def test_default_sensor_entropy_probe_is_lightweight_fallback() -> None:
    assert default_sensor_entropy_probe() == (0.5, "fallback")


def test_hardware_sampler_entropy_probe_averages_ok_samples() -> None:
    sampler = CachedHardwareSampler(
        HardwareDriverRegistry(
            [
                MockSignalProvider(value=0.2, provider_id="a"),
                MockSignalProvider(value=0.8, provider_id="b"),
            ]
        ),
        ttl_seconds=2.0,
    )

    value, status = hardware_sampler_entropy_probe(sampler)

    assert value == 0.5
    assert status == "ok"


def test_hardware_sampler_entropy_probe_falls_back_without_ok_samples() -> None:
    sampler = CachedHardwareSampler(HardwareDriverRegistry([]))

    value, status = hardware_sampler_entropy_probe(sampler, provider_ids=["missing"])

    assert value == 0.5
    assert status == "fallback"


def test_hardware_sampler_entropy_probe_ignores_non_finite_values() -> None:
    class BadSample:
        status = "ok"
        value = math.nan

    class BadSampler:
        def sample(self, provider_ids=None):
            return [BadSample()]

    value, status = hardware_sampler_entropy_probe(BadSampler())

    assert value == 0.5
    assert status == "fallback"


class FakeProfile:
    emf_index = 0.42
    entropy_score = 0.9
    timing_jitter_ms = 0.01
    system_load = 0.2
    sensor_entropy = 0.6
    recommendation = "mittel"
    counter_frequencies = [528.0, 741.0]
    source_health = {"rng": "ok"}
    replay = {"algorithm": "emf-profile-v2"}

    def to_dict(self) -> dict[str, object]:
        return {
            "timestamp": "2026-07-03T12:00:00",
            "emf_index": self.emf_index,
            "entropy_score": self.entropy_score,
            "timing_jitter_ms": self.timing_jitter_ms,
            "system_load": self.system_load,
            "sensor_entropy": self.sensor_entropy,
            "recommendation": self.recommendation,
            "counter_frequencies": self.counter_frequencies,
            "source_health": self.source_health,
            "replay": self.replay,
        }


class FakeProfileService:
    def measure(self) -> FakeProfile:
        return FakeProfile()


def test_web_measure_emf_uses_shared_profile_service(monkeypatch) -> None:
    from apps.web import emf

    monkeypatch.setattr(emf, "EMFProfileService", lambda: FakeProfileService())

    payload = emf.measure_emf()

    assert payload["emf_index"] == 0.42
    assert payload["source_health"] == {"rng": "ok"}
    assert payload["replay"]["algorithm"] == "emf-profile-v2"


def test_workflow_step05_uses_shared_profile_for_state(monkeypatch) -> None:
    from apps.cli.workflow import step05_emf

    monkeypatch.setattr(step05_emf, "EMFProfileService", lambda: FakeProfileService())
    state = WorkflowState(
        client_rates=np.array([1.0, 2.0, 3.0]),
        client_frequency=432.0,
    )

    result = step05_emf.step_05_emf(state, verbose=False)

    assert result.composite_emf_index == 0.42
    assert result.counter_frequencies == [528.0, 741.0]
    assert result.emf_corrected_frequency == 432.0 * (1.0 - 0.42 * 0.05)
    assert result.compensation_vector is not None
    assert 5 in result.step_completed
