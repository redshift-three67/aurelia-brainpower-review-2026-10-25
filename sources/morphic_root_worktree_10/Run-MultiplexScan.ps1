param()

$ErrorActionPreference = 'Stop'

# Vom Speicherort des Skripts aus arbeiten (Projekt-Root)
Set-Location -Path $PSScriptRoot

$projectRoot = $PSScriptRoot
$preferredPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (Test-Path -LiteralPath $preferredPython) {
    $pythonExe = $preferredPython
} else {
    $pythonExe = 'python'
}
$env:PYTHONIOENCODING = 'utf-8'

function Test-MorphicEnvironment {
    param([string]$PythonExe)

    $output = & $PythonExe -m apps.cli.main health --strict 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host '[FEHLER] Morphic Health-Preflight fehlgeschlagen.' -ForegroundColor Red
        Write-Host $output -ForegroundColor Yellow
        Write-Host 'Behebung: .\.venv\Scripts\python.exe -m pip install -r requirements.txt' -ForegroundColor Yellow
        throw 'Morphic Health-Preflight fehlgeschlagen.'
    }
    Write-Host '[OK] Morphic Health-Preflight' -ForegroundColor Green
    foreach ($line in $output) {
        Write-Host ("  {0}" -f $line) -ForegroundColor DarkGray
    }

    $sourceOutput = & $PythonExe -m apps.cli.main sources validate 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host '[FEHLER] Source-Registry-Preflight fehlgeschlagen.' -ForegroundColor Red
        Write-Host $sourceOutput -ForegroundColor Yellow
        throw 'Source-Registry-Preflight fehlgeschlagen.'
    }
    Write-Host '[OK] Source-Registry-Preflight' -ForegroundColor Green
    foreach ($line in $sourceOutput) {
        Write-Host ("  {0}" -f $line) -ForegroundColor DarkGray
    }
}

function Get-MorphicProfiles {
    param([string]$PythonExe)

    $script = "import json; from core.profile_sync import get_all_profiles; print(json.dumps([{'name': p.name, 'display': p.display_name} for p in get_all_profiles()], ensure_ascii=False))"
    $output = & $PythonExe -c $script 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host '[FEHLER] Profilkatalog konnte nicht aus core.profile_sync geladen werden.' -ForegroundColor Red
        Write-Host $output -ForegroundColor Yellow
        throw 'Profilkatalog konnte nicht geladen werden.'
    }

    $rawJson = ($output -join "`n")
    $profileData = $rawJson | ConvertFrom-Json
    $profiles = @()
    $number = 1
    foreach ($profile in $profileData) {
        $display = [string]$profile.display
        if ([string]::IsNullOrWhiteSpace($display)) {
            $display = [string]$profile.name
        }
        $profiles += [pscustomobject]@{
            Number = $number
            Name = [string]$profile.name
            Display = $display
        }
        $number++
    }

    if ($profiles.Count -eq 0) {
        throw 'Profilkatalog enthaelt keine aktiven Profile.'
    }
    return $profiles
}

Test-MorphicEnvironment -PythonExe $pythonExe

$lastClientFile = Join-Path $PSScriptRoot 'last_client.json'
$lastClient = $null
if (Test-Path $lastClientFile) {
    try {
        $lastClient = Get-Content $lastClientFile -Raw | ConvertFrom-Json
    } catch {
        $lastClient = $null
    }
}

Write-Host 'Morphic Engine V1 - Multiplex-Scan (PowerShell Launcher)' -ForegroundColor Cyan
Write-Host ''

# === SCAN-MODUS AUSWAHL ===
Write-Host '=======================================' -ForegroundColor Cyan
Write-Host 'SCAN-MODUS AUSWAHL' -ForegroundColor Cyan
Write-Host '=======================================' -ForegroundColor Cyan
Write-Host '  1) Einzelprofil-Scan  - Klassischer Scan mit einem Profil' -ForegroundColor DarkYellow
Write-Host '  2) Top-N Auto-Scan    - Automatische Ermittlung der relevantesten Profile (Top-3/5/7/9)' -ForegroundColor DarkYellow
Write-Host ''
$scanModeInput = Read-Host 'Scan-Modus (1 oder 2, Standard 1)'
if ([string]::IsNullOrWhiteSpace($scanModeInput)) {
    $scanModeInput = '1'
}
$useTop5Scan = ($scanModeInput -eq '2')

function Read-TopNSelection {
    $allowedTopN = @(3, 5, 7, 9)
    while ($true) {
        Write-Host ''
        Write-Host 'Top-N Auswahl fuer den Auto-Scan:' -ForegroundColor Yellow
        Write-Host '  3) Schnellere fokussierte Auswahl' -ForegroundColor DarkYellow
        Write-Host '  5) Standard-Auswahl' -ForegroundColor DarkYellow
        Write-Host '  7) Erweiterte Auswahl' -ForegroundColor DarkYellow
        Write-Host '  9) Vollere Priorisierung wie im alten TOP9-Archiv' -ForegroundColor DarkYellow
        $topNInput = Read-Host 'Top-N (3/5/7/9, Standard 5)'
        if ([string]::IsNullOrWhiteSpace($topNInput)) {
            return 5
        }
        try {
            $topNValue = [int]$topNInput
        } catch {
            Write-Host 'Bitte 3, 5, 7 oder 9 eingeben.' -ForegroundColor Yellow
            continue
        }
        if ($allowedTopN -contains $topNValue) {
            return $topNValue
        }
        Write-Host 'Bitte 3, 5, 7 oder 9 eingeben.' -ForegroundColor Yellow
    }
}

$TopN = 5
if ($useTop5Scan) {
    $TopN = Read-TopNSelection
}

# === ANALYSE-LEVEL AUSWAHL ===
Write-Host ''
Write-Host '=======================================' -ForegroundColor Cyan
Write-Host 'ANALYSE-LEVEL' -ForegroundColor Cyan
Write-Host '=======================================' -ForegroundColor Cyan
Write-Host '  1) Level 1 - Schnellscan (5 Profile, ~30s)' -ForegroundColor DarkYellow
Write-Host '  2) Level 2 - Standard (35 Profile, ~2min)' -ForegroundColor DarkYellow
Write-Host '  3) Level 3 - Erweitert (55 Profile, ~3min) [STANDARD]' -ForegroundColor DarkYellow
Write-Host '  4) Level 4 - Komplett (153+ Profile, ~8min)' -ForegroundColor DarkYellow
Write-Host ''
$levelInput = Read-Host 'Level (1-4, Standard 3)'
if ([string]::IsNullOrWhiteSpace($levelInput)) {
    $levelInput = '3'
}
try {
    $AnalysisLevel = [Math]::Max(1, [Math]::Min(4, [int]$levelInput))
} catch {
    $AnalysisLevel = 3
}
Write-Host ("  Gewaehltes Level: {0}" -f $AnalysisLevel) -ForegroundColor DarkCyan

Write-Host ''

$profiles = @(Get-MorphicProfiles -PythonExe $pythonExe)

# Profil-Auswahl nur bei Einzelprofil-Scan anzeigen
if (-not $useTop5Scan) {
    Write-Host 'Verfuegbare Profile (Nummer oder Name eingeben):' -ForegroundColor Yellow
    foreach ($p in $profiles) {
        Write-Host ("  {0,2}) {1}" -f $p.Number, $p.Display) -ForegroundColor DarkYellow
    }
    Write-Host ''
}

Write-Host 'Hinweis: Das Feld "Fokus" ist eine optionale Freitext-Eingabe (z.B. Symptom oder System).' -ForegroundColor Yellow
Write-Host 'Beispiele fuer Fokus:' -ForegroundColor Yellow
Write-Host '  Atmungsorgane' -ForegroundColor DarkYellow
Write-Host '  Herz-Kreislauf' -ForegroundColor DarkYellow
Write-Host '  Haut' -ForegroundColor DarkYellow
Write-Host '  Schwindel' -ForegroundColor DarkYellow
Write-Host '  Zaehen / Zahnherde' -ForegroundColor DarkYellow
Write-Host '  Knochen / Skelett' -ForegroundColor DarkYellow
Write-Host '  toxische Stoerfelder' -ForegroundColor DarkYellow
Write-Host '  Strahlenbelastungen' -ForegroundColor DarkYellow
Write-Host ''

# Kurze interaktive Eingabe
$defaultName = if ($lastClient -and $lastClient.Name) { [string]$lastClient.Name } else { '' }
$promptName = if ($defaultName) { "Nachname [$defaultName]" } else { 'Nachname' }
do {
    $input = Read-Host $promptName
    if ([string]::IsNullOrWhiteSpace($input) -and $defaultName) {
        $Name = $defaultName
    } else {
        $Name = $input
    }
} while ([string]::IsNullOrWhiteSpace($Name))

$defaultFirst = if ($lastClient -and $lastClient.FirstName) { [string]$lastClient.FirstName } else { '' }
$promptFirst = if ($defaultFirst) { "Vorname [$defaultFirst]" } else { 'Vorname' }
do {
    $input = Read-Host $promptFirst
    if ([string]::IsNullOrWhiteSpace($input) -and $defaultFirst) {
        $FirstName = $defaultFirst
    } else {
        $FirstName = $input
    }
} while ([string]::IsNullOrWhiteSpace($FirstName))

$defaultBirthDate = if ($lastClient -and $lastClient.BirthDate) { [string]$lastClient.BirthDate } else { '' }
$promptBirthDate = if ($defaultBirthDate) { "Geburtsdatum (z.B. 30091940) [$defaultBirthDate]" } else { 'Geburtsdatum (z.B. 30091940)' }
do {
    $input = Read-Host $promptBirthDate
    if ([string]::IsNullOrWhiteSpace($input) -and $defaultBirthDate) {
        $BirthDate = $defaultBirthDate
    } else {
        $BirthDate = $input
    }
} while ([string]::IsNullOrWhiteSpace($BirthDate))

$defaultBirthPlace = if ($lastClient -and $lastClient.BirthPlace) { [string]$lastClient.BirthPlace } else { '' }
$promptBirthPlace = if ($defaultBirthPlace) { "Geburtsort (z.B. Augsburg) [$defaultBirthPlace]" } else { 'Geburtsort (z.B. Augsburg)' }
do {
    $input = Read-Host $promptBirthPlace
    if ([string]::IsNullOrWhiteSpace($input) -and $defaultBirthPlace) {
        $BirthPlace = $defaultBirthPlace
    } else {
        $BirthPlace = $input
    }
} while ([string]::IsNullOrWhiteSpace($BirthPlace))

$lastClientOut = [pscustomobject]@{
    Name       = $Name
    FirstName  = $FirstName
    BirthDate  = $BirthDate
    BirthPlace = $BirthPlace
}
try {
    $lastClientOut | ConvertTo-Json | Set-Content -Encoding UTF8 $lastClientFile
} catch {
}

# Profil-Eingabe nur bei Einzelprofil-Scan
$Profile = 'full'
if (-not $useTop5Scan) {
    $ProfileInput = Read-Host 'Profil (Nummer oder Name, z.B. 4 oder full)'
    if ([string]::IsNullOrWhiteSpace($ProfileInput)) {
        $Profile = 'full'
    } else {
        if ($ProfileInput -match '^[0-9]+$') {
            $num = [int]$ProfileInput
            $match = $profiles | Where-Object { $_.Number -eq $num } | Select-Object -First 1
            if ($match) {
                $Profile = [string]$match.Name
            } else {
                $Profile = $ProfileInput
            }
        } else {
            $Profile = $ProfileInput
        }
    }
}

$Focus = Read-Host 'Fokus (optional, z.B. Atmungsorgane)'

# Bild-Vector optional
$ImagePath = ''
$imgInput = Read-Host 'Bild-Vector Pfad (optional, JPG/PNG fuer Bildsignatur - leer = kein Bild)'
if (-not [string]::IsNullOrWhiteSpace($imgInput)) {
    if (Test-Path -LiteralPath $imgInput) {
        $ImagePath = $imgInput
        Write-Host ("  Bild geladen: {0}" -f $ImagePath) -ForegroundColor DarkCyan
    } else {
        Write-Host "  Bild nicht gefunden - wird ignoriert." -ForegroundColor Yellow
    }
}

$UseFocusWeighting = $true
if (-not [string]::IsNullOrWhiteSpace($Focus)) {
    $fwInput = Read-Host 'Fokus-Gewichtung aktivieren? (J/n, Standard J = sanfte Priorisierung des Fokus)'
    if (-not [string]::IsNullOrWhiteSpace($fwInput)) {
        $fwNorm = $fwInput.Trim().ToLower()
        if ($fwNorm -eq 'n' -or $fwNorm -eq 'nein') {
            $UseFocusWeighting = $false
        }
    }
}

$PlanetType = Read-Host 'Geburtsplanet / Planetentyp (optional, z.B. Mars, Venus, Sonne)'

Write-Host ''
Write-Host 'Intention (optional, Standard: keine):' -ForegroundColor Yellow
Write-Host '  1) healing      - Heilung (Faktor 1.272)' -ForegroundColor DarkYellow
Write-Host '  2) clearing     - Klaerung/Entgiftung (Faktor 1.732)' -ForegroundColor DarkYellow
Write-Host '  3) protection   - Schutz/Immunstaerkung (Faktor 1.414)' -ForegroundColor DarkYellow
Write-Host '  4) transformation - Tiefgreifende Aenderung (Faktor 2.236)' -ForegroundColor DarkYellow
Write-Host '  5) harmonization - Balance (Faktor 1.618)' -ForegroundColor DarkYellow
Write-Host '  6) activation   - Aktivierung (Faktor 2.718)' -ForegroundColor DarkYellow
Write-Host '  0) keine        - Keine Gewichtung' -ForegroundColor DarkYellow

$IntentionInput = Read-Host 'Intention (0-6, Standard 0 = keine)'
$Intention = ''
switch ($IntentionInput) {
    '1' { $Intention = 'healing' }
    '2' { $Intention = 'clearing' }
    '3' { $Intention = 'protection' }
    '4' { $Intention = 'transformation' }
    '5' { $Intention = 'harmonization' }
    '6' { $Intention = 'activation' }
    Default { $Intention = '' }
}

Write-Host ''
Write-Host 'Personalprofil (0.0 - 1.0, Standard 0.5). Leere Eingabe = 0.5.' -ForegroundColor Yellow
Write-Host 'Templates: 1=Neutral, 2=Physisch, 3=Mental, 4=Astral, 5=Emotional, 6=Manuell' -ForegroundColor Yellow

function Read-PersonalValue($label) {
    while ($true) {
        $input = Read-Host $label
        if ([string]::IsNullOrWhiteSpace($input)) {
            return 0.5
        }
        try {
            $val = [double]$input
        } catch {
            Write-Host 'Bitte eine Zahl zwischen 0.0 und 1.0 eingeben.' -ForegroundColor Yellow
            continue
        }
        if ($val -lt 0.0 -or $val -gt 1.0) {
            Write-Host 'Bitte eine Zahl zwischen 0.0 und 1.0 eingeben.' -ForegroundColor Yellow
            continue
        }
        return $val
    }
}

$PEmotion  = 0.5
$PPhysisch = 0.5
$PMental   = 0.5
$PAstral   = 0.5

$tpl = Read-Host 'Personalprofil-Template (1-6, Standard 1=Neutral)'
if ([string]::IsNullOrWhiteSpace($tpl)) {
    $tpl = '1'
}

switch ($tpl) {
    '1' {
        $PEmotion  = 0.5
        $PPhysisch = 0.5
        $PMental   = 0.5
        $PAstral   = 0.5
    }
    '2' {
        $PEmotion  = 0.2
        $PPhysisch = 0.9
        $PMental   = 0.3
        $PAstral   = 0.2
    }
    '3' {
        $PEmotion  = 0.3
        $PPhysisch = 0.2
        $PMental   = 0.9
        $PAstral   = 0.4
    }
    '4' {
        $PEmotion  = 0.4
        $PPhysisch = 0.2
        $PMental   = 0.4
        $PAstral   = 0.9
    }
    '5' {
        $PEmotion  = 0.9
        $PPhysisch = 0.3
        $PMental   = 0.4
        $PAstral   = 0.4
    }
    '6' {
        $PEmotion  = Read-PersonalValue 'Emotion [0.0-1.0, Standard 0.5]'
        $PPhysisch = Read-PersonalValue 'Physisch [0.0-1.0, Standard 0.5]'
        $PMental   = Read-PersonalValue 'Mental [0.0-1.0, Standard 0.5]'
        $PAstral   = Read-PersonalValue 'Astral [0.0-1.0, Standard 0.5]'
    }
    Default {
        $PEmotion  = 0.5
        $PPhysisch = 0.5
        $PMental   = 0.5
        $PAstral   = 0.5
    }
}

Write-Host ''
Write-Host 'Entropie-Konfiguration (Hardware):' -ForegroundColor Yellow

$defaultEntropyMode = if ($env:ME_ENTROPY_MODE -and $env:ME_ENTROPY_MODE.Trim()) { $env:ME_ENTROPY_MODE } else { 'enhanced' }
$modeInput = Read-Host ("Entropie-Modus [enhanced/legacy] (Standard: {0})" -f $defaultEntropyMode)

if ([string]::IsNullOrWhiteSpace($modeInput)) {
    $env:ME_ENTROPY_MODE = $defaultEntropyMode
} else {
    $env:ME_ENTROPY_MODE = $modeInput.Trim().ToLower()
}

if (-not $env:ME_NETWORK_ENTROPY_URL -or -not $env:ME_NETWORK_ENTROPY_URL.Trim()) {
    $env:ME_NETWORK_ENTROPY_URL = 'https://1.1.1.1'
}

Write-Host ('  ME_ENTROPY_MODE         = {0}' -f $env:ME_ENTROPY_MODE) -ForegroundColor DarkCyan
Write-Host ('  ME_NETWORK_ENTROPY_URL  = {0}' -f $env:ME_NETWORK_ENTROPY_URL) -ForegroundColor DarkCyan

if ($env:ME_TRUERNG_PORT -and $env:ME_TRUERNG_PORT.Trim()) {
    Write-Host ('  ME_TRUERNG_PORT         = {0}' -f $env:ME_TRUERNG_PORT) -ForegroundColor DarkCyan
} else {
    Write-Host '  ME_TRUERNG_PORT         = (nicht gesetzt)' -ForegroundColor DarkGray
}

Write-Host ''

$arguments = @(
    '-m', 'apps.cli.main', 'field', 'multiplex-scan',
    $Name,
    $FirstName,
    '--birth-date', $BirthDate,
    '--birth-place', $BirthPlace,
    '--profile', $Profile,
    '--hardware-profile', 'windows',
    '--export', 'C:\Benutzer_Archive_Start',
    '--k-total', 4096,
    '--top-k', 384,
    '--synergy',
    '--synergy-combos', 4,
    '--synergy-threshold', 7.0,
    '--morphic-field',
    '--p-emotion',  $PEmotion,
    '--p-physisch', $PPhysisch,
    '--p-mental',   $PMental,
    '--p-astral',   $PAstral
)

if (-not [string]::IsNullOrWhiteSpace($PlanetType)) {
    $arguments += @('--planet-type', $PlanetType)
}

if (-not [string]::IsNullOrWhiteSpace($Focus)) {
    $arguments += @('--focus', $Focus)
    if (-not $UseFocusWeighting) {
        $arguments += '--no-focus-weighting'
    }
}

if (-not [string]::IsNullOrWhiteSpace($Intention)) {
    $arguments += @('--intention', $Intention)
}

if (-not [string]::IsNullOrWhiteSpace($ImagePath)) {
    $arguments += @('--image', $ImagePath)
}

Write-Host ''

# === TOP-N SCAN ODER EINZELPROFIL-SCAN ===
if ($useTop5Scan) {
    Write-Host '=======================================' -ForegroundColor Cyan
    Write-Host ("TOP-{0} AUTO-SCAN (mit Fokus-Gewichtung, Level {1})" -f $TopN, $AnalysisLevel) -ForegroundColor Cyan
    Write-Host '=======================================' -ForegroundColor Cyan
    $levelProfiles = @{ 1 = 5; 2 = 35; 3 = 55; 4 = 153 }
    $profileCount = $levelProfiles[$AnalysisLevel]
    Write-Host ("Scannt automatisch {0} Profile und analysiert die Top-{1}" -f $profileCount, $TopN) -ForegroundColor DarkCyan
    Write-Host ("Profilbasis: Level {0} ({1} Profile) aus core.profile_sync" -f $AnalysisLevel, $profileCount) -ForegroundColor DarkCyan
    if (-not [string]::IsNullOrWhiteSpace($Focus)) {
        Write-Host ("Fokus: {0}" -f $Focus) -ForegroundColor DarkCyan
    } else {
        Write-Host 'Fokus: (nicht gesetzt)' -ForegroundColor DarkGray
    }
    Write-Host 'Gewichtung: Top-Fokus +25%, Sekundaer +15%, Kontext +10%' -ForegroundColor DarkGray
    Write-Host ''
    
    $topNArguments = @(
        '-m', 'apps.cli.main', 'scan', 'top3-scan',
        $Name,
        $FirstName,
        '--birth-date', $BirthDate,
        '--birth-place', $BirthPlace,
        '--export', 'C:\Benutzer_Archive_Start',
        '--hardware-profile', 'windows',
        '--k-total', '4096',
        '--top-k', '384',
        '--synergy',
        '--synergy-combos', '4',
        '--synergy-threshold', '6.0',
        '--top-n', $TopN.ToString(),
        '--level', $AnalysisLevel.ToString()
    )
    
    if (-not [string]::IsNullOrWhiteSpace($Focus)) {
        $topNArguments += @('--focus', $Focus)
    }
    
    Write-Host 'Python:' $pythonExe -ForegroundColor DarkGray
    Write-Host 'Argumente:' -ForegroundColor DarkGray
    ($topNArguments -join ' ') | Write-Host
    Write-Host ''
    
    $env:PYTHONIOENCODING = 'utf-8'
    $env:PYTHONUTF8 = '1'
    
    & $pythonExe @topNArguments
    $exitCode = $LASTEXITCODE
} else {
    Write-Host 'Starte Multiplex-Scan...' -ForegroundColor Cyan
    Write-Host ("Profil: {0}" -f $Profile) -ForegroundColor DarkCyan
    if (-not [string]::IsNullOrWhiteSpace($Intention)) {
        Write-Host ("Intention: {0}" -f $Intention) -ForegroundColor DarkCyan
    }
    if (-not [string]::IsNullOrWhiteSpace($Focus)) {
        Write-Host ("Fokus:  {0}" -f $Focus) -ForegroundColor DarkCyan
    }
    Write-Host ''

    Write-Host 'Python:' $pythonExe -ForegroundColor DarkGray
    Write-Host 'Argumente:' -ForegroundColor DarkGray
    ($arguments -join ' ') | Write-Host
    Write-Host ''

    & $pythonExe @arguments
    $exitCode = $LASTEXITCODE
}

if ($exitCode -eq 0) {
    Write-Host 'Scan erfolgreich abgeschlossen.' -ForegroundColor Green
    Write-Host ''
    
    # Bei Top-N Scan: Deutung, Trendanalyse, Synergy und PDF
    if ($useTop5Scan) {
        Write-Host ''
        Write-Host ("Top-{0} Analyse abgeschlossen. HTML-Berichte wurden im Benutzer_Archive_Start gespeichert." -f $TopN) -ForegroundColor Green
        Write-Host ''
        
        # === DEUTUNGS-BERICHT GENERIEREN ===
        Write-Host '=======================================' -ForegroundColor Magenta
        Write-Host ("DEUTUNGS-BERICHT (TOP-{0})" -f $TopN) -ForegroundColor Magenta
        Write-Host '=======================================' -ForegroundColor Magenta
        Write-Host ''
        Write-Host 'Moechten Sie eine KI-Tiefenanalyse (Ollama LLM) hinzufuegen?' -ForegroundColor Yellow
        Write-Host '  J/j = Ja, mit KI-Analyse' -ForegroundColor DarkYellow
        Write-Host '  N/n = Nein, Standard-Deutung' -ForegroundColor DarkYellow
        Write-Host ''
        
        $llmInput = Read-Host 'KI-Tiefenanalyse? (J/N, Standard N)'
        
        $deutungArgs = @(
            '-m', 'tools.interpretation_generator',
            $Name,
            $FirstName,
            '--birth-date', $BirthDate,
            '--birth-place', $BirthPlace,
            '--scans', $TopN.ToString(),
            '--age', '2',
            '--archive-root', 'C:\Benutzer_Archive_Start',
            '--output-root', 'C:\Benutzer_Deutung_Start'
        )
        
        if (-not [string]::IsNullOrWhiteSpace($Focus)) {
            $deutungArgs += '--focus'
            $deutungArgs += $Focus
        }
        
        if ($llmInput -eq 'J' -or $llmInput -eq 'j') {
            Write-Host ''
            Write-Host ("Deutungs-Bericht mit KI-Tiefenanalyse wird erstellt ({0} Top-Profile)..." -f $TopN) -ForegroundColor Magenta
            $deutungArgs += '--llm'
        } else {
            Write-Host ''
            Write-Host ("Standard-Deutungs-Bericht wird erstellt ({0} Top-Profile)..." -f $TopN) -ForegroundColor Magenta
        }
        
        try {
            $deutungProcess = Start-Process -FilePath $pythonExe -ArgumentList $deutungArgs -WorkingDirectory $PSScriptRoot -NoNewWindow -Wait -PassThru
            if ($deutungProcess.ExitCode -eq 0) {
                Write-Host ''
                Write-Host 'Deutungs-Bericht wurde in C:\Benutzer_Deutung_Start gespeichert.' -ForegroundColor Green
            } else {
                Write-Host 'Deutungs-Bericht konnte nicht erstellt werden.' -ForegroundColor Yellow
            }
        } catch {
            Write-Host "Fehler bei Deutungs-Generierung: $($_.Exception.Message)" -ForegroundColor Yellow
        }
        
        # === TRENDANALYSE ===
        Write-Host ''
        Write-Host '=======================================' -ForegroundColor Cyan
        Write-Host 'TRENDANALYSE WIRD AKTUALISIERT...' -ForegroundColor Cyan
        Write-Host '=======================================' -ForegroundColor Cyan
        Write-Host ''
        
        $trendArgs = @(
            '-m', 'tools.trend_analyzer',
            $Name,
            $FirstName,
            '--birth-date', $BirthDate,
            '--birth-place', $BirthPlace,
            '--save',
            '--db',
            '--output', 'html',
            '--archive-root', 'C:\Benutzer_Archive_Start',
            '--output-root', 'C:\Benutzer_Trends_Start'
        )
        
        try {
            $trendProcess = Start-Process -FilePath $pythonExe -ArgumentList $trendArgs -WorkingDirectory $PSScriptRoot -NoNewWindow -Wait -PassThru
            if ($trendProcess.ExitCode -eq 0) {
                Write-Host ''
                Write-Host 'Trendanalyse wurde in C:\Benutzer_Trends_Start gespeichert.' -ForegroundColor Green
            } else {
                Write-Host 'Trendanalyse konnte nicht erstellt werden (evtl. noch keine historischen Daten).' -ForegroundColor Yellow
            }
        } catch {
            Write-Host "Fehler bei Trendanalyse: $($_.Exception.Message)" -ForegroundColor Yellow
        }
        
        Write-Host ''
        
        # === SYNERGY-GESAMTBERICHT ===
        Write-Host '=======================================' -ForegroundColor Yellow
        Write-Host 'SYNERGY-GESAMTBERICHT' -ForegroundColor Yellow
        Write-Host '=======================================' -ForegroundColor Yellow
        Write-Host ("Konsolidiert Synergien aus allen Top-{0} Profilen..." -f $TopN) -ForegroundColor DarkYellow
        Write-Host ''
        
        $synergyArgs = @(
            '-m', 'tools.synergy_consolidator',
            $Name,
            $FirstName,
            '--birth-date', $BirthDate,
            '--birth-place', $BirthPlace,
            '--hours', '2'
        )
        
        try {
            $synergyProcess = Start-Process -FilePath $pythonExe -ArgumentList $synergyArgs -WorkingDirectory $PSScriptRoot -NoNewWindow -Wait -PassThru
            if ($synergyProcess.ExitCode -eq 0) {
                Write-Host ''
                Write-Host 'Synergy-Gesamtbericht wurde in C:\Benutzer_Synergy_Start gespeichert.' -ForegroundColor Green
            } else {
                Write-Host 'Synergy-Gesamtbericht konnte nicht erstellt werden.' -ForegroundColor Yellow
            }
        } catch {
            Write-Host "Fehler bei Synergy-Konsolidierung: $($_.Exception.Message)" -ForegroundColor Yellow
        }
        
        Write-Host ''
        
        # === REMEDY-BERICHT ===
        Write-Host '=======================================' -ForegroundColor Magenta
        Write-Host ("REMEDY-BERICHT (TOP-{0})" -f $TopN) -ForegroundColor Magenta
        Write-Host '=======================================' -ForegroundColor Magenta
        Write-Host ("Erstelle Remedy-Kombinationen aus Top-{0} Session..." -f $TopN) -ForegroundColor DarkMagenta
        Write-Host ''
        
        $remedyArgs = @(
            '-m', 'tools.remedy_reporter',
            $Name,
            $FirstName,
            '--birth-date', $BirthDate,
            '--birth-place', $BirthPlace,
            '--top-n', $TopN.ToString(),
            '--session'
        )
        
        try {
            $remedyProcess = Start-Process -FilePath $pythonExe -ArgumentList $remedyArgs -WorkingDirectory $PSScriptRoot -NoNewWindow -Wait -PassThru
            if ($remedyProcess.ExitCode -eq 0) {
                Write-Host ''
                Write-Host 'Remedy-Bericht wurde in C:\Benutzer_Remedies_Start gespeichert.' -ForegroundColor Green
            } else {
                Write-Host 'Remedy-Bericht konnte nicht erstellt werden.' -ForegroundColor Yellow
            }
        } catch {
            Write-Host "Fehler bei Remedy-Generierung: $($_.Exception.Message)" -ForegroundColor Yellow
        }
        
        Write-Host ''
        
        # === PDF-EXPORT ===
        Write-Host '=======================================' -ForegroundColor Blue
        Write-Host 'PDF-EXPORT (OPTIONAL)' -ForegroundColor Blue
        Write-Host '=======================================' -ForegroundColor Blue
        Write-Host ''
        Write-Host 'Moechten Sie die Berichte als PDF exportieren?' -ForegroundColor Yellow
        Write-Host '  J/j = Ja, neueste Berichte als PDF' -ForegroundColor DarkYellow
        Write-Host '  A/a = Alle Berichte als PDF' -ForegroundColor DarkYellow
        Write-Host '  N/n = Nein, ueberspringen' -ForegroundColor DarkYellow
        Write-Host ''
        
        $pdfInput = Read-Host 'PDF-Export? (J/A/N, Standard N)'
        
        if ($pdfInput -eq 'J' -or $pdfInput -eq 'j' -or $pdfInput -eq 'A' -or $pdfInput -eq 'a') {
            Write-Host ''
            Write-Host 'PDF-Export wird gestartet...' -ForegroundColor Blue
            
            $pdfArgs = @('-m', 'tools.pdf_exporter', $Name, $FirstName)
            
            if ($pdfInput -eq 'A' -or $pdfInput -eq 'a') {
                $pdfArgs += '--all'
                Write-Host '   (Alle Berichte werden exportiert)' -ForegroundColor DarkBlue
            } else {
                $pdfArgs += '--latest'
                Write-Host '   (Nur neueste Berichte werden exportiert)' -ForegroundColor DarkBlue
            }
            
            try {
                $pdfProcess = Start-Process -FilePath $pythonExe -ArgumentList $pdfArgs -WorkingDirectory $PSScriptRoot -NoNewWindow -Wait -PassThru
                if ($pdfProcess.ExitCode -eq 0) {
                    Write-Host ''
                    Write-Host 'PDF-Export abgeschlossen.' -ForegroundColor Green
                } else {
                    Write-Host 'PDF-Export fehlgeschlagen.' -ForegroundColor Yellow
                }
            } catch {
                Write-Host "Fehler bei PDF-Export: $($_.Exception.Message)" -ForegroundColor Yellow
            }
        } else {
            Write-Host 'PDF-Export uebersprungen.' -ForegroundColor Gray
        }
        
        Write-Host ''
        Write-Host '=======================================' -ForegroundColor Green
        Write-Host 'ALLE BERICHTE ABGESCHLOSSEN' -ForegroundColor Green
        Write-Host '=======================================' -ForegroundColor Green
        Write-Host ''
        Write-Host 'Gespeicherte Berichte:' -ForegroundColor White
        Write-Host '  - Scan-Berichte:    C:\Benutzer_Archive_Start' -ForegroundColor Gray
        Write-Host '  - Deutung:          C:\Benutzer_Deutung_Start' -ForegroundColor Gray
        Write-Host '  - Trendanalyse:     C:\Benutzer_Trends_Start' -ForegroundColor Gray
        Write-Host '  - Synergy-Gesamt:   C:\Benutzer_Synergy_Start' -ForegroundColor Gray
        Write-Host '  - Remedy-Bericht:   C:\Benutzer_Remedies_Start' -ForegroundColor Gray
        Write-Host '  - PDF-Exporte:      In den jeweiligen Ordnern' -ForegroundColor Gray
        Write-Host ''
        
        # === HARMONISIERUNG ===
        Write-Host 'Harmonisierungs-Optionen:' -ForegroundColor Yellow
        Write-Host '  1) Klassisch - Direkte Harmonisierung' -ForegroundColor DarkYellow
        Write-Host '  2) Hardware  - Hardware-Modulation (CPU/GPU/RAM)' -ForegroundColor DarkYellow
        Write-Host '  3) Beides    - Klassisch + Hardware parallel' -ForegroundColor DarkYellow
        Write-Host '  0) Keine     - Beenden' -ForegroundColor DarkYellow
        Write-Host ''
        
        $harmInput = Read-Host 'Harmonisierung (0-3, Standard 0)'
        
        if ($harmInput -eq '0' -or $harmInput -eq '') {
            Write-Host 'Keine Harmonisierung. Scan beendet.' -ForegroundColor Gray
            exit 0
        }
        
        $baseExport = 'C:\Benutzer_Archive_Start'
        $clientFolder = ("{0}_{1}_{2}_{3}" -f $Name, $FirstName, $BirthDate, $BirthPlace).Trim().Replace(' ', '_')
        $clientDir = Join-Path $baseExport $clientFolder
        
        if ($harmInput -eq '2' -or $harmInput -eq '3') {
            Write-Host ''
            Write-Host 'Starte Hardware-Harmonisierung (432 Hz, 5 Min)...' -ForegroundColor Cyan
            
            $hwDuration = 5
            $hwArgs = @(
                '-m', 'tools.hardware_harmonizer',
                '--frequency', '432',
                '--duration', $hwDuration.ToString(),
                '--mode', 'balanced'
            )
            
            try {
                $hwOutput = & $pythonExe @hwArgs 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Host 'Hardware-Harmonisierung gestartet.' -ForegroundColor Green
                } else {
                    Write-Host 'Hardware-Harmonisierung konnte nicht gestartet werden.' -ForegroundColor Yellow
                }
            } catch {
                Write-Host "Fehler: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        
        if ($harmInput -eq '1' -or $harmInput -eq '3') {
            $jsonFile = $null
            if (Test-Path $clientDir) {
                $jsonFile = Get-ChildItem -Path $clientDir -Filter '*_multiplex_scan.json' -File -Recurse | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            }
            
            if (-not $jsonFile) {
                Write-Host 'Keine Multiplex-JSON fuer die Harmonisierung gefunden.' -ForegroundColor Yellow
            } else {
                try {
                    $exportData = Get-Content $jsonFile.FullName -Raw | ConvertFrom-Json
                    $sections = $null
                    if ($exportData.sub_results -and $exportData.sub_results.sections) {
                        $sections = $exportData.sub_results.sections
                    } elseif ($exportData.bat_subgroups) {
                        $sections = $exportData.bat_subgroups
                    }
                    
                    if (-not $sections) {
                        Write-Host 'Export enthaelt keine Sektionen fuer die Harmonisierung.' -ForegroundColor Yellow
                    } else {
                        $items = @()
                        foreach ($sec in $sections) {
                            if ($sec.items) {
                                foreach ($it in $sec.items) {
                                    $prio = $it.priority
                                    if ($prio -eq 'hoch' -or $prio -eq 'mittel') {
                                        $items += [PSCustomObject]@{
                                            Label = $it.label
                                            Score = [double]$it.score
                                            Priority = $prio
                                            Rates = $it.rates
                                        }
                                    }
                                }
                            }
                        }
                        
                        if (-not $items -or $items.Count -eq 0) {
                            Write-Host 'Keine Items mit hoher oder mittlerer Prioritaet gefunden.' -ForegroundColor Yellow
                        } else {
                            $high = $items | Where-Object { $_.Priority -eq 'hoch' } | Sort-Object -Property Score -Descending
                            $mid  = $items | Where-Object { $_.Priority -eq 'mittel' } | Sort-Object -Property Score -Descending
                            $sequence = @($high) + @($mid) | Select-Object -First 20
                            $rounds = 3
                            $totalItems = $sequence.Count * $rounds
                            $totalSeconds = $totalItems * 10
                            $totalMinutes = [math]::Round($totalSeconds / 60.0, 1)
                            
                            Write-Host ''
                            Write-Host '=======================================' -ForegroundColor Green
                            Write-Host 'KLASSISCHE HARMONISIERUNG' -ForegroundColor Green
                            Write-Host '=======================================' -ForegroundColor Green
                            Write-Host ('Items: {0}' -f $sequence.Count) -ForegroundColor Cyan
                            Write-Host ('Runden: {0}' -f $rounds) -ForegroundColor Cyan
                            Write-Host ('Geschaetzte Dauer: {0} Minuten' -f $totalMinutes) -ForegroundColor Cyan
                            Write-Host ''
                            
                            $startTime = Get-Date
                            $currentItem = 0
                            
                            for ($r = 1; $r -le $rounds; $r++) {
                                Write-Host "--- Runde $r von $rounds ---" -ForegroundColor Magenta
                                foreach ($it in $sequence) {
                                    $currentItem++
                                    $rateDisplay = if ($it.Rates -and $it.Rates.Count -ge 2) { "$($it.Rates[0])-$($it.Rates[1])" } else { 'N/A' }
                                    $elapsed = (Get-Date) - $startTime
                                    $avgPerItem = if ($currentItem -gt 1) { $elapsed.TotalSeconds / ($currentItem - 1) } else { 10 }
                                    $remaining = ($totalItems - $currentItem) * $avgPerItem
                                    $estimatedRemaining = [TimeSpan]::FromSeconds($remaining)
                                    $progress = ($currentItem / $totalItems) * 100
                                    
                                    Write-Host ''
                                    Write-Host ('[{0}/{1}] {2:F1}% | Verbleibend: ~{3}m {4}s' -f $currentItem, $totalItems, $progress, [math]::Floor($estimatedRemaining.TotalMinutes), $estimatedRemaining.Seconds) -ForegroundColor DarkGray
                                    Write-Host ('Harmonisierung: {0} Hz | {1}' -f $rateDisplay, $it.Label) -ForegroundColor Cyan
                                    
                                    Start-Sleep -Seconds 7
                                    Write-Host 'Pause...' -ForegroundColor DarkGray
                                    Start-Sleep -Seconds 3
                                }
                            }
                            
                            Write-Host ''
                            Write-Host '=======================================' -ForegroundColor Green
                            Write-Host 'HARMONISIERUNG ABGESCHLOSSEN' -ForegroundColor Green
                            Write-Host '=======================================' -ForegroundColor Green
                            $totalElapsed = (Get-Date) - $startTime
                            Write-Host ('Gesamtdauer: {0}m {1}s' -f [math]::Floor($totalElapsed.TotalMinutes), $totalElapsed.Seconds) -ForegroundColor Cyan
                        }
                    }
                } catch {
                    Write-Host ('Fehler bei der Harmonisierung: {0}' -f $_.Exception.Message) -ForegroundColor Red
                }
            }
        }
        
        exit 0
    }
    
    # === SINGLE-SCAN POST-PROCESSING ===
    Write-Host ''
    Write-Host 'Single-Scan abgeschlossen. HTML-Bericht wurde im Benutzer_Archive_Start gespeichert.' -ForegroundColor Green
    Write-Host ''
    
    # === SYNERGY-BERICHT (SINGLE) ===
    Write-Host '=======================================' -ForegroundColor Yellow
    Write-Host 'SYNERGY-BERICHT (SINGLE-SCAN)' -ForegroundColor Yellow
    Write-Host '=======================================' -ForegroundColor Yellow
    Write-Host ''
    
    $synergyArgs = @(
        '-m', 'tools.synergy_consolidator',
        $Name,
        $FirstName,
        '--birth-date', $BirthDate,
        '--birth-place', $BirthPlace,
        '--single'
    )
    
    try {
        $synergyProcess = Start-Process -FilePath $pythonExe -ArgumentList $synergyArgs -WorkingDirectory $PSScriptRoot -NoNewWindow -Wait -PassThru
        if ($synergyProcess.ExitCode -eq 0) {
            Write-Host 'Synergy-Bericht wurde in C:\Benutzer_Synergy_Start gespeichert.' -ForegroundColor Green
        } else {
            Write-Host 'Synergy-Bericht konnte nicht erstellt werden.' -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Fehler bei Synergy-Generierung: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    Write-Host ''
    
    # === REMEDY-BERICHT ===
    Write-Host '=======================================' -ForegroundColor Magenta
    Write-Host 'REMEDY-BERICHT' -ForegroundColor Magenta
    Write-Host '=======================================' -ForegroundColor Magenta
    Write-Host ''
    
    $remedyArgs = @(
        '-m', 'tools.remedy_reporter',
        $Name,
        $FirstName,
        '--birth-date', $BirthDate,
        '--birth-place', $BirthPlace,
        '--single'
    )
    
    try {
        $remedyProcess = Start-Process -FilePath $pythonExe -ArgumentList $remedyArgs -WorkingDirectory $PSScriptRoot -NoNewWindow -Wait -PassThru
        if ($remedyProcess.ExitCode -eq 0) {
            Write-Host 'Remedy-Bericht wurde in C:\Benutzer_Remedies_Start gespeichert.' -ForegroundColor Green
        } else {
            Write-Host 'Remedy-Bericht konnte nicht erstellt werden.' -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Fehler bei Remedy-Generierung: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    Write-Host ''
    
    # === TRENDANALYSE ===
    Write-Host '=======================================' -ForegroundColor Cyan
    Write-Host 'TRENDANALYSE WIRD AKTUALISIERT...' -ForegroundColor Cyan
    Write-Host '=======================================' -ForegroundColor Cyan
    Write-Host ''
    
    $trendArgs = @(
        '-m', 'tools.trend_analyzer',
        $Name,
        $FirstName,
        '--birth-date', $BirthDate,
        '--birth-place', $BirthPlace,
        '--save',
        '--db',
        '--output', 'html',
        '--archive-root', 'C:\Benutzer_Archive_Start',
        '--output-root', 'C:\Benutzer_Trends_Start'
    )
    
    try {
        $trendProcess = Start-Process -FilePath $pythonExe -ArgumentList $trendArgs -WorkingDirectory $PSScriptRoot -NoNewWindow -Wait -PassThru
        if ($trendProcess.ExitCode -eq 0) {
            Write-Host 'Trendanalyse wurde in C:\Benutzer_Trends_Start gespeichert.' -ForegroundColor Green
        } else {
            Write-Host 'Trendanalyse konnte nicht erstellt werden (evtl. noch keine historischen Daten).' -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Fehler bei Trendanalyse: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    Write-Host ''
    
    # === DEUTUNGS-BERICHT (OPTIONAL) ===
    Write-Host '=======================================' -ForegroundColor Magenta
    Write-Host 'DEUTUNGS-BERICHT (SINGLE-SCAN)' -ForegroundColor Magenta
    Write-Host '=======================================' -ForegroundColor Magenta
    Write-Host ''
    Write-Host 'Moechten Sie eine Deutung fuer diesen Scan erstellen?' -ForegroundColor Yellow
    Write-Host '  J/j = Ja, mit KI-Analyse' -ForegroundColor DarkYellow
    Write-Host '  N/n = Nein, ueberspringen' -ForegroundColor DarkYellow
    Write-Host ''
    
    $deutungInput = Read-Host 'Deutung erstellen? (J/N, Standard N)'
    
    if ($deutungInput -eq 'J' -or $deutungInput -eq 'j') {
        $deutungArgs = @(
            '-m', 'tools.interpretation_generator',
            $Name,
            $FirstName,
            '--birth-date', $BirthDate,
            '--birth-place', $BirthPlace,
            '--scans', '1',
            '--age', '2',
            '--llm'
        )
        
        if (-not [string]::IsNullOrWhiteSpace($Focus)) {
            $deutungArgs += '--focus'
            # Focus als ein einziges Argument (wichtig bei Kommas/Leerzeichen)
            $deutungArgs += "`"$Focus`""
        }
        
        Write-Host ''
        Write-Host 'Deutungs-Bericht wird erstellt...' -ForegroundColor Magenta
        
        try {
            $deutungProcess = Start-Process -FilePath $pythonExe -ArgumentList $deutungArgs -WorkingDirectory $PSScriptRoot -NoNewWindow -Wait -PassThru
            if ($deutungProcess.ExitCode -eq 0) {
                Write-Host 'Deutungs-Bericht wurde in C:\Benutzer_Deutung_Start gespeichert.' -ForegroundColor Green
            } else {
                Write-Host 'Deutungs-Bericht konnte nicht erstellt werden.' -ForegroundColor Yellow
            }
        } catch {
            Write-Host "Fehler bei Deutungs-Generierung: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    } else {
        Write-Host 'Deutung uebersprungen.' -ForegroundColor Gray
    }
    
    Write-Host ''
    Write-Host '=======================================' -ForegroundColor Green
    Write-Host 'SINGLE-SCAN BERICHTE ABGESCHLOSSEN' -ForegroundColor Green
    Write-Host '=======================================' -ForegroundColor Green
    Write-Host ''
    Write-Host 'Gespeicherte Berichte:' -ForegroundColor White
    Write-Host '  - Scan-Bericht:     C:\Benutzer_Archive_Start' -ForegroundColor Gray
    Write-Host '  - Synergy-Bericht:  C:\Benutzer_Synergy_Start' -ForegroundColor Gray
    Write-Host '  - Remedy-Bericht:   C:\Benutzer_Remedies_Start' -ForegroundColor Gray
    Write-Host '  - Trendanalyse:     C:\Benutzer_Trends_Start' -ForegroundColor Gray
    if ($deutungInput -eq 'J' -or $deutungInput -eq 'j') {
        Write-Host '  - Deutung:          C:\Benutzer_Deutung_Start' -ForegroundColor Gray
    }
    Write-Host ''
}

exit $exitCode
