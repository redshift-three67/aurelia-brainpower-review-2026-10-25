# Run-BatAreaScan.ps1 - Zweistufiger BAT-Bereichs-Scan
# Schritt 1: Scannt alle 82 BAT-Bereiche
# Schritt 2: Detail-Scan der Top-N Bereiche mit Remedies

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ''
Write-Host '=======================================' -ForegroundColor Cyan
Write-Host 'BAT-BEREICHS-SCAN (Zweistufig)' -ForegroundColor Cyan
Write-Host '=======================================' -ForegroundColor Cyan
Write-Host ''

# Eingaben sammeln
$Name = Read-Host 'Nachname'
$FirstName = Read-Host 'Vorname'
$BirthDate = Read-Host 'Geburtsdatum (TTMMJJJJ)'
$BirthPlace = Read-Host 'Geburtsort'

Write-Host ''
Write-Host 'Anzahl der Top-Bereiche fuer Detail-Scan (Standard: 2):' -ForegroundColor Yellow
$TopAreasInput = Read-Host 'Top-Bereiche (1-5)'
if ([string]::IsNullOrWhiteSpace($TopAreasInput)) {
    $TopAreas = 2
} else {
    $TopAreas = [int]$TopAreasInput
    if ($TopAreas -lt 1) { $TopAreas = 1 }
    if ($TopAreas -gt 5) { $TopAreas = 5 }
}

# Intention-Auswahl
Write-Host ''
Write-Host 'Intention (optional, Standard: keine):' -ForegroundColor Yellow
Write-Host '  1) healing      - Heilung' -ForegroundColor DarkYellow
Write-Host '  2) clearing     - Klaerung' -ForegroundColor DarkYellow
Write-Host '  3) protection   - Schutz' -ForegroundColor DarkYellow
Write-Host '  4) transformation - Transformation' -ForegroundColor DarkYellow
Write-Host '  5) harmonization - Harmonisierung' -ForegroundColor DarkYellow
Write-Host '  0) keine        - Keine' -ForegroundColor DarkYellow

$IntentionInput = Read-Host 'Intention (0-5, Standard 0)'
$Intention = ''
switch ($IntentionInput) {
    '1' { $Intention = 'healing' }
    '2' { $Intention = 'clearing' }
    '3' { $Intention = 'protection' }
    '4' { $Intention = 'transformation' }
    '5' { $Intention = 'harmonization' }
    Default { $Intention = '' }
}

Write-Host ''
Write-Host '=======================================' -ForegroundColor Cyan
Write-Host 'Starte BAT-Bereichs-Scan...' -ForegroundColor Cyan
Write-Host "Klient: $FirstName $Name" -ForegroundColor DarkCyan
Write-Host "Top-Bereiche: $TopAreas" -ForegroundColor DarkCyan
if (-not [string]::IsNullOrWhiteSpace($Intention)) {
    Write-Host "Intention: $Intention" -ForegroundColor DarkCyan
}
Write-Host '=======================================' -ForegroundColor Cyan
Write-Host ''

# Python-Interpreter
$pythonExe = 'python'

# Argumente aufbauen
$arguments = @(
    '-m', 'apps.cli.main', 'bat-area-scan',
    $Name,
    $FirstName,
    '--birth-date', $BirthDate,
    '--birth-place', $BirthPlace,
    '--top-areas', $TopAreas
)

if (-not [string]::IsNullOrWhiteSpace($Intention)) {
    $arguments += @('--intention', $Intention)
}

# Scan ausfuehren
try {
    & $pythonExe $arguments
    $exitCode = $LASTEXITCODE
}
catch {
    Write-Host "Fehler beim Ausfuehren: $_" -ForegroundColor Red
    $exitCode = 1
}

Write-Host ''
if ($exitCode -eq 0) {
    Write-Host 'BAT-Bereichs-Scan erfolgreich abgeschlossen!' -ForegroundColor Green
    Write-Host ''
    
    # === REMEDY-EMPFEHLUNGEN FÜR BAT-BEREICHE ===
    Write-Host '=======================================' -ForegroundColor Cyan
    Write-Host 'REMEDY-EMPFEHLUNGEN' -ForegroundColor Cyan
    Write-Host '=======================================' -ForegroundColor Cyan
    Write-Host ''
    
    $baseExport = 'C:\Benutzer_Archive'
    $clientFolder = ("{0}_{1}_{2}_{3}" -f $Name, $FirstName, $BirthDate, $BirthPlace).Trim().Replace(' ', '_')
    $clientDir = Join-Path $baseExport $clientFolder
    
    if (Test-Path $clientDir) {
        $jsonFile = Get-ChildItem -Path $clientDir -Filter '*_bat_area_scan.json' -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        
        if ($jsonFile) {
            try {
                # Hole Remedy-Empfehlungen für BAT-Bereiche
                $jsonPath = $jsonFile.FullName -replace '\\', '\\\\'
                $remedyScript = @"
import sys
sys.path.insert(0, '.')
from services.remedy_service import find_remedies_for_group
import json

# Lade BAT-Scan-Ergebnis
with open('$jsonPath', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extrahiere Top-Bereiche
top_areas = []
if 'top_areas' in data:
    top_areas = data['top_areas'][:5]  # Top 5

# Hole Remedies für BAT-Gruppen
remedies_found = {}
for area in top_areas:
    area_name = area.get('area', '')
    # Mappe BAT-Bereiche zu Gruppen
    group_mapping = {
        'bakterien': 'bakterien_fein',
        'viren': 'viren_fein',
        'pilze': 'pilze_fein',
        'parasiten': 'parasiten_fein',
        'schmerz': 'schmerz',
        'verletzung': 'verletzung'
    }
    
    for key, group in group_mapping.items():
        if key in area_name.lower():
            remedies = find_remedies_for_group(group, max_results=3)
            if remedies:
                remedies_found[area_name] = remedies
            break

# Ausgabe
if remedies_found:
    print('Empfohlene Remedies für BAT-Bereiche:')
    print('')
    for area, remedies in remedies_found.items():
        print(f'Bereich: {area}')
        for name, indication in remedies:
            print(f'  → {name}')
            if indication:
                print(f'    {indication[:100]}...')
        print('')
else:
    print('Keine spezifischen Remedy-Empfehlungen verfügbar.')
"@
                
                $remedyOutput = python -c $remedyScript 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Host $remedyOutput -ForegroundColor DarkCyan
                } else {
                    Write-Host 'Remedy-Empfehlungen konnten nicht geladen werden.' -ForegroundColor Yellow
                }
            } catch {
                Write-Host 'Fehler beim Laden der Remedy-Empfehlungen.' -ForegroundColor Yellow
            }
        }
    }
    
    Write-Host ''
    Write-Host '=======================================' -ForegroundColor Cyan
    Write-Host ''
    
    # === HARMONISIERUNGS-OPTION ===
    $harmInput = Read-Host 'Hardware-Harmonisierung starten? (j/n)'
    if ($harmInput -eq 'j') {
        Write-Host ''
        Write-Host 'Starte Hardware-Harmonisierung (432 Hz, 5 Min)...' -ForegroundColor Cyan
        
        $hwArgs = @(
            '-m', 'apps.cli.main', 'harmonize',
            432.0,  # Frequenz in Hz
            5,      # Dauer in Minuten
            '--intention', 'harmonization',
            '--cpu'
        )
        
        try {
            & $pythonExe $hwArgs
            Write-Host 'Hardware-Harmonisierung gestartet.' -ForegroundColor Green
        } catch {
            Write-Host 'Fehler beim Starten der Hardware-Harmonisierung.' -ForegroundColor Red
        }
    }
} else {
    Write-Host "BAT-Bereichs-Scan beendet mit Code: $exitCode" -ForegroundColor Yellow
}

Write-Host ''
Write-Host 'Druecken Sie eine beliebige Taste zum Beenden...'
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
