# Gate 5 EMF Authority and Source Truth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the local Single-Core EMF gate with one durable modern/legacy authority, explicit manual activation, fail-closed lease revocation, and per-value source truth.

**Architecture:** Preserve `EmfTelemetryAuthority` and `EMFProfileService` as the authority and measurement core. Register modern and legacy route families against the same operations and durable state, then make the Workbench revalidate server status after every mutation and render each proxy value with its source health. Do not integrate remote hardware, physical sensors, or platform WebSockets.

**Tech Stack:** Python 3.12, FastAPI, durable JSON authority records, Vanilla JavaScript DOM APIs, pytest, Node VM tests, Playwright isolated browser runner.

**Authoritative design:** `docs/superpowers/specs/2026-08-06-gate5-emf-authority-source-truth-design.md`

**Commit rule:** Do not commit, stage, push, reset, or clean unless the user gives a separate explicit instruction. Every task ends with a scoped uncommitted checkpoint and an empty Git index.

---

## File Map

### Production files

- Modify `apps/web/emf_authority.py`: race-safe default-off initialization and shared authority factory.
- Modify `apps/web/emf.py`: safe status contract, common modern/legacy HTTP handlers, common WebSocket lease loop, and shared monitor.
- Modify `apps/web/main.py`: use the shared authority factory and register the legacy compatibility router beside the modern router.
- Modify `web_app.py`: remove `_emf_active`, `_measure_emf`, and all independent EMF handlers; initialize shared authority/session state and include the common routers.
- Verify `apps/web/static/workbench-api.js`: existing modern-only route calls remain unchanged; no legacy fallback is added.
- Modify `apps/web/static/app.js`: server-confirmed enable/disable flow and independent hardware-truth refresh.
- Modify `apps/web/static/workbench-render.js`: product label, four source-health rows, valid-value handling, and derived-proxy explanation.
- Modify `apps/web/static/index.html`: exact proxy language and activation-lifetime copy.
- Modify `apps/web/static/app.css`: compact source-status badges and responsive metric rows.

### Test files

- Modify `tests/test_emf_enable_authority.py`: initialization, persistence, partial-state, and subprocess authority tests.
- Modify `tests/test_web_emf_security.py`: shared safe status, modern HTTP lease races, and modern WebSocket behavior.
- Create `tests/test_gate5_emf_route_parity.py`: modern/legacy route registration, authentication, payload, and source-authority parity.
- Create `tests/test_gate5_emf_source_truth_js.py`: Node/DOM tests for confirmed status flow, product language, source badges, and invalid values.
- Modify `tests/test_web_shell.py`: active app exposes both route families without changing launcher authority.
- Modify `tests/browser/workbench.spec.js`: no auto-enable, POST-to-confirming-GET order, hardware refresh, source truth, responsive acceptance, and legacy smoke.

### Acceptance files created only after implementation and both reviews pass

- Create `docs/reviews/2026-08-06-gate5-emf-authority-source-truth-review-1.md`.
- Create `docs/reviews/2026-08-06-gate5-emf-authority-source-truth-review-2.md`.
- Create `docs/reviews/2026-08-06-gate5-emf-authority-source-truth-freeze.sha256`.
- Create `docs/reviews/2026-08-06-gate5-emf-authority-source-truth-freeze.md`.
- Create `docs/status/2026-08-06-gate5-emf-authority-source-truth-acceptance.md`.
- Modify `PROJECT_MEMORY/00_CURRENT_STATE.md` only after all evidence hashes verify.

---

## Operational Preflight

- [ ] **Step 1: Verify the Gate-4 continuation baseline**

Run from `C:\morphic_v1\.worktrees\operator-workbench-phase1`:

```powershell
git branch --show-current
git log -1 --oneline
git diff --cached --name-only
```

Expected:

- branch `report-ux-polish`;
- HEAD `2d38d3b` until the user separately authorizes a commit;
- empty index;
- the intentional Gate-4 source/evidence diff and Gate-5 spec/plan remain uncommitted.

- [ ] **Step 2: Reverify the Gate-4 source manifest before Gate-5 source changes**

Use the bounded verifier from the Gate-4 acceptance record against:

`docs/reviews/2026-07-31-gate4-primary-workflow-report-ux-freeze.sha256`

Expected: `MANIFEST_OK 33/33`.

- [ ] **Step 3: Verify resources and protected processes**

Require:

- one Kilo main process;
- at least 3.5 GiB free RAM before full matrices;
- ports `8090`, `8765`, and `8766` either free or owned by a separately documented user process;
- no stale pytest, isolated server, Playwright, scan-gate, or Harmonization process.

Do not stop unrelated user processes.

---

### Task 1: Race-Safe Durable Authority Initialization

**Files:**
- Modify: `apps/web/emf_authority.py`
- Modify: `apps/web/main.py`
- Test: `tests/test_emf_enable_authority.py`

- [ ] **Step 1: Write RED initialization and partial-state tests**

Add these tests:

```python
from apps.web.emf_authority import build_emf_telemetry_authority


def test_emf_authority_factory_initializes_disabled_once(tmp_path):
    first = build_emf_telemetry_authority(tmp_path)
    assert first.is_enabled() is False

    first.set_enabled(True)
    second = build_emf_telemetry_authority(tmp_path)
    assert second.is_enabled() is True
    assert second.path == first.path


def test_emf_authority_factory_does_not_repair_partial_state(tmp_path):
    authority_path = tmp_path / "emf-telemetry-authority.json"
    authority_path.write_text('{"enabled":true,"generation":1}', encoding="utf-8")

    authority = build_emf_telemetry_authority(tmp_path)

    assert authority.is_enabled() is False
    assert authority_path.read_text(encoding="utf-8") == '{"enabled":true,"generation":1}'
```

Retain the existing cross-process test and add a factory recreation assertion
after subprocess activation.

- [ ] **Step 2: Run RED**

```powershell
$env:PYTHONUTF8='1'
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_emf_enable_authority.py -q --tb=short
```

Expected: collection or assertion failure because `build_emf_telemetry_authority` does not exist.

- [ ] **Step 3: Add a lock-safe disabled initializer**

Add to `EmfTelemetryAuthority`:

```python
def initialize_disabled_if_missing(self) -> None:
    with _authority_lock(self.path):
        if self.path.exists() or self.generation_path.exists():
            return
        generation_record = {"activation_id": uuid.uuid4().hex, "generation": 1}
        durable_write_bytes(
            self.generation_path,
            json.dumps(
                generation_record, sort_keys=True, separators=(",", ":")
            ).encode("utf-8"),
        )
        durable_write_bytes(
            self.path,
            json.dumps(
                {"enabled": False, **generation_record},
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8"),
        )
```

Add the factory:

```python
def build_emf_telemetry_authority(
    runtime_dir: str | Path | None = None,
) -> EmfTelemetryAuthority:
    root = Path(runtime_dir) if runtime_dir is not None else Path.cwd() / "codex_tmp"
    authority = EmfTelemetryAuthority(root / "emf-telemetry-authority.json")
    authority.initialize_disabled_if_missing()
    return authority
```

The `path.exists() or generation_path.exists()` condition is deliberate: a
partial record remains fail-closed and is never silently repaired.

- [ ] **Step 4: Use the factory in the modern app**

Replace the manual construction and `if not path.exists(): set_enabled(False)`
block in `apps/web/main.py` with:

```python
app.state.emf_telemetry_authority = build_emf_telemetry_authority(runtime_path)
```

- [ ] **Step 5: Run GREEN and neighboring startup tests**

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest `
  tests/test_emf_enable_authority.py `
  tests/test_web_shell.py `
  tests/test_web_emf_security.py `
  -q --tb=short
```

Expected: all selected tests pass.

- [ ] **Step 6: Uncommitted checkpoint**

Run `git diff --check`, verify `git diff --cached --name-only` is empty, and
record the scoped diff. Do not commit.

---

### Task 2: Safe Shared HTTP Contract and Dual Routers

**Files:**
- Modify: `apps/web/emf.py`
- Modify: `apps/web/main.py`
- Modify: `tests/test_web_emf_security.py`
- Create: `tests/test_gate5_emf_route_parity.py`
- Modify: `tests/test_web_shell.py`

- [ ] **Step 1: Write RED safe-status tests**

In `tests/test_web_emf_security.py`, assert the exact modern payload before and
after enable/disable:

```python
EXPECTED_DISABLED = {
    "active": False,
    "activation_policy": "until_manually_disabled",
    "measurement_label": "System-/Entropie-basierter EMF-Proxy-Index",
}


def test_emf_status_exposes_only_safe_manual_lifetime_contract(tmp_path):
    app = create_app(runtime_dir=tmp_path)
    response = request(app, "GET", "/api/emf/status")
    assert response.status_code == 200
    assert response.json() == EXPECTED_DISABLED
    assert "generation" not in response.text
    assert "activation_id" not in response.text
    assert str(tmp_path) not in response.text
```

Add tests proving POST enable and disable return the re-read safe status and
that `continuous=true` does not change the payload or policy.

For enabled modern and legacy profile responses, assert that `generation`,
`activation_id`, authority paths, and lease tokens are absent from the complete
serialized payload.

- [ ] **Step 2: Write RED dual-router tests**

Create `tests/test_gate5_emf_route_parity.py` with exact route checks:

```python
@pytest.mark.parametrize("prefix", ["/api/emf", "/api/v1/emf"])
def test_emf_route_families_share_safe_status_and_authority(tmp_path, prefix):
    app = create_app(runtime_dir=tmp_path)
    assert request(app, "POST", f"{prefix}/enable").json()["active"] is True
    assert request(app, "GET", "/api/emf/status").json()["active"] is True
    assert request(app, "GET", "/api/v1/emf/status").json()["active"] is True
    assert request(app, "POST", f"{prefix}/disable").json()["active"] is False
```

Add API-key cases for both route families. With `MORPHIC_API_KEY` set, missing
or wrong credentials must return 401 before any generation change. Add one
session-cookie case per route family using the existing `SessionAuthority`
fixture pattern so API-key and session behavior remain equivalent.

With a deterministic fake measurement and enabled authority, both profile
routes must return the same payload. Parameterize the existing post-read
authentication/lease revocation tests across both route families.

- [ ] **Step 3: Run RED**

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest `
  tests/test_web_emf_security.py `
  tests/test_gate5_emf_route_parity.py `
  -q --tb=short
```

Expected: safe-status assertions and all legacy route requests fail.

- [ ] **Step 4: Add safe contract constants and payload helper**

In `apps/web/emf.py` add:

```python
EMF_ACTIVATION_POLICY = "until_manually_disabled"
EMF_MEASUREMENT_LABEL = "System-/Entropie-basierter EMF-Proxy-Index"


def emf_status_payload(authority) -> dict[str, object]:
    return {
        "active": authority.is_enabled(),
        "activation_policy": EMF_ACTIVATION_POLICY,
        "measurement_label": EMF_MEASUREMENT_LABEL,
    }
```

- [ ] **Step 5: Register the same handlers on both route families**

Keep the existing modern router and add:

```python
legacy_router = APIRouter(prefix="/api/v1/emf", tags=["emf-legacy"])
```

Stack modern and legacy decorators on the same handler functions. Enable calls
`set_enabled(True)`, disable calls `set_enabled(False)`, and both return
`emf_status_payload(authority)` after
the durable write. Status returns the same helper payload. Keep
`Depends(verify_api_key)` on every HTTP handler.

Use this exact registration pattern for enable, and the same stacked pattern
for disable, status, profile, and monitor:

```python
@router.post("/enable")
@legacy_router.post("/enable")
async def emf_enable(
    request: Request,
    continuous: bool = False,
    _api_key: str | None = Depends(verify_api_key),
) -> dict[str, object]:
    del continuous
    authority = request.app.state.emf_telemetry_authority
    authority.set_enabled(True)
    return emf_status_payload(authority)
```

- [ ] **Step 6: Include the legacy router in the active app**

Import `legacy_router` in `apps/web/main.py` and register it beside `emf_router`.
Add a `tests/test_web_shell.py` assertion that both `/api/emf/status` and
`/api/v1/emf/status` are present while the root launcher remains
`apps.web.main:app`.

```python
app.include_router(emf_router)
app.include_router(legacy_emf_router)
```

- [ ] **Step 7: Run GREEN**

Run the Step 3 command plus `tests/test_web_shell.py`. Expected: all pass.

- [ ] **Step 8: Uncommitted checkpoint**

Run Python compile for `apps/web/emf.py` and `apps/web/main.py`, then diff/index
checks. Do not commit.

---

### Task 3: Remove the Legacy Boolean and Delegate `web_app.py`

**Files:**
- Modify: `web_app.py`
- Modify: `tests/test_gate5_emf_route_parity.py`

- [ ] **Step 1: Write RED legacy-authority closure tests**

Add static assertions:

```python
def test_deprecated_web_app_has_no_second_emf_authority():
    source = Path("web_app.py").read_text(encoding="utf-8")
    assert "_emf_active" not in source
    assert "def _measure_emf" not in source
    assert "_emf_active = True" not in source
    assert "include_router(emf_router)" in source
    assert "include_router(legacy_emf_router)" in source
```

Add a behavioral import test that uses `web_app.app`, confirms both route
families share one authority object, and proves a legacy status GET does not
enable it.

- [ ] **Step 2: Run RED**

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_gate5_emf_route_parity.py -q --tb=short
```

Expected: old boolean, old measure function, and independent routes fail the
closure assertions.

- [ ] **Step 3: Initialize shared state in the deprecated app**

In `web_app.py` import:

```python
from apps.web.emf import router as emf_router
from apps.web.emf import legacy_router as legacy_emf_router
from apps.web.emf_authority import build_emf_telemetry_authority
from apps.web.security import SessionAuthority
```

Initialize once:

```python
app.state.session_authority = SessionAuthority()
legacy_runtime_dir = os.getenv("MORPHIC_RUNTIME_DIR")
app.state.emf_telemetry_authority = build_emf_telemetry_authority(
    Path(legacy_runtime_dir) if legacy_runtime_dir else None
)
app.include_router(emf_router)
app.include_router(legacy_emf_router)
```

Mount `apps/web/static` at `/static` in the deprecated app so the shared monitor
HTML uses the same CSP-safe CSS and JavaScript as the modern route. Add a route
test for `/api/v1/emf/monitor`, `/static/emf-monitor.css`, and
`/static/emf-monitor.js`.

```python
APP_STATIC_DIR = ROOT / "apps" / "web" / "static"
app.mount(
    "/static",
    StaticFiles(directory=str(APP_STATIC_DIR)),
    name="modern-static",
)
```

- [ ] **Step 4: Delete only the independent legacy EMF implementation**

Remove:

- `_measure_emf`;
- `_emf_active`;
- the old `/api/v1/emf/enable`, disable, status, profile, monitor, and WebSocket
  handlers;
- inline monitor JavaScript tied to connect-auto-enable.

Do not refactor unrelated legacy analysis/profile/amplifier routes.

- [ ] **Step 5: Run GREEN and import smoke**

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_gate5_emf_route_parity.py -q --tb=short
& C:\morphic_v1\.venv\Scripts\python.exe -c "import web_app; print(len(web_app.app.routes))"
```

Expected: tests pass and import exits 0.

- [ ] **Step 6: Uncommitted checkpoint**

Compile `web_app.py`, run scoped diff/index checks, and do not commit.

---

### Task 4: Modern and Legacy WebSocket Lease Parity

**Files:**
- Modify: `apps/web/emf.py`
- Modify: `tests/test_web_emf_security.py`
- Modify: `tests/test_gate5_emf_route_parity.py`

- [ ] **Step 1: Add RED route-family WebSocket cases**

Parameterize the existing fake-WebSocket behavioral tests over modern and
legacy route functions/paths. Cover:

- unauthenticated before activation or measurement;
- authenticated but disabled;
- current API key and enabled authority sends one safe snapshot;
- API-key or session revocation before measurement sends nothing;
- disable inside the measurement callback sends nothing and closes `4409`;
- connection does not change a disabled authority to enabled;
- an unexpected measurement exception closes `1011` without exception text in
  any payload.

The disable-during-measurement case must assert:

```python
assert websocket.sent == []
assert websocket.close_codes == [4409]
assert app.state.emf_telemetry_authority.is_enabled() is False
```

- [ ] **Step 2: Run RED**

Run the two EMF security/parity test files. Expected: legacy route coverage or
revocation assertions fail before consolidation is complete.

- [ ] **Step 3: Share one WebSocket handler**

Register the same `emf_websocket` function on both routers. Preserve this order
for every iteration:

1. resolve app state;
2. authenticate;
3. require enabled authority;
4. accept;
5. reauthenticate;
6. acquire lease;
7. measure;
8. reauthenticate again;
9. revalidate lease;
10. send;
11. sleep.

Do not catch and hide the explicit authentication/disabled close paths. Generic
internal exceptions may close `1011` without exposing exception text.

Use stacked route decorators and an explicit internal-error close:

```python
@router.websocket("/ws")
@legacy_router.websocket("/ws")
async def emf_websocket(websocket: WebSocket) -> None:
    scope = getattr(websocket, "scope", {}) or {}
    app = scope.get("app")
    state = getattr(app, "state", None) if app is not None else None
    if state is None:
        await websocket.close(code=1011)
        return
    authentication_required = get_api_key() is not None
    if not websocket_authenticated(websocket, state, authentication_required):
        await websocket.close(code=4401)
        return
    authority = state.emf_telemetry_authority
    if not authority.is_enabled():
        await websocket.close(code=4409)
        return
    await websocket.accept()
    try:
        while True:
            current_auth_required = get_api_key() is not None
            if not websocket_authenticated(websocket, state, current_auth_required):
                await websocket.close(code=4401)
                return
            lease = authority.begin_measurement()
            if lease is None:
                await websocket.close(code=4409)
                return
            payload = measure_emf()
            current_auth_required = get_api_key() is not None
            if not websocket_authenticated(websocket, state, current_auth_required):
                await websocket.close(code=4401)
                return
            if not authority.measurement_is_current(lease):
                await websocket.close(code=4409)
                return
            await websocket.send_json({"type": "emf_update", **payload})
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        return
    except Exception:
        await _close_internal_error(websocket)


async def _close_internal_error(websocket: WebSocket) -> None:
    try:
        await websocket.close(code=1011)
    except Exception:
        return
```

- [ ] **Step 4: Run GREEN**

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest `
  tests/test_web_emf_security.py `
  tests/test_gate5_emf_route_parity.py `
  -q --tb=short
```

Expected: all pass.

- [ ] **Step 5: Uncommitted checkpoint**

Compile, diff-check, verify empty index, and do not commit.

---

### Task 5: Server-Confirmed Workbench Activation Flow

**Files:**
- Verify: `apps/web/static/workbench-api.js`
- Modify: `apps/web/static/app.js`
- Create: `tests/test_gate5_emf_source_truth_js.py`

- [ ] **Step 1: Write RED Node tests for mutation ordering**

Build a small Node harness around the Workbench API and DOM functions. Record
calls and assert:

```javascript
await setEmfTelemetryEnabled(true, caseGeneration);
console.log(JSON.stringify({calls, active: MorphicWorkbenchState.emfTelemetryActive}));
```

Expected successful call order:

```json
{
  "calls": ["POST enable", "GET status", "GET hardware"],
  "active": true
}
```

Add a case where POST succeeds but status GET rejects. Assert:

- state is not changed to active based on the POST response;
- both buttons remain in an unknown/error-safe state;
- hardware GET is not called;
- no legacy URL is requested.

Add a storage/persistence contract asserting that EMF activation state is not
written to `localStorage`, `sessionStorage`, Workbench drafts, or template
payloads.

- [ ] **Step 2: Run RED**

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_gate5_emf_source_truth_js.py -q --tb=short
```

Expected: current direct POST trust and call ordering fail.

- [ ] **Step 3: Make status loading return confirmation**

Refactor `loadEmfTelemetryStatus()` to return `true` only after an authoritative
payload updates state and controls, and `false` after its existing error render.
Validate `payload.active` as an exact Boolean before using it.

- [ ] **Step 4: Add a pending control state without changing authority state**

Add a helper that disables both buttons and updates copy while leaving
`state.emfTelemetryActive` unchanged:

```javascript
function showEmfTelemetryPending(message) {
  const status = $("#emf-telemetry-state");
  const enable = $("#emf-enable-button");
  const disable = $("#emf-disable-button");
  if (status) {
    status.textContent = message;
    status.className = "inline-state neutral";
  }
  if (enable) enable.disabled = true;
  if (disable) disable.disabled = true;
}
```

- [ ] **Step 5: Revalidate after every POST**

`setEmfTelemetryEnabled()` must:

1. show pending without assuming the requested value;
2. call modern enable or disable;
3. abort on generation drift;
4. await `loadEmfTelemetryStatus(generation)`;
5. load hardware truth only when status confirmation succeeded;
6. on POST failure, attempt one status reload and keep hardware refresh
   independent from guessed mutation state.

- [ ] **Step 6: Run GREEN and syntax checks**

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_gate5_emf_source_truth_js.py -q --tb=short
node --check apps/web/static/workbench-api.js
node --check apps/web/static/app.js
```

- [ ] **Step 7: Uncommitted checkpoint**

Run scoped diff/index checks and do not commit.

---

### Task 6: Per-Value Source Truth and Product Language

**Files:**
- Modify: `apps/web/static/workbench-render.js`
- Modify: `apps/web/static/index.html`
- Modify: `apps/web/static/app.css`
- Modify: `tests/test_gate5_emf_source_truth_js.py`
- Modify: `tests/browser/workbench.spec.js`

- [ ] **Step 1: Write RED rendering tests**

Use the DOM harness to render a calibration payload containing:

```javascript
{
  emf_index: 0.42,
  entropy_score: 0.73,
  timing_jitter_ms: 0.18,
  system_load: 0.61,
  sensor_entropy: 0.5,
  source_health: {
    rng: "ok",
    cpu_timing: "partial",
    system_load: "ok",
    sensor_entropy: "fallback"
  },
  replay: {sensor_source: "fallback"}
}
```

Assert exact visible labels for the aggregate proxy and all four source keys,
plus distinct status classes for `ok`, `partial`, and `fallback`.

Add parameterized invalid cases for each value: `null`, missing, `""`,
`"ungueltig"`, `NaN`, `Infinity`, and `-Infinity`. Invalid aggregate values must
produce no gauge. Invalid component values must show `--` while retaining their
source status.

- [ ] **Step 2: Run RED**

Run `tests/test_gate5_emf_source_truth_js.py`. Expected: product label, source
rows, and invalid component behavior are absent.

- [ ] **Step 3: Add strict finite-value rendering helpers**

In `workbench-render.js`, add a helper that accepts only non-empty finite
numeric values and returns `null` otherwise. Do not use `Number(null)` as a
valid zero.

Define the fixed display map:

```javascript
const EMF_PROXY_METRICS = [
  ["Entropie", "entropy_score", "rng"],
  ["Jitter (ms)", "timing_jitter_ms", "cpu_timing"],
  ["Systemlast", "system_load", "system_load"],
  ["Sensorentropie", "sensor_entropy", "sensor_entropy"],
];
```

For each row, render value or `--`, the source key, and a normalized status.
Unknown health values render `unknown`, never `ok`.

- [ ] **Step 4: Apply the exact product language**

Replace visible aggregate labels with:

`System-/Entropie-basierter EMF-Proxy-Index`

Add concise copy stating that the index is derived and is not a physical field
measurement. Update active status help to say `aktiv bis manuell deaktiviert`.

- [ ] **Step 5: Add minimal responsive CSS**

Use existing token colors and add only:

- `.emf-source-row` for value/source/status alignment;
- `.emf-source-key` monospace treatment;
- `.emf-source-status` variants for `ok`, `partial`, `fallback`, and `unknown`;
- a 375px rule that stacks row metadata without horizontal page overflow.

- [ ] **Step 6: Run GREEN and neighbor contracts**

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest `
  tests/test_gate5_emf_source_truth_js.py `
  tests/test_workbench_ui_quality_contracts.py `
  tests/test_web_hardware_truth.py `
  -q --tb=short
node --check apps/web/static/workbench-render.js
```

- [ ] **Step 7: Uncommitted checkpoint**

Run diff/index checks and do not commit.

---

### Task 7: Browser Contract and Responsive Acceptance

**Files:**
- Modify: `tests/browser/workbench.spec.js`
- Modify: `tests/test_gate5_emf_route_parity.py`

- [ ] **Step 1: Write a focused Playwright RED test**

Route status, mutation, and hardware requests. Assert:

1. initial Workbench load sends no enable/disable POST;
2. enable click calls POST, confirming status GET, then hardware GET;
3. buttons reflect only confirmed status;
4. active copy includes manual-disable lifetime;
5. four source keys and fallback badges are visible;
6. invalid aggregate removes the gauge;
7. disable click confirms inactive and returns to disabled display;
8. at 375px, page `scrollWidth === clientWidth`.

Add a lightweight HTTP legacy smoke through the browser request context proving
`/api/v1/emf/status` matches `/api/emf/status` and does not activate.

- [ ] **Step 2: Run browser RED**

```powershell
node tests/browser/run-isolated-tests.js --grep "Gate 5 EMF authority"
```

Expected: the new focused test fails before final UI behavior is complete.

- [ ] **Step 3: Make only Gate-5-visible corrections**

Fix selectors/copy/ordering required by the RED test. Do not alter scan,
Harmonization, report, scoring, hardware-driver, or source-catalog behavior.

- [ ] **Step 4: Run browser GREEN**

Run the Step 2 command. Expected: `1 passed` with zero retries.

- [ ] **Step 5: Manual Desktop and 375px acceptance**

Start an isolated server on a verified free port, never port 8090. Verify and
record:

- default-off initial state;
- deliberate enable and disable;
- active-until-manually-disabled copy;
- aggregate proxy label;
- all four source keys/statuses;
- invalid-value no-gauge behavior;
- no horizontal page overflow at 375px;
- no legacy connect-auto-enable;
- modern and legacy status equality.

Capture temporary screenshots, inspect them, then remove screenshots, server,
script, and isolated runtime.

- [ ] **Step 6: Run the complete Gate-5 focus matrix**

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
$env:OPENBLAS_NUM_THREADS='1'
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest `
  tests/test_emf_enable_authority.py `
  tests/test_web_emf_security.py `
  tests/test_gate5_emf_route_parity.py `
  tests/test_gate5_emf_source_truth_js.py `
  tests/test_web_shell.py `
  tests/test_workbench_ui_quality_contracts.py `
  -q --tb=short
```

Expected: all selected tests pass.

- [ ] **Step 7: Syntax, compile, and diff checks**

```powershell
node --check apps/web/static/workbench-api.js
node --check apps/web/static/app.js
node --check apps/web/static/workbench-render.js
node --check tests/browser/workbench.spec.js
& C:\morphic_v1\.venv\Scripts\python.exe -m py_compile `
  apps/web/emf_authority.py `
  apps/web/emf.py `
  apps/web/main.py `
  web_app.py
git diff --check
git diff --cached --name-only
```

Expected: all syntax/compile/diff checks pass and index is empty.

---

### Task 8: Full Verification, Independent Reviews, and Immutable Freeze

**Files:**
- Create the five Gate-5 acceptance files listed in the File Map.
- Modify `PROJECT_MEMORY/00_CURRENT_STATE.md` only after evidence verification.

- [ ] **Step 1: Final resource and process preflight**

Require one Kilo process, at least 3.5 GiB free RAM, known port ownership, and no
stale test/browser/server process.

- [ ] **Step 2: Run the full Python suite on final source bytes**

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
$env:OPENBLAS_NUM_THREADS='1'
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests -q --tb=short
```

Expected: zero failures. Record exact pass/skip/warning counts and duration.

- [ ] **Step 3: Run the full isolated browser matrix serially**

```powershell
npm --prefix tests/browser test
```

Expected: every shard passes. Record each count and duration.

- [ ] **Step 4: Obtain final specification review**

Dispatch a read-only reviewer against the approved Gate-5 design and current
bytes. Acceptance requires `APPROVE` and `P0=P1=P2=P3=0`. Every valid finding
requires a new RED/GREEN loop, affected matrices, full matrices, and re-review.

- [ ] **Step 5: Obtain final quality/security review**

Only after Step 4 approves, dispatch a separate read-only reviewer. Acceptance
requires `APPROVE` and `P0=P1=P2=0`. Re-review after every source change.

- [ ] **Step 6: Build the SHA-256 source manifest**

Include every Gate-5 production, legacy, test, design, plan, authority, and
browser-runner file changed or directly relied upon. Use lowercase SHA-256 and
normalized relative paths. Exclude review, freeze, status, and project-memory
files from the source manifest.

- [ ] **Step 7: Write review, freeze, and acceptance records**

Record:

- branch and HEAD;
- intentional uncommitted source scope;
- manifest path, entry count, and hash;
- exact focused/full/browser/manual results;
- review session IDs, verdicts, findings, and document hashes;
- modern/legacy parity and durable-lifetime facts;
- explicit non-goals;
- ports, processes, temporary-runtime state, and empty index;
- no commit, staging, push, reset, or clean.

- [ ] **Step 8: Verify every manifest and evidence hash**

Use a bounded PowerShell verifier. Expected: `MANIFEST_OK N/N` and exact hashes
for both reviews and the freeze record.

- [ ] **Step 9: Update the Golden Record**

Only after Step 8 passes, update `PROJECT_MEMORY/00_CURRENT_STATE.md` with Gate-5
acceptance, evidence hashes, exact tests, preserved Gates 1-4, and the next
Single-Core roadmap unit, Gate 6.

- [ ] **Step 10: Final uncommitted checkpoint**

Run a fresh Gate-5 focus regression, source/evidence hash verification,
syntax/compile/diff/index checks, port/process/temp-runtime audit, and one-Kilo
check. Do not commit without separate user authorization.

---

## Execution Order and Stop Gates

Execute Tasks 1 through 8 strictly in order.

Stop immediately when:

- initialization overwrites an existing or partial authority;
- modern and legacy routes diverge;
- an unauthenticated or disabled path measures;
- WebSocket connect enables telemetry;
- disable permits a post-revocation send;
- UI treats POST success as confirmed state without GET revalidation;
- invalid values render a zero or gauge;
- source health is missing or mislabeled;
- a test requires hardware, network, Quantum, report, or Harmonization changes;
- RAM/process/port preflight is not clean;
- either independent review rejects the final source bytes.

Gate 4's verified manifest remains the rollback reference throughout Gate 5.
