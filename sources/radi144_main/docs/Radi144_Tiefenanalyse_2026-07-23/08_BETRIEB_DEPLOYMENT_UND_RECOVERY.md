# 08 - Betrieb, Deployment und Recovery

## 1. Unterstützte Betriebsmodelle im Ist-Zustand

### 1.1 Windows API/Browser

Vorgesehener Ablauf:

1. `install_dependencies.bat` erzeugt `.venv`.
2. Requirements und zusätzliche Pakete werden installiert.
3. `run.bat` prüft das API-Profil.
4. `main.py` startet Uvicorn im Reloadmodus.
5. Browseroberfläche wird im aktuellen Arbeitsbaum durch FastAPI ausgeliefert.

Probleme:

- Batchdateien hängen vom aktuellen Arbeitsverzeichnis ab.
- Reloadmodus ist kein Produktionsstart.
- README nennt Port 8000, aktueller Direktstart 8090.
- Browser wird nicht automatisch geöffnet.
- der Runtime-Preflight prüft Modulfund, nicht kompatible Versionen oder Funktionsfähigkeit.

### 1.2 Windows PowerShell/CLI

`generate_matrix.ps1` startet `dev_cli.py` und erzeugt lokale Ausgaben. Dieses Modell ist funktional breit, aber an Windows, PowerShell, Tkinter/Winsound und CWD-abhängige Pfade gekoppelt.

### 1.3 Linux/systemd

Zielmodell:

- Debian 12,
- Python 3.11,
- NVIDIA/CUDA,
- `/opt/resonance-engine`,
- Servicekonto `resonance`,
- Uvicorn mit konfigurierbaren Workern,
- Logdateien unter `/var/log/resonance-engine`.

Die vorhandene Unit enthält positive Härtung:

- `NoNewPrivileges=true`,
- `ProtectSystem=strict`,
- `PrivateTmp=true`,
- begrenzte `ReadWritePaths`.

Sie löst aber Authentisierung, Pfadsandbox innerhalb freigegebener Verzeichnisse, Multiworker-Persistenz, TLS oder Monitoring nicht.

## 2. Installations- und Umgebungsdrift

### 2.1 Zwei Windows-Venv-Modelle

- `install_dependencies.bat` erstellt `.venv`.
- `setup_new_pc.bat` erstellt optional `venv`.
- `run.bat` sucht nur `.venv` und fällt sonst auf globales Python zurück.

Ein Setup kann deshalb erfolgreich wirken, während der Start eine andere Pythoninstallation verwendet.

### 2.2 Python-Version

- README/Batch: Python 3.10+.
- Linux-Setup: Python 3.11.
- Bus: `StrEnum`, damit mindestens Python 3.11.
- kein `requires-python`-Metadatum.

### 2.3 Dependencyinstallation

Windows:

- installiert Requirements,
- installiert mehrere Pakete anschließend nochmals unversioniert.

Linux:

- installiert Torch/Torchvision aus CUDA-Index,
- installiert danach `requirements.txt`, das Torch erneut als offene Mindestversion enthält.

Mögliche Folge: CPU-/CUDA-Wheel oder Version kann unbeabsichtigt ersetzt werden.

## 3. Konfigurationsmanagement

### 3.1 Tatsächlich verwendete Variablen

- `APP_HOST`
- `APP_PORT`
- `CORS_ORIGINS`
- `API_KEY`
- `DWAVE_API_TOKEN`
- `R144_ERASURE_GATE_TOKEN`
- `R144_AUDIT_LOG_PATH`

### 3.2 Deklarierte, aber wirkungslose oder unvollständig verdrahtete Variablen

`deploy/server.env.example` dokumentiert:

- `USE_CUDA`,
- `EMF_ENABLED`,
- `EMF_CONTINUOUS_MONITORING`,
- `EMF_CALIBRATION_INTERVAL_SEC`,
- `DATA_DIR`,
- `LOG_DIR`,
- `EXPORT_DIR`.

Diese Werte werden in der sichtbaren API-/Enginekonfiguration nicht als zentrale Settings ausgewertet. Gefährliche Scheinsicherheit:

- `USE_CUDA=false` verhindert GPU-Nutzung nicht zuverlässig.
- `EXPORT_DIR` begrenzt `output_path` nicht.
- `DATA_DIR` verlegt Runtime-Daten nicht.
- EMF-Envwerte steuern den Startzustand nicht.

Gleichzeitig fehlen die tatsächlich verwendeten Lösch-/Auditvariablen im Beispiel.

### 3.3 Clean-Checkout-Problem

`deploy/server.env` ist ignoriert (`.gitignore:29-30`), die systemd-Unit verlangt sie zwingend (`deploy/resonance-engine.service:10-12`). `setup_server.sh` erzeugt sie nicht aus dem Beispiel.

Folge:

- sauberer Clone: Service kann wegen fehlender Env-Datei scheitern,
- lokale Arbeitskopie: vorhandene Env/Secrets können per rsync mitkopiert werden.

## 4. Deploymentprozess

### 4.1 Ist-Ablauf

`deploy/setup_server.sh`:

1. installiert Betriebssystempakete und NVIDIA-Pakete,
2. erzeugt Servicekonto und Verzeichnisse,
3. rsynct den Arbeitsbaum,
4. erzeugt `venv`,
5. installiert Torch und Requirements,
6. prüft CUDA nur informativ,
7. installiert/aktiviert systemd,
8. führt EMF-Profiling als Validierung aus.

### 4.2 Kritische Lücken

- `rsync` wird verwendet, aber nicht installiert.
- Source ist ein beliebiger, eventuell dirty Arbeitsbaum.
- Denylist statt Packaging-Allowlist.
- sensible ignorierte Dateien können kopiert werden.
- Owner wird vor rsync gesetzt; kopierte Dateien können danach falsche Eigentümer besitzen.
- kein Buildartefakt, keine Prüfsumme, keine Signatur.
- kein Predeploy-Backup.
- keine Datenmigration.
- kein Readinesscheck vor Traffic.
- kein atomarer Releasewechsel.
- kein Rollback.
- keine reproduzierbare Dependencyauflösung.

### 4.3 CUDA

Das Setup gibt `torch.cuda.is_available()` aus, bricht bei `False` aber nicht ab. Die API fällt bei CUDA-Initialisierungsfehlern still auf CPU zurück. Ein vermeintlicher GPU-Server kann dadurch unerkannt im langsameren CPU-Modus laufen.

## 5. Packaging und Release

Nicht gefunden:

- `pyproject.toml`,
- Wheel-/sdist-Konfiguration,
- Lock-/Constraintsdatei,
- Dockerfile/Compose,
- CI/CD-Workflow,
- Releaseworkflow,
- Tags,
- Changelog als verlässlicher SSOT,
- Artefaktsignaturen,
- SBOM,
- Projektlizenz und Third-Party-Notices.

Ein Release ist derzeit eine Dateikopie, kein unveränderliches, reproduzierbares Produktartefakt.

## 6. Health, Readiness und Observability

### 6.1 Health

`GET /` liefert statisch `status: active` (`main.py:115-121`). Nicht geprüft werden:

- Storelesbarkeit/-schreibbarkeit,
- Datenintegrität,
- freier RAM/Commit/VRAM/Disk,
- GPU-Verfügbarkeit,
- Referenzdaten,
- Workerzustand,
- Backupalter,
- Queue-/Jobzustand.

### 6.2 Logging

Ist:

- Python-Basislogging als Text,
- systemd appendet stdout/stderr in zwei Dateien,
- CLI schreibt Klarname, Fokus, Score und Matrixstring.

Fehlend:

- strukturierte Logs,
- Correlation-/Request-/Session-ID,
- PII-Redaktion,
- Logrotation und Retention,
- zentrale Sammlung,
- Metriken,
- Tracing,
- Alarmierung,
- Crash-/OOM-Erfassung.

`setup_server.sh` empfiehlt `journalctl`, obwohl stdout/stderr in Dateien umgeleitet werden.

### 6.3 Metriken/SLO

Keine nachweisbaren Definitionen für:

- Verfügbarkeit,
- Latenz,
- Fehlerrate,
- Jobdurchsatz,
- GPU-/RAM-/Diskschwellen,
- Queuealter,
- Backupfrische,
- RPO/RTO.

## 7. Workload- und Kapazitätsmanagement

Aktuell:

- schwere Arbeit direkt im Request,
- kein Jobmodell,
- keine GPU-Semaphore,
- keine Backpressure,
- keine Rate Limits,
- keine serverseitige Cancel-Kooperation,
- hardwareadaptive, aber nicht vollständig sichere Speicherheuristik.

Vier Worker sind kein belastbarer Ersatz. Sie erhöhen stattdessen:

- JSON-Races,
- GPU-Speicherdruck,
- divergierende Enginezustände,
- nicht deterministisches Routing von WebSocket-/Analysezuständen.

## 8. Backup und Recovery

### 8.1 Ist-Befund

- Historische In-Repo-Restorewerkzeuge gelten als stale.
- Dokumentation verweist auf externe ShadowCopies.
- Kein ausführbarer, aktueller SSOT-Prozess im Repository.
- Vorhandene Snapshots sind älter als aktuelle Runtime-Daten.
- Metadaten- und Artefaktsicherung können auseinanderfallen.

### 8.2 Fehlende Recovery-Eigenschaften

- RPO/RTO,
- konsistenter Snapshot,
- Verschlüsselung,
- Offsite-Strategie,
- Rotationsplan,
- Restore-Staging,
- regelmäßiger Restore-Beweis,
- Datenmigration beim Restore,
- Schlüssel-/Secretwiederherstellung,
- Löschung aus Backups,
- Disaster-/Incident-Runbook.

## 9. Update und Rollback

Der aktuelle Setupweg überschreibt die aktive Installation und installiert frische offene Dependencyversionen. Es fehlen:

- versionierte Releaseverzeichnisse,
- atomarer Symlinkwechsel,
- Kompatibilitätscheck,
- Schema-Migrationen,
- Vor-/Nachdeploy-Backup,
- Datenrollback,
- Canary/Blue-Green,
- dokumentiertes Rollbackkommando.

## 10. Supportfähigkeit

Nicht nachgewiesen:

- technische/fachliche Owner,
- Supportkontakt,
- Betriebszeiten/SLA/SLO,
- Eskalationspfad,
- Incidentprozess,
- Datenschutzvorfallprozess,
- Diagnosebundle,
- bekannte Fehler als aktueller Katalog,
- Zielhardware- und Kompatibilitätsmatrix.

Die vielen Root-Diagnoseskripte ersetzen kein unterstütztes Diagnosewerkzeug.

## 11. Operations-Reifegrad

| Bereich | Ist 0-4 | Kerndefizit |
|---|---:|---|
| Windows-Installation | 1,7 | zwei Venv-Modelle, keine Versionserzwingung |
| Linux-Deployment | 0,8 | Arbeitsbaumkopie, Env-/Owner-/Dependencyprobleme |
| Packaging | 0,2 | kein Artefakt |
| Konfiguration | 1,0 | tote und fehlende Settings |
| Mehrprozessfähigkeit | 0,4 | JSON und globaler Enginezustand |
| Logging | 1,1 | Textlogs ohne Rotation/Redaktion |
| Monitoring | 0,3 | keine technischen Metriken/Alerts |
| Health/Readiness | 0,4 | statischer Rootstatus |
| Backup/Restore | 0,5 | kein aktueller verifizierter Prozess |
| Upgrade/Rollback | 0,2 | nicht vorhanden |
| Release/CI | 0,1 | keine Pipeline/Tags/Artefakte |
| Supply Chain | 0,1 | kein Lock, Scan, Lizenz, SBOM |
| Support | 0,3 | keine Owner/Runbooks/SLO |

## 12. Betriebszielbild

Vor einem produktiven Serverbetrieb wird mindestens benötigt:

1. versioniertes, signiertes Artefakt aus sauberer CI,
2. typisiertes, fail-closed Settingsmodell,
3. getrennte Secrets,
4. TLS/Proxy/Firewall/Auth,
5. kontrollierter Analyseworker statt synchroner Schwerlast,
6. transaktionale Persistenz,
7. technische Health-/Readinesschecks,
8. strukturierte Logs, Metriken und Alerts,
9. verschlüsselte Backups mit Restoretest,
10. atomarer Upgrade-/Rollbackprozess,
11. dokumentierte Owner, SLO, Incident- und Datenschutzrunbooks.
