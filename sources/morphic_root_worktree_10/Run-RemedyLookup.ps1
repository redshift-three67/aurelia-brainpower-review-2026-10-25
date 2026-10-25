# Run-RemedyLookup.ps1 - Remedy-Datenbank durchsuchen
# Suche nach Remedies und Pathogenen

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ''
Write-Host '=======================================' -ForegroundColor Cyan
Write-Host 'REMEDY-DATENBANK SUCHE' -ForegroundColor Cyan
Write-Host '=======================================' -ForegroundColor Cyan
Write-Host ''

# Python-Interpreter
$pythonExe = 'python'

# Menü
Write-Host 'Suchoptionen:' -ForegroundColor Yellow
Write-Host '  1) Keyword   - Suche nach Keyword' -ForegroundColor DarkYellow
Write-Host '  2) Gruppe    - Remedies für Gruppe anzeigen' -ForegroundColor DarkYellow
Write-Host '  3) Pathogen  - Pathogen suchen' -ForegroundColor DarkYellow
Write-Host '  4) Statistik - Datenbank-Statistik anzeigen' -ForegroundColor DarkYellow
Write-Host '  0) Beenden   - Skript beenden' -ForegroundColor DarkYellow
Write-Host ''

$choice = Read-Host 'Auswahl (0-4)'

switch ($choice) {
    '1' {
        # Keyword-Suche
        Write-Host ''
        $keyword = Read-Host 'Suchbegriff (z.B. arnica, echinacea, bakterien)'
        
        if (-not [string]::IsNullOrWhiteSpace($keyword)) {
            Write-Host ''
            Write-Host "Suche nach '$keyword'..." -ForegroundColor Cyan
            Write-Host ''
            
            $searchScript = @"
import sys
sys.path.insert(0, '.')
from services.remedy_service import find_remedies_by_keyword

remedies = find_remedies_by_keyword('$keyword', max_results=10)

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
"@
            
            try {
                & $pythonExe -c $searchScript
            } catch {
                Write-Host "Fehler: $_" -ForegroundColor Red
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
        
        $group = Read-Host 'Gruppe'
        
        if (-not [string]::IsNullOrWhiteSpace($group)) {
            Write-Host ''
            Write-Host "Remedies für Gruppe '$group'..." -ForegroundColor Cyan
            Write-Host ''
            
            $groupScript = @"
import sys
sys.path.insert(0, '.')
from services.remedy_service import find_remedies_for_group

remedies = find_remedies_for_group('$group', max_results=10)

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
"@
            
            try {
                & $pythonExe -c $groupScript
            } catch {
                Write-Host "Fehler: $_" -ForegroundColor Red
            }
        }
    }
    
    '3' {
        # Pathogen-Suche
        Write-Host ''
        $keyword = Read-Host 'Pathogen-Suchbegriff (z.B. staphylo, candida, herpes)'
        
        if (-not [string]::IsNullOrWhiteSpace($keyword)) {
            Write-Host ''
            Write-Host "Suche nach Pathogen '$keyword'..." -ForegroundColor Cyan
            Write-Host ''
            
            $pathogenScript = @"
import sys
sys.path.insert(0, '.')
from services.remedy_service import find_pathogens_by_keyword, get_remedies_for_pathogen

pathogens = find_pathogens_by_keyword('$keyword', max_results=5)

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
                print(f'     → {name}')
        print('')
else:
    print('Keine Pathogene gefunden.')
"@
            
            try {
                & $pythonExe -c $pathogenScript
            } catch {
                Write-Host "Fehler: $_" -ForegroundColor Red
            }
        }
    }
    
    '4' {
        # Statistik
        Write-Host ''
        Write-Host 'Datenbank-Statistik...' -ForegroundColor Cyan
        Write-Host ''
        
        $statsScript = @"
import sys
sys.path.insert(0, '.')
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
"@
        
        try {
            & $pythonExe -c $statsScript
        } catch {
            Write-Host "Fehler: $_" -ForegroundColor Red
        }
    }
    
    Default {
        Write-Host 'Beendet.' -ForegroundColor Gray
    }
}

Write-Host ''
Write-Host 'Druecken Sie eine beliebige Taste zum Beenden...'
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
