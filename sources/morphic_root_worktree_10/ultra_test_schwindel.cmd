@echo off
echo ======================================================================
echo ULTRA-TEST: SCHWINDEL-ANALYSE MIT QUANTUM-SYNERGY
echo ======================================================================
echo.
echo Klientin: Von Ruetzen-Kositzkau Claudia
echo Fokus: Schwindel
echo.
echo ======================================================================
echo.

cd /d "%~dp0"

python ultra_test_schwindel.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================================================
    echo ULTRA-TEST ERFOLGREICH ABGESCHLOSSEN
    echo ======================================================================
    echo.
    echo Bericht wurde im Klientin-Verzeichnis gespeichert.
    echo.
) else (
    echo.
    echo ======================================================================
    echo ULTRA-TEST FEHLGESCHLAGEN - Fehlercode: %ERRORLEVEL%
    echo ======================================================================
)

pause
