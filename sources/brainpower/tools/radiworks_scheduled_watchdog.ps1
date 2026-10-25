$ErrorActionPreference = 'Stop'
$source = 'C:\Users\Hubert111\Documents\Radiworks\radiworks_port'
$launcherScript = Join-Path $PSScriptRoot 'radiworks_scheduled_launcher.pyw'
$pythonw = Join-Path $source 'engine\.venv\Scripts\pythonw.exe'
$logPath = Join-Path (Split-Path -Parent $PSScriptRoot) 'runtime\radiworks-watchdog.log'
$failed = $false

foreach ($port in 8103..8109) {
  $name = "RadiWorks-Local-$port"
  try {
    $task = Get-ScheduledTask -TaskName $name -ErrorAction Stop
    $arguments = "`"$launcherScript`" $port"
    if ($task.Actions.Count -ne 1 -or $task.Actions[0].Execute -ne $pythonw -or
        $task.Actions[0].Arguments -ne $arguments) {
      throw "Aufgabe $name hat eine andere Aktion; Start verweigert."
    }
    # A deliberate Disabled state is the maintenance switch; never undo it.
    if ($task.State -eq 'Ready') {
      Start-ScheduledTask -TaskName $name -ErrorAction Stop
      Add-Content -LiteralPath $logPath -Encoding UTF8 -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') restarted=$name"
    }
  } catch {
    $failed = $true
    Add-Content -LiteralPath $logPath -Encoding UTF8 -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') task=$name error=$($_.Exception.Message)"
  }
}
if ($failed) { exit 1 }
