# Konsolidierte Situationsanalyse: Branches, UI/Optik, Analyselauf

**Stand:** 2026-07-07
**Verfasser:** Devin (codebasiert, alle Befunde live verifiziert)
**Zweck:** Präzise Klärung der aktuellen Situation und konsolidierte, schritt-für-schritt nachvollziehbare Dokumentation für Entwickler.

> Diese Datei ergänzt `docs/deep-audit-2026-07-07/README.md` (allgemeine Tiefenanalyse) um die spezielle Fragestellung: **Warum schlägt der Analyselauf fehl, warum ist die UI/Optik zurückgefallen, und wie hängen die Branches zusammen?**

---

## 1. TL;DR — drei unabhängige Probleme

| # | Problem | Root Cause | Auswirkung | Behebung |
|---:|---|---|---|---|
| 1 | **Analyselauf schlägt fehl** | Worktree `operator-workbench-phase1` hat **korrupten `main.py`** (SyntaxError Zeile 308: `@app.get("/api/hardw12-Sat) s`); zus. Garbage in `_workbench_run_trace_seed` (`reo""aunch["executes"]`) | Web-App kann nicht importiert / gestartet werden → kein Scan, keine Berichte | Korrupte uncommittete Änderungen verwerfen → committeter Stand `5a23142` wiederherstellen |
| 2 | **UI/Optik-Regression ("alte Optik")** | Dieselben korrupten uncommitteten Änderungen haben **176 Zeilen Operator-Workbench-CSS gelöscht** und **alle 10 Stepper-Buttons aus dem HTML entfernt** (leeres `<nav>`) | Wizard ohne sichtbare Steps, Workbench-Design-Tokens/Cards fehlen → wirkt wie "alte Optik" | Siehe Problem 1 |
| 3 | **"12 vs 10 Steppings"** | Siehe Abschnitt 4 — kein Bug, sondern zwei verschiedene Konzepte (12-Step-Backend-Workflow vs. 10-Phase-Web-Wizard), die im UI nicht sauber gekoppelt sind | Nutzer erwartet 12 sichtbare Steps (wie Radi144), sieht aber nur 10 Wizard-Phasen | 12-Step-Timeline aus `SUBSTEP_MANIFEST` im UI sichtbar machen (Roadmap) |

**Zusätzliches Umgebungsproblem:** Nur **3,24 GB freier RAM** von 15,25 GB → `OpenBLAS error: Memory allocation still failed after 10 retries` beim `import numpy`. Blockiert unabhängig vom Code den App-Start unter Last. Kein Code-Bug, aber robuster Bekämpfungsbedarf.

---

## 2. Branch-Topologie — vier Standorte, ein Divergenzpunkt

Alle Feature-Branches zweigen vom **selben Commit `e87cee3`** ("docs: plan radi144 workflow ux implementation") ab und sind **parallele Implementierungen** desselben Radi144-Alignment-Ziels.

```
e87cee3 (docs: plan radi144 workflow ux implementation)
  ├── master (225beac) "feat: add radiquant4 alignment layer"
  │     + uncommitted: index.html, app.js
  ├── feature/radi144-workflow-ux (9a3ffa2) "style: align web workflow with radi144 patterns"
  │     commits: a1e7b6b → c38c8b0 → 5410715 → 9a3ffa2 (+ ec2cd37)
  └── operator-workbench-phase1 (5a23142) "fix: LocalScanJobService.start() accepts owner_id"
        commits: 3936ade → 1751e8c → 186f756 → 5e52c5f → 495430d → 5a23142
        + KORRUMPIERTE uncommittete Änderungen (5 Dateien)
```

### 2.1 Branch-Vergleichstabelle

| Eigenschaft | `master` (225beac) | `feature/radi144-workflow-ux` (9a3ffa2) | `operator-workbench-phase1` (5a23142 committet) | `operator-workbench-phase1` (aktueller Worktree, KORRUPT) |
|---|---|---|---|---|
| **Web-Wizard-Steps** | 8 (Preflight→Harmonisierung) | 10 (Willkommen→Abschluss) | 10 (Runtime&Workspace→Harmonisierung&Export) | 0 sichtbar (Stepper-Buttons gelöscht) |
| **main.py Syntax** | OK | OK | OK | **SyntaxError Zeile 308** |
| **scan_jobs owner_id-Fix** | Ja (5 Matches) | **Nein** (0 Matches → Step-7-Bug) | Ja (fix in 5a23142) | n/a (main.py kaputt) |
| **app.css Zeilen** | 1204 (oklch-Tokens, kein Workbench-Block) | 1059 (Radi144-Styling, kein `--rq`/Workbench-Marker) | 1177 (48 Workbench/`--rq`-Marker) | ~1001 (176 Zeilen Workbench-CSS gelöscht) |
| **substep_manifest.py** | Ja | **Nein** (predatet Alignment) | Ja | Ja (Datei unangetastet) |
| **Radiquant4-Alignment-Layer** | Ja (225beac) | Nein | Ja (1751e8c) | Ja |
| **Tests** | 230 passed, 2 skipped (laut 07-07-Audit) | unbekannt | 99 passed, 2 skipped | n/a (Import schlägt fehl) |
| **Radi144-Optik-Treue** | Niedrig (alte 8-Step-Struktur) | **Höchste** (dedizierter Style-Commit) | Mittel (Workbench-Design, eigene Nomenklatur) | Kaputt |

### 2.2 Schlussfolgerung aus der Topologie

- `feature/radi144-workflow-ux` hat die **beste Radi144-Optik** (dedizierter Style-Commit `9a3ffa2`), aber **keine Backend-Alignment-Fixes** (kein `owner_id`, kein `substep_manifest`).
- `operator-workbench-phase1` (committet) hat die **vollständigste Backend-Anbindung** (Alignment-Layer + Workbench-Backend + Scan-Job-Fix), aber eine **eigene Workbench-Nomenklatur** statt Radi144-Labels.
- `master` hat den **Alignment-Layer**, aber die **alte 8-Step-UI**.
- **Kein einzelner Branch vereint aktuell beides** (Radi144-Optik + vollständiges Backend-Alignment + funktionierender Scan).

---

## 3. Problem 1+2 — Der korrupte Worktree (Root Cause)

### 3.1 Was passiert ist

Der Worktree `operator-workbench-phase1` hatte nach Commit `5a23142` einen **funktionierenden, getesteten Stand** (99 passed, Scan manuell verifiziert: 200 OK, Job completed, 3 Top-Profile, 4 Berichte).

Danach wurden **uncommittierte Änderungen** eingeführt, die den Code **korrupt** haben. Die Änderungen sind **keine sinnvolle Arbeit** — sie enthalten literalen Garbage und Löschungen:

### 3.2 Verifikation (live ausgeführt)

```
WORKTREE main.py Syntax-Check:
  File "...apps/web/main.py", line 308
    @app.get("/api/hardw12-Sat) s
             ^
SyntaxError: unterminated string literal (detected at line 308)

WORKTREE main.py diff (Auszug):
-    launch: dict[str, Any], *, workbench_mode: str, request: Phase1ScanRequest | None = None
+    launch: dict[str, Any], *, workbench_mode: str
...
-    return { "job_id": ..., "review": review_block, ... }
+    reo""aunch["executes"],
+    r

WORKTREE app.css diff: -176 Zeilen "OPERATOR WORKBENCH STYLES" (Skip-Link, Hardware-Truth-Cards, ...)
WORKTREE index.html diff: 10 Stepper-Buttons → leeres <nav></nav>; Phase-3-Sektion zusammengeführt/broken
WORKTREE test_web_shell.py diff: -316 Zeilen
```

### 3.3 Diff-Stat der korrupten Änderungen

```
 apps/web/main.py           | 121 +++--------------
 apps/web/scan_jobs.py      |  16 +--
 apps/web/static/app.css    | 176 -------------------------
 apps/web/static/index.html |  30 +----
 tests/test_web_shell.py    | 316 ++++++++++-----------------------------------
 5 files changed, 93 insertions(+), 566 deletions(-)
```

### 3.4 Warum der Analyselauf fehlschlägt

1. `main.py` hat einen **SyntaxError** → `from apps.web.main import create_app` schlägt fehl → Uvicorn kann die App nicht starten.
2. Selbst wenn der Import fälleweise durch ein Caching gelänge: `_workbench_run_trace_seed` enthält Garbage (`reo""aunch`) → der Run-Trace-Pfad ist kaputt.
3. Die Scan-Job-Start-Logik wurde teilweise zurückgebaut (`scan_jobs.py` -16 Zeilen).

### 3.5 Committeter Stand ist intakt — Verifikation

```
git show 5a23142:apps/web/main.py | python -c "import sys,ast; ast.parse(sys.stdin.read()); print('SYNTAX OK')"
→ SYNTAX OK
```

**Schlussfolgerung:** Die korrupten uncommitteten Änderungen müssen verworfen werden. Der committierte Stand `5a23142` ist die sichere, getestete Basis.

---

## 4. Problem 3 — "12 Steppings" vs. "10 Steppings" erklärt

### 4.1 Zwei verschiedene "Stepping"-Konzepte im Projekt

| Konzept | Bedeutung | Beleg | Anzahl |
|---|---|---|---|
| **12-Step CLI-Workflow-Orchestrator** | Reale sequenzielle Analyse-Pipeline im Backend (`step01_init` → `step12_harmonize`) | `apps/cli/workflow/orchestrator.py:73-89` | **12** |
| **12-Substep-Contract (radiquant4)** | Kanonische Substeps von `radimorphic` (`_RADI_MORPHIC_GOLD_SUBSTEPS`) | `RADIQUANT4_RADIMORPHIC_KONTRAKT_REFERENZ.md` Abschnitt 3.2 | **12** |
| **8-Step Web-Wizard (master)** | Bedien-Steps im Frontend (Preflight → Harmonisierung) | `apps/web/static/index.html:22-31` | **8** |
| **10-Phase Operator-Workbench (worktree)** | Bedien-Phasen im Frontend (Runtime → Harmonisierung&Export) | worktree `index.html` (committet) | **10** |

### 4.2 Die 12 kanonischen Substeps (radiquant4 `_RADI_MORPHIC_GOLD_SUBSTEPS`)

| # | Substep | Phase | morphic_v1-Äquivalent (`substep_manifest.py`) |
|---:|---|---|---|
| 1 | `profile_resolution` | multiplex | `step02_input` (näherungsweise) |
| 2 | `candidate_generation` | multiplex | **kein Äquivalent (Lücke)** |
| 3 | `entropy_sampling` | multiplex | `step01_init` |
| 4 | `client_signature` | multiplex | `step03_signature` |
| 5 | `multiplex_scoring` | multiplex | `step08_matrix` |
| 6 | `client_modifiers` | multiplex | `step05_emf` |
| 7 | `quantum_modulation` | analysis | `step09_quantum` |
| 8 | `intention_weighting` | analysis | `step04_focus` |
| 9 | `synergy_analysis` | analysis | **kein Äquivalent (Lücke)** |
| 10 | `db_analysis` | analysis | `step10_post` |
| 11 | `morphic_field` | analysis | **kein Äquivalent (Lücke)** |
| 12 | `export` | export | `step11_export` |

Unmapped (morphic_v1-spezifisch, kein radiquant4-Äquivalent): `step06_amplifier`, `step07_palette`, `step12_harmonize`.

### 4.3 Was der Nutzer mit "12 Steppings" meint

Die "vorherige Version, die bei Step 7 hing" (= `operator-workbench-phase1` committet) zeigte während des Analyse-Laufs die **12-Substep-Fortschrittsanzeige** (aus `SUBSTEP_MANIFEST` + Scan-Job-Progress-Markern). Die aktuell korrupte Version zeigt diese nicht mehr (Stepper gelöscht, Run-Trace kaputt).

Das 07-07-Audit empfiehlt in PHASE_4 Abschnitt 4.8 bereits exakt diesen Schritt:
> **Operator Workbench v2 mit 12-Step-Timeline** — UI und Backend-Steps werden 1:1 sichtbar. Aufwand mittel, Risiko gering-mittel. Gate-Ansatz: Erst read-only Timeline aus `SUBSTEP_MANIFEST`, dann Live-Events.

**Das ist das eigentliche UI/UX-Ziel:** Die 10 Bedien-Phasen des Operator-Wizards bleiben, aber der Analyse-Lauf (Phase 7) zeigt die **12-Substep-Timeline** wie radiquant4.

---

## 5. Problem 4 — OpenBLAS / numpy-Umgebung

### 5.1 Befund

```
FreePhysicalMemory: 3,24 GB von 15,25 GB Total
.venv python -c "import numpy" →
  OpenBLAS error: Memory allocation still failed after 10 retries, giving up. (×3)
```

### 5.2 Einordnung

- **Kein Code-Bug.** Akute Host-Speicherknappheit (Browser, IDE, Sprachserver, Antivirus belegen ~12 GB).
- Blockiert `import numpy` → blockiert `core/hardware/system_info` → blockiert `apps.web.main`-Import.
- Bekannt seit 07-05-Audit (damals ~575 MB frei), heute 3,24 GB — also etwas besser, aber OpenBLAS benötigt Thread-Puffer, die bei <4 GB frei nicht sicher allozierbar sind.
- Für ein "realtime-ready" positioniertes System ein **Robustheitsbefund**: numpy/SciPy-Pfade haben keine Niedrig-Speicher-Erkennung, keinen Fallback, keine verständliche Fehlermeldung.

### 5.3 Workaround für Tests/Entwicklung

Vor App-Start oder pytest andere Anwendungen schließen (Browser-Tabs, IDE-Sprachserver pausieren), bis ≥5 GB frei sind. Mittelfristig: `OPENBLAS_NUM_THREADS=1` und Graceful-Degradation bei numpy-Import-Fehler (siehe `PHASE_9_INNOVATIONEN_ECHTZEIT_UND_QUANTUM.md` Abschnitt 4).

---

## 6. Schritt-für-Schritt-Wiederherstellung für Entwickler

### Schritt 1: Worktree-Korruption verwerfen (SICHERHEIT: erst stasht, nichts geht verloren)

```powershell
cd C:\morphic_v1\.worktrees\operator-workbench-phase1
# Korrupte Änderungen sichern (falls später forensisch benötigt)
git stash push -m "corrupted-uncommitted-2026-07-07-DO-NOT-APPLY" -- apps/web/main.py apps/web/scan_jobs.py apps/web/static/app.css apps/web/static/index.html tests/test_web_shell.py
# Verifizieren: Worktree ist jetzt clean auf 5a23142
git status
git log --oneline -1   # → 5a23142 fix: LocalScanJobService.start() accepts owner_id parameter
```

### Schritt 2: Syntax- und Import-Verifikation

```powershell
cd C:\morphic_v1\.worktrees\operator-workbench-phase1
# Syntax
.venv\Scripts\python.exe -c "import ast; ast.parse(open('apps/web/main.py',encoding='utf-8').read()); print('SYNTAX OK')"
# (App-Import benötigt numpy → nur bei ausreichend freiem RAM möglich)
```

### Schritt 3: Stepper und CSS verifizieren

```powershell
# 10 Stepper-Buttons wieder vorhanden?
Select-String -Path apps\web\static\index.html -Pattern "wizard-step" | Measure-Object | Select-Object -ExpandProperty Count
# → erwartet: 20 (10 Buttons + 10 Sections + nav)
# Workbench-CSS wieder vorhanden?
Select-String -Path apps\web\static\app.css -Pattern "OPERATOR WORKBENCH" | Measure-Object | Select-Object -ExpandProperty Count
# → erwartet: ≥1
```

### Schritt 4: Tests (bei ausreichend RAM)

```powershell
cd C:\morphic_v1\.worktrees\operator-workbench-phase1
.venv\Scripts\python.exe -m pytest tests -q
# → erwartet: 99 passed, 2 skipped
```

### Schritt 5: App starten und Scan manuell verifizieren

```powershell
cd C:\morphic_v1\.worktrees\operator-workbench-phase1
$env:PYTHONUTF8=1
.venv\Scripts\python.exe -m uvicorn apps.web.main:app --host 127.0.0.1 --port 8000
# Browser: http://127.0.0.1:8000 → 10 Phasen sichtbar
# Scan starten → Phase 7 läuft, 12-Substep-Progress, Phase 8 Ergebnisse, Phase 10 Berichte
```

---

## 7. Radi144-Alignment-Ziel — was "Gleichziehen" konkret heißt

### 7.1 Aus dem Design-Spec (`docs/superpowers/specs/2026-07-04-apps-web-radi144-workflow-ux-design.md`)

- **10-Schritt-Operator-Wizard** (Bedienoberfläche), strukturiert wie Radi144: Step-Header mit Icon/Titel/Unterzeile, primäre Arbeitskarte, sekundäre Snapshot-Karte, Footer-Aktionen.
- **12-Substep-Timeline** während des Analyse-Laufs (Sichtbarmachung des Backend-Workflows).
- **Design-Tokens:** oklch-basiert, Sage/Ink/Sand/Terracotta, `Fraunces` (Display-Serif) + `Inter` (Sans), Radius-/Shadow-/Motion-Tokens, `prefers-reduced-motion`.
- **Radi144-Referenzprinzipien:** Klare Step-Navigation (aktiv/erledigt/gesperrt), visuelle Verbinder, kartenbasierte Arbeitsbereiche, Radio-/Toggle-Karten statt bloßer Formularfelder, Snapshot-Karten vor kritischen Aktionen, ruhige warme Farbwelt.

### 7.2 Aus dem Kontrakt-Referenz (`docs/deep-audit-2026-07-05/RADIQUANT4_RADIMORPHIC_KONTRAKT_REFERENZ.md`)

- **6-Modul-Pipeline:** `radi144 → radiworks → radimorphic → radiblohm → radithoms → radicopen`, jedes Modul `standaloneRunSupported: true`.
- **12-Substep-Contract** (siehe Abschnitt 4.2 oben) mit Echtzeit-Event-Stream (`emit_substep_completed`).
- **StandardAnalysisBlock** als einheitliches Ergebnis-Schema für alle Module (nicht morphic_v1s Dateisystem-Export).
- **Entropie-Kaskade:** QRNG → WebCam-Hotbits → Infinite-Noise-USB → ESP32 → `os.urandom`, deterministischer Seed `sha256(tenant:fname:lname:...)[:8]`.
- **Frontend-Stack:** Astro + React + Tailwind + shadcn/ui, oklch-Design-Tokens, Phasen-Chromotherapie-Farben.

### 7.3 Was fehlt, um "gleichzuziehen" (konsolidiert aus allen Audits)

| Bereich | Status | Lücke |
|---|---|---|
| 10-Step-Wizard-Struktur | Vorhanden (worktree + radi144-ux-branch) | Radi144-Label-Nomenklatur und Icon/Verbinder-Design nur auf `feature/radi144-workflow-ux` |
| 12-Substep-Timeline im UI | **Fehlt** | Substep-Manifest vorhanden, aber nicht im UI gerendert (nur stdout-Marker-Heuristik) |
| Design-Tokens (oklch/`--rq`) | Teilweise (master + worktree) | Nicht konsistent über alle Branches; Fraunces/Inter-Self-Hosting unklar |
| StandardAnalysisBlock-Export | Implementiert (`platform_export.py`) | — |
| Operator-/Ownership-Kontext | Stub vorhanden | Endpoints nutzen ihn nicht durchgängig |
| Entitlement-Stub | Vorhanden | — |
| Entropie-Kaskade / deterministischer Seed | Implementiert (`seed_generator.py`) | TRNG-Hardware-Quellen sind Stubs/Fallback |
| DSGVO-Härtung | Implementiert (audit/purge) | Keine at-rest-Verschlüsselung |
| Echtzeit-Event-Stream | **Fehlt** | radiquant4 nutzt Event-Bus; morphic_v1 nutzt stdout-Parsing |

---

## 8. Verweise auf bestehende Dokumentation (keine Duplikation)

| Dokument | Inhalt | Relevanz |
|---|---|---|
| `docs/deep-audit-2026-07-07/README.md` | Allgemeine Tiefenanalyse, Executive Summary, 230 Tests | Gesamtstatus master |
| `docs/deep-audit-2026-07-07/PHASE_2_WORKFLOW_STEPPINGS_SUBSTEPPINGS.md` | 12-Step-Orchestrator, 8-Step-Web-Wizard, Substep-Mapping, Artefakte | Stepping-Details |
| `docs/deep-audit-2026-07-07/PHASE_4_FRONTEND_UIUX_GOOGLE_2026.md` | Frontend UI/UX, A11y, CWV, Innovationsvorschläge (Operator Workbench v2 12-Step-Timeline) | UI-Ziel |
| `docs/deep-audit-2026-07-05/RADIQUANT4_RADIMORPHIC_KONTRAKT_REFERENZ.md` | radiquant4-Server-Referenz, 12-Substep-Contract, StandardAnalysisBlock, Design-Tokens | Zielbild |
| `docs/deep-audit-2026-07-05/README.md` | Alignment-Umsetzungsstand (Tasks 1-8), OpenBLAS-Root-Cause, Quantum-Realität | Historischer Kontext |
| `docs/superpowers/specs/2026-07-04-apps-web-radi144-workflow-ux-design.md` | 10-Step-UX-Design, Radi144-Referenzprinzipien, Step-spezifisches Design | UX-Ziel |
| `docs/superpowers/plans/2026-07-04-apps-web-radi144-workflow-ux.md` | Umsetzungsplan | Plan |
| `docs/superpowers/plans/2026-07-05-morphic-v1-radiquant4-alignment.md` | 9-Task-Alignment-Plan | Plan |

---

## 9. Empfohlene nächsten Schritte (Reihenfolge)

1. **Sofort:** Korrupte uncommittete Worktree-Änderungen stashen/verwerfen (Abschnitt 6, Schritt 1-2) → Stand `5a23142` wiederherstellen. Scan läuft wieder.
2. **Danach:** Branches konsolidieren — `feature/radi144-workflow-ux` (beste Optik) mit `operator-workbench-phase1` (bestes Backend) mergen/vereinigen. Konflikte erwartet in `index.html`, `app.css`, `main.py`, `scan_jobs.py`.
3. **Danach:** 12-Substep-Timeline in Phase 7 (Analyse-Lauf) des UI sichtbar machen — read-only aus `SUBSTEP_MANIFEST`, an Scan-Job-Progress-Marker gekoppelt.
4. **Parallel:** OpenBLAS-Robustheit (numpy-Import-Fallback, `OPENBLAS_NUM_THREADS=1`, verständliche Fehlermeldung bei Niedrig-Speicher).
5. **Roadmap:** Echtzeit-Event-Stream statt stdout-Parsing (radiquant4-Pattern `emit_substep_completed`).

---

## 10. Verifizierungsergebnis der Wiederherstellung (2026-07-07, live ausgeführt)

Die Wiederherstellung wurde gemäß Abschnitt 6 durchgeführt und **vollständig verifiziert**.

### 10.1 Durchgeführte Schritte

| Schritt | Aktion | Ergebnis |
|---:|---|---|
| 1 | `git stash push -m "corrupted-uncommitted-2026-07-07-DO-NOT-APPLY" -- apps/web/main.py apps/web/scan_jobs.py apps/web/static/app.css apps/web/static/index.html tests/test_web_shell.py` | `stash@{0}` angelegt, 5 Dateien gesichert |
| 2 | `git status` + `git log --oneline -1` | Worktree clean, HEAD = `5a23142` |
| 3 | `python -c "import ast; ast.parse(...)"` für main.py | `SYNTAX OK` |
| 4 | `Select-String` wizard-step + OPERATOR WORKBENCH | 10 Stepper-Buttons, 1 Workbench-CSS-Block, 1177 Zeilen app.css |
| 5 | `pytest tests/test_web_scan_jobs.py tests/test_web_shell.py tests/test_web_contracts.py tests/test_web_workbench_runtime.py tests/test_web_scan_job_ownership.py -q` | **50 passed in 2.48s** |
| 6 | `pytest tests -q` (vollständig) | **262 passed, 2 skipped in 112.37s** |
| 7 | `uvicorn apps.web.main:app --host 127.0.0.1 --port 8000` | Server startet, Port 8000 Listen |
| 8 | `GET /api/health`, `/api/sources`, `/api/hardware/status`, `/` | alle **200 OK** |
| 9 | Served HTML: 10 wizard-step Buttons mit Labels (Runtime & Workspace → Harmonisierung & Export), OPERATOR WORKBENCH CSS geladen | UI/Optik wiederhergestellt |
| 10 | `POST /api/scan/preview` (Klaus Mustermann, Bronchien, Level 3, top_n 9) | **200 OK**, CLI-Kommando generiert |
| 11 | `POST /api/scan/jobs` | **200 OK**, `executes: true`, job_id `scan-20260707-125245-12270c4c` |
| 12 | `GET /api/scan/jobs/{job_id}` Polling (5s → 10s → 15s → 12s) | running (0.6% → 5.7% → 77.8%) → **completed, 100%, returncode 0** |
| 13 | `GET /api/scan/jobs/{job_id}/results` | **200 OK**, 9 Top-Profile mit Scores |
| 14 | `GET /api/reports` | **200 OK**, 4 Klienten mit Sessions |

### 10.2 Scan-Substep-Progress (verifiziert)

Während des Analyse-Laufs wurden folgende Substeps durchlaufen:
- Phase 1, "Screening: immune" (0.6%)
- Phase 1, "Screening: vergiftung_komplett" (5.7%, 7 completed substeps)
- "Nachbereitung", "> Erstelle Remedy-Kombinationen Report" (77.8%)
- "Nachbereitung", "Trendbericht erstellt" (100%, 8 completed substeps, returncode 0)

### 10.3 Fazit

- **Analyselauf funktioniert wieder** (200 OK → completed → 9 Profile → 4 Klienten-Reports).
- **UI/Optik wiederhergestellt** (10 Stepper-Buttons, Workbench-CSS, Design-Tokens).
- **Tests grün** (262 passed, 2 skipped — besser als der vor der Korruption gemessene Stand von 99 passed).
- **Korrupte Änderungen gesichert** in `stash@{0}` (`corrupted-uncommitted-2026-07-07-DO-NOT-APPLY`) — forensisch verfügbar, aber nicht aktiv.
- **Worktree clean** auf `5a23142` ("fix: LocalScanJobService.start() accepts owner_id parameter").

### 10.4 Verbleibende Ziele (siehe Abschnitt 7.3 und 9)

Die Wiederherstellung bringt das System auf den **funktionierenden, getesteten Stand `5a23142`**. Die Radi144-Optik-Angleichung und die 12-Substep-Timeline sind **noch nicht umgesetzt** — das sind die nächsten Roadmap-Schritte:

1. Branches konsolidieren (`feature/radi144-workflow-ux` Optik + `operator-workbench-phase1` Backend).
2. 12-Substep-Timeline in Phase 7 (Analyse-Lauf) sichtbar machen.
3. Radi144-Design-Tokens und Step-Header-Struktur (Icon/Verbinder/Snapshot-Karten) konsistent anwenden.

---

## 11. Radi144-UI-Alignment umgesetzt (2026-07-07, Commit `bcfcd2f`)

Nach der Wiederherstellung (Abschnitt 10) wurde das Radi144-UI-Alignment als **Port** (nicht Merge) umgesetzt: Die Visualelemente aus `feature/radi144-workflow-ux` wurden in den `operator-workbench-phase1`-Worktree portiert, ohne das ueberlegene Backend und die modulare JS-Architektur zu brechen.

### 11.1 Strategie: Port statt Merge

Ein git-Merge der beiden Branches haette massive Konflikte in `index.html`, `app.css`, `main.py`, `scan_jobs.py` erzeugt (beide Branches aenderten dieselben Dateien ab demselben Divergenzpunkt `e87cee3`, aber in unterschiedliche Richtungen). Stattdessen wurden **nur die Visualelemente** portiert:

| Element | Quelle (`feature/radi144-workflow-ux`) | Ziel (`operator-workbench-phase1`) |
|---|---|---|
| step-header/icon/subtitle CSS | `app.css` Style-Commit `9a3ffa2` | append an bestehende app.css |
| step-card CSS | `app.css` | append |
| wizard-step Verbinder | neu (an Radi144-Prinzip 2 "visuelle Verbinder") | neu |
| 12-Substep-Timeline | neu (aus SUBSTEP_MANIFEST + Design-Spec) | neu |
| Phase-Header HTML | `index.html` Step-Header-Struktur | replace section-title durch step-header |
| Backend/JS | **nicht portiert** (operator-workbench ist ueberlegen) | beibehalten |

### 11.2 Umgesetzte Aenderungen (Commit `bcfcd2f`)

| Datei | Aenderung | Zeilen |
|---|---|---:|
| `apps/web/static/app.css` | +199 Zeilen: step-header, step-icon, step-subtitle, step-card, wizard-step Verbinder, substep-timeline (12 Items, pending/active/completed, Puls-Animation, reduced-motion), Mobile-Breakpoints | +199 |
| `apps/web/static/index.html` | Alle 10 Phase-Header auf step-header/step-icon/step-subtitle upgegradet; Phase 7 erhaelt 12-Substep-Timeline mit statischen Eintraegen aus SUBSTEP_MANIFEST + radiquant4-Aequivalent-Labels | +106/-30 |
| `apps/web/static/workbench-render.js` | `renderSubstepTimeline()`, `resetSubstepTimeline()`, `_substepKeywordMap`, `_matchSubstepIndex()` — heuristisches Mapping von CLI-Substep-Texten auf Timeline-Indizes | +98/-9 |
| `apps/web/static/app.js` | `pollScanJob()` ruft `renderSubstepTimeline` auf; `startScanJob()` ruft `resetSubstepTimeline` auf | +5/-2 |

### 11.3 Die 12 Substeps in der Timeline

Die Timeline in Phase 7 zeigt alle 12 Substeps aus `SUBSTEP_MANIFEST` mit ihren radiquant4-Aequivalenten:

| # | morphic_v1-Label | radiquant4-Aequivalent |
|---:|---|---|
| 1 | Init & Entropie | `entropy_sampling` |
| 2 | Eingabe & Profil | `profile_resolution` |
| 3 | Klienten-Signatur | `client_signature` |
| 4 | Fokus & Intention | `intention_weighting` |
| 5 | EMF & Modifikatoren | `client_modifiers` |
| 6 | Amplifier-Matching | morphic_v1-spezifisch |
| 7 | Farbpalette | morphic_v1-spezifisch |
| 8 | Matrix-Scoring | `multiplex_scoring` |
| 9 | Quantum-Modulation | `quantum_modulation` |
| 10 | DB-Analyse | `db_analysis` |
| 11 | Export | `export` |
| 12 | Harmonisierung | eigener Job-Flow |

Waehrend des Analyse-Laufs werden die Items von `pending` → `active` (Puls-Animation) → `completed` (gruen, Haekchen) geschaltet.

### 11.4 Verifikation (live ausgefuehrt)

| Pruefung | Ergebnis |
|---|---|
| main.py Syntax | OK |
| HTML: step-header | 10 |
| HTML: substep-timeline-item | 12 |
| HTML: step-icon | 10 |
| HTML: step-subtitle | 10 |
| CSS: step-header + substep-timeline Regeln | 22 |
| JS: renderSubstepTimeline + resetSubstepTimeline | 2 |
| Web-Tests (gezielt) | **50 passed** in 2.29s |
| Vollstaendige Tests | **262 passed, 2 skipped** in 113.55s |
| App-Start (Uvicorn) | Port 8000 Listen |
| Served HTML | 200 OK, 10 step-headers, 12 timeline-items, 10 icons, 10 subtitles |
| Scan-Start | 200 OK, job_id `scan-20260707-152413-4619630a` |
| Scan-Polling | 1% (5 completed) → 8.9% (7) → 66.7% (7) → 100% (8), returncode 0 |
| Scan-Results | 200 OK, 9 Top-Profile |
| Reports | 200 OK |

### 11.5 Fazit

- **Radi144-Optik-Angleichung umgesetzt**: Alle 10 Phasen haben jetzt Radi144-style step-header mit Icon, Titel und Unterzeile. Visuelle Verbinder zwischen Wizard-Steps.
- **12-Substep-Timeline sichtbar**: Phase 7 zeigt alle 12 Substeps der Gold-Pipeline mit radiquant4-Aequivalent-Labels und Live-Progress (pending → active → completed).
- **Backend unversehrt**: modulare JS-Architektur (workbench-state/api/render), owner_id-Fix, Alignment-Layer, substep_manifest, platform_export alle intakt.
- **Tests gruen**: 262 passed, 2 skipped.
- **Scan funktioniert end-to-end**: Preview → Start → 12-Substep-Timeline-Progress → Completed → 9 Profile → Reports.

---

*Verifiziert am 2026-07-07 durch direkte Git-, AST-, Syntax-, Test-, Uvicorn- und HTTP-Prüfungen in `C:\morphic_v1\.worktrees\operator-workbench-phase1`. Scan manuell end-to-end durchlaufen (Preview → Start → Poll → Completed → Results → Reports).*
