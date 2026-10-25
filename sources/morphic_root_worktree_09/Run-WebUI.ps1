param(
    [switch]$OpenAdmin,
    [int]$Port = 8000,
    [string]$RuntimeRoot = "",
    [switch]$IsolatedAcceptance,
    [switch]$NoBrowser,
    [switch]$ExitAfterHealth
)

$ErrorActionPreference = "Stop"

function New-MorphicAdminBootstrapNonce {
    $Bytes = [byte[]]::new(48)
    $Generator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $Generator.GetBytes($Bytes)
    } finally {
        $Generator.Dispose()
    }
    return [Convert]::ToBase64String($Bytes).TrimEnd("=").Replace("+", "-").Replace("/", "_")
}

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

$HostName = "127.0.0.1"
$AdminExpectedOrigin = "http://$HostName`:$Port"
$AdminExpectedHost = "$HostName`:$Port"
$AdminBootstrapNonce = New-MorphicAdminBootstrapNonce
$env:MORPHIC_ADMIN_EXPECTED_ORIGIN = $AdminExpectedOrigin
$env:MORPHIC_ADMIN_EXPECTED_HOST = $AdminExpectedHost
$env:MORPHIC_ADMIN_BOOTSTRAP_NONCE = $AdminBootstrapNonce
$env:MORPHIC_ADMIN_BOOTSTRAP_CREATED_AT_UTC = (Get-Date).ToUniversalTime().ToString("o")
$LaunchUrl = "$AdminExpectedOrigin/"
$HealthUrl = "$AdminExpectedOrigin/api/health"
if ($OpenAdmin) {
    $LaunchUrl = "$AdminExpectedOrigin/static/admin.html#admin_nonce=$AdminBootstrapNonce"
}

if ($IsolatedAcceptance) {
    if ([string]::IsNullOrWhiteSpace($RuntimeRoot)) {
        $RuntimeRoot = Join-Path $env:TEMP ("morphic-webui-acceptance-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
    }
    $RuntimeRoot = [System.IO.Path]::GetFullPath($RuntimeRoot)
    New-Item -ItemType Directory -Path $RuntimeRoot -Force | Out-Null

    $env:MORPHIC_BROWSER_PORT = [string]$Port
    $env:MORPHIC_BROWSER_RUNTIME_ROOT = $RuntimeRoot
    $env:MORPHIC_BROWSER_HEALTH_TOKEN = [guid]::NewGuid().ToString("N")
    $env:MORPHIC_RUNTIME_DIR = Join-Path $RuntimeRoot "runtime"
    $env:MORPHIC_HARMONIZATION_JOBS_DIR = Join-Path $RuntimeRoot "harmonization-jobs"
    $env:MORPHIC_PARALLEL_EXPORT_ROOT = Join-Path $RuntimeRoot "exports"
    $env:MORPHIC_OPERATOR_ID = "webui-acceptance-operator"
    $env:MORPHIC_TENANT_ID = "webui-acceptance-$PID"
    $env:MORPHIC_GROUP_ANALYSIS_ENABLED = "0"
    $env:MORPHIC_ADMIN_CATALOG_ENABLED = "0"
    $env:OPENBLAS_NUM_THREADS = "1"
    $env:OMP_NUM_THREADS = "1"
    $env:MKL_NUM_THREADS = "1"
    $env:NUMEXPR_NUM_THREADS = "1"
    $env:PYTHONUTF8 = "1"
    $env:PYTHONIOENCODING = "utf-8"
}

Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "Morphic Engine V1 - Apps/Web UI" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "  Frontend:   $AdminExpectedOrigin/" -ForegroundColor Green
Write-Host "  API Health: $AdminExpectedOrigin/api/health" -ForegroundColor Green
if ($IsolatedAcceptance) {
    Write-Host "  Runtime:    $RuntimeRoot" -ForegroundColor Green
    Write-Host "  Beenden:   Enter in diesem Fenster" -ForegroundColor DarkGray
} else {
    Write-Host "  Beenden: Ctrl+C" -ForegroundColor DarkGray
}
Write-Host ""

$existing = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($existing) {
    throw "Port $Port ist bereits belegt (PID $($existing.OwningProcess)). Bestehenden Prozess nicht automatisch beendet. Bitte den Listener prüfen oder einen freien Port verwenden."
}

if ($IsolatedAcceptance) {
    $StdoutLog = Join-Path $RuntimeRoot "server.stdout.log"
    $StderrLog = Join-Path $RuntimeRoot "server.stderr.log"
    $ServerArgs = @("-X", "utf8", "tests\browser\isolated_server.py")
    $ServerProcess = Start-Process -FilePath $PythonExe -ArgumentList $ServerArgs -WorkingDirectory $RepoRoot -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog -PassThru
    $PortOwnerPid = $null
    try {
        $Deadline = (Get-Date).AddSeconds(60)
        $HealthReady = $false
        while ((Get-Date) -lt $Deadline) {
            $ServerProcess.Refresh()
            if ($ServerProcess.HasExited) {
                throw "QA-Server wurde vor Health beendet (ExitCode $($ServerProcess.ExitCode)). Logs: $StdoutLog / $StderrLog"
            }
            try {
                $response = Invoke-WebRequest -UseBasicParsing -Uri $HealthUrl -TimeoutSec 2
                if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                    $HealthReady = $true
                    break
                }
            } catch {
            }
            Start-Sleep -Milliseconds 500
        }
        if (-not $HealthReady) {
            throw "QA-Server wurde auf $HealthUrl nicht innerhalb von 60 Sekunden gesund. Logs: $StdoutLog / $StderrLog"
        }

        $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $listener) {
            throw "QA Health war OK, aber der Port-Owner fuer $Port konnte nicht gelesen werden."
        }
        $PortOwnerPid = [int]$listener.OwningProcess
        Write-Host "QA Health: OK ($HealthUrl)" -ForegroundColor Green
        Write-Host "Launcher-PID: $($ServerProcess.Id)" -ForegroundColor Green
        Write-Host "Port-Owner-PID: $PortOwnerPid" -ForegroundColor Green
        Write-Host "Logs: $StdoutLog / $StderrLog" -ForegroundColor DarkGray
        if (-not $NoBrowser) {
            Start-Process $LaunchUrl
        }
        if ($ExitAfterHealth) {
            Write-Host "ExitAfterHealth aktiv: QA-Server wird wieder beendet." -ForegroundColor DarkGray
        } else {
            [void](Read-Host "Enter druecken, um den isolierten QA-Server zu beenden")
        }
    } finally {
        if ($PortOwnerPid) {
            $CurrentListener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($CurrentListener -and [int]$CurrentListener.OwningProcess -eq $PortOwnerPid) {
                Stop-Process -Id $PortOwnerPid -Force -ErrorAction SilentlyContinue
            }
        }
        $ServerProcess.Refresh()
        if (-not $ServerProcess.HasExited) {
            Stop-Process -Id $ServerProcess.Id -Force -ErrorAction SilentlyContinue
        }
        for ($attempt = 0; $attempt -lt 20; $attempt++) {
            $remaining = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
            if (-not $remaining) {
                Write-Host "Port $Port ist frei." -ForegroundColor Green
                break
            }
            Start-Sleep -Milliseconds 250
        }
    }
    exit
}

Start-Job -Name "MorphicWebUILaunchBrowser" -ScriptBlock {
    param(
        [string]$LaunchUrl,
        [string]$HealthUrl,
        [bool]$NoBrowser
    )

    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri $HealthUrl -TimeoutSec 2
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                if (-not $NoBrowser) {
                    Start-Process $LaunchUrl
                }
                return
            }
        } catch {
        }
        Start-Sleep -Milliseconds 500
    }
} -ArgumentList $LaunchUrl, $HealthUrl, $NoBrowser | Out-Null

& $PythonExe -m uvicorn apps.web.main:app --host $HostName --port $Port
