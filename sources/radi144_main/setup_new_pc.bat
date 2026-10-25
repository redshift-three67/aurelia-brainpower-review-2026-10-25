@echo off
setlocal enabledelayedexpansion

echo =======================================================
echo    12x12 Resonance Engine - New PC Setup Wizard
echo =======================================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FEHLER] Python wurde nicht gefunden.
    echo Bitte installieren Sie Python 3.10 oder neuer von https://www.python.org
    echo WICHTIG: Aktivieren Sie 'Add Python to PATH' waehrend der Installation.
    pause
    exit /b
)

echo [OK] Python gefunden.
echo.

:: 2. Create Virtual Environment (Optional but recommended)
set /p USE_VENV="Moechten Sie eine isolierte Umgebung (venv) erstellen? (j/N): "
if /i "%USE_VENV%"=="j" (
    echo Erstelle virtuelle Umgebung...
    python -m venv venv
    call venv\Scripts\activate
    echo [OK] Umgebung aktiviert.
)

:: 3. Upgrade pip
echo [1/3] Aktualisiere Paket-Manager (pip)...
python -m pip install --upgrade pip

:: 4. Install Requirements
echo [2/3] Installiere Kern-Abhaengigkeiten...
python -m pip install -r requirements.txt

:: 5. Install Additional Tools
echo [3/3] Installiere Erweiterungen...
python -m pip install psutil reportlab openpyxl numpy argcomplete

:: 6. Check PyTorch CUDA Status
echo.
echo =======================================================
echo    Hardware-Kompatibilitaets-Check
echo =======================================================
python -c "import torch; print('PyTorch Version:', torch.__version__); print('NVIDIA GPU (CUDA) verfuegbar:', 'JA' if torch.cuda.is_available() else 'NEIN (CPU Modus aktiv)')"
echo.

echo =======================================================
echo    Setup abgeschlossen.
echo    Sie koennen die Applikation nun mit 
echo    'generate_matrix.ps1' starten.
echo =======================================================
echo.
pause
