# Gate 4 Primary Workflow and Report UX - Acceptance Status

**Acceptance date:** 2026-08-06
**Branch:** `report-ux-polish`
**HEAD:** `2d38d3bfa3f204491fe066fbc986e07fffc2ff06`
**Verdict:** **GATE 4 ACCEPTED**

## Result

The primary Workbench now has one catalog-first report flow with durable,
fail-closed report-session authority from the Top-N orchestrator through the
owner-bound results response and browser state machine.

Accepted behavior:

- both primary Systemmodell exits are removed;
- the report catalog is above a full-width non-sticky preview;
- automatic preview selects only from the completed scan's exact canonical
  report session;
- parent Top-N marker and production archive/catalog use the same
  `S_TOP{N}_SESSION` identifier;
- manual selection remains authoritative and stale responses cannot replace it;
- New Case clears report session, selection, focus, preview, and link state;
- the desktop catalog is a locally scrollable horizontal toolbar;
- the mobile catalog is vertical without page overflow;
- roving focus clamps at endpoints, persists across catalog refreshes, and
  scrolls locally without activating a preview;
- modern, legacy, and absent MediaQueryList environments remain operable;
- `/workflow-stepping` remains available as an internal direct route.

## Verification

| Check | Final result |
|---|---|
| Gate-4 focus matrix | `615 passed, 3 skipped in 63.50s` |
| Full Python suite | `3108 passed, 17 skipped, 9 warnings in 458.07s` |
| Full browser matrix | `49 passed` (`13/12/12/12`) |
| Canonical-session/compatibility matrix | `240 passed in 7.33s` |
| Manual desktop | PASS at `1280x900` |
| Manual mobile | PASS at `375x812` |
| Direct internal route | HTTP `200`, 12 steps |
| Specification review | APPROVE, `P0=P1=P2=P3=0` |
| Quality/security review | APPROVE, `P0=P1=P2=P3=0` |
| Syntax/compile/diff/index | PASS / PASS / PASS / empty |

## Immutable Evidence

| Evidence | SHA-256 |
|---|---|
| `docs/reviews/2026-07-31-gate4-primary-workflow-report-ux-freeze.sha256` | `ba17d57f5d05c2f3247cf680e813ceafa77fe1d4a98c38598a224a2f5dfeeef6` |
| `docs/reviews/2026-07-31-gate4-primary-workflow-report-ux-review-1.md` | `a2fa25ef569a94a6f3035503ec44130c616279c9edb283a446e5db4a07c4e867` |
| `docs/reviews/2026-07-31-gate4-primary-workflow-report-ux-review-2.md` | `d6d13c221f3639e63a7519c18b1ca9e2a9313e7bd36ac9416e035ac2b9c75d88` |
| `docs/reviews/2026-07-31-gate4-primary-workflow-report-ux-freeze.md` | `9224a6ce868503f742b3379596d2f708b2cd568745f2b1fc2d57aac9bd1d4508` |

The source manifest contains 33 entries. A bounded verifier must report
`MANIFEST_OK 33/33` before this acceptance is used as a continuation baseline.

## Operational Closure

- ports `8000`, `8090`, `8765`, `8766`, and `55737` are free;
- no owned test/server/supervisor/Playwright/scan/harmonization process remains;
- no temporary manual or `morphic-browser-*` runtime remains;
- Git index is empty;
- no commit, push, reset, clean, or unrelated deletion was performed.

## Preserved Earlier Gates

- Gate 1 local AI remains explicit, per-case, loopback-only, and default-off.
- Gate 2 Adaptive Limits remains default-off with its accepted detail-scope
  semantics.
- Gate 3 scan-profile pool and process authority remain accepted.

## Non-Goals and Next Gate

Gate 4 is not the complete Single-Core baseline requested by the operator. The
next formal roadmap unit is Gate 5, EMF activation and source truth, followed by
Gates 6-8 for report catalog focus, interpretation/E-E-A-T, and HTML/PDF parity.
Full terminal Single-Core parity, Harmonization parity, freeze, and live
acceptance remain required before remote hardware/WebSocket, external catalog
activation, Quantum/Grover, or Radiquant/Lovable Cloud integration.

Radi144 and `radiquant-cloud-build` remain read-only structural references for
future modular platform integration. Radi144 may guide frontend UI/UX, stepper,
and sequence structure, but it is not an authority for RadiMorphic algorithms,
core engines, or domain functionality without an explicit matching contract.
