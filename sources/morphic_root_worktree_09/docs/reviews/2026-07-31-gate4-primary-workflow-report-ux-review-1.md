# Gate 4 Primary Workflow and Report UX - Specification Review

**Acceptance run:** 2026-08-06
**Branch:** `report-ux-polish`
**HEAD:** `2d38d3bfa3f204491fe066fbc986e07fffc2ff06`
**Review session:** `ses_02a85adbcffeh5vUhsT2HmYG5Z`
**Final verdict:** **APPROVE**

## Scope

The review compared the current tracked Gate-4 bytes and the intentional
uncommitted remediation diff against:

- `docs/superpowers/plans/2026-07-31-gate4-primary-workflow-report-ux.md`;
- `docs/superpowers/specs/2026-07-31-gate4-primary-workflow-report-ux-design.md`;
- the approved 2026-08-01 report-authority recovery plan and state-machine design.

The reviewed boundary covered durable report-session authority, owner-bound
result exposure, exact-session automatic preview, manual selection authority,
stale/reset behavior, catalog-first layout, roving focus, responsive
orientation, and internal route preservation.

## Review History

The initial review rejected endpoint wrapping, missing focus-anchor persistence,
missing local nearest scrolling, and missing parent marker emission coverage.
The retained stable-preview behavior was investigated separately and the
reviewer withdrew that finding because it is explicitly permitted by the later
approved recovery contract.

The first re-review found an unconditional `window.matchMedia()` module-load
regression in Node harnesses. That regression was reproduced, fixed by feature
detection, and independently re-reviewed.

## Final Findings

| Severity | Count |
|---|---:|
| P0 | 0 |
| P1 | 0 |
| P2 | 0 |
| P3 | 0 |

The final review confirmed:

- clamped orientation-aware focus resolution;
- one roving tab stop and a persisted focus anchor;
- nearest local scrolling without preview activation from focus movement;
- exact-session selection and preserved manual authority;
- parent Top-N marker coverage and downstream durable authority coverage;
- no regression in no-`matchMedia` harnesses.

## Boundary

This verdict accepts Gate 4 only. It does not approve core-engine changes,
scoring changes, archive migration, productive hardware/WebSocket activation,
cloud integration, or the remaining Single-Core gates.
