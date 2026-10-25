# Root Directory Cleanup Script
# Morphic Engine V1 - Phase 1

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "ROOT DIRECTORY CLEANUP" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Files to delete (unnecessary)
$filesToDelete = @(
    "desktop.ini",
    "dir",
    "python",
    "remedies.db",  # Empty file (0 bytes), duplicate of data/remedies.db
    "bench_out.txt",
    "test_result.txt"
)

# Test files to move to tests/exploratory/
$testFiles = Get-ChildItem -Path . -File | Where-Object {
    $_.Name -like "test_*.py" -and $_.Directory.Name -eq "Morphic_Engine_V1"
}

# Markdown docs to move to docs/archive/
$docsToArchive = Get-ChildItem -Path . -File | Where-Object {
    $_.Name -like "*.md" -and 
    $_.Name -ne "README.md" -and 
    $_.Name -ne "PROJECT_STATE.md"
}

Write-Host "Actions to perform:" -ForegroundColor Yellow
Write-Host "1. Delete unnecessary files: $($filesToDelete.Count) files" -ForegroundColor White
Write-Host "2. Move test files to tests/exploratory/: $($testFiles.Count) files" -ForegroundColor White
Write-Host "3. Move docs to docs/archive/: $($docsToArchive.Count) files" -ForegroundColor White
Write-Host ""

# Show details
Write-Host "Files to delete:" -ForegroundColor Yellow
foreach ($file in $filesToDelete) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Write-Host "  - $file ($size bytes)" -ForegroundColor Red
    }
}
Write-Host ""

Write-Host "Test files to move:" -ForegroundColor Yellow
$testFiles | Select-Object Name | Format-Table
Write-Host ""

Write-Host "Docs to archive:" -ForegroundColor Yellow
$docsToArchive | Select-Object Name, @{Name="Size(KB)";Expression={[math]::Round($_.Length/1KB, 2)}} | Format-Table
Write-Host ""

$confirmation = Read-Host "Proceed with cleanup? (yes/no)"

if ($confirmation -eq "yes") {
    # 1. Delete unnecessary files
    Write-Host ""
    Write-Host "Deleting unnecessary files..." -ForegroundColor Yellow
    foreach ($file in $filesToDelete) {
        if (Test-Path $file) {
            try {
                Remove-Item $file -Force
                Write-Host "  ✓ Deleted: $file" -ForegroundColor Green
            } catch {
                Write-Host "  ✗ Failed: $file - $_" -ForegroundColor Red
            }
        }
    }
    
    # 2. Move test files
    Write-Host ""
    Write-Host "Moving test files..." -ForegroundColor Yellow
    if (-not (Test-Path "tests\exploratory")) {
        New-Item -Path "tests\exploratory" -ItemType Directory -Force | Out-Null
        Write-Host "  Created: tests\exploratory" -ForegroundColor Green
    }
    
    foreach ($file in $testFiles) {
        try {
            Move-Item $file.FullName -Destination "tests\exploratory\" -Force
            Write-Host "  ✓ Moved: $($file.Name)" -ForegroundColor Green
        } catch {
            Write-Host "  ✗ Failed: $($file.Name) - $_" -ForegroundColor Red
        }
    }
    
    # 3. Archive docs
    Write-Host ""
    Write-Host "Archiving documentation..." -ForegroundColor Yellow
    if (-not (Test-Path "docs\archive")) {
        New-Item -Path "docs\archive" -ItemType Directory -Force | Out-Null
        Write-Host "  Created: docs\archive" -ForegroundColor Green
    }
    
    foreach ($doc in $docsToArchive) {
        try {
            Move-Item $doc.FullName -Destination "docs\archive\" -Force
            Write-Host "  ✓ Archived: $($doc.Name)" -ForegroundColor Green
        } catch {
            Write-Host "  ✗ Failed: $($doc.Name) - $_" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Write-Host "✓ Root cleanup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Remaining in root:" -ForegroundColor Cyan
    Get-ChildItem -Path . -File | Where-Object {$_.Name -like "*.md" -or $_.Name -like "*.py"} | Select-Object Name | Format-Table
    
} else {
    Write-Host "Cleanup cancelled." -ForegroundColor Yellow
}
