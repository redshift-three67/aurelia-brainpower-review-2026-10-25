@echo off
REM Qualitätstest: Vergleicht tinyllama vs phi3

cd /d C:\Users\Hubert111\CascadeProjects\Radialgo2\Morphic_Engine_V1

echo ============================================================
echo QUALITÄTSTEST: MODELL-VERGLEICH
echo ============================================================
echo.
echo Testet 30 Items aus verschiedenen Gruppen:
echo - Homöopathie, TCM, Schüssler
echo - Mineralien, Vitamine, Aminosäuren
echo - Bakterien, Viren, Meridiane
echo - Chakren, Frequenzen, Metalle
echo.
echo Vergleicht:
echo 1. tinyllama (schnell, einfach)
echo 2. phi3:latest (langsamer, präziser)
echo.

pause

python test_quality_comparison.py --compare

echo.
echo ============================================================
echo TEST ABGESCHLOSSEN
echo ============================================================
echo.

pause
