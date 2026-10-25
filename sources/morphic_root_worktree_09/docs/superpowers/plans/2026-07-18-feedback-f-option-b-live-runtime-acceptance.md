# Feedback f Option B Live Runtime Acceptance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a protected Web/API runtime read model and an ASGI transport acceptance test proving the Admin Catalog lifecycle drives explicit Catalog runtime selection after app reload and rollback.

**Architecture:** Extend `apps/web/admin_catalog.py` with `GET /api/admin/catalog/runtime`, reusing existing admin auth, context and service factories. Add `tests/test_web_admin_catalog_runtime_acceptance.py` to drive Draft/Validate/Diff/Publish/Activate/Rollback through real ASGI requests and verify runtime state through the new endpoint.

**Tech Stack:** Python 3.12 via `C:\morphic_v1\.venv\Scripts\python.exe`, FastAPI router functions, Pydantic, existing Admin Catalog service/store/runtime adapter, pytest.

---

### Task 1: Protected Runtime Read Model

**Files:**
- Modify: `apps/web/admin_catalog.py`
- Create: `tests/test_web_admin_catalog_runtime_acceptance.py`

- [x] **Step 1: Write the failing transport test**

Create `tests/test_web_admin_catalog_runtime_acceptance.py` with an ASGI helper, test-local Catalog service factory and a test named
`test_admin_catalog_transport_runtime_acceptance_survives_app_reload_and_rollback`.
The test must:

```python
def test_admin_catalog_transport_runtime_acceptance_survives_app_reload_and_rollback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MORPHIC_ADMIN_CATALOG_ENABLED", "on")
    context = catalog_context("live")
    db_path = tmp_path / "catalog.sqlite3"

    app = app_for_catalog(tmp_path, db_path, context, suffix="one")
    headers = admin_headers(app)
    activate_revision_via_api(app, headers, "draft-a", "revision-a", revision_entries("a"), None, 0, 1)

    reloaded = app_for_catalog(tmp_path, db_path, context, suffix="two")
    runtime = request(reloaded, "GET", "/api/admin/catalog/runtime", headers=admin_headers(reloaded))
    assert runtime.status_code == 200
    assert runtime.json()["selected_source"] == "catalog"
    assert runtime.json()["active_revision_id"] == "revision-a"
    assert runtime.json()["group_ids"] == ["group-a"]

    activate_revision_via_api(reloaded, admin_headers(reloaded), "draft-b", "revision-b", revision_entries("b", stable_managed_ids=True), "revision-a", 1, 2)

    after_second = app_for_catalog(tmp_path, db_path, context, suffix="three")
    second_runtime = request(after_second, "GET", "/api/admin/catalog/runtime", headers=admin_headers(after_second))
    assert second_runtime.json()["active_revision_id"] == "revision-b"
    assert second_runtime.json()["group_ids"] == ["group-b"]
    assert second_runtime.json()["profile_ids"] == ["profile-a"]
    assert second_runtime.json()["remedy_ids"] == ["remedy-a"]
    assert second_runtime.json()["pathogen_ids"] == ["pathogen-a"]
    assert second_runtime.json()["relation_ids"] == ["relation-a"]
    assert second_runtime.json()["multiplex_ids"] == ["multiplex-a"]

    rollback = request(
        after_second,
        "POST",
        "/api/admin/catalog/revisions/revision-a/rollback",
        json_body={
            "expected_previous_revision_id": "revision-b",
            "expected_activation_version": 2,
            "reason": "option b rollback to revision a",
        },
        headers=admin_headers(after_second),
    )
    assert rollback.status_code == 200
    assert rollback.json()["activation_version"] == 3

    after_rollback = app_for_catalog(tmp_path, db_path, context, suffix="four")
    rollback_runtime = request(after_rollback, "GET", "/api/admin/catalog/runtime", headers=admin_headers(after_rollback))
    assert rollback_runtime.json()["active_revision_id"] == "revision-a"
    assert rollback_runtime.json()["group_ids"] == ["group-a"]

    foreign = app_for_catalog(tmp_path, db_path, catalog_context("foreign"), suffix="foreign")
    foreign_runtime = request(foreign, "GET", "/api/admin/catalog/runtime", headers=admin_headers(foreign))
    assert foreign_runtime.status_code == 409
    assert foreign_runtime.json()["detail"]["code"] == "active_revision_missing"

    monkeypatch.setenv("MORPHIC_ADMIN_CATALOG_ENABLED", "off")
    disabled = request(after_rollback, "GET", "/api/admin/catalog/runtime", headers=admin_headers(after_rollback))
    assert disabled.status_code == 200
    assert disabled.json()["selected_source"] == "legacy"
    assert disabled.json()["catalog_enabled"] is False
    assert disabled.json()["active_revision_id"] is None
    assert disabled.json()["group_ids"] == []
```

- [x] **Step 2: Run RED**

Run:

```powershell
$env:PYTHONUTF8="1"
$env:OPENBLAS_NUM_THREADS="1"
$env:TMP=(Resolve-Path -LiteralPath 'codex_tmp').Path
$env:TEMP=(Resolve-Path -LiteralPath 'codex_tmp').Path
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests\test_web_admin_catalog_runtime_acceptance.py -q -p no:cacheprovider --basetemp codex_tmp\pytest-option-b-red
```

Expected: fail because `GET /api/admin/catalog/runtime` is not implemented and returns 404 instead of 200/409.

- [x] **Step 3: Implement the runtime endpoint**

In `apps/web/admin_catalog.py`, import:

```python
from core.admin_catalog.runtime_adapter import (
    CatalogRuntimeConfigError,
    CatalogRuntimeError,
    ConfiguredRuntime,
    load_configured_runtime,
)
```

Add helpers:

```python
def _runtime_error_detail(exc: CatalogRuntimeError) -> dict[str, Any]:
    return {
        "code": exc.code,
        "message": str(exc),
        "active_revision_id": exc.active_revision_id,
    }


def _runtime_mapping(selected: ConfiguredRuntime, context: CatalogContext) -> dict[str, Any]:
    snapshot = selected.catalog_snapshot
    return {
        "context": context.canonical_mapping(),
        "mode": selected.mode,
        "selected_source": selected.selected_source,
        "catalog_enabled": selected.catalog_enabled,
        "active_revision_id": selected.active_revision_id,
        "profile_ids": sorted(profile.name for profile in selected.profiles)
        if snapshot is not None
        else [],
        "group_ids": snapshot.list_groups() if snapshot is not None else [],
        "remedy_ids": sorted(snapshot.remedies) if snapshot is not None else [],
        "pathogen_ids": sorted(snapshot.pathogens) if snapshot is not None else [],
        "relation_ids": sorted(
            relation.entry_id for relation in snapshot.remedy_relations
        )
        if snapshot is not None
        else [],
        "multiplex_ids": sorted(snapshot.multiplexes) if snapshot is not None else [],
    }
```

Add route:

```python
@router.get("/runtime")
def admin_catalog_runtime(request: Request) -> dict[str, Any]:
    service, context = _service_and_context(request)
    try:
        selected = load_configured_runtime(service.store, context)
    except CatalogRuntimeConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_runtime_error_detail(exc),
        ) from exc
    except CatalogRuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_runtime_error_detail(exc),
        ) from exc
    return _runtime_mapping(selected, context)
```

- [x] **Step 4: Run GREEN**

Run the same pytest command with `--basetemp codex_tmp\pytest-option-b-green`.
Expected: `passed`.

### Task 2: Fail-Closed Endpoint Boundaries

**Files:**
- Modify: `tests/test_web_admin_catalog_runtime_acceptance.py`

- [x] **Step 1: Add boundary tests**

Add tests:

```python
def test_admin_catalog_runtime_endpoint_requires_admin_security(tmp_path: Path) -> None:
    context = catalog_context("security")
    db_path = tmp_path / "catalog.sqlite3"
    app = app_for_catalog(tmp_path, db_path, context, suffix="security")

    response = request(app, "GET", "/api/admin/catalog/runtime")

    assert response.status_code == 503
    assert response.json()["detail"] == "admin security not configured"


def test_admin_catalog_runtime_endpoint_rejects_invalid_switch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MORPHIC_ADMIN_CATALOG_ENABLED", "invalid")
    context = catalog_context("invalid")
    db_path = tmp_path / "catalog.sqlite3"
    app = app_for_catalog(tmp_path, db_path, context, suffix="invalid")

    response = request(app, "GET", "/api/admin/catalog/runtime", headers=admin_headers(app))

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "invalid_catalog_enabled_value"
```

- [x] **Step 2: Run boundary tests**

Run:

```powershell
$env:PYTHONUTF8="1"
$env:OPENBLAS_NUM_THREADS="1"
$env:TMP=(Resolve-Path -LiteralPath 'codex_tmp').Path
$env:TEMP=(Resolve-Path -LiteralPath 'codex_tmp').Path
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests\test_web_admin_catalog_runtime_acceptance.py -q -p no:cacheprovider --basetemp codex_tmp\pytest-option-b-boundaries
```

Expected: all tests in the file pass.

### Task 3: Status And Verification

**Files:**
- Create: `docs/status/2026-07-18-feedback-f-option-b-live-runtime-acceptance.md`
- Modify: `docs/2026-07-17-aktueller-umsetzungsplan-fortschritt.md`
- Modify: `docs/status/2026-07-17-umsetzungsplan-status-tiefenanalyse.md`

- [x] **Step 1: Run focused regression**

Run:

```powershell
$env:PYTHONUTF8="1"
$env:OPENBLAS_NUM_THREADS="1"
$env:TMP=(Resolve-Path -LiteralPath 'codex_tmp').Path
$env:TEMP=(Resolve-Path -LiteralPath 'codex_tmp').Path
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests\test_web_admin_catalog_runtime_acceptance.py tests\test_web_admin_catalog.py tests\test_admin_catalog_runtime_acceptance.py tests\test_admin_catalog_runtime_consumption.py tests\test_admin_catalog_shadow_comparison.py -q -p no:cacheprovider --basetemp codex_tmp\pytest-option-b-final
```

Expected: all selected tests pass.

- [x] **Step 2: Run static checks**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m py_compile apps\web\admin_catalog.py tests\test_web_admin_catalog_runtime_acceptance.py
git diff --check
rg -n "[ \t]+$" apps\web\admin_catalog.py tests\test_web_admin_catalog_runtime_acceptance.py docs\status\2026-07-18-feedback-f-option-b-live-runtime-acceptance.md docs\2026-07-17-aktueller-umsetzungsplan-fortschritt.md docs\status\2026-07-17-umsetzungsplan-status-tiefenanalyse.md
rg -n "^(<<<<<<<|=======|>>>>>>>)" apps\web\admin_catalog.py tests\test_web_admin_catalog_runtime_acceptance.py docs\status\2026-07-18-feedback-f-option-b-live-runtime-acceptance.md docs\2026-07-17-aktueller-umsetzungsplan-fortschritt.md docs\status\2026-07-17-umsetzungsplan-status-tiefenanalyse.md
```

Expected: `py_compile` and `git diff --check` exit 0; ripgrep scans return no matches. Existing LF/CRLF warnings from dirty tracked files are acceptable.

- [x] **Step 3: Update docs**

Create the Option-B status record with exact pass counts, endpoint contract,
remaining no-product-default boundary and note that no commit/staging/push was
performed. Update both rollups so Option B is technically closed as an API/ASGI
transport gate and the next optional step is a browser-smoke, not a product GO.
