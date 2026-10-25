# Gate 3 Browser Process Supervisor Implementation Plan

> **Execution record:** Implemented task-by-task with the required Superpowers workflow. Checked boxes record verified completion.

**Goal:** Replace Remediation F's after-the-fact PID cleanup with one long-lived supervisor that owns each isolated server or Playwright process tree until verified convergence.

**Status:** Remediation F implemented, independently reviewed, and focused-verified. Parent Gate 3 remains open pending the later full Python and complete browser matrices.

**Architecture:** A Python supervisor starts one productive command, places it in a Windows Job Object or starts it in a new POSIX session used only as a lifecycle boundary, accepts a private stop request on stdin, and exits only after the complete tree is absent. POSIX signals are sent only to individually and immediately revalidated PID/create-time/owner/token identities; no numeric PGID grants authority. The Node runner tracks supervisors rather than productive PIDs, coordinates shutdown with one absolute deadline, and preserves runtime data on ambiguity. The two Gate-3 Node harnesses retain their explicit timeout and awaited completion-marker contract.

**Tech Stack:** Python 3.11+, `subprocess`, `ctypes`, `psutil`, Node.js `child_process`, pytest, Playwright.

**Constraint:** Do not commit or stage in this cumulative worktree. Do not use existing live ports. Do not layer a PID fallback on top of the supervisor; the experimental `process_tree_cleanup.py` path has been removed.

---

## File Map

- Create `tests/browser/process_tree_supervisor.py`: stable process-tree authority and control protocol.
- Create `tests/test_browser_process_tree_supervisor.py`: unit and real platform-selective supervisor contracts.
- Modify `tests/browser/run-isolated-tests.js`: spawn and track supervisors, not productive commands.
- Modify `tests/test_workbench_option_explanations.py`: Node runner lifecycle, shutdown, and supervisor integration contracts.
- Modify `tests/test_workbench_scan_profile_pool_js.py`: preserve the already implemented two-helper timeout and awaited marker contract.
- Delete `tests/browser/process_tree_cleanup.py`: obsolete after stable supervisor ownership is active.

## Task 1: Python Supervisor Core

**Files:**
- Create: `tests/browser/process_tree_supervisor.py`
- Create: `tests/test_browser_process_tree_supervisor.py`

- [x] **Step 1: Write RED tests for the control and result contract**

Create tests that invoke the supervisor around a tiny Python child and require a readiness JSON line without secrets:

```python
def test_supervisor_publishes_ready_then_propagates_child_exit(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(SUPERVISOR),
            "--",
            sys.executable,
            "-c",
            "raise SystemExit(7)",
        ],
        input="",
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    ready = json.loads(completed.stdout.splitlines()[0])
    assert ready == {"event": "ready", "schema_version": 1}
    assert completed.returncode == 7
    assert "MORPHIC_BROWSER_PROCESS_TREE_TOKEN" not in completed.stdout
    assert "MORPHIC_BROWSER_PROCESS_TREE_TOKEN" not in completed.stderr
```

Also add RED cases for missing command, malformed token, productive spawn failure, EOF-triggered cleanup, and explicit `stop\n` cleanup.

- [x] **Step 2: Run RED**

```cmd
set "PYTHONUTF8=1" && set "PYTHONIOENCODING=utf-8" && set "OPENBLAS_NUM_THREADS=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_browser_process_tree_supervisor.py -q --tb=short
```

Expected: collection or execution failures because the supervisor does not exist.

- [x] **Step 3: Implement the minimal protocol shell**

Implement these boundaries in `process_tree_supervisor.py`:

```python
TOKEN_ENV = "MORPHIC_BROWSER_PROCESS_TREE_TOKEN"
TOKEN_PATTERN = re.compile(r"^[0-9a-f]{32}$")
READY_RECORD = {"event": "ready", "schema_version": 1}


def _read_stop(stop_event: threading.Event) -> None:
    line = sys.stdin.readline()
    if line == "" or line.strip() == "stop":
        stop_event.set()


def main() -> int:
    command = _parse_command()
    token = os.environ.pop(TOKEN_ENV, "")
    if TOKEN_PATTERN.fullmatch(token) is None:
        raise SystemExit("invalid isolated browser process authority")
    tree = ProcessTree.start(command, token=token)
    print(json.dumps(READY_RECORD, sort_keys=True), flush=True)
    stop_event = threading.Event()
    threading.Thread(target=_read_stop, args=(stop_event,), daemon=True).start()
    return tree.run_until_exit_or_stop(stop_event)
```

Readiness must contain no PID, token, environment name, path, or command.

- [x] **Step 4: Run protocol GREEN**

Run the command from Step 2. Expected: protocol tests pass; platform containment tests may remain RED until Steps 5-8.

- [x] **Step 5: Write RED tests for stable Windows authority**

On Windows, spawn a productive root that starts a sleeping descendant, writes both PIDs to a test-owned file, then exits. Send `stop` and assert both exact PID/create-time identities are absent before the supervisor exits.

Add unit tests for:

```python
assert job.kill_on_close is True
assert job.assigned_root_identity == ProcessIdentity(root_pid, root_create_time)
assert job.active_processes() == 0
```

Simulate `AssignProcessToJobObject`, `TerminateJobObject`, and `QueryInformationJobObject` failures and require nonzero supervisor exit without signalling any unrelated PID.

- [x] **Step 6: Implement Windows Job Object ownership**

Use a private `_WindowsJob` class modeled on the already verified pattern in `services/scan_process_gate.py`, but keep this implementation under `tests/browser/`:

```python
class _WindowsJob:
    def __init__(self) -> None:
        self.handle = _create_kill_on_close_job()

    def assign(self, process_handle: int) -> None:
        if not kernel32.AssignProcessToJobObject(self.handle, process_handle):
            raise OSError(ctypes.get_last_error(), "AssignProcessToJobObject failed")

    def terminate(self, exit_code: int = 1) -> None:
        if not kernel32.TerminateJobObject(self.handle, exit_code):
            raise OSError(ctypes.get_last_error(), "TerminateJobObject failed")

    def active_processes(self) -> int:
        return _query_active_processes(self.handle)
```

Do not rely on `subprocess.Popen(CREATE_SUSPENDED)`: Python does not expose the
primary thread handle as a supported resume contract. Instead, run the same file
in a private `--entry` mode. The entry process blocks on a one-byte `go` pipe,
starts no productive child before that byte, and then `executes`/spawns the real
command only after the parent supervisor has assigned the entry process to the
Job Object:

```python
entry = subprocess.Popen(
    [sys.executable, __file__, "--entry", "--", *command],
    stdin=subprocess.PIPE,
    stdout=sys.stdout,
    stderr=sys.stderr,
    env=child_environment,
)
job.assign(int(entry._handle))
entry.stdin.write(b"g")
entry.stdin.close()
```

The `--entry` path must reject EOF or any byte other than `g` without spawning
the productive command. Job inheritance then contains the entry and all
productive descendants. Retain the Job handle until `ActiveProcesses == 0`.
Closing the supervisor must never release an active tree without kill-on-close
protection.

- [x] **Step 7: Write RED tests for POSIX identity authority**

On POSIX, start a root and resistant descendant in a new session. Require
root-first `SIGTERM`, individual descendant signalling, at most one `SIGKILL`
escalation per exact identity, and two safe empty scans before success. Unit-test
PID/create-time replacement as absence and unreadable or changed owner/token
authority as ambiguity. Assert that the implementation contains no `os.killpg`,
numeric PGID signalling, or process-group probe.

- [x] **Step 8: Implement POSIX identity ownership**

Capture the same-owner baseline before spawn, start with
`start_new_session=True`, and record the root creation time before readiness. The
new session is a lifecycle boundary only. Discover candidate identities through
parent linkage and the run-local token, then immediately revalidate PID,
creation time, owner, and token before each individual signal. Use one absolute
deadline and require two consecutive safe empty scans:

```python
term_signaled = set()
authority.signal(root_identity, force=False)
empty_scans = 0
while time.monotonic() < term_deadline:
    targets = authority.scan()
    for identity in targets:
        if identity != root_identity and identity not in term_signaled:
            if authority.signal(identity, force=False):
                term_signaled.add(identity)
    empty_scans = empty_scans + 1 if not targets else 0
    if empty_scans >= 2:
        return

authority.signal(root_identity, force=True)
kill_signaled = set()
empty_scans = 0
while time.monotonic() < deadline:
    targets = authority.scan()
    for identity in targets:
        if identity != root_identity and identity not in kill_signaled:
            kill_signaled.add(identity)
            authority.signal(identity, force=True)
    empty_scans = empty_scans + 1 if not targets else 0
    if empty_scans >= 2:
        return
```

`authority.signal()` must revalidate immediately rather than trust the preceding
scan. Never use the session ID or numeric PGID as signal authority. Unreadable
relevant identities and unexpected errors remain failures.

- [x] **Step 9: Run Task 1 GREEN and static checks**

```cmd
set "PYTHONUTF8=1" && set "PYTHONIOENCODING=utf-8" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_browser_process_tree_supervisor.py -q --tb=short
C:\morphic_v1\.venv\Scripts\python.exe -m py_compile tests/browser/process_tree_supervisor.py tests/test_browser_process_tree_supervisor.py
git diff --check -- tests/browser/process_tree_supervisor.py tests/test_browser_process_tree_supervisor.py
```

Expected: PASS; cached index empty; no test-owned process remains.

## Task 2: Node Runner Uses Supervisors

**Files:**
- Modify: `tests/browser/run-isolated-tests.js`
- Modify: `tests/test_workbench_option_explanations.py`

- [x] **Step 1: Write RED tests for supervisor spawn arguments**

Add Node behavior tests that inject `spawn` and assert both productive commands are wrapped:

```javascript
if (serverCall.command !== python) throw new Error('server supervisor missing');
if (!serverCall.args.includes('process_tree_supervisor.py')) throw new Error('wrong server owner');
if (!serverCall.args.includes('isolated_server.py')) throw new Error('server command missing');
if (!playwrightCall.args.includes('@playwright')) throw new Error('Playwright command missing');
if (!serverCall.options.env.MORPHIC_BROWSER_PROCESS_TREE_TOKEN) throw new Error('tree token missing');
if (serverCall.options.env.MORPHIC_BROWSER_PROCESS_TREE_TOKEN
    === playwrightCall.options.env.MORPHIC_BROWSER_PROCESS_TREE_TOKEN) {
  throw new Error('tree authority reused across commands');
}
```

Require supervisor stdin to be piped and productive token absence from argv.

- [x] **Step 2: Run RED**

```cmd
set "PYTHONUTF8=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_option_explanations.py -q --tb=short -k "browser_runner and supervisor"
```

Expected: FAIL because Node still spawns productive commands directly.

- [x] **Step 3: Implement `spawnSupervised()`**

Add one runner boundary:

```javascript
function spawnSupervised(command, args, options, dependencies = {}) {
  const treeToken = randomUUID().replaceAll('-', '');
  const supervisor = (dependencies.spawn || spawn)(
    resolvePython(),
    [PROCESS_TREE_SUPERVISOR, '--', command, ...args],
    {
      ...options,
      env: {...options.env, [TREE_TOKEN_ENV]: treeToken},
      stdio: ['pipe', options.stdout || 'pipe', options.stderr || 'pipe'],
      detached: false,
    },
  );
  return trackSupervisor(supervisor);
}
```

Use separate tokens for server and Playwright. Remove productive `detached` options and all Node-side productive PID/PGID signalling.

- [x] **Step 4: Write RED tests for readiness and natural exit**

Require Node to wait for the supervisor's single readiness record before server health or Playwright result handling. Malformed, duplicated, oversized, or token-bearing readiness output must fail closed.

- [x] **Step 5: Implement bounded readiness parsing**

Keep protocol parsing separate from productive log forwarding. Cap buffered protocol bytes and accept exactly:

```json
{"event":"ready","schema_version":1}
```

After readiness, forward remaining stdout/stderr according to the existing server-log and Playwright-output contracts.

- [x] **Step 6: Write RED tests for stop deduplication**

Call `cleanupGroup()` and `shutdown()` concurrently for one supervisor. Assert one `stop\n` write, one bounded wait, zero retained listeners, and one runtime decision.

- [x] **Step 7: Implement supervisor stop state**

Store one stop promise per supervisor:

```javascript
function stopSupervisor(supervisor, deadline) {
  const state = supervisorStates.get(supervisor);
  if (state.stopPromise) return state.stopPromise;
  state.stopPromise = requestStopAndWait(supervisor, deadline);
  return state.stopPromise;
}
```

Do not delete state until the supervisor exit/error has settled and listeners are removed.

- [x] **Step 8: Run Task 2 GREEN**

Run the full `tests/test_workbench_option_explanations.py` file and `node --check tests/browser/run-isolated-tests.js`. Expected: PASS.

## Task 3: Shutdown, Error Ordering, And Runtime Preservation

**Files:**
- Modify: `tests/browser/run-isolated-tests.js`
- Modify: `tests/test_workbench_option_explanations.py`

- [x] **Step 1: Write shutdown-vs-spawn RED tests**

Cover shutdown:

- after port allocation and before server supervisor spawn;
- after health and before Playwright supervisor spawn;
- while supervisor readiness is pending;
- while `finally` already owns the same stop promise.

Each case must end within one injected absolute deadline with no newly accepted group.

- [x] **Step 2: Implement one shutdown deadline**

Create the deadline once and pass remaining time to child and run quiescence:

```javascript
const deadline = now() + shutdownTimeoutMs;
await waitForOperations(children.map(stopSupervisor), remaining(deadline));
await waitForOperations(activeRunOperations, remaining(deadline));
```

The second phase never receives a fresh full timeout.

- [x] **Step 3: Write RED tests for supervisor failures**

Test synchronous spawn throw, asynchronous `error` before and after wait registration, malformed readiness, control-pipe write failure, supervisor timeout, and nonzero supervisor exit.

For every case assert:

- tracker/listener convergence;
- bounded runner completion;
- primary error before cleanup error;
- runtime removal only when absence is proven.

- [x] **Step 4: Implement fail-closed error aggregation**

Use one helper:

```javascript
function combinePrimaryAndCleanup(primary, cleanup) {
  if (!primary) return cleanup;
  if (!cleanup) return primary;
  return new AggregateError(
    [primary, cleanup],
    'Test group failed and cleanup also failed',
    {cause: primary},
  );
}
```

No `process.exitCode` path may leave a tracked supervisor or active run promise able to keep Node alive indefinitely.

- [x] **Step 5: Run Task 3 GREEN**

```cmd
set "PYTHONUTF8=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_option_explanations.py -q --tb=short
```

Expected: PASS with no port-owning process or temporary runtime from the tests.

## Task 4: Real Parent/Descendant And Harness Contracts

**Files:**
- Modify: `tests/test_browser_process_tree_supervisor.py`
- Modify: `tests/test_workbench_option_explanations.py`
- Verify: `tests/test_workbench_scan_profile_pool_js.py`

- [x] **Step 1: Add real platform-selective tree tests**

Spawn a real productive root that creates a resistant descendant and writes both identities. Force leader exit, request supervisor stop, and assert exact PID/create-time absence. On Windows also assert Job Object convergence; on POSIX assert new-session lifecycle isolation plus convergence through individually revalidated identities.

Use finite condition polling and `finally` cleanup. Never use fixed PIDs or signal any process lacking the test-owned authority.

- [x] **Step 2: Add real supervisor-failure preservation test**

Inject a controlled supervisor cleanup failure after a productive child exists. Require bounded nonzero exit, preserved runtime root, no unhandled Node error, and absence of every process whose identity was published by the test probe.

- [x] **Step 3: Preserve the two-helper Node harness boundary**

Run these existing contracts unchanged:

```cmd
C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_scan_profile_pool_js.py -q --tb=short -k "fixed_timeout or completion_markers"
```

Expected: PASS. Do not migrate any other historical Node harness.

- [x] **Step 4: Run focused Node and browser neighbors**

```cmd
set "PYTHONUTF8=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_option_explanations.py tests/test_workbench_scan_profile_pool_js.py tests/test_workbench_gate0_catalog_state.py tests/test_workbench_dogfood_frontend_contracts.py tests/test_workbench_review_regressions.py tests/test_workbench_render_js.py -q --tb=short
call npm --prefix tests/browser test -- --grep "Scanprofil-Pool|Registry-Quellen|catalog failure|catalog responses reorder"
```

Expected: all pass; the self-isolated runner leaves no owned process, listener, runtime root, or occupied port.

## Task 5: Remove Experimental Cleanup And Review

**Files:**
- Delete: `tests/browser/process_tree_cleanup.py`
- Verify: complete Remediation F scope

- [x] **Step 1: Prove the old helper has no consumers**

Search for `process_tree_cleanup.py`, `runTokenCleanupHelper`, direct productive PID/PGID fallback, and `taskkill` in `run-isolated-tests.js`. Expected: no executable old-helper consumer remains; references to the deleted path are historical plan records only; Node has no productive PID cleanup path.

- [x] **Step 2: Delete the obsolete helper**

Delete `tests/browser/process_tree_cleanup.py` only after Task 4 is green.

- [x] **Step 3: Run compile and syntax checks**

```cmd
C:\morphic_v1\.venv\Scripts\python.exe -m py_compile tests/browser/process_tree_supervisor.py tests/test_browser_process_tree_supervisor.py tests/test_workbench_option_explanations.py tests/test_workbench_scan_profile_pool_js.py
node --check tests/browser/run-isolated-tests.js
node --check tests/browser/workbench.spec.js
git diff --check -- tests/browser/run-isolated-tests.js tests/browser/process_tree_supervisor.py tests/browser/process_tree_cleanup.py tests/test_browser_process_tree_supervisor.py tests/test_workbench_option_explanations.py tests/test_workbench_scan_profile_pool_js.py
```

Expected: PASS; cached index empty.

- [x] **Step 4: Run independent Spec review**

Review against `docs/superpowers/specs/2026-07-28-gate3-browser-process-supervisor-design.md`. Fix every P0-P2 with a new RED/GREEN cycle until APPROVE.

- [x] **Step 5: Run independent Quality/Security review**

Review containment authority, Job Object lifetime, POSIX identity lifetime, control protocol, deadlines, listener cleanup, runtime preservation, PID/create-time handling, token leakage, and test realism. Fix every P0-P2 and re-review until APPROVE.

- [x] **Step 6: Run final focused verification**

Run Tasks 1-4 matrices on the final reviewed bytes. Then verify with `psutil` that no `process_tree_supervisor.py`, `isolated_server.py`, Playwright runner, or test-owned browser descendant remains; no owned temporary runtime remains except an intentionally preserved test fixture; port 8766 is free; accepted live ports remain untouched; and `git diff --cached --name-only` is empty.

## Verification Summary

- Independent Spec and Quality/Security review cycles completed with no open
  P0-P2 finding after the final documentation correction.
- Static checks passed; the cached index remained empty.
- Final focused results on identical bytes: supervisor `94 passed, 3 skipped`;
  option/runner contracts `62 passed`; two-helper boundary `2 passed, 36
  deselected`; Gate-3 Node neighbors `166 passed`; self-isolated browser grep `6
  passed`.
- Final inventory: zero owned supervisor/server/Playwright processes, no readable
  token-environment leak, port 8766 free, accepted ports 8090/8765 unchanged,
  and unrelated temporary roots preserved.

## Completion Boundary

Remediation F achieved its focused completion boundary: the supervisor is the
sole productive process-tree authority, no Node PID/PGID fallback remains, both
review cycles have no open P0-P2 finding, focused Python/Node/browser matrices
passed on identical bytes, and no test-owned process, port, listener, or new
temporary runtime remains. Parent Gate 3 remains open until the subsequent full
Python and complete browser matrices pass.
