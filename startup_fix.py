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
            # If running on Windows, always use the fixed desktop version
            logger.info("Detected Windows environment - running fixed desktop version")
            
            # تنظیم متغیرهای محیطی برای اجرای نیتیو در ویندوز
            logger.info("Setting up environment for native Windows execution")
            os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
            os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
            os.environ["QT_SCALE_FACTOR"] = "1"
            
            # بررسی متغیرهای محیطی API برای هوش مصنوعی
            # اگر تنظیم نشده باشند، مقادیر موقت برای جلوگیری از خطا تنظیم می‌شوند
            if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("HUGGINGFACE_API_KEY"):
                logger.info("Setting dummy API keys to prevent errors")
                os.environ["OPENAI_API_KEY"] = "sk_dummy_key_for_windows"
                os.environ["HUGGINGFACE_API_KEY"] = "hf_dummy_key_for_windows"
                
                # ذخیره علامت غیرفعال بودن ویژگی‌های هوش مصنوعی
                app_dir = os.path.join(os.path.expanduser('~'), '.persian_life_manager')
                app_data_dir = os.path.join(app_dir, 'app_data')
                os.makedirs(app_data_dir, exist_ok=True)
                
                with open(os.path.join(app_data_dir, 'ai_features_disabled'), 'w', encoding='utf-8') as f:
                    f.write("AI features are disabled due to missing API keys.")
                
                logger.info("AI features will be disabled for this session")
            
            try:
                # بررسی وجود کلاس User و ویژگی username
                # برای اطمینان از اینکه تغییرات لازم اعمال شده‌اند
                logger.info("Checking User class for username attribute...")
                from app.core.auth import User
                test_user = User("test-id", "Test User", "test@example.com")
                if hasattr(test_user, 'username'):
                    logger.info("User class has username attribute - all good!")
                else:
                    logger.warning("User class does not have username attribute - update code!")
            except Exception as e:
                logger.warning(f"Could not verify User class: {e}")
            
            # Create directories for local user data storage
            app_dir = os.path.join(os.path.expanduser('~'), '.persian_life_manager')
            user_data_dir = os.path.join(app_dir, 'user_data')
            os.makedirs(user_data_dir, exist_ok=True)
            logger.info(f"Ensuring user data directory exists: {user_data_dir}")
            
            # اجرای نسخه fixed بدون توجه به نتیجه بررسی
            logger.info("Starting Persian Life Manager Desktop (Windows Native)")
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