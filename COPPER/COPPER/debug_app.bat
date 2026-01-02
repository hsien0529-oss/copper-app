@echo on
cd /d "%~dp0"

echo [STEP 1] Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please make sure Python is installed and added to PATH.
    pause
    goto :end
)

echo [STEP 2] Check pip...
pip --version
if %errorlevel% neq 0 (
    echo [ERROR] pip not found!
    pause
    goto :end
)

echo [STEP 3] Installing dependencies...
echo (If you have no internet, this will fail)
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] pip install returned error. 
    echo Continuing anyway to see if app can run...
)

echo [STEP 4] Starting Streamlit...
streamlit run copper_app.py

:end
echo.
echo [DEBUG] Script finished. Window will stay open.
cmd /k
