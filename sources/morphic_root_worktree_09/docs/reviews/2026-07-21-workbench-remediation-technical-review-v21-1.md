## Freeze-v21-Review

**Verdikt: APPROVE**  
**Konfidenz: HOCH**  
**Befunde: P0=0 · P1=0 · P2=0 · P3=0**  
**Scope-Drift: 0**

### Verifiziert

- `/api/privacy/clients` verwendet `Depends(verify_api_key)` und damit dieselbe API-Key-/Browser-Session-Grenze wie Reports, Scans und Harmonisierung. Anonymer Zugriff bei konfiguriertem Schlüssel ist mit 401 abgedeckt; der lokale No-Key-Safe-View bleibt erhalten.
- POSIX-Startup:
  - pidfd wird unmittelbar nach `Popen` und vor der Creation-Time-Abfrage erworben.
  - pidfd-Akquisitionsfehler plus Gate-Wait-Timeout bleiben gemeinsam erhalten.
  - Identity `None` und Identity-Ausnahmen führen über den vorab erworbenen pidfd.
  - Signal-, Close- und Wait-Fehler werden vollständig versucht und geordnet zusammen mit dem Primärfehler bewahrt.
  - Startup-pidfd-Closefehler plus Waitfehler bleiben gemeinsam erhalten.
  - Produktive POSIX-Pfade verwenden symbolisch `signal.SIGTERM`/`signal.SIGKILL`; kein numerischer produktiver Signal-Fallback gefunden.
  - Der Crash-/Recovery-Test schließt den pidfd in `finally`.
- Windows:
  - `DuplicateHandle` ist exakt gebunden: aktueller Prozess als Quelle, lokaler Job-Handle, Gate-Prozess als Ziel, Access `0`, nicht vererbbar, `DUPLICATE_SAME_ACCESS`.
  - Duplicate-/Close-Doppelfehler werden in der richtigen Reihenfolge geprüft.
  - Der separate Owner-Prozess endet mit `os._exit(0)`; Recovery und Stop erfolgen anschließend aus einem anderen Prozesskontext.
- Erneuter Produkt-/Security-Scope-Check ergab keine Regression bei Authentifizierung, Ownership, Persistenz, Prozessautorität, Hardware-Cleanup, Polling, Reset, Telemetrie oder Accessibility.

### Start-/Endbindung

- Branch/HEAD: `operator-workbench-phase1` / `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest-SHA-256: `a2707d64bfd8d4da8e30bc25c6e0dda9d4fb2cec398a68c80a82c7064d8586d3`
- Einzelhashes: **121/121 OK**
- Aggregat: `b947987d8a31c52d7cdca2f143d0f1e85763b68b6707c27f2a54618366ba935a`
- Population: **122/122**, bidirektional vollständig
- Endstatus-Fingerprint: `a6472f46964aabd482bde5e4d1cc6dead383d68c023421abe5c23542ecb462b8`
- Drift: **keine**

### Ausführung

- Keine Dateien erstellt oder verändert.
- Keine Tests, Projektimporte oder Produktprozesse ausgeführt; ausschließlich read-only Quelltext-, Git- und Hashprüfung.
- Keine Probleme oder Blocker aufgetreten.