#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Desktop entry point for Persian Life Manager Application - Fixed Version
"""

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication
from app.ui.login_window_fix import LoginWindowFixed

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
    """Main function for running the fixed desktop application"""
    try:
        # Create application directory if it doesn't exist
        app_dir = os.path.join(os.path.expanduser('~'), '.persian_life_manager')
        os.makedirs(app_dir, exist_ok=True)
        
        # Initialize QApplication with appropriate parameters
        app = QApplication(sys.argv)
        app.setApplicationName("Persian Life Manager")
        app.setApplicationDisplayName("Persian Life Manager")
        app.setStyle("Fusion")  # Use Fusion style for better cross-platform appearance
        
        # Set default font
        default_font = app.font()
        default_font.setPointSize(10)
        app.setFont(default_font)
        
        # Set stylesheet if available
        try:
            style_path = "app/ui/style/dark.qss"
            if os.path.exists(style_path):
                with open(style_path, "r", encoding="utf-8") as f:
                    app.setStyleSheet(f.read())
                logger.info(f"Applied stylesheet from {style_path}")
            else:
                # Fallback stylesheet for essential styling
                app.setStyleSheet("""
                    QWidget {
                        background-color: #121212;
                        color: #ffffff;
                    }
                    QPushButton {
                        background-color: #1a1a1a;
                        color: #ffffff;
                        border: 1px solid #333333;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #2a2a2a;
                        border: 1px solid #444444;
                    }
                    QLineEdit {
                        background-color: #2a2a2a;
                        color: #ffffff;
                        border: 1px solid #444444;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QLabel {
                        color: #ffffff;
                    }
                """)
                logger.warning(f"Stylesheet not found at {style_path}, using fallback styles")
        except Exception as e:
            logger.warning(f"Could not load stylesheet: {str(e)}")
        
        # Show login window
        login_window = LoginWindowFixed()
        login_window.show()
        
        # Run application
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Critical error in main application: {str(e)}", exc_info=True)
        # Create an emergency QApplication if needed
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(
            None, 
            "خطای سیستمی", 
            f"خطایی جدی در اجرای برنامه رخ داده است:\n{str(e)}"
        )
        sys.exit(1)

if __name__ == "__main__":
    main()