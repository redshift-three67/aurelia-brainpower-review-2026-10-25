@echo off
REM Schneller Test: Nur qwen2.5 Modelle

cd /d C:\Users\Hubert111\CascadeProjects\Radialgo2\Morphic_Engine_V1

echo ============================================================
echo QWEN2.5 QUALITÄTSTEST
echo ============================================================
echo.
echo Testet qwen2.5 Modelle (empfohlen für beste Balance):
echo.
echo 1. qwen2.5:1.5b - Sehr schnell, gut
echo 2. qwen2.5:3b   - Beste Balance (EMPFOHLEN)
echo.
echo Installiere zuerst (falls nicht vorhanden):
echo   ollama pull qwen2.5:1.5b
echo   ollama pull qwen2.5:3b
echo.

pause

echo.
echo ============================================================
echo TEST 1: qwen2.5:1.5b
echo ============================================================
echo.
python test_quality_comparison.py --model qwen2.5:1.5b

echo.
echo ============================================================
echo TEST 2: qwen2.5:3b
echo ============================================================
echo.
python test_quality_comparison.py --model qwen2.5:3b

echo.
echo ============================================================
echo TESTS ABGESCHLOSSEN
echo ============================================================
echo.

pause
