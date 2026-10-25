# V2 Realtime EMF Profile Design

## Goal

Build the first V2 realtime foundation for Morphic Engine by replacing duplicated EMF measurement logic with one shared profile service, adding lightweight trace events for harmonization, and preserving deterministic replay metadata without stressing the local Windows system.

## Scope

This first V2 slice is intentionally narrow:

- Create one shared EMF profile service used by web EMF endpoints and CLI workflow step 05.
- Produce a typed, JSON-safe profile snapshot with entropy, timing, system load, source health, recommendation, and counter frequencies.
- Add a small append-only event writer for harmonization lifecycle and cycle metrics.
- Keep all measurements short, local, and low load.
- Keep port `8090` untouched.
- Keep the full pytest suite deferred; use focused tests only.

## Non-Goals

- No rewrite of all hardware providers.
- No long-running GPU, CPU, RAM, or WebSocket load tests.
- No clinical or medical accuracy claims.
- No external network dependency.
- No replacement of the current JSON job store in this slice.

## Current Context

`apps/web/emf.py` contains a pure-Python `measure_emf()` implementation for `/api/emf/profile` and `/api/emf/ws`.

`apps/cli/workflow/step05_emf.py` contains a similar but numpy-based EMF flow that modifies `WorkflowState` with a compensation vector, counter frequencies, and corrected frequency.

`core/hardware/sensors.py` already exposes `SensorManager.get_combined_entropy()`, but this value is not part of the web EMF profile today.

`services/harmonization_worker.py` runs JSON-backed background jobs and computes hardware modulation metrics each cycle, but the cycle metrics are not persisted as a trace.

## Architecture

### EMF Profile Service

Create `core/realtime/emf_profile.py`.

The module owns:

- `EMFProfile`: dataclass for one measurement snapshot.
- `EMFProfileService`: low-load service that measures entropy, timing jitter, system load, optional sensor entropy, composite EMF index, recommendation, and counter frequencies.
- Helper functions for clamping, histogram-based entropy scoring, and JSON-safe serialization.

The profile shape is:

```python
{
    "timestamp": "2026-07-03T12:00:00.000000",
    "emf_index": 0.2145,
    "entropy_score": 0.9821,
    "timing_jitter_ms": 0.0132,
    "system_load": 0.31,
    "sensor_entropy": 0.5,
    "recommendation": "niedrig",
    "counter_frequencies": [528.0],
    "source_health": {
        "rng": "ok",
        "cpu_timing": "ok",
        "system_load": "ok",
        "sensor_entropy": "fallback"
    },
    "replay": {
        "algorithm": "emf-profile-v2",
        "sample_size": 2048,
        "timing_iterations": 20,
        "sensor_manager": "core.hardware.sensors.SensorManager"
    }
}
```

### Web Integration

`apps/web/emf.py` keeps its route contract stable. `measure_emf()` remains available for compatibility, but delegates to `EMFProfileService().measure().to_dict()`.

The WebSocket payload remains:

```python
{"type": "emf_update", **profile}
```

This preserves the existing UI behavior.

### CLI Workflow Integration

`apps/cli/workflow/step05_emf.py` uses the shared service for sensing and profiling. It keeps the existing compensation-vector logic because that behavior is workflow-specific.

The workflow state receives:

- `composite_emf_index` from the profile.
- `counter_frequencies` from the profile.
- unchanged vector compensation and corrected frequency behavior.

### Harmonization Event Trace

Create `core/realtime/event_log.py`.

The event log writes JSON Lines files under `data/harmonization_jobs/events/`.

Each event includes:

- `timestamp`
- `job_id`
- `event_type`
- `payload`
- `sequence`

`services/harmonization_worker.py` appends:

- `job_started`
- `cycle_metrics`
- `stop_requested`
- `completed`
- `error`

Cycle events include the existing modulation metrics and one EMF profile snapshot on the first cycle and then every 10 cycles, matching the existing status-save cadence to avoid extra load.

## Determinism And Replay

The first slice does not make stochastic measurements deterministic. Instead, it records enough metadata to replay or explain a completed run:

- algorithm identifier
- sample size
- timing iteration count
- source health
- sensor entropy fallback status
- per-cycle modulation metrics in the event log

Future slices can add signed hash chains, seeded deterministic replay, and calibration baselines.

## Error Handling

Measurement failures must degrade to neutral values instead of breaking endpoints or workflow runs:

- `sensor_entropy`: fallback to `0.5`
- `system_load`: fallback to `0.3`
- unavailable optional modules: mark source health as `fallback`
- unexpected measurement error: return a valid profile with source health marking the failing component

Harmonization event logging must never stop a harmonization job. Event write failures are swallowed after best effort.

## Testing

Use focused tests only:

- Profile service returns bounded values and JSON-safe fields.
- Histogram entropy scoring treats concentrated bytes as lower quality than varied bytes.
- Web `measure_emf()` delegates to the shared profile shape.
- CLI `step_05_emf()` consumes a fake profile service and updates `WorkflowState`.
- Event log appends JSON Lines events with sequence numbers.
- Harmonization worker appends lifecycle/cycle events with monkeypatched time and modulation.

Do not run the full pytest suite in this slice.

## Migration

No public endpoint changes are required. Existing callers of `/api/emf/profile`, `/api/emf/ws`, and workflow step 05 continue to work.

## Risks

- EMF semantics are heuristic. The implementation must label values as operational telemetry, not medical truth.
- Sensor availability differs by machine. The service must make fallback status explicit.
- Harmonization workers are multiprocessing-based. Event logging must be file-safe and lightweight.

## Acceptance Criteria

- One shared EMF profile service is used by web and CLI workflow step 05.
- Profile output includes bounded metrics, source health, counter frequencies, and replay metadata.
- Harmonization jobs write lifecycle and cycle JSONL events without breaking existing job JSON behavior.
- Focused tests pass.
- Full pytest suite remains documented as deferred.
