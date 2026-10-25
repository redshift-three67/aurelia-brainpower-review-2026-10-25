param([switch]$Disable)
$ErrorActionPreference = 'Stop'
$appRoot = Split-Path -Parent $PSScriptRoot
$taskName = 'GovernorWorkbench-Local'
if ($Disable) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Output 'Governor-Autostart entfernt. Laufender Dienst bleibt unberührt.'
    exit
}
$pythonPath = (Get-Content -LiteralPath (Join-Path $appRoot 'runtime-python.json') -Raw | ConvertFrom-Json).python
$pythonWindowless = Join-Path (Split-Path -Parent $pythonPath) 'pythonw.exe'
if (-not (Test-Path -LiteralPath $pythonWindowless)) { throw 'pythonw.exe fehlt; Python-Installation prüfen.' }
$action = New-ScheduledTaskAction -Execute $pythonWindowless -Argument ('-m governor_workbench serve --config "' + (Join-Path $appRoot 'config.local.json') + '"') -WorkingDirectory $appRoot
$trigger = New-ScheduledTaskTrigger -AtLogOn -User ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
$principal = New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description 'Lokale Governor-Projektbeobachtung; keine automatischen Produktänderungen.' -Force | Out-Null
Write-Output 'Governor startet künftig bei Anmeldung dieses Benutzers, ohne Administratorrechte.'
