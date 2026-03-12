@echo off
REM ============================================
REM  Optical Measurement Tool - Build Script
REM  Creates a standalone distributable (.exe)
REM ============================================

set VENV=.venv
set PYTHON=%VENV%\Scripts\python.exe
set PYINSTALLER=%VENV%\Scripts\pyinstaller.exe

echo === Optical Measurement Tool - Build ===
echo.

REM Check if .venv exists
if not exist %VENV% (
    echo [1/4] Creating virtual environment...
    python -m venv %VENV%
) else (
    echo [1/4] Virtual environment already exists.
)

REM Install dependencies
echo [2/4] Installing dependencies...
%VENV%\Scripts\pip.exe install -r requirements.txt pyinstaller --quiet

REM Clean previous build
echo [3/4] Cleaning previous build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build with PyInstaller (single-file standalone)
echo [4/4] Building standalone executable...
%PYINSTALLER% ^
    --name "OpticalMeasurement" ^
    --onefile ^
    --windowed ^
    --noconfirm ^
    --clean ^
    --icon "assets\icon.ico" ^
    --add-data "assets;assets" ^
    --hidden-import PIL ^
    --hidden-import PIL._tkinter_finder ^
    --hidden-import numpy ^
    --hidden-import tkinter ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo === BUILD FAILED ===
    pause
    exit /b 1
)

REM Clean up build directory
echo Cleaning up temporary build files...
if exist build rmdir /s /q build
if exist OpticalMeasurement.spec del OpticalMeasurement.spec

echo.
echo === BUILD SUCCESSFUL ===
echo Output: dist\OpticalMeasurement.exe
echo Run:    dist\OpticalMeasurement.exe
echo.
pause
