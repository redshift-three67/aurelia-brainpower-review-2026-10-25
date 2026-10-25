# MASTER CLEANUP SCRIPT
# Morphic Engine V1 - Complete Phase 1 Cleanup
# 
# This script orchestrates the entire cleanup process

param(
    [switch]$AutoConfirm
)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "MORPHIC ENGINE V1 - MASTER CLEANUP" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "This script will perform:" -ForegroundColor Yellow
Write-Host "1. Backup files cleanup (~189 files)" -ForegroundColor White
Write-Host "2. Root directory cleanup (unnecessary files)" -ForegroundColor White
Write-Host "3. Test files organization" -ForegroundColor White
Write-Host "4. Documentation archival" -ForegroundColor White
Write-Host "5. Git commit of changes" -ForegroundColor White
Write-Host ""

if (-not $AutoConfirm) {
    $proceed = Read-Host "Start master cleanup? (yes/no)"
    if ($proceed -ne "yes") {
        Write-Host "Cleanup cancelled." -ForegroundColor Yellow
        exit
    }
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "STEP 1: BACKUP FILES CLEANUP" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Find backup files
$backupFiles = Get-ChildItem -Path . -Recurse -File | Where-Object {
    $_.Name -like "*.bak" -or 
    $_.Name -like "*.bak_*" -or 
    $_.Name -like "*.shadow_*" -or 
    $_.Name -like "*.damaged_*"
}

Write-Host "Found $($backupFiles.Count) backup files" -ForegroundColor Green
Write-Host "Deleting..." -ForegroundColor Yellow

$deletedBackups = 0
foreach ($file in $backupFiles) {
    try {
        Remove-Item -Path $file.FullName -Force
        $deletedBackups++
    } catch {
        Write-Host "Failed: $($file.Name)" -ForegroundColor Red
    }
}

Write-Host "✓ Deleted $deletedBackups backup files" -ForegroundColor Green
Write-Host ""

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "STEP 2: ROOT CLEANUP" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Delete unnecessary files
$filesToDelete = @("desktop.ini", "dir", "python", "remedies.db", "bench_out.txt", "test_result.txt")
$deletedRoot = 0

foreach ($file in $filesToDelete) {
    if (Test-Path $file) {
        try {
            Remove-Item $file -Force
            Write-Host "✓ Deleted: $file" -ForegroundColor Green
            $deletedRoot++
        } catch {
            Write-Host "✗ Failed: $file" -ForegroundColor Red
        }
    }
}

Write-Host "✓ Deleted $deletedRoot unnecessary files" -ForegroundColor Green
Write-Host ""

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "STEP 3: ORGANIZE TEST FILES" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Create tests/exploratory directory
if (-not (Test-Path "tests\exploratory")) {
    New-Item -Path "tests\exploratory" -ItemType Directory -Force | Out-Null
    Write-Host "Created: tests\exploratory" -ForegroundColor Green
}

# Move test files
$testFiles = Get-ChildItem -Path . -File | Where-Object {
    $_.Name -like "test_*.py" -and $_.Directory.Name -eq "Morphic_Engine_V1"
}

$movedTests = 0
foreach ($file in $testFiles) {
    try {
        Move-Item $file.FullName -Destination "tests\exploratory\" -Force
        Write-Host "✓ Moved: $($file.Name)" -ForegroundColor Green
        $movedTests++
    } catch {
        Write-Host "✗ Failed: $($file.Name)" -ForegroundColor Red
    }
}

Write-Host "✓ Moved $movedTests test files" -ForegroundColor Green
Write-Host ""

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "STEP 4: ARCHIVE DOCUMENTATION" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Create docs/archive directory
if (-not (Test-Path "docs\archive")) {
    New-Item -Path "docs\archive" -ItemType Directory -Force | Out-Null
    Write-Host "Created: docs\archive" -ForegroundColor Green
}

# Move docs (except README.md and PROJECT_STATE.md)
$docsToArchive = Get-ChildItem -Path . -File | Where-Object {
    $_.Name -like "*.md" -and 
    $_.Name -ne "README.md" -and 
    $_.Name -ne "PROJECT_STATE.md"
}

$archivedDocs = 0
foreach ($doc in $docsToArchive) {
    try {
        Move-Item $doc.FullName -Destination "docs\archive\" -Force
        Write-Host "✓ Archived: $($doc.Name)" -ForegroundColor Green
        $archivedDocs++
    } catch {
        Write-Host "✗ Failed: $($doc.Name)" -ForegroundColor Red
    }
}

Write-Host "✓ Archived $archivedDocs documentation files" -ForegroundColor Green
Write-Host ""

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "CLEANUP SUMMARY" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Deleted backup files: $deletedBackups" -ForegroundColor Green
Write-Host "Deleted root files: $deletedRoot" -ForegroundColor Green
Write-Host "Moved test files: $movedTests" -ForegroundColor Green
Write-Host "Archived docs: $archivedDocs" -ForegroundColor Green
Write-Host ""
Write-Host "Total changes: $($deletedBackups + $deletedRoot + $movedTests + $archivedDocs)" -ForegroundColor Yellow
Write-Host ""

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "STEP 5: GIT COMMIT" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$gitCommit = Read-Host "Commit changes to Git? (yes/no)"

if ($gitCommit -eq "yes") {
    Write-Host "Adding changes to git..." -ForegroundColor Yellow
    git add .
    
    Write-Host "Committing..." -ForegroundColor Yellow
    git commit -m "chore: Phase 1 cleanup - removed $deletedBackups backups, organized tests and docs"
    
    Write-Host "✓ Changes committed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Git status:" -ForegroundColor Cyan
    git status
} else {
    Write-Host "Git commit skipped. Run manually:" -ForegroundColor Yellow
    Write-Host "  git add ." -ForegroundColor White
    Write-Host "  git commit -m 'chore: Phase 1 cleanup'" -ForegroundColor White
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "✓ MASTER CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Review git diff to verify changes" -ForegroundColor White
Write-Host "2. Run: py -3.13 -m pytest tests/ (verify tests still work)" -ForegroundColor White
Write-Host "3. Continue with Phase 2: Dependencies audit" -ForegroundColor White
