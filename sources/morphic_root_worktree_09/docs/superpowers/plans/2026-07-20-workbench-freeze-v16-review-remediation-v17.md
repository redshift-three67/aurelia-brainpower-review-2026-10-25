# Operator Workbench Freeze-v16 Review Remediation — Freeze v17

**Date:** 2026-07-20  
**Branch/HEAD:** `operator-workbench-phase1` / `3271ff9366ab3fecb2a158913a0cc19ed6a06726`  
**Status:** REMEDIATION COMPLETE / FINAL EXACT-BYTE GATES PENDING / NO-GO

Freeze v16 remains immutable rejected evidence: SHA-256 `211449e60904aa4ee8a6d84846fcecbd9a77ab770777765ade9278cdaa6a8782`, 101 entries, aggregate `5b2b1d42152043ac0c33c310786121dc3944ad945ef35427d6ff5ebdae64c2f4`, population 102, zero drift. Reviews: one zero-finding APPROVE; one `REQUEST CHANGES P1=1,P2=1` for Windows numeric-PID termination and missing direct tri-state tests.

## V17 closure

1. Windows scans now receive a deterministic named Job Object derived one-way from the private process-group token. The gate supervisor is assigned through its already-open `Popen._handle` before the release file is published, so no productive descendant can spawn outside the job before assignment.
2. Normal stop and post-release rollback no longer invoke `taskkill /PID`. They terminate the stable in-memory Job handle or reopen the same named Job Object after recovery and call `TerminateJobObject`; missing authority is fail-closed ambiguity. Successful termination closes the authority handle.
3. Job assignment failure kills only the original supervisor through its already-open `Popen` handle before release, waits for confirmation, and aborts start.
4. Tests assert both Windows stop and rollback use `_terminate_windows_job`, never `subprocess.run/taskkill`, and remain bound to the captured Job handle even if the numeric PID is mutated to simulate reuse.
5. Direct strict-identity matrices cover readable match, readable mismatch, missing expected identity, `NoSuchProcess`, `ProcessLookupError`, `ESRCH`, `AccessDenied`, `EIO`, and generic errors.
6. Existing real Windows start/rollback tests exercise actual Job creation/assignment/termination; preliminary process matrix is `70 passed, 1 skipped`.

Next: exact static/focused/full Python and isolated Playwright gates, cleanup and port/runtime verification, immutable Freeze v17, and two independent zero-finding/zero-drift reviews. No commit, push, backup, document GO, external shadow copy, or productive use before all gates.
