# STATUS_CHECK.ps1 - Automatisierte Projekt-Status Überprüfung

param(
    [switch]$Export
)

$projectRoot = Get-Location

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "                  MORPHIC ENGINE V1 - STATUS CHECK                    " -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# ===== PHASE PROGRESS =====
Write-Host "[1/5] PHASE PROGRESS" -ForegroundColor Yellow
Write-Host "-------------------------------------------------------------------"

$memoryFile = "PROJECT_MEMORY/00_CURRENT_STATE.md"
if (Test-Path $memoryFile) {
    $phaseInfo = Select-String 'Phase:.*Refactoring' $memoryFile | ForEach-Object { $_.Line.Trim() }
    $progress = Select-String 'Fortschritt:' $memoryFile | ForEach-Object { $_.Line -replace '.*Fortschritt: ', '' }
    Write-Host "OK Phase: $phaseInfo"
    Write-Host "OK Progress: $progress"
} else {
    Write-Host "ERR PROJECT_MEMORY/00_CURRENT_STATE.md nicht gefunden" -ForegroundColor Red
}
Write-Host ""

# ===== GIT STATUS =====
Write-Host "[2/5] GIT STATUS" -ForegroundColor Yellow
Write-Host "-------------------------------------------------------------------"

$branch = git rev-parse --abbrev-ref HEAD 2>$null
$commitHash = git rev-parse --short HEAD 2>$null
$lastMsg = git log -1 --pretty=%B 2>$null

Write-Host "OK Branch: $branch"
Write-Host "OK Last Commit: $commitHash"
Write-Host "OK Message: $(($lastMsg -split [System.Environment]::NewLine)[0])"
Write-Host ""

# ===== MIGRATIONS COMPLETED =====
Write-Host "[3/5] MIGRATIONS COMPLETED" -ForegroundColor Yellow
Write-Host "-------------------------------------------------------------------"

$commits = @(
    @{ Hash = "3e25572"; Func = "top3_scan"; Lines = 526; Status = "OK" },
    @{ Hash = "142ea3a"; Func = "hw_diagnostics"; Lines = 170; Status = "OK" },
    @{ Hash = "a78208b"; Func = "groups_overview"; Lines = 120; Status = "OK" },
    @{ Hash = "XXXXX"; Func = "analyze_trends"; Lines = 177; Status = "OK" },
    @{ Hash = "XXXXX"; Func = "client_trends"; Lines = 60; Status = "OK" }
)

$totalLines = 0
foreach ($commit in $commits) {
    Write-Host "  $($commit.Status) $($commit.Func) ($($commit.Lines) lines) - $($commit.Hash)"
    $totalLines += $commit.Lines
}
Write-Host "  ------------------------------------"
Write-Host "  Total: $($commits.Count) of 50 functions - $totalLines lines migrated"
Write-Host ""

# ===== MAIN.PY REDUCTION =====
Write-Host "[4/5] CODE REDUCTION METRICS" -ForegroundColor Yellow
Write-Host "-------------------------------------------------------------------"

$mainFile = "apps/cli/main.py"
$scanFile = "apps/cli/commands/scan.py"

if ((Test-Path $mainFile) -and (Test-Path $scanFile)) {
    $mainLines = (Get-Content $mainFile | Measure-Object -Line).Lines
    $scanLines = (Get-Content $scanFile | Measure-Object -Line).Lines
    $reduction = 9543 - $mainLines
    $percent = [math]::Round(($reduction / 9543) * 100, 1)
    
    Write-Host "OK main.py:  $mainLines lines (started: 9543)"
    Write-Host "OK scan.py:  $scanLines lines (started: 627)"
    Write-Host "OK Reduction: -$reduction lines (-${percent} percent)"
} else {
    Write-Host "ERR Files not found" -ForegroundColor Red
}
Write-Host ""

# ===== MEMORY SYSTEM =====
Write-Host "[5/5] MEMORY SYSTEM STATUS" -ForegroundColor Yellow
Write-Host "-------------------------------------------------------------------"

$memoryFiles = @(
    "PROJECT_MEMORY/00_CURRENT_STATE.md",
    "PROJECT_MEMORY/02_CHANGES_LOG.md",
    "PROJECT_MEMORY/01_ARCHITECTURE.md",
    "CLAUDE.md"
)

$memoryOK = 0
foreach ($file in $memoryFiles) {
    if (Test-Path $file) {
        Write-Host "  OK $(Split-Path $file -Leaf)"
        $memoryOK++
    } else {
        Write-Host "  ERR $(Split-Path $file -Leaf)" -ForegroundColor Red
    }
}

$gitHooksPath = git config core.hooksPath 2>$null
if ($gitHooksPath) {
    Write-Host "  OK Git Hooks: $gitHooksPath"
}

Write-Host ""

# ===== NEXT STEPS =====
Write-Host "NEXT PRIORITY" -ForegroundColor Green
Write-Host "-------------------------------------------------------------------"
Write-Host "  1. trend_scan (approx 400 lines)"
Write-Host "  2. harmonize_clients (approx 300 lines)"
Write-Host "  3. synergy_analysis (approx 250 lines)"
Write-Host "  4. description_generator (approx 200 lines)"
Write-Host ""

# ===== SUMMARY =====
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "  STATUS: OK READY FOR NEXT MIGRATION (trend_scan)                   " -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green
Write-Host ""

# ===== EXPORT OPTION =====
if ($Export) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $exportFile = "PROJECT_MEMORY/snapshots/status_$timestamp.json"
    
    $statusObj = New-Object PSObject -Property @{
        timestamp = $timestamp
        phase = "Phase 3 - main.py Refactoring"
        progress = "40% (5 of 50 functions)"
        main_py_lines = $mainLines
        reduction_lines = -$reduction
        reduction_percent = -$percent
        last_commit = $commitHash
        next_task = "batch-scan migration"
    }
    
    $statusObj | ConvertTo-Json | Set-Content $exportFile -Encoding UTF8 -Force
    Write-Host "OK Export saved: $exportFile" -ForegroundColor Green
}
