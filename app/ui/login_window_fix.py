#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Login Window for Persian Life Manager Application - Fixed Version
"""

import os
import sys
import logging
import time
import datetime
import uuid
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QMessageBox, QFrame, QSizePolicy,
    QApplication
)
from PyQt6.QtCore import Qt, pyqtSlot, QSize
from PyQt6.QtGui import QPixmap, QIcon, QColor

# Import the centralized user class
from app.ui.simple_user_module import SimpleUser as SimplifiedUser

logger = logging.getLogger(__name__)


# Simplified widgets for more reliable operation
class SimpleNeonButton(QPushButton):
    """Simplified neon button for reliability"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(45)
        
        # Set button style directly
        self.setStyleSheet("""
            QPushButton {
                background-color: #121212;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #1a1a1a;
                border: 1px solid #00ffcc;
                color: #00ffcc;
            }
            
            QPushButton:pressed {
                background-color: #00cc88;
                color: #121212;
            }
        """)


# Main Login Window
class LoginWindowFixed(QWidget):
    """Fixed and Simplified Login Window"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle("ورود به برنامه")
        self.setFixedSize(900, 600)
        
        # Main layout with two panels
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left panel (graphic)
        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #121212; color: white;")
        left_panel.setFixedWidth(450)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # App title
        app_title = QLabel("مدیریت مالی، سلامتی و زمان‌بندی")
        app_title.setStyleSheet("color: #00ffaa; font-size: 22px; font-weight: bold;")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        app_subtitle = QLabel("سامانه هوشمند برای زندگی مدرن")
        app_subtitle.setStyleSheet("color: white; font-size: 16px;")
        app_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        left_layout.addStretch(1)
        left_layout.addWidget(app_title)
        left_layout.addWidget(app_subtitle)
        left_layout.addStretch(2)
        
        # Right panel (login form)
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: #1a1a1a; color: white;")
        
        form_layout = QVBoxLayout(right_panel)
        form_layout.setContentsMargins(50, 50, 50, 50)
        form_layout.setSpacing(20)
        
        # Login form
        login_title = QLabel("ورود به حساب کاربری")
        login_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        login_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        username_label = QLabel("نام کاربری")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("نام کاربری خود را وارد کنید")
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                color: white;
                padding: 8px;
                border-radius: 3px;
                min-height: 35px;
            }
            QLineEdit:focus {
                border: 1px solid #00ffaa;
            }
        """)
        
        password_label = QLabel("رمز عبور")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("رمز عبور خود را وارد کنید")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                color: white;
                padding: 8px;
                border-radius: 3px;
                min-height: 35px;
            }
            QLineEdit:focus {
                border: 1px solid #00ffaa;
            }
        """)
        
        self.remember_me = QCheckBox("مرا به خاطر بسپار")
        self.remember_me.setStyleSheet("color: white;")
        
        # Login and alternate login buttons
        self.login_btn = SimpleNeonButton("ورود")
        self.login_btn.clicked.connect(self.handle_login)
        
        self.google_btn = SimpleNeonButton("ورود با حساب گوگل")
        self.google_btn.setStyleSheet("""
            QPushButton {
                background-color: #121212;
                color: #4285F4;
                border: 1px solid #4285F4;
                border-radius: 3px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a1a1a;
                border: 1px solid #5294FF;
            }
        """)
        self.google_btn.clicked.connect(self.handle_google_login)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #3a3a3a;")
        
        self.guest_btn = SimpleNeonButton("ورود به عنوان مهمان")
        self.guest_btn.setStyleSheet("""
            QPushButton {
                background-color: #121212;
                color: #00bfff;
                border: 1px solid #00bfff;
                border-radius: 3px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a1a1a;
                border: 1px solid #33ccff;
            }
        """)
        self.guest_btn.clicked.connect(self.handle_guest_login)
        
        # Add widgets to form layout
        form_layout.addWidget(login_title)
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.remember_me)
        form_layout.addStretch(1)
        form_layout.addWidget(self.login_btn)
        form_layout.addWidget(self.google_btn)
        form_layout.addWidget(separator)
        form_layout.addWidget(self.guest_btn)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
    
    @pyqtSlot()
    def handle_login(self):
        """Handle login button click - simplified version to just show we have data"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "خطا", "لطفا نام کاربری و رمز عبور را وارد کنید.")
            return
        
        # Show processing message
        processing_msg = QMessageBox(self)
        processing_msg.setWindowTitle("ورود")
        processing_msg.setText("در حال پردازش اطلاعات ورود...\nلطفاً منتظر بمانید.")
        processing_msg.setIcon(QMessageBox.Icon.Information)
        processing_msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
        processing_msg.show()
        
        # Simple simulation of processing delay
        QApplication.processEvents()
        time.sleep(1)
        processing_msg.close()
        
        # Create direct user for testing
        user = SimplifiedUser(
            id=f"user-{uuid.uuid4()}",
            username=username,
            email=f"{username}@example.com"
        )
        
        # Open main window
        self.open_main_window(user)
    
    @pyqtSlot()
    def handle_guest_login(self):
        """Handle guest login - simple direct implementation"""
        # Show processing message
        processing_msg = QMessageBox(self)
        processing_msg.setWindowTitle("ورود به عنوان مهمان")
        processing_msg.setText("در حال ایجاد حساب مهمان...\nلطفاً چند لحظه صبر کنید.")
        processing_msg.setIcon(QMessageBox.Icon.Information)
        processing_msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
        processing_msg.show()
        
        # Process events to show the message
        QApplication.processEvents()
        
        try:
            # Basic unique ID based on timestamp
            guest_id = f"guest-{int(time.time())}"
            
            # Create guest user with all required attributes
            guest_user = SimplifiedUser(
                id=guest_id,
                username="کاربر مهمان",
                name="کاربر مهمان",
                email=f"{guest_id}@guest.persianlifemanager.local",
                is_guest=True
            )
            
            # Log guest creation
            logger.info(f"Created guest user: {guest_user}")
            
            # Small delay for message visibility
            time.sleep(1)
            processing_msg.close()
            
            # Open main window with guest user
            self.open_main_window(guest_user)
            
        except Exception as e:
            # Close the processing message and show error
            processing_msg.close()
            
            error_msg = f"خطا در ایجاد حساب مهمان: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "خطا", error_msg)
    
    @pyqtSlot()
    def handle_google_login(self):
        """Simplified Google login for Windows - creates a custom user directly"""
        # Information about alternative approach
        info_msg = QMessageBox(self)
        info_msg.setWindowTitle("روش جایگزین ورود با گوگل")
        info_msg.setText(
            "به خاطر مشکلات مرتبط با ورود با گوگل در نسخه ویندوز، "
            "یک حساب ویژه با قابلیت‌های کامل ایجاد می‌شود.\n\n"
            "در نسخه‌های بعدی، ورود با گوگل به صورت کامل پشتیبانی خواهد شد."
        )
        info_msg.setIcon(QMessageBox.Icon.Information)
        info_msg.exec()
        
        # Show processing message
        processing_msg = QMessageBox(self)
        processing_msg.setWindowTitle("ورود با گوگل")
        processing_msg.setText("در حال ایجاد حساب کاربری...\nلطفاً چند لحظه صبر کنید.")
        processing_msg.setIcon(QMessageBox.Icon.Information)
        processing_msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
        processing_msg.show()
        
        # Process events to show the message
        QApplication.processEvents()
        
        try:
            # Create a unique ID
            google_id = f"google-{int(time.time())}"
            
            # Create Google user with a special name to distinguish it
            google_user = SimplifiedUser(
                id=google_id,
                username="کاربر گوگل",
                name="کاربر گوگل",
                email=f"{google_id}@gmail.persianlifemanager.local",
                is_guest=False  # Not a guest, but a special Google user
            )
            
            # Add special metadata
            google_user.metadata = {
                "provider": "google",
                "login_method": "alternative"
            }
            
            # Log creation
            logger.info(f"Created alternative Google user: {google_user}")
            
            # Small delay for message visibility
            time.sleep(1)
            processing_msg.close()
            
            # Open main window with Google user
            self.open_main_window(google_user)
            
        except Exception as e:
            # Close the processing message and show error
            processing_msg.close()
            
            error_msg = f"خطا در ایجاد حساب گوگل: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "خطا", error_msg)
    
    def open_main_window(self, user):
        """Open the main application window"""
        try:
            from app.ui.main_window_fix import MainWindowFixed
            
            # Show loading message
            loading_msg = QMessageBox(self)
            loading_msg.setWindowTitle("در حال بارگذاری")
            loading_msg.setText("لطفاً منتظر بمانید...\nدر حال بارگذاری برنامه‌ی اصلی")
            loading_msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
            loading_msg.show()
            QApplication.processEvents()
            
            # Log the user we're opening the window with
            logger.info(f"Opening main window with user: {user}")
            logger.info(f"User details: ID={user.id}, Username={user.username}, Name={user.name}")
            
            # Small delay for visibility
            time.sleep(1)
            
            # Create and show main window
            self.main_window = MainWindowFixed(user)
            
            # Close loading message
            loading_msg.close()
            
            # Show main window and close login
            self.main_window.show()
            self.close()
            
        except Exception as e:
            logger.error(f"Error opening main window: {str(e)}")
            QMessageBox.critical(
                self, 
                "خطا در باز کردن برنامه", 
                f"خطا در باز کردن پنجره اصلی برنامه:\n{str(e)}"
            )


# Standalone test
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # For better compatibility
    
    login = LoginWindowFixed()
    login.show()
    
    sys.exit(app.exec())