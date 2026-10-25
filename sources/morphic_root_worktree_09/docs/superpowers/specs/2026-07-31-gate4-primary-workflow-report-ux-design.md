# Gate 4 Primary Workflow and Report UX Design

**Date:** 2026-07-31
**Status:** User-approved specification; implementation not started
**Branch:** `operator-workbench-phase1`
**Parent gate:** Gate 4 in
`.hermes/plans/2026-07-21_152301-operator-workbench-korrekturen-a-bis-p.md`

## 1. Purpose

Gate 4 simplifies the primary Operator Workbench and prioritizes report
inspection without changing the scan engine, report generation, harmonization,
ownership, or security model.

The gate removes both links from the primary workflow to the explanatory
12-step system model. It then changes Phase 10 from a sticky two-column layout
to a sequential report experience:

1. choose a compact report card;
2. inspect the selected report in a full-width preview;
3. continue deliberately to harmonization and completion.

The separate `/workflow-stepping` route and its static assets remain available
internally. Removing primary-workflow links is not route decommissioning.

## 2. User Decisions

- Report cards show their client and session context directly.
- The catalog uses roving tabindex rather than ordinary Tab stops for every
  card.
- Desktop uses Left/Right navigation; mobile uses Up/Down; Home/End work in
  both orientations.
- Automatic preview is allowed only for the exact active scan report session.
- The active report session is linked explicitly; heuristics are forbidden.
- Within the active session, the newest inline-capable report is preferred:
  HTML first, then the newest TXT or JSON report, and PDF only when no inline
  report exists.
- The implementation is CSS-centered and keeps the existing API and report
  rendering boundaries rather than introducing a new frontend module.
- Radi144 is a visual and sequential-flow reference, not a source of engine or
  API behavior.

## 3. Existing Authority

The following current contracts remain authoritative:

- `loadReports()` owns catalog loading and stale-request rejection.
- `renderReportPreview()` owns report selection, preview loading, sandbox
  reset, Selection-Token protection, and harmonization enablement.
- Report catalog data is grouped by tenant-safe client and session records.
- Report HTML is rendered only in the existing sandboxed iframe.
- File opening uses the existing report file endpoint and separate link.
- The current scan job, owner scope, case generation, and request token remain
  the authority boundaries.
- `New Case` clears scan, report, preview, run-trace, and harmonization state.

Gate 4 extends these boundaries; it does not replace them.

## 4. Radi144 Transfer Contract

### Adopted patterns

- A clear sequential flow from selection to active detail to next action.
- Warm ivory, sage, sand, and restrained accent hierarchy already compatible
  with the current Workbench tokens.
- Compact action cards with visible active state and concise metadata.
- A full-width detail surface below the selection controls.
- Responsive orientation: compact horizontal choice flow on desktop and
  full-width vertical cards on mobile.
- Visible progress, loading, empty, selected, and error states.

### Explicitly excluded patterns

- Inline event handlers or `innerHTML` rendering.
- Simulated, random, or timer-based progress.
- Automatic step advancement.
- External font or asset dependencies.
- Direct Radi144 `/api/v1` coupling.
- Matrix, EMF, harmonization, export, or core-engine behavior.
- Therapeutic or physical-effect claims.

The current CSP-safe DOM construction, local design tokens, API modules, and
truthful process state remain mandatory.

## 5. Primary Workflow Simplification

The primary `index.html` must contain neither of these links or equivalent
replacement links:

- `Systemmodell oeffnen` in the scan-stage explanation;
- `Systemfluss ansehen` in the completion actions.

The surrounding copy must remain truthful without directing the operator away
from the primary workflow. The system-model route, tests for that route, and
its static files remain unchanged.

No wizard step is added, removed, renamed, or reordered by Gate 4.

## 6. Report Layout

### Desktop

- `reports-layout` becomes one column.
- The catalog panel appears first.
- The preview panel appears below and spans the full panel width.
- The preview panel is not sticky.
- The report list is a compact horizontally scrollable card track.
- Horizontal scrolling is local to the catalog; the page must not gain
  horizontal overflow.

### Mobile

- At the existing 768px responsive boundary, report cards become a vertical,
  full-width stack.
- The catalog has no horizontal scroll in mobile orientation.
- Preview, metadata, and file action remain within viewport width at 375px and
  320px.

### Report cards

Every report card remains a real `button` and displays:

- format icon and report title or filename;
- client label;
- session label;
- format and modification time.

The selected card uses the existing sage selection language and
`aria-pressed="true"`. Client and session data come from the catalog payload;
they are never inferred from the visible filename.

Existing client/session iteration may remain internally, but selection must be
understandable from each card without requiring an expanded group heading.

## 7. Report Session Authority

### Backend extraction

The existing scan already emits validated `MORPHIC_MULTIPLEX_EXPORT_V1`
records containing `session_id`. Gate 4 reuses that structured output.

At terminal job finalization, the Web scan adapter derives an optional report
session authority under these rules:

1. only validated export records are considered;
2. all accepted records must contain the same non-empty session ID;
3. zero records, invalid records, or more than one session ID produce no
   authority;
4. filesystem names, timestamps, and report ordering are not fallback
   authorities;
5. the result is persisted with the owner-bound job/run-trace state before
   catalog selection.

The owner-bound scan results response adds exactly one optional field:

```json
{
  "report_session_id": "20260731_120000"
}
```

The field is `null` when no exact authority exists. Existing response fields,
score values, result ordering, and report generation remain unchanged.

### Browser state

The browser stores the accepted value as per-case `activeReportSessionId` only
after the existing job ID, case generation, and request-token checks pass.

`New Case` resets:

- `activeReportSessionId`;
- `activeReportId`;
- catalog roving focus anchor;
- auto-selection attempt state;
- iframe source and `srcdoc`;
- text preview, title, metadata, state, and file link.

No report session or selection is written to templates, drafts, local storage,
or session storage.

## 8. Automatic Preview Selection

Catalog loading may select automatically only when all conditions are true:

- `activeReportSessionId` is non-empty;
- the catalog contains an exact `session_id` match;
- no valid manual report selection already exists for the current case;
- automatic selection has not already been attempted for the same session and
  case generation.

Candidate ranking is deterministic:

1. newest HTML report;
2. newest report among TXT and JSON;
3. newest PDF report;
4. no selection if the matched session has no files.

Timestamps are used only to rank files inside the already-authorized exact
session. They are never used to choose a session.

A refresh preserves a still-present manual selection. If that report
disappears, the selection and preview authority are cleared. Refresh must not
silently choose a different client or session. A later exact active-session
match may trigger the one permitted automatic attempt only when no manual
selection remains.

The automatic attempt is recorded only after an exact session match exists and
candidate ranking is evaluated. A catalog load with no exact session match does
not consume the later exact-match opportunity.

Automatic preview must not move keyboard focus.

## 9. Keyboard and Accessibility Contract

The report track is a labelled toolbar containing pressed-state buttons.

- Exactly one report card has `tabindex="0"`; all other cards have `-1`.
- With no selection, the first card is the roving anchor.
- With a selection, the selected card is the roving anchor.
- Left/Right move focus on desktop.
- Up/Down move focus at the mobile breakpoint.
- Home/End move focus to the first/last card.
- Arrow and Home/End navigation does not wrap; it clamps at the first and last
  card.
- Enter and Space use native button activation.
- Arrow navigation changes focus only; it does not load a preview.
- Pointer activation updates selection and the roving anchor.
- Re-render restores the anchor by report ID when that card still exists.
- Focus is never moved by catalog load, refresh, or automatic preview.

The toolbar exposes the active orientation. Focused cards are scrolled into the
catalog viewport without scrolling the page sideways. Focus-visible styling,
contrast, reduced-motion behavior, and readable long values are mandatory.

Catalog and preview state remain separately announced. The iframe keeps its
existing sandbox and title. The file-open link remains outside report buttons,
preventing nested interactive controls.

## 10. Loading, Empty, and Error Behavior

- Catalog loading shows a neutral state and retains stale-request protection.
- An empty catalog shows a visible empty state and creates no roving anchor.
- Catalog failure shows a visible error and starts no preview.
- Missing or conflicting report-session authority leaves the preview neutral
  with an explanatory message.
- Preview loading resets stale frame/text content before the request.
- Preview failure clears `activeReportId`, removes pressed selection, disables
  harmonization start, and displays the safe API error message.
- Authentication failures continue to follow the existing application-wide
  auth handling.
- A stale case generation or stale catalog/preview token may not render cards,
  select a report, or update the preview.

## 11. Scope and Non-goals

### In scope

- Primary-workflow link removal.
- Phase-10 HTML and CSS layout.
- Report-card context rendering.
- Roving keyboard behavior.
- Exact scan-job to report-session authority.
- Fail-closed auto-preview of one report in the exact active session.
- New Case and refresh correctness for the added state.

### Out of scope

- Changes to scan algorithms, Top-N selection, scores, report content, report
  generators, PDF rendering, or archive hierarchy.
- Gate 5 EMF changes.
- Gate 6 catalog filtering by user-relevant report kind.
- Gate 7 canonical report content or LLM policy.
- Harmonization behavior or job authority.
- Workflow step count or navigation rules outside the report catalog.
- Removal of the system-model route.
- New persistence, telemetry, external assets, or cloud services.

## 12. Verification Contract

### Static and unit coverage

- Primary `index.html` contains no system-model links while the internal route
  test remains green.
- Report layout is catalog-first, one-column, full-width preview, and non-sticky.
- Cards include client/session context and safe text construction.
- Structured export records yield one exact optional report session ID.
- Missing, malformed, and conflicting records yield `null`.
- Owner isolation remains enforced.
- No new browser persistence key exists.

### DOM and interaction coverage

- Roving tabindex has one anchor.
- Desktop Left/Right and mobile Up/Down work.
- Home/End clamp to first/last.
- Enter/Space activate through native button behavior.
- Arrow focus alone does not request a preview.
- `aria-pressed` tracks only the active report.
- Exact-session auto-selection obeys deterministic format ranking.
- Manual selection survives refresh and is not overwritten.
- No exact session means no automatic selection.
- New Case clears session, selection, preview, iframe, and file link.

### Browser acceptance

- Desktop catalog is horizontally scrollable above a full-width preview.
- 768px, 375px, and 320px layouts stack cards without page overflow.
- Focused cards remain visible inside the local catalog scroller.
- Preview iframe remains sandboxed.
- Both system-model links are absent from the primary page.
- The separate `/workflow-stepping` route remains reachable.

### Final gate

- Focused Python/Node matrix passes.
- JavaScript syntax checks pass.
- Full Python suite passes with only documented pre-existing warnings.
- Full isolated browser matrix passes.
- Manual desktop and 375px acceptance passes.
- Process, port, runtime, diff, and Git-index cleanup checks pass.
- Two independent final reviews report no open P0-P3 and P0-P2 findings.

## 13. Operational Stability

Implementation follows `PROJECT_MEMORY/00_CURRENT_STATE.md`:

- integrated Grep/Glob calls are not run in parallel;
- searches use targeted `rg` shell commands with hard timeouts until the
  upstream tool-completion issue is fixed;
- broad diff output is avoided;
- Python and browser matrices run serially after memory/process preflight;
- only one Kilo main process remains active.
