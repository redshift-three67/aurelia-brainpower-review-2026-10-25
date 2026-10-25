# Operator Workbench Freeze-v12 Review Remediation — Freeze v13

**Date:** 2026-07-20  
**Branch/HEAD:** `operator-workbench-phase1` / `3271ff9366ab3fecb2a158913a0cc19ed6a06726`  
**Status:** REMEDIATION COMPLETE / FINAL EXACT-BYTE GATES PENDING / NO-GO

Freeze v12 remains immutable rejected evidence: manifest `1d4931a9e14387ce891b8a27d39235889c671cc66b9375f2e78a78d7eb74d2fc`, 85 entries, aggregate `a51bbec277472ba434a645edd8d2862478938eed0f7529ce7d68628fc3d988ae`, zero drift. Reviews: `REQUEST CHANGES P1=2`; `REQUEST CHANGES P1=2,P2=1`.

## V13 closure

1. Unrelated processes are filtered by preliminary PGID before pidfd acquisition. A target candidate is then opened and PGID is revalidated against the stable-handle interval, so PID reuse cannot inherit the preliminary decision.
2. Supervisor `ProcessLookupError`/`ESRCH` during pidfd acquisition is treated as a normal exit race and token-bound descendants are still enumerated. Other supervisor acquisition failures become `ProcessAuthorityAmbiguousError`.
3. `_close_process_handles()` attempts every descriptor independently and returns all close failures. Enumeration cleanup catches `BaseException`, closes all transferred handles, and re-raises the original exception. Consumer cleanup also attempts every handle and only raises a cleanup failure when no original exception is active.
4. Adversarial tests prove foreign-PGID filtering before open, supervisor-exit continuation to a valid member, and all-handle close attempts after the first close error.

Pre-transition verification: static/compile/JavaScript checks pass; focused matrix `97 passed, 1 skipped`; full Python `1288 passed, 9 skipped`; isolated Playwright `18 passed`. The initial combined shell gate aborted before tests with `stdin is not a tty` and is not counted; each constituent gate was rerun independently and passed.

Next immutable lifecycle: rerun the exact static, focused, full Python and Playwright gates after this plan transition, clean artifacts and verify ports/runtime data, create Freeze v13, then obtain two independent zero-finding/zero-drift reviews. No commit, push, backup or productive use.
