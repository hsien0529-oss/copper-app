@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==========================================
echo    Copper Price App - Launcher
echo    (Repair Version)
echo ==========================================

:: 1. Check for Python
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python (check "Add Python to PATH" during installation).
    echo Download: https://www.python.org/downloads/
    pause
    exit /b
)

:: 2. Install dependencies
echo [INFO] Checking dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Dependency check failed. 
    echo Trying to proceed anyway...
)

:: 3. Run App (Using python -m streamlit to identify path correctly)
echo.
echo [INFO] Starting Application...
echo.
python -m streamlit run copper_app.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application crashed or failed to start.
    echo Please take a screenshot of this error message.
    echo.
) else (
    echo.
    echo [INFO] App closed normally.
)

pause
