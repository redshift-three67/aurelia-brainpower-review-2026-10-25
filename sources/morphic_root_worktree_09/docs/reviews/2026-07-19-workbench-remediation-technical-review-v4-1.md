## Operator Workbench Freeze v4 — Independent Technical Review

**Verdict: REQUEST CHANGES**  
**Confidence: HIGH**

### Identity and freeze verification

| Check | Start | End |
|---|---|---|
| Repository | `C:/morphic_v1/.worktrees/operator-workbench-phase1` | Same |
| Branch | `operator-workbench-phase1` | Same |
| HEAD | `3271ff9366ab3fecb2a158913a0cc19ed6a06726` | Same |
| Manifest SHA-256 | `9d0a26a13577ef4c86bca1309fd2672123b7675dd4c4b13393ac76997b7843ad` | Same |
| `sha256sum -c` | 41/41 OK | 41/41 OK |
| Manifest entries | 41 | 41 |
| Git modified/untracked population | 42 paths | 42 paths |
| Scope equality | Exact: 41 manifest paths plus v4 manifest | Exact |
| `git diff --check` | Exit 0; line-ending warnings only | Exit 0; line-ending warnings only |

**Inspection confirmation:** all **41/41 manifest-scoped files** were read and inspected. The two remediation plans and rejected v1–v3 manifests were reconciled as historical evidence only.

**Aggregate:** Hashing the 41 hash lines **as listed** produces the expected  
`60f284e31cd620c438739b8b4573e96f5b0eb963c01cba33302357daaab6df38`.

A literal `LC_ALL=C sort` before hashing instead produces  
`6af655002fa58e40a28f11f9e7ccc90037bacf5468e258a11f5564030a64d6c0`; see P3 finding below.

### Findings

#### P1 — Pending harmonization jobs stop polling permanently

**Location:** `apps/web/static/app.js:556-585`, especially `579-581`

**Impact:** `WorkerHarmonizationService.start()` can legitimately return a persisted job while it is still `pending`. The browser polls once, but schedules another poll only when status is exactly `running`. A normal process-start race can therefore leave a successfully launched harmonization permanently displayed as pending with no automatic progress updates.

**Reproduction reasoning:** Start returns immediately after spawning the worker. If the first status snapshot is `pending`, line 579 does not schedule `harmonizationPollTimer`; no later transition to `running` is observed.

**Required fix:** Treat all nonterminal active states, at minimum `pending` and `running`, as pollable. Add behavioral coverage where start and first poll return `pending`, followed by `running` and terminal status.

---

#### P1 — Failed New Case teardown leaves the old case half-detached

**Location:** `apps/web/static/app.js:669-703`, especially `678-682` and `698-702`

**Impact:** Reset increments `caseGeneration` and cancels both poll timers before authoritative server stops succeed. If either stop fails, reset returns `false`, but old asynchronous continuations remain invalidated and monitoring remains cancelled while active job IDs and case data are retained. The operator loses authoritative observation of still-running work.

**Reproduction reasoning:** Give the state an active scan, make its stop endpoint fail, and call reset. The function reaches the catch with the old ID still present, but generation has advanced and the prior poll timer is gone.

**Required fix:** Do not commit generation invalidation or timer cancellation until all required server teardown operations succeed, or restore the old generation and restart authoritative polling on failure. Add a browser test asserting the complete failure postcondition, not only the successful-reset path.

---

#### P1 — Scan process-tree stop can report success after an unverified or incomplete kill

**Location:** `apps/web/scan_jobs.py:352-375`; inadequate test at `tests/test_web_scan_jobs.py:197-241`

**Impact:** Scan descendants may continue productive work after the API returns `stopped`.

**Reproduction reasoning:**

- Windows `taskkill` has no timeout and its return code is ignored.
- If `taskkill` fails while the parent exits, the code skips fallback termination because only the parent is polled; surviving children are never verified.
- POSIX sends one `SIGTERM` to the process group but later escalation kills only the parent process, not the group. A child ignoring `SIGTERM` can remain alive.
- The current tests use a fake parent and merely assert that `taskkill`/`killpg` was called; they never spawn or verify a descendant. The Windows fake even simulates a non-success parent outcome without checking command success.

**Required fix:** Bound the tree-kill command, inspect its result, retain the process-group identity, escalate the entire POSIX group with `SIGKILL`, and verify descendants cannot continue. Add a real synthetic parent-plus-child behavioral test on supported platforms.

---

#### P1 — Harmonization impulse cancellation latency is not actually bounded

**Location:** `apps/web/contracts.py:145,153-155`; `services/harmonization_worker.py:505-518`

**Impact:** A stop can remain ineffective for substantially longer than the advertised five-second bound while hardware/modulation code executes.

**Reproduction reasoning:** `pulse_seconds <= 5` bounds only the value passed to synchronous `modulate_hardware()`. There is no cancellation predicate or enforceable deadline inside that call. Additionally, `target_frequency` has no upper bound; modulation implementations can derive extremely large cycle counts from it. The worker cannot observe a stop until the synchronous call returns.

**Required fix:** Make impulse execution cooperatively cancellable with deadline checks, or isolate it in a killable bounded subprocess. Add a defensible target-frequency ceiling and behavioral coverage using a deliberately blocking/overrunning modulator.

---

#### P1 — Stop can race with and still emit a completed-cycle telemetry event

**Location:** `services/harmonization_worker.py:554-583`

**Impact:** Trace telemetry can claim `cycle_metrics` for work that was concurrently stopped, contradicting the stated “interrupted work cannot be counted or emitted as completed” contract.

**Reproduction reasoning:** After `execute_pulse_pause_cycle()` returns true, the worker builds and appends `cycle_metrics` at line 561. Only afterward does it reload the job and check for `stopped`. A stop published in that interval therefore produces a completed-cycle event even though `cycles_completed` is not incremented.

**Required fix:** Serialize the terminal stop check and cycle commit at the same cross-process atomic boundary. Whichever operation acquires the boundary first must define the truthful ordering. Add a deterministic interleaving test that blocks immediately before cycle finalization and races stop against it.

---

#### P2 — Production report-preview response and browser renderer disagree

**Location:** `apps/web/reports.py:223-263`; `apps/web/static/app.js:501-531`; misleading mock at `tests/browser/workbench.spec.js:33-37`

**Impact:** A real preview displays an opaque report hash as its title and an empty size, rather than the report filename/metadata. The acceptance test passes only because it mocks fields the production API does not return.

**Reproduction reasoning:** Backend preview payloads expose `file_name` but no `title` or `size`. The browser reads `preview.title || reportId` and `preview.size`. The Playwright fixture supplies artificial `title` and `size` fields, masking the real contract.

**Required fix:** Either return `title`/`size` from the API or render `file_name` and actual available metadata. Make the browser test use the production payload shape.

---

#### P2 — Several claimed adversarial closures remain token/fake-domain tests

**Locations:**

- `tests/test_web_scan_jobs.py:197-241`
- `tests/test_workbench_review_regressions.py:115-151,227-266,269-296`
- `tests/browser/workbench.spec.js:136-149`
- `tests/test_workbench_dogfood_navigation_accessibility.py:10-93`

**Impact:** The suite can remain green while process descendants survive, reset failure leaves polling detached, pending harmonization never advances, cross-process stop ordering is wrong, or ARIA progress polling is broken.

**Reasoning:** Significant contracts are tested through source-string assertions, fake process calls, same-process threads, or manually assigning `aria-valuenow`. These do not exercise the concurrency/process/browser domains claimed by F3-02, F3-04, F3-05, F3-08, F3-12, and F3-13.

**Required fix:** Add behavioral tests for:

- a real synthetic process tree;
- pending-to-running browser polling;
- failed stop during New Case;
- cross-process worker-save versus stop;
- the stop-versus-cycle-finalization interleaving;
- real productive multi-profile telemetry chronology;
- polling-driven progressbar updates.

---

#### P3 — Manifest aggregate wording does not describe its actual recipe

**Location:** `docs/reviews/2026-07-19-workbench-remediation-technical-freeze-v4.sha256:14,32-36`

**Impact:** An independent reviewer following the stated “exact sorted hash lines” recipe obtains a different aggregate.

**Reproduction reasoning:** The expected aggregate is obtained from the lines in manifest order. A literal lexical sort moves the unsuffixed historical freeze relative to v2/v3 and produces `6af655…`, not `60f284…`.

**Required fix:** In the replacement freeze, either lexically sort the lines and regenerate the aggregate, or state precisely that the aggregate hashes the lines “as listed” without re-sorting.

### Counts

| Priority | Count |
|---|---:|
| P0 | 0 |
| P1 | 5 |
| P2 | 2 |
| P3 | 1 |
| **Total** | **8** |

### Drift statement

No reviewed file, manifest entry, branch, HEAD, scope path, or manifest hash drifted between start and end. The verdict is bound to the exact v4 bytes identified above.

### Review hygiene

- No tests, imports, application/server processes, package operations, or formatting commands were run.
- No files were created, modified, or deleted.
- Only read, Git inspection, search, and hashing operations were used.
- Issues encountered: harmless Git line-ending warnings and the manifest aggregate recipe ambiguity described above.