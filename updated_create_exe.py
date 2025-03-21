#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build script for creating Windows executable (.exe) file for Persian Life Manager
"""

import os
import sys
import subprocess
import pkg_resources
import shutil
import platform

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not"""
    try:
        pkg_resources.get_distribution("pyinstaller")
        print("PyInstaller is already installed.")
    except pkg_resources.DistributionNotFound:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully.")

def create_executable():
    """Create executable using PyInstaller"""
    print("Starting executable creation...")
    
    # Basic configuration
    app_name = "Persian Life Manager"
    entry_point = "run_desktop_fix.py"  # Use the simplified fixed version
    icon_path = "generated-icon.png"
    
    # Create or ensure the temporary build directory exists
    if not os.path.exists('build'):
        os.makedirs('build')
    
    # Create the spec file content with necessary configurations
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{entry_point}'],
    pathex=[os.path.abspath(os.getcwd())],
    binaries=[],
    datas=[
        ('app', 'app'),
        ('{icon_path}', '.'),
        ('.env', '.'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'logging',
        'json',
        'uuid',
        'time',
        'datetime',
        'os',
        'sys',
    ],
    hookspath=[],
    hooksconfig={{}},
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
    name='{app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{icon_path}'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{app_name}',
)
"""
    
    # Write the spec file
    spec_path = 'persian_life_manager.spec'
    with open(spec_path, 'w', encoding='utf-8') as spec_file:
        spec_file.write(spec_content)
    
    # Build with PyInstaller
    os.environ['PYTHONIOENCODING'] = 'utf-8'  # Make sure Unicode is handled correctly
    
    build_command = [
        'pyinstaller',
        '--clean',  # Clean cache before building
        spec_path
    ]
    
    try:
        subprocess.run(build_command, check=True)
        print(f"\n[SUCCESS] Executable created successfully in 'dist/{app_name}'")
        print(f"Run the application by opening 'dist/{app_name}/{app_name}.exe'")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Failed to create executable: {e}")
        return False
    
    return True

def create_installer():
    """Create installer using NSIS (Windows only)"""
    if platform.system() != 'Windows':
        print("Installer creation is only supported on Windows.")
        return False
    
    # Check if NSIS is installed
    nsis_path = shutil.which('makensis')
    if not nsis_path:
        print("NSIS (Nullsoft Scriptable Install System) is not installed or not in PATH.")
        print("Please install NSIS to create an installer: https://nsis.sourceforge.io/Download")
        return False
    
    print("Creating installer with NSIS...")
    
    # Create the NSIS script
    nsis_script = """
; Persian Life Manager Installer Script

!include "MUI2.nsh"

; Application information
Name "Persian Life Manager"
OutFile "Persian_Life_Manager_Setup.exe"
InstallDir "$PROGRAMFILES\\Persian Life Manager"
InstallDirRegKey HKCU "Software\\Persian Life Manager" ""

; Request application privileges
RequestExecutionLevel admin

; Interface settings
!define MUI_ABORTWARNING
!define MUI_ICON ".\\generated-icon.png"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installation section
Section "Install"
    SetOutPath "$INSTDIR"
    File /r "dist\\Persian Life Manager\\*.*"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\Persian Life Manager"
    CreateShortcut "$SMPROGRAMS\\Persian Life Manager\\Persian Life Manager.lnk" "$INSTDIR\\Persian Life Manager.exe"
    CreateShortcut "$DESKTOP\\Persian Life Manager.lnk" "$INSTDIR\\Persian Life Manager.exe"
    
    ; Write registry keys for uninstaller
    WriteRegStr HKCU "Software\\Persian Life Manager" "" $INSTDIR
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Persian Life Manager" "DisplayName" "Persian Life Manager"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Persian Life Manager" "UninstallString" "$INSTDIR\\Uninstall.exe"
SectionEnd

; Uninstaller section
Section "Uninstall"
    ; Remove application files
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\\Persian Life Manager\\Persian Life Manager.lnk"
    RMDir "$SMPROGRAMS\\Persian Life Manager"
    Delete "$DESKTOP\\Persian Life Manager.lnk"
    
    ; Remove registry keys
    DeleteRegKey HKCU "Software\\Persian Life Manager"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Persian Life Manager"
SectionEnd
"""
    
    # Write the NSIS script
    with open('installer.nsi', 'w', encoding='utf-8') as f:
        f.write(nsis_script)
    
    # Build the installer
    try:
        subprocess.run(['makensis', 'installer.nsi'], check=True)
        print("\n[SUCCESS] Installer created successfully: Persian_Life_Manager_Setup.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Failed to create installer: {e}")
        return False

def main():
    """Main function"""
    print("\n=== Persian Life Manager EXE Builder ===\n")
    
    # Verify Python version
    python_version = platform.python_version()
    print(f"Using Python {python_version}")
    
    # Check and install PyInstaller if needed
    check_pyinstaller()
    
    # Create executable
    if create_executable():
        # If on Windows, offer to create installer
        if platform.system() == 'Windows':
            create_installer_choice = input("\nDo you want to create an installer? (y/n): ").strip().lower()
            if create_installer_choice == 'y':
                create_installer()
    else:
        print("Executable creation failed. Please check the errors above.")

if __name__ == "__main__":
    main()