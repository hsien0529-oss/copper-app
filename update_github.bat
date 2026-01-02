@echo off
cd /d "%~dp0"

echo ==========================================
echo       GitHub Update Tool
echo ==========================================

echo [INFO] Adding all changes...
git add .

set /p commit_msg="Enter commit message (Press Enter for 'Update configuration'): "
if "%commit_msg%"=="" set commit_msg=Update configuration

echo [INFO] Committing...
git commit -m "%commit_msg%"

echo [INFO] Pushing to GitHub...
git push

if %errorlevel% neq 0 (
    echo [ERROR] Push failed. Please check your internet connection or git status.
) else (
    echo [SUCCESS] Changes pushed to GitHub successfully!
)

pause
