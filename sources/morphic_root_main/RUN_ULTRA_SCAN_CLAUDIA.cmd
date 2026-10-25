@echo off
echo ======================================================================
echo ULTRA-SCAN MIT QUANTUM-SYNERGY
echo ======================================================================
echo.
echo Klientin: Von Ruetzen-Kositzkau Claudia
echo Geburtsdatum: 02.03.1970
echo Ort: Berlin
echo Fokus: Schwindel
echo.
echo Features:
echo   - 277 Gruppen (Full-Profile)
echo   - Quantum-Synergy Analyse
echo   - Synergy-Kombinations-Groesse: 3
echo   - Synergy-Threshold: 7.0/10.0
echo.
echo ======================================================================
echo.

cd /d "%~dp0"

python -m apps.cli.main multiplex-scan "Von Rützen-Kositzkau" "Claudia" --birth-date "02031970" --birth-place "Berlin" --profile "full" --focus "Schwindel" --export "Benutzer_Archive" --synergy --synergy-combos 3 --synergy-threshold 7.0 --top-k 50

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================================================
    echo ULTRA-SCAN ERFOLGREICH ABGESCHLOSSEN
    echo ======================================================================
    echo.
    echo Bericht wurde im Klientin-Verzeichnis gespeichert:
    echo Benutzer_Archive\Von_Ruetzen-Kositzkau_Claudia_02031970_Berlin\
    echo.
    echo Dateien:
    echo   - JSON: Vollstaendige Scan-Daten
    echo   - HTML: Klienten-freundlicher Bericht mit Quantum-Synergy
    echo   - TXT:  Text-Zusammenfassung
    echo.
) else (
    echo.
    echo ======================================================================
    echo ULTRA-SCAN FEHLGESCHLAGEN - Fehlercode: %ERRORLEVEL%
    echo ======================================================================
)

pause
