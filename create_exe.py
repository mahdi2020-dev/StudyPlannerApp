#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build script for creating Windows executable (.exe) file for Persian Life Manager
"""

import os
import sys
import shutil
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not"""
    try:
        import PyInstaller
        logger.info("PyInstaller is already installed.")
    except ImportError:
        logger.info("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        logger.info("PyInstaller installed successfully.")

def create_executable():
    """Create executable using PyInstaller"""
    # Clean previous build if exists
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    logger.info("Creating executable...")
    
    # Create .spec file
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_desktop.py'],  # Use run_desktop.py instead of main.py for better desktop support
    pathex=[],
    binaries=[],
    datas=[
        ('app/resources', 'app/resources'),
        ('app/templates', 'app/templates'),
        ('app/static', 'app/static'),
        ('serviceAccountKey.json', '.'),
        ('app/ui/style', 'app/ui/style'),  # Include style files
    ],
    hiddenimports=[
        'firebase_admin',
        'firebase_admin.auth',
        'firebase_admin.credentials',
        'firebase_admin.firestore',
        'jdatetime',
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtWebEngineCore',
        'app.core.auth',
        'app.core.database',
        'app.core.firebase_adapter',
        'app.core.firebase_auth',
        'app.core.supabase_client',
        'app.models.user',
        'app.models.finance',
        'app.models.health',
        'app.models.calendar',
        'app.services.ai_service',
        'app.services.ai_chat_service',
        'app.services.ai_advisor',
        'app.services.speech_to_text',
        'app.services.religious_service',
        'app.services.calendar_converter',
        'app.ui.widgets',
        'app.ui.style',
        'app.ui.dashboard',
        'app.ui.main_window',
        'app.ui.login_window',
        'openai',
        'uuid',
        'webbrowser',
        'threading',
        'time',
        'datetime',
        'json',
        'logging',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Persian Life Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app/resources/images/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Persian Life Manager',
)
"""
    
    with open("persian_life_manager.spec", "w") as f:
        f.write(spec_content)
    
    # Run PyInstaller with the spec file
    subprocess.check_call([
        sys.executable, 
        "-m", 
        "PyInstaller", 
        "persian_life_manager.spec",
        "--clean"
    ])
    
    logger.info("Executable created successfully.")
    logger.info("The executable is located in the 'dist/Persian Life Manager' directory.")

def create_installer():
    """Create installer using NSIS (Windows only)"""
    if os.name != 'nt':
        logger.warning("NSIS installer can only be created on Windows. Skipping.")
        return
    
    try:
        import winreg
        # Check if NSIS is installed
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\NSIS")
            nsis_path = winreg.QueryValue(key, None)
            winreg.CloseKey(key)
        except:
            logger.error("NSIS not found. Please install NSIS from https://nsis.sourceforge.io/Download")
            return
        
        # Create NSIS script
        nsis_script = """
; Persian Life Manager Installer Script
!include "MUI2.nsh"

; General
Name "Persian Life Manager"
OutFile "Persian_Life_Manager_Setup.exe"
InstallDir "$PROGRAMFILES\\Persian Life Manager"
InstallDirRegKey HKCU "Software\\Persian Life Manager" ""

; Interface Settings
!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "Farsi"
!insertmacro MUI_LANGUAGE "English"

; Installer Sections
Section "Install"
  SetOutPath "$INSTDIR"
  File /r "dist\\Persian Life Manager\\*.*"
  
  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\\Persian Life Manager"
  CreateShortcut "$SMPROGRAMS\\Persian Life Manager\\Persian Life Manager.lnk" "$INSTDIR\\Persian Life Manager.exe"
  CreateShortcut "$DESKTOP\\Persian Life Manager.lnk" "$INSTDIR\\Persian Life Manager.exe"
  
  ; Write registry keys
  WriteRegStr HKCU "Software\\Persian Life Manager" "" $INSTDIR
  WriteUninstaller "$INSTDIR\\Uninstall.exe"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\PersianLifeManager" "DisplayName" "Persian Life Manager"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\PersianLifeManager" "UninstallString" "$INSTDIR\\Uninstall.exe"
SectionEnd

; Uninstaller Section
Section "Uninstall"
  ; Remove files and uninstaller
  RMDir /r "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$DESKTOP\\Persian Life Manager.lnk"
  Delete "$SMPROGRAMS\\Persian Life Manager\\Persian Life Manager.lnk"
  RMDir "$SMPROGRAMS\\Persian Life Manager"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\PersianLifeManager"
  DeleteRegKey HKCU "Software\\Persian Life Manager"
SectionEnd
"""
        
        with open("installer.nsi", "w") as f:
            f.write(nsis_script)
        
        # Run NSIS compiler
        makensis_path = os.path.join(nsis_path, "makensis.exe")
        if os.path.exists(makensis_path):
            subprocess.check_call([makensis_path, "installer.nsi"])
            logger.info("Installer created successfully.")
            logger.info("The installer is located at 'Persian_Life_Manager_Setup.exe'.")
        else:
            logger.error(f"NSIS compiler not found at {makensis_path}")
    except Exception as e:
        logger.error(f"Failed to create installer: {str(e)}")

def main():
    """Main function"""
    logger.info("Starting build process...")
    
    check_pyinstaller()
    create_executable()
    create_installer()
    
    logger.info("Build process completed.")

if __name__ == "__main__":
    main()