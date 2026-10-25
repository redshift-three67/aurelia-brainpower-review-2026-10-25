# Run-RemedyLookup.ps1 - Remedy-Datenbank durchsuchen
# Suche nach Remedies und Pathogenen

param(
    [ValidateSet('Interactive', 'Keyword', 'Group', 'Pathogen', 'Stats', 'Exit')]
    [string]$Action = 'Interactive',
    [string]$Query,
    [switch]$NoPause
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

$projectRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$pythonCandidates = @(
    (Join-Path $projectRoot '.venv\Scripts\python.exe'),
    (Join-Path $projectRoot '..\..\.venv\Scripts\python.exe')
)
$pythonExe = $pythonCandidates |
    Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } |
    Select-Object -First 1
if (-not $pythonExe) {
    throw 'Projekt-Python wurde nicht gefunden. Erwartet: .venv\Scripts\python.exe.'
}
$pythonExe = (Resolve-Path -LiteralPath $pythonExe).Path

function Invoke-ProjectPython {
    param(
        [Parameter(Mandatory = $true)][string]$Code,
        [string[]]$Arguments = @()
    )

    $pythonArguments = @('-I', '-X', 'utf8', '-', $projectRoot) + $Arguments
    $Code | & $pythonExe @pythonArguments
    if ($LASTEXITCODE -ne 0) {
        $nativeExitCode = $LASTEXITCODE
        $exception = [System.Exception]::new(
            "Projekt-Python wurde mit Exitcode $nativeExitCode beendet."
        )
        $exception.Data['NativeExitCode'] = $nativeExitCode
        throw $exception
    }
}

function Get-NativeExitCode {
    param([System.Management.Automation.ErrorRecord]$ErrorRecord)

    $nativeExitCode = $ErrorRecord.Exception.Data['NativeExitCode']
    if ($nativeExitCode -is [int] -and $nativeExitCode -ne 0) {
        return $nativeExitCode
    }
    return 1
}

Write-Host ''
Write-Host '=======================================' -ForegroundColor Cyan
Write-Host 'REMEDY-DATENBANK SUCHE' -ForegroundColor Cyan
Write-Host '=======================================' -ForegroundColor Cyan
Write-Host ''

# Menü
Write-Host 'Suchoptionen:' -ForegroundColor Yellow
Write-Host '  1) Keyword   - Suche nach Keyword' -ForegroundColor DarkYellow
Write-Host '  2) Gruppe    - Remedies für Gruppe anzeigen' -ForegroundColor DarkYellow
Write-Host '  3) Pathogen  - Pathogen suchen' -ForegroundColor DarkYellow
Write-Host '  4) Statistik - Datenbank-Statistik anzeigen' -ForegroundColor DarkYellow
Write-Host '  0) Beenden   - Skript beenden' -ForegroundColor DarkYellow
Write-Host ''

$choice = switch ($Action) {
    'Keyword' { '1' }
    'Group' { '2' }
    'Pathogen' { '3' }
    'Stats' { '4' }
    'Exit' { '0' }
    Default { Read-Host 'Auswahl (0-4)' }
}
$scriptExitCode = 0

switch ($choice) {
    '1' {
        # Keyword-Suche
        Write-Host ''
        $keyword = if ($Action -eq 'Interactive') {
            Read-Host 'Suchbegriff (z.B. arnica, echinacea, bakterien)'
        } else {
            $Query
        }
        
        if ([string]::IsNullOrWhiteSpace($keyword)) {
            Write-Host 'Fehler: Suchbegriff ist erforderlich.' -ForegroundColor Red
            $scriptExitCode = 2
        } else {
            Write-Host ''
            Write-Host 'Keyword-Suche...' -ForegroundColor Cyan
            Write-Host ''
            
            $searchScript = @'
import sys
sys.path.insert(0, sys.argv[1])
from services.remedy_service import find_remedies_for_group

remedies = find_remedies_for_group(sys.argv[2], max_results=10)[:10]

if remedies:
    print(f'Gefunden: {len(remedies)} Remedies')
    print('')
    for i, (name, indication) in enumerate(remedies, 1):
        print(f'{i}. {name}')
        if indication:
            print(f'   {indication[:150]}...')
        print('')
else:
    print('Keine Remedies gefunden.')
'@
            
            try {
                Invoke-ProjectPython -Code $searchScript -Arguments @($keyword)
            } catch {
                Write-Host "Fehler: $_" -ForegroundColor Red
                $scriptExitCode = Get-NativeExitCode $_
            }
        }
    }
    
    '2' {
        # Gruppen-Suche
        Write-Host ''
        Write-Host 'Verfügbare Gruppen:' -ForegroundColor Yellow
        Write-Host '  bakterien_fein, viren_fein, pilze_fein, parasiten_fein' -ForegroundColor DarkYellow
        Write-Host '  schmerz, verletzung, entgiftung, hormone, psyche' -ForegroundColor DarkYellow
        Write-Host '  bachblueten, homoeopathie, spagyrik, orthomolekular' -ForegroundColor DarkYellow
        Write-Host ''
        
        $group = if ($Action -eq 'Interactive') { Read-Host 'Gruppe' } else { $Query }
        
        if ([string]::IsNullOrWhiteSpace($group)) {
            Write-Host 'Fehler: Suchbegriff ist erforderlich.' -ForegroundColor Red
            $scriptExitCode = 2
        } else {
            Write-Host ''
            Write-Host 'Gruppen-Suche...' -ForegroundColor Cyan
            Write-Host ''
            
            $groupScript = @'
import sys
sys.path.insert(0, sys.argv[1])
from services.remedy_service import find_remedies_for_group

remedies = find_remedies_for_group(sys.argv[2], max_results=10)[:10]

if remedies:
    print(f'Gefunden: {len(remedies)} Remedies')
    print('')
    for i, (name, indication) in enumerate(remedies, 1):
        print(f'{i}. {name}')
        if indication:
            print(f'   {indication[:150]}...')
        print('')
else:
    print('Keine Remedies für diese Gruppe gefunden.')
'@
            
            try {
                Invoke-ProjectPython -Code $groupScript -Arguments @($group)
            } catch {
                Write-Host "Fehler: $_" -ForegroundColor Red
                $scriptExitCode = Get-NativeExitCode $_
            }
        }
    }
    
    '3' {
        # Pathogen-Suche
        Write-Host ''
        $keyword = if ($Action -eq 'Interactive') {
            Read-Host 'Pathogen-Suchbegriff (z.B. staphylo, candida, herpes)'
        } else {
            $Query
        }
        
        if ([string]::IsNullOrWhiteSpace($keyword)) {
            Write-Host 'Fehler: Suchbegriff ist erforderlich.' -ForegroundColor Red
            $scriptExitCode = 2
        } else {
            Write-Host ''
            Write-Host 'Pathogen-Suche...' -ForegroundColor Cyan
            Write-Host ''
            
            $pathogenScript = @'
import sys
sys.path.insert(0, sys.argv[1])
from services.remedy_service import find_pathogens_by_keyword, get_remedies_for_pathogen

pathogens = find_pathogens_by_keyword(sys.argv[2], max_results=5)

if pathogens:
    print(f'Gefunden: {len(pathogens)} Pathogene')
    print('')
    for i, pathogen in enumerate(pathogens, 1):
        print(f'{i}. {pathogen["name"]} ({pathogen["pathogen_type"]})')
        
        # Hole Remedies für dieses Pathogen
        remedies = get_remedies_for_pathogen(pathogen['id'], max_results=3)
        if remedies:
            print('   Empfohlene Remedies:')
            for name, indication in remedies:
                print(f'     -> {name}')
        print('')
else:
    print('Keine Pathogene gefunden.')
'@
            
            try {
                Invoke-ProjectPython -Code $pathogenScript -Arguments @($keyword)
            } catch {
                Write-Host "Fehler: $_" -ForegroundColor Red
                $scriptExitCode = Get-NativeExitCode $_
            }
        }
    }
    
    '4' {
        # Statistik
        Write-Host ''
        Write-Host 'Datenbank-Statistik...' -ForegroundColor Cyan
        Write-Host ''
        
        $statsScript = @'
import sys
sys.path.insert(0, sys.argv[1])
from services.remedy_service import get_remedy_stats

stats = get_remedy_stats()

print('=' * 70)
print('REMEDY-DATENBANK STATISTIK')
print('=' * 70)
print('')
print(f'Remedies:        {stats["total_remedies"]}')
print(f'Pathogene:       {stats["total_pathogens"]}')
print(f'Multiplex-Links: {stats["multiplex_links"]}')
print('')
print(f'GESAMT:          {stats["total_remedies"] + stats["total_pathogens"] + stats["multiplex_links"]} Datensätze')
print('')

if stats.get('pathogens_by_type'):
    print('Pathogene nach Typ:')
    for ptype, count in sorted(stats['pathogens_by_type'].items(), key=lambda x: -x[1]):
        print(f'  {ptype}: {count}')
    print('')

if stats.get('by_category'):
    print('Top-10 Remedy-Kategorien:')
    sorted_cats = sorted(stats['by_category'].items(), key=lambda x: -x[1])
    for cat, count in sorted_cats[:10]:
        print(f'  {cat}: {count}')

print('=' * 70)
'@
        
        try {
            Invoke-ProjectPython -Code $statsScript
        } catch {
            Write-Host "Fehler: $_" -ForegroundColor Red
            $scriptExitCode = Get-NativeExitCode $_
        }
    }
    
    Default {
        Write-Host 'Beendet.' -ForegroundColor Gray
    }
}

Write-Host ''
if (-not $NoPause) {
    Write-Host 'Druecken Sie eine beliebige Taste zum Beenden...'
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
}
exit $scriptExitCode
