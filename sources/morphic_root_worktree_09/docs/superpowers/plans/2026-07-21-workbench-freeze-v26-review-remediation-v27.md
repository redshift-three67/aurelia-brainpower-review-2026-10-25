# Operator Workbench Freeze-v26 Review Remediation — Freeze v27

**Date:** 2026-07-21  
**Branch/HEAD:** `operator-workbench-phase1` / `3271ff9366ab3fecb2a158913a0cc19ed6a06726`  
**Status:** CANDIDATE VERIFICATION

## Immutable predecessor

Freeze v26 remains rejected. Its reports are preserved as `technical-review-v26-1.md` and `technical-review-v26-2.md`.

## RED→GREEN remediation

1. Browser sessions use a monotone observed auth generation; key rollback and disable/reenable cannot resurrect old sessions.
2. EMF enable authority is atomic, cross-process, default-disabled and consumed by HTTP, WebSocket, Workbench and Harmonization paths.
3. Scan-start HTTP responses contain only lifecycle fields; commands, client data, paths, launcher metadata and parallel-export details remain internal.
4. Scan diagnostics are bounded and redact command values, paths, emails and secrets; HTTP, UI and WebSocket share the same projection.
5. Harmonization launches through the already hardened `LocalScanJobService` gate, giving its worker and descendants the same POSIX pidfd and named Windows Job Object authority as scan jobs.
6. Authority linkage is persisted before productive release; recovery is tri-state and ambiguity remains owner-reserving.
7. Stop publishes `stopped` only after full authority convergence; convergence failure persists `authority_ambiguous`.
8. Hardware cleanup attempts every join/terminate/kill path and preserves primary and cleanup failures in ordered `BaseExceptionGroup` form.

## Verification contract

- Static/compile/JavaScript checks.
- Focused security, authority, recovery, lifecycle and disclosure suites.
- Full Python suite.
- Isolated Playwright run on `127.0.0.1:8765` after port check.
- Remove browser/runtime artifacts before Freeze v27.
- Freeze exact dirty population and obtain two independent zero-finding reviews before any document gate.
