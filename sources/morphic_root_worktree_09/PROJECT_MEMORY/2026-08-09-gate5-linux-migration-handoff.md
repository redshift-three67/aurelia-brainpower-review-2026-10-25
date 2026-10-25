# Gate 5 Linux Migration Handoff

**Created:** 2026-08-09
**Purpose:** Exact continuation point for Gate 5, Task 8 on the local Debian root server
**Canonical Debian path:** `/opt/Prototypen/Radimorphic`
**Windows source worktree:** `C:/morphic_v1/.worktrees/operator-workbench-phase1`
**Windows root checkout is not the source:** `C:/morphic_v1` (`master@411ff09`)
**Windows local branch:** `report-ux-polish`
**Pushed migration branch:** `gate5-linux-migration-20260809`
**Gate-5 source checkpoint commit:** `77227be`
**Tracked completeness commit:** `397cc842177cfc2ad5dcbf243f2fb9c3a307c5f1`
**Authoritative continuation point:** latest tip of the pushed migration branch
**Original baseline HEAD:** `2d38d3bfa3f204491fe066fbc986e07fffc2ff06`
**Required remote:** `https://github.com/redshift-three67/radimorphic.git`
**Remote name in the Windows worktree:** `upstream`
**Remote integration target observed after fetch:** `upstream/report-ux-polish@59f8559`
**Gate status:** Gate 4 ACCEPTED; Gate 5 NOT ACCEPTED; Gate 6 blocked

## Paste This Into The New Linux Session

```text
Work only in `/opt/Prototypen/Radimorphic` on the local Debian root server.
Do not use or infer any Windows workspace as the project target. Start by printing
`pwd -P`, `git branch --show-current`, `git log -1 --format='%H%n%D'`,
`git diff --cached --name-only`, and the scoped tracked diff names. Identify the
remote whose URL is `https://github.com/redshift-three67/radimorphic.git`; it
was named `upstream` on Windows and will normally be named `origin` in a fresh
clone. Fetch `<remote>/gate5-linux-migration-20260809` and
`<remote>/report-ux-polish`. Start the continuation on the migration branch at
its latest remote tip. Commit `77227be` is the Gate-5 source checkpoint inside
that branch; later commits complete and document the exact tracked Windows
state. Treat the branch as an intentionally incomplete Gate-5 WIP checkpoint,
not as an accepted gate. A fresh clone of this branch must start with an empty
Git index and no tracked working-tree diff.

The Windows folder `C:/morphic_v1` is a multi-worktree container, not the
authoritative checkout. Its root checkout remained on `master@411ff09` with
separate historical edits. The authoritative Windows source was
`C:/morphic_v1/.worktrees/operator-workbench-phase1`. Do not copy the Windows
root `.git`, `.worktrees`, `.venv`, `node_modules`, caches, runtime directories,
or linked-worktree `.git` file into Debian. Those metadata contain Windows paths
and are not portable.

Preferred Debian bootstrap, executed with permissions appropriate for `/opt`:

1. Ensure `/opt/Prototypen` exists.
2. If `/opt/Prototypen/Radimorphic` does not yet exist, run:
   `git clone https://github.com/redshift-three67/radimorphic.git /opt/Prototypen/Radimorphic`
3. Run `cd /opt/Prototypen/Radimorphic` and verify `pwd -P` prints exactly
   `/opt/Prototypen/Radimorphic`.
4. Fetch the migration and integration branches, then create/switch the local
   branch from `<remote>/gate5-linux-migration-20260809`.
5. Verify the branch contains tracked completeness commit
   `397cc842177cfc2ad5dcbf243f2fb9c3a307c5f1` and that both Git diff commands
   are empty.
6. Create a new Linux Python 3.12 virtual environment inside the clone. Never
   reuse a copied Windows virtual environment.

If `/opt/Prototypen/Radimorphic` already came from a Windows folder upload,
inspect `.git` before doing anything else. If `.git` is a file referring to a
Windows `gitdir:` path, stop and replace that directory with a fresh clone; do
not repair linked-worktree metadata in place. Preserve the uploaded folder
separately only as an archive until the GitHub clone is verified.

The Windows push found that `upstream/report-ux-polish` had advanced by 26
commits from baseline `2d38d3b` to `59f8559`, while the Gate-5 checkpoint is one
separate commit based on `2d38d3b`. Do not force-push and do not blindly merge
all 26 commits into Gate 5. Inspect the divergence first. In particular,
`59f8559` is named `Punkt a: Remedy-Index auf einheitliches Report-Theme;
Top5-Smoke-Test entflakt`, and the remote history also contains Linux/container
pytest and Playwright stabilization commits. Use those commits as targeted
references for the Debian blocker. Integrate only technically required changes
after checking conflicts against current Gate-5 authority/UI bytes; every such
byte change invalidates reviews and requires fresh matrices.

Read, in this order:
1. PROJECT_MEMORY/2026-08-09-gate5-linux-migration-handoff.md
2. docs/superpowers/specs/2026-08-06-gate5-emf-authority-source-truth-design.md
3. docs/superpowers/plans/2026-08-06-gate5-emf-authority-source-truth.md
4. PROJECT_MEMORY/2026-08-09-gate5-session-verbatim.md only if exact user wording is needed.

`PROJECT_MEMORY/00_CURRENT_STATE.md` is included for historical continuity but
predates the final Windows review/fix/migration sequence. This migration handoff
is authoritative when the two documents differ.

Continue Gate 5, Task 8 from the persistent full-suite blocker. Do not restart
the implementation from scratch and do not treat the earlier Windows
specification review as current approval: it rejected the old snapshot and its
three findings were subsequently fixed. The pre-fix snapshot and review are
invalidated by source/test changes.

First establish a clean Linux execution environment. Use the project virtual
environment or create an equivalent Python 3.12 environment without modifying
application behavior. Set PYTHONUTF8=1, PYTHONIOENCODING=utf-8, and
OPENBLAS_NUM_THREADS=1 for test commands. Do not run tests, browser shards,
reviews, or manual acceptance in parallel. Do not use broad repository searches.
Use named file reads and targeted `rg` commands over explicit files.

Immediate diagnostic sequence:
1. Verify no pytest, Python test, Uvicorn, isolated_server, Playwright,
   scan-gate, or Harmonization process is running.
2. Run only:
   `python -m pytest tests/test_top5_workflow_smoke.py::test_top5_scan_writes_multiplex_exports -q --tb=short`
3. On Windows this test repeatedly timed out inside its own 180-second
   `subprocess.run` even with 5.86 GiB free RAM. Determine whether it passes on
   the unbounded Debian host. Do not increase or weaken the test timeout unless
   a real product defect or platform contract justifies a reviewed code change.
   Before changing the test, inspect the already-pushed remote fix with
   `git show 59f8559 -- tests/test_top5_workflow_smoke.py` and its directly
   changed production files. Do not cherry-pick it blindly because the commit
   also contains Remedy report-theme work.
   The migration branch already contains the Windows working-tree changes to
   `apps/cli/commands/scan.py` and
   `apps/cli/commands/helpers/utility_helpers.py`; therefore the Debian test
   must run against the same canonical Top-N session-ID bytes as the final
   Windows attempts.
4. If it fails on Debian, use systematic debugging: inspect the named test and
   the exact CLI child process, identify the final completed workflow step and
   distinguish computation hang from inherited stdout/stderr handles. Write a
   failing regression test before any production fix. Do not modify unrelated
   historical Gate-4/CLI work merely to silence the suite.
5. Re-run the two Windows timing flakes individually only if Linux reproduces
   them:
   - tests/test_browser_process_tree_supervisor.py::test_parallel_real_supervisors_have_disjoint_random_token_authority
   - tests/test_workbench_option_explanations.py::test_browser_runner_real_readiness_pipe_failure_breaks_writer_without_leak
   Both passed immediately in isolated Windows reruns and are not confirmed
   Gate-5 defects.

After the CLI blocker is green, run the affected Gate-5 regression explicitly.
The last Windows affected run was 994 passed in 84.78s. Then run the complete
Python suite exactly once on unchanged final bytes:
`python -m pytest tests -q --tb=short`.
Acceptance requires zero failures. Record exact pass/skip/warning counts and
duration. Linux will not reproduce the nine known Windows DPAPI decoding
warnings; record the actual Linux warning result instead of copying Windows
counts.

Then run the full isolated browser matrix serially with
`npm --prefix tests/browser test`. The runner uses four serial shards. Record
each shard count and duration. The last pre-fix Windows evidence was 51 passed
as 13/13/13/12, but it is invalidated by the fixes and must be regenerated.
Install browser dependencies only if missing and document the exact command.
The runner must leave no supervisor, isolated server, Playwright process,
runtime root, or listener behind.

Because production, authority, routing, report, and UI bytes changed, repeat
manual isolated desktop and 375px acceptance. Verify: /ui redirects to the
modern Workbench; initial default-off; deliberate enable and disable; modern
and legacy status parity; visible label
`System-/Entropie-basierter EMF-Proxy-Index`; source keys rng, cpu_timing,
system_load, sensor_entropy; transparent fallback; invalid aggregate renders
`--` without a gauge; no horizontal overflow at 375px; no browser, console,
page, or request errors. Remove all temporary screenshots, scripts, runtime
directories, and servers.

Create a fresh lowercase SHA-256 snapshot over the exact 31-file Gate-5 review
scope listed below. Normalize paths with forward slashes. Keep the temporary
pre-review snapshot outside final acceptance artifacts. Dispatch a fresh,
read-only whole-gate specification review against current working-tree bytes.
No tests, edits, commits, staging, servers, integrated grep, integrated glob,
or broad git status in the reviewer. The specification acceptance is APPROVE
with P0=P1=P2=P3=0. A tool-completion failure without verdict/finding is not a
reject; repeat only the review if the snapshot is unchanged.

After specification approval, verify the same snapshot byte-for-byte and
dispatch a separate fresh quality/security whole-gate review with identical
scope and read-only limits. Quality acceptance is APPROVE with P0=P1=P2=0.
Any valid finding must be technically verified, fixed minimally with strict
TDD, and followed by affected tests, full Python suite, browser matrix, manual
acceptance where relevant, a new snapshot, and both reviews from the start.

Only after both reviews approve the exact same verified snapshot, create:
- docs/reviews/2026-08-06-gate5-emf-authority-source-truth-review-1.md
- docs/reviews/2026-08-06-gate5-emf-authority-source-truth-review-2.md
- docs/reviews/2026-08-06-gate5-emf-authority-source-truth-freeze.sha256
- docs/reviews/2026-08-06-gate5-emf-authority-source-truth-freeze.md
- docs/status/2026-08-06-gate5-emf-authority-source-truth-acceptance.md

The final source manifest must contain every changed or directly used Gate-5
production, legacy, test, design, plan, authority, and browser-runner file.
Exclude review documents, freeze record, acceptance status, and PROJECT_MEMORY.
Verify MANIFEST_OK N/N and the hashes of both review documents, freeze record,
and acceptance record. Then and only then update
PROJECT_MEMORY/00_CURRENT_STATE.md to Gate-5 ACCEPTED, preserve Gates 1-4 as
accepted, and mark Gate 6 as next but not started.

Do not call Gate 5 ACCEPTED unless both reviews approve the same hash-verified
snapshot, all required records exist, every hash verifies, the Git index is
empty, and no temporary Gate-5 process/artifact remains. Do not commit or push
again unless the user gives a new explicit instruction.
```

## Current Technical State

The Windows session resumed from a fully tested but not reviewed Gate-5 source
state. A fresh 31-file pre-review snapshot was created at:

`C:\Users\HUBERT~1\AppData\Local\Temp\opencode\gate5-prereview-20260809T072959Z.sha256`

It contained 31 entries and had SHA-256:

`b4cc05948d944cb2bd0433ade6abc2bba4d51f15ef32bfea6dbffc5c8b0d52b9`

That snapshot is obsolete and must never be used for acceptance because source
and test bytes changed after the review findings.

### Rejected Specification Review

- Child session: `ses_01a919c57ffelv6Gqe16VmZ0jf`
- Verdict: `REJECT`
- Counts: `P0=0 P1=2 P2=1 P3=0`
- Snapshot was verified unchanged before findings were investigated.

Findings and resulting changes:

1. `apps/web/emf.py:234` held a blocking cross-process authority lock over
   `await websocket.send_json()`. A same-event-loop disable or another lock
   acquisition could block the event loop behind WebSocket backpressure.
   - `apps/web/emf_authority.py` now provides `async_publish_permit()` and
     acquires/releases the synchronous cross-process permit through
     `asyncio.to_thread`, with cancellation cleanup.
   - `apps/web/emf.py` offloads authority reads/writes and uses the async permit
     for WebSocket emission.
   - `apps/web/security.py` uses the async permit for final HTTP body emission.
   - `apps/web/workbench.py` offloads authority lease reads.
   - TDD coverage:
     `tests/test_emf_enable_authority.py::test_async_publish_permit_waits_without_blocking_event_loop`
     and
     `tests/test_gate5_final_security_remediation.py::test_websocket_backpressure_does_not_deadlock_same_loop_disable`.

2. `apps/web/static/app.js:904` retained old active calibration/source UI when
   the post-mutation hardware refresh failed.
   - The catch path now sets `hardwareTruth = null` and clears
     `#realtime-calibration` plus `#hardware-gate-warnings` before showing the
     existing explicit endpoint error.
   - TDD coverage:
     `tests/test_gate5_emf_source_truth_js.py::test_failed_hardware_refresh_invalidates_stale_emf_rendering`.

3. `web_app.py:765` allowed a client directory symlink/junction to expose
   external report names and sizes during legacy report listing.
   - Listing now resolves the allowed root, client directory, walked roots,
     child directories, and report files; it prunes or skips every path outside
     the canonical allowed root before metadata access.
   - TDD coverage uses a real Windows junction fallback:
     `tests/test_gate5_final_security_remediation.py::test_legacy_report_list_rejects_client_directory_symlink_escape`.

No fresh specification approval exists after these fixes. No quality/security
review has run on these fixed bytes.

## Verification Evidence After Fixes

Valid targeted evidence on the fixed bytes:

- New permit/backpressure tests: `2 passed in 4.21s`.
- Stale hardware refresh regression: `1 passed`; `node --check apps/web/static/app.js` passed.
- Legacy report symlink plus neighboring list/roundtrip tests: `3 passed in 1.95s`.
- Explicit 12-file Gate-5/security regression: `994 passed in 84.78s`.
- Two harmonization files investigated after an invalid timed-out run:
  `212 passed in 19.17s`.
- Two full-suite timing failures rerun in isolation:
  `2 passed in 3.98s`.

Invalid or failing evidence:

- A full suite with a 700-second tool timeout stopped around 90%; no verdict.
- A mistaken `--last-failed` diagnostic selected the full suite and stopped at
  38%; no verdict.
- The completed full suite result was:
  `3724 passed, 17 skipped, 3 failed, 9 warnings in 857.09s`.
- Failure 1:
  `tests/test_browser_process_tree_supervisor.py::test_parallel_real_supervisors_have_disjoint_random_token_authority`.
  It observed an existing but still-empty second marker file. It passed in the
  immediate isolated rerun.
- Failure 2:
  `tests/test_top5_workflow_smoke.py::test_top5_scan_writes_multiplex_exports`.
  Its CLI child exceeded the test's internal 180-second timeout. It failed
  again in isolation at low free RAM and again with 5.86 GiB free RAM. This is
  the only persistent blocker at migration time.
- Failure 3:
  `tests/test_workbench_option_explanations.py::test_browser_runner_real_readiness_pipe_failure_breaks_writer_without_leak`.
  It passed in the immediate isolated rerun.
- The nine warnings were the known Windows DPAPI subprocess decode warnings.

The earlier pre-fix evidence from the user was 3723 passed, 17 skipped, 51
browser tests, and manual desktop/375px PASS. It was valid before the four new
tests and source changes, but it no longer satisfies final acceptance.

## Exact Review Scope

Design and plan:

- `docs/superpowers/specs/2026-08-06-gate5-emf-authority-source-truth-design.md`
- `docs/superpowers/plans/2026-08-06-gate5-emf-authority-source-truth.md`

Production and legacy:

- `apps/web/emf.py`
- `apps/web/emf_authority.py`
- `apps/web/main.py`
- `apps/web/security.py`
- `apps/web/hardware_truth.py`
- `apps/web/workbench.py`
- `web_app.py`
- `core/realtime/emf_profile.py`

Frontend and monitor:

- `apps/web/static/app.css`
- `apps/web/static/app.js`
- `apps/web/static/index.html`
- `apps/web/static/workbench-api.js`
- `apps/web/static/workbench-render.js`
- `apps/web/static/workbench-state.js`
- `apps/web/static/emf-monitor.css`
- `apps/web/static/emf-monitor.js`

Gate-5 tests:

- `tests/browser/workbench.spec.js`
- `tests/test_emf_enable_authority.py`
- `tests/test_web_emf_security.py`
- `tests/test_web_shell.py`
- `tests/test_gate5_emf_route_parity.py`
- `tests/test_gate5_emf_source_truth_js.py`
- `tests/test_gate5_final_security_remediation.py`
- `tests/test_realtime_emf_profile.py`
- `tests/test_web_hardware_truth.py`
- `tests/test_web_hardware_status.py`
- `tests/test_workbench_option_explanations.py`
- `tests/test_workbench_ui_quality_contracts.py`
- `tests/test_workbench_report_dom_js.py`

Directly used browser runner for the final source manifest:

- `tests/browser/run-isolated-tests.js`
- `tests/browser/isolated_server.py`
- `tests/browser/process_tree_supervisor.py`
- `tests/browser/playwright.config.js`
- `tests/browser/package.json`
- `tests/browser/package-lock.json`

## Git And Worktree Boundaries

The Windows worktree was intentionally dirty before this session. Historical
untracked artifacts must not be treated as Gate-5 findings or silently cleaned.
The first migration commit intentionally omitted six pre-existing tracked
changes, but the completeness audit proved they were needed to reproduce the
actual CLI/full-suite/documentation bytes. A later scoped completeness commit
therefore includes:

- `apps/cli/commands/helpers/utility_helpers.py`
- `apps/cli/commands/scan.py`
- `tests/test_gate4_report_catalog_js.py`
- `tests/test_topn_cli_phase1_options.py`
- `tests/test_topn_export_paths.py`
- `PROJECT_MEMORY/00_CURRENT_STATE.md`

The CLI files implement the canonical `S_TOP{N}_SESSION` catalog marker contract;
the three tests participate in the actual full-suite state; the Golden Record
preserves historical continuity. The latest migration-branch tip therefore
contains every tracked source, test, design, plan, and project-memory byte that
differed in the Windows worktree at handoff time.

This completeness statement refers specifically to the active Windows source
worktree `C:/morphic_v1/.worktrees/operator-workbench-phase1`. It does not refer
to the separate root checkout at `C:/morphic_v1`, which remained on
`master@411ff09` with local changes in `PROJECT_MEMORY/00_CURRENT_STATE.md`,
`apps/web/static/app.js`, and `apps/web/static/index.html`. Those root-checkout
bytes are historical and must not overwrite the migration branch on Debian.

Historical untracked runtime, shadow-copy, screenshot, cache, and generated
artifacts remain deliberately excluded from Git because they are not required
to build, test, review, or continue Gate 5. Do not copy them into a fresh clone.
This is an exact reproducible tracked project checkpoint, not a byte-for-byte
archive of disposable local artifacts.

The checkpoint was pushed to `upstream/gate5-linux-migration-20260809` because
a non-fast-forward push to the advanced `upstream/report-ux-polish` was
correctly rejected. The user explicitly authorized this migration push; no
later implementation commit/push is authorized without another instruction.

### Completeness Verification On Debian

After switching to the migration branch in `/opt/Prototypen/Radimorphic`, verify:

```bash
test "$(pwd -P)" = "/opt/Prototypen/Radimorphic"
git diff --name-only
git diff --cached --name-only
git log -1 --format='%H%n%D'
git merge-base --is-ancestor 397cc842177cfc2ad5dcbf243f2fb9c3a307c5f1 HEAD
```

Both diff commands must print nothing. Compare the reported HEAD with the
remote migration-branch tip before installing dependencies or running tests.
The `merge-base` command must exit with status 0.
If the uploaded Windows folder contains additional untracked artifacts, ignore
them and use the GitHub branch as the source/test/documentation authority.

## Port And Process Note

On Windows, `127.0.0.1:8090` was intentionally owned by an external Radi144
reference server (`C:\Users\Hubert111\Documents\Radi144`) and the user required
it to remain running. The Gate-5 plan permits port 8090 to be free **or owned by
a separately documented user process**. The process was not terminated and is
irrelevant on the Debian host. Manual Gate-5 acceptance must use an isolated
free port and never 8090.

## Token And Resource Strategy

- Keep one main step active.
- Keep an evidence ledger with exact command, byte state, result, and duration.
- Reuse evidence only while source/test bytes are unchanged.
- Run focused tests before expensive matrices.
- Run Python full suite, browser matrix, reviews, and manual acceptance serially.
- Use small named read batches and explicit-file `rg`; no open repository search.
- Do not reconstruct historical transcripts during implementation; consult the
  separate verbatim file only for disputed requirements.
- A pure tool-completion failure without verdict does not invalidate unchanged
  test evidence or become a review rejection.
- Any source/test change invalidates both reviews and all final snapshot hashes.
