@echo off
set "PYTHON_EXE=.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

%PYTHON_EXE% -c "from app.bootstrap import CLI_PROFILE, enforce_profile; enforce_profile(CLI_PROFILE); print('Radi144 CLI Runtime-Preflight: OK')"
if %errorlevel% neq 0 (
    echo.
    echo [FEHLER] Radi144 CLI Runtime-Preflight fehlgeschlagen.
    echo Bitte zuerst install_dependencies.bat ausfuehren.
    pause
    exit /b 1
)

%PYTHON_EXE% dev_cli.py --name "Max Mustermann" --dob "1980-05-20" --focus "Generelle Vitalisierung und Harmonisierung" > dev_results.txt 2>&1
type dev_results.txt
