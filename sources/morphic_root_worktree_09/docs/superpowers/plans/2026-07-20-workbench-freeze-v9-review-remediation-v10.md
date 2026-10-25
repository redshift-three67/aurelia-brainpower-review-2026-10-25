# Operator Workbench Freeze-v9 Review Remediation — Freeze v10

**Date:** 2026-07-20  
**Branch:** `operator-workbench-phase1`  
**Baseline/HEAD:** `3271ff9366ab3fecb2a158913a0cc19ed6a06726`  
**Status:** REMEDIATION COMPLETE / FINAL EXACT-BYTE GATES PENDING / NO-GO

## 1. Supersession

Freeze v9 remains immutable rejected evidence:

- manifest SHA-256 `3c30e1b4927e91aeffbc23067fa0bfc490e549d4e52695d08faaf8035e292969`;
- 73 hashes, aggregate `886ff1f9513234799619592ee1cbdb464d34d9a9c200dae074df9c418d80859a`, exact population and zero review drift;
- review 1: `REQUEST CHANGES`, `P0=0,P1=0,P2=1,P3=2`, report SHA-256 `02807b8beb8fc276e1f3e4c22b85a5cb672783d173aaba04729c9bdace1d5c99`;
- review 2: `REQUEST CHANGES`, `P0=0,P1=1,P2=1,P3=0`, report SHA-256 `7e8f2f00f56d8ee56a8bd574b3763ccb230203181fed32ce9546d51e121b80c6`.

## 2. V10-A — Non-argv token transport and owner-only persistence

- remove the token from the gate command line;
- transport it via a non-argv local channel and remove the gate-only copy before spawning productive work;
- enforce owner-only POSIX permissions on runtime directories and token-bearing durable files;
- document that hostile processes under the same OS account are outside the local trust boundary;
- tests must prove token absence from API and gate argv plus `0700` directory / `0600` state semantics on POSIX.

## 3. V10-B — Race-free final POSIX signalling

Numeric `killpg()` is permitted only while the positively identified live supervisor pins that process group. After supervisor loss, never signal a numeric group. Enumerate token-proven members and signal stable kernel process handles (Linux pidfds); if stable handles are unavailable, fail closed rather than signal. Repeat bounded enumeration until no proven member remains and confirm absence.

RED contracts:

1. a group changing from proven to foreign immediately before signalling receives no signal;
2. supervisor-less stop never calls `killpg()`;
3. stable handles target only token-proven members;
4. AccessDenied while reading an environment produces failed/not-running status and no signal.

## 4. V10-C — Complete single-flight adversarial evidence

Add browser contracts proving scheduled/manual coalescing, one successor timer, old-request/new-generation independence, and identity-safe cleanup where an old promise cannot clear newer in-flight authority.

## 5. Gates

Use RED→GREEN microgates, neighboring regressions, full static/Python/Playwright verification, artifact cleanup and port verification. Then create a new immutable Freeze v10 and obtain two independent zero-finding, zero-drift reviews. No commit, push, document GO, backup or productive data use before all later gates pass.

## 6. Implemented candidate and trust boundary

- Gate provenance is absent from `argv`; it crosses the launcher boundary only in `MORPHIC_SCAN_GATE_TOKEN`, which the gate removes from its own environment before launching productive work.
- Token-bearing state is atomically created owner-only: runtime parent `0700`, temporary and final files `0600`. Windows receives the same explicit calls while ACL enforcement remains an OS concern.
- Public/API snapshots still exclude the token.
- POSIX signalling no longer uses a reusable numeric PGID. The service opens Linux pidfds first, validates exact PGID and token provenance against those processes, then signals only the stable handles. Supervisor identity uses the same stable-handle route. If pidfds or environment access are unavailable, the action fails closed.
- AccessDenied, foreign-token, supervisorless, stable-handle targeting, non-argv transport, temporary/final mode and post-release rollback contracts are present.
- Polling evidence now proves same-key request/timer coalescing and that completion of an old generation cannot clear or duplicate a newer request authority.

Local trust boundary: the operator service assumes its OS account and private runtime directory are controlled by the operator. A malicious process already executing as that same account is outside this boundary; cross-account observation, public API exposure, process-list exposure and accidental broad filesystem modes remain in scope and are blocked.

Candidate evidence before this lifecycle transition:

- focused process/durable/security matrix: `85 passed, 1 skipped`;
- complete Python suite: `1276 passed, 9 skipped`;
- isolated Chromium suite: `17 passed`;
- static, compile, JavaScript and diff checks: pass.

After this plan transition, the exact static/focused/full-Python/full-Playwright gates must run once more without any later in-scope patch before Freeze v10 is calculated.
