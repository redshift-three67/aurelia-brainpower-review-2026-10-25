# Operator Workbench Freeze-v7 Review Remediation — Freeze v8

**Date:** 2026-07-20  
**Branch:** `operator-workbench-phase1`  
**Baseline/HEAD:** `3271ff9366ab3fecb2a158913a0cc19ed6a06726`  
**Status:** REMEDIATION COMPLETE / VERIFIED / FREEZE V8 PENDING / NO-GO

## 1. Supersession

Freeze v7 remains immutable rejected evidence:

- manifest: `docs/reviews/2026-07-20-workbench-remediation-technical-freeze-v7.sha256`
- manifest SHA-256: `53b8d15a2a0ff79428af39b60757246d3d0e27f9c81f131eafd76bcdc6529693`
- scope: 66 files; aggregate `bcbd3c90f7a6df0ed99eb23791b6c728b2584aa05386abafeddd0c47ea8fda62`
- complete reviewer verdict: `REQUEST CHANGES`, `P0=0, P1=2, P2=2, P3=0`, zero drift
- report: `docs/reviews/2026-07-20-workbench-remediation-technical-review-v7-2.md`
- report SHA-256: `c17a4e4e09db3ebcc0515e5d882ea54c86c7b37e7f427f1b964cdeb10a551442`
- the other reviewer timed out without a verdict and counts as neither approval nor request-changes

Any remediation below supersedes Freeze v7. No prior review can be reused. Backup, commit, push, documentation GO and productive GO remain prohibited until a new freeze obtains two independent zero-finding approvals.

## 2. V8-A — POSIX process-group authority

RED contracts:

1. On POSIX, a productive leader may exit while a same-PGID descendant remains alive; the supervisor must remain authoritative.
2. A recovered service must report the job active while the stored PGID is live even if the supervisor PID has exited.
3. Stop must terminate the stored PGID after supervisor exit, while refusing PID/PGID reuse or foreign-group control.
4. A real POSIX test must prove leader exit, live group member, service restart, stop and confirmed descendant absence.

Design boundary: use process-group membership/liveness on POSIX rather than parent/child ancestry. Persist an independently validated supervisor identity plus PGID. Stop and recovery must fail closed if identity/provenance cannot be established.

## 3. V8-B — Total hardware-spawn convergence

RED contract: inject failure on the second `Process.start()` after the first process has emitted its started PID and is waiting at the pulse boundary. The API may return only after the first process is absent.

Design boundary: wrap process creation, every partial-start state and all later paths in one convergence `try/finally`. For every successfully started process: clear stop, release pulse, bounded join, terminate, bounded join, kill and final join as needed.

## 4. V8-C — Durable harmonization authority

RED contracts:

1. Job snapshots delegate to the shared durable publication primitive.
2. Stop markers delegate to the same primitive.
3. Injected publication failure leaves the prior canonical job bytes unchanged and removes private temp bytes.
4. Tests cover both JSON snapshots and stop-marker publication.

Design boundary: use `apps.web.durable_io.durable_write_bytes` for harmonization jobs and stop markers; do not duplicate the platform-specific durability implementation.

## 5. V8-D — Poll recovery and explicit scan retry

RED browser contracts:

1. A transient scan failure followed by success clears only that job/generation's degraded central `aria-live` state.
2. Harmonization does the same.
3. After scan polling pauses on 401/403, a visible manual retry resumes the same active job after reauthentication.
4. Stale generation/job callbacks cannot clear or resume newer authority.

Design boundary: track degradation ownership by domain, job and generation. Add a visible scan refresh/retry control analogous to harmonization; keep active job authority while polling is paused.

## 6. Verification and freeze order

1. Write and confirm each RED microgate.
2. Implement minimally; run neighboring tests after each gate.
3. Run static checks and changed-area matrix.
4. Run full Python suite and isolated full Playwright suite on isolated ports/runtime paths.
5. Remove generated artifacts and verify ports 8000/8765 free, port 8090 untouched, and tracked runtime data unchanged.
6. Update this plan to the exact verified lifecycle state, rerun final broad gates if required, and create Freeze v8.
7. Verify every hash, aggregate and dirty-scope equality.
8. Obtain two new independent read-only reviews with `P0=P1=P2=P3=0` and zero drift.
9. Only after dual technical approval may documentation gates and the verified external post-state shadow copy proceed.

## 7. Implemented closure and candidate evidence

- V8-A: the POSIX supervisor now evaluates live non-zombie members of its process group instead of relying only on ancestry. Recovery and status remain active when the supervisor has exited but the persisted PGID remains live; stop controls that PGID and confirms group absence. Mocked restart/stop contracts pass on Windows. A real POSIX leader-exit + supervisor-crash + restart + stop + descendant-absence test is included and host-gated; this Windows host has WSL2 enabled but no installed distribution, so that contract is not executable locally and is reported as skipped rather than fabricated.
- V8-B: all successfully started hardware processes enter one unconditional convergence `finally` boundary. A second-spawn failure now releases pulse/stop authority, joins, terminates, kills if required, and confirms absence of the first child before returning.
- V8-C: harmonization job snapshots and stop markers now use the shared durable platform publication primitive. Delegation and failed-publication preservation tests cover both authorities.
- V8-D: scan and harmonization poll failures carry job/generation/revision ownership. A successful same-authority poll clears only its own central degradation state. Scan auth pause exposes a visible, generation-bound manual status retry.

Candidate verification before final plan-state transition:

- focused v8 matrix: `94 passed, 1 skipped`;
- full Python suite: `1269 passed, 9 skipped`;
- isolated Chromium Playwright suite: `16 passed`;
- JavaScript syntax checks and `git diff --check`: pass;
- tracked harmonization runtime data unchanged;
- browser/runtime artifacts removed;
- ports 8000 and 8765 free; reserved Radi144 port 8090 remained on PID 17136 and untouched.

Exact-byte final broad gates after this lifecycle transition: focused matrix `94 passed, 1 skipped`; complete Python suite `1269 passed, 9 skipped`; isolated Chromium Playwright suite `16 passed`; static checks passed. Freeze v8 may now be created after artifact cleanup and exact scope capture.
