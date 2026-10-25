$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $ProjectRoot = Split-Path -Parent (Split-Path -Parent $RepoRoot)
    $FallbackPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    if (Test-Path $FallbackPython) {
        $PythonExe = $FallbackPython
    } else {
        throw "Python-Umgebung nicht gefunden: $PythonExe oder $FallbackPython"
    }
}

$Port = 8000
$HostName = "127.0.0.1"

Write-Host "" 
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "Morphic Engine V1 - Apps/Web UI" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "  Frontend:   http://$HostName`:$Port/" -ForegroundColor Green
Write-Host "  API Health: http://$HostName`:$Port/api/health" -ForegroundColor Green
Write-Host "  Beenden: Ctrl+C" -ForegroundColor DarkGray
Write-Host ""

$existing = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -First 1
if ($existing) {
    Write-Host "Port $Port ist bereits belegt - bestehender Prozess wird beendet..." -ForegroundColor Yellow
    Stop-Process -Id $existing.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

Start-Process "http://$HostName`:$Port/"

& $PythonExe -m uvicorn apps.web.main:app --host $HostName --port $Port
