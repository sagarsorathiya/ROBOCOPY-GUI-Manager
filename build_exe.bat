@echo off
REM Build script for ROBOCOPY GUI standalone executable
REM This creates a .exe file that can run on any Windows PC without dependencies

echo ================================================
echo ROBOCOPY GUI - Standalone Executable Builder
echo ================================================
echo.
echo This will create RobocopyGUI.exe that can run on
echo any Windows PC without installing Python.
echo.
pause

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Building standalone executable...
echo.

REM Run the Python build script
python build.py

echo.
echo Build process completed.
echo Check the 'dist' folder for RobocopyGUI.exe
echo.
pause
