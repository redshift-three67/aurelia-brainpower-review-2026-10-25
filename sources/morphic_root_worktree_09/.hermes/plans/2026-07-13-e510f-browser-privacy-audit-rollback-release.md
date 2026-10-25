# E5.10F Browser-, Privacy-, Audit- und Rollback-Gesamtfreigabe – Implementation Plan

> **For Hermes:** Diesen Plan strikt testgetrieben und gateweise ausführen. Kein Commit/Push/Reset/Clean ohne ausdrückliche Freigabe. Port 8090 und bestehende Prozesse unangetastet lassen.

**Goal:** Die bereits implementierte streng lokale E5.10-Gruppenwirkung ausschließlich über eine bewusste Browserauswahl aktivierbar machen, alle Default-/Rollback-/Redaktionsverträge real nachweisen und E5.10 erst nach Desktop-/320-px-Browserabnahme freigeben.

**Architecture:** Der Gruppen-Draft-Editor bleibt vom Scanformular getrennt. Eine neue, ebenfalls außerhalb des Formulars liegende Aktivierungskarte zeigt serverseitigen Kill-Switch, explizite Stärke und eine leere Draft-Auswahl. `formScanPayload({includeGroupActivation})` fügt `group_draft_id` nur beim realen Scanstart und nur bei gesetztem Aktivierungs-Opt-in plus explizit ausgewähltem Draft hinzu; Preview, Review, Workbench-Draft, Template und localStorage bleiben frei von Aktivierungsdaten. Das Backend behält die vorhandene Draft→Identity→Consent→Root-/Child-Handle-Kette und fail-closed Semantik.

**Tech Stack:** HTML/CSS/Vanilla JavaScript, FastAPI/Pydantic, Windows DPAPI, pytest, Node-Syntaxcheck, lokaler Browser.

---

## Vorbedingung und Sicherung

- Autoritative Übergabe `docs/session-handoffs/2026-07-13_002808/*` gelesen.
- Live revalidiert: Branch `operator-workbench-phase1`, HEAD `619a1f5`, Dirty Tree absichtlich erhalten, `git diff --check` Exit 0.
- Hash-verifizierte ShadowCopy vor Mutation: `E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260713_081504_e510f` (18 Dateien, `SOURCE_MANIFEST.sha256` vollständig OK).

## Unverhandelbare Verträge

1. Ohne bewussten Browser-Opt-in fehlt `group_draft_id` vollständig im Scanpayload.
2. Kein Draft wird für die Scanaktivierung automatisch ausgewählt; der automatisch geladene Editor-Draft ist keine Aktivierung.
3. Preview, Review, Template, generischer Workbench-Draft, localStorage und sessionStorage enthalten keine `group_draft_id` oder Handle-/Gruppenwerte.
4. Nur `startScanJob()` darf `formScanPayload({includeGroupActivation: true})` verwenden.
5. Aktivierungs-Opt-in ohne explizite Draft-Auswahl wird clientseitig blockiert.
6. Kill-Switch aus oder Stärke `0` wird sichtbar als „keine produktive Wirkung“ dargestellt und bleibt backendseitig baseline-äquivalent ohne Storezugriff.
7. Gültiger Draft plus aktuelle Einzelconsents plus Flag an plus Stärke >0 darf den bestehenden handle-only Backendpfad erreichen.
8. Ungültige Aktivierung bleibt fail-closed; kein stiller Baseline-Scan unter behaupteter Aktivierung.
9. API, Job-Snapshot, Run-Trace, Logs, Reports und Manifeste bleiben frei von Handles, Draft-ID, Rohidentitäten, Mitgliedslisten, Raten und Zentroide.
10. Geo bleibt vollständig unverdrahtet.

### Task 1: Browser-Aktivierungsvertrag RED

**Files:**
- Create: `tests/test_workbench_group_activation_dom.py`

**Steps:**
1. Test fordert Aktivierungscheckbox, leere Draft-Auswahl, sichtbaren Wirkungsstatus und klare Default-Aus-Texte in `index.html`.
2. Test schneidet `formScanPayload` aus `app.js` aus und fordert optionale Aktivierung sowie ausschließlich `group_draft_id` als Gruppenfeld.
3. Test fordert: Preview/Review/Template nutzen Defaultpayload; nur `startScanJob()` aktiviert `includeGroupActivation`.
4. Test fordert: keine Gruppenaktivierungs-ID in `workbench-state.js`, localStorage-/sessionStorage-Schlüsseln oder generischen Draft-/Templatepfaden.
5. Fokustest ausführen und erwartetes RED wegen fehlender Controls/Verdrahtung bestätigen.

### Task 2: Minimale explizite Browseraktivierung GREEN

**Files:**
- Modify: `apps/web/static/index.html`
- Modify: `apps/web/static/app.js`
- Modify bei Bedarf: `apps/web/static/app.css`

**Steps:**
1. Aktivierungscheckbox `group-scan-activation-enabled`, Select `group-scan-draft-id` mit unveränderlichem leeren Platzhalter und Status `group-scan-activation-state` ergänzen.
2. Sichere Draft-Metadaten aus `loadGroupDrafts()` als Optionen darstellen, ohne erstes Element vorzuselektieren.
3. Editor-Autoload funktional erhalten, aber Auswahlstate strikt getrennt halten.
4. `formScanPayload(options = {})` erstellt Basispayload und ergänzt nur bei `includeGroupActivation === true`, checked Opt-in und explizitem Selectwert `group_draft_id`.
5. `validateScanPayload(payload, options = {})` blockiert bewusste Aktivierung ohne Draft-ID.
6. Nur `startScanJob()` ruft Payload/Validierung mit Aktivierungsoption auf.
7. Bei Save/Delete Draftliste neu laden; nach Delete ausgewählte ID entfernen und Status auf keine Wirkung setzen.
8. Policy-Rendering zeigt Flag/Stärke und Browserbereitschaft korrekt; Texte „keine Scanwirkung“ aus E5.10C/D werden auf den realen E5.10E/F-Stand aktualisiert.
9. RED-Test erneut ausführen und GREEN bestätigen; vorhandene Draft-/Policy-/Client-Persistence-DOM-Tests mitziehen.

### Task 3: Backend-Rollback- und Redaktionsmatrix RED→GREEN

**Files:**
- Create oder Modify: `tests/test_group_e510f_release_matrix.py`
- Modify Produktion nur bei real belegter Lücke; keine präventiven Refactors.

**Matrix:**
- A Flag aus: Baseline, kein Storezugriff.
- B Stärke `None`/`0`: Baseline, kein Handle/Storezugriff.
- C gültiger Draft/Subject/Consents/Flag/Stärke: Root-Handle und positive synthetische `AnalysisService`-Wirkung.
- D Draft `analysis_consent=False`: 422/fail-closed vor Scanstart.
- E Subject nicht Mitglied: 422/fail-closed.
- F Einzelconsent fehlt/widerrufen/abgelaufen: 422/fail-closed.
- G fremder Owner/Workspace/Tenant: 403 bzw. kontextgebunden fail-closed.
- H Handle abgelaufen/manipuliert/wiederverwendet: fail-closed.
- I Kill-Switch nach Aktivierung aus: neue Scans baseline, keine neuen Handles.
- J Identity- oder Draft-Erasure: weitere Aktivierung inert/fail-closed.
- K Responses, Snapshots, Run-Traces, Logs, Reports und Manifeste redigiert.

**Steps:**
1. Vorhandene Testabdeckung wiederverwenden und nur echte Lücken als neue Tests schreiben.
2. Jeden neuen Test einzeln als erwartetes RED ausführen.
3. Nur falls ein RED einen Produktionsfehler belegt, minimale Backendänderung implementieren.
4. Neuen Matrixfokus vollständig grün ausführen.

### Task 4: Statische Privacy-/Boundary-Prüfung

**Files:**
- Modify: `tests/test_group_e510_release_gate.py`
- Modify: `tests/test_workbench_group_activation_dom.py`

**Steps:**
1. Request-Feldmenge weiterhin auf `group_draft_id` begrenzen; Rohgruppenfelder/Handles verbieten.
2. `group_draft_id` in Run-Trace, Launcherresponse, Job-Snapshot, Report-/Manifestbuildern verbieten.
3. Aktivierungs-Environment nur privat und nicht persistiert nachweisen.
4. `node --check` für alle geänderten JS-Dateien und `git diff --check` ausführen.

### Task 5: Fokussierte und vollständige Regression

**Commands:**

```bash
PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe -m pytest \
  tests/test_workbench_group_activation_dom.py \
  tests/test_workbench_group_analysis_policy_dom.py \
  tests/test_workbench_group_draft_dom.py \
  tests/test_web_group_productive_activation.py \
  tests/test_group_e510f_release_matrix.py \
  tests/test_group_e510_release_gate.py -q

PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe -m pytest tests -q --ignore=tests/test_top5_workflow_smoke.py

PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe -m pytest \
  tests/test_top5_workflow_smoke.py::test_top5_scan_writes_multiplex_exports -q

node --check apps/web/static/app.js
node --check apps/web/static/workbench-api.js
git diff --check
```

Gemeinsame Rate-Limit-429-Ausreißer ehrlich klassifizieren und einzeln in frischen Prozessen nachweisen; nicht als gemeinsamen grünen Lauf ausgeben.

### Task 6: Reale lokale Browserabnahme

**Voraussetzung:** Vor Start Ports prüfen; 8090 nicht verwenden oder verändern. Freien Loopback-Port wählen.

**Desktop-/320-px-Matrix:**
1. Default: Aktivierung aus, kein Draft vorausgewählt, Status „keine Wirkung“.
2. Draft speichern/laden: Editor darf laden, Aktivierungsselect bleibt leer.
3. Aktivierung an ohne Draft: Start clientseitig blockiert.
4. Flag aus und ausgewählter Draft: sichtbar keine produktive Wirkung; Backend baseline.
5. Stärke 0: sichtbar keine produktive Wirkung; kein Handle.
6. Flag an, Stärke >0, gültiger synthetischer Draft/Consents: realer Top-N-Start und positive synthetische Wirkung.
7. Widerruf/Ablauf/Erasure: fail-closed und verständliche UI-Fehlermeldung.
8. Netzwerkpayload enthält nur die erlaubte `group_draft_id`; Responses/Status/Trace/Reports bleiben redigiert.
9. 320 px: kein horizontaler Seitenoverflow; Controls bedienbar und Status lesbar.
10. Testserver beenden; ausschließlich selbst erzeugte synthetische Drafts/Identitäten/Handles gezielt löschen.

### Task 7: Gatebericht und finale Entscheidung

**Files:**
- Create: `docs/status/2026-07-13-e510f-browser-privacy-audit-rollback-release-gate.md`
- Modify: `docs/status/2026-07-12-gesamtstruktur-fortschritt.md`

Nur reale Ergebnisse eintragen. `E5.10 GO` und Feedback e `100 %` ausschließlich wenn sämtliche Matrixfälle, reale Browserabnahme, Cleanup, Rest-Suite, Top-5, Compile/Syntax und Diff-Check bestanden sind. Geo bleibt separat NO-GO.
