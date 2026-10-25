# Gate 5 Current Handoff and Kilo Stability Record

Snapshot: `2026-08-07T22:13:19+02:00`

## Exact Repository State

- Worktree: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
- Branch: `report-ux-polish`
- HEAD: `2d38d3bfa3f204491fe066fbc986e07fffc2ff06`
- Upstream: `upstream/report-ux-polish`, `0 ahead / 0 behind`
- Git index: empty
- Gate-5 WIP manifest: `PROJECT_MEMORY/2026-08-06-gate5-wip-source.sha256`
- WIP verification: `GATE5_WIP_MANIFEST_OK 33/33`
- WIP-manifest SHA-256: `82fb7525f1da1a186147663a55be04efa756f69c1aa5de8dcd7220c42de36d59`
- No source file was changed after the WIP verification. This handoff and the
  matching new-session prompt are intentionally outside that recovery manifest.

The worktree is intentionally dirty because it contains accepted uncommitted
Gate-4 work, Gate-5 source and test work, recovery records, and historical
untracked artifacts. Never stage, commit, push, reset, clean, checkout, or
delete historical artifacts without separate user authorization.

## Gate 5 State

Gate 5 is **NOT ACCEPTED**.

- Tasks 1 through 7 are implemented and taskwise independently reviewed.
- The final Gate-5 Python suite passed on the current WIP bytes:
  `3693 passed, 17 skipped, 9 known Windows DPAPI decode warnings in 513.64s`.
- The final isolated browser matrix passed on the current WIP bytes:
  `51 passed` in four serial shards: `13 / 13 / 13 / 12`.
- The focused Gate-5 evidence already recorded before the full matrices remains:
  focus `408 passed`, focused browser `1 passed`, and explanation/Task-5/6/UI
  matrix `126 passed`.
- The remaining Task-8 work is a fresh manual Desktop/375px run on the correct
  isolated entrypoint, then the two final whole-Gate reviews, source manifest,
  freeze, acceptance record, hash verification, Golden Record update, and final
  uncommitted checkpoint.

## Important Manual-Acceptance Correction

An attempted manual run at `2026-08-07` used this unsupported combination:

```text
MORPHIC_RUNTIME_DIR=<temporary path>
python -m uvicorn apps.web.main:app
```

It failed on `POST /api/emf/enable` with `RuntimeError: EMF generation authority
is unreadable`. This is **not a confirmed Gate-5 product defect**.

Root cause:

- `apps.web.main:app` is the module-global app built with `create_app()` and
  therefore retains its default `cwd/codex_tmp` authority root.
- That existing root contains a deliberately fail-closed historical partial
  record: `codex_tmp/emf-telemetry-authority.json` is `{"enabled":false}` and
  has no matching generation file.
- The intended isolated entrypoint is `tests/browser/isolated_server.py`, which
  calls `create_app(runtime_dir=runtime_root / "runtime")` explicitly.
- `Run-WebUI.ps1 -IsolatedAcceptance` deliberately starts that same factory
  entrypoint, not `apps.web.main:app` directly.

The incorrect direct server also migrated the tracked fixture
`data/harmonization_jobs/harm_ba41c018.json`. It was restored byte-for-byte to
HEAD. The temporary server, script, runtime, and port `55737` were removed.

Do not change production code for this incident unless a new RED test proves a
failure of a supported entrypoint.

## Exact Next Technical Sequence

1. Start a fresh Kilo session using
   `PROJECT_MEMORY/2026-08-07-gate5-new-session-prompt.md`.
2. Verify the WIP manifest before any source change. Stop and investigate any
   mismatch.
3. Run the resource/process/port preflight. Do not run a full matrix under
   `3.5 GiB` free RAM.
4. Repeat manual Desktop and 375px acceptance only through the isolated factory
   server: `tests/browser/isolated_server.py` or
   `Run-WebUI.ps1 -IsolatedAcceptance`. Never use direct Uvicorn plus a
   temporary `MORPHIC_RUNTIME_DIR` for this purpose.
5. Record actual status parity, default-off, deliberate enable/disable,
   `System-/Entropie-basierter EMF-Proxy-Index`, four source keys/statuses,
   fallback visibility, invalid aggregate no-gauge rendering, and no 375px
   horizontal overflow. Inspect temporary screenshots, then remove all temporary
   server/runtime/script/screenshot artifacts.
6. If the source bytes remain unchanged, obtain a new independent whole-Gate
   specification review and then a separate quality/security review. A valid
   finding requires a fresh RED/GREEN loop and rerun of all affected/full
   matrices before re-review.
7. Only after both APPROVE verdicts, create the Gate-5 source manifest, review
   records, freeze record, acceptance status, and Golden Record update. Verify
   every recorded SHA-256 before claiming acceptance.

## Kilo Hang and Token-Economy Findings

The current Kilo process was measured at `2026-08-07T22:07` with:

- start time `2026-08-06T00:09:28+02:00` (more than 46 hours old);
- `3.72 GiB` private memory and `2.08 GiB` working set;
- free RAM repeatedly below the Gate-5 threshold (`2.10-2.60 GiB`), and later
  `1.11 GiB` at the `22:13` snapshot.

This violates the project stability protocol in `PROJECT_MEMORY/00_CURRENT_STATE.md`:
compact/restart Kilo after 12 hours or above 2 GiB private memory. It explains
the apparent lack of progress: the session itself became memory-constrained.
It does not indicate a hanging Python suite. The complete suite and browser
matrix both finished successfully.

Contributing token/context pressure was also observed:

- broad `git status` output contained many historical untracked artifacts;
- full test-dot streams and warning tracebacks were retained in the session;
- a complete historical session transcript was large enough to be truncated;
- past sessions recorded a model-output-limit event;
- the Golden Record documents an intermittent large-worktree completion hang in
  integrated Grep/Glob tools. Use bounded `rg` through Bash instead, never
  parallel broad integrated Grep/Glob calls.

`kilo --version` is `7.4.20` and `kilo config check` reports no warnings. The
global config has no explicit `compaction` block, so it relies on Kilo defaults.
Do not put provider credentials into this handoff or future prompts.

## Mandatory Session Discipline

- At every stable task boundary and before a full suite, write or refresh a
  concise project checkpoint with branch, HEAD, WIP hash, dirty scope, exact
  next command, test result, ports, and temporary-runtime status.
- Use `/compact` at the first of: 90 minutes of active work, 1.5 GiB Kilo
  private memory, large review output, or before a full suite/review dispatch.
- End and reopen a fresh session at 12 hours or 2 GiB Kilo private memory. Do
  not wait for resource pressure.
- Keep one primary task and one long-running command at a time. Full suites,
  browser matrices, and reviews are serial.
- Prefer bounded summaries: `git diff --stat`, named file reads, targeted `rg`
  with a timeout, and test summaries. Never dump all untracked artifacts, an
  entire transcript, or a complete giant diff into the session.
- Use the project checkpoint as authority. Kilo session history is only a
  convenience layer and must not be reconstructed wholesale during recovery.
- Consider explicitly setting `compaction.auto=true` and `compaction.prune=true`
  in global Kilo configuration after a separate review of that configuration.

## Current Operational State

- No stale pytest, Uvicorn, isolated-server, Playwright, scan-gate, or
  Harmonization process was found after cleanup.
- Ports `8000`, `8090`, `8765`, `8766`, and `55737` were free at the snapshot.
- No temporary Gate-5 manual acceptance server or runtime remains.
- The current session should now be ended rather than used for further Gate-5
  implementation because it is below the required RAM threshold.
