# Operator Workbench Freeze-v3 Review Remediation and Freeze-v4 Implementation Plan

> **For Hermes:** Execute this plan in the active worktree task-by-task with conservative RED→GREEN microgates. Do not commit, push, back up, or touch protected ports 8000/8090. Every repository patch, including documentation, invalidates the current freeze candidate and requires a new freeze plus two new reviews.

> **Historical status:** Freeze v4 was created, reviewed without drift, and rejected by both reviewers. This plan is superseded for execution by `2026-07-19-workbench-freeze-v4-review-remediation-v5.md`; its earlier test totals are historical evidence only.

**Goal:** Convert every independent Freeze-v3 P1–P3 review finding into an executable behavioral gate, verify the current WIP remediation, close any remaining defect, and produce one complete Freeze v4 that receives two independent drift-free approvals with `P0=P1=P2=P3=0`.

**Architecture:** Bind scan outputs to artifacts emitted by the exact child process instead of filesystem recency; serialize terminal/stop state across processes; make New Case a server-aware lifecycle boundary; keep tenant, authentication and ownership authority consistent; and test browser/accessibility behavior through observable outcomes rather than source-token assertions. Treat all changes since Freeze v3 as unapproved WIP until the complete regression ladder and approval gates succeed.

**Tech Stack:** Python 3.11/FastAPI/Pydantic, multiprocessing and cross-platform file locking, vanilla JavaScript, pytest, Node VM tests, Playwright, Git/SHA-256 manifests.

---

## 1. Non-negotiable safety and change-control contract

- Active worktree: `C:\morphic_v1\.worktrees\operator-workbench-phase1`.
- Required branch: `operator-workbench-phase1`.
- Baseline/HEAD at plan creation: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`.
- Freeze v1, v2 and v3 are permanently superseded and cannot supply approval evidence.
- Freeze-v3 reviewed manifest SHA-256: `38ec0dd6fbace72a04910738e0750a8d7643ca2079ccf9d60d72cbb3188911b1`.
- Freeze-v3 reviewed scope aggregate: `185fce900e919d62473b78788c4b7e41a3c72c7232b91d9fae0f5e2038ea0358`.
- Protected live ports: 8000 and 8090. Do not stop, restart or repurpose them.
- Browser acceptance may use only a freshly verified free loopback port, currently planned as 8765.
- Use synthetic identities and synthetic artifacts only. Do not inspect or mutate real client exports for verification.
- No scoring, ranking, profile content, productive catalog, database activation or source-import semantics may change.
- No commit, push, external backup or post-state shadow copy before all required approvals.
- A failing freeze is retained as evidence and marked superseded; never overwrite or reuse it.
- Any post-freeze code, test or documentation patch requires a complete new manifest and two fresh reviews.

## 2. Consolidated finding-to-gate matrix

| ID | Priority | Consolidated Freeze-v3 finding | Required executable closure | Current WIP state; not approval evidence |
|---|---:|---|---|---|
| F3-01 | P1 | Results can bind to a later/concurrent same-client session and infer unproven sibling exports. | Return only artifacts captured from the exact process output; reject paths outside the job export root; adversarial later/concurrent-session test. | Implemented in `scan_jobs.py`/`main.py`; focused test passed, full post-final-patch verification pending. |
| F3-02 | P1 | New Case can orphan in-flight server work; stale bootstrap/async loaders can rehydrate cleared state. | Block reset during mutation; stop known scan/harmonization jobs before local clear; generation-check bootstrap and continuations; browser race tests. | WIP implemented in `app.js`, `workbench-api.js`, scan stop API/service; final regression ladder pending. |
| F3-03 | P1 | Pending harmonization stop can fail while UI falsely reports stopped. | Worker accepts pending/running stop; API returns authoritative status; UI renders stopped only on terminal confirmation. | WIP implemented; focused tests passed. |
| F3-04 | P1 | Durable stop marker has check→replace race; stale JSON can republish running. | Serialize marker and JSON replacement across processes; load reconciles marker; adversarial blocked-write race test. | WIP implemented with job lock and marker reconciliation; focused race test passed. |
| F3-05 | P1 | Stop is not prompt during long impulse/pause; durations are unbounded. | Bound pulse/pause contract; check before impulse; interrupt pause in short slices; prove no completed cycle is emitted for interrupted work. | WIP implemented with `le=5`, prechecks and interruptible pause; focused tests passed. |
| F3-06 | P1 | Scan status/results disclose identity-bearing commands/tails without uniform API-key and ownership gates. | Require `verify_api_key`; assert owner before status/results/stop disclosure or side effect; test configured key and foreign owner. | WIP implemented; focused ownership/auth tests passed. |
| F3-07 | P1 | Tenant authority splits when `runtime_dir` is supplied. | Resolve persisted context once against `runtime_path`; use that tenant for report roots/catalog/export/harmonization; test app A after environment changes to app B. | WIP implemented; focused tenant test passed. |
| F3-08 | P2 | Productive telemetry can regress export→phase2 and mark export complete during remaining profile analysis. | Model productive multi-profile chronology; prevent post-analysis stages until final Phase-2 profile; enforce monotonic stage IDs. | WIP implemented; focused telemetry tests passed. |
| F3-09 | P2 | New Case leaves sensitive result/report/group DOM and can permanently hide report preview. | Clear metrics, iframe `srcdoc`, title/meta/link, report state, group strength and controls; later preview must unhide/render; browser assertions. | WIP implemented; Playwright passed before final API-helper patch. |
| F3-10 | P2/P3 | Radio-card rerender detaches focus; Home/End omitted. | After selection, focus the newly rendered live selected node; support arrows/Home/End; behavior test active element and selected value. | WIP implemented; Playwright behavior passed. |
| F3-11 | P2 | Trace once-only finalization is process-local. | Cross-process lock around register/get/finalize; two spawned processes yield exactly one finalization and one conflict. | WIP implemented; spawned-process test passed. |
| F3-12 | P3 | Harmonization progress lacks complete progressbar semantics. | Add role/min/max/current and update `aria-valuenow` during polling/reset; DOM/behavior test. | WIP implemented; focused accessibility tests passed. |
| F3-13 | P2/P3 | Tests/docs overstate closure and use source-token/non-adversarial checks. | Replace or supplement tokens with adversarial behavior tests; reconcile documentation with actual evidence and remove contradictory claims. | Behavioral tests added; documentation reconciliation remains an explicit gate below. |

No finding is considered closed merely because the WIP column says implemented. Closure requires its specified tests, the full suite, browser acceptance, complete Freeze v4 and two zero-finding reviews of exactly that freeze.

---

### Task 0: Re-establish a verified post-patch baseline

**Objective:** Verify the last `workbench-api.js` compatibility patch and establish trustworthy current evidence before any further mutation.

**Files:**
- Verify: `apps/web/static/workbench-api.js`
- Test: `tests/test_workbench_dogfood_frontend_contracts.py`
- Test: `tests/test_workbench_render_js.py`

**Step 1: Confirm branch, HEAD and current scope**

Run:

```bash
cd /c/morphic_v1/.worktrees/operator-workbench-phase1
git branch --show-current
git rev-parse HEAD
git status --short
git diff --check
```

Expected:
- branch `operator-workbench-phase1`;
- HEAD `3271ff9366ab3fecb2a158913a0cc19ed6a06726` unless explicitly advanced later;
- existing WIP preserved;
- `git diff --check` exit 0, allowing only line-ending warnings.

**Step 2: Run the three previously failing Node contracts**

```bash
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 OPENBLAS_NUM_THREADS=1
/c/morphic_v1/.venv/Scripts/python.exe -m pytest \
  tests/test_workbench_dogfood_frontend_contracts.py::test_api_error_flattens_fastapi_validation_details \
  tests/test_workbench_render_js.py::test_scan_preview_rejects_non_success_http_response \
  tests/test_workbench_render_js.py::test_all_workbench_api_helpers_reject_non_success_responses -q
```

Expected: `3 passed`. If RED, change only the API helper compatibility boundary, then rerun this exact gate.

**Step 3: Re-run JavaScript syntax checks**

```bash
node --check apps/web/static/app.js
node --check apps/web/static/workbench-api.js
node --check apps/web/static/workbench-render.js
node --check apps/web/static/workbench-state.js
node --check apps/web/static/workflow-stepping.js
```

Expected: all exit 0.

**Step 4: Do not commit**

Record exact output in the eventual verification section. The user’s approval discipline overrides routine task-level commits.

---

### Task 1: Prove exact scan-run artifact attribution and process-tree cancellation

**Objective:** Close F3-01 and the scan half of F3-02 with behavioral evidence under concurrency and cancellation.

**Files:**
- Modify if RED: `apps/web/scan_jobs.py`
- Modify if RED: `apps/web/main.py`
- Test: `tests/test_web_scan_jobs.py`
- Test: `tests/test_workbench_review_regressions.py`
- Test: `tests/test_web_scan_job_ownership.py`

**Step 1: Add/inspect exact-artifact RED contracts**

The tests must prove:
1. job A emits artifact A;
2. a later/concurrent same-client artifact B exists and is newer;
3. results for A contain A only;
4. no inferred sibling path appears unless emitted and present;
5. a path outside the configured export root is ignored;
6. stdout paths are accumulated across partial polling reads and flushed at terminal state.

**Step 2: Run exact-attribution tests**

```bash
/c/morphic_v1/.venv/Scripts/python.exe -m pytest \
  tests/test_workbench_review_regressions.py -k 'artifact or result or historical' \
  tests/test_web_scan_jobs.py -k 'artifact or buffer or terminal' -q
```

Expected: all selected tests pass. A source-token assertion alone is insufficient.

**Step 3: Add/inspect process-tree stop contract**

Use a synthetic subprocess that spawns one child and writes only synthetic PIDs/markers under `tmp_path`. Stop the scan through `LocalScanJobService.stop()` and prove:
- parent terminates;
- spawned child cannot continue productive work;
- snapshot becomes `stopped`;
- repeated stop is idempotent;
- no real process or export path is touched.

Platform contract:
- Windows: new process group plus `taskkill /T /F`, with bounded fallback;
- POSIX test path: new session plus `killpg`.

**Step 4: Run scan cancellation and boundary tests**

```bash
/c/morphic_v1/.venv/Scripts/python.exe -m pytest \
  tests/test_web_scan_jobs.py \
  tests/test_web_scan_job_ownership.py -q
```

Expected: all pass.

---

### Task 2: Prove harmonization stop truth, promptness and durable ordering

**Objective:** Close F3-03, F3-04 and F3-05 across pending, running, impulse, pause and stale-save races.

**Files:**
- Modify if RED: `apps/web/contracts.py`
- Modify if RED: `apps/web/harmonization.py`
- Modify if RED: `services/harmonization_worker.py`
- Modify if RED: `apps/web/static/app.js`
- Test: `tests/test_harmonization_worker_stop.py`
- Test: `tests/test_harmonization_worker_pulse_pause_execution.py`
- Test: `tests/test_workbench_review_regressions.py`
- Test: `tests/test_web_shell.py`

**Step 1: Verify pending-stop behavior**

RED contract: create a persisted pending synthetic job, stop it before worker startup, then run the worker entry. Expected:
- stop response is authoritative `stopped`;
- no impulse/pause productive event occurs;
- worker exits without reviving the job.

**Step 2: Verify stale-save interleaving**

The test must block a running-state atomic write after it owns the job lock, start stop concurrently, release the write, and prove stop publishes last. A sequential stale save after stop is not sufficient.

**Step 3: Verify impulse/pause interruption**

Use fake clock/sleep/modulator only. Prove:
- stop is checked before impulse;
- pause checks in bounded slices;
- interrupted work does not increment `cycles_completed` or emit `cycle_metrics` as completed;
- `stop_requested` is observable;
- request validation rejects pulse/pause values above the documented bound.

**Step 4: Verify API/UI stop truth**

The frontend test must simulate a non-stopped response and prove it does not cancel polling or announce success. Then simulate `stopped` and prove it does.

**Step 5: Run the harmonization gate**

```bash
/c/morphic_v1/.venv/Scripts/python.exe -m pytest \
  tests/test_harmonization_worker_stop.py \
  tests/test_harmonization_worker_pulse_pause_execution.py \
  tests/test_web_shell.py -k 'harmonization or pulse or pause or stop' \
  tests/test_workbench_review_regressions.py -k 'harmonization or stop' -q
```

Expected: all selected tests pass with no thread/process warnings.

---

### Task 3: Prove authentication, ownership, tenant and trace authority

**Objective:** Close F3-06, F3-07 and F3-11 without weakening local no-key mode.

**Files:**
- Modify if RED: `apps/web/main.py`
- Modify if RED: `apps/web/workbench_runtime.py`
- Test: `tests/test_web_scan_job_ownership.py`
- Test: `tests/test_web_shell.py`
- Test: `tests/test_web_workbench_runtime.py`

**Step 1: Verify disclosure boundary matrix**

For scan status, results and stop, test:
- no configured key: local backward-compatible behavior;
- configured key with no/wrong header: 401 before disclosure;
- matching key and owner: success;
- matching key but foreign owner: 403;
- failed ownership check performs no stop side effect.

**Step 2: Verify tenant stability after environment drift**

Create app A with tenant A and explicit `runtime_dir`; change environment to tenant B and create app B. Invoke app A’s report catalog factory only after the change. Expected:
- app A remains entirely rooted in tenant A;
- app B remains entirely rooted in tenant B;
- scan export/report validation/harmonization binding do not cross.

**Step 3: Verify process-wide trace once-only semantics**

Spawn two independent Python processes with separate `WorkbenchRuntimeStore` instances against the same `tmp_path`. Both attempt terminal finalization. Expected multiset: exactly `['conflict', 'finalized']`; final JSON is complete and valid.

Also prove register/finalize serialization does not deadlock and lock initialization works on Windows when another process owns the byte lock.

**Step 4: Run authority tests**

```bash
/c/morphic_v1/.venv/Scripts/python.exe -m pytest \
  tests/test_web_scan_job_ownership.py \
  tests/test_web_shell.py -k 'tenant or owner or api_key or report_root' \
  tests/test_web_workbench_runtime.py -q
```

Expected: all pass.

---

### Task 4: Prove New Case as a complete privacy and lifecycle boundary

**Objective:** Close F3-02 and F3-09 through real browser behavior, including races.

**Files:**
- Modify if RED: `apps/web/static/app.js`
- Modify if RED: `apps/web/static/workbench-api.js`
- Modify if RED: `apps/web/static/workbench-state.js`
- Modify if RED: `apps/web/static/workbench-render.js`
- Test: `tests/test_workbench_review_regressions.py`
- Test: `tests/test_workbench_report_dom_js.py`
- Test/harness: `codex_tmp/acceptance-20260719/workbench.spec.js`

**Step 1: Define the reset postcondition**

After successful reset, prove all are cleared or restored:
- form-associated identity/context values;
- file picker and image metadata;
- both consent checks and group-consent identity/retention state;
- scan/harmonization/report IDs, results and run trace;
- timers and polling references;
- result metric grid and status text;
- report iframe `srcdoc`, title, metadata and open link;
- report catalog’s case-local selection/state;
- group analysis strength and sensitive group fields;
- backing selects and visible cards in sync;
- action buttons disabled according to prerequisites;
- current step reset to the first phase.

**Step 2: Verify reset during mutation**

Intercept a delayed mutating request. While pending:
- New Case button is disabled;
- direct reset invocation returns false and does not clear only half the case;
- after mutation settles, reset becomes available.

**Step 3: Verify server work is stopped before clear**

With synthetic active scan and harmonization IDs, intercept stop endpoints and prove both are called and return terminal state before local IDs disappear. If either stop fails, reset must not claim success.

**Step 4: Verify stale bootstrap cannot rehydrate**

Delay one initial case-sensitive loader, trigger reset, then release it. Expected: old response does not repopulate cleared state or DOM. The test must exercise generation capture across the entire bootstrap sequence.

**Step 5: Verify report preview remains reusable**

After reset, load a synthetic safe preview in the new case and prove the panel is unhidden and displays only the new content.

---

### Task 5: Prove truthful telemetry and accessibility behavior

**Objective:** Close F3-08, F3-10 and F3-12 with productive chronology and live-DOM focus assertions.

**Files:**
- Modify if RED: `apps/web/scan_jobs.py`
- Modify if RED: `apps/web/static/index.html`
- Modify if RED: `apps/web/static/app.js`
- Modify if RED: `apps/web/static/workbench-render.js`
- Test: `tests/test_web_scan_jobs.py`
- Test: `tests/test_workbench_dogfood_scan_truth.py`
- Test: `tests/test_workbench_dogfood_navigation_accessibility.py`
- Test/harness: `codex_tmp/acceptance-20260719/workbench.spec.js`

**Step 1: Replay productive Top-3 chronology**

Use the real output order from `apps/cli/commands/scan.py`:
- Phase 2 profile 1;
- child export output;
- Phase 2 profile 2;
- child export output;
- final profile;
- post-analysis stages.

Expected:
- no backward stage transition;
- export and later stages are not completed before all profiles finish;
- current stage remains distinct from completed stages;
- terminal completion closes the final current stage exactly once.

**Step 2: Verify radio focus in the live DOM**

For arrow, Home and End:
- selection changes;
- rerender occurs;
- `document.activeElement` is the newly rendered selected radio, not a detached node;
- exactly one card has `aria-checked=true` and `tabindex=0`.

**Step 3: Verify progress semantics**

Prove the harmonization progress element has `role=progressbar`, `aria-valuemin=0`, `aria-valuemax=100`, and polling/reset update `aria-valuenow` consistently with visible width/text.

**Step 4: Run telemetry/accessibility tests**

```bash
/c/morphic_v1/.venv/Scripts/python.exe -m pytest \
  tests/test_web_scan_jobs.py \
  tests/test_workbench_dogfood_scan_truth.py \
  tests/test_workbench_dogfood_navigation_accessibility.py \
  tests/test_workbench_report_dom_js.py -q
```

Expected: all pass.

---

### Task 6: Replace overstated evidence and reconcile documentation

**Objective:** Close F3-13 and ensure claims match executable evidence.

**Files:**
- Modify: `docs/superpowers/plans/2026-07-19-workbench-dogfood-remediation.md`
- Modify: this plan only if observed evidence requires correction
- Modify/Test: relevant tests only when replacing weak token checks

**Step 1: Classify every review finding**

For F3-01 through F3-13, record one of:
- behaviorally verified closed;
- still open with exact blocker;
- intentionally deferred with user approval and explicit NO-GO consequence.

No item may be marked closed based only on source strings.

**Step 2: Correct prior overclaims**

Reconcile at minimum:
- “every continuation guarded” versus actual bootstrap/mutation behavior;
- “atomic/once-only” versus cross-process semantics;
- poll-write wording versus terminal-only sync;
- session binding language versus exact process-emitted artifacts;
- reset completeness and report-preview reuse;
- current test counts and timestamps.

**Step 3: Add a v3 supersession section**

Record both v3 verdicts, their priorities and that v3 was drift-free but rejected. State that only v4 can become approval evidence.

**Step 4: Run documentation checks**

```bash
git diff --check
```

Expected: exit 0 apart from harmless line-ending warnings. Do not create Freeze v4 yet if any documentation patch remains anticipated.

---

### Task 7: Execute the complete verification ladder

**Objective:** Produce final pre-freeze evidence for one unchanged candidate.

**Step 1: Focused review suite**

```bash
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 OPENBLAS_NUM_THREADS=1
/c/morphic_v1/.venv/Scripts/python.exe -m pytest \
  tests/test_workbench_review_regressions.py \
  tests/test_web_scan_jobs.py \
  tests/test_web_workbench_runtime.py \
  tests/test_harmonization_worker_stop.py \
  tests/test_harmonization_worker_pulse_pause_execution.py \
  tests/test_web_scan_job_ownership.py \
  tests/test_web_shell.py \
  tests/test_workbench_dogfood_frontend_contracts.py \
  tests/test_workbench_dogfood_navigation_accessibility.py \
  tests/test_workbench_dogfood_scan_truth.py \
  tests/test_workbench_report_dom_js.py -q
```

Expected: all pass; no warnings from unhandled threads/processes.

**Step 2: Full suite**

```bash
/c/morphic_v1/.venv/Scripts/python.exe -m pytest tests -q
```

Expected: zero failures. Record exact passed/skipped count and duration; do not copy an earlier count.

**Step 3: Static checks**

```bash
node --check apps/web/static/app.js
node --check apps/web/static/workbench-api.js
node --check apps/web/static/workbench-render.js
node --check apps/web/static/workbench-state.js
node --check apps/web/static/workflow-stepping.js
git diff --check
```

Expected: all exit 0.

**Step 4: Check ports before browser service**

```bash
powershell.exe -NoProfile -Command '$p=Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue; if($p){exit 2}else{"PORT_8765_FREE"}'
```

Expected: `PORT_8765_FREE`. Also record but do not alter listeners on 8000/8090.

**Step 5: Isolated Playwright acceptance**

Start only port 8765 with isolated operator/tenant variables and the project venv. Run the three existing scenarios plus:
- delayed mutation/reset block;
- active server-job stop-before-clear;
- stale bootstrap response rejection;
- report preview reuse after reset;
- live radio Home/End focus;
- progressbar value updates.

Expected: all browser tests pass with no page errors, console errors or unexpected HTTP 4xx/5xx.

**Step 6: Cleanup and postcondition**

Remove only generated `node_modules`, `test-results` and exact synthetic runtime/export paths. Stop the tracked 8765 server and verify 8765 is free. Verify 8000/8090 are unchanged.

---

### Task 8: Create complete technical Freeze v4

**Objective:** Freeze every changed and untracked implementation/test/document path exactly once.

**Step 1: Capture live scope**

```bash
git status --short
git diff --name-only 3271ff9366ab3fecb2a158913a0cc19ed6a06726
git ls-files --others --exclude-standard
```

Build the scope from tracked changes plus untracked files. Include this new plan and the reconciled remediation plan. Exclude only the self-referential v4 manifest itself from its own entries.

**Step 2: Create a new immutable manifest**

Target:

`docs/reviews/2026-07-19-workbench-remediation-technical-freeze-v4.sha256`

Do not overwrite v1/v2/v3 manifests.

**Step 3: Verify manifest and scope completeness**

Required evidence:
- every manifest line `OK` under `sha256sum -c`;
- manifest path set equals changed+untracked path set excluding only v4 manifest;
- aggregate hash recorded;
- branch and HEAD recorded;
- `git diff --check` passed;
- exact latest test/browser evidence recorded.

**Step 4: Freeze discipline**

After v4 creation, no repository patch is permitted while its reviews run. Any patch means v4 and all v4 verdicts are superseded.

---

### Task 9: Obtain two independent drift-free technical approvals

**Objective:** Require two genuinely independent reviews of the exact same v4 bytes.

Each reviewer must:
- be given baseline, branch, v4 manifest path/hash and aggregate;
- inspect all scoped files;
- explicitly revisit every v1/v2/v3 finding, especially F3-01 through F3-13;
- perform read-only review only—no tests, imports, services or writes;
- verify manifest and aggregate at start and end;
- report counts for P0, P1, P2 and P3;
- return `APPROVE` only when all four counts are zero and drift is zero.

Gate outcome:
- two APPROVE verdicts, both `P0=P1=P2=P3=0`, same start/end hashes: technical gate passes;
- any finding or drift: NO-GO, preserve evidence, patch, create v5 and repeat from Task 7.

---

### Task 10: Documentation freeze, final approvals and external post-state

**Objective:** Complete the user’s change-control sequence without invalidating technical approval.

1. Only after two technical approvals, update final gate/status documentation with exact observed evidence.
2. Because this is a repository patch, create a separate document freeze.
3. Obtain two independent drift-free zero-finding reviews of that document freeze.
4. No backup occurs before both document reviews approve.
5. After all approvals, request/confirm the authorized external destination.
6. Create the external post-state shadow copy only then.
7. Generate a SHA-256 manifest externally and independently verify every entry.
8. Recheck source worktree and external copy hashes; record GO only if they match and all prior gates remain valid.
9. Commit/push remain prohibited unless the user separately authorizes them.

---

## 3. Definition of Done

This plan is complete only when all conditions hold simultaneously:

- F3-01 through F3-13 have executable behavioral closure evidence.
- The latest focused suite passes.
- The latest full suite passes with zero failures.
- JavaScript syntax checks and `git diff --check` pass.
- Isolated browser acceptance, including races and post-reset reuse, passes.
- Temporary service and synthetic artifacts are cleaned; port 8765 is free.
- Protected ports 8000 and 8090 were not restarted or repurposed.
- Freeze v4 (or a later replacement) covers the exact complete scope.
- Two independent technical reviews approve identical bytes with zero P0–P3 and zero drift.
- Final documentation has its own freeze and two independent approvals.
- The authorized external post-state shadow copy exists and its SHA-256 manifest is independently verified.
- No unauthorized commit, push or backup occurred.

Until every condition is met, status remains **NO-GO**.

## 4. Immediate next action

Execute Task 0 only: rerun the three previously failing Node contract tests against the final defensive `workbench-api.js` patch. If they pass, proceed to Task 1 without changing unrelated files.