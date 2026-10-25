@echo off
setlocal enabledelayedexpansion

echo =======================================================
echo    12x12 Resonance Engine - Dependency Installer
echo =======================================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FEHLER] Python wurde nicht gefunden.
    echo Bitte installieren Sie Python 3.10 oder neuer von python.org
    echo Achten Sie darauf, 'Add Python to PATH' anzukreuzen.
    pause
    exit /b
)

echo [OK] Python gefunden.
echo.

:: 1b. Create isolated project virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo [SETUP] Erstelle isolierte Projektumgebung .venv ...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [FEHLER] .venv konnte nicht erstellt werden.
        pause
        exit /b 1
    )
)

set "PYTHON_EXE=.venv\Scripts\python.exe"
echo [OK] Projekt-Python: %PYTHON_EXE%
echo.

:: 2. Upgrade pip
echo [1/3] Aktualisiere pip...
%PYTHON_EXE% -m pip install --upgrade pip

:: 3. Install Requirements
echo [2/3] Installiere Basis-Abhaengigkeiten...
%PYTHON_EXE% -m pip install -r requirements.txt

:: 4. Install specialized Audio/GUI/Export libs
echo [3/3] Installiere spezialisierte Bibliotheken...
%PYTHON_EXE% -m pip install reportlab openpyxl numpy argcomplete psutil

:: 5. Hard Runtime Verification (Option A)
echo.
echo Pruefe Radi144 API Runtime...
%PYTHON_EXE% -c "from app.bootstrap import API_PROFILE, enforce_profile; enforce_profile(API_PROFILE); import torch; print('API Runtime OK'); print('PyTorch Version:', torch.__version__); print('CUDA verfuegbar:', torch.cuda.is_available())"
if %errorlevel% neq 0 (
    echo [FEHLER] API Runtime Verification fehlgeschlagen.
    pause
    exit /b 1
)

echo.
echo Pruefe Radi144 CLI Runtime...
%PYTHON_EXE% -c "from app.bootstrap import CLI_PROFILE, enforce_profile; enforce_profile(CLI_PROFILE); import numpy; import reportlab; import openpyxl; print('CLI Runtime OK')"
if %errorlevel% neq 0 (
    echo [FEHLER] CLI Runtime Verification fehlgeschlagen.
    pause
    exit /b 1
)

echo.
echo =======================================================
echo    Installation abgeschlossen.
echo    Sie koennen nun generate_matrix.ps1 starten.
echo =======================================================
echo.
pause
