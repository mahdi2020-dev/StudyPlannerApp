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
        
        # بررسی و تنظیم متغیرهای محیطی Supabase
        self.check_supabase_env()
        
        # راه‌اندازی سرویس احراز هویت
        self.auth_service = AuthService()
        self.auth_service.initialize()
        
        self.init_ui()
        
    def check_supabase_env(self):
        """بررسی و تنظیم متغیرهای محیطی Supabase"""
        import os
        import json
        import logging
        
        logger = logging.getLogger(__name__)
        
        # مسیر پیش‌فرض فایل تنظیمات
        config_path = os.path.expanduser("~/.persian_life_manager/config.json")
        
        # بررسی وجود متغیرهای محیطی
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        # اگر متغیرهای محیطی تنظیم نشده‌اند، از فایل تنظیمات بخوانیم
        if not supabase_url or not supabase_key:
            logger.info("Supabase environment variables not set. Trying to load from config file...")
            
            try:
                # بررسی وجود فایل تنظیمات
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        
                    # تنظیم متغیرهای محیطی از فایل تنظیمات
                    if 'SUPABASE_URL' in config:
                        os.environ['SUPABASE_URL'] = config['SUPABASE_URL']
                        logger.info("Loaded SUPABASE_URL from config file")
                        
                    if 'SUPABASE_KEY' in config:
                        os.environ['SUPABASE_KEY'] = config['SUPABASE_KEY']
                        logger.info("Loaded SUPABASE_KEY from config file")
                else:
                    # ایجاد فایل تنظیمات پیش‌فرض
                    logger.warning("Config file not found. Creating a default one.")
                    os.makedirs(os.path.dirname(config_path), exist_ok=True)
                    
                    # مقادیر پیش‌فرض برای فایل تنظیمات
                    default_config = {
                        'SUPABASE_URL': 'https://bkleshmdjkoonfphznsd.supabase.co',  # مقدار از تصویر دوم که ارسال کردید
                        'SUPABASE_KEY': '',  # نیاز به تنظیم دستی دارد
                    }
                    
                    with open(config_path, 'w') as f:
                        json.dump(default_config, f, indent=4)
                        
                    logger.info(f"Default config file created at {config_path}")
                    
                    # نمایش پیام به کاربر در مورد Supabase key
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self,
                        "تنظیمات Supabase",
                        f"فایل تنظیمات Supabase در مسیر زیر ایجاد شد:\n{config_path}\n\n"
                        "لطفاً کلید Supabase را در این فایل تنظیم کنید یا از گزینه «ورود به عنوان مهمان» استفاده نمایید.\n\n"
                        "کلید Supabase را می‌توانید از داشبورد خود در Supabase به دست آورید."
                    )
            except Exception as e:
                logger.error(f"Error loading config: {str(e)}")
        
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
        
        # Login and guest login buttons
        buttons_layout = QHBoxLayout()
        
        self.login_btn = NeonButton("ورود")
        self.login_btn.clicked.connect(self.handle_login)
        
        self.guest_btn = NeonButton("ورود به عنوان مهمان")
        self.guest_btn.setColor(QColor(0, 170, 255))
        self.guest_btn.clicked.connect(self.handle_guest_login)
        
        buttons_layout.addWidget(self.login_btn)
        buttons_layout.addWidget(self.guest_btn)
        
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
            # Use the updated auth service with Supabase
            success, session_id, error_message = self.auth_service.login(username, password)
            
            if success and session_id:
                # Get user from session
                user = self.auth_service.get_user_by_session(session_id)
                if user:
                    logger.info(f"User {username} logged in successfully")
                    self.open_main_window(user)
                else:
                    QMessageBox.warning(self, "خطا", "خطا در دریافت اطلاعات کاربری.")
            else:
                error_msg = error_message if error_message else "نام کاربری یا رمز عبور اشتباه است."
                QMessageBox.warning(self, "خطا", error_msg)
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            QMessageBox.critical(self, "خطای سیستم", f"خطا در ورود: {str(e)}")
    
    @pyqtSlot()
    def handle_guest_login(self):
        """Handle guest login button click"""
        # اول با روش ساده و مستقیم ورود مهمان را انجام می‌دهیم (مناسب برای EXE)
        # این روش جایگزین به طور خاص طراحی شده تا در محیط‌های بدون دسترسی به Supabase کار کند
        try:
            from app.core.auth import User
            import uuid
            import datetime
            
            logger.info("Using direct guest login method (for Windows EXE)")
            
            # ایجاد شناسه یکتا و داده‌های کاربر مهمان
            guest_id = f"guest-{uuid.uuid4()}"
            guest_user = User(
                user_id=guest_id,
                name="کاربر مهمان",
                email=f"{guest_id}@guest.persianlifemanager.app",
                is_guest=True
            )
            
            # ذخیره زمان ورود (اختیاری)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            guest_user.login_time = current_time
            
            logger.info(f"Direct guest login successful with ID: {guest_id}")
            self.open_main_window(guest_user)
            return
            
        except Exception as direct_error:
            # اگر روش اول با خطا مواجه شد، خطا را ثبت می‌کنیم
            logger.error(f"Direct guest login failed: {str(direct_error)}")
            
            # سپس روش دوم را امتحان می‌کنیم (استفاده از AuthService)
            try:
                # بررسی وجود و راه‌اندازی سرویس احراز هویت
                if hasattr(self, 'auth_service') and self.auth_service:
                    success, session_id, guest_user = self.auth_service.create_guest_session()
                    
                    if success and guest_user:
                        logger.info("Guest user logged in via auth service")
                        self.open_main_window(guest_user)
                        return
                    else:
                        logger.error("Auth service returned unsuccessful guest login")
                else:
                    logger.error("Auth service not initialized for guest login")
                    
                # اگر به اینجا رسیدیم، هر دو روش شکست خورده‌اند
                raise Exception("Both guest login methods failed")
                    
            except Exception as auth_error:
                logger.error(f"Auth service guest login error: {str(auth_error)}")
                
                # نمایش پیام خطا به کاربر
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self, 
                    "خطا در ورود مهمان", 
                    "متأسفانه ورود به عنوان مهمان با مشکل مواجه شد.\n"
                    "لطفاً مجدداً تلاش کنید یا با پشتیبانی تماس بگیرید."
                )
    
    def open_main_window(self, user):
        """Open the main application window"""
        self.main_window = MainWindow(user)
        self.main_window.show()
        self.close()
