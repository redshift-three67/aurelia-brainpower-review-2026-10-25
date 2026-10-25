# V2 Hardware Snapshot Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add opt-in driver-layer hardware snapshots to EMF profiling and harmonization traces without changing the lightweight default path.

**Architecture:** Introduce `core/hardware/snapshots.py` as the replayable snapshot adapter above `CachedHardwareSampler`. The harmonization worker captures snapshots only when `hardware_config["use_driver_layer"]` is true, feeds the captured summary into `EMFProfileService`, and records both EMF profile and snapshot in cycle trace events.

**Tech Stack:** Python dataclasses, existing FastAPI/Pydantic web shell, Typer CLI, pytest, existing JSONL event tracing.

---

## File Structure

- Create `core/hardware/snapshots.py`: snapshot dataclasses, summary calculation, safe service wrapper, EMF sensor probe adapter.
- Modify `core/hardware/drivers.py`: allow explicit `HardwareDriverRegistry.default(allow_device_open=False)`.
- Modify `core/realtime/emf_profile.py`: add `sensor_source` replay metadata while preserving defaults.
- Modify `services/harmonization_worker.py`: add `capture_realtime_context()` and opt-in worker event payload.
- Modify `apps/cli/commands/harmonize.py`: add `--driver-layer/--no-driver-layer`.
- Modify `apps/web/main.py`: add `use_driver_layer` request field and pass it to `hardware_config`.
- Check `apps/web/harmonization.py`: keep the adapter contract generic through `hardware_config` so old callers stay compatible.
- Add `tests/test_hardware_snapshots.py`.
- Modify `tests/test_realtime_emf_profile.py`.
- Modify `tests/test_harmonization_worker_stop.py`.
- Modify `tests/test_web_shell.py`.

## Task 1: Hardware Snapshot Service

**Files:**
- Create: `core/hardware/snapshots.py`
- Test: `tests/test_hardware_snapshots.py`

- [ ] **Step 1: Write failing snapshot service tests**

Append/create `tests/test_hardware_snapshots.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_hardware_snapshots.py -q
```

Expected: FAIL because `core.hardware.snapshots` does not exist.

- [ ] **Step 3: Implement snapshot service**

Create `core/hardware/snapshots.py`:

```python
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


def _summary(samples: list[HardwareSignalSample]) -> HardwareSnapshotSummary:
    total = len(samples)
    ok_values = [
        float(sample.value)
        for sample in samples
        if sample.status == "ok" and math.isfinite(float(sample.value))
    ]
    quality_values = [
        float(sample.quality)
        for sample in samples
        if math.isfinite(float(sample.quality))
    ]
    ok_count = sum(1 for sample in samples if sample.status == "ok")
    fallback_count = sum(1 for sample in samples if sample.status in {"fallback", "unavailable", "timeout"})
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
        entropy_mean=round(sum(ok_values) / len(ok_values), 4) if ok_values else 0.5,
        quality_mean=round(sum(quality_values) / len(quality_values), 4) if quality_values else 0.0,
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
```

- [ ] **Step 4: Run snapshot service tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_hardware_snapshots.py -q
```

Expected: PASS.

## Task 2: Registry Factory And EMF Replay Metadata

**Files:**
- Modify: `core/hardware/drivers.py`
- Modify: `core/realtime/emf_profile.py`
- Modify: `tests/test_hardware_driver_layer.py`
- Modify: `tests/test_realtime_emf_profile.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_hardware_driver_layer.py`:

```python
def test_default_registry_can_explicitly_enable_device_open() -> None:
    registry = HardwareDriverRegistry.default(allow_device_open=True)

    providers = {status.provider_id: registry.get(status.provider_id) for status in registry.list_statuses()}

    assert providers["hid_sensor"].allow_device_open is True
    assert providers["truerng"].allow_device_open is True
```

Add to `tests/test_realtime_emf_profile.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_hardware_driver_layer.py::test_default_registry_can_explicitly_enable_device_open tests\test_realtime_emf_profile.py::test_profile_service_records_sensor_source_in_replay -q
```

Expected: FAIL because the registry factory and `sensor_source` argument do not exist yet.

- [ ] **Step 3: Implement minimal changes**

In `core/hardware/drivers.py`, change:

```python
@classmethod
def default(cls) -> "HardwareDriverRegistry":
    return cls(
        [
            CpuTimingSignalProvider(),
            HidSignalProvider(),
            TrueRngSignalProvider(),
        ]
    )
```

to:

```python
@classmethod
def default(cls, *, allow_device_open: bool = False) -> "HardwareDriverRegistry":
    return cls(
        [
            CpuTimingSignalProvider(),
            HidSignalProvider(allow_device_open=allow_device_open),
            TrueRngSignalProvider(allow_device_open=allow_device_open),
        ]
    )
```

In `core/realtime/emf_profile.py`, add `sensor_source: str = "fallback"` to `EMFProfileService.__init__`, store it on `self._sensor_source`, and replace the replay sensor marker with:

```python
"sensor_source": self._sensor_source,
```

- [ ] **Step 4: Run focused tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_hardware_driver_layer.py tests\test_realtime_emf_profile.py tests\test_hardware_snapshots.py -q
```

Expected: PASS.

## Task 3: Worker Realtime Context Integration

**Files:**
- Modify: `services/harmonization_worker.py`
- Modify: `tests/test_harmonization_worker_stop.py`

- [ ] **Step 1: Write failing worker tests**

Add to `tests/test_harmonization_worker_stop.py`:

```python
def test_realtime_context_default_does_not_build_snapshot_service(monkeypatch) -> None:
    built: list[bool] = []

    def fake_build_snapshot_service(*args, **kwargs):
        built.append(True)
        raise AssertionError("snapshot service should not be built")

    monkeypatch.setattr(worker, "build_hardware_snapshot_service", fake_build_snapshot_service, raising=False)
    monkeypatch.setattr(
        worker,
        "measure_realtime_emf_profile",
        lambda hardware_config=None: {"emf_index": 0.2, "replay": {"sensor_source": "fallback"}},
    )

    context = worker.capture_realtime_context({"use_cpu": False})

    assert context == {"emf_profile": {"emf_index": 0.2, "replay": {"sensor_source": "fallback"}}}
    assert built == []


def test_realtime_context_opt_in_adds_hardware_snapshot(monkeypatch) -> None:
    class FakeSummary:
        entropy_mean = 0.8
        health = "ok"

    class FakeSnapshot:
        summary = FakeSummary()

        def to_dict(self):
            return {
                "summary": {"entropy_mean": 0.8, "health": "ok"},
                "samples": [{"source_id": "mock", "status": "ok", "value": 0.8}],
                "replay": {"algorithm": "hardware-snapshot-v2"},
            }

    class FakeSnapshotService:
        def capture(self, provider_ids=None):
            assert provider_ids == ["cpu_timing"]
            return FakeSnapshot()

    captured_sources: list[str] = []

    class FakeProfile:
        def to_dict(self):
            return {
                "emf_index": 0.31,
                "sensor_entropy": 0.8,
                "source_health": {"sensor_entropy": "ok"},
                "replay": {"sensor_source": captured_sources[-1]},
            }

    class FakeProfileService:
        def __init__(self, **kwargs):
            captured_sources.append(kwargs["sensor_source"])
            value, status = kwargs["sensor_entropy_probe"]()
            assert value == 0.8
            assert status == "ok"

        def measure(self):
            return FakeProfile()

    monkeypatch.setattr(worker, "build_hardware_snapshot_service", lambda **kwargs: FakeSnapshotService(), raising=False)
    monkeypatch.setattr(worker, "EMFProfileService", FakeProfileService, raising=False)

    context = worker.capture_realtime_context({"use_driver_layer": True})

    assert context["emf_profile"]["sensor_entropy"] == 0.8
    assert context["emf_profile"]["replay"]["sensor_source"] == "hardware_snapshot"
    assert context["hardware_snapshot"]["summary"]["health"] == "ok"
```

Update `test_worker_appends_realtime_trace_events()` so the monkeypatch targets `capture_realtime_context` and returns both fields:

```python
monkeypatch.setattr(
    worker,
    "capture_realtime_context",
    lambda hardware_config=None: {
        "emf_profile": {"emf_index": 0.2, "replay": {"algorithm": "emf-profile-v2"}},
        "hardware_snapshot": {"summary": {"health": "ok"}},
    },
)
```

Assert:

```python
assert '"hardware_snapshot": {"summary": {"health": "ok"}}' in events
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_harmonization_worker_stop.py::test_realtime_context_default_does_not_build_snapshot_service tests\test_harmonization_worker_stop.py::test_realtime_context_opt_in_adds_hardware_snapshot -q
```

Expected: FAIL because `capture_realtime_context` does not exist.

- [ ] **Step 3: Implement worker context**

In `services/harmonization_worker.py`, import lazily at module level for monkeypatchability:

```python
try:
    from core.hardware.snapshots import (
        build_hardware_snapshot_service,
        snapshot_sensor_entropy_probe,
    )
    from core.realtime.emf_profile import EMFProfileService
except Exception:
    build_hardware_snapshot_service = None
    snapshot_sensor_entropy_probe = None
    EMFProfileService = None
```

Replace `measure_realtime_emf_profile()` with a hardware-config-aware implementation and add `capture_realtime_context()`:

```python
def measure_realtime_emf_profile(hardware_config: Optional[Dict[str, object]] = None) -> dict[str, object]:
    service_cls = EMFProfileService
    if service_cls is None:
        from core.realtime.emf_profile import EMFProfileService as service_cls
    return service_cls().measure().to_dict()


def capture_realtime_context(hardware_config: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    config = hardware_config or {}
    if not bool(config.get("use_driver_layer", False)):
        return {"emf_profile": measure_realtime_emf_profile(config)}

    try:
        builder = build_hardware_snapshot_service
        probe_adapter = snapshot_sensor_entropy_probe
        service_cls = EMFProfileService
        if builder is None or probe_adapter is None or service_cls is None:
            from core.hardware.snapshots import (
                build_hardware_snapshot_service as builder,
                snapshot_sensor_entropy_probe as probe_adapter,
            )
            from core.realtime.emf_profile import EMFProfileService as service_cls

        service = builder(allow_device_open=False)
        provider_ids = config.get("driver_provider_ids") or ["cpu_timing"]
        snapshot = service.capture(provider_ids=list(provider_ids))
        emf_profile = service_cls(
            sensor_entropy_probe=lambda: probe_adapter(snapshot),
            sensor_source="hardware_snapshot",
        ).measure().to_dict()
        return {
            "emf_profile": emf_profile,
            "hardware_snapshot": snapshot.to_dict(),
        }
    except Exception as exc:
        profile = measure_realtime_emf_profile(config)
        return {
            "emf_profile": profile,
            "hardware_snapshot": {
                "summary": {"health": "fallback"},
                "samples": [],
                "replay": {"algorithm": "hardware-snapshot-v2", "error": str(exc)},
            },
        }
```

In `run_harmonization_worker()`, replace:

```python
cycle_payload["emf_profile"] = measure_realtime_emf_profile()
```

with:

```python
cycle_payload.update(capture_realtime_context(job.hardware_config))
```

- [ ] **Step 4: Run worker tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_harmonization_worker_stop.py -q
```

Expected: PASS.

## Task 4: CLI And Web Opt-In Controls

**Files:**
- Modify: `apps/cli/commands/harmonize.py`
- Modify: `apps/web/main.py`
- Inspect: `apps/web/harmonization.py`
- Modify: `tests/test_harmonization_worker_stop.py`
- Modify: `tests/test_web_shell.py`

- [ ] **Step 1: Write failing CLI and web tests**

In `tests/test_harmonization_worker_stop.py`, extend `test_harmonize_cli_delegates_start_status_and_stop()` start invocation with:

```python
"--driver-layer",
```

and expected `hardware_config` with:

```python
"use_driver_layer": True,
```

In `tests/test_web_shell.py`, update `test_web_shell_can_start_poll_and_stop_harmonization_job()` POST JSON to include:

```python
"use_driver_layer": True,
```

and expected started config with:

```python
"use_driver_layer": True,
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_harmonization_worker_stop.py::test_harmonize_cli_delegates_start_status_and_stop tests\test_web_shell.py::test_web_shell_can_start_poll_and_stop_harmonization_job -q
```

Expected: FAIL because CLI/web do not pass the new field.

- [ ] **Step 3: Implement CLI and web fields**

In `apps/cli/commands/harmonize.py`, add parameter:

```python
use_driver_layer: bool = typer.Option(False, "--driver-layer/--no-driver-layer", help="V2 Hardware Driver Layer fuer EMF-Snapshots verwenden"),
```

and add to `hardware_config`:

```python
"use_driver_layer": use_driver_layer,
```

In `apps/web/main.py`, add to `HarmonizationRequest`:

```python
use_driver_layer: bool = False
```

and add to `hardware_config`:

```python
"use_driver_layer": request.use_driver_layer,
```

Inspect `apps/web/harmonization.py` and keep `WorkerHarmonizationService.start()` passing `hardware_config` through unchanged. Do not add a new `HarmonizationJob` dataclass field because old job JSON files load through strict dataclass construction.

- [ ] **Step 4: Run CLI/web tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_harmonization_worker_stop.py tests\test_web_shell.py -q
```

Expected: PASS.

## Task 5: Final Focused Verification And Commit

**Files:**
- All changed files from Tasks 1-4.

- [ ] **Step 1: Run focused hardware/realtime suite**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_hardware_snapshots.py tests\test_hardware_driver_layer.py tests\test_realtime_emf_profile.py tests\test_harmonization_worker_stop.py tests\test_web_shell.py tests\test_web_hardware_status.py -q
```

Expected: PASS.

- [ ] **Step 2: Check git diff**

Run:

```powershell
git diff --stat
git diff --check
```

Expected: no whitespace errors; changed files match this plan.

- [ ] **Step 3: Commit implementation**

Run:

```powershell
git add core\hardware\snapshots.py core\hardware\drivers.py core\realtime\emf_profile.py services\harmonization_worker.py apps\cli\commands\harmonize.py apps\web\main.py tests\test_hardware_snapshots.py tests\test_hardware_driver_layer.py tests\test_realtime_emf_profile.py tests\test_harmonization_worker_stop.py tests\test_web_shell.py
git commit -m "feat: add v2 hardware snapshot integration"
```

Expected: commit succeeds.

## Deferred

- Full pytest suite remains deferred because of prior RAM/CPU/OpenBLAS instability.
- Real external HID/serial open from operator UI is not included in this step.
- Calibration baselines and bounded score weighting are the next safe layer after snapshots are present in traces.
