# Gate 2 Adaptive Limits Acceptance Freeze

**Date:** 2026-07-31
**Branch:** `operator-workbench-phase1`
**HEAD:** `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
**Status:** ACCEPTED CANDIDATE - exact scope frozen by SHA-256 manifest

## Immutable Scope

- Manifest: `docs/reviews/2026-07-31-gate2-adaptive-limits-freeze.sha256`
- Manifest SHA-256: `f62bc57e77a629e8d9c501a2a598f0bb0ff79058f04facce2750b07e00c347bc`
- Frozen parent, authority, production, test, and plan files: 20
- Authority correction:
  `docs/reviews/2026-07-31-gate2-adaptive-limits-authority.md`
  - SHA-256: `019894e71931d1f46dc9ffee20cb554e9708c9c9cdca33a6a9c39f7c4c9eda2e`

The authority correction makes the detailed Gate-2 plan authoritative over the
historical parent plan where that parent conflates Top-N profile selection,
per-profile Phase-2 detail breadth, and general report scope.

## Accepted Behavior

- Adaptive Limits defaults to off in backend, preview, and Workbench.
- All level profiles remain in the screening pool and Top-N profile selection
  remains unchanged.
- Opt-in caps only per-selected-profile detail breadth at
  `min(top_k, max(32, top_n * 16))` and never increases a smaller request.
- Opt-in caps only owner-bound `top_profiles` to at most five; scores and order
  are preserved.
- Top-level `top_resonances` and the cross-session `GET /api/reports` catalog
  are not subject to that five-profile cap.
- Valid Top-N without a limit flag preserves Top-N with Adaptive Limits off.
- Invalid command shape or Top-N, duplicate/conflicting flags, and separate or
  attached Boolean values fail closed to legacy display limit 10/off.
- Preview, help, and review copy state the Phase-2 and owner-bound effects
  without claiming a general report cap; New Case restores false.

## Verification On Frozen Bytes

- First review RED/GREEN: `3 failed, 15 passed` then `18 passed`.
- Second review RED/GREEN: `5 failed, 19 passed` then `24 passed`.
- Focused Gate-2 browser: `1 passed`.
- Final Gate-2 focus matrix: `533 passed`.
- Full Python suite: `3018 passed, 17 skipped, 9 warnings` in `346.81s`.
- Warning class: existing `PytestUnhandledThreadExceptionWarning` from Windows
  DPAPI subprocess-reader UTF-8 decoding; no failed assertion.
- Full browser suite: `48 passed` in four isolated 12-test shards.
- JavaScript syntax, Python compile, scoped diff, index, ports, processes, and
  temporary-runtime checks: PASS.

One attempted npm-proxied focused browser command lost its `--grep` option and
reported `No tests found`; it changed no source, left no process, and was
replaced by the direct isolated-runner command that passed.

## Independent Reviews

- Specification and semantic review:
  `docs/reviews/2026-07-31-gate2-adaptive-limits-review-1.md`
  - SHA-256: `c98dac52a8cf5b7ff7efd0c8f0483a700ba01b7620a19970c317466e2f542635`
  - Session: `ses_048a4f65dffePxfz0XA9qEzdJM`
  - Verdict: APPROVE, P0-P3 = 0
- Quality and security review:
  `docs/reviews/2026-07-31-gate2-adaptive-limits-review-2.md`
  - SHA-256: `fcfc210ea914e6232be05582edf06cadfd07a5e530076c6819214f72da5a12dc`
  - Session: `ses_04894fe0effeiSTW7yeV2taXMZ`
  - Verdict: APPROVE, P0-P2 = 0

## Operational State

- Protected port `8090` remained unchanged on PID `1692`.
- Temporary ports `8765` and `8766` are free.
- No isolated server, process-tree supervisor, Playwright workbench process,
  scan process gate, harmonization process entry, or `morphic-browser-*`
  runtime remains.
- Git index is empty. No commit, staging, push, reset, or unrelated cleanup
  occurred.
