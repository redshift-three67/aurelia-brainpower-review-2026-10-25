# Technical Production GO Freeze v6

Date: 2026-07-25

Status: `NO-GO / REVIEW CANDIDATE`

Branch: `operator-workbench-phase1`

HEAD/baseline: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`

Worktree: `C:\morphic_v1\.worktrees\operator-workbench-phase1`

## 1. Preservation boundary

The worktree is intentionally dirty. This freeze binds the current working-file bytes; HEAD is only the baseline identity and does not imply a clean tree. Freeze creation did not broadly stage, reset, clean, commit, or change unrelated source/test bytes. Existing dirty-worktree bytes were preserved.

The frozen byte list is:

`docs/reviews/2026-07-22-technical-production-go-freeze-v6.sha256`

Manifest SHA-256:

`5bdf57840f2db647ff98bafb2c88571143ef733c38ced540d3a3b9a7f24608dd`

This record and the manifest are not entries in the manifest. The record cannot contain its own SHA-256 without a circular self-reference. Its SHA-256 is therefore computed only after the final record write and reported externally. That external value is part of each reviewer's start/end drift contract.

## 2. v5 rejection and v6 delta

Freeze v5 is immutable rejected evidence. Review v5-2 found one P1: harmonization start-operation/process authority still used delimiter or bare-operator owner identity while scan authority used collision-safe `owner-v1-...` tenant/operator scope.

v6 applies the smallest authorized correction:

- `apps/web/main.py`: harmonization start operations now use `operator_owner_scope(context)`, same as scan starts.
- `services/harmonization_worker.py`: harmonization process authority now uses collision-safe tenant/operator owner scope when both components are present, preserving the prior ownerless fallback for incomplete direct-service calls.
- `tests/test_web_shell.py` and `tests/test_harmonization_worker_recovery.py`: added RED->GREEN coverage for delimiter-collision harmonization start replay and process-authority owner scope; updated existing harmonization start-operation fixtures to the new owner scope.

## 3. Scope algorithm

The manifest contains 117 unique regular files:

1. Start from all 113 paths in the immutable v5 manifest `docs/reviews/2026-07-22-technical-production-go-freeze-v5.sha256`.
2. Add rejected v5 evidence files: `docs/reviews/2026-07-22-technical-production-go-freeze-v5.sha256`, `docs/reviews/2026-07-22-technical-production-go-freeze-v5.md`, `docs/reviews/2026-07-22-technical-production-go-review-v5-1.md`, and `docs/reviews/2026-07-22-technical-production-go-review-v5-2.md`.
3. Add every additional modified or untracked regular source/test/static path under `apps/`, `core/`, `services/`, `tools/`, and `tests/` present at freeze time.
4. Require every selected path to exist as a regular, non-reparse-point file. Normalize each path to a repository-relative slash path. Compute lowercase SHA-256 over its exact bytes.
5. Remove duplicates, sort paths with ordinal string ordering, and write exactly `<64 lowercase hex><two ASCII spaces><path>` per line with a final LF.
6. Exclude the v6 manifest, v6 record, and the future v6 review outputs from their own scope.

There were zero duplicate, missing, ignored-but-required, non-regular, symlink, junction, or reparse scope entries.

## 4. Exclusions

The following are intentionally outside the technical production scope:

- `__pycache__/`, `*.pyc`, caches, and generated logs;
- `node_modules/`, `tests/browser/test-results/`, `playwright-report/`, and other Playwright output;
- runtime state, generated reports, generated harmonization-job state, and other runtime/report artifacts;
- harmonization-job locks and other lock files;
- `Benutzer_Archive__manual-acceptance/`;
- old plans, old reviews, and old freeze manifests except the specifically included v4/v5 freeze and review evidence plus recovery design/plan documents;
- unrelated data and reference directories;
- the new v6 manifest, this v6 record, and the two future v6 review outputs.

These exclusions prevent generated, historical, private/manual-acceptance, dependency-install, and unrelated reference bytes from being mistaken for the current Workbench/recovery implementation.

## 5. Fresh root verification evidence

The following fresh root-worktree verification completed after the v6 source/test bytes and before this documentation-only freeze:

| Gate | Result |
|---|---|
| New RED tests before fix | `2 failed` for harmonization delimiter collision and process-authority owner scope |
| New GREEN tests after fix | `2 passed in 1.93s` |
| Harmonization-focused regression slice | `340 passed in 46.72s` |
| Python compile | `16/16`, exit 0 |
| Node syntax checks | `6/6`, exit 0 |
| Patch hygiene | `git diff --check`, exit 0 |
| Focused remediation matrix | `910 passed, 3 skipped in 81.21s (0:01:21)` |
| Full Python suite | `2300 passed, 12 skipped, 9 warnings in 342.88s (0:05:42)` |
| Browser matrix | `38 passed, 0 failed, 0 retries` |

The 16 compile targets were `apps/web/authority_ids.py`, `apps/web/durable_io.py`, `apps/web/emf_authority.py`, `apps/web/start_operations.py`, `apps/web/scan_jobs.py`, `apps/web/scan_live.py`, `apps/web/workbench_runtime.py`, `apps/web/workbench.py`, `apps/web/analyze.py`, `apps/web/report_handles.py`, `apps/web/reports.py`, `apps/web/main.py`, `core/compliance/operator_context.py`, `services/harmonization_worker.py`, `services/harmonization_process_entry.py`, and `services/scan_process_gate.py`.

The six Node checks were `apps/web/static/app.js`, `apps/web/static/workbench-api.js`, `apps/web/static/workbench-render.js`, `apps/web/static/workbench-state.js`, `tests/browser/workbench.spec.js`, and `tests/browser/playwright.config.js`.

The full Python suite emitted the existing Windows subprocess UTF-8 decode warnings in local vector/group draft tests; they did not fail the suite.

## 6. Browser evidence and lifecycle

Final browser evidence root:

`C:\Users\HUBERT~1\AppData\Local\Temp\opencode\morphic-freeze-v6-task8-20260725`

Accepted browser shards used `PLAYWRIGHT_BASE_URL=http://127.0.0.1:8766`, `PLAYWRIGHT_CHROMIUM_EXECUTABLE=C:\Program Files\Google\Chrome\Application\chrome.exe`, one worker, zero retries, and `npm test -- --fully-parallel --shard=N/6`.

| Shard | Evidence subdirectory | Uvicorn server PID | Result |
|---|---|---:|---|
| `1/6` | `pass-shard-1` | `27908` | `7 passed (11.1s)` |
| `2/6` | `pass-shard-2` | `29372` | `7 passed (4.1s)` |
| `3/6` | `pass-shard-3` | `28192` | `6 passed (2.9s)` |
| `4/6` | `pass-shard-4` | `28900` | `6 passed (3.9s)` |
| `5/6` | `pass-shard-5` | `17168` | `6 passed (2.7s)` |
| `6/6` | `pass-shard-6` | `29184` | `6 passed (5.6s)` |

Each shard used a fresh isolated server, runtime root, and harmonization-jobs root under its evidence subdirectory. Each server answered `/api/health` with HTTP 200 before Playwright started. The process tree was stopped after each shard and `127.0.0.1:8766` was verified listener-free before the next shard.

The accepted `pass-shard-*` logs were checked for HTTP 429/5xx, `Too Many`, `Traceback`, and `ERROR:` patterns with no matches.

Post-browser cleanup removed generated `tests/browser/test-results/` and `tests/browser/node_modules/`; `tests/browser/playwright-report/` was not present. The retained browser source/package files are exactly the four files listed in the manifest.

## 7. Tool versions

| Tool | Version |
|---|---|
| Python | `3.12.10` from `C:\morphic_v1\.venv\Scripts\python.exe` |
| Node | `v22.22.0` |
| npm | `11.18.0` |
| Playwright | `1.61.1` from `tests/browser/package.json` and `package-lock.json` |

## 8. Browser package byte evidence

The current manifest contains these browser package/input hashes:

| Path | SHA-256 |
|---|---|
| `tests/browser/package.json` | `183692ff7150ed8ffce00bd7b1edec52ebb2c3715694b2e09b523e151834d5a9` |
| `tests/browser/package-lock.json` | `20b0a6be6062420ea47224cb04cc59d0e8ad42c97a0fbc0230702417488cd494` |
| `tests/browser/playwright.config.js` | `7771feb1f9c4dd4c340d1285a8117fb3a28b2e73d3d8e04834210c2c19702ed3` |
| `tests/browser/workbench.spec.js` | `0c38e7496a66b42682b22b21eed072df3f89c2ddadaf0a881c23519d3f5dc468` |

## 9. Runtime state at freeze creation

Observed read-only at `2026-07-25T22:06:05.9575635+02:00`:

| Port/category | Exact observation |
|---|---|
| `8090` | One listener on `127.0.0.1`, PID `7976`, parent PID `12608`, `python.exe`, creation time previously observed as `2026-07-24 09:27:38` |
| `8090` executable | `C:\Users\Hubert111\AppData\Roaming\uv\python\cpython-3.11.12-windows-x86_64-none\python.exe` |
| `8090` command | `"C:\Users\Hubert111\AppData\Roaming\uv\python\cpython-3.11.12-windows-x86_64-none\python.exe" main.py` |
| `8765` | Free, listener count 0 |
| `8766` | Free, listener count 0 |
| Task leaks | 0 Morphic uvicorn/listener processes on `8765` or `8766`; no Playwright Chrome/Edge processes remained |

The observed `8090` process was not changed. PID `7976` is an observation, not a future assumption; reviewers and any later live gate must query the owner again.

## 10. Superseded evidence

The v4 and v5 candidates are immutable rejected evidence and cannot authorize GO or a live start:

- `docs/reviews/2026-07-22-technical-production-go-freeze-v4.md`
- `docs/reviews/2026-07-22-technical-production-go-freeze-v4.sha256`
- `docs/reviews/2026-07-22-technical-production-go-freeze-v5.md`
- `docs/reviews/2026-07-22-technical-production-go-freeze-v5.sha256`
- `docs/reviews/2026-07-22-technical-production-go-review-v5-1.md`
- `docs/reviews/2026-07-22-technical-production-go-review-v5-2.md`

Historical v3/v29 and earlier review files may inform inspection, but neither their hashes nor their verdicts authorize this v6 candidate or a restart.

## 11. Independent review gate

There is no technical production GO and no port `8765` start/restart until two independent read-only reviews both complete this contract:

1. At review start, recompute the v6 manifest file SHA-256 and compare it with `5bdf57840f2db647ff98bafb2c88571143ef733c38ced540d3a3b9a7f24608dd`. Recompute this record's SHA-256 and compare it with the exact external value reported after final record write.
2. Validate all 117 manifest lines for exact syntax, ordinal order, uniqueness, regular-file existence, and lowercase SHA-256. Recompute every file entry and require zero missing files and zero mismatches.
3. Inspect the complete manifest scope, the current diff against HEAD, v4/v5 rejected evidence, this v5 remediation plan, the v6 ownership fix, and all seven closure contracts. Do not treat accepted agent evidence as a substitute for root evidence.
4. Do not edit files, run tests, start or stop servers, or alter the dirty worktree during review.
5. At review end, repeat the manifest-file SHA, record SHA, and every entry verification. Require start drift 0 and end drift 0.
6. Return `APPROVE` only with `P0=0`, `P1=0`, `P2=0`, and `P3=0`.

Required verdict form:

```text
APPROVE
start drift: 0
end drift: 0
P0: 0
P1: 0
P2: 0
P3: 0
```

Any drift or finding rejects this candidate. Preserve it as historical evidence; do not patch a reviewed freeze in place.

## 12. Rollback and recovery posture

Preserve the current dirty worktree at `C:\morphic_v1\.worktrees\operator-workbench-phase1`. Do not reset, clean, or broadly stage it. `git status --porcelain=v1 -uall` identifies the working-tree state, while the manifest identifies the exact 117 reviewed file bytes. Recovery means retaining those bytes and comparing status plus manifest; no destructive Git rollback command is authorized by this record.

Port `8765` has not been started from this candidate. If the candidate drifts or review fails, leave `8765` unstarted, preserve this v6 evidence, make only separately authorized corrections, repeat the complete verification ladder, and create a new freeze version.
