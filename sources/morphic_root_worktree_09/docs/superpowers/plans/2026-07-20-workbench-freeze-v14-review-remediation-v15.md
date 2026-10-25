# Operator Workbench Freeze-v14 Review Remediation — Freeze v15

**Date:** 2026-07-20  
**Branch/HEAD:** `operator-workbench-phase1` / `3271ff9366ab3fecb2a158913a0cc19ed6a06726`  
**Status:** REMEDIATION COMPLETE / FINAL EXACT-BYTE GATES PENDING / NO-GO

Freeze v14 remains immutable rejected evidence: SHA-256 `ff06cb2902f5a43cefee09afc3bda9971d5a558efc1576b6f508269b85513f68`, 93 entries, aggregate `3e7dd5ca5c85ba1cc87a26d79f909125da7448f2e284a8590af13c0bca1bb601`, population 94, zero drift. Reviews: `REQUEST CHANGES P2=1`; `REQUEST CHANGES P1=1,P2=1`.

## V15 closure

1. Candidate and supervisor pidfd acquisition now classify every normal non-exit `Exception` as `ProcessAuthorityAmbiguousError`; only `ProcessLookupError` and `OSError(ESRCH)` remain local exit races. This makes `stop()` persist `authority_ambiguous` before returning an error.
2. Supervisor post-open identity/PGID revalidation is isolated. Exit/ESRCH closes the supervisor handle exactly once and continues to token-bound descendants. Every other normal revalidation failure is ambiguous before any signal.
3. Tests prove generic `ValueError` through the complete locked stop/persistence path, supervisor disappearance after successful open with descendant signal and exact supervisor close, post-open `EACCES` with no signal plus durable ambiguity, and candidate generic acquisition failure.
4. The primary-start-error test now creates a real `KeyboardInterrupt` traceback and verifies that the grouped primary retains the same traceback object and originating frame.
5. Preliminary matrix: `58 passed, 1 skipped`; compile checks pass.

Next: exact static/focused/full Python and isolated Playwright gates, artifact/runtime/port cleanup, immutable Freeze v15, and two independent zero-finding/zero-drift reviews. No commit, push, backup, document GO, external shadow copy, or productive use before all gates.
