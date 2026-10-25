## Freeze-v24 Review

**Verdikt: REQUEST CHANGES — NICHT APPROVE**  
**Konfidenz: hoch**  
**Befunde: P0=0 · P1=1 · P2=0 · P3=1**  
**Scope-Drift: 0**

### Befunde

| Prio | Befund | Evidenz |
|---|---|---|
| **P1** | **Die konfigurierte Authentifizierung schützt weiterhin nicht alle produktiven Diagnose- und WebSocket-Flächen.** Insbesondere `/api/emf/profile` liefert Betriebs-/Systemtelemetrie ohne `verify_api_key`; `/api/emf/ws` ruft sofort `accept()` auf und sendet diese Telemetrie ohne Authentifizierung oder erneute Prüfung. Auch `/api/synergy/stats` veröffentlicht Datenbankstatistik beziehungsweise rohe Fehlerdetails ohne Authentifizierung. Damit ist der v24-Anspruch „protected diagnostics“ im vollständigen Produktscope nicht erfüllt. | `apps/web/emf.py:43-54,78-94`; `apps/web/synergy.py:26-50` |
| **P3** | Die vollständige HTTP-Erfolgsmatrix ist noch nicht exakt testgebunden: Für Matching-Owner akzeptiert der Results-Test lediglich `status_code != 403` statt des exakten Erfolgsstatus und Payload-Vertrags. Dadurch könnten beispielsweise 404/500 bestehen, ohne dass die Matrix fehlschlägt. | `tests/test_web_scan_job_ownership.py:128-143`, besonders Zeile 140 |

### Positiv verifiziert

- Scan-WebSocket authentifiziert und prüft Ownership vor `accept()` und erstem Store-Zugriff.
- Browser-Session-Widerruf und Owner-Wechsel werden vor jedem Scan-WebSocket-Versand erneut geprüft.
- Status, Results, Stop und Sync-Trace verwenden strikte, fail-closed Scan-Job-Ownership.
- Run-Trace wird über den zugehörigen dauerhaften Scan-Job aufgelöst; fehlende, blanke und fremde Owner werden abgewiesen.
- Die vier in v23 konkret benannten Diagnoserouten (`/api/health`, `/api/hardware/status`, `/api/sources`, `/api/workbench/hardware`) sind jetzt geschützt.
- Windows-Recovery behält Jobs bei Authority-/Query-/Close-Fehlern als `authority_ambiguous`, statt sie zu verwerfen.
- Erfolgreiche Windows-Termination plus Close-Fehler führt weiterhin einen bounded wait aus; Close- und Wait-Fehler werden geordnet gruppiert.
- POSIX verwendet pidfd-basierte Signalisierung und erhält Authority-/Signal-/Close-Fehler in den geprüften verschachtelten Pfaden.

### Exakte Start-/Endbindung

Start und Ende waren identisch:

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest SHA-256: `3eda0d54664a491091e8b08c6882dd6c3a6f657be12ac0519cc331e40f08c64c`
- Hash-Einträge: `136`; alle verifiziert
- Exakter Hashzeilen-Aggregat: `b7e98e2d6816f5f1d4566e40877776fd4be5ba6e74ec150217c24e304594ecf7`
- Population: `137`; keine fehlenden oder zusätzlichen Pfade
- Status-Fingerprint: `c8331ddaa9bad3aa7b1e610f9a8174792e6acbbb8a9623af871472b786d4b691`
- Drift: **0**

### Durchführung

- Strikt read-only; keine Tests, Projektimporte oder Produktprozesse ausgeführt.
- **Keine Dateien erstellt oder verändert.**