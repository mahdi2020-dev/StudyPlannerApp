#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main Window for Persian Life Manager Application - Fixed Version
"""

import sys
import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, 
    QPushButton, QLabel, QSizePolicy, QSpacerItem, QFrame, QApplication
)
from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QIcon, QFont

# Import our universal user class
from app.ui.simple_user_module import SimpleUser as SimplifiedUser

logger = logging.getLogger(__name__)

class SimpleNeonButton(QPushButton):
    """Simplified neon button for reliability"""
    
    def __init__(self, text="", icon_text="", parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(45)
        self._active = False
        self.icon_text = icon_text
        
        # Set button style directly
        self.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #cccccc;
                border: 1px solid #333333;
                border-radius: 3px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                text-align: left;
            }
            
            QPushButton:hover {
                background-color: #222222;
                border: 1px solid #444444;
                color: #ffffff;
            }
        """)
        
        if icon_text:
            self.setText(f"{icon_text} {text}")
    
    def setActive(self, active):
        """Set button active state"""
        self._active = active
        if active:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #243333;
                    color: #00ffaa;
                    border: 1px solid #00cc88;
                    border-radius: 3px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: bold;
                    text-align: left;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #1a1a1a;
                    color: #cccccc;
                    border: 1px solid #333333;
                    border-radius: 3px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: bold;
                    text-align: left;
                }
                
                QPushButton:hover {
                    background-color: #222222;
                    border: 1px solid #444444;
                    color: #ffffff;
                }
            """)
    
    def isActive(self):
        """Check if button is active"""
        return self._active


class UserProfileWidget(QFrame):
    """User profile widget for sidebar"""
    
    def __init__(self, user, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QFrame {
                background-color: #243333;
                border-radius: 3px;
            }
            
            QLabel#usernameLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
            }
            
            QLabel#userEmailLabel {
                color: #00ffaa;
                font-size: 12px;
            }
        """)
        self.setMinimumHeight(80)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Username - safely getting username
        username = getattr(user, "username", getattr(user, "name", "کاربر"))
        self.username_label = QLabel(username)
        self.username_label.setObjectName("usernameLabel")
        
        # Email - safely getting email
        email = getattr(user, "email", "")
        status_text = "آنلاین" if email else "کاربر مهمان"
        self.status_label = QLabel(status_text)
        self.status_label.setObjectName("userEmailLabel")
        
        layout.addWidget(self.username_label)
        layout.addWidget(self.status_label)


class DashboardWidget(QWidget):
    """Simplified Dashboard with message"""
    
    def __init__(self, user=None):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("داشبورد")
        title.setStyleSheet("color: #00ffaa; font-size: 24px; font-weight: bold;")
        
        welcome_msg = QLabel(f"به برنامه مدیریت زندگی پرشین خوش آمدید {getattr(user, 'username', '')}")
        welcome_msg.setStyleSheet("color: white; font-size: 16px;")
        
        status_msg = QLabel("این نسخه ساده‌شده برنامه است. برای استفاده از امکانات کامل، با پشتیبانی تماس بگیرید.")
        status_msg.setStyleSheet("color: #cccccc; font-size: 14px;")
        
        layout.addWidget(title)
        layout.addWidget(welcome_msg)
        layout.addSpacing(20)
        layout.addWidget(status_msg)
        layout.addStretch()


class PlaceholderWidget(QWidget):
    """Placeholder widget for modules"""
    
    def __init__(self, title):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #00ffaa; font-size: 24px; font-weight: bold;")
        
        message = QLabel("این بخش در نسخه آزمایشی در دسترس نیست.")
        message.setStyleSheet("color: white; font-size: 16px;")
        
        layout.addWidget(title_label)
        layout.addWidget(message)
        layout.addStretch()


class MainWindowFixed(QMainWindow):
    """Main application window with navigation and module containers - Fixed Version"""
    
    def __init__(self, user):
        super().__init__()
        
        # Validate user object has required attributes
        if not hasattr(user, 'username'):
            logger.error(f"User object missing username attribute: {user}")
            # Add username if missing
            user.username = getattr(user, 'name', "کاربر")
        
        if not hasattr(user, 'name'):
            logger.error(f"User object missing name attribute: {user}")
            # Add name if missing
            user.name = getattr(user, 'username', "کاربر")
        
        self.user = user
        logger.info(f"Initializing MainWindowFixed with user: {user.username}")
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle("مدیریت مالی، سلامتی و زمان‌بندی")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
                color: white;
            }
            QWidget {
                background-color: #121212;
                color: white;
            }
        """)
        
        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("""
            QWidget#sidebar {
                background-color: #1a1a1a;
                border-right: 1px solid #2a2a2a;
            }
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(10)
        
        # User profile section
        self.profile_widget = UserProfileWidget(self.user)
        sidebar_layout.addWidget(self.profile_widget)
        
        # Navigation buttons
        self.dashboard_btn = SimpleNeonButton("داشبورد", "🏠")
        self.finance_btn = SimpleNeonButton("مدیریت مالی", "💰")
        self.health_btn = SimpleNeonButton("سلامتی", "❤️")
        self.calendar_btn = SimpleNeonButton("زمان‌بندی", "📅")
        self.ai_advisor_btn = SimpleNeonButton("مشاور هوشمند", "🤖")
        self.settings_btn = SimpleNeonButton("تنظیمات", "⚙️")
        
        # Connect button signals
        self.dashboard_btn.clicked.connect(lambda: self.change_page(0))
        self.finance_btn.clicked.connect(lambda: self.change_page(1))
        self.health_btn.clicked.connect(lambda: self.change_page(2))
        self.calendar_btn.clicked.connect(lambda: self.change_page(3))
        self.ai_advisor_btn.clicked.connect(lambda: self.change_page(4))
        self.settings_btn.clicked.connect(lambda: self.change_page(5))
        
        # Add buttons to layout
        sidebar_layout.addWidget(self.dashboard_btn)
        sidebar_layout.addWidget(self.finance_btn)
        sidebar_layout.addWidget(self.health_btn)
        sidebar_layout.addWidget(self.calendar_btn)
        sidebar_layout.addWidget(self.ai_advisor_btn)
        sidebar_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        sidebar_layout.addWidget(self.settings_btn)
        
        main_layout.addWidget(self.sidebar)
        
        # Content area
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("contentArea")
        self.content_area.setStyleSheet("""
            QWidget#contentArea {
                background-color: #121212;
            }
        """)
        
        # Initialize simple modules
        self.dashboard = DashboardWidget(self.user)
        self.finance_module = PlaceholderWidget("مدیریت مالی")
        self.health_module = PlaceholderWidget("سلامتی")
        self.calendar_module = PlaceholderWidget("زمان‌بندی")
        self.ai_advisor_module = PlaceholderWidget("مشاور هوشمند")
        self.settings_widget = PlaceholderWidget("تنظیمات")
        
        # Add modules to stacked widget
        self.content_area.addWidget(self.dashboard)
        self.content_area.addWidget(self.finance_module)
        self.content_area.addWidget(self.health_module)
        self.content_area.addWidget(self.calendar_module)
        self.content_area.addWidget(self.ai_advisor_module)
        self.content_area.addWidget(self.settings_widget)
        
        main_layout.addWidget(self.content_area)
        
        # Set initial page
        self.content_area.setCurrentIndex(0)
        self.dashboard_btn.setActive(True)
    
    @pyqtSlot(int)
    def change_page(self, index):
        """Change the current page in the stacked widget"""
        # Reset all button states
        for btn in [self.dashboard_btn, self.finance_btn, self.health_btn, 
                    self.calendar_btn, self.ai_advisor_btn, self.settings_btn]:
            btn.setActive(False)
        
        # Set the active button
        if index == 0:
            self.dashboard_btn.setActive(True)
        elif index == 1:
            self.finance_btn.setActive(True)
        elif index == 2:
            self.health_btn.setActive(True)
        elif index == 3:
            self.calendar_btn.setActive(True)
        elif index == 4:
            self.ai_advisor_btn.setActive(True)
        elif index == 5:
            self.settings_btn.setActive(True)
        
        # Change the page
        self.content_area.setCurrentIndex(index)


# Standalone test
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # For better compatibility
    
    test_user = SimplifiedUser(username="تست")
    window = MainWindowFixed(test_user)
    window.show()
    
    sys.exit(app.exec())