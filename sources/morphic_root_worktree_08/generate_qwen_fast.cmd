@echo off
REM Schnelle Generierung mit qwen2.5:3b (EMPFOHLEN)

cd /d C:\Users\Hubert111\CascadeProjects\Radialgo2\Morphic_Engine_V1

echo ============================================================
echo BESCHREIBUNGS-GENERIERUNG MIT QWEN2.5:3B
echo ============================================================
echo.
echo Modell: qwen2.5:3b (BESTE BALANCE!)
echo Threads: 4 (parallel)
echo.
echo Vorteile:
echo - 3x schneller als phi3
echo - Fast gleiche Qualität wie phi3
echo - Sehr gutes Deutsch
echo - Medizinisches Wissen
echo.
echo Geschätzte Dauer: 15-18 Min
echo.
echo WICHTIG: 
echo 1. Ollama muss laufen (ollama serve)
echo 2. qwen2.5:3b muss installiert sein:
echo    ollama pull qwen2.5:3b
echo.

pause

python generate_descriptions.py --mode update --threads 4 --model qwen2.5:3b --batch-size 20

echo.
echo ============================================================
echo FERTIG
echo ============================================================
echo.

pause
