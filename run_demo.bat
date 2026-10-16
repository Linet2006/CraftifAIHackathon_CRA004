@echo off
REM ==============================================================================
REM SentinelAI - Workplace Safety Sentinel One-Click Launcher
REM ==============================================================================
echo ===================================================================
echo   SentinelAI - Workplace Safety Sentinel & Physical AI Engine
echo   HackwithBangalore 4.0 / CraftifAI PipeGen Track
echo ===================================================================
echo.

set SCRIPT_DIR=%~dp0

REM Ensure synthetic video asset exists
if not exist "%SCRIPT_DIR%backend\sample_assets\workplace_safety_demo.mp4" (
    echo [INFO] Generating high-resolution factory safety video scenario...
    python "%SCRIPT_DIR%backend\sample_assets\download_or_generate_samples.py"
)

echo [START] Launching SentinelAI Backend & Operations Console on http://127.0.0.1:8000 ...
echo [INFO] Press Ctrl+C in this terminal to stop the server.
echo.

start http://127.0.0.1:8000
python "%SCRIPT_DIR%backend\server.py"
