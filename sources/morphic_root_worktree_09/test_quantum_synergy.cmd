@echo off
echo ======================================================================
echo QUANTUM-SYNERGY TEST SUITE
echo ======================================================================
echo.

cd /d "%~dp0"

python test_quantum_synergy.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================================================
    echo TESTS ERFOLGREICH ABGESCHLOSSEN
    echo ======================================================================
) else (
    echo.
    echo ======================================================================
    echo TESTS FEHLGESCHLAGEN - Fehlercode: %ERRORLEVEL%
    echo ======================================================================
)

pause
