# Local Operator Runbook – Morphic V1

**Betriebsprofil:** Phase 2A, lokaler Einoperator
**Geltung:** Windows-Arbeitsstation, ausschließlich Loopback
**Nicht freigegeben:** LAN, Internet, Mehrbenutzer, SaaS

## 1. Sicherheitsgrenze

| Gegenstand | Vorgabe |
|---|---|
| Bindadresse | `127.0.0.1`, `localhost` oder `::1` |
| Kontrollierter Python-Start | `web_server.py`; Nicht-Loopback wird vor Uvicorn abgewiesen |
| PowerShell-Start | `Run-WebUI.ps1`; fest auf `127.0.0.1:8000` |
| Portkonflikt | prüfen und bewusst lösen; Launcher beendet niemals fremde Prozesse |
| Netzwerkmodus | gesperrt, bis Phase 2B mit TLS, IdP, Principal-/Tenant-AuthZ abgeschlossen ist |
| Daten | Klienten-/Export-/Runtime-Daten lokal behandeln; nicht in Git oder Supportausgaben kopieren |

## 2. Vor dem Start

```powershell
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
  Where-Object { $_.LocalPort -in 8000,8090 } |
  Select-Object LocalAddress,LocalPort,OwningProcess
```

Wenn Port 8000 belegt ist: Prozess und Zweck prüfen. Den Prozess nicht blind beenden. Einen kontrollierten alternativen Testport nur mit explizitem Loopback-Bind verwenden.

## 3. Start

Bevorzugt:

```powershell
& C:\morphic_v1\.worktrees\operator-workbench-phase1\Run-WebUI.ps1
```

Oder kontrolliert ohne Browserstart:

```powershell
$env:PYTHONUTF8="1"
$env:OPENBLAS_NUM_THREADS="1"
& C:\morphic_v1\.venv\Scripts\python.exe web_server.py
```

Öffne ausschließlich `http://127.0.0.1:8000/`.

## 4. Post-Start-Schnellprüfung

```powershell
Invoke-WebRequest http://127.0.0.1:8000/api/health | Select-Object StatusCode
Invoke-WebRequest http://127.0.0.1:8000/api/workbench/registry | Select-Object StatusCode
```

Erwartet: HTTP 200. Ein invalides Scan-Preview-Request muss HTTP 422 liefern; das beweist, dass Vertragsvalidierung aktiv ist.

## 5. Betriebshinweise

- Die Workbench fordert vor Vorschau und Scanstart Pflichtfelder, DDMMYYYY-Geburtsdatum und beide Einwilligungen.
- API-/Previewfehler werden als Operatorstatus dargestellt. Kein Laufwechsel/Polling ohne nichtleere Job-ID.
- HTML-Berichtsvorschauen liegen in einem `sandbox`-Iframe; das Backend sanitisiert die zugelassene HTML-Vorschau zusätzlich.
- Bei Browser-, Speicher- oder Hardwareproblemen nicht die Engineformeln ändern. Erst Health, Hardware Truth und Job-/Run-Trace prüfen.

## 6. Beenden

Im gestarteten Terminal `Ctrl+C` verwenden und anschließend Listener erneut prüfen. Keine erzwungenen Prozessabschüsse, außer sie wurden nach Identifikation und eigener Verantwortung bewusst entschieden.

## 7. Netzwerk- oder Mehrbenutzerbedarf

Nicht durch Umsetzen von `APP_HOST` oder einen offenen Uvicorn-Host improvisieren. Vorher ist Phase 2B erforderlich: TLS, OIDC/IdP oder gleichwertige signierte Sessions, serverseitiger Principal, Rollen, Tenant-/Owner-AuthZ, CORS-/Origin-Policy und negative Zugriffstests.
