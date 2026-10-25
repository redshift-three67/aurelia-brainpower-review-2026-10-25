param([string]$PythonExe)
$ErrorActionPreference = 'Stop'
$appRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $appRoot
if (-not $PythonExe) {
    $PythonExe = & py -3.12 -c 'import sys; print(sys.executable)' 2>$null
    if (-not $PythonExe) { $PythonExe = & py -3.13 -c 'import sys; print(sys.executable)' 2>$null }
}
if (-not $PythonExe -or -not (Test-Path -LiteralPath $PythonExe)) { throw 'Python 3.11+ installieren oder -PythonExe mit vollständigem Pfad angeben.' }
& $PythonExe -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)'
if ($LASTEXITCODE -ne 0) { throw 'Python 3.11 oder neuer erforderlich.' }
@{python=$PythonExe} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $appRoot 'runtime-python.json') -Encoding utf8
& $PythonExe -m governor_workbench init --config (Join-Path $appRoot 'config.local.json') --template (Join-Path $appRoot 'config.example.json')
if ($LASTEXITCODE -ne 0) { throw 'Konfigurationsinitialisierung fehlgeschlagen.' }
& $PythonExe -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'Installationstests fehlgeschlagen.' }
Write-Output 'Governor installiert. Keine zusätzlichen Python-Pakete, Node-Installation oder Docker erforderlich.'
Write-Output 'Jetzt config.local.json an die Projektpfade dieses PCs anpassen und doctor ausführen.'
