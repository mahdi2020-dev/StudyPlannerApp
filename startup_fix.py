#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quick Startup Script for Persian Life Manager
This script detects the platform and runs the most appropriate version
"""

import os
import sys
import platform
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def is_windows():
    """Check if platform is Windows"""
    return platform.system().lower() == 'windows'

def is_running_in_replit():
    """Check if the application is running in Replit environment"""
    return os.environ.get('REPL_ID') is not None

def main():
    """Main function that decides which version to run"""
    try:
        logger.info(f"Starting Persian Life Manager on {platform.system()}")
        
        if is_running_in_replit():
            # If running in Replit, use the web preview version
            logger.info("Detected Replit environment - running web interface")
            import main
            main.run_replit_web_preview()
        elif is_windows():
            # If running on Windows, use the desktop app with GUI
            logger.info("Detected Windows environment - running fixed desktop version")
            import run_desktop_fix
            run_desktop_fix.main()
        else:
            # For other platforms, try the standard desktop app
            logger.info(f"Running desktop app on {platform.system()}")
            import run_desktop
            run_desktop.main()
    
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"Error loading required modules: {e}")
        print("\nPlease ensure all dependencies are installed by running:")
        print("  pip install -r requirements.txt")
    
    except Exception as e:
        logger.critical(f"Critical error during startup: {e}", exc_info=True)
        print(f"Critical error during startup: {e}")
        
        # If PyQt6 is available, show error in GUI
        try:
            from PyQt6.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv)
            QMessageBox.critical(
                None, 
                "خطای سیستمی", 
                f"خطایی جدی در اجرای برنامه رخ داده است:\n{str(e)}"
            )
        except ImportError:
            # If PyQt6 is not available, just print the error
            pass

if __name__ == "__main__":
    main()