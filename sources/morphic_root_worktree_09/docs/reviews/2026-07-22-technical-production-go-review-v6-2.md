# Technical Production GO Review v6-2

## Verdict

No P0-P3 findings. Approved.

```text
APPROVE
start drift: 0
end drift: 0
P0: 0
P1: 0
P2: 0
P3: 0
```

## Drift Checks

| Check | Start | End |
|---|---|---|
| Manifest file SHA-256 | `5bdf57840f2db647ff98bafb2c88571143ef733c38ced540d3a3b9a7f24608dd` | `5bdf57840f2db647ff98bafb2c88571143ef733c38ced540d3a3b9a7f24608dd` |
| Record SHA-256 | `3607c4fa553beefd2ec68065173b132bd02340e9a6da51e47e6a6628c43b90e2` | `3607c4fa553beefd2ec68065173b132bd02340e9a6da51e47e6a6628c43b90e2` |
| Expected hash match | yes | yes |

## Manifest Verification

| Check | Start | End |
|---|---:|---:|
| Lines | 117 | 117 |
| Final LF | yes | yes |
| CR bytes | 0 | 0 |
| Exact syntax errors | 0 | 0 |
| Path normalization errors | 0 | 0 |
| Unique paths | 117 | 117 |
| Duplicate paths | 0 | 0 |
| Ordinal-order errors | 0 | 0 |
| Missing files | 0 | 0 |
| Non-regular files | 0 | 0 |
| Reparse/symlink entries | 0 | 0 |
| Entry SHA-256 mismatches | 0 | 0 |

## Scope And Diff Review

HEAD is `3271ff9366ab3fecb2a158913a0cc19ed6a06726`. The worktree is intentionally dirty, consistent with the freeze record.

Scope checks passed:

| Scope Check | Result |
|---|---:|
| v4 manifest paths included in v6 | 90/90 |
| v5 manifest paths included in v6 | 113/113 |
| Rejected v5 evidence files included | 4/4 |
| Modified/untracked source/test/static candidates under `apps/`, `core/`, `services/`, `tools/`, `tests/` missing from v6 | 0/106 |

v5 to v6 manifest delta is limited to four added v5 evidence files and four changed paths: `apps/web/main.py`, `services/harmonization_worker.py`, `tests/test_harmonization_worker_recovery.py`, and `tests/test_web_shell.py`.

## v5 P1 Remediation

The rejected v5 P1 was harmonization start/process authority using delimiter-composed or bare operator ownership. v6 closes that path:

| Area | Evidence |
|---|---|
| Web harmonization start operation owner | `apps/web/main.py:758-760` returns `operator_owner_scope(context)` for all start kinds |
| Start operation claim | `apps/web/main.py:792-796` passes that owner into `StartOperationStore` |
| Harmonization process owner | `services/harmonization_worker.py:740-755` returns collision-safe `owner-v1-...` when tenant and operator are both present |
| Process replay/start authority | `services/harmonization_worker.py:1709-1727` uses the scoped owner for `expected_owner_id` and `owner_id` |
| Regression coverage | `tests/test_web_shell.py:277-297` covers delimiter-collision harmonization replay; `tests/test_harmonization_worker_recovery.py:1088-1128` covers process-authority owner scope |

The remaining bare-operator fallback in `services/harmonization_worker.py:756-758` is only for incomplete direct-service calls where a tenant/operator scope cannot be formed; the web and persisted tenant/operator authority paths pass both components and use the scoped owner.

## Closure Contracts

RV4-01: shared authority ID validation is used before route/path/lock boundaries, and diagnostics redaction is command-position based.

RV4-02: scan ownership uses exact tenant/operator owner scope, and Workbench runtime state is tenant-hashed.

RV4-03: run traces are insert-only for new/replayed starts, terminal sync creates missing traces before one-time finalization, and `/api/analyze` is an authenticated 410 tombstone.

RV4-04: harmonization records are strictly parsed; expired-lease reconciliation observes process authority outside `_job_lock` and revision-checks before commit.

RV4-05: unresolved scan statuses such as `authority_ambiguous`, `rollback_failed`, missing status, and unknown status remain reserved in browser/server flow until terminal confirmation.

RV4-06: listed authority files route parent creation through `durable_mkdir_parents`; targeted search found no remaining direct `mkdir(parents=True)` calls in those files.

RV4-07: reports are cataloged by root identity plus relative components and served through one verified handle with `StreamingResponse`, not report-content `FileResponse`.

## Findings

No P0, P1, P2, or P3 findings.

No tests, builds, installs, server/browser commands, process changes, file writes, staging, commits, resets, or cleans were performed during this read-only review.
