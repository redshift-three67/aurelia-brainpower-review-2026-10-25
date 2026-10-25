@echo off
REM Parallele Generierung mit phi3 (4 Threads)

cd /d C:\Users\Hubert111\CascadeProjects\Radialgo2\Morphic_Engine_V1

echo ============================================================
echo PARALLELE BESCHREIBUNGS-GENERIERUNG
echo ============================================================
echo.
echo Modell: phi3:latest (gute Qualität)
echo Threads: 4 (parallel)
echo Geschwindigkeit: ~4-5x schneller als sequentiell
echo.
echo WICHTIG: Ollama muss laufen (ollama serve)
echo.

pause

python generate_descriptions.py --mode update --threads 4 --model phi3:latest --batch-size 20

echo.
echo ============================================================
echo FERTIG
echo ============================================================
echo.

pause
