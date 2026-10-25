param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$appRoot = Split-Path -Parent $PSScriptRoot
$configPath = Join-Path $appRoot 'config.local.json'
if (-not (Test-Path -LiteralPath $configPath)) { throw 'Bitte zuerst Install-Windows.ps1 ausführen.' }
$runtimePath = Join-Path $appRoot 'runtime-python.json'
if (-not (Test-Path -LiteralPath $runtimePath)) { throw 'Python-Installation fehlt. Install-Windows.ps1 erneut ausführen.' }
$pythonPath = (Get-Content -LiteralPath $runtimePath -Raw | ConvertFrom-Json).python
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Gespeicherter Python-Pfad fehlt.' }
$config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
$url = 'http://127.0.0.1:' + $config.port
$running = $false
try {
    $health = Invoke-RestMethod -Uri ($url + '/health') -TimeoutSec 2
    if ($health.service -eq 'governor-workbench') { $running = $true }
} catch { }
if ($health -and $health.service -ne 'governor-workbench') { throw 'Port durch fremden Dienst belegt. Governor-Port ändern.' }
if (-not $running) {
    $logDir = Join-Path $appRoot 'runtime'
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    Start-Process -FilePath $pythonPath -ArgumentList @('-m','governor_workbench','serve','--config',('"' + $configPath + '"')) -WorkingDirectory $appRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDir 'service.stdout.log') -RedirectStandardError (Join-Path $logDir 'service.stderr.log') | Out-Null
    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        Start-Sleep -Milliseconds 300
        try { $health = Invoke-RestMethod -Uri ($url + '/health') -TimeoutSec 1; if ($health.service -eq 'governor-workbench') { $ready = $true; break } } catch { }
    }
    if (-not $ready) { throw ('Dienststart fehlgeschlagen. Siehe ' + (Join-Path $logDir 'service.stderr.log')) }
}
if (-not $NoBrowser) { Start-Process $url }
Write-Output ('Governor läuft: ' + $url)
