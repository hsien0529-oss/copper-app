@echo off
cd /d "%~dp0"
echo Checking and installing dependencies...
pip install -r requirements.txt
echo Starting Copper Price App...
streamlit run copper_app.py
pause
