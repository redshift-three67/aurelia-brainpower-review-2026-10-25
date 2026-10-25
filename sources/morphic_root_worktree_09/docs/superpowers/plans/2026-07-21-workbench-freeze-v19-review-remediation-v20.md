# Operator Workbench Freeze-v19 Review Remediation — Freeze v20

**Date:** 2026-07-21  
**Branch/HEAD:** `operator-workbench-phase1` / `3271ff9366ab3fecb2a158913a0cc19ed6a06726`  
**Status:** REMEDIATION COMPLETE / FINAL EXACT-BYTE GATES PENDING / NO-GO

Freeze v19 remains immutable rejected evidence (`068a6c3ccb07271dce21967661d1814accac02b708f3ca101ad8206aba3ba8bc`, 113 entries, aggregate `0a0a6dcada4ade826fdbd553f318787d01828b7bbe5ff110d6f4b8412773e636`, population 114, zero drift).

## V20 closure

1. POSIX startup acquires a pidfd immediately after spawning the unreleased gate and before Creation-Time lookup. Identity failure signals only through that pidfd; no POSIX `Popen.kill()` remains. If pidfd acquisition fails, the unreleased gate is allowed to self-timeout and is reaped without a numeric signal.
2. The POSIX supervisor-crash adversarial test now acquires a pidfd and signals through `pidfd_send_signal`; stable service authority performs all survivor cleanup.
3. Windows outer Job authority is duplicated into the gate supervisor process with `DuplicateHandle` before release. The named Job Object therefore survives exit of the original service/handle-owner process while the gate remains active.
4. A real separate-process Windows test starts a scan, exits the original service process with `os._exit(0)`, then recovers, queries and terminates the named Job from a new process context.
5. Job retention failure closes the local handle; retention plus CloseHandle failures preserve both ordered errors.

Next: exact static/focused/full Python and Playwright gates, cleanup, Freeze v20 and dual reviews. No GO, commit, push, backup, shadow copy or productive data.
