# Operator Workbench Freeze-v11 Review Remediation — Freeze v12

**Date:** 2026-07-20  
**Branch/HEAD:** `operator-workbench-phase1` / `3271ff9366ab3fecb2a158913a0cc19ed6a06726`  
**Status:** REMEDIATION COMPLETE / FINAL EXACT-BYTE GATES PENDING / NO-GO

## Supersession

Freeze v11 remains immutable rejected evidence: manifest SHA-256 `2a089645bcc6e6265e013b48f13f31181e65c7cc09191184a5a81d8320e9427a`, 81 entries, aggregate `802b19686a013a37e4e51e9a535579cd7d9e4b0253353a6947edec3c1d2c4f9d`, zero drift. Reviews: `REQUEST CHANGES` (`P1=2`) and `REQUEST CHANGES` (`P1=3`).

## V12-A — Full-population authority decision

Enumerate the complete target PGID before deciding. A valid token records `found_valid` but never returns early. Every live target-PGID member with unreadable, absent or mismatched provenance makes the whole population ambiguous, independent of process order. Recovery, snapshot, stop and rollback use this same contract.

## V12-B — Acquisition errors and descriptor ownership

Only `ProcessLookupError`/`ESRCH` while opening a pidfd count as a vanished candidate. `EACCES`, `EPERM`, resource errors and every other acquisition failure fail closed before signalling. On every unsuccessful enumeration, close the current descriptor and every previously collected descriptor exactly once.

## V12-C — Ambiguity recovery transition

Under the existing service and per-job locks, a later complete, non-ambiguous absence proof atomically changes persisted `authority_ambiguous` to `stopped`. Until then, stop raises and New Case remains blocked.

## RED→GREEN evidence required

Cover valid-before-AccessDenied and reverse ordering; missing/mismatched token; pidfd-open `ESRCH` vs `EACCES`; accumulated-handle cleanup; mixed stop/rollback; recovery/snapshot ambiguity; and later confirmed-absence transition. Then full static, focused, Python and isolated Playwright gates; cleanup/ports; immutable Freeze v12; two independent zero-finding, zero-drift reviews. No commit, push, backup or productive use before all later gates.

## Candidate closure

- `_process_group_alive()` now scans the complete population, never returns on the first valid member, and treats unreadable, missing or mismatched provenance on every live target-PGID member as ambiguity.
- pidfd enumeration opens stable handles before validation, but only confirmed process disappearance is skippable. Every other acquisition, membership or provenance failure aborts before signalling.
- Any failed enumeration centrally closes both the current descriptor and every previously accumulated descriptor.
- The separately create-time-bound supervisor is excluded only after its stable handle and identity are validated; a reused numeric PID is not excluded.
- Stop persists ambiguity raised during both initial inspection and convergence. A later complete absence proof transitions `authority_ambiguous` to persisted `stopped` under the same service/job locks.
- Tests cover valid-before-ambiguous ordering, mismatched token, AccessDenied, `EACCES` versus `ESRCH`, complete descriptor cleanup, snapshot/recovery publication, stop/rollback refusal and ambiguity recovery.

After this transition all exact-byte gates must run again before Freeze v12 is calculated.
