@echo off
setlocal EnableDelayedExpansion
REM ==============================================================================
REM SentinelAI - Workplace Safety Sentinel One-Click Launcher
REM ==============================================================================
echo ===================================================================
echo   SentinelAI - Workplace Safety Sentinel & Physical AI Engine
echo   HackwithBangalore 4.0 / CraftifAI PipeGen Track
echo ===================================================================
echo.

set "SCRIPT_DIR=%~dp0"

REM 1. Prioritize isolated project Virtual Environment (.venv)
if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" (
    set "PYTHON_CMD=%SCRIPT_DIR%.venv\Scripts\python.exe"
    echo [INFO] Active Environment: Project Virtual Environment (.venv)
) else (
    echo [INFO] Virtual environment not found. Checking system Python...
    where python >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set "PYTHON_CMD=python"
    ) else (
        where py >nul 2>nul
        if %ERRORLEVEL% EQU 0 (
            set "PYTHON_CMD=py"
        ) else if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
            set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
        ) else if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
            set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
        ) else (
            echo [ERROR] Python was not found in your system PATH!
            echo Please make sure Python 3.10+ is installed.
            echo.
            pause
            exit /b 1
        )
    )
)

echo [INFO] Using Python: %PYTHON_CMD%

REM 2. Ensure synthetic video asset exists
if not exist "%SCRIPT_DIR%backend\sample_assets\workplace_safety_demo.mp4" (
    echo [INFO] Generating high-resolution factory safety video scenario...
    "%PYTHON_CMD%" "%SCRIPT_DIR%backend\sample_assets\download_or_generate_samples.py"
)

REM 3. Launch Server (Browser will open automatically once listening)
echo [START] Starting SentinelAI Edge Server on http://127.0.0.1:8000 ...
echo [INFO] Please keep this window open while using the application.
echo [INFO] Press Ctrl+C in this terminal to stop the server.
echo.

"%PYTHON_CMD%" "%SCRIPT_DIR%backend\server.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Server encountered an unexpected issue and stopped.
    pause
)
