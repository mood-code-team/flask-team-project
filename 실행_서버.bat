@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title Mood Code

echo.
echo  Mood Code Server
echo  http://127.0.0.1:5000/
echo  Stop: Ctrl+C
echo.

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

set "PY=python"
if exist "venv\Scripts\python.exe" (
    set "PY=venv\Scripts\python.exe"
)

echo Python: %PY%
"%PY%" --version
if errorlevel 1 (
    echo Python not found. Install Python 3 or run: py -3 -m venv venv
    pause
    exit /b 1
)

"%PY%" -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo pip install failed
    pause
    exit /b 1
)

"%PY%" hspace_server.py
if errorlevel 1 (
    echo Server failed to start
    pause
    exit /b 1
)

pause
