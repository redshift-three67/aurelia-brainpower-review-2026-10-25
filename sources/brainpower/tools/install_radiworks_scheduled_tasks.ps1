$ErrorActionPreference = 'Stop'
$source = 'C:\Users\Hubert111\Documents\Radiworks\radiworks_port'
$launcherScript = Join-Path $PSScriptRoot 'radiworks_scheduled_launcher.pyw'
$hostScript = Join-Path $PSScriptRoot 'radiworks_scheduled_host.ps1'
$watchdogScript = Join-Path $PSScriptRoot 'radiworks_scheduled_watchdog.ps1'
$pythonw = Join-Path $source 'engine\.venv\Scripts\pythonw.exe'
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

foreach ($path in @($launcherScript, $hostScript, $watchdogScript, $pythonw)) {
  if (!(Test-Path -LiteralPath $path)) { throw "Benötigter Pfad fehlt: $path" }
}

foreach ($port in 8103..8109) {
  $name = "RadiWorks-Local-$port"
  $arguments = "`"$launcherScript`" $port"
  $existing = Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue
  if ($existing) {
    if ($existing.Actions.Count -ne 1 -or
        $existing.Actions[0].Execute -ne $pythonw -or
        $existing.Actions[0].Arguments -ne $arguments) {
      throw "Aufgabe $name besteht bereits mit anderer Aktion; nicht überschrieben."
    }
  } else {
    $action = New-ScheduledTaskAction -Execute $pythonw -Argument $arguments
    $trigger = New-ScheduledTaskTrigger -AtLogOn -User $user
    $principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
    $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) `
      -MultipleInstances IgnoreNew -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) `
      -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger `
      -Principal $principal -Settings $settings `
      -Description "RadiWorks $port unabhängig von Codex; nutzt den vorhandenen Laufzeitordner und wartet bei belegtem Port." | Out-Null
  }
  $task = Get-ScheduledTask -TaskName $name -ErrorAction Stop
  if ($task.State -ne 'Running') { Start-ScheduledTask -TaskName $name -ErrorAction Stop }
  "task=$name state=$((Get-ScheduledTask -TaskName $name).State) user=$user"
}

$watchdogScript = Join-Path $PSScriptRoot 'radiworks_scheduled_watchdog.ps1'
if (!(Test-Path -LiteralPath $watchdogScript)) { throw 'Kontrollskript fehlt.' }
$name = 'RadiWorks-Local-Watchdog'
$arguments = "`"$launcherScript`" --watchdog"
$existing = Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue
if ($existing) {
  if ($existing.Actions.Count -ne 1 -or $existing.Actions[0].Execute -ne $pythonw -or
      $existing.Actions[0].Arguments -ne $arguments) {
    throw "Aufgabe $name besteht bereits mit anderer Aktion; nicht überschrieben."
  }
} else {
  $action = New-ScheduledTaskAction -Execute $pythonw -Argument $arguments
  $triggers = @(
    (New-ScheduledTaskTrigger -AtLogOn -User $user),
    (New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 1))
  )
  $principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
  $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 1) `
    -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
  Register-ScheduledTask -TaskName $name -Action $action -Trigger $triggers -Principal $principal `
    -Settings $settings -Description 'Prüft jede Minute die sieben RadiWorks-Hosts; startet nur bekannte beendete Aufgaben, erhält deaktivierte Aufgaben.' | Out-Null
}
Start-ScheduledTask -TaskName $name -ErrorAction Stop
"task=$name installed=true interval_minutes=1 user=$user"
