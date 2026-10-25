from __future__ import annotations

from types import SimpleNamespace

from core.hardware.drivers import (
    CachedHardwareSampler,
    CpuTimingSignalProvider,
    HardwareDriverRegistry,
    HardwareSignalSample,
    HidSignalProvider,
    MockSignalProvider,
    TrueRngSignalProvider,
)


def test_signal_sample_is_json_safe_and_clamps_value() -> None:
    sample = HardwareSignalSample(
        source_id="x",
        source_type="mock",
        status="ok",
        value=1.5,
        unit="normalized_entropy",
        duration_ms=1.2,
        quality=2.0,
        metadata={"n": 1},
    )

    data = sample.to_dict()

    assert data["value"] == 1.0
    assert data["quality"] == 1.0
    assert data["error"] == ""
    assert isinstance(data["timestamp"], str)


def test_signal_sample_sanitizes_metadata_for_json() -> None:
    sample = HardwareSignalSample(
        source_id="x",
        source_type="mock",
        status="ok",
        value=0.4,
        metadata={
            "nan": float("nan"),
            "nested": {"inf": float("inf")},
            "items": [1, object()],
        },
    )

    data = sample.to_dict()

    assert data["metadata"]["nan"] == 0.0
    assert data["metadata"]["nested"]["inf"] == 0.0
    assert isinstance(data["metadata"]["items"][1], str)


def test_mock_provider_returns_deterministic_sample() -> None:
    provider = MockSignalProvider(value=0.42, provider_id="mock_a")

    sample = provider.sample()

    assert sample.source_id == "mock_a"
    assert sample.status == "ok"
    assert sample.value == 0.42
    assert sample.metadata["provider"] == "MockSignalProvider"


def test_cpu_timing_provider_returns_bounded_sample() -> None:
    provider = CpuTimingSignalProvider(iterations=8)

    sample = provider.sample(timeout_ms=20)
    data = sample.to_dict()

    assert data["source_id"] == "cpu_timing"
    assert data["source_type"] == "system"
    assert data["status"] == "ok"
    assert 0.0 <= data["value"] <= 1.0
    assert 0.0 <= data["quality"] <= 1.0
    assert data["duration_ms"] >= 0.0


def test_hid_provider_unavailable_without_matching_device() -> None:
    provider = HidSignalProvider(hid_module=None)

    assert provider.is_available() is False
    sample = provider.sample(timeout_ms=5)
    assert sample.status == "unavailable"
    assert sample.value == 0.5


def test_hid_provider_does_not_open_device_unless_enabled() -> None:
    opened: list[bool] = []

    class FakeDevice:
        def open(self, vid, pid):
            opened.append(True)

        def set_nonblocking(self, value):
            pass

        def read(self, size):
            return [1, 2, 3]

        def close(self):
            pass

    fake_hid = SimpleNamespace(
        enumerate=lambda vid, pid: [{"vendor_id": vid, "product_id": pid}],
        device=lambda: FakeDevice(),
    )
    provider = HidSignalProvider(hid_module=fake_hid)

    sample = provider.sample(timeout_ms=5)

    assert sample.status == "fallback"
    assert sample.error == "device_open_disabled"
    assert opened == []


def test_truerng_provider_unavailable_without_serial_support() -> None:
    provider = TrueRngSignalProvider(list_ports_module=None, serial_module=None)

    assert provider.is_available() is False
    sample = provider.sample(timeout_ms=5)
    assert sample.status == "unavailable"
    assert sample.value == 0.5


def test_truerng_provider_rejects_generic_ftdi_without_truerng_identity() -> None:
    fake_ports = SimpleNamespace(
        comports=lambda: [
            SimpleNamespace(
                vid=0x0403,
                pid=0x6001,
                product="USB Serial Converter",
                description="FTDI Serial",
                manufacturer="FTDI",
                serial_number="ABC",
                device="COM9",
            )
        ]
    )
    fake_serial = SimpleNamespace(Serial=lambda *args, **kwargs: None)
    provider = TrueRngSignalProvider(
        list_ports_module=fake_ports,
        serial_module=fake_serial,
    )

    assert provider.is_available() is False
    assert provider.sample(timeout_ms=5).status == "unavailable"


def test_registry_lists_provider_status_without_sampling() -> None:
    registry = HardwareDriverRegistry(
        [
            MockSignalProvider(value=0.2, provider_id="mock_a"),
            MockSignalProvider(value=0.8, provider_id="mock_b"),
        ]
    )

    statuses = registry.list_statuses()

    assert [s.provider_id for s in statuses] == ["mock_a", "mock_b"]
    assert [s.available for s in statuses] == [True, True]
    assert registry.get("mock_b").sample().value == 0.8


def test_default_registry_can_explicitly_enable_device_open() -> None:
    registry = HardwareDriverRegistry.default(allow_device_open=True)

    providers = {
        status.provider_id: registry.get(status.provider_id)
        for status in registry.list_statuses()
    }

    assert providers["hid_sensor"].allow_device_open is True
    assert providers["truerng"].allow_device_open is True


class CountingProvider(MockSignalProvider):
    def __init__(self) -> None:
        super().__init__(value=0.25, provider_id="counting")
        self.calls = 0

    def sample(self, timeout_ms: int | None = None):
        self.calls += 1
        return super().sample(timeout_ms=timeout_ms)


def test_cached_sampler_reuses_fresh_sample() -> None:
    provider = CountingProvider()
    registry = HardwareDriverRegistry([provider])
    sampler = CachedHardwareSampler(registry, ttl_seconds=10.0)

    first = sampler.sample(["counting"])[0]
    second = sampler.sample(["counting"])[0]

    assert first.value == second.value
    assert provider.calls == 1


def test_cached_sampler_preserves_empty_provider_selection() -> None:
    provider = CountingProvider()
    registry = HardwareDriverRegistry([provider])
    sampler = CachedHardwareSampler(registry)

    assert sampler.sample([]) == []
    assert provider.calls == 0


def test_cached_sampler_refreshes_expired_sample() -> None:
    provider = CountingProvider()
    registry = HardwareDriverRegistry([provider])
    sampler = CachedHardwareSampler(registry, ttl_seconds=0.0)

    sampler.sample(["counting"])
    sampler.sample(["counting"])

    assert provider.calls == 2


def test_cached_sampler_returns_fallback_for_unknown_provider() -> None:
    registry = HardwareDriverRegistry([])
    sampler = CachedHardwareSampler(registry)

    sample = sampler.sample(["missing"])[0]

    assert sample.source_id == "missing"
    assert sample.status == "fallback"
    assert sample.value == 0.5
