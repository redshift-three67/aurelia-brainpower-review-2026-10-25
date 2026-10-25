# Lokale Gruppen-Workbench – DPAPI-Entwurf ohne Scanwirkung

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Eine getrennte, lokale Workbench-Erfassung für einwilligungsgebundene Gruppenentwürfe bereitstellen, die in der Windows-DPAPI-Feasibility-Ablage speichert und löscht, aber weder Scanrequest noch Launcher, CLI, Score, Job, Report, Trace oder Manifest verändert.

**Architecture:** Der bisherige `LocalVectorDraftStore` bleibt der einzige Speicherpfad für Gruppen-/Geo-Entwürfe; der generische Workbench-JSON-Draft darf nicht verwendet werden, weil er Gruppen-/Geo-Sensitivität nicht erkennt und Klartext schreibt. Ein eigener FastAPI-Router verwaltet ausschließlich einen einzelnen, lokalen Gruppenentwurf mittels strikter Pydantic-Modelle und gibt außerhalb der expliziten Ladeoperation nur redigierte Safe-Summaries zurück. Das Frontend ergänzt Phase 2 um eine Gruppenkarte mit zwei getrennten Einwilligungen und verwendet nur die neuen, dedizierten API-Helfer.

**Tech Stack:** FastAPI, Pydantic v2, Windows DPAPI/ACL über `LocalVectorDraftStore`, Vanilla JavaScript, bestehende Workbench-Tests.

---

## Ausgangsbefund und harte Grenzen

- Die aktuelle Gruppenkarte ist bewusst deaktiviert: `apps/web/static/index.html:113-120`.
- Der generische Draft-Endpunkt (`apps/web/workbench.py:61-75`) schreibt über `WorkbenchRuntimeStore` Klartext-JSON (`apps/web/workbench_runtime.py:49-67`) und darf deshalb keine Gruppenentwürfe aufnehmen.
- Die bestehende DPAPI-Ablage akzeptiert nur OS-Temp-Unterverzeichnisse, verschlüsselt atomar und kann safe listen, laden, Dry-Run-Erasure und bestätigtes Löschen (`core/compliance/local_vector_draft_store.py:28-148`).
- `GroupContextDraft` hat strikte Felder, pseudonyme Mitglieder, Mitglieder-/Persistenz-Einwilligung, begrenzte Retention und nun eine getrennte `analysis_consent`-Vormerkung. Die Vormerkung alleine aktiviert keinen Vektor.
- Die Browser-Policy verbietet Geolocation weiterhin (`apps/web/main.py:320-334`) und bleibt unverändert.
- `Phase1ScanRequest` darf keine Gruppenfelder erhalten. `apps/web/group_analysis_activation.py` bleibt ein nicht gerouteter in-memory Helper und darf nicht in Scanpfade importiert werden.

## API-Entscheidung

Neuer Router `apps/web/group_drafts.py`, in `create_app()` registriert, mit folgenden lokalen Endpunkten:

- `GET /api/workbench/group-draft`: nur Safe-Summary oder `{draft_id: null, vectors: []}`.
- `PUT /api/workbench/group-draft`: akzeptiert ein striktes `GroupContextDraft` plus kanonische `draft_id`; speichert ausschließlich im DPAPI-Store und antwortet nur mit Safe-Summary.
- `GET /api/workbench/group-draft/{draft_id}`: gibt den vollständigen lokalen Entwurf nur über den lokalen Workbench-Endpunkt zurück, damit der Operator ihn explizit weiterbearbeiten kann. Nie in Log, Job, Trace, Report oder Manifest übernehmen.
- `DELETE /api/workbench/group-draft/{draft_id}`: verlangt `confirmation_id` und ruft die bestehende bestätigte Erasure-Funktion auf.
- `GET /api/workbench/group-draft/erasure-dry-run`: redigierter, nicht mutierender Retention-Plan.

Der Router erstellt den Store im OS-Temp-Verzeichnis unter einer festen lokalen Workbench-Namensraumkennung. Er verwendet **nicht** `runtime_dir/workbench`, weil dieser Pfad außerhalb von OS-Temp liegen kann und Klartext-Workbenchdaten enthält. Kein neuer Kryptographie-Dependency und kein Browser-LocalStorage für Gruppeninhalt.

---

### Task 1: Strikte Router-Verträge und Fail-Closed-Speicherfactory

**Objective:** Die dedizierte Gruppen-Draft-API als isolierten Vertrag definieren, ohne Produktivpfade zu berühren.

**Files:**
- Create: `apps/web/group_drafts.py`
- Create: `tests/test_web_group_drafts.py`
- Modify: `apps/web/main.py:358-365`

**Step 1: Write failing tests**

- `PUT` ohne `persistence_consent=True` → HTTP 422.
- Mitglied ohne `consent_recorded=True` → HTTP 422.
- Ein gültiger Entwurf liefert nur Safe-Summary; Antwort enthält niemals `group_label` oder `cli-...`-Mitgliedsreferenzen.
- Unknown fields → HTTP 422.
- `GET` Safe-Summary nach dem Speichern enthält `analysis_enabled=False`.
- `DELETE` mit falscher Confirmation → HTTP 422/400 und die Ciphertext-Datei bleibt lesbar.
- Dry-run löscht keine Ciphertext-Datei.

**Step 2: Run RED**

```bash
PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe -m pytest tests/test_web_group_drafts.py -q
```

Expected: FAIL because Router/Endpunkte fehlen.

**Step 3: Implement minimum**

- Erzeuge Router ohne Scan-/Launcher-Imports.
- Erzeuge DPAPI-Store ausschließlich in `Path(tempfile.gettempdir()) / "morphic-workbench-local-vector-drafts"`.
- Verwende keine `WorkbenchRuntimeStore`-Methoden.
- Response-Modell bzw. Mapping immer von `draft.safe_summary()` ableiten.
- Router in `create_app()` registrieren, aber keine Änderung am `Phase1ScanRequest`, `_phase1_scan_payload()` oder `_workbench_run_trace_seed()`.

**Step 4: Run focused tests**

Expected: PASS.

---

### Task 2: Dauerhafte Nichtwirkungs-/Redaktions-Regressionstests

**Objective:** Jede versehentliche Verbindung des lokalen Gruppenrouters mit produktiven Pfaden verhindern.

**Files:**
- Modify: `tests/test_local_vector_draft_integration_boundary.py`
- Modify: `tests/test_group_analysis_authorization.py`
- Modify: `tests/test_web_workbench_runtime.py`

**Step 1: Write failing tests**

- `Phase1ScanRequest.model_fields` bleibt frei von Gruppe/Geo.
- `apps/web/launcher.py`, `apps/cli/commands/field.py`, `apps/web/main.py`-Scanfunktionen und Manifestmodule enthalten weder Gruppenentwurfs- noch Aktivierungsrohwerte.
- Ein gestarteter Scan-Job enthält keine Gruppenreferenz, Gruppenlabel, Centroid oder `analysis_consent` im Run-Trace.
- Router-Response-Summaries enthalten niemals Klartextgruppe, Mitglieds-ID oder DPAPI-Pfad.

**Step 2: Run RED; implement ausschließlich die notwendigen Redaktionsgrenzen; rerun GREEN.**

---

### Task 3: Gruppenkarte in Phase 2 – reine lokale Erfassung

**Objective:** Die deaktivierte Gruppenkarte durch einen klar beschrifteten lokalen Entwurfsflow ersetzen, ohne irgendeinen Scanparameter zu setzen.

**Files:**
- Modify: `apps/web/static/index.html:99-139`
- Modify: `apps/web/static/app.css`
- Modify: `tests/test_workbench_client_context_dom.py`
- Create/extend: `tests/test_workbench_group_draft_dom.py`

**Required markup:**

- Karte `data-vector="group" data-vector-state="local-draft"`, nicht `active`.
- Gruppenbezeichnung (lokaler Entwurf), bis zu 100 pseudonyme Mitglieds-IDs im Format `cli-...`, keine Namen/E-Mail-Eingaben.
- Checkboxen getrennt für: Mitgliedseinwilligung, lokale DPAPI-Speicherung, spätere Analyse-Einwilligungsvormerkung.
- Hinweistexte: „Nicht Teil der Scan-Anfrage“, „keine Auswirkung auf den aktuellen Scan“, „keine Browser-Geolocation“, „lokal/Windows-DPAPI“.
- Speichern, Laden, Löschen und Retention-Dry-Run, jeweils klarer Statusbereich `aria-live="polite"`.

**Tests:**

- Keine `name=`-Felder der Gruppenkarte sind über `form="scan-form"` mit dem Scanformular verbunden.
- `formScanPayload()` enthält keine Gruppenfelder.
- Die UI zeigt „lokaler Entwurf – nicht in Analyse einbezogen“, solange die spätere Aktivierungsfreigabe fehlt.
- 320px: Karte horizontal überlauffrei; keine `innerHTML`-Einführung.

---

### Task 4: Dedizierte Browser-API und State – kein LocalStorage für Gruppendaten

**Objective:** UI mit den isolierten Endpunkten verbinden, ohne Gruppeninhalt in generischen Draft/Template- oder Browser-Storagepfaden abzulegen.

**Files:**
- Modify: `apps/web/static/workbench-api.js:25-62`
- Modify: `apps/web/static/workbench-state.js`
- Modify: `apps/web/static/app.js:654-679`
- Extend: `tests/test_workbench_client_context_persistence.py`
- Create/extend: `tests/test_workbench_group_draft_js.py`

**Step 1: Write failing JS/source-contract tests**

- Neue API-Methoden adressieren nur `/api/workbench/group-draft...`.
- Keine Gruppenwerte in `saveDraft`, `saveTemplate`, `formScanPayload` oder `localStorage`.
- Save-Schaltfläche ist bis zur lokalen Speicherfreigabe deaktiviert.
- Eine aktivierte Analyse-Einwilligungsvormerkung ändert nur den Gruppen-Draft-Payload, nie den Scanpayload.
- Löschen übergibt eine exakte `confirmation_id`.

**Step 2: Implement minimum**

- `MorphicWorkbenchApi.loadGroupDraftSafe`, `saveGroupDraft`, `loadGroupDraft`, `deleteGroupDraft`, `dryRunGroupDraftErasure`.
- `MorphicWorkbenchState` enthält höchstens redigierten UI-Status und aktuelle `draft_id`; keine persistenten Gruppeninhalte über `localStorage`.
- `app.js` liest/schreibt die Gruppenfelder nur über dedizierte API-Aufrufe und aktualisiert Status mit `textContent`/bestehenden Renderhilfen.

**Step 3: Verify Node syntax and source tests.**

---

### Task 5: Manuelle Browser-Abnahme und vollständige Regression

**Objective:** Lokale Gruppenentwurfserfassung real prüfen, ohne einen Scan zu beeinflussen.

**Steps:**

1. Vor Serverstart Ports 8000/8090 prüfen; bestehende Prozesse nie beenden.
2. Server nur auf freiem alternativen Loopback-Port starten, z. B. 8001:
   ```bash
   OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe -m uvicorn apps.web.main:app --host 127.0.0.1 --port 8001
   ```
3. In Phase 2 einen pseudonymen Zwei-Mitglieder-Entwurf mit beiden Einwilligungen speichern.
4. Prüfen: Safe-Status zeigt nur Mitgliederanzahl/Retention, nicht Label/IDs.
5. Vorschau erzeugen und sicherstellen, dass Command und `/api/scan/preview` unverändert bleiben.
6. Browser neu laden; gespeicherten lokalen Entwurf über dedizierten Endpunkt wieder öffnen.
7. Erasure-Dry-Run ausführen; danach Entwurf explizit mit passender Confirmation löschen.
8. Desktop und 320px prüfen.
9. Gesamte Suite:
   ```bash
   PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe -m pytest tests -q
   node --check apps/web/static/app.js
   node --check apps/web/static/workbench-api.js
   node --check apps/web/static/workbench-state.js
   git diff --check
   ```

---

## Explizit nicht Teil dieses Gates

- Keine Erweiterung von `Phase1ScanRequest`, CLI-Flags oder Launcher.
- Keine echte Scan-/Score-/Report-/Job-/Trace-/Manifest-Wirkung aus der UI.
- Keine automatische Clientprofil-Auflösung und keine Übergabe von Mitgliedsraten über HTTP.
- Kein Browser-GPS, Geocoding, Netzwerkdienst oder neue Crypto-Abhängigkeit.
- Kein Commit/Push ohne erneute ausdrückliche Nutzerfreigabe.

## Nach diesem Gate nötige separate Entscheidung

Für echte produktive Gruppenwirkung muss vor der Scanverdrahtung eine vertrauenswürdige Quelle für die Mitgliedsraten festgelegt werden. Das aktuelle Projekt besitzt keine zustimmungsgebundene Clientprofil-Registry, die historische bzw. aktuelle Mitgliedssignaturen sicher auflösen kann. Ein künftiger Scan-Gate muss deshalb diesen Resolver, Tenant/Owner-Bindung, Datenminimierung, Redaction, Erasure und Vergleichstests als eigenes Vorhaben behandeln; Gruppenraten dürfen nicht als Rohwerte aus dem Browser an `/api/scan/*` gesendet werden.
