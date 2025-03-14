#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Settings UI for Persian Life Manager Application
"""

import logging
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QCheckBox, QTabWidget, 
    QFormLayout, QFrame, QFileDialog, QMessageBox,
    QSpinBox, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSlot, QSize
from PyQt6.QtGui import QColor, QFont

from app.models.user import User
from app.core.auth import AuthService
from app.core.encryption import EncryptionService
from app.ui.widgets import NeonButton, NeonLineEdit, GlowLabel

logger = logging.getLogger(__name__)

class SettingsWidget(QWidget):
    """Settings widget for application configuration"""
    
    def __init__(self, user: User):
        super().__init__()
        
        self.user = user
        self.auth_service = AuthService()
        self.encryption_service = EncryptionService()
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize the UI components"""
        self.setObjectName("settingsWidget")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Module title
        title = QLabel("تنظیمات")
        title.setObjectName("moduleTitle")
        main_layout.addWidget(title)
        
        # Tabs for different settings
        self.tabs = QTabWidget()
        self.tabs.setObjectName("settingsTabs")
        
        # Create tabs
        self.account_tab = QWidget()
        self.appearance_tab = QWidget()
        self.backup_tab = QWidget()
        self.about_tab = QWidget()
        
        self.tabs.addTab(self.account_tab, "حساب کاربری")
        self.tabs.addTab(self.appearance_tab, "ظاهر برنامه")
        self.tabs.addTab(self.backup_tab, "پشتیبان‌گیری")
        self.tabs.addTab(self.about_tab, "درباره برنامه")
        
        # Setup tab contents
        self.setup_account_tab()
        self.setup_appearance_tab()
        self.setup_backup_tab()
        self.setup_about_tab()
        
        main_layout.addWidget(self.tabs)
        
    def setup_account_tab(self):
        """Setup the account settings tab"""
        layout = QVBoxLayout(self.account_tab)
        
        # User profile section
        profile_frame = QFrame()
        profile_frame.setObjectName("formCard")
        profile_layout = QFormLayout(profile_frame)
        
        # Username (display only)
        self.username_label = QLabel(self.user.username)
        
        # Change password section
        self.current_password = NeonLineEdit()
        self.current_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_password.setPlaceholderText("رمز عبور فعلی")
        
        self.new_password = NeonLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password.setPlaceholderText("رمز عبور جدید")
        
        self.confirm_password = NeonLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password.setPlaceholderText("تکرار رمز عبور جدید")
        
        self.change_password_btn = NeonButton("تغییر رمز عبور")
        self.change_password_btn.clicked.connect(self.change_password)
        
        # Add form fields
        profile_layout.addRow("نام کاربری:", self.username_label)
        profile_layout.addRow("رمز عبور فعلی:", self.current_password)
        profile_layout.addRow("رمز عبور جدید:", self.new_password)
        profile_layout.addRow("تکرار رمز عبور:", self.confirm_password)
        
        # Security settings
        security_frame = QFrame()
        security_frame.setObjectName("formCard")
        security_layout = QFormLayout(security_frame)
        
        self.enable_encryption = QCheckBox("رمزنگاری داده‌های حساس")
        self.enable_encryption.setChecked(True)
        
        self.auto_logout = QCheckBox("خروج خودکار پس از عدم فعالیت")
        
        self.logout_timeout = QSpinBox()
        self.logout_timeout.setRange(1, 60)
        self.logout_timeout.setValue(15)
        self.logout_timeout.setSuffix(" دقیقه")
        self.logout_timeout.setEnabled(False)
        
        self.auto_logout.stateChanged.connect(
            lambda state: self.logout_timeout.setEnabled(state == Qt.CheckState.Checked)
        )
        
        security_layout.addRow("", self.enable_encryption)
        security_layout.addRow("", self.auto_logout)
        security_layout.addRow("زمان خروج:", self.logout_timeout)
        
        # Save button
        self.save_account_btn = NeonButton("ذخیره تنظیمات")
        self.save_account_btn.clicked.connect(self.save_account_settings)
        
        layout.addWidget(QLabel("اطلاعات کاربری"))
        layout.addWidget(profile_frame)
        layout.addWidget(QLabel("تنظیمات امنیتی"))
        layout.addWidget(security_frame)
        layout.addWidget(self.change_password_btn)
        layout.addWidget(self.save_account_btn)
        layout.addStretch(1)
        
    def setup_appearance_tab(self):
        """Setup the appearance settings tab"""
        layout = QVBoxLayout(self.appearance_tab)
        
        # Theme settings
        theme_frame = QFrame()
        theme_frame.setObjectName("formCard")
        theme_layout = QFormLayout(theme_frame)
        
        self.theme_selector = QComboBox()
        self.theme_selector.addItem("تم نئون تیره (پیش‌فرض)")
        self.theme_selector.addItem("تم نئون روشن")
        self.theme_selector.addItem("تم کلاسیک")
        
        self.accent_color = QComboBox()
        self.accent_color.addItem("نئون سبز (پیش‌فرض)")
        self.accent_color.addItem("نئون آبی")
        self.accent_color.addItem("نئون بنفش")
        self.accent_color.addItem("نئون قرمز")
        
        self.font_size = QComboBox()
        self.font_size.addItem("کوچک")
        self.font_size.addItem("متوسط (پیش‌فرض)")
        self.font_size.addItem("بزرگ")
        
        theme_layout.addRow("تم برنامه:", self.theme_selector)
        theme_layout.addRow("رنگ اصلی:", self.accent_color)
        theme_layout.addRow("اندازه متن:", self.font_size)
        
        # UI preferences
        ui_frame = QFrame()
        ui_frame.setObjectName("formCard")
        ui_layout = QFormLayout(ui_frame)
        
        self.show_animations = QCheckBox("نمایش انیمیشن‌ها")
        self.show_animations.setChecked(True)
        
        self.compact_view = QCheckBox("نمای فشرده")
        
        self.rtl_layout = QCheckBox("چیدمان راست به چپ")
        self.rtl_layout.setChecked(True)
        
        ui_layout.addRow("", self.show_animations)
        ui_layout.addRow("", self.compact_view)
        ui_layout.addRow("", self.rtl_layout)
        
        # Preview section
        preview_label = QLabel("برای مشاهده تغییرات ظاهری، برنامه را مجدداً راه‌اندازی کنید.")
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_label.setObjectName("previewLabel")
        
        # Save button
        self.save_appearance_btn = NeonButton("ذخیره تنظیمات")
        self.save_appearance_btn.clicked.connect(self.save_appearance_settings)
        
        layout.addWidget(QLabel("تم و رنگ‌ها"))
        layout.addWidget(theme_frame)
        layout.addWidget(QLabel("تنظیمات رابط کاربری"))
        layout.addWidget(ui_frame)
        layout.addWidget(preview_label)
        layout.addWidget(self.save_appearance_btn)
        layout.addStretch(1)
        
    def setup_backup_tab(self):
        """Setup the backup settings tab"""
        layout = QVBoxLayout(self.backup_tab)
        
        # Backup section
        backup_frame = QFrame()
        backup_frame.setObjectName("formCard")
        backup_layout = QFormLayout(backup_frame)
        
        self.backup_location = NeonLineEdit()
        self.backup_location.setReadOnly(True)
        self.backup_location.setPlaceholderText("مسیر پیش‌فرض")
        
        browse_button = NeonButton("انتخاب مسیر")
        browse_button.clicked.connect(self.browse_backup_location)
        
        backup_location_layout = QHBoxLayout()
        backup_location_layout.addWidget(self.backup_location)
        backup_location_layout.addWidget(browse_button)
        
        self.auto_backup = QCheckBox("پشتیبان‌گیری خودکار")
        
        self.backup_interval = QComboBox()
        self.backup_interval.addItem("روزانه")
        self.backup_interval.addItem("هفتگی")
        self.backup_interval.addItem("ماهانه")
        self.backup_interval.setEnabled(False)
        
        self.auto_backup.stateChanged.connect(
            lambda state: self.backup_interval.setEnabled(state == Qt.CheckState.Checked)
        )
        
        backup_layout.addRow("مسیر پشتیبان:", backup_location_layout)
        backup_layout.addRow("", self.auto_backup)
        backup_layout.addRow("فاصله زمانی:", self.backup_interval)
        
        # Backup and restore buttons
        backup_button_layout = QHBoxLayout()
        
        self.create_backup_btn = NeonButton("ایجاد پشتیبان")
        self.create_backup_btn.clicked.connect(self.create_backup)
        
        self.restore_backup_btn = NeonButton("بازیابی پشتیبان")
        self.restore_backup_btn.setColor(QColor(0, 170, 255))
        self.restore_backup_btn.clicked.connect(self.restore_backup)
        
        backup_button_layout.addWidget(self.create_backup_btn)
        backup_button_layout.addWidget(self.restore_backup_btn)
        
        # Save backup settings
        self.save_backup_btn = NeonButton("ذخیره تنظیمات")
        self.save_backup_btn.clicked.connect(self.save_backup_settings)
        
        layout.addWidget(QLabel("تنظیمات پشتیبان‌گیری"))
        layout.addWidget(backup_frame)
        layout.addLayout(backup_button_layout)
        layout.addWidget(self.save_backup_btn)
        layout.addStretch(1)
        
    def setup_about_tab(self):
        """Setup the about tab"""
        layout = QVBoxLayout(self.about_tab)
        
        # Add scrollable area for about content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        about_content = QWidget()
        about_layout = QVBoxLayout(about_content)
        
        # App logo/title
        app_title = GlowLabel("مدیریت مالی، سلامتی و زمان‌بندی", glow_color=QColor(0, 255, 170))
        app_title.setObjectName("appTitleLarge")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        version_label = QLabel("نسخه 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setObjectName("versionLabel")
        
        # About text
        about_text = QLabel(
            """
            <p>این برنامه یک سامانه جامع برای مدیریت امور مالی، پیگیری وضعیت سلامتی و زمان‌بندی فعالیت‌ها است که به طور ویژه برای کاربران ایرانی طراحی شده است.</p>
            
            <h3>ویژگی‌های اصلی:</h3>
            <ul>
                <li>مدیریت مالی: ثبت و پیگیری تراکنش‌های مالی، دسته‌بندی هزینه‌ها و گزارش‌گیری</li>
                <li>مدیریت سلامتی: ثبت فعالیت‌های ورزشی، پیگیری شاخص‌های سلامتی و توصیه‌های هوشمند</li>
                <li>تقویم و زمان‌بندی: برنامه‌ریزی با تقویم شمسی، مدیریت رویدادها و یادآوری‌ها</li>
                <li>داشبورد: نمایش خلاصه‌ای از اطلاعات مهم مالی، سلامتی و زمان‌بندی</li>
                <li>پشتیبانی از تقویم شمسی (جلالی)</li>
                <li>رابط کاربری راست به چپ برای زبان فارسی</li>
                <li>ذخیره‌سازی امن و رمزنگاری شده اطلاعات حساس</li>
            </ul>
            
            <h3>فناوری‌های استفاده شده:</h3>
            <ul>
                <li>زبان برنامه‌نویسی: Python</li>
                <li>رابط کاربری: PyQt6</li>
                <li>پایگاه داده: SQLite</li>
                <li>تحلیل داده: Pandas</li>
                <li>نمایش نمودار: Matplotlib / Chart.js</li>
                <li>هوش مصنوعی: TensorFlow Lite</li>
            </ul>
            
            <p>© ۱۴۰۲ - تمامی حقوق محفوظ است.</p>
            """
        )
        about_text.setWordWrap(True)
        about_text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        about_text.setObjectName("aboutText")
        
        # Contact info
        contact_info = QLabel(
            """
            <p><strong>ارتباط با ما:</strong></p>
            <p>ایمیل: info@persianlifemanager.ir</p>
            <p>وب‌سایت: www.persianlifemanager.ir</p>
            """
        )
        contact_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contact_info.setObjectName("contactInfo")
        
        # Add all widgets to layout
        about_layout.addWidget(app_title)
        about_layout.addWidget(version_label)
        about_layout.addWidget(about_text)
        about_layout.addStretch(1)
        about_layout.addWidget(contact_info)
        
        # Set the scroll area content
        scroll_area.setWidget(about_content)
        
        layout.addWidget(scroll_area)
        
    def load_settings(self):
        """Load current settings"""
        # In a real app, this would load from a settings file or database
        # For this example, we'll just use defaults
        
        # Security settings
        self.enable_encryption.setChecked(True)
        self.auto_logout.setChecked(False)
        self.logout_timeout.setValue(15)
        
        # Appearance settings
        self.theme_selector.setCurrentIndex(0)  # Dark neon theme
        self.accent_color.setCurrentIndex(0)    # Neon green
        self.font_size.setCurrentIndex(1)       # Medium
        
        self.show_animations.setChecked(True)
        self.compact_view.setChecked(False)
        self.rtl_layout.setChecked(True)
        
        # Backup settings
        home_dir = os.path.expanduser("~")
        default_backup_path = os.path.join(home_dir, "Persian_Life_Manager_Backup")
        self.backup_location.setText(default_backup_path)
        
        self.auto_backup.setChecked(False)
        self.backup_interval.setCurrentIndex(1)  # Weekly
    
    @pyqtSlot()
    def change_password(self):
        """Handle password change request"""
        current_password = self.current_password.text()
        new_password = self.new_password.text()
        confirm_password = self.confirm_password.text()
        
        if not current_password or not new_password or not confirm_password:
            QMessageBox.warning(self, "خطا", "لطفا تمام فیلدها را پر کنید.")
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "خطا", "رمز عبور جدید و تکرار آن مطابقت ندارند.")
            return
        
        if len(new_password) < 6:
            QMessageBox.warning(self, "خطا", "رمز عبور باید حداقل ۶ کاراکتر باشد.")
            return
        
        # Verify current password
        if not self.auth_service.verify_password(self.user.username, current_password):
            QMessageBox.warning(self, "خطا", "رمز عبور فعلی اشتباه است.")
            return
        
        try:
            # Update password
            self.auth_service.change_password(self.user.username, new_password)
            
            # Clear password fields
            self.current_password.clear()
            self.new_password.clear()
            self.confirm_password.clear()
            
            QMessageBox.information(self, "موفقیت", "رمز عبور با موفقیت تغییر یافت.")
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در تغییر رمز عبور: {str(e)}")
    
    @pyqtSlot()
    def save_account_settings(self):
        """Save account settings"""
        # In a real app, this would save to a settings file or database
        encryption_enabled = self.enable_encryption.isChecked()
        auto_logout_enabled = self.auto_logout.isChecked()
        logout_timeout = self.logout_timeout.value()
        
        # Simulate saving settings
        settings = {
            "security": {
                "encryption_enabled": encryption_enabled,
                "auto_logout_enabled": auto_logout_enabled,
                "logout_timeout": logout_timeout
            }
        }
        
        logger.info(f"Account settings saved: {settings}")
        QMessageBox.information(self, "موفقیت", "تنظیمات حساب کاربری با موفقیت ذخیره شد.")
    
    @pyqtSlot()
    def save_appearance_settings(self):
        """Save appearance settings"""
        # In a real app, this would save to a settings file or database
        theme = self.theme_selector.currentText()
        accent_color = self.accent_color.currentText()
        font_size = self.font_size.currentText()
        
        show_animations = self.show_animations.isChecked()
        compact_view = self.compact_view.isChecked()
        rtl_layout = self.rtl_layout.isChecked()
        
        # Simulate saving settings
        settings = {
            "appearance": {
                "theme": theme,
                "accent_color": accent_color,
                "font_size": font_size,
                "show_animations": show_animations,
                "compact_view": compact_view,
                "rtl_layout": rtl_layout
            }
        }
        
        logger.info(f"Appearance settings saved: {settings}")
        QMessageBox.information(self, "موفقیت", "تنظیمات ظاهری با موفقیت ذخیره شد.")
    
    @pyqtSlot()
    def browse_backup_location(self):
        """Open dialog to select backup location"""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "انتخاب مسیر پشتیبان‌گیری",
            self.backup_location.text()
        )
        
        if directory:
            self.backup_location.setText(directory)
    
    @pyqtSlot()
    def create_backup(self):
        """Create a database backup"""
        # In a real app, this would actually create a backup
        backup_location = self.backup_location.text()
        
        if not backup_location:
            QMessageBox.warning(self, "خطا", "لطفا مسیر پشتیبان‌گیری را انتخاب کنید.")
            return
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(backup_location, exist_ok=True)
            
            # Simulate backup process
            QMessageBox.information(
                self, 
                "موفقیت", 
                f"پشتیبان‌گیری با موفقیت در مسیر زیر انجام شد:\n{backup_location}"
            )
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در ایجاد پشتیبان: {str(e)}")
    
    @pyqtSlot()
    def restore_backup(self):
        """Restore from a backup"""
        # In a real app, this would ask for a backup file and restore from it
        backup_file, _ = QFileDialog.getOpenFileName(
            self, 
            "انتخاب فایل پشتیبان",
            self.backup_location.text(),
            "Database Backup (*.db *.sqlite *.backup);;All Files (*)"
        )
        
        if not backup_file:
            return
        
        reply = QMessageBox.warning(
            self, 
            "هشدار", 
            "بازیابی پشتیبان باعث حذف تمام داده‌های فعلی می‌شود. آیا مطمئن هستید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Simulate restore process
                QMessageBox.information(
                    self, 
                    "موفقیت", 
                    "بازیابی پشتیبان با موفقیت انجام شد. لطفاً برنامه را مجدداً راه‌اندازی کنید."
                )
            except Exception as e:
                logger.error(f"Error restoring backup: {str(e)}")
                QMessageBox.critical(self, "خطا", f"خطا در بازیابی پشتیبان: {str(e)}")
    
    @pyqtSlot()
    def save_backup_settings(self):
        """Save backup settings"""
        # In a real app, this would save to a settings file or database
        backup_location = self.backup_location.text()
        auto_backup = self.auto_backup.isChecked()
        backup_interval = self.backup_interval.currentText()
        
        # Simulate saving settings
        settings = {
            "backup": {
                "location": backup_location,
                "auto_backup": auto_backup,
                "interval": backup_interval
            }
        }
        
        logger.info(f"Backup settings saved: {settings}")
        QMessageBox.information(self, "موفقیت", "تنظیمات پشتیبان‌گیری با موفقیت ذخیره شد.")
