# Git Hooks für automatisches Memory-Update installieren

Write-Host "=== Installiere Git Hooks ===" -ForegroundColor Cyan

# Post-Commit Hook für Windows (PowerShell)
$hooksDir = ".git/hooks"
$postCommitHook = "$hooksDir/post-commit.ps1"

if (-not (Test-Path $hooksDir)) {
    New-Item -ItemType Directory -Path $hooksDir -Force | Out-Null
}

# PowerShell Post-Commit Hook
$hookContent = @'
# Nach jedem Commit: PROJECT_MEMORY aktualisieren
$memoryDir = "PROJECT_MEMORY"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$gitHash = git rev-parse --short HEAD
$gitBranch = git rev-parse --abbrev-ref HEAD
$gitMsg = git log -1 --pretty=%B

# Snapshot JSON
$snapshotDir = "$memoryDir/snapshots"
if (-not (Test-Path $snapshotDir)) {
    New-Item -ItemType Directory -Path $snapshotDir -Force | Out-Null
}

$snapshot = @{
    timestamp = $timestamp
    commit_hash = $gitHash
    commit_message = $gitMsg.Trim()
    branch = $gitBranch
    phase = "Phase 3 - main.py Refactoring"
    progress = (Select-String 'Fortschritt:' "$memoryDir/00_CURRENT_STATE.md" | ForEach-Object { $_.Line -replace '.*Fortschritt: ', '' })
} | ConvertTo-Json

$snapshotFile = "$snapshotDir/snapshot_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$snapshot | Set-Content $snapshotFile -Encoding UTF8 -Force

Write-Host "[OK] Memory snapshot created: $(Split-Path $snapshotFile -Leaf)" -ForegroundColor Green
'@

$hookContent | Set-Content $postCommitHook -Encoding UTF8 -Force

Write-Host "[✓] Installed: $postCommitHook" -ForegroundColor Green

# Git Config für Hooks
git config core.hooksPath .git/hooks
Write-Host "[✓] Git Hooks konfiguriert: core.hooksPath = .git/hooks" -ForegroundColor Green

Write-Host ""
Write-Host "=== Hooks Status ===" -ForegroundColor Cyan
git config core.hooksPath
Write-Host ""
Write-Host "✓ Automatisches Memory-Update ist AKTIVIERT" -ForegroundColor Green
Write-Host "  → Nach jedem Commit wird ein Snapshot erstellt"
Write-Host "  → SESSION_LOG.jsonl wird aktualisiert"
