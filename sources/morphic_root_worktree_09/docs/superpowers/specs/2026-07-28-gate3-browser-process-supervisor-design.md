# Gate 3 Browser Process Supervisor Design

**Date:** 2026-07-28
**Status:** Implemented and focused-verified
**Scope:** Remediation F process authority for the isolated browser-test runner

## 1. Goal

The isolated Playwright runner must own every server and Playwright process tree
from spawn until verified cleanup. Synchronous and asynchronous spawn failures,
runner shutdown, test timeout, leader exit, and cleanup failure must all finish
within one bounded cleanup window without deleting forensic runtime data while a
test-owned process may still exist.

The two Gate-3 Node harnesses in
`tests/test_workbench_scan_profile_pool_js.py` remain bounded by an explicit
timeout and must emit an awaited completion marker after their final assertion.

## 2. Selected Architecture

`tests/browser/run-isolated-tests.js` no longer starts the isolated server or
Playwright CLI directly. Each productive command is started by one dedicated
Python supervisor under `tests/browser/`.

The supervisor:

- creates the productive child itself;
- records the child's PID and creation time before publishing readiness;
- injects a cryptographically random, run-local process-tree token only into
  the isolated child environment;
- remains alive until the complete productive tree is absent;
- owns all TERM/KILL escalation and descendant discovery;
- exits nonzero when tree absence cannot be proven.

The Node runner tracks only the supervisor process and never falls back to
signalling a stale productive PID or process-group number.

## 3. Authority And Data Flow

1. `runGroup()` allocates the isolated runtime root, port, health token, and a
   separate random process-tree token for each supervised command.
2. Node starts the supervisor with the productive command and clean isolated
   environment. The tree token is not placed in command arguments, logs, or
   runtime records.
3. The supervisor starts the productive child inside a platform-specific
   lifecycle boundary: a Job Object on Windows or a new session on POSIX. It
   captures the root identity internally and publishes only the fixed readiness
   record with no process identity data.
4. Node waits for supervisor readiness before waiting for server health or the
   Playwright result.
5. Cleanup sends a private `stop` control message. EOF, runner termination, and
   supervisor exceptions enter the same cleanup boundary.
6. The supervisor stops the productive root first, then converges the
   platform-specific containment authority: stable Job membership on Windows,
   or repeatedly discovered exact identities on POSIX. It verifies absence
   before exiting.
7. Node removes the runtime root only after every supervisor reports successful
   convergence. Any cleanup ambiguity preserves the runtime root.

Real test harnesses may set the optional
`MORPHIC_BROWSER_SUPERVISOR_IDENTITY_SIDECAR` environment variable to an
absolute, test-owned, previously absent path. The supervisor consumes and
removes this variable before constructing any productive environment, then
atomically writes its immutable `pid` and `create_time` pair before readiness.
The normal runner never sets this variable. The path and identity never appear
in readiness, command arguments, logs, or productive environments.

## 4. Platform Contract

On Windows, assignment to the private kill-on-close Job Object is the stable
containment authority. Job membership authorizes every contained descendant even
if that process later removes or changes its environment token. Cleanup softly
terminates the still-exact productive root first, then uses bounded Job
termination and `ActiveProcesses` queries until the Job is empty. Any external
process considered by a test-harness fallback still requires exact PID/creation
time, owner, and token authority.

On POSIX, the supervisor creates a new session as a lifecycle boundary only. The
session and its numeric process-group ID never grant signal authority. The
supervisor records the same-owner baseline before spawn, discovers linked or
run-token-bearing candidates, and immediately revalidates PID, creation time,
owner, and run-local token before every individual TERM or KILL. Identity reuse,
owner/token drift, or unreadable relevant authority fails closed. Two consecutive
safe empty discovery scans are required before convergence.

Outside stable Windows Job membership, processes without the exact run-local
token are never signalled. Same-user processes whose environment or identity
cannot be read produce cleanup ambiguity, not false successful convergence.

## 5. Lifecycle And Concurrency

`runGroup()` registers its operation before the first spawn. Shutdown closes new
group admission, waits for registered operations only until one absolute
deadline, and deduplicates concurrent stop requests per supervisor.

Supervisor and runner cleanup share absolute deadlines. No phase receives a new
full timeout after a previous phase consumed time. Child `error`, `exit`, and
control-channel listeners are removed after settlement.

Real Python harness fallback cleanup also creates one absolute deadline at
entry. Protocol wait, token discovery, each exact TERM/KILL wait, supervisor
fallback, and final identity-absence verification consume only the remaining
time from that deadline. Deadline exhaustion is retained as a cleanup error
after any primary assertion or timeout. The protocol wait is capped below the
total budget to reserve `min(1 second, total / 2)` for exact fallback work;
this reserve does not extend or recreate the original deadline.

A supervisor spawn failure before readiness still removes an unused runtime
root. A productive spawn or cleanup failure preserves the runtime root whenever
process absence is not proven.

Primary errors precede cleanup errors in aggregate failures.

## 6. Node Harness Contract

Only `_run_app_script()` and `_run_render_script()` in
`tests/test_workbench_scan_profile_pool_js.py` receive the Gate-3 timeout and
completion protocol.

Each generated Node program:

- awaits its outer test operation;
- emits one unpredictable completion marker only after the last assertion;
- exits nonzero on rejected operations or missing completion;
- cannot pass merely because an unresolved Promise has no active Node handles.

The readiness protocol remains exactly
`{"event":"ready","schema_version":1}`. It contains no PID, creation time,
sidecar path, token, or command data.

Python requires both exit code zero and the expected marker. A timeout remains a
normal `subprocess.TimeoutExpired` test failure.

## 7. Error Handling

- Supervisor start failure: bounded failure, no productive child, safe removal
  of the unused runtime root.
- Productive spawn failure: supervisor exits nonzero after proving no productive
  process exists.
- Health or Playwright timeout: Node requests supervisor stop and waits only for
  the remaining global cleanup budget.
- Supervisor cleanup ambiguity: Node reports failure and preserves runtime data.
- Runner signal: new groups are rejected; active supervisors are stopped once;
  the runner exits only after bounded quiescence or an explicit cleanup failure.

No supervisor or control-channel failure may leave Node waiting indefinitely for
a live child.

## 8. Verified Test Coverage

Verified test-first coverage includes:

- synchronous and asynchronous supervisor spawn failure;
- productive server and Playwright spawn failure;
- child error before and after listener registration;
- shutdown after health but before Playwright spawn;
- concurrent `finally` and signal cleanup deduplication;
- leader exit with a resistant descendant;
- TERM-to-KILL escalation and global-deadline exhaustion;
- PID/create-time replacement and unreadable same-user candidates;
- supervisor/control-channel failure with runtime preservation;
- real platform-selective parent/descendant cleanup without network ports;
- missing Node harness completion marker and unresolved Promise;
- fixed timeout on exactly the two Gate-3 Node harness helpers.

The final focused run also proved that no runner, supervisor, isolated server,
Playwright, or browser descendant remained; no new owned temporary runtime was
left; and the Git index was empty.

## 9. Verified Result

- `process_tree_supervisor.py` is the sole productive process-tree authority;
  the experimental cleanup helper and Node PID/PGID fallback are absent.
- Independent Spec and Quality/Security review cycles completed with no open
  P0-P2 finding after the final documentation correction.
- Final focused results on identical bytes were: supervisor `94 passed, 3
  skipped`; option/runner contracts `62 passed`; two-helper boundary `2 passed,
  36 deselected`; Gate-3 Node neighbors `166 passed`; self-isolated browser grep
  `6 passed`.
- Final inventory found zero owned supervisor/server/Playwright processes, no
  readable token-environment leak, port 8766 free, accepted ports 8090/8765
  unchanged, unrelated temporary roots preserved, and an empty Git index.

This completes Remediation F only. Parent Gate 3 remains open until the later
full Python and complete browser matrices pass.

## 10. Non-Goals

- No production application or API changes.
- No general migration of historical Node harnesses.
- No reusable production process supervisor.
- No live-port use outside the existing self-isolated Playwright runner.
- No commit, staging, or cleanup of unrelated worktree changes.
