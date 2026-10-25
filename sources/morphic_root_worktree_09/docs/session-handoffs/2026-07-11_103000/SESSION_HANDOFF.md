# Session Handoff — E3 vectors, H1 harmonization, and core-engine comparison

**Created:** 2026-07-11
**Worktree:** `C:\morphic_v1\.worktrees\operator-workbench-phase1`
**Branch:** `operator-workbench-phase1`
**Commit/push:** none in this session; do not commit or push without a fresh explicit user approval.

---

## 1. Exact continuation instruction

Use the current worktree, not the historic reference as an editing target. Read `CLAUDE.md`, this handoff, `docs/plans/2026-07-11-e3-radi144-historic-v1-consolidated-plan.md`, and the current git status before changing anything.

Continue with **H1.3**, not E3.2, unless the user changes priority:

1. Add a DOM/UI regression test for the current harmonization status panel fields:
   - `#harmonization-phase-label`
   - `#harmonization-lease-label`
   - interrupted/manual-action message.
2. Verify the persisted `current_phase`, `heartbeat_at`, and `interrupted` state reaches the existing poll endpoint and UI without exposing client data.
3. Run focused tests, `node --check apps/web/static/app.js`, then the full suite.
4. Only after all tests are green, start the web service on a **free** local port (normally `8001`; never disturb existing ports `8000` or `8090`) for manual browser evidence: start, impulse, pause, stop, refresh/reload, interrupted/lease indication, keyboard control, and 320px layout.
5. Do **not** auto-resume interrupted jobs. The present recovery contract intentionally marks only a stale dead-worker lease as `interrupted`; it never starts a second worker.

After H1.3 is fully green and manually evidenced, perform E3.2 as a read-only image-path audit before adding any image behavior.

---

## 2. Safety and design invariants

- The productive web score path is: `index.html` → `app.js:formScanPayload()` → web contract → `apps/web/launcher.py` → `scan top3-scan` → `field multiplex-scan` → `AnalysisService.encode_profile()`.
- E1 and E2 must remain separate from this score path. In particular, `clientContextDraftPayload()` must not be merged into `formScanPayload()`.
- E2 fields `birth_time`, `email`, and `notes` are local opt-in documentation context only; no scan/report/manifest/job-event use.
- E3 score effects are default disabled. A missing opt-in must preserve default command arguments, scores, report content, and artifacts.
- No Radi144 formula has been copied into V1 scoring. Do not import the Radi144 planet sine, geo heuristic, or SHA/RGB/entropy image formula.
- Do not touch `Benutzer_Archive__ws-*` artifacts.
- Do not read or expose credentials, tokens, passwords, or `.env` contents.
- Historic code under `C:\Users\Hubert111\Documents\Radimorphic\Morphic_Engine_V1` is read-only reference material.

---

## 3. Gate status

| Gate | Status | Verified result | Remaining |
|---|---|---|---|
| E1 client-context display | complete | Existing active client inputs visibly separated from inactive vector ideas; scan contract unchanged | none |
| E2 local opt-in context | complete | `birth_time`, `email`, `notes` saved only as consent-gated local draft context; not in scan payload | none |
| E3.1 planet opt-in | complete pending browser observation | Explicit disabled-by-default planet control; finite vocabulary; contract → launcher → Top-N forwarding | UI/browser evidence can be included in H1.3 visit |
| E3.2 image-path audit | pending | none | trace active V1 image path only; do not change formula |
| H1.1 planner | complete | pure deterministic top-20/high-medium/dedup/factor×21-min planner | not yet bound to completed scan results in UI |
| H1.2 pulse/pause worker | complete at focused-test level | actual impulse/pause phases, duration factor, worker lease/heartbeat, conservative interruption | no automatic resume by design |
| H1.3 workbench binding | in progress | snapshot/UI supports phase, lease, and interrupted/manual-action state | DOM test, full suite, manual browser evidence |

Current todo state:
- `h12`: completed
- `h13`: in progress
- `e32`: pending

---

## 4. E3.1 — planet-type implementation

### Implemented behavior

- `apps/web/contracts.py`
  - `planetary_vector_enabled: bool = False`
  - `planet_type: str = ""`
  - finite validated vocabulary: `Mars`, `Venus`, `Sonne`, `Saturn`, `Neptun`.
- `apps/web/launcher.py`
  - appends `--planet-type <value>` only when opt-in is true and a value is present.
- `apps/cli/commands/scan.py`
  - Top-N option adapter and command accept/forward `--planet-type`.
  - empty default produces no extra CLI argument.
- `apps/web/static/index.html`
  - disabled-by-default checkbox and planet selector.
- `apps/web/static/app.js`
  - `formScanPayload()` transports the opt-in and selected planet.

### Important constraints

- Do not state historic Multiplex/Top-N parity: the old `Run-MultiplexScan.ps1` did not forward `--planet-type` in its separate Top-N argument list.
- Use the existing V1 `planet_to_rate`, never Radi144’s sinus formula.
- Planet must not enter E2 draft persistence.

### Tests added/changed

- `tests/test_topn_cli_phase1_options.py`
- `tests/test_web_launcher.py`
- `tests/test_workbench_planetary_vector_dom.py`
- `tests/test_workbench_client_context_dom.py`

Known result after E3.1: `342 passed, 2 skipped in 116.99s` and JS syntax/diff checks passed.

---

## 5. H1.1 — deterministic harmonization planner

### New files

- `core/harmonization/sequence_planner.py`
- `tests/test_harmonization_sequence_planner.py`

### Implemented semantics

`plan_harmonization_sequence()`:

- accepts synthetic result items;
- retains only `hoch`/`mittel` priorities;
- derives priority from score where absent (`>0.5` high, `>0.2` medium);
- deduplicates by label while retaining the maximum score;
- score-sorts and caps at 20 items;
- determines rounds via `duration_factor × 21 × 60 / (pulse + pause)` with at least one round when items exist;
- returns items, rounds, total item count, planned seconds, rejected count.

`plan_harmonization_from_scan_export()` recognizes the supported historic-shaped containers:

- `sub_results.sections[].items`
- `sub_results.top`
- `nls_scores`
- `bat_subgroups[].items`

It is pure and must remain free of client identity, paths, filesystem reads, hardware, and score mutation.

Known result: `3 passed in 0.06s`; full suite later reached `344 passed, 2 skipped in 116.69s`.

---

## 6. H1.2 — worker pulse/pause and conservative recovery

### Modified file

- `services/harmonization_worker.py`

### Worker semantics now implemented

- One cycle is `pulse_seconds + pause_seconds`, not one second.
- Total planned worker duration is `duration_factor × 21 minutes`.
- Hardware modulation receives `duration_seconds=pulse_seconds`.
- Pause has no hardware modulation.
- JSONL phase events are emitted for `impulse` and `pause`.
- Persisted `current_phase` transitions:
  - `initializing`
  - `impulse`
  - `pause`
  - `interrupted`
- Job records persist `worker_pid`, `heartbeat_at`, and `current_phase`.
- Heartbeat/progress save after each completed cycle.

### Recovery semantics

`recover_interrupted_harmonization_jobs(lease_seconds=30)`:

- checks active/running jobs;
- marks only jobs with an expired/missing heartbeat **and** a non-alive worker PID as `interrupted`;
- emits `interrupted / expired_dead_worker_lease`;
- never resumes a job automatically;
- never changes a job whose worker PID is alive.

This is intentionally conservative. The JSON-file store still is not a generally authoritative multi-process, crash-safe runtime store; do not claim it is.

### Tests

- `tests/test_harmonization_worker_pulse_pause_execution.py`
- `tests/test_harmonization_worker_recovery.py`
- existing `tests/test_harmonization_worker_pulse_pause.py`
- existing `tests/test_harmonization_worker_stop.py`

Known results:

- focused H1.2 group: `10 passed in 0.44s`;
- full suite after H1.2: `346 passed, 2 skipped in 113.92s`.

---

## 7. H1.3 — currently in progress

### Current implementation

- `apps/web/harmonization.py:WorkerHarmonizationService._snapshot()` now exposes:
  - real persisted `phase`, falling back to generic phase only if absent;
  - `lease.worker_pid`;
  - `lease.heartbeat_at`;
  - `manual_action_required` when status is `interrupted`.
- `apps/web/static/index.html` now contains `#harmonization-lease-label`.
- `apps/web/static/app.js:pollHarmonizationJob()` renders:
  - phase;
  - progress;
  - cycles;
  - heartbeat (or `kein Heartbeat`);
  - existing error text, or `Manuelle Folgeaktion erforderlich` for interrupted jobs without a detailed error.
- Test added: `tests/test_web_harmonization_phase_snapshot.py`.

### Last focused validation after H1.3 changes

```text
3 passed in 0.27s
node --check apps/web/static/app.js: passed
py_compile apps/web/harmonization.py services/harmonization_worker.py: passed
git diff --check: passed (only existing CRLF warnings)
```

### Mandatory unfinished verification

A full suite has **not yet been rerun after the final H1.3 snapshot/UI changes**. Run it before any completion claim:

```bash
PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe -m pytest tests -q \
  && node --check apps/web/static/app.js \
  && git diff --check
```

Then add DOM/UI assertions and run a manual browser check on a free port. Do not use or disturb `8000` or `8090`.

---

## 8. Historic engine vs current engine — final findings

Read-only reference: `C:\Users\Hubert111\Documents\Radimorphic\Morphic_Engine_V1`.

### File-level divergence

| Area | Historic Python files | Current Python files | Shared paths | Changed shared paths |
|---|---:|---:|---:|---:|
| `core/` | 96 | 93 | 69 | 63 |
| `services/` | 17 | 9 | 9 | 8 |
| `apps/cli/` | 22 | 40 | 12 | 10 |

### High-value core differences

| Capability | Historic | Current | Decision |
|---|---|---|---|
| Base Copen rate logic | present | present | preserve |
| Name/date/place vector | present | present | preserve |
| Planet vector | present | present + controlled E3.1 web path | retain current gate |
| Image signature | encoder support | encoder support | audit active path in E3.2; no formula migration |
| Focus-image vector | present in historic `AnalysisService` | not active there | score-risk; separate future gate only |
| Birth-time vector | present in historic `AnalysisService` | not active in current productive analysis service | score-risk; keep E2 documentation-only until explicit gate |
| Modifier-scaled resonance map | present historic | not in current `AnalysisService` score map | high score risk; do not restore casually |
| Group pairwise resonance | historic service implementation | not active in current service | future preview-only adapter first |
| Adaptive HarmonizationEngine | historic has convergence result, finite numeric guards, momentum, optional feedback source | current engine simpler | separate deterministic comparison/hardening gate |
| Workbench/privacy/operator/tenant infrastructure | less comparable/historic | materially stronger current implementation | preserve current architecture |

### Core conclusion

The historic engine is broader in some score-affecting and mathematical features. The current system is stronger in Web contract boundaries, opt-in design, privacy, operator/tenant context, traceability, and testable operational controls. Do not copy historic functions wholesale. Compare and introduce one capability at a time with default equivalence tests.

---

## 9. Backups created during this session

All are external ShadowCopies under `E:\mprphic_v1_Backups\` and include a `SOURCE_MANIFEST.sha256`:

- `morphic_v1_showcopy_20260711_085220`
- `morphic_v1_showcopy_20260711_090332`
- `morphic_v1_showcopy_20260711_091201`
- `morphic_v1_showcopy_20260711_091853`
- `morphic_v1_showcopy_20260711_094342`
- `morphic_v1_showcopy_20260711_102412`

Earlier same-day E1/E2 backups also exist and are recorded in prior session context.

---

## 10. Current git state and scope warning

Current branch is `operator-workbench-phase1`.

The worktree was already substantially dirty before this session. `git status --short` currently includes many modified and untracked files beyond the exact H1/E3 work listed above. Do not reset, clean, stage all, commit all, or remove any `Benutzer_Archive__ws-*` directory.

The tracked diff currently reports `22 files changed, 1046 insertions(+), 253 deletions(-)` plus many existing untracked files. This aggregate is **not** attributable solely to this session.

`git diff --check` succeeds but emits known LF→CRLF warnings for pre-existing tracked files.

---

## 11. Copyable next-session prompt

```text
Continue in C:\morphic_v1\.worktrees\operator-workbench-phase1 on branch operator-workbench-phase1.

Read CLAUDE.md and docs/session-handoffs/2026-07-11_103000/SESSION_HANDOFF.md first. Do not commit, push, reset, clean, or touch Benutzer_Archive__ws-* artifacts. Treat C:\Users\Hubert111\Documents\Radimorphic\Morphic_Engine_V1 as read-only reference.

Resume H1.3 only: add DOM/UI regression coverage for persisted harmonization phase, lease/heartbeat and interrupted/manual-action state; then run the full suite, JS syntax check and diff check. Afterwards do manual browser evidence only on a free port (not 8000/8090). Do not automatically resume interrupted jobs. Default scan scores and E2 local-only context must remain unchanged.

After H1.3 is closed, next task is E3.2: read-only audit of the active V1 image path before any image-vector changes.
```
