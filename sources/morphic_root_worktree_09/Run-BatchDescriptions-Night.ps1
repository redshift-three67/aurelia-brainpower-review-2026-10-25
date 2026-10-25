# ============================================================================
# Nacht-Batch: Beschreibungsgenerierung für alle Kategorien
# ============================================================================
# Datum: 27.11.2025
# Zweck: Generiert AI-Beschreibungen für alle Item-Kategorien über Nacht
# Dauer: ~6-10 Stunden (abhängig von Ollama-Performance)
# ============================================================================

param(
    [switch]$SkipCompleted = $true,  # Überspringe bereits fertige Kategorien
    [switch]$DryRun = $false         # Nur anzeigen, was gemacht würde
)

# Farben für Output
$ColorSuccess = "Green"
$ColorInfo = "Cyan"
$ColorWarning = "Yellow"
$ColorError = "Red"

# Kategorien in Reihenfolge (kleinste zuerst für schnelles Feedback)
$Categories = @(
    @{Name="bachblueten"; Status="✅ Fertig"; Skip=$true},
    @{Name="bakterien"; Status="✅ Fertig"; Skip=$true},
    @{Name="viren"; Status="⏳ Ausstehend"; Skip=$false},
    @{Name="pilze"; Status="⏳ Ausstehend"; Skip=$false},
    @{Name="parasiten"; Status="⏳ Ausstehend"; Skip=$false},
    @{Name="chakra"; Status="⏳ Ausstehend"; Skip=$false},
    @{Name="meridiane"; Status="⏳ Ausstehend"; Skip=$false},
    @{Name="wirbelsaeule"; Status="⏳ Ausstehend"; Skip=$false},
    @{Name="schmerz"; Status="⏳ Ausstehend"; Skip=$false},
    @{Name="organe"; Status="⏳ Ausstehend"; Skip=$false},
    @{Name="orthomolekular"; Status="⏳ Ausstehend"; Skip=$false},
    @{Name="homoeopathie"; Status="⏳ Ausstehend"; Skip=$false},
    @{Name="spagyrik"; Status="⏳ Ausstehend"; Skip=$false},
    @{Name="sonstige"; Status="⏳ Ausstehend"; Skip=$false},
    @{Name="bat_akut"; Status="⏳ Ausstehend (GROSS!)"; Skip=$false}  # Am Ende, weil am größten
)

# Logging
$LogFile = "batch_descriptions_night_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$StartTime = Get-Date

function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] $Message"
    Write-Host $LogMessage -ForegroundColor $Color
    Add-Content -Path $LogFile -Value $LogMessage
}

# ============================================================================
# START
# ============================================================================

Write-Log "============================================================================" $ColorInfo
Write-Log "NACHT-BATCH: Beschreibungsgenerierung gestartet" $ColorInfo
Write-Log "============================================================================" $ColorInfo
Write-Log "Startzeit: $StartTime" $ColorInfo
Write-Log "Log-Datei: $LogFile" $ColorInfo
Write-Log ""

# Prüfe Ollama-Verfügbarkeit
Write-Log "Prüfe Ollama-Verfügbarkeit..." $ColorInfo
try {
    $OllamaTest = python tools/batch_descriptions.py --test 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Log "✅ Ollama verfügbar und llama3.2:3b bereit" $ColorSuccess
    } else {
        Write-Log "❌ Ollama nicht verfügbar! Abbruch." $ColorError
        Write-Log "Ausgabe: $OllamaTest" $ColorError
        exit 1
    }
} catch {
    Write-Log "❌ Fehler beim Ollama-Test: $_" $ColorError
    exit 1
}

Write-Log ""

# Zeige Kategorien-Übersicht
Write-Log "============================================================================" $ColorInfo
Write-Log "KATEGORIEN-ÜBERSICHT" $ColorInfo
Write-Log "============================================================================" $ColorInfo

$TotalCategories = $Categories.Count
$CompletedCategories = ($Categories | Where-Object { $_.Skip -eq $true }).Count
$PendingCategories = $TotalCategories - $CompletedCategories

foreach ($Cat in $Categories) {
    $StatusColor = if ($Cat.Skip) { $ColorSuccess } else { $ColorWarning }
    Write-Log "  $($Cat.Status) $($Cat.Name)" $StatusColor
}

Write-Log ""
Write-Log "Gesamt: $TotalCategories Kategorien" $ColorInfo
Write-Log "Fertig: $CompletedCategories Kategorien" $ColorSuccess
Write-Log "Ausstehend: $PendingCategories Kategorien" $ColorWarning
Write-Log ""

if ($DryRun) {
    Write-Log "DRY-RUN-MODUS: Keine Änderungen werden vorgenommen." $ColorWarning
    Write-Log ""
}

# ============================================================================
# BATCH-GENERIERUNG
# ============================================================================

Write-Log "============================================================================" $ColorInfo
Write-Log "STARTE BATCH-GENERIERUNG" $ColorInfo
Write-Log "============================================================================" $ColorInfo
Write-Log ""

$ProcessedCount = 0
$SuccessCount = 0
$SkippedCount = 0
$ErrorCount = 0

foreach ($Cat in $Categories) {
    $CategoryName = $Cat.Name
    
    # Überspringe fertige Kategorien
    if ($SkipCompleted -and $Cat.Skip) {
        Write-Log "⏭️  Überspringe '$CategoryName' (bereits fertig)" $ColorInfo
        $SkippedCount++
        continue
    }
    
    $ProcessedCount++
    
    Write-Log ""
    Write-Log "────────────────────────────────────────────────────────────────────────" $ColorInfo
    Write-Log "[$ProcessedCount/$PendingCategories] KATEGORIE: $CategoryName" $ColorInfo
    Write-Log "────────────────────────────────────────────────────────────────────────" $ColorInfo
    
    $CategoryStartTime = Get-Date
    
    if ($DryRun) {
        Write-Log "  [DRY-RUN] Würde ausführen: python tools/batch_descriptions.py --category $CategoryName" $ColorWarning
        $SuccessCount++
    } else {
        try {
            Write-Log "  Starte Generierung..." $ColorInfo
            
            # Führe Batch-Generierung aus
            $Output = python tools/batch_descriptions.py --category $CategoryName 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                # Extrahiere Statistiken aus Output
                $GeneratedCount = 0
                if ($Output -match "Generierte Beschreibungen: (\d+)") {
                    $GeneratedCount = $Matches[1]
                }
                
                $CategoryEndTime = Get-Date
                $CategoryDuration = $CategoryEndTime - $CategoryStartTime
                
                Write-Log "  ✅ Erfolgreich abgeschlossen" $ColorSuccess
                Write-Log "     Generierte Beschreibungen: $GeneratedCount" $ColorSuccess
                Write-Log "     Dauer: $($CategoryDuration.ToString('hh\:mm\:ss'))" $ColorInfo
                
                $SuccessCount++
            } else {
                Write-Log "  ❌ Fehler bei Kategorie '$CategoryName'" $ColorError
                Write-Log "     Exit-Code: $LASTEXITCODE" $ColorError
                Write-Log "     Ausgabe: $Output" $ColorError
                
                $ErrorCount++
            }
        } catch {
            Write-Log "  ❌ Exception bei Kategorie '$CategoryName': $_" $ColorError
            $ErrorCount++
        }
    }
}

# ============================================================================
# ZUSAMMENFASSUNG
# ============================================================================

$EndTime = Get-Date
$TotalDuration = $EndTime - $StartTime

Write-Log ""
Write-Log "============================================================================" $ColorInfo
Write-Log "NACHT-BATCH ABGESCHLOSSEN" $ColorInfo
Write-Log "============================================================================" $ColorInfo
Write-Log "Endzeit: $EndTime" $ColorInfo
Write-Log "Gesamtdauer: $($TotalDuration.ToString('hh\:mm\:ss'))" $ColorInfo
Write-Log ""
Write-Log "STATISTIK:" $ColorInfo
Write-Log "  Verarbeitet: $ProcessedCount Kategorien" $ColorInfo
Write-Log "  Erfolgreich: $SuccessCount Kategorien" $ColorSuccess
Write-Log "  Übersprungen: $SkippedCount Kategorien" $ColorInfo
Write-Log "  Fehler: $ErrorCount Kategorien" $(if ($ErrorCount -gt 0) { $ColorError } else { $ColorSuccess })
Write-Log ""
Write-Log "Log-Datei: $LogFile" $ColorInfo
Write-Log "============================================================================" $ColorInfo

# Exit-Code basierend auf Erfolg
if ($ErrorCount -gt 0) {
    exit 1
} else {
    exit 0
}
