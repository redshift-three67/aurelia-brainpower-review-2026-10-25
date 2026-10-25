# Radi144 Strategic Optimization Plan

## 1. Review scope and snapshot boundary

| Item | Verified value |
|---|---|
| Repository root | `C:/Users/Hubert111/Documents/Radi144` |
| Branch / HEAD at review start | `main` / `b8ac33a1360f1cb56f06e602fcd37cbda2a9c641` |
| Tracked-source aggregate SHA-256 at review start | `925abe104fb07bede859c5c47288567fbdb820bac6e9318da7e695614b38dbae` |
| Pre-existing worktree change | `AGENTS.md` added but unstaged |
| Review method | Static source, configuration, test, Git and documentation inspection only; no project imports, tests, server startup, database access, or runtime artifact inspection/execution. |
| Intended change of this review | This document only. |

This plan separates verified present implementation from the target architecture described in the July 2026 handoff material. Those handoff documents describe a prior snapshot on `fix/r144-frontend-synergy` at `9649e9b`; they are useful governance input but are not current-state evidence for this `main` snapshot.

## 2. Current architecture map

```text
Browser UI / PowerShell UI / CLI
        |                 |
        +---- HTTP API ----+-------------------+
        |                  |                   |
     main.py           dev_cli.py        generate_matrix.ps1
        |                  |                   |
        +---------- application orchestration -+
                           |
                    app/api/resonance.py
                           |
       +-------------------+---------------------+
       |                   |                     |
ResonanceMatrixEngine  archive services       PDF export
       |                   |                     |
algorithms/          JSON files under       arbitrary paths
- signatures         data/runtime/          accepted by API
- EMF simulation
- amplifier matching
       |
Torch / NumPy / psutil / optional report tooling

Parallel, intentionally unconnected preparation:
app/interchange_bus + bus_consumer_service -> local SQLite consumer only
```

### Architectural boundaries and invariants

| Boundary / invariant | Current evidence | Required preservation rule |
|---|---|---|
| Protected calculation core | `app/algorithms/resonance_engine.py`, `client_signature.py`, `emf_compensator.py`, `amplifier.py` | Do not change result-producing semantics until a reviewed, resource-bounded golden baseline exists. |
| Local-first operation | `main.py` defaults to `127.0.0.1:8090`; Product Purpose Contract requires offline capability | Preserve loopback-only, one-process local operation as the safe default. |
| Non-medical product posture | `app/services/safety_service.py` adds a disclaimer and response markers | Make the approved purpose/claim policy enforceable before expanding interfaces or distribution. |
| PII-bearing runtime authority | `data/runtime/clients.json`, `sessions.json`, `artifacts.json`; models persist cleartext identity and focus data | Treat every runtime store, browser cache, export, log and report as `restricted_client` until classified and protected. |
| API/CLI/UI share an engine but not one orchestration service | API calls `ResonanceMatrixEngine`; CLI contains a separate large orchestration flow; PowerShell remains separate | Consolidate only behind characterization tests; do not refactor all three paths together. |
| Bus is preparatory, not an integration backbone | `app/interchange_bus/**`, `bus_consumer_service.py` | Keep default-off and disconnected. Do not connect it to engine, Lovable, Radiquant, or external transport without a later approved transport decision. |
| Runtime dependency gate | `app/bootstrap.py`, `run.bat` | Retain fail-closed dependency preflight, but make interpreter, settings and lockfile behavior reproducible. |

## 3. Dependency map

| Layer | Direct dependencies | Notes |
|---|---|---|
| API host | FastAPI, Uvicorn, Pydantic, `httpx<0.28` for TestClient | `main.py` creates a process-global app and imports global router/engine state. |
| Algorithm engine | Torch, NumPy, psutil | Candidate generation, projection and similarity tensors are allocated in request execution. CUDA is optional, but default engine initialization requests it. |
| Exports | ReportLab, OpenPyXL | API PDF generation and CLI export have separate implementations. |
| Persistence | Pydantic models + JSON files | `JsonStore` only gives per-file atomic replacement; it has no lock, revision, cross-store transaction, encryption, or migration capability. |
| Browser | vanilla HTML/CSS/JS | No package-managed frontend build. Browser and server use a broad state surface. |
| Bus preparation | Python stdlib SQLite | Current read-side consumer bootstraps and writes a local SQLite schema; message integrity is a self-hash, not producer authentication. |
| Optional/aspirational | D-Wave SDK, RTL-SDR, Pillow | D-Wave and SDR are not installed/connected productive capabilities; Pillow is conditionally used but absent from `requirements.txt`. |

## 4. Verified high-risk optimization targets

| Priority | Finding | Evidence | Strategic response |
|---:|---|---|---|
| 1 | The API exposes client-controlled absolute/relative read and write paths. | `app/api/resonance.py:128-150`, `212-228`, `535-693`, `864-874` | Replace path transport with opaque server-side resource IDs and contained roots before any non-loopback use. |
| 2 | HTTP authentication is optional and WebSocket routes accept connections before authorization/origin/payload checks. | `main.py:78-107`; `app/api/resonance.py:1072-1221` | Define one local access model covering HTTP, WebSocket, destructive actions and UI behavior. Refuse external binding without it. |
| 3 | Engine work is synchronous, global-stateful and resource-heavy. | `app/api/resonance.py:27-33`, `413-693`; `app/algorithms/resonance_engine.py:49-105`, `999-1111` | Establish a small deterministic execution profile, resource budget and single-flight/job boundary before load or integration work. |
| 4 | Engine semantics and product claims diverge. | `resonance_engine.py:566-575`, `1113-1155`; `emf_compensator.py:52-63`, `574-635`; README claims; Product Purpose Contract §8 | Characterize actual behavior and clearly classify simulation, mock and metaphorical features before any claim/UI modernization. |
| 5 | JSON runtime records contain cleartext PII and can lose updates across processes. | `app/models/*.py`; `app/services/json_store.py:15-36`; service methods; systemd supports configurable workers | Keep one writer/process now; later migrate through a tested, encrypted, transactional data lifecycle—not a direct in-place conversion. |
| 6 | Erasure is not transactionally recoverable and the fallback gate token is a known source value. | `app/services/erasure_service.py:30-35`, `178-241`; `app/services/audit_service.py:40-69` | Do not rely on the current cascade for protected data. Design a journaled erasure/recovery protocol only after data authority and key custody are approved. |
| 7 | Public response and database endpoints disclose absolute filesystem paths. | `app/api/resonance.py:535-551`, `554-639`; report manifest model | Replace paths with opaque references and separate operator-only diagnostics. |
| 8 | The API request schema permits conflicting identity inputs and contains flags that are not consumed by the engine call. | `app/schemas/resonance.py:8-29`; `app/api/resonance.py:279-305`, `441-452` | Specify disjoint input modes and a truthful request/response contract after golden characterization. |
| 9 | Browser/PDF/CLI reports are independent composition paths. | `user_workflow.*`, `dev_cli.py`, `app/api/resonance.py:696-884` | First map output equivalence and privacy rules; then extract shared presentation primitives incrementally. |
| 10 | Supply-chain and deployment definitions are not reproducible. | `requirements.txt`; `deploy/server.env.example`; `deploy/resonance-engine.service`; no lockfile, CI, SBOM, or license manifest | Build an allowlisted artifact and platform-specific locked environments only after the local runtime and data boundaries are stable. |

## 5. Strategic sequence

Each gate is approval-dependent. No implementation, integration, commit, data migration, server exposure, or core change is authorized by this plan.

### Gate 0 — Freeze current authority and reconcile documentation

**Objective:** create a current-snapshot authority record before relying on historical handoff material.

1. Capture the complete current Git state, tracked/untracked/ignored populations, source hashes and active configuration-presence metadata without exposing secrets.
2. Identify the authoritative current product-purpose document and label the July handoff documents as historical unless re-approved against the current `main` snapshot.
3. Produce an active-surface inventory: API/OpenAPI, browser UI, CLI, PowerShell, reports, deployment scripts, reference data and bus preparation.
4. Do not run the full engine suite until an explicit resource preflight permits a bounded profile.

**Exit evidence:** hash-bound checkpoint; documented source of truth; no source drift during capture; approval to begin policy work.

### Gate 1 — Policy, claims and data classification

**Objective:** translate the approved non-medical purpose into a versioned, fail-closed runtime policy without touching algorithms.

1. Create a claim inventory for all active human-facing text and API metadata.
2. Classify every data flow: request, runtime JSON, browser storage, log, report, PDF, template, temporary image, bus envelope and deployment artifact.
3. Define a policy version set and drift checks that reject unknown claim/data/policy versions.
4. Qualify or remove only demonstrably inaccurate presentation claims; do not alter engine outputs.

**Exit evidence:** complete traceability matrix; negative drift tests; no `app/algorithms/**` change; independent product/compliance review.

### Gate 2 — Golden core characterization and resource profile

**Objective:** establish what the current core actually does under a safe, synthetic, deterministic test profile.

1. Define synthetic fixtures only; no client, runtime, export or historical session data.
2. Control time, RNG, candidate count, threads, device and output roots through a test harness without changing production semantics.
3. Run each characterized scenario in fresh bounded processes and record input/source/dependency/output hashes.
4. Explicitly separate deterministic paths from intentional nondeterminism: organ clock, HRV simulation, EMF profiling, CUDA and image temporary-path behavior.
5. Record CPU RAM, Windows commit/pagefile and VRAM peak thresholds; stop on native failures.

**Exit evidence:** approved immutable baseline with reproducible outcomes and resource budget. Only then can any core-correctness proposal be considered separately.

### Gate 3 — Local access, paths and execution containment

**Objective:** make the standalone profile safely bounded before it can be exposed beyond loopback.

1. Make loopback, one worker and explicit safe settings mandatory defaults.
2. Require coherent HTTP/WebSocket authorization, Origin handling, payload limits and error redaction.
3. Replace direct client paths with fixed import/export roots and opaque references; include canonical containment and symlink protection.
4. Add a single-flight execution gate, bounded queue/job model, timeout/cancel strategy and resource checks outside the protected core.
5. Exercise only bounded synthetic negative tests.

**Exit evidence:** external binding fails closed when safeguards are incomplete; no local path disclosure or arbitrary writes; no uncontrolled concurrent engine work.

### Gate 4 — Transactional private data lifecycle

**Objective:** replace fragmented cleartext JSON authority only with a complete lifecycle design.

1. Specify entity relationships, opaque IDs, migrations, encryption/key custody, retention, audit and recovery before writing storage code.
2. Implement and test a transactional data authority on synthetic copies, including concurrency, crash, disk-full and permission failure paths.
3. Use a journaled deletion protocol with resume/retry and a restore drill into an isolated staging root.
4. Migrate real existing data only under a separately approved dry-run, backup and review gate.

**Exit evidence:** complete synthetic migration/recovery/erasure evidence; no secret material in repository, logs or manifests; approved data owner and key custody.

### Gate 5 — Truthful contracts and adapters

**Objective:** create a versioned boundary around an unchanged core.

1. Define contract schemas for validated inputs, opaque identifiers, policy versions, idempotency, typed errors, unchanged native result and additive projection.
2. Validate all unknown versions/options fail closed; ensure no platform metadata reaches the core.
3. Build a transport-neutral local adapter only after the contract and storage gates are green.
4. Prove direct-core and adapter-native results match the golden baseline.

**Exit evidence:** contract conformance, native-result preservation, no `app/algorithms/**` diff, no live external connection.

### Gate 6 — Deferred bus and external integration decision

**Objective:** decide whether the existing bus is useful after—not before—the module contract exists.

1. Publish an ADR that selects either `not used` or a narrowly local edge-only bus role.
2. If retained, add producer authentication, ACL enforcement, quarantine, durable idempotency, retention, backup and restore; a self-hash is insufficient.
3. Prohibit network-file-share SQLite, direct bus-to-engine calls and bus substitution for platform identity/job authority.
4. Test external integration only in a synthetic serialized harness after all earlier gates are approved.

**Exit evidence:** explicit transport decision; default remains disabled unless all required authority and recovery properties have been independently verified.

### Gate 7 — Release engineering and operator experience

**Objective:** create a reproducible, safe deliverable only after the above boundaries are stable.

1. Consolidate packaging around an allowlist, locked dependency sets and a single interpreter policy.
2. Generate SBOM, provenance/license records, vulnerability evidence, signed content manifest and rollback artifact.
3. Make readiness distinct from liveness and include only redacted technical state.
4. Improve browser security/accessibility and CLI/PowerShell safety with contract and browser tests, not broad cosmetic rewrites.

**Exit evidence:** clean reproducible build; CI gate matrix; recovery/rollback proof; explicit release approval.

## 6. Non-negotiable sequencing constraints

| Constraint | Rationale |
|---|---|
| No engine semantic change before Gate 2 | Core outputs are not yet characterized and the current environment has documented OOM/native-failure history. |
| No external bind before Gate 3 | Current APIs include path, destructive and unauthenticated WebSocket risks. |
| No real or identifiable client data before Gate 4 | Cleartext persistence, browser state, logs, retention, encryption and recoverable erasure are incomplete. |
| No Radiquant/Lovable/bus wiring before Gate 5 and a dedicated Gate 6 decision | The current bus is intentionally disconnected and does not supply platform-level identity, authorization or producer authenticity. |
| No multiworker persistence before transactional authority | JSON whole-file replacement cannot guarantee cross-process consistency. |
| No release/package claim before Gate 7 | Dependency locks, license/provenance, CI, SBOM and immutable build evidence are absent. |

## 7. Optimization principles

1. Prefer bounded, additive adapters over replacing the calculation core.
2. Make policies and contracts executable before optimizing performance or UX.
3. Optimize measured peak memory/commit behavior, not only free RAM or nominal GPU memory.
4. Replace file paths with opaque references at every boundary.
5. Treat privacy, deletion and recovery as one lifecycle, not separate endpoint features.
6. Keep standalone offline operation viable and separate from future platform authority.
7. Use synthetic fixtures and isolated roots for every new test gate.
8. Require independent review after every gate that changes a security, privacy, authority or core-semantic boundary.

## 8. Approval request

The recommended first approved action is Gate 0 only: a hash-bound, current-`main` repository/SSOT checkpoint with no product-code, runtime-data or integration changes. All later gates remain proposals pending explicit approval.
