# Gate 4 Primary Workflow and Report UX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove both system-model exits from the primary Workbench and deliver a Radi144-aligned, accessible catalog-first report flow with exact active-session auto-preview.

**Architecture:** Keep the current report API, catalog loader, preview renderer, iframe sandbox, and case-generation/request-token authorities. Extend the durable scan-job adapter with one fail-closed `report_session_id`, render the existing nested catalog payload as compact context-rich buttons, and use CSS plus a small roving-focus controller for desktop/mobile orientation.

**Tech Stack:** FastAPI, Python dataclasses and durable JSON state, Vanilla JavaScript DOM APIs, CSS media queries, pytest, Node VM tests, Playwright isolated browser runner.

**Authoritative design:** `docs/superpowers/specs/2026-07-31-gate4-primary-workflow-report-ux-design.md`

**Commit rule:** Do not commit, stage, push, reset, or clean unless the user gives a separate explicit instruction. Each task ends with an uncommitted diff/index checkpoint instead of a commit.

---

## File Map

### Production files

- Modify `apps/web/scan_jobs.py`: validate, accumulate, persist, recover, and expose one optional report-session authority from existing structured export markers.
- Modify `apps/web/main.py`: add `report_session_id` to the owner-bound scan-results response without changing existing results.
- Modify `apps/web/static/workbench-state.js`: hold per-case report-session and catalog focus state only in memory.
- Modify `apps/web/static/app.js`: flatten catalog entries for presentation, render context cards, preserve manual selection, perform exact-session auto-preview, and implement roving focus.
- Modify `apps/web/static/index.html`: remove both system-model links, make the catalog a labelled toolbar, and update positional copy from “left” to “above”.
- Modify `apps/web/static/app.css`: one-column catalog/preview layout, horizontal desktop track, vertical mobile cards, non-sticky preview, and focus/overflow states.

### Test files

- Create `tests/test_gate4_report_session_authority.py`: pure structured-marker validation and fail-closed authority tests.
- Create `tests/test_gate4_report_catalog_js.py`: Node VM tests for flattening, ranking, exact-session selection, and state helpers.
- Modify `tests/test_web_scan_jobs.py`: durable job-state and incremental marker integration coverage.
- Modify `tests/test_workbench_adaptive_limits.py`: owner-bound results response coverage for `report_session_id` while preserving Gate-2 behavior.
- Modify `tests/test_web_shell.py`: primary-link removal and internal route preservation.
- Modify `tests/test_workbench_report_dom_js.py`: safe context-card construction and no `innerHTML` regression.
- Modify `tests/test_workbench_ui_quality_contracts.py`: layout, non-sticky preview, toolbar, and overflow contracts.
- Modify `tests/browser/workbench.spec.js`: exact-session auto-preview, manual authority, roving keyboard behavior, responsive layout, New Case reset, and internal route reachability.

### Acceptance files created only after all code and reviews pass

- Create `docs/reviews/2026-07-31-gate4-primary-workflow-report-ux-review-1.md`.
- Create `docs/reviews/2026-07-31-gate4-primary-workflow-report-ux-review-2.md`.
- Create `docs/reviews/2026-07-31-gate4-primary-workflow-report-ux-freeze.sha256`.
- Create `docs/reviews/2026-07-31-gate4-primary-workflow-report-ux-freeze.md`.
- Create `docs/status/2026-07-31-gate4-primary-workflow-report-ux-acceptance.md`.
- Modify `PROJECT_MEMORY/00_CURRENT_STATE.md` only after freeze verification succeeds.

---

## Operational Preflight

- [ ] **Step 1: Rotate the long-lived Kilo process before implementation**

Run `/compact`, exit Kilo cleanly, and relaunch in
`C:\morphic_v1\.worktrees\operator-workbench-phase1` because the current main
process exceeded 2 GiB private memory and 12 hours runtime.

Expected after relaunch: one `kilo.exe` main process and materially lower private memory.

- [ ] **Step 2: Verify branch, index, ports, and stale processes**

Run:

```powershell
git branch --show-current
git diff --cached --name-only
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
  Where-Object { $_.LocalPort -in 8090,8765,8766 } |
  Select-Object LocalPort,OwningProcess
Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -match 'pytest|isolated_server\.py|process_tree_supervisor\.py|playwright.*workbench' } |
  Select-Object ProcessId,ParentProcessId,Name,CommandLine
```

Expected: branch `operator-workbench-phase1`; empty index; port 8090 remains PID 1692; ports 8765/8766 free; no owned test process.

- [ ] **Step 3: Follow the stable search protocol**

Use targeted shell searches only:

```powershell
rg --line-number --glob '*.py' --glob '*.js' 'PATTERN' exact/path
```

Every search command must have a 30-120 second tool timeout. Do not place integrated Grep/Glob calls in `multi_tool_use.parallel`.

---

### Task 1: Durable Structured Report-Session Authority

**Files:**
- Create: `tests/test_gate4_report_session_authority.py`
- Modify: `apps/web/scan_jobs.py:550-590,592-751,2118-2179,2928-3012`
- Modify: `tests/test_web_scan_jobs.py`

- [ ] **Step 1: Write pure RED tests for structured marker validation**

Create `tests/test_gate4_report_session_authority.py`:

```python
from __future__ import annotations

import json

from apps.web.scan_jobs import (
    _resolved_report_session_id,
    _update_report_session_authority,
)


def _record(session_id: str, *, profile: str = "P1") -> str:
    payload = {
        "version": 1,
        "profile": profile,
        "session_id": session_id,
        "json_path": f"C:/reports/{profile}.json",
        "html_path": f"C:/reports/{profile}.html",
    }
    return "MORPHIC_MULTIPLEX_EXPORT_V1 " + json.dumps(payload)


def test_report_session_authority_accepts_one_consistent_session() -> None:
    ids, invalid = _update_report_session_authority(
        [_record("session-a", profile="P1"), _record("session-a", profile="P2")],
        session_ids=set(),
        invalid=False,
    )

    assert invalid is False
    assert ids == {"session-a"}
    assert _resolved_report_session_id(ids, invalid) == "session-a"


def test_report_session_authority_rejects_conflicting_sessions() -> None:
    ids, invalid = _update_report_session_authority(
        [_record("session-a"), _record("session-b", profile="P2")],
        session_ids=set(),
        invalid=False,
    )

    assert ids == {"session-a", "session-b"}
    assert _resolved_report_session_id(ids, invalid) is None


def test_report_session_authority_rejects_any_malformed_prefixed_record() -> None:
    ids, invalid = _update_report_session_authority(
        [_record("session-a"), "MORPHIC_MULTIPLEX_EXPORT_V1 {not-json"],
        session_ids=set(),
        invalid=False,
    )

    assert ids == {"session-a"}
    assert invalid is True
    assert _resolved_report_session_id(ids, invalid) is None


def test_report_session_authority_ignores_unrelated_output() -> None:
    ids, invalid = _update_report_session_authority(
        ["Analyse gestartet", "Export gespeichert: C:/reports/P1.json"],
        session_ids=set(),
        invalid=False,
    )

    assert ids == set()
    assert invalid is False
    assert _resolved_report_session_id(ids, invalid) is None
```

- [ ] **Step 2: Run RED and verify missing helpers**

Run:

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
$env:OPENBLAS_NUM_THREADS='1'
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_gate4_report_session_authority.py -q --tb=short
```

Expected: collection/import failure because `_update_report_session_authority` and `_resolved_report_session_id` do not exist.

- [ ] **Step 3: Implement the pure fail-closed parser**

Add near the scan-job parsing helpers in `apps/web/scan_jobs.py`:

```python
_MULTIPLEX_EXPORT_PREFIX = "MORPHIC_MULTIPLEX_EXPORT_V1 "
_MULTIPLEX_EXPORT_KEYS = {
    "version",
    "profile",
    "session_id",
    "json_path",
    "html_path",
}


def _update_report_session_authority(
    lines: list[str],
    *,
    session_ids: set[str],
    invalid: bool,
) -> tuple[set[str], bool]:
    updated = set(session_ids)
    invalid_record = invalid
    for line in lines:
        if not line.startswith(_MULTIPLEX_EXPORT_PREFIX):
            continue
        try:
            payload = json.loads(line[len(_MULTIPLEX_EXPORT_PREFIX) :])
        except (json.JSONDecodeError, TypeError):
            invalid_record = True
            continue
        if (
            type(payload) is not dict
            or set(payload) != _MULTIPLEX_EXPORT_KEYS
            or payload.get("version") != 1
            or type(payload.get("profile")) is not str
            or not payload["profile"]
            or type(payload.get("session_id")) is not str
            or not payload["session_id"]
            or type(payload.get("json_path")) is not str
            or not payload["json_path"]
            or type(payload.get("html_path")) is not str
            or not payload["html_path"]
        ):
            invalid_record = True
            continue
        updated.add(payload["session_id"])
    return updated, invalid_record


def _resolved_report_session_id(
    session_ids: set[str], invalid: bool
) -> str | None:
    if invalid or len(session_ids) != 1:
        return None
    return next(iter(session_ids))
```

Use strict `type(...) is ...` checks so booleans and coercible objects do not become authority.

- [ ] **Step 4: Run the pure tests GREEN**

Run the Step 2 command.

Expected: `4 passed`.

- [ ] **Step 5: Write RED integration coverage for incremental and recovered jobs**

In `tests/test_web_scan_jobs.py`, add tests using the file's existing local-store/fake-process fixture pattern. Feed one marker in the first stdout chunk and a second same-session marker in the terminal chunk. Assert:

```python
assert running["report_session_id"] == "session-a"
assert completed["report_session_id"] == "session-a"
assert recovered["report_session_id"] == "session-a"
```

Add a second case with `session-a` followed by `session-b` and assert:

```python
assert completed["report_session_id"] is None
assert recovered["report_session_id"] is None
```

The fixture must write the exact `_record(...)` lines to the job's durable stdout log and exercise the existing persisted-job reload path; it must not patch the resolver helper.

- [ ] **Step 6: Run integration RED**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_web_scan_jobs.py -q --tb=short
```

Expected: new assertions fail because the job payload has no durable report-session fields.

- [ ] **Step 7: Persist and expose authority in the job store**

Add to `_LocalScanJob`:

```python
report_session_ids: set[str] = field(default_factory=set)
report_session_invalid: bool = False
```

Persist these fields:

```python
"report_session_ids": sorted(job.report_session_ids),
"report_session_invalid": job.report_session_invalid,
```

Recover them fail-closed while preserving concrete schema-v1 jobs created before Gate 4:

```python
raw_report_session_ids = payload.get("report_session_ids", [])
if not isinstance(raw_report_session_ids, list) or any(
    type(item) is not str or not item for item in raw_report_session_ids
):
    raise TypeError("persisted scan job report session ids are invalid")
raw_report_session_invalid = payload.get("report_session_invalid", False)
if type(raw_report_session_invalid) is not bool:
    raise TypeError("persisted scan job report session state is invalid")
```

Return both parsed values from `_parse_persisted_job_payload`, hydrate the dataclass in both recovery paths, and update only `stdout_lines` during polling:

```python
job.report_session_ids, job.report_session_invalid = (
    _update_report_session_authority(
        stdout_lines,
        session_ids=job.report_session_ids,
        invalid=job.report_session_invalid,
    )
)
```

Add to the public job dictionary:

```python
"report_session_id": _resolved_report_session_id(
    job.report_session_ids,
    job.report_session_invalid,
),
```

Do not parse stderr, truncated tails, filenames, artifact paths, or timestamps.

- [ ] **Step 8: Run Task 1 GREEN and compile**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_gate4_report_session_authority.py tests/test_web_scan_jobs.py -q --tb=short
& C:\morphic_v1\.venv\Scripts\python.exe -m py_compile apps/web/scan_jobs.py tests/test_gate4_report_session_authority.py tests/test_web_scan_jobs.py
```

Expected: all selected tests pass and compile exits 0.

- [ ] **Step 9: Uncommitted checkpoint**

Run:

```powershell
git diff --check -- apps/web/scan_jobs.py tests/test_gate4_report_session_authority.py tests/test_web_scan_jobs.py
git diff --cached --name-only
```

Expected: diff check passes apart from line-ending warnings; index remains empty.

---

### Task 2: Owner-Bound Results Contract and Per-Case Browser State

**Files:**
- Modify: `apps/web/main.py:1412-1535`
- Modify: `apps/web/static/workbench-state.js:1-40`
- Modify: `apps/web/static/app.js:1187-1214,1730-1930`
- Test: `tests/test_workbench_adaptive_limits.py`
- Test: `tests/test_gate4_report_catalog_js.py`

- [ ] **Step 1: Write RED API tests**

Extend the existing `_AdaptiveResultJobs` fixture in
`tests/test_workbench_adaptive_limits.py` with a `report_session_id` constructor
argument that is returned from `get_owned()`. Add:

```python
def test_owner_bound_results_expose_exact_optional_report_session(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MORPHIC_OPERATOR_ID", "gate-4-report-owner")
    export_root = tmp_path / "exports"
    artifacts = _ranked_result_artifacts(export_root, 3)
    jobs = _AdaptiveResultJobs(
        ["--top-n", "3"],
        artifacts,
        report_session_id="session-exact",
    )
    app = create_app(scan_jobs=jobs, runtime_dir=tmp_path / "runtime")
    jobs.owner_id = operator_owner_scope(app.state.operator_context)

    response = request(app, "GET", "/api/scan/jobs/gate-2-results/results")

    assert response.status_code == 200
    assert response.json()["report_session_id"] == "session-exact"
```

Add the same call with `report_session_id=None` and assert the JSON field is `None`. Existing score/order assertions must remain unchanged.

- [ ] **Step 2: Run API RED**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_adaptive_limits.py -q --tb=short
```

Expected: only the new response-field assertions fail.

- [ ] **Step 3: Add the response field without weakening ownership**

In `scan_job_results()`, after `get_owned_scan_job(job_id)` and existing artifact validation, normalize:

```python
raw_report_session_id = job.get("report_session_id")
report_session_id = (
    raw_report_session_id
    if type(raw_report_session_id) is str and raw_report_session_id
    else None
)
```

Add to the existing response dictionary:

```python
"report_session_id": report_session_id,
```

Do not move this logic before owner validation and do not expose command/stdout paths.

- [ ] **Step 4: Run API GREEN**

Run the Step 2 command.

Expected: all Gate-2/owner-bound result tests pass.

- [ ] **Step 5: Write RED frontend-state tests**

Create `tests/test_gate4_report_catalog_js.py` with a Node VM harness that loads
`workbench-state.js` and the function definitions from `app.js`. Assert the
initial state and New Case source contain all resets:

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_JS = ROOT / "apps" / "web" / "static" / "workbench-state.js"
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"


def test_gate4_report_state_is_memory_only_and_reset_per_case() -> None:
    state = STATE_JS.read_text(encoding="utf-8")
    app = APP_JS.read_text(encoding="utf-8")
    reset = app.split("async function resetWorkbenchForNewCase", 1)[1].split(
        "function wireWorkbench", 1
    )[0]

    assert "activeReportSessionId: null" in state
    assert "reportFocusId: null" in state
    assert "reportAutoSelectionKey: null" in state
    assert "state.activeReportSessionId = null" in reset
    assert "state.reportFocusId = null" in reset
    assert "state.reportAutoSelectionKey = null" in reset
    assert "localStorage" not in state
    assert "sessionStorage" not in state
```

- [ ] **Step 6: Run frontend-state RED**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_gate4_report_catalog_js.py::test_gate4_report_state_is_memory_only_and_reset_per_case -q --tb=short
```

Expected: missing state/reset assertions fail.

- [ ] **Step 7: Add per-case state and accept results authority**

Add to `MorphicWorkbenchState`:

```javascript
activeReportSessionId: null,
reportFocusId: null,
reportAutoSelectionKey: null,
reportSelectionSource: null,
```

In `loadScanResults()` after generation/job checks and before `loadReports()` can run:

```javascript
window.MorphicWorkbenchState.activeReportSessionId =
  typeof results.report_session_id === "string" && results.report_session_id
    ? results.report_session_id
    : null;
```

Reset all four fields in `resetWorkbenchForNewCase()` together with `activeReportId`.

- [ ] **Step 8: Run Task 2 GREEN and syntax checks**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_adaptive_limits.py tests/test_gate4_report_catalog_js.py -q --tb=short
node --check apps/web/static/workbench-state.js
node --check apps/web/static/app.js
```

Expected: all selected tests pass and both syntax checks exit 0.

- [ ] **Step 9: Uncommitted checkpoint**

Run scoped `git diff --check` for Task 2 files and confirm `git diff --cached --name-only` is empty.

---

### Task 3: Remove Primary Exits and Build the Catalog-First Layout

**Files:**
- Modify: `apps/web/static/index.html:455-483,542-584,666-672`
- Modify: `apps/web/static/app.css:880-1110, responsive blocks`
- Modify: `tests/test_web_shell.py`
- Modify: `tests/test_workbench_ui_quality_contracts.py`

- [ ] **Step 1: Write RED static contract tests**

Add to `tests/test_web_shell.py`:

```python
def test_gate4_primary_workbench_has_no_system_model_exit(
    tmp_path: Path,
) -> None:
    app = create_app(runtime_dir=tmp_path)

    primary = request(app, "GET", "/")
    internal = request(app, "GET", "/workflow-stepping")

    assert primary.status_code == 200
    assert 'href="/workflow-stepping"' not in primary.text
    assert "Systemmodell oeffnen" not in primary.text
    assert "Systemfluss ansehen" not in primary.text
    assert internal.status_code == 200
    assert "12-Schritt-Systemmodell" in internal.text
```

Add to `tests/test_workbench_ui_quality_contracts.py`:

```python
def test_gate4_report_catalog_precedes_full_width_nonsticky_preview() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    css = APP_CSS.read_text(encoding="utf-8")
    phase = html.split('id="finalize-phase"', 1)[1].split(
        '<!-- Phase 11:', 1
    )[0]

    assert phase.index('id="report-catalog-panel"') < phase.index(
        'id="report-preview-panel"'
    )
    report_list = phase.split('id="report-list"', 1)[1].split(">", 1)[0]
    assert 'role="toolbar"' in report_list
    assert 'aria-orientation="horizontal"' in report_list
    layout = css.split(".reports-layout", 1)[1].split(".reports-column", 1)[0]
    preview = css.split(".report-preview-column", 1)[1].split(
        ".report-preview-panel", 1
    )[0]
    assert "grid-template-columns: minmax(0, 1fr)" in layout
    assert "position: sticky" not in preview
```

- [ ] **Step 2: Run static RED**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_web_shell.py::test_gate4_primary_workbench_has_no_system_model_exit tests/test_workbench_ui_quality_contracts.py::test_gate4_report_catalog_precedes_full_width_nonsticky_preview -q --tb=short
```

Expected: both tests fail on current links/two-column/sticky layout.

- [ ] **Step 3: Remove only the primary links**

Replace the Phase-7 helper with non-linking truth:

```html
<p class="helper-text">Die angezeigten Stages stammen aus dem tatsaechlichen Top-N-Scan und bilden keinen separaten System-Walkthrough ab.</p>
```

Remove only this Phase-11 anchor:

```html
<a class="secondary-button" href="/workflow-stepping">Systemfluss ansehen</a>
```

Do not change the route or workflow-stepping assets.

- [ ] **Step 4: Make the catalog a labelled toolbar and update positional copy**

Change the report-list node to:

```html
<div id="report-list" class="report-list scroll-region" role="toolbar" aria-label="Berichte auswaehlen" aria-orientation="horizontal" aria-live="polite"></div>
```

Replace “Waehle links” with “Waehle oben” in the initial HTML and New Case reset copy.

- [ ] **Step 5: Implement the CSS-centered layout**

Replace the two-column/sticky rules with:

```css
.reports-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 20px;
  align-items: start;
}

.report-list {
  display: flex;
  gap: 12px;
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 4px 4px 10px;
  scroll-snap-type: x proximity;
  scrollbar-gutter: stable;
}

.report-item {
  flex: 0 0 clamp(240px, 28vw, 340px);
  min-width: 0;
  scroll-snap-align: start;
}

.report-preview-column {
  position: static;
  width: 100%;
}
```

At `max-width: 768px` add:

```css
.report-list {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  overflow-x: visible;
  overflow-y: visible;
  padding-inline: 0;
  scroll-snap-type: none;
}

.report-item {
  width: 100%;
  max-width: 100%;
}
```

Keep iframe sandbox/readability rules unchanged.

- [ ] **Step 6: Run static GREEN and CSS/HTML neighbors**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_web_shell.py tests/test_workbench_ui_quality_contracts.py tests/test_workbench_no_inner_html_js.py tests/test_workflow_stepping_runtime.py -q --tb=short
```

Expected: all selected tests pass; internal route remains covered.

- [ ] **Step 7: Uncommitted checkpoint**

Run scoped `git diff --check`; confirm index empty.

---

### Task 4: Context Cards and Exact-Session Auto-Preview

**Files:**
- Modify: `apps/web/static/app.js:1282-1474`
- Modify: `apps/web/static/app.css:915-1030`
- Modify: `tests/test_gate4_report_catalog_js.py`
- Modify: `tests/test_workbench_report_dom_js.py`

- [ ] **Step 1: Write RED pure ranking and flattening tests**

Append a Node VM test to `tests/test_gate4_report_catalog_js.py`. The script
loads `app.js` with `document.addEventListener` stubbed and calls these planned
global functions:

```javascript
const clients = [{
  client_id: "client-a",
  label: "Klient A",
  sessions: [{
    session_id: "session-active",
    label: "Session aktiv",
    files: [
      {id: "pdf-new", kind: "PDF", modified_at: "2026-07-31T12:04:00Z"},
      {id: "json-new", kind: "JSON", modified_at: "2026-07-31T12:03:00Z"},
      {id: "html-old", kind: "HTML", modified_at: "2026-07-31T12:01:00Z"},
    ],
  }],
}];
const entries = flattenReportEntries(clients);
const chosen = automaticReportCandidate(entries, "session-active");
console.log(JSON.stringify({entries, chosen}));
```

Assert in Python:

```python
assert payload["entries"][0]["client_label"] == "Klient A"
assert payload["entries"][0]["session_label"] == "Session aktiv"
assert payload["chosen"]["id"] == "html-old"
```

Add cases proving newest TXT/JSON wins when HTML is absent, PDF is last fallback,
and an unknown session returns `null` even when newer reports exist elsewhere.

- [ ] **Step 2: Run helper RED**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_gate4_report_catalog_js.py -q --tb=short
```

Expected: Node fails because the planned helpers do not exist.

- [ ] **Step 3: Implement deterministic pure helpers**

Add before `loadReports()`:

```javascript
function flattenReportEntries(clients) {
  const entries = [];
  (Array.isArray(clients) ? clients : []).forEach((client) => {
    (Array.isArray(client.sessions) ? client.sessions : []).forEach((session) => {
      (Array.isArray(session.files) ? session.files : []).forEach((file) => {
        entries.push({
          ...file,
          client_id: client.client_id || "",
          client_label: client.label || client.client_id || "Unbekannt",
          session_id: session.session_id || "",
          session_label: session.label || session.session_id || "Unbekannt",
        });
      });
    });
  });
  return entries;
}

function reportModifiedTime(entry) {
  const parsed = Date.parse(entry.modified_at || "");
  return Number.isFinite(parsed) ? parsed : 0;
}

function automaticReportCandidate(entries, sessionId) {
  if (typeof sessionId !== "string" || !sessionId) return null;
  const matches = entries.filter((entry) => entry.session_id === sessionId);
  const tiers = [
    (entry) => String(entry.kind || entry.type || "").toUpperCase() === "HTML",
    (entry) => ["TXT", "JSON"].includes(String(entry.kind || entry.type || "").toUpperCase()),
    (entry) => String(entry.kind || entry.type || "").toUpperCase() === "PDF",
  ];
  for (const accepts of tiers) {
    const ranked = matches.filter(accepts).sort(
      (left, right) => reportModifiedTime(right) - reportModifiedTime(left)
    );
    if (ranked.length) return ranked[0];
  }
  return null;
}
```

- [ ] **Step 4: Render flat context-rich buttons without `innerHTML`**

Replace nested `<details>` creation in `loadReports()` with iteration over
`flattenReportEntries(data.clients)`. Each `button.report-item` must append text
nodes/elements for:

```javascript
const clientMeta = document.createElement("span");
clientMeta.className = "report-item-client";
clientMeta.textContent = entry.client_label;
const sessionMeta = document.createElement("span");
sessionMeta.className = "report-item-session";
sessionMeta.textContent = entry.session_label;
```

Set `data-report-id`, `data-session-id`, `aria-pressed`, and the roving tabindex.
The click handler calls:

```javascript
renderReportPreview(entry.id, caseGeneration, "manual");
```

Update `tests/test_workbench_report_dom_js.py` to assert no `innerHTML`, no
`createElement("summary")`, presence of both metadata classes, and textContent
construction.

- [ ] **Step 5: Preserve manual authority and perform one exact auto-selection**

Change the signature:

```javascript
async function renderReportPreview(
  reportId,
  generation = caseGeneration,
  selectionSource = "manual"
)
```

At function entry bind the existing state authority:

```javascript
const state = window.MorphicWorkbenchState;
```

On successful preview only, set:

```javascript
state.activeReportId = reportId;
state.reportSelectionSource = selectionSource;
state.reportFocusId = reportId;
```

In `loadReports()`:

1. preserve `activeReportId` if the ID still exists;
2. clear report selection/preview authority if it disappeared;
3. derive `autoKey = `${generation}:${state.activeReportSessionId}``;
4. only when no manual selection exists and `reportAutoSelectionKey !== autoKey`, find an exact candidate;
5. set `reportAutoSelectionKey = autoKey` only after an exact candidate exists;
6. call `await renderReportPreview(candidate.id, generation, "auto")`;
7. re-check catalog token and generation before and after the awaited preview.

Never select from a different session and never focus the selected card from
this path.

- [ ] **Step 6: Run Task 4 GREEN**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_gate4_report_catalog_js.py tests/test_workbench_report_dom_js.py tests/test_workbench_ui_quality_contracts.py -q --tb=short
node --check apps/web/static/app.js
```

Expected: selected tests and syntax pass.

- [ ] **Step 7: Uncommitted checkpoint**

Run scoped diff check and verify empty index.

---

### Task 5: Roving Focus, Responsive Orientation, and Browser Acceptance

**Files:**
- Modify: `apps/web/static/app.js: report helpers and wireWorkbench()`
- Modify: `apps/web/static/app.css: report focus and responsive rules`
- Modify: `tests/test_gate4_report_catalog_js.py`
- Modify: `tests/browser/workbench.spec.js`

- [ ] **Step 1: Write RED static/Node focus-contract tests**

Add assertions that `app.js` contains one delegated report-list keydown handler,
uses `matchMedia("(max-width: 768px)")`, updates `aria-orientation`, and handles
`ArrowLeft`, `ArrowRight`, `ArrowUp`, `ArrowDown`, `Home`, and `End` without
calling `renderReportPreview` in the arrow branch.

Add a Node test around a small fake card collection that calls the planned pure
index resolver:

```javascript
console.log(JSON.stringify({
  leftAtStart: nextReportFocusIndex(0, 4, "ArrowLeft", false),
  right: nextReportFocusIndex(1, 4, "ArrowRight", false),
  downMobile: nextReportFocusIndex(1, 4, "ArrowDown", true),
  wrongAxisMobile: nextReportFocusIndex(1, 4, "ArrowRight", true),
  home: nextReportFocusIndex(2, 4, "Home", false),
  end: nextReportFocusIndex(1, 4, "End", true),
}));
```

Expected payload:

```json
{
  "leftAtStart": 0,
  "right": 2,
  "downMobile": 2,
  "wrongAxisMobile": 1,
  "home": 0,
  "end": 3
}
```

- [ ] **Step 2: Run focus RED**

Run the Gate-4 JS test file.

Expected: missing resolver/handler assertions fail.

- [ ] **Step 3: Implement clamped orientation-aware focus resolution**

Add:

```javascript
function nextReportFocusIndex(index, length, key, mobile) {
  if (length <= 0) return -1;
  if (key === "Home") return 0;
  if (key === "End") return length - 1;
  const backward = mobile ? key === "ArrowUp" : key === "ArrowLeft";
  const forward = mobile ? key === "ArrowDown" : key === "ArrowRight";
  if (backward) return Math.max(0, index - 1);
  if (forward) return Math.min(length - 1, index + 1);
  return index;
}
```

Add one `matchMedia` object and helpers that:

- set exactly one card tabindex to `0`;
- restore anchor by `reportFocusId`, then selected report, then first card;
- update `aria-orientation` on media changes;
- on accepted key, prevent default, update tabindex, focus the target, save its
  ID, and call `scrollIntoView({block: "nearest", inline: "nearest"})`;
- do not load a report until native click activation.

Wire one delegated `keydown` listener on `#report-list` in `wireWorkbench()`.

- [ ] **Step 4: Add focus-visible and reduced-motion-safe CSS**

Ensure `.report-item:focus-visible` has the established sage outline and that
`scroll-behavior` or card transitions are disabled under the existing
`prefers-reduced-motion: reduce` block.

- [ ] **Step 5: Write RED Playwright acceptance**

Add one focused test to `tests/browser/workbench.spec.js` that routes:

- completed scan results with `report_session_id: "session-active"`;
- report catalog containing another newer session plus the active session with
  PDF, JSON, and HTML candidates;
- preview endpoint responses recording requested report IDs.

The test must assert:

```javascript
await expect(page.locator('a[href="/workflow-stepping"]')).toHaveCount(0);
await expect(page.locator('#report-list')).toHaveAttribute('role', 'toolbar');
await expect(page.locator('#report-list')).toHaveAttribute('aria-orientation', 'horizontal');
await expect(page.locator('.report-item[aria-pressed="true"]')).toHaveAttribute('data-report-id', 'active-html');
expect(previewRequests).toEqual(['active-html']);
```

Then focus the selected card, press ArrowRight, and assert focus moved but
`previewRequests` did not change. Press Enter and assert one new preview request
and one pressed card. Press Home/End and assert clamped endpoint focus.

Refresh the catalog after setting a manual selection and assert the same report
remains selected without an automatic replacement.

Set viewport 375px, assert `aria-orientation="vertical"`, use ArrowDown, and
assert `document.documentElement.scrollWidth === document.documentElement.clientWidth`.

Click New Case and assert session/selection/frame/link reset. Finally navigate
directly to `/workflow-stepping` and assert HTTP/render success.

- [ ] **Step 6: Run Playwright RED**

Run only the new test through the direct runner, not npm argument proxy:

```powershell
node tests/browser/run-isolated-tests.js --grep "Gate 4 report catalog"
```

Expected: test fails on missing layout/keyboard/auto-selection behavior before implementation is complete.

- [ ] **Step 7: Complete browser-visible behavior and run GREEN**

Fix only Gate-4 code until the Step 6 command reports `1 passed`. Preserve
iframe sandbox, preview token checks, manual authority, and New Case cleanup.

- [ ] **Step 8: Run the complete Gate-4 focus matrix**

Run:

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
$env:OPENBLAS_NUM_THREADS='1'
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest `
  tests/test_gate4_report_session_authority.py `
  tests/test_gate4_report_catalog_js.py `
  tests/test_web_scan_jobs.py `
  tests/test_workbench_adaptive_limits.py `
  tests/test_web_shell.py `
  tests/test_workbench_report_dom_js.py `
  tests/test_workbench_ui_quality_contracts.py `
  tests/test_workflow_stepping_runtime.py `
  -q --tb=short
```

Expected: all selected tests pass.

- [ ] **Step 9: Run syntax, compile, diff, and cleanup checks**

Run:

```powershell
node --check apps/web/static/workbench-state.js
node --check apps/web/static/app.js
node --check tests/browser/workbench.spec.js
& C:\morphic_v1\.venv\Scripts\python.exe -m py_compile apps/web/scan_jobs.py apps/web/main.py tests/test_gate4_report_session_authority.py tests/test_gate4_report_catalog_js.py
git diff --check
git diff --cached --name-only
```

Expected: syntax/compile/diff pass and index is empty.

---

### Task 6: Full Verification, Independent Reviews, and Immutable Freeze

**Files:**
- Create the five acceptance files listed in the File Map.
- Modify `PROJECT_MEMORY/00_CURRENT_STATE.md` only after all checks pass.

- [ ] **Step 1: Resource and process preflight**

Verify one Kilo process, at least 3.5 GiB free RAM, port 8090 still PID 1692,
ports 8765/8766 free, and no stale test/browser process. Do not start matrices
until preflight is clean.

- [ ] **Step 2: Run the full Python suite on final source bytes**

Run:

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
$env:OPENBLAS_NUM_THREADS='1'
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests -q --tb=short
```

Expected: zero failures; record exact passed/skipped/warning counts and duration.

- [ ] **Step 3: Run the full isolated browser matrix serially**

Run:

```powershell
npm --prefix tests/browser test
```

Expected: all four shards pass. Record each shard count and duration.

- [ ] **Step 4: Perform manual desktop and 375px acceptance**

Use an isolated temporary server, never port 8090. Verify:

- no system-model links in the primary workflow;
- catalog above preview;
- horizontal desktop track with local scrolling;
- full-width non-sticky preview;
- exact active-session auto-preview;
- manual selection and pressed state;
- keyboard behavior;
- vertical 375px cards and no page overflow;
- direct internal `/workflow-stepping` route still works.

Capture viewport measurements and screenshots as temporary evidence; remove the
temporary runtime and server afterward.

- [ ] **Step 5: Run final operational cleanup audit**

Expected: port 8090 unchanged, 8765/8766 free, no isolated server, supervisor,
Playwright, scan gate, harmonization entry, or `morphic-browser-*` runtime; Git
index empty.

- [ ] **Step 6: Obtain final specification review**

Dispatch a read-only reviewer against the approved design and current bytes.
Acceptance requires `APPROVE` with zero P0-P3. Fix every finding through a new
RED/GREEN loop, rerun affected and full matrices, then re-review.

- [ ] **Step 7: Obtain final quality/security review**

Only after Step 6 approves, dispatch a separate read-only quality/security
reviewer. Acceptance requires `APPROVE` with zero P0-P2. Re-review after every
change.

- [ ] **Step 8: Build the SHA-256 scope manifest**

Include every production, test, design, plan, and authority file changed or
relied upon by Gate 4. Hash exact final bytes with `Get-FileHash -Algorithm
SHA256`; write lowercase hashes and normalized relative paths. Do not include
the review/freeze/status files in the source manifest.

- [ ] **Step 9: Write review, freeze, and status records**

Record:

- branch and HEAD;
- exact manifest hash and entry count;
- exact test counts/durations;
- manual viewport facts;
- review session IDs, verdicts, and document hashes;
- the limited Gate-4 boundary and explicit non-goals;
- port/process/index state;
- no commit/staging/push/reset.

- [ ] **Step 10: Verify every manifest and evidence hash**

Use a bounded PowerShell verifier that checks every listed file exists and
matches. Expected: `MANIFEST_OK N/N` and all review/freeze hashes exact.

- [ ] **Step 11: Update the Golden Record**

Only after Step 10 succeeds, update `PROJECT_MEMORY/00_CURRENT_STATE.md` with
Gate-4 acceptance, freeze paths/hashes, exact verification counts, preserved
Gate-1/Gate-2/Gate-3 boundaries, stable Kilo protocol, and the next roadmap gate.

- [ ] **Step 12: Final uncommitted checkpoint**

Run fresh regression, manifest, diff, index, port, process, temporary-runtime,
and one-Kilo-process checks. Do not commit without separate user authorization.
