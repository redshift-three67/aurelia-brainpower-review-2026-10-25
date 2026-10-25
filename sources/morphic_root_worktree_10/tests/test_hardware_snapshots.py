from __future__ import annotations

from core.hardware.drivers import (
    CachedHardwareSampler,
    HardwareDriverRegistry,
    HardwareSignalSample,
    MockSignalProvider,
)
from core.hardware.snapshots import (
    HardwareSnapshotService,
    snapshot_sensor_entropy_probe,
)


def test_snapshot_service_summarizes_ok_samples() -> None:
    sampler = CachedHardwareSampler(
        HardwareDriverRegistry(
            [
                MockSignalProvider(value=0.2, provider_id="a"),
                MockSignalProvider(value=0.8, provider_id="b"),
            ]
        )
    )
    service = HardwareSnapshotService(sampler=sampler)

    snapshot = service.capture(provider_ids=["a", "b"])
    data = snapshot.to_dict()

    assert data["summary"]["total_count"] == 2
    assert data["summary"]["ok_count"] == 2
    assert data["summary"]["entropy_mean"] == 0.5
    assert data["summary"]["health"] == "ok"
    assert data["replay"]["algorithm"] == "hardware-snapshot-v2"
    assert [sample["source_id"] for sample in data["samples"]] == ["a", "b"]


def test_snapshot_service_returns_fallback_snapshot_on_sampler_failure() -> None:
    class FailingSampler:
        ttl_seconds = 2.0
        timeout_ms = 75

        def sample(self, provider_ids=None):
            raise RuntimeError("boom")

    service = HardwareSnapshotService(sampler=FailingSampler())

    snapshot = service.capture(provider_ids=["x"])
    data = snapshot.to_dict()

    assert data["summary"]["health"] == "fallback"
    assert data["samples"][0]["source_id"] == "snapshot"
    assert data["samples"][0]["status"] == "fallback"
    assert "boom" in data["samples"][0]["error"]


def test_snapshot_sensor_entropy_probe_reports_partial_status() -> None:
    sampler = CachedHardwareSampler(HardwareDriverRegistry([]))
    service = HardwareSnapshotService(sampler=sampler)

    snapshot = service.capture(provider_ids=["missing"])
    value, status = snapshot_sensor_entropy_probe(snapshot)

    assert value == 0.5
    assert status == "fallback"


def test_snapshot_summary_ignores_non_ok_values_for_entropy_mean() -> None:
    class MixedSampler:
        ttl_seconds = 0.0
        timeout_ms = 10

        def sample(self, provider_ids=None):
            return [
                HardwareSignalSample(
                    source_id="ok",
                    source_type="mock",
                    status="ok",
                    value=0.9,
                    quality=0.8,
                ),
                HardwareSignalSample(
                    source_id="fallback",
                    source_type="mock",
                    status="fallback",
                    value=0.1,
                    quality=0.0,
                ),
            ]

    snapshot = HardwareSnapshotService(sampler=MixedSampler()).capture()

    assert snapshot.summary.entropy_mean == 0.9
    assert snapshot.summary.quality_mean == 0.4
    assert snapshot.summary.health == "partial"
