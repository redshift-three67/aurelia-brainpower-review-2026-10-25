$ErrorActionPreference = 'Stop'
$appRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $appRoot
$pythonPath = (Get-Content -LiteralPath (Join-Path $appRoot 'runtime-python.json') -Raw | ConvertFrom-Json).python
& $pythonPath -m governor_workbench stop --config (Join-Path $appRoot 'config.local.json')
if ($LASTEXITCODE -ne 0) { throw 'Governor konnte nicht regulär beendet werden.' }
