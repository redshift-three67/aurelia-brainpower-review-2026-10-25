@echo off
REM Zeigt Statistiken der Beschreibungs-Datenbank

cd /d C:\Users\Hubert111\CascadeProjects\Radialgo2\Morphic_Engine_V1

echo ============================================================
echo BESCHREIBUNGS-DATENBANK - STATISTIKEN
echo ============================================================
echo.

python generate_descriptions.py --mode stats

echo.
pause
