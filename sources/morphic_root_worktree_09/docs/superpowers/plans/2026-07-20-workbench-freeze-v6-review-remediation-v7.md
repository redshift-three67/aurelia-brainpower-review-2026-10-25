# Operator Workbench Freeze-v6 Review Remediation — Freeze v7

**Date:** 2026-07-20  
**Branch:** `operator-workbench-phase1`  
**Baseline/HEAD:** `3271ff9366ab3fecb2a158913a0cc19ed6a06726`  
**Status:** REMEDIATION COMPLETE / VERIFIED / FREEZE V7 PENDING / NO-GO

## 1. Supersession and evidence

Freeze v6 remains immutable historical evidence:

- manifest: `docs/reviews/2026-07-20-workbench-remediation-technical-freeze-v6.sha256`
- manifest SHA-256: `279a2d365636a9989eb1a9e6cfae74d7eaa9f248ec3e3c8b3c1cb2bae3147e39`
- aggregate: `d1758106368f9449f4e2b93873f3a1bbedfdd07229dda70a4dd735caf9027b45`
- scope: 58 files; review population: 59
- successful reviewer: `REQUEST CHANGES`, `P0=0, P1=4, P2=4, P3=0`, zero drift
- complete successful review preserved byte-for-byte at `docs/reviews/2026-07-20-workbench-remediation-technical-review-v6-2.md`; SHA-256 `cd1f93ba0e590b4bec597e3c98bcff03fbd3ac43bfbc06bdb1626b6d780454fe`
- the other reviewer timed out without a summary or verdict and counts as neither approval nor request-changes

Any remediation below supersedes Freeze v6. No v6 approval may be reused. No backup, commit, push, documentation GO or productive GO is permitted before a new freeze and two new zero-finding reviews.

## 2. Root-cause gates

### V7-A — Pre-execution durable scan registration and process-tree authority

Closes F-01, F-02 and their F-08 evidence gaps.

RED contracts:

1. A scan command cannot perform productive work before a durable `starting` registration exists.
2. Injected controller failure after process creation but before release leaves no productive orphan; the gate process times out safely.
3. After controller restart, a live descendant remains controllable even after the originally requested command exits.
4. Cross-instance snapshots are proven with independent spawned processes, not only threads.
5. PID, creation time and process-group/tree identity remain mandatory and PID reuse stays fail-closed.

Minimal design:

- launch a small process-gate supervisor rather than the productive command directly;
- persist PID/creation-time/group/owner/log/command state before publishing a release token;
- supervisor starts productive work only after release and remains alive until its full descendant tree has converged;
- recovered stop targets the supervisor/process group/tree, including the leader-ended case;
- terminal state and cleanup are persisted atomically.

### V7-B — Killable hardware-modulation isolation

Closes F-03 and its F-08 evidence gap.

RED contracts:

1. A deliberately noncooperative CPU/GPU/RAM task is physically terminated after pulse deadline plus grace.
2. No child process or executor thread remains alive when the API returns an overrun.
3. Cooperative CPU/GPU/RAM tasks still start in one pulse window, receive one shared stop event and return their results.
4. Worker process termination is bounded and owner/tenant authority can subsequently converge.

Minimal design: move independently selected hardware paths into supervised killable child processes. Signal a shared multiprocessing stop event at pulse end; join through a bounded grace; terminate/kill survivors; join them before returning. Do not use non-daemon executor threads as the isolation boundary.

### V7-C — Restart-safe harmonization ownership and stop-aware error commit

Closes F-04, F-05 and their F-08 evidence gaps.

RED contracts:

1. Persist worker PID plus process creation time/nonce.
2. PID reuse cannot preserve an active-job reservation.
3. Composition-root startup recovers interrupted jobs.
4. Recovery runs under the same registry/job lock immediately before owner/tenant reservation.
5. Stop winning between exception decision and persistence produces stored `stopped` and no `error` event.
6. Confirmed `error` still stores and publishes exactly one `error` event.

### V7-D — Visible bounded polling degradation

Closes F-06.

RED contracts for scan and harmonization polling:

1. transient failures publish a visible, `aria-live` degraded/offline state;
2. retries use bounded exponential backoff rather than an endless fixed five-second loop;
3. authentication failures terminate automatic polling and require explicit re-authentication/retry;
4. a subsequent successful poll clears the degraded state without reviving an obsolete case generation.

### V7-E — Crash-durable filesystem replacement

Closes F-07.

RED contracts:

1. scan-state temporary bytes are flushed before publication;
2. publication uses a durable replace primitive: POSIX file fsync + rename + parent-directory fsync; Windows write-through replacement with bounded sharing retries;
3. workbench stores use the same durable boundary;
4. injected failure before publication leaves prior authority bytes unchanged and removes only the private temporary file;
5. corrupt canonical JSON remains fail-closed and byte-identical.

### V7-F — Behavioral evidence completion

Closes the remaining F-08 items:

- real independent-process scan polling;
- process-gate crash injection;
- leader-ended/live-descendant restart stop;
- hardware child absence after overrun;
- harmonization startup/pre-reservation recovery and PID reuse;
- stop-vs-exception terminal publication;
- report-catalog parallel single-flight, cache-error release and TTL invalidation.

## 3. TDD execution order

1. V7-E durable primitive first, because V7-A registrations depend on it.
2. V7-A scan process gate and restart/tree contracts.
3. V7-C harmonization identity/recovery/error commit.
4. V7-B killable hardware isolation.
5. V7-D browser polling degradation.
6. V7-F remaining report-cache and independent-process evidence.
7. Focused matrix, full Python suite, static checks and full isolated Playwright suite.
8. Remove generated browser artifacts and verify ports 8000/8765 free and port 8090 untouched.
9. Create Freeze v7 containing Freeze v6, the complete successful v6 review, this plan, all product/test changes and transitive dependencies.
10. Verify hashes/scope/aggregate and obtain two new independent read-only reviews with `P0=P1=P2=P3=0` and zero drift.

## 4. Release status

Current status is `NO-GO / Freeze v6 rejected / Freeze v7 candidate verified`. Real client data, formal acceptance, backup and productive GO remain prohibited until a hash-bound Freeze v7 receives two independent drift-free reviews with `P0=P1=P2=P3=0`.

## 5. Implemented closure and final candidate evidence

Implemented closure:

- V7-A: durable pre-execution scan registration, gated productive release, persistent supervisor identity, Windows Job Object process-tree authority, restart recovery, PID-reuse checks, leader-ended descendant stop, and spawned-process polling evidence.
- V7-B: CPU/GPU/RAM/WebSocket modulation paths run in killable spawned processes with one shared pulse boundary, cooperative stop event, bounded grace, terminate/kill fallback, final joins and explicit survivor-PID evidence.
- V7-C: harmonization jobs persist worker creation time; recovery validates PID identity, runs at FastAPI lifespan startup and immediately before owner/tenant reservation under registry authority; error publication uses the same stop-aware terminal commit boundary as completion.
- V7-D: scan and harmonization polling expose visible degraded/auth-paused states, use bounded exponential retries and preserve generation/job authority.
- V7-E: scan and workbench JSON stores use one durable publication primitive with file flush, POSIX parent-directory flush, Windows write-through replacement and bounded sharing retries.
- V7-F: behavioral tests now cover real spawned scan pollers, gate-registration failure, leader-ended descendants, noncooperative child absence, production hardware paths, startup/pre-reservation recovery, PID reuse, stop-vs-error publication, report-cache single-flight/error release/TTL invalidation, and browser polling failures.

Final candidate verification after all product, test, harness and plan changes:

- changed-area matrix: `78 passed`;
- full Python suite: `1264 passed, 8 skipped`;
- isolated Chromium Playwright suite: `15 passed`;
- `git diff --check`: pass (line-ending conversion warnings only, no whitespace errors);
- Python compile checks for all v7 Python modules: pass;
- `node --check` for `app.js` and `workbench.spec.js`: pass;
- generated browser/runtime artifacts removed;
- tracked `data/harmonization_jobs` population unchanged after isolated tests;
- ports 8000 and 8765 free after QA; reserved Radi144 port 8090 remained on PID 17136.

Next permitted action: create and independently verify Freeze v7. No repository mutation is permitted while its two read-only technical reviews are running.
