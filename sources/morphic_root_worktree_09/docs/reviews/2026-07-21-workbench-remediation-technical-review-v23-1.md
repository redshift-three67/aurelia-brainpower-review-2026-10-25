## Freeze-v23 Review

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**

### Befunde

| Priorität | Befund | Beleg |
|---|---|---|
| **P1** | **Windows-Recovery verwirft persistierte Jobs bei erfolgreicher Authority-Abfrage, aber fehlgeschlagenem `CloseHandle`.** `_windows_job_active()` wirft in diesem Fall `OSError`; `_recover_jobs()` fängt diesen breit ab und führt `continue` aus. Ein möglicherweise aktiver Job verschwindet dadurch aus dem Service und nachfolgende Status-/Stop-Aufrufe können falsch 404 liefern. | `apps/web/scan_jobs.py:625-635`, `apps/web/scan_jobs.py:1102-1112` |
| **P2** | **Windows-Termination führt bei anschließendem Handle-Close-Fehler keinen bounded wait mehr aus.** Nach erfolgreichem `TerminateJobObject` wirft der Close-Pfad vor Rückkehr; dadurch werden die Wait-/Bestätigungszweige in Stop und Rollback übersprungen. Die geforderte vollständige Terminate→Close→Wait-Fehlererhaltung ist damit nicht geschlossen. | `apps/web/scan_jobs.py:549-565`, `apps/web/scan_jobs.py:904-911`, `apps/web/scan_jobs.py:1343-1353` |
| **P2** | **Die verlangte vollständige Missing/Blank/Foreign/Matching-Matrix ist nicht vorhanden.** HTTP-Status/Results/Stop/Sync decken die Owner-Matrix weitgehend ab; WebSocket deckt nur fehlende Authentifizierung, fremden und passenden Owner ab. Missing/blank Owner sowie Session-Cookie-Authentifizierung fehlen. Run-Trace hat Matching/Foreign, aber keine expliziten Missing-/Blank-Owner-Fälle. | `tests/test_web_scan_live_security.py:44-90`, `tests/test_web_scan_job_ownership.py:77-143`, `tests/test_web_workbench_runtime.py:450-498` |

### Positiv verifiziert

- Scan-WebSocket authentifiziert vor Store-Zugriff und `accept()`.
- API-Key und Browser-Session werden berücksichtigt.
- Kein persistenter Fallback-Store im Scan-WebSocket.
- Strict-Owner-Prüfung erfolgt vor `accept()` und erstem Datenversand.
- Run-Trace löst zuerst den zugehörigen Scan-Job auf und prüft dessen strikten Owner.
- POSIX verwendet pidfd-basierte Signalisierung; keine numerische Signal-Fallback-Autorität im geprüften Pfad.
- POSIX-Acquisition-, Validation-, Signal- und Descriptor-Close-Fehler werden überwiegend geordnet erhalten.
- Windows Job-Name ist vom privaten Token abgeleitet; Assignment und `DuplicateHandle`-Setup entsprechen dem erwarteten Vertrag.
- Terminate-/Query-plus-Close-Gruppierung innerhalb der jeweiligen Helfer ist vorhanden.

### Freeze-Bindung – Start und Ende identisch

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest SHA-256: `116682a5ea20eda60dcc10d3629b659baffda0574a7d453e981b8bdc89a69f61`
- 132 Hash-Einträge, alle korrekt
- Aggregate: `64558ac9a280dbaa66e82af6036dc99ca208d4cb5684d903a1751e7b70b25e50`
- Population: 133 Pfade, exakte bidirektionale Übereinstimmung
- Drift: **keine**

### Änderungen / Einschränkungen

- Keine Dateien erstellt oder verändert.
- Gemäß Vorgabe keine Tests oder Produktivmodule ausgeführt; ausschließlich statische, read-only Prüfung und Bindungs-/Hash-Verifikation.