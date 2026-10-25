# Apps/Web Phase 1 UX Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refine the Phase 1 client-facing `apps/web` experience so the report catalog, preview, lists, titles, and accessibility are calmer, HTML-first, and easier for clients to use.

**Architecture:** Keep all file generation unchanged and improve presentation only. `apps/web/reports.py` becomes the policy layer for what is visible in the client catalog, while `apps/web/static/index.html`, `app.js`, and `app.css` reshape the catalog + preview UX. Existing report tools stay responsible for generating artifacts; this round only changes what clients see first and how large lists are rendered.

**Tech Stack:** FastAPI, vanilla HTML/CSS/JS in `apps/web/static`, existing report generators, pytest.

---

### Task 1: Make the catalog HTML-first and session-friendly

**Files:**
- Modify: `apps/web/reports.py`
- Modify: `apps/web/main.py`
- Modify: `tests/test_web_reports.py`
- Create: `tests/test_web_catalog_client_view.py`

- [ ] **Step 1: Write the failing catalog policy test**

```python
# tests/test_web_catalog_client_view.py
from pathlib import Path

from apps.web.reports import ReportCatalog


def test_catalog_shows_only_html_items_in_client_listing(tmp_path: Path) -> None:
    root = tmp_path / "Benutzer_Archive_Start" / "Mustermann_Klaus_09041966_Augsburg" / "20260630_210612_TOP3_SESSION"
    root.mkdir(parents=True)
    (root / "a.html").write_text("<html></html>", encoding="utf-8")
    (root / "a.json").write_text("{}", encoding="utf-8")
    (root / "a.pdf").write_bytes(b"%PDF-1.4\n")

    payload = ReportCatalog([tmp_path / "Benutzer_Archive_Start"]).list()
    files = payload["clients"][0]["sessions"][0]["files"]

    assert [f["kind"] for f in files] == ["HTML"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_web_catalog_client_view.py tests/test_web_reports.py -q`
Expected: FAIL because the catalog currently includes JSON/TXT/PDF in the client listing.

- [ ] **Step 3: Implement client-visible filtering + title shaping**

```python
# apps/web/reports.py
CLIENT_VISIBLE_KINDS = {"HTML"}


def _client_visible_files(files: list[dict[str, object]]) -> list[dict[str, object]]:
    return [item for item in files if item.get("kind") in CLIENT_VISIBLE_KINDS]


def _display_title(entry: dict[str, object]) -> str:
    session = str(entry.get("session_id", "")).replace("_", " ")
    client = str(entry.get("client_id", "")).replace("_", " ")
    kind = str(entry.get("report_label", "Bericht"))
    return f"{kind} - {session} - {client}".strip(" -")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_web_catalog_client_view.py tests/test_web_reports.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/web/reports.py apps/web/main.py tests/test_web_reports.py tests/test_web_catalog_client_view.py
git commit -m "feat: make client report catalog html-first"
```

### Task 2: Rebuild the catalog + preview layout for readability

**Files:**
- Modify: `apps/web/static/index.html`
- Modify: `apps/web/static/app.js`
- Modify: `apps/web/static/app.css`
- Modify: `tests/test_web_shell.py`

- [ ] **Step 1: Write the failing shell/layout expectation test**

```python
# tests/test_web_shell.py
assert "report-catalog-panel" in response.text
assert "report-preview-panel" in response.text
assert "Berichtspfad" not in response.text
assert "JSON" not in response.text
assert "PDF" not in response.text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_web_shell.py -q`
Expected: FAIL because the current shell still exposes broader file metadata and older layout proportions.

- [ ] **Step 3: Implement the new two-column layout**

```html
<section class="report-layout">
  <aside id="report-catalog-panel" class="report-catalog-panel">
    <h2>Sessions</h2>
    <div id="report-session-list"></div>
  </aside>
  <section id="report-preview-panel" class="report-preview-panel">
    <header class="preview-header">
      <h2 id="report-preview-title">Berichtsvorschau</h2>
      <button id="open-report-button" type="button">Im neuen Fenster öffnen</button>
    </header>
    <iframe id="report-preview-frame" title="Berichtsvorschau"></iframe>
  </section>
</section>
```

```css
.report-layout { display: grid; grid-template-columns: minmax(240px, 28%) minmax(0, 72%); gap: 1rem; }
.report-session-list { max-height: 72vh; overflow: auto; }
@media (max-width: 960px) { .report-layout { grid-template-columns: 1fr; } }
```

- [ ] **Step 4: Update JS rendering to show grouped sessions and only client-friendly labels**

```javascript
function renderSessions(client) {
  const list = $("#report-session-list");
  list.replaceChildren();
  client.sessions.forEach((session) => {
    const block = document.createElement("section");
    block.className = "session-block";
    block.innerHTML = `<h3>${session.session_label}</h3>`;
    session.files.forEach((file) => block.appendChild(reportLink(file)));
    list.appendChild(block);
  });
}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_web_shell.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add apps/web/static/index.html apps/web/static/app.js apps/web/static/app.css tests/test_web_shell.py
git commit -m "feat: simplify report catalog and widen preview"
```

### Task 3: Limit visible list sizes in client-facing HTML reports

**Files:**
- Modify: `apps/cli/commands/helpers/harmonization_helpers.py`
- Modify: `tools/remedy_reporter.py`
- Modify: `tools/synergy_consolidator.py`
- Modify: `tools/trend_analyzer.py`
- Create: `tests/test_report_visible_limits.py`

- [ ] **Step 1: Write the failing visible-limit test**

```python
# tests/test_report_visible_limits.py
from apps.cli.commands.helpers.harmonization_helpers import _visible_item_limit


def test_visible_item_limit_caps_large_lists_for_clients() -> None:
    assert _visible_item_limit(total_count=10) == 10
    assert _visible_item_limit(total_count=21) == 21
    assert _visible_item_limit(total_count=67) == 21
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_report_visible_limits.py -q`
Expected: FAIL because no shared visible-limit helper exists yet.

- [ ] **Step 3: Introduce a shared visible-limit rule and scroll containers**

```python
# apps/cli/commands/helpers/harmonization_helpers.py
VISIBLE_CLIENT_LIMIT = 21
VISIBLE_SCROLL_THRESHOLD = 30


def _visible_item_limit(total_count: int) -> int:
    return total_count if total_count <= VISIBLE_CLIENT_LIMIT else VISIBLE_CLIENT_LIMIT
```

```html
<div class="scroll-table" data-total-items="67">
  ... first 21 rows rendered ...
</div>
<p class="scroll-hint">Weitere Einträge sind per Scrollen erreichbar.</p>
```

- [ ] **Step 4: Apply the rule to remedy/synergy/trend and large resonance tables**

```python
# tools/remedy_reporter.py
visible = remedies[:_visible_item_limit(len(remedies))]
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_report_visible_limits.py tests/test_web_shell.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add apps/cli/commands/helpers/harmonization_helpers.py tools/remedy_reporter.py tools/synergy_consolidator.py tools/trend_analyzer.py tests/test_report_visible_limits.py
git commit -m "feat: cap visible client report lists"
```

### Task 4: Improve HTML report readability and accessibility baseline

**Files:**
- Modify: `apps/web/static/app.css`
- Modify: `apps/web/static/index.html`
- Modify: `tools/reporting_common.py`
- Modify: `apps/cli/commands/helpers/harmonization_helpers.py`
- Modify: `tests/test_web_shell.py`

- [ ] **Step 1: Write/extend shell expectations for accessibility-critical structure**

```python
# tests/test_web_shell.py
assert 'aria-label="Berichtsvorschau"' in response.text
assert 'aria-live="polite"' in response.text
