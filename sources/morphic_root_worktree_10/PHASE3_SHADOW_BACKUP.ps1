# PHASE3_SHADOW_BACKUP.ps1
# Erstellt Shadow-Copies vor kritischem Refactoring
# Gemäss PROJECT_MEMORY Protokollierungssystem

param(
    [switch]$Restore,
    [string]$BackupName = ""
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$shadowDir = "PROJECT_MEMORY/shadow_backups"

# Shadow-Backup Verzeichnis erstellen
if (-not (Test-Path $shadowDir)) {
    New-Item -ItemType Directory -Path $shadowDir -Force | Out-Null
}

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "PHASE 3 - SHADOW BACKUP SYSTEM" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# RESTORE MODE
# ============================================================================
if ($Restore) {
    Write-Host "RESTORE MODE" -ForegroundColor Yellow
    Write-Host ""
    
    if (-not $BackupName) {
        Write-Host "Verfügbare Backups:" -ForegroundColor Green
        $backups = Get-ChildItem -Path $shadowDir -Directory | Sort-Object Name -Descending
        $backups | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor White }
        Write-Host ""
        $BackupName = Read-Host "Backup-Name zum Wiederherstellen"
    }
    
    $backupPath = Join-Path $shadowDir $BackupName
    
    if (-not (Test-Path $backupPath)) {
        Write-Host "[FEHLER] Backup nicht gefunden: $BackupName" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Wiederherstellung von: $BackupName" -ForegroundColor Yellow
    $confirm = Read-Host "WARNUNG: Aktuelle Dateien werden überschrieben! Fortfahren? (yes/no)"
    
    if ($confirm -ne "yes") {
        Write-Host "Abgebrochen." -ForegroundColor Yellow
        exit
    }
    
    # Restore files
    $manifest = Get-Content (Join-Path $backupPath "manifest.json") | ConvertFrom-Json
    
    foreach ($file in $manifest.files) {
        $sourcePath = Join-Path $backupPath $file.backup_name
        $targetPath = $file.original_path
        
        if (Test-Path $sourcePath) {
            Copy-Item -Path $sourcePath -Destination $targetPath -Force
            Write-Host "  [OK] Wiederhergestellt: $targetPath" -ForegroundColor Green
        } else {
            Write-Host "  [WARNUNG] Nicht gefunden: $sourcePath" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "Wiederherstellung abgeschlossen!" -ForegroundColor Green
    exit
}

# ============================================================================
# BACKUP MODE
# ============================================================================

$backupName = "shadow_$timestamp"
$backupPath = Join-Path $shadowDir $backupName

Write-Host "Erstelle Shadow-Backup: $backupName" -ForegroundColor Green
Write-Host ""

# Dateien die gesichert werden sollen
$filesToBackup = @(
    "apps/cli/main.py",
    "apps/cli/commands/scan.py",
    "apps/cli/commands/trend.py",
    "apps/cli/commands/harmonize.py",
    "apps/cli/commands/synergy.py",
    "apps/cli/commands/descriptions.py",
    "requirements.txt",
    "PROJECT_MEMORY/00_CURRENT_STATE.md"
)

# Backup-Verzeichnis erstellen
New-Item -ItemType Directory -Path $backupPath -Force | Out-Null

# Manifest erstellen
$manifest = @{
    timestamp = $timestamp
    datetime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    phase = "3"
    purpose = "Shadow backup before main.py refactoring"
    git_commit = ""
    files = @()
}

try {
    $manifest.git_commit = (git rev-parse HEAD 2>$null)
} catch {
    $manifest.git_commit = "N/A"
}

# Dateien sichern
$fileCount = 0
foreach ($file in $filesToBackup) {
    if (Test-Path $file) {
        $fileInfo = Get-Item $file
        $backupFileName = $fileInfo.Name + ".shadow"
        $backupFilePath = Join-Path $backupPath $backupFileName
        
        Copy-Item -Path $file -Destination $backupFilePath -Force
        
        $manifest.files += @{
            original_path = $file
            backup_name = $backupFileName
            size_bytes = $fileInfo.Length
            hash = (Get-FileHash -Path $file -Algorithm SHA256).Hash
        }
        
        $fileCount++
        Write-Host "  [OK] Gesichert: $file" -ForegroundColor Green
    } else {
        Write-Host "  [WARNUNG] Nicht gefunden: $file" -ForegroundColor Yellow
    }
}

# Manifest speichern
$manifest | ConvertTo-Json -Depth 10 | Set-Content -Path (Join-Path $backupPath "manifest.json") -Encoding UTF8

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Shadow-Backup erstellt!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Backup: $backupName" -ForegroundColor White
Write-Host "Dateien: $fileCount" -ForegroundColor White
Write-Host "Pfad: $backupPath" -ForegroundColor White
Write-Host ""
Write-Host "Zum Wiederherstellen:" -ForegroundColor Yellow
Write-Host "  .\PHASE3_SHADOW_BACKUP.ps1 -Restore -BackupName $backupName" -ForegroundColor White
Write-Host ""

# ============================================================================
# UPDATE PROJECT_MEMORY
# ============================================================================

Write-Host "Aktualisiere PROJECT_MEMORY..." -ForegroundColor Green
.\UPDATE_MEMORY.ps1 -Action "Shadow backup created: $backupName" -Phase "3" -Details "$fileCount files backed up"

Write-Host ""
Write-Host "[OK] Alles bereit fuer Phase 3 Refactoring!" -ForegroundColor Green
