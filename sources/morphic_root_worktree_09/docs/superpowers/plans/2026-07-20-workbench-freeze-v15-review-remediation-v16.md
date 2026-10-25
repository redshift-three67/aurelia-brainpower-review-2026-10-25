# Operator Workbench Freeze-v15 Review Remediation — Freeze v16

**Date:** 2026-07-20  
**Branch/HEAD:** `operator-workbench-phase1` / `3271ff9366ab3fecb2a158913a0cc19ed6a06726`  
**Status:** REMEDIATION COMPLETE / FINAL EXACT-BYTE GATES PENDING / NO-GO

Freeze v15 remains immutable rejected evidence: SHA-256 `de20792835dd7e68a7ef18e4aaf0cd3e76815f29dc950ab947bef751f6a009a6`, 97 entries, aggregate `f39ec0f9c5522b194160c4b2ead5aacf20a5601d23fdc9231c9f9ccaf176d853`, population 98, zero drift. Both reviews: `REQUEST CHANGES P1=1` for the same Creation-Time classification flaw.

## V16 closure

1. `_strict_process_identity_matches()` is a dedicated tri-state/exception-preserving boundary: `None` only for confirmed `ProcessLookupError`, `psutil.NoSuchProcess`, or `OSError(ESRCH)`; `False` only for a readable identity mismatch; every unreadable non-exit error propagates.
2. Supervisor post-open validation uses this strict boundary before PGID validation. Non-exit Creation-Time failures become `ProcessAuthorityAmbiguousError` before descendant enumeration or signalling. Confirmed exit still closes the supervisor handle and permits token-bound descendant convergence.
3. The initial locked `stop()` identity gate uses the same strict boundary and durably persists `authority_ambiguous` on unreadable identity, preventing the earlier swallowed-error path even before pidfd acquisition.
4. Adversarial full-stop tests make the first Creation-Time read succeed, then inject `psutil.AccessDenied` and `OSError(EIO)` after successful supervisor pidfd acquisition. They assert two reads, zero signals, exactly one supervisor-handle close, in-memory `authority_ambiguous`, and the same durable state.
5. Preliminary matrix: `60 passed, 1 skipped`; compile checks pass.

Next: exact static/focused/full Python and isolated Playwright gates, cleanup and port/runtime verification, immutable Freeze v16, and two independent zero-finding/zero-drift reviews. No commit, push, backup, document GO, external shadow copy, or productive use before all gates.
