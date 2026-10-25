## Freeze-v19-Review

**Verdikt: `REQUEST CHANGES`**  
**Konfidenz: HOCH**  
**Befunde:** `P0=0, P1=0, P2=1, P3=0`  
**Scope-Drift:** `0`

### Befund

| Priorität | Befund | Ort |
|---|---|---|
| **P2** | Der echte Windows-Restartvertrag ist weiterhin nicht vollständig belegt. Der Test erzeugt eine zweite `LocalScanJobService`-Instanz, während die erste Instanz und ihr äußerer Job-Handle im selben Prozess weiterleben. Er prüft daher nicht, ob das benannte äußere Job Object nach Ende des ursprünglichen Service-/Handle-Eigentümerprozesses erneut geöffnet, abgefragt und terminiert werden kann. Das verschachtelte Gate-Job-Object mit `KILL_ON_JOB_CLOSE` verhindert zwar den Fall „Gate-Supervisor beendet, produktiver Nachfahre lebt“, schließt aber den separaten Fall „Serviceprozess beendet, Gate-Supervisor lebt“ nicht. | `tests/test_web_scan_jobs.py:1277-1310`, `services/scan_process_gate.py:64-75,152-157`, `docs/superpowers/plans/2026-07-21-workbench-freeze-v18-review-remediation-v19.md:13` |

### Bestätigte Closures

- Recovery konstruiert zuerst `_LocalScanJob` und entscheidet anschließend über `_job_runtime_active()`; Windows fragt dabei das benannte Job Object unabhängig von PID/Creation-Time ab (`scan_jobs.py:956-1014`).
- Windows-Stop konsultiert Job-Autorität vor jeder PID-Identitätsentscheidung (`scan_jobs.py:1123-1176`).
- Assignment- und `CloseHandle`-Fehler bleiben geordnet im `ExceptionGroup` erhalten; direkter Vertragstest vorhanden.
- Handle-/pidfd-Cleanup versucht alle stabilen Handles; numerische Cleanup-Signalisierung wurde entfernt.
- Der v18-POSIX-Escape ist geschlossen: tokenweite Ermittlung plus pidfd-Signalisierung erfasst auch Nachfahren nach neuer Session; fremde/recycelte Gruppen bleiben fail-closed.
- Der übrige Security-/Produktscope ist gegenüber v18 byte-identisch; geändert wurden nur `apps/web/scan_jobs.py`, `tests/test_web_scan_jobs.py` und neue Review-Dokumente. Keine neuen Befunde bei Auth, Ownership, Persistenz, Hardware, Polling, Reset, Telemetrie oder Accessibility.

### Start-/Endbindung

- Branch/HEAD: `operator-workbench-phase1` / `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest: `068a6c3ccb07271dce21967661d1814accac02b708f3ca101ad8206aba3ba8bc`
- Einzelhashes: `113/113 OK`
- Aggregat: `0a0a6dcada4ade826fdbd553f318787d01828b7bbe5ff110d6f4b8412773e636`
- Population: `114`
- Scope minus Dirty: `0`
- Dirty minus Scope: `0`
- Status-Fingerprint Start/End: `0a63e8f87f536610e0692115e214a2662c06614936cd3edfe2256ec4fcf4907b`
- Drift: **keine**

### Ausführung

- Keine Dateien erstellt oder verändert.
- Keine Tests, Projektimporte oder Produktprozesse ausgeführt.
- Ein anfänglicher read-only Shell-Quoting-Versuch schlug ohne Seiteneffekt fehl; die vollständige Bindung wurde danach erfolgreich wiederholt.