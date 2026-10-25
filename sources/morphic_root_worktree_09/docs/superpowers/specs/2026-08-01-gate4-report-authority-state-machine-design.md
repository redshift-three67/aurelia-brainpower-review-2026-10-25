# Gate 4 Report Authority State Machine Design

**Date:** 2026-08-01
**Status:** User-approved architecture correction; implementation pending
**Branch:** `operator-workbench-phase1`
**Parent specification:**
`docs/superpowers/specs/2026-07-31-gate4-primary-workflow-report-ux-design.md`

## 1. Purpose

This design corrects the internal authority architecture of Gate 4 Task 4. It
does not change the approved report UX, API, persistence, ownership, security,
or harmonization contracts.

Repeated race fixes exposed one root cause: report authority is distributed
across public browser fields, private request tokens, pending variables, DOM
snapshots, and imperative harmonization-button updates. Correcting one race can
therefore create another interaction among catalog reload, active-session
change, manual preview, fingerprint refresh, reset, and harmonization.

The correction replaces those distributed decisions with one small, explicit,
pure state reducer inside `apps/web/static/app.js`.

## 2. Chosen Boundary

The state machine is internal to `app.js`.

- No frontend framework or generic state-management library is introduced.
- No new production JavaScript module is introduced.
- `workbench-api.js` remains the I/O boundary.
- Existing DOM construction, iframe sandboxing, and API routes remain intact.
- `loadReports()`, `renderReportPreview()`, `loadScanResults()`, and New Case
  remain orchestration adapters, but no longer make independent authority
  decisions.
- Existing report fields in `MorphicWorkbenchState` remain observable for
  compatibility, but are projections written only by the authority adapter.

An extracted module was rejected because it would broaden Gate 4 and conflict
with the approved no-new-frontend-module boundary. Further token-specific
patches were rejected because multiple verified fixes exposed new races.

## 3. Canonical State

The reducer owns one immutable report-authority value with these dimensions:

| Field | Meaning |
|---|---|
| `generation` | Current case epoch. |
| `activeSessionId` | Exact owner-checked report session accepted from scan results. |
| `catalog` | Latest accepted catalog token and deduplicated entries by report ID. |
| `stable` | Last successfully rendered report, source, session, fingerprint, and immutable preview view model. |
| `pending` | At most one preview intent: `manual`, `auto`, or `refresh`. |
| `deferredRefresh` | Required refresh delayed behind a manual intent or reset. |
| `autoAttemptKey` | Attempt state for one `generation:activeSessionId` authority. |
| `focusId` | Logical roving-focus anchor; Task 5 remains responsible for keyboard movement. |
| `resetCheckpoint` | Coherent pre-reset stable authority and refresh requirement. |

Request contexts returned by the reducer contain the request ID, generation,
report ID, expected fingerprint, intent kind, and, for auto intent, exact
session and catalog authority. Completion events must present the same context.

The stable preview view is normalized from an authoritative preview response.
It is never captured from the current DOM. A transient `loading`, `empty`, or
`error` DOM state therefore cannot become the stable fallback.

## 4. Events and Effects

The reducer accepts explicit events:

- `ACTIVE_SESSION_ACCEPTED`
- `CATALOG_REQUESTED`
- `CATALOG_ACCEPTED`
- `CATALOG_FAILED`
- `PREVIEW_REQUESTED`
- `PREVIEW_SUCCEEDED`
- `PREVIEW_FAILED`
- `PREVIEW_STALE`
- `RESET_STARTED`
- `RESET_ABORTED`
- `RESET_COMPLETED`
- `HARMONIZATION_STATE_CHANGED`
- `FOCUS_MOVED`

The reducer has no API or DOM side effects. It returns the next state plus
bounded effects for the existing adapters:

- render catalog cards and their selected/focus projection;
- render `empty`, `loading`, `ready`, or `error` preview state;
- start one preview request with an immutable authority context;
- retain, clear, or refresh the stable preview;
- expose the derived active report ID and selection source;
- expose whether harmonization may start;
- ignore an event with an explicit stale reason.

Effects are executed only by the existing `app.js` adapters. Async completions
must re-enter the reducer; adapters may not commit report authority directly.
Every UI path that changes harmonization start/pending/run state, including
harmonization start failure and terminal polling, must use the same derived
eligibility projection instead of enabling the button from `activeReportId`
alone.

## 5. Invariants

The implementation must preserve these invariants:

1. Only an authoritative successful preview can replace `stable`.
2. `activeReportId` is the projection of `stable.reportId`; a neutral preview
   cannot retain an active report ID.
3. At most one preview intent is authoritative.
4. Manual intent has priority over auto-selection and background refresh.
5. Auto intent is bound to the exact active session, catalog token,
   fingerprint, generation, and request ID captured at request time.
6. Stale completion mutates neither stable selection nor preview nor
   auto-attempt state.
7. An authoritative auto failure consumes that exact session attempt; a stale
   auto completion does not.
8. A report is harmonization-eligible only when its stable preview still
   matches the accepted catalog fingerprint and no preview, reset, or
   harmonization transition is pending.
9. Selection, pressed state, focus projection, preview view, and
   harmonization eligibility derive from the same next state.
10. Duplicate report IDs remain fail-closed first-wins, as characterized by the
    existing Gate 4 tests.
11. All report authority remains memory-only and is cleared by successful New
    Case completion.

## 6. Session Change and Refresh Policy

Manual and automatic selections intentionally differ.

- A valid manual stable selection remains authoritative across catalog reloads
  and is never replaced automatically merely because the active scan session
  changes.
- If that manual report fingerprint changes, its refresh runs before any auto
  selection. Harmonization remains disabled until the current version loads.
- An automatic stable selection from an older session may remain visible as a
  fallback while the exact candidate for the newly active session loads.
- Fingerprint drift of that older automatic selection must not run first and
  block the new exact-session candidate.
- Success of the new exact-session preview replaces the old stable selection.
- Failure may retain the last valid stable view according to existing Task 4
  characterization, but that view is harmonization-eligible only if its own
  accepted fingerprint is still current.

This refines the parent specification's generic preview-failure rule: a failed
replacement request never makes its requested report active, so it may leave a
different previously successful stable report selected. A failed refresh of
the already active report may retain its last successful view only as an
explicit outdated fallback; it is not harmonization-eligible until a current
refresh succeeds.

This closes the verified `session-a` report A drift blocking `session-b`
candidate C race without weakening manual-selection authority.

## 7. Reset Policy

`RESET_STARTED` synchronously invalidates catalog and preview request contexts,
disables harmonization, clears non-restorable pending intent, and records a
coherent checkpoint before any server stop await.

`RESET_ABORTED` restores stable selection and preview atomically. A pending
async request is never resurrected. If the checkpoint already contained a
catalog/stable fingerprint mismatch, the stable view may be restored only as
an outdated fallback, the refresh remains required, and harmonization stays
disabled until that refresh succeeds.

`RESET_COMPLETED` advances the generation and clears catalog, stable preview,
pending intent, deferred refresh, auto-attempt state, focus projection, iframe,
text preview, metadata, file link, and harmonization eligibility.

This closes the verified reset-abort race where a neutral DOM fallback retained
`activeReportId` and incorrectly enabled harmonization.

## 8. Error and Stale Handling

- Catalog failure does not authorize a preview and does not mutate a newer
  accepted catalog.
- Preview loading clears stale frame/text presentation but not the stable
  authority used for an allowed fallback.
- An authoritative preview failure produces one explicit reducer transition.
- A stale result performs no UI or authority commit.
- Authentication errors continue through existing global handling.
- Safe API error text and iframe sandbox behavior remain unchanged.
- Direct imperative harmonization-button updates in report lifecycle paths are
  replaced by the single derived eligibility projection.

## 9. TDD and Migration

Implementation remains inside Gate 4 Task 4 and proceeds in this order:

1. Add a real Node RED for old auto A in session A, active session change to B,
   A fingerprint drift, and exact-session candidate C.
2. Add a real Node RED for reset abort with a deferred active-report refresh;
   neutral preview plus enabled harmonization must be impossible.
3. Add focused pure transition tests for authority, stale completion, manual
   priority, auto attempt, fingerprint refresh, and reset checkpoint behavior.
4. Introduce the pure reducer and state constructor in `app.js`.
5. Route catalog, preview, active-session, reset, and harmonization projection
   through the reducer while preserving existing APIs and DOM helpers.
6. Remove superseded distributed report tokens and pending variables only after
   their characterization tests pass through the reducer path.
7. Run the complete Task 4 Python/Node matrix and JavaScript syntax check.
8. Obtain fresh independent specification and quality/security approval before
   Task 5 begins.

Existing Task 4 tests remain characterization and may be updated only when a
test directly encodes the superseded internal mechanism rather than approved
behavior.

## 10. Scope

In scope:

- Gate 4 Task 4 report-authority architecture;
- the two verified races and directly coupled authority invariants;
- focused tests required to prevent regressions.

Out of scope:

- Task 5 roving keyboard implementation and browser acceptance;
- report API, persistence, ownership, backend harmonization, or scan changes;
- new browser persistence;
- generic CSS/DOM/state frameworks;
- unrelated `app.js` refactoring;
- commit, staging, push, reset, or clean without separate user instruction.

## 11. Acceptance

Task 4 is complete only when:

- both new race tests fail before the correction and pass afterward;
- all existing Task 4 characterization tests pass;
- `node --check apps/web/static/app.js` passes;
- scoped diff and empty-index checks pass;
- an independent specification review reports `APPROVE` with no P0-P3;
- a later independent quality/security review reports `APPROVE` with no P0-P2;
- no Task 5 behavior is implemented early.
