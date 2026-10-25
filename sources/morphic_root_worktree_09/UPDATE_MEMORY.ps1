# UPDATE_MEMORY.ps1
# Automatisiert Project Memory Updates nach wichtigen Änderungen

param(
    [Parameter(Mandatory=$true)]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [string]$Details = "",
    
    [Parameter(Mandatory=$false)]
    [string]$Phase = "2"
)

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
$timestampFile = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "UPDATE PROJECT MEMORY" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Action: $Action" -ForegroundColor Yellow
Write-Host "Phase: $Phase" -ForegroundColor Yellow
Write-Host "Timestamp: $timestamp" -ForegroundColor White
Write-Host ""

# ============================================================================
# 1. Update 00_CURRENT_STATE.md
# ============================================================================

Write-Host "[1/4] Updating 00_CURRENT_STATE.md..." -ForegroundColor Green

$currentStatePath = "PROJECT_MEMORY/00_CURRENT_STATE.md"
$currentState = Get-Content $currentStatePath -Raw

# Update "Letztes Update" timestamp
$currentState = $currentState -replace "(\*\*Letztes Update:\*\*) .+", "`$1 $timestamp UTC+1"

# Update "Letzte 10 Aktionen" (add new action to top)
$newAction = "10. **$timestamp** - $Action"
if ($currentState -match "## LETZTE 10 AKTIONEN \(CHRONOLOGISCH\)(.+?)---" -and $matches[1]) {
    $actionsSection = $matches[1]
    $actions = $actionsSection -split "`n" | Where-Object { $_ -match "^\d+\." } | Select-Object -First 9
    
    $newActionsSection = @"


$newAction
$($actions -join "`n")

---
"@
    
    $currentState = $currentState -replace "## LETZTE 10 AKTIONEN \(CHRONOLOGISCH\)(.+?)---", "## LETZTE 10 AKTIONEN (CHRONOLOGISCH)$newActionsSection"
}

Set-Content -Path $currentStatePath -Value $currentState -Encoding UTF8
Write-Host "  [OK] 00_CURRENT_STATE.md updated" -ForegroundColor Green

# ============================================================================
# 2. Update 02_CHANGES_LOG.md
# ============================================================================

Write-Host "[2/4] Updating 02_CHANGES_LOG.md..." -ForegroundColor Green

$changesLogPath = "PROJECT_MEMORY/02_CHANGES_LOG.md"
$changesLog = Get-Content $changesLogPath -Raw

# Add new entry at top (after header)
$newEntry = @"

### $timestamp - $Action
**Typ:** Auto-Update  
**Änderungen:**
$Details

**Ausgeführt durch:** UPDATE_MEMORY.ps1

---
"@

# Insert after "## 2025-12-15 | Session 1 | Cleanup & Dependencies Audit"
$changesLog = $changesLog -replace "(## \d{4}-\d{2}-\d{2} \| Session \d+ \| .+)", "`$1$newEntry"

Set-Content -Path $changesLogPath -Value $changesLog -Encoding UTF8
Write-Host "  [OK] 02_CHANGES_LOG.md updated" -ForegroundColor Green

# ============================================================================
# 3. Create Session Log Entry (JSON)
# ============================================================================

Write-Host "[3/4] Creating session log entry..." -ForegroundColor Green

$sessionLogPath = "PROJECT_MEMORY/snapshots/session_log.jsonl"

# Git info
$gitHash = ""
$gitStatus = ""
try {
    $gitHash = (git rev-parse HEAD 2>$null)
    $gitStatus = (git status --short 2>$null) -join "; "
} catch {
    $gitHash = "N/A"
    $gitStatus = "N/A"
}

$sessionEntry = @{
    timestamp = $timestampFile
    datetime = $timestamp
    action = $Action
    details = $Details
    phase = $Phase
    git_hash = $gitHash
    git_status = $gitStatus
} | ConvertTo-Json -Compress

Add-Content -Path $sessionLogPath -Value $sessionEntry -Encoding UTF8
Write-Host "  [OK] Session log entry created" -ForegroundColor Green

# ============================================================================
# 4. Optional: Create Snapshot
# ============================================================================

if ($Action -match "Phase \d+ (abgeschlossen|completed)" -or $Action -match "Snapshot") {
    Write-Host "[4/4] Creating snapshot..." -ForegroundColor Green
    
    $snapshotPath = "PROJECT_MEMORY/snapshots/snapshot_$timestampFile.json"
    
    $snapshot = @{
        timestamp = $timestampFile
        datetime = $timestamp
        action = $Action
        phase = $Phase
        git_hash = $gitHash
        git_status = $gitStatus
        files_changed = (git diff --name-only 2>$null) -join "; "
        current_state = (Get-Content $currentStatePath -Raw)
    } | ConvertTo-Json -Depth 10
    
    Set-Content -Path $snapshotPath -Value $snapshot -Encoding UTF8
    Write-Host "  [OK] Snapshot created: $snapshotPath" -ForegroundColor Green
} else {
    Write-Host "[4/4] No snapshot needed (use -Action 'Snapshot' to force)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "MEMORY UPDATE COMPLETE" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# USAGE EXAMPLES
# ============================================================================
<#
.\UPDATE_MEMORY.ps1 -Action "requirements.txt updated" -Details "Added websockets, psutil, scipy" -Phase "2"
.\UPDATE_MEMORY.ps1 -Action "Phase 2 completed" -Phase "2"
.\UPDATE_MEMORY.ps1 -Action "main.py refactoring started" -Phase "3"
#>
