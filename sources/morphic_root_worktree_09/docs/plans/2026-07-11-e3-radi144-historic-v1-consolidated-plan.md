# E3 vector integration and harmonization parity plan

> **For Hermes:** Execute only one approved gate at a time. Do not commit or push without explicit user approval.

**Goal:** Add only verified historic-Morphic capabilities to the current Workbench without changing the default Top-N scan output, then restore the proven impulse/pause sequence as a separate harmonization-parity gate.

**Architecture:** Keep vector effects separate from the existing `top3-scan` → `multiplex-scan` contract. A new value is accepted only with an explicit opt-in and must have a default-disabled equivalence test. Harmonization parity is independent: it consumes an already completed, redacted scan-result sequence and must not change scan scoring.

**Evidence reviewed (read-only):**
- Historic launcher: `C:\Users\Hubert111\Documents\Radimorphic\Morphic_Engine_V1\Run-MultiplexScan.ps1`.
- Historic vector encoder: `C:\Users\Hubert111\Documents\Radimorphic\Morphic_Engine_V1\services\analysis_service.py:33-61`.
- Historic profile encoder: `C:\Users\Hubert111\Documents\Radimorphic\Morphic_Engine_V1\core\profiles\profile.py:16-125`.
- Current worker: `services/harmonization_worker.py:341-483`.

---

## Verified consolidation

| Area | Historic fact | Current state | Plan consequence |
|---|---|---|---|
| Planet type | Single-profile PowerShell launcher forwards `--planet-type`; encoder appends `planet_to_rate` to the client-rate vector. | Web Top-N contract has no proven planet opt-in. | First score-affecting vector candidate; reuse V1's existing `planet_to_rate`, never the Radi144 sine formula. |
| Planet type in historic Top-N | `Run-MultiplexScan.ps1` builds a separate Top-N argument list without `--planet-type`. | No current Web Top-N support. | Do not claim historic Top-N parity. Add only after default command-equivalence and opted-in effect tests. |
| Image vector | Encoder supports `image_signature` and optional focus-image rates. | Historic PowerShell Multiplex workflow constructs `ClientProfile(..., image_signature=None)`; productive image input in that workflow is not verified. | Do not treat it as a proven historic workflow feature. Keep current local-path image behavior; analyse its dedicated active path separately. |
| Classic harmonization | Reads completed multiplex JSON; collects items; retains high/medium priority; deduplicates by label at maximum score; limits to 20; repeats sequence within `factor × 21 min`; sleeps exactly pulse then pause for each item. | Worker persists `pulse_seconds`, `pause_seconds`, `duration_factor`, and `solfeggio_base` but its loop currently runs a fixed one-second hardware cycle and ignores pulse/pause segmentation. | This is a real functional parity gap. Treat it as H1, independent of E3 scoring. |

## Invariants for every gate

1. Default Web Top-N request, CLI invocation, score ordering, report content, and generated artifact format remain unchanged.
2. No Radi144 formula is copied into the V1 scoring path.
3. No raw image bytes, birth time, coordinate, group-member, or optional-context data enters reports, manifests, or runtime traces unless a dedicated privacy gate permits it.
4. The historic priority sequence is derived only from the completed scan result; it must never trigger a new scan or mutate scores.
5. Use synthetic test data only. Do not open or alter any `Benutzer_Archive__ws-*` artifacts.

---

## Gate E3.1: Planet-type contract and default equivalence

**Objective:** Carry one explicit planet type through the Web → launcher → Top-N CLI path while keeping the default command byte-for-byte equivalent.

**Files:**
- Modify: `apps/web/contracts.py`, `apps/web/launcher.py`, `apps/cli/commands/scan.py`, `apps/web/static/index.html`, `apps/web/static/app.js`
- Create/modify tests: `tests/test_web_contracts.py`, `tests/test_topn_cli_phase1_options.py`, `tests/test_workbench_scan_gates_js.py`

### Tasks

1. Write a RED test that the default Web request produces the existing Top-N CLI argument sequence exactly.
2. Write a RED test that a missing opt-in discards any planet text and that enabled planet text appends exactly one validated `--planet-type` pair.
3. Define a finite, documented V1 planet vocabulary based on the existing CLI help: `Mars`, `Venus`, `Sonne`, `Saturn`, `Neptun`; reject unknown values rather than silently hashing free text.
4. Add an unchecked, explicitly labelled Web opt-in. Do not preselect a planet and do not include it in context-draft persistence.
5. Forward the option through the Web request and launcher only when the opt-in is true.
6. Add the accepted CLI option to the Top-N path and construct the existing `ClientProfile.planet_type` there.
7. Run RED/GREEN focused tests, `node --check apps/web/static/app.js`, full `pytest tests -q`, and `git diff --check`.

**Acceptance:** An omitted opt-in has identical CLI arguments and identical regression-fixture results. An enabled synthetic planet produces a reproducible but intentionally different vector trace, labelled `planet_type`.

## Gate E3.2: Image-path audit, not formula migration

**Objective:** Establish the exact active V1 image-path behavior before expanding it.

**Files:**
- Read first: `apps/cli/workflow/step03_signature.py`, `apps/cli/workflow/orchestrator.py`, `apps/web/analyze.py`, `services/analysis_service.py`
- Create test only if a missing active-path contract is found.

### Tasks

1. Trace local `.jpg`/`.jpeg` input from Web form to its active V1 signature computation.
2. Compare only V1's existing image derivation with the historic encoder contract; do not import Radi144's SHA/RGB/entropy algorithm.
3. Add a synthetic-image determinism test only after the active path is identified.
4. Document whether image input is already score-effective, workflow-only, or display-only.

**Acceptance:** The result labels the actual source and effect accurately. No new image upload, image persistence, or scoring formula is introduced.

## Gate H1.1: Pure harmonization-sequence planner

**Objective:** Recreate the historic sequence-selection semantics as a pure, testable planner with no worker or hardware side effect.

**Files:**
- Create: `core/harmonization/sequence_planner.py`
- Create: `tests/test_harmonization_sequence_planner.py`

### Tasks

1. Write RED tests with synthetic scan items for: supported result shapes, high/medium selection, threshold fallback, score-descending order, label deduplication retaining maximum score, top-20 limit, and round calculation.
2. Implement a pure function returning a redacted sequence, counts, planned duration, and rejected-item reasons.
3. Verify it consumes neither client identity nor raw export paths.
4. Run focused tests and full suite.

**Acceptance:** For the same synthetic result data and timing configuration, the planned item order and total duration are deterministic and match the historic PowerShell rules.

## Gate H1.2: Worker pulse/pause execution parity

**Objective:** Make the persisted pulse/pause values actual execution semantics while preserving stop behavior and job recovery.

**Files:**
- Modify: `services/harmonization_worker.py:341-483`
- Modify: `apps/web/harmonization.py`
- Modify/create tests: `tests/test_harmonization_worker_pulse_pause.py`, `tests/test_harmonization_worker_stop.py`

### Tasks

1. Write RED tests with a fake clock and fake hardware adapter: one item must execute an impulse segment of exactly `pulse_seconds`, then a pause segment of exactly `pause_seconds`; pause must perform no hardware modulation.
2. Introduce explicit `phase` (`impulse`/`pause`) and item/cycle progress events; retain the current job fields for backward compatibility.
3. Execute only the H1.1 planner sequence; never use a single global target frequency as a substitute for scan-item semantics.
4. Test stop during impulse and stop during pause; no later segment may start.
5. Test reload/recovery from persisted job state before activating any long-running browser path.
6. Run focused tests, full suite, and `git diff --check`.

**Acceptance:** The worker finally honors persisted timing values and exposes an auditable phase trace. No score or ranking changes occur.

## Gate H1.3: Workbench binding and manual evidence

**Objective:** Bind a completed Web run to the H1 planner without exposing raw archive contents or claiming an untested physical effect.

**Files:**
- Modify: `apps/web/static/app.js`, `apps/web/static/workbench-api.js`, `apps/web/static/workbench-render.js`, `apps/web/static/index.html`
- Modify tests: `tests/test_workbench_*`, `tests/test_runtime_erasure_harmonization_dry_run.py`

### Tasks

1. Require a completed run reference and explicit operator start action.
2. Display sequence count, pulse, pause, planned duration, current phase, and stop action.
3. Keep client/context data out of the worker trace; send only the redacted planner sequence and job configuration.
4. Perform browser evidence: keyboard start/stop, phase transition, cancellation, refresh/reload, and 320px layout.
5. Perform Art.17 dry-run evidence against the new trace before any persistent production integration.

**Acceptance:** The Workbench faithfully represents an actual executing job state rather than a visual timer, and the default scan path remains unchanged.

## Decision order

1. Approve E3.1 first if a score-effective planet opt-in is the immediate priority.
2. Approve H1.1 next if restoring the historic impulse/pause behavior is the immediate priority; it is lower scoring risk and independently valuable.
3. Do not start E3.2 or H1.2 until the immediately preceding gate is green and reviewed.

**Verification baseline before any implementation:** timestamped hash-verified ShadowCopy; `git diff --check`; focused RED/GREEN tests; full `pytest tests -q`; JavaScript syntax checks for changed files; no commit/push without explicit approval.
