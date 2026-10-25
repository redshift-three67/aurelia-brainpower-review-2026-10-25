# Operator Workbench: Radi144-UI/UX-Konsolidierung + Harmonisierungs-Backend

> **Für agentische Bearbeiter:** Empfohlener Sub-Skill: `superpowers:subagent-driven-development` oder `superpowers:executing-plans`. Schritte nutzen Checkbox-Syntax (`- [ ]`) zum Tracking. Dieser Plan ist **selbsterklärend** (Datei:Zeile-Belege statt Annahmen) und baut auf dem committeten Stand `bcfcd2f` im Worktree `operator-workbench-phase1` auf.

**Ziel:** Die vom Nutzer am 2026-07-07 gemeldeten 8 UI/UX-Lücken (a–h) beheben, ohne den funktionierenden Scan-Workflow (262 passed, 2 skipped) zu regressieren. Nach Abschluss soll die Web-Oberfläche in Führung, Erklärung und Optik nah an `http://localhost:8090/user_workflow.html` (Radi144-Referenz) liegen, bei weiterhin ehrlicher morphic_v1-Fachlogik.

**Baseline:** Worktree `C:\morphic_v1\.worktrees\operator-workbench-phase1`, Branch `operator-workbench-phase1`, HEAD `bcfcd2f` ("feat: align web UI with Radi144 patterns + 12-Substep-Timeline").

**Referenzen:**
- `docs/superpowers/specs/2026-07-04-apps-web-radi144-workflow-ux-design.md` (ursprüngliche Zielvision, Prinzipien 1–8)
- `docs/deep-audit-2026-07-07/SITUATION_KONSOLIDIERT_BRANCHES_UI_ANALYSELAUF.md` (Branch-Historie, vorherige Wiederherstellung)
- `docs/superpowers/plans/2026-07-05-morphic-v1-radiquant4-alignment.md` (radiquant4-Alignment-Status, siehe Abschnitt 0 unten)
- Radi144-Live-Referenz: `http://localhost:8090/user_workflow.html`

---

## 0. Radiquant4-Alignment-Status (beantwortet Nutzerpunkt h)

Codebasiert geprüft (`grep`/`git show` am 2026-07-07):

| Task (aus `2026-07-05-morphic-v1-radiquant4-alignment.md`) | Status | Beleg |
|---|---|---|
| 1. Standard-Output-Adapter (`platform_export.py`) | ✅ erledigt | Datei existiert, in `step11_export.py` verdrahtet |
| 2. Operator/Workspace-Context + Ownership | ✅ erledigt (inkl. Step 4/5, urspr. deferred) | `apps/web/main.py:459-519` ruft `resolve_operator_context`/`assert_owner` bei Job-Results auf |
| 3. Entitlement-Stub | ✅ erledigt | `core/compliance/entitlement_stub.py` |
| 4. Quantum-Pfad-Härtung | ✅ erledigt | `tests/test_quantum_real_path.py`, `QISKIT_VERIFICATION_LOG.md` |
| 5. Deterministischer Seed + Entropie-Kaskade | ✅ erledigt | `core/realtime/seed_generator.py` |
| 6. Substep-Vokabular-Mapping | ✅ erledigt, jetzt auch UI-sichtbar | `apps/cli/workflow/substep_manifest.py`, seit `bcfcd2f` als 12-Substep-Timeline in Phase 7 gerendert |
| 7. DSGVO-Härtung (Audit-Actor, Purge) | ✅ erledigt | `runtime_manifest.py` `append_audit(actor=...)`, `purge_expired(...)` |
| 8. Design-Token-Übernahme | ✅ erledigt | `--rq-*` Tokens in `app.css`, seit `bcfcd2f` um Radi144-Step-Header/Timeline erweitert |
| 9. Tests | ✅ erledigt | 262 passed, 2 skipped |

**Fazit:** Die radiquant4-Alignment-Vorbereitung ist auf Code-Ebene **vollständig** (alle 9 Tasks). Die in diesem Plan behandelten Punkte a–h sind **UI/UX-Politur und ein Backend-Lücke bei der Harmonisierungs-Zyklus-Logik** (siehe Task 7), keine radiquant4-Anbindungsarbeit mehr. Explizit **außerhalb** dieses und des Vorgänger-Plans (siehe "Nicht-Ziele" in `2026-07-05-morphic-v1-radiquant4-alignment-design.md`): echte Netzwerk-Integration gegen einen laufenden radiquant4-Server, Astro/React-Migration, Postgres/Redis/Celery.

---

## 1. Gap-Analyse: Nutzerpunkte a–h → Root Cause → Datei

| # | Nutzerpunkt | Root Cause (belegt) | Datei(en) |
|---|---|---|---|
| a | Fokus-Pflicht/Optional unklar | `contracts.py:20` `focus: str = Field(min_length=1)` ist **Pflichtfeld** (treibt `--focus` im CLI-Aufruf), aber UI kennzeichnet das nicht. Zusätzlich existiert `main_symptom: str = ""` (**optional**, `contracts.py:28`) bereits im Contract, wird aber **nirgends im HTML exponiert** — Radi144 trennt genau das (Pflicht-Fokus vs. optionales Anliegen). | `apps/web/static/index.html` Phase 3, `apps/web/contracts.py:20,28` |
| b | Fokushistorie fehlt | Keine `localStorage`-Logik für zuletzt verwendete Fokus-Werte vorhanden (Radi144: „Schnellauswahl“ + „Letzte Fokusse“). | `apps/web/static/app.js`, `workbench-state.js` |
| c | Profilvorlage/Entropie-Modus ohne Wirkungserklärung | Reale Semantik nur im Backend sichtbar: `apps/cli/commands/scan.py:422-448` (`_phase1_template_values`: `phase1-default`=0.5/0.5/0.5/0.5 ausgewogen, `personal-balanced`=0.6 auf allen Achsen, `personal-focused`=physisch 0.75/astral 0.45 körperbetont) und `scan.py:459-484` (`entropy_mode`: `legacy`=Standard-RNG, `enhanced`=`ME_ENTROPY_MODE=enhanced`, `hybrid`=zusätzlich `--hybrid-entropy`). UI zeigt nur `<select>` ohne Erklärtext. | `apps/web/static/index.html` Phase 4, `apps/cli/commands/scan.py:422-484` |
| d | Referenzbild soll `.jpg` sein | `contracts.py:102-108` (`normalize_image_path`) validiert nur `strip()`, keine Extension-Prüfung; HTML-Platzhalter suggeriert `.png`; `<input type="file">` fehlt komplett (nur Text-Pfadfeld). | `apps/web/contracts.py:102-108`, `apps/web/static/index.html` Phase 4 |
| e | Workbench-Modus & „Hardware-Truth nicht verfuegbar“ unerklärt | `<select id="workbench-mode">` ohne Beschreibungstext; Fallback-Text kommt aus `app.js:145-147` (`loadHardwareTruth` catch-Block) — reiner Fehlertext ohne Erklärung/Retry. | `apps/web/static/index.html` Phase 5, `apps/web/static/app.js:138-148` |
| f | Kein Auto-Sprung zu Phase 7 nach Start; leere Review-Cards | **Bestätigter Bug 1:** `renderReviewCards()` ist in `workbench-render.js:96-128` definiert, wird aber **in `app.js` nirgends aufgerufen** → Review-Grid bleibt leer (siehe Screenshot). **Bestätigter Bug 2:** `startScanJob()` (`app.js:165-181`) ruft nach erfolgreichem Start keinen `showStep(6)`/`navigate` auf — Nutzer bleibt auf Phase 6 stehen, bis manuell „Weiter“ geklickt wird. | `apps/web/static/app.js:165-181`, `workbench-render.js:96-128` |
| g1 | Workflow wirkt gegenüber Radi144 (`localhost:8090/user_workflow.html`) nicht „fertig“ (Steppings, Übergänge, Farben, Erklärungen) | Radi144-Referenz nutzt durchgängig: Emoji-Icons pro Sektion, kurze Erklärkästen („📚 Hinweis zum ...“) vor **jeder** komplexen Eingabe, farbcodierte Auswahl-Chips statt reiner `<select>`, Live-Zusammenfassung/Snapshot am Ende jeder Phase. Der Workbench-Port aus `bcfcd2f` hat Step-Header/Timeline übernommen, aber **nicht** die Erklärkästen, Auswahl-Chips und den durchgängigen Snapshot-Rhythmus. | durchgängig `apps/web/static/index.html`, `app.css` |
| g2 | Berichtskatalog unübersichtlich, Vorschau nicht professionell, Harmonisierung braucht eigene Phase, Anlehnung an `Run-MultiplexScan.ps1` fehlt | Phase 10 (`finalize-phase`) bündelt Berichtskatalog + Vorschau + Harmonisierung in einem Panel (`index.html` `finalize-phase`-Section) — kein Platz für Struktur. **Backend-Lücke bestätigt:** `services/harmonization_worker.py:489-494` (`start_harmonization_job`) kennt nur `target_frequency`, `duration_minutes`, `intention`, `hardware_config` — **keine** Impuls-/Pause-Sekunden, keinen Dauer-Faktor (×21 Min), keine Solfeggio-Basis, obwohl Radi144s „Impuls/Pausen-Harmonisierung“ (Referenz: `Run-MultiplexScan.ps1`) genau das als Kernkonzept hat. Web, CLI (`apps/cli/commands/harmonize.py`) und Workflow-Step (`step12_harmonize.py`) teilen sich zwar denselben Worker (echt, keine Fake-Diskrepanz), aber der Worker selbst bildet den Impuls/Pause-Zyklus nicht ab. | `apps/web/static/index.html` Phase 10, `apps/web/harmonization.py`, `apps/web/contracts.py` (`HarmonizationRequest`), `services/harmonization_worker.py:489-494` |

---

## 2. Aufgaben (TDD, sequenziell nach Priorität)

### Task 1 (P0 — Bugfix, keine UI-Änderung nötig): Review-Cards füllen + Auto-Advance nach Scan-Start

**Dateien:** `apps/web/static/app.js`

- [ ] Schritt 1: In `bootstrapWorkbench()` bzw. im Stepper-Klick-Handler (`workbench-render.js:21-27` `renderStepper`) einen Hook ergänzen: beim Wechsel zu `review-phase` (Index 5) `window.MorphicWorkbenchRender.renderReviewCards(formScanPayload(), window.MorphicWorkbenchState.hardwareTruth)` aufrufen. Einfachste Umsetzung: in `navigate()` (`app.js:350-358`) und im Stepper-Klick (`workbench-render.js:25`) nach `showStep(...)` prüfen `if (index === 5) { ... renderReviewCards(...) }`.
- [ ] Schritt 2: `generatePreview()` (`app.js:152-163`) ruft zusätzlich `renderReviewCards(...)` auf, damit die Karten auch beim manuellen „Vorschau erzeugen“-Klick aktuell sind.
- [ ] Schritt 3: In `startScanJob()` (`app.js:165-181`) nach erfolgreichem `showInlineState("Analyse gestartet", "ok")` **sofort** `navigate(1)` bzw. `window.MorphicWorkbenchRender.showStep(6)` aufrufen (springt zu `run-phase`), **bevor** `pollScanJob` gestartet wird — Timeline und Job-Status-Panel sind dann von Anfang an sichtbar.
- [ ] Schritt 4: Test ergänzen in `tests/test_web_shell.py` (oder neuer `tests/test_web_workbench_review_wiring.py`): JS-Verhalten ist in Python-Tests nicht direkt prüfbar — stattdessen einen Playwright-artigen Smoke-Test **falls Playwright bereits Projekt-Dependency ist** (prüfen: `grep -r playwright pyproject.toml`); falls nicht vorhanden, diesen Schritt als manuelle Verifikation dokumentieren (siehe Abschnitt 4) statt neue Test-Infrastruktur einzuführen.
- [ ] Schritt 5: Manuell verifizieren (Abschnitt 4, Check 1+2).

### Task 2 (P1): Fokus-Feld — Pflicht/Optional klarstellen + Hauptsymptom exponieren

**Dateien:** `apps/web/static/index.html` (Phase 3), `apps/web/static/app.js` (`formScanPayload`)

- [ ] Schritt 1: In Phase 3 (`focus-phase`) das bestehende `<label class="focus-input">` um ein sichtbares Pflicht-Badge ergänzen, z. B. `<span class="required-badge">Pflichtfeld</span>` neben dem Label, plus kurzen Hinweistext direkt darunter (`step-subtitle`-Klasse wiederverwenden oder neue `.field-hint`): "Der Fokus-Text fliesst direkt in die Analyse (`--focus`) ein und beeinflusst Matrix/Scoring."
- [ ] Schritt 2: Neues optionales Feld „Hauptsymptom / Anliegen (optional)“ ergänzen, gebunden an `name="main_symptom"` (Contract-Feld existiert bereits, `contracts.py:28`), mit Hinweis „Wird nur dokumentiert, beeinflusst die Berechnung nicht.“
- [ ] Schritt 3: `formScanPayload()` in `app.js` um `main_symptom: String(data.get("main_symptom") || "").trim()` ergänzen (Feld existiert im Contract bereits, aktuell nicht im Payload).
- [ ] Schritt 4: CSS für `.required-badge`/`.field-hint` in `app.css` ergänzen (kleine, Radi144-artige Pille, z. B. Terracotta-Akzent wie `.step-icon`).
- [ ] Schritt 5: Regressionstest in `tests/test_web_contracts.py` ergänzen: POST mit `main_symptom` gesetzt → im generierten Preview-Kommando erscheint es **nicht** als CLI-Flag (nur dokumentarisch), Contract akzeptiert es weiterhin optional (bereits der Fall, nur Testabdeckung fehlt evtl. — prüfen vor Neuanlage).

### Task 3 (P1): Fokushistorie (client-seitig, privacy-safe)

**Dateien:** `apps/web/static/workbench-state.js`, `apps/web/static/app.js`, `apps/web/static/index.html`

- [ ] Schritt 1: In `workbench-state.js` zwei Funktionen ergänzen: `loadFocusHistory()` (liest `localStorage["morphic_focus_history"]`, JSON-Array, max. 8 Einträge) und `saveFocusToHistory(value)` (dedupliziert, prepend, trunkiert auf 8, schreibt zurück). Nur der reine Fokus-Text wird gespeichert — **keine** Klientendaten, DSGVO-unkritisch (kein Personenbezug).
- [ ] Schritt 2: In `index.html` Phase 3 unter dem Fokus-Input einen Container `<div id="focus-history-chips" class="chip-row"></div>` ergänzen.
- [ ] Schritt 3: In `app.js`: beim Betreten von Phase 3 (analog Task 1 Hook) `renderFocusHistoryChips()` aufrufen (neue Funktion in `workbench-render.js`, rendert Chips aus `loadFocusHistory()`, Klick auf Chip setzt `#scan-form input[name=focus]`). Beim erfolgreichen `generatePreview()`/`startScanJob()` `saveFocusToHistory(payload.focus)` aufrufen.
- [ ] Schritt 4: CSS `.chip-row`, `.chip` in `app.css` (kompakte, klickbare Pillen, Radi144-Farbwelt: Sage-Rahmen, Hover-Fill).
- [ ] Schritt 5: Manuelle Verifikation (Abschnitt 4, Check 3) — kein Python-Test nötig (reine Client-Logik ohne Server-Kontakt).

### Task 4 (P1): Profilvorlage & Entropie-Modus — Wirkungserklärung

**Dateien:** `apps/web/static/index.html` (Phase 4)

- [ ] Schritt 1: Unter dem Profilvorlage-`<select>` einen `<p class="field-hint">` mit den drei realen Effekten ergänzen (Text exakt aus `scan.py:422-448` ableiten, keine Erfindung): „Phase-1 Standard: alle vier Achsen (Emotion/Physisch/Mental/Astral) gleich gewichtet (0.5). Persönlich ausgewogen: alle Achsen erhöht (0.6). Persönlich fokussiert: körperbetont (Physisch 0.75, Astral 0.45).“
- [ ] Schritt 2: Unter dem Entropie-Modus-`<select>` analog: „Legacy: Standard-Zufallsquelle. Enhanced: erweiterte Entropie-Qualität. Hybrid: zusätzlich Hardware-/Hybrid-Entropiequelle aktiv.“ (Basis: `scan.py:459-484`).
- [ ] Schritt 3 (optional, falls Zeit): `<select>` durch Radio-Karten ersetzen (Radi144-Prinzip 5 „Auswahloptionen als Radio-/Toggle-Karten“), CSS-Wiederverwendung von `.step-card`. **Nicht blockierend** für Task-Abschluss — als Stretch-Goal markieren.
- [ ] Schritt 4: Keine Backend-Änderung nötig (reine Erklärtexte). `tests/test_web_shell.py` ggf. um einen Snapshot-Assert erweitern, der die neuen Hint-Texte in der ausgelieferten HTML erwartet (`"koerperbetont" in response.text` o. ä.) — nur falls das Projekt bereits HTML-Text-Assertions in `test_web_shell.py` nutzt (vorher prüfen, keinen neuen Test-Stil einführen).

### Task 5 (P1): Referenzbild auf `.jpg`/`.jpeg` festlegen

**Dateien:** `apps/web/contracts.py`, `apps/web/static/index.html` (Phase 4)

- [ ] Schritt 1: Test zuerst (`tests/test_web_contracts.py`): `Phase1ScanRequest(image_path="foo.png", ...)` soll `ValueError`/422 auslösen; `image_path="foo.jpg"` und `"foo.jpeg"` sollen akzeptiert werden; `image_path=None` weiterhin erlaubt (Feld bleibt optional).
- [ ] Schritt 2: `normalize_image_path` (`contracts.py:102-108`) erweitern: nach `strip()` prüfen `cleaned.lower().endswith((".jpg", ".jpeg"))`, sonst `raise ValueError("image_path must be a .jpg/.jpeg file")`.
- [ ] Schritt 3: HTML-Input in Phase 4 ergänzen: `<input id="image-file-input" type="file" accept="image/jpeg">` zusätzlich zum bestehenden Pfad-Textfeld (Radi144 hat ebenfalls echten Datei-Upload, siehe `user_workflow.html` „📷 Bild hochladen“). Placeholder-Text von `klient-reference.png` auf `klient-reference.jpg` ändern.
- [ ] Schritt 4 (minimal-invasiv, kein neuer Upload-Endpoint): Datei-Input liest lokal nur den Dateinamen aus (`input.files[0].name`) und schreibt ihn in das bestehende Pfad-Textfeld — echte Datei-Upload-Infrastruktur ist laut `2026-07-04`-Design-Spec „Nicht in Scope“ für einen minimalen Schritt; falls ein echter Server-Upload gewünscht ist, das als **separaten** Folge-Task markieren (nicht Teil dieses Plans, um Scope nicht zu sprengen).
- [ ] Schritt 5: `pytest tests/test_web_contracts.py -q` grün, danach vollständige Suite.

### Task 6 (P1): Workbench-Modus erklären + „Hardware-Truth nicht verfügbar“ verbessern

**Dateien:** `apps/web/static/index.html` (Phase 5), `apps/web/static/app.js`

- [ ] Schritt 1: Unter dem `#workbench-mode`-Select einen `.field-hint` ergänzen: „Standard: reine Anzeige der Hardware-Klassifikation. Expert: zusätzliche Rohdaten/Warnungen für Diagnosezwecke, kein Einfluss auf das Scan-Ergebnis.“ (Wirkung anhand `apps/web/hardware_truth.py`/`main.py` `build_hardware_status_payload(mode=...)` vor Formulierung kurz verifizieren, keine Erfindung.)
- [ ] Schritt 2: `loadHardwareTruth()` Catch-Block (`app.js:144-147`) verbessern: statt nur `"Hardware-Truth nicht verfuegbar."` einen Hinweis mit Ursache-Kategorie und Retry-Button rendern, z. B. `<p class="hardware-note">Hardware-Truth-Endpunkt aktuell nicht erreichbar (Server-Neustart oder Ressourcenengpass). <button id="retry-hardware-truth" class="secondary-button" type="button">Erneut versuchen</button></p>`, Retry-Button ruft `loadHardwareTruth()` erneut auf.
- [ ] Schritt 3: Keine Backend-Änderung. `tests/test_web_workbench_runtime.py` bereits vorhanden — prüfen ob dort ein Fehlerfall-Test sinnvoll ergänzt werden kann (JS-seitig, sonst manuelle Verifikation).

### Task 7 (P2 — Backend-Erweiterung, größter Scope): Harmonisierung als eigene Phase + Impuls/Pause/Solfeggio-Zyklus

**Dateien:** `services/harmonization_worker.py`, `apps/web/contracts.py`, `apps/web/harmonization.py`, `apps/web/static/index.html`, `apps/web/static/app.js`, `apps/web/static/app.css`, `apps/cli/commands/harmonize.py` (falls CLI-Flags mitziehen sollen — siehe Schritt 6)

Dies ist der größte Einzeltask. Zwei Teilziele: **(A)** Harmonisierung/Export aus Phase 10 in eine **eigene Phase 11** auslagern (Wizard wird 10→11 Phasen, `registry`/Stepper entsprechend anpassen), **(B)** Impuls/Pause/Solfeggio-Parameter im Backend nachrüsten.

- [ ] Schritt 1 (Test zuerst, Backend): `tests/test_harmonization_worker.py` (neu oder erweitern falls vorhanden — vorher prüfen) — Test für `start_harmonization_job(..., pulse_seconds=3, pause_seconds=2, duration_factor=1, solfeggio_base=432.0)`: Job-Objekt speichert diese Felder, `total_cycles` wird aus `duration_factor * 21 * 60 / (pulse_seconds + pause_seconds)` berechnet statt nur `duration_minutes * 60`.
- [ ] Schritt 2: `services/harmonization_worker.py:489-494` (`start_harmonization_job`) um optionale Parameter erweitern: `pulse_seconds: float = 3.0, pause_seconds: float = 2.0, duration_factor: int = 1, solfeggio_base: float = 432.0`. Rückwärtskompatibel: bestehende Aufrufer (CLI `harmonize.py`, Workflow `step12_harmonize.py`) funktionieren unverändert mit Defaults.
- [ ] Schritt 3: `apps/web/contracts.py` `HarmonizationRequest` um dieselben Felder erweitern (mit denselben Defaults, `Field(gt=0)` für Sekundenwerte), `apps/web/harmonization.py` `WorkerHarmonizationService.start()` reicht sie durch.
- [ ] Schritt 4 (Frontend, Struktur): In `index.html` die bestehende `finalize-phase`-Section (aktuell Berichtskatalog + Vorschau + Harmonisierung kombiniert) aufteilen:
  - Phase 10 „Berichtskatalog & Export“ behält nur Berichtsliste + Inline-Vorschau + Exportlinks.
  - **Neue Phase 11** „Harmonisierung & Abschluss“ (`data-step="10"`) bekommt das komplette Harmonisierungs-Formular inkl. neuer Felder: Impuls (Sekunden), Pause (Sekunden), Dauer-Faktor (× 21 Min, mit Hinweistext „1 = 21 Min · 7 = 147 Min · 21 = 441 Min“ analog Radi144), Solfeggio-Basis als Radio-Karten (432/528/429.62/498.90 Hz).
  - Stepper-Button-Liste um einen 11. Eintrag ergänzen; **zwei Stellen synchron halten:** (1) client-seitiges Fallback-Array in `app.js:364-376` (`bootstrapWorkbench`, greift wenn `/api/workbench/registry` fehlschlägt) um `{id:"harmonize",label:"Harmonisierung & Abschluss"}` erweitern, (2) serverseitige Quelle `apps/web/workbench_registry.py` (`build_workbench_registry()`, exponiert über `GET /api/workbench/registry` in `apps/web/workbench.py:17-19`) — dort die Step-Liste um denselben Eintrag ergänzen, da dies im Normalfall (kein Fetch-Fehler) die tatsächlich verwendete Quelle ist.
- [ ] Schritt 5: `formHarmonizationPayload()` (`app.js:48-62`) um die neuen Felder erweitern (`pulse_seconds`, `pause_seconds`, `duration_factor`, `solfeggio_base`), CSS für Radio-Karten (Solfeggio-Auswahl) aus Task 4 Stretch-Goal-Pattern wiederverwenden falls dort umgesetzt, sonst einfache `<select>` als Minimalversion.
- [ ] Schritt 6 (optional, nur falls gewünscht): CLI-Flags `--pulse-seconds`/`--pause-seconds`/`--duration-factor`/`--solfeggio-base` in `apps/cli/commands/harmonize.py` ergänzen, damit `Run-MultiplexScan.ps1`/CLI-Nutzer dieselbe Zyklus-Kontrolle wie die Web-UI erhalten (echte Parität statt nur Web-seitiger Anreicherung). **Nur umsetzen, wenn Nutzer das explizit bestätigt** — sonst reicht rückwärtskompatibler Default für CLI/Workflow.
- [ ] Schritt 7: Vollständige Testsuite grün, inkl. neuer `test_harmonization_worker.py`.

### Task 8 (P2): Berichtskatalog professionalisieren

**Dateien:** `apps/web/static/index.html` (neue Phase 10), `apps/web/static/app.js` (`loadReports`, `renderReportPreview`), `apps/web/static/app.css`

- [ ] Schritt 1: Aktuelle flache `report-item`-Buttons (`app.js:250-255`) um sichtbare Metadaten erweitern: Datum/Session statt nur `kind — name`. Datenquelle: `client.sessions[].files[]` liefert laut `reports.py` bereits `kind`/`name`/`id` — prüfen ob zusätzlich ein Zeitstempel-Feld existiert (`reports.py` Zeile ~348-430 `_group_entries`); falls ja, im Item-Label ergänzen.
- [ ] Schritt 2: Gruppierung visuell aufwerten: `.report-group` als einklappbare `<details>/<summary>` statt flacher `<div>`-Liste (reduziert Unübersichtlichkeit bei vielen Clients/Sessions, siehe `PHASE_4_FRONTEND_UIUX_GOOGLE_2026.md` Befund U6 „Large Report DOM“).
- [ ] Schritt 3: Inline-Vorschau-Karte (`report-preview-card`) um einen klar abgesetzten Header mit Datei-Icon je Typ (HTML/JSON/TXT/PDF) ergänzen, CSS-Klassen `.report-preview-frame`/`.report-preview-text` beibehalten (funktionieren bereits, nur visuelle Politur).
- [ ] Schritt 4: Manuelle Verifikation gegen reale Report-Daten (mind. 4 Klienten, wie in Abschnitt 4 Check 5 vorhandener Scan-Output).

### Task 9 (P3 — größere Politur, nach P0–P2): Radi144-Parität — Erklärkästen, Auswahl-Chips, Snapshot-Rhythmus

**Dateien:** durchgängig `index.html`, `app.css`

- [ ] Schritt 1: Für jede Phase mit komplexer Eingabe (3, 4, 5, 7-neu) einen `.notice`- oder neuen `.hint-box`-Block direkt unter dem `step-header` ergänzen, im Ton der Radi144-Referenz („📚 Hinweis zum Fokus: Der Fokus-Text wird ... transformiert und beeinflusst die gesamte Matrix-Berechnung.“) — Texte **ausschließlich** aus realem Code-Verhalten ableiten (siehe Task 4 als Vorlage), keine Fantasie-Erklärungen.
- [ ] Schritt 2: Wo fachlich sinnvoll (Profilvorlage, Entropie-Modus, Solfeggio-Basis aus Task 7) `<select>` durch Radio-Karten-Gruppen ersetzen (Prinzip 5 aus Design-Spec), CSS-Vorlage `.step-card` + neue `.choice-card`/`.choice-card.selected`.
- [ ] Schritt 3: Am Ende jeder Eingabe-Phase (3, 4, 5) einen Mini-Snapshot einblenden (Radi144-Prinzip 6 „Zusammenfassungs-/Snapshot-Karten vor kritischen Aktionen“) — kann dieselbe `renderReviewCards`-Logik aus Task 1 nutzen, nur lokal auf die jeweilige Phase beschränkt (z. B. „Aktueller Fokus: Bronchien, Top-5“ direkt in Phase 3).
- [ ] Schritt 4: Farbcodierung prüfen: `--phase-diagnose/-analyse/-harmonize` Tokens (laut `RADIQUANT4_RADIMORPHIC_KONTRAKT_REFERENZ.md` Abschnitt 11) sind als Konzept vorhanden — prüfen ob sie bereits in `app.css` aus Task 8 des Alignment-Plans real genutzt werden (`grep -- "--phase-" app.css`); falls nur deklariert, aber nicht auf Phasen angewendet: `step-icon`/`.eyebrow` je Phasen-Gruppe (Aufnahme=diagnose, Analyse-Lauf=analyse, Harmonisierung=harmonize) einfärben.
- [ ] Schritt 5: Dies ist ein Politur-Task ohne feste Fertigstellungs-Metrik — als „gut genug“ gilt: alle P0–P2-Punkte behoben, mindestens 3 Erklärkästen ergänzt, Farbcodierung an mind. 3 Phasen sichtbar, volle Testsuite weiterhin grün.

---

## 3. Reihenfolge-Empfehlung

1. **Task 1** (P0-Bugfix, klein, hoher Nutzen — behebt den irritierendsten Befund f)
2. **Task 2, 3, 5, 6** (P1, unabhängig voneinander, können parallel/in beliebiger Reihenfolge)
3. **Task 4** (P1, unabhängig)
4. **Task 7** (P2, größter Scope — Backend zuerst testen, dann Frontend-Strukturänderung)
5. **Task 8** (P2, unabhängig von Task 7 im Kern, aber Phase-10-Umbau aus Task 7 Schritt 4 zuerst abschließen, um keine doppelte HTML-Umstrukturierung zu riskieren)
6. **Task 9** (P3, zuletzt — Politur auf stabiler Basis)

Nach **jedem** Task: `pytest tests -q` (Ziel weiterhin `262 passed, 2 skipped` + neue Tests grün) und manuelle Verifikation gemäß Abschnitt 4.

---

## 4. Verifikationsplan (nach jedem Task auszuführen)

Server-Start (**wichtig:** das Projekt-`.venv`, nicht ein anderes venv auf dem `PATH`, verwenden — siehe `docs/deep-audit-2026-07-07/SITUATION_KONSOLIDIERT_BRANCHES_UI_ANALYSELAUF.md` Abschnitt „uvicorn falsches venv“):

```powershell
cd C:\morphic_v1\.worktrees\operator-workbench-phase1
$env:PYTHONUTF8=1; $env:OPENBLAS_NUM_THREADS=1
& C:\morphic_v1\.venv\Scripts\python.exe -m uvicorn apps.web.main:app --host 127.0.0.1 --port 8000
```

| # | Check | Erwartung |
|---|---|---|
| 1 | Review-Cards (Task 1) | Phase 6 zeigt gefüllte `#review-client`/`#review-focus`/`#review-profile`/`#review-hardware` statt leerer Boxen |
| 2 | Auto-Advance (Task 1) | Klick „Analyse starten“ → UI springt sofort zu Phase 7, Timeline läuft live mit |
| 3 | Fokushistorie (Task 3) | Nach 2 Scans mit unterschiedlichem Fokus erscheinen Chips in Phase 3, Klick übernimmt Wert |
| 4 | Hinweistexte (Task 4, 6) | Phase 4/5 zeigen Erklärtext unter den Selects, kein reiner `<select>` ohne Kontext mehr |
| 5 | Bild-Validierung (Task 5) | POST mit `image_path=foo.png` → 422; mit `foo.jpg` → 200 |
| 6 | Harmonisierung eigene Phase (Task 7) | Stepper zeigt 11 Phasen; Phase 11 enthält Impuls/Pause/Solfeggio-Felder; Job-Start liefert `total_cycles` passend zu `duration_factor` |
| 7 | Vollständige Suite | `& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests -q` → alle grün, keine Regression ggü. `262 passed, 2 skipped` |
| 8 | Scan End-to-End weiterhin funktionsfähig | Preview → Start → Poll → `completed` → Results → Reports, wie in `SITUATION_KONSOLIDIERT_BRANCHES_UI_ANALYSELAUF.md` Abschnitt 10/11 dokumentiert |

---

## 5. Nicht-Ziele (explizit ausgeschlossen)

- Echter Server-seitiger Datei-Upload für Referenzbilder (nur Dateiname-Übernahme ins bestehende Pfadfeld, siehe Task 5 Schritt 4).
- Netzwerk-Integration gegen einen echten radiquant4-Server (Alignment-Layer ist bereits vollständig vorbereitet, siehe Abschnitt 0; echte Anbindung folgt separatem Plan, sobald ein Zielserver benannt ist).
- Astro/React/Tailwind-Framework-Migration.
- CLI-Flag-Erweiterung für Harmonisierungs-Zyklusparameter (Task 7 Schritt 6), außer explizit vom Nutzer bestätigt.
