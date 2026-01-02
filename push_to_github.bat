@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo       GitHub Auto-Uploader Tool
echo       User: hsien0529-oss
echo ==========================================

:: 1. Check if Git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed on this system.
    echo Please download and install Git for Windows first.
    pause
    exit /b
)

:: 2. Initialize Git if not present
if not exist .git (
    echo [INFO] Initializing new Git repository...
    git init
    git branch -M main
)

:: 3. Add files
echo [INFO] Adding files...
git add .

:: 4. Commit
set /p commit_msg="Enter commit message (Press Enter for 'Auto Update'): "
if "%commit_msg%"=="" set commit_msg=Auto Update

echo [INFO] Committing with message: "%commit_msg%"
git commit -m "%commit_msg%"

:: 5. Check Remote
git remote get-url origin >nul 2>nul
if %errorlevel% equ 0 goto :push

:: 6. Add Remote if missing
echo.
echo [WARN] No remote repository linked.
echo Please create a NEW repository on GitHub first (do not add README/license).
set /p repo_name="Enter the Repository Name (e.g. copper-app): "
git remote add origin https://github.com/hsien0529-oss/%repo_name%.git

:push
echo.
echo [INFO] Pushing to GitHub (origin/main)...
git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Push failed!
    echo Possible reasons:
    echo 1. Repository name does not exist on GitHub.
    echo 2. You are not logged in (check pop-up window).
    echo 3. Conflict (pull first if repo is not empty).
) else (
    echo.
    echo [SUCCESS] Upload completed successfully!
)

pause
