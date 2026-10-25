# E5.10E Streng lokale Gruppen-Produktivintegration – Implementation Plan

> **For Hermes:** Diesen Plan konservativ, testgetrieben und gateweise ausführen. Kein Commit/Push/Clean ohne ausdrückliche Freigabe.

**Goal:** Einen explizit eingewilligten, owner-/workspace-/tenant-gebundenen Gruppenentwurf ausschließlich bei aktivem serverseitigem Kill-Switch und expliziter Stärke über kurzlebige One-Time-Handles in den lokalen Top-N-Scan einbinden, ohne Rohidentitäten, Mitgliedslisten, Raten oder Zentroide in CLI-Argumente, Job-Snapshots, Logs, Reports, Traces oder Manifeste zu schreiben.

**Architecture:** Die Webroute erzeugt aus `draft_id` und dem gescannten, kanonisch abgeleiteten `subject_id` serverseitig einen autorisierten In-Memory-Kandidaten und legt ihn als DPAPI-geschützten Root-Handle ab. `LocalScanJobService` reicht nur eine interne, nicht im Snapshot gespeicherte Environment-Konfiguration an den Top-N-Prozess. Der Top-N-Orchestrator konsumiert den Root-Handle einmalig und erzeugt pro Multiplex-Subprozess einen eigenen kurzlebigen Child-Handle; jeder Field-Worker konsumiert genau einen Child-Handle und übergibt den rekonstruierten `GroupAnalysisOptIn` ausschließlich an `AnalysisService.encode_profile()`. Fehlt irgendeine Freigabebedingung, bleibt der Scan exakt baseline-äquivalent; ein ausdrücklich angeforderter, aber ungültiger Aktivierungspfad scheitert fail-closed vor dem Scanstart.

**Tech Stack:** FastAPI/Pydantic, Typer, Windows DPAPI, Python subprocess environment, pytest, NumPy.

---

## Unverhandelbare Verträge

1. `MORPHIC_GROUP_ANALYSIS_ENABLED` fehlt/ist unbekannt → keine Wirkung.
2. Stärke fehlt oder ist `0.0` → keine Wirkung und kein Identity-/Draft-Zugriff.
3. Produktive Gruppenaktivierung ist explizit; kein implizites „zuletzt geladener Draft“.
4. `subject_id` wird serverseitig aus den aktuellen Scan-Identitätsdaten abgeleitet und muss Mitglied des Drafts sein.
5. Browser/Request transportiert keine Raten, Zentroide oder Member-Rate-Mappings.
6. Jobcommand, Job-Snapshot, Run-Trace, Report und Manifest enthalten weder Handle noch Gruppenidentität/-werte.
7. Handle und Storepfad werden nur über einen pro Prozess explizit gebauten Environment-Block transportiert.
8. Top-N konsumiert den Root-Handle einmal und fächert pro Multiplex-Aufruf einen Child-Handle auf.
9. Jeder Child-Handle ist One-Time, kurzlebig, kontextgebunden und wird vor Analyse-Rückgabe gelöscht.
10. Explizit angeforderte Aktivierung mit ungültigem/abgelaufenem/widerrufenem Consent scheitert vor Prozessstart; kein stilles Zurückfallen auf Baseline.
11. Nach Prozessstart auftretender Handle-Fehler beendet den betroffenen Scan fail-closed; kein stiller Baseline-Scan unter behaupteter Aktivierung.
12. Geo bleibt vollständig unverdrahtet.

## Rollback-Matrix

| Fall | Erwartung |
|---|---|
| Aktivierung nicht angefordert | exakt bestehender Command/Job/Analysepfad |
| Kill-Switch aus | exakt Baseline, kein Draft-/Identity-Zugriff |
| Stärke `None` | exakt Baseline, kein Draft-/Identity-Zugriff |
| Stärke `0.0` | exakt Baseline, kein Draft-/Identity-Zugriff |
| Draft-Analyseconsent false | 422/fail-closed vor Prozessstart |
| Mitgliedsconsent fehlt/widerrufen/abgelaufen | 422/fail-closed vor Prozessstart |
| Subject nicht im Draft | 422/fail-closed vor Prozessstart |
| fremder Operator/Workspace/Tenant | 403/fail-closed |
| Root-/Child-Handle abgelaufen oder manipuliert | Workerfehler, keine Baseline-Tarnung |
| Handle wiederverwendet | fail-closed |
| Kill-Switch nach Gate deaktiviert | neue Scans exakt Baseline; bestehende Handles werden nicht neu ausgegeben |
| Featurecode entfernt/deaktiviert | bestehender CLI-/Webscan bleibt kompatibel |

### Task 1: Runtime-Handle-Umgebungsgrenze

**Files:**
- Create: `core/compliance/group_activation_runtime.py`
- Test: `tests/test_group_activation_runtime.py`

RED-Verträge:
- Ohne Environment-Aktivierung wird `None` geliefert und kein Store geöffnet.
- Unvollständige Aktivierungsumgebung scheitert fail-closed.
- Gültiger Handle wird kontextgebunden genau einmal konsumiert.
- Environment-Safe-Summary enthält weder Handle noch Pfad, IDs oder Werte.

### Task 2: Field-Worker konsumiert genau einen Child-Handle

**Files:**
- Modify: `apps/cli/commands/field.py`
- Test: `tests/test_field_group_activation_runtime.py`

RED-Verträge:
- Defaultaufruf bleibt exakt wie zuvor.
- Gültiger Child-Handle wird vor `AnalysisService.encode_profile()` konsumiert und als `group_opt_in` übergeben.
- Ungültiger/abgelaufener Handle beendet den Aufruf fail-closed.
- Exportpayload und Konsolenausgabe enthalten keine Aktivierungsdetails.

### Task 3: Top-N-Orchestrator konsumiert Root-Handle und fächert Child-Handles auf

**Files:**
- Modify: `apps/cli/commands/scan.py`
- Test: `tests/test_topn_group_activation_fanout.py`

RED-Verträge:
- Ohne Aktivierungsumgebung bleiben Subprocess-Command und Environment baseline-äquivalent.
- Root-Handle wird einmal konsumiert.
- Für jeden Screening- und Detailprozess wird ein eigener Child-Handle erzeugt.
- Child-Handles erscheinen nie in Commands oder Ausgaben.
- Subprozessfehler bei angeforderter Aktivierung wird nicht als Baseline-Erfolg behandelt.

### Task 4: ScanJobService erhält nicht persistierte Environment-Overrides

**Files:**
- Modify: `apps/web/scan_jobs.py`
- Modify: `tests/test_web_workbench_runtime.py`

RED-Verträge:
- `start(..., env_overrides=...)` gibt Overrides ausschließlich an `subprocess.Popen(env=...)`.
- Snapshot/Response/Trace enthält keine Override-Schlüssel oder -Werte.
- Ohne Overrides bleibt das bestehende Verhalten unverändert.

### Task 5: Serverseitige Aktivierungsvorbereitung

**Files:**
- Create: `apps/web/group_analysis_runtime.py`
- Modify: `apps/web/main.py`
- Modify: `apps/web/contracts.py`
- Test: `tests/test_web_group_productive_activation.py`
- Evolve: `tests/test_group_e510_release_gate.py`

RED-Verträge:
- Request darf höchstens einen kanonischen `group_draft_id` als explizite Aktivierungsreferenz tragen; keine Member-/Raten-/Zentroidfelder.
- Aktivierung wird nur bei Flag=true und expliziter Stärke >0 vorbereitet.
- Scanidentität wird serverseitig zu `subject_id` abgeleitet.
- Draft, Identity Source, Resolver und Autorisierung werden vor Prozessstart geprüft.
- Nur Root-Handle/Storekonfiguration gelangt in nicht persistierte Job-Environment-Overrides.
- Response, Job-Snapshot und Run-Trace bleiben redigiert.
- Bei Flag off/Stärke 0 wird kein Handle erzeugt und der bestehende Scan unverändert gestartet.

### Task 6: Frontend explizit und redigiert verdrahten

**Files:**
- Modify: `apps/web/static/index.html`
- Modify: `apps/web/static/app.js`
- Modify: `apps/web/static/workbench-api.js`
- Test: `tests/test_workbench_group_activation_dom.py`

Verträge:
- Gruppenwirkung muss separat und ausdrücklich angefordert werden.
- Kein Rohvektor/Membermapping im Browserpayload oder Browserstorage.
- UI zeigt Feature-Flag, explizite Stärke und Aktivierungsbereitschaft, aber keine versteckten IDs.
- Flag off oder Stärke 0 zeigt klar „keine produktive Wirkung“.

### Task 7: E5.10E-Verifikation und Gatebericht

**Files:**
- Create: `docs/status/2026-07-13-e510e-local-productive-group-integration-gate.md`
- Modify: `docs/status/2026-07-12-gesamtstruktur-fortschritt.md`

Verifikation:
- fokussierte E5.10E-Tests;
- Redaktions-/Boundary-Suchen;
- Rest-Suite ohne Top-5;
- bekannte Rate-Limiter-Ausreißer separat in frischen Prozessen;
- Top-5-Smoke separat;
- `py_compile`;
- `node --check`;
- `git diff --check`;
- reale Browserabnahme bleibt E5.10F, sofern E5.10E keine vollständig abnahmefähige UI erreicht.

**Freigabegrenze:** Erst wenn Tasks 1–5 und alle Rollback-Verträge grün sind, darf E5.10E technisch GO heißen. E5.10 insgesamt bleibt bis E5.10F NO-GO.