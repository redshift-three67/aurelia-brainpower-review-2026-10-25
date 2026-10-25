# Apps Web Workflow Stepper Phase 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move reports and harmonization into the guided `apps/web` wizard as explicit steps 7 and 8.

**Architecture:** Keep the existing static web shell and API contracts. Extend the current HTML panels, `WORKFLOW_STEPS`, validation, and light CSS layout rules without introducing a new state model or changing scan/report/harmonization backend logic.

**Tech Stack:** FastAPI static shell, vanilla HTML/CSS/JavaScript, pytest shell assertions in `tests/test_web_shell.py`.

---

## File Structure

- Modify: `tests/test_web_shell.py`
  - Assert the shell exposes 8 wizard steps, `reports` and `harmonization` as `wizard-panel`s, and the expected JS validation/auto-navigation markers.
- Modify: `apps/web/static/index.html`
  - Add stepper buttons 7 and 8.
  - Change progress seed text to `1 / 8`.
  - Make `#reports` a `wizard-panel` with `data-step="6"`.
  - Move harmonization out of the report preview stack into its own `#harmonization` wizard panel with `data-step="7"`.
- Modify: `apps/web/static/app.js`
  - Add `Berichte` and `Harmonisierung` to `WORKFLOW_STEPS`.
  - Gate step 7 -> step 8 on `activeReportId`.
  - After successful auto-preview of a report, move to step 7.
  - Keep harmonization start gating tied to `activeReportId`.
- Modify: `apps/web/static/app.css`
  - Keep report layout robust for long titles.
  - Make sticky offsets less aggressive on smaller viewports.
  - Let the report preview be sticky only on desktop.

## Task 1: Lock 8-Step Shell Expectations

**Files:**
- Modify: `tests/test_web_shell.py`

- [x] **Step 1: Write the failing shell markup test**

Update `test_web_shell_exposes_guided_workflow_stepping` so it expects:

```python
assert 'data-step="7"' in response.text
assert 'id="reports" class="panel wizard-panel reports-panel" data-step="6"' in response.text
assert 'id="harmonization" class="panel wizard-panel harmonization-panel" data-step="7"' in response.text
assert "Berichtskatalog &amp; Vorschau" in response.text
assert "Workflowabschluss &amp; Harmonisierung" in response.text
assert response.text.count('class="wizard-step') == 8
```

Remove the old implicit expectation that `data-step="5"` is the final wizard structure.

- [x] **Step 2: Write the failing static behavior test**

Update `test_web_shell_static_assets_define_wizard_behavior` so it expects:

```python
assert '{label: "Berichte"}' in js
assert '{label: "Harmonisierung"}' in js
assert 'if (currentStep === 6)' in js
assert 'Bitte zuerst einen Bericht in der Vorschau oeffnen.' in js
assert 'goToStep(6);' in js
assert ".harmonization-panel" in css
```

- [x] **Step 3: Run focused tests to verify RED**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_web_shell.py::test_web_shell_exposes_guided_workflow_stepping tests\test_web_shell.py::test_web_shell_static_assets_define_wizard_behavior -q
```

Expected: FAIL because the shell still has six steps and reports/harmonization are not separate wizard panels.

## Task 2: Move Reports and Harmonization Into Wizard Panels

**Files:**
- Modify: `apps/web/static/index.html`

- [x] **Step 1: Add stepper buttons and progress seed**

Change the stepper block to include:

```html
<button class="wizard-step" type="button" data-step="6"><span>7</span>Berichte</button>
<button class="wizard-step" type="button" data-step="7"><span>8</span>Harmonisierung</button>
```

Change:

```html
<span class="op-pct" id="wizard-progress-label">1 / 6</span>
```

to:

```html
<span class="op-pct" id="wizard-progress-label">1 / 8</span>
```

- [x] **Step 2: Convert reports to wizard step 7**

Change the reports section opening to:

```html
<section id="reports" class="panel wizard-panel reports-panel" data-step="6" aria-labelledby="reports-heading">
```

Keep the report catalog and preview card inside this section.

- [x] **Step 3: Move harmonization to wizard step 8**

Create a sibling section after `#reports`:

```html
<section id="harmonization" class="panel wizard-panel harmonization-panel" data-step="7" aria-labelledby="harmonization-heading">
```

Move the existing `report-preview-card harmonization-card` content into this section and set the title to:

```html
<h2 id="harmonization-heading">Workflowabschluss &amp; Harmonisierung</h2>
```

Keep all existing IDs and form field names unchanged.

## Task 3: Extend Wizard Behavior

**Files:**
- Modify: `apps/web/static/app.js`

- [x] **Step 1: Extend `WORKFLOW_STEPS`**

Change:

```javascript
  {label: "Analysefreigabe"}
```

to:

```javascript
  {label: "Analysefreigabe"},
  {label: "Berichte"},
  {label: "Harmonisierung"}
```

- [x] **Step 2: Add step 7 validation**

In `validateCurrentStep()`, add:

```javascript
if (currentStep === 6) {
  const ok = Boolean(activeReportId);
  if (!ok) {
    setReportState("Bitte zuerst einen Bericht in der Vorschau oeffnen.", "warn");
    showHarmonizationState("Bitte zuerst einen Bericht in der Vorschau oeffnen.", "warn");
  }
  return ok;
}
```

- [x] **Step 3: Move to reports after successful report preview**

In `previewReport(entry)`, after `syncHarmonizationControls();`, add:

```javascript
if (currentStep < 6) {
  goToStep(6);
}
```

This makes the successful scan auto-preview land on the `Berichte` panel without skipping directly to harmonization.

## Task 4: Stabilize Layout for the New Steps

**Files:**
- Modify: `apps/web/static/app.css`

- [x] **Step 1: Add harmonization panel spacing**

Add:

```css
.harmonization-panel {
  margin-top: 0;
}
```

- [x] **Step 2: Broaden report catalog layout**

Change:

```css
grid-template-columns: minmax(260px, 320px) minmax(0, 1fr);
```

to:

```css
grid-template-columns: minmax(300px, 360px) minmax(0, 1fr);
```

- [x] **Step 3: Reduce sticky pressure**

Change desktop preview sticky offset:

```css
top: 150px;
```

to:

```css
top: 138px;
```

And in the `max-width: 980px` block keep `.report-preview-column { position: static; }`.

## Task 5: Verify the Slice

**Files:**
- No production file changes unless verification reveals a regression.

- [x] **Step 1: Run focused web shell tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_web_shell.py -q
```

Expected: PASS.

- [x] **Step 2: Run browser check on a port other than 8090**

Start the app on an available port such as `8091`, then inspect the first screen and wizard navigation.

Expected:

- Eight step buttons are visible.
- Step 7 shows reports.
- Step 8 shows harmonization.
- Step 8 remains functionally gated until a report is selected.

- [x] **Step 3: Check diff**

Run:

```powershell
git diff -- apps/web/static/index.html apps/web/static/app.js apps/web/static/app.css tests/test_web_shell.py docs/superpowers/plans/2026-07-04-apps-web-workflow-stepper-phase2.md
```

Expected: only the planned UI/test/plan changes appear.

## Self-Review

- Spec coverage: The plan covers 8 visible steps, report and harmonization panels, report-gated harmonization, auto-transition to reports, responsive/sticky constraints, and focused verification.
- Placeholder scan: No `TBD` or `TODO` markers are used.
- Type consistency: Step numbers match zero-based JS state (`reports` = `6`, `harmonization` = `7`) and one-based UI labels (`7`, `8`).
