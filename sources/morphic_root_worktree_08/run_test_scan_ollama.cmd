@echo off
REM Test-Scan mit Ollama-Beschreibungen
REM Klientin: Claudia Von Rützen-Kositzkau
REM Fokus: Schwindel

cd /d C:\Users\Hubert111\CascadeProjects\Radialgo2\Morphic_Engine_V1

echo ============================================================
echo MORPHIC ENGINE V1 - TEST-SCAN MIT OLLAMA
echo ============================================================
echo.
echo Klientin: Claudia Von Rützen-Kositzkau
echo Fokus: Schwindel
echo Ollama-Modell: phi3:latest
echo.
echo Starte Scan...
echo.

python -m apps.cli.main multiplex-scan "Von Rützen-Kositzkau" Claudia -d 02031970 -p Berlin --profile full --seed test-ollama-20251116 --k-total 2048 --top-k 128 --focus Schwindel --hardware-profile windows --export "Benutzer_Archive"

echo.
echo ============================================================
echo SCAN ABGESCHLOSSEN
echo ============================================================
echo.
echo Bericht gespeichert in:
echo Benutzer_Archive\Von_Rützen-Kositzkau_Claudia_02031970_Berlin\
echo.

pause
