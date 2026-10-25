# Workbench Gate 3 Scanprofil-Pool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Die Workbench zeigt den tatsaechlich gescreenten internen Profilpool und nicht scanwirksame Registry-Quellen getrennt, durchsuchbar und wahrheitsgetreu an und bindet Preview sowie Start fail-closed an den geprueften Pool-Fingerprint.

**Architecture:** `core.profile_sync` bleibt die einzige Gate-3-Profilautoritaet. `apps/web/workbench.py` erzeugt aus dem geordneten internen Pool einen kanonischen SHA-256-Fingerprint und einen erweiterten Read-only-Katalog; `apps/web/main.py` validiert denselben Fingerprint vor Preview und vor jeder Startoperation. Das Frontend uebernimmt nur den serverseitigen Fingerprint fuer das aktuelle Level, sperrt Aktionen bei Loading/Error/Stale und rendert interne Profile sowie externe Registry-Quellen ohne Aktivierungsillusion.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, Vanilla JavaScript, HTML/CSS, pytest, Node/VM, Playwright.

---

## Scope und Referenz

Verbindliche Spec:

`docs/superpowers/specs/2026-07-27-workbench-gate3-scan-profile-pool-design.md`

Gate 3 aktiviert keine externen Profile, keinen Admin-Catalog-Provider und keine Netzwerkquelle. Die 16 Registry-aktiven Quellen bleiben `scan_effect=false`; produktive externe Integration bleibt Gate 14. Kein Commit, Staging oder Push ohne ausdrueckliche Nutzerfreigabe.

## Dateien und Verantwortlichkeiten

| Datei | Verantwortung |
|---|---|
| `apps/web/workbench.py` | Kanonischer Pool-Fingerprint und erweiterter Katalogresponse |
| `apps/web/contracts.py` | Requestfeld fuer den vollstaendigen Pool-Fingerprint |
| `apps/web/main.py` | Fail-closed Validierung vor Preview und Startoperation |
| `apps/web/static/workbench-state.js` | Aktueller Katalog-/Fingerprintzustand |
| `apps/web/static/app.js` | Payloadbindung, Levelinvalidierung und Aktionssperre |
| `apps/web/static/workbench-render.js` | Zusammenfassung, Badges, Suche, interne/externe Details und Fehlerzustaende |
| `apps/web/static/index.html` | Initial gesperrte Aktionen und statische Erklaerung |
| `apps/web/static/app.css` | Skeleton, Badges, Suchfeld und responsive Listen |
| `tests/test_web_scan_profile_catalog.py` | Backend-Katalog- und Fingerprintvertrag |
| `tests/test_workbench_scan_profile_pool_binding.py` | Preview-/Startbindung und Side-Effect-Grenzen |
| `tests/test_workbench_scan_profile_pool_js.py` | Frontend-State-, Payload-, Gate- und Rendervertrag |
| `tests/browser/workbench.spec.js` | Nutzerfluss, Suche, Retry, stale Response und Responsive-Abnahme |

### Task 1: Kanonischen Katalog- und Fingerprintvertrag per TDD implementieren

**Files:**
- Modify: `tests/test_web_scan_profile_catalog.py`
- Modify: `apps/web/workbench.py:1-108`

- [ ] **Step 1: RED-Tests fuer Stabilitaet und relevante Drift schreiben**

Erweitere `tests/test_web_scan_profile_catalog.py`:

```python
from apps.web.workbench import (
    build_scan_profile_catalog,
    build_scan_profile_pool_fingerprint,
)


def test_scan_profile_pool_fingerprint_is_stable_and_order_sensitive() -> None:
    profiles = [("a", "Alpha"), ("b", "Beta")]
    first = build_scan_profile_pool_fingerprint(3, profiles)

    assert first == build_scan_profile_pool_fingerprint(3, list(profiles))
    assert len(first) == 64
    assert first == first.lower()
    assert first != build_scan_profile_pool_fingerprint(4, profiles)
    assert first != build_scan_profile_pool_fingerprint(3, list(reversed(profiles)))
    assert first != build_scan_profile_pool_fingerprint(3, [("a", "Neu"), ("b", "Beta")])


def test_registry_sources_do_not_change_internal_pool_fingerprint() -> None:
    profiles = [("a", "Alpha")]
    without_sources = build_scan_profile_catalog(
        profile_level=3,
        internal_profiles=profiles,
        registry_sources=[],
    )
    with_sources = build_scan_profile_catalog(
        profile_level=3,
        internal_profiles=profiles,
        registry_sources=[_Source("external", "Extern", active=True)],
    )

    assert without_sources["pool_authority"]["fingerprint"] == (
        with_sources["pool_authority"]["fingerprint"]
    )
```

- [ ] **Step 2: RED fuer erweiterten Response schreiben**

Der bestehende Trennungstest muss mindestens pruefen:

```python
authority = catalog["pool_authority"]
assert catalog["schema_version"] == 1
assert authority == {
    "source": "legacy",
    "label": "Legacy",
    "revision": None,
    "revision_short": None,
    "fingerprint": authority["fingerprint"],
    "fingerprint_short": authority["fingerprint"][:12],
}
assert catalog["external"]["scan_effect"] is False
assert catalog["external"]["activation_available"] is False
assert catalog["external"]["activation_gate"] == "gate_14"
assert catalog["external"]["active_source_count"] == 1
assert catalog["external"]["active_sources"] == [{
    "id": "source-active",
    "label": "Aktive Referenzquelle",
    "scan_effect": False,
    "reason_code": "registry_metadata_only",
}]
```

- [ ] **Step 3: RED ausfuehren**

```cmd
set "PYTHONUTF8=1" && set "PYTHONIOENCODING=utf-8" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_web_scan_profile_catalog.py -q --tb=short
```

Expected: Import- oder Key-Fehler fuer den noch fehlenden Fingerprint-/Authority-Vertrag; bestehende Fehlerredaktion bleibt gruen.

- [ ] **Step 4: Minimalen Fingerprint implementieren**

In `apps/web/workbench.py`:

```python
import hashlib
import json


SCAN_PROFILE_POOL_SCHEMA_VERSION = 1


def build_scan_profile_pool_fingerprint(
    profile_level: int,
    internal_profiles: list[tuple[str, str]],
) -> str:
    canonical = {
        "schema_version": SCAN_PROFILE_POOL_SCHEMA_VERSION,
        "profile_level": int(profile_level),
        "pool_source": "legacy",
        "profiles": [
            {"id": str(profile_id), "label": str(label)}
            for profile_id, label in internal_profiles
        ],
    }
    encoded = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
```

`build_scan_profile_catalog()` berechnet den Fingerprint einmal, behaelt die interne Screening-Reihenfolge und ergaenzt exakt die Felder aus der Spec. `external.count` bleibt `0`; `active_source_count` ist `len(active_sources)`.

- [ ] **Step 5: Aktuellen internen Fingerprint-Provider ergaenzen**

```python
def current_scan_profile_pool_fingerprint(profile_level: int) -> str:
    profiles = get_top_n_analysis_profiles_by_level(profile_level)
    return build_scan_profile_pool_fingerprint(profile_level, profiles)
```

Diese Funktion liest absichtlich keine `SourceRegistry`, weil externe Quellen in Gate 3 keine Scanwirkung besitzen.

- [ ] **Step 6: GREEN ausfuehren**

```cmd
set "PYTHONUTF8=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_web_scan_profile_catalog.py -q --tb=short
```

Expected: PASS.

### Task 2: Preview und Start an den aktuellen Fingerprint binden

**Files:**
- Modify: `apps/web/contracts.py:16-39`
- Modify: `apps/web/main.py:29-35,101,976-1182`
- Create: `tests/test_workbench_scan_profile_pool_binding.py`
- Modify: zentrale Scanrequest-Fixtures unter `tests/`, soweit fuer das neue Pflichtfeld erforderlich

- [ ] **Step 1: RED fuer Requestsyntax schreiben**

In `tests/test_workbench_scan_profile_pool_binding.py`:

```python
import pytest
from pydantic import ValidationError

from apps.web.contracts import Phase1ScanRequest


def _request_payload(fingerprint: str) -> dict[str, object]:
    return {
        "last_name": "Gate",
        "first_name": "Drei",
        "birth_date": "09041966",
        "birth_place": "Augsburg",
        "focus": "synthetischer Fokus",
        "profile_level": 3,
        "top_n": 5,
        "scan_profile_pool_fingerprint": fingerprint,
        "consent_local": True,
        "consent_safety": True,
    }


@pytest.mark.parametrize("fingerprint", ["", "A" * 64, "a" * 63, "g" * 64])
def test_scan_request_rejects_invalid_pool_fingerprint(fingerprint: str) -> None:
    with pytest.raises(ValidationError):
        Phase1ScanRequest.model_validate(_request_payload(fingerprint))
```

Ein zweiter Test entfernt das Feld vollstaendig und erwartet ebenfalls `ValidationError`.

- [ ] **Step 2: RED fuer stale Preview und Start ohne Side Effects schreiben**

Erzeuge eine App mit einem `ScanJobStore`-Double, dessen `start()` bei jedem Aufruf fehlschlaegt. Monkeypatche in `apps.web.main` den aktuellen Fingerprint auf `"b" * 64` und sende `"a" * 64`.

```python
preview = request(
    app,
    "POST",
    "/api/scan/preview",
    json_body=_request_payload("a" * 64),
)
started = request(
    app,
    "POST",
    "/api/scan/jobs",
    json_body=_request_payload("a" * 64),
)

assert preview.status_code == 409
assert started.status_code == 409
assert preview.json() == {
    "detail": "Scanprofil-Pool hat sich geändert. Bitte neu laden und erneut prüfen."
}
assert jobs.started == []
assert list(app.state.start_operations.root.glob("*.json")) == []
```

Der Test prueft damit direkt, dass vor dem Claim keine persistierte Startoperation erzeugt wurde.

- [ ] **Step 3: RED ausfuehren**

```cmd
set "PYTHONUTF8=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_scan_profile_pool_binding.py -q --tb=short
```

Expected: Pflichtfeld-/409-Vertrag fehlt.

- [ ] **Step 4: Requestfeld implementieren**

In `Phase1ScanRequest`:

```python
scan_profile_pool_fingerprint: str = Field(
    min_length=64,
    max_length=64,
    pattern=r"^[0-9a-f]{64}$",
)
```

- [ ] **Step 5: Gemeinsame fail-closed Validierung implementieren**

In `apps/web/main.py` importiere `current_scan_profile_pool_fingerprint` neben dem Workbench-Router und ergaenze:

```python
def _assert_current_scan_profile_pool(request: Phase1ScanRequest) -> None:
    current = current_scan_profile_pool_fingerprint(request.profile_level)
    if not hmac.compare_digest(request.scan_profile_pool_fingerprint, current):
        raise HTTPException(
            status_code=409,
            detail=(
                "Scanprofil-Pool hat sich geändert. "
                "Bitte neu laden und erneut prüfen."
            ),
        )
```

Importiere `hmac`. Rufe die Funktion in `scan_preview()` vor `_phase1_scan_payload()` und in `scan_job_start()` vor `operator_ctx` und `_start_operation()` auf.

- [ ] **Step 6: Erfolgspfad testen**

Der Test erzeugt den aktuellen Wert mit `current_scan_profile_pool_fingerprint(3)`, erwartet Preview 200 und einen einzigen Startaufruf. Der Fingerprint darf nicht im erzeugten CLI-Kommando vorkommen.

- [ ] **Step 7: Betroffene Test-Fixtures aktualisieren**

Suche alle POST-Bodies fuer `/api/scan/preview` und `/api/scan/jobs`. Zentrale Helfer erhalten den echten Fingerprint fuer ihr `profile_level`; Tests, die Pydantic nur intern ohne Endpoint validieren, muessen das neue Pflichtfeld ebenfalls bewusst setzen. Keine Produktions-Default- oder Kompatibilitaetsausnahme einfuehren.

- [ ] **Step 8: GREEN und Nachbarn ausfuehren**

```cmd
set "PYTHONUTF8=1" && set "OPENBLAS_NUM_THREADS=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_scan_profile_pool_binding.py tests/test_web_contracts.py tests/test_web_launcher.py tests/test_web_shell.py tests/test_web_authority_ids.py tests/test_start_operations.py -q --tb=short
```

Expected: PASS.

### Task 3: Frontend-Payload und Aktionssperre per TDD implementieren

**Files:**
- Create: `tests/test_workbench_scan_profile_pool_js.py`
- Modify: `apps/web/static/workbench-state.js:23-28`
- Modify: `apps/web/static/app.js:220-242,291-373,536-604,1453-1460,1674-1680`
- Modify: `apps/web/static/index.html:432-435`

- [ ] **Step 1: Node/VM-RED fuer aktuellen Fingerprint schreiben**

Der Test laedt reales `app.js` mit DOM-/API-Doubles und prueft:

```javascript
MorphicWorkbenchState.scanProfileCatalogStatus = "ready";
MorphicWorkbenchState.scanProfileCatalogLevel = 3;
MorphicWorkbenchState.scanProfileCatalog = {
  profile_level: 3,
  pool_authority: {fingerprint: "a".repeat(64)},
};
scanFormControl("profile_level").value = "3";

if (formScanPayload().scan_profile_pool_fingerprint !== "a".repeat(64)) {
  throw new Error("current fingerprint missing from payload");
}

scanFormControl("profile_level").value = "4";
if (formScanPayload().scan_profile_pool_fingerprint !== "") {
  throw new Error("stale level fingerprint leaked into payload");
}
```

- [ ] **Step 2: Node/VM-RED fuer Action-Gate schreiben**

Pruefe fuer `loading`, `error`, ungueltigen Fingerprint und falsches Level, dass Preview und Start deaktiviert bleiben. Bei `ready`, passendem Level und 64 Hexzeichen wird Preview aktiviert; Start bleibt zusaetzlich durch bestehende Reservation/Pending-Flags steuerbar.

- [ ] **Step 3: RED ausfuehren**

```cmd
set "PYTHONUTF8=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_scan_profile_pool_js.py -q --tb=short
```

- [ ] **Step 4: State und Payload implementieren**

`workbench-state.js` behaelt Katalog, Status, Fehler und Level als einzige Fingerprintquelle. `formScanPayload()` setzt:

```javascript
scan_profile_pool_fingerprint:
  state.scanProfileCatalogStatus === "ready"
  && Number(state.scanProfileCatalog?.profile_level) === Number(payload.profile_level)
    ? String(state.scanProfileCatalog?.pool_authority?.fingerprint || "")
    : "",
```

Passe die lokale Variablenstruktur so an, dass kein `payload` vor seiner Initialisierung referenziert wird: erst `profileLevel`, dann das Payloadobjekt bauen.

- [ ] **Step 5: Eine zentrale Aktionsfunktion implementieren**

```javascript
function scanProfilePoolReadyForCurrentLevel() {
  const state = window.MorphicWorkbenchState;
  const level = Number(scanFormControl("profile_level")?.value || 3);
  const fingerprint = String(
    state.scanProfileCatalog?.pool_authority?.fingerprint || ""
  );
  return state.scanProfileCatalogStatus === "ready"
    && Number(state.scanProfileCatalog?.profile_level) === level
    && /^[0-9a-f]{64}$/.test(fingerprint);
}

function updateScanActionAvailability() {
  const state = window.MorphicWorkbenchState;
  const poolReady = scanProfilePoolReadyForCurrentLevel();
  const preview = $("#preview-button");
  const start = $("#start-analysis-button");
  if (preview) preview.disabled = !poolReady || state.scanRunActive;
  if (start) {
    start.disabled = !poolReady || state.scanStartPending || state.scanRunActive;
  }
}
```

`setScanReservationControls()` delegiert die Startentscheidung danach an diese Funktion. Loading/Ready/Error, Levelwechsel, Reset und Start-Finally rufen sie auf.

- [ ] **Step 6: Defensive Guard vor Preview und Start implementieren**

`validateScanPayload()` gibt bei fehlendem aktuellem Fingerprint eine klare Meldung zurueck. Dadurch bleibt der Request auch bei programmatischem Button-Klick gesperrt.

- [ ] **Step 7: HTML initial sperren**

```html
<button id="preview-button" ... disabled>Vorschau erzeugen</button>
<button id="start-analysis-button" ... disabled>Analyse starten</button>
```

- [ ] **Step 8: GREEN und bestehende Single-Flight-Tests ausfuehren**

```cmd
set "PYTHONUTF8=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_scan_profile_pool_js.py tests/test_workbench_gate0_catalog_state.py tests/test_workbench_dogfood_frontend_contracts.py tests/test_workbench_review_regressions.py -q --tb=short
node --check apps/web/static/app.js
node --check apps/web/static/workbench-state.js
```

### Task 4: Suchbare interne und transparente externe Poolansicht implementieren

**Files:**
- Modify: `tests/test_workbench_scan_profile_pool_js.py`
- Modify: `apps/web/static/workbench-render.js:331-387`
- Modify: `apps/web/static/app.js:536-604`
- Modify: `apps/web/static/index.html:70-95`
- Modify: `apps/web/static/app.css:1555-1568`

- [ ] **Step 1: Render-RED fuer Summary und Badges schreiben**

Rendere einen Response mit `profile_level=4`, `internal.count=208`, `top_n=5`, Quelle `legacy` und Fingerprint-Kurzform. Pruefe exakt aus dem DOM-Text:

```text
Level 4 prüft 208 interne Screening-Profile; anschließend werden Top-5 vollständig analysiert.
Poolquelle: Legacy
Fingerprint: abcdef123456
```

Kein Test darf die Zahl `208` aus einer Frontendkonstante beziehen; sie kommt nur aus dem Testpayload.

- [ ] **Step 2: Render-RED fuer interne Suche schreiben**

Das DOM-Double muss Eventlistener ausloesen koennen. Nach Suchwert `beta` bleiben nur Profile sichtbar, deren ID oder Label case-insensitive passt; der Zaehler lautet `1 von 3 Profilen`. Die urspruengliche Payloadreihenfolge bleibt byte-/objektgleich.

- [ ] **Step 3: Render-RED fuer externe Wahrheit schreiben**

Pruefe:

```text
2 Registry-Quellen sind betriebsbereit; 0 als Scanprofile freigegeben.
Keine Wirkung auf diesen Scan, Profilpool oder Score.
Externe Scanprofile erst nach validierter Catalog-Freigabe in Gate 14.
```

Jeder Source-Eintrag nennt `keine Scanwirkung`. Im externen Container existieren keine `input`-, Aktivierungs- oder Toggle-Buttons.

- [ ] **Step 4: RED ausfuehren**

```cmd
set "PYTHONUTF8=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_scan_profile_pool_js.py -q --tb=short
```

- [ ] **Step 5: Renderer minimal implementieren**

`renderReviewCards()` nutzt `formData.top_n` und ausschliesslich Responsefelder. Interne Profile werden mit `Array.from(...).sort()` auf einer Kopie nach Label/ID sortiert. Suchfeld, Zaehler, Listen und Nulltreffer werden ausschliesslich ueber DOM-APIs und `textContent` erzeugt.

Externe Quellen erhalten ein eigenes `<details>`. Der Text verwendet `active_source_count`, nicht indirekt eine hardcodierte Anzahl. Bei `registry_only` bleibt Scanwirkung immer false.

- [ ] **Step 6: Runtime-Hinweis angleichen**

`#source-analysis-integration` verwendet nach erfolgreichem Load dieselbe klare Aussage und nennt keine Quelle schlicht „aktiv“ ohne Registry-Kontext.

- [ ] **Step 7: Loading/Error als nicht bestaetigten Pool rendern**

Loading erhaelt Skeleton-/Statusmarkup. Error rendert redigierten Grund und Retry, aber keine Profilanzahl `0`. Beide Zustaende bleiben mit der Aktionssperre aus Task 3 gekoppelt.

- [ ] **Step 8: CSS ergaenzen**

Nutze bestehende Tokens. Das Suchfeld nimmt maximal die Containerbreite ein; Listen umbrechen IDs/Labels; Badges und Details erzeugen bei 320/375 px keinen horizontalen Overflow. Keine neuen globalen Layoutregeln.

- [ ] **Step 9: GREEN ausfuehren**

```cmd
set "PYTHONUTF8=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_workbench_scan_profile_pool_js.py tests/test_workbench_render_js.py tests/test_workbench_no_inner_html_js.py tests/test_workbench_option_explanations.py -q --tb=short
node --check apps/web/static/workbench-render.js
```

### Task 5: Browservertrag fuer Suche, stale Responses, Fehler und Responsive

**Files:**
- Modify: `tests/browser/workbench.spec.js`

- [ ] **Step 1: Default-Katalogmock auf neues Schema aktualisieren**

Alle erfolgreichen Katalogmocks erhalten einen gueltigen Vollfingerprint, Kurzfingerprint, Authority und externe Gate-3-Felder. Mocks fuer alte Level bleiben absichtlich unterscheidbar.

- [ ] **Step 2: Browsertest fuer transparente Quellen und Suche schreiben**

Der Test navigiert real zu Phase 6, prueft Summary/Badges, oeffnet beide `<details>`, filtert ein Profil ueber Tastatur und bestaetigt:

- korrekten Ergebniszaehler;
- keine externe Checkbox/Schaltflaeche;
- sichtbare Aussage „keine Wirkung“ und „Gate 14“;
- Preview-/Startpayload mit dem angezeigten Vollfingerprint.

- [ ] **Step 3: Browsertest fuer fail-closed Loading/Error schreiben**

Verzoegere beziehungsweise verweigere den Katalogrequest. Preview und Start bleiben deaktiviert. Nach HTTP-Fehler zeigt Retry keinen falschen Nullpool; nach erfolgreichem Retry werden Aktionen freigegeben.

- [ ] **Step 4: Bestehenden Reorder-Test erweitern**

Die spaete Level-3-Response darf weder den sichtbaren Level-4-Pool noch dessen Fingerprint oder Aktionsstatus ueberschreiben.

- [ ] **Step 5: Responsive-Abnahme schreiben**

Pruefe Viewports 1280, 768 und 375 px. Interne/externe Details geoeffnet, langes Source-Label und Fingerprint-Badge duerfen keinen horizontalen Dokumentoverflow erzeugen.

- [ ] **Step 6: Fokussierte Browsermatrix ausfuehren**

```cmd
call npm --prefix tests/browser test -- --grep "Scanprofil-Pool|Registry-Quellen|catalog failure|catalog responses reorder"
```

Expected: PASS; der selbstverwaltete Runner hinterlaesst keinen Serverprozess und keinen temporaeren Runtimepfad.

### Task 6: Regression, Reviews und Abnahme

**Files:**
- Verify only: gesamter Gate-3-Scope

- [ ] **Step 1: Fokussierte Pythonmatrix ausfuehren**

```cmd
set "PYTHONUTF8=1" && set "PYTHONIOENCODING=utf-8" && set "OPENBLAS_NUM_THREADS=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/test_web_scan_profile_catalog.py tests/test_workbench_scan_profile_pool_binding.py tests/test_workbench_scan_profile_pool_js.py tests/test_web_contracts.py tests/test_web_launcher.py tests/test_web_shell.py tests/test_start_operations.py tests/test_workbench_gate0_catalog_state.py tests/test_workbench_dogfood_frontend_contracts.py tests/test_workbench_render_js.py tests/test_workbench_review_regressions.py tests/test_topn_cli_phase1_options.py -q --tb=short
```

- [ ] **Step 2: Syntax, Compile und Diff pruefen**

```cmd
C:\morphic_v1\.venv\Scripts\python.exe -m py_compile apps/web/workbench.py apps/web/contracts.py apps/web/main.py tests/test_web_scan_profile_catalog.py tests/test_workbench_scan_profile_pool_binding.py tests/test_workbench_scan_profile_pool_js.py
node --check apps/web/static/app.js
node --check apps/web/static/workbench-state.js
node --check apps/web/static/workbench-render.js
node --check tests/browser/workbench.spec.js
git diff --check -- apps/web/workbench.py apps/web/contracts.py apps/web/main.py apps/web/static/workbench-state.js apps/web/static/app.js apps/web/static/workbench-render.js apps/web/static/index.html apps/web/static/app.css tests/test_web_scan_profile_catalog.py
```

- [ ] **Step 3: Zwei getrennte Reviews durchfuehren**

Zuerst Spec-Compliance gegen die freigegebene Gate-3-Spec. Erst nach `APPROVE` folgt eine frische Code-Quality-Review auf Fingerprint-Kanonisierung, Race Conditions, Side-Effect-Reihenfolge, ID-/Label-Sicherheit, Accessibility, Testluecken und Scope. Alle Critical/Important Findings werden per RED/GREEN behoben und erneut geprueft.

- [ ] **Step 4: Vollstaendige Browser- und Python-Suite ausfuehren**

```cmd
call npm --prefix tests/browser test
set "PYTHONUTF8=1" && set "PYTHONIOENCODING=utf-8" && set "OPENBLAS_NUM_THREADS=1" && C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests -q --tb=short
```

- [ ] **Step 5: Cleanup bestaetigen**

Keine `isolated_server.py`-/Playwright-Prozesse, keine `morphic-browser-*`-Temporaerpfade, Port 8766 frei und akzeptierter Live-Port 8765 unveraendert. Git-Index bleibt leer.

## Abschlussgrenze

Gate 3 geht erst in manuelle Abnahme, wenn der konkrete interne Pool durchsuchbar und an Preview/Start gebunden ist, externe Registry-Quellen eindeutig ohne Scanwirkung und ohne Aktivierungscontrol erscheinen, Loading/Error/Stale fail-closed bleiben, beide Reviews keine offenen Critical/Important Findings enthalten und fokussierte sowie vollstaendige Suiten auf denselben Bytes bestanden sind.
