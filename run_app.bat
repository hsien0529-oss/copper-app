@echo off
cd /d "%~dp0"
echo ==========================================
echo    Copper Price App - Launcher
echo ==========================================

:: 1. Check for Python
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python (remember to check "Add Python to PATH").
    echo Download: https://www.python.org/downloads/
    pause
    exit /b
)

:: 2. Install dependencies (Quiet mode to reduce noise, unless error)
echo [INFO] Checking dependencies...
pip install -r requirements.txt >nul
if %errorlevel% neq 0 (
    echo [WARNING] Failed to auto-install dependencies. 
    echo Trying to continue, but app might fail if libraries are missing.
    echo.
    echo If you are offline, this is expected.
)

:: 3. Run App
echo.
echo [INFO] Starting Application...
echo.
streamlit run copper_app.py

:: 4. Pause on exit
echo.
echo [INFO] App has closed.
pause
