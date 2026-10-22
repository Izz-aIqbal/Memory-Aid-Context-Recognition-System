@echo off
REM Memory Aid System - Quick Launch Script
REM This batch file helps you quickly launch different modes

setlocal enabledelayedexpansion

echo.
echo ============================================
echo  Memory Aid with Context Recognition
echo ============================================
echo.
echo Select mode:
echo.
echo  1. Run with Mock Data (No Camera)
echo  2. Run with Webcam (Real Detection)
echo  3. Launch Web Dashboard
echo  4. Run Headless Mode
echo  5. Open All (App + Dashboard)
echo.

set /p choice="Enter choice (1-5): "

if "%choice%"=="1" (
    echo Running with mock data...
    python app.py --mock
) else if "%choice%"=="2" (
    echo Running with webcam...
    python app.py
) else if "%choice%"=="3" (
    echo Launching dashboard...
    streamlit run ui/dashboard.py
) else if "%choice%"=="4" (
    echo Running headless for 30 minutes...
    python app.py --headless --duration 30
) else if "%choice%"=="5" (
    echo Opening both app and dashboard...
    start cmd /k python app.py --mock
    timeout /t 2
    streamlit run ui/dashboard.py
) else (
    echo Invalid choice!
)

pause
