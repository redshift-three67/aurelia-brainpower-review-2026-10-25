# RadiWorks Broadcast-Dock Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Die vorhandene Broadcast-Statusleiste wird in der Analyseansicht als ausklappbares, stets sichtbares Dock nutzbar; ein separater Vertrag beschreibt spätere parallele Aufträge pro Fall ohne deren Aktivierung.

**Architecture:** Der getrennte 8103-Kandidat erhält nur HTML/CSS/JS für die bestehende Statusleiste. Ihre Queue-Daten bleiben bei `statusbar.js`; das Backend und der Broadcast-Manager bleiben unverändert. Ein neues Brainpower-Prüfdokument bindet die zukünftige Auftragsisolation an Aurelia- und Modul-Template-Gates.

**Tech Stack:** Vanilla HTML/CSS/JavaScript, vorhandene FastAPI-Engine, lokaler Chrome/Playwright-Browsertest und Python-Pytest.

---

### Task 1: Dock-Zustände und Datenanzeige

**Files:**
- Modify: `runtime/rw-s46-canonical-20260929/radiworks_port/webapp/index.html`
- Modify: `runtime/rw-s46-canonical-20260929/radiworks_port/webapp/css/app.css`
- Modify: `runtime/rw-s46-canonical-20260929/radiworks_port/webapp/js/boot.js`
- Modify: `runtime/rw-s46-canonical-20260929/radiworks_port/webapp/js/views/statusbar.js`
- Test: `runtime/test_radiworks_dock_8104.cjs`

- [x] **Step 1: Failing browser check.** In an isolated 8104 home, assert `#dock-toggle` exists, is visible only on Analyse, starts `aria-expanded=false`, changes to true on click, collapses with Escape, and keeps the last result row reachable above the dock at 1280, 390 and 320 CSS pixels. The test uses only artificial data.
- [x] **Step 2: Run the check and confirm it fails because the dock does not exist.** Command: `node runtime/test_radiworks_dock_8104.cjs`; expected: nonzero exit with missing `#dock-toggle`.
- [x] **Step 3: Add the toolbar and wrapping content without duplicating queue elements.** The statusbar retains `#queue-bars`, `#resonated-mini` and `#gv-mini`; add `<button id="dock-toggle" type="button" aria-controls="dock-content" aria-expanded="false">Broadcast-Status öffnen</button>` plus `<span id="dock-summary" role="status">0 aktiv · 0 wartend</span>` and wrap the four existing columns in `#dock-content`.
- [x] **Step 4: Bind tab and toggle state.** `activateTab` toggles `body.analysis-active`. The statusbar initializer toggles `body.dock-open` and `aria-expanded`, supports Escape without intercepting open dialogs, and updates `#dock-summary` only when active/queued counts change. Leaving Analyse restores the original flowing statusbar; no queue request is added.
- [x] **Step 5: Add responsive CSS.** Keep `.statusbar-content` as the existing four-column grid outside Analyse. Within Analyse, `.statusbar` is fixed at the bottom with a 48 px closed height and a bounded expanded height; `.app-main` gets equivalent bottom clearance. At 900/600 px the existing two-/one-column grid applies to `.statusbar-content`; at 390/320 px the closed dock is the default and the expanded content scrolls internally. Respect `prefers-reduced-motion` and existing focus tokens.
- [x] **Step 6: Run `node --check` on both changed JS files and the isolated browser check.** Expected: syntax exit 0; keyboard, width and dock assertions pass.

### Task 2: Preserve functional paths

**Files:**
- Test: `runtime/rw-s46-canonical-20260929/radiworks_port/engine/tests`
- Test: `runtime/rw-s46-canonical-20260929/radiworks_port/engine/tools/browser_smoke/smoke.mjs`

- [x] **Step 1: Run the Python engine suite on candidate sources.** `PYTHONPATH` points to the candidate `engine/src`; expected: exit 0 with only the known Windows symlink skip.
- [x] **Step 2: Run the existing synthetic browser smoke and focused dock check on an isolated port.** Expected: all existing sections plus dock checks pass; no writes to 8102, 8090 or 8787.
- [x] **Step 3: Verify 8103 without restart.** Only static HTML/CSS/JS changed. `/ping`, `/` and `statusbar.js` returned HTTP 200 with new dock markup and logic. A restart could interrupt the active case or queue; no synthetic writes were made to 8103. Ports 8102, 8090 and 8787 were untouched.

### Task 3: Document parallel job boundary and handoff

**Files:**
- Create: `docs/verification/RADIWORKS_PARALLEL_FALLAUFTRAEGE_2026-10-01.md`
- Modify: `docs/verification/RADIWORKS_KANDIDAT_2026-10-01.md`

- [x] **Step 1: Record current behavior.** One process-wide active case/GV state; local queue may hold multiple virtual elements up to `MAX_ACTIVE=8`, but elements are not independently isolated per case/job. Multiple case sessions are not equivalent to parallel jobs.
- [x] **Step 2: Specify future contract and tests.** Server-authorized `(tenant_id, client_id, case_id, job_id)`, opaque case ID, idempotent command identity, per-job Draft/Passport/GV/entropy/recovery/queue/events, revision-safe case aggregation, cancellation and scoped WebSocket replay. State that `Modul_Templates` v1 and the RadiWorks local profile require a versioned delta; no normative API/schema or runtime is changed here.
- [x] **Step 3: Add proof and limits to the candidate report.** Include isolated browser/Python results, exact 8103 static/probe status and operator acceptance when available. Retain S4.6/S4.7 historical percentages until separately rescored; S4.8 remains 0%.
- [x] **Step 4: Ask for a focused 8103 operator look at the closed/open dock after the technical checks.** The operator confirmed the four focused UI checks on 8103. This does not constitute full RadiWorks or Aurelia approval.

**Execution selection:** Inline in this session. The running preview and shared candidate files make parallel writers counterproductive; no additional agent is needed for this bounded UI change.

