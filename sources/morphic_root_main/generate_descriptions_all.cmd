@echo off
REM Generiert alle fehlenden Beschreibungen

cd /d C:\Users\Hubert111\CascadeProjects\Radialgo2\Morphic_Engine_V1

echo ============================================================
echo BESCHREIBUNGS-GENERATOR
echo ============================================================
echo.
echo Generiert Beschreibungen für alle Items ohne Beschreibung
echo mit Ollama LLM (phi3:latest)
echo.
echo WICHTIG: Ollama muss laufen (ollama serve)
echo.

pause

python generate_descriptions.py --mode update --batch-size 10

echo.
echo ============================================================
echo FERTIG
echo ============================================================
echo.

pause
