# Auto-Update PROJECT_MEMORY nach Git-Änderungen
# Installiere mit: git config core.hooksPath .git/hooks

param(
    [string]$Phase = "3",
    [string]$Progress = "36%",
    [string]$Status = "3 Funktionen migriert"
)

$memoryDir = "PROJECT_MEMORY"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$gitHash = git rev-parse --short HEAD
$gitBranch = git rev-parse --abbrev-ref HEAD
$gitMsg = git log -1 --pretty=%B

# Snapshot JSON erstellen
$snapshotDir = "$memoryDir/snapshots"
$snapshotFile = "$snapshotDir/snapshot_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

if (-not (Test-Path $snapshotDir)) {
    New-Item -ItemType Directory -Path $snapshotDir -Force | Out-Null
}

$snapshot = @{
    timestamp = $timestamp
    commit_hash = $gitHash
    commit_message = $gitMsg.Trim()
    branch = $gitBranch
    phase = "Phase $Phase - main.py Refactoring"
    progress = $Progress
    status = $Status
} | ConvertTo-Json

$snapshot | Set-Content $snapshotFile -Encoding UTF8 -Force

# Session-Log (JSONL für Streaming)
$sessionLog = "$memoryDir/snapshots/session_log.jsonl"
$logEntry = $snapshot
Add-Content $sessionLog $logEntry -Encoding UTF8 -Force

Write-Host "[✓] Memory Updated: $snapshotFile" -ForegroundColor Green
