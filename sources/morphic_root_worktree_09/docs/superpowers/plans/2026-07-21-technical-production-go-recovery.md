# Technical Production GO Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the remaining Gate-0 durability and idempotency findings, verify the exact current worktree, and deliver a reviewed live technical production GO on port 8765.

**Architecture:** `StartOperationStore` remains the cross-process request authority, while `LocalScanJobService` gains late durable adoption for services that were created before another process persisted a job. Start failures expose an explicit server disposition so the browser only replaces operation authority after the server proves that no job was committed. The existing worktree is preserved and frozen by exact hashes instead of being reset, broadly staged, or implicitly committed.

**Tech Stack:** Python 3.11, FastAPI, Pydantic, pytest, durable JSON state, Windows/POSIX file locks, vanilla JavaScript, Node.js, Playwright, PowerShell 7.

---

## File Map

- Modify `apps/web/scan_jobs.py`: late durable job adoption and per-job start serialization.
- Modify `apps/web/main.py`: explicit `safe-to-replace` disposition for failures proven to occur before job creation.
- Modify `apps/web/static/workbench-api.js`: propagate the response disposition onto API errors.
- Modify `apps/web/static/app.js`: retain operation authority unless the server explicitly marks it safe to replace.
- Modify `tests/test_web_scan_jobs.py`: pre-existing service adoption and duplicate-spawn prevention.
- Modify `tests/test_web_shell.py`: true job-created/claim-pending recovery, harmonization parity, corruption, and safe-replacement response contracts.
- Modify `tests/test_workbench_dogfood_frontend_contracts.py`: executable JavaScript contracts for error disposition and key retention.
- Modify `tests/browser/workbench.spec.js`: response-loss and ambiguous-422 operation-key behavior.
- Verify `apps/web/start_operations.py`: required key, owner/request binding, process lock, immutable completion.
- Verify `apps/web/durable_io.py`: atomic publication and durability boundary.
- Create `docs/reviews/2026-07-21-technical-production-go-freeze-v4.sha256`: exact scope manifest.
- Create `docs/reviews/2026-07-21-technical-production-go-freeze-v4.md`: verification and review contract.
- Create `docs/status/2026-07-21-technical-production-go.md`: final runtime evidence and recovery point.
- Modify `PROJECT_MEMORY/00_CURRENT_STATE.md`: authoritative GO status after live acceptance.

No Git commit is authorized by this plan. Replace commit checkpoints with focused status/diff checks and immutable hash freezes.

### Task 1: Prove Late Scan-Job Adoption Fails Before Implementation

**Files:**
- Modify: `tests/test_web_scan_jobs.py`
- Test: `tests/test_web_scan_jobs.py`

- [ ] **Step 1: Add the late-adoption regression test**

Append this test near the existing restart and parallel-service tests:

```python
def test_service_created_before_job_adopts_later_persisted_job(tmp_path: Path) -> None:
    root = tmp_path / "jobs"
    observer = LocalScanJobService(root, cwd=tmp_path)
    writer = LocalScanJobService(root, cwd=tmp_path)
    command = [sys.executable, "-c", "import time; time.sleep(30)"]
    started = writer.start(
        command,
        owner_id="owner-late-adoption",
        job_id="scan-op-late-adoption-1234",
    )
    job_id = str(started["job_id"])

    try:
        adopted = observer.get(job_id)
        assert adopted["job_id"] == job_id
        assert adopted["owner_id"] == "owner-late-adoption"
        assert adopted["command"] == command
    finally:
        LocalScanJobService(root, cwd=tmp_path).stop(job_id)
```

- [ ] **Step 2: Run the test and confirm RED**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_web_scan_jobs.py::test_service_created_before_job_adopts_later_persisted_job -q
```

Expected: FAIL with `KeyError` from `LocalScanJobService.get()` because `observer._jobs` was populated before the writer persisted the job.

- [ ] **Step 3: Add the duplicate-spawn prevention test**

Append:

```python
def test_existing_deterministic_job_is_replayed_without_second_spawn(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    observer = LocalScanJobService(root, cwd=tmp_path)
    writer = LocalScanJobService(root, cwd=tmp_path)
    command = [sys.executable, "-c", "import time; time.sleep(30)"]
    job_id = "scan-op-single-spawn-1234"
    started = writer.start(command, owner_id="owner-a", job_id=job_id)

    def duplicate_spawn(*args, **kwargs):
        raise AssertionError("existing deterministic job attempted a second spawn")

    monkeypatch.setattr(scan_jobs.subprocess, "Popen", duplicate_spawn)
    try:
        replayed = observer.start(command, owner_id="owner-a", job_id=job_id)
        assert replayed["job_id"] == started["job_id"]
        assert replayed["owner_id"] == "owner-a"
    finally:
        LocalScanJobService(root, cwd=tmp_path).stop(job_id)
```

- [ ] **Step 4: Run the duplicate-spawn test and confirm RED**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_web_scan_jobs.py::test_existing_deterministic_job_is_replayed_without_second_spawn -q
```

Expected: FAIL with `existing deterministic job attempted a second spawn`.

- [ ] **Step 5: Add the corrupt-state fail-closed test**

Extend the import from `apps.web.scan_jobs` with `ProcessAuthorityAmbiguousError`, then append:

```python
def test_corrupt_persisted_deterministic_job_fails_closed_before_spawn(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "jobs"
    service = LocalScanJobService(root, cwd=tmp_path)
    job_id = "scan-op-corrupt-state-1234"
    service._state_path(job_id).write_text("{not-json", encoding="utf-8")

    def duplicate_spawn(*args, **kwargs):
        raise AssertionError("corrupt durable authority attempted a spawn")

    monkeypatch.setattr(scan_jobs.subprocess, "Popen", duplicate_spawn)
    with pytest.raises(ProcessAuthorityAmbiguousError, match="unreadable"):
        service.start(
            [sys.executable, "-c", "pass"],
            owner_id="owner-a",
            job_id=job_id,
        )
```

- [ ] **Step 6: Run the corrupt-state test and confirm RED**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_web_scan_jobs.py::test_corrupt_persisted_deterministic_job_fails_closed_before_spawn -q
```

Expected: FAIL because the current service silently treats the unreadable state as absent and reaches `duplicate_spawn`.

### Task 2: Implement Late Adoption and Serialized Deterministic Starts

**Files:**
- Modify: `apps/web/scan_jobs.py:1042-1437`
- Test: `tests/test_web_scan_jobs.py`

- [ ] **Step 1: Add a same-process start lock**

In `LocalScanJobService.__init__`, add a separate lock for complete start decisions:

```python
self._jobs: dict[str, _LocalScanJob] = {}
self._lock = threading.Lock()
self._start_lock = threading.Lock()
```

- [ ] **Step 2: Add a cross-process start-decision lock**

Add this method immediately after `_process_lock`:

```python
@contextmanager
def _start_process_lock(self, job_id: str):
    lock_path = self.root / f".{job_id}.start.lock"
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(descriptor, b"0")
        os.fsync(descriptor)
        os.close(descriptor)
    except FileExistsError:
        pass
    with lock_path.open("r+b") as handle:
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
```

- [ ] **Step 3: Make recovery targetable**

Change `_recover_jobs` to accept a job ID and select either one state path or the startup glob:

```python
def _recover_jobs(self, job_id: str | None = None) -> None:
    root = self.root.resolve()
    state_paths = (
        [self._state_path(job_id)]
        if job_id is not None
        else list(self.root.glob("*.state.json"))
    )
    for state_path in state_paths:
        if not state_path.exists():
            continue
        try:
            payload = json.loads(state_path.read_text(encoding="utf-8"))
            recovered_job_id = str(payload["job_id"])
            pid = int(payload["pid"])
            create_time = float(payload["process_create_time"])
            process_group_id = int(payload["process_group_id"])
            process_group_token = payload.get("process_group_token")
            stdout_path = Path(str(payload["stdout_path"])).resolve()
            stderr_path = Path(str(payload["stderr_path"])).resolve()
            if (
                state_path.name != f"{recovered_job_id}.state.json"
                or not stdout_path.is_relative_to(root)
                or not stderr_path.is_relative_to(root)
            ):
                if job_id is not None:
                    raise ProcessAuthorityAmbiguousError(
                        "persisted scan job authority is unreadable"
                    )
                continue
            process = _RecoveredProcess(pid, create_time)
            forced_status = payload.get("forced_status")
            job = _LocalScanJob(
                job_id=recovered_job_id,
                command=[str(value) for value in payload.get("command", [])],
                process=process,
                stdout_path=stdout_path,
                stderr_path=stderr_path,
                created_at=str(payload["created_at"]),
                updated_at=str(payload.get("updated_at", payload["created_at"])),
                stdout_pos=int(payload.get("stdout_pos", 0)),
                stderr_pos=int(payload.get("stderr_pos", 0)),
                progress_percent=payload.get("progress_percent"),
                current_phase=payload.get("current_phase"),
                current_substep=payload.get("current_substep"),
                completed_labels=list(payload.get("completed_labels", [])),
                seen_labels=set(payload.get("completed_labels", [])),
                completed_stage_ids=list(payload.get("completed_stage_ids", [])),
                seen_stage_ids=set(payload.get("completed_stage_ids", [])),
                current_stage_id=payload.get("current_stage_id"),
                stdout_buffer=str(payload.get("stdout_buffer", "")),
                stderr_buffer=str(payload.get("stderr_buffer", "")),
                owner_id=payload.get("owner_id"),
                artifact_paths=list(payload.get("artifact_paths", [])),
                forced_status=forced_status,
                phase2_profiles_started=bool(payload.get("phase2_profiles_started", False)),
                phase2_profiles_complete=bool(payload.get("phase2_profiles_complete", False)),
                process_create_time=create_time,
                process_group_id=process_group_id,
                process_group_token=process_group_token,
                start_released=bool(payload.get("start_released", True)),
                authority_namespace=str(
                    payload.get("authority_namespace", self.authority_namespace)
                ),
            )
            if forced_status is None:
                try:
                    runtime_active = _job_runtime_active(job)
                except Exception:
                    job.forced_status = "authority_ambiguous"
                else:
                    if not runtime_active:
                        job.forced_status = "failed"
            self._jobs[recovered_job_id] = job
            if job.forced_status != forced_status:
                self._persist_job(job)
        except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as exc:
            if job_id is not None:
                raise ProcessAuthorityAmbiguousError(
                    "persisted scan job authority is unreadable"
                ) from exc
            continue
```

- [ ] **Step 4: Adopt durable state on cache miss**

Replace `get` with:

```python
def get(self, job_id: str) -> dict[str, object]:
    with self._lock, self._process_lock(job_id):
        if job_id not in self._jobs:
            self._recover_jobs(job_id)
        job = self._jobs[job_id]
        self._refresh_job(job)
        return self._snapshot(job)
```

- [ ] **Step 5: Serialize and replay deterministic starts before spawning**

Rename the current `start` implementation to `_start_new_job` and preserve its existing body after job-ID validation. Its signature is:

```python
def _start_new_job(
    self,
    command: list[str],
    owner_id: str | None,
    env_overrides: Mapping[str, str] | None,
    job_id: str,
) -> dict[str, object]:
```

Add this public wrapper in its place:

```python
def start(
    self,
    command: list[str],
    owner_id: str | None = None,
    env_overrides: Mapping[str, str] | None = None,
    job_id: str | None = None,
) -> dict[str, object]:
    resolved_job_id = job_id or (
        f"scan-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    )
    if not resolved_job_id.startswith(("scan-", "harm-auth-")) or any(
        character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        for character in resolved_job_id
    ):
        raise ValueError("invalid authority job id")

    with self._start_lock, self._start_process_lock(resolved_job_id):
        try:
            existing = self.get(resolved_job_id)
        except KeyError:
            existing = None
        if existing is not None:
            if list(existing.get("command", [])) != list(command):
                raise ValueError("existing scan job command identity mismatch")
            if existing.get("owner_id") != owner_id:
                raise ValueError("existing scan job owner identity mismatch")
            return existing
        return self._start_new_job(
            command,
            owner_id,
            env_overrides,
            resolved_job_id,
        )
```

Remove duplicate job-ID generation and validation from `_start_new_job`; its first executable lines become:

```python
stdout_path = self.root / f"{job_id}.stdout.log"
stderr_path = self.root / f"{job_id}.stderr.log"
created_at = _utc_now()
exec_command = _execution_command(command)
```

- [ ] **Step 6: Run the focused scan-service tests**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_web_scan_jobs.py::test_service_created_before_job_adopts_later_persisted_job tests/test_web_scan_jobs.py::test_existing_deterministic_job_is_replayed_without_second_spawn tests/test_web_scan_jobs.py::test_corrupt_persisted_deterministic_job_fails_closed_before_spawn tests/test_web_scan_jobs.py::test_scan_restart_recovers_and_stops_real_windows_process_tree tests/test_web_scan_jobs.py::test_parallel_recovered_services_never_regress_persisted_scan_cursor tests/test_web_scan_jobs.py::test_independent_processes_poll_one_recovered_scan_without_state_drift -q
```

Expected: all selected tests PASS; platform-specific tests may report SKIPPED only where their existing marker requires it.

### Task 3: Replace the False Crash Test with a Real Job-Created/Pending-Claim Test

**Files:**
- Modify: `tests/test_web_shell.py:1-15,1532-1599`
- Test: `tests/test_web_shell.py`

- [ ] **Step 1: Import the real scan service and interpreter module**

Add:

```python
import sys

from apps.web.scan_jobs import LocalScanJobService
```

- [ ] **Step 2: Replace the current restart test with a real durable-job test**

Replace `test_pending_scan_operation_reconciles_after_server_restart_without_duplicate` with:

```python
def test_pending_scan_operation_adopts_precreated_durable_job_without_duplicate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = tmp_path / "runtime"
    job_root = runtime / "web_jobs"
    observer = LocalScanJobService(job_root, cwd=tmp_path)
    writer = LocalScanJobService(job_root, cwd=tmp_path)
    app = create_app(runtime_dir=runtime, scan_jobs=observer)
    body = _gate0_scan_start_body()
    key = "scan-crash-recovery-12345678"
    request_model = web_main.Phase1ScanRequest.model_validate(body)
    request_sha256 = hashlib.sha256(
        request_model.model_dump_json().encode("utf-8")
    ).hexdigest()
    context = app.state.operator_context
    owner = f"{context.tenant_id}:{context.operator_id}"
    assert app.state.start_operations.begin(
        kind="scan",
        key=key,
        owner_id=owner,
        request_sha256=request_sha256,
    ) is None
    pending = app.state.start_operations.begin(
        kind="scan",
        key=key,
        owner_id=owner,
        request_sha256=request_sha256,
    )
    assert pending is not None
    job_id = str(pending["job_id"])
    writer.start(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        owner_id=context.operator_id,
        job_id=job_id,
    )
    app.state.start_operations = StartOperationStore(app.state.start_operations.root)

    def duplicate_start(*args, **kwargs):
        raise AssertionError("replay attempted to create a duplicate scan")

    monkeypatch.setattr(observer, "start", duplicate_start)
    try:
        response = request(
            app,
            "POST",
            "/api/scan/jobs",
            body,
            {"Idempotency-Key": key},
        )
        assert response.status_code == 200
        assert response.json()["job_id"] == job_id
        completed = app.state.start_operations.begin(
            kind="scan",
            key=key,
            owner_id=owner,
            request_sha256=request_sha256,
        )
        assert completed is not None
        assert completed["state"] == "completed"
        assert len(list(job_root.glob("*.state.json"))) == 1
    finally:
        LocalScanJobService(job_root, cwd=tmp_path).stop(job_id)
```

- [ ] **Step 3: Run the replacement test**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_web_shell.py::test_pending_scan_operation_adopts_precreated_durable_job_without_duplicate -q
```

Expected: PASS only after Task 2; the injected `duplicate_start` must not execute.

- [ ] **Step 4: Add harmonization pending-claim parity**

Append:

```python
def test_pending_harmonization_operation_adopts_existing_job_without_duplicate(
    tmp_path: Path,
) -> None:
    jobs = FakeHarmonizationJobs()
    app, report_id = app_with_harmonization_report(tmp_path, jobs)
    body = _gate0_harmonization_start_body(report_id)
    key = "harm-crash-recovery-12345678"
    request_model = web_main.HarmonizationRequest.model_validate(body)
    request_sha256 = hashlib.sha256(
        request_model.model_dump_json().encode("utf-8")
    ).hexdigest()
    context = app.state.operator_context
    owner = f"{context.tenant_id}:{context.operator_id}"
    assert app.state.start_operations.begin(
        kind="harmonization",
        key=key,
        owner_id=owner,
        request_sha256=request_sha256,
    ) is None
    pending = app.state.start_operations.begin(
        kind="harmonization",
        key=key,
        owner_id=owner,
        request_sha256=request_sha256,
    )
    assert pending is not None
    jobs.start(
        mode="clearing",
        target_frequency=432.0,
        duration_minutes=21,
        intention="clearing",
        hardware_config={"use_cpu": True},
        report_id=report_id,
        tenant_id=context.tenant_id,
        operator_id=context.operator_id,
        job_id=str(pending["job_id"]),
    )

    response = request(
        app,
        "POST",
        "/api/harmonization/jobs",
        body,
        {"Idempotency-Key": key},
    )

    assert response.status_code == 200
    assert response.json()["job_id"] == pending["job_id"]
    assert len(jobs.started) == 1
```

- [ ] **Step 5: Add corrupt harmonization-record parity**

Append:

```python
def test_corrupt_start_operation_record_fails_closed_without_new_harmonization(
    tmp_path: Path,
) -> None:
    jobs = FakeHarmonizationJobs()
    app, report_id = app_with_harmonization_report(tmp_path, jobs)
    body = _gate0_harmonization_start_body(report_id)
    key = "harm-corrupt-record-12345678"
    headers = {"Idempotency-Key": key}
    first = request(app, "POST", "/api/harmonization/jobs", body, headers)
    assert first.status_code == 200
    context = app.state.operator_context
    path, _, _ = app.state.start_operations._path(
        "harmonization",
        key,
        f"{context.tenant_id}:{context.operator_id}",
    )
    path.write_text("{not-json", encoding="utf-8")

    retry = request(app, "POST", "/api/harmonization/jobs", body, headers)

    assert retry.status_code == 409
    assert "x-morphic-start-operation" not in retry.headers
    assert len(jobs.started) == 1
```

- [ ] **Step 6: Run the complete Gate-0 endpoint group**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_web_shell.py -k "idempotency or replay or pending or corrupt or payload_mismatch" -q
```

Expected: all selected tests PASS.

### Task 4: Make Operation-Key Replacement Explicit and Fail-Closed

**Files:**
- Modify: `apps/web/main.py:678-910`
- Modify: `apps/web/static/workbench-api.js:63-93`
- Modify: `apps/web/static/app.js:95-102`
- Modify: `tests/test_web_shell.py`
- Modify: `tests/test_workbench_dogfood_frontend_contracts.py`

- [ ] **Step 1: Add failing server-disposition tests**

Append these tests:

```python
def test_scan_precreation_failure_marks_operation_safe_to_replace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jobs = FakeScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)

    def reject_activation(*args, **kwargs):
        raise LookupError("synthetic activation rejection")

    monkeypatch.setattr(web_main, "prepare_group_scan_activation", reject_activation)
    response = request(app, "POST", "/api/scan/jobs", _gate0_scan_start_body())

    assert response.status_code == 422
    assert response.headers["x-morphic-start-operation"] == "safe-to-replace"
    assert jobs.started == []


def test_harmonization_missing_report_marks_operation_safe_to_replace(
    tmp_path: Path,
) -> None:
    jobs = FakeHarmonizationJobs()
    report_root = tmp_path / "empty-reports"
    report_root.mkdir()
    app = create_app(
        runtime_dir=tmp_path / "runtime",
        report_roots=[report_root],
        harmonization_jobs=jobs,
    )
    response = request(
        app,
        "POST",
        "/api/harmonization/jobs",
        _gate0_harmonization_start_body("missing-report"),
    )

    assert response.status_code == 404
    assert response.headers["x-morphic-start-operation"] == "safe-to-replace"
    assert jobs.started == []
```

Add `assert "x-morphic-start-operation" not in mismatch.headers` to the payload-mismatch test and the equivalent assertion to both corrupt-record tests.

- [ ] **Step 2: Add executable JavaScript disposition tests**

Add this Python test using the existing `_run_node` helper:

```python
def test_api_error_exposes_start_operation_disposition() -> None:
    script = f"""
const fs=require('fs'); const vm=require('vm');
global.window={{MorphicWorkbenchState:{{pendingMutations:0}}}};
global.document={{querySelector(){{return null;}}}};
global.fetch=async()=>({{
  ok:false,
  status:422,
  headers:{{get(name){{return name.toLowerCase()==='x-morphic-start-operation' ? 'safe-to-replace' : null;}}}},
  async json(){{return {{detail:'rejected before creation'}};}}
}});
vm.runInThisContext(fs.readFileSync({str(API_JS)!r},'utf8'));
(async()=>{{
  try {{ await window.MorphicWorkbenchApi.startScanJob({{}}, 'scan-operation-1234'); }}
  catch (error) {{
    if (error.startOperationDisposition !== 'safe-to-replace') throw error;
    return;
  }}
  throw new Error('request unexpectedly resolved');
}})().catch(error=>{{console.error(error);process.exit(1);}});
"""
    result = _run_node(script)
    assert result.returncode == 0, result.stderr
```

Add this second Python test:

```python
def test_start_operation_retention_requires_explicit_safe_disposition() -> None:
    script = f"""
const fs=require('fs'); const vm=require('vm');
global.window={{MorphicWorkbenchState:{{}},addEventListener(){{}}}};
global.document={{querySelector(){{return null;}},querySelectorAll(){{return[];}}}};
vm.runInThisContext(fs.readFileSync({str(APP_JS)!r},'utf8'));
if (!shouldRetainStartOperation({{status:422,payload:{{detail:'validation'}}}})) {{
  throw new Error('ambiguous 422 discarded operation authority');
}}
if (shouldRetainStartOperation({{status:404,startOperationDisposition:'safe-to-replace'}})) {{
  throw new Error('proven pre-creation failure retained stale authority');
}}
"""
    result = _run_node(script)
    assert result.returncode == 0, result.stderr
```

- [ ] **Step 3: Run the disposition tests and confirm RED**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_web_shell.py tests/test_workbench_dogfood_frontend_contracts.py -k "operation or disposition or corrupt or mismatch" -q
```

Expected: FAIL because the response header and JavaScript error property do not yet exist.

- [ ] **Step 4: Add a server helper for proven pre-creation failures**

Inside `create_app`, near `_start_operation`, add:

```python
def _fail_start_before_creation(
    claim: Any,
    *,
    status_code: int,
    detail: str,
    cause: BaseException | None = None,
) -> None:
    claim.fail_before_creation()
    error = HTTPException(
        status_code=status_code,
        detail=detail,
        headers={"X-Morphic-Start-Operation": "safe-to-replace"},
    )
    if cause is not None:
        raise error from cause
    raise error
```

Use the same header on the existing `claim.state == "failed"` responses. Replace every branch that currently calls `claim.fail_before_creation()` and immediately raises HTTP 403, 404, 409, or 422 with `_fail_start_before_creation(...)`. Do not add the header to identity mismatch, corrupt record, lost job authority, persistence errors, timeouts, or 5xx responses.

Use these exact replacements:

```python
if claim.state == "failed":
    raise HTTPException(
        status_code=409,
        detail="harmonization start operation failed before job creation",
        headers={"X-Morphic-Start-Operation": "safe-to-replace"},
    )
```

```python
except (KeyError, FileNotFoundError) as exc:
    _fail_start_before_creation(
        claim,
        status_code=404,
        detail="report not found",
        cause=exc,
    )
```

```python
except RuntimeError as exc:
    if "active harmonization job" not in str(exc):
        raise
    _fail_start_before_creation(
        claim,
        status_code=409,
        detail="active harmonization job already exists",
        cause=exc,
    )
```

```python
if claim.state == "failed":
    raise HTTPException(
        status_code=409,
        detail="scan start operation failed before job creation",
        headers={"X-Morphic-Start-Operation": "safe-to-replace"},
    )
```

```python
except OwnershipError as exc:
    _fail_start_before_creation(
        claim,
        status_code=403,
        detail="resource access forbidden",
        cause=exc,
    )
except FileNotFoundError as exc:
    _fail_start_before_creation(
        claim,
        status_code=404,
        detail="group draft not found",
        cause=exc,
    )
except LookupError as exc:
    _fail_start_before_creation(
        claim,
        status_code=422,
        detail="group activation is unavailable",
        cause=exc,
    )
except ValueError as exc:
    _fail_start_before_creation(
        claim,
        status_code=422,
        detail=str(exc),
        cause=exc,
    )
```

Change the non-conflict `StartOperationError` mapping in `_start_operation` to:

```python
except StartOperationError as exc:
    raise HTTPException(
        status_code=422,
        detail=str(exc),
        headers={"X-Morphic-Start-Operation": "safe-to-replace"},
    ) from exc
```

- [ ] **Step 5: Propagate the response disposition through `requestJson`**

Immediately before throwing an HTTP error in `workbench-api.js`, add:

```javascript
error.startOperationDisposition = response.headers?.get?.(
  "x-morphic-start-operation"
) || null;
```

- [ ] **Step 6: Replace the browser retention heuristic**

Replace `shouldRetainStartOperation` with:

```javascript
function shouldRetainStartOperation(error) {
  if (!error?.status) return true;
  return error.startOperationDisposition !== "safe-to-replace";
}
```

- [ ] **Step 7: Run server and JavaScript contract tests**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_web_shell.py tests/test_workbench_dogfood_frontend_contracts.py tests/test_workbench_error_ui_js.py -q
```

Expected: all tests PASS.

### Task 5: Prove Browser Response-Loss and Ambiguous-422 Behavior

**Files:**
- Modify: `tests/browser/workbench.spec.js`
- Test: `tests/browser/workbench.spec.js`

- [ ] **Step 1: Add an ambiguous 422 retention test**

Append:

```javascript
test('ambiguous scan 422 retains the same operation authority', async ({ page }) => {
  const operationKeys = [];
  await page.route('**/api/scan/jobs', async route => {
    if (route.request().method() !== 'POST') return route.continue();
    operationKeys.push(route.request().headers()['idempotency-key']);
    await route.fulfill({
      status: 422,
      contentType: 'application/json',
      body: JSON.stringify({detail: 'ambiguous validation response'}),
    });
  });
  const fill = async () => page.evaluate(() => {
    const values = {
      last_name: 'Ambiguous', first_name: 'Synthetic', birth_date: '09041966',
      birth_place: 'Augsburg', focus: 'QA Fokus', main_symptom: 'QA Kontext',
    };
    Object.entries(values).forEach(([name, value]) => {
      document.querySelector(`[name="${name}"]`).value = value;
    });
    document.querySelector('#consent-local').checked = true;
    document.querySelector('#consent-safety').checked = true;
  });
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  await fill();
  expect(await page.evaluate(() => startScanJob())).toBe(false);
  const originalKey = await page.evaluate(
    () => localStorage.getItem('morphic_scan_start_operation_id'),
  );
  expect(originalKey).toBeTruthy();
  await page.reload();
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  await fill();
  expect(await page.evaluate(() => startScanJob())).toBe(false);
  expect(operationKeys).toHaveLength(2);
  expect(operationKeys[1]).toBe(operationKeys[0]);
});
```

- [ ] **Step 2: Add a safe-to-replace test**

Append:

```javascript
test('proven precreation failure clears scan operation authority', async ({ page }) => {
  await page.route('**/api/scan/jobs', async route => {
    if (route.request().method() !== 'POST') return route.continue();
    await route.fulfill({
      status: 404,
      headers: {'X-Morphic-Start-Operation': 'safe-to-replace'},
      contentType: 'application/json',
      body: JSON.stringify({detail: 'report not found'}),
    });
  });
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  await page.evaluate(() => {
    const values = {
      last_name: 'Replace', first_name: 'Synthetic', birth_date: '09041966',
      birth_place: 'Augsburg', focus: 'QA Fokus', main_symptom: 'QA Kontext',
    };
    Object.entries(values).forEach(([name, value]) => {
      document.querySelector(`[name="${name}"]`).value = value;
    });
    document.querySelector('#consent-local').checked = true;
    document.querySelector('#consent-safety').checked = true;
  });
  expect(await page.evaluate(() => startScanJob())).toBe(false);
  expect(await page.evaluate(
    () => localStorage.getItem('morphic_scan_start_operation_id'),
  )).toBeNull();
});
```

- [ ] **Step 3: Preserve the real response-loss test**

Keep `scan start reconciles a lost response with the same idempotency key` using `route.fetch()` followed by `route.abort('failed')`. Do not replace it with a mocked success because it is the commit-before-response-loss proof.

- [ ] **Step 4: Run JavaScript syntax checks**

Run each command:

```powershell
node --check apps/web/static/app.js
node --check apps/web/static/workbench-api.js
node --check tests/browser/workbench.spec.js
```

Expected: each command exits 0 with no syntax error.

### Task 6: Run the Complete Verification Ladder

**Files:**
- Verify: all production and test files in the technical GO scope

- [ ] **Step 1: Run Python compile checks**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m py_compile apps/web/durable_io.py apps/web/start_operations.py apps/web/scan_jobs.py apps/web/main.py
```

Expected: exit 0 with no output.

- [ ] **Step 2: Run the focused Gate-0 matrix**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_start_operations.py tests/test_web_durable_io.py tests/test_web_scan_jobs.py tests/test_web_shell.py tests/test_workbench_dogfood_frontend_contracts.py tests/test_workbench_error_ui_js.py -q
```

Expected: zero failures and zero errors.

- [ ] **Step 3: Run the complete Python suite**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests -q
```

Expected: zero failures and zero errors. Record exact passed/skipped counts and duration in the freeze document.

- [ ] **Step 4: Check patch hygiene**

Run:

```powershell
git diff --check
```

Expected: exit 0. Known LF/CRLF conversion warnings are informational; whitespace errors are not accepted.

- [ ] **Step 5: Install the locked browser-test dependency**

Run in `tests/browser`:

```powershell
npm ci
```

Expected: exit 0 using `package-lock.json` and `@playwright/test` 1.61.1.

- [ ] **Step 6: Start an isolated QA server on port 8766**

Start `C:\morphic_v1\.venv\Scripts\python.exe -m uvicorn apps.web.main:app --host 127.0.0.1 --port 8766` with the worktree as the process working directory. Redirect stdout/stderr to the approved temporary directory `C:\Users\HUBERT~1\AppData\Local\Temp\opencode\morphic-go-qa` and record the PID. Confirm `/api/health` returns HTTP 200 before Playwright starts.

- [ ] **Step 7: Run the complete browser matrix**

Run in `tests/browser` with `PLAYWRIGHT_BASE_URL=http://127.0.0.1:8766`:

```powershell
npm test
```

Expected: all Playwright tests PASS with zero retries.

- [ ] **Step 8: Stop only the recorded QA PID**

Stop the process recorded in Step 6, wait for exit, and verify port 8766 is free. Do not stop processes by image name and do not touch ports 8090 or 8765.

If any production patch is made after Step 3 or Step 7, rerun Steps 1-8 before creating the freeze.

### Task 7: Create the Exact-Byte Freeze and Obtain Two Reviews

**Files:**
- Create: `docs/reviews/2026-07-21-technical-production-go-freeze-v4.sha256`
- Create: `docs/reviews/2026-07-21-technical-production-go-freeze-v4.md`

- [ ] **Step 1: Define the freeze scope**

Include every changed or untracked production/test file under `apps/`, `core/`, `services/`, `tools/`, and `tests/` that contributes to the current Workbench, plus `pyproject.toml`, `Run-WebUI.ps1`, the approved design, and this plan. Exclude runtime outputs, `Benutzer_Archive__manual-acceptance`, `data/harmonization_jobs/*.json`, lock files, caches, browser `node_modules`, generated reports, old review files, and old freeze manifests.

- [ ] **Step 2: Generate sorted SHA-256 entries**

Write one lowercase SHA-256 and one repository-relative slash-normalized path per line:

```text
abbac9036df4e3a97f8d1d1700762431455b8278b288db6f7a152a07a8ade9c2  apps/web/durable_io.py
```

Sort by ordinal repository-relative path. Verify every manifest path exists and every recomputed hash matches.

- [ ] **Step 3: Write the freeze record**

Record:

- branch and HEAD;
- dirty-worktree preservation statement;
- manifest SHA-256;
- exact focused/full/browser test counts and durations;
- Python and Node versions;
- QA PID/port lifecycle;
- known excluded runtime artifacts;
- rollback/recovery command and pre-state location;
- review rule: drift 0 and `P0=P1=P2=P3=0`.

- [ ] **Step 4: Dispatch two independent read-only reviews**

Each reviewer receives the design, implementation plan, freeze record, manifest, current diff, and prior Gate-0-v3 findings. Each reviewer must recompute the freeze and all scope hashes at start and end, inspect the full technical scope, and return severity-ranked findings with file/line evidence.

- [ ] **Step 5: Enforce the review gate**

GO requires both reviews to report:

```text
APPROVE
start drift: 0
end drift: 0
P0: 0
P1: 0
P2: 0
P3: 0
```

If either review reports a finding, preserve freeze v4 as rejected evidence, add a failing regression test, apply the smallest fix, rerun Task 6, create freeze v5, and obtain two new independent reviews. Never patch a reviewed freeze in place.

### Task 8: Start Port 8765 and Perform Live Production Acceptance

**Files:**
- Create: `docs/status/2026-07-21-technical-production-go.md`
- Modify: `PROJECT_MEMORY/00_CURRENT_STATE.md`

- [ ] **Step 1: Perform the immediate pre-start gate**

Recompute the accepted freeze manifest, verify drift 0, verify ports 8090, 8765, and 8766, and confirm port 8765 is free. Record the project interpreter path, worktree path, intended command, runtime roots, log paths, and exact rollback command.

- [ ] **Step 2: Start the reviewed worktree on port 8765**

Start only:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m uvicorn apps.web.main:app --host 127.0.0.1 --port 8765
```

Use `C:\morphic_v1\.worktrees\operator-workbench-phase1` as the working directory, redirect logs to the approved temporary location, retain the PID, and do not open or stop port 8090.

- [ ] **Step 3: Verify health and runtime identity**

Require HTTP 200 from `/api/health` and verify `/` identifies `Morphic Engine V1` and `Operator Workbench`.

- [ ] **Step 4: Verify the authoritative Level-4 profile catalog**

Require HTTP 200 from:

```text
/api/workbench/scan-profile-catalog?profile_level=4
```

Assert `profile_level == 4`, `internal.count > 0`, `total_scan_profiles == internal.count`, and every internal entry has non-empty `id` and `label`.

- [ ] **Step 5: Verify live scan start and replay**

POST the synthetic Gate-0 scan payload with one fresh `Idempotency-Key`, record the returned job ID, POST the exact same payload and key again, and require the same job ID. Stop that exact job through `/api/scan/jobs/{job_id}/stop` and require a terminal stopped state.

- [ ] **Step 6: Run the live browser smoke**

Open `http://127.0.0.1:8765/` through Playwright, wait for `document.body.dataset.workbenchReady === 'true'`, verify health and profile-pool rendering, navigate the synthetic client workflow through review, and assert no page errors or unexpected HTTP 4xx/5xx responses.

- [ ] **Step 7: Write final evidence and update the Golden Record**

Create `docs/status/2026-07-21-technical-production-go.md` with accepted freeze hash, both review verdicts, live PID, command, port checks, endpoint results, synthetic job/replay evidence, rollback command, and remaining Gates 1-16 as separately deferred scope.

Update `PROJECT_MEMORY/00_CURRENT_STATE.md` so its first section states technical production GO, names the accepted freeze/status record, identifies port 8765 and PID, and defines the next action as discussion of Gate 1 rather than further Gate-0 remediation.

- [ ] **Step 8: Final drift and process check**

Recompute all accepted hashes. Documentation added after code review must receive its own documentation-bound hash check. Verify the recorded PID still owns port 8765 and `/api/health` still returns HTTP 200. Any mismatch returns the status to NO-GO.
