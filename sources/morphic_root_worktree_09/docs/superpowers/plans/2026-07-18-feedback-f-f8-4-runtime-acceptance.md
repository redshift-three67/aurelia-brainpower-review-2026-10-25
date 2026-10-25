# Feedback f F8.4 Runtime Acceptance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an isolated F8.4 acceptance gate proving the Admin Catalog lifecycle can drive explicit Catalog runtime selection through activation, reload, rollback, isolation and kill-switch boundaries.

**Architecture:** Add a small reusable acceptance harness in `core/admin_catalog/runtime_acceptance.py` that orchestrates existing `AdminCatalogService`, `CatalogStore`, and `runtime_adapter` APIs. Add focused pytest coverage in `tests/test_admin_catalog_runtime_acceptance.py`. Update status docs after verification only.

**Tech Stack:** Python 3.12 via `C:\morphic_v1\.venv\Scripts\python.exe`, stdlib dataclasses, existing Admin Catalog modules, pytest.

---

### Task 1: F8.4 Acceptance Harness

**Files:**
- Create: `core/admin_catalog/runtime_acceptance.py`
- Create: `tests/test_admin_catalog_runtime_acceptance.py`

- [x] **Step 1: Write the failing test**

Create `tests/test_admin_catalog_runtime_acceptance.py` with a test that imports
`run_synthetic_runtime_acceptance()` from `core.admin_catalog.runtime_acceptance`,
builds two valid synthetic Catalog revisions, and asserts:

```python
evidence = run_synthetic_runtime_acceptance(service, context, revision_one, revision_two)
assert evidence.status == "passed"
assert evidence.activation_versions == (1, 2, 3)
assert evidence.revision_after_reload == "revision-a"
assert evidence.revision_after_second_activation == "revision-b"
assert evidence.revision_after_rollback == "revision-a"
assert evidence.group_ids_after_reload == ("group-a",)
assert evidence.group_ids_after_second_activation == ("group-b",)
assert evidence.group_ids_after_rollback == ("group-a",)
assert evidence.foreign_context_error_code == "active_revision_missing"
assert evidence.kill_switch_disabled_selected_source == "legacy"
assert evidence.audit_chain_valid is True
assert evidence.redacted is True
```

- [x] **Step 2: Run RED**

Run:

```powershell
$env:PYTHONUTF8="1"
$env:OPENBLAS_NUM_THREADS="1"
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests\test_admin_catalog_runtime_acceptance.py -q -p no:cacheprovider
```

Expected: fail with `ModuleNotFoundError: No module named 'core.admin_catalog.runtime_acceptance'`.

- [x] **Step 3: Implement the minimal harness**

Create an immutable evidence dataclass and the function:

```python
@dataclass(frozen=True, slots=True)
class RuntimeAcceptanceEvidence:
    status: str
    activation_versions: tuple[int, int, int]
    revision_after_reload: str
    revision_after_second_activation: str
    revision_after_rollback: str
    group_ids_after_reload: tuple[str, ...]
    group_ids_after_second_activation: tuple[str, ...]
    group_ids_after_rollback: tuple[str, ...]
    foreign_context_error_code: str
    kill_switch_disabled_selected_source: str
    audit_chain_valid: bool
    redacted: bool
```

`run_synthetic_runtime_acceptance()` must use existing service methods for
create/validate/diff/publish/activate/rollback and existing runtime adapter
functions for runtime selection.

- [x] **Step 4: Run GREEN**

Run the same pytest command. Expected: `passed`.

- [x] **Step 5: Run focused regression**

Run:

```powershell
$env:PYTHONUTF8="1"
$env:OPENBLAS_NUM_THREADS="1"
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests\test_admin_catalog_runtime_acceptance.py tests\test_admin_catalog_runtime_consumption.py tests\test_web_admin_catalog.py -q -p no:cacheprovider
```

Expected: all selected tests pass.

### Task 2: F8.4 Status Evidence

**Files:**
- Create: `docs/status/2026-07-18-feedback-f-F8-4-runtime-acceptance.md`
- Modify: `docs/2026-07-17-aktueller-umsetzungsplan-fortschritt.md`
- Modify: `docs/status/2026-07-17-umsetzungsplan-status-tiefenanalyse.md`

- [x] **Step 1: Write the status record**

Document the exact F8.4 scope, implemented artifacts, contracts, verification
commands, pass counts and remaining Option-B boundary.

- [x] **Step 2: Update rollups**

Change F8 from `3/4` to `4/4`, Feedback f from `97 %` to technically closed
for Option A, and keep Option B as the next live/browser acceptance target.

- [x] **Step 3: Verify docs and static checks**

Run:

```powershell
git diff --check
& C:\morphic_v1\.venv\Scripts\python.exe -m py_compile core\admin_catalog\runtime_acceptance.py tests\test_admin_catalog_runtime_acceptance.py
```

Expected: exit 0; only known LF/CRLF warnings may appear from existing dirty files.

### Task 3: Final Verification

**Files:**
- No additional files unless a verification gap is found.

- [x] **Step 1: Run final focused acceptance matrix**

Run:

```powershell
$env:PYTHONUTF8="1"
$env:OPENBLAS_NUM_THREADS="1"
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests\test_admin_catalog_runtime_acceptance.py tests\test_admin_catalog_runtime_consumption.py tests\test_web_admin_catalog.py tests\test_admin_catalog_shadow_comparison.py -q -p no:cacheprovider
```

- [x] **Step 2: Report exact state**

Report modified/untracked counts, test commands, pass counts, open Option-B
work, and state clearly that no commit/staging/push was performed.
