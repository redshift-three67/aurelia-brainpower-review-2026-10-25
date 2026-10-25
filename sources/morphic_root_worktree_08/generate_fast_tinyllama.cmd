@echo off
REM Schnelle Generierung mit tinyllama (4 Threads)

cd /d C:\Users\Hubert111\CascadeProjects\Radialgo2\Morphic_Engine_V1

echo ============================================================
echo SCHNELLE BESCHREIBUNGS-GENERIERUNG
echo ============================================================
echo.
echo Modell: tinyllama (sehr schnell!)
echo Threads: 4 (parallel)
echo Geschwindigkeit: ~10-15x schneller als sequentiell
echo.
echo WICHTIG: 
echo 1. Ollama muss laufen (ollama serve)
echo 2. tinyllama muss installiert sein (ollama pull tinyllama)
echo.

pause

python generate_descriptions.py --mode update --threads 4 --model tinyllama --batch-size 20

echo.
echo ============================================================
echo FERTIG
echo ============================================================
echo.

pause
