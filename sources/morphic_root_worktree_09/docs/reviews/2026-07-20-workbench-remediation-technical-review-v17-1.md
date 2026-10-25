## Technischer Freeze-v17-Abschlussreview

# **REQUEST CHANGES**

**Konfidenz:** HOCH  
**Befunde:** `P0=0, P1=2, P2=1, P3=0`  
**Scope-Drift:** **keine**

### Befundmatrix

| Priorität | Befund | Ort |
|---|---|---|
| **P1** | Windows-Recovery und Rollback verlieren die benannte Job-Object-Autorität, sobald der Supervisor beendet ist. Recovery prüft unter Windows ausschließlich die Supervisor-PID; `_process_group_alive()` liefert dort grundsätzlich `False`. Der persistierte private Token wird nicht zum Öffnen/Prüfen des benannten Job Objects verwendet. Rollback kehrt bei beendetem Supervisor ebenfalls zurück, ohne das möglicherweise weiter aktive Job Object zu terminieren. Produktive Nachfahren können daher nach Supervisor-Crash oder entsprechendem Post-Release-Fehler weiterlaufen und anschließend nicht mehr gestoppt werden. | `apps/web/scan_jobs.py:303-310`, `apps/web/scan_jobs.py:697-703`, `apps/web/scan_jobs.py:844-903`, `apps/web/scan_jobs.py:1016-1046` |
| **P1** | Eine bereits persistierte fehlende beziehungsweise mehrdeutige Prozessautorität wird im Stop-Pfad ohne Job-Object-Terminierung in `stopped` umgewandelt. Wenn Supervisor und numerische Gruppenprüfung inaktiv erscheinen, setzt der `authority_ambiguous`-Zweig den Status direkt auf Erfolg. Das verletzt die geforderte Fail-closed-Grenze und kann einen weiterhin aktiven, aber nicht geöffneten Windows-Job als gestoppt melden. | `apps/web/scan_jobs.py:1032-1043`, `apps/web/scan_jobs.py:1070-1073` |
| **P2** | Der beim Start erzeugte Windows-Job-Handle besitzt keinen Abschlussweg bei normalem beziehungsweise unabhängig terminalem Job. Er wird nur durch erfolgreiche `_terminate_windows_job()`-Aufrufe geschlossen. Regulär abgeschlossene Scans behalten daher Handle und Job Object bis zum Ende des Serviceprozesses; bei vielen Jobs entsteht ein dauerhafter Kernel-Handle-Leak. | `apps/web/scan_jobs.py:428`, `apps/web/scan_jobs.py:461-489`, `apps/web/scan_jobs.py:1075-1161` |

### Erforderliche Korrekturen

1. Eine gemeinsame Windows-Job-Autoritätsfunktion einführen, die:
   - den vorhandenen Handle verwendet oder
   - das ausschließlich aus dem persistierten privaten Token abgeleitete Job Object per Name öffnet,
   - dessen Aktivität sicher bestimmt,
   - fehlende beziehungsweise unlesbare Autorität als `authority_ambiguous` behandelt.

2. Diese Autorität in **Recovery, Stop und Rollback unabhängig von der Supervisor-PID** verwenden. Ein beendeter Supervisor darf nicht beweisen, dass sein Job Object keine produktiven Mitglieder mehr besitzt.

3. `authority_ambiguous` niemals allein aufgrund numerischer Inaktivität in `stopped` umwandeln. `stopped` darf erst nach bestätigter Job-Terminierung oder positiv bestätigter Job-Abwesenheit veröffentlicht werden.

4. Klare Handle-Eigentümerschaft implementieren:
   - erfolgreicher Stop/Rollback: Handle exakt einmal schließen;
   - normaler Terminalzustand: gehaltenen Handle exakt einmal schließen;
   - fehlgeschlagene Terminierung: definierter Retry-/Close-Vertrag;
   - Service-Shutdown: verbleibende eigene Handles schließen.

5. Adversariale Windows-Verträge ergänzen:
   - Supervisor beendet, Job-Nachfahre aktiv, Service-Recovery, Stop über benannten Job;
   - Rollback bei bereits beendetem Supervisor und aktivem Job-Nachfahren;
   - fehlender/unlesbarer benannter Job bleibt `authority_ambiguous`;
   - kein falsches `stopped`;
   - normaler Abschluss schließt den Handle exakt einmal.

### Bestätigte v17-Closures

- Job-Name ist deterministisch und einwegig aus dem privaten Prozessgruppen-Token abgeleitet.
- Zuweisung erfolgt vor Release über den bereits geöffneten `Popen._handle`.
- Assignment-Fehler beendet den Gate-Supervisor über dessen stabilen `Popen`-Handle vor produktivem Spawn.
- Im produktiven `scan_jobs.py` existiert kein `taskkill`-Pfad mehr.
- Aktiver Stop und aktiver Rollback verwenden Job-Handle/-Name statt numerischer PID-Signalisierung.
- Die direkte strikte Identitätsmatrix deckt Match, Mismatch, fehlende Sollidentität, `NoSuchProcess`, `ProcessLookupError`, `ESRCH` und nicht bestätigte Fehler ab.
- Der unveränderte v9–v16-/Gesamtproduktscope wurde gegen die früheren Auth-, Ownership-, Persistenz-, POSIX-Provenienz-, Hardware-, Polling-, Reset-, Telemetrie- und Accessibility-Befundklassen abgeglichen; außerhalb der genannten Windows-Lifecycle-Befunde ergab sich kein zusätzlicher P0–P3-Befund.

### Freeze-v17-Bindung

| Prüfung | Start | Ende |
|---|---:|---:|
| Branch | `operator-workbench-phase1` | identisch |
| HEAD | `3271ff9366ab3fecb2a158913a0cc19ed6a06726` | identisch |
| Manifest-SHA-256 | `ccb996eb4c167b525581d384f44c6dcfe3e97a94043504903a5731fe092948ce` | identisch |
| Einzelhashes | `105/105 OK` | `105/105 OK` |
| Hashzeilen-Aggregat | `92309bc9a7b86d16774f861ad5cb680505b7fc092e7c4b4d4d930905f45746aa` | identisch |
| Exakte Population | `106` | `106` |
| Scope minus Dirty | leer | leer |
| Dirty minus Scope | leer | leer |
| Drift | keine | keine |

**End-Status-Fingerprint:**  
`64e8ca6a0038bc269cb429e528dc633db66fb851ba3b1b27ad41a5be8c7bd7ac`

### Ausführung

- Keine Dateien erstellt, verändert oder gelöscht.
- Keine Tests, Projektimporte, Server, Netzwerkzugriffe oder Installationen ausgeführt.
- Ein erster Inline-Python-Populationsparser hatte einen harmlosen Quotingfehler; die korrigierte vollständige Startprüfung und die reservierte Endbindung waren erfolgreich.

**Endgültiges Verdikt: `REQUEST CHANGES — P0=0, P1=2, P2=1, P3=0; null Scope-Drift`.**