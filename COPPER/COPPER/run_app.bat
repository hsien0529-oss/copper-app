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

:: 2. Install dependencies
echo [INFO] Checking dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies. Check your internet connection.
    pause
    exit /b
)

:: 3. Run App
echo.
echo [INFO] Starting Application...
echo.
streamlit run copper_app.py
pause
