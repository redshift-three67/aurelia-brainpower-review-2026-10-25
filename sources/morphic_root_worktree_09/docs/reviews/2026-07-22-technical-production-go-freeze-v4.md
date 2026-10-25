# Technical Production GO Freeze v4

Date: 2026-07-22

Status: `NO-GO / REVIEW CANDIDATE`

Branch: `operator-workbench-phase1`

HEAD/baseline: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`

Worktree: `C:\morphic_v1\.worktrees\operator-workbench-phase1`

## 1. Preservation boundary

The worktree is intentionally dirty. This freeze binds the current working-file bytes; HEAD is only the baseline identity and does not imply a clean tree. Freeze creation did not broadly stage, reset, clean, commit, or change source/test bytes. Unrelated existing changes and artifacts were preserved.

The frozen byte list is:

`docs/reviews/2026-07-22-technical-production-go-freeze-v4.sha256`

Manifest SHA-256:

`4fd8759400cd6e774695172b192b9e5499e6324f203b1753ff4b6646af1b4aaf`

This record and the manifest are not entries in the manifest. The record cannot contain its own SHA-256 without a circular self-reference. Its SHA-256 is therefore computed only after the final record write and reported separately in the Task 7 return. That external value is part of each reviewer's start/end drift contract.

## 2. Scope algorithm

The manifest contains 90 unique regular files:

1. Capture `git status --porcelain=v1 -uall` and select every currently modified or untracked source, test, and static-asset path under `apps/`, `core/`, `services/`, `tools/`, and `tests/` that contributes to the current Workbench/recovery. After the explicit exclusions below, this produced 86 paths. No qualifying `tools/` path was reported.
2. Include all four browser files explicitly required by the recovery gate: `tests/browser/package.json`, `tests/browser/package-lock.json`, `tests/browser/playwright.config.js`, and `tests/browser/workbench.spec.js`.
3. Add `Run-WebUI.ps1` and `pyproject.toml` even though they were unchanged, plus the approved design and plan: `docs/superpowers/specs/2026-07-21-technical-production-go-recovery-design.md` and `docs/superpowers/plans/2026-07-21-technical-production-go-recovery.md`.
4. Require every selected path to exist as a regular, non-reparse-point file. Normalize each path to a repository-relative slash path. Compute lowercase SHA-256 over its exact bytes.
5. Remove duplicates, sort paths with ordinal string ordering, and write exactly `<64 lowercase hex><two ASCII spaces><path>` per line with a final newline.
6. Exclude this new v4 manifest and this record from their own scope.

There were zero duplicate, missing, or non-regular selected paths. No requested scope path was ambiguous: all 86 qualifying status paths were included, and the four fixed additions brought the count to 90.

## 3. Exclusions

The following are intentionally outside the technical production scope:

- `__pycache__/`, `*.pyc`, caches, and generated logs;
- `node_modules/`, `tests/browser/test-results/`, `playwright-report/`, and other Playwright output;
- runtime state, generated reports, and other runtime/report artifacts;
- `Benutzer_Archive__manual-acceptance/`;
- `data/harmonization_jobs/*.json`, harmonization-job locks, and other locks;
- old plans, old reviews, and old freeze manifests, except the two specifically approved recovery design/plan documents included above;
- unrelated data and reference directories;
- the new v4 manifest and record themselves.

These exclusions prevent generated, historical, private/manual-acceptance, dependency-install, and unrelated reference bytes from being mistaken for the current Workbench/recovery implementation.

## 4. Fresh root verification evidence

The following fresh root-worktree verification completed after the final source/test bytes and before this documentation-only freeze:

| Gate | Result |
|---|---|
| Full Python suite | `1589 passed, 9 skipped in 295.68s` |
| Python compile | `8/8`, exit 0 |
| Node syntax checks | `6/6`, exit 0 |
| Patch hygiene | `git diff --check`, exit 0 |
| Root browser matrix | `33 passed, 0 failed` |

The eight compile targets were `apps/web/durable_io.py`, `apps/web/start_operations.py`, `apps/web/scan_jobs.py`, `apps/web/main.py`, `apps/web/harmonization.py`, `services/scan_process_gate.py`, `services/harmonization_worker.py`, and `services/harmonization_process_entry.py`.

The six Node checks were `apps/web/static/app.js`, `apps/web/static/workbench-api.js`, `apps/web/static/workbench-render.js`, `apps/web/static/workbench-state.js`, `tests/browser/workbench.spec.js`, and `tests/browser/playwright.config.js`.

The root browser run used six isolated shards with pass counts `6, 6, 6, 5, 5, 5`, totaling 33 with zero failures. Root logs are under:

`C:\Users\Hubert111\AppData\Local\Temp\opencode\morphic-browser-root-20260722-215510`

Accepted agent evidence directories may be used only as supporting evidence. They do not replace, widen, or override the fresh root verification above. No tests were rerun and no application/test server was started while creating this freeze.

Tool versions:

- Python `3.12.10`
- Node `v22.22.0`
- npm `11.18.0`

## 5. Browser package byte evidence

Task 6 evidence directory:

`C:\Users\HUBERT~1\AppData\Local\Temp\opencode\morphic-go-qa\task6-evidence-20260722T211115801`

Task 6 recorded identical before/after hashes and `ALL_UNCHANGED True` for these browser inputs. The current manifest contains the same lowercase values:

| Path | SHA-256 |
|---|---|
| `tests/browser/package.json` | `183692ff7150ed8ffce00bd7b1edec52ebb2c3715694b2e09b523e151834d5a9` |
| `tests/browser/package-lock.json` | `20b0a6be6062420ea47224cb04cc59d0e8ad42c97a0fbc0230702417488cd494` |
| `tests/browser/playwright.config.js` | `7771feb1f9c4dd4c340d1285a8117fb3a28b2e73d3d8e04834210c2c19702ed3` |
| `tests/browser/workbench.spec.js` | `1ba9e6e8273856a9159611bfd93368fd251ae6bb4e002f9094c40903ecbcc008` |

## 6. Runtime state at freeze creation

Observed read-only at `2026-07-22T22:00:56.8108193+02:00`:

| Port/category | Exact observation |
|---|---|
| 8090 | One listener on `127.0.0.1`, PID `9984`, `python.exe`, parent PID `9168`, creation time `2026-07-22 21:25:18` |
| 8090 executable | `C:\Users\Hubert111\AppData\Roaming\uv\python\cpython-3.11.12-windows-x86_64-none\python.exe` |
| 8090 command | `"C:\Users\Hubert111\AppData\Roaming\uv\python\cpython-3.11.12-windows-x86_64-none\python.exe" main.py` |
| 8765 | Free, listener count 0 |
| 8766 | Free, listener count 0 |
| Task leaks | 0 |

The zero-leak inventory covered `scan_process_gate`, `harmonization_process_entry`, uvicorn on ports 8765/8766, Playwright Node processes, and Playwright Chromium/Chrome/Edge processes. The observed 8090 process was not changed. PID 9984 is an observation, not a future assumption; reviewers and the pre-start gate must query the owner again.

## 7. Superseded evidence

The prior Gate 0 v3 candidate and broad remediation v29 remain rejected/superseded historical evidence:

- `docs/reviews/2026-07-21-operator-workbench-corrections-gate0-technical-freeze-v3.md`
- `docs/reviews/2026-07-21-workbench-remediation-technical-freeze-v29.sha256`

Their associated reviews may inform inspection, but neither freeze, its hashes, nor its verdicts authorize GO or a restart. This v4 candidate does not retroactively accept them.

## 8. Independent review gate

There is no technical production GO and no port 8765 start/restart until two independent read-only reviews both complete this contract:

1. At review start, recompute the v4 manifest file SHA-256 and compare it with `4fd8759400cd6e774695172b192b9e5499e6324f203b1753ff4b6646af1b4aaf`. Recompute the record SHA-256 and compare it with the exact external Task 7 return value.
2. Validate all 90 manifest lines for exact syntax, ordinal order, uniqueness, regular-file existence, and lowercase SHA-256. Recompute every file entry and require zero missing files and zero mismatches.
3. Inspect the complete manifest scope, the current diff against HEAD, the approved design/plan, and relevant superseded findings. Do not treat accepted agent evidence as a substitute for root evidence.
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

## 9. Rollback and recovery posture

Preserve the current dirty worktree at `C:\morphic_v1\.worktrees\operator-workbench-phase1`. Do not reset, clean, or broadly stage it. `git status --porcelain=v1 -uall` identifies the working-tree state, while the manifest identifies the exact 90 reviewed file bytes. Recovery means retaining those bytes and comparing status plus manifest; no destructive Git rollback command is authorized by this record.

Port 8765 has not been started from this candidate. If the candidate drifts or review fails, leave 8765 unstarted, preserve this v4 evidence, make only separately authorized corrections, repeat the complete verification ladder, and create a new freeze version.
