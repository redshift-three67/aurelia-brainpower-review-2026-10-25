# Operator Workbench Freeze-v21 Review Remediation — Freeze v22

**Date:** 2026-07-21  
**Branch/HEAD:** `operator-workbench-phase1` / `3271ff9366ab3fecb2a158913a0cc19ed6a06726`  
**Status:** REMEDIATION COMPLETE / FINAL EXACT-BYTE GATES PENDING / NO-GO

Freeze v21 remains immutable rejected evidence (`a2707d64bfd8d4da8e30bc25c6e0dda9d4fb2cec398a68c80a82c7064d8586d3`, 121 entries, aggregate `b947987d8a31c52d7cdca2f143d0f1e85763b68b6707c27f2a54618366ba935a`, population 122, zero drift). One reviewer approved with zero findings; the second reported P1=1/P2=2, therefore no technical approval.

## V22 closure

1. Scan status, stop, sync-trace and results now use a strict scan-specific ownership boundary. Missing/blank `owner_id` is fail-closed with HTTP 403; explicit matching owner remains allowed and foreign owner remains forbidden. Legacy data requires a separately evidenced owner migration before access.
2. `_signal_posix_authority()` now preserves a simultaneous primary signal/authority failure and every pidfd close failure in an ordered `BaseExceptionGroup`; no close failure is suppressed by an active exception.
3. Windows Job assignment/retention startup cleanup now always attempts both stable `Popen`-handle kill and wait. Kill/wait failures are grouped after the original Job setup failure and cannot mask it.
4. RED→GREEN adversarial tests bind all three remediations, including signal+close and retention+kill+wait concurrent failures.

Next: exact static/focused/full Python and Playwright gates, cleanup, Freeze v22 and dual read-only reviews. No GO, commit, push, backup, shadow copy or productive data.
