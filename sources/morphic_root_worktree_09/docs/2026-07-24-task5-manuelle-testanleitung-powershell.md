# Task 5: Manuelle Testanleitung fuer PowerShell

Diese Anleitung startet die Operator Workbench fuer die manuelle Abnahme von
Freeze-v5 Task 5 / RV4-05. Der Test verwendet einen eigenen Runtime-Ordner und
Port `8766`. Port `8765` bleibt unangetastet.

## Voraussetzungen

- Windows PowerShell ist verfuegbar.
- Der Worktree `C:\morphic_v1\.worktrees\operator-workbench-phase1` existiert.
- Die Projektumgebung `C:\morphic_v1\.venv` ist installiert.
- Fuer Server und Browser werden zwei PowerShell-Fenster verwendet.

## 1. Server in PowerShell 1 starten

### 1.1 In den richtigen Worktree wechseln

```powershell
Set-Location "C:\morphic_v1\.worktrees\operator-workbench-phase1"
```

### 1.2 Branch kontrollieren

```powershell
git branch --show-current
```

Erwartete Ausgabe:

```text
operator-workbench-phase1
```

Bei einer anderen Ausgabe nicht fortfahren.

### 1.3 Isolierten Runtime-Ordner anlegen

```powershell
$runtime = Join-Path $env:TEMP ("morphic-task5-manual-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
New-Item -ItemType Directory -Path $runtime | Out-Null
$runtime
```

Die letzte Zeile zeigt den fuer diesen Test verwendeten Runtime-Ordner an.
Den Ordner bis zum Abschluss der Abnahme nicht loeschen.

### 1.4 Ressourcenlimits und Runtime setzen

```powershell
$env:MORPHIC_RUNTIME_DIR = $runtime
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"
```

Diese Limits vermeiden unnoetige parallele numerische Worker und reduzieren
die Speicherlast auf dem lokalen Rechner.

### 1.5 Port 8766 kontrollieren

```powershell
Get-NetTCPConnection -State Listen -LocalPort 8766 -ErrorAction SilentlyContinue
```

Erwartung: keine Ausgabe. Falls eine Verbindung angezeigt wird, den Server
nicht starten und den bereits laufenden Prozess nicht ungeprueft beenden.

### 1.6 Applikation im Vordergrund starten

```powershell
& "C:\morphic_v1\.venv\Scripts\python.exe" -X utf8 -m uvicorn apps.web.main:app --host 127.0.0.1 --port 8766
```

Erwartete Abschlussmeldungen:

```text
Application startup complete.
Uvicorn running on http://127.0.0.1:8766
```

PowerShell 1 geoeffnet lassen. Der Server laeuft im Vordergrund.

## 2. Anwendung in PowerShell 2 oeffnen

### 2.1 Healthcheck ausfuehren

```powershell
(Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8766/api/health" -TimeoutSec 10).StatusCode
```

Erwartete Ausgabe:

```text
200
```

### 2.2 Anwendung im Standardbrowser oeffnen

```powershell
Start-Process "http://127.0.0.1:8766/"
```

## 3. Task-5-Pruefpunkte

1. Die Operator Workbench wird ohne Startfehler geladen.
2. Beim Start eines Scans wird der Start-Button deaktiviert.
3. Solange der Scan aktiv oder sein Status ungeklaert ist, bleiben Refresh und
   der sichtbare Scan-Stop-Button verfuegbar.
4. Ein ungeklaerter Status darf Ergebnisse oder Laufspur nicht als terminal
   finalisieren.
5. Eine nicht bestaetigte Stop-Antwort oder ein Requestfehler darf die aktive
   Scan-Reservation nicht freigeben.
6. Erst ein terminal bestaetigter Status `stopped` gibt die Reservation frei,
   aktiviert den Start-Button und deaktiviert Refresh und Stop.
7. Ein terminal `completed` gemeldeter Scan laedt Ergebnisse, Laufspur und
   Berichtskatalog. Ein Authentifizierungsfehler im Nachlauf laesst einen
   erneuten Refresh zu, ohne den Scan wieder als aktiv zu markieren.

Die Statuswerte `authority_ambiguous`, `rollback_failed`, ein fehlender Status
oder ein unbekannter Status sind normalerweise nur ueber gezielte Testdaten
reproduzierbar. Falls einer davon im manuellen Lauf erscheint, darf kein neuer
Scan gestartet werden, bevor Refresh oder Stop einen terminalen Zustand
bestaetigt.

## 4. Testserver kontrolliert beenden

Nach Abschluss der manuellen Pruefung in PowerShell 1 `Strg+C` druecken.

Erwartete Abschlussmeldungen:

```text
Shutting down
Application shutdown complete.
```

Danach in PowerShell 2 kontrollieren, dass Port `8766` frei ist:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 8766 -ErrorAction SilentlyContinue
```

Erwartung: keine Ausgabe.

## 5. Verhalten bei Fehlern oder Abbruch

Den Server bei einem Fehler nicht mehrfach blind starten. Stattdessen folgende
Informationen sichern:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 8766 -ErrorAction SilentlyContinue
Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -match "uvicorn apps\.web\.main:app" -and
    $_.CommandLine -match "--port 8766"
} | Select-Object ProcessId, ParentProcessId, CommandLine
```

Ausserdem die vollstaendige Fehlermeldung aus PowerShell 1 und den zuletzt
sichtbaren Zustand in der Anwendung dokumentieren. Keine fremden Prozesse
beenden und den isolierten Runtime-Ordner bis zur Auswertung erhalten.
