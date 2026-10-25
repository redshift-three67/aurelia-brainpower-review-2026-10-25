# Cleanup Backup Files Script
# Morphic Engine V1 - Phase 1

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "BACKUP FILES CLEANUP" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Find all backup files
Write-Host "Searching for backup files..." -ForegroundColor Yellow
$backupFiles = Get-ChildItem -Path . -Recurse -File | Where-Object {
    $_.Name -like "*.bak" -or 
    $_.Name -like "*.bak_*" -or 
    $_.Name -like "*.shadow_*" -or 
    $_.Name -like "*.damaged_*"
}

$totalCount = $backupFiles.Count
$totalSize = ($backupFiles | Measure-Object -Property Length -Sum).Sum / 1MB

Write-Host "Found: $totalCount files" -ForegroundColor Green
Write-Host "Total Size: $([math]::Round($totalSize, 2)) MB" -ForegroundColor Green
Write-Host ""

# Show first 20 files
Write-Host "Sample files (first 20):" -ForegroundColor Yellow
$backupFiles | Select-Object -First 20 Name, @{Name="Size(KB)";Expression={[math]::Round($_.Length/1KB, 2)}}, Directory | Format-Table -AutoSize

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Ready to delete $totalCount files ($([math]::Round($totalSize, 2)) MB)" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Ask for confirmation
$confirmation = Read-Host "Delete all backup files? (yes/no)"

if ($confirmation -eq "yes") {
    Write-Host ""
    Write-Host "Deleting files..." -ForegroundColor Red
    
    $deleted = 0
    foreach ($file in $backupFiles) {
        try {
            Remove-Item -Path $file.FullName -Force
            $deleted++
            if ($deleted % 10 -eq 0) {
                Write-Host "Deleted: $deleted / $totalCount files..." -ForegroundColor Yellow
            }
        } catch {
            Write-Host "Failed to delete: $($file.Name) - $_" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Write-Host "✓ Cleanup complete! Deleted $deleted files." -ForegroundColor Green
    Write-Host ""
    Write-Host "Run 'git add .' and 'git commit -m \"chore: remove backup files\"' to commit changes" -ForegroundColor Cyan
} else {
    Write-Host "Cleanup cancelled." -ForegroundColor Yellow
}
