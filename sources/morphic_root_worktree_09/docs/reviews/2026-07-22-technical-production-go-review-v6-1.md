# Technical Production GO Review v6-1

## Verdict

```text
APPROVE
start drift: 0
end drift: 0
P0: 0
P1: 0
P2: 0
P3: 0
```

## Hash Observations

Start recomputation matched expected values:

| Item | Observed SHA-256 |
|---|---|
| v6 manifest | `5bdf57840f2db647ff98bafb2c88571143ef733c38ced540d3a3b9a7f24608dd` |
| v6 record | `3607c4fa553beefd2ec68065173b132bd02340e9a6da51e47e6a6628c43b90e2` |

End recomputation matched the same values:

| Item | Observed SHA-256 |
|---|---|
| v6 manifest | `5bdf57840f2db647ff98bafb2c88571143ef733c38ced540d3a3b9a7f24608dd` |
| v6 record | `3607c4fa553beefd2ec68065173b132bd02340e9a6da51e47e6a6628c43b90e2` |

## Manifest Verification

Start and end entry verification both produced:

| Check | Result |
|---|---:|
| Manifest lines | 117 |
| Final LF | yes |
| CR bytes | 0 |
| Syntax errors | 0 |
| Uppercase hashes | 0 |
| Ordinal-order mismatches | 0 |
| Duplicate paths | 0 |
| Missing files | 0 |
| Non-regular entries | 0 |
| Reparse/symlink entries | 0 |
| Entry SHA-256 mismatches | 0 |

## Scope And Diff Summary

Reviewed worktree `C:\morphic_v1\.worktrees\operator-workbench-phase1` at `HEAD` `3271ff9366ab3fecb2a158913a0cc19ed6a06726`.

`git diff --stat HEAD --` reported 70 tracked modified files, 20,207 insertions, and 1,582 deletions. Of those tracked modified files, 69 are manifest-scoped; the one tracked modified file outside the manifest is excluded runtime state: `data/harmonization_jobs/harm_ba41c018.json`.

Manifest scope checks passed:

| Scope Check | Result |
|---|---:|
| v4 manifest paths included in v6 | 90/90 |
| v5 manifest paths included in v6 | 113/113 |
| v5 rejected evidence files included | 4/4 |
| Qualifying modified/untracked source/test/static candidates under `apps/`, `core/`, `services/`, `tools/`, `tests/` | 106 |
| Qualifying candidates missing from v6 manifest | 0 |
| Manifest-scoped source/test/static paths not present in qualifying status set | 0 |

v6 versus rejected v5 manifest:

| Category | Paths |
|---|---|
| Added | `docs/reviews/2026-07-22-technical-production-go-freeze-v5.md`, `docs/reviews/2026-07-22-technical-production-go-freeze-v5.sha256`, `docs/reviews/2026-07-22-technical-production-go-review-v5-1.md`, and `docs/reviews/2026-07-22-technical-production-go-review-v5-2.md` |
| Changed | `apps/web/main.py`, `services/harmonization_worker.py`, `tests/test_harmonization_worker_recovery.py`, and `tests/test_web_shell.py` |
| Removed | none |

No tests, builds, installs, servers, browsers, process starts/stops, file edits, staging, commits, resets, or cleans were run.

## Technical Review

No P0-P3 findings.

Reviewed the rejected v5 P1 and v6 fix:

| Area | Evidence |
|---|---|
| Harmonization start-operation owner scope | `apps/web/main.py:758-760` now returns `operator_owner_scope(context)` for every start-operation kind, eliminating the rejected `tenant:operator` delimiter collision. |
| Harmonization process-authority owner scope | `services/harmonization_worker.py:740-758` derives `owner-v1-...` from `OperatorContext` when tenant and operator are both present. |
| Process replay/start authority uses derived scope | `services/harmonization_worker.py:1670-1730` passes the collision-safe owner scope to `get_for_replay()` and `start()`. |
| Web harmonization start supplies both components | `apps/web/main.py:855-857` and `apps/web/main.py:906-908` pass the current tenant/operator into replay and start. |
| Regression coverage | `tests/test_web_shell.py:277-297` covers delimiter-collision harmonization replay; `tests/test_harmonization_worker_recovery.py:1088-1128` covers process-authority owner scope. |

Reviewed the seven closure contracts:

| Contract | Review Summary |
|---|---|
| RV4-01 Job-ID path authority and diagnostics redaction | `apps/web/authority_ids.py:21-40` provides strict ASCII authority IDs and creation-prefix validation. Route/path/lock callers validate before path derivation, including `apps/web/scan_jobs.py:1329-1399`. Diagnostics redaction is position-based in `apps/web/scan_diagnostics.py:70-111`. |
| RV4-02 Cross-tenant scan/runtime exposure | `core/compliance/operator_context.py:42-52` derives collision-safe owner scope. Scan start/replay/status/stop/sync paths use it in `apps/web/main.py:993-1212`; WebSocket revalidation uses it in `apps/web/scan_live.py:57-65` and `apps/web/scan_live.py:123-136`. Workbench stores are tenant-hashed in `apps/web/workbench_runtime.py:43-52`. |
| RV4-03 Run traces and legacy analyze | `apps/web/workbench_runtime.py:174-239` implements insert-only trace creation and one-time terminal finalization. Scan start/replay ensures traces in `apps/web/main.py:1057-1175`; sync reconstructs missing traces in `apps/web/main.py:1235-1239`. `/api/analyze` is an authenticated 410 tombstone in `apps/web/analyze.py:12-23`. |
| RV4-04 Harmonization records and stale lease reconciliation | Strict harmonization record parsing is in `services/harmonization_worker.py:455-580`. Ordinary expired get observes process authority outside `_job_lock` and revision-checks before commit in `services/harmonization_worker.py:1044-1119`. |
| RV4-05 Browser/server unresolved scan reservation | Browser terminal scan statuses are exactly `completed`, `failed`, `stopped` in `apps/web/static/app.js:39` and `apps/web/static/app.js:345-381`; unresolved/unknown statuses keep reservation in `apps/web/static/app.js:775-781` and `apps/web/static/app.js:878-883`. Server stop retains unresolved authority until confirmed inactive in `apps/web/scan_jobs.py:2137-2227`. |
| RV4-06 Durable parent directory creation | Shared durable parent creation is implemented in `apps/web/durable_io.py:178-258`; `durable_write_bytes()` calls it in `apps/web/durable_io.py:303-318`. Targeted search over listed authority files found no remaining direct `mkdir(parents=True)` calls. |
| RV4-07 Report handle safety | Catalog identities include root identity and components in `apps/web/reports.py:195-216`. Preview/download open one verified handle in `apps/web/reports.py:293-351`; downloads stream that handle through `apps/web/main.py:730-756`. Report-content `FileResponse` reopen path was not present. |
