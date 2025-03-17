#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Desktop entry point for Persian Life Manager Application
"""

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication
from app.ui.login_window import LoginWindow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.expanduser('~'), '.persian_life_manager', 'app.log'))
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function for running the desktop application"""
    # Create application directory if it doesn't exist
    app_dir = os.path.join(os.path.expanduser('~'), '.persian_life_manager')
    os.makedirs(app_dir, exist_ok=True)
    
    # Initialize QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Persian Life Manager")
    app.setApplicationDisplayName("Persian Life Manager")
    
    # Set stylesheet
    try:
        with open("app/ui/style/dark.qss", "r") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        logger.warning(f"Could not load stylesheet: {str(e)}")
    
    # Show login window
    login_window = LoginWindow()
    login_window.show()
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()