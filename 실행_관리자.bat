@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title Mood Code Admin

echo.
echo  Mood Code Admin Server
echo  http://127.0.0.1:5000/admin
echo  ID: gygs1010
echo  PW: dnjsdlf@102360
echo  Stop: Ctrl+C
echo.

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

py -3 --version >nul 2>&1
if not errorlevel 1 (
    echo Bootstrap Python: py -3
    py -3 --version
    if errorlevel 1 goto no_python
    goto boot_ok
)

echo Bootstrap Python: python
python --version
if errorlevel 1 goto no_python
goto boot_ok

:no_python
echo Python not found. Install Python 3 from https://www.python.org/downloads/
pause
exit /b 1

:boot_ok
if not exist ".env" (
    if exist ".env.example" (
        copy /Y ".env.example" ".env" >nul
        echo [setup] .env created from .env.example
    )
)

py -3 --version >nul 2>&1
if not errorlevel 1 (
    py -3 scripts\ensure_venv.py
) else (
    python scripts\ensure_venv.py
)
if errorlevel 1 (
    echo venv setup failed
    pause
    exit /b 1
)

set "PY=venv\Scripts\python.exe"
echo Python: %PY%
"%PY%" --version
if errorlevel 1 (
    echo venv python not found after setup
    pause
    exit /b 1
)

if not exist "database\shop.db" (
    echo [setup] First run: creating database and sample data...
    "%PY%" scripts\seed_db.py
    if errorlevel 1 (
        echo seed_db.py failed
        pause
        exit /b 1
    )
)

"%PY%" -c "from app import create_app; from scripts.seed_db import seed_admin; app=create_app(); ctx=app.app_context(); ctx.push(); seed_admin(); ctx.pop()" >nul 2>&1

set "MOODCODE_OPEN_URL=/admin/"
set "FLASK_USE_RELOADER=0"
"%PY%" hspace_server.py
if errorlevel 1 (
    echo Server failed to start
    pause
    exit /b 1
)

pause
