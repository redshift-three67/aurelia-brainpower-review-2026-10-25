# V2 Hardware Snapshot Integration Design

## Goal

Add the next safe V2 step after the hardware driver layer: opt-in realtime hardware snapshots that can enrich EMF profiles and harmonization traces without sampling or opening external devices by default.

## Context

The current V2 realtime work has two stable foundations:

- `core/realtime/emf_profile.py` provides a shared `EMFProfileService` with an injectable sensor entropy probe.
- `core/hardware/drivers.py` provides provider contracts, CPU/HID/TrueRNG/mock providers, a registry, and a cached sampler. HID and serial device opens are disabled by default.

The harmonization worker already writes JSONL lifecycle and cycle events under `data/harmonization_jobs/events/`, but it still calls `EMFProfileService()` with the lightweight default fallback. That means the trace is replayable at the EMF algorithm level, but not yet enriched by the driver-layer hardware observations.

## Approaches Considered

### Recommended: Snapshot service plus opt-in worker wiring

Create a small `HardwareSnapshotService` on top of `CachedHardwareSampler`. It captures JSON-safe samples, computes a compact summary, and exposes a sensor entropy tuple that `EMFProfileService` can consume. The harmonization worker adds this snapshot only when `hardware_config["use_driver_layer"]` is true.

This keeps the driver layer independent, makes traces explainable, and keeps external device access explicitly disabled unless a later operator-approved path enables it.

### Alternative: Directly inject sampler into every EMF call

The worker and web routes could pass `hardware_sampler_entropy_probe(CachedHardwareSampler(...))` directly into `EMFProfileService`. This is smaller, but it loses reusable snapshot metadata and makes replay weaker because event traces would only contain the derived entropy value.

### Deferred: Live hardware-weighted scoring

Analysis and harmonization scoring could be changed immediately based on live hardware observations. This is deliberately deferred. Without baseline calibration and replay validation, changing core resonance scores would make results harder to explain and could reduce repeatability.

## Architecture

Add `core/hardware/snapshots.py` with:

- `HardwareSnapshot`: immutable JSON-safe snapshot data.
- `HardwareSnapshotSummary`: total/ok/fallback/error counts, mean usable entropy, mean quality, and health state.
- `HardwareSnapshotService`: captures snapshots from an injected or default `CachedHardwareSampler`.
- `snapshot_sensor_entropy_probe(snapshot)`: converts a captured snapshot into the `(value, status)` shape expected by `EMFProfileService`.
- `build_hardware_snapshot_service(...)`: creates the default registry/sampler while preserving the no-device-open default.

Extend `HardwareDriverRegistry.default()` with an optional `allow_device_open: bool = False` parameter. The default remains unchanged. This only enables future explicit paths to construct providers that may open HID/serial devices; it does not change any current hot path.

Extend `EMFProfileService` with an optional `sensor_source` label in replay metadata. Existing default behavior remains unchanged.

## Harmonization Flow

Add `capture_realtime_context(hardware_config)` in `services/harmonization_worker.py`.

When `use_driver_layer` is false or absent:

- Return the existing lightweight EMF profile only.
- Do not construct or sample the hardware driver layer.

When `use_driver_layer` is true:

- Capture one hardware snapshot per traced EMF context window.
- Feed the captured snapshot summary into `EMFProfileService` as sensor entropy.
- Add both `emf_profile` and `hardware_snapshot` to the `cycle_metrics` payload.
- Preserve best-effort behavior: snapshot failures return a fallback snapshot and never stop the job.

The worker should continue tracing only cycle 1 and every tenth cycle for EMF context, preserving current load characteristics.

## CLI And Web Controls

Add opt-in flags/fields:

- CLI `harmonize harmonize`: `--driver-layer/--no-driver-layer`, default off.
- Web `HarmonizationRequest`: `use_driver_layer: bool = False`.

Both pass `use_driver_layer` into `hardware_config`. Existing callers remain compatible.

External HID/serial opening remains off in this step. If a later step exposes it, it should require an explicit operator-level control and should continue to document that Windows native open behavior cannot be hard-timeout guaranteed.

## Analysis And Harmonization Semantics

This step improves accuracy and traceability by making the realtime hardware context visible and replayable. It does not yet alter core resonance scores.

The next scoring step should use stored snapshots to compute a bounded confidence/context adjustment, not direct unbounded score changes. That later work needs calibration baselines and replay tests first.

## Error Handling

- Snapshot capture never raises into web or worker callers.
- Unknown providers produce fallback samples through `CachedHardwareSampler`.
- Non-finite values are sanitized before JSON output.
- If hardware snapshot capture fails, the trace still contains a fallback summary with `health="fallback"`.

## Testing

Focused tests only:

- Snapshot service captures mock provider samples and produces JSON-safe summaries.
- Disabled/default worker path does not sample the driver layer.
- Opt-in worker path writes `hardware_snapshot` and feeds sensor entropy into `emf_profile`.
- CLI passes `use_driver_layer` in `hardware_config`.
- Web harmonization request passes `use_driver_layer` in `hardware_config`.
- Existing hardware driver, realtime EMF, worker, and web-shell focused tests still pass.

Full pytest remains deferred because this Windows environment has already shown RAM/CPU sensitivity under larger suites.

## Acceptance Criteria

- Default behavior is unchanged and lightweight.
- Port `8090` is not touched.
- Driver-layer snapshots are opt-in and replayable.
- No external HID/serial device is opened by default.
- Harmonization trace events can show which hardware observations influenced an EMF profile.
- Focused tests pass without running the full suite.
