# Operator Workbench Freeze-v10 Review Remediation — Freeze v11

**Date:** 2026-07-20  
**Branch:** `operator-workbench-phase1`  
**Baseline/HEAD:** `3271ff9366ab3fecb2a158913a0cc19ed6a06726`  
**Status:** REMEDIATION COMPLETE / FINAL EXACT-BYTE GATES PENDING / NO-GO

## Supersession

Freeze v10 remains immutable rejected evidence:

- manifest SHA-256 `713857a5a092984539febefe81688402b57b24cd96a5bf89806cb337061bf1e9`;
- 77 hashes, aggregate `3dc9980ec125b21fc3a604d747735e59364108eded5c913b55e51f3cc1e1370e`;
- review 1 `REQUEST CHANGES`, `P1=2`, report SHA-256 `b16f778d0041b10920ad14de601e2d6b831792fc16f8db8e94ef6150eea41cad`;
- review 2 `REQUEST CHANGES`, `P1=2`, report SHA-256 `c8bb02b12220bb5e1e587dd927f386359a4be22a01c76e286681bb25d2bcd7ad`.

## V11-A — Global ambiguity is fail-closed

Model target-group inspection as authoritative or ambiguous. If a member of the target PGID cannot expose provenance, abort the complete signal round before any pidfd is signalled. Recovery, snapshot, stop and rollback must never infer absence from an unreadable member. Tests cover mixed valid supervisor/member plus target-group `AccessDenied`, with zero signals and failed status.

## V11-B — Per-handle exit races and bounded convergence

Treat pidfd `ESRCH`/`ProcessLookupError` as already converged for that handle, continue signalling all remaining validated handles, aggregate every other error fail-closed, and re-enumerate within bounded TERM/KILL convergence loops until no proven member remains or an explicit timeout/error is returned. Tests cover stale first handle, live later handle, and a member appearing between rounds.

## V11-C — Pending scan start blocks New Case

A case reset must fail closed while `scanStartPending` is true, retaining the generation and eventual start-response authority. A delayed-start browser contract proves reset cannot discard a server-created job before its ID is captured.

## Gates

After RED→GREEN microgates, run focused/static/full Python and isolated full Playwright gates, clean all artifacts, verify ports and tracked runtime data, create immutable Freeze v11, and obtain two independent zero-finding/zero-drift reviews. No commit, push, document GO, backup or productive use before later gates.

## Candidate closure

- Target-PGID provenance inspection now distinguishes absence from ambiguity. Any `AccessDenied` for a target-group member aborts the whole handle collection before the first signal; stop persists `authority_ambiguous` and raises, while rollback also raises without signalling.
- pidfd `ESRCH`/`ProcessLookupError` is treated as convergence of only that handle. Remaining validated descriptors are still signalled; other errors are processed for every handle and then fail closed as an aggregate error.
- TERM/KILL convergence now performs bounded re-enumeration and repeated stable-handle rounds until authority is absent or an explicit error/timeout occurs. A fork-between-rounds contract requires a second KILL round.
- The reported delayed scan-start/New-Case race was already blocked by the shared mutation fence: `apiFetch(..., mutating=true)` increments `pendingMutations` before awaiting the POST, and reset refuses while it is nonzero. A delayed-response browser contract now proves generation and eventual job-ID authority are retained.
- Pre-final evidence: process/security matrix `41 passed, 1 skipped`; isolated Playwright `18 passed`; static checks pass.

After this plan transition, all exact-byte gates must run again before Freeze v11 is calculated.
