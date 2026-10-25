# Operator Workbench Freeze-v17 Review Remediation — Freeze v18

**Date:** 2026-07-21  
**Branch/HEAD:** `operator-workbench-phase1` / `3271ff9366ab3fecb2a158913a0cc19ed6a06726`  
**Status:** REMEDIATION COMPLETE / FINAL EXACT-BYTE GATES PENDING / NO-GO

Freeze v17 remains immutable rejected evidence (`ccb996eb4c167b525581d384f44c6dcfe3e97a94043504903a5731fe092948ce`, 105 entries, aggregate `92309bc9a7b86d16774f861ad5cb680505b7fc092e7c4b4d4d930905f45746aa`, population 106, zero drift). Both reviews requested changes.

## V18 closure

1. Windows Job Object activity is queried via `QueryInformationJobObject`; Recovery, Snapshot, Stop and Rollback use this authority independently of supervisor PID state.
2. Missing or unreadable named Job authority remains durable `authority_ambiguous`; `stopped` requires confirmed inactive Job authority or successful `TerminateJobObject`.
3. Held Windows handles close exactly once after successful termination or natural terminal activity; close failures propagate rather than being discarded.
4. POSIX authority is token-wide across same-owner processes, not PGID-only. Inherited private-token descendants remain discoverable after `setsid()`, `setpgid()` or `start_new_session=True`; every selected PID is opened as pidfd and token-revalidated post-open.
5. Original PGID foreign-token members still fail closed. Same-owner unreadable provenance is globally ambiguous; other-owner processes are excluded before environment access.
6. Real descendant recovery test now starts the child in a new POSIX session. Numeric `taskkill /PID` cleanup was removed from all tests; cleanup retries stable service authority only.
7. Tests cover supervisor-ended Windows rollback, unreadable Job authority persistence/no termination, real restart Job stop, and natural terminal handle close.

Next: exact static/focused/full Python and isolated Playwright gates, cleanup, immutable Freeze v18, two independent zero-finding technical reviews. No commit, push, backup, document GO, external shadow copy or productive data.
