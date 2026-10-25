@echo off
echo ======================================================================
echo PHASE 4 INTEGRATION TEST
echo ======================================================================
echo.

cd /d "%~dp0"

python test_phase4_integration.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================================================
    echo TEST ERFOLGREICH ABGESCHLOSSEN
    echo ======================================================================
) else (
    echo.
    echo ======================================================================
    echo TEST FEHLGESCHLAGEN - Fehlercode: %ERRORLEVEL%
    echo ======================================================================
)

pause
