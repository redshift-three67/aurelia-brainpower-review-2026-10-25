# Erstelle Restore Point v1.4.9.1 Pre-Bugfix
$ProjectRoot = Get-Location
$RestorePointsDir = Join-Path $ProjectRoot "RestorePoints"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupDir = Join-Path $RestorePointsDir "RestorePoint_v1491_PreBugfix_$Timestamp"

Write-Host "========================================" -ForegroundColor Green
Write-Host "RESTORE POINT CREATOR v1.4.9.1" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Project Root: $ProjectRoot" -ForegroundColor Cyan
Write-Host "Backup Destination: $BackupDir" -ForegroundColor Cyan
Write-Host ""

# Erstelle RestorePoints Verzeichnis falls nicht vorhanden
if (-not (Test-Path $RestorePointsDir)) {
    New-Item -Path $RestorePointsDir -ItemType Directory | Out-Null
    Write-Host "[OK] Created RestorePoints directory" -ForegroundColor Green
}

# Kopiere Projekt (mit Excludes)
Write-Host "[1] Starting backup copy..." -ForegroundColor Yellow

$ExcludePatterns = @(
    '__pycache__',
    '.git',
    'venv',
    'env',
    'build_env',
    'RestorePoints',
    'Analysen',
    'Radi144',
    '*.pyc',
    '*.tmp',
    '*.wav',
    'temp_group.json',
    '.pytest_cache',
    '.vscode',
    'create_restore_point.py',
    'create_restore.ps1',
    'restore_output.txt'
)

# Kopiere mit Exclude
Copy-Item -Path "$ProjectRoot\*" -Destination $BackupDir -Recurse -Exclude $ExcludePatterns -Force -ErrorAction SilentlyContinue

Write-Host "[2] Backup copy completed" -ForegroundColor Green

# Erstelle RESTORE_INFO.txt
Write-Host "[3] Creating RESTORE_INFO.txt..." -ForegroundColor Yellow

$RestoreInfo = @"
================================================================================
RESTORE POINT INFORMATION
================================================================================

Created: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Label: Pre-Bugfix Snapshot v1.4.9.1
Version: 1.4.9.1 (Adaptive Hardware & Client Synergy Edition)
Date: 05. Februar 2026

================================================================================
FEATURES IN THIS SNAPSHOT
================================================================================
- Adaptive HW Scaling (psutil, 80k-1M Kandidaten)
- UTF-8 BOM Fix fuer JSON Gruppen-Import
- Group Birth Place Integration (Geburtsort in Signatur)
- User Guide (DE) fuer Klienten
- Rekursiver DB-Scan mit Top-21 Ranking
- Audio-Harmonisierung mit Solfeggio-Layering
- Harmonizer mit Puls/Pause-Zyklen

================================================================================
RECOVERY INSTRUCTIONS
================================================================================
1. Copy entire folder to: C:\Users\<Username>\CascadeProjects\12x12
2. Overwrite existing files (Analysen folder will be preserved)
3. Run: setup_new_pc.bat (installs dependencies)
4. Test: generate_matrix.ps1

================================================================================
KNOWN ISSUES (Fixed after this snapshot)
================================================================================
B1: PkADDING typo in dev_cli.py line 282 (PDF padding missing)
B2: `$u_ae`/`$u_ue` variables undefined in generate_matrix.ps1
M1: REST API not updated to v1.4.9 features
M2: main.py version still 1.0.0

================================================================================
"@

$RestoreInfoPath = Join-Path $BackupDir "RESTORE_INFO.txt"
Set-Content -Path $RestoreInfoPath -Value $RestoreInfo -Encoding UTF8

Write-Host "[4] RESTORE_INFO.txt created" -ForegroundColor Green

# Berechne Größe
$Size = (Get-ChildItem $BackupDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "[5] Backup size: $([Math]::Round($Size, 2)) MB" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "SUCCESS: Restore point created!" -ForegroundColor Green
Write-Host "Location: $BackupDir" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
