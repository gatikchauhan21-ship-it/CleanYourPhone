@echo off
setlocal enabledelayedexpansion
title CleanYourPhone Launcher

echo ========================================================
echo         CleanYourPhone - Windows Launcher
echo ========================================================
echo.

:: Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

:: Check if ADB is installed
where adb >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARNING] ADB is not detected in your PATH.
    echo Ensure Android Platform Tools are installed and added to PATH.
    echo.
)

:: Install requirements if colorama or requests are missing
python -c "import colorama, requests" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [INFO] Installing required dependencies...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
)

echo [INFO] Starting CleanYourPhone CLI...
python -m src.cli
pause
