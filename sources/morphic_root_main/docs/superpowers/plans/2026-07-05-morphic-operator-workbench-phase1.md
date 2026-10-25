# Morphic Operator Workbench Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current 8-step Phase-1 web shell with a single official 10-phase Operator Workbench that adds a review gate, runtime-backed resume/templates, a hardware truth layer, and a real result/finalization workspace without changing the underlying production scan path.

**Architecture:** Keep `apps/web/main.py` as the only official web entry point, but move new workbench concerns into dedicated backend modules: a workflow registry, a hardware truth builder, and a runtime-backed workbench store. On the frontend, split the current large `app.js` into small static modules and rebuild the shell around the agreed 10-phase workbench while preserving the existing scan/harmonization endpoints and report catalog.

**Tech Stack:** FastAPI, Pydantic, plain HTML/CSS/JavaScript, pytest, runtime JSON stores under `data/runtime` or `runtime_dir`

---

## Scope Boundary

This plan intentionally covers the **first implementation stage** from the approved design:

- canonical 10-phase workbench
- review & release gate
- runtime-backed draft/template persistence
- result workspace
- hardware truth model
- standard/expert mode
- run trace manifest

This plan does **not** include:

- event-driven replacement of stdout parsing
- report catalog privacy redesign
- new input modes like group/geo/image as first-class operator starts
- real quartz integration
- deeper scan algorithm changes
- OpenBLAS stabilization work outside the web workbench scope

## File Map

### Create

- `apps/web/workbench_registry.py`
  - Single source of truth for the 10 workbench phases, labels, CTA text, and allowed transitions.
- `apps/web/hardware_truth.py`
  - Builds the hardware/realtime truth snapshot and expert-mode gate warnings from current backend signals.
- `apps/web/workbench_runtime.py`
  - Persists draft state, templates, and run trace manifests in runtime JSON stores.
- `apps/web/workbench.py`
  - FastAPI router for `/api/workbench/*` endpoints.
- `apps/web/static/workbench-state.js`
  - Frontend workbench state, current phase, draft state, template state, and mode state.
- `apps/web/static/workbench-api.js`
  - Browser API helpers for registry, hardware truth, draft/template persistence, scan, reports, and harmonization.
- `apps/web/static/workbench-render.js`
  - Renders the 10-step nav, focus management, review cards, result workspace, and finalization state.
- `tests/test_workbench_registry.py`
  - Registry and transition tests.
- `tests/test_web_hardware_truth.py`
  - Hardware truth classification and expert-mode warning tests.
- `tests/test_web_workbench_runtime.py`
  - Draft/template/run-trace store and router tests.

### Modify

- `apps/web/contracts.py`
  - Add workbench mode and workbench-related request/response models.
- `apps/web/main.py`
  - Instantiate the workbench store, include the new router, and seed run traces from scan/harmonization starts.
- `apps/web/launcher.py`
  - Return review-friendly launcher metadata used by the workbench review gate.
- `apps/web/harmonization.py`
  - Include report binding and workbench mode in harmonization-facing payloads/snapshots.
- `apps/web/static/index.html`
  - Replace the 8-step shell with the 10-phase operator workbench markup.
- `apps/web/static/app.js`
  - Shrink to a bootstrap file that wires the three new frontend modules together.
- `apps/web/static/app.css`
  - Update layout and add styles for the 10-phase workbench, focus handling, hardware truth cards, result workspace, and reduced motion.
- `tests/test_web_contracts.py`
  - Cover new workbench request fields and validation.
- `tests/test_web_shell.py`
  - Update structure assertions from 8-step wizard to 10-phase workbench and new workbench endpoints.
- `tests/test_web_hardware_status.py`
  - Keep the existing non-sampling guarantee while validating the new truth-model path does not force device reads.

### Read During Implementation

- `docs/superpowers/specs/2026-07-05-morphic-operator-workbench-design.md`
- `docs/deep-audit-2026-07-04/PHASE_6_RADI144_TRANSFER_WORKFLOW_UIUX.md`
- `docs/deep-audit-2026-07-04/PHASE_7_HARDWARE_ECHTZEIT_DETERMINISMUS.md`

---

### Task 1: Canonical Workbench Contracts And Registry

**Files:**
- Create: `apps/web/workbench_registry.py`
- Modify: `apps/web/contracts.py`
- Test: `tests/test_workbench_registry.py`
- Test: `tests/test_web_contracts.py`

- [ ] **Step 1: Write the failing registry and contract tests**

```python
# tests/test_workbench_registry.py
from apps.web.workbench_registry import build_workbench_registry


def test_workbench_registry_exposes_10_canonical_steps() -> None:
    payload = build_workbench_registry()

    assert payload["version"] == 1
    assert [step["id"] for step in payload["steps"]] == [
        "runtime",
        "client",
        "focus",
        "profile",
        "hardware",
        "review",
        "run",
        "results",
        "details",
        "finalize",
    ]
    assert payload["steps"][5]["label"] == "Review & Freigabe"
    assert payload["steps"][9]["label"] == "Harmonisierung & Export"


def test_workbench_registry_marks_pipeline_view_as_explanatory_only() -> None:
    payload = build_workbench_registry()

    assert payload["pipeline_view"]["href"] == "/workflow-stepping"
    assert payload["pipeline_view"]["kind"] == "explanatory"
```

```python
# tests/test_web_contracts.py
from pydantic import ValidationError

from apps.web.contracts import HarmonizationRequest, Phase1ScanRequest


def test_phase1_scan_request_accepts_workbench_mode() -> None:
    request = Phase1ScanRequest(
        last_name="Deisenhofer",
        first_name="Klaus",
        birth_date="09041966",
        birth_place="Augsburg",
        focus="Bronchien",
        consent_local=True,
        consent_safety=True,
        workbench_mode="expert",
    )

    assert request.workbench_mode == "expert"


def test_phase1_scan_request_rejects_unknown_workbench_mode() -> None:
    try:
        Phase1ScanRequest(
            last_name="Deisenhofer",
            first_name="Klaus",
            birth_date="09041966",
            birth_place="Augsburg",
            focus="Bronchien",
            consent_local=True,
            consent_safety=True,
            workbench_mode="turbo",
        )
    except ValidationError as exc:
        assert "workbench_mode must be one of standard or expert" in str(exc)
    else:
        raise AssertionError("expected ValidationError")


def test_harmonization_request_accepts_report_binding_and_workbench_mode() -> None:
    request = HarmonizationRequest(
        target_frequency=432.0,
        duration_minutes=5,
        workbench_mode="standard",
        report_id="rep-123",
    )

    assert request.workbench_mode == "standard"
    assert request.report_id == "rep-123"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `& ".\.venv\Scripts\python.exe" -m pytest tests/test_workbench_registry.py tests/test_web_contracts.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'apps.web.workbench_registry'` and/or missing `workbench_mode` / `HarmonizationRequest` fields.

- [ ] **Step 3: Implement the registry file and contract additions**

```python
# apps/web/workbench_registry.py
from __future__ import annotations


WORKBENCH_STEPS = [
    {
        "id": "runtime",
        "label": "Runtime & Workspace",
        "cta": "Weiter zu Klient / Kontext",
    },
    {"id": "client", "label": "Klient / Kontext", "cta": "Weiter zu Fokus & Zielsetzung"},
    {"id": "focus", "label": "Fokus & Zielsetzung", "cta": "Weiter zu Analyseprofil"},
    {"id": "profile", "label": "Analyseprofil", "cta": "Weiter zu Hardware & Realtime"},
    {"id": "hardware", "label": "Hardware & Realtime", "cta": "Weiter zu Review & Freigabe"},
    {"id": "review", "label": "Review & Freigabe", "cta": "Analyse starten"},
    {"id": "run", "label": "Analyse-Lauf", "cta": "Weiter zu Ergebnis-Uebersicht"},
    {"id": "results", "label": "Ergebnis-Uebersicht", "cta": "Weiter zu Technische Details"},
    {"id": "details", "label": "Technische Details & Nachvollziehbarkeit", "cta": "Weiter zu Harmonisierung & Export"},
    {"id": "finalize", "label": "Harmonisierung & Export", "cta": "Workflow abschliessen"},
]


def build_workbench_registry() -> dict[str, object]:
    return {
        "version": 1,
        "steps": WORKBENCH_STEPS,
        "modes": ["standard", "expert"],
        "pipeline_view": {
            "href": "/workflow-stepping",
            "label": "Systemfluss ansehen",
            "kind": "explanatory",
        },
    }
```

```python
# apps/web/contracts.py
class Phase1ScanRequest(BaseModel):
    # existing fields unchanged
    workbench_mode: str = "standard"

    @field_validator("workbench_mode")
    @classmethod
    def validate_workbench_mode(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if cleaned not in {"standard", "expert"}:
            raise ValueError("workbench_mode must be one of standard or expert")
        return cleaned


class HarmonizationRequest(BaseModel):
    intention: str = Field(default="harmonization", min_length=1)
    target_frequency: float = Field(default=432.0, gt=0)
    duration_minutes: int = Field(default=5, ge=1)
    use_cpu: bool = True
    use_gpu: bool = False
    use_ram: bool = False
    use_websocket: bool = False
    use_driver_layer: bool = False
    workbench_mode: str = "standard"
    report_id: str | None = None

    @field_validator("workbench_mode")
    @classmethod
    def validate_mode(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if cleaned not in {"standard", "expert"}:
            raise ValueError("workbench_mode must be one of standard or expert")
        return cleaned
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `& ".\.venv\Scripts\python.exe" -m pytest tests/test_workbench_registry.py tests/test_web_contracts.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/workbench_registry.py apps/web/contracts.py tests/test_workbench_registry.py tests/test_web_contracts.py
git commit -m "feat: add workbench registry and request contracts"
```

### Task 2: Hardware Truth Model And Expert-Mode Gate API

**Files:**
- Create: `apps/web/hardware_truth.py`
- Create: `apps/web/workbench.py`
- Modify: `apps/web/main.py`
- Test: `tests/test_web_hardware_truth.py`
- Test: `tests/test_web_hardware_status.py`

- [ ] **Step 1: Write the failing hardware truth tests**

```python
# tests/test_web_hardware_truth.py
from apps.web.hardware_truth import build_hardware_truth_snapshot


def test_hardware_truth_snapshot_classifies_components_without_sampling() -> None:
    payload = build_hardware_truth_snapshot(
        system_report={
            "cpu": {"model": "Test CPU"},
            "gpu": {"has_gpu": False},
            "sensors": {"devices": []},
        },
        driver_layer={"providers": [], "note": "status does not open devices"},
        emf_profile={"source_health": {"sensor_entropy": "fallback"}},
        mode="standard",
    )

    by_id = {item["id"]: item for item in payload["components"]}
    assert by_id["cpu"]["status"] == "real_active"
    assert by_id["gpu"]["status"] in {"software_fallback", "real_available_not_used"}
    assert by_id["quartz"]["status"] == "not_implemented"
    assert payload["mode"] == "standard"


def test_hardware_truth_snapshot_adds_expert_gate_warnings() -> None:
    payload = build_hardware_truth_snapshot(
        system_report={
            "cpu": {"model": "Test CPU"},
            "gpu": {"has_gpu": False},
            "sensors": {"devices": []},
        },
        driver_layer={"providers": [], "note": "status does not open devices"},
        emf_profile={"source_health": {"sensor_entropy": "fallback"}},
        mode="expert",
    )

    assert payload["mode"] == "expert"
    assert any("fallback" in warning.lower() for warning in payload["gate_warnings"])
```

```python
# tests/test_web_hardware_status.py
import apps.web.main as web_main

from tests.test_web_shell import request


def test_workbench_hardware_endpoint_does_not_force_sampling(monkeypatch) -> None:
    sampled: list[str] = []

    class FakeRegistry:
        @classmethod
        def default(cls):
            return cls()

        def list_statuses(self):
            from core.hardware.drivers import HardwareProviderStatus

            return [
                HardwareProviderStatus(
                    provider_id="fake",
                    provider_type="mock",
                    display_name="Fake Provider",
                    available=True,
                    default_timeout_ms=7,
                )
            ]

        def sample(self, *args, **kwargs):
            sampled.append("sampled")
            raise AssertionError("workbench endpoint must not sample providers")

    monkeypatch.setattr(web_main, "HardwareDriverRegistry", FakeRegistry, raising=False)
    web_main.driver_layer_status.cache_clear()
    app = web_main.create_app(runtime_dir=None)
    app.state.hardware_status_builder = lambda: {
        "cpu": {},
        "gpu": {"has_gpu": False},
        "sensors": {"devices": []},
    }

    response = request(app, "GET", "/api/workbench/hardware")

    assert response.status_code == 200
    payload = response.json()
    assert payload["components"][0]["id"] == "cpu"
    assert sampled == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `& ".\.venv\Scripts\python.exe" -m pytest tests/test_web_hardware_truth.py tests/test_web_hardware_status.py -v`

Expected: FAIL because `apps.web.hardware_truth` and the new workbench endpoint do not exist.

- [ ] **Step 3: Implement the truth model and workbench router**

```python
# apps/web/hardware_truth.py
from __future__ import annotations

from typing import Any

from core.realtime.emf_profile import EMFProfileService


def _component(
    component_id: str,
    label: str,
    role: str,
    status: str,
    truth_class: str,
    *,
    used_in_analysis: bool,
    used_in_harmonization: bool,
    notes: list[str],
) -> dict[str, object]:
    return {
        "id": component_id,
        "label": label,
        "role": role,
        "status": status,
        "truth_class": truth_class,
        "used_in_analysis": used_in_analysis,
        "used_in_harmonization": used_in_harmonization,
        "notes": notes,
    }


def build_hardware_truth_snapshot(
    *,
    system_report: dict[str, Any],
    driver_layer: dict[str, Any],
    emf_profile: dict[str, Any],
    mode: str,
) -> dict[str, object]:
    gpu = system_report.get("gpu", {}) or {}
    devices = (system_report.get("sensors", {}) or {}).get("devices", []) or []
    has_external_devices = bool(devices)

    components = [
        _component(
            "cpu",
            "CPU Timing",
            "Analysekontext + Harmonisierungsmodulation",
            "real_active",
            "environment_dependent",
            used_in_analysis=True,
            used_in_harmonization=True,
            notes=["cpu_timer and timing jitter are active in current runtime paths"],
        ),
        _component(
            "gpu",
            "GPU",
            "Status / optionale Entropie",
            "real_available_not_used" if gpu.get("has_gpu") else "software_fallback",
            "mixed",
            used_in_analysis=bool(gpu.get("has_gpu")),
            used_in_harmonization=False,
            notes=["current harmonization worker simulates GPU modulation on CPU"],
        ),
        _component(
            "ram",
            "RAM",
            "Systemlast + Harmonisierungsmodulation",
            "real_active",
            "environment_dependent",
            used_in_analysis=False,
            used_in_harmonization=True,
            notes=["RAM is used as load/context and access-pattern modulation"],
        ),
        _component(
            "driver_layer",
            "Driver Layer",
            "Status / Snapshot / Telemetrie",
            "real_available_not_used",
            "environment_dependent",
            used_in_analysis=False,
            used_in_harmonization=False,
            notes=[str(driver_layer.get("note", ""))],
        ),
        _component(
            "sensor_entropy",
            "HID / serial / TrueRNG",
            "Optionale Entropiequelle",
            "real_available_not_used" if has_external_devices else "software_fallback",
            "stochastic",
            used_in_analysis=has_external_devices,
            used_in_harmonization=False,
            notes=[f"sensor source health: {emf_profile.get('source_health', {}).get('sensor_entropy', 'unknown')}"],
        ),
        _component(
            "websocket",
            "WebSocket",
            "Realtime-Transport",
            "simulation",
            "simulated",
            used_in_analysis=False,
            used_in_harmonization=False,
            notes=["scan-live and EMF websocket endpoints exist, harmonization websocket path is simulated"],
        ),
        _component(
            "quartz",
            "Quartz",
            "keine aktive Integration",
            "not_implemented",
            "simulated",
            used_in_analysis=False,
            used_in_harmonization=False,
            notes=["quartz is hard-coded disabled in the current backend"],
        ),
    ]

    gate_warnings: list[str] = []
    if mode == "expert" and emf_profile.get("source_health", {}).get("sensor_entropy") != "ok":
        gate_warnings.append("Expert mode: sensor entropy is running in fallback/partial mode.")
    if mode == "expert" and any(item["id"] == "websocket" and item["status"] == "simulation" for item in components):
        gate_warnings.append("Expert mode: websocket harmonization is simulated in the current runtime.")

    return {
        "mode": mode,
        "components": components,
        "gate_warnings": gate_warnings,
        "calibration": emf_profile,
    }


def measure_realtime_calibration() -> dict[str, object]:
    return EMFProfileService().measure().to_dict()
```

```python
# apps/web/workbench.py
from __future__ import annotations

from fastapi import APIRouter, Request

from apps.web.hardware_truth import build_hardware_truth_snapshot, measure_realtime_calibration
from apps.web.workbench_registry import build_workbench_registry

router = APIRouter(prefix="/api/workbench", tags=["workbench"])


@router.get("/registry")
def registry() -> dict[str, object]:
    return build_workbench_registry()


@router.get("/hardware")
def hardware(request: Request, mode: str = "standard") -> dict[str, object]:
    system_report = request.app.state.hardware_status_builder()
    driver_layer = request.app.state.driver_layer_status_builder()
    calibration = measure_realtime_calibration()
    return build_hardware_truth_snapshot(
        system_report=system_report,
        driver_layer=driver_layer,
        emf_profile=calibration,
        mode=mode,
    )
```

```python
# apps/web/main.py
from apps.web.workbench import router as workbench_router

app.state.driver_layer_status_builder = driver_layer_status
app.state.hardware_status_builder = hardware_status_payload_builder
app.include_router(workbench_router)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `& ".\.venv\Scripts\python.exe" -m pytest tests/test_web_hardware_truth.py tests/test_web_hardware_status.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/hardware_truth.py apps/web/workbench.py apps/web/main.py tests/test_web_hardware_truth.py tests/test_web_hardware_status.py
git commit -m "feat: add workbench hardware truth api"
```

### Task 3: Runtime-Backed Drafts, Templates, And Run Trace Manifests

**Files:**
- Create: `apps/web/workbench_runtime.py`
- Modify: `apps/web/contracts.py`
- Modify: `apps/web/workbench.py`
- Modify: `apps/web/main.py`
- Modify: `apps/web/launcher.py`
- Test: `tests/test_web_workbench_runtime.py`
- Test: `tests/test_web_contracts.py`

- [ ] **Step 1: Write the failing runtime store tests**

```python
# tests/test_web_workbench_runtime.py
from pathlib import Path

from apps.web.workbench_runtime import WorkbenchRuntimeStore


def test_workbench_runtime_store_roundtrips_draft_template_and_run_trace(tmp_path: Path) -> None:
    store = WorkbenchRuntimeStore(tmp_path)

    store.save_draft({"current_step": "hardware", "form": {"focus": "Bronchien"}})
    draft = store.load_draft()
    assert draft["current_step"] == "hardware"

    template = store.save_template("bronchien-default", {"top_n": 5, "entropy_mode": "hybrid"})
    assert template["template_id"].startswith("tpl-")
    assert store.list_templates()[0]["name"] == "bronchien-default"

    trace = store.register_run_trace(
        run_id="scan-123",
        payload={"workbench_mode": "expert", "focus": "Bronchien"},
    )
    assert trace["run_id"] == "scan-123"
    assert store.get_run_trace("scan-123")["payload"]["workbench_mode"] == "expert"
```

```python
# tests/test_web_contracts.py
def test_workbench_template_request_requires_name() -> None:
    from apps.web.contracts import WorkbenchTemplateRequest

    request = WorkbenchTemplateRequest(name="phase1 expert", payload={"top_n": 5})
    assert request.name == "phase1 expert"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `& ".\.venv\Scripts\python.exe" -m pytest tests/test_web_workbench_runtime.py tests/test_web_contracts.py -v`

Expected: FAIL because `WorkbenchRuntimeStore` and template request models do not exist.

- [ ] **Step 3: Implement the runtime store and router endpoints**

```python
# apps/web/workbench_runtime.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4


class WorkbenchRuntimeStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        return self.root / f"{name}.json"

    def _load(self, name: str, default: dict[str, Any]) -> dict[str, Any]:
        path = self._path(name)
        if not path.exists():
            return json.loads(json.dumps(default))
        return default | json.loads(path.read_text(encoding="utf-8"))

    def _save(self, name: str, payload: dict[str, Any]) -> None:
        self._path(name).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def load_draft(self) -> dict[str, Any]:
        return self._load("draft", {"draft": {}})["draft"]

    def save_draft(self, draft: dict[str, Any]) -> dict[str, Any]:
        payload = {"draft": draft}
        self._save("draft", payload)
        return draft

    def list_templates(self) -> list[dict[str, Any]]:
        return self._load("templates", {"templates": []})["templates"]

    def save_template(self, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        store = self._load("templates", {"templates": []})
        entry = {"template_id": f"tpl-{uuid4().hex[:12]}", "name": name, "payload": payload}
        store["templates"].insert(0, entry)
        self._save("templates", store)
        return entry

    def delete_template(self, template_id: str) -> None:
        store = self._load("templates", {"templates": []})
        store["templates"] = [item for item in store["templates"] if item["template_id"] != template_id]
        self._save("templates", store)

    def register_run_trace(self, *, run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        store = self._load("runs", {"runs": {}})
        entry = {"run_id": run_id, "payload": payload}
        store["runs"][run_id] = entry
        self._save("runs", store)
        return entry

    def update_run_trace(self, run_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        store = self._load("runs", {"runs": {}})
        entry = store["runs"].get(run_id, {"run_id": run_id, "payload": {}})
        entry["payload"].update(patch)
        store["runs"][run_id] = entry
        self._save("runs", store)
        return entry

    def get_run_trace(self, run_id: str) -> dict[str, Any]:
        return self._load("runs", {"runs": {}})["runs"][run_id]
```

```python
# apps/web/contracts.py
class WorkbenchTemplateRequest(BaseModel):
    name: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
```

```python
# apps/web/workbench.py
from apps.web.contracts import WorkbenchTemplateRequest


@router.get("/draft")
def get_draft(request: Request) -> dict[str, Any]:
    return {"draft": request.app.state.workbench_store.load_draft()}


@router.put("/draft")
def put_draft(request: Request, payload: dict[str, Any]) -> dict[str, Any]:
    return {"draft": request.app.state.workbench_store.save_draft(payload)}


@router.get("/templates")
def list_templates(request: Request) -> dict[str, Any]:
    return {"templates": request.app.state.workbench_store.list_templates()}


@router.post("/templates")
def save_template(request: Request, payload: WorkbenchTemplateRequest) -> dict[str, Any]:
    return {"template": request.app.state.workbench_store.save_template(payload.name, payload.payload)}


@router.delete("/templates/{template_id}")
def delete_template(request: Request, template_id: str) -> dict[str, Any]:
    request.app.state.workbench_store.delete_template(template_id)
    return {"deleted": template_id}


@router.get("/run-trace/{run_id}")
def run_trace(request: Request, run_id: str) -> dict[str, Any]:
    return request.app.state.workbench_store.get_run_trace(run_id)
```

```python
# apps/web/main.py
from apps.web.workbench_runtime import WorkbenchRuntimeStore

workbench_root = runtime_path / "workbench" if runtime_path is not None else Path.cwd() / "codex_tmp" / "workbench"
app.state.workbench_store = WorkbenchRuntimeStore(workbench_root)

# inside scan_job_start()
app.state.workbench_store.register_run_trace(
    run_id=launch["job_id"],
    payload={
        "workbench_mode": request.workbench_mode,
        "launcher": launch["launcher"],
        "focus": launch["focus"],
        "profile_template": request.profile_template,
        "entropy_mode": request.entropy_mode,
    },
)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `& ".\.venv\Scripts\python.exe" -m pytest tests/test_web_workbench_runtime.py tests/test_web_contracts.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/workbench_runtime.py apps/web/workbench.py apps/web/contracts.py apps/web/main.py apps/web/launcher.py tests/test_web_workbench_runtime.py tests/test_web_contracts.py
git commit -m "feat: add workbench runtime persistence"
```

### Task 4: Rebuild The Frontend As A 10-Phase Operator Workbench

**Files:**
- Create: `apps/web/static/workbench-state.js`
- Create: `apps/web/static/workbench-api.js`
- Create: `apps/web/static/workbench-render.js`
- Modify: `apps/web/static/index.html`
- Modify: `apps/web/static/app.js`
- Modify: `apps/web/static/app.css`
- Test: `tests/test_web_shell.py`

- [ ] **Step 1: Write the failing shell structure tests**

```python
# tests/test_web_shell.py
def test_web_shell_exposes_10_phase_operator_workbench(tmp_path: Path) -> None:
    app = create_app(runtime_dir=tmp_path)

    response = request(app, "GET", "/")

    assert response.status_code == 200
    assert "Operator Workbench" in response.text
    assert response.text.count('<button class="wizard-step') == 10
    assert "Runtime &amp; Workspace" in response.text
    assert "Hardware &amp; Realtime" in response.text
    assert "Review &amp; Freigabe" in response.text
    assert "Ergebnis-Uebersicht" in response.text
    assert "Technische Details &amp; Nachvollziehbarkeit" in response.text
    assert "Harmonisierung &amp; Export" in response.text
    assert 'id="workbench-mode"' in response.text
    assert 'id="hardware-phase"' in response.text
    assert 'id="review-phase"' in response.text
    assert 'id="details-phase"' in response.text
    assert 'id="finalize-phase"' in response.text


def test_web_shell_static_assets_reference_workbench_modules() -> None:
    html = (ROOT / "apps" / "web" / "static" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "apps" / "web" / "static" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "apps" / "web" / "static" / "app.css").read_text(encoding="utf-8")

    assert "/static/workbench-state.js" in html
    assert "/static/workbench-api.js" in html
    assert "/static/workbench-render.js" in html
    assert "prefers-reduced-motion" in css
    assert "function bootstrapWorkbench" in js
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `& ".\.venv\Scripts\python.exe" -m pytest tests/test_web_shell.py -v`

Expected: FAIL because the current shell still exposes the 8-step Phase-1 wizard and the new module files do not exist.

- [ ] **Step 3: Implement the 10-phase shell and split the frontend modules**

```html
<!-- apps/web/static/index.html -->
<a class="skip-link" href="#main-content">Zum Hauptinhalt springen</a>

<header class="topbar" role="banner">
  <div>
    <p class="eyebrow">Morphic Operator Workbench</p>
    <h1>Morphic Engine V1</h1>
    <p class="topbar-subtitle">Analyse, Hardware-Kontext, Review, Ergebnis, Harmonisierung und Export in einem offiziellen Operator-Flow.</p>
  </div>
  <div class="status-strip" aria-label="Systemstatus Kurzfassung" role="status" aria-live="polite">
    <span id="health-pill" class="pill neutral">Health wird geladen</span>
    <span id="source-pill" class="pill neutral">Quellen werden geladen</span>
    <span id="mode-pill" class="pill neutral">Modus: Standard</span>
  </div>
</header>

<nav class="wizard-stepper" id="wizard-stepper" role="navigation" aria-label="Workbench-Navigation"></nav>

<main id="main-content" class="workspace">
  <section id="runtime-phase" class="panel wizard-panel active" data-step="runtime"></section>
  <section id="client-phase" class="panel wizard-panel" data-step="client"></section>
  <section id="focus-phase" class="panel wizard-panel" data-step="focus"></section>
  <section id="profile-phase" class="panel wizard-panel" data-step="profile"></section>
  <section id="hardware-phase" class="panel wizard-panel" data-step="hardware"></section>
  <section id="review-phase" class="panel wizard-panel" data-step="review"></section>
  <section id="run-phase" class="panel wizard-panel" data-step="run"></section>
  <section id="results-phase" class="panel wizard-panel" data-step="results"></section>
  <section id="details-phase" class="panel wizard-panel" data-step="details"></section>
  <section id="finalize-phase" class="panel wizard-panel" data-step="finalize"></section>
</main>

<script src="/static/workbench-state.js" defer></script>
<script src="/static/workbench-api.js" defer></script>
<script src="/static/workbench-render.js" defer></script>
<script src="/static/app.js" defer></script>
```

```javascript
// apps/web/static/workbench-state.js
window.MorphicWorkbenchState = {
  registry: null,
  currentStepId: "runtime",
  workbenchMode: "standard",
  activeJobId: null,
  activeReportId: null,
  activeHarmonizationJobId: null,
  draft: {},
};
```

```javascript
// apps/web/static/workbench-api.js
window.MorphicWorkbenchApi = {
  async loadRegistry() {
    const response = await fetch("/api/workbench/registry");
    return response.json();
  },
  async loadHardware(mode) {
    const response = await fetch(`/api/workbench/hardware?mode=${encodeURIComponent(mode)}`);
    return response.json();
  },
  async loadDraft() {
    const response = await fetch("/api/workbench/draft");
    return response.json();
  },
  async saveDraft(payload) {
    const response = await fetch("/api/workbench/draft", {
      method: "PUT",
      headers: {"content-type": "application/json"},
      body: JSON.stringify(payload),
    });
    return response.json();
  },
};
```

```javascript
// apps/web/static/app.js
async function bootstrapWorkbench() {
  const registryPayload = await window.MorphicWorkbenchApi.loadRegistry();
  window.MorphicWorkbenchState.registry = registryPayload;
  window.MorphicWorkbenchRender.renderStepper(registryPayload.steps);
  window.MorphicWorkbenchRender.renderShell();
}

window.addEventListener("DOMContentLoaded", () => {
  bootstrapWorkbench();
});
```

```css
/* apps/web/static/app.css */
.skip-link {
  position: absolute;
  left: 16px;
  top: -40px;
  padding: 8px 12px;
  background: #fffdf7;
  color: #263029;
  border: 1px solid #d9d6ca;
}

.skip-link:focus {
  top: 16px;
}

.hardware-card[data-status="simulation"] {
  border-left: 4px solid var(--warn);
}

.hardware-card[data-status="not_implemented"] {
  border-left: 4px solid var(--bad);
}

@media (prefers-reduced-motion: reduce) {
  html {
    scroll-behavior: auto;
  }

  .wizard-panel.active,
  .op-fill {
    animation: none;
    transition: none;
  }
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `& ".\.venv\Scripts\python.exe" -m pytest tests/test_web_shell.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/static/index.html apps/web/static/app.js apps/web/static/app.css apps/web/static/workbench-state.js apps/web/static/workbench-api.js apps/web/static/workbench-render.js tests/test_web_shell.py
git commit -m "feat: rebuild web shell as operator workbench"
```

### Task 5: Review Gate, Result Workspace, And Finalization Wiring

**Files:**
- Modify: `apps/web/main.py`
- Modify: `apps/web/harmonization.py`
- Modify: `apps/web/static/workbench-api.js`
- Modify: `apps/web/static/workbench-render.js`
- Modify: `apps/web/static/app.js`
- Test: `tests/test_web_shell.py`

- [ ] **Step 1: Write the failing review/result/finalization tests**

```python
# tests/test_web_shell.py
def test_web_shell_scan_start_registers_run_trace_mode_and_launcher(tmp_path: Path) -> None:
    jobs = FakeScanJobs()
    app = create_app(runtime_dir=tmp_path, scan_jobs=jobs)

    response = request(
        app,
        "POST",
        "/api/scan/jobs",
        json_body={
            "last_name": "Deisenhofer",
            "first_name": "Klaus",
            "birth_date": "09041966",
            "birth_place": "Augsburg",
            "focus": "Bronchien",
            "consent_local": True,
            "consent_safety": True,
            "workbench_mode": "expert",
        },
    )

    assert response.status_code == 200
    trace = app.state.workbench_store.get_run_trace("job-test")
    assert trace["payload"]["workbench_mode"] == "expert"
    assert "launcher" in trace["payload"]


def test_web_shell_harmonization_start_carries_report_binding(tmp_path: Path) -> None:
    jobs = FakeHarmonizationJobs()
    app = create_app(runtime_dir=tmp_path, harmonization_jobs=jobs)

    response = request(
        app,
        "POST",
        "/api/harmonization/jobs",
        json_body={
            "target_frequency": 432.0,
            "duration_minutes": 5,
            "report_id": "rep-123",
            "workbench_mode": "standard",
        },
    )

    assert response.status_code == 200
    assert jobs.started[0]["hardware_config"]["use_cpu"] is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `& ".\.venv\Scripts\python.exe" -m pytest tests/test_web_shell.py::test_web_shell_scan_start_registers_run_trace_mode_and_launcher tests/test_web_shell.py::test_web_shell_harmonization_start_carries_report_binding -v`

Expected: FAIL because run traces are not seeded and harmonization payloads do not yet carry report binding/workbench mode.

- [ ] **Step 3: Implement review/result/finalization wiring**

```python
# apps/web/main.py inside scan_job_start()
trace = app.state.workbench_store.register_run_trace(
    run_id=launch["job_id"],
    payload={
        "workbench_mode": request.workbench_mode,
        "review": {
            "client": {
                "last_name": request.last_name,
                "first_name": request.first_name,
                "birth_date": request.birth_date,
                "birth_place": request.birth_place,
            },
            "focus": launch["focus"],
            "profile": {
                "profile_template": request.profile_template,
                "entropy_mode": request.entropy_mode,
                "adaptive_limits": request.adaptive_limits,
            },
        },
        "launcher": launch["launcher"],
    },
)
```

```python
# apps/web/harmonization.py
def _snapshot(self, job: object) -> dict[str, object]:
    # existing fields kept
    return {
        # existing snapshot fields,
        "report_id": getattr(job, "report_id", None),
        "workbench_mode": getattr(job, "workbench_mode", "standard"),
    }
```

```javascript
// apps/web/static/workbench-render.js
function renderReviewPanel(state) {
  const panel = document.querySelector("#review-phase");
  panel.innerHTML = `
    <div class="section-title">
      <p class="eyebrow">Phase 6</p>
      <h2>Review & Freigabe</h2>
    </div>
    <div class="review-grid">
      <article class="review-card" id="review-client"></article>
      <article class="review-card" id="review-focus"></article>
      <article class="review-card" id="review-profile"></article>
      <article class="review-card" id="review-hardware"></article>
    </div>
    <div class="action-row">
      <button id="review-refresh-button" class="secondary-button" type="button">Review aktualisieren</button>
      <button id="start-analysis-button" class="primary-button" type="button">Analyse starten</button>
    </div>
  `;
}

function renderResultsWorkspace(resultPayload, tracePayload) {
  const results = document.querySelector("#results-phase");
  const details = document.querySelector("#details-phase");
  const finalize = document.querySelector("#finalize-phase");

  results.innerHTML = `
    <div class="section-title"><p class="eyebrow">Phase 8</p><h2>Ergebnis-Uebersicht</h2></div>
    <div class="metric-grid">
      <div class="metric"><span>Top-Profile</span><strong>${(resultPayload.top_profiles || []).length}</strong></div>
      <div class="metric"><span>Top-Resonanzen</span><strong>${(resultPayload.top_resonances || []).length}</strong></div>
      <div class="metric"><span>Status</span><strong>${resultPayload.status || "-"}</strong></div>
      <div class="metric"><span>Job</span><strong>${resultPayload.job_id || "-"}</strong></div>
    </div>
    <div class="action-row">
      <button class="secondary-button" type="button" id="open-details-button">Technische Details ansehen</button>
      <button class="secondary-button" type="button" id="open-finalize-button">Zu Harmonisierung & Export</button>
    </div>
  `;

  details.innerHTML = `
    <div class="section-title"><p class="eyebrow">Phase 9</p><h2>Technische Details & Nachvollziehbarkeit</h2></div>
    <pre class="command-box scroll-region" tabindex="0">${JSON.stringify(tracePayload, null, 2)}</pre>
  `;

  finalize.innerHTML = `
    <div class="section-title"><p class="eyebrow">Phase 10</p><h2>Harmonisierung & Export</h2></div>
    <div class="action-row">
      <button class="primary-button" type="button" id="harmonization-start-button">Harmonisierung starten</button>
      <button class="secondary-button" type="button" id="save-template-button">Als Template speichern</button>
      <button class="secondary-button" type="button" id="new-case-button">Neuen Fall starten</button>
    </div>
    <pre class="command-box scroll-region" tabindex="0">${JSON.stringify(resultPayload.export_paths || {}, null, 2)}</pre>
  `;
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `& ".\.venv\Scripts\python.exe" -m pytest tests/test_web_shell.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/main.py apps/web/harmonization.py apps/web/static/workbench-api.js apps/web/static/workbench-render.js apps/web/static/app.js tests/test_web_shell.py
git commit -m "feat: wire review gate and result workspace"
```

### Task 6: Separate The Pipeline View And Finish Regression Coverage

**Files:**
- Modify: `apps/web/main.py`
- Modify: `apps/web/static/index.html`
- Modify: `tests/test_web_shell.py`
- Modify: `tests/test_web_reports.py`

- [ ] **Step 1: Write the failing explanatory-surface tests**

```python
# tests/test_web_shell.py
def test_workflow_stepping_is_explanatory_not_primary_operator_flow(tmp_path: Path) -> None:
    app = create_app(runtime_dir=tmp_path)

    response = request(app, "GET", "/workflow-stepping")

    assert response.status_code == 200
    assert "12-Step" in response.text
    assert "Systemfluss" in response.text or "Dokumentationsseite" in response.text


def test_index_links_to_pipeline_view_as_secondary_surface(tmp_path: Path) -> None:
    app = create_app(runtime_dir=tmp_path)

    response = request(app, "GET", "/")

    assert response.status_code == 200
    assert 'href="/workflow-stepping"' in response.text
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `& ".\.venv\Scripts\python.exe" -m pytest tests/test_web_shell.py::test_workflow_stepping_is_explanatory_not_primary_operator_flow tests/test_web_shell.py::test_index_links_to_pipeline_view_as_secondary_surface -v`

Expected: FAIL because the index does not yet link to the pipeline view as a secondary surface and the explanatory positioning text is missing.

- [ ] **Step 3: Reposition the pipeline view and tighten final web-focused coverage**

```python
# apps/web/main.py
@app.get("/workflow-stepping")
def workflow_stepping() -> HTMLResponse:
    """Serviert die separate Pipeline-/Dokumentationsoberflaeche, nicht den primaeren Operator-Flow."""
    if WORKFLOW_STEPPING_HTML.exists():
        content = WORKFLOW_STEPPING_HTML.read_text(encoding="utf-8")
        note = (
            "<section class='pipeline-note' style='padding:16px 24px;border-bottom:1px solid #d9d6ca;background:#f7f4ef;color:#23323a;'>"
            "<strong>Systemfluss.</strong> Diese Seite erklaert die Pipeline und ist nicht die primaere Operator-Oberflaeche. "
            "Die offizielle Arbeitsoberflaeche bleibt die Morphic Operator Workbench unter /."
            "</section>"
        )
        if "<main class=\"main\">" in content:
            content = content.replace("<main class=\"main\">", f"{note}<main class=\"main\">", 1)
        else:
            content = note + content
        return HTMLResponse(content, status_code=200)
    return HTMLResponse("<h1>workflow_stepping.html nicht gefunden</h1>", status_code=404)
```

```html
<!-- apps/web/static/index.html -->
<a class="secondary-button" href="/workflow-stepping">Systemfluss ansehen</a>
```

```python
# tests/test_web_reports.py
from pathlib import Path

from apps.web.reports import ReportCatalog


def test_report_catalog_still_supports_workbench_result_workspace_payloads(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    client_dir = report_root / "Mustermann_Klaus_09041966_Augsburg"
    client_dir.mkdir(parents=True)
    html_file = client_dir / "20260115_101530_multiplex_scan.html"
    html_file.write_text("<html><body><h1>HTML Bericht</h1></body></html>", encoding="utf-8")

    catalog = ReportCatalog([report_root])

    listing = catalog.list(include_all_formats=True)
    session = listing["clients"][0]["sessions"][0]
    entry = session["files"][0]
    preview = catalog.preview(entry["id"])

    assert entry["kind"] == "HTML"
    assert preview["mode"] == "html"
    assert "HTML Bericht" in preview["content"]
```

- [ ] **Step 4: Run the final targeted verification**

Run: `& ".\.venv\Scripts\python.exe" -m pytest tests/test_workbench_registry.py tests/test_web_contracts.py tests/test_web_hardware_truth.py tests/test_web_workbench_runtime.py tests/test_web_shell.py tests/test_web_hardware_status.py tests/test_web_reports.py -v`

Expected: PASS.

Run: `& ".\.venv\Scripts\python.exe" -m apps.cli.main health --strict`

Expected: `Status: OK`

Run: `& ".\.venv\Scripts\python.exe" -m apps.cli.main sources validate`

Expected: registry valid output with non-error exit code.

- [ ] **Step 5: Commit**

```bash
git add apps/web/main.py apps/web/static/index.html tests/test_web_shell.py tests/test_web_reports.py
git commit -m "feat: finalize operator workbench phase 1"
```

## Self-Review

### Spec Coverage

- 10-phase canonical workbench: Tasks 1 and 4
- review gate: Task 5
- runtime-backed resume/templates: Task 3
- result workspace and finalization: Task 5
- separate explanatory pipeline surface: Task 6
- hardware truth model: Task 2
- standard/expert mode: Tasks 1, 2, 5
- run trace manifest: Task 3 and Task 5

No approved first-stage requirement is left without a task.

### Placeholder Scan

The plan intentionally avoids placeholders. Where future work exists, it is explicitly marked as a `planned follow-up stage` and is not required for this first implementation stage.

### Type And Naming Consistency

- Workbench step IDs are consistently:
  - `runtime`, `client`, `focus`, `profile`, `hardware`, `review`, `run`, `results`, `details`, `finalize`
- Workbench mode is consistently:
  - `standard`, `expert`
- Shared backend concepts are consistently named:
  - `WorkbenchRuntimeStore`
  - `build_workbench_registry()`
  - `build_hardware_truth_snapshot()`
  - `run_trace`

## Notes For Execution

- The current repository has unrelated local modifications in `apps/web/static/*` and `tests/test_web_shell.py`; execution should integrate carefully rather than overwrite blindly.
- The global test suite currently shows a separate OpenBLAS-related instability in subprocess-heavy CLI/reporting paths; this plan therefore uses targeted web-focused verification commands as the required success gate for this feature.
