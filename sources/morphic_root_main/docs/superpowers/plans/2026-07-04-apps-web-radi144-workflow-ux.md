# Apps Web Radi144 Workflow UX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the Morphic V1 web workflow into a Radi144-nearer 10-step experience with real image-reference upload, explicit local PII draft storage, and preserved Phase-1 CLI handoff.

**Architecture:** Keep the current FastAPI + static HTML/CSS/JS architecture. Add one narrow upload/staging endpoint that writes image references under the runtime job area and returns an `image_path` consumed by the existing `Phase1ScanRequest` contract. Keep PII persistence entirely browser-local, opt-in only, and make the UI migration incremental so existing API and CLI behavior remains testable.

**Tech Stack:** FastAPI, Pydantic, Vanilla HTML/CSS/JS, pytest, local browser verification.

---

## File Map

- Modify: `apps/web/main.py`
  - Add `/api/uploads/image-reference` endpoint.
  - Store uploaded image files under `runtime_dir/web_uploads` or `codex_tmp/web-uploads`.
  - Return `image_path`, `file_name`, `size`, and `content_type`.
  - Parse the single-file multipart body narrowly in-app to avoid adding a new `python-multipart` dependency.
- Modify: `apps/web/static/index.html`
  - Replace the 8-step shell with a 10-step Radi144-nearer shell.
  - Preserve `scan-form`, existing scan field names, `preview-button`, `start-analysis-button`, reports and harmonization IDs where possible.
  - Add `image-upload`, `image-upload-state`, `image-upload-meta`, `client-storage-opt-in`, and `client-storage-clear`.
- Modify: `apps/web/static/app.js`
  - Update `WORKFLOW_STEPS` to 10 entries.
  - Update validation for new step indexes.
  - Add image-upload handler that posts to `/api/uploads/image-reference` and writes the returned path to `image_path`.
  - Add opt-in local draft storage using key `morphic_v1_client_draft`.
  - Add result-matrix rendering through existing `/api/scan/jobs/{job_id}/results`.
- Modify: `apps/web/static/app.css`
  - Add Radi144-nearer stepper, card, step header, radio-card, toggle-card, upload, matrix, and mobile styles.
  - Keep existing report/harmonization readability rules.
- Modify: `tests/test_web_shell.py`
  - Update shell structure assertions from 8 to 10 steps.
  - Add upload endpoint tests.
  - Add static JS/CSS assertions for local storage opt-in, upload handler, 10-step validation, and no hidden PII autosave.

## Execution Notes

- Do not stage unrelated dirty files unless the current task intentionally modifies them.
- Keep existing field names stable: `last_name`, `first_name`, `birth_date`, `birth_place`, `focus`, `profile_level`, `top_n`, `profile_template`, `entropy_mode`, `image_path`, `adaptive_limits`.
- Do not add external frontend dependencies or remote fonts.
- Preserve the CLI assertion that `--image` receives the final staged `image_path`.
- Prefer narrow commits after each task.

---

### Task 1: Add Web Shell Tests for the 10-Step Contract

**Files:**
- Modify: `tests/test_web_shell.py`

- [ ] **Step 1: Update the first-screen expectations**

Replace the UI labels in `test_web_shell_serves_phase1_client_facing_first_screen` so it asserts the new workflow language:

```python
assert "Morphic Engine V1" in response.text
assert "Radi144-naher Klienten-Workflow" in response.text
assert "Klienten-Daten" in response.text
assert "EMF-/Umfeld-Analyseprofil" in response.text
assert "Zusammenfassung &amp; Start" in response.text
assert "/static/app.css" in response.text
assert "/static/app.js" in response.text
```

- [ ] **Step 2: Update the guided workflow structure test**

In `test_web_shell_exposes_guided_workflow_stepping`, replace the 8-step assertions with the 10-step contract:

```python
assert response.text.count('<button class="wizard-step') == 10
assert 'data-step="9"' in response.text
assert 'id="system" class="panel wizard-panel active" data-step="0"' in response.text
assert 'id="consent" class="panel wizard-panel" data-step="1"' in response.text
assert 'id="client" class="panel wizard-panel" data-step="2"' in response.text
assert 'id="focus" class="panel wizard-panel" data-step="3"' in response.text
assert 'id="analysis-config" class="panel wizard-panel" data-step="4"' in response.text
assert 'id="environment-profile" class="panel wizard-panel" data-step="5"' in response.text
assert 'id="preview" class="panel wizard-panel" data-step="6"' in response.text
assert 'id="result-matrix" class="panel wizard-panel result-matrix-panel" data-step="7"' in response.text
assert 'id="reports" class="panel wizard-panel reports-panel" data-step="8"' in response.text
assert 'id="harmonization" class="panel wizard-panel harmonization-panel" data-step="9"' in response.text
assert "Willkommen &amp; Systemstatus" in response.text
assert "Hinweise &amp; Einwilligung" in response.text
assert "Analyse-Konfiguration" in response.text
assert "Harmonisierung, Export &amp; Abschluss" in response.text
```

- [ ] **Step 3: Add upload and local-storage DOM assertions**

Add these assertions to the same test:

```python
assert 'id="image-upload"' in response.text
assert 'id="image-upload-state"' in response.text
assert 'id="image-upload-meta"' in response.text
assert 'name="image_path"' in response.text
assert 'id="client-storage-opt-in"' in response.text
assert 'id="client-storage-clear"' in response.text
assert 'data-pii-storage="opt-in"' in response.text
```

- [ ] **Step 4: Update static asset assertions**

In `test_web_shell_static_assets_define_wizard_behavior`, add:

```python
assert '{label: "Willkommen & Systemstatus"}' in js
assert '{label: "Harmonisierung, Export & Abschluss"}' in js
assert "function uploadImageReference" in js
assert '"/api/uploads/image-reference"' in js
assert "function saveClientDraftIfEnabled" in js
assert "function restoreClientDraft" in js
assert "function clearClientDraft" in js
assert 'const CLIENT_DRAFT_KEY = "morphic_v1_client_draft";' in js
assert "client-storage-opt-in" in js
assert "localStorage.setItem(CLIENT_DRAFT_KEY" in js
assert "function loadResultMatrix" in js
assert '"/api/scan/jobs/"' in js
assert "if (currentStep === 8)" in js
assert "goToStep(8);" in js
assert ".step-card" in css
assert ".radio-card-grid" in css
assert ".upload-card" in css
assert ".result-matrix-panel" in css
assert ".workflow-shell" in css
```

- [ ] **Step 5: Run the targeted tests and verify they fail**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_web_shell.py::test_web_shell_serves_phase1_client_facing_first_screen tests\test_web_shell.py::test_web_shell_exposes_guided_workflow_stepping tests\test_web_shell.py::test_web_shell_static_assets_define_wizard_behavior -q
```

Expected: FAIL because the app still exposes 8 steps and no upload/local-storage UI.

- [ ] **Step 6: Commit the failing contract tests**

```powershell
git add tests\test_web_shell.py
git commit -m "test: define radi144 web workflow contract"
```

---

### Task 2: Add Narrow Image Upload/Staging Endpoint

**Files:**
- Modify: `apps/web/main.py`
- Modify: `tests/test_web_shell.py`

- [ ] **Step 1: Add upload endpoint test**

Add this test near the scan preview tests:

```python
def test_web_shell_uploads_image_reference_to_runtime_staging(tmp_path: Path) -> None:
    app = create_app(runtime_dir=tmp_path)
    boundary = "----morphic-boundary"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="file"; filename="client.png"\r\n'
        "Content-Type: image/png\r\n"
        "\r\n"
    ).encode("utf-8") + b"\x89PNG\r\n\x1a\nfake-image" + (
        f"\r\n--{boundary}--\r\n"
    ).encode("utf-8")
    headers = [
        (b"host", b"testserver"),
        (b"content-type", f"multipart/form-data; boundary={boundary}".encode("ascii")),
        (b"content-length", str(len(body)).encode("ascii")),
    ]

    async def run() -> AsgiResponse:
        sent = False
        events: list[dict[str, Any]] = []

        async def receive() -> dict[str, Any]:
            nonlocal sent
            if sent:
                return {"type": "http.disconnect"}
            sent = True
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message: dict[str, Any]) -> None:
            events.append(message)

        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "POST",
            "path": "/api/uploads/image-reference",
            "raw_path": b"/api/uploads/image-reference",
            "query_string": b"",
            "headers": headers,
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
            "scheme": "http",
        }
        await app(scope, receive, send)
        status = next(event["status"] for event in events if event["type"] == "http.response.start")
        response_body = b"".join(event.get("body", b"") for event in events if event["type"] == "http.response.body")
        return AsgiResponse(status, response_body)

    response = asyncio.run(run())
    payload = response.json()

    assert response.status_code == 200
    assert payload["file_name"] == "client.png"
    assert payload["content_type"] == "image/png"
    assert payload["size"] > 0
    assert payload["image_path"].endswith("client.png")
    assert Path(payload["image_path"]).is_file()
    assert str(tmp_path / "web_uploads") in payload["image_path"]
```

- [ ] **Step 2: Add invalid upload test**

```python
def test_web_shell_rejects_non_image_reference_upload(tmp_path: Path) -> None:
    app = create_app(runtime_dir=tmp_path)
    boundary = "----morphic-boundary"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="file"; filename="client.exe"\r\n'
        "Content-Type: application/octet-stream\r\n"
        "\r\n"
        "not an image"
        f"\r\n--{boundary}--\r\n"
    ).encode("utf-8")
    headers = [
        (b"host", b"testserver"),
        (b"content-type", f"multipart/form-data; boundary={boundary}".encode("ascii")),
        (b"content-length", str(len(body)).encode("ascii")),
    ]

    async def run() -> AsgiResponse:
        sent = False
        events: list[dict[str, Any]] = []

        async def receive() -> dict[str, Any]:
            nonlocal sent
            if sent:
                return {"type": "http.disconnect"}
            sent = True
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message: dict[str, Any]) -> None:
            events.append(message)

        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "POST",
            "path": "/api/uploads/image-reference",
            "raw_path": b"/api/uploads/image-reference",
            "query_string": b"",
            "headers": headers,
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
            "scheme": "http",
        }
        await app(scope, receive, send)
        status = next(event["status"] for event in events if event["type"] == "http.response.start")
        response_body = b"".join(event.get("body", b"") for event in events if event["type"] == "http.response.body")
        return AsgiResponse(status, response_body)

    response = asyncio.run(run())

    assert response.status_code == 400
    assert "unsupported image reference" in response.text
```

- [ ] **Step 3: Run upload tests and verify they fail**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_web_shell.py::test_web_shell_uploads_image_reference_to_runtime_staging tests\test_web_shell.py::test_web_shell_rejects_non_image_reference_upload -q
```

Expected: FAIL with 404 or missing endpoint.

- [ ] **Step 4: Add parser imports**

At the top of `apps/web/main.py`, add:

```python
import re
```

Keep the existing FastAPI import unchanged:

```python
from fastapi import Depends, FastAPI, HTTPException, Request
```

- [ ] **Step 5: Add upload helpers near `DEFAULT_REPORT_ROOTS`**

Add:

```python
ALLOWED_IMAGE_UPLOAD_SUFFIXES = {".png", ".jpg", ".jpeg"}
ALLOWED_IMAGE_UPLOAD_TYPES = {"image/png", "image/jpeg"}
MAX_IMAGE_UPLOAD_BYTES = 10 * 1024 * 1024
MULTIPART_FILENAME_RE = re.compile(r'filename="([^"]*)"')
MULTIPART_CONTENT_TYPE_RE = re.compile(r"content-type:\s*([^\r\n;]+)", re.IGNORECASE)


def _upload_root(runtime_path: Path | None) -> Path:
    if runtime_path is not None:
        return runtime_path / "web_uploads"
    return Path.cwd() / "codex_tmp" / "web-uploads"


def _safe_upload_name(file_name: str) -> str:
    raw_name = Path(file_name or "image-reference").name
    cleaned = "".join(
        char if char.isalnum() or char in {".", "-", "_"} else "_"
        for char in raw_name
    ).strip("._")
    return cleaned or "image-reference"


def _multipart_boundary(content_type: str) -> bytes:
    marker = "boundary="
    if marker not in content_type:
        raise HTTPException(status_code=400, detail="multipart boundary missing")
    boundary = content_type.split(marker, 1)[1].strip().strip('"')
    if not boundary:
        raise HTTPException(status_code=400, detail="multipart boundary missing")
    return boundary.encode("utf-8")


def _parse_single_file_upload(body: bytes, content_type: str) -> tuple[str, str, bytes]:
    boundary = _multipart_boundary(content_type)
    delimiter = b"--" + boundary
    for raw_part in body.split(delimiter):
        if b"Content-Disposition" not in raw_part:
            continue
        headers, separator, data = raw_part.partition(b"\r\n\r\n")
        if not separator:
            continue
        header_text = headers.decode("utf-8", errors="replace")
        if 'name="file"' not in header_text:
            continue
        filename_match = MULTIPART_FILENAME_RE.search(header_text)
        content_type_match = MULTIPART_CONTENT_TYPE_RE.search(header_text)
        filename = filename_match.group(1) if filename_match else "image-reference"
        upload_type = (
            content_type_match.group(1).strip().lower()
            if content_type_match
            else "application/octet-stream"
        )
        return filename, upload_type, data.rstrip(b"\r\n")
    raise HTTPException(status_code=400, detail="image reference file missing")
```

- [ ] **Step 6: Add endpoint inside `create_app` before scan endpoints**

Add this route after `/api/reports/{report_id}/file`:

```python
    @app.post("/api/uploads/image-reference")
    async def upload_image_reference(
        request: Request,
        _api_key: str | None = Depends(verify_api_key),
    ) -> dict[str, Any]:
        body = await request.body()
        original_name, content_type, data = _parse_single_file_upload(
            body,
            request.headers.get("content-type", ""),
        )
        suffix = Path(original_name).suffix.lower()
        if suffix not in ALLOWED_IMAGE_UPLOAD_SUFFIXES:
            raise HTTPException(
                status_code=400,
                detail="unsupported image reference suffix",
            )
        if content_type not in ALLOWED_IMAGE_UPLOAD_TYPES:
            raise HTTPException(
                status_code=400,
                detail="unsupported image reference content type",
            )
        if not data:
            raise HTTPException(status_code=400, detail="empty image reference")
        if len(data) > MAX_IMAGE_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="image reference too large")

        target_root = _upload_root(app.state.runtime_dir)
        target_root.mkdir(parents=True, exist_ok=True)
        target = target_root / _safe_upload_name(original_name)
        counter = 1
        while target.exists():
            target = target_root / f"{target.stem}-{counter}{target.suffix}"
            counter += 1
        target.write_bytes(data)
        return {
            "image_path": str(target),
            "file_name": target.name,
            "size": len(data),
            "content_type": content_type,
        }
```

- [ ] **Step 7: Run upload tests and verify they pass**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_web_shell.py::test_web_shell_uploads_image_reference_to_runtime_staging tests\test_web_shell.py::test_web_shell_rejects_non_image_reference_upload -q
```

Expected: PASS.

- [ ] **Step 8: Commit upload endpoint**

```powershell
git add apps\web\main.py tests\test_web_shell.py
git commit -m "feat: stage web image reference uploads"
```

---

### Task 3: Migrate HTML Shell to 10 Radi144-Nearer Steps

**Files:**
- Modify: `apps/web/static/index.html`
- Modify: `tests/test_web_shell.py`

- [ ] **Step 1: Replace topbar copy**

Change the topbar text to:

```html
<p class="eyebrow">Radi144-naher Klienten-Workflow</p>
<h1>Morphic Engine V1</h1>
<p class="topbar-subtitle">Gefuehrte Aufnahme, Analyseprofil, Ergebnispruefung und Harmonisierung in zehn klaren Schritten.</p>
```

- [ ] **Step 2: Replace stepper buttons with 10 entries**

Use this exact navigation:

```html
<nav class="wizard-stepper" id="wizard-stepper" role="navigation" aria-label="Workflow-Navigation">
  <button class="wizard-step active" type="button" data-step="0" aria-current="step"><span>1</span>Willkommen</button>
  <button class="wizard-step" type="button" data-step="1"><span>2</span>Hinweise</button>
  <button class="wizard-step" type="button" data-step="2"><span>3</span>Klienten-Daten</button>
  <button class="wizard-step" type="button" data-step="3"><span>4</span>Fokus</button>
  <button class="wizard-step" type="button" data-step="4"><span>5</span>Konfiguration</button>
  <button class="wizard-step" type="button" data-step="5"><span>6</span>Umfeldprofil</button>
  <button class="wizard-step" type="button" data-step="6"><span>7</span>Start</button>
  <button class="wizard-step" type="button" data-step="7"><span>8</span>Matrix</button>
  <button class="wizard-step" type="button" data-step="8"><span>9</span>Berichte</button>
  <button class="wizard-step" type="button" data-step="9"><span>10</span>Abschluss</button>
</nav>
```

- [ ] **Step 3: Rename compliance panel to consent**

Change the second panel opening tag from:

```html
<section id="compliance" class="panel wizard-panel" data-step="1">
```

to:

```html
<section id="consent" class="panel wizard-panel" data-step="1">
```

Keep `id="consent-local"` and `id="consent-safety"` unchanged.

- [ ] **Step 4: Add PII opt-in card inside the client panel**

After the `scan-form`, add:

```html
<div class="step-card privacy-card" data-pii-storage="opt-in">
  <div class="card-title-row">
    <div>
      <span class="op-label">Lokaler Entwurf</span>
      <strong>Klientendaten auf diesem Geraet merken</strong>
    </div>
  </div>
  <p class="muted-copy">Standard ist keine Speicherung. Mit Opt-in werden nur die Eingaben dieses Formulars im Browser dieses Geraets gespeichert.</p>
  <label class="checkline">
    <input id="client-storage-opt-in" type="checkbox">
    <span>Klientendaten browserlokal merken</span>
  </label>
  <button id="client-storage-clear" class="secondary-button" type="button">Lokalen Entwurf loeschen</button>
  <span id="client-storage-state" class="inline-state">keine Speicherung aktiv</span>
</div>
```

- [ ] **Step 5: Split configuration and environment panels**

Keep `profile_template`, `entropy_mode`, `top_n`, and `profile_level` inside `scan-form`, but move the general controls into a new step 5:

```html
<section id="analysis-config" class="panel wizard-panel" data-step="4">
  <div class="step-header">
    <span class="step-icon">5</span>
    <div>
      <p class="eyebrow">Step 5</p>
      <h2>Analyse-Konfiguration</h2>
      <p class="step-subtitle">Template, Auswertungstiefe und Ergebnisumfang fuer Phase 1 festlegen.</p>
    </div>
  </div>
  <div class="step-card">
    <div class="control-row">
      <!-- keep existing profile_level, top_n, profile_template and entropy_mode controls here -->
    </div>
  </div>
</section>
```

Then make the old `profile` panel step 6 and rename it:

```html
<section id="environment-profile" class="panel wizard-panel" data-step="5">
```

- [ ] **Step 6: Add upload UI to environment-profile**

Inside `environment-profile`, replace the old image path label with:

```html
<div class="upload-card">
  <label>
    <span>Bildreferenz hochladen</span>
    <input id="image-upload" type="file" accept="image/png,image/jpeg">
  </label>
  <input form="scan-form" name="image_path" placeholder="Noch keine Bildreferenz gewaehlt">
  <span id="image-upload-state" class="inline-state">kein Upload gewaehlt</span>
  <p id="image-upload-meta" class="muted-copy">PNG oder JPG. Der lokale Pfad wird nach dem Upload in den Phase-1-Handoff uebernommen.</p>
</div>
```

- [ ] **Step 7: Move preview panel to step 7**

Change:

```html
<section id="preview" class="panel wizard-panel" data-step="5">
```

to:

```html
<section id="preview" class="panel wizard-panel" data-step="6">
```

Update visible heading to `Zusammenfassung &amp; Start`.

- [ ] **Step 8: Add result matrix panel**

Insert this panel between preview and reports:

```html
<section id="result-matrix" class="panel wizard-panel result-matrix-panel" data-step="7" aria-labelledby="result-matrix-heading">
  <div class="step-header">
    <span class="step-icon">8</span>
    <div>
      <p class="eyebrow">Step 8</p>
      <h2 id="result-matrix-heading">Ergebnis-Matrix</h2>
      <p class="step-subtitle">Top-Profile und Resonanzen aus dem letzten Scan kompakt pruefen.</p>
    </div>
  </div>
  <div class="step-card">
    <div class="report-toolbar">
      <span id="result-matrix-state" class="inline-state">Noch kein Scan-Ergebnis geladen</span>
      <button id="refresh-result-matrix-button" class="secondary-button" type="button" disabled>Matrix aktualisieren</button>
    </div>
    <div id="result-matrix-list" class="result-matrix-list scroll-region" aria-live="polite" tabindex="0">
      <p class="empty-state">Nach einer abgeschlossenen Analyse erscheinen hier Profile, Resonanzen und Exportpfade.</p>
    </div>
  </div>
</section>
```

- [ ] **Step 9: Move reports and harmonization panels**

Change reports to `data-step="8"` and harmonization to `data-step="9"`. Update harmonization heading:

```html
<h2 id="harmonization-heading">Harmonisierung, Export &amp; Abschluss</h2>
```

- [ ] **Step 10: Run shell tests and verify HTML failures narrow**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_web_shell.py::test_web_shell_serves_phase1_client_facing_first_screen tests\test_web_shell.py::test_web_shell_exposes_guided_workflow_stepping -q
```

Expected: PASS for the first-screen and structural HTML assertions.

- [ ] **Step 11: Commit HTML migration**

```powershell
git add apps\web\static\index.html tests\test_web_shell.py
git commit -m "feat: migrate web shell to ten step workflow"
```

---

### Task 4: Update Workflow JS for 10 Steps, Uploads, and Opt-In Draft Storage

**Files:**
- Modify: `apps/web/static/app.js`
- Modify: `tests/test_web_shell.py`

- [ ] **Step 1: Update workflow constants**

Replace `WORKFLOW_STEPS` with:

```javascript
const WORKFLOW_STEPS = [
  {label: "Willkommen & Systemstatus"},
  {label: "Hinweise & Einwilligung"},
  {label: "Klienten-Daten"},
  {label: "Fokus & Intention"},
  {label: "Analyse-Konfiguration"},
  {label: "EMF-/Umfeld-Analyseprofil"},
  {label: "Zusammenfassung & Start"},
  {label: "Ergebnis-Matrix"},
  {label: "Ergebnis-Details & Berichte"},
  {label: "Harmonisierung, Export & Abschluss"}
];

const CLIENT_DRAFT_KEY = "morphic_v1_client_draft";
```

- [ ] **Step 2: Update validation indexes**

Replace `validateCurrentStep` branch logic with:

```javascript
function validateCurrentStep() {
  if (currentStep === 1) {
    const local = $("#consent-local");
    const safety = $("#consent-safety");
    const ok = Boolean(local?.checked && safety?.checked);
    if (!ok) showInlineState("Einwilligung bestaetigen", "warn");
    return ok;
  }

  if ([2, 3, 4, 5, 6].includes(currentStep)) {
    const form = $("#scan-form");
    if (!form) return true;
    if (typeof form.reportValidity === "function") return form.reportValidity();
    return form.checkValidity();
  }

  if (currentStep === 8) {
    const ok = Boolean(activeReportId);
    if (!ok) {
      setReportState("Bitte zuerst einen Bericht in der Vorschau oeffnen.", "warn");
      showHarmonizationState("Bitte zuerst einen Bericht in der Vorschau oeffnen.", "warn");
    }
    return ok;
  }

  return true;
}
```

- [ ] **Step 3: Add upload helper**

Add before `formPayload`:

```javascript
async function uploadImageReference() {
  const input = $("#image-upload");
  const state = $("#image-upload-state");
  const meta = $("#image-upload-meta");
  const pathInput = document.querySelector('input[name="image_path"]');
  const file = input?.files?.[0];
  if (!file) return;
  if (state) {
    state.textContent = "Upload laeuft";
    state.dataset.state = "warn";
  }
  const data = new FormData();
  data.append("file", file);
  try {
    const response = await fetch("/api/uploads/image-reference", {
      method: "POST",
      body: data
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(JSON.stringify(payload));
    if (pathInput) pathInput.value = payload.image_path || "";
    if (state) {
      state.textContent = "Bildreferenz bereit";
      state.dataset.state = "ok";
    }
    if (meta) {
      meta.textContent = `${payload.file_name} · ${payload.size} Bytes · ${payload.content_type}`;
    }
  } catch (error) {
    if (state) {
      state.textContent = "Uploadfehler";
      state.dataset.state = "bad";
    }
    if (meta) meta.textContent = String(error.message || error);
  }
}
```

- [ ] **Step 4: Add opt-in draft helpers**

Add before `bindWorkflow`:

```javascript
function clientDraftPayload() {
  const form = $("#scan-form");
  if (!form) return {};
  const data = new FormData(form);
  return {
    last_name: String(data.get("last_name") || ""),
    first_name: String(data.get("first_name") || ""),
    birth_date: String(data.get("birth_date") || ""),
    birth_place: String(data.get("birth_place") || ""),
    focus: String(data.get("focus") || ""),
    main_symptom: String(data.get("main_symptom") || ""),
    notes: String(data.get("notes") || ""),
    profile_level: String(data.get("profile_level") || "3"),
    top_n: String(data.get("top_n") || "5"),
    profile_template: String(data.get("profile_template") || "phase1-default"),
    entropy_mode: String(data.get("entropy_mode") || "legacy"),
    image_path: String(data.get("image_path") || ""),
    adaptive_limits: data.get("adaptive_limits") === "on"
  };
}

function applyClientDraft(draft) {
  Object.entries(draft || {}).forEach(([name, value]) => {
    const field = document.querySelector(`[name="${name}"]`);
    if (!field) return;
    if (field.type === "checkbox") {
      field.checked = Boolean(value);
    } else {
      field.value = String(value == null ? "" : value);
    }
  });
}

function saveClientDraftIfEnabled() {
  const enabled = Boolean($("#client-storage-opt-in")?.checked);
  const state = $("#client-storage-state");
  if (!enabled) {
    if (state) {
      state.textContent = "keine Speicherung aktiv";
      state.dataset.state = "neutral";
    }
    return;
  }
  localStorage.setItem(CLIENT_DRAFT_KEY, JSON.stringify(clientDraftPayload()));
  if (state) {
    state.textContent = "lokaler Entwurf gespeichert";
    state.dataset.state = "ok";
  }
}

function restoreClientDraft() {
  const raw = localStorage.getItem(CLIENT_DRAFT_KEY);
  if (!raw) return;
  try {
    applyClientDraft(JSON.parse(raw));
    const optIn = $("#client-storage-opt-in");
    if (optIn) optIn.checked = true;
    const state = $("#client-storage-state");
    if (state) {
      state.textContent = "lokaler Entwurf geladen";
      state.dataset.state = "ok";
    }
  } catch (error) {
    localStorage.removeItem(CLIENT_DRAFT_KEY);
  }
}

function clearClientDraft() {
  localStorage.removeItem(CLIENT_DRAFT_KEY);
  const optIn = $("#client-storage-opt-in");
  if (optIn) optIn.checked = false;
  const state = $("#client-storage-state");
  if (state) {
    state.textContent = "lokaler Entwurf geloescht";
    state.dataset.state = "neutral";
  }
}
```

- [ ] **Step 5: Add result matrix loader**

Add near report functions:

```javascript
function renderResultMatrix(payload) {
  const list = $("#result-matrix-list");
  if (!list) return;
  const profiles = Array.isArray(payload.top_profiles) ? payload.top_profiles : [];
  const paths = payload.export_paths || {};
  if (!profiles.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "Noch keine Matrixdaten fuer diesen Scan verfuegbar.";
    list.replaceChildren(empty);
    return;
  }
  const nodes = profiles.map((profile) => {
    const item = document.createElement("article");
    item.className = "result-matrix-item";
    const title = document.createElement("strong");
    title.textContent = profile.profile || "Profil";
    const score = document.createElement("span");
    score.textContent = `Score ${Number(profile.score || 0).toFixed(2)}`;
    const resonances = document.createElement("p");
    resonances.textContent = (profile.top_resonances || [])
      .map((entry) => `${entry.label} (${Number(entry.score || 0).toFixed(2)})`)
      .join(", ") || "Keine Resonanzen gelistet.";
    item.append(title, score, resonances);
    return item;
  });
  if (Object.keys(paths).length) {
    const exportItem = document.createElement("article");
    exportItem.className = "result-matrix-item";
    const title = document.createElement("strong");
    title.textContent = "Exportpfade";
    const details = document.createElement("p");
    details.textContent = Object.entries(paths).map(([key, value]) => `${key}: ${value}`).join(" · ");
    exportItem.append(title, details);
    nodes.push(exportItem);
  }
  list.replaceChildren(...nodes);
}

async function loadResultMatrix(jobId = activeJobId) {
  const state = $("#result-matrix-state");
  if (!jobId) {
    if (state) {
      state.textContent = "Noch kein Scan-Ergebnis geladen";
      state.dataset.state = "neutral";
    }
    return;
  }
  if (state) {
    state.textContent = "Matrix wird geladen";
    state.dataset.state = "warn";
  }
  try {
    const response = await fetch(`/api/scan/jobs/${encodeURIComponent(jobId)}/results`);
    const payload = await response.json();
    if (!response.ok) throw new Error(JSON.stringify(payload));
    renderResultMatrix(payload);
    if (state) {
      state.textContent = "Matrix bereit";
      state.dataset.state = "ok";
    }
  } catch (error) {
    if (state) {
      state.textContent = "Matrixfehler";
      state.dataset.state = "bad";
    }
  }
}
```

- [ ] **Step 6: Update scan completion flow**

Inside `pollScanJob`, when `payload.status === "completed"`, call:

```javascript
await loadResultMatrix(jobId);
await loadReports(null, true);
goToStep(7);
```

- [ ] **Step 7: Update report preview routing**

In `previewReport`, change:

```javascript
if (currentStep < 6) {
  goToStep(6);
}
```

to:

```javascript
if (currentStep < 8) {
  goToStep(8);
}
```

- [ ] **Step 8: Bind new controls**

In `bindWorkflow`, add:

```javascript
$("#image-upload")?.addEventListener("change", uploadImageReference);
$("#client-storage-opt-in")?.addEventListener("change", saveClientDraftIfEnabled);
$("#client-storage-clear")?.addEventListener("click", clearClientDraft);
$("#refresh-result-matrix-button")?.addEventListener("click", () => loadResultMatrix());
$("#scan-form")?.addEventListener("input", saveClientDraftIfEnabled);
restoreClientDraft();
```

- [ ] **Step 9: Run static asset tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_web_shell.py::test_web_shell_static_assets_define_wizard_behavior -q
```

Expected: PASS.

- [ ] **Step 10: Commit JS behavior**

```powershell
git add apps\web\static\app.js tests\test_web_shell.py
git commit -m "feat: add ten step workflow behavior"
```

---

### Task 5: Apply Radi144-Nearer Visual System

**Files:**
- Modify: `apps/web/static/app.css`
- Modify: `tests/test_web_shell.py`

- [ ] **Step 1: Add or update CSS tokens**

At the top of `app.css`, ensure these variables exist:

```css
:root {
  --surface: #fffdf7;
  --surface-strong: #f7f1e6;
  --card: #ffffff;
  --ink: #24231f;
  --muted: #6f6a60;
  --line: #ded5c5;
  --sage: #6f8063;
  --sage-strong: #4f6248;
  --terracotta: #b66a4d;
  --terracotta-soft: #f4dfd5;
  --sand: #e8dcc8;
  --focus-ring: rgba(111, 128, 99, 0.32);
}
```

- [ ] **Step 2: Add step-header and card styles**

Add:

```css
.workflow-shell {
  width: min(1180px, calc(100vw - 32px));
  margin: 0 auto;
}

.step-header {
  align-items: flex-start;
  display: flex;
  gap: 14px;
  margin-bottom: 18px;
}

.step-icon {
  align-items: center;
  background: var(--terracotta-soft);
  border: 1px solid rgba(182, 106, 77, 0.35);
  border-radius: 8px;
  color: var(--terracotta);
  display: inline-flex;
  flex: 0 0 42px;
  font-weight: 800;
  height: 42px;
  justify-content: center;
}

.step-subtitle,
.muted-copy {
  color: var(--muted);
  line-height: 1.55;
  margin: 6px 0 0;
}

.step-card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 18px;
}

.card-title-row {
  align-items: center;
  display: flex;
  justify-content: space-between;
  gap: 12px;
}
```

- [ ] **Step 3: Add radio/toggle/upload/matrix styles**

Add:

```css
.radio-card-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.radio-card,
.toggle-card,
.upload-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 14px;
}

.radio-card:has(input:checked),
.toggle-card:has(input:checked) {
  border-color: var(--sage);
  box-shadow: 0 0 0 3px var(--focus-ring);
}

.result-matrix-list {
  display: grid;
  gap: 12px;
  max-height: 540px;
}

.result-matrix-item {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 14px;
}

.result-matrix-item strong {
  color: var(--ink);
  display: block;
  margin-bottom: 6px;
}
```

- [ ] **Step 4: Strengthen mobile behavior**

Add:

```css
@media (max-width: 760px) {
  .wizard-stepper {
    overflow-x: auto;
    padding-bottom: 8px;
  }

  .wizard-step {
    flex: 0 0 148px;
    min-height: 56px;
    white-space: normal;
  }

  .step-header,
  .card-title-row,
  .report-toolbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .workflow-shell {
    width: min(100vw - 20px, 1180px);
  }
}
```

- [ ] **Step 5: Run CSS/static tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_web_shell.py::test_web_shell_static_assets_define_wizard_behavior tests\test_web_shell.py::test_web_shell_accessibility_and_report_readability_baseline -q
```

Expected: PASS.

- [ ] **Step 6: Commit CSS**

```powershell
git add apps\web\static\app.css tests\test_web_shell.py
git commit -m "style: align web workflow with radi144 patterns"
```

---

### Task 6: Preserve CLI Handoff and Full Focused Web Tests

**Files:**
- Modify: `apps/web/static/app.js` when the focused tests reveal a broken payload or storage contract.
- Modify: `apps/web/main.py` when the focused tests reveal a broken upload or scan API contract.
- Modify: `tests/test_web_shell.py` only when assertions do not match the approved spec.

- [ ] **Step 1: Run all web shell tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_web_shell.py -q
```

Expected: PASS.

- [ ] **Step 2: If CLI handoff tests fail, preserve existing payload names**

Check that `formPayload()` still returns:

```javascript
return {
  last_name: String(data.get("last_name") || "").trim(),
  first_name: String(data.get("first_name") || "").trim(),
  birth_date: String(data.get("birth_date") || "").trim(),
  birth_place: String(data.get("birth_place") || "").trim(),
  image_path: String(data.get("image_path") || "").trim() || null,
  focus: String(data.get("focus") || "").trim(),
  profile_level: Number(data.get("profile_level") || 3),
  top_n: Number(data.get("top_n") || 5),
  profile_template: String(data.get("profile_template") || "").trim() || "phase1-default",
  entropy_mode: String(data.get("entropy_mode") || "").trim() || "legacy",
  adaptive_limits: data.get("adaptive_limits") === "on",
  consent_local: Boolean($("#consent-local")?.checked),
  consent_safety: Boolean($("#consent-safety")?.checked)
};
```

- [ ] **Step 3: If PII test concerns appear, enforce opt-in only**

Verify the only localStorage write is inside `saveClientDraftIfEnabled()` after:

```javascript
const enabled = Boolean($("#client-storage-opt-in")?.checked);
if (!enabled) {
  return;
}
localStorage.setItem(CLIENT_DRAFT_KEY, JSON.stringify(clientDraftPayload()));
```

- [ ] **Step 4: Commit focused test fixes if any**

```powershell
git add apps\web\static\app.js apps\web\main.py tests\test_web_shell.py
git commit -m "fix: preserve web workflow contracts"
```

If no files changed during this task, record in the handoff that the preservation check required no commit.

---

### Task 7: Browser Verification

**Files:**
- No source changes expected.
- Screenshots: `codex_tmp/radi144-workflow-desktop.png`, `codex_tmp/radi144-workflow-mobile.png`

- [ ] **Step 1: Start the web app on a free port**

Run:

```powershell
.\.venv\Scripts\python.exe -m uvicorn apps.web.main:app --host 127.0.0.1 --port 8092
```

Expected: server starts and serves `http://127.0.0.1:8092/`.

- [ ] **Step 2: Verify desktop manually or with Playwright**

Check:

```text
URL: http://127.0.0.1:8092/
Viewport: 1440x1000
Expected:
- 10 stepper buttons visible or horizontally usable.
- Progress label starts at 1 / 10.
- Step 3 includes opt-in local draft controls.
- Step 6 includes image upload and image_path fallback.
- Step 8 result matrix exists.
- Step 10 harmonization controls still render.
```

- [ ] **Step 3: Verify mobile manually or with Playwright**

Check:

```text
URL: http://127.0.0.1:8092/
Viewport: 390x844
Expected:
- No text overlap in topbar, stepper, cards, buttons or forms.
- Stepper scrolls horizontally.
- Buttons wrap without clipping.
- Report and harmonization panels remain readable.
```

- [ ] **Step 4: Save screenshots**

Save:

```text
codex_tmp/radi144-workflow-desktop.png
codex_tmp/radi144-workflow-mobile.png
```

- [ ] **Step 5: Stop the server**

Stop the uvicorn process that was started for this verification.

---

### Task 8: Final Review and Handoff

**Files:**
- Review only unless fixes are found.

- [ ] **Step 1: Check git status**

Run:

```powershell
git status --short
```

Expected: only intended files changed, or clean after task commits.

- [ ] **Step 2: Review final diff**

Run:

```powershell
git diff --stat
git diff -- apps\web\main.py apps\web\static\index.html apps\web\static\app.js apps\web\static\app.css tests\test_web_shell.py
```

Expected:

```text
- No unrelated rewrites.
- No hidden PII autosave.
- Upload endpoint is limited to image suffix/content type and size.
- CLI handoff still uses image_path.
- Workflow has exactly 10 steps.
```

- [ ] **Step 3: Run final focused verification**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_web_shell.py -q
```

Expected: PASS.

- [ ] **Step 4: Prepare concise handoff**

Report:

```text
Implemented:
- 10-step Radi144-nearer workflow.
- Image-reference upload/staging with existing image_path handoff.
- Opt-in browser-local client draft storage with reset.
- Result matrix step.
- Updated tests and desktop/mobile browser verification.

Verification:
- tests/test_web_shell.py passed.
- Desktop screenshot: codex_tmp/radi144-workflow-desktop.png
- Mobile screenshot: codex_tmp/radi144-workflow-mobile.png
```
