# Gate 2 Adaptive Limits Authority Reconciliation

**Date:** 2026-07-31
**Branch:** `operator-workbench-phase1`
**HEAD:** `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
**Status:** AUTHORITATIVE CORRECTION

## Sources

- Historical parent plan:
  `.hermes/plans/2026-07-21_152301-operator-workbench-korrekturen-a-bis-p.md`
  Gate 2, especially lines 159-165.
- Detailed implementation plan:
  `docs/superpowers/plans/2026-07-26-workbench-gate2-adaptive-limits.md`
  section `Verbindlicher Wirkungsvertrag`.
- Product authority:
  `apps/cli/commands/scan.py`, `apps/web/display_scores.py`,
  `apps/web/main.py`, and the owner-bound results endpoint.

## Conflict

The historical parent plan says Adaptive Limits can reduce the number of
profiles that are fully analyzed and can cap the general result/report scope.
That wording combines three different collections and is not the implemented
contract.

The detailed Gate-2 plan is the authoritative correction for this gate. The
parent plan remains a historical roadmap record and is not silently rewritten.

## Authoritative Effect Contract

1. Backend, preview, and Workbench default to `adaptive_limits=false`.
2. Every profile in the selected level remains in the initial screening pool.
3. Top-N continues to select the profiles that receive the complete Phase-2
   analysis path. Adaptive Limits does not reduce or replace that Top-N profile
   selection.
4. Only after opt-in, the internal detail breadth within each selected profile
   is capped at `min(top_k, max(32, top_n * 16))`. A smaller requested `top_k`
   is never increased.
5. This detail cap can remove detail candidates and therefore can make
   ReportDETAIL and visible detail hits differ. It does not change the score
   formula or reorder surviving items.
6. Only after opt-in, the owner-bound scan-job results endpoint limits
   `top_profiles` to at most five entries. It preserves the existing score sort
   and values.
7. The endpoint's top-level `top_resonances` collection is not subject to this
   five-profile display cap.
8. The historical cross-session `GET /api/reports` catalog has no `job_id` and
   remains outside the Gate-2 cap.
9. A valid `--top-n` with no Adaptive-/Fixed-Limits flag preserves Top-N and
   treats Adaptive Limits as off. Missing or invalid Top-N, non-list or
   non-string commands, duplicated or conflicting limit flags, and Boolean
   limit flags carrying a separate or `=`-attached illegal value fail closed to
   the established legacy display limit and Adaptive Limits off.
10. Help text and the review card expose the selected state before scan start;
    New Case restores the unchecked default.

## Corrected Parent-Plan Reading

For Gate-2 acceptance, parent-plan wording about reducing the number of
"vollstaendig weiteranalysierten Profile" must be read as reducing the internal
detail-candidate breadth inside the already Top-N-selected profiles. Wording
about "Ergebnis/Report hoechstens 5" applies only to the owner-bound
`top_profiles` display, not to `top_resonances`, ReportCatalog, or
`GET /api/reports`.

This reconciliation changes no production code and introduces no new product
behavior. It records the behavior already implemented and tested by the
detailed Gate-2 plan.
