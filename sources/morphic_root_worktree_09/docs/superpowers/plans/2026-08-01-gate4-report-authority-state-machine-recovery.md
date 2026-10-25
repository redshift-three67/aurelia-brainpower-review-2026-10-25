# Gate 4 Report Authority State Machine Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish Gate 4 Task 4 by replacing distributed report-authority decisions with one small internal reducer that closes the two remaining verified races without implementing Task 5 early.

**Architecture:** Keep the reducer, state constructor, and adapter inside `apps/web/static/app.js`. Existing API and DOM functions become effect adapters; `MorphicWorkbenchState` report fields remain compatibility projections written only from reducer state. Stable preview data is an immutable view model, never a snapshot captured from transient DOM.

**Tech Stack:** Vanilla JavaScript, Node VM tests driven by pytest, existing FastAPI report endpoints, pytest, Git diff/index checks.

**Authoritative design:** `docs/superpowers/specs/2026-08-01-gate4-report-authority-state-machine-design.md`

**Parent Gate 4 plan:** `docs/superpowers/plans/2026-07-31-gate4-primary-workflow-report-ux.md`, Task 4

**Commit rule:** Do not commit, stage, push, reset, clean, checkout, or revert. Each task ends with a scoped uncommitted checkpoint because the user explicitly prohibited Git mutation without separate authorization.

---

## File Map

### Production

- Modify `apps/web/static/app.js`: add the pure report-authority reducer and route report catalog, preview, active-session, reset, and harmonization-button projection through it.

### Tests

- Modify `tests/test_gate4_report_catalog_js.py`: add the two missing runtime race reproductions, pure reducer transition coverage, and update assertions that directly name superseded private variables.
- Read-only neighbor `tests/test_workbench_report_dom_js.py`: verify safe card construction remains unchanged.
- Read-only neighbor `tests/test_workbench_ui_quality_contracts.py`: verify Task 3 layout remains unchanged.

### Authority records

- Read-only `docs/superpowers/specs/2026-07-31-gate4-primary-workflow-report-ux-design.md`.
- Read-only `docs/superpowers/specs/2026-08-01-gate4-report-authority-state-machine-design.md`.
- Read-only `docs/superpowers/plans/2026-07-31-gate4-primary-workflow-report-ux.md`.

---

## Operational Preflight

- [ ] **Step 1: Verify resources before every implementation or review subagent**

Run serially:

```powershell
$os = Get-CimInstance Win32_OperatingSystem
[pscustomobject]@{
  FreePhysicalGiB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
  FreeVirtualGiB = [math]::Round($os.FreeVirtualMemory / 1MB, 2)
}
Get-Process kilo -ErrorAction SilentlyContinue |
  Select-Object Id,StartTime,@{N='PrivateGiB';E={[math]::Round($_.PrivateMemorySize64/1GB,2)}}
```

Expected: one Kilo main process and enough headroom for one serial subagent. Do not dispatch when Windows has emitted a new Event 2004 or virtual headroom is below 3 GiB.

- [ ] **Step 2: Verify worktree boundaries**

Run:

```powershell
git branch --show-current
git diff --cached --name-only
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
  Where-Object { $_.LocalPort -in 8090,8765,8766 } |
  Select-Object LocalPort,OwningProcess
```

Expected: branch `operator-workbench-phase1`, empty index, protected port 8090 unchanged, and test ports 8765/8766 free.

---

### Task 1: Lock the Two Remaining Races as RED

**Files:**
- Modify: `tests/test_gate4_report_catalog_js.py`
- Test: `tests/test_gate4_report_catalog_js.py`

- [ ] **Step 1: Add the old-auto/session-switch/fingerprint RED**

Add `test_old_auto_fingerprint_drift_cannot_block_new_exact_session_candidate` using the existing `_run_app_script()` harness. Its Node body must perform this exact sequence:

```javascript
const state = window.MorphicWorkbenchState;
let files = [
  {id: "report-a", kind: "HTML", session_id: "session-a", modified_at: "2026-08-01T10:00:00Z", size: 10},
  {id: "report-c", kind: "HTML", session_id: "session-b", modified_at: "2026-08-01T10:00:00Z", size: 10},
];
let resultSession = "session-a";
const catalogPayload = () => ({clients: [{
  client_id: "client-a",
  sessions: [
    {session_id: "session-a", files: files.filter(file => file.session_id === "session-a")},
    {session_id: "session-b", files: files.filter(file => file.session_id === "session-b")},
  ],
}]});
Object.assign(state, {
  activeJobId: "scan-a",
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
const previewCalls = [];
window.MorphicWorkbenchApi = {
  async loadReports() { return catalogPayload(); },
  async loadScanResults() { return {report_session_id: resultSession}; },
  async loadRunTrace() { return {}; },
  async loadReportPreview(reportId) {
    previewCalls.push(reportId);
    return {mode: "text", kind: "HTML", title: reportId, content: reportId, size: 10};
  },
};

await loadScanResults("scan-a", caseGeneration, true);
await loadReports(caseGeneration, true);
state.activeJobId = "scan-b";
resultSession = "session-b";
await loadScanResults("scan-b", caseGeneration, true);
files = files.map(file => file.id === "report-a"
  ? {...file, modified_at: "2026-08-01T10:01:00Z", size: 20}
  : file);
await loadReports(caseGeneration, true);
if (
  previewCalls.join(",") !== "report-a,report-c"
  || state.activeReportId !== "report-c"
  || state.reportSelectionSource !== "auto"
  || nodes["#report-preview-text"].textContent !== "report-c"
) {
  throw new Error(`new session candidate blocked: ${previewCalls}/${state.activeReportId}`);
}
```

Do not call internal private helpers to manufacture authority. The test must use
`loadScanResults()`, `loadReports()`, and preview API completions.

- [ ] **Step 2: Add the reset-abort/deferred-refresh RED**

Add `test_reset_abort_with_deferred_refresh_never_enables_harmonization_without_current_stable_preview`. Reuse the existing harness, but perform this exact public sequence:

1. Load catalog A-v1 and B, then manually preview A successfully.
2. Start manual B with a controlled unresolved promise.
3. Change A to v2 and call `loadReports()` so A refresh becomes deferred.
4. Set an active scan job and start New Case with a controlled rejected `stopScanJob()`.
5. Resolve B while reset is pending; its outcome must be `stale`.
6. Reject scan stop and await reset abort.
7. Assert the UI is never neutral while `activeReportId` remains set and the harmonization button is enabled.

The terminal assertion must be:

```javascript
const neutralWithAuthority = (
  nodes["#report-preview-panel"].dataset.state === "empty"
  && state.activeReportId !== null
);
if (
  resetOutcome !== false
  || outcomeB !== REPORT_PREVIEW_OUTCOME.STALE
  || neutralWithAuthority
  || !nodes["#harmonization-start-button"].disabled
) {
  throw new Error(
    `unsafe reset abort: ${resetOutcome}/${outcomeB}/`
    + `${nodes["#report-preview-panel"].dataset.state}/${state.activeReportId}/`
    + `${nodes["#harmonization-start-button"].disabled}`
  );
}
```

- [ ] **Step 3: Run both tests and preserve the exact RED evidence**

Run:

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
$env:OPENBLAS_NUM_THREADS='1'
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest `
  tests/test_gate4_report_catalog_js.py::test_old_auto_fingerprint_drift_cannot_block_new_exact_session_candidate `
  tests/test_gate4_report_catalog_js.py::test_reset_abort_with_deferred_refresh_never_enables_harmonization_without_current_stable_preview `
  -q --tb=short
```

Expected: `2 failed`. The first failure must show that only A was requested or C was not bound. The second must show the neutral/active/harmonization inconsistency. A test harness error, missing fixture, or syntax error is not accepted RED evidence.

- [ ] **Step 4: Uncommitted checkpoint**

Run:

```powershell
git diff --check -- tests/test_gate4_report_catalog_js.py
git diff --cached --name-only
```

Expected: diff check clean and index empty.

---

### Task 2: Introduce the Pure Authority Reducer

**Files:**
- Modify: `apps/web/static/app.js:51-78,1326-1441`
- Modify: `tests/test_gate4_report_catalog_js.py`

- [ ] **Step 1: Add pure transition REDs**

Add `test_report_authority_reducer_enforces_manual_auto_stale_and_reset_invariants`. Invoke planned globals directly and assert these transitions:

```javascript
let authority = createReportAuthorityState(4);
authority = reduceReportAuthority(authority, {
  type: "ACTIVE_SESSION_ACCEPTED", generation: 4, sessionId: "session-b",
}).state;
const requestedCatalog = reduceReportAuthority(authority, {
  type: "CATALOG_REQUESTED", generation: 4,
});
const catalogRequest = requestedCatalog.effects.find(
  effect => effect.type === "LOAD_CATALOG"
).request;
authority = reduceReportAuthority(requestedCatalog.state, {
  type: "CATALOG_ACCEPTED",
  generation: 4,
  request: catalogRequest,
  entries: [
    {id: "a", session_id: "session-a", kind: "HTML", modified_at: "v1", size: 1},
    {id: "c", session_id: "session-b", kind: "HTML", modified_at: "v1", size: 1},
  ],
}).state;
const manual = reduceReportAuthority(authority, {
  type: "PREVIEW_REQUESTED", generation: 4, reportId: "a", intent: "manual",
});
const manualRequest = manual.effects.find(
  effect => effect.type === "LOAD_PREVIEW"
).request;
const blockedAuto = reduceReportAuthority(manual.state, {
  type: "PREVIEW_REQUESTED", generation: 4, reportId: "c", intent: "auto",
});
if (blockedAuto.effects.length !== 0 || blockedAuto.state.pending.requestId !== manual.state.pending.requestId) {
  throw new Error("auto replaced manual intent");
}
const stale = reduceReportAuthority(manual.state, {
  type: "PREVIEW_STALE", request: {...manualRequest, requestId: -1},
});
if (stale.state !== manual.state) throw new Error("stale completion mutated authority");
const reset = reduceReportAuthority(manual.state, {type: "RESET_STARTED", generation: 4});
if (!reset.state.resetCheckpoint || reset.state.pending !== null || reset.state.canHarmonize) {
  throw new Error("reset start did not atomically checkpoint and invalidate");
}
```

Also assert that state and event input objects are not mutated.

- [ ] **Step 2: Run the reducer test RED**

Run the single new test. Expected: Node fails because `createReportAuthorityState` and `reduceReportAuthority` do not exist.

- [ ] **Step 3: Add constants and the immutable state constructor**

Add near `REPORT_PREVIEW_OUTCOME`:

```javascript
const REPORT_AUTHORITY_EVENT = Object.freeze({
  ACTIVE_SESSION_ACCEPTED: "ACTIVE_SESSION_ACCEPTED",
  CATALOG_REQUESTED: "CATALOG_REQUESTED",
  CATALOG_ACCEPTED: "CATALOG_ACCEPTED",
  CATALOG_FAILED: "CATALOG_FAILED",
  PREVIEW_REQUESTED: "PREVIEW_REQUESTED",
  PREVIEW_SUCCEEDED: "PREVIEW_SUCCEEDED",
  PREVIEW_FAILED: "PREVIEW_FAILED",
  PREVIEW_STALE: "PREVIEW_STALE",
  RESET_STARTED: "RESET_STARTED",
  RESET_ABORTED: "RESET_ABORTED",
  RESET_COMPLETED: "RESET_COMPLETED",
  HARMONIZATION_STATE_CHANGED: "HARMONIZATION_STATE_CHANGED",
  FOCUS_MOVED: "FOCUS_MOVED",
});

function createReportAuthorityState(generation = 0) {
  return Object.freeze({
    generation,
    nextCatalogRequestId: 1,
    acceptedCatalogRequestId: 0,
    nextPreviewRequestId: 1,
    activeSessionId: null,
    entriesById: new Map(),
    stable: null,
    pending: null,
    deferredRefresh: null,
    autoAttemptKey: null,
    focusId: null,
    resetCheckpoint: null,
    harmonizationStartPending: false,
    harmonizationRunActive: false,
    canHarmonize: false,
  });
}
```

Use fresh `Map` and plain-object copies for every transition. Never mutate `current`, `event`, `entriesById`, `stable`, or `pending` in place.

- [ ] **Step 4: Implement the pure transition contract**

Implement:

```javascript
function reduceReportAuthority(current, event) {
  // Return the same object and no effects for stale generation/request events.
  // Otherwise return Object.freeze({state: nextState, effects}).
}
```

Required exact behavior:

| Event | State transition | Effect |
|---|---|---|
| `ACTIVE_SESSION_ACCEPTED` | Set normalized non-empty string or `null`. Do not clear a valid manual stable selection. | none |
| `CATALOG_REQUESTED` | Allocate and return one catalog request ID. | `{type: "LOAD_CATALOG", request}` |
| `CATALOG_ACCEPTED` | Accept only current generation/latest request; replace deduplicated map; clear removed stable; derive refresh/auto priority. | `RENDER_CATALOG`, optionally one `LOAD_PREVIEW` |
| `PREVIEW_REQUESTED` | Reject auto/refresh behind manual; allocate immutable request context with expected fingerprint and session. | `RENDER_LOADING`, `LOAD_PREVIEW` |
| `PREVIEW_SUCCEEDED` | Accept only exact pending context and current fingerprint; replace stable with normalized view; clear pending/deferred as applicable. | `RENDER_STABLE` |
| `PREVIEW_FAILED` | Accept only exact pending context; retain a different valid stable fallback; consume authoritative auto attempt; current-version mismatch keeps `canHarmonize=false`. | `RENDER_STABLE` or `RENDER_ERROR` |
| `PREVIEW_STALE` | Nonmatching context returns the same state; matching stale clears only that pending intent and does not consume auto attempt. | restore valid stable or none |
| `RESET_STARTED` | Store stable/deferred checkpoint, clear pending, invalidate request counters, set `canHarmonize=false`. | `DISABLE_HARMONIZATION` |
| `RESET_ABORTED` | Restore checkpoint without resurrecting pending request; preserve refresh requirement. | render stable fallback or neutral |
| `RESET_COMPLETED` | Return a fresh state for the next generation. | render empty and disable harmonization |
| `HARMONIZATION_STATE_CHANGED` | Store pending/run flags and recompute eligibility. | `SYNC_HARMONIZATION` |
| `FOCUS_MOVED` | Store ID only if present in accepted catalog. | `RENDER_CATALOG_SELECTION` |

Compute eligibility in exactly one helper:

```javascript
function reportAuthorityCanHarmonize(authority) {
  const stableEntry = authority.stable
    ? authority.entriesById.get(authority.stable.reportId)
    : null;
  return Boolean(
    authority.stable
    && stableEntry
    && authority.stable.entryFingerprint === reportEntryFingerprint(stableEntry)
    && authority.pending === null
    && authority.resetCheckpoint === null
    && !authority.harmonizationStartPending
    && !authority.harmonizationRunActive
  );
}
```

- [ ] **Step 5: Run reducer GREEN without changing orchestration**

Run the reducer test plus pure flatten/ranking tests. Expected: all selected tests pass; the two integration race tests remain RED because adapters are not migrated yet.

- [ ] **Step 6: Syntax and checkpoint**

Run:

```powershell
node --check apps/web/static/app.js
git diff --check -- apps/web/static/app.js tests/test_gate4_report_catalog_js.py
git diff --cached --name-only
```

Expected: syntax/diff clean and index empty.

---

### Task 3: Route Session, Catalog, and Preview Through the Reducer

**Files:**
- Modify: `apps/web/static/app.js:51-78,1212-1257,1442-2020`
- Modify: `tests/test_gate4_report_catalog_js.py`

- [ ] **Step 1: Add the single adapter and compatibility projection**

Replace the private report globals with:

```javascript
let reportAuthority = createReportAuthorityState(caseGeneration);

function projectReportAuthority(authority = reportAuthority) {
  const state = window.MorphicWorkbenchState;
  state.activeReportSessionId = authority.activeSessionId;
  state.activeReportId = authority.stable?.reportId || null;
  state.reportSelectionSource = authority.stable?.selectionSource || null;
  state.reportFocusId = authority.focusId;
  state.reportAutoSelectionKey = authority.autoAttemptKey;
}

function transitionReportAuthority(event) {
  const transition = reduceReportAuthority(reportAuthority, event);
  reportAuthority = transition.state;
  projectReportAuthority(reportAuthority);
  return transition.effects;
}
```

Add one bounded effect adapter. Extract the existing DOM statements into the
named render helpers; those helpers render data but never change authority:

```javascript
async function applyReportAuthorityEffects(effects) {
  let outcome = REPORT_PREVIEW_OUTCOME.STALE;
  for (const effect of effects) {
    if (effect.type === "RENDER_CATALOG") renderReportCatalog(effect.entries);
    else if (effect.type === "RENDER_LOADING") renderReportPreviewLoading();
    else if (effect.type === "RENDER_STABLE") renderStableReportView(effect.view);
    else if (effect.type === "RENDER_EMPTY") renderEmptyReportPreview(effect.message);
    else if (effect.type === "RENDER_ERROR") renderReportPreviewError(effect.message);
    else if (effect.type === "LOAD_PREVIEW") {
      outcome = await executeReportPreviewRequest(effect.request);
    }
  }
  return outcome;
}
```

`renderReportCatalog`, `renderReportPreviewLoading`, `renderStableReportView`,
`renderEmptyReportPreview`, and `renderReportPreviewError` must contain only the
safe DOM construction already present in Task 4. `executeReportPreviewRequest`
is the only preview API adapter and always completes through a reducer event.

Remove direct writes to the five projected fields from report lifecycle code. Task 2 result normalization must dispatch `ACTIVE_SESSION_ACCEPTED` only after its existing job/generation/request checks.

- [ ] **Step 2: Convert catalog loading to request/effect authority**

`loadReports()` must:

1. dispatch `CATALOG_REQUESTED` before the API call;
2. carry the returned request context through the await;
3. dispatch `CATALOG_ACCEPTED` with `flattenReportEntries(data.clients)`;
4. render cards from the accepted reducer state;
5. execute at most one reducer-emitted `LOAD_PREVIEW` effect;
6. dispatch `CATALOG_FAILED` only for the same request context.

Do not refresh an old automatic stable report before the reducer has reconciled the new active session. A manual stable report remains dominant.

- [ ] **Step 3: Normalize preview responses into immutable view models**

Add:

```javascript
function reportPreviewView(reportId, preview) {
  const mode = preview?.mode === "html"
    ? "html"
    : preview?.mode === "file"
      ? "file"
      : "text";
  return Object.freeze({
    reportId,
    mode,
    kind: String(preview?.kind || preview?.mode || ""),
    title: String(preview?.title || preview?.file_name || reportId),
    content: typeof preview?.content === "string" ? preview.content : "",
    size: preview?.size ?? "",
    fileHref: `/api/reports/${encodeURIComponent(reportId)}/file`,
  });
}
```

Replace `captureReportPreviewSnapshot()` authority with this model. A renderer may apply the model to iframe/text/title/meta/link, but it may not read transient DOM to define authority.

- [ ] **Step 4: Convert preview loading and completion**

`renderReportPreview()` becomes an adapter:

1. dispatch `PREVIEW_REQUESTED` and return `STALE` when no `LOAD_PREVIEW` effect is emitted;
2. render loading from the effect;
3. call `loadReportPreview(effect.request.reportId)`;
4. for HTML, await the existing sandbox load before success dispatch;
5. dispatch `PREVIEW_SUCCEEDED` with the immutable view and exact request context;
6. dispatch `PREVIEW_FAILED` with safe error text on authoritative API failure;
7. dispatch `PREVIEW_STALE` when generation/catalog/fingerprint/request authority no longer matches;
8. execute a reducer-emitted deferred refresh only after the terminal transition.

The reducer, not the adapter, decides whether the outcome is `SUCCESS`, `FAILURE`, or `STALE` and whether a fallback remains selected.

- [ ] **Step 5: Make the first race GREEN**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest `
  tests/test_gate4_report_catalog_js.py::test_old_auto_fingerprint_drift_cannot_block_new_exact_session_candidate `
  tests/test_gate4_report_catalog_js.py::test_report_authority_reducer_enforces_manual_auto_stale_and_reset_invariants `
  tests/test_gate4_report_catalog_js.py::test_same_report_id_reloads_only_when_catalog_version_changes `
  tests/test_gate4_report_catalog_js.py::test_pending_manual_intent_defers_active_fingerprint_refresh_and_wins_on_success `
  tests/test_gate4_report_catalog_js.py::test_failed_pending_manual_runs_deferred_latest_active_fingerprint_refresh `
  -q --tb=short
```

Expected: all selected tests pass. If an old assertion reads a removed private token, rewrite it to assert observable state, API call order, pending effect, or reducer request identity; do not recreate the old global for the test.

- [ ] **Step 6: Run all Task 4 Node characterization**

Run `tests/test_gate4_report_catalog_js.py -q --tb=short`.

Expected: only the reset-abort race may remain RED at this checkpoint. Every other existing test must pass before Task 4 continues.

- [ ] **Step 7: Syntax and checkpoint**

Run scoped syntax, diff, and empty-index checks.

---

### Task 4: Route Reset and Harmonization Eligibility Through the Reducer

**Files:**
- Modify: `apps/web/static/app.js:2022-2148,2276-2551`
- Modify: `tests/test_gate4_report_catalog_js.py`

- [ ] **Step 1: Centralize harmonization-button projection**

Add exactly one UI helper:

```javascript
function syncReportHarmonizationAvailability() {
  const button = $("#harmonization-start-button");
  if (button) button.disabled = !reportAuthority.canHarmonize;
}
```

Call it after every report-authority transition and after
`HARMONIZATION_STATE_CHANGED`. Remove report-lifecycle and harmonization
catch/finally/poll-terminal assignments that use `!state.activeReportId`.

- [ ] **Step 2: Convert reset start and every abort path**

At the synchronous start of `resetWorkbenchForNewCase()`:

```javascript
state.resetInProgress = true;
transitionReportAuthority({
  type: REPORT_AUTHORITY_EVENT.RESET_STARTED,
  generation: caseGeneration,
});
syncReportHarmonizationAvailability();
```

Every pre-stop and stop-error abort path must dispatch:

```javascript
state.resetInProgress = false;
const effects = transitionReportAuthority({
  type: REPORT_AUTHORITY_EVENT.RESET_ABORTED,
  generation: caseGeneration,
});
applyReportAuthorityEffects(effects);
syncReportHarmonizationAvailability();
```

Do not restore a pending promise. If the checkpoint is fingerprint-outdated,
render its immutable fallback view, retain the required refresh, and leave
harmonization disabled.

- [ ] **Step 3: Convert successful reset**

Immediately after `caseGeneration += 1`, dispatch:

```javascript
const effects = transitionReportAuthority({
  type: REPORT_AUTHORITY_EVENT.RESET_COMPLETED,
  generation: caseGeneration,
});
applyReportAuthorityEffects(effects);
```

Remove duplicate direct report-field resets and private authority resets. Keep
the existing explicit iframe/text/title/meta/link clearing as an idempotent UI
safety check, and retain all unrelated scan/group/harmonization cleanup.

- [ ] **Step 4: Make the second race GREEN**

Run the reset-abort race plus all existing reset tests in
`tests/test_gate4_report_catalog_js.py` selected by exact node IDs:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest `
  tests/test_gate4_report_catalog_js.py::test_reset_abort_with_deferred_refresh_never_enables_harmonization_without_current_stable_preview `
  tests/test_gate4_report_catalog_js.py::test_new_case_invalidates_pending_report_before_blocked_stop_await `
  tests/test_gate4_report_catalog_js.py::test_aborted_new_case_restores_stable_active_preview_after_sync_invalidation `
  tests/test_gate4_report_catalog_js.py::test_aborted_reset_without_stable_preview_restores_neutral_catalog_state `
  tests/test_gate4_report_catalog_js.py::test_new_case_runtime_clears_report_authority_and_preview `
  -q --tb=short
```

Expected: all selected tests pass and no terminal state combines an empty/error preview, non-null projected active report, and enabled harmonization.

- [ ] **Step 5: Add a mutation proof for derived eligibility**

Extend `_run_app_script()` with an optional mutation that replaces the call to
`reportAuthorityCanHarmonize()` with `Boolean(authority.stable)`. Run the reset
race under that mutation and assert non-zero Node exit. This proves the test
depends on fingerprint-current eligibility rather than only a disabled-button
literal.

- [ ] **Step 6: Run complete Task 4 GREEN**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest `
  tests/test_gate4_report_catalog_js.py `
  tests/test_workbench_report_dom_js.py `
  tests/test_workbench_ui_quality_contracts.py `
  -q --tb=short
node --check apps/web/static/app.js
```

Expected: all tests pass; no Task 5 keydown/matchMedia behavior is present.

- [ ] **Step 7: Remove superseded mechanism only after GREEN**

Run targeted search:

```powershell
rg --line-number 'reportCatalogRequestToken|reportPreviewRequestToken|pendingManualReportPreview|stableReportPreviewAuthority|currentReportEntriesById|deferredReportVersionRefresh|captureReportPreviewSnapshot|restoreReportPreviewSnapshot' apps/web/static/app.js tests/test_gate4_report_catalog_js.py
```

Expected: no production reference remains. Test references may remain only in
historical mutation-input text that explicitly proves the old mechanism is
absent; prefer removing such references.

- [ ] **Step 8: Uncommitted checkpoint**

Run:

```powershell
git diff --check -- apps/web/static/app.js tests/test_gate4_report_catalog_js.py
git diff --cached --name-only
```

Expected: clean diff and empty index.

---

### Task 5: Independent Task 4 Reviews and Handoff Back to Parent Plan

**Files:**
- Review only: `apps/web/static/app.js`
- Review only: `tests/test_gate4_report_catalog_js.py`
- Review authority: both Gate 4 design files and both Gate 4 plan files

- [ ] **Step 1: Run resource and process preflight**

Require one Kilo process, no recent Event 2004, sufficient virtual memory, protected port 8090 unchanged, test ports free, and no stale Node/Python test process.

- [ ] **Step 2: Run focused Task 4 matrix on final bytes**

Run the Task 4 command from the parent plan plus syntax and scoped diff/index checks. Record exact counts and duration.

- [ ] **Step 3: Obtain independent specification review**

Dispatch a fresh read-only reviewer. Review current source and tests against:

- parent Gate 4 design Sections 7-10 and 12;
- recovery design Sections 3-11;
- parent Task 4 acceptance;
- both new race reproductions.

Acceptance: `APPROVE`, zero P0-P3. Any finding returns to the relevant RED/GREEN task, followed by complete re-review.

- [ ] **Step 4: Obtain independent quality/security review**

Only after specification approval, dispatch a different read-only reviewer.
Require explicit review of reducer purity, stale request rejection, immutable
preview model, DOM safety, iframe sandbox preservation, harmonization
eligibility, complexity, and false-green test risk.

Acceptance: `APPROVE`, zero P0-P2. Any change invalidates both reviews and
requires affected tests, full Task 4 matrix, spec re-review, then quality
re-review.

- [ ] **Step 5: Mark parent Task 4 complete and continue at Task 5**

Do not edit the parent plan checkboxes. Update the live session task state only after
both reviews approve and checks pass. The next implementation point is parent
plan Task 5, `Roving Focus, Responsive Orientation, and Browser Acceptance`.

- [ ] **Step 6: Final Task 4 checkpoint**

Confirm:

```powershell
git diff --cached --name-only
node --check apps/web/static/app.js
```

Expected: empty index and syntax success. Do not commit.
