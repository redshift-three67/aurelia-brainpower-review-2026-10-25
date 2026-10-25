# Operator Workbench Freeze-v28 Review Remediation — Freeze v29

**Date:** 2026-07-21  
**Branch/HEAD:** `operator-workbench-phase1` / `3271ff9366ab3fecb2a158913a0cc19ed6a06726`  
**Status:** CANDIDATE VERIFICATION

## Immutable predecessor

Freeze v28 remains rejected. Its two zero-drift reports are preserved under `docs/reviews/2026-07-21-workbench-remediation-technical-review-v28-{1,2}.md`.

## RED→GREEN remediation

1. Workbench hardware measurements now use an EMF generation lease, revalidate authentication immediately before return and rebuild a disabled payload after generation revocation.
2. Hardware truth never samples implicitly; productive callers must supply an explicitly authorized calibration.
3. CLI workflow Step 05 is default-off and measures only through an explicit durable authority path with post-measure generation validation.
4. EMF generations use a durable sidecar counter. Main-state deletion/corruption cannot revive an old generation; legacy valid state migrates conservatively and corrupt generation authority fails closed.
5. Whitespace-only tenant/operator ownership is incomplete and globally reserving.
6. Windows start rollback reuses full Job Object convergence including `ActiveProcesses == 0`, wait/query/close grouping and handle cleanup.
7. POSIX convergence preserves TERM failures and continues with KILL only while authority remains unambiguous; authority ambiguity stops further signalling and all failures remain grouped.
8. Snapshot completion re-polls return code after process-tree convergence before persisting terminal status.
9. Scan WebSocket not-found and timeout frames revalidate current auth; timeout additionally re-reads ownership. Protected job IDs were removed from these error frames.
10. Diagnostics redact Cookie/Set-Cookie, access tokens and refresh tokens in addition to API keys and Authorization values.

## Verification contract

- Static, compile and JavaScript checks.
- Focused security/authority suites: `112 passed, 1 skipped` plus subsequent focused regressions.
- Full Python suite: `1384 passed, 9 skipped`.
- Isolated Playwright on `127.0.0.1:8765`.
- Remove browser/runtime artifacts and verify ports before Freeze v29.
- Require two independent `P0=P1=P2=P3=0`, zero-drift technical reviews before document gates.
