# Gate 5 EMF Authority and Source Truth Design

**Date:** 2026-08-06
**Worktree:** `C:\morphic_v1\.worktrees\operator-workbench-phase1`
**Branch:** `report-ux-polish`
**Status:** User-approved design; implementation not started

## Goal

Complete the local Single-Core EMF gate without introducing physical sensor,
remote hardware, cloud, or medical claims. The operator must deliberately
enable or disable telemetry, every productive path must obey one durable lease
authority, and every displayed proxy value must identify its technical source
and fallback state.

## Accepted Decisions

1. `EmfTelemetryAuthority` remains the only productive activation authority.
2. Activation persists across reloads and controlled process restarts until the
   operator explicitly disables it.
3. Software fallback values remain visible, but every value is labelled with
   its source and `ok`, `partial`, or `fallback` status.
4. Legacy `/api/v1/emf/*` endpoints remain available as compatibility routes,
   but delegate to the same modern authority and measurement implementation.
5. Legacy routes enforce the same API-key/session and lease security as modern
   routes, even when that breaks previously unauthenticated legacy callers.
6. Gate 5 does not connect the Linux server, external hardware, or remote
   WebSockets. Those remain post-baseline platform work.

## Current Accepted Foundation

Task 69 already provides:

- explicit Workbench enable and disable controls;
- default-off authority creation;
- durable generation and activation records;
- private propagation of the authority path to the scan child;
- measurement leases that are revalidated after productive reads;
- modern HTTP and WebSocket authentication checks;
- disabled-state rendering without a fabricated zero value;
- browser coverage for invalid EMF index values.

Gate 5 must preserve these guarantees.

## Current Gaps

1. Successful enable/disable POSTs are trusted directly by the UI before a
   confirming status read.
2. The Workbench displays proxy metrics but not the source status for each
   component.
3. `web_app.py` still contains `_emf_active`, a separate measurement function,
   unprotected legacy routes, and WebSocket connect-auto-enable behavior.
4. Modern and legacy route contracts are not proven to share one durable
   authority across process boundaries.
5. The product label can still appear as a generic EMF index instead of the
   required proxy description.

## Architecture

### Single Durable Authority

`EmfTelemetryAuthority` owns a durable main record and generation record. An
enable or disable operation rotates the generation and activation ID. A
measurement obtains an opaque lease from `begin_measurement()` and may publish
only while `measurement_is_current(lease)` remains true.

The authority record is initialized disabled only when it does not yet exist.
Existing valid state is never silently reset at application startup.

No API response exposes the generation, activation ID, authority path, or
lease token.

### Shared Modern and Legacy Operations

`apps/web/emf.py` provides the shared operations for:

- enable;
- disable;
- status;
- one HTTP profile measurement;
- WebSocket authentication, lease acquisition, measurement, and revalidation;
- monitor HTML.

The modern `/api/emf/*` router and legacy `/api/v1/emf/*` compatibility router
call those same operations. They do not duplicate mutable state or measurement
logic.

`apps/web/main.py` binds both routers to its existing app state.

`web_app.py` removes `_emf_active` and `_measure_emf` as authorities, initializes
the same authority/session infrastructure for its deprecated standalone app,
and binds the shared routers. A legacy WebSocket connection never enables
telemetry.

### Measurement Service

All productive measurements use `core.realtime.emf_profile.EMFProfileService`.
The index remains a composite system/entropy proxy derived from:

- OS CSPRNG sample quality (`rng`);
- CPU timing jitter (`cpu_timing`);
- current CPU/memory load (`system_load`);
- optional sensor entropy (`sensor_entropy`).

No Gate-5 code treats this composite as a physical field measurement.

## API Contract

### Status

Both `GET /api/emf/status` and `GET /api/v1/emf/status` return the same safe
payload:

```json
{
  "active": false,
  "activation_policy": "until_manually_disabled",
  "measurement_label": "System-/Entropie-basierter EMF-Proxy-Index"
}
```

### Enable and Disable

Both route families require the same API-key/session security.

- `POST .../enable` rotates to an enabled generation and returns the re-read
  safe status payload.
- `POST .../disable` rotates to a disabled generation and returns the re-read
  safe status payload.
- Request query values such as the historical `continuous` flag do not create a
  second activation mode.

### Profile Measurement

Both profile routes:

1. authenticate;
2. acquire an enabled-generation lease;
3. fail with HTTP 409 before measurement when disabled;
4. measure through `EMFProfileService`;
5. revalidate authentication and lease after measurement;
6. fail closed when either authority changed;
7. return only the safe profile payload.

### WebSocket

Both WebSocket routes:

- close with `4401` before accept when authentication fails;
- close with `4409` when telemetry is disabled;
- never auto-enable;
- revalidate authentication and lease before every send;
- send no snapshot measured under a revoked generation;
- close on disable instead of emitting a final stale snapshot.

## Workbench UI Contract

### Activation Controls

The initial page load only reads status and never enables telemetry.

During enable or disable:

1. both buttons are temporarily disabled;
2. the protected POST is sent;
3. the UI re-reads authoritative status;
4. button state is derived only from that confirming response;
5. hardware truth is reloaded independently;
6. an unknown status produces an explicit error state, not a guessed state.

Active copy states that telemetry remains active until manually disabled.

### Product Language

The visible aggregate label is:

> System-/Entropie-basierter EMF-Proxy-Index

The UI must not use physical field, exposure, burden, diagnosis, treatment, or
effectiveness language. A different physical-sensor label is allowed only in a
future gate with confirmed sensor authority.

### Source Truth

Each displayed metric includes its source key and health state:

| Displayed value | Source key |
|---|---|
| Entropy | `rng` |
| Timing jitter | `cpu_timing` |
| System load | `system_load` |
| Sensor entropy | `sensor_entropy` |

The aggregate index is labelled as derived. `ok`, `partial`, and `fallback`
remain distinct. Hardware component states remain separately represented as
`real_active`, `real_available_not_used`, `software_fallback`,
`not_implemented`, or `unknown`.

### Invalid Values

For every aggregate or component value, `null`, missing, empty, non-numeric,
NaN, and infinity render as `--`. Invalid aggregate values do not render a
gauge and are never coerced to zero.

## Failure and Race Handling

- Disable during an HTTP measurement discards the measured payload and returns
  HTTP 409.
- Disable during a WebSocket measurement closes without sending the payload.
- Authentication rotation during a productive read fails closed.
- Partial authority writes fail closed under the existing generation-record
  contract.
- Status-read failure after a successful POST leaves the UI in an unknown/error
  state until a later authoritative read succeeds.
- Hardware-truth failure does not rewrite activation state; it is reported as a
  separate display failure.
- Startup never repairs an unreadable authority by silently enabling it.

## Security and Privacy

- All modern and legacy mutating/read/streaming routes use the same security
  policy.
- No lease, API key, session token, local path, raw random bytes, or new raw
  sensor sample is returned to the browser. Gate-5 source badges expose only
  the fixed source keys and health states defined in this specification.
- WebSocket state is bounded to one authenticated connection loop and the
  current generation.
- Gate 5 does not open network listeners beyond the existing loopback app.
- No telemetry activation is persisted in browser storage, drafts, or
  templates.

## TDD and Acceptance Matrix

### Authority and HTTP

- first initialization is disabled;
- enable survives app recreation and a subprocess read;
- disable rotates and revokes an existing lease;
- modern and legacy routes return identical safe status;
- modern and legacy routes enforce identical authentication;
- disabled profile routes never call the measurement service;
- post-read revocation discards the payload.

### WebSocket

- unauthenticated connection measures nothing;
- disabled connection measures nothing;
- connection never enables authority;
- current authenticated lease can send one safe snapshot;
- authentication or authority revocation before send closes without payload;
- modern and legacy routes have equivalent behavior.

### UI and Rendering

- page load performs status GET only;
- POST success is not accepted without a confirming GET;
- hardware truth reload follows status revalidation;
- all four source keys and statuses render;
- fallback values are visible and explicitly labelled;
- invalid values show `--` and no aggregate gauge;
- active copy states the manual-disable lifetime;
- Desktop and 375px have no page overflow.

### Legacy Authority Closure

Static and behavioral tests prove that `web_app.py` contains no `_emf_active`,
no separate `_measure_emf`, and no connect-auto-enable path. Launcher tests
prove active entry points use the consolidated routers.

### Final Gate

Gate 5 requires:

- focused authority/security/UI matrices green;
- full Python suite green;
- full isolated browser matrix green;
- manual Desktop and 375px acceptance;
- two independent APPROVE reviews with zero blocking findings;
- SHA-256 source manifest and verified review/freeze/status records;
- clean ports, no owned stale processes, and empty Git index.

## Non-Goals

- physical EMF sensor integration;
- Linux root-server integration;
- remote or cross-host WebSocket transport;
- hardware modulation or Quartz control;
- score, ranking, or analysis changes;
- report, PDF, archive, or Harmonization changes;
- external catalog activation;
- Quantum/Grover integration;
- Radiquant/Lovable Cloud integration.

## Rollback Boundary

Gate 4's verified source manifest remains the rollback reference. Gate 5 uses a
new independent manifest and never rewrites Gate-4 evidence. If Gate 5 fails,
the EMF authority remains default-off or manually disabled and no later
hardware/platform gate may start.
