# Morphic Engine V1

## Aktueller Betriebsstatus

Morphic Engine V1 ist ein **lokal funktionsfähiger Operator-Prototyp**. Die Operator Workbench ist für einen einzelnen lokalen Benutzer vorgesehen. Sie ist **nicht für externen Mehrbenutzer-, LAN- oder SaaS-Betrieb freigegeben**.

Aktive Schutzgrenze:

- kontrollierte Startwege binden ausschließlich an Loopback (`127.0.0.1`, `localhost`, `::1`)
- `web_server.py` weist Nicht-Loopback-`APP_HOST` fail-closed ab
- `Run-WebUI.ps1` bindet fest an `127.0.0.1` und beendet keinen bereits laufenden Listener
- Netzwerkbetrieb erfordert vorab Phase 2B: TLS, zentral abgeleitete Principal-/Tenant-Identität, Authentisierung und Autorisierung

## Start unter Windows

### Empfohlen: PowerShell-Launcher

```powershell
& C:\morphic_v1\.worktrees\operator-workbench-phase1\Run-WebUI.ps1
```

Der Launcher verwendet Port 8000. Ist dieser belegt, bricht er absichtlich ab und nennt die PID; der bestehende Prozess wird nie automatisch beendet.

### Kontrollierter Python-Start

```powershell
$env:PYTHONUTF8="1"
$env:OPENBLAS_NUM_THREADS="1"
& C:\morphic_v1\.venv\Scripts\python.exe web_server.py
```

`APP_HOST` darf nur `127.0.0.1`, `localhost` oder `::1` sein. Beispielsweise wird `APP_HOST=0.0.0.0` vor dem Serverstart abgewiesen.

> Den direkten `uvicorn`-Aufruf nur für isolierte Entwicklungs-/Testläufe mit explizitem `--host 127.0.0.1` verwenden. Er umgeht die Schutzprüfung des kontrollierten `web_server.py`-Startwegs.

## Operativer Umgang

- Vor jedem Start: Portbelegung prüfen; keine fremden Prozesse beenden.
- Keine Klientenexporte, Runtime-Daten oder Secrets in Git, Tests oder Supporttickets kopieren.
- Die API-Key-Option ist kein Mehrbenutzer- oder Tenant-System. Für den gewählten lokalen Loopbackmodus bleibt sie eine zusätzliche optionale lokale Barriere.
- Einen ausführlichen Ablauf enthält `docs/LOCAL_OPERATOR_RUNBOOK.md`.

## Repository-Struktur

```text
apps/        CLI-, API- und Web-Frontends
core/        Domänenlogik, Compliance, Resonanz, Persistenz
providers/   Hardware-/Daten-/Quantum-Adapter
services/    Anwendungsservices
infra/       Konfiguration, Logging, Orchestrierung
data/        Schemata, Referenzdaten, Artefakte
docs/        Architektur, Audit, Runbooks und Pläne
tests/       pytest-Regressionen
```

## Validierung

```powershell
$env:PYTHONUTF8="1"
$env:OPENBLAS_NUM_THREADS="1"
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests -q
node --check apps/web/static/app.js
node --check apps/web/static/workbench-api.js
node --check apps/web/static/workbench-render.js
```
