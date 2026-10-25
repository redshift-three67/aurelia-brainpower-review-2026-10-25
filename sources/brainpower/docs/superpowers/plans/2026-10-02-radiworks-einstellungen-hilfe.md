# RadiWorks Settings Help Implementation Plan

> **For agentic workers:** This bounded UI change is executed locally. Preserve existing source WIP and all product gates.

**Goal:** Explain every currently displayed RadiWorks setting and its actual effect without changing saved values or analysis behavior.

**Architecture:** Render presentation metadata beside the existing dynamic settings controls. Unknown keys receive a conservative fallback. Keep the current GET/PUT contract and form collection unchanged.

**Tech Stack:** Vanilla JavaScript/CSS, local FastAPI preview, browser accessibility inspection.

---

### Task 1: Isolate and document current behavior

- [x] Compare all settings keys against server and browser readers; identify only three active keys.
- [x] Verify live GET `/settings` and record that integers are currently empty.
- [x] Copy the current `webapp` to `Brainpower/runtime/rw-settings-help-20261002` and record hashes of the four intended source files.

### Task 2: Add explanations without changing persistence

- [x] Update staged `webapp/js/views/settings.js`: names, active/inactive status and concise consequences for the eleven Boolean keys and `entropy.defaultMode`; use text nodes and a fallback for unknown keys.
- [x] Synchronize the Broadcast binaural checkbox after a successful Settings save in staged `webapp/js/views/broadcast.js`.
- [x] Update staged `webapp/css/app.css` for readable stacked help and narrow screens; keep the existing controls and save payload.
- [x] Update staged `webapp/index.html` with an introductory note explaining that some Original-Schalter are currently only stored.

### Task 3: Verify and promote

- [x] Run `node --check` on staged JavaScript and a synthetic browser save/sync check against an isolated staged preview on port 8107.
- [x] Back up exact destination bytes; copy only five verified webapp files to the promoted RadiWorks source, checking hashes and HTTP-served bytes afterward. Keep the older candidate as the prior milestone.
- [x] Read 8103 `/ping`, `/settings`, `/cases`, `/drafts`, `/databases` and virtual queue. Auto mode was active, so no restart or live setting change was made; browser behavior was checked in the isolated 8107 preview.
- [x] Record the tested result and remaining Peggotty/real-camera gates. Three RadiWorks-specific Module_Templates references were backed up and synchronized. Do not infer Aurelia approval.

### Task 4: Additive Area and Peggotty follow-up

- [x] Keep the numeric Area scan; add a separate 31 × 12 visual color overlay from local browser randomness with explicit non-Hotbits wording. Verify create, strengthen, reset and unchanged numeric scan in the synthetic browser.
- [x] Reject duplicate Peggotty script labels before execution with a clear 422 response in an isolated engine copy; full isolated suite: 292 passed, 2 skipped.
- [ ] Promote the Peggotty engine change only after a safe 8103 maintenance window; the live Auto mode and broadcasts are currently active.
