# Operator Workbench Dogfood Remediation Implementation Plan

> **For Hermes:** Execute macroblocks in order with strict RED→GREEN microgates. Do not commit, push, back up, or touch ports 8000/8090. A final post-state copy is forbidden before approvals.

**Goal:** Close all 26 confirmed dogfood findings without changing analysis/scoring semantics or weakening privacy, tenant, ownership, consent, or hardware-truth boundaries.

**Architecture:** Fix contract mismatches at their source, make the Web scan UI describe the actual `top3-scan` stages rather than the separate 12-step orchestrator, bind reports and harmonization explicitly, and make navigation/accessibility state deterministic. Keep the explanatory 12-step page separate and CSP-safe.

**Tech Stack:** FastAPI/Pydantic, vanilla JavaScript, pytest Node-VM DOM harnesses, Playwright browser acceptance.

## Safety and scope

- Active worktree only: `C:\morphic_v1\.worktrees\operator-workbench-phase1`.
- Protected live ports: 8000 and 8090; do not restart or modify them.
- Browser acceptance uses a fresh free loopback port and isolated runtime/report roots.
- Synthetic test identities only; exact synthetic cleanup after evidence capture.
- No scoring, profile, database, catalog activation, productive group activation, or source import mutations.
- No pre-approval backup. Freeze/review evidence stays in-repository until two technical approvals and document approvals.

## Macroblock A — Bootstrap, form and feedback contracts

1. RED: health object shape renders correct profile/database metrics and does not flip OK to error.
2. GREEN: normalize health object/legacy shapes in one helper.
3. RED: optional context reload targets controls associated via `form="scan-form"`.
4. GREEN: shared associated-control lookup.
5. RED: FastAPI detail arrays become safe actionable messages; template feedback uses the correct helper signature.
6. GREEN: normalize error details and template state.
7. RED/GREEN: semantic source `<ul>`, full-width styled textareas, CSP-safe report preview shell.

Files: `apps/web/static/{index.html,app.js,workbench-api.js,app.css}`, `apps/web/reports.py`, focused `tests/test_workbench_*` modules.

## Macroblock B — Truthful scan stages, trace and results

1. RED: scan status exposes canonical actual stage IDs; no `harmonization` stage in `top3-scan` telemetry.
2. GREEN: track completed stage IDs in `scan_jobs.py`; preserve existing human labels additively.
3. RED: completed scan does not mark a separate harmonization step complete.
4. GREEN: replace misleading 12-step execution timeline with actual Web-scan stage timeline and explanatory link.
5. RED/GREEN: status polling remains read-only; one explicit authenticated, owner-checked terminal POST finalizes the minimized run trace exactly once.
6. RED/GREEN: Phase 8 renders profile names, scores and top resonances, not only counts.

Files: `apps/web/{scan_jobs.py,main.py,contracts.py}`, `apps/web/static/{index.html,app.js,workbench-render.js,app.css}`, tests for scan jobs, web runtime, results DOM and timeline DOM.

## Macroblock C — Reports and harmonization

1. RED/GREEN: launcher export root and report catalog derive from the same tenant-aware function.
2. RED/GREEN: `/api/reports` returns HTML/JSON/TXT/PDF grouped entries; client UI handles all preview modes.
3. RED/GREEN: reports refresh automatically after scan completion.
4. RED: harmonization start requires a valid selected report ID and binds operator/tenant/report metadata.
5. GREEN: validate report in current tenant catalog and pass binding through service/worker metadata.
6. RED/GREEN: duration metadata equals `duration_factor × 21`; remove contradictory client calculation.
7. RED/GREEN: make Solfeggio semantics honest—use it as the selected target basis or label it metadata-only; preserve explicit target frequency as authoritative.

Files: `apps/web/{launcher.py,main.py,contracts.py,harmonization.py,reports.py}`, `services/harmonization_worker.py`, frontend files and focused tests.

## Macroblock D — Navigation, review, reset and accessibility

1. RED/GREEN: phase readiness gates prevent forward jumps into run/results/details/reports/harmonization before prerequisites, while backward navigation remains available.
2. RED/GREEN: review displays every scan-affecting option and both consent states without sensitive persistence expansion.
3. RED/GREEN: New Case clears form values, consents, preview/results/trace/report/job state, timers and status panels.
4. RED/GREEN: stepper uses `aria-controls`, panel `aria-labelledby`, roving tabindex, focus movement, Home/End and `scrollIntoView`.
5. RED/GREEN: progressbar semantics and status text for scan stages.
6. RED/GREEN: choice cards use radio/pressed semantics; mobile gets bottom navigation/progressive disclosure for advanced group controls.
7. RED/GREEN: fallback stepper remains directly clickable and `currentStepId` stays synchronized.

## Macroblock E — CSP-safe explanatory 12-step page

1. RED: CSS and JS assets must return 200 with correct media types; no external fonts, inline script/style/event handlers.
2. GREEN: serve dedicated assets under `/static`, align DOM/CSS class names, use button navigation.
3. RED/GREEN: keyboard/focus/ARIA/reduced-motion behavior.
4. RED/GREEN: reconcile Top-N, levels, profile count wording, PDF path and explain that this is the separate `workflow-scan` model, not current Web `top3-scan` telemetry.

## Regression ladder and acceptance

1. New regression modules.
2. Existing focused Workbench/Web/Group/Harmonization tests.
3. `node --check` for all changed JS.
4. `git diff --check` and Python compile checks.
5. Full `pytest tests -q`, persist exact output.
6. Isolated Playwright desktop/tablet/mobile acceptance, real shortest safe scan, real impulse/pause/stop, exact cleanup.
7. Verify ports 8000/8090 untouched and worktree scope only.

## Freeze and approvals

1. Create technical freeze with SHA-256 manifest for plan, implementation and tests.
2. Dispatch two independent read-only reviewers against identical freeze hash; require start/end hash equality and P0=P1=P2=P3=0.
3. Any patch supersedes the freeze and reviews; repeat.
4. After technical approvals, update gate/status documentation, create document freeze and two document reviews.
5. No external post-state shadow copy before all approvals; only then create and independently reverify if the user authorizes the external destination.

## Implementation result — 2026-07-19

All five macroblocks were implemented on baseline `3271ff9366ab3fecb2a158913a0cc19ed6a06726` without committing, pushing, restarting port 8000, or touching port 8090.

Closed finding groups:

- Findings 2, 6, 10, 13, 18 and 26: corrected bootstrap, associated-form reload, template/error feedback, textarea styling and source-list semantics.
- Findings 4, 7, 19, 21, 24 and 25: actual Web-scan stage IDs, terminal trace updates, truthful stage UI, result details, report refresh and clickable fallback navigation.
- Findings 3, 11, 12, 20, 22 and 23: aligned report/export roots, all supported formats, CSP-safe preview styling, mandatory report binding, effective Solfeggio target and 21-minute duration factor.
- Findings 5, 8, 9, 14, 15 and 17: privacy-complete new-case reset, readiness gates, complete review, optional mobile disclosure, keyboard/ARIA semantics and safe polling exemption.
- Findings 1 and 16: rebuilt `/workflow-stepping` as a CSP-safe, self-hosted, interactive and contract-correct explanatory surface.

Final verification evidence:

- Full suite after review remediation: `1198 passed, 8 skipped in 174.47s`.
- Review-regression and affected contract suites: `72 passed in 1.78s`; final focused review/scan/report subset: `17 passed in 0.82s`.
- Final isolated Playwright acceptance on port 8765: `3 passed in 6.9s` (desktop gates/review/reset, mobile disclosure/overflow, workflow-stepping CSP/navigation).
- `node --check`: `app.js`, `workbench-api.js`, `workbench-render.js`, `workbench-state.js`, `workflow-stepping.js` passed.
- `git diff --check` passed; only line-ending normalization warnings were emitted.
- Post-acceptance: port 8765 free; protected ports 8000 (PID 22532) and 8090 (PID 3304) remained listening and were not restarted.
- Temporary Playwright `node_modules` and `test-results` were removed; the small acceptance spec/config remain under ignored `codex_tmp/acceptance-20260719/` as local evidence.

No release/GO is implied until the freeze and independent approval gates below are complete.

### Superseded freeze and review remediation

Technical freeze v1 (`2aaa2a560f2024f54aec299f246cf947c7d756cd5ad0cdce4e4c694a1021a4b8`) was reviewed twice without drift and rejected. It is permanently superseded, not reused as approval evidence. The review findings were closed with new RED→GREEN coverage:

- New-case reset now invalidates in-flight async continuations with a generation token and clears associated controls, both consent checkboxes, group-consent identity/validity/retention state, and active consent identifiers.
- Scan stage order is monotonic; only a stage actually left is marked complete, and the final current stage is closed only at terminal completion.
- Safe GET polls no longer write the run trace. A distinct authenticated/owner-checked terminal `POST .../sync-trace` performs the mutation once.
- Harmonization report, mode, tenant and operator bindings are persisted in the worker job JSON, survive service reconstruction, and are ownership-checked before status disclosure or stop side effects.
- Harmonization request ambiguity was removed: duration is derived solely from `duration_factor * 21`, while Solfeggio uses the authoritative `target_frequency` only.
- Choice cards now implement one radio semantic with roving tabindex and arrow navigation; generated step controls label their panels, and fallback navigation preserves a real step ID.

Freeze v2 must include every code, test and documentation change above and receive two fresh, independent, zero-finding reviews.

### Superseded freeze v2 and second review remediation

Technical freeze v2 (`8de943c773ad91a4bc7a518b77e143978f6d2790dc43b07a40166640e7a0afdf`) was also reviewed twice without drift and rejected. It is permanently superseded. The second review round was closed with further RED→GREEN gates:

- The v2 candidate added generation checks to preview/start/results/reports/harmonization, sensitive loaders and draft/consent/policy mutations. Freeze-v3 review later proved that in-flight server mutations and bootstrap lifecycle still required the stronger F3-02 boundary below.
- New-case reset clears the file picker, restores profile/entropy/Solfeggio backing values and visible cards together, and restores every consent-dependent action button to a disabled state.
- The v2 candidate removed historical fallback and constrained directory selection by job time. Freeze-v3 review later proved mtime selection was still ambiguous for concurrent same-client runs; F3-01 replaces it with exact process-emitted artifacts.
- Terminal scan snapshots unconditionally flush unterminated stdout/stderr fragments before final telemetry is computed.
- Terminal trace synchronization is authenticated, owner-checked and terminal-only. The v2 once-only check was process-local; F3-11 adds the cross-process serialization required by Freeze-v3 review.
- Productive and visible stages now use `export → synergy → remedy → interpretation → trend` consistently.
- Harmonization JSON writes are atomically replaced and use a durable stop marker. Freeze-v3 review identified the remaining marker-check→replace race; F3-04 adds process serialization and load-time marker reconciliation.
- Generated profile and entropy radio groups have accessible names; hidden backing selects are removed from keyboard focus.

Post-remediation evidence for freeze v3:

- Full suite: `1204 passed, 8 skipped in 167.06s`.
- Affected backend/frontend/worker suite: `72 passed in 2.56s`; focused final report/review gate: `14 passed in 0.65s`.
- Strengthened Playwright acceptance: `3 passed in 4.3s`, including consent, file-picker, backing-select, visible-choice-card and disabled-action reset assertions.
- JavaScript syntax checks and `git diff --check` passed.
- Isolated port 8765 was stopped and verified free after acceptance; ports 8000 and 8090 were not restarted.

Freeze v3 had to include all implementation, regression-test and documentation changes from both rejected rounds and receive two fresh independent reviews with `P0=P1=P2=P3=0` and zero drift.

### Superseded freeze v3 and third review remediation

Technical freeze v3 (`38ec0dd6fbace72a04910738e0750a8d7643ca2079ccf9d60d72cbb3188911b1`) was reviewed twice without drift and rejected. It is permanently superseded and cannot provide approval evidence. Reviewer 1 reported `P0=0, P1=4, P2=3, P3=1`; reviewer 2 reported `P0=0, P1=5, P2=3, P3=1`.

The findings were deduplicated into the executable F3-01 through F3-13 gates in `2026-07-19-workbench-freeze-v3-review-remediation-v4.md`. The current unapproved v4 candidate includes these remediation contracts:

- Scan result attribution uses only artifact paths emitted by the exact child process, validates that they exist under the job export root, and does not infer a newer same-client session or sibling export.
- Scan stop terminates the Windows process tree or POSIX process group. New Case waits for authoritative scan and harmonization terminal responses before clearing local references and is blocked while a mutating request is pending.
- Bootstrap and case-sensitive continuations capture one case generation and reject stale responses after reset.
- Pending and running harmonization jobs can be stopped. Stop marker publication, JSON snapshots and stale worker saves are process-serialized; marker reconciliation remains authoritative on load.
- Pulse/pause request values are bounded, impulse has a pre-check, pause is interruptible in short slices, and interrupted work cannot be counted as a completed cycle.
- Scan status, results and stop share configured API-key and ownership boundaries; a foreign-owner rejection occurs before the stop side effect.
- Report roots and catalogs remain bound to the tenant resolved for the app runtime even if process environment variables later change.
- Terminal run-trace finalization is serialized across independent processes, not only threads or one store instance.
- Productive multi-profile telemetry cannot advance into export/post-analysis stages until the final Phase-2 profile completes.
- New Case clears result metrics, report iframe/title/meta/link, group strength and sensitive controls; report preview can render and unhide again for the next case.
- Rerendered radio cards retain focus on the new live node and implement Arrow/Home/End behavior; harmonization progress exposes and resets `aria-valuenow`.
- Browser acceptance is now stored under `tests/browser/` so it is part of the reviewable freeze scope instead of remaining only in an ignored local harness.

Pre-freeze evidence already obtained for the candidate included the final API-helper compatibility nodes (`3 passed`), the consolidated backend/concurrency matrix (`71 passed`), and the reviewable Playwright matrix (`5 passed`). Those values remain historical Freeze-v4 evidence only.

### Superseded Freeze v4 and fourth review remediation

Freeze v4 (`9d0a26a13577ef4c86bca1309fd2672123b7675dd4c4b13393ac76997b7843ad`) covered 41 files and was verified 41/41 without drift. Both independent reviews rejected the candidate:

- Review 1: `REQUEST CHANGES`, `P0=0, P1=5, P2=2, P3=1`.
- Review 2: `REJECT`, `P0=0, P1=1, P2=2, P3=2`.

The full byte-exact reports are preserved as:

- `docs/reviews/2026-07-19-workbench-remediation-technical-review-v4-1.md`
- `docs/reviews/2026-07-19-workbench-remediation-technical-review-v4-2.md`

Freeze v4 is permanently superseded. The consolidated causes and executable closure contracts are defined in `2026-07-19-workbench-freeze-v4-review-remediation-v5.md`. The v5 candidate adds scan single-flight, pending harmonization polling, failure-atomic New Case behavior, verified process-tree cancellation, cooperatively bounded hardware modulation, stop-versus-cycle-commit serialization, complete lifecycle/preview DOM scrubbing, production-shaped preview metadata and a behavioral read-only-GET rate-limit boundary.

No release claim is based on intermediate v5 checks. A fresh focused matrix, complete suite, static checks and isolated eight-scenario Playwright run must all pass on unchanged final candidate bytes before Freeze v5. Freeze v5 then requires two new independent read-only reviews with zero drift and `P0=P1=P2=P3=0`.
