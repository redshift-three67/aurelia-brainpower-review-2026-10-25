# Operator Workbench Freeze-v20 Review Remediation — Freeze v21

**Date:** 2026-07-21  
**Branch/HEAD:** `operator-workbench-phase1` / `3271ff9366ab3fecb2a158913a0cc19ed6a06726`  
**Status:** REMEDIATION COMPLETE / FINAL EXACT-BYTE GATES PENDING / NO-GO

Freeze v20 remains immutable rejected evidence (`c3fd537a0671861a4fc3378a8baed8f3ab9003cefc10321608f60091272d333d`, 117 entries, aggregate `10a5374277197a7f9c5b7e2b4ac6e9c419e7d29c62145a2a70540bfcbebd3087`, population 118, zero drift).

## V21 closure

1. `/api/privacy/clients` now uses the same `Depends(verify_api_key)` API-key/browser-session boundary as reports, scans and harmonization. A RED→GREEN contract proves anonymous access returns 401 when auth is configured while the no-key safe-view behavior remains compatible.
2. POSIX startup failure cleanup is consolidated: pidfd signal, close and process reaping are all attempted; primary identity failure plus every cleanup failure is retained in ordered `BaseExceptionGroup` evidence.
3. pidfd acquisition failure plus unreleased-gate wait timeout preserves both authority and timeout failures rather than masking either.
4. Creation-Time exceptions after pidfd acquisition follow the same stable cleanup boundary. Startup-pidfd close failure plus wait failure preserves all errors.
5. Product code uses symbolic `signal.SIGKILL`; no numeric signal fallback remains.
6. POSIX crash-injection pidfd close is in `finally`.
7. Deterministic tests bind exact Windows `DuplicateHandle` source/target/handle/access/inherit/options arguments and duplicate-plus-close double-failure ordering, supplementing the real separate-owner-process test.

Next: exact static/focused/full Python and Playwright gates, artifact cleanup, Freeze v21 and dual read-only reviews. No GO, commit, push, backup, shadow copy or productive data.
