param(
  [Parameter(Mandatory = $true)][ValidateSet('Start', 'Status', 'Stop')][string]$Action,
  [Parameter(Mandatory = $true)][ValidateSet(8104, 8105)][int]$Port
)

$ErrorActionPreference = 'Stop'
$workspace = 'C:\Users\Hubert111\Documents\Brainpower'
$source = 'C:\Users\Hubert111\Documents\Radiworks\radiworks_port'
$catalog = Join-Path $workspace 'runtime\radiworks-catalog-releases\e33ea136d8ea448fada7524757385ee4\data'
$runtime = Join-Path $workspace "runtime\radiworks-local-$Port"
$python = Join-Path $source 'engine\.venv\Scripts\python.exe'
$markerPath = Join-Path $runtime 'instance.json'
$url = "http://127.0.0.1:$Port"

function Test-PortOpen([int]$number) {
  $client = [System.Net.Sockets.TcpClient]::new()
  try {
    $attempt = $client.ConnectAsync('127.0.0.1', $number)
    return $attempt.Wait(800) -and $client.Connected
  } catch {
    return $false
  } finally {
    $client.Dispose()
  }
}

function Get-OwnedProcess {
  if (!(Test-Path -LiteralPath $markerPath)) { return $null }
  $marker = Get-Content -LiteralPath $markerPath -Raw | ConvertFrom-Json
  if ($marker.port -ne $Port -or $marker.runtime -ne $runtime -or $marker.source -ne $source) {
    throw "Instanzmarker passt nicht zu Port $Port."
  }
  $process = Get-Process -Id $marker.pid -ErrorAction SilentlyContinue
  if (!$process) { return $null }
  $recordedStart = ([datetime]$marker.startedUtc).ToUniversalTime()
  if ($process.StartTime.ToUniversalTime().Ticks -ne $recordedStart.Ticks) { return $null }
  return $process
}

function Get-Health {
  $ping = Invoke-RestMethod -Uri "$url/ping" -TimeoutSec 3
  if ($ping.result -ne 'pong' -or $ping.module -ne 'radiworks.engine') {
    throw "Port $Port antwortet nicht als RadiWorks."
  }
  return $ping
}

function Assert-OwnListener {
  $process = Get-OwnedProcess
  if (!$process) { throw "Port $Port ist belegt, aber nicht als diese Instanz nachgewiesen." }
  $null = Get-Health
  return $process
}

if ($Action -eq 'Status') {
  if (!(Test-PortOpen $Port)) {
    $process = Get-OwnedProcess
    if ($process) { throw "Instanzprozess $($process.Id) lebt, aber Port $Port antwortet nicht." }
    "port=$Port status=stopped runtime=$runtime"
    exit 0
  }
  $process = Assert-OwnListener
  $cases = Invoke-RestMethod -Uri "$url/cases" -TimeoutSec 3
  $entropy = Invoke-RestMethod -Uri "$url/entropy/status" -TimeoutSec 3
  "port=$Port status=running pid=$($process.Id) cases=$($cases.cases.Count) entropy_default=$($entropy.defaultMode) recovery_available=$($entropy.stochasticRecovery.available) runtime=$runtime"
  exit 0
}

if ($Action -eq 'Stop') {
  if (!(Test-PortOpen $Port)) {
    $process = Get-OwnedProcess
    if ($process) { throw "Instanzprozess $($process.Id) lebt, aber Port $Port antwortet nicht." }
    "port=$Port status=already_stopped"
    exit 0
  }
  $process = Assert-OwnListener
  $auto = Invoke-RestMethod -Uri "$url/auto-mode" -TimeoutSec 3
  $queue = Invoke-RestMethod -Uri "$url/broadcast/queue" -TimeoutSec 3
  if ($auto.enabled -or $queue.active.Count -gt 0 -or $queue.queued.Count -gt 0) {
    throw "Port $Port hat Auto-Modus oder Broadcast-Aufträge; Stop abgewiesen."
  }
  Stop-Process -Id $process.Id -ErrorAction Stop
  if (!$process.WaitForExit(10000)) { throw "Instanzprozess $($process.Id) endete nicht rechtzeitig." }
  $deadline = (Get-Date).AddSeconds(10)
  while ((Get-Date) -lt $deadline -and (Test-PortOpen $Port)) {
    Start-Sleep -Milliseconds 100
  }
  if (Test-PortOpen $Port) { throw "Port $Port antwortet nach Stop weiter; Zustand prüfen." }
  "port=$Port status=stopped"
  exit 0
}

foreach ($path in @($workspace, $source, $catalog, $python)) {
  if (!(Test-Path -LiteralPath $path)) { throw "Benötigter Pfad fehlt: $path" }
}
if (Test-PortOpen $Port) {
  $process = Assert-OwnListener
  "port=$Port status=already_running pid=$($process.Id) runtime=$runtime"
  exit 0
}
$oldProcess = Get-OwnedProcess
if ($oldProcess) { throw "Alter Instanzprozess $($oldProcess.Id) lebt noch ohne Port $Port." }

New-Item -ItemType Directory -Path $runtime -Force | Out-Null
$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$out = Join-Path $runtime "server-$stamp.out.log"
$err = Join-Path $runtime "server-$stamp.err.log"
$variables = @('RADIOWORKS_HOME', 'RADIOWORKS_DATA_DIR', 'RADIOWORKS_SCOPE_MODE',
  'RADIOWORKS_LOCAL_TENANT_ID', 'RADIOWORKS_LOCAL_CLIENT_ID', 'RADIOWORKS_LOCAL_JOB_ID',
  'RADIOWORKS_JOURNAL_KEY', 'PYTHONPATH')
$previous = @{}
foreach ($name in $variables) {
  $previous[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
}
try {
  $env:RADIOWORKS_HOME = $runtime
  $env:RADIOWORKS_DATA_DIR = $catalog
  $env:RADIOWORKS_SCOPE_MODE = 'local'
  $env:RADIOWORKS_LOCAL_TENANT_ID = 'preview'
  $env:RADIOWORKS_LOCAL_CLIENT_ID = "instance-$Port"
  $env:RADIOWORKS_LOCAL_JOB_ID = "local-$Port"
  $env:PYTHONPATH = Join-Path (Join-Path $source 'engine') 'src'
  Remove-Item Env:RADIOWORKS_JOURNAL_KEY -ErrorAction SilentlyContinue
  $child = Start-Process -FilePath $python -ArgumentList @('run.py', '--port', [string]$Port) `
    -WorkingDirectory (Join-Path $source 'engine') -RedirectStandardOutput $out `
    -RedirectStandardError $err -WindowStyle Hidden -PassThru
} finally {
  foreach ($name in $variables) {
    [Environment]::SetEnvironmentVariable($name, $previous[$name], 'Process')
  }
  $previous.Clear()
}

try {
  $deadline = (Get-Date).AddSeconds(30)
  $ready = $false
  while ((Get-Date) -lt $deadline) {
    Start-Sleep -Milliseconds 400
    if ($child.HasExited) { throw "RadiWorks $Port endete vor Bereitschaft; Fehlerprotokoll: $err" }
    try {
      $null = Get-Health
      $entropy = Invoke-RestMethod -Uri "$url/entropy/status" -TimeoutSec 2
      if ($entropy.defaultMode -eq 'seeded' -and !$entropy.stochasticRecovery.available) {
        $ready = $true
        break
      }
    } catch { }
  }
  if (!$ready) { throw "RadiWorks $Port wurde nicht bereit; Fehlerprotokoll: $err" }
  $manifest = Invoke-RestMethod -Uri "$url/manifest" -TimeoutSec 3
  $marker = [ordered]@{
    port = $Port
    pid = $child.Id
    startedUtc = $child.StartTime.ToUniversalTime().ToString('o')
    runtime = $runtime
    source = $source
    catalog = $catalog
    manifestHash = $manifest.hash
    mode = 'seeded'
  }
  $tmp = Join-Path $runtime 'instance.json.tmp'
  $marker | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $tmp -Encoding UTF8
  Move-Item -LiteralPath $tmp -Destination $markerPath -Force
  "port=$Port status=started pid=$($child.Id) runtime=$runtime manifest=$($manifest.hash)"
} catch {
  if ($child -and !$child.HasExited) { Stop-Process -Id $child.Id -ErrorAction SilentlyContinue }
  throw
}
