# Gate 4 Primary Workflow and Report UX - Immutable Freeze

**Acceptance timestamp:** `2026-08-06T08:32:05+02:00`
**Worktree:** `C:\morphic_v1\.worktrees\operator-workbench-phase1`
**Branch:** `report-ux-polish`
**HEAD:** `2d38d3bfa3f204491fe066fbc986e07fffc2ff06`
**Decision:** **GATE 4 ACCEPTED**

## Frozen Source Scope

| Evidence | Value |
|---|---|
| Source manifest | `docs/reviews/2026-07-31-gate4-primary-workflow-report-ux-freeze.sha256` |
| Manifest SHA-256 | `ba17d57f5d05c2f3247cf680e813ceafa77fe1d4a98c38598a224a2f5dfeeef6` |
| Manifest entries | 33 |
| Specification review | `docs/reviews/2026-07-31-gate4-primary-workflow-report-ux-review-1.md` |
| Specification review SHA-256 | `a2fa25ef569a94a6f3035503ec44130c616279c9edb283a446e5db4a07c4e867` |
| Quality/security review | `docs/reviews/2026-07-31-gate4-primary-workflow-report-ux-review-2.md` |
| Quality/security review SHA-256 | `d6d13c221f3639e63a7519c18b1ca9e2a9313e7bd36ac9416e035ac2b9c75d88` |

The source manifest excludes review, freeze, status, and project-memory files.
It includes all production, authority, plan, design, test, and browser-runner
files changed or directly relied upon by the accepted Gate-4 boundary.

## Final Verification

| Check | Result |
|---|---|
| Gate-4 focus matrix | `615 passed, 3 skipped in 63.50s` |
| Full Python suite | `3108 passed, 17 skipped, 9 warnings in 458.07s` |
| Browser shard 1 | `13 passed in 47.3s` |
| Browser shard 2 | `12 passed in 8.4s` |
| Browser shard 3 | `12 passed in 6.3s` |
| Browser shard 4 | `12 passed in 12.1s` |
| Browser total | `49 passed` |
| Canonical-session/compatibility matrix | `240 passed in 7.33s` |
| JavaScript syntax | `app.js` and `workbench.spec.js` passed |
| Python compile | Gate-4 production/test modules passed |
| Diff hygiene | passed; line-ending advisories only |
| Git index | empty |

The nine Python warnings are the known Windows DPAPI subprocess-reader UTF-8
decode warnings. They did not produce test failures.

## Manual Browser Acceptance

An isolated temporary server was used on port `55737`; port `8090` was not
used. The server, screenshots, script, and runtime were removed after visual
inspection.

Desktop `1280x900`:

- no primary Systemmodell link;
- catalog above preview;
- horizontal local report track with `clientWidth=987` and `scrollWidth=4572`;
- full-width non-sticky preview panel, width `1034.67`;
- exact active-session auto-preview selected `active-html`;
- manual selection changed to `active-json` only after activation;
- roving focus moved without an extra preview request;
- no page overflow.

Mobile `375x812`:

- vertical report orientation;
- list and maximum card width `253.33`;
- non-sticky preview width `290.67`;
- ArrowDown moved focus to `active-pdf`;
- no page overflow.

The direct internal `/workflow-stepping` route returned HTTP `200` and rendered
12 workflow steps.

## Independent Reviews

| Review | Session | Verdict | Findings |
|---|---|---|---|
| Specification | `ses_02a85adbcffeh5vUhsT2HmYG5Z` | APPROVE | `P0=P1=P2=P3=0` |
| Quality/security | `ses_02a660eb7ffe0DhUp5wc0JUXh5` / `G4-QS-R2-20260806-080732` | APPROVE | `P0=P1=P2=P3=0` |

Review findings were resolved through focused RED/GREEN loops before the final
full matrices. The final seven-file remediation establishes clamped accessible
focus, durable focus anchors, local scrolling, modern/legacy/absent
MediaQueryList support, production Top-N marker coverage, and one canonical
catalog session ID `S_TOP{N}_SESSION`.

## Operational State

- ports `8000`, `8090`, `8765`, `8766`, and `55737`: free;
- stale pytest, Uvicorn, isolated-server, supervisor, Playwright, scan-gate, and
  harmonization-entry processes: none;
- temporary `morphic-browser-*` runtimes: none;
- one Kilo main process;
- free RAM before final full matrices: `7.58 GiB`;
- free RAM after final matrices/audit: `6.53 GiB`;
- Git index: empty;
- no commit, staging, push, reset, clean, or unrelated deletion was performed.

## Accepted Boundary

Gate 4 accepts the primary catalog-first report workflow and its exact durable
session authority only. It preserves the accepted Gate-1 local-AI boundary,
Gate-2 Adaptive-Limits boundary, and Gate-3 scan-profile authority.

Gate 4 does not complete the full Single-Core baseline. It does not approve or
activate archive migration, complete report/LLM/PDF parity, productive
harmonization parity, external catalog runtime, remote hardware/WebSockets,
Quantum/Grover, or cloud-platform integration.
