# ============================================================================
# Nacht-Batch: Remedy & Pathogen Beschreibungsgenerierung
# ============================================================================
# Datum: 27.11.2025
# Zweck: Generiert AI-Beschreibungen für alle Remedies & Pathogene über Nacht
# Dauer: ~8-12 Stunden (2606 Items!)
# ============================================================================

param(
    [int]$BatchSize = 50,           # Items pro Batch
    [int]$DelaySeconds = 2,         # Pause zwischen Batches (Ollama-Schonung)
    [switch]$RemediesToo = $true,   # Auch Remedies (nicht nur Pathogene)
    [switch]$DryRun = $false        # Nur anzeigen, was gemacht würde
)

# Farben für Output
$ColorSuccess = "Green"
$ColorInfo = "Cyan"
$ColorWarning = "Yellow"
$ColorError = "Red"

# Logging
$LogFile = "remedy_descriptions_night_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$StartTime = Get-Date

function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] $Message"
    Write-Host $LogMessage -ForegroundColor $Color
    Add-Content -Path $LogFile -Value $LogMessage
}

function Get-RemedyStats {
    $StatsScript = @"
import sys
sys.path.insert(0, '.')
from services.remedy_service import get_remedy_stats
stats = get_remedy_stats()
print(f"{stats['total_remedies']},{stats['remedies_without_description']},{stats['total_pathogens']}")
"@
    
    $Result = python -c $StatsScript 2>&1
    if ($LASTEXITCODE -eq 0) {
        $Parts = $Result -split ","
        return @{
            TotalRemedies = [int]$Parts[0]
            RemediesTodo = [int]$Parts[1]
            TotalPathogens = [int]$Parts[2]
        }
    }
    return $null
}

# ============================================================================
# START
# ============================================================================

Write-Log "============================================================================" $ColorInfo
Write-Log "NACHT-BATCH: REMEDY & PATHOGEN BESCHREIBUNGEN" $ColorInfo
Write-Log "============================================================================" $ColorInfo
Write-Log ""

if ($DryRun) {
    Write-Log "🔍 DRY-RUN-MODUS (keine Änderungen)" $ColorWarning
    Write-Log ""
}

# Prüfe Ollama
Write-Log "Prüfe Ollama-Verfügbarkeit..." $ColorInfo
try {
    $OllamaTest = ollama list 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Log "✅ Ollama verfügbar" $ColorSuccess
    } else {
        Write-Log "❌ Ollama nicht verfügbar!" $ColorError
        Write-Log "   Bitte starte Ollama: ollama serve" $ColorWarning
        exit 1
    }
} catch {
    Write-Log "❌ Ollama nicht installiert!" $ColorError
    exit 1
}

Write-Log ""

# Hole Statistiken
Write-Log "Hole Datenbank-Statistiken..." $ColorInfo
$Stats = Get-RemedyStats

if ($Stats) {
    Write-Log "📊 Aktuelle Statistiken:" $ColorInfo
    Write-Log "   Remedies gesamt: $($Stats.TotalRemedies)" $ColorInfo
    Write-Log "   Remedies ohne Beschreibung: $($Stats.RemediesTodo)" $ColorWarning
    Write-Log "   Pathogene gesamt: $($Stats.TotalPathogens)" $ColorInfo
    Write-Log ""
    
    $TotalTodo = $Stats.RemediesTodo + $Stats.TotalPathogens
    $EstimatedHours = [math]::Ceiling($TotalTodo / 300)  # ~300 Items/Stunde
    
    Write-Log "Geschätzte Dauer: ~$EstimatedHours Stunden" $ColorWarning
    Write-Log ""
} else {
    Write-Log "⚠️  Konnte Statistiken nicht laden" $ColorWarning
    Write-Log ""
}

if ($DryRun) {
    Write-Log "DRY-RUN beendet. Keine Änderungen vorgenommen." $ColorInfo
    exit 0
}

# ============================================================================
# PATHOGENE BESCHREIBUNGEN
# ============================================================================

Write-Log "============================================================================" $ColorInfo
Write-Log "PHASE 1: PATHOGEN-BESCHREIBUNGEN" $ColorInfo
Write-Log "============================================================================" $ColorInfo
Write-Log ""

Write-Log "Starte Pathogen-Beschreibungsgenerierung..." $ColorInfo
Write-Log "Batch-Größe: $BatchSize Items" $ColorInfo
Write-Log "Pause zwischen Batches: $DelaySeconds Sekunden" $ColorInfo
Write-Log ""

$PathogenScript = @"
import sys
sys.path.insert(0, '.')
from services.remedy_service import get_remedy_connection
from services.description_service import generate_description, save_description

# Hole alle Pathogene ohne Beschreibung
with get_remedy_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, p.name, p.pathogen_type, p.indication
        FROM pathogens p
        WHERE p.id NOT IN (
            SELECT pathogen_id FROM pathogen_descriptions
            WHERE description IS NOT NULL AND description != ''
        )
        ORDER BY p.pathogen_type, p.name
    ''')
    
    pathogens = cursor.fetchall()
    total = len(pathogens)
    
    print(f'Gefunden: {total} Pathogene ohne Beschreibung')
    
    for i, (pid, name, ptype, indication) in enumerate(pathogens, 1):
        print(f'[{i}/{total}] {name}')
        
        # Generiere Beschreibung
        prompt = f'''Beschreibe kurz und prägnant (max. 200 Wörter):

{name}

Typ: {ptype}
{indication if indication else ''}

Fokus auf:
- Energetische Eigenschaften
- Harmonisierungspotential
- Keine medizinischen Heilversprechen
- Rechtssichere Formulierung
'''
        
        try:
            description = generate_description(name, 'pathogen', custom_prompt=prompt)
            
            # Speichere in pathogen_descriptions Tabelle
            cursor.execute('''
                INSERT OR REPLACE INTO pathogen_descriptions (pathogen_id, description)
                VALUES (?, ?)
            ''', (pid, description))
            
            conn.commit()
            print(f'  ✅ Beschreibung generiert')
            
        except Exception as e:
            print(f'  ❌ Fehler: {e}')
        
        # Pause alle $BatchSize Items
        if i % $BatchSize == 0:
            import time
            time.sleep($DelaySeconds)
"@

try {
    python -c $PathogenScript
    if ($LASTEXITCODE -eq 0) {
        Write-Log "✅ Pathogen-Beschreibungen abgeschlossen" $ColorSuccess
    } else {
        Write-Log "⚠️  Pathogen-Beschreibungen mit Fehlern beendet" $ColorWarning
    }
} catch {
    Write-Log "❌ Fehler bei Pathogen-Beschreibungen: $_" $ColorError
}

Write-Log ""

# ============================================================================
# REMEDY BESCHREIBUNGEN (Optional)
# ============================================================================

if ($RemediesToo) {
    Write-Log "============================================================================" $ColorInfo
    Write-Log "PHASE 2: REMEDY-BESCHREIBUNGEN" $ColorInfo
    Write-Log "============================================================================" $ColorInfo
    Write-Log ""
    
    Write-Log "Starte Remedy-Beschreibungsgenerierung..." $ColorInfo
    Write-Log ""
    
    $RemedyScript = @"
import sys
sys.path.insert(0, '.')
from services.remedy_service import get_remedy_connection, list_all_remedies
from services.description_service import generate_description, save_description

# Hole alle Remedies ohne Beschreibung
remedies = list_all_remedies()
todo = [r for r in remedies if not r['description']]

print(f'Gefunden: {len(todo)} Remedies ohne Beschreibung')

for i, remedy in enumerate(todo, 1):
    print(f'[{i}/{len(todo)}] {remedy["name"]}')
    
    # Generiere Beschreibung
    prompt = f'''Beschreibe kurz und prägnant (max. 200 Wörter):

{remedy["name"]}

Kategorie: {remedy["category"]}
Indikation: {remedy["indication"] if remedy["indication"] else "Allgemein"}

Fokus auf:
- Energetische Wirkweise
- Harmonisierungspotential
- Traditionelle Anwendung
- Keine medizinischen Heilversprechen
- Rechtssichere Formulierung
'''
    
    try:
        description = generate_description(remedy["name"], 'remedy', custom_prompt=prompt)
        save_description(remedy["name"], description, 'remedy')
        print(f'  ✅ Beschreibung generiert')
        
    except Exception as e:
        print(f'  ❌ Fehler: {e}')
    
    # Pause alle $BatchSize Items
    if i % $BatchSize == 0:
        import time
        time.sleep($DelaySeconds)
"@
    
    try {
        python -c $RemedyScript
        if ($LASTEXITCODE -eq 0) {
            Write-Log "✅ Remedy-Beschreibungen abgeschlossen" $ColorSuccess
        } else {
            Write-Log "⚠️  Remedy-Beschreibungen mit Fehlern beendet" $ColorWarning
        }
    } catch {
        Write-Log "❌ Fehler bei Remedy-Beschreibungen: $_" $ColorError
    }
    
    Write-Log ""
}

# ============================================================================
# ABSCHLUSS
# ============================================================================

$EndTime = Get-Date
$Duration = $EndTime - $StartTime

Write-Log "============================================================================" $ColorInfo
Write-Log "NACHT-BATCH ABGESCHLOSSEN" $ColorSuccess
Write-Log "============================================================================" $ColorInfo
Write-Log ""
Write-Log "Startzeit: $($StartTime.ToString('yyyy-MM-dd HH:mm:ss'))" $ColorInfo
Write-Log "Endzeit: $($EndTime.ToString('yyyy-MM-dd HH:mm:ss'))" $ColorInfo
Write-Log "Dauer: $($Duration.Hours)h $($Duration.Minutes)m $($Duration.Seconds)s" $ColorInfo
Write-Log ""

# Finale Statistiken
$FinalStats = Get-RemedyStats
if ($FinalStats) {
    Write-Log "📊 Finale Statistiken:" $ColorSuccess
    Write-Log "   Remedies ohne Beschreibung: $($FinalStats.RemediesTodo)" $ColorInfo
    Write-Log ""
}

Write-Log "Log gespeichert: $LogFile" $ColorInfo
Write-Log "============================================================================" $ColorInfo

# Beep zum Abschluss (falls PC noch läuft)
[console]::beep(800,300)
[console]::beep(1000,300)
[console]::beep(1200,500)
