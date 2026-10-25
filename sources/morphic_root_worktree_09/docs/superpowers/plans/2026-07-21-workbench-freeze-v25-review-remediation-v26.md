# Operator Workbench Freeze-v25 Review Remediation — Freeze v26

**Date:** 2026-07-21  
**Branch/HEAD:** `operator-workbench-phase1` / `3271ff9366ab3fecb2a158913a0cc19ed6a06726`  
**Status:** REMEDIATION IN VERIFICATION

## Immutable predecessor

Freeze v25 remains rejected. Its manifest and both review reports are immutable evidence.

## RED → GREEN microgates

1. Dynamically bind WebSocket authorization and browser sessions to the current API-key generation.
2. Protect `/api/status` when authentication is configured.
3. Make EMF activation authoritative for profile, WebSocket, and workbench calibration measurement.
4. Remove raw hardware errors and sensitive process/owner/runtime fields from successful HTTP payloads.
5. Make harmonization polling single-flight per generation/job.
6. Make harmonization stop converge the worker process before publishing `stopped`.
7. Bind scan and harmonization ownership success/failure responses to exact generic payloads.
8. Run focused, full Python, static and browser gates; clean all generated artifacts; create a new immutable freeze only after green verification.

## Release gates

No document approval, external shadow copy, staging, commit, push, production data, or GO before two independent zero-finding technical reviews with exact hash/population binding and zero drift.
