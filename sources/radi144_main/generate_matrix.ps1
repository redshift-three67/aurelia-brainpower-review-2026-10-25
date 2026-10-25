<#
.SYNOPSIS
    12x12 Resonance Matrix Generator (Dev Edition)
.DESCRIPTION
    Generiert eine 12x12 Resonanz-Matrix basierend auf Klienten-Daten und Fokus.
    Gibt die Matrix als visuelles Raster und als 144-stelligen Zahlen-String aus.
    Speichert Ergebnisse automatisch in 'dev_results.txt' und exportiert PDF/Excel.
#>

# 0. Global System & Encoding Setup
# Set terminal to UTF-8
chcp 65001 >$null

# Set encoding to UTF8 to handle special characters correctly
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

# k) Hintergrundfarbe: PowerShell-Blau, Grundschrift: Weiss
try {
    $Host.UI.RawUI.BackgroundColor = "DarkBlue"
    $Host.UI.RawUI.ForegroundColor = "White"
    Clear-Host
} catch { }

# ASCII-Umlaut Ersetzungen fuer Terminal-Ausgabe
$u_ae = "ae"  # ä
$u_ue = "ue"  # ü
$u_oe = "oe"  # ö
$u_ss = "ss"  # ß

# 1. Dependency Check
Write-Host "Pruefe System-Abhaengigkeiten..." -ForegroundColor DarkGray

function Resolve-Radi144PythonCommand {
    $Candidates = @(
        (Join-Path $PSScriptRoot ".venv\Scripts\python.exe"),
        (Join-Path $PSScriptRoot ".venv\bin\python"),
        "python",
        "py"
    )

    foreach ($Candidate in $Candidates) {
        try {
            if (($Candidate -like "*\python.exe" -or $Candidate -like "*/python") -and -not (Test-Path $Candidate)) {
                continue
            }
            & $Candidate --version 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) { return $Candidate }
        } catch { }
    }

    return $null
}

$PythonCommand = Resolve-Radi144PythonCommand
$PythonCommandExpression = if ($PythonCommand -and ($PythonCommand -match "\s")) { "`"$PythonCommand`"" } else { $PythonCommand }
$PythonCheck = if ($PythonCommand) { & $PythonCommand --version 2>$null } else { $null }
if ($null -eq $PythonCheck) {
    Write-Host "[FEHLER] Python nicht gefunden!" -ForegroundColor Red
    Write-Host "Bitte installieren Sie Python von https://python.org" -ForegroundColor Yellow
    Write-Host "Druecken Sie eine Taste zum Beenden..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

# Check for torch and reportlab
$Missing = @()
try { & $PythonCommand -c "import torch" 2>$null } catch { }
if ($LASTEXITCODE -ne 0) { $Missing += "torch (PyTorch)" }
try { & $PythonCommand -c "import reportlab" 2>$null } catch { }
if ($LASTEXITCODE -ne 0) { $Missing += "reportlab (PDF Export)" }

if ($Missing.Count -gt 0) {
    Write-Host "[INFO] Es fehlen Module: $($Missing -join ', ')" -ForegroundColor Yellow
    $Choice = Read-Host "Moechten Sie die Abhaengigkeiten jetzt automatisch installieren? (j/N)"
    if ($Choice -eq "j" -or $Choice -eq "J") {
        Write-Host "Starte Installation..." -ForegroundColor Cyan
        Start-Process "cmd.exe" "/c `"$PSScriptRoot\install_dependencies.bat`"" -Wait
        # Re-check after install
        Write-Host "Installation abgeschlossen. Bitte starten Sie das Skript erneut." -ForegroundColor Green
        pause
        exit
    }
}

# 2. Fenstertitel und Farbe
$Host.UI.RawUI.WindowTitle = "12x12 Resonance Dev Console v1.5.0 (Symmetry & Amplifier Edition)"
$Host.UI.RawUI.BackgroundColor = "Black"
$Host.UI.RawUI.ForegroundColor = "Cyan"

Clear-Host

# Session Persistence
$SessionFile = Join-Path $PSScriptRoot "last_session.json"
$Defaults = @{
    Surname = "Mustermann"
    Firstname = "Max"
    Dob = "01011990"
    Place = "Unbekannt"
    Planet = ""
}

if (Test-Path $SessionFile) {
    try {
        $SavedData = Get-Content $SessionFile -Raw | ConvertFrom-Json
        if ($SavedData.Surname) { $Defaults.Surname = $SavedData.Surname }
        if ($SavedData.Firstname) { $Defaults.Firstname = $SavedData.Firstname }
        if ($SavedData.Dob) { $Defaults.Dob = $SavedData.Dob }
        if ($SavedData.Place) { $Defaults.Place = $SavedData.Place }
        if ($SavedData.Planet) { $Defaults.Planet = $SavedData.Planet }
    } catch {
        Write-Host "Info: Konnte letzte Sitzung nicht laden." -ForegroundColor DarkGray
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   12x12 RESONANCE MATRIX GENERATOR     " -ForegroundColor Yellow
Write-Host "   Version 1.5.0 - Symmetry & Amplifier  " -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1.5 Template-Historie (Gespeicherte Konfigurationen)
# Phase-4 Adapter: bevorzugt stabile Runtime-Metadaten, faellt aber auf die alte lokale
# session_templates.json zurueck. Keine PowerShell-Neuschreibung, nur lesende Entkopplung.
$RuntimeDir = Join-Path $PSScriptRoot "data\runtime"
$RuntimeSessionFile = Join-Path $RuntimeDir "sessions.json"
$RuntimeTemplateFile = Join-Path $RuntimeDir "powershell_templates.json"
$LegacyTemplateFile = Join-Path $PSScriptRoot "data\session_templates.json"
$TemplateFile = $LegacyTemplateFile
$TemplateLoaded = $false

if (Test-Path $RuntimeSessionFile) {
    try {
        $env:RADI144_RUNTIME_DIR = $RuntimeDir
        & $PythonCommand -c "from app.services.session_archive_service import export_powershell_templates_from_runtime_dir; import os; export_powershell_templates_from_runtime_dir(os.environ['RADI144_RUNTIME_DIR'])" 2>$null | Out-Null
        if (Test-Path $RuntimeTemplateFile) {
            $TemplateFile = $RuntimeTemplateFile
            Write-Host "Runtime-Metadaten fuer Templates geladen (data/runtime)." -ForegroundColor DarkGray
        }
    } catch {
        Write-Host "Info: Runtime-Metadaten konnten nicht als PowerShell-Templates exportiert werden." -ForegroundColor DarkGray
    } finally {
        Remove-Item Env:\RADI144_RUNTIME_DIR -ErrorAction SilentlyContinue
    }
}

if ((-not (Test-Path $TemplateFile)) -and (Test-Path $LegacyTemplateFile)) {
    # Fallback: legacy session_templates.json
    $TemplateFile = $LegacyTemplateFile
}

if (Test-Path $TemplateFile) {
    try {
        $TemplateData = Get-Content $TemplateFile -Raw -Encoding UTF8 | ConvertFrom-Json
        $Templates = $TemplateData.templates
        
        if ($Templates -and $Templates.Count -gt 0) {
            Write-Host "Gespeicherte Konfigurationen gefunden:" -ForegroundColor Gray
            Write-Host " [0] Neue Konfiguration (manuell)" -ForegroundColor Green
            
            $MaxShow = [Math]::Min($Templates.Count, 21)
            for ($ti = 0; $ti -lt $MaxShow; $ti++) {
                $t = $Templates[$ti]
                $tDate = $t.timestamp
                $tName = $t.client_name
                $tFocus = if ($t.focus.Length -gt 30) { $t.focus.Substring(0, 30) + "..." } else { $t.focus }
                $tSym = switch ($t.symmetry) { "horizontal" { "Spiegel" } "quadrant" { "Mandala" } Default { "" } }
                $tAmp = if ($t.amplifier) { $t.amplifier } else { "" }
                $tMode = if ($t.mode -eq "precision") { "P" } else { "Q" }
                $tTplName = if ($t.template_name) { "[$($t.template_name)] " } else { "" }
                $tInfo = "${tTplName}$tDate | $tName | $tFocus"
                if ($tSym) { $tInfo += " | $tSym" }
                if ($tAmp) { $tInfo += " | $tAmp" }
                $tInfo += " | $tMode"
                Write-Host " [$($ti+1)] $tInfo" -ForegroundColor Cyan
            }
            
            $TplInput = Read-Host "Template waehlen (0-$MaxShow) [0]"
            if ([string]::IsNullOrWhiteSpace($TplInput)) { $TplInput = "0" }
            
            $TplIdx = [int]$TplInput
            if ($TplIdx -ge 1 -and $TplIdx -le $MaxShow) {
                $SelTemplate = $Templates[$TplIdx - 1]
                
                # Template-Werte uebernehmen
                $Defaults.Surname = $SelTemplate.surname
                $Defaults.Firstname = $SelTemplate.firstname
                $Defaults.Dob = $SelTemplate.dob
                $Defaults.Place = $SelTemplate.place
                $Defaults.Planet = $SelTemplate.planet
                
                # Konfigurationswerte merken
                $TplFocus = $SelTemplate.focus
                $TplWeight = $SelTemplate.weight
                $TplPalette = $SelTemplate.palette
                $TplMode = $SelTemplate.mode
                $TplHrv = $SelTemplate.hrv_sim
                $TplQuantum = $SelTemplate.quantum_active
                $TplPlanetary = $SelTemplate.use_planetary
                $TplEmf = $SelTemplate.emf_compensate
                $TplAmplifier = $SelTemplate.amplifier
                $TplSymmetry = $SelTemplate.symmetry
                
                $TemplateLoaded = $true
                Write-Host " -> Template geladen: $($SelTemplate.client_name) ($($SelTemplate.timestamp))" -ForegroundColor Green
                Write-Host ""
            }
        }
    } catch {
        Write-Host "Info: Template-Datei konnte nicht gelesen werden." -ForegroundColor DarkGray
    }
}

# 2.1 Analyse-Typ Auswahl
while ($true) {
    Write-Host "Waehlen Sie den Analyse-Typ:" -ForegroundColor Gray
    Write-Host " [1] Einzelklient (Standard)" -ForegroundColor Cyan
    Write-Host " [2] Gruppen-Analyse (Synergie)" -ForegroundColor Cyan
    Write-Host " [3] Geo-Resonanz (Haus, Grundstueck, Ort)" -ForegroundColor Cyan
    Write-Host " [4] Bild-Resonanz (Foto/Scan als Vektor)" -ForegroundColor Cyan
    $TypeChoice = Read-Host "Auswahl (1-4) [1]"
    if ([string]::IsNullOrWhiteSpace($TypeChoice)) { $TypeChoice = "1" }
    
    if ($TypeChoice -match "^[1-4]$") { break }
    Write-Host "[!] Bitte waehlen Sie 1, 2, 3 oder 4." -ForegroundColor Yellow
}

$SpecArgs = ""
$Surname = "Synergy"
$Firstname = "Group"
$Dob = "01011990"
$Place = "Unknown"
$Planet = ""

if ($TypeChoice -eq "1") {
    # --- Einzelklient Flow ---
    # 1. Nachname
    $Def = $Defaults.Surname
    $Surname = Read-Host "Name (Nachname) [$Def]"
    if ([string]::IsNullOrWhiteSpace($Surname)) { $Surname = $Def }

    # 2. Vorname
    $Def = $Defaults.Firstname
    $Firstname = Read-Host "Vorname [$Def]        "
    if ([string]::IsNullOrWhiteSpace($Firstname)) { $Firstname = $Def }

    # 3. Geburtsdatum
    $Def = $Defaults.Dob
    $Dob = Read-Host "Geburtsdatum [$Def]   "
    if ([string]::IsNullOrWhiteSpace($Dob)) { $Dob = $Def }

    # 4. Geburtsort
    $Def = $Defaults.Place
    $Place = Read-Host "Geburtsort [$Def]     "
    if ([string]::IsNullOrWhiteSpace($Place)) { $Place = $Def }

    # 5. Geburtsplanet
    $Def = $Defaults.Planet
    $PlanetLabel = if ($Def) { "[$Def]" } else { "(Optional)" }
    $Planet = Read-Host "Geburtsplanet $PlanetLabel"
    if ([string]::IsNullOrWhiteSpace($Planet)) { $Planet = $Def }
}
elseif ($TypeChoice -eq "2") {
    # --- Gruppen-Analyse Flow ---
    Write-Host ""
    Write-Host "Gruppen-Eingabe Methode:" -ForegroundColor Gray
    Write-Host " [1] JSON-Datei importieren" -ForegroundColor Cyan
    Write-Host " [2] TXT-Liste importieren (Nachname;Vorname;DDMMYYYY)" -ForegroundColor Cyan
    Write-Host " [3] Manuelle Eingabe (Schritt-fuer-Schritt)" -ForegroundColor Cyan
    $GroupMethod = Read-Host "Auswahl (1-3) [1]"
    
    if ($GroupMethod -eq "2") {
        $TxtPath = Read-Host "Pfad zur .txt Datei"
        if (Test-Path $TxtPath) {
            $Lines = Get-Content $TxtPath
            $GroupMembers = @()
            foreach ($Line in $Lines) {
                if ($Line -match ";") {
                    $P = $Line.Split(";")
                    $GroupMembers += @{
                        last_names = @($P[0].Trim())
                        first_name = $P[1].Trim()
                        birth_date = $P[2].Trim()
                        birth_place = if ($P.Count -gt 3) { $P[3].Trim() } else { "Unbekannt" }
                    }
                }
            }
            $JsonPath = Join-Path $PSScriptRoot "temp_group.json"
            $GroupMembers | ConvertTo-Json | Set-Content $JsonPath -Encoding utf8
            $SpecArgs = "--group `"$JsonPath`""
        }
    }
    elseif ($GroupMethod -eq "3") {
        $GroupMembers = @()
        Write-Host "Geben Sie die Mitglieder ein (LEERE ZEILE bei Nachname zum Beenden):" -ForegroundColor Yellow
        while ($true) {
            $gLname = Read-Host " Nachname"
            if ([string]::IsNullOrWhiteSpace($gLname)) { break }
            $gFname = Read-Host " Vorname "
            $gDob   = Read-Host " Geburtsdatum (DDMMYYYY)"
            $gPlace = Read-Host " Geburtsort"
            $GroupMembers += @{
                last_names = @($gLname)
                first_name = $gFname
                birth_date = $gDob
                birth_place = $gPlace
            }
        }
        if ($GroupMembers.Count -gt 0) {
            $SaveChoice = Read-Host "Als JSON speichern? (j/N)"
            $JsonPath = Join-Path $PSScriptRoot "temp_group.json"
            if ($SaveChoice -eq "j") {
                $SaveName = Read-Host "Dateiname (ohne .json)"
                $JsonPath = Join-Path $PSScriptRoot "$SaveName.json"
            }
            $GroupMembers | ConvertTo-Json | Set-Content $JsonPath -Encoding utf8
            $SpecArgs = "--group `"$JsonPath`""
        }
    }
    else {
        $GroupPath = Read-Host "Pfad zur .json Datei"
        if (Test-Path $GroupPath) { $SpecArgs = "--group `"$GroupPath`"" }
    }
    $Firstname = "Gruppe"
    $Surname = "Analyse"
}
elseif ($TypeChoice -eq "3") {
    # --- Geo-Resonanz Flow ---
    Write-Host ""
    Write-Host "Geo-Daten Eingabe:" -ForegroundColor Gray
    Write-Host " [Oeffne Google Maps...]" -ForegroundColor DarkGray
    Start-Process "https://www.google.com/maps"
    $LatLon = Read-Host "Koordinaten (Lat,Lon)"
    $Radius = Read-Host "Umkreis-Radius in Metern [0]"
    if ([string]::IsNullOrWhiteSpace($Radius)) { $Radius = "0" }
    
    # Geo-Label: Eindeutiger Name fuer diesen Geo-Punkt
    $GeoLabel = Read-Host "Bezeichnung/Label fuer diesen Ort (z.B. 'Praxis Muenchen')"
    if ([string]::IsNullOrWhiteSpace($GeoLabel)) { $GeoLabel = "Geo-Punkt $LatLon" }
    
    $SpecArgs = "--coords `"$LatLon,$Radius`""
    $Firstname = $GeoLabel
    $Surname = ""
    Write-Host " -> Geo-Label: $GeoLabel" -ForegroundColor Green
}
elseif ($TypeChoice -eq "4") {
    # --- Bild-Resonanz Flow ---
    Write-Host ""
    Write-Host "Bild-Resonanz:" -ForegroundColor Gray
    Write-Host " Unterstuetzte Formate: JPG, PNG, BMP, TIFF" -ForegroundColor DarkGray
    
    # Datei-Dialog oeffnen
    Add-Type -AssemblyName System.Windows.Forms
    $OpenDialog = New-Object System.Windows.Forms.OpenFileDialog
    $OpenDialog.Title = "Bild fuer Resonanz-Analyse waehlen"
    $OpenDialog.Filter = "Bilder (*.jpg;*.jpeg;*.png;*.bmp;*.tiff)|*.jpg;*.jpeg;*.png;*.bmp;*.tiff|Alle Dateien (*.*)|*.*"
    $OpenDialog.InitialDirectory = [Environment]::GetFolderPath("MyPictures")
    
    $DialogResult = $OpenDialog.ShowDialog()
    if ($DialogResult -eq [System.Windows.Forms.DialogResult]::OK) {
        $ImagePath = $OpenDialog.FileName
        $ImageLabel = [System.IO.Path]::GetFileNameWithoutExtension($ImagePath)
        Write-Host " -> Bild: $ImageLabel" -ForegroundColor Green
        Write-Host " -> Pfad: $ImagePath" -ForegroundColor DarkGray
        $SpecArgs = "--image-path `"$ImagePath`""
        $Firstname = $ImageLabel
        $Surname = ""
    } else {
        Write-Host " [!] Kein Bild gewaehlt. Breche ab." -ForegroundColor Red
        exit
    }
}

# 2.2 Planetare Resonanz Toggle
Write-Host ""
$PlanetaryInput = Read-Host "Planetare Resonanz in Analyse einbeziehen? (j/N)"
$PlanetaryFlag = if ($PlanetaryInput -eq "j" -or $PlanetaryInput -eq "J") { "--use-planetary" } else { "" }

# 2.3 Datenbank-Vorwahl (Wissensfelder & Scan)
$DbImportDir = Join-Path $PSScriptRoot "db_import"
if (-not (Test-Path $DbImportDir)) { New-Item -Path $DbImportDir -ItemType Directory | Out-Null }
# Rekursive Suche nach .txt Dateien inkl. Unterordnern
$DbFiles = Get-ChildItem -Path $DbImportDir -Filter "*.txt" -Recurse

$AutoFocus = $null
$SelectedDbPath = $null

if ($DbFiles) {
    Write-Host ""
    
    # --- DB-Vorauswahl: Top-5 passende Datenbanken empfehlen ---
    Write-Host "Moechten Sie zuerst die passendsten Datenbanken zum Vektor ermitteln?" -ForegroundColor Cyan
    $DbPreChoice = Read-Host " (j/N)"
    if ($DbPreChoice -eq "j" -or $DbPreChoice -eq "J") {
        Write-Host ""
        $ExtraFocus = Read-Host " Optionaler Extra-Fokus fuer die DB-Empfehlung (leer = nur Vektor)"
        
        Write-Host " Scanne $($DbFiles.Count) Datenbanken gegen den Vektor..." -ForegroundColor Cyan
        
        # Konstruiere Scan-Params
        $PreScanParams = @()
        if (-not [string]::IsNullOrWhiteSpace($Surname))   { $PreScanParams += "--surname `"$Surname`"" }
        if (-not [string]::IsNullOrWhiteSpace($Firstname)) { $PreScanParams += "--firstname `"$Firstname`"" }
        if (-not [string]::IsNullOrWhiteSpace($Dob))       { $PreScanParams += "--dob `"$Dob`"" }
        if (-not [string]::IsNullOrWhiteSpace($Place))     { $PreScanParams += "--place `"$Place`"" }
        if (-not [string]::IsNullOrWhiteSpace($Planet))    { $PreScanParams += "--planet `"$Planet`"" }
        if (-not [string]::IsNullOrWhiteSpace($PlanetaryFlag)) { $PreScanParams += $PlanetaryFlag }
        if (-not [string]::IsNullOrWhiteSpace($SpecArgs)) { $PreScanParams += $SpecArgs }
        if (-not [string]::IsNullOrWhiteSpace($ExtraFocus)) { $PreScanParams += "--focus `"$ExtraFocus`"" }
        
        # DB-Pfade in Temp-Datei schreiben (vermeidet Kommandozeilen-Laengenlimit)
        $DbListFile = Join-Path $PSScriptRoot "_temp_db_list.txt"
        $DbFiles | ForEach-Object { $_.FullName } | Set-Content -Path $DbListFile -Encoding UTF8
        
        $PreScanScript = Join-Path $PSScriptRoot "dev_cli.py"
        $PreScanFullCmd = "$PythonCommandExpression `"$PreScanScript`" " + ($PreScanParams -join " ") + " --db-rank-file `"$DbListFile`" 2>&1"
        
        $PreScanOutput = Invoke-Expression $PreScanFullCmd | Out-String
        
        # Temp-Datei aufraeumen
        if (Test-Path $DbListFile) { Remove-Item $DbListFile -Force }
        
        $RankedDbPaths = @()
        if ($PreScanOutput -match "(?s)###DBRANK###(.+?)###ENDDBRANK###") {
            $RankedDbs = $Matches[1].Trim()
            Write-Host ""
            Write-Host " Top-5 passendste Datenbanken:" -ForegroundColor Green
            $RankIdx = 1
            foreach ($line in $RankedDbs.Split("`n")) {
                if (-not [string]::IsNullOrWhiteSpace($line)) {
                    Write-Host "  [$RankIdx] $($line.Trim())" -ForegroundColor Cyan
                    # Extrahiere DB-Dateinamen aus der Zeile (Format: "0.1234 | dateiname.txt (N Eintraege)")
                    if ($line -match "\|\s*(.+?\.txt)") {
                        $RankedName = $Matches[1].Trim()
                        $FoundFile = $DbFiles | Where-Object { $_.Name -eq $RankedName } | Select-Object -First 1
                        if ($FoundFile) { $RankedDbPaths += $FoundFile.FullName }
                    }
                    $RankIdx++
                }
            }
            Write-Host ""
            Write-Host " [0] Keine / Komplette DB-Liste anzeigen" -ForegroundColor DarkGray
            Write-Host ""
            $RankChoice = Read-Host " Top-5 Auswahl (1-5) oder [0] fuer volle Liste [0]"
            if ($RankChoice -match "^[1-5]$" -and [int]$RankChoice -le $RankedDbPaths.Count) {
                $SelectedDbPath = $RankedDbPaths[[int]$RankChoice - 1]
                Write-Host " -> DB gewaehlt: $(Split-Path $SelectedDbPath -Leaf)" -ForegroundColor Magenta
            }
        } else {
            Write-Host " [!] DB-Ranking konnte nicht ermittelt werden." -ForegroundColor Yellow
            Write-Host " Debug: $PreScanOutput" -ForegroundColor DarkGray
        }
    }
    
    # Nur volle Liste zeigen wenn noch keine DB gewaehlt wurde
    if (-not $SelectedDbPath) {
        Write-Host "Wissens-Datenbanken (Vektorisierung & Scan):" -ForegroundColor Gray
        Write-Host " [0] Keine (Nur Manueller Fokus)" -ForegroundColor Cyan
        
        # Strukturierte Anzeige: Gruppiert nach Unterordnern
        $d = 1
        $LastCategory = ""
        foreach ($File in ($DbFiles | Sort-Object DirectoryName, Name)) {
            $RelDir = $File.DirectoryName.Replace($DbImportDir, "").TrimStart("\")
            if (-not $RelDir) { $RelDir = "(Stammverzeichnis)" }
            
            # Kategorie-Header nur bei Wechsel anzeigen
            if ($RelDir -ne $LastCategory) {
                Write-Host ""
                Write-Host "  --- $RelDir ---" -ForegroundColor Yellow
                $LastCategory = $RelDir
            }
            Write-Host " [$d] $($File.Name)" -ForegroundColor Cyan
            $d++
        }
        # DbFiles neu sortieren damit Index uebereinstimmt
        $DbFiles = $DbFiles | Sort-Object DirectoryName, Name
        
        Write-Host ""
        $DbChoice = Read-Host "Auswahl (0-$($DbFiles.Count)) [0]"
        if ($DbChoice -match "^\d+$" -and [int]$DbChoice -gt 0 -and [int]$DbChoice -le $DbFiles.Count) {
            $SelectedDbPath = $DbFiles[[int]$DbChoice - 1].FullName
            Write-Host " -> DB gewaehlt: $($DbFiles[[int]$DbChoice - 1].Name)" -ForegroundColor Magenta
        }
    }
    
    if ($SelectedDbPath) {
        
        Write-Host " Datenbank nach Top-Resonanzen scannen?" -ForegroundColor Cyan
        $ScanChoice = Read-Host " (J/n)"
        if ([string]::IsNullOrWhiteSpace($ScanChoice)) { $ScanChoice = "j" }
        
        if ($ScanChoice -eq "j" -or $ScanChoice -eq "J") {
            # Top-N Auswahl
            Write-Host "" 
            Write-Host " Wie viele Top-Resonanzen ermitteln?" -ForegroundColor Cyan
            Write-Host "  [1] Top-1  (staerkste Einzelresonanz)" -ForegroundColor DarkCyan
            Write-Host "  [2] Top-5  (kompakte Auswahl)" -ForegroundColor DarkCyan
            Write-Host "  [3] Top-9  (mittlere Tiefe)" -ForegroundColor DarkCyan
            Write-Host "  [4] Top-21 (volle Analyse)" -ForegroundColor DarkCyan
            $TopNChoice = Read-Host " Auswahl (1-4) [4]"
            if ([string]::IsNullOrWhiteSpace($TopNChoice)) { $TopNChoice = "4" }
            switch ($TopNChoice) {
                "1" { $TopN = 1 }
                "2" { $TopN = 5 }
                "3" { $TopN = 9 }
                default { $TopN = 21 }
            }
            Write-Host " -> Top-$TopN Analyse gewaehlt" -ForegroundColor Green
            
            Write-Host " Starte Datenbank-Scan gegen den definierten Vektor..." -ForegroundColor Cyan
            
            # Konstruiere vorlaeufige Params fuer den Scan
            $ScanParams = @()
            if (-not [string]::IsNullOrWhiteSpace($Surname))   { $ScanParams += "--surname `"$Surname`"" }
            if (-not [string]::IsNullOrWhiteSpace($Firstname)) { $ScanParams += "--firstname `"$Firstname`"" }
            if (-not [string]::IsNullOrWhiteSpace($Dob))       { $ScanParams += "--dob `"$Dob`"" }
            if (-not [string]::IsNullOrWhiteSpace($Place))     { $ScanParams += "--place `"$Place`"" }
            if (-not [string]::IsNullOrWhiteSpace($Planet))    { $ScanParams += "--planet `"$Planet`"" }
            if (-not [string]::IsNullOrWhiteSpace($PlanetaryFlag)) { $ScanParams += $PlanetaryFlag }
            if (-not [string]::IsNullOrWhiteSpace($SpecArgs)) { $ScanParams += $SpecArgs }
            
            $ScanScriptPath = Join-Path $PSScriptRoot "dev_cli.py"
            $ScanCommand = "$PythonCommandExpression `"$ScanScriptPath`" " + ($ScanParams -join " ") + " --db-path `"$SelectedDbPath`" --db-scan --db-top-n $TopN"
            
            # Fuehre Scan aus und fange Output ab (Out-String sorgt fuer ein zusammenhaengendes Ergebnis)
            $ScanOutput = Invoke-Expression $ScanCommand | Out-String
            
            # Extrahiere Top-N aus dem Output
            if ($ScanOutput -match "###TOP21###(.*)###ENDTOP21###") {
                $AutoFocus = $Matches[1].Trim()
                Write-Host " -> Top-$TopN Resonanzen erfolgreich ermittelt." -ForegroundColor Green
                
                # Praefix-Option: Vor Uebernahme als Fokusse
                Write-Host ""
                Write-Host " Praefix fuer die Resonanzen voranstellen?" -ForegroundColor Cyan
                Write-Host " (z.B. 'Heilung:', 'Chakra:', oder leer lassen fuer kein Praefix)" -ForegroundColor DarkGray
                $FocusPrefix = Read-Host " Praefix [kein]"
                if (-not [string]::IsNullOrWhiteSpace($FocusPrefix)) {
                    $FocusPrefix = $FocusPrefix.Trim()
                    # Praefix an jeden Fokus-Eintrag voranstellen
                    $PrefixedItems = @()
                    foreach ($item in $AutoFocus.Split(";")) {
                        if (-not [string]::IsNullOrWhiteSpace($item)) {
                            $PrefixedItems += "$FocusPrefix $($item.Trim())"
                        }
                    }
                    $AutoFocus = $PrefixedItems -join ";"
                    Write-Host " -> Praefix '$FocusPrefix' angewendet auf $($PrefixedItems.Count) Fokusse" -ForegroundColor Green
                }
            } else {
                Write-Host " [!] Fehler beim DB-Scan oder keine Resonanzen gefunden." -ForegroundColor Yellow
                Write-Host " Debug-Info: $ScanOutput" -ForegroundColor DarkGray
            }
        } else {
            # Wenn kein Scan gewuenscht, DB nur als Pfad uebergeben (wie frueher)
            $SpecArgs += " --db-path `"$SelectedDbPath`""
        }
    }
}

# Save Session (Nur bei Einzelklient sinnvoll fuer Wiederholung)
if ($TypeChoice -eq "1") {
    $NewSession = @{
        Surname = $Surname
        Firstname = $Firstname
        Dob = $Dob
        Place = $Place
        Planet = $Planet
    }
    $NewSession | ConvertTo-Json | Set-Content $SessionFile
}

# 5. Fokus Auswahl
Write-Host ""
Write-Host "--- Fokus Eingabe ---" -ForegroundColor Yellow

# History Datei setup (Immer definieren, da spaeter fuer Update benoetigt)
$HistoryFile = Join-Path $PSScriptRoot "focus_history.txt"
if (-not (Test-Path $HistoryFile)) {
    New-Item -Path $HistoryFile -ItemType File -Force | Out-Null
}

$FocusList = @()

# Template-Fokus anbieten (wenn Template geladen und Fokus vorhanden)
if ($TemplateLoaded -and -not [string]::IsNullOrWhiteSpace($TplFocus)) {
    $TplFocusParts = $TplFocus -split ";" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    Write-Host "Gespeicherte Fokus-Themen aus Template ($($TplFocusParts.Count) Themen):" -ForegroundColor Magenta
    $fi = 1
    foreach ($tf in $TplFocusParts) {
        Write-Host "  [$fi] $tf" -ForegroundColor DarkCyan
        $fi++
    }
    Write-Host ""
    Write-Host " [J] Alle uebernehmen  [N] Neu eingeben  [E] Editieren" -ForegroundColor Gray
    $TplFocusChoice = Read-Host " Auswahl (J/N/E) [J]           "
    if ([string]::IsNullOrWhiteSpace($TplFocusChoice)) { $TplFocusChoice = "J" }
    
    if ($TplFocusChoice -eq "J" -or $TplFocusChoice -eq "j") {
        $FocusList = @($TplFocusParts)
        Write-Host " -> $($FocusList.Count) Fokus-Themen aus Template uebernommen." -ForegroundColor Green
    } elseif ($TplFocusChoice -eq "E" -or $TplFocusChoice -eq "e") {
        # Editier-Modus: Jedes Thema einzeln bestaetigen/editieren/entfernen
        foreach ($tf in $TplFocusParts) {
            Write-Host "  Fokus: '$tf'" -ForegroundColor Cyan
            $EditF = Read-Host "  Editieren/ENTER=behalten/'-'=entfernen"
            if ($EditF -eq "-") {
                Write-Host "    -> Entfernt." -ForegroundColor DarkGray
            } elseif (-not [string]::IsNullOrWhiteSpace($EditF)) {
                $FocusList += $EditF
                Write-Host "    -> Geaendert: '$EditF'" -ForegroundColor Green
            } else {
                $FocusList += $tf
                Write-Host "    -> Beibehalten." -ForegroundColor DarkCyan
            }
        }
        Write-Host " -> $($FocusList.Count) Fokus-Themen nach Bearbeitung." -ForegroundColor Green
    }
    # Bei "N" bleibt FocusList leer -> normale Eingabe folgt
}

if ($FocusList.Count -eq 0 -and -not [string]::IsNullOrWhiteSpace($AutoFocus)) {
    Write-Host "Vorschlag: Nutze Top-21 Resonanzen aus dem DB-Scan als Fokus?" -ForegroundColor Gray
    $UseScan = Read-Host " (J/n)"
    if ([string]::IsNullOrWhiteSpace($UseScan)) { $UseScan = "j" }
    
    if ($UseScan -eq "j" -or $UseScan -eq "J") {
        $FocusList = $AutoFocus.Split(";")
        Write-Host " -> Top-21 geladen." -ForegroundColor Magenta
    }
}

if ($FocusList.Count -eq 0) {
    Write-Host "Optionen:" -ForegroundColor Gray
    Write-Host " - Einzeilige Texte oder Nummer (z.B. '1' fuer Harmonisierung)" -ForegroundColor Gray
    Write-Host " - Mehrzeiliger Text / Copy & Paste (wird automatisch in Einzel-Fokusse zerlegt)" -ForegroundColor Gray
    Write-Host " - Maximale Anzahl Fokus-Themen: 42 (FIFO)" -ForegroundColor DarkGray
    Write-Host " - LEERE ZEILE zum Abschliessen und Starten der Analyse" -ForegroundColor Green
    Write-Host ""
    
    # Standard Themen definieren
    $FocusOptions = @("Harmonisierung", "Vitalitaet", "Klarheit", "Schutz", "Blockadenloesung", "Erfolg", "Liebe", "Fuelle")
    
    # History laden und unique Eintraege hinzufuegen
    $History = Get-Content $HistoryFile -Encoding UTF8 -ErrorAction SilentlyContinue
    if ($History) {
        # Nimm die letzten 10 einzigartigen Eintraege, die nicht in Standard sind
        $RecentUnique = $History | Select-Object -Unique | Where-Object { $FocusOptions -notcontains $_ } | Select-Object -Last 10
        if ($RecentUnique) {
            $FocusOptions += $RecentUnique
        }
    }
    
    # Custom Option am Ende
    $FocusOptions += ">> EIGENER FOKUS (Neu eingeben)..."
    
    # Schnell-Auswahl anzeigen
    Write-Host "Historie / Vorlagen:" -ForegroundColor Gray
    $i = 1
    foreach ($Opt in $FocusOptions) {
        Write-Host " [$i] $Opt" -ForegroundColor Cyan
        $i++
    }
    Write-Host ""
    
    while ($true) {
        $Prompt = " Fokus $($FocusList.Count + 1)"
        if ($FocusList.Count -gt 0) { $Prompt += " [ENTER zum Starten]" }
        $Line = Read-Host "$Prompt"
        
        if ([string]::IsNullOrWhiteSpace($Line)) { break }
        
        # Check if number was entered (Selection/Edit mode)
        if ($Line -match "^\d+$") {
            $Idx = [int]$Line - 1
            if ($Idx -ge 0 -and $Idx -lt $FocusOptions.Count) {
                $Selected = $FocusOptions[$Idx]
                if ($Selected -match ">> EIGENER FOKUS") {
                    $Line = Read-Host " >> Bitte neuen Fokus eingeben"
                } else {
                    # Editable focus selection
                    Write-Host " -> Gew$($u_ae)hlt: '$Selected'" -ForegroundColor Cyan
                    $EditLine = Read-Host " Fokus editieren oder ENTER zur Best$($u_ae)tigung"
                    $Line = if ([string]::IsNullOrWhiteSpace($EditLine)) { $Selected } else { $EditLine }
                }
            }
        }
    
        # Handle potentially pasted multi-line text or semicolon separated strings
        $Parts = $Line -split "[\r\n;]+" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
        
        foreach ($Part in $Parts) {
            $Cleaned = $Part.Trim()
            if (-not [string]::IsNullOrWhiteSpace($Cleaned)) {
                $FocusList += $Cleaned
                Write-Host "   [OK] Hinzugef$($u_ue)gt: $Cleaned" -ForegroundColor DarkCyan
                
                # FIFO: Limit total list to 42
                if ($FocusList.Count -gt 42) {
                    $Oldest = $FocusList[0]
                    $FocusList = $FocusList[1..($FocusList.Count-1)]
                    Write-Host "   [FIFO] Limit von 42 erreicht. '$Oldest' wurde entfernt." -ForegroundColor Yellow
                }
            }
        }
    }
}

if ($FocusList.Count -eq 0) {
    $Focus = "Harmonisierung"
} else {
    $Focus = $FocusList -join ";"
}

# Update History (FIFO - Keep only last 10 unique, exclude defaults)
foreach ($F in ($Focus -split ";")) {
    $History = Get-Content $HistoryFile -Encoding UTF8 -ErrorAction SilentlyContinue
    if ($null -eq $History) { $History = @() }
    
    # If already in history, remove it first to move it to the end (FIFO/LIFO mix for recent items)
    $History = $History | Where-Object { $_ -ne $F }
    
    # Add new item if not a standard option
    if ($FocusOptions -notcontains $F) {
        $History += $F
        # Limit history to 42
        if ($History.Count -gt 42) { $History = $History | Select-Object -Last 42 }
        Set-Content -Path $HistoryFile -Value $History -Encoding UTF8
    }
}

Write-Host " -> Gewaehlt: $Focus" -ForegroundColor Green

# === KONFIGURATION: Template-Override ODER manuelle Eingabe ===

if ($TemplateLoaded) {
    # Template-Werte direkt uebernehmen
    $Weight = $TplWeight
    $PaletteName = $TplPalette
    $CalcMode = $TplMode
    $HrvSimFlag = if ($TplHrv -eq $true) { "--hrv-sim" } else { "" }
    $QuantumFlag = if ($TplQuantum -eq $true) { "--quantum-active" } else { "" }
    $EmfFlag = if ($TplEmf -eq $true) { "--emf-compensate" } else { "" }
    $AmplifierArg = if ($TplAmplifier) { "--amplifier `"$TplAmplifier`"" } else { "" }
    $SymmetryArg = if ($TplSymmetry -and $TplSymmetry -ne "none") { "--symmetry $TplSymmetry" } else { "" }
    $MatrixSize = if ($SelTemplate.matrix_size) { [int]$SelTemplate.matrix_size } else { 12 }
    $MatrixSizeArg = if ($MatrixSize -ne 12) { "--matrix-size $MatrixSize" } else { "" }
    
    # Template-Konfiguration anzeigen
    Write-Host "Template-Konfiguration:" -ForegroundColor Yellow
    Write-Host "  Matrix:        ${MatrixSize}x${MatrixSize}" -ForegroundColor DarkCyan
    Write-Host "  Gewichtung:    $Weight" -ForegroundColor DarkCyan
    Write-Host "  Palette:       $PaletteName" -ForegroundColor DarkCyan
    Write-Host "  Modus:         $CalcMode" -ForegroundColor DarkCyan
    if ($HrvSimFlag) { Write-Host "  HRV-Sim:       Aktiv" -ForegroundColor DarkCyan }
    if ($QuantumFlag) { Write-Host "  Quantum:       Aktiv" -ForegroundColor DarkCyan }
    if ($EmfFlag) { Write-Host "  EMF-Komp.:     Aktiv" -ForegroundColor DarkCyan }
    if ($AmplifierArg) { Write-Host "  Verstaerker:   $TplAmplifier" -ForegroundColor DarkCyan }
    if ($SymmetryArg) { Write-Host "  Symmetrie:     $TplSymmetry" -ForegroundColor DarkCyan }
    Write-Host ""
    
} else {

# 5.5 Matrix-Groesse (mit Hardware-Auto-Detect)
Write-Host ""
Write-Host "Matrix-Groesse waehlen:" -ForegroundColor Gray
Write-Host " [1] 12x12 (Standard - 144 Zellen)" -ForegroundColor Green
Write-Host " [2] 24x24 (Erweitert - 576 Zellen)" -ForegroundColor Cyan

# Hardware-Erkennung: GPU VRAM pruefen fuer 36x36
$Has36x36 = $false
try {
    $GpuCheck = & $PythonCommand -c "import torch; vram=torch.cuda.get_device_properties(0).total_memory/(1024**3) if torch.cuda.is_available() else 0; print(f'{vram:.1f}')" 2>$null
    if ($LASTEXITCODE -eq 0 -and $GpuCheck) {
        $VramGb = [double]$GpuCheck
        if ($VramGb -ge 8.0) {
            $Has36x36 = $true
            Write-Host " [3] 36x36 (Server/RTX - 1296 Zellen) [GPU: $($VramGb.ToString('0.0')) GB VRAM]" -ForegroundColor Yellow
        }
    }
} catch { }

if (-not $Has36x36) {
    Write-Host " [3] 36x36 (nicht verfuegbar - benoetigt GPU >= 8 GB VRAM)" -ForegroundColor DarkGray
}

$MatrixInput = Read-Host "Auswahl (1-3) [1]           "
$MatrixSize = 12
$MatrixSizeArg = ""
if ($MatrixInput -eq "2") {
    $MatrixSize = 24
    $MatrixSizeArg = "--matrix-size 24"
    Write-Host " -> Matrix: 24x24 (576 Zellen)" -ForegroundColor Green
} elseif ($MatrixInput -eq "3" -and $Has36x36) {
    $MatrixSize = 36
    $MatrixSizeArg = "--matrix-size 36"
    Write-Host " -> Matrix: 36x36 (1296 Zellen, Server-GPU)" -ForegroundColor Yellow
} elseif ($MatrixInput -eq "3" -and -not $Has36x36) {
    Write-Host " [!] 36x36 nicht verfuegbar auf dieser Hardware. Nutze 12x12." -ForegroundColor Red
} else {
    Write-Host " -> Matrix: 12x12 (Standard)" -ForegroundColor Green
}

# 6. Gewichtung
Write-Host ""
Write-Host "Fokus Gewichtung:" -ForegroundColor Gray
Write-Host " [0] Deaktiviert        - Rein objektive Analyse (0.0)" -ForegroundColor Gray
Write-Host " [1] Sanft              - Subtile Einflusnahme (0.4)" -ForegroundColor Cyan
Write-Host " [2] Normal (Standard)  - Ausgewogene Balance (1.0)" -ForegroundColor Green
Write-Host " [3] Stark              - Dominante Priorisierung (1.5)" -ForegroundColor Red
$WeightInput = Read-Host "Auswahl (0-3) [2]           "

switch ($WeightInput) {
    "0" { $Weight = "Deaktiviert" }
    "1" { $Weight = "Sanft" }
    "3" { $Weight = "Stark" }
    Default { $Weight = "Normal" }
}

# 7. Farbpalette
$PaletteFile = Join-Path $PSScriptRoot "palettes.json"
$PaletteName = "Radionik (Standard)"

if (Test-Path $PaletteFile) {
    try {
        $Json = Get-Content $PaletteFile -Raw -Encoding UTF8 | ConvertFrom-Json
        $PaletteNames = $Json.PSObject.Properties.Name
        
        Write-Host ""
        Write-Host "Farbpalette waehlen:" -ForegroundColor Gray
        $i = 1
        $PaletteList = @()
        
        foreach ($Name in $PaletteNames) {
            Write-Host " [$i] $Name" -ForegroundColor Cyan
            $PaletteList += $Name
            $i++
        }
        Write-Host " [$i] Natur Heilsam - Wald/Erde/Himmel/Moos/Nebel/Morgenrot" -ForegroundColor DarkGreen
        $PaletteList += "Natur Heilsam"
        $i++
        Write-Host " [$i] Unified Coherent - Optimal (Client+Alle Fokusse monochrom)" -ForegroundColor White
        $PaletteList += "Unified Coherent"
        $DefaultPal = $i
        
        $PalInput = Read-Host "Auswahl (Default: $DefaultPal)        "
        if ([string]::IsNullOrWhiteSpace($PalInput)) { $PalInput = "$DefaultPal" }
        
        $Index = [int]$PalInput - 1
        if ($Index -ge 0 -and $Index -lt $PaletteList.Count) {
            $PaletteName = $PaletteList[$Index]
        }
    } catch {
        Write-Host "Info: Standard Palette wird verwendet." -ForegroundColor DarkGray
    }
}

    # 7b. Berechnungs-Modus
    Write-Host ""
    Write-Host "Berechnungs-Modus:" -ForegroundColor Gray
    Write-Host " [1] Quantum (Stochastisch - Lebendiges Feld)" -ForegroundColor Cyan
    Write-Host " [2] Precision (Deterministisch - Reproduzierbar)" -ForegroundColor Cyan
    $ModeInput = Read-Host " Auswahl (1-2) [1]             "
    $CalcMode = "quantum"
    if ($ModeInput -eq "2") { 
        $CalcMode = "precision" 
        Write-Host " -> Modus: Precision (Deterministisch)" -ForegroundColor Magenta
    } else {
        Write-Host " -> Modus: Quantum (Standard)" -ForegroundColor Green
    }

    # 7c. Innovative Module
    Write-Host ""
    Write-Host "Erweiterte Module aktivieren:" -ForegroundColor Gray
    $HrvSimInput = Read-Host " HRV Bio-Feedback Simulation? (j/N) "
    $HrvSimFlag = if ($HrvSimInput -eq "j" -or $HrvSimInput -eq "J") { "--hrv-sim" } else { "" }
    
    $QuantumActiveInput = Read-Host " Quantum-Modul (D-Wave) aktiv? (j/N) "
    $QuantumFlag = if ($QuantumActiveInput -eq "j" -or $QuantumActiveInput -eq "J") { "--quantum-active" } else { "" }

    $EmfInput = Read-Host " EMF-Umfeld-Kompensation aktiv? (J/n) "
    $EmfFlag = if ($EmfInput -eq "n" -or $EmfInput -eq "N") { "" } else { "--emf-compensate" }

    # 7d. Amplifier (Resonanz-Verstaerker)
    Write-Host ""
    Write-Host "Resonanz-Verstaerker (Amplifier):" -ForegroundColor Gray
    Write-Host " [0] Keiner" -ForegroundColor Gray
    Write-Host " [1] Rosenquarz (Liebe/Herz) - 350 Hz" -ForegroundColor White
    Write-Host " [2] Amethyst (Intuition/Klarheit) - 480 Hz" -ForegroundColor White
    Write-Host " [3] Bergkristall (Universell) - 528 Hz" -ForegroundColor Cyan
    Write-Host " [4] Schwarzer Turmalin (EMF-Schutz) - 174 Hz" -ForegroundColor Cyan
    Write-Host " [5] Schungit (EMF-Absorption) - 196 Hz" -ForegroundColor Green
    Write-Host " [6] Orgonit-Pyramide Schungit (Raumharm.) - 7.83 Hz" -ForegroundColor Yellow
    Write-Host " [7] Orgonit-Pyramide Bergkristall - 7.83 Hz" -ForegroundColor Yellow
    Write-Host " [8] Lapislazuli (Weisheit) - 448 Hz" -ForegroundColor Blue
    Write-Host " [9] Selenit (Reinigung) - 560 Hz" -ForegroundColor White
    $AmpInput = Read-Host " Auswahl (0-9) [5]              "
    $AmplifierArg = ""
    $AmpNames = @("", "rosenquarz", "amethyst", "bergkristall", "schwarzer_turmalin", "schungit", "orgonit_pyramide_schungit", "orgonit_pyramide_bergkristall", "lapislazuli", "selenit")
    if ([string]::IsNullOrWhiteSpace($AmpInput)) { $AmpInput = "5" }
    $AmpIdx = [int]$AmpInput
    if ($AmpIdx -ge 1 -and $AmpIdx -lt $AmpNames.Count) {
        $AmplifierArg = "--amplifier `"$($AmpNames[$AmpIdx])`""
        Write-Host " -> Verstaerker: $($AmpNames[$AmpIdx])" -ForegroundColor Green
    }

    # 7e. Symmetrie-Modus
    Write-Host ""
    Write-Host "Matrix-Symmetrie:" -ForegroundColor Gray
    Write-Host " [0] Original (Maximale Akkuranz)" -ForegroundColor Cyan
    Write-Host " [1] Spiegel (Links-Rechts, 88-95% Score) (Standard)" -ForegroundColor Green
    Write-Host " [2] Mandala (4-Quadranten, 78-88% Score)" -ForegroundColor Cyan
    $SymInput = Read-Host " Auswahl (0-2) [1]              "
    $SymmetryArg = ""
    if ($SymInput -eq "0") {
        Write-Host " -> Symmetrie: Original (keine)" -ForegroundColor Green
    } elseif ($SymInput -eq "2") {
        $SymmetryArg = "--symmetry quadrant"
        Write-Host " -> Symmetrie: Mandala (4-Quadranten)" -ForegroundColor Green
    } else {
        $SymmetryArg = "--symmetry horizontal"
        Write-Host " -> Symmetrie: Spiegel (Links-Rechts)" -ForegroundColor Green
    }

} # Ende: Template vs. Manuelle Konfiguration

    # 8. Harmonisierung (Optional)
    Write-Host ""
    Write-Host "Harmonisierung:" -ForegroundColor Gray
    $HarmonizeInput = Read-Host "Starten nach Analyse? (J/n)     "
    if ([string]::IsNullOrWhiteSpace($HarmonizeInput)) { $HarmonizeInput = "j" }
    $HarmonizeArgs = ""

    if ($HarmonizeInput -eq "j" -or $HarmonizeInput -eq "J") {
        $Pulse = Read-Host " Impuls (Sekunden) [14]         "
        if ([string]::IsNullOrWhiteSpace($Pulse)) { $Pulse = "14" }
        
        $Pause = Read-Host " Pause (Sekunden) [14]          "
        if ([string]::IsNullOrWhiteSpace($Pause)) { $Pause = "14" }
        
        $Duration = Read-Host " Dauer (Faktor x 21min) [21]    "
        if ([string]::IsNullOrWhiteSpace($Duration)) { $Duration = "21" }

        Write-Host " Solfeggio/Basis Modulation:" -ForegroundColor Gray
        Write-Host " [1] 528.00 Hz (DNA/Transformation)" -ForegroundColor Cyan
        Write-Host " [2] 429.62 Hz (Bio-Resonanz)" -ForegroundColor Cyan
        Write-Host " [3] Natuerliche Stimmung (432.00 Hz) (Standard)" -ForegroundColor Green
        $SolfInput = Read-Host " Auswahl (1-3) [3]             "
        $SolfFreq = switch ($SolfInput) {
            "1" { "528" }
            "2" { "429.62" }
            Default { "432" }
        }
        
        $AudioInput = Read-Host " Audio-Ausgabe aktivieren? (j/N)    "
        $AudioFlag = ""
        if ($AudioInput -eq "j" -or $AudioInput -eq "J") {
            $AudioFlag = "--audio --solfeggio $SolfFreq"
            Write-Host " -> Audio aktiv (Modulation: $SolfFreq Hz)" -ForegroundColor Magenta
        }
        
        $HarmonizeArgs = "--harmonize --pulse $Pulse --pause $Pause --duration $Duration $AudioFlag"
        
        $TotalMin = [double]$Duration * 21
        Write-Host " -> Harmonisierung aktiv ($TotalMin Min)" -ForegroundColor Magenta
    }

# 9. Template-Benennung (Optional)
Write-Host ""
Write-Host "Template-Benennung (fuer spaetere Identifikation):" -ForegroundColor Gray
if ($TemplateLoaded -and $SelTemplate.template_name) {
    Write-Host " Vorheriger Name: $($SelTemplate.template_name)" -ForegroundColor DarkCyan
}
$TemplateName = Read-Host " Name eingeben (Enter = leer)   "
$TemplateNameArg = ""
if (-not [string]::IsNullOrWhiteSpace($TemplateName)) {
    $TemplateNameArg = "--template-name `"$TemplateName`""
    Write-Host " -> Template: '$TemplateName'" -ForegroundColor Green
} else {
    Write-Host " -> Kein Template-Name vergeben" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "Starte Berechnung fuer $Firstname $Surname..." -ForegroundColor Green
Write-Host "Gewichtung: $Weight | Palette: $PaletteName" -ForegroundColor DarkGray
Write-Host "----------------------------------------" -ForegroundColor Gray

# Python Script aufrufen
$ScriptPath = Join-Path $PSScriptRoot "dev_cli.py"

if (-not (Test-Path $ScriptPath)) {
    Write-Host "Fehler: dev_cli.py nicht gefunden in $PSScriptRoot" -ForegroundColor Red
    exit
}

# Ausfuehrung mit robustem Argument-Handling
$Params = @()
if (-not [string]::IsNullOrWhiteSpace($Surname))   { $Params += "--surname `"$Surname`"" }
if (-not [string]::IsNullOrWhiteSpace($Firstname)) { $Params += "--firstname `"$Firstname`"" }
if (-not [string]::IsNullOrWhiteSpace($Dob))       { $Params += "--dob `"$Dob`"" }
if (-not [string]::IsNullOrWhiteSpace($Place))     { $Params += "--place `"$Place`"" }
if (-not [string]::IsNullOrWhiteSpace($Planet))    { $Params += "--planet `"$Planet`"" }
# Focus wird ueber Temp-Datei uebergeben (robust fuer lange Strings mit Semikolons/Umlauten)
$FocusTempFile = Join-Path $PSScriptRoot "data\.focus_temp.txt"
try {
    [System.IO.File]::WriteAllText($FocusTempFile, $Focus, [System.Text.Encoding]::UTF8)
    $Params += "--focus-file `"$FocusTempFile`""
} catch {
    # Fallback: Direkte Uebergabe
    if (-not [string]::IsNullOrWhiteSpace($Focus)) { $Params += "--focus `"$Focus`"" }
}
if (-not [string]::IsNullOrWhiteSpace($Weight))    { $Params += "--weight `"$Weight`"" }
if (-not [string]::IsNullOrWhiteSpace($PaletteName)) { $Params += "--palette `"$PaletteName`"" }
if (-not [string]::IsNullOrWhiteSpace($CalcMode))  { $Params += "--mode `"$CalcMode`"" }

# Flags hinzufuegen (nur wenn sie nicht leer sind)
if (-not [string]::IsNullOrWhiteSpace($HrvSimFlag)) { $Params += $HrvSimFlag }
if (-not [string]::IsNullOrWhiteSpace($QuantumFlag)) { $Params += $QuantumFlag }
if (-not [string]::IsNullOrWhiteSpace($PlanetaryFlag)) { $Params += $PlanetaryFlag }
if (-not [string]::IsNullOrWhiteSpace($EmfFlag)) { $Params += $EmfFlag }
if (-not [string]::IsNullOrWhiteSpace($AmplifierArg)) { $Params += $AmplifierArg }
if (-not [string]::IsNullOrWhiteSpace($SymmetryArg)) { $Params += $SymmetryArg }
if (-not [string]::IsNullOrWhiteSpace($MatrixSizeArg)) { $Params += $MatrixSizeArg }
if (-not [string]::IsNullOrWhiteSpace($TemplateNameArg)) { $Params += $TemplateNameArg }

# Spezial-Args und Harmonisierung
if (-not [string]::IsNullOrWhiteSpace($SpecArgs)) { $Params += $SpecArgs }
if (-not [string]::IsNullOrWhiteSpace($HarmonizeArgs)) { $Params += $HarmonizeArgs }

$Command = "$PythonCommandExpression `"$ScriptPath`" " + ($Params -join " ")
Invoke-Expression $Command

Write-Host ""
Write-Host "Fertig." -ForegroundColor Green
Write-Host "Druecken Sie eine beliebige Taste zum Beenden..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
