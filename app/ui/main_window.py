#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main Window for Persian Life Manager Application
"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, 
    QPushButton, QLabel, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QIcon

from app.ui.dashboard import Dashboard
from app.ui.finance_module import FinanceModule
from app.ui.health_module import HealthModule
from app.ui.calendar_module import CalendarModule
from app.ui.settings import SettingsWidget
from app.ui.ai_advisor_module import AIAdvisorModule
from app.ui.widgets import NeonIconButton, UserProfileWidget
from app.core.auth import User

class MainWindow(QMainWindow):
    """Main application window with navigation and module containers"""
    
    def __init__(self, user: User):
        super().__init__()
        
        self.user = user
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle("مدیریت مالی، سلامتی و زمان‌بندی")
        self.setMinimumSize(1200, 800)
        
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
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # User profile section
        self.profile_widget = UserProfileWidget(self.user)
        sidebar_layout.addWidget(self.profile_widget)
        
        # Navigation buttons
        self.nav_buttons_container = QWidget()
        nav_buttons_layout = QVBoxLayout(self.nav_buttons_container)
        nav_buttons_layout.setContentsMargins(10, 20, 10, 20)
        nav_buttons_layout.setSpacing(10)
        
        # Create navigation buttons
        self.dashboard_btn = NeonIconButton("داشبورد", "🏠")
        self.finance_btn = NeonIconButton("مدیریت مالی", "💰")
        self.health_btn = NeonIconButton("سلامتی", "❤️")
        self.calendar_btn = NeonIconButton("زمان‌بندی", "📅")
        self.ai_advisor_btn = NeonIconButton("مشاور هوشمند", "🤖")
        self.settings_btn = NeonIconButton("تنظیمات", "⚙️")
        
        # Connect button signals
        self.dashboard_btn.clicked.connect(lambda: self.change_page(0))
        self.finance_btn.clicked.connect(lambda: self.change_page(1))
        self.health_btn.clicked.connect(lambda: self.change_page(2))
        self.calendar_btn.clicked.connect(lambda: self.change_page(3))
        self.ai_advisor_btn.clicked.connect(lambda: self.change_page(4))
        self.settings_btn.clicked.connect(lambda: self.change_page(5))
        
        # Add buttons to layout
        nav_buttons_layout.addWidget(self.dashboard_btn)
        nav_buttons_layout.addWidget(self.finance_btn)
        nav_buttons_layout.addWidget(self.health_btn)
        nav_buttons_layout.addWidget(self.calendar_btn)
        nav_buttons_layout.addWidget(self.ai_advisor_btn)
        nav_buttons_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        nav_buttons_layout.addWidget(self.settings_btn)
        
        sidebar_layout.addWidget(self.nav_buttons_container)
        main_layout.addWidget(self.sidebar)
        
        # Content area
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("contentArea")
        
        # Initialize modules
        self.dashboard = Dashboard(self.user)
        self.finance_module = FinanceModule(self.user)
        self.health_module = HealthModule(self.user)
        self.calendar_module = CalendarModule(self.user)
        self.ai_advisor_module = AIAdvisorModule(self.user)
        self.settings_widget = SettingsWidget(self.user)
        
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
