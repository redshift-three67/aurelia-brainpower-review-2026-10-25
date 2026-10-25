## Freeze-v25 Review

**Verdikt: REQUEST CHANGES — NICHT APPROVE**  
**Konfidenz: hoch für Codebefunde, mittel für Freeze-Bindung**  
**Befunde: P0=0 · P1=3 · P2=2 · P3=1**

| Prio | Befund | Evidenz |
|---|---|---|
| **P1** | **WebSockets reagieren nicht fail-closed auf eine dynamische Aktivierung der Authentifizierung.** Beide Handler speichern `authentication_required` einmal beim Verbindungsaufbau. Wurde die Verbindung im No-Key-Modus geöffnet, liefert `websocket_authenticated(..., required=False)` dauerhaft `True`, selbst wenn danach ein API-Key konfiguriert wird. Rotation/Widerruf eines bereits konfigurierten Keys funktioniert; `no key → configured key` hingegen nicht. | `apps/web/emf.py:96-108`; `apps/web/scan_live.py:42-70`; `apps/web/security.py:75-86` |
| **P1** | **Nicht alle HTTP-Diagnoseflächen verwenden konfigurierte Authentifizierung.** `/api/status` bleibt ohne `verify_api_key` öffentlich und die Tests schreiben selbst bei konfigurierbarer Auth-Architektur explizit HTTP 200 fest. Das widerspricht dem verlangten vollständigen Diagnose-Audit und dem Freeze-Header „all diagnostics auth“. | `apps/web/main.py:484-486`; `tests/test_web_shell.py:293-310` |
| **P1** | **Harmonization-Stop besitzt keine bestätigte POSIX-/Windows-Prozesskonvergenz.** Der Stop-Pfad schreibt lediglich einen Marker und publiziert sofort `stopped`; er signalisiert, terminiert oder joint den `multiprocessing.Process` nicht. Ein blockierter Hardware-/Treiberaufruf kann daher nach erfolgreichem Stop-Response weiterlaufen. | `services/harmonization_worker.py:774-788,791-812`; `apps/web/harmonization.py:164-173` |
| **P2** | **Rohe Exceptions gelangen weiterhin in Hardware-HTTP-Payloads.** `/api/hardware/status` kann `driver_layer.error = str(exc)` liefern; `/api/workbench/hardware` übernimmt `measure_realtime_calibration()` einschließlich `error: str(exc)`. Damit ist „generic errors/no traceback material“ nicht vollständig geschlossen. | `apps/web/main.py:112-130,535-544`; `apps/web/hardware_truth.py:27-45,58,130-135` |
| **P2** | **Owner-/Tenant-IDs und rohe Laufzeitfehler werden in erfolgreichen Ressourcen-Payloads veröffentlicht.** Scan-Status gibt `owner_id`, vollständigen Befehl, `stdout_tail`, `stderr_tail` und Artefaktpfade zurück; Harmonization-Snapshots geben `tenant_id`, `operator_id` und das rohe `error_message` zurück. Ein Subprozess-Traceback kann so trotz Analyze-Fix weiterhin über HTTP erscheinen. | `apps/web/scan_jobs.py:1489-1506`; `apps/web/main.py:781-793`; `apps/web/harmonization.py:175-207`; `services/harmonization_worker.py:695-697` |
| **P3** | **Die vollständige Owner-Erfolgs-/Fehlermatrix ist nicht exakt payload-gebunden.** Nur Scan Results prüft den kompletten 200-Envelope. Status, Stop und Sync prüfen für Matching Owner lediglich HTTP 200; bei fehlendem/blankem/fremdem Owner fehlen überwiegend exakte generische Response-Verträge. Harmonization-Pfade besitzen keine entsprechende vollständige Matrix. | `tests/test_web_scan_job_ownership.py:77-93,107-151` |

### Positiv verifiziert

- EMF verweigert bei anfänglich konfigurierter Authentifizierung vor `accept()`, Aktivierung und Messung.
- EMF und Scan prüfen Session-/API-Key-Autorität vor jeder Messung beziehungsweise jedem Store-Zugriff/Send erneut.
- Scan-WebSocket prüft Ownership vor `accept()` und wiederholt sie vor dem Versand.
- Scan Results ist für Matching Owner exakt auf HTTP 200 und den vollständigen bereinigten Envelope gebunden.
- Scan-Ownership bleibt bei `None`, leerem und Whitespace-Owner fail-closed.
- Die geprüften Scan-POSIX-pidfd- und Windows-Job-Object-Hilfspfade bewahren kombinierte Primär-/Cleanup-Fehler weitgehend geordnet.

### Freeze-Bindung

- Manifest bei Start und Endlesung: Branch `operator-workbench-phase1`, HEAD `3271ff9366ab3fecb2a158913a0cc19ed6a06726`, deklarierter Umfang `146 + Manifest`.
- Erwartete Werte laut Auftrag: Manifest-SHA `e69b33ac…c5a`, Aggregat `680c3176…29d2`, Population `147`.
- Wegen der ausdrücklichen Vorgabe **„keine Ausführung“** wurden SHA-Prüfung, 146 Einzelhashes, Aggregat, Git-Status-Population und End-Rehash nicht ausgeführt. Die exakte kryptographische Zero-Drift-Bindung ist daher **nicht unabhängig bestätigt**.

### Hygiene

- Rein statische, read-only Prüfung; keine Tests, Imports oder Produktprozesse.
- **Keine Dateien erstellt oder verändert.**
- Kein `APPROVE`: mehrere P1–P3-Befunde und keine unabhängig ausführbare Zero-Drift-Bestätigung.