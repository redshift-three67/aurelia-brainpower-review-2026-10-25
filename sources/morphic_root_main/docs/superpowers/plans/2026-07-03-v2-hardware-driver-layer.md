# V2 Hardware Driver Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a safe hardware driver layer that detects, samples, caches, and reports real/virtual local hardware sources without blocking realtime web or worker hotpaths.

**Architecture:** Add `core/hardware/drivers.py` as the canonical driver contract with JSON-safe samples, provider statuses, CPU/HID/TrueRNG/mock providers, a registry, and a TTL cached sampler. Integrate the driver layer as opt-in entropy input for `EMFProfileService` and expose provider availability on `/api/hardware/status` without opening or sampling external devices.

**Tech Stack:** Python dataclasses, defensive optional imports, existing FastAPI status endpoint, pytest focused tests, no network dependency, no Full Pytest Suite.

---

## File Structure

- Create `core/hardware/drivers.py`: provider contract, sample/status dataclasses, CPU/HID/TrueRNG/mock providers, registry, cached sampler.
- Modify `core/realtime/emf_profile.py`: add `hardware_sampler_entropy_probe()` opt-in helper.
- Modify `apps/web/main.py`: add `driver_layer` section to `/api/hardware/status`.
- Test `tests/test_hardware_driver_layer.py`: provider, registry, cache, probe behavior.
- Modify `tests/test_realtime_emf_profile.py`: opt-in hardware sampler entropy tests if needed.
- Modify `tests/test_web_contracts.py` or add `tests/test_web_hardware_status.py`: hardware status includes driver layer without sampling.

---

### Task 1: Driver Dataclasses, CPU Provider, Mock Provider

**Files:**
- Create: `core/hardware/drivers.py`
- Test: `tests/test_hardware_driver_layer.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_hardware_driver_layer.py`:

```python
from __future__ import annotations

from core.hardware.drivers import (
    CpuTimingSignalProvider,
    HardwareSignalSample,
    MockSignalProvider,
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
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_hardware_driver_layer.py -q
```

Expected: import failure for `core.hardware.drivers`.

- [ ] **Step 3: Implement minimal driver layer**

Create `core/hardware/drivers.py` with:

```python
from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Protocol


VALID_STATUSES = {"ok", "unavailable", "timeout", "error", "fallback"}


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0
    if not math.isfinite(number):
        number = 0.0
    return max(minimum, min(maximum, number))


@dataclass
class HardwareSignalSample:
    source_id: str
    source_type: str
    status: str
    value: float
    unit: str = "normalized_entropy"
    duration_ms: float = 0.0
    quality: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self) -> None:
        if self.status not in VALID_STATUSES:
            self.status = "error"
        self.value = clamp(self.value)
        self.quality = clamp(self.quality)
        self.duration_ms = max(0.0, float(self.duration_ms))
        self.error = str(self.error or "")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HardwareProviderStatus:
    provider_id: str
    provider_type: str
    display_name: str
    available: bool
    default_timeout_ms: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class HardwareSignalProvider(Protocol):
    provider_id: str
    provider_type: str
    display_name: str
    default_timeout_ms: int

    def is_available(self) -> bool: ...

    def sample(self, timeout_ms: int | None = None) -> HardwareSignalSample: ...


class MockSignalProvider:
    provider_type = "mock"
    display_name = "Mock Signal"
    default_timeout_ms = 1

    def __init__(self, value: float = 0.5, provider_id: str = "mock") -> None:
        self.provider_id = provider_id
        self._value = clamp(value)

    def is_available(self) -> bool:
        return True

    def sample(self, timeout_ms: int | None = None) -> HardwareSignalSample:
        return HardwareSignalSample(
            source_id=self.provider_id,
            source_type=self.provider_type,
            status="ok",
            value=self._value,
            quality=1.0,
            metadata={"provider": self.__class__.__name__},
        )


class CpuTimingSignalProvider:
    provider_id = "cpu_timing"
    provider_type = "system"
    display_name = "CPU Timing"
    default_timeout_ms = 50

    def __init__(self, iterations: int = 32) -> None:
        self.iterations = max(3, int(iterations))

    def is_available(self) -> bool:
        return True

    def sample(self, timeout_ms: int | None = None) -> HardwareSignalSample:
        started = time.perf_counter()
        timeout = max(1, int(timeout_ms or self.default_timeout_ms)) / 1000.0
        stamps: list[int] = []
        try:
            while len(stamps) < self.iterations:
                stamps.append(time.perf_counter_ns())
                if time.perf_counter() - started >= timeout:
                    break
            if len(stamps) < 3:
                return HardwareSignalSample(
                    source_id=self.provider_id,
                    source_type=self.provider_type,
                    status="timeout",
                    value=0.5,
                    quality=0.0,
                    duration_ms=(time.perf_counter() - started) * 1000.0,
                    metadata={"provider": self.__class__.__name__, "sample_count": len(stamps)},
                )
            diffs = [float(stamps[i + 1] - stamps[i]) for i in range(len(stamps) - 1)]
            mean = sum(diffs) / len(diffs)
            variance = sum((x - mean) ** 2 for x in diffs) / len(diffs)
            rel = math.sqrt(max(variance, 0.0)) / abs(mean or 1.0)
            value = clamp(rel / (rel + 1.0))
            return HardwareSignalSample(
                source_id=self.provider_id,
                source_type=self.provider_type,
                status="ok",
                value=value,
                quality=clamp(len(stamps) / float(self.iterations)),
                duration_ms=(time.perf_counter() - started) * 1000.0,
                metadata={"provider": self.__class__.__name__, "sample_count": len(stamps)},
            )
        except Exception as exc:
            return HardwareSignalSample(
                source_id=self.provider_id,
                source_type=self.provider_type,
                status="error",
                value=0.5,
                quality=0.0,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                metadata={"provider": self.__class__.__name__},
                error=str(exc),
            )
```

- [ ] **Step 4: Run tests to verify GREEN**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_hardware_driver_layer.py -q
```

Expected: Task 1 tests pass.

---

### Task 2: HID/TrueRNG Providers And Registry

**Files:**
- Modify: `core/hardware/drivers.py`
- Test: `tests/test_hardware_driver_layer.py`

- [ ] **Step 1: Add failing tests**

Append:

```python
from core.hardware.drivers import (
    HardwareDriverRegistry,
    HidSignalProvider,
    TrueRngSignalProvider,
)


def test_hid_provider_unavailable_without_matching_device(monkeypatch) -> None:
    provider = HidSignalProvider(hid_module=None)

    assert provider.is_available() is False
    sample = provider.sample(timeout_ms=5)
    assert sample.status == "unavailable"
    assert sample.value == 0.5


def test_truerng_provider_unavailable_without_serial_support() -> None:
    provider = TrueRngSignalProvider(list_ports_module=None, serial_module=None)

    assert provider.is_available() is False
    sample = provider.sample(timeout_ms=5)
    assert sample.status == "unavailable"
    assert sample.value == 0.5


def test_registry_lists_provider_status_without_sampling() -> None:
    registry = HardwareDriverRegistry([
        MockSignalProvider(value=0.2, provider_id="mock_a"),
        MockSignalProvider(value=0.8, provider_id="mock_b"),
    ])

    statuses = registry.list_statuses()

    assert [s.provider_id for s in statuses] == ["mock_a", "mock_b"]
    assert [s.available for s in statuses] == [True, True]
    assert registry.get("mock_b").sample().value == 0.8
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_hardware_driver_layer.py -q
```

Expected: import failures for HID/TrueRNG/registry.

- [ ] **Step 3: Implement providers and registry**

Add `HidSignalProvider`, `TrueRngSignalProvider`, and `HardwareDriverRegistry` to `core/hardware/drivers.py`.

Key behaviors:

- `HidSignalProvider(hid_module=None)` is unavailable and never imports real HID during tests.
- `TrueRngSignalProvider(list_ports_module=None, serial_module=None)` is unavailable.
- `HardwareDriverRegistry.list_statuses()` calls only `is_available()`, not `sample()`.
- `HardwareDriverRegistry.default()` constructs CPU/HID/TrueRNG providers.

- [ ] **Step 4: Run tests to verify GREEN**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_hardware_driver_layer.py -q
```

Expected: Task 1 and 2 tests pass.

---

### Task 3: Cached Hardware Sampler

**Files:**
- Modify: `core/hardware/drivers.py`
- Test: `tests/test_hardware_driver_layer.py`

- [ ] **Step 1: Add failing tests**

Append:

```python
from core.hardware.drivers import CachedHardwareSampler


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
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_hardware_driver_layer.py -q
```

Expected: missing `CachedHardwareSampler`.

- [ ] **Step 3: Implement cached sampler**

Add `CachedHardwareSampler` to `core/hardware/drivers.py`.

Required behavior:

- cache by `source_id`
- TTL default `2.0`
- default timeout `75`
- `sample(provider_ids=None)` defaults to all registry providers
- unknown provider returns `HardwareSignalSample(status="fallback", value=0.5)`
- provider exceptions return fallback samples

- [ ] **Step 4: Run tests to verify GREEN**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_hardware_driver_layer.py -q
```

Expected: all driver layer tests pass.

---

### Task 4: EMFProfile Hardware Sampler Probe

**Files:**
- Modify: `core/realtime/emf_profile.py`
- Test: `tests/test_realtime_emf_profile.py`

- [ ] **Step 1: Add failing tests**

Append to `tests/test_realtime_emf_profile.py`:

```python
from core.hardware.drivers import HardwareDriverRegistry, CachedHardwareSampler, MockSignalProvider
from core.realtime.emf_profile import hardware_sampler_entropy_probe


def test_hardware_sampler_entropy_probe_averages_ok_samples() -> None:
    sampler = CachedHardwareSampler(
        HardwareDriverRegistry([
            MockSignalProvider(value=0.2, provider_id="a"),
            MockSignalProvider(value=0.8, provider_id="b"),
        ]),
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
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_realtime_emf_profile.py tests\test_hardware_driver_layer.py -q
```

Expected: missing `hardware_sampler_entropy_probe`.

- [ ] **Step 3: Implement opt-in probe**

In `core/realtime/emf_profile.py`, add:

```python
def hardware_sampler_entropy_probe(
    sampler: object,
    provider_ids: list[str] | None = None,
) -> tuple[float, str]:
    try:
        samples = sampler.sample(provider_ids)
    except Exception:
        return 0.5, "fallback"
    ok_values = [float(s.value) for s in samples if getattr(s, "status", "") == "ok"]
    if not ok_values:
        return 0.5, "fallback"
    value = round(sum(ok_values) / len(ok_values), 4)
    status = "ok" if len(ok_values) == len(samples) else "partial"
    return clamp(value), status
```

- [ ] **Step 4: Run tests to verify GREEN**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_realtime_emf_profile.py tests\test_hardware_driver_layer.py -q
```

Expected: EMF and driver layer tests pass.

---

### Task 5: Web Hardware Status Integration

**Files:**
- Modify: `apps/web/main.py`
- Test: `tests/test_web_hardware_status.py`

- [ ] **Step 1: Write failing web status test**

Create `tests/test_web_hardware_status.py`:

```python
from __future__ import annotations

import apps.web.main as web_main
import core.hardware.system_info as system_info


def test_hardware_status_includes_driver_layer_without_sampling(monkeypatch) -> None:
    sampled: list[str] = []
    registry_calls: list[str] = []

    class FakeRegistry:
        @classmethod
        def default(cls):
            registry_calls.append("default")
            return cls()

        def list_statuses(self):
            from core.hardware.drivers import HardwareProviderStatus

            return [
                HardwareProviderStatus(
                    provider_id="fake",
                    provider_type="mock",
                    display_name="Fake Provider",
                    available=True,
                    default_timeout_ms=7,
                )
            ]

        def sample(self, *args, **kwargs):
            sampled.append("sampled")
            raise AssertionError("status endpoint must not sample providers")

    monkeypatch.setattr(web_main, "HardwareDriverRegistry", FakeRegistry, raising=False)
    monkeypatch.setattr(
        system_info,
        "get_full_system_report",
        lambda: {
            "profile": "test",
            "os": {},
            "cpu": {},
            "gpu": {},
            "sensors": {"devices": []},
        },
    )
    web_main.driver_layer_status.cache_clear()
    app = web_main.create_app(runtime_dir=None)
    endpoint = next(
        route.endpoint
        for route in app.routes
        if getattr(route, "path", None) == "/api/hardware/status"
    )

    payload = endpoint()
    second_payload = endpoint()

    assert payload["driver_layer"]["providers"][0]["provider_id"] == "fake"
    assert payload["driver_layer"]["providers"][0]["available"] is True
    assert "status does not open devices" in payload["driver_layer"]["note"]
    assert "timeout-protected" not in payload["driver_layer"]["note"]
    assert second_payload["driver_layer"]["providers"][0]["provider_id"] == "fake"
    assert sampled == []
    assert registry_calls == ["default"]
```

- [ ] **Step 2: Run test to verify RED**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_web_hardware_status.py -q
```

Expected: monkeypatch/import failure because `apps.web.main.HardwareDriverRegistry` is not imported or response lacks `driver_layer`.

- [ ] **Step 3: Implement web status integration**

In `apps/web/main.py`:

- import `HardwareDriverRegistry`
- in `hardware_status()`, create `driver_registry = HardwareDriverRegistry.default()`
- add `driver_layer` with `[status.to_dict() for status in driver_registry.list_statuses()]`
- do not call `sample()` or open external devices in this endpoint
- catch registry errors and return `driver_layer.error`

- [ ] **Step 4: Run test to verify GREEN**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_web_hardware_status.py -q
```

Expected: web hardware status test passes.

---

### Task 6: Focused Verification, Review, Commit

**Files:**
- All files changed in Tasks 1-5.

- [ ] **Step 1: Run driver-focused tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_hardware_driver_layer.py tests\test_realtime_emf_profile.py tests\test_web_hardware_status.py -q
```

Expected: all focused hardware-driver tests pass.

- [ ] **Step 2: Run small web regression**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_web_contracts.py tests\test_web_shell.py -q
```

Expected: web contract/shell tests pass.

- [ ] **Step 3: Run small entropy/provider regression**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_entropy_providers_smoke.py -q
```

Expected: existing entropy provider smoke tests pass.

- [ ] **Step 4: Review diff**

Run:

```powershell
git status --short
git diff --stat
```

Expected: only intended driver-layer files and tests are changed.

- [ ] **Step 5: Commit implementation**

Run:

```powershell
git add .
git commit -m "feat: add v2 hardware driver layer"
```

Expected: one implementation commit after the design and plan commits.

## Deferred

- Full pytest suite remains deferred per `docs/superpowers/plans/2026-07-03-deferred-full-pytest.md`.
- Adapting `SensorManager` and `select_entropy_source()` internally to the driver layer is a later compatibility migration.
- Analysis/harmonization weighting of hardware snapshots comes after this layer is stable.
