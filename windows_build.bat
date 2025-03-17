@echo off
REM Build script for Persian Life Manager Windows executable

echo Starting build process for Persian Life Manager...

REM Create necessary directories
mkdir build 2>nul
mkdir dist 2>nul

REM Check for Python installation
python --version
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed. Please install Python 3.11 or higher.
    exit /b 1
)

REM Check for pip installation
pip --version
if %ERRORLEVEL% NEQ 0 (
    echo Error: pip is not installed. Please install pip.
    exit /b 1
)

REM Install requirements
echo Installing required packages...
pip install -r requirements.txt
pip install pyinstaller

REM Create executable
echo Creating executable...
pyinstaller ^
    --name "Persian Life Manager" ^
    --icon=app/resources/images/icon.ico ^
    --windowed ^
    --noconfirm ^
    --clean ^
    --add-data "app/resources;app/resources" ^
    --add-data "app/templates;app/templates" ^
    --add-data "app/static;app/static" ^
    --add-data "serviceAccountKey.json;." ^
    --hidden-import firebase_admin ^
    --hidden-import firebase_admin.auth ^
    --hidden-import firebase_admin.credentials ^
    --hidden-import firebase_admin.firestore ^
    --hidden-import jdatetime ^
    --hidden-import PyQt6 ^
    --hidden-import PyQt6.QtWidgets ^
    --hidden-import PyQt6.QtCore ^
    --hidden-import PyQt6.QtGui ^
    --hidden-import PyQt6.QtWebEngineWidgets ^
    --hidden-import openai ^
    --hidden-import tflite_runtime ^
    run_desktop.py

echo Build complete!
echo The executable is located in the 'dist\Persian Life Manager' directory.
echo.
echo To create a Windows installer, you need NSIS installed.
echo Download NSIS from: https://nsis.sourceforge.io/Download

pause