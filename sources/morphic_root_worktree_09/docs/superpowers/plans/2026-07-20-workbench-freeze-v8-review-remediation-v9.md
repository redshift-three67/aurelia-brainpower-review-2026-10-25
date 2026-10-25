# Operator Workbench Freeze-v8 Review Remediation — Freeze v9

**Date:** 2026-07-20  
**Branch:** `operator-workbench-phase1`  
**Baseline/HEAD:** `3271ff9366ab3fecb2a158913a0cc19ed6a06726`  
**Status:** REMEDIATION COMPLETE / VERIFIED / FREEZE V9 PENDING / NO-GO

## 1. Supersession

Freeze v8 remains immutable rejected evidence:

- manifest SHA-256: `ddca521250a8b3f558a71ccc42617499e04a2ed770b8b6aaa3b6887c00c9a3ef`
- scope: 69 files; aggregate `a0554a01566728c34a3a00810bd25576b7eaf22c876ae1c3607d12ebb3536530`
- review 1: `REQUEST CHANGES`, `P0=0, P1=1, P2=0, P3=0`, report SHA-256 `19023a74649c6ccc82d74ae28583cce0978d620297fa73b66ca1d187469a5a5a`
- review 2: `REQUEST CHANGES`, `P0=0, P1=3, P2=1, P3=0`, report SHA-256 `3f32449cf6d1d327e7c82217ba14e54c588fa9cd59b93a52359e7a447bde93d4`
- both reviews proved identical branch, HEAD, all 69 hashes, aggregate, dirty population and null drift

Any remediation below requires a new Freeze v9 and two new independent zero-finding reviews. Backup, commit, push, documentation GO and productive GO remain prohibited.

## 2. V9-A — Restart-durable POSIX group provenance

Persist a cryptographically random group token with each scan. The gate injects it only into the productive process environment; descendants inherit it. After supervisor loss, group liveness and stop authority require both the stored PGID and a live non-zombie group member exposing the exact token. Numeric PGID alone never grants authority.

RED contracts:

1. foreign/reused live PGID with wrong or absent token is not `running`;
2. stop on that state never calls `killpg()`;
3. matching token preserves restart/stop authority after supervisor exit;
4. serialized state round-trips the token without exposing it in API snapshots.

## 3. V9-B — Post-release start rollback

Any exception after gate release must converge the full platform authority: Windows process tree/Job and POSIX process group, not only the supervisor PID. Absence must be confirmed before propagating the registration/publication failure.

RED contract: inject failure in the post-release `_snapshot()` durable write after a productive descendant has started; assert no supervisor or descendant remains.

## 4. V9-C — Confirmed hardware convergence

Cleanup must continue across per-process terminate/kill/join errors. After the final join, every started child is checked again. Any survivor raises an explicit `HardwareModulationOverrunError` carrying survivor PIDs; normal return is impossible while a child is alive.

RED contracts:

1. ineffective kill leaves a simulated survivor and raises explicit convergence failure;
2. cleanup failure for one child does not prevent cleanup of later children;
3. partial second-spawn failure still returns only after first-child absence.

## 5. V9-D — Scan poll single-flight

A domain/job/generation keyed in-flight authority merges concurrent scan polls. Manual retry and scheduled polling share this authority; one request may create at most one successor timer. Reset/generation change cannot let an older request clear the newer authority.

RED browser contract: concurrent manual retries against one paused job produce one fetch and one next-timer authority; a newer generation/job is not blocked by an older request.

## 6. Gates

For each block: RED proof, minimal implementation, focused GREEN and neighboring regression. Then static checks, focused matrix, complete Python suite, isolated complete Playwright suite, artifact cleanup, runtime-data and port verification, exact plan transition, final broad rerun, Freeze v9 hash/scope verification, and two independent read-only reviews. External shadow copy only after dual technical and document approval.

## 7. Implemented closure and candidate evidence

- V9-A: every scan now persists an unexposed random process-group token. The gate injects it only into the productive environment. Supervisor-less POSIX recovery/stop requires exact PGID plus token provenance; foreign/reused groups fail closed and are never signalled.
- V9-B: every start exception, including the post-release final snapshot, invokes full platform-authority rollback and confirms supervisor/descendant absence before propagation.
- V9-C: hardware cleanup isolates every join/terminate/kill failure, continues across all children, rechecks every child after final joins and raises a PID-bearing convergence error for any survivor.
- V9-D: scan polling is single-flight per job/generation across scheduled and manual retries; reset relinquishes old authority without allowing stale completion to clear newer ownership.

Candidate evidence before this final lifecycle transition:

- focused process/store/hardware matrix: `77 passed, 1 skipped`, followed by corrected neighboring matrix `38 passed, 1 skipped`;
- complete Python suite after all product/test changes: `1272 passed, 9 skipped`;
- isolated Chromium Playwright suite: `16 passed`;
- compile, JavaScript syntax and diff checks: pass;
- tracked runtime data remained unchanged; port 8090 remained untouched.

The exact-byte final broad gates must be repeated after this plan transition before Freeze v9 creation.
