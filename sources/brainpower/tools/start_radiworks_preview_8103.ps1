$ErrorActionPreference = 'Stop'

$url = 'http://127.0.0.1:8103'
$workspace = 'C:\Users\Hubert111\Documents\Brainpower'
$runtime = Join-Path $workspace 'runtime\radiworks-preview-8103'
$source = 'C:\Users\Hubert111\Documents\Radiworks\radiworks_port'
$catalog = Join-Path $workspace 'runtime\radiworks-catalog-releases\e33ea136d8ea448fada7524757385ee4\data'
$python = Join-Path $source 'engine\.venv\Scripts\python.exe'
$keyPath = 'E:\Aurelia-Recovery\RadiWorks\stochastic-journal-8103.key'

try {
  $ping = Invoke-RestMethod -Uri "$url/ping" -TimeoutSec 3
  if ($ping.result -eq 'pong') {
    $entropy = Invoke-RestMethod -Uri "$url/entropy/status" -TimeoutSec 3
    if (!$entropy.stochasticRecovery.available) {
      throw '8103 is running without the external journal key; refusing a second instance.'
    }
    'radiworks_8103_already_running=true stochastic_recovery_available=true'
    exit 0
  }
} catch {
  if ($_.Exception.Message -match 'running without the external journal key') { throw }
}

foreach ($path in @($runtime, $source, $catalog, $python, $keyPath)) {
  if (!(Test-Path -LiteralPath $path)) { throw "Required path missing: $path" }
}

$key = (Get-Content -LiteralPath $keyPath -Raw -ErrorAction Stop).Trim()
if ($key.Length -ne 44) { throw 'External Fernet key has unexpected length.' }
try {
  $env:RADIOWORKS_HOME = $runtime
  $env:RADIOWORKS_DATA_DIR = $catalog
  $env:RADIOWORKS_SCOPE_MODE = 'local'
  $env:RADIOWORKS_LOCAL_TENANT_ID = 'preview'
  $env:RADIOWORKS_LOCAL_CLIENT_ID = 'candidate'
  $env:RADIOWORKS_LOCAL_JOB_ID = 'test-8103'
  $env:PYTHONPATH = Join-Path (Join-Path $source 'engine') 'src'
  $env:RADIOWORKS_JOURNAL_KEY = $key
  $key = $null

  $out = Join-Path $runtime 'server.external-key.out.log'
  $err = Join-Path $runtime 'server.external-key.err.log'
  $child = Start-Process -FilePath $python -ArgumentList @('run.py', '--port', '8103') `
    -WorkingDirectory (Join-Path $source 'engine') -RedirectStandardOutput $out -RedirectStandardError $err `
    -WindowStyle Hidden -PassThru
  $deadline = (Get-Date).AddSeconds(30)
  while ((Get-Date) -lt $deadline) {
    Start-Sleep -Milliseconds 500
    if ($child.HasExited) { throw "RadiWorks exited before readiness; inspect $err" }
    try {
      $ping = Invoke-RestMethod -Uri "$url/ping" -TimeoutSec 2
      $entropy = Invoke-RestMethod -Uri "$url/entropy/status" -TimeoutSec 2
      if ($ping.result -eq 'pong' -and $entropy.stochasticRecovery.available) {
        "radiworks_8103_started=true stochastic_recovery_available=true pid=$($child.Id)"
        exit 0
      }
    } catch { }
  }
  throw "RadiWorks did not become ready; inspect $err"
} finally {
  $key = $null
  Remove-Item Env:RADIOWORKS_JOURNAL_KEY -ErrorAction SilentlyContinue
}
