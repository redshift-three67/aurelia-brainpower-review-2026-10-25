# Run-Harmonization.ps1 - Hardware-Harmonisierung starten/stoppen/status
# Direkte Steuerung des Harmonisierungs-Systems

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ''
Write-Host '=======================================' -ForegroundColor Cyan
Write-Host 'HARDWARE-HARMONISIERUNG' -ForegroundColor Cyan
Write-Host '=======================================' -ForegroundColor Cyan
Write-Host ''

# Python-Interpreter
$pythonExe = 'python'

# Menü
Write-Host 'Optionen:' -ForegroundColor Yellow
Write-Host '  1) Starten   - Neue Harmonisierung starten' -ForegroundColor DarkYellow
Write-Host '  2) Status    - Aktuellen Status anzeigen' -ForegroundColor DarkYellow
Write-Host '  3) Stoppen   - Laufende Harmonisierung beenden' -ForegroundColor DarkYellow
Write-Host '  0) Beenden   - Skript beenden' -ForegroundColor DarkYellow
Write-Host ''

$choice = Read-Host 'Auswahl (0-3)'

switch ($choice) {
    '1' {
        # Starten
        Write-Host ''
        Write-Host 'Harmonisierungs-Parameter:' -ForegroundColor Yellow
        Write-Host ''
        
        $frequencyInput = Read-Host 'Frequenz in Hz (Standard: 432.0 = harmonisch)'
        if ([string]::IsNullOrWhiteSpace($frequencyInput)) {
            $frequency = 432.0
        } else {
            $frequency = [double]$frequencyInput
        }
        
        $durationInput = Read-Host 'Dauer in Minuten (Standard: 5)'
        if ([string]::IsNullOrWhiteSpace($durationInput)) {
            $duration = 5
        } else {
            $duration = [int]$durationInput
        }
        
        Write-Host ''
        Write-Host 'Intention:' -ForegroundColor Yellow
        Write-Host '  1) healing        - Heilung' -ForegroundColor DarkYellow
        Write-Host '  2) clearing       - Klärung' -ForegroundColor DarkYellow
        Write-Host '  3) protection     - Schutz' -ForegroundColor DarkYellow
        Write-Host '  4) transformation - Transformation' -ForegroundColor DarkYellow
        Write-Host '  5) harmonization  - Harmonisierung (Standard)' -ForegroundColor DarkYellow
        Write-Host '  6) activation     - Aktivierung' -ForegroundColor DarkYellow
        Write-Host ''
        
        $intentionInput = Read-Host 'Intention (1-6, Standard 5)'
        $intention = 'harmonization'
        switch ($intentionInput) {
            '1' { $intention = 'healing' }
            '2' { $intention = 'clearing' }
            '3' { $intention = 'protection' }
            '4' { $intention = 'transformation' }
            '5' { $intention = 'harmonization' }
            '6' { $intention = 'activation' }
            Default { $intention = 'harmonization' }
        }
        
        Write-Host ''
        Write-Host "Starte Harmonisierung ($frequency Hz, $duration Min, $intention)..." -ForegroundColor Cyan
        Write-Host ''
        
        $args = @(
            '-m', 'apps.cli.main', 'harmonize',
            $frequency,
            $duration,
            '--intention', $intention,
            '--cpu'
        )
        
        try {
            $output = & $pythonExe $args 2>&1 | Out-String
            Write-Host $output
            
            if ($LASTEXITCODE -eq 0) {
                # Extrahiere Job-ID aus Output
                if ($output -match 'Job-ID:\s*([a-f0-9-]+)') {
                    $jobId = $Matches[1]
                    
                    Write-Host ''
                    Write-Host '=======================================' -ForegroundColor Green
                    Write-Host 'HARMONISIERUNG LÄUFT' -ForegroundColor Green
                    Write-Host '=======================================' -ForegroundColor Green
                    Write-Host "Job-ID: $jobId" -ForegroundColor Cyan
                    Write-Host "Dauer: $duration Minuten" -ForegroundColor Cyan
                    Write-Host ''
                    
                    # Live-Status-Anzeige
                    $startTime = Get-Date
                    $endTime = $startTime.AddMinutes($duration)
                    
                    Write-Host 'Drücke STRG+C zum Abbrechen der Anzeige (Job läuft weiter!)' -ForegroundColor Yellow
                    Write-Host ''
                    
                    while ((Get-Date) -lt $endTime) {
                        $elapsed = (Get-Date) - $startTime
                        $remaining = $endTime - (Get-Date)
                        $progress = ($elapsed.TotalMinutes / $duration) * 100
                        
                        # Fortschrittsbalken
                        $barLength = 40
                        $filled = [math]::Floor($progress / 100 * $barLength)
                        $empty = $barLength - $filled
                        $bar = ('#' * $filled) + ('-' * $empty)
                        
                        Write-Host "`r[$bar] $([math]::Round($progress, 1))% | Verbleibend: $([math]::Floor($remaining.TotalMinutes))m $($remaining.Seconds)s" -NoNewline -ForegroundColor Cyan
                        
                        Start-Sleep -Seconds 5
                    }
                    
                    Write-Host ''
                    Write-Host ''
                    Write-Host 'Harmonisierung abgeschlossen!' -ForegroundColor Green
                } else {
                    Write-Host ''
                    Write-Host 'Harmonisierung gestartet (Job-ID nicht gefunden).' -ForegroundColor Yellow
                }
            } else {
                Write-Host ''
                Write-Host 'Fehler beim Starten der Harmonisierung.' -ForegroundColor Red
            }
        } catch {
            Write-Host ''
            Write-Host "Fehler: $_" -ForegroundColor Red
        }
    }
    
    '2' {
        # Status
        Write-Host ''
        Write-Host 'Hole Status...' -ForegroundColor Cyan
        Write-Host ''
        
        $args = @(
            '-m', 'apps.cli.main', 'harmonize-status'
        )
        
        try {
            & $pythonExe $args
        } catch {
            Write-Host ''
            Write-Host "Fehler: $_" -ForegroundColor Red
        }
    }
    
    '3' {
        # Stoppen
        Write-Host ''
        Write-Host 'Stoppe Harmonisierung...' -ForegroundColor Cyan
        Write-Host ''
        
        $args = @(
            '-m', 'apps.cli.main', 'harmonize-stop'
        )
        
        try {
            & $pythonExe $args
            if ($LASTEXITCODE -eq 0) {
                Write-Host ''
                Write-Host 'Harmonisierung gestoppt.' -ForegroundColor Green
            } else {
                Write-Host ''
                Write-Host 'Fehler beim Stoppen.' -ForegroundColor Red
            }
        } catch {
            Write-Host ''
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
