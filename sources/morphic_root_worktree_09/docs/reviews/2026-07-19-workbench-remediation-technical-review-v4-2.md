## Freeze-v4 Independent Review

**Verdict: REJECT**  
**Confidence: HIGH**  
**Counts:** P0=0 · P1=1 · P2=2 · P3=2

### Freeze identity and scope

| Boundary | Branch | HEAD | Manifest SHA-256 | Entries | `sha256sum -c` | Aggregate | Working scope |
|---|---|---|---|---:|---:|---|---:|
| START | `operator-workbench-phase1` | `3271ff9366ab3fecb2a158913a0cc19ed6a06726` | `9d0a26a13577ef4c86bca1309fd2672123b7675dd4c4b13393ac76997b7843ad` | 41 | 41/41 OK | `60f284e31cd620c438739b8b4573e96f5b0eb963c01cba33302357daaab6df38` | Exact 42 paths |
| END | `operator-workbench-phase1` | `3271ff9366ab3fecb2a158913a0cc19ed6a06726` | `9d0a26a13577ef4c86bca1309fd2672123b7675dd4c4b13393ac76997b7843ad` | 41 | 41/41 OK | `60f284e31cd620c438739b8b4573e96f5b0eb963c01cba33302357daaab6df38` | Exact 42 paths |

Scope-set differences were empty at both boundaries. All 41 manifest files were read completely. No drift occurred.

## Findings

### P1 — Concurrent scans can create two uncontrolled poll loops, mix results, and orphan one server process

**Locations:**  
- `apps/web/static/workbench-api.js:10-13`  
- `apps/web/static/app.js:323-405`  
- `apps/web/static/app.js:669-697`

Only **New Case** is disabled while a mutating request is pending. The analysis-start control remains enabled, and `startScanJob()` has no single-flight guard.

Adversarial trace:

1. Operator starts scan A.
2. Before A’s response, operator starts scan B for the same client.
3. A returns and sets `activeJobId=A`; polling A begins.
4. B returns and replaces it with `activeJobId=B`; polling B begins.
5. Both asynchronous fetches can schedule independent timers. Because `jobPollTimer` stores only the latest handle, clearing it cannot cancel the other loop.
6. Whichever job completes last overwrites shared `scanResults` and `runTrace`; completion order can disagree with `activeJobId`.
7. New Case stops only B. If A remains active, it becomes orphaned server work and may still generate reports.

The exact-artifact backend prevents A from consuming B’s files, but the shared frontend state can still display the wrong run and fail to stop all work.

### P2 — New Case hides status panels without clearing sensitive lifecycle state

**Locations:**  
- `apps/web/static/app.js:731-766`  
- `apps/web/static/index.html:447-466`  
- `apps/web/static/index.html:596-614`

Reset hides the scan and harmonization panels but leaves values such as:

- old job IDs;
- status and return code;
- phase/substep;
- scan progress width and `aria-valuenow`;
- harmonization status, mode, lease/heartbeat, cycles, and error text.

On the next start, the panel is unhidden before the first status poll returns. Old-case values can therefore briefly reappear alongside the new job ID. This violates the intended privacy boundary and the documented “privacy-complete” reset contract.

### P2 — Switching preview modes retains the previous report in hidden DOM

**Location:** `apps/web/static/app.js:501-531`

When switching:

- HTML → text/PDF: the iframe is hidden, but its old `srcdoc` remains.
- Text → HTML: the text element is hidden, but its old content remains.

Thus, a previously selected report remains resident in hidden DOM while another report is displayed. New Case clears the iframe, but ordinary report-to-report reuse does not. Each mode transition should clear the inactive preview carrier before rendering the selected report.

### P3 — Regression tests do not behaviorally prove several claimed former-bug closures

**Locations:**  
- `tests/browser/workbench.spec.js:53-57`  
- `tests/browser/workbench.spec.js:110-149`  
- `tests/test_workbench_dogfood_navigation_accessibility.py:59-72`

Gaps include:

- Live radio focus is behaviorally checked only for `End`; Arrow and `Home` rely largely on source-token assertions.
- The progress test directly assigns `aria-valuenow=67`; it does not invoke polling and therefore would not fail if poll-driven ARIA updates broke.
- The stale-bootstrap test delays only the first registry request. It does not exercise reset between later bootstrap awaits, so it would not catch delayed report/hardware/draft rehydration regressions across the full sequence.
- No test covers scan A/B concurrency, competing poll loops, result overwrite, or reset stopping every active scan.

### P3 — Documentation overstates closure despite remaining reset/test gaps

**Locations:**  
- `docs/superpowers/plans/2026-07-19-workbench-dogfood-remediation.md:94-100`  
- `docs/superpowers/plans/2026-07-19-workbench-dogfood-remediation.md:154-169`

The document describes the reset as privacy-complete and states that the candidate includes behavioral closure for lifecycle/accessibility issues. The retained status DOM, retained alternate preview content, concurrent-scan gap, and non-behavioral test areas above make those closure statements unsupported.

## Adversarial areas inspected without additional findings

- Exact scan A/B artifact attribution at the backend.
- Windows process-tree/POSIX process-group scan stop implementation.
- New Case during tracked mutation and stale bootstrap generation checks.
- Pending/running harmonization stop.
- Stop marker versus stale harmonization worker save.
- Two-process terminal trace finalization.
- Operator checks before scan status/results/stop.
- Tenant report-root stability after environment mutation.
- Productive multi-profile telemetry ordering.
- Choice-card live-node focus and Arrow/Home/End implementation.
- Progressbar markup/update/reset implementation.
- Mobile horizontal-overflow rules and acceptance.
- CSP, self-hosted assets, lack of inline scripts/styles, and sandboxed preview.
- Reset followed by a new HTML preview.

## Read-only/no-drift statement

- No tests, imports, servers, installs, checkouts, resets, cleanups, or repository writes were performed.
- No repository files were created or modified.
- End identity, hashes, aggregate, and exact scope matched START with no drift.