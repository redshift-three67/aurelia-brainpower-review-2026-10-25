# V2 Hardware Driver Layer Design

## Goal

Build a safe, testable hardware driver layer for Morphic Engine V2 so real local hardware can be detected, sampled, cached, and reported without blocking web requests, destabilizing Windows, or mixing true device reads with software simulation.

## Scope

This slice creates the driver layer and integrates it into realtime profiling/status surfaces:

- Define a shared hardware signal contract for real and virtual providers.
- Implement lightweight CPU timing, HID, TrueRNG/serial, and mock providers behind one interface.
- Add a cached sampler that enforces short read windows, timeout/fallback status where supported, and JSON-safe snapshots.
- Keep real HID/serial reads opt-in; native device-open behavior is Windows-driver-dependent and is not used by default status/hotpath code.
- Let `EMFProfileService` consume the cached sampler only when explicitly configured.
- Let `/api/hardware/status` report driver-layer providers and health.
- Preserve compatibility with existing `core.hardware.sensors.SensorManager` and `providers.hardware.entropy_sources` during this slice.

## Non-Goals

- No automatic long-running HID, serial, GPU, RAM, or network probes in web or worker hotpaths.
- No replacement of the full analysis or scan entropy flow in this slice.
- No clinical or medical accuracy claims.
- No external network dependency.
- No Full Pytest Suite run; use focused tests only.

## Current Context

`core.hardware.sensors` contains a `Sensor` abstraction, `HIDSensor`, `TrueRandomSensor`, and `SensorManager`. It can perform a 0.5 second HID read in `get_combined_entropy()`.

`providers.hardware.entropy_sources` contains another abstraction named `EntropySource` with CPU, HID, TrueRNG, QRNG, GPU, network, and mock sources. Some providers can block or touch external devices directly.

`core.realtime.emf_profile` currently defaults to lightweight software telemetry and exposes `sensor_manager_entropy_probe()` as an explicit heavy/legacy path.

`apps.web.main` exposes `/api/hardware/status` by calling `core.hardware.system_info.get_full_system_report()` and adding explanatory notes.

The next layer must reduce duplication and make hardware use explicit, bounded, and inspectable.

## Architecture

### Hardware Signal Model

Create `core/hardware/drivers.py`.

The module owns:

- `HardwareSignalSample`
- `HardwareProviderStatus`
- `HardwareSignalProvider`
- `CpuTimingSignalProvider`
- `HidSignalProvider`
- `TrueRngSignalProvider`
- `MockSignalProvider`
- `HardwareDriverRegistry`
- `CachedHardwareSampler`

The canonical sample shape is:

```python
{
    "source_id": "cpu_timing",
    "source_type": "system",
    "status": "ok",
    "timestamp": "2026-07-03T12:00:00.000000",
    "value": 0.3125,
    "unit": "normalized_entropy",
    "duration_ms": 12.4,
    "quality": 0.81,
    "metadata": {
        "sample_count": 256,
        "provider": "CpuTimingSignalProvider"
    },
    "error": ""
}
```

Valid statuses:

- `ok`
- `unavailable`
- `timeout`
- `error`
- `fallback`

Values are normalized to `0.0 <= value <= 1.0`. Providers may include raw metadata, but the top-level sample remains JSON-safe.

### Provider Contract

`HardwareSignalProvider` exposes:

```python
provider_id: str
provider_type: str
display_name: str
default_timeout_ms: int
is_available() -> bool
sample(timeout_ms: int | None = None) -> HardwareSignalSample
```

Provider implementations must never raise from `sample()`. Errors become `HardwareSignalSample(status="error", value=0.5, error="...")`.

`is_available()` must be short and defensive. It can return `False` if optional packages are missing or no matching hardware is detected.

### Providers

`CpuTimingSignalProvider`

- Always available.
- Uses a short timing-jitter sample.
- Default timeout target: 50 ms.
- No external dependencies.
- Status `ok` when a bounded sample is collected.

`HidSignalProvider`

- Uses optional `hid`.
- Defaults to VID `0x0E50`, PID `0x0002`, matching existing Trigonal Sensor assumptions.
- `is_available()` enumerates matching devices.
- `sample()` opens the device nonblocking, reads until timeout, and closes in `finally`.
- No data returns `fallback` with neutral value `0.5`.
- Missing library or device returns `unavailable`.

`TrueRngSignalProvider`

- Uses optional `serial` / `serial.tools.list_ports`.
- Detects TrueRNG-style ports using existing VID/PID/name heuristics from `providers.hardware.entropy_sources.TrueRngSource`.
- Reads a small byte window with short timeout.
- Missing library or device returns `unavailable`.

`MockSignalProvider`

- Deterministic provider for tests and replay.
- Always available.
- Returns configured normalized value and metadata.

### Registry

`HardwareDriverRegistry.default()` creates providers in this order:

1. CPU timing
2. HID
3. TrueRNG

The registry exposes:

- `list_statuses()`
- `available_providers()`
- `get(provider_id)`
- `sample(provider_ids=None, timeout_ms=None)`

The default registry must not sample HID or serial unless `sample()` is explicitly called.

### Cached Sampler

`CachedHardwareSampler` wraps a registry and stores recent samples by provider ID.

Behavior:

- TTL default: 2.0 seconds.
- Timeout default: 75 ms per provider.
- `sample(provider_ids)` returns cached samples if fresh.
- Expired or missing cache entries trigger provider reads.
- Exceptions from registry/provider become `fallback` samples.

This sampler is the only object that realtime web/EMF code should use.

### EMF Profile Integration

Extend `core.realtime.emf_profile` with an opt-in helper:

```python
hardware_sampler_entropy_probe(sampler: CachedHardwareSampler) -> tuple[float, str]
```

The helper:

- samples configured providers through the cache
- combines available `ok` samples using a conservative average
- returns `(0.5, "fallback")` when no real sample is available
- returns status `ok`, `fallback`, or `partial`

`EMFProfileService` default behavior stays lightweight and unchanged. Real hardware becomes explicit dependency injection:

```python
EMFProfileService(sensor_entropy_probe=lambda: hardware_sampler_entropy_probe(sampler))
```

### Web Status Integration

`/api/hardware/status` adds a `driver_layer` object:

```python
{
    "driver_layer": {
        "providers": [
            {
                "provider_id": "cpu_timing",
                "provider_type": "system",
                "display_name": "CPU Timing",
                "available": true,
                "default_timeout_ms": 50
            }
        ],
        "note": "Driver layer is available; status does not open devices. Real HID/serial reads are opt-in and use short read windows, but native open behavior depends on the Windows driver."
    }
}
```

This endpoint must list provider availability but must not perform blocking HID/serial samples.

## Compatibility

Existing `SensorManager` and `EntropySource` code remains available. This slice does not remove or rename those APIs.

Future slices can adapt `SensorManager` and `select_entropy_source()` internally to use the new driver layer. That migration is intentionally separate so current scan and field commands remain stable.

## Error Handling

- Provider imports are optional and guarded.
- Missing hardware returns `unavailable`, not an exception.
- Device read errors return `error`.
- Time-bounded no-data reads return `fallback`; native device-open calls are avoided by default and only run when explicitly enabled.
- `CachedHardwareSampler` never raises to web/worker callers.
- All samples are JSON-safe dataclass dictionaries.

## Testing

Use focused tests only:

- CPU provider returns bounded JSON-safe samples.
- Mock provider returns deterministic samples.
- HID provider reports `unavailable` when the `hid` module is absent or no device is found.
- TrueRNG provider reports `unavailable` when serial support/device is absent.
- Registry lists providers without sampling external hardware.
- Cached sampler reuses fresh samples and refreshes expired ones.
- Hardware entropy probe returns fallback for no ok samples and average for ok samples.
- `/api/hardware/status` includes `driver_layer` without sampling HID/serial.

Do not run the full pytest suite in this slice.

## Risks

- Real HID/serial behavior varies by driver and Windows permissions. The design isolates this to provider classes, keeps device-open reads opt-in, and returns explicit health status.
- Timeouts in Python cannot forcibly cancel every blocking native call. Providers must use nonblocking/short-timeout APIs where the libraries support them.
- Driver values are operational telemetry, not diagnostic truth. The API must expose source and health metadata so downstream analysis can reason about quality.

## Acceptance Criteria

- A shared `core.hardware.drivers` layer exists with provider/status/sample dataclasses.
- CPU, HID, TrueRNG, and mock providers implement the same contract.
- A cached sampler prevents repeated realtime reads in hotpaths.
- `EMFProfileService` can opt into driver-layer entropy without changing the lightweight default.
- `/api/hardware/status` reports driver-layer provider health without sampling devices.
- Focused tests pass.
- Git contains separate spec, plan, and implementation commits.
