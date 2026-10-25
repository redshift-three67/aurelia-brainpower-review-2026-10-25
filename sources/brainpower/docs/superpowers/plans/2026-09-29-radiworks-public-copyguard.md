# RadiWorks Public CopyGuard Implementation Plan

> **For agentic workers:** Use the test-driven-development and verification-before-completion skills for each task. This plan runs inline in the existing RadiWorks WIP checkout; do not create another checkout or commit unrelated changes.

**Goal:** Block unsafe public text while preserving internal analysis and case data.

**Architecture:** A pure CopyGuard projection is applied at the HTTP JSON and WebSocket publication boundaries. A narrow current-case metadata endpoint avoids a lossy browser read/write round trip. Existing safe paths retain their shape and content.

**Tech Stack:** Python/FastAPI/pytest, vanilla JS, local Playwright development smoke.

---

### Task 1: Public projection and outgoing transports

**Files:** `radiworks_port/engine/src/radiworks/copyguard.py`, `radiworks_port/engine/src/radiworks/api/routes.py`, `radiworks_port/engine/src/radiworks/main.py`, new `radiworks_port/engine/tests/test_public_copyguard.py`.

- [x] Add a failing test using a synthetic `Heilt garantiert` rate. Assert raw stored Draft and Case remain unchanged, while HTTP analysis/current/draft/case/session/statistics outputs and WS history/replay omit that string. Assert safe `Arnica` output is unchanged.
- [x] Run only that test and confirm a content assertion fails (not setup).
- [x] Implement a nonmutating `public_view` projection and apply it once to HTTP JSON route results plus errors, and once before WS event history is stored. Keep `record_broadcast_terminal` on the raw event.
- [x] Run the focused test to green and verify existing API/WS tests.

### Task 2: Preserve raw case data through UI edits

**Files:** `radiworks_port/engine/src/radiworks/api/routes.py`, `radiworks_port/webapp/js/api.js`, `radiworks_port/webapp/js/views/analyze.js`, `radiworks_port/webapp/js/views/cases.js`, `radiworks_port/engine/tests/test_public_copyguard.py`.

- [x] Add a failing case-edit test that saves metadata after receiving a redacted case, then checks the stored analysis still has the raw rate. Add a negative test that rejects a full redacted case round trip.
- [x] Run those tests red. Add `POST /cases/current/metadata` with field-presence handling and safe value checks. Update both browser editors to use it for an active case; retain safe new-case creation through `POST /cases`.
- [x] Run tests green; check JavaScript syntax.

### Task 3: Browser and documentation verification

**Files:** `radiworks_port/engine/tools/browser_smoke/smoke.mjs`, module README, Brainpower S4 evidence and `WIEDERAUFNAHME.md`.

- [x] Confirm the existing browser-smoke negative assertion changes from red to green using the isolated synthetic instance; include direct-button disabled behavior and WS payload assertion where practical.
- [x] Run the full engine pytest suite, JS syntax checks and `git diff --check`. Report actual pass/skip counts and any unresolved S4 text surfaces.
- [x] Update evidence with measured S4.3 checklist percentage; do not claim total-module or Host/Aurelia approval.
