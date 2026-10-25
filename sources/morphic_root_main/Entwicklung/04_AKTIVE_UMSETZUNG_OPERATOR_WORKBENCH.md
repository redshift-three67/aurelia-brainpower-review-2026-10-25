# Aktive Umsetzung - Operator Workbench

## 1. Arbeitskontext

Aktiver Umsetzungsort:

- `C:/morphic_V1/.worktrees/operator-workbench-phase1`

Branch:

- `operator-workbench-phase1`

Status:

- noch nicht committed
- Backend-Grundgeruest vorhanden
- Frontend-Umbau noch nicht begonnen

## 2. Bereits umgesetzte Teile

### Task 1 - erledigt

Bereits vorhanden:

- `apps/web/workbench_registry.py`
- `workbench_mode` fuer `Phase1ScanRequest`
- zugehoerige Tests in:
  - `tests/test_workbench_registry.py`
  - `tests/test_web_contracts.py`

### Task 2 - erledigt

Bereits vorhanden:

- `apps/web/hardware_truth.py`
- `apps/web/workbench.py` mit:
  - `/api/workbench/registry`
  - `/api/workbench/hardware`
- `apps/web/main.py` besitzt die noetigen Builder-Seams fuer Hardware-/Truth-Nutzung
- zugehoerige Tests in:
  - `tests/test_web_hardware_truth.py`
  - `tests/test_web_hardware_status.py`

### Task 3 - erledigt

Bereits vorhanden:

- `apps/web/workbench_runtime.py`
- Runtime-backed Draft-/Template-/Run-Trace-Store
- Endpunkte fuer:
  - Draft
  - Templates
  - Run Trace
- `app.state.workbench_store`
- initiales best-effort Run-Trace-Seeding bei `/api/scan/jobs`

Wichtige bereinigte Eigenschaften:

- expliziter Draft-Envelope
- Locking im Store fuer den aktuellen Single-App-Instanz-Scope
- Run Trace ohne rohen CLI-Command und ohne freie sensible Textfelder

## 3. Noch nicht begonnen

### Task 4

- 10-Phasen-Frontend in `apps/web/static/*`
- Modulaufteilung:
  - `workbench-state.js`
  - `workbench-api.js`
  - `workbench-render.js`
- `app.js` als Bootstrap

### Task 5

- Review-Gate im Frontend
- Ergebnis-Uebersicht
- Technische Detailansicht
- finaler Arbeitsbereich fuer Harmonisierung und Export

### Task 6

- Pipeline-Oberflaeche als rein erklaerende Flaeche neu positionieren
- finale Regression-Coverage fuer den Workbench-Schnitt

## 4. Aktuelle Worktree-Dateien

Geaendert:

- `apps/web/contracts.py`
- `apps/web/harmonization.py`
- `apps/web/main.py`
- `services/harmonization_worker.py`
- `tests/test_web_contracts.py`
- `tests/test_web_hardware_status.py`
- `tests/test_web_shell.py`

Neu:

- `apps/web/hardware_truth.py`
- `apps/web/workbench.py`
- `apps/web/workbench_registry.py`
- `apps/web/workbench_runtime.py`
- `tests/test_web_hardware_truth.py`
- `tests/test_web_workbench_runtime.py`
- `tests/test_workbench_registry.py`

## 5. Aktuelle verifizierte Testlage des Worktree-Schnitts

Aktuell selbst verifiziert:

- `tests/test_web_workbench_runtime.py`
- `tests/test_web_contracts.py`
- `tests/test_web_shell.py`

Ergebnis:

- `34 passed in 2.00s`

Zusaetzlich frueher im Verlauf verifiziert:

- `tests/test_workbench_registry.py`
- `tests/test_web_hardware_truth.py`
- `tests/test_web_hardware_status.py`

## 6. Wichtige Einordnung

Der aktuelle Worktree ist **kein fertiger Operator Workbench**, sondern eine bereits substanzielle Backend-/API-Vorbereitung der Workbench.

Was heute schon real ist:

- Workbench-Metadatenmodell
- Hardware-Truth-API
- Runtime-Persistenz fuer Drafts/Templates/Run Trace

Was heute noch fehlt, damit ein Operator dies wirklich benutzt:

- die 10-Phasen-Frontend-Shell
- Review-Gate
- Ergebnis-/Detail-/Finalisierungsphasen
