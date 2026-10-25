# Operator Workbench Freeze-v27 Review Remediation — Freeze v28

**Date:** 2026-07-21  
**Branch/HEAD:** `operator-workbench-phase1` / `3271ff9366ab3fecb2a158913a0cc19ed6a06726`  
**Status:** CANDIDATE VERIFICATION

## Immutable predecessor

Freeze v27 remains rejected. Its two drift-free reports are preserved under `docs/reviews/2026-07-21-workbench-remediation-technical-review-v27-{1,2}.md`.

## RED→GREEN remediation

1. Missing EMF authority now fails closed for every Harmonization caller, including CLI/workflow paths.
2. EMF measurements use durable generations and are discarded after disable/rotation before publication.
3. EMF and scan WebSockets revalidate authentication after productive reads; scan ownership is re-read immediately before send.
4. Ownerless, blank-owner and ambiguous Harmonization jobs reserve global start authority.
5. Windows stop retains/query-checks the named Job Object until `ActiveProcesses == 0`; wait/query/close failures are grouped.
6. Parent-owned Windows handles close after gate registration/release while the gate retains durable named authority.
7. POSIX signalling and multiple pidfd-close failures retain all ordered errors.
8. Hardware cleanup protects every event/join/alive/terminate/kill/close operation, closes Process/Queue resources and groups all failures with the primary error.
9. Scan diagnostics redact whitespace-bearing paths and `Authorization: Bearer` credentials.

## Verification contract

- Static, compile and JavaScript checks.
- Focused authority/security/cleanup suites.
- Full Python suite: `1379 passed, 9 skipped`.
- Isolated Playwright: `18 passed` on `127.0.0.1:8765`.
- Remove browser/runtime artifacts and verify ports before Freeze v28.
- Require two independent `P0=P1=P2=P3=0`, zero-drift technical reviews before document gates.
