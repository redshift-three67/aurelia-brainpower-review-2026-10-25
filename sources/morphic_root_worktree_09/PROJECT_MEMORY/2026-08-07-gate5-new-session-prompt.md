# Gate 5 New Session Prompt - Exact Restart

```text
Resume the RadiMorphic Single-Core baseline exactly at Gate 5 Task 8.

Work only in this existing worktree:
C:\morphic_v1\.worktrees\operator-workbench-phase1

Expected branch: report-ux-polish
Expected HEAD: 2d38d3bfa3f204491fe066fbc986e07fffc2ff06

Read only these documents first, in this order:
1. PROJECT_MEMORY/2026-08-07-gate5-current-handoff.md
2. PROJECT_MEMORY/00_CURRENT_STATE.md
3. PROJECT_MEMORY/2026-08-06-gate5-session-checkpoint.md
4. docs/superpowers/specs/2026-08-06-gate5-emf-authority-source-truth-design.md
5. docs/superpowers/plans/2026-08-06-gate5-emf-authority-source-truth.md

Do not read the entire prior Kilo session transcript. It is historical context,
not the recovery authority, and causes unnecessary token/context pressure.

Before any edit or test, verify:
- branch and HEAD;
- empty Git index;
- at least 3.5 GiB free RAM;
- one Kilo main process;
- ports 8000, 8090, 8765, 8766, and 55737 are free or separately documented;
- no stale pytest, Uvicorn, isolated-server, Playwright, scan-gate, or
  Harmonization process;
- PROJECT_MEMORY/2026-08-06-gate5-wip-source.sha256 exactly matches current
  source bytes (`GATE5_WIP_MANIFEST_OK 33/33`).

Stop on a manifest mismatch, insufficient RAM, unexpected port owner, or stale
process. Do not guess and do not run full matrices under insufficient RAM.

Important current result:
- Gate 5 Tasks 1-7 are implemented and taskwise approved.
- Full Python suite on current WIP bytes: 3693 passed, 17 skipped, 9 known
  Windows DPAPI decode warnings in 513.64s.
- Full isolated browser matrix on current WIP bytes: 51 passed in four serial
  shards (13/13/13/12).
- Gate 5 is NOT ACCEPTED. Manual acceptance, final whole-Gate reviews, manifest,
  freeze, acceptance record, Golden Record update, and final checkpoint remain.

Resume at the correct next action:
1. Repeat the real manual Desktop and 375px acceptance with a temporary,
   isolated runtime through tests/browser/isolated_server.py or
   Run-WebUI.ps1 -IsolatedAcceptance.
2. Do NOT launch `python -m uvicorn apps.web.main:app` with a temporary
   MORPHIC_RUNTIME_DIR. That is not the isolated factory entrypoint and can read
   the intentionally fail-closed historical codex_tmp authority state.
3. Verify default-off, deliberate enable/disable, durable manual-disable
   lifetime, modern/legacy status parity, exact proxy label, four source
   keys/statuses, fallback visibility, invalid aggregate no-gauge behavior, and
   no 375px page overflow. Inspect temporary screenshots and remove every
   temporary server/runtime/script/screenshot afterwards.
4. If sources remain unchanged, dispatch a fresh independent whole-Gate Spec
   review, then a separate Quality/Security review. Both must APPROVE with zero
   blocking findings.
5. Only then build and verify the final SHA-256 source manifest, review records,
   freeze record, acceptance record, Golden Record update, and final uncommitted
   checkpoint.

No source change is currently authorized or needed for the failed direct-Uvicorn
manual attempt. It was a wrong test entrypoint, not a confirmed product defect.
If a supported-entrypoint failure is found, use strict RED/GREEN TDD and rerun
the full matrices and reviews after the source change.

Hard boundaries:
- no staging, commit, push, reset, clean, checkout, or deletion of historical
  artifacts without separate user authorization;
- preserve accepted Gate-4 changes and all historical untracked files;
- no Gate 6, remote hardware/WSS, Quantum/Grover, cloud, catalog activation,
  report/PDF, or Harmonization scope expansion;
- use bounded `rg` through Bash with a timeout instead of broad integrated
  Grep/Glob; do not parallelize broad searches;
- use `/compact` before long matrices/reviews or at 90 minutes / 1.5 GiB Kilo
  private memory, and start a fresh session at 12 hours / 2 GiB.
```
