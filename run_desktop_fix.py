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
        
        # Create directories for user data and application data
        user_data_dir = os.path.join(app_dir, 'user_data')
        app_data_dir = os.path.join(app_dir, 'app_data')
        os.makedirs(user_data_dir, exist_ok=True)
        os.makedirs(app_data_dir, exist_ok=True)
        
        # Disable OpenAI API key error by setting a placeholder
        # This prevents the error message from showing on startup
        if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("HUGGINGFACE_API_KEY"):
            # Set empty environment variables to prevent errors
            logger.info("Setting dummy API keys to prevent errors")
            os.environ["OPENAI_API_KEY"] = "sk_dummy_key_for_windows"
            os.environ["HUGGINGFACE_API_KEY"] = "hf_dummy_key_for_windows"
            
            # Save indicator that AI features will be disabled
            with open(os.path.join(app_data_dir, 'ai_features_disabled'), 'w', encoding='utf-8') as f:
                f.write("AI features are disabled due to missing API keys.")
            
            logger.info("AI features will be disabled for this session")
        
        # Set application as native
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        os.environ["QT_SCALE_FACTOR"] = "1"
        
        # Initialize QApplication with appropriate parameters
        app = QApplication(sys.argv)
        app.setApplicationName("Persian Life Manager")
        app.setApplicationDisplayName("Persian Life Manager")
        app.setStyle("Fusion")  # Use Fusion style for better cross-platform appearance
        
        # Set default font
        default_font = app.font()
        default_font.setPointSize(10)
        app.setFont(default_font)
        
        # Add icon for Windows
        try:
            from PyQt6.QtGui import QIcon
            icon_path = "generated-icon.png"
            if os.path.exists(icon_path):
                app.setWindowIcon(QIcon(icon_path))
                logger.info(f"Applied application icon from {icon_path}")
        except Exception as icon_error:
            logger.warning(f"Could not set application icon: {str(icon_error)}")
        
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