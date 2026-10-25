# Technical Production GO Freeze v4 Review Remediation and Freeze v5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close all seven Freeze v4 review finding clusters with fail-closed authority boundaries, then produce a fully verified Freeze v5 candidate for two independent zero-drift reviews.

**Architecture:** Central validators and durable-I/O primitives protect every path-derived authority before filesystem or lock access. Scan ownership becomes an exact tenant-and-operator scope while the existing `owner_id` field remains unchanged; harmonization reconciliation separates unlocked process-authority reads from revision-checked state commits; reports are served from one verified open handle. Freeze v4 remains immutable and rejected, and Freeze v5 becomes eligible only after final-byte verification and two clean reviews.

**Tech Stack:** Python 3.12, FastAPI/Starlette, Pydantic, pytest, durable JSON state, POSIX `openat`/`O_NOFOLLOW`, Windows `CreateFileW`/`FlushFileBuffers`, vanilla JavaScript, Node.js, Playwright, PowerShell 7, SHA-256 manifests.

---

## Change Control

- `docs/reviews/2026-07-22-technical-production-go-freeze-v4.md` and `docs/reviews/2026-07-22-technical-production-go-freeze-v4.sha256` are immutable rejected evidence. Do not edit or replace either file.
- The v4 manifest SHA-256 remains `4fd8759400cd6e774695172b192b9e5499e6324f203b1753ff4b6646af1b4aaf`; it identifies v4 only and cannot authorize v5 or a live start.
- The target is Freeze v5 after Tasks 1-7, the complete Task 8 verification ladder, and two independent reviews that each report start drift 0, end drift 0, and `P0=P1=P2=P3=0`.
- No commits are authorized. Do not run `git add`, `git commit`, `git reset`, `git clean`, checkout-based restoration, or broad staging at any point in this plan.
- Preserve unrelated dirty-worktree bytes. Use path-limited status and diff inspection only.
- Run every command from `C:\morphic_v1\.worktrees\operator-workbench-phase1` unless a step explicitly names `tests/browser` as its working directory.

## Reviewer Findings Mapping

The IDs below label the seven finding clusters supplied for this remediation; they do not invent reviewer severity or evidence files.

| Plan ID | Finding cluster | Closing task | Required proof |
|---|---|---:|---|
| RV4-01 | Job-ID path authority and incomplete argv redaction | 1 | One strict validator before every path/lock boundary; adversarial IDs create no files; short and dash-prefixed client values are redacted while flags remain visible |
| RV4-02 | Cross-tenant scan/runtime exposure | 2 | Collision-safe tenant/operator owner scope, exact checks on every access path, fail-closed legacy records, tenant-hashed Workbench stores |
| RV4-03 | Missing/overwritten run traces and live legacy analyze path | 3 | Insert-only trace creation for new/replay, missing terminal trace reconstruction, auth-sensitive optional UI sync, authenticated HTTP 410 tombstone |
| RV4-04 | Permissive harmonization records and stale lease reconciliation | 4 | Closed parser, fail-closed registry, unlocked authority read plus revision recheck, no start during get, stop wins races |
| RV4-05 | Browser releases unresolved scan authority | 5 | Unresolved statuses retain reservation and controls; terminal stop frees it; rollback failure clears only after confirmed absence |
| RV4-06 | Parent directories are created without durable directory-entry proof | 6 | Shared parent creation, per-component persistence, fail-closed Windows fallback, ordered fault tests, all authority call sites migrated |
| RV4-07 | Report catalog path re-resolution and response reopen races | 7 | Root-relative catalog identity, one safe handle for preview/download, no report `FileResponse`, swap/reparse/root-collision tests |

## Explicit Exclusions

- Do not infer a tenant from a bare legacy `owner_id`, operator ID, workspace ID, path, filename, process, or runtime root. Blank, ownerless, and old operator-only scan records remain forbidden and are not rewritten.
- Known harmonization legacy record shapes may be parsed only as specified in Task 4. Missing tenant/operator ownership remains unassigned and fail-closed; an active ownerless record reserves globally until authority proves a terminal state or a separately reviewed migration supplies ownership.
- Do not add aliases or compatibility execution for `/api/analyze`; its only supported behavior is the authenticated HTTP 410 tombstone.
- Do not add report-ID fallback lookup, path re-resolution after handle validation, or `FileResponse` for report content.
- Do not redesign CLI workflows, report formats, harmonization algorithms, browser styling, or unrelated stores.
- Task 8 ends at an accepted v5 review gate. Starting port 8765, writing a production-GO status, or updating `PROJECT_MEMORY` is a separate live gate after v5 acceptance.

## File Map

| Area | Primary responsibility |
|---|---|
| `apps/web/authority_ids.py` | Closed ASCII authority-ID validation used before route, persisted, path, and lock operations |
| `core/compliance/operator_context.py` | Collision-safe owner-scope derivation and exact scope assertion |
| `apps/web/workbench_runtime.py` | Tenant-hashed runtime root and insert-only/finalized run traces |
| `services/harmonization_worker.py` | Strict record parser and revision-safe expired-lease reconciliation |
| `apps/web/durable_io.py` | Durable per-component parent-directory creation and durable byte publication |
| `apps/web/report_handles.py` | Platform-specific root-relative report handle opening and lifecycle |
| `apps/web/static/app.js` | Unresolved scan reservation, refresh/stop controls, and optional trace sync |
| `docs/reviews/2026-07-22-technical-production-go-freeze-v5.*` | Final exact-byte v5 manifest and review contract |

### Task 1: Enforce Job-ID Path Authority and Structural Diagnostics Redaction

**Files:** Create `apps/web/authority_ids.py` and `tests/test_web_authority_ids.py`. Modify `apps/web/scan_jobs.py`, `apps/web/scan_live.py`, `apps/web/start_operations.py`, `apps/web/workbench_runtime.py`, `apps/web/workbench.py`, `apps/web/main.py`, `apps/web/scan_diagnostics.py`, `apps/web/harmonization.py`, `services/harmonization_worker.py`, and `services/harmonization_process_entry.py`. Extend `tests/test_web_scan_jobs.py`, `tests/test_web_scan_live_security.py`, `tests/test_web_scan_diagnostics.py`, `tests/test_web_workbench_runtime.py`, `tests/test_harmonization_worker_recovery.py`, `tests/test_harmonization_worker_pulse_pause.py`, and `tests/test_web_shell.py`.

- [ ] **RED:** Add parametrized containment tests for `..`, forward slash, backslash, `C:\absolute`, `/absolute`, `\\server\share`, `name:ads`, empty/whitespace, non-ASCII, NUL, and 129-character IDs. Spy on path, lock, open, and write functions and require zero calls after rejection. Add route, WebSocket, run-trace, persisted scan, persisted harmonization, and process-entry cases. Add diagnostics cases where client values are `Li` and `--private-value`, while `--focus`, `--birth-date`, and `--adaptive-limits` remain visible.

```powershell
& "C:\morphic_v1\.venv\Scripts\python.exe" -m pytest tests/test_web_authority_ids.py tests/test_web_scan_diagnostics.py tests/test_web_scan_jobs.py tests/test_web_scan_live_security.py tests/test_web_workbench_runtime.py tests/test_harmonization_worker_recovery.py tests/test_harmonization_worker_pulse_pause.py tests/test_web_shell.py -q
```

Expected RED: at least one adversarial ID reaches a path/lock call, and short or dash-prefixed client values remain visible in diagnostics.

- [ ] **Minimal GREEN:** Implement one shared validator accepting only 1-128 ASCII characters matching `[A-Za-z0-9][A-Za-z0-9_-]*`. Keep scan-start prefix checks (`scan-` or `harm-auth-`) and harmonization-start prefix checks (`harm_`) as additional creation rules. Validate route IDs before store calls, persisted IDs before derived paths, all scan/harmonization path and lock helpers at entry, WebSocket IDs before lookup, and run IDs before runtime-store locking. Invalid external IDs return controlled 422/4404 responses; unreadable persisted IDs raise the existing fail-closed authority error and never get sanitized into another filename.

- [ ] **Minimal GREEN:** Replace value-length and `startswith("--")` heuristics with argv-position classification. Preserve the interpreter/module/subcommand tokens; preserve value flags `--birth-date`, `--birth-place`, `--level`, `--export`, `--hardware-profile`, `--k-total`, `--top-k`, `--synergy-combos`, `--synergy-threshold`, `--top-n`, `--profile-template`, `--entropy-mode`, `--image`, `--planet-type`, and `--focus`; preserve boolean flags `--synergy` and `--adaptive-limits`; classify the two positional client names and every value following a value flag as sensitive even when one character long or beginning with `-`.

- [ ] **Focused verification:** Re-run the RED command and require zero failures, then run `& "C:\morphic_v1\.venv\Scripts\python.exe" -m py_compile apps/web/authority_ids.py apps/web/scan_jobs.py apps/web/scan_live.py apps/web/workbench_runtime.py services/harmonization_worker.py services/harmonization_process_entry.py` with exit 0.

- [ ] **Full verification:** Run `& "C:\morphic_v1\.venv\Scripts\python.exe" -m pytest tests -q`; require zero failures/errors and record counts for Task 8 comparison.

- [ ] **Review checkpoint:** Run `git status --short -- apps/web services/harmonization_worker.py services/harmonization_process_entry.py tests` and `git diff --check -- apps/web services/harmonization_worker.py services/harmonization_process_entry.py tests`. Inspect the path-limited diff and require validator use before every string-to-path/string-to-lock transition; do not stage or commit.

### Task 2: Bind Scan and Workbench State to the Exact Tenant and Operator

**Files:** Modify `core/compliance/operator_context.py`, `apps/web/main.py`, `apps/web/scan_jobs.py`, `apps/web/scan_live.py`, `apps/web/workbench.py`, `apps/web/workbench_runtime.py`, and `apps/web/start_operations.py`. Extend `tests/test_operator_context.py`, `tests/test_web_scan_job_ownership.py`, `tests/test_web_scan_live_security.py`, `tests/test_web_workbench_runtime.py`, and `tests/test_web_shell.py`.

- [ ] **RED:** Add collision tests for `(tenant="a:b", operator="c")` versus `(tenant="a", operator="b:c")`; same-operator/different-tenant REST status, results, stop, sync-trace, run-trace, replay, and WebSocket tests; blank and bare operator-only persisted owner tests; and Workbench draft/template/trace tests proving different tenants sharing one base root cannot see or overwrite each other. Assert raw tenant IDs are absent from directory names and `WorkbenchRuntimeStore(explicit_root)` without `tenant_id` still writes directly below `explicit_root`.

```powershell
& "C:\morphic_v1\.venv\Scripts\python.exe" -m pytest tests/test_operator_context.py tests/test_web_scan_job_ownership.py tests/test_web_scan_live_security.py tests/test_web_workbench_runtime.py tests/test_web_shell.py -q
```

Expected RED: the same operator in another tenant matches the old `owner_id`, and Workbench stores share `runtime/workbench`.

- [ ] **Minimal GREEN:** Add `operator_owner_scope(context)` as `owner-v1-` plus the full SHA-256 of canonical JSON `[tenant_id, operator_id]`; reject missing/blank components. Persist that value in the existing scan `owner_id` field without changing the scan schema. Add an exact assertion that accepts only that scope and use it for new starts, pending/completed replay, every scan REST route, WebSocket send revalidation, results, stop, sync-trace, and Workbench run-trace access.

- [ ] **Minimal GREEN:** Change `WorkbenchRuntimeStore(root, tenant_id=None)` so `None` preserves the exact explicit root, while a supplied nonblank tenant uses `root / ("tenant-v1-" + sha256(tenant_id UTF-8).hexdigest())` for draft, templates, locks, and run traces. Resolve `OperatorContext` before constructing the store in `create_app`, then pass `operator_context.tenant_id`. A supplied blank tenant is an error, not the unscoped mode.

- [ ] **Focused verification:** Re-run the RED command and require zero failures. Also run `& "C:\morphic_v1\.venv\Scripts\python.exe" -m pytest tests/test_start_operations.py tests/test_workbench_client_context_persistence.py -q` and require zero failures.

- [ ] **Full verification:** Run `& "C:\morphic_v1\.venv\Scripts\python.exe" -m pytest tests -q`; require zero failures/errors.

- [ ] **Review checkpoint:** Run `git diff --check -- core/compliance/operator_context.py apps/web/main.py apps/web/scan_jobs.py apps/web/scan_live.py apps/web/workbench.py apps/web/workbench_runtime.py apps/web/start_operations.py tests`. Inspect every comparison and prove no use of `operator_id`, `workspace_id`, delimiter concatenation, or legacy blank ownership can satisfy the new scan scope; do not stage or commit.

### Task 3: Make Run Traces Recoverable and Retire Legacy Analyze Execution

**Files:** Modify `apps/web/workbench_runtime.py`, `apps/web/main.py`, `apps/web/workbench.py`, `apps/web/analyze.py`, and `apps/web/static/app.js`. Extend `tests/test_web_workbench_runtime.py`, `tests/test_web_shell.py`, `tests/test_workbench_review_regressions.py`, and `tests/browser/workbench.spec.js`.

- [ ] **RED:** Add tests proving a replay creates a missing trace without changing an existing trace, terminal sync reconstructs and finalizes a missing trace, two ensure callers cannot overwrite first-writer fields, non-auth trace-sync errors do not downgrade a completed UI job, 401/403 still surface as auth pause, and `/api/analyze` returns 410 without importing or calling `apps.cli.workflow.orchestrator.run_workflow`.

```powershell
& "C:\morphic_v1\.venv\Scripts\python.exe" -m pytest tests/test_web_workbench_runtime.py tests/test_web_shell.py tests/test_workbench_review_regressions.py -q
```

Expected RED: replay has no trace, missing terminal sync returns 404, trace errors enter poll degradation, or `/api/analyze` reaches workflow execution.

- [ ] **Minimal GREEN:** Replace merge-style registration with `ensure_run_trace(run_id, seed)`: under the tenant store lock, return an existing entry byte-semantically unchanged or insert one new entry. Call it after both new and replayed scan authority is established. For terminal sync, insert a minimal nonterminal seed when absent and then use the existing one-time terminal finalizer; keep duplicate terminal finalization as 409.

- [ ] **Minimal GREEN:** In the browser, treat sync/load of run-trace data as optional for non-auth 404/409/5xx failures, but rethrow 401/403 so authentication remains fail-closed. Replace `/api/analyze` with an authenticated `JSONResponse(status_code=410, content={"detail":"legacy analyze endpoint retired; use /api/scan/jobs"})`; retain the route as a tombstone and remove all `run_workflow` imports/calls from it.

- [ ] **Focused verification:** Re-run the RED command, then run `node --check apps/web/static/app.js` and `& "C:\morphic_v1\.venv\Scripts\python.exe" -m py_compile apps/web/workbench_runtime.py apps/web/main.py apps/web/workbench.py apps/web/analyze.py`; require exit 0.

- [ ] **Full verification:** Run `& "C:\morphic_v1\.venv\Scripts\python.exe" -m pytest tests -q`; require zero failures/errors.

- [ ] **Review checkpoint:** Run `git diff --check -- apps/web/workbench_runtime.py apps/web/main.py apps/web/workbench.py apps/web/analyze.py apps/web/static/app.js tests/test_web_workbench_runtime.py tests/test_web_shell.py tests/test_workbench_review_regressions.py tests/browser/workbench.spec.js`. Verify replay never mutates an existing trace and `rg "run_workflow" apps/web/analyze.py` returns no match; do not stage or commit.

### Task 4: Parse Harmonization Records Strictly and Reconcile Expired Leases on Get

**Files:** Modify `services/harmonization_worker.py` and `apps/web/harmonization.py`. Create `tests/test_harmonization_worker_records.py`. Extend `tests/test_harmonization_worker_recovery.py`, `tests/test_harmonization_worker_stop.py`, `tests/test_web_harmonization_phase_snapshot.py`, and `tests/test_web_shell.py`.

- [ ] **RED:** Add table-driven record tests for unknown/missing fields, bool-as-int, nonfinite/out-of-range numbers, invalid status/phase/forced-status combinations, cycle/progress contradictions, filename/job-ID mismatch, malformed timestamps, invalid owner types, and mixed legacy fields. Add registry tests where one malformed `*.json` blocks active-job decisions. Add ordinary `WorkerHarmonizationService.get()` tests for expired starting/running authority, terminal authority, authority failure, and a barrier-controlled concurrent stop that changes the record between authority read and commit.

```powershell
& "C:\morphic_v1\.venv\Scripts\python.exe" -m pytest tests/test_harmonization_worker_records.py tests/test_harmonization_worker_recovery.py tests/test_harmonization_worker_stop.py tests/test_web_harmonization_phase_snapshot.py tests/test_web_shell.py -q
```

Expected RED: permissive dataclass construction accepts a malformed shape, ordinary get leaves an expired lease stale, or stale reconciliation overwrites stop.

- [ ] **Minimal GREEN:** Add one parser used by `load`, registry enumeration, replay, worker entry, get, stop, and recovery. Current schema v2 must contain exactly every persisted `HarmonizationJob` dataclass field. The only accepted legacy forms are unversioned or `schema_version == 1` records containing required fields `job_id`, `target_frequency`, `duration_minutes`, `intention`, `hardware_config`, `status`, `start_time`, `end_time`, `progress_percent`, `error_message`, `cycles_completed`, and `total_cycles`, plus only these shipped optional fields: `pulse_seconds`, `pause_seconds`, `duration_factor`, `solfeggio_base`, `report_id`, `workbench_mode`, `tenant_id`, `operator_id`, `worker_pid`, `worker_create_time`, `heartbeat_at`, `current_phase`, `authority_job_id`, and `forced_status`. Normalize omitted optional legacy fields to the dataclass defaults in memory; save only exact v2. Never derive missing ownership.

- [ ] **Minimal GREEN:** Enforce real finite numerics with bool rejected; nonnegative duration/factor/cycles; positive pulse, pause, target, and solfeggio values; progress in `[0,100]`; `cycles_completed <= total_cycles`; canonical IDs; string-keyed JSON-safe hardware config; valid optional ISO timestamps; statuses limited to `pending`, `starting`, `running`, `completed`, `stopped`, `error`, `interrupted`, and `authority_ambiguous`; and `forced_status` limited to `None` or `authority_ambiguous` with matching public status/phase. Any malformed registry member raises before a new start or reservation release.

- [ ] **Minimal GREEN:** On ordinary get, reconcile only the requested active record when its lease is expired. Under `_job_lock`, capture canonical record bytes/hash and authority ID; release the job lock; call authority `get` exactly once and never `start`; reacquire the job lock; reload and compare the captured revision before any write. Starting/running authority remains active. Terminal authority reconciles to completed/error only when already matching, otherwise to interrupted unless a stop marker/current stopped state wins. Authority uncertainty persists `authority_ambiguous`. A changed revision returns the newer state and never overwrites it.

- [ ] **Focused verification:** Re-run the RED command and `& "C:\morphic_v1\.venv\Scripts\python.exe" -m py_compile services/harmonization_worker.py apps/web/harmonization.py`; require exit 0 and zero failures.

- [ ] **Full verification:** Run `& "C:\morphic_v1\.venv\Scripts\python.exe" -m pytest tests -q`; require zero failures/errors.

- [ ] **Review checkpoint:** Run `git diff --check -- services/harmonization_worker.py apps/web/harmonization.py tests/test_harmonization_worker_records.py tests/test_harmonization_worker_recovery.py tests/test_harmonization_worker_stop.py tests/test_web_harmonization_phase_snapshot.py tests/test_web_shell.py`. Trace the lock order and prove no process-authority read occurs while `_job_lock` is held and no get path can start a worker; do not stage or commit.

### Task 5: Keep Unresolved Scan Authority Reserved in the Browser and Server

**Files:** Modify `apps/web/static/app.js`, `apps/web/static/index.html`, and `apps/web/scan_jobs.py`. Extend `tests/test_workbench_review_regressions.py`, `tests/test_workbench_dogfood_frontend_contracts.py`, `tests/test_web_scan_jobs.py`, and `tests/browser/workbench.spec.js`.

- [ ] **RED:** Add browser/harness cases for `authority_ambiguous`, `rollback_failed`, missing status, and literal `unknown`. Require `activeJobId` and active reservation to remain, start disabled, no sync-trace request, refresh enabled, and a visible stop control. Then return `stopped` on refresh/stop and require the reservation to clear. Add server tests proving `rollback_failed` remains unresolved on an ambiguous/failed authority probe and becomes `stopped` only after an authoritative inactive result, including restart recovery.

```powershell
& "C:\morphic_v1\.venv\Scripts\python.exe" -m pytest tests/test_workbench_review_regressions.py tests/test_workbench_dogfood_frontend_contracts.py tests/test_web_scan_jobs.py -q
```

Expected RED: the poller enters its generic terminal branch, enables start, disables refresh, or invokes trace finalization for an unresolved status; an absent rollback process still returns `rollback_failed`.

- [ ] **Minimal GREEN:** Define terminal scan statuses exactly as `completed`, `failed`, and `stopped`. Treat `starting`, `pending`, `running`, `authority_ambiguous`, `rollback_failed`, absent/non-string status, and every unknown value as an active reservation. Keep `activeJobId`, set `scanRunActive`, disable start, keep refresh and new `#scan-stop-button` enabled, display manual-control text, and skip results/trace finalization. The explicit stop action clears authority only after a terminal response; an unresolved response or error retains it.

- [ ] **Minimal GREEN:** In `LocalScanJobService.stop`, retain `rollback_failed` through every uncertain probe or convergence error. Publish `stopped` only after the same stable process-tree authority used by stop positively reports no active supervisor/group/job object, including a post-convergence recheck. Persist that transition under the job lock so a later browser refresh observes the terminal state.

- [ ] **Focused verification:** Re-run the RED command and `node --check apps/web/static/app.js`. With an isolated server on `127.0.0.1:8766`, run `npm test -- --grep "unresolved scan authority"` from `tests/browser`; require all selected tests to pass with zero retries.

- [ ] **Full verification:** Run `& "C:\morphic_v1\.venv\Scripts\python.exe" -m pytest tests -q`; require zero failures/errors. Run the complete Playwright matrix in Task 8 after all final bytes are present.

- [ ] **Review checkpoint:** Run `git diff --check -- apps/web/static/app.js apps/web/static/index.html apps/web/scan_jobs.py tests/test_workbench_review_regressions.py tests/test_workbench_dogfood_frontend_contracts.py tests/test_web_scan_jobs.py tests/browser/workbench.spec.js`. Verify the browser terminal set is closed and the server cannot clear rollback failure on numeric PID absence alone; do not stage or commit.

### Task 6: Make Authority Parent Directory Creation Durable

**Files:** Modify `apps/web/durable_io.py`, `apps/web/emf_authority.py`, `apps/web/start_operations.py`, `apps/web/scan_jobs.py`, `apps/web/workbench_runtime.py`, `core/compliance/operator_context.py`, `core/compliance/group_activation_handle_store.py`, `core/compliance/local_client_identity_store.py`, `core/compliance/local_vector_draft_store.py`, `core/compliance/runtime_manifest.py`, `core/compliance/run_manifest_persistence.py`, `core/compliance/progress_events.py`, `core/compliance/web_job_manifest.py`, `core/source_registry.py`, `services/harmonization_worker.py`, and `services/scan_process_gate.py`. Extend `tests/test_web_durable_io.py`, `tests/test_emf_enable_authority.py`, `tests/test_start_operations.py`, `tests/test_group_activation_handle_store.py`, `tests/test_local_client_identity_store.py`, `tests/test_local_vector_draft_store.py`, `tests/test_runtime_privacy_manifest.py`, `tests/test_run_manifest_persistence.py`, `tests/test_progress_events.py`, `tests/test_web_job_manifest.py`, and `tests/test_source_registry.py`.

- [ ] **RED:** Add ordered call-trace tests for a three-level missing parent tree, injected mkdir/open/fsync/FlushFileBuffers failures at each component, concurrent creators, an existing-file component, and symlink/reparse components. Require no deeper component after a fault and no authority file publication when parent durability is unproven. Add spies proving every listed authority call site reaches the shared helper rather than `Path.mkdir(parents=True, ...)`.

```powershell
& "C:\morphic_v1\.venv\Scripts\python.exe" -m pytest tests/test_web_durable_io.py tests/test_emf_enable_authority.py tests/test_start_operations.py tests/test_group_activation_handle_store.py tests/test_local_client_identity_store.py tests/test_local_vector_draft_store.py tests/test_runtime_privacy_manifest.py tests/test_run_manifest_persistence.py tests/test_progress_events.py tests/test_web_job_manifest.py tests/test_source_registry.py -q
```

Expected RED: nested directories appear through one non-durable `mkdir(parents=True)`, and injected directory flush failure does not stop publication.

- [ ] **Minimal GREEN:** Add `durable_mkdir_parents(path)` to `apps/web/durable_io.py`. Walk from the nearest existing ancestor one component at a time; reject non-directory and link/reparse components. On POSIX, `os.mkdir` one component, fsync the parent directory entry, open/fsync the new directory, then descend. Preserve owner-only modes where the current caller requires them.

- [ ] **Minimal GREEN:** On Windows, first probe directory-flush support on the nearest existing parent. If unsupported and any component is missing, raise `OSError("durable directory creation unavailable; pre-provision parent")` before the first mkdir; already-preprovisioned non-reparse directories remain usable. When supported, create one component, open parent and child directory handles with `CreateFileW` plus `FILE_FLAG_BACKUP_SEMANTICS` and `FILE_FLAG_OPEN_REPARSE_POINT`, reject reparse points, call `FlushFileBuffers` for the new parent entry and child directory, close both handles, then descend. Any create/open/flush/close failure is fail-closed and blocks authority publication.

- [ ] **Minimal GREEN:** Replace direct recursive parent creation in every file listed above. `durable_write_bytes` must call the helper before temporary creation, so all current and future durable-byte clients inherit the boundary. Lock-file and process-gate parent creation must call it explicitly before open.

- [ ] **Focused verification:** Re-run the RED command and `& "C:\morphic_v1\.venv\Scripts\python.exe" -m py_compile apps/web/durable_io.py apps/web/emf_authority.py apps/web/start_operations.py apps/web/scan_jobs.py apps/web/workbench_runtime.py services/harmonization_worker.py services/scan_process_gate.py`; require exit 0 and zero failures.

- [ ] **Full verification:** Run `& "C:\morphic_v1\.venv\Scripts\python.exe" -m pytest tests -q`; require zero failures/errors, with platform-specific skips only where the test marker documents unavailable Windows reparse creation.

- [ ] **Review checkpoint:** Run `git diff --check -- apps/web/durable_io.py apps/web/emf_authority.py apps/web/start_operations.py apps/web/scan_jobs.py apps/web/workbench_runtime.py core/compliance core/source_registry.py services/harmonization_worker.py services/scan_process_gate.py tests`. Run `rg "mkdir\(parents=True"` over the listed authority files and require no remaining direct recursive creation; do not stage or commit.

### Task 7: Serve Reports Through One Root-Bound Safe Handle

**Files:** Create `apps/web/report_handles.py` and `tests/test_web_report_handles.py`. Modify `apps/web/reports.py` and `apps/web/main.py`. Extend `tests/test_web_reports.py`, `tests/test_web_shell.py`, and `tests/test_workbench_report_dom_js.py`.

- [ ] **RED:** Add tests for two roots containing the same relative report path, roots with colliding names/case forms, final-file replacement after cataloging, file swap after safe open but before read, symlinked intermediate/final components, Windows junction/reparse components, non-regular files, and root deletion/replacement. Spy on open calls and require preview to read the verified handle and download to stream that same handle exactly once. Assert the report endpoint constructs no `FileResponse`.

```powershell
& "C:\morphic_v1\.venv\Scripts\python.exe" -m pytest tests/test_web_report_handles.py tests/test_web_reports.py tests/test_web_shell.py tests/test_workbench_report_dom_js.py -q
```

Expected RED: `_find` returns a path that is resolved/read again, `preview` uses `Path.read_text`, or the download response reopens through `FileResponse`.

- [ ] **Minimal GREEN:** Store each catalog entry as an opaque ID mapped to a canonical root identity plus validated relative path components; include the full root identity and relative path in the ID digest so equal relative paths in distinct roots cannot collide. Keep absolute paths private. Do not infer or search for an old ID after catalog refresh.

- [ ] **Minimal GREEN:** Add a context-managed safe opener. On POSIX, open the configured root directory, walk each component with `os.open(..., dir_fd=parent_fd, O_NOFOLLOW | O_DIRECTORY)` and open the final component once with `O_NOFOLLOW`; require a regular file by `fstat`. On Windows, open root and each component with `CreateFileW`, `FILE_FLAG_BACKUP_SEMANTICS` for directories, and `FILE_FLAG_OPEN_REPARSE_POINT`; reject `FILE_ATTRIBUTE_REPARSE_POINT`; use `GetFinalPathNameByHandleW` to require the final file path is below the final root-handle path; require a disk file; convert only the accepted final handle to a Python binary stream. Close every intermediate/failure handle exactly once.

- [ ] **Minimal GREEN:** Build preview content and metadata from that one handle using `fstat` and bounded reads. For downloads, return `StreamingResponse` whose iterator reads the already-open handle and closes it in `finally`; set media type, content length, and safe attachment headers from catalog/fstat metadata. The report endpoint must not pass a path to `FileResponse` or reopen after validation.

- [ ] **Focused verification:** Re-run the RED command and `& "C:\morphic_v1\.venv\Scripts\python.exe" -m py_compile apps/web/report_handles.py apps/web/reports.py apps/web/main.py`; require exit 0 and zero failures.

- [ ] **Full verification:** Run `& "C:\morphic_v1\.venv\Scripts\python.exe" -m pytest tests -q`; require zero failures/errors. Run the complete browser matrix in Task 8 to confirm preview/download behavior remains usable.

- [ ] **Review checkpoint:** Run `git diff --check -- apps/web/report_handles.py apps/web/reports.py apps/web/main.py tests/test_web_report_handles.py tests/test_web_reports.py tests/test_web_shell.py tests/test_workbench_report_dom_js.py`. Inspect handle ownership for every return/error/cancellation path and require no report-content `FileResponse`, `Path.read_text`, or second open; do not stage or commit.

### Task 8: Run Final Verification, Freeze v5, and Obtain Two Drift-Zero Reviews

**Files:** Create `docs/reviews/2026-07-22-technical-production-go-freeze-v5.sha256` and `docs/reviews/2026-07-22-technical-production-go-freeze-v5.md`. After freezing, create reviewer outputs `docs/reviews/2026-07-22-technical-production-go-review-v5-1.md` and `docs/reviews/2026-07-22-technical-production-go-review-v5-2.md`. Do not modify v4 files.

- [ ] **Final static verification:** Run the following against final candidate bytes and require every command to exit 0.

```powershell
& "C:\morphic_v1\.venv\Scripts\python.exe" -m py_compile apps/web/authority_ids.py apps/web/durable_io.py apps/web/emf_authority.py apps/web/start_operations.py apps/web/scan_jobs.py apps/web/scan_live.py apps/web/workbench_runtime.py apps/web/workbench.py apps/web/analyze.py apps/web/report_handles.py apps/web/reports.py apps/web/main.py core/compliance/operator_context.py services/harmonization_worker.py services/harmonization_process_entry.py services/scan_process_gate.py
node --check apps/web/static/app.js
node --check apps/web/static/workbench-api.js
node --check apps/web/static/workbench-render.js
node --check apps/web/static/workbench-state.js
node --check tests/browser/workbench.spec.js
node --check tests/browser/playwright.config.js
git diff --check
```

- [ ] **Final focused matrix:** Run the complete remediation matrix and require zero failures/errors.

```powershell
& "C:\morphic_v1\.venv\Scripts\python.exe" -m pytest tests/test_web_authority_ids.py tests/test_web_scan_diagnostics.py tests/test_operator_context.py tests/test_web_scan_job_ownership.py tests/test_web_scan_live_security.py tests/test_web_workbench_runtime.py tests/test_web_shell.py tests/test_harmonization_worker_records.py tests/test_harmonization_worker_recovery.py tests/test_harmonization_worker_stop.py tests/test_web_harmonization_phase_snapshot.py tests/test_workbench_review_regressions.py tests/test_workbench_dogfood_frontend_contracts.py tests/test_web_durable_io.py tests/test_start_operations.py tests/test_emf_enable_authority.py tests/test_web_report_handles.py tests/test_web_reports.py tests/test_workbench_report_dom_js.py -q
```

- [ ] **Final full Python suite:** Run `& "C:\morphic_v1\.venv\Scripts\python.exe" -m pytest tests -q`; require zero failures/errors and record exact passed, skipped, and duration values in the v5 record.

- [ ] **Final browser suite:** Verify ports 8090, 8765, and 8766 without altering their owners; require 8766 free. Run `npm ci` from `tests/browser`. Start only `& "C:\morphic_v1\.venv\Scripts\python.exe" -m uvicorn apps.web.main:app --host 127.0.0.1 --port 8766` with isolated temporary runtime/log roots, record its PID, require `/api/health` HTTP 200, then run `npm test` from `tests/browser` with `PLAYWRIGHT_BASE_URL=http://127.0.0.1:8766`. Require every test to pass with zero retries, stop only the recorded PID, and prove 8766 is free. Do not touch 8090 or start 8765.

- [ ] **Post-browser byte gate:** Remove only generated `tests/browser/node_modules/`, `tests/browser/test-results/`, and `tests/browser/playwright-report/` if this run created them. Re-run all static checks, the focused matrix, the full Python suite, and `git diff --check` if any scoped source/test/document byte changed after its prior successful command.

- [ ] **Build the v5 scope:** Form the union of all 90 paths from the immutable v4 manifest, both immutable v4 freeze files, this plan, every create/modify/test path named in Tasks 1-7, and every additional modified or untracked regular source/test/static path under `apps/`, `core/`, `services/`, `tools/`, and `tests/` present at freeze time. Exclude caches, `*.pyc`, runtime state, generated reports/logs, lock files, `node_modules`, Playwright output, `Benutzer_Archive__manual-acceptance`, the two v5 review outputs, and the v5 manifest/record themselves. Reject missing, duplicate, ignored-but-required, non-regular, symlink, junction, or reparse scope entries.

- [ ] **Write the v5 manifest:** Sort normalized repository-relative slash paths by ordinal string order. Write exactly `<64 lowercase hex><two spaces><path><LF>` for each exact file byte sequence, including a final LF. Recompute every entry and the manifest SHA-256 independently; require zero mismatches and record both the path count and manifest hash.

- [ ] **Write the v5 record:** Record branch/HEAD baseline, dirty-worktree preservation, explicit v4 rejection, scope algorithm and exclusions, manifest SHA-256, exact static/focused/full/browser results, Python/Node/npm/Playwright versions, isolated PID/port lifecycle, and the required review verdict. Compute and retain the final record SHA-256 externally because the record cannot contain its own hash. After this point, do not patch any v5-scoped byte.

- [ ] **Independent review 1:** Give reviewer 1 the v5 manifest/record and external record hash, v4 manifest/record, this plan, complete v5 scope, and diff against HEAD. Require independent start and end recomputation of the manifest file hash, record hash, every entry hash, ordering, uniqueness, path population, and exclusions, plus severity-ranked technical review of all seven closure contracts.

- [ ] **Independent review 2:** Give reviewer 2 the same immutable inputs without reviewer 1's conclusions. Require the same independent start/end drift and full technical checks.

- [ ] **Acceptance gate:** Both review files must contain exactly this verdict data and evidence supporting it:

```text
APPROVE
start drift: 0
end drift: 0
P0: 0
P1: 0
P2: 0
P3: 0
```

- [ ] **Failure rule:** Any hash drift, scope mismatch, test failure, browser failure, or P0-P3 finding makes v5 immutable/rejected evidence. Add a new failing regression, apply the smallest authorized correction, repeat the complete final ladder, and create v6; never patch v5 in place.

- [ ] **Separate live gate:** Only after both v5 reviews approve may a new, separately authorized live plan recompute accepted hashes, verify 8765 is free, start the exact reviewed command on 8765, run live acceptance, and write production status. This implementation plan does not authorize that start.
