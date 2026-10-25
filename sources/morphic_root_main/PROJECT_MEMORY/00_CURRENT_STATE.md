# MORPHIC ENGINE V1 - AKTUELLER ZUSTAND

**Letztes Update:** 2026-07-08
**Session:** Radi144-UI/UX-Konsolidierung (Operator Workbench) + radiquant4-Vorbereitung
**Aktiver Arbeitsort:** `.worktrees/operator-workbench-phase1` (Branch `operator-workbench-phase1`) — **NICHT** `master`
**Status:** Radiquant4-Alignment-Layer vollstaendig (9/9 Tasks). UI/UX-Konsolidierungsplan: **alle 9 Tasks fertig** (Commit `d8c75d4`).

---

## ⚠️ WICHTIG FUER JEDE NEUE SESSION (z. B. Claude Code CLI)

1. **Nicht im Repo-Root (`C:\morphic_v1`) weiterarbeiten.** Die aktive Entwicklung findet im Git-Worktree
   `C:\morphic_v1\.worktrees\operator-workbench-phase1` (Branch `operator-workbench-phase1`) statt.
   `cd` dorthin, bevor Code geaendert wird.
2. **Lies zuerst:** `docs/superpowers/plans/2026-07-07-operator-workbench-radi144-uiux-consolidation.md`
   (im Worktree UND im Root vorhanden, da `docs/` auf `master` committet wurde). Das ist der Arbeitsplan
   mit allen 9 Tasks, TDD-Schritten, Datei:Zeile-Belegen und einem Verifikationsplan.
3. **Bekannter Store-Zustand auf `master`:** `apps/web/static/app.js` und `apps/web/static/index.html`
   haben dort **unbezogene, alte uncommittete Aenderungen** aus einer fruehen Session (Diff-Stat: 16
   Zeilen app.js, 196 Zeilen index.html). Diese sind **nicht** Teil der aktuellen Konsolidierungsarbeit
   und wurden bewusst nicht angefasst. Vor jeder Aktion auf `master` selbst pruefen (`git diff`), ob sie
   noch gebraucht werden oder verworfen werden koennen — nicht ungefragt loeschen oder committen.
4. **Der Worktree ist der einzige Ort mit dem aktuellen Funktionsstand** (10-Phasen-Operator-Workbench,
   12-Substep-Timeline, radiquant4-Alignment-Layer, laufende UI/UX-Konsolidierung).

---

## PROJEKTHISTORIE (KURZ, FUER KONTEXT)

1. **Bis 2026-07-02:** `apps/cli/main.py`-Refactoring (9.543 → 72 Zeilen), 153 Tests gruen (siehe Git-Historie
   auf `master` fuer Details — dieser Abschnitt der Datei ist historisch, nicht mehr der aktuelle Fokus).
2. **2026-07-04/05:** Deep-Audits (`docs/deep-audit-2026-07-04/`, `docs/deep-audit-2026-07-05/`),
   radiquant4-Referenzanalyse (`RADIQUANT4_RADIMORPHIC_KONTRAKT_REFERENZ.md`), radiquant4-Alignment-Plan
   erstellt und **vollstaendig umgesetzt** (Standard-Output-Adapter, Operator-Context/Ownership,
   Entitlement-Stub, Quantum-Pfad-Haertung, deterministischer Seed, Substep-Mapping, DSGVO-Haertung,
   Design-Tokens — alle 9 Tasks, siehe `docs/superpowers/plans/2026-07-05-morphic-v1-radiquant4-alignment.md`).
3. **2026-07-06:** Operator-Workbench Tasks 4-6 (10-Phasen-Frontend-Rebuild, Review-Gate/Result-Workspace,
   Pipeline-View-Trennung) im Worktree `operator-workbench-phase1` umgesetzt, committet, `owner_id`-Bugfix
   in `LocalScanJobService.start()`.
4. **2026-07-07 (Vormittag):** Kritischer Bug im Worktree gefunden und behoben (korrupter uncommitteter
   Stand mit SyntaxError in `main.py`) — siehe `docs/deep-audit-2026-07-07/SITUATION_KONSOLIDIERT_BRANCHES_UI_ANALYSELAUF.md`
   fuer die vollstaendige forensische Aufarbeitung. Danach: Radi144-Visual-Alignment portiert (Commit
   `bcfcd2f` — Step-Header/Icon/Subtitle, 12-Substep-Timeline in Phase 7).
5. **2026-07-07 (Nachmittag):** Nutzer-Feedback mit 8 konkreten UI/UX-Luecken (a-h) nach Live-Test der
   Workbench gegen die Radi144-Referenz (`http://localhost:8090/user_workflow.html`). Daraus entstand
   `docs/superpowers/plans/2026-07-07-operator-workbench-radi144-uiux-consolidation.md`. **Umsetzung
   laeuft aktuell, siehe Abschnitt "Fortschritt" unten.**

---

## FORTSCHRITT: RADI144-UI/UX-KONSOLIDIERUNGSPLAN

Referenz: `docs/superpowers/plans/2026-07-07-operator-workbench-radi144-uiux-consolidation.md`
Aktueller Commit im Worktree: **`d8c75d4`** ("feat: radi144 parity polish - phase colors, hint-boxes, mini-snapshot (task 9)")

| Task | Titel | Status | Details |
|---|---|---|---|
| 0 | radiquant4-Alignment-Status | ✅ verifiziert vollstaendig | Alle 9 Tasks des Vorgaengerplans bestaetigt (siehe Plan Abschnitt 0) |
| 1 | Review-Cards fuellen + Auto-Advance nach Scan-Start | ✅ **fertig** | `renderReviewCards` wird jetzt via `window.MorphicWorkbenchOnStepEnter`-Hook aufgerufen; `startScanJob()` ruft `navigate(1)` |
| — | **Bonus-Fix (nicht im Original-Plan, waehrend Task 6 gefunden):** Hardware-Truth-Rendering-Bug | ✅ **fertig** | Backend liefert `components` als Dict (`hardware_truth.py`), Frontend erwartete Array → `TypeError` → immer "nicht verfuegbar". Fix in `renderHardwareTruth()`: `Object.values()`-Fallback + `gate_warnings`-Anzeige |
| 2 | Fokus-Feld Pflicht/Optional + Hauptsymptom | ✅ **fertig** (Commit `18b2c4f`) | HTML+JS fertig (Pflicht-Badge, Hinweistext, `main_symptom`-Feld+Payload). Backend-Regressionstests fuer `main_symptom`/Focus-Merge-Edge-Cases in `tests/test_web_launcher.py` ergaenzt |
| 3 | Fokushistorie (localStorage) | ✅ **fertig** | `workbench-state.js` (`loadFocusHistory`/`saveFocusToHistory`), `workbench-render.js` (`renderFocusHistoryChips`), `app.js`-Wiring, CSS via Commit `38fc4d3` |
| 4 | Profilvorlage/Entropie-Modus Wirkungserklaerung | ✅ **fertig** (Commit `53c405e`) | Erklaertexte in HTML (echte Werte aus `scan.py:422-484`). Choice-Card-UI an Profilvorlage/Entropie-Modus-Selects gewired |
| 5 | Referenzbild auf `.jpg`/`.jpeg` | ✅ **fertig** (Commit `bbda9ae`) | HTML-Input (`type="file" accept="image/jpeg"`) + Backend-Validierung in `contracts.py` `normalize_image_path()` durchgesetzt |
| 6 | Workbench-Modus erklaeren + Hardware-Truth-Fehlertext | ✅ **fertig** (verifiziert 2026-07-08) | Alle 3 Plan-Schritte erfuellt: `.field-hint` unter `#workbench-mode`-Select erklaert Standard/Expert-Wirkung (index.html:216), `loadHardwareTruth()`-Catch-Block zeigt Ursache-Kategorie + Retry-Button (app.js:139-157). Schritt 3 (Fehlerfall-Test) bewusst nicht als Backend-Test umgesetzt: Fehlerpfad ist client-seitig (Netzwerk/Server-Fehler), kein Backend-Test-Fall — kein JS-Test-Runner im Projekt vorhanden, laut Plan "sonst manuelle Verifikation" |
| 7 | Harmonisierung eigene Phase 11 + Impuls/Pause/Solfeggio-Backend | ✅ **fertig** (Commit `ea3a457`, 2026-07-08) | Backend-Kette (Schritt 1-3) fertig und live end-to-end verifiziert: `HarmonizationJob`/`start_harmonization_job()` um `pulse_seconds`/`pause_seconds`/`duration_factor`/`solfeggio_base` erweitert (`services/harmonization_worker.py`), durchgereicht via `contracts.py` → `main.py` → `harmonization.py` (Server-Test: POST mit pulse=4/pause=1/factor=1 lieferte korrekt `total_cycles=252`). Frontend-Struktur (Schritt 4) fertig: `workbench_registry.py` hat jetzt 11 Steps (`finalize`="Berichtskatalog & Export", neu `harmonize`="Harmonisierung & Abschluss"), `app.js`-Fallback synchron, `index.html` in Phase 10 (nur Berichtskatalog) + neue Phase 11 (`harmonize-phase`, Impuls/Pause/Dauer-Faktor-Formular + Solfeggio-Choice-Cards, wiederverwendet `.choice-card`-CSS aus Task 4 ohne Änderung) aufgeteilt. Neue Testdatei: `tests/test_harmonization_worker_pulse_pause.py`. Schritt 6 (CLI-Flags in `harmonize.py`) bewusst ausgelassen — laut Plan nur bei expliziter Nutzerbestätigung umzusetzen, wurde nicht angefragt |
| 8 | Berichtskatalog professionalisieren | ✅ **fertig** (Commit `fbfd75c`, 2026-07-08) | `loadReports()` in `app.js` umgebaut: `<details>/<summary>`-Gruppierung (Client + Session) statt flacher `<div>`-Liste, wiederverwendet bereits vorhandene, bis dahin ungenutzte CSS-Klassen (`.report-client-group`/`.report-session-group` etc.). Echte Metadaten aus `reports.py` `_group_entries()`: Session-/Dateizahl, `modified_at`-Zeitstempel (formatiert via `toLocaleString`). Datei-Typ-Icons (HTML/JSON/TXT/PDF) via `REPORT_KIND_ICONS`, auch im Preview-Header. Live gegen echte Report-Daten verifiziert (5 Klienten, 555 Dateien in `C:/Benutzer_*_Start`) |
| 9 | Radi144-Paritaet Politur | ✅ **fertig** (Commit `d8c75d4`, 2026-07-08) | Phasen-Farbcodierung: alle 11 Sections tragen jetzt `.phase-diagnose`/`.phase-analyse`/`.phase-harmonize` (nutzt die bereits deklarierten, bis dahin ungenutzten `--rq-phase-*`-Tokens aus dem radiquant4-Alignment). Gruppierung: diagnose=Aufnahme/Vorbereitung (Phasen 1-6), analyse=Ausfuehrung/Auswertung (Phasen 7-10), harmonize=Phase 11. Zwei neue `.hint-box`-Bloecke im Radi144-Ton (Phase 3: Top-N erweitert auch den Adaptive-Limits-Screening-Umfang, aus `scan.py` `_effective_adaptive_top_k`; Phase 5: ehrliche Hardware-Klassifikationsstufen aus `build_hardware_truth_snapshot()`) — zusammen mit den bestehenden `.field-hint`s aus Task 4/6 sind es 3+ Erklaerkaesten. Live-Mini-Snapshot in Phase 3 (`#focus-mini-snapshot`, `updateFocusMiniSnapshot()`-Hook auf Step-Enter + Formular-Input). Live verifiziert: 6 phase-diagnose + 4 phase-analyse + 1 phase-harmonize, 2 hint-boxes, Mini-Snapshot rendern korrekt |

**Testlauf 2026-07-08 (nach Commit `d8c75d4`):** `273 passed, 2 skipped` (voller `pytest tests -q`-Lauf, ~101s), zusätzlich live gegen den Server verifiziert.

### ⚠️ NAECHSTER KONKRETER SCHRITT

**Alle 9 Tasks des Radi144-UI/UX-Konsolidierungsplans sind abgeschlossen, verifiziert und committet**
(letzter Commit `d8c75d4`). Der Plan `docs/superpowers/plans/2026-07-07-operator-workbench-radi144-uiux-consolidation.md`
ist damit vollstaendig umgesetzt. Moegliche naechste Schritte, falls gewuenscht:

1. Neue Anforderungen/Feedback vom Nutzer nach einem erneuten Live-Test gegen die Radi144-Referenz
   (`http://localhost:8090/user_workflow.html`) einholen.
2. Schritt 6 aus Task 7 (CLI-Flags `--pulse-seconds`/`--pause-seconds`/`--duration-factor`/`--solfeggio-base`
   in `apps/cli/commands/harmonize.py`) nachziehen, falls echte CLI/Web-Paritaet gewuenscht wird — war bewusst
   ausgelassen, da nicht explizit bestaetigt.
3. Ggf. Merge von `operator-workbench-phase1` nach `master` vorbereiten/besprechen.

---

## VERIFIKATION (IMMER NACH JEDER AENDERUNG)

```powershell
cd C:\morphic_v1\.worktrees\operator-workbench-phase1

# Tests (Projekt-.venv verwenden, NICHT irgendein anderes venv auf PATH!)
$env:PYTHONUTF8="1"
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests -q
# Letzter bekannter Stand: 262 passed, 2 skipped (vor WIP-Commit 3a957a3;
# nach 3a957a3 wurden gezielt 44 relevante Tests erneut gruen verifiziert,
# voller Lauf empfohlen vor naechstem Commit)

# JS-Syntax-Check
node --check apps/web/static/app.js
node --check apps/web/static/workbench-render.js
node --check apps/web/static/workbench-state.js

# HTML-Struktur-Check (kein Node/HTML-Linter im Projekt, daher Python html.parser)
& C:\morphic_v1\.venv\Scripts\python.exe -c "from html.parser import HTMLParser; ..."
# (vollstaendiges Snippet siehe Commit-Message von 3a957a3 im Git-Log)

# Server starten (WICHTIG: Projekt-.venv, sonst ModuleNotFoundError: numpy,
# siehe docs/deep-audit-2026-07-07/SITUATION_KONSOLIDIERT_BRANCHES_UI_ANALYSELAUF.md)
$env:OPENBLAS_NUM_THREADS="1"
& C:\morphic_v1\.venv\Scripts\python.exe -m uvicorn apps.web.main:app --host 127.0.0.1 --port 8000
```

**Bekanntes Umgebungsproblem:** Der Host hat oft nur 3-4 GB freien RAM, was zu
`OpenBLAS error: Memory allocation still failed` bei `import numpy` fuehren kann. Kein Code-Bug — vor
Testlaeufen ggf. andere Anwendungen schliessen. `OPENBLAS_NUM_THREADS=1` reduziert das Risiko.

**Radi144-Referenz zum Live-Vergleich:** `http://localhost:8090/user_workflow.html` (laeuft als
separater Server, nicht Teil dieses Repos — nur zum visuellen/strukturellen Abgleich verwenden).

---

## SYSTEMKONFIGURATION

- **Python:** `.venv/` im Repo-Root `C:\morphic_v1\.venv` (wird von allen Worktrees geteilt/referenziert)
- **Test-Runner:** `& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests/` (aus dem jeweiligen
  Worktree-Verzeichnis heraus, damit relative Pfade stimmen)
- **Git-Worktrees:**
  ```
  C:/morphic_v1                                       [master]                   — NICHT aktiv bearbeiten
  C:/morphic_v1/.worktrees/apps-web-phase1            [feature/apps-web-phase1]  — inaktiv/alt
  C:/morphic_v1/.worktrees/operator-workbench-phase1  [operator-workbench-phase1] — ★ AKTIV
  C:/morphic_v1/.worktrees/radi144-workflow-ux        [feature/radi144-workflow-ux] — alternativer,
                                                          nicht gemergter UI-Ansatz (siehe
                                                          SITUATION_KONSOLIDIERT_BRANCHES_UI_ANALYSELAUF.md
                                                          Abschnitt 2 fuer Vergleich der Branches)
  ```

---

## WICHTIGE DOKUMENTE (LESEREIHENFOLGE FUER NEUEN KONTEXT)

1. **Diese Datei** (Golden Record, aktuellster Stand)
2. `docs/superpowers/plans/2026-07-07-operator-workbench-radi144-uiux-consolidation.md` (der aktive Plan)
3. `docs/deep-audit-2026-07-07/SITUATION_KONSOLIDIERT_BRANCHES_UI_ANALYSELAUF.md` (Branch-Historie,
   Bug-Forensik, Radi144-Zieldefinition)
4. `docs/deep-audit-2026-07-07/README.md` (Executive Summary der Codebase, 2026-07-07)
5. `docs/deep-audit-2026-07-05/RADIQUANT4_RADIMORPHIC_KONTRAKT_REFERENZ.md` (radiquant4-Zielkontrakt,
   fuer spaetere echte Integration)
6. `CLAUDE.md` (Schnellreferenz, verweist hierher)

---

## KRITISCHE PFADE

```
.worktrees/operator-workbench-phase1/apps/web/static/index.html       10-Phasen-Wizard-HTML
.worktrees/operator-workbench-phase1/apps/web/static/app.css          Design-Tokens + Styles (CSS-Luecke, s.o.)
.worktrees/operator-workbench-phase1/apps/web/static/app.js           Business-Logik/Event-Wiring
.worktrees/operator-workbench-phase1/apps/web/static/workbench-render.js  Rendering (DOM), keine Fetches
.worktrees/operator-workbench-phase1/apps/web/static/workbench-state.js  Zustand + Fokushistorie
.worktrees/operator-workbench-phase1/apps/web/static/workbench-api.js    Alle fetch()-Aufrufe
.worktrees/operator-workbench-phase1/apps/web/contracts.py            Pydantic-Request/Response-Schemas
.worktrees/operator-workbench-phase1/apps/web/hardware_truth.py       Hardware-Klassifikation (Dict-Contract!)
.worktrees/operator-workbench-phase1/apps/web/harmonization.py        Harmonisierungs-Service-Adapter
.worktrees/operator-workbench-phase1/services/harmonization_worker.py  Impuls/Pause-Zyklus-Luecke (Task 7)
.worktrees/operator-workbench-phase1/apps/cli/commands/scan.py:422-484  Reale Profilvorlage/Entropie-Semantik
.worktrees/operator-workbench-phase1/apps/cli/workflow/substep_manifest.py  12-Substep-Mapping (Timeline-Quelle)
```

---

**Golden Record bei Context-Loss:** Diese Datei zuerst lesen. Danach den Plan (Abschnitt "Wichtige Dokumente").
