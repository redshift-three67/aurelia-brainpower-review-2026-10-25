# Operator Workbench Freeze-v5 Review Remediation and Freeze-v6 Implementation Plan

> **For Hermes:** Execute task-by-task with conservative RED→GREEN microgates. Do not commit, push, back up, or touch protected ports 8000/8090. Every repository patch invalidates Freeze v5 and requires Freeze v6 plus two new reviews.

**Goal:** Close every Freeze-v5 P1–P3 finding with production-bound behavioral evidence and produce a complete drift-free Freeze v6.

**Architecture:** Consolidate the two independent v5 reviews by root cause, not finding count. Security boundaries move to one shared composition root; browser lifecycle actions use explicit single-flight/generation tokens; long-running worker and persistence transitions acquire the authority lock at their final boundary; cross-process file stores use process locks; read and mutation traffic receive separate budgets.

**Tech Stack:** FastAPI, Pydantic, vanilla JavaScript, Python multiprocessing/threading, file-backed runtime state, pytest, Node VM contracts, Playwright.

**Status:** IN ARBEIT / NO-GO

---

## 1. Rejected freeze evidence

- Freeze v5: `docs/reviews/2026-07-20-workbench-remediation-technical-freeze-v5.sha256`
- Freeze SHA-256: `8d4615f6718cb27e7159212fe142c4b544a7c2c05d7a4837b7186295d4dd9078`
- Review 1: `docs/reviews/2026-07-20-workbench-remediation-technical-review-v5-1.md`
  - byte-exact SHA-256: `2882f555479f96917942a94ca338dce5ba52233d0c3d02fbb9253ef645a28591`
  - `REQUEST CHANGES`, P0=0/P1=7/P2=8/P3=2
- Review 2: `docs/reviews/2026-07-20-workbench-remediation-technical-review-v5-2.md`
  - byte-exact SHA-256: `6b945653154a06e82d53094a0cb1437d0599019413305393d6393d513ec74f84`
  - `REQUEST CHANGES`, P0=0/P1=4/P2=5/P3=1

Both reviews verified branch, HEAD, Freeze SHA, aggregate, 47/47 file hashes and exact 48-path scope at start and end with zero drift. Freeze v5 is permanently superseded.

## 2. Consolidated cause-to-gate map

| Gate | Consolidated findings | Required production boundary |
|---|---|---|
| V6-A | R1 F-01/F-12; R2 Auth P1 | One API-key/session authority for reports, workbench persistence, scan and harmonization; no internal report paths in responses; browser session uses HttpOnly cookie, never source/localStorage |
| V6-B | R1 F-02/F-04; R2 harmonization/duration P1 | Browser and server harmonization single-flight; bounded duration factor; owner/tenant concurrent-job reservation |
| V6-C | R1 F-03/F-08; R2 preview/New Case P1/P2 | Reset-in-progress mutation fence; explicitly partial teardown semantics; preview selection token; visible accessible errors and safe action binding |
| V6-D | R1 F-05; R2 worker domain gaps | Selected hardware paths run concurrently under one wall-clock pulse deadline; each selected path begins before deadline and remains cooperatively cancellable |
| V6-E | R1 F-06; R2 test-domain P2 | Final status load→decision→save→event under one job lock; no completed event unless persisted authority is completed; deterministic blocked-boundary race test |
| V6-F | R1 F-07/F-10; R2 scan snapshot P2 | Durable scan PID/group/owner/log/artifact registration and conservative restart recovery; snapshot mutation serialized under job/service lock; real restart and parallel-poll tests |
| V6-G | R1 F-09; R2 process-store P2 | Draft/template load→modify→replace under process lock; independent-process lost-update tests |
| V6-H | R1 F-11 | Separate read and mutation budgets; safe polls/bootstrap remain usable; expensive report traversal has bounded/cached budget |
| V6-I | R1 F-13/F-14/F-16; R2 DOM scrub P2 | Empty first-screen PII; full Review/Mini/Group DOM scrub; calendar-valid birth date; HTML max values synchronized with backend |
| V6-J | R1 F-17 | Reciprocal workflow tab/panel ARIA IDs and `aria-labelledby` |
| V6-K | R1 F-15; R2 evidence P2/P3 | Replace token/fake-domain claims with real browser/process/race evidence and precisely bounded documentation claims |

## 3. Execution tasks

### Task 1: Preserve and supersede Freeze v5

**Files:**
- Preserve: both v5 review reports listed above
- Create: this plan

**Steps:**
1. Copy each report byte-for-byte from the Hermes delegation artifact.
2. Verify source and destination SHA-256 equality.
3. Record v5 as `REQUEST CHANGES / SUPERSEDED`; never rewrite its manifest.
4. Verify `git diff --check`.

### Task 2: Bound harmonization and enforce single-flight (V6-B)

**Files:**
- Modify: `apps/web/contracts.py`
- Modify: `apps/web/static/workbench-state.js`
- Modify: `apps/web/static/app.js`
- Modify: `apps/web/static/index.html`
- Modify: harmonization start service/router boundary
- Test: `tests/test_web_contracts.py`
- Test: `tests/test_workbench_review_regressions.py`
- Test: `tests/browser/workbench.spec.js`

**RED contracts:**
1. `duration_factor` above the supported set/range is rejected before process start.
2. Two rapid clicks produce exactly one request and one poll authority.
3. A second server start for the same owner/tenant while active is rejected atomically.
4. Startbutton is disabled during start and active run, then restored only after terminal state/reset.

### Task 3: Unify authentication and public report shape (V6-A)

**Files:**
- Modify: `apps/web/security.py`
- Modify: `apps/web/main.py`
- Modify: `apps/web/workbench.py`
- Modify: `apps/web/reports.py`
- Modify: `apps/web/static/workbench-api.js`
- Modify: `apps/web/static/index.html`
- Test: `tests/test_web_shell.py`
- Test: `tests/test_web_catalog_client_view.py`
- Test: browser auth scenario

**RED contracts:**
1. With API key configured, reports, preview, file, draft, template and trace reads return 401 without valid session/header.
2. Report responses never contain `_root_path`, `_full_path` or absolute host paths.
3. Login endpoint accepts the configured key, creates a random server-held session and sets Secure-where-applicable, HttpOnly, SameSite=Strict cookie.
4. Browser uses the cookie session and never persists or embeds the key.
5. Logout/restart invalidates the session fail-closed.

### Task 4: Reset/preview lifecycle authority (V6-C)

**Files:**
- Modify: `apps/web/static/app.js`
- Modify: `apps/web/static/workbench-api.js`
- Modify: `apps/web/static/workbench-state.js`
- Test: `tests/browser/workbench.spec.js`

**RED contracts:**
1. A/B preview completion in either order binds only the last explicit selection.
2. Preview failure clears/deactivates actionable binding and reports through `aria-live`.
3. No mutation may begin while `resetInProgress` is true.
4. If scan stop succeeds and harmonization stop fails, UI reports explicit partial teardown, clears the stopped scan authority, retains the still-running harmonization authority and does not claim atomic reset.
5. Delayed bootstrap responses from every loader are generation-checked.

### Task 5: Worker terminal and hardware concurrency (V6-D/V6-E)

**Files:**
- Modify: `services/hardware_modulation.py`
- Modify: `services/harmonization_worker.py`
- Test: `tests/test_harmonization_worker_pulse_pause_execution.py`
- Test: `tests/test_harmonization_worker_stop.py`

**RED contracts:**
1. CPU/GPU/RAM selections begin concurrently and each sees an initially live shared predicate.
2. Stop/deadline causes all futures to converge within a bounded grace period.
3. Stop injected exactly after final precheck but before terminal commit yields persisted `stopped` and no `completed` event.
4. Completed event is emitted only from the persisted completed authority.

### Task 6: Durable and serialized scan authority (V6-F)

**Files:**
- Modify: `apps/web/scan_jobs.py`
- Test: `tests/test_web_scan_jobs.py`
- Test: `tests/test_web_scan_job_ownership.py`

**RED contracts:**
1. Start persists job ID, PID/group, owner, command, log paths and artifact authority atomically.
2. A fresh service reconstructs a running job conservatively and can status/stop it.
3. Missing/reused PID identity fails closed rather than signaling an unrelated process.
4. Two parallel snapshots cannot regress offsets, stages or progress.
5. Real Windows parent/child restart-stop test proves both processes terminate.

### Task 7: Cross-process runtime writes (V6-G)

**Files:**
- Modify: `apps/web/workbench_runtime.py`
- Test: `tests/test_web_workbench_runtime.py`

**RED contracts:**
1. Independent processes saving distinct templates preserve both.
2. Draft writes are process-serialized and never expose partial JSON.
3. Delete-vs-save has a deterministic documented winner under the same lock.

### Task 8: Separate read/mutation budgets (V6-H)

**Files:**
- Modify: `apps/web/security.py`
- Modify: `apps/web/main.py`
- Modify: `apps/web/reports.py` if cache boundary is required
- Test: `tests/test_web_shell.py`

**RED contracts:**
1. 61 read-only bootstrap GETs do not consume the 60-request mutation budget.
2. The 61st mutation remains 429.
3. Expensive report-list reads have a separate bounded budget/cache and cannot trigger unbounded parallel root traversal.
4. Safe per-job polling remains observable without starving mutations.

### Task 9: Privacy, validation and HTML parity (V6-I)

**Files:**
- Modify: `apps/web/static/index.html`
- Modify: `apps/web/static/app.js`
- Modify: `apps/web/contracts.py`
- Test: `tests/test_web_contracts.py`
- Test: `tests/browser/workbench.spec.js`

**RED contracts:**
1. Fresh HTML contains no prefilled person-like identity/focus values.
2. New Case clears Review cards, mini snapshot and all group/context/policy status carriers.
3. Impossible dates such as `31022024` and `00000000` are rejected; leap dates are handled correctly.
4. Frequency/impulse/pause input maxima equal backend limits.

### Task 10: Reciprocal workflow ARIA (V6-J)

**Files:**
- Modify: `apps/web/static/workflow-stepping.js`
- Modify: `apps/web/static/workflow-stepping.html`
- Test: `tests/test_workflow_stepping_runtime.py`

**RED contract:** Every generated tab has stable ID and `aria-controls`; every panel has matching `aria-labelledby`.

### Task 11: Evidence correction and regression ladder (V6-K)

**Files:**
- Update: v5/v6 remediation plans only before final broad run
- Include: v5 manifest and both complete v5 review reports in v6 scope

**Required order:**
1. New review-regression tests.
2. Neighboring feature suites.
3. Combined affected matrix.
4. Full `pytest tests -q` on final candidate bytes.
5. JS checks, `py_compile`, `git diff --check`.
6. Port precheck; isolated Playwright run on 8765; stop and verify cleanup.
7. Remove generated `node_modules`/`test-results` only.
8. Create Freeze v6 with exact dirty scope and unambiguous path-sorted LF aggregate.
9. Verify every hash, aggregate and scope population independently.
10. Dispatch two independent read-only reviewers; no repository writes while they run.

## 4. Release gates

Freeze v6 remains NO-GO unless both independent reviews return `APPROVE` with `P0=P1=P2=P3=0`, identical start/end branch/HEAD/freeze/hash/population and zero drift. Only then may gate/status documents be updated, separately frozen and independently reviewed. The external post-state shadow copy is prohibited until those documentation reviews also approve.

## 5. Implementation status before Freeze v6

All V6-A through V6-J remediation blocks are implemented with focused regression evidence. The final candidate includes:

- one API-key/session authority for reports, report files/previews, workbench persistence and group persistence;
- server-held restart-scoped browser sessions using HttpOnly, SameSite=Strict cookies, explicit logout and constant-time key comparison;
- public report payloads without `_root_path` or `_full_path`;
- app-scoped, tenant-bound report catalogs with a bounded TTL and a single-flight cache lock;
- browser and server single-flight harmonization, bounded request values and owner/tenant active-job conflict handling;
- generation/request-token protection for preview, registry, health, sources, hardware, reports, drafts and group bootstrap loaders;
- an explicit New-Case mutation fence and truthful partial teardown when only one of two server jobs stops;
- parallel hardware paths with bounded future convergence and explicit overrun failure;
- stop-aware cycle/terminal commits, including the exact stop-after-load-before-save regression boundary;
- atomic, fsynced and process-locked draft/template/run-trace persistence, fail-closed corrupt JSON handling, direct-reader partial-JSON evidence and documented create-vs-delete identity semantics;
- durable scan registration with PID, process creation identity, process-group identity, owner, logs, cursors, progress and artifacts; restart reconstruction; PID-reuse fail-closed handling; process-tree stop; and cross-instance snapshot serialization;
- separate mutation, ordinary-read, report-read and polling rate-limit buckets;
- neutral privacy defaults, complete New-Case DOM scrub, calendar-date validation and reciprocal workflow ARIA relationships.

Pre-final remediation evidence included `133 passed` in the combined affected matrix, `15 passed` for runtime persistence, `12 passed` for scan jobs, `9 passed` for pulse/pause execution and `14 passed` in Playwright. The final broad ladder below must be rerun after this status update and before hashing; only those final runs bind the Freeze-v6 candidate.
