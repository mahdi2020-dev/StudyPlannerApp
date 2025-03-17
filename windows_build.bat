@echo off
echo ===================================
echo Building Persian Life Manager for Windows...
echo ===================================

:: Check if Python is installed
python --version 2>NUL
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.11 or later from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if PyInstaller is installed
python -c "import PyInstaller" 2>NUL
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo Error: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

:: Check for required Python packages
echo Checking dependencies...
python -c "import supabase" 2>NUL
if errorlevel 1 (
    echo Installing Supabase client...
    pip install supabase
)

python -c "import PyQt6" 2>NUL
if errorlevel 1 (
    echo Installing PyQt6...
    pip install PyQt6 PyQt6-WebEngine
)

python -c "import jdatetime" 2>NUL
if errorlevel 1 (
    echo Installing jdatetime...
    pip install jdatetime
)

python -c "import openai" 2>NUL
if errorlevel 1 (
    echo Installing OpenAI...
    pip install openai
)

echo Creating model file (if not exists)...
python create_model.py

:: Build the executable
echo Building executable...
pyinstaller --name="Persian Life Manager" ^
            --icon=generated-icon.png ^
            --windowed ^
            --clean ^
            --add-data="app/resources;app/resources" ^
            --add-data="app/static;app/static" ^
            --add-data="app/templates;app/templates" ^
            --add-data="app/ui/style;app/ui/style" ^
            run_desktop.py

:: Check if build was successful
if not exist "dist\Persian Life Manager\Persian Life Manager.exe" (
    echo Error: Build failed
    pause
    exit /b 1
)

echo ===================================
echo Build successful!
echo Executable created at dist\Persian Life Manager\Persian Life Manager.exe
echo ===================================

pause