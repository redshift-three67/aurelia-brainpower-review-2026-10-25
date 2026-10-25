# Workbench Gate 2 Adaptive Limits Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adaptive Limits sind in der Workbench standardmaessig aus und ihre tatsaechliche Wirkung auf Phase-2-Details sowie die ownergebundene sichtbare Top-Profilliste ist vor dem Scan eindeutig pruefbar.

**Architecture:** Der bestehende Backenddefault `False`, der CLI-Detail-Cap und `adaptive_result_limit()` bleiben die Autoritaet. Der ownergebundene Ergebnisendpunkt liest Top-N und Opt-in aus dem persistierten Startkommando und wendet den Display-Cap auf `top_profiles` an. Die UI wird durch Entfernen des HTML-`checked`-Defaults daran angeglichen; `form.reset()` stellt dadurch auch bei „Neuer Fall“ automatisch `false` wieder her. Sichtbare Hilfen und Reviewkarte unterscheiden Screening-Pool, Top-N-Profilwahl, Phase-2-Detail-`top_k`, ReportDETAIL und die ownergebundene sichtbare Top-Profilliste ohne eine Aenderung der Scoreformel zu behaupten.

**Tech Stack:** HTML5, Vanilla JavaScript, Python `html.parser`, pytest, Node/VM, Playwright.

---

## Verbindlicher Wirkungsvertrag

- Backend-, Preview- und Workbench-Default sind `adaptive_limits=false`.
- Alle Profile des gewaehlten Levels bleiben im initialen Screening-Pool.
- Top-N bestimmt weiterhin, welche Profile vollstaendig in Phase 2 analysiert werden.
- Nur nach Opt-in wird der interne Phase-2-Detailumfang je ausgewaehltem Profil auf `min(top_k, max(32, top_n * 16))` begrenzt.
- Nur nach Opt-in wird die ownergebundene `top_profiles`-Ergebnisliste auf hoechstens 5 Eintraege begrenzt.
- Der Phase-2-Detail-Cap kann ReportDETAIL reduzieren. Der sitzungsuebergreifende historische Katalog `GET /api/reports` bleibt unveraendert und liegt ausdruecklich ausserhalb des jobgebundenen Caps.
- Die vorhandene Scoreformel und die Reihenfolge der uebergebenen Treffer werden nicht veraendert; durch abgeschnittene Detail- oder Displaymengen koennen sichtbare Detailtreffer fehlen.
- Review und Hilfe nennen den aktiven oder inaktiven Zustand vor dem Scan explizit.
- Kein Commit, Staging oder Push ohne ausdrueckliche Nutzerfreigabe.

## Dateien und Verantwortlichkeiten

| Datei | Verantwortung |
|---|---|
| `tests/test_workbench_adaptive_limits.py` | HTML-/Copy-/Defaultvertrag und integrativer ownergebundener Ergebnis-Endpunktvertrag |
| `apps/web/static/index.html` | Default-off und vollstaendige technisch korrekte Erklaerung |
| `apps/web/static/workbench-render.js` | Explizite Wirkung in der Reviewkarte |
| `apps/web/main.py` | Top-N und Opt-in aus dem Job-Snapshot lesen und `top_profiles` jobgebunden begrenzen |
| `tests/test_topn_cli_phase1_options.py` | Phase-2-Detailcap und veraenderte Detailkandidatenmenge |
| `tests/test_web_display_scores.py` | Display-Cap ohne Score- oder Reihenfolgenaenderung |
| `tests/browser/workbench.spec.js` | Erstladung, Payload, Review und „Neuer Fall“ im Browser |

`apps/web/contracts.py`, `apps/web/launcher.py`, `apps/cli/commands/scan.py` und `apps/web/display_scores.py` werden nur gelesen. Ihr bestehendes Verhalten wird durch Tests eingefroren; Gate 2 fuehrt dort keine neue Logik ein.

`ReportCatalog` und `GET /api/reports` werden nicht geaendert. Der globale historische Berichtskatalog besitzt keine `job_id` und darf nicht aus dem Zustand eines einzelnen Scans gekappt werden.

### Task 1: Gate-2-Default und Copy als RED-Vertrag festschreiben

**Files:**
- Create: `tests/test_workbench_adaptive_limits.py`
- Read: `apps/web/static/index.html`
- Read: `apps/web/contracts.py`

- [ ] **Step 1: HTML-Parser und Defaultvertrag anlegen**

```python
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

from apps.web.contracts import Phase1ScanRequest


ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "apps" / "web" / "static" / "index.html"
RENDER_JS = ROOT / "apps" / "web" / "static" / "workbench-render.js"


class AdaptiveLimitsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.control: dict[str, str | None] | None = None
        self.help_parts: list[str] = []
        self._inside_help = False

    def handle_starttag(self, tag, attrs) -> None:
        attributes = dict(attrs)
        if tag == "input" and attributes.get("name") == "adaptive_limits":
            self.control = attributes
        if attributes.get("id") == "adaptive-limits-help":
            self._inside_help = True

    def handle_endtag(self, tag) -> None:
        if self._inside_help and tag == "p":
            self._inside_help = False

    def handle_data(self, data) -> None:
        if self._inside_help and data.strip():
            self.help_parts.append(" ".join(data.split()))
```

- [ ] **Step 2: Default-off und Pflichtaussagen testen**

```python
def test_adaptive_limits_default_and_help_match_product_contract() -> None:
    parser = AdaptiveLimitsParser()
    parser.feed(INDEX_HTML.read_text(encoding="utf-8"))

    assert Phase1ScanRequest.model_fields["adaptive_limits"].default is False
    assert parser.control is not None
    assert "checked" not in parser.control
    assert parser.control.get("aria-describedby") == "adaptive-limits-help"

    help_text = " ".join(parser.help_parts)
    for marker in (
        "Standard: aus",
        "Screening-Pool",
        "Top-N",
        "Phase-2-Detailumfang",
        "max(32, Top-N × 16)",
        "höchstens 5",
        "Scoreformel",
    ):
        assert marker in help_text
```

- [ ] **Step 3: Test ausfuehren und RED bestaetigen**

Run:

```cmd
set "PYTHONUTF8=1" && set "PYTHONIOENCODING=utf-8" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_adaptive_limits.py -q --tb=short
```

Expected: FAIL, weil das HTML-Control noch `checked` ist und die bestehende Gate-1-Copy noch „derzeit aktiv“ nennt.

### Task 2: Reviewwirkung als RED-Vertrag festschreiben

**Files:**
- Modify: `tests/test_workbench_render_js.py`
- Read: `apps/web/static/workbench-render.js`

- [ ] **Step 1: Node/VM-Test fuer beide Reviewzustaende ergaenzen**

Der Test erstellt die vier Reviewkarten als minimale DOM-Doubles, fuehrt `renderReviewCards()` zweimal aus und prueft:

```javascript
window.MorphicWorkbenchRender.renderReviewCards(
  {adaptive_limits: false},
  {components: {}},
);
if (!cards["#review-profile"].textContent.includes(
  "aus (voller angeforderter Detailumfang; ownergebundene Top-Profile bis Top-N)"
)) throw new Error("default-off effect is not visible in review");

window.MorphicWorkbenchRender.renderReviewCards(
  {adaptive_limits: true},
  {components: {}},
);
if (!cards["#review-profile"].textContent.includes(
  "aktiv (Phase-2-Detail-Cap; höchstens 5 ownergebundene Top-Profile)"
)) throw new Error("opt-in effect is not visible in review");
```

Der Python-Test startet dieses Skript mit `subprocess.run(["node", "-e", script], ...)` und verlangt `returncode == 0`.

- [ ] **Step 2: Fokussierten Test ausfuehren und RED bestaetigen**

Run:

```cmd
set "PYTHONUTF8=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_render_js.py::test_review_cards_explain_both_adaptive_limits_states -q --tb=short
```

Expected: FAIL, weil die Reviewkarte bisher nur `ja` beziehungsweise `nein` anzeigt.

### Task 3: Bestehende CLI- und Displaywirkung ausdruecklich einfrieren

**Files:**
- Modify: `tests/test_topn_cli_phase1_options.py`
- Modify: `tests/test_web_display_scores.py`
- Read: `apps/cli/commands/scan.py:496-501`
- Read: `apps/web/display_scores.py:19-45`

- [ ] **Step 1: Detailkandidatenmenge ohne und mit Opt-in testen**

Erweitere `test_adaptive_limits_reduce_detail_top_k_without_starving_reports()`:

```python
detail_candidates = list(range(192))
without_limits = detail_candidates[
    :_effective_adaptive_top_k(192, top_n=7, adaptive_limits=False)
]
with_limits = detail_candidates[
    :_effective_adaptive_top_k(192, top_n=7, adaptive_limits=True)
]

assert without_limits == detail_candidates
assert with_limits == detail_candidates[:112]
assert 191 in without_limits
assert 191 not in with_limits
```

- [ ] **Step 2: Display-Cap ohne Scoremutation testen**

Ergaenze `test_display_score_helpers_round_visible_scores_and_preserve_raw_values()`:

```python
ranked = [
    {"profile": f"P{index}", "score": 10.0 - index}
    for index in range(9)
]
assert limit_display_items(ranked, top_n=9, adaptive_limits=False) == ranked
assert limit_display_items(ranked, top_n=9, adaptive_limits=True) == ranked[:5]
assert [item["score"] for item in ranked] == [10.0 - index for index in range(9)]
```

- [ ] **Step 3: Wirkungsvertraege ausfuehren**

Run:

```cmd
set "PYTHONUTF8=1" && set "OPENBLAS_NUM_THREADS=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_topn_cli_phase1_options.py tests/test_web_display_scores.py -q --tb=short
```

Expected: PASS. Diese Tests frieren vorhandene Logik ein; ein Fehlschlag waere vor jeder Produktionscodeaenderung als Vertragsabweichung zu untersuchen.

### Task 4: Browser-RED fuer Erstladung und „Neuer Fall“ belegen

**Files:**
- Modify: `tests/browser/workbench.spec.js`

- [ ] **Step 1: Browsertest ergaenzen**

```javascript
test('adaptive limits sind initial und nach neuem Fall bewusst aus', async ({page}) => {
  const errors = captureErrors(page);
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');

  const adaptive = page.locator('[name="adaptive_limits"]');
  await expect(adaptive).not.toBeChecked();
  expect(await page.evaluate(() => formScanPayload().adaptive_limits)).toBe(false);

  await page.evaluate(() => enterStep(3, false));
  await adaptive.check();
  expect(await page.evaluate(() => formScanPayload().adaptive_limits)).toBe(true);
  await page.evaluate(() => MorphicWorkbenchRender.renderReviewCards(
    formScanPayload(), {components: {}}
  ));
  await expect(page.locator('#review-profile')).toContainText(
    'aktiv (Phase-2-Detail-Cap; höchstens 5 ownergebundene Top-Profile)'
  );

  expect(await page.evaluate(() => resetWorkbenchForNewCase())).toBe(true);
  await expect(adaptive).not.toBeChecked();
  expect(await page.evaluate(() => formScanPayload().adaptive_limits)).toBe(false);
  expect(errors).toEqual([]);
});
```

- [ ] **Step 2: Browser-RED vor dem HTML-Patch belegen**

Run:

```cmd
call npm --prefix tests/browser test -- --grep "adaptive limits sind initial"
```

Expected: FAIL wegen initial gesetzter Checkbox.

### Task 5: Minimalen UI-Patch implementieren und GREEN belegen

**Files:**
- Modify: `apps/web/static/index.html:307,371-372`
- Modify: `apps/web/static/workbench-render.js:301-309`
- Modify: `apps/web/main.py:1249-1334`
- Test: `tests/test_workbench_adaptive_limits.py`
- Test: `tests/browser/workbench.spec.js`

- [ ] **Step 1: HTMLdefault auf aus stellen**

Entferne ausschliesslich das boolesche Attribut `checked`:

```html
<input form="scan-form" name="adaptive_limits" type="checkbox" aria-describedby="adaptive-limits-help">
```

- [ ] **Step 2: Technisch korrekte Hilfe einsetzen**

Die sichtbare Hilfe muss in ganzen Saetzen abdecken:

```html
<strong>Zweck:</strong> Den internen Phase-2-Detailumfang und die ownergebundene sichtbare Top-Profilliste bewusst begrenzen.
<strong>Standard:</strong> aus.
<strong>Auswirkung:</strong> Alle Profile des Levels bleiben im Screening-Pool und Top-N bestimmt weiterhin die vollstaendig analysierten Profile; nur der Detailumfang je ausgewaehltem Profil wird auf hoechstens max(32, Top-N × 16) begrenzt. Dadurch kann ReportDETAIL weniger Detailtreffer enthalten, und die ownergebundene sichtbare Top-Profilliste zeigt hoechstens 5 Treffer.
<strong>Keine Auswirkung:</strong> Screening-Pool und Top-N-Profilwahl werden nicht geaendert. Scoreformel und Reihenfolge werden nicht geaendert. Der globale Berichtskatalog bleibt unveraendert; durch gekuerzte Detail- und Displaymengen koennen sichtbare Detailtreffer fehlen.
<strong>Datenschutz-/Hardwaregrenze:</strong> Reiner lokaler Umfangsparameter ohne zusaetzliche Datenspeicherung oder Hardwareaktivierung.
```

- [ ] **Step 3: Reviewtext fuer beide Zustaende praezisieren**

```javascript
["Adaptive Limits", formData.adaptive_limits
  ? "aktiv (Phase-2-Detail-Cap; höchstens 5 ownergebundene Top-Profile)"
  : "aus (voller angeforderter Detailumfang; ownergebundene Top-Profile bis Top-N)"],
```

- [ ] **Step 3a: Ownergebundenen Ergebnis-Cap verdrahten**

Der echte `GET /api/scan/jobs/{job_id}/results` akzeptiert `job["command"]` nur als `list[str]`, verlangt genau ein vollstaendiges `--top-n` und verwirft doppelte oder widerspruechliche Adaptive-/Fixed-Flags zentral als mehrdeutig. Ein einzelnes `--fixed-limits` oder kein Limitflag bedeutet ausdruecklich Adaptive Limits aus. `adaptive_result_limit(top_n, adaptive_limits)` begrenzt ausschliesslich `top_profiles`. Typungueltige, mehrdeutige und Legacy-/Testjobs ohne gueltiges `--top-n` behalten den bisherigen Grenzwert 10 und behandeln Adaptive Limits als aus. Top-level `top_resonances`, `ReportCatalog` und `GET /api/reports` bleiben unveraendert.

Der integrative RED-/GREEN-Vertrag erzeugt neun echte `*_multiplex_scan.json`-Artefakte und ruft den ownergebundenen Endpoint auf: ohne Opt-in neun Profile, mit Opt-in exakt die ersten fuenf bei unveraenderten Scores und unveraenderter Reihenfolge.

- [ ] **Step 4: Gate-2-Vertrag und Browserfall gruen ausfuehren**

Run:

```cmd
set "PYTHONUTF8=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_adaptive_limits.py tests/test_topn_cli_phase1_options.py tests/test_web_display_scores.py tests/test_workbench_render_js.py::test_review_cards_explain_both_adaptive_limits_states -q --tb=short
call npm --prefix tests/browser test -- --grep "adaptive limits sind initial"
```

Expected: Beide Befehle bestehen.

### Task 6: Regression, Reviews und Abnahme

**Files:**
- Verify only: gesamter Gate-2-Scope

- [ ] **Step 1: Fokussierte Nachbarmatrix ausfuehren**

```cmd
set "PYTHONUTF8=1" && set "PYTHONIOENCODING=utf-8" && set "OPENBLAS_NUM_THREADS=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_adaptive_limits.py tests/test_workbench_option_explanations.py tests/test_topn_cli_phase1_options.py tests/test_web_display_scores.py tests/test_web_contracts.py tests/test_web_launcher.py tests/test_web_shell.py tests/test_web_scan_job_ownership.py tests/test_workbench_render_js.py tests/test_workbench_review_regressions.py -q --tb=short
```

- [ ] **Step 2: Syntax und Diff pruefen**

```cmd
node --check apps/web/static/workbench-render.js
node --check tests/browser/workbench.spec.js
git diff --check -- apps/web/main.py apps/web/static/index.html apps/web/static/workbench-render.js tests/test_workbench_adaptive_limits.py tests/test_topn_cli_phase1_options.py tests/test_web_display_scores.py docs/superpowers/plans/2026-07-26-workbench-gate2-adaptive-limits.md
```

- [ ] **Step 3: Vollstaendige Browser- und Python-Suite ausfuehren**

```cmd
call npm --prefix tests/browser test
set "PYTHONUTF8=1" && set "PYTHONIOENCODING=utf-8" && set "OPENBLAS_NUM_THREADS=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests -q --tb=short
```

- [ ] **Step 4: Zwei getrennte Reviews durchfuehren**

Zuerst Spec-Compliance gegen den verbindlichen Wirkungsvertrag pruefen. Erst nach APPROVE folgt Code-Quality-Review auf Funktionsfehler, Accessibility, falsche Claims, Testluecken und unbeabsichtigte Scope-Erweiterung. Alle Critical/Important Findings werden vor Abnahme behoben und erneut geprueft.

## Abschlussgrenze

Gate 2 geht nur in manuelle Abnahme, wenn Erstladung und „Neuer Fall“ `false` liefern, Opt-in-Wirkung in Hilfe und Review korrekt sichtbar ist, der ownergebundene Ergebnisendpunkt 9 beziehungsweise 5 unveraenderte Top-Profile liefert, der globale Berichtskatalog unangetastet bleibt, die bestehenden CLI-/Display-Caps unveraendert nachgewiesen sind, alle fokussierten und vollstaendigen Tests gruen sind und beide Reviews keine offenen Critical/Important Findings enthalten.
