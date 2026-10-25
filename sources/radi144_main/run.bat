@echo off
echo Starting 12x12 Resonance Matrix Engine...
echo.

set "PYTHON_EXE=.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

:: Check if Python is installed
%PYTHON_EXE% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    pause
    exit /b
)

:: Install dependencies if needed (optional check)
:: pip install -r requirements.txt

:: Hard runtime preflight (Option A)
%PYTHON_EXE% -c "from app.bootstrap import API_PROFILE, enforce_profile; enforce_profile(API_PROFILE); print('Radi144 API Runtime-Preflight: OK')"
if %errorlevel% neq 0 (
    echo.
    echo [FEHLER] Radi144 API Runtime-Preflight fehlgeschlagen.
    echo Bitte zuerst install_dependencies.bat ausfuehren.
    pause
    exit /b 1
)

:: Start Server
%PYTHON_EXE% main.py

pause
