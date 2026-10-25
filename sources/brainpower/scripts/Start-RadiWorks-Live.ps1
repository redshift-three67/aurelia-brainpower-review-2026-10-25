param()

$ErrorActionPreference = 'Stop'
$workspace = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$homePath = Join-Path $workspace 'runtime/radiworks-live-8102'
$catalogPath = Join-Path $workspace 'runtime/radiworks-catalog-releases/3c052ad0e9c0417e8aa1c29515fbba4e/data'
$enginePath = Join-Path $env:USERPROFILE 'Documents/Radiworks/radiworks_port/engine'
$pythonPath = Join-Path $enginePath '.venv/Scripts/python.exe'
$runPath = Join-Path $enginePath 'run.py'
$url = 'http://127.0.0.1:8102/'

foreach ($path in @($catalogPath, $pythonPath, $runPath)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "RadiWorks-Startvoraussetzung fehlt: $path"
    }
}

$listener = @(Get-NetTCPConnection -LocalPort 8102 -State Listen -ErrorAction SilentlyContinue)
if ($listener.Count -gt 0) {
    $owners = @($listener | Select-Object -ExpandProperty OwningProcess -Unique)
    if ($owners.Count -ne 1) { throw 'Port 8102 hat mehr als einen Besitzer.' }
    $ownerProcess = Get-CimInstance Win32_Process -Filter "ProcessId=$($owners[0])"
    if ($ownerProcess.CommandLine -notlike '*Radiworks*radiworks_port*engine*run.py --port 8102*') {
        throw "Port 8102 ist bereits von einem anderen Prozess belegt (PID $($owners[0]))."
    }
    $reply = Invoke-RestMethod -Uri ($url + 'ping') -TimeoutSec 5
    if ($reply.result -ne 'pong' -or $reply.module -ne 'radiworks.engine') {
        throw 'Auf Port 8102 antwortet kein erwarteter RadiWorks-Dienst.'
    }
    Write-Output "RadiWorks aktiv: $url"
    return
}

New-Item -ItemType Directory -Path $homePath -Force | Out-Null
$env:RADIOWORKS_HOME = $homePath
$env:RADIOWORKS_DATA_DIR = $catalogPath
$process = Start-Process -FilePath $pythonPath -ArgumentList @($runPath, '--port', '8102') `
    -WorkingDirectory $enginePath -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $homePath 'server.out.log') `
    -RedirectStandardError (Join-Path $homePath 'server.err.log') -PassThru

for ($attempt = 0; $attempt -lt 30; $attempt++) {
    Start-Sleep -Milliseconds 500
    try {
        $reply = Invoke-RestMethod -Uri ($url + 'ping') -TimeoutSec 2
        $databases = Invoke-RestMethod -Uri ($url + 'databases') -TimeoutSec 2
        if ($reply.result -eq 'pong' -and $reply.module -eq 'radiworks.engine' -and
            @($databases.databases).Count -eq 76) {
            Write-Output "RadiWorks bereit: $url (76 Datenbanken; Start-PID $($process.Id))"
            return
        }
    } catch {
        # Während des Starts ist die API noch nicht erreichbar.
    }
}
throw "RadiWorks wurde nicht bereit. Diagnose: $(Join-Path $homePath 'server.err.log')"
