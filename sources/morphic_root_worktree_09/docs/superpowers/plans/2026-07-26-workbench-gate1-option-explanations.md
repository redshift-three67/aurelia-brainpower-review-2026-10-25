# Workbench Gate 1 Option Explanations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Alle aktuell vorhandenen optionalen oder wirkungsändernden Workbench-Funktionen erhalten eine sichtbare, verständliche und programmatisch verknüpfte Erklärung; die maximale Harmonisierungsdauer von 441 Minuten erfordert eine ausdrückliche Bestätigung.

**Architecture:** Statische Controls werden in `index.html` über gruppierte Hilfetexte und `aria-describedby` verbunden. Dynamische Auswahlkarten erhalten in `workbench-render.js` getrennte zugängliche Namen und Beschreibungen. `app.js` ergänzt ausschließlich den Maximaldauer-Startschutz; Scanpayloads, Defaults, Scoring, Backendverträge und Persistenz bleiben unverändert.

**Tech Stack:** HTML5, ARIA, Vanilla JavaScript, Python `html.parser`, pytest, Node/VM-Tests, Playwright.

---

## Scope-Grenzen

- Gate 1 verändert den fehlerhaften Adaptive-Limits-Default noch nicht; das ist Gate 2.
- Gate 1 aktiviert keine EMF-Telemetrie; das ist Gate 5.
- Gate 1 aktiviert keine lokale KI und ändert den aktuellen `--llm`-Pfad noch nicht; das ist Gate 7.
- Gate 1 führt keinen Geschlechts-/Profilfilter ein; das ist Gate 12.
- Gate 1 ändert keine Harmonisierungssequenz; das ist Gate 13.
- EMF, lokale KI und Profilkontext erhalten nur sichtbare Statuswahrheit: derzeit nicht auswählbar beziehungsweise default-off.
- Kein Commit oder Staging ohne ausdrückliche Nutzerfreigabe.

## Dateien und Verantwortlichkeiten

| Datei | Verantwortung |
|---|---|
| `tests/test_workbench_option_explanations.py` | Neuer fokussierter RED/GREEN-Vertrag für statische Hilfen, ARIA-Verknüpfung, dynamische Auswahlkarten und Maximaldauer-Schutz |
| `apps/web/static/index.html` | Sichtbare Hilfetexte, eindeutige IDs, `aria-describedby`, Statuswahrheit und 441-Minuten-Bestätigung |
| `apps/web/static/workbench-render.js` | Eindeutige IDs sowie getrennte `aria-labelledby`-/`aria-describedby`-Semantik für dynamische Radio-Karten |
| `apps/web/static/app.js` | Schutz vor Start mit Dauerfaktor 21 ohne ausdrückliche Bestätigung; wahrheitsgetreue Solfeggio-Kurztexte |
| `tests/browser/workbench.spec.js` | Browserabnahme für zugängliche Beschreibungen, mobile Breite und 441-Minuten-Bestätigung |

`apps/web/static/app.css` wird nicht geändert. Die bestehenden Klassen `.field-hint`, `.hint-box`, `.notice.warn`, `.checkline` und `.inline-state` reichen aus.

### Task 1: Statischen Gate-1-Vertrag als RED-Test festschreiben

**Files:**
- Create: `tests/test_workbench_option_explanations.py`
- Read: `apps/web/static/index.html`
- Read: `apps/web/static/app.js`

- [ ] **Step 1: Parser und Pflichtmatrix anlegen**

Die Testdatei beginnt mit:

```python
from __future__ import annotations

from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "apps" / "web" / "static" / "index.html"
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"


class OptionHelpParser(HTMLParser):
    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[tuple[str, dict[str, str | None]]] = []
        self.id_counts: Counter[str] = Counter()
        self.text_parts: dict[str, list[str]] = defaultdict(list)
        self._tags: list[str] = []
        self._open_ids: list[tuple[str, int]] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        self.elements.append((tag, attributes))
        element_id = attributes.get("id")
        if element_id:
            self.id_counts[element_id] += 1
        if tag not in self.VOID_TAGS:
            self._tags.append(tag)
            if element_id:
                self._open_ids.append((element_id, len(self._tags)))

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        self.elements.append((tag, attributes))
        element_id = attributes.get("id")
        if element_id:
            self.id_counts[element_id] += 1

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if not text:
            return
        for element_id, _depth in self._open_ids:
            self.text_parts[element_id].append(text)

    def handle_endtag(self, tag: str) -> None:
        self._open_ids = [
            item for item in self._open_ids if item[1] != len(self._tags)
        ]
        if self._tags:
            self._tags.pop()

    def by_id(self, element_id: str) -> dict[str, str | None]:
        for _tag, attributes in self.elements:
            if attributes.get("id") == element_id:
                return attributes
        raise AssertionError(f"missing element id: {element_id}")

    def by_name(self, name: str) -> dict[str, str | None]:
        for _tag, attributes in self.elements:
            if attributes.get("name") == name:
                return attributes
        raise AssertionError(f"missing element name: {name}")

    def text_by_id(self, element_id: str) -> str:
        return " ".join(self.text_parts[element_id])


HELP_LINKS = {
    "focus-history-help": [("id", "focus-history-consent"), ("id", "clear-focus-history")],
    "main-symptom-help": [("name", "main_symptom")],
    "client-context-help": [
        ("name", "birth_time"), ("name", "email"), ("name", "notes"),
        ("id", "context-persistence-consent"), ("id", "save-client-context-button"),
    ],
    "group-draft-help": [
        ("id", "group-draft-label"), ("id", "group-draft-members"),
        ("id", "group-members-consent"), ("id", "group-persistence-consent"),
        ("id", "group-analysis-consent"), ("id", "save-group-draft-button"),
        ("id", "group-erasure-dry-run-button"), ("id", "delete-group-draft-button"),
        ("id", "group-delete-confirmation"),
    ],
    "group-consent-help": [
        ("id", "group-identity-first-name"), ("id", "group-identity-last-name"),
        ("id", "group-identity-birth-date"), ("id", "group-identity-birth-place"),
        ("id", "group-identity-retention-days"),
        ("id", "group-identity-persistence-consent"),
        ("id", "register-group-identity-button"), ("id", "group-consent-client-id"),
        ("id", "group-consent-valid-until"), ("id", "group-consent-confirmation"),
        ("id", "enable-group-consent-button"), ("id", "revoke-group-consent-button"),
    ],
    "group-policy-help": [
        ("id", "group-analysis-strength"), ("id", "save-group-analysis-policy-button"),
    ],
    "group-activation-help": [
        ("id", "group-scan-activation-enabled"), ("id", "group-scan-draft-id"),
    ],
    "reference-image-help": [("id", "image-file-input"), ("id", "image-path-input")],
    "planetary-vector-help": [
        ("name", "planetary_vector_enabled"), ("name", "planet_type"),
    ],
    "profile-template-help": [("id", "profile-template-choices")],
    "entropy-mode-help": [("id", "entropy-mode-choices")],
    "adaptive-limits-help": [("name", "adaptive_limits")],
    "workbench-mode-help": [("id", "workbench-mode")],
    "emf-help": [("id", "realtime-calibration")],
    "harmonization-intention-help": [("name", "intention")],
    "harmonization-frequency-help": [
        ("name", "target_frequency"), ("id", "solfeggio-base-choices"),
    ],
    "harmonization-cycle-help": [("name", "pulse_seconds"), ("name", "pause_seconds")],
    "harmonization-duration-help": [("name", "duration_factor")],
    "harmonization-hardware-help": [
        ("name", "use_cpu"), ("name", "use_gpu"), ("name", "use_ram"),
        ("name", "use_websocket"), ("name", "use_driver_layer"),
    ],
    "template-persistence-help": [
        ("id", "template-sensitive-consent"), ("id", "save-template-button"),
    ],
}
```

- [ ] **Step 2: Vollständige sichtbare Verknüpfung testen**

```python
def _parser() -> OptionHelpParser:
    parser = OptionHelpParser()
    parser.feed(INDEX_HTML.read_text(encoding="utf-8"))
    return parser


def test_static_option_controls_have_complete_linked_explanations() -> None:
    parser = _parser()
    markers = (
        "Zweck:", "Standard:", "Auswirkung:", "Keine Auswirkung:",
        "Datenschutz-/Hardwaregrenze:",
    )

    for help_id, controls in HELP_LINKS.items():
        assert parser.id_counts[help_id] == 1
        help_attributes = parser.by_id(help_id)
        assert "hidden" not in help_attributes
        assert help_attributes.get("aria-hidden") != "true"
        help_text = parser.text_by_id(help_id)
        for marker in markers:
            assert marker in help_text, f"{help_id}: missing {marker}"

        for kind, value in controls:
            attributes = parser.by_id(value) if kind == "id" else parser.by_name(value)
            described_by = str(attributes.get("aria-describedby") or "").split()
            assert help_id in described_by, f"{kind}={value} not linked to {help_id}"
```

- [ ] **Step 3: Lokale Speichergrenzen und technische Begriffe testen**

```python
def test_local_options_explain_storage_retention_deletion_and_scan_effect() -> None:
    parser = _parser()
    for help_id in (
        "focus-history-help", "client-context-help", "group-draft-help",
        "group-consent-help", "group-policy-help", "group-activation-help",
        "template-persistence-help",
    ):
        text = parser.text_by_id(help_id)
        for marker in ("Speicherort:", "Aufbewahrung:", "Löschweg:", "Aktueller Scan:"):
            assert marker in text, f"{help_id}: missing {marker}"

    draft_text = parser.text_by_id("group-draft-help")
    assert "DPAPI" in draft_text
    assert "an dieses Windows-Benutzerkonto gebundene Verschlüsselung" in draft_text

    policy_text = parser.text_by_id("group-policy-help")
    assert "Kill-Switch" in policy_text
    assert "serverseitiger Not-Aus-Schalter" in policy_text
    assert "Policy-Kandidat" in policy_text
    assert "nur vorgemerkter Vorschlag" in policy_text
    assert "0 = keine Gruppenwirkung" in policy_text
    assert "1 = volle angeforderte Gruppenwirkung" in policy_text
```

- [ ] **Step 4: Fehlende künftige Controls als ehrliche Statusflächen testen**

```python
def test_future_optional_features_are_explained_without_premature_controls() -> None:
    parser = _parser()
    local_ai = parser.text_by_id("local-ai-help")
    profile_context = parser.text_by_id("profile-context-help")

    assert "derzeit nicht auswählbar" in local_ai
    assert "Gate 7" in local_ai
    assert "derzeit nicht auswählbar" in profile_context
    assert "Gate 12" in profile_context

    assert not any(attributes.get("name") == "local_ai_enabled" for _, attributes in parser.elements)
    assert not any(attributes.get("name") == "profile_context" for _, attributes in parser.elements)
```

- [ ] **Step 5: Test ausführen und erwartetes RED bestätigen**

Run:

```powershell
$env:PYTHONUTF8 = "1"
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_option_explanations.py -q
```

Expected: FAIL, weil die Help-IDs und `aria-describedby`-Verknüpfungen noch fehlen. Ein Import-, Syntax- oder Parserfehler ist kein gültiges RED.

### Task 2: Statische Erklärungen minimal in HTML ergänzen

**Files:**
- Modify: `apps/web/static/index.html:156-235`
- Modify: `apps/web/static/index.html:242-258`
- Modify: `apps/web/static/index.html:294-369`
- Modify: `apps/web/static/index.html:387-402`
- Modify: `apps/web/static/index.html:586-645`
- Test: `tests/test_workbench_option_explanations.py`

- [ ] **Step 1: Bestehende Hilfetexte mit eindeutigen IDs versehen und Controls verbinden**

Für jede Gruppe aus `HELP_LINKS` gilt dasselbe Muster:

```html
<input id="focus-history-consent" type="checkbox" aria-describedby="focus-history-help">
<button id="clear-focus-history" type="button" aria-describedby="focus-history-help">...</button>
<p id="focus-history-help" class="field-hint">
  <strong>Zweck:</strong> Bis zu acht frühere Fokus-Texte in diesem Browser wiederverwenden.
  <strong>Standard:</strong> aus.
  <strong>Auswirkung:</strong> Eine Auswahl übernimmt den Text in das Fokusfeld.
  <strong>Keine Auswirkung:</strong> Die Historie startet keinen Scan und ändert keine Scores selbst.
  <strong>Datenschutz-/Hardwaregrenze:</strong> Nur Browser-localStorage, kein Hardwarezugriff.
  <strong>Speicherort:</strong> localStorage dieses Browsers.
  <strong>Aufbewahrung:</strong> höchstens acht Einträge ohne Zeitautomatik.
  <strong>Löschweg:</strong> Löschtaste oder Deaktivieren der Freigabe.
  <strong>Aktueller Scan:</strong> nur der in das Fokusfeld übernommene Text wirkt.
</p>
```

Mehrere Controls dürfen denselben Gruppenhinweis referenzieren. Jeder Help-ID-Wert kommt exakt einmal vor.

- [ ] **Step 2: Wahrheitsgetreue Pflichttexte verwenden**

Die folgenden Aussagen sind verbindlich:

| Help-ID | Verbindliche Kernaussage |
|---|---|
| `main-symptom-help` | Standard leer; wird mit Fokus kombiniert; kann Profilpriorisierung und Berichtstext ändern; keine Diagnose |
| `client-context-help` | Kein Scan-/Scoreeffekt; Speicherung nur nach Freigabe als lokale tenantgebundene JSON-Datei; kein UI-Löschweg; neuer Fall löscht den Entwurf nicht |
| `group-draft-help` | DPAPI als an das Windows-Benutzerkonto gebundene Verschlüsselung erklären; 30 Tage Metadatenfrist; Dry-Run löscht nichts; keine automatische Scanwirkung |
| `group-consent-help` | Sensible Identität erst nach Freigabe lokal DPAPI-geschützt; Standard 365 Tage; Widerruf löscht nicht Identität oder Entwurf |
| `group-policy-help` | Gruppenstärke 0 bis 1 erklären; Policy-Kandidat = nur vorgemerkter Vorschlag; Kill-Switch = serverseitiger Not-Aus-Schalter; nur Prozessspeicher |
| `group-activation-help` | Standard aus; nur realer nächster Scan; Preview/Templates bleiben gruppenfrei; alle Gates bleiben erforderlich |
| `reference-image-help` | Kein Upload; nur Dateiname/Pfad; serverseitig erreichbare JPG-Datei kann einen Analysevektor und damit Scores beeinflussen |
| `planetary-vector-help` | Standard aus; deterministisch aus der Bezeichnung erzeugte Rate; keine Astronomie-, Standort- oder Sensormessung |
| `profile-template-help` | Standard Phase-1; verändert persönliche Achsen und nur passende Vektorvergleiche; keine Speicher-/Hardwarewirkung |
| `entropy-mode-help` | Standard Legacy; Enhanced/Hybrid können Entropie-Fallbacks einschließlich Netzwerk-Timing verwenden; keine EMF-Messung |
| `adaptive-limits-help` | Aktueller UI-Standard noch aktiv bis Gate 2; begrenzt Detail-/Exportumfang, nicht Profilpool oder Scoreformel |
| `workbench-mode-help` | Standard Standard; Expert zeigt zusätzliche Warnungen; keine Score-/Hardwareaktivierung |
| `emf-help` | System-/Entropie-basierter EMF-Proxy; default-off; derzeit keine Workbench-Aktivierung; kein Nullwert bei fehlender Messung |
| `harmonization-intention-help` | Organisatorische Kennzeichnung; keine nachgewiesene therapeutische Wirkung; kein rückwirkender Scan-Effekt |
| `harmonization-frequency-help` | Rechen-/Speicher-Timingziel; kein Ton oder physisches Feld; Solfeggio-Karten setzen dasselbe Frequenzfeld |
| `harmonization-cycle-help` | Impuls = lokale Rechenphase, Pause = Wartezeit; kein physischer Impuls und kein Scan-Effekt |
| `harmonization-duration-help` | Faktor ×21 Minuten; 21 = 441 Minuten; Faktor 21 erfordert Bestätigung |
| `harmonization-hardware-help` | CPU reale Rechenlast; GPU nur CPU-simulierte Matrix; RAM ca. 10 MiB temporär; WebSocket simuliert; Driver Layer öffnet keine Geräte |
| `template-persistence-help` | Tenantgebundene lokale JSON-Datei; keine automatische Löschung; Gruppenaktivierung und optionaler Kontext nicht enthalten |

- [ ] **Step 3: Fehlende Funktionen nur als Statuswahrheit ergänzen**

In Phase 5 beziehungsweise beim Profilkontext werden keine Controls angelegt. Es werden nur sichtbare Hinweise ergänzt:

```html
<p id="local-ai-help" class="field-hint">
  <strong>Zweck:</strong> Lokale KI-Deutung transparent steuern.
  <strong>Standard:</strong> derzeit nicht auswählbar.
  <strong>Auswirkung:</strong> Gate 7 führt später ein ausdrückliches lokales Opt-in ein.
  <strong>Keine Auswirkung:</strong> Dieser Hinweis aktiviert keine KI und ändert keine Scores.
  <strong>Datenschutz-/Hardwaregrenze:</strong> Keine neue Datenübertragung oder Modellaktivierung in Gate 1.
</p>
<p id="profile-context-help" class="field-hint">
  <strong>Zweck:</strong> Optionalen Profilkontext transparent auswählen.
  <strong>Standard:</strong> derzeit nicht auswählbar; alle/neutral.
  <strong>Auswirkung:</strong> Gate 12 führt zuerst kuratierte Metadaten und Shadow-Vergleiche ein.
  <strong>Keine Auswirkung:</strong> Dieser Hinweis filtert keine Profile und ändert keine Scores.
  <strong>Datenschutz-/Hardwaregrenze:</strong> Keine Ableitung aus Name oder Geburtsdaten.
</p>
```

- [ ] **Step 4: Statischen Vertrag grün ausführen**

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_option_explanations.py -q
```

Expected: Die statischen Tests sind PASS; der dynamische Karten- und Maximaldauervertrag bleibt bis Tasks 3/4 RED.

### Task 3: Dynamische Choice-Cards zugänglich beschreiben

**Files:**
- Modify: `apps/web/static/workbench-render.js:486-543`
- Modify: `apps/web/static/app.js:1605-1610`
- Test: `tests/test_workbench_option_explanations.py`
- Test: `tests/test_workbench_render_js.py`

- [ ] **Step 1: Node/VM-RED-Test ergänzen**

Der Test rendert zwei Optionen in einen Container mit `id="profile-template-choices"` und `aria-describedby="profile-template-help"`. Er prüft:

```javascript
const labelledBy = card.getAttribute("aria-labelledby");
const describedBy = card.getAttribute("aria-describedby").split(/\s+/);
if (!labelledBy) throw new Error("missing aria-labelledby");
if (!describedBy.includes("profile-template-help")) throw new Error("missing group help");
if (!describedBy.some((id) => id.endsWith("-hint"))) throw new Error("missing option hint");
if (!document.getElementById(labelledBy)) throw new Error("broken accessible label");
for (const id of describedBy) {
  if (!document.getElementById(id)) throw new Error(`broken description: ${id}`);
}
```

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_option_explanations.py -q
```

Expected: FAIL wegen fehlender IDs und ARIA-Beziehungen.

- [ ] **Step 2: Minimalen Renderer implementieren**

In `renderChoiceCards()`:

```javascript
const valueToken = String(opt.value).replace(/[^A-Za-z0-9_-]+/g, "-");
const titleId = `${container.id}-${valueToken}-title`;
const hintId = `${container.id}-${valueToken}-hint`;
title.id = titleId;
hint.id = hintId;
card.setAttribute("aria-labelledby", titleId);
const sharedDescriptionIds = String(container.getAttribute("aria-describedby") || "")
  .split(/\s+/)
  .filter(Boolean);
card.setAttribute("aria-describedby", [hintId, ...sharedDescriptionIds].join(" "));
```

Keine Änderung an Click-, Tastatur-, Fokus- oder Auswahlsemantik.

- [ ] **Step 3: Solfeggio-Kurztexte auf reale Semantik korrigieren**

```javascript
const SOLFEGGIO_BASE_OPTIONS = [
  { value: "432", label: "432 Hz", hint: "Setzt das gemeinsame Frequenzfeld auf 432 Hz." },
  { value: "528", label: "528 Hz", hint: "Setzt das gemeinsame Frequenzfeld auf 528 Hz." },
  { value: "429.62", label: "429.62 Hz", hint: "Setzt das gemeinsame Frequenzfeld auf 429,62 Hz." },
  { value: "498.90", label: "498.90 Hz", hint: "Setzt das gemeinsame Frequenzfeld auf 498,90 Hz." },
];
```

- [ ] **Step 4: Renderer- und Nachbartests grün ausführen**

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_option_explanations.py tests/test_workbench_render_js.py tests/test_workbench_review_regressions.py -q
node --check apps/web/static/workbench-render.js
node --check apps/web/static/app.js
```

Expected: PASS ohne Warnungen oder JavaScript-Syntaxfehler.

### Task 4: Maximaldauer 441 Minuten ausdrücklich bestätigen

**Files:**
- Modify: `apps/web/static/index.html:586-618`
- Modify: `apps/web/static/app.js:1110-1164`
- Test: `tests/test_workbench_option_explanations.py`

- [ ] **Step 1: RED-Vertrag für Bestätigung und Guard ergänzen**

```python
def test_maximum_harmonization_duration_requires_confirmation_before_start() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    app = APP_JS.read_text(encoding="utf-8")
    form = html.split('<form id="harmonization-form"', 1)[1].split("</form>", 1)[0]
    assert 'id="harmonization-max-duration-confirmation"' in form
    assert "441 Minuten" in form
    assert 'id="harmonization-confirmation-state"' in html

    start = app.split("async function startHarmonizationJob", 1)[1].split(
        "async function pollHarmonizationJob", 1
    )[0]
    assert "body.duration_factor === 21" in start
    assert "harmonization-max-duration-confirmation" in start
    assert start.index("harmonization-max-duration-confirmation") < start.index(
        "MorphicWorkbenchApi.startHarmonization"
    )
```

Run:

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_option_explanations.py -q
```

Expected: FAIL, weil Checkbox, Statusfläche und Guard fehlen.

- [ ] **Step 2: Bestätigung innerhalb des Formulars ergänzen**

```html
<label class="checkline">
  <input id="harmonization-max-duration-confirmation" type="checkbox" aria-describedby="harmonization-duration-help">
  <span>Maximaldauer von 441 Minuten ausdrücklich bestätigen</span>
</label>
<span id="harmonization-confirmation-state" class="inline-state" role="status" aria-live="polite"></span>
```

- [ ] **Step 3: Guard vor Operation-ID und API-Aufruf implementieren**

Unmittelbar nach `const body = formHarmonizationPayload();`:

```javascript
const maximumDurationConfirmed = $("#harmonization-max-duration-confirmation")?.checked === true;
if (body.duration_factor === 21 && !maximumDurationConfirmed) {
  const confirmationState = $("#harmonization-confirmation-state");
  if (confirmationState) {
    confirmationState.textContent = "Bitte die Maximaldauer von 441 Minuten ausdrücklich bestätigen.";
    confirmationState.className = "inline-state bad";
  }
  return;
}
```

Der Guard steht vor `startOperationId("harmonization")`. Für Faktoren 1-20 bleibt das Verhalten unverändert. Beim erfolgreichen Start wird die Statusfläche geleert.

- [ ] **Step 4: RED/GREEN-Vertrag und bestehende Harmonisierungsnachbarn ausführen**

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest `
  tests/test_workbench_option_explanations.py `
  tests/test_workbench_dogfood_reports_harmonization.py `
  tests/test_workbench_harmonization_status_dom.py -q
```

Expected: PASS; bestehende Faktoren 1 und 2 starten ohne neue Bestätigung.

### Task 5: Browserabnahme und Regression

**Files:**
- Modify: `tests/browser/workbench.spec.js`
- Test: `tests/test_workbench_option_explanations.py`

- [ ] **Step 1: Browser-RED-Test für zugängliche Beschreibungen hinzufügen**

Der Test prüft repräsentativ:

```javascript
for (const selector of [
  '#focus-history-consent',
  '[name="main_symptom"]',
  '#image-file-input',
  '[name="adaptive_limits"]',
  '#workbench-mode',
  '[name="duration_factor"]',
  '#template-sensitive-consent',
]) {
  const control = page.locator(selector);
  const ids = (await control.getAttribute('aria-describedby')).split(/\s+/).filter(Boolean);
  expect(ids.length).toBeGreaterThan(0);
  for (const id of ids) {
    await expect(page.locator(`#${id}`)).toContainText('Standard:');
  }
}

await expect(page.locator('#profile-template-choices [data-value="phase1-default"]'))
  .toHaveAccessibleName('Phase-1 Standard');
await expect(page.locator('#profile-template-choices [data-value="phase1-default"]'))
  .toHaveAccessibleDescription(/Standard:/);
```

Bei 375 px wird zusätzlich geprüft, dass kein horizontaler Dokumentoverflow entsteht.

- [ ] **Step 2: Browser-RED/GREEN-Test für Faktor 21 hinzufügen**

Der API-Aufruf wird im Browser gezählt. Ohne Bestätigung bleibt der Zähler `0` und die Statusfläche fordert die Bestätigung. Nach Setzen der Checkbox erfolgt genau ein Startaufruf.

- [ ] **Step 3: Fokussierte Python- und Browsermatrix ausführen**

```powershell
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:OPENBLAS_NUM_THREADS = "1"
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest `
  tests/test_workbench_option_explanations.py `
  tests/test_workbench_ui_quality_contracts.py `
  tests/test_workbench_dogfood_navigation_accessibility.py `
  tests/test_workbench_focus_history_privacy_js.py `
  tests/test_workbench_client_context_persistence.py `
  tests/test_workbench_planetary_vector_dom.py `
  tests/test_workbench_group_draft_dom.py `
  tests/test_workbench_group_consent_dom.py `
  tests/test_workbench_group_analysis_policy_dom.py `
  tests/test_workbench_group_activation_dom.py `
  tests/test_workbench_dogfood_reports_harmonization.py `
  tests/test_workbench_harmonization_status_dom.py `
  tests/test_workbench_render_js.py `
  tests/test_workbench_no_inner_html_js.py `
  tests/test_workbench_review_regressions.py -q
node --check apps/web/static/app.js
node --check apps/web/static/workbench-render.js
git diff --check
```

Playwright läuft auf einem neuen isolierten Server/Port, nicht auf dem akzeptierten Port 8765:

```powershell
$env:PLAYWRIGHT_BASE_URL = "http://127.0.0.1:8766"
npm --prefix tests/browser test -- --grep "optionale Funktionen|441 Minuten"
```

- [ ] **Step 4: Vollsuite auf unveränderten Bytes ausführen**

```powershell
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests -q --tb=short
```

Expected: Keine neue Regression gegenüber Freeze v6. Bestehende, nicht durch Gate 1 verursachte Worktree-Probleme werden separat dokumentiert und nicht durch Scope-Ausweitung behoben.

## Abschlussgrenze

Gate 1 ist erst technisch geschlossen, wenn:

- alle fokussierten Tests grün sind;
- der RED-Fehlschlag vor der Implementierung belegt wurde;
- die Browserabnahme auf Desktop und 375 px grün ist;
- keine Scanpayload-, Default-, Score-, Backend-, Persistenz- oder Hardwarewirkung außerhalb des 441-Minuten-Guards geändert wurde;
- die Vollsuite und statischen Checks auf unveränderten Bytes abgeschlossen sind;
- der Scope für Freeze und zwei unabhängige Reviews bereit ist.
