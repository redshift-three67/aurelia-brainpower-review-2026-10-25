# Apps/Web Phase 1 Consolidation Implementation Plan
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate the approved Phase 1 end-user workflow into `apps/web` so operators can run the full client analysis + harmonization flow from one web shell while the CLI remains the execution engine behind the scenes.

**Architecture:** Keep `apps/web` as the only user-facing app in Phase 1. FastAPI owns request validation, job orchestration, report discovery, and preview APIs; `apps.cli.main` stays as the subprocess backend for scans and exports. Explicitly defer admin/source-management creation, editing, and maintenance workflows to Phase 2; Phase 1 only supports the client-facing flow.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, Uvicorn, existing CLI/PowerShell tooling, vanilla HTML/CSS/JS in `apps/web/static`, `pytest`.

---

### Task 1: Lock the Phase 1 web contract and remove Phase 2 scope from the shell

**Files:**
- Create: `apps/web/contracts.py`
- Modify: `apps/web/main.py`
- Modify: `apps/web/static/index.html`
- Modify: `apps/web/static/app.js`
- Test: `tests/test_web_contracts.py`
- Test: `tests/test_web_shell.py`

- [ ] Add explicit request/response models for the Phase 1 flow: client identity, personal profile template, entropy mode, optional image path/upload reference, `top_n` (`3|5|7|9`), adaptive result limits, and report preview type.
- [ ] Move request validation out of `apps/web/main.py` into `apps/web/contracts.py` so the API contract is stable and testable.

```python
# apps/web/contracts.py
class ScanFlowRequest(BaseModel):
    last_name: str = Field(min_length=1)
    first_name: str = Field(min_length=1)
    birth_date: str = Field(min_length=1)
    birth_place: str = Field(min_length=1)
    focus: str = Field(min_length=1)
    top_n: Literal[3, 5, 7, 9] = 5
    profile_template: str = Field(default="default", min_length=1)
    entropy_mode: Literal["standard", "hybrid"] = "standard"
    image_path: str = ""
    adaptive_limits: bool = True
```

- [ ] Update the shell copy/step labels so the UI is clearly Phase 1 client-facing; remove or hide admin/source-management language and controls from the wizard.
- [ ] Keep read-only health/preflight visibility if useful, but do not expose source editing, quarantine, registry maintenance, or admin CRUD in `apps/web`.
- [ ] Run:

```bash
python -m pytest tests/test_web_contracts.py tests/test_web_shell.py -q
```

---

### Task 2: Build a canonical web-to-CLI launcher aligned to `Run-MultiplexScan.ps1`

**Files:**
- Create: `apps/web/launcher.py`
- Modify: `apps/web/main.py`
- Modify: `apps/web/static/app.js`
- Test: `tests/test_web_launcher.py`
- Test: `tests/test_web_shell.py`
- Reference: `Run-MultiplexScan.ps1`

- [ ] Extract `_preview_command()` from `apps/web/main.py` into a dedicated launcher module that mirrors the productive CLI/PS1 flow instead of hardcoding a partial command.
- [ ] Ensure the builder emits the same top-level decisions as `Run-MultiplexScan.ps1`: top-n selection, focus, profile selection/template, entropy mode, optional image, export root, and harmonization-related flags where Phase 1 needs them.
- [ ] Keep preview and execution paths identical except for the `executes` flag.

```python
# apps/web/launcher.py
def build_scan_command(request: ScanFlowRequest) -> list[str]:
    command = [
        "python", "-m", "apps.cli.main", "field", "field-test",
        request.last_name, request.first_name,
        "--birth-date", request.birth_date,
        "--birth-place", request.birth_place,
        "--focus", request.focus,
        "--top-n", str(request.top_n),
        "--profile", request.profile_template,
        "--export", request.export_root,
    ]
    if request.entropy_mode == "hybrid":
        command.append("--hybrid-entropy")
    if request.image_path.strip():
        command.extend(["--image", request.image_path.strip()])
    return command
```

- [ ] Add a lightweight launcher metadata response so the UI can show “productive PS1/CLI job flow” and the exact command before execution.
- [ ] Run:

```bash
python -m pytest tests/test_web_launcher.py tests/test_web_shell.py -q
python -m pytest tests/test_launcher_topn.py -q
```

---

### Task 3: Add personal profile templates, entropy mode, image option, and adaptive limits to the client flow

**Files:**
- Modify: `apps/web/static/index.html`
- Modify: `apps/web/static/app.js`
- Modify: `apps/web/main.py`
- Modify: `apps/web/contracts.py`
- Test: `tests/test_web_shell.py`

- [ ] Extend the form with:
  - personal profile template selector
  - entropy mode selector (`standard` / `hybrid`)
  - image option (`image_path` for Phase 1)
  - adaptive result limit toggle
- [ ] Default adaptive limits from `top_n`, but allow the backend to cap preview/report payload size more aggressively for `7` and `9`.
- [ ] Keep the current top-n validation and expand the payload builder.

```js
function formPayload() {
  const data = new FormData($("#scan-form"));
  return {
    last_name: String(data.get("last_name") || "").trim(),
    first_name: String(data.get("first_name") || "").trim(),
    birth_date: String(data.get("birth_date") || "").trim(),
    birth_place: String(data.get("birth_place") || "").trim(),
    focus: String(data.get("focus") || "").trim(),
    top_n: Number(data.get("top_n") || 5),
    profile_template: String(data.get("profile_template") || "default"),
    entropy_mode: String(data.get("entropy_mode") || "standard"),
    image_path: String(data.get("image_path") || "").trim(),
    adaptive_limits: data.get("adaptive_limits") === "on"
  };
}
```

- [ ] Show the chosen template/mode/image status in the preview panel before the job starts.
- [ ] Run:

```bash
python -m pytest tests/test_web_shell.py -q
```

---

### Task 4: Surface real job progress and substeps for scan execution

**Files:**
- Modify: `apps/web/scan_jobs.py`
- Modify: `apps/web/main.py`
- Modify: `apps/web/static/index.html`
- Modify: `apps/web/static/app.js`
- Modify: `apps/web/static/app.css`
- Test: `tests/test_web_scan_jobs.py`
- Test: `tests/test_web_shell.py`

- [ ] Extend job snapshots beyond `stdout_tail`/`stderr_tail` to expose progress percent, current phase, current substep, and a bounded list of completed substeps parsed from CLI output.
- [ ] Parse known step markers from the productive flow (`[1/5]`, `[3/5]`, “Export”, “Harmonisierung”, etc.) instead of showing a fake fixed-width progress bar.
- [ ] Add dedicated UI elements for current phase, current substep, and substep checklist.

```python
# apps/web/scan_jobs.py
def _snapshot(self, job: _LocalScanJob) -> dict[str, object]:
    stdout_tail = _tail(job.stdout_path)
    progress = parse_scan_progress(stdout_tail)
    return {
        "executes": True,
        "job_id": job.job_id,
        "status": status,
        "returncode": returncode,
        "command": job.command,
        "stdout_tail": stdout_tail,
        "stderr_tail": _tail(job.stderr_path),
        "progress_percent": progress.percent,
        "phase": progress.phase,
        "current_substep": progress.current_substep,
        "completed_substeps": progress.completed_substeps,
    }
```

- [ ] Update the frontend to render visible progress/substeps for both scan and harmonization jobs.
- [ ] Run:

```bash
python -m pytest tests/test_web_scan_jobs.py tests/test_web_shell.py -q
```

---

### Task 5: Support the five-root, per-client, per-session report model and add inline preview for HTML/JSON/TXT/PDF

**Files:**
- Modify: `apps/web/reports.py`
- Modify: `apps/web/main.py`
- Modify: `apps/web/static/index.html`
- Modify: `apps/web/static/app.js`
- Modify: `apps/web/static/app.css`
- Test: `tests/test_web_reports.py`
- Test: `tests/test_web_shell.py`
- Reference: `tools/reporting_common.py`
- Reference: `apps/cli/commands/helpers/utility_helpers.py`

- [ ] Expand `ReportCatalog` to index all Phase 1 report roots
