#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Login Window for Persian Life Manager Application
"""

import os
import sys
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QMessageBox, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSlot, QSize
from PyQt6.QtGui import QPixmap, QIcon, QColor

from app.core.auth import AuthService
from app.ui.main_window import MainWindow
from app.ui.widgets import NeonButton, NeonLineEdit, GlowLabel

logger = logging.getLogger(__name__)

class LoginWindow(QWidget):
    """Login and registration window for the application"""
    
    def __init__(self):
        super().__init__()
        
        self.auth_service = AuthService()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle("ورود به برنامه")
        self.setFixedSize(900, 600)
        self.setObjectName("loginWindow")
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left panel (graphic)
        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_panel.setFixedWidth(450)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # App logo & name
        app_title = GlowLabel("مدیریت مالی، سلامتی و زمان‌بندی", glow_color=QColor(0, 255, 170))
        app_title.setObjectName("appTitle")
        
        app_subtitle = QLabel("سامانه هوشمند برای زندگی مدرن")
        app_subtitle.setObjectName("appSubtitle")
        app_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        left_layout.addStretch(1)
        left_layout.addWidget(app_title, 0, Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(app_subtitle, 0, Qt.AlignmentFlag.AlignCenter)
        left_layout.addStretch(2)
        
        # Right panel (login form)
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        
        form_layout = QVBoxLayout(right_panel)
        form_layout.setContentsMargins(50, 50, 50, 50)
        form_layout.setSpacing(20)
        
        # Login form
        login_title = QLabel("ورود به حساب کاربری")
        login_title.setObjectName("loginTitle")
        login_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        username_label = QLabel("نام کاربری")
        self.username_input = NeonLineEdit()
        self.username_input.setPlaceholderText("نام کاربری خود را وارد کنید")
        
        password_label = QLabel("رمز عبور")
        self.password_input = NeonLineEdit()
        self.password_input.setPlaceholderText("رمز عبور خود را وارد کنید")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.remember_me = QCheckBox("مرا به خاطر بسپار")
        self.remember_me.setObjectName("rememberMe")
        
        # Login and register buttons
        buttons_layout = QHBoxLayout()
        
        self.login_btn = NeonButton("ورود")
        self.login_btn.clicked.connect(self.handle_login)
        
        self.register_btn = NeonButton("ثبت نام")
        self.register_btn.setColor(QColor(0, 170, 255))
        self.register_btn.clicked.connect(self.handle_register)
        
        buttons_layout.addWidget(self.login_btn)
        buttons_layout.addWidget(self.register_btn)
        
        # Add widgets to form layout
        form_layout.addWidget(login_title)
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.remember_me)
        form_layout.addStretch(1)
        form_layout.addLayout(buttons_layout)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
    @pyqtSlot()
    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "خطا", "لطفا نام کاربری و رمز عبور را وارد کنید.")
            return
        
        try:
            user = self.auth_service.login(username, password)
            if user:
                logger.info(f"User {username} logged in successfully")
                self.open_main_window(user)
            else:
                QMessageBox.warning(self, "خطا", "نام کاربری یا رمز عبور اشتباه است.")
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            QMessageBox.critical(self, "خطای سیستم", f"خطا در ورود: {str(e)}")
    
    @pyqtSlot()
    def handle_register(self):
        """Handle register button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "خطا", "لطفا نام کاربری و رمز عبور را وارد کنید.")
            return
            
        if len(password) < 6:
            QMessageBox.warning(self, "خطا", "رمز عبور باید حداقل ۶ کاراکتر باشد.")
            return
            
        try:
            if self.auth_service.user_exists(username):
                QMessageBox.warning(self, "خطا", "این نام کاربری قبلا ثبت شده است.")
                return
                
            user = self.auth_service.register(username, password)
            if user:
                QMessageBox.information(self, "ثبت نام موفق", "ثبت نام با موفقیت انجام شد. اکنون می‌توانید وارد شوید.")
                logger.info(f"User {username} registered successfully")
            else:
                QMessageBox.warning(self, "خطا", "خطا در ثبت نام. لطفا دوباره تلاش کنید.")
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            QMessageBox.critical(self, "خطای سیستم", f"خطا در ثبت نام: {str(e)}")
    
    def open_main_window(self, user):
        """Open the main application window"""
        self.main_window = MainWindow(user)
        self.main_window.show()
        self.close()
