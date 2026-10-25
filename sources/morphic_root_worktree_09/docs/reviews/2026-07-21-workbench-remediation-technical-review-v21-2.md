## Freeze-v21-Zweitreview

**Verdikt: REQUEST CHANGES**  
**Konfidenz: hoch**  
**Befunde: P0=0 · P1=1 · P2=2 · P3=0**  
**Scope-Drift: 0**

### Befunde

| Prio | Befund | Evidenz |
|---|---|---|
| **P1** | Die Scan-Ownership bleibt für Legacy-/recovered Jobs ohne `owner_id` absichtlich fail-open. Status, Ergebnis und Stop akzeptieren damit einen authentifizierten, aber nicht als Eigentümer belegten Operator. Der Test schreibt dieses Verhalten ausdrücklich fest. Für einen strikten Ownership-Vertrag muss fehlende Eigentümerschaft fail-closed sein oder über eine separat belegte Migration gebunden werden. | `apps/web/main.py:769-790,838-858`; `tests/test_web_scan_job_ownership.py:75-81` |
| **P2** | Im allgemeinen POSIX-Signalpfad gehen gleichzeitige Close-Fehler verloren: `_signal_posix_authority()` erzeugt zunächst den Signalfehler, unterdrückt im `finally` aber `close_failures`, sobald bereits eine Exception aktiv ist. Damit ist die vollständige Signal-/Close-Fehlermatrix außerhalb des korrigierten Startup-Helfers nicht erfüllt. | `apps/web/scan_jobs.py:825-844` |
| **P2** | Nach einem Windows-Assignment-/`DuplicateHandle`-Fehler führt der aufrufende Startup-Pfad `process.kill()` und `wait()` ohne Exception-Gruppierung aus. Ein Kill-/Wait-Fehler kann daher den ursprünglichen Job-Retention-Fehler ersetzen. Die lokalen Duplicate-/Close-Doppelfehler sind korrekt geordnet, aber die vollständige Startup-Lifetime-/Error-Matrix endet nicht an `_create_windows_job()`. | `apps/web/scan_jobs.py:487-511,1210-1219`; exakte Tests nur in `tests/test_web_scan_jobs.py:355-422` |

### Bestätigte Punkte

- `/api/privacy/clients` verwendet jetzt `Depends(verify_api_key)`; konfigurierte Auth wird mit HTTP 401 geprüft.
- Reports, Workbench-Persistenz, Gruppenentwürfe/-einwilligungen/-policy, Scan- und Harmonisierungsendpunkte besitzen die vorgesehenen Auth-Grenzen.
- Fremde explizite Scan- und Harmonisierungs-Owner werden mit HTTP 403 abgewiesen.
- Der POSIX-**Startup**-Helfer gruppiert Primär-, Signal-, Close- und Wait-Fehler und verwendet `signal.SIGKILL`.
- In produktivem POSIX-Code wurden keine numerischen Signal-Fallbacks, `os.kill`, `killpg` oder `taskkill` gefunden. Verbleibende `process.kill()`-Aufrufe liegen in Windows-Zweigen.
- Die exakten `DuplicateHandle`-Argumente sind testgebunden: Current Process, lokaler Job-Handle, Gate-Prozesshandle, Access `0`, nicht erblich, `DUPLICATE_SAME_ACCESS`.
- Frühere Lifecycle-, Persistenz-, Polling-, Hardware-Cleanup-, Reset-, Telemetrie- und Accessibility-Bereiche wurden statisch weiterverfolgt; kein zusätzlicher Befund dort.

### Freeze-Bindung

Start und Ende identisch:

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest-SHA: `a2707d64bfd8d4da8e30bc25c6e0dda9d4fb2cec398a68c80a82c7064d8586d3`
- Einzelhashes: **121/121 OK**
- Population: **122**
- Status-Fingerprint: `a6472f46964aabd482bde5e4d1cc6dead383d68c023421abe5c23542ecb462b8`
- Drift: **0**
- Das vorgegebene Aggregat `b947987d…` konnte nicht unabhängig reproduziert werden: Ein zusätzlicher read-only Aggregatbefehl wurde vom Tool-Gate blockiert. Es wird daher nicht fälschlich als eigenständig bestätigt ausgewiesen.

### Ausführung

- Keine Tests, Projektimporte, Netzwerkzugriffe oder Produktprozesse.
- **Keine Dateien erstellt oder verändert.**
- Ein read-only Aggregat-Rechenversuch wurde blockiert; alle übrigen Freeze- und Endprüfungen liefen erfolgreich.