# V1 Remedy Profile And Trend History Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore per-profile Remedy reports and replace the minimal trend placeholder with a usable label/score trend history from existing scan JSON exports.

**Architecture:** Keep scan engines unchanged. Extend `tools.remedy_reporter` to emit one `*_remedy.html/json` per source scan next to the existing total `*_topN_remedies.html/json`, and extend `tools.trend_analyzer` to compare top labels across at least two scans.

**Tech Stack:** Python stdlib JSON/Path, existing `tools.reporting_common.render_legacy_html`, pytest subprocess tests.

---

## File Structure

| File | Responsibility |
|---|---|
| `tools/remedy_reporter.py` | Generate total Remedy report and per-profile Remedy detail reports from existing scan JSONs. |
| `tools/trend_analyzer.py` | Build trend entries across scan JSONs, write JSON/HTML trend history, keep `Hinweis.txt` fallback for insufficient history. |
| `tests/test_remedy_trend_history.py` | Regression tests for per-profile Remedy files and real trend entries. |
| `docs/RADI144_UIUX_DSGVO_REFERENZANALYSE_20260628.md` | Status note after implementation. |

---

### Task 1: Failing Tests

**Files:**
- Create: `tests/test_remedy_trend_history.py`

- [ ] **Step 1: Write failing tests**

Create two source scan JSON files. Assert:

- `tools.remedy_reporter` writes the existing total `*_top3_remedies.html`.
- It additionally writes one `*_remedy.html` per source profile.
- The per-profile HTML includes the source profile name and remedy labels.
- `tools.trend_analyzer` with two scans writes `trendanalyse_*.json/html`.
- Trend JSON contains a `trends` list with label, first_score, latest_score and delta.
- Trend HTML contains `Trend-Historik` and the tested label.

- [ ] **Step 2: Run tests to verify they fail**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_remedy_trend_history.py -q
```

Expected: fail because per-profile Remedy files and real trend entries do not yet exist.

---

### Task 2: Per-Profile Remedy Reports

**Files:**
- Modify: `tools/remedy_reporter.py`

- [ ] **Step 1: Add source profile helper**

Add helper functions:

- `_profile_label_from_source(path, payload)`
- `_remedies_from_payload(path, payload)`
- `_write_profile_remedy_report(path, payload, output_dir)`

- [ ] **Step 2: Generate per-profile reports**

Inside `consolidate_remedy_synergies()`, after loading each source payload, write:

- `<safe_profile>_remedy.json`
- `<safe_profile>_remedy.html`

The HTML uses `render_legacy_html()` and includes a simple Remedy table.

- [ ] **Step 3: Register per-profile artifacts**

In `main()`, register `*_remedy.json` and `*_remedy.html` with artifact types:

- `remedy_profile_json`
- `remedy_profile_html`

- [ ] **Step 4: Run Remedy-focused test**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_remedy_trend_history.py::test_remedy_reporter_writes_per_profile_reports -q
```

Expected: pass.

---

### Task 3: Trend History

**Files:**
- Modify: `tools/trend_analyzer.py`

- [ ] **Step 1: Add trend extraction helpers**

Add helper functions:

- `_load_json(path)`
- `_top_items(payload)`
- `_build_trends(files)`

Trend entries contain:

```python
{
    "label": label,
    "group": group,
    "occurrences": count,
    "first_score": first_score,
    "latest_score": latest_score,
    "delta": latest_score - first_score,
    "direction": "steigend" | "fallend" | "stabil",
}
```

- [ ] **Step 2: Write real trend JSON and HTML**

For `len(files) >= 2`, write:

- `trendanalyse_<stamp>.json` containing `source_files` and `trends`
- `trendanalyse_<stamp>.html` containing heading `Trend-Historik` and a table

Keep `Hinweis.txt` behavior for fewer than two files.

- [ ] **Step 3: Run trend-focused test**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_remedy_trend_history.py::test_trend_analyzer_writes_score_history -q
```

Expected: pass.

---

### Task 4: Verification

- [ ] **Step 1: Run focused tests**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_remedy_trend_history.py tests\test_report_tool_archives.py tests\test_report_manifest_registration.py -q
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
| Scope | Per-profile Remedy reports and trend history only; no scan/scoring changes. |
| Compliance | Existing Wellbeing block remains part of all `render_legacy_html()` outputs. |
| Placeholder scan | No `TODO` or `TBD` markers. |
