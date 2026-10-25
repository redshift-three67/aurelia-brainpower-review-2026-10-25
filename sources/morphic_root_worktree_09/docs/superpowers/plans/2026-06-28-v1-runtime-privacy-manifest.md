# V1 Runtime Privacy Manifest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local runtime privacy manifest with pseudonymous clients, sessions, artifacts, append-only audit, and gated erasure cascade.

**Architecture:** Keep scan engines and export paths unchanged. Add a small JSON-backed service under `core/compliance/runtime_manifest.py`, expose it via a new `privacy` CLI app, and let report/export code register produced artifacts after successful writes.

**Tech Stack:** Python stdlib JSON/Path/hashlib/uuid, Typer CLI, pytest.

---

## File Structure

| File | Responsibility |
|---|---|
| `core/compliance/runtime_manifest.py` | Runtime JSON stores, pseudonym IDs, safe client projection, audit append, erasure manifest and gated delete. |
| `apps/cli/commands/privacy.py` | CLI for safe client list, erasure manifest, gated delete and client audit. |
| `apps/cli/main.py` | Register `privacy` Typer app. |
| `tools/reporting_common.py` | Helper to register report artifacts from standalone report tools. |
| `tools/synergy_consolidator.py` | Register `synergy_gesamt.json/html` artifacts. |
| `tools/remedy_reporter.py` | Register remedy JSON/HTML artifacts. |
| `tools/trend_analyzer.py` | Register trend notice or trend JSON/HTML artifacts. |
| `tools/interpretation_generator.py` | Register interpretation HTML artifacts. |
| `apps/cli/commands/field.py` | Register scan JSON/HTML/TXT artifacts after successful export writes. |
| `apps/cli/commands/scan.py` | Register simple `scan analyze` JSON/HTML artifacts after successful export writes. |
| `tests/test_runtime_privacy_manifest.py` | Unit tests for pseudonym, safe view, artifact manifest, audit and erasure. |
| `tests/test_privacy_cli.py` | CLI tests for list/manifest/delete/audit. |
| `tests/test_report_manifest_registration.py` | Integration tests that report tools register artifacts. |

---

## Implementation Notes

- Runtime root defaults to `data/runtime`.
- Tests set `MORPHIC_RUNTIME_DIR` to a temp directory.
- Gate token defaults to `MORPHIC_ERASURE_ACKNOWLEDGED` and can be overridden with `MORPHIC_ERASURE_GATE_TOKEN`.
- Safe client views must not expose `first_name`, `last_name`, `birth_date` or `birth_place`.
- Deletion removes JSON-store entries and registered files only. It does not scan arbitrary folders.
- If a report tool cannot register an artifact, report generation must not fail; registration is best-effort for compatibility.

---

### Task 1: Runtime Manifest Service Tests

**Files:**
- Create: `tests/test_runtime_privacy_manifest.py`
- Create later: `core/compliance/runtime_manifest.py`

- [ ] **Step 1: Write the failing tests**

```python
from pathlib import Path

import pytest

from core.compliance.runtime_manifest import (
    DEFAULT_ERASURE_GATE_TOKEN,
    RuntimeManifestService,
)


def test_register_client_safe_view_strips_pii(tmp_path: Path) -> None:
    service = RuntimeManifestService(tmp_path)
    client = service.get_or_create_client(
        {
            "first_name": "Klaus",
            "last_name": "Mustermann",
            "birth_date": "09041966",
            "birth_place": "Augsburg",
        }
    )

    safe = service.list_clients_safe()

    assert client["client_id"].startswith("cli-")
    assert safe == [{"client_id": client["client_id"], "created_at": client["created_at"], "updated_at": client["updated_at"]}]
    assert "Klaus" not in str(safe)
    assert "Mustermann" not in str(safe)


def test_register_artifact_creates_session_artifact_and_audit(tmp_path: Path) -> None:
    service = RuntimeManifestService(tmp_path)
    artifact_file = tmp_path / "reports" / "bericht.html"
    artifact_file.parent.mkdir()
    artifact_file.write_text("report", encoding="utf-8")

    artifact = service.register_artifact(
        {"first_name": "Klaus", "last_name": "Mustermann", "birth_date": "09041966", "birth_place": "Augsburg"},
        artifact_type="html",
        path=artifact_file,
        label="Deutung",
        session_id="sess-test",
        focus="Bronchien",
        config={"command": "interpretation"},
    )

    assert artifact["artifact_id"].startswith("art-")
    assert service.load_store("artifacts")["artifacts"][0]["path"] == str(artifact_file)
    assert service.load_store("sessions")["sessions"][0]["session_id"] == "sess-test"
    assert any(e["action"] == "artifact_register" for e in service.load_store("audit_log")["entries"])


def test_erasure_manifest_is_non_destructive_and_execute_is_gated(tmp_path: Path) -> None:
    service = RuntimeManifestService(tmp_path)
    artifact_file = tmp_path / "reports" / "bericht.html"
    artifact_file.parent.mkdir()
    artifact_file.write_text("report", encoding="utf-8")
    artifact = service.register_artifact(
        {"first_name": "Klaus", "last_name": "Mustermann", "birth_date": "09041966", "birth_place": "Augsburg"},
        artifact_type="html",
        path=artifact_file,
        label="Deutung",
        session_id="sess-test",
    )
    client_id = artifact["client_id"]

    manifest = service.erasure_manifest(client_id)

    assert manifest["client_entry_present"] is True
    assert manifest["gated"] is True
    assert manifest["artifacts"][0]["path"] == str(artifact_file)
    assert artifact_file.exists()

    with pytest.raises(ValueError, match="Gate"):
        service.execute_erasure(client_id, gate_token="WRONG")

    result = service.execute_erasure(client_id, gate_token=DEFAULT_ERASURE_GATE_TOKEN)

    assert result["outcome"] == "ok"
    assert result["removed_clients"] == 1
    assert result["removed_sessions"] == 1
    assert result["removed_artifacts"] == 1
    assert result["removed_files"] == 1
    assert not artifact_file.exists()
    assert service.list_clients_safe() == []
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_runtime_privacy_manifest.py -q
```

Expected: import failure for `core.compliance.runtime_manifest`.

---

### Task 2: Implement Runtime Manifest Service

**Files:**
- Create: `core/compliance/runtime_manifest.py`

- [ ] **Step 1: Implement JSON-backed service**

Create `core/compliance/runtime_manifest.py` with:

- `DEFAULT_ERASURE_GATE_TOKEN = "MORPHIC_ERASURE_ACKNOWLEDGED"`
- `runtime_root()` reading `MORPHIC_RUNTIME_DIR`
- `RuntimeManifestService`
- `get_or_create_client()`
- `list_clients_safe()`
- `create_session()`
- `register_artifact()`
- `append_audit()`
- `erasure_manifest()`
- `execute_erasure()`

- [ ] **Step 2: Run service tests**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_runtime_privacy_manifest.py -q
```

Expected: `3 passed`.

---

### Task 3: Privacy CLI Tests And Commands

**Files:**
- Create: `tests/test_privacy_cli.py`
- Create: `apps/cli/commands/privacy.py`
- Modify: `apps/cli/main.py`

- [ ] **Step 1: Write failing CLI tests**

Test that:

- `privacy clients --runtime <tmp> --json` returns safe clients without PII.
- `privacy erasure-manifest <client_id> --runtime <tmp>` returns manifest JSON.
- `privacy erase <client_id> --runtime <tmp> --gate-token MORPHIC_ERASURE_ACKNOWLEDGED` deletes registered file.
- `privacy audit <client_id> --runtime <tmp> --json` returns audit entries.

- [ ] **Step 2: Implement CLI**

Add Typer commands:

- `clients`
- `erasure-manifest`
- `erase`
- `audit`

Register with `app.add_typer(privacy_app, name="privacy")`.

- [ ] **Step 3: Run CLI tests**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_privacy_cli.py -q
```

Expected: CLI tests pass.

---

### Task 4: Report Artifact Registration

**Files:**
- Create: `tests/test_report_manifest_registration.py`
- Modify: `tools/reporting_common.py`
- Modify: `tools/interpretation_generator.py`
- Modify: `tools/synergy_consolidator.py`
- Modify: `tools/remedy_reporter.py`
- Modify: `tools/trend_analyzer.py`
- Modify: `apps/cli/commands/field.py`
- Modify: `apps/cli/commands/scan.py`

- [ ] **Step 1: Write failing integration tests**

Test at minimum:

- `tools.interpretation_generator` with `MORPHIC_RUNTIME_DIR=<tmp/runtime>` writes an artifact manifest entry for its HTML report.
- `tools.synergy_consolidator` registers `synergy_gesamt.html` and `synergy_gesamt.json`.
- Reduced `scan top3-scan` registers at least one `multiplex_scan` artifact.

- [ ] **Step 2: Implement best-effort registration helper**

Add to `tools/reporting_common.py`:

- `client_info(last_name, first_name, birth_date, birth_place)`
- `register_report_artifacts(paths, client, artifact_type, label, session_id="", focus="", config=None)`

The helper catches registration exceptions and returns an empty list on failure.

- [ ] **Step 3: Wire report tools and scan exports**

After successful file writes, call `register_report_artifacts()` or `RuntimeManifestService.register_artifact()`.

- [ ] **Step 4: Run registration tests**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_report_manifest_registration.py -q
```

Expected: registration tests pass.

---

### Task 5: Verification

- [ ] **Step 1: Run focused compliance tests**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_runtime_privacy_manifest.py tests\test_privacy_cli.py tests\test_report_manifest_registration.py tests\test_top5_workflow_smoke.py -q
```

Expected: all selected tests pass.

- [ ] **Step 2: Run full suite**

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Expected: full suite passes.

- [ ] **Step 3: Run health and source validation**

```powershell
.\.venv\Scripts\python.exe -m apps.cli.main health
.\.venv\Scripts\python.exe -m apps.cli.main sources validate
```

Expected: health status OK, source registry valid.

---

## Self-Review

| Check | Ergebnis |
|---|---|
| Spec coverage | Deckt Pseudonym-Safe-View, Artifact-Manifest, Audit, Erasure Manifest und gated Delete ab. |
| Placeholder scan | Keine `TODO`-/`TBD`-Marker. |
| Scope | Keine UI-Implementierung und keine Kernengine-Aenderung in diesem Schnitt. |
