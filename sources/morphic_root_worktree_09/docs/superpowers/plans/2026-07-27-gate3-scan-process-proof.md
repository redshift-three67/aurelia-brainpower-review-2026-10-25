# Gate 3 Scan Process Proof Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bind a Workbench-confirmed scan-profile fingerprint to the real process-gated CLI child with a private, one-shot nonce/digest proof while preserving direct CLI compatibility.

**Architecture:** `scan_process_gate.py` creates a random nonce after release and binds it to the private fingerprint with a shared versioned SHA-256 helper. The CLI atomically removes and validates the proof triplet before pool resolution or any scan side effect. The process-tree token remains a separate persisted recovery authority and no longer participates in fingerprint validation.

**Tech Stack:** Python 3.11+, Typer, FastAPI in-process test client, `subprocess`, `psutil`, pytest, Windows/POSIX process gate.

**Constraint:** Do not commit or stage in this cumulative worktree. The normal commit steps are intentionally replaced by diff/index checks.

---

## File Map

- Modify `core/profile_sync/__init__.py`: shared private proof environment names and deterministic proof builder.
- Modify `services/scan_process_gate.py`: generate and inject the one-shot proof only after release.
- Modify `apps/cli/commands/scan.py`: remove the rejected group-token heuristic and validate the proof triplet before all side effects.
- Modify `tests/test_profile_sync_authority.py`: proof-builder unit contract.
- Modify `tests/test_web_durable_io.py`: gate generation, child environment, and no-spawn failure contract.
- Modify `tests/test_topn_cli_phase1_options.py`: CLI proof state matrix and direct compatibility.
- Modify `tests/test_scan_profile_fingerprint_process_integration.py`: real Web-to-gate-to-CLI proof, exact negative causes, hard timeout, cleanup, and leak checks.

### Task 1: Shared One-Shot Proof Contract

**Files:**
- Modify: `core/profile_sync/__init__.py:18-38`
- Test: `tests/test_profile_sync_authority.py`

- [ ] **Step 1: Write failing proof-builder tests**

Add tests that import the not-yet-defined constants and helper:

```python
from core.profile_sync import (
    SCAN_PROCESS_GATE_NONCE_ENV,
    SCAN_PROCESS_GATE_PROOF_ENV,
    build_scan_process_gate_proof,
)


def test_scan_process_gate_proof_is_stable_and_domain_bound() -> None:
    nonce = "a" * 64
    fingerprint = "b" * 64

    proof = build_scan_process_gate_proof(nonce, fingerprint)

    assert re.fullmatch(r"[0-9a-f]{64}", proof)
    assert proof == build_scan_process_gate_proof(nonce, fingerprint)
    assert proof != build_scan_process_gate_proof("c" * 64, fingerprint)
    assert proof != build_scan_process_gate_proof(nonce, "d" * 64)
    assert SCAN_PROCESS_GATE_NONCE_ENV == "MORPHIC_SCAN_PROCESS_GATE_NONCE"
    assert SCAN_PROCESS_GATE_PROOF_ENV == "MORPHIC_SCAN_PROCESS_GATE_PROOF"


@pytest.mark.parametrize("nonce", ["", "a" * 63, "A" * 64, "g" * 64, None])
def test_scan_process_gate_proof_rejects_invalid_nonce(nonce: object) -> None:
    with pytest.raises(ProfileAuthorityError, match="process proof"):
        build_scan_process_gate_proof(nonce, "b" * 64)
```

- [ ] **Step 2: Run RED**

Run:

```cmd
set "PYTHONUTF8=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_profile_sync_authority.py -q --tb=short
```

Expected: collection/import failure because the proof constants and builder do not exist.

- [ ] **Step 3: Implement the minimal shared builder**

Add next to `SCAN_PROFILE_POOL_FINGERPRINT_ENV`:

```python
SCAN_PROCESS_GATE_NONCE_ENV = "MORPHIC_SCAN_PROCESS_GATE_NONCE"
SCAN_PROCESS_GATE_PROOF_ENV = "MORPHIC_SCAN_PROCESS_GATE_PROOF"
_SCAN_PROCESS_GATE_PROOF_DOMAIN = b"morphic-scan-process-gate-v1\0"
_SHA256_HEX_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def build_scan_process_gate_proof(nonce: object, fingerprint: object) -> str:
    """Bind one gate-generated nonce to the private fingerprint value."""
    if type(nonce) is not str or _SHA256_HEX_PATTERN.fullmatch(nonce) is None:
        raise ProfileAuthorityError("Scan process proof is invalid.")
    if type(fingerprint) is not str or len(fingerprint) > 128:
        raise ProfileAuthorityError("Scan process proof is invalid.")
    payload = (
        _SCAN_PROCESS_GATE_PROOF_DOMAIN
        + nonce.encode("ascii")
        + b"\0"
        + fingerprint.encode("utf-8")
    )
    return hashlib.sha256(payload).hexdigest()
```

The helper deliberately permits an empty or syntactically malformed fingerprint so the real gate can still mark the child as gate-bound; the CLI owns fingerprint syntax and authority validation.

- [ ] **Step 4: Run GREEN and authority regression**

```cmd
set "PYTHONUTF8=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_profile_sync_authority.py tests/test_procedural_groups_readiness.py -q --tb=short
```

Expected: PASS.

- [ ] **Step 5: Check scope without staging**

```cmd
git diff --check -- core/profile_sync/__init__.py tests/test_profile_sync_authority.py
```

Expected: no whitespace errors; cached output empty.

### Task 2: Gate-Generated Proof Injection

**Files:**
- Modify: `services/scan_process_gate.py:193-212`
- Test: `tests/test_web_durable_io.py:1190-1275`

- [ ] **Step 1: Write the child-environment RED test**

Extend the existing mocked `supervise()` test to set a private fingerprint in the gate environment and capture `subprocess.Popen(..., env=...)`:

```python
def test_scan_process_gate_generates_private_fingerprint_proof_after_release(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fingerprint = "b" * 64
    release = tmp_path / "job.release"
    release.write_bytes(b"released\n")
    captured: dict[str, object] = {}
    monkeypatch.setenv(SCAN_PROFILE_POOL_FINGERPRINT_ENV, fingerprint)
    monkeypatch.setattr(scan_process_gate.secrets, "token_hex", lambda size: "a" * 64)
    monkeypatch.setattr(scan_process_gate.subprocess, "Popen", capture_completed_child(captured))

    result = scan_process_gate.supervise(
        release, tmp_path / "started", 1.0, "tree-token", ["productive"]
    )

    environment = captured["env"]
    assert result == 0
    assert environment[SCAN_PROFILE_POOL_FINGERPRINT_ENV] == fingerprint
    assert environment[SCAN_PROCESS_GATE_NONCE_ENV] == "a" * 64
    assert environment[SCAN_PROCESS_GATE_PROOF_ENV] == build_scan_process_gate_proof(
        "a" * 64, fingerprint
    )
    assert environment["MORPHIC_SCAN_GROUP_TOKEN"] == "tree-token"
```

Also assert that no `Popen` call occurs before `release_path` exists and that inherited nonce/proof values are overwritten rather than forwarded.

- [ ] **Step 2: Run RED**

```cmd
set "PYTHONUTF8=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_web_durable_io.py -q --tb=short -k "scan_process_gate"
```

Expected: proof keys are absent from the captured child environment.

- [ ] **Step 3: Generate the proof immediately before child spawn**

Import `secrets` and the shared proof contract. After the release wait and before `Popen`, build a fresh child environment:

```python
fingerprint = os.environ.get(SCAN_PROFILE_POOL_FINGERPRINT_ENV, "")
nonce = secrets.token_hex(32)
proof = build_scan_process_gate_proof(nonce, fingerprint)
child_environment = dict(os.environ)
child_environment["MORPHIC_SCAN_GROUP_TOKEN"] = token
child_environment[SCAN_PROCESS_GATE_NONCE_ENV] = nonce
child_environment[SCAN_PROCESS_GATE_PROOF_ENV] = proof
child = subprocess.Popen(command, shell=False, env=child_environment)
```

Do not add nonce or proof to arguments, result files, process-tree state, or logs.

- [ ] **Step 4: Add and pass the generation-failure test**

Patch `secrets.token_hex` or the proof builder to raise and assert that `Popen` is never called. Run:

```cmd
set "PYTHONUTF8=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_web_durable_io.py -q --tb=short -k "scan_process_gate"
```

Expected: PASS with no productive child on proof-generation failure.

- [ ] **Step 5: Syntax and scope checks**

```cmd
C:\morphic_v1\.venv\Scripts\python.exe -m py_compile services/scan_process_gate.py tests/test_web_durable_io.py
```

Expected: PASS; cached output empty.

### Task 3: CLI Proof Validation And Direct Compatibility

**Files:**
- Modify: `apps/cli/commands/scan.py:1-33,1310-1358`
- Test: `tests/test_topn_cli_phase1_options.py`

- [ ] **Step 1: Write the proof-state matrix before changing production code**

Use `CliRunner` and existing lightweight scan fakes. Parameterize:

```python
@pytest.mark.parametrize(
    ("nonce", "proof", "fingerprint", "should_reach_pool"),
    [
        (None, None, None, True),
        ("a" * 64, None, "b" * 64, False),
        (None, "c" * 64, "b" * 64, False),
        ("short", "c" * 64, "b" * 64, False),
        ("a" * 64, "short", "b" * 64, False),
        ("a" * 64, "c" * 64, None, False),
        ("a" * 64, "c" * 64, "b" * 64, False),
    ],
)
def test_top3_scan_process_proof_fails_before_pool_and_activation(...):
    ...
```

For the valid case, calculate `proof = build_scan_process_gate_proof(nonce, fingerprint)` and assert pool resolution is reached. For every invalid/partial case assert:

- exit code `1`;
- exact generic profile-authority message;
- no traceback, nonce, digest, fingerprint, or private environment name;
- pool loader, `resolve_operator_context`, export creation, and `subprocess.run` were not called;
- all three private keys are absent from `os.environ` in the first patched failure probe.

- [ ] **Step 2: Add the rejected-heuristic compatibility RED**

Set only `MORPHIC_SCAN_GROUP_TOKEN` and no proof/fingerprint. Reuse the direct-CLI healthy fake and assert the pool loader is reached. This must fail against the current line that treats group-token presence as gate binding.

- [ ] **Step 3: Run RED**

```cmd
set "PYTHONUTF8=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_topn_cli_phase1_options.py -q --tb=short -k "process_proof or group_token"
```

Expected: invalid proof states are accepted or fail too late, and group-token-only direct mode is rejected.

- [ ] **Step 4: Replace the group-token heuristic with proof validation**

Import `re`, the two proof environment constants, and
`build_scan_process_gate_proof`. At the first lines of `top3_scan`, pop all
three values:

```python
expected_fingerprint = os.environ.pop(SCAN_PROFILE_POOL_FINGERPRINT_ENV, None)
gate_nonce = os.environ.pop(SCAN_PROCESS_GATE_NONCE_ENV, None)
gate_proof = os.environ.pop(SCAN_PROCESS_GATE_PROOF_ENV, None)
gate_bound = gate_nonce is not None or gate_proof is not None
if gate_bound:
    valid_shape = (
        isinstance(gate_nonce, str)
        and re.fullmatch(r"[0-9a-f]{64}", gate_nonce) is not None
        and isinstance(gate_proof, str)
        and re.fullmatch(r"[0-9a-f]{64}", gate_proof) is not None
        and isinstance(expected_fingerprint, str)
        and re.fullmatch(r"[0-9a-f]{64}", expected_fingerprint) is not None
    )
    if not valid_shape:
        _fail_top3_scan("Scanprofil-Pool stimmt nicht mit der bestätigten Autorität überein.")
    expected_proof = build_scan_process_gate_proof(gate_nonce, expected_fingerprint)
    if not hmac.compare_digest(gate_proof, expected_proof):
        _fail_top3_scan("Scanprofil-Pool stimmt nicht mit der bestätigten Autorität überein.")
```

Delete the `MORPHIC_SCAN_GROUP_TOKEN` condition. Keep the existing later Core-pool fingerprint comparison so both direct fingerprint input and gate-bound input use the same authority.

- [ ] **Step 5: Run GREEN and CLI regression**

```cmd
set "PYTHONUTF8=1" && set "PYTHONIOENCODING=utf-8" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_topn_cli_phase1_options.py tests/test_topn_structured_records.py tests/test_topn_session_scope.py -q --tb=short
```

Expected: PASS.

- [ ] **Step 6: Compile and check scope**

```cmd
C:\morphic_v1\.venv\Scripts\python.exe -m py_compile apps/cli/commands/scan.py tests/test_topn_cli_phase1_options.py
```

Expected: PASS; cached output empty.

### Task 4: Real Process Integration, Hard Timeout, And Leak Proof

**Files:**
- Modify: `tests/test_scan_profile_fingerprint_process_integration.py`
- Verify: `apps/web/main.py`
- Verify: `apps/web/scan_jobs.py`
- Verify: `services/scan_process_gate.py`
- Verify: `apps/cli/commands/scan.py`

- [ ] **Step 1: Replace the non-cancellable executor boundary**

Replace `ThreadPoolExecutor` with a daemon `threading.Thread` and `queue.Queue`. Always set `release_allowed` in `finally`, stop any known job authority, and join for a second finite deadline. Fail while the daemon remains isolated instead of invoking an executor context manager that waits forever:

```python
responses: queue.Queue[object] = queue.Queue(maxsize=1)

def start_request() -> None:
    try:
        responses.put(request(app, "POST", "/api/scan/jobs", payload))
    except BaseException as exc:
        responses.put(exc)

worker = threading.Thread(target=start_request, daemon=True)
worker.start()
...
release_allowed.set()
worker.join(timeout=20)
assert not worker.is_alive(), "scan start request exceeded its hard deadline"
started = responses.get_nowait()
if isinstance(started, BaseException):
    raise started
```

- [ ] **Step 2: Extend the child probe before production changes**

The `sitecustomize` probe records at process entry that fingerprint, nonce, and digest were present. Register an `atexit` probe that records all three are absent after `top3_scan` has popped them. At activation and first subscan, assert the triplet is absent from parent env, child env, and argv.

- [ ] **Step 3: Run the positive integration RED**

```cmd
set "PYTHONUTF8=1" && set "PYTHONIOENCODING=utf-8" && set "OPENBLAS_NUM_THREADS=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_scan_profile_fingerprint_process_integration.py::test_web_start_binds_private_fingerprint_through_real_gate_to_cli -q -s --tb=short
```

Expected before Tasks 1-3 GREEN: proof markers are absent or are not popped. Expected after Tasks 1-3: PASS.

- [ ] **Step 4: Make negative failures causally exact**

For missing fingerprint, mismatched fingerprint, malformed nonce, malformed digest, partial proof, and tampered digest assert:

```python
assert terminal["status"] == "failed"
assert terminal["returncode"] not in {None, 0}
assert "Scanprofil-Pool stimmt nicht mit der bestätigten Autorität überein." in terminal["stderr_tail"]
assert "Traceback" not in terminal["stderr_tail"]
assert not activation_marker.exists()
assert not subscan_marker.exists()
assert not export_root.exists()
assert json.loads(exit_marker.read_text(encoding="ascii")) == {
    "fingerprint_absent": True,
    "nonce_absent": True,
    "proof_absent": True,
}
```

Use the real gate for missing/mismatched fingerprint. Use a direct real CLI child with an explicitly constructed proof triplet for malformed/partial/tampered states, because the production gate always generates a valid nonce and digest.

- [ ] **Step 5: Prove public and persisted non-disclosure**

Check all of these surfaces for the fingerprint, nonce, digest, and all three environment variable names:

- start HTTP response;
- owned status response;
- sync-trace response;
- in-memory public job snapshot;
- persisted job JSON;
- start-operation JSON;
- run trace;
- stdout/stderr;
- release, started, result, state, log, and probe files under the isolated runtime root.

Exclude the private probe payload itself only where it intentionally records boolean presence; it must never record the values.

- [ ] **Step 6: Run the complete focused matrix**

```cmd
set "PYTHONUTF8=1" && set "PYTHONIOENCODING=utf-8" && set "OPENBLAS_NUM_THREADS=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_scan_profile_fingerprint_process_integration.py tests/test_scan_job_private_environment.py tests/test_profile_sync_authority.py tests/test_procedural_groups_readiness.py tests/test_web_durable_io.py tests/test_web_scan_jobs.py tests/test_web_scan_job_ownership.py tests/test_topn_cli_phase1_options.py tests/test_topn_structured_records.py tests/test_topn_session_scope.py -q --tb=short
```

Expected: PASS; only established platform skips are allowed.

- [ ] **Step 7: Compile, leak, process, and diff checks**

```cmd
C:\morphic_v1\.venv\Scripts\python.exe -m py_compile core/profile_sync/__init__.py services/scan_process_gate.py apps/cli/commands/scan.py tests/test_scan_profile_fingerprint_process_integration.py
git diff --check -- core/profile_sync/__init__.py services/scan_process_gate.py apps/cli/commands/scan.py tests/test_profile_sync_authority.py tests/test_web_durable_io.py tests/test_topn_cli_phase1_options.py tests/test_scan_profile_fingerprint_process_integration.py
```

Verify no test-owned `scan_process_gate.py` or CLI descendant remains and no isolated runtime directory remains locked. Expected: compile and diff PASS; cached output empty; no process or private-value leak.

- [ ] **Step 8: Independent reviews**

Run a spec-compliance review against `docs/superpowers/specs/2026-07-27-gate3-scan-process-proof-design.md`. After APPROVE, run a separate code-quality/security review. Fix every P0-P2 via a new RED/GREEN cycle and re-review until both are clean.

Do not mark Gate 3 complete until Remediation F and the final full Python/browser matrices also pass.
