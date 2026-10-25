param(
  [Parameter(Mandatory = $true)][ValidateRange(8103, 8109)][int]$Port
)

$ErrorActionPreference = 'Stop'
$workspace = 'C:\Users\Hubert111\Documents\Brainpower'
$source = 'C:\Users\Hubert111\Documents\Brainpower\runtime\rw-r6-release-20261008'
$legacySource = 'C:\Users\Hubert111\Documents\Radiworks\radiworks_port'
$configPath = Join-Path $workspace "runtime\rw-r6-rollout-20261008\instance-$Port.json"
$catalog = Join-Path $workspace 'runtime\radiworks-catalog-releases\e33ea136d8ea448fada7524757385ee4\data'
$runtime = if ($Port -eq 8103) {
  Join-Path $workspace 'runtime\radiworks-preview-8103'
} else {
  Join-Path $workspace "runtime\radiworks-local-$Port"
}
$python = Join-Path $legacySource 'engine\.venv\Scripts\python.exe'
$keyPath = 'E:\Aurelia-Recovery\RadiWorks\stochastic-journal-8103.key'
$markerPath = Join-Path $runtime 'instance.json'
$logPath = Join-Path $runtime 'scheduled-host.log'
$url = "http://127.0.0.1:$Port"

New-Item -ItemType Directory -Path $runtime -Force | Out-Null

function Write-HostEvent([string]$message) {
  $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') port=$Port $message"
  Add-Content -LiteralPath $logPath -Value $line -Encoding UTF8
  Write-Output $line
}

function Test-PortOpen {
  $client = [System.Net.Sockets.TcpClient]::new()
  try {
    $attempt = $client.ConnectAsync('127.0.0.1', $Port)
    return $attempt.Wait(500) -and $client.Connected
  } catch {
    return $false
  } finally {
    $client.Dispose()
  }
}

function Test-RadiWorksReady {
  try {
    $ping = Invoke-RestMethod -Uri "$url/ping" -TimeoutSec 2
    if ($ping.result -ne 'pong' -or $ping.module -ne 'radiworks.engine') { return $false }
    $entropy = Invoke-RestMethod -Uri "$url/entropy/status" -TimeoutSec 2
    if ($Port -eq 8103) { return [bool]$entropy.stochasticRecovery.available }
    return ($entropy.defaultMode -eq 'seeded' -and !$entropy.stochasticRecovery.available)
  } catch {
    return $false
  }
}

function Test-OldOwnedProcess {
  if ($Port -eq 8103 -or !(Test-Path -LiteralPath $markerPath)) { return $false }
  $marker = Get-Content -LiteralPath $markerPath -Raw | ConvertFrom-Json
  if ($marker.port -ne $Port -or $marker.runtime -ne $runtime -or ($marker.source -ne $source -and $marker.source -ne $legacySource -and $marker.source -ne 'C:\Users\Hubert111\Documents\Brainpower\runtime\rw-c23-fixed-release-20261005')) {
    throw 'Instanzmarker passt nicht zum geplanten Port und Laufzeitordner.'
  }
  $process = Get-Process -Id $marker.pid -ErrorAction SilentlyContinue
  if (!$process) { return $false }
  $recordedStart = ([datetime]$marker.startedUtc).ToUniversalTime()
  return ($process.StartTime.ToUniversalTime().Ticks -eq $recordedStart.Ticks)
}

function Start-OwnedEngine {
  foreach ($path in @($source, $catalog, $python, $configPath)) {
    if (!(Test-Path -LiteralPath $path)) { throw "Benötigter Pfad fehlt: $path" }
  }
  $key = $null
  if ($Port -eq 8103) {
    if (!(Test-Path -LiteralPath $keyPath)) { throw 'Externer 8103-Wiederherstellungsschlüssel fehlt.' }
    $key = (Get-Content -LiteralPath $keyPath -Raw).Trim()
    if ($key.Length -ne 44) { throw 'Externer 8103-Wiederherstellungsschlüssel hat unerwartete Länge.' }
  }

  $names = @('RADIOWORKS_HOME', 'RADIOWORKS_DATA_DIR', 'RADIOWORKS_SCOPE_MODE',
    'RADIOWORKS_LOCAL_TENANT_ID', 'RADIOWORKS_LOCAL_CLIENT_ID', 'RADIOWORKS_LOCAL_JOB_ID',
    'RADIOWORKS_JOURNAL_KEY', 'PYTHONPATH')
  $previous = @{}
  foreach ($name in $names) {
    $previous[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
  }
  $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
  $out = Join-Path $runtime "scheduled-$stamp.out.log"
  $err = Join-Path $runtime "scheduled-$stamp.err.log"
  try {
    $env:RADIOWORKS_HOME = $runtime
    $env:RADIOWORKS_DATA_DIR = $catalog
    $env:RADIOWORKS_SCOPE_MODE = 'local'
    $env:RADIOWORKS_LOCAL_TENANT_ID = 'preview'
    $env:RADIOWORKS_LOCAL_CLIENT_ID = if ($Port -eq 8103) { 'candidate' } else { "instance-$Port" }
    $env:RADIOWORKS_LOCAL_JOB_ID = if ($Port -eq 8103) { 'test-8103' } else { "local-$Port" }
    $env:PYTHONPATH = Join-Path (Join-Path $source 'engine') 'src'
    if ($Port -eq 8103) { $env:RADIOWORKS_JOURNAL_KEY = $key }
    else { Remove-Item Env:RADIOWORKS_JOURNAL_KEY -ErrorAction SilentlyContinue }
    $child = Start-Process -FilePath $python -ArgumentList @('service.py', '--config', ('"' + $configPath + '"')) `
      -WorkingDirectory $source -RedirectStandardOutput $out `
      -RedirectStandardError $err -WindowStyle Hidden -PassThru
  } finally {
    $key = $null
    foreach ($name in $names) {
      [Environment]::SetEnvironmentVariable($name, $previous[$name], 'Process')
    }
    $previous.Clear()
  }

  $deadline = (Get-Date).AddSeconds(30)
  while ((Get-Date) -lt $deadline -and !$child.HasExited) {
    Start-Sleep -Milliseconds 500
    if (Test-RadiWorksReady) { break }
  }
  if (!(Test-RadiWorksReady)) {
    Write-HostEvent "engine_not_ready pid=$($child.Id) error_log=$err; no duplicate start while process lives"
    $child.WaitForExit()
    return
  }

  if ($Port -ne 8103) {
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
  }
  Write-HostEvent "engine_started pid=$($child.Id)"
  $child.WaitForExit()
  Write-HostEvent "engine_exited pid=$($child.Id) exit_code=$($child.ExitCode)"
}

Write-HostEvent 'host_started; waiting for an occupied port without stopping its process'
$occupiedState = ''
while ($true) {
  try {
    if (Test-PortOpen) {
      $state = if (Test-RadiWorksReady) { 'radiworks_ready' } else { 'occupied_or_unresponsive' }
      if ($state -ne $occupiedState) { Write-HostEvent $state }
      $occupiedState = $state
      Start-Sleep -Seconds 10
      continue
    }
    if ($occupiedState -ne 'port_free') { Write-HostEvent 'port_free' }
    $occupiedState = 'port_free'
    if (Test-OldOwnedProcess) {
      Write-HostEvent 'old_owned_process_alive_without_port; refusing duplicate runtime'
      Start-Sleep -Seconds 10
      continue
    }
    Start-OwnedEngine
  } catch {
    Write-HostEvent "start_deferred: $($_.Exception.Message)"
  }
  Start-Sleep -Seconds 30
}

