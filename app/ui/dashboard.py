#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dashboard UI for Persian Life Manager Application
"""

import logging
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QFrame, QGridLayout, QHeaderView,
    QSplitter, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSlot, QDate, QSize
from PyQt6.QtGui import QColor, QFont

from app.services.finance_service import FinanceService
from app.services.health_service import HealthService
from app.services.calendar_service import CalendarService
from app.models.user import User
from app.ui.widgets import NeonCard, ChartWidget, GlowLabel
from app.utils.date_utils import get_current_persian_date, gregorian_to_persian
from app.utils.persian_utils import get_persian_month_name

logger = logging.getLogger(__name__)

class Dashboard(QWidget):
    """Main dashboard displaying summary information from all modules"""
    
    def __init__(self, user: User):
        super().__init__()
        
        self.user = user
        self.finance_service = FinanceService(user.id)
        self.health_service = HealthService(user.id)
        self.calendar_service = CalendarService(user.id)
        
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        """Initialize the UI components"""
        self.setObjectName("dashboard")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Welcome section
        welcome_layout = QHBoxLayout()
        
        self.welcome_label = GlowLabel(f"خوش آمدید، {self.user.username}!", glow_color=QColor(0, 255, 170))
        self.welcome_label.setObjectName("welcomeLabel")
        
        self.date_label = QLabel()
        self.date_label.setObjectName("dateLabel")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        welcome_layout.addWidget(self.welcome_label)
        welcome_layout.addStretch(1)
        welcome_layout.addWidget(self.date_label)
        
        main_layout.addLayout(welcome_layout)
        
        # Summary cards
        cards_layout = QHBoxLayout()
        
        # Financial summary card
        self.finance_card = NeonCard("خلاصه مالی", "", QColor(0, 255, 170))
        
        # Health summary card
        self.health_card = NeonCard("وضعیت سلامتی", "", QColor(255, 0, 128))
        
        # Tasks summary card
        self.tasks_card = NeonCard("وظایف امروز", "", QColor(0, 170, 255))
        
        cards_layout.addWidget(self.finance_card)
        cards_layout.addWidget(self.health_card)
        cards_layout.addWidget(self.tasks_card)
        
        main_layout.addLayout(cards_layout)
        
        # Finance and health charts row
        charts_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Financial chart
        self.finance_chart = ChartWidget("نمودار درآمد و هزینه ماهانه")
        
        # Health chart
        self.health_chart = ChartWidget("روند فعالیت‌های ورزشی هفتگی")
        
        charts_splitter.addWidget(self.finance_chart)
        charts_splitter.addWidget(self.health_chart)
        
        main_layout.addWidget(charts_splitter)
        
        # Bottom sections - upcoming events and tasks
        bottom_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Upcoming events section
        events_container = QWidget()
        events_layout = QVBoxLayout(events_container)
        
        events_title = QLabel("رویدادهای آینده")
        events_title.setObjectName("sectionTitle")
        
        self.events_table = QTableWidget()
        self.events_table.setColumnCount(4)
        self.events_table.setHorizontalHeaderLabels(["تاریخ", "زمان", "عنوان", "مکان"])
        self.events_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        events_layout.addWidget(events_title)
        events_layout.addWidget(self.events_table)
        
        # Pending tasks section
        tasks_container = QWidget()
        tasks_layout = QVBoxLayout(tasks_container)
        
        tasks_title = QLabel("وظایف در انتظار")
        tasks_title.setObjectName("sectionTitle")
        
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(4)
        self.tasks_table.setHorizontalHeaderLabels(["عنوان", "تاریخ مهلت", "اولویت", "وضعیت"])
        self.tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        tasks_layout.addWidget(tasks_title)
        tasks_layout.addWidget(self.tasks_table)
        
        bottom_splitter.addWidget(events_container)
        bottom_splitter.addWidget(tasks_container)
        
        main_layout.addWidget(bottom_splitter)
        
        # Update dashboard date
        self.update_date()
    
    def update_date(self):
        """Update the current date display"""
        current_persian_date = get_current_persian_date()
        self.date_label.setText(f"امروز: {current_persian_date}")
    
    def load_data(self):
        """Load data for all dashboard sections"""
        self.load_finance_summary()
        self.load_health_summary()
        self.load_tasks_summary()
        self.load_upcoming_events()
        self.load_pending_tasks()
        self.load_charts()
    
    def load_finance_summary(self):
        """Load financial summary for the dashboard"""
        try:
            summary = self.finance_service.get_monthly_summary()
            
            income = summary['income']
            expense = summary['expense']
            balance = income - expense
            
            balance_color = "green" if balance >= 0 else "red"
            
            summary_text = f"""
            <div style='text-align: center;'>
                <p>درآمد: {income:,} تومان</p>
                <p>هزینه: {expense:,} تومان</p>
                <p>مانده: <span style='color: {balance_color};'>{balance:,} تومان</span></p>
            </div>
            """
            
            self.finance_card.setHtml(summary_text)
        except Exception as e:
            logger.error(f"Error loading finance summary: {str(e)}")
            self.finance_card.setValue("خطا در بارگذاری اطلاعات")
    
    def load_health_summary(self):
        """Load health summary for the dashboard"""
        try:
            weekly_summary = self.health_service.get_weekly_summary()
            latest_metrics = self.health_service.get_latest_metrics()
            
            if not latest_metrics:
                self.health_card.setValue("داده‌ای برای نمایش وجود ندارد")
                return
            
            summary_text = f"""
            <div style='text-align: center;'>
                <p>وزن فعلی: {latest_metrics.weight} کیلوگرم</p>
                <p>فشار خون: {latest_metrics.systolic}/{latest_metrics.diastolic}</p>
                <p>فعالیت هفتگی: {weekly_summary['exercise_count']} جلسه ({weekly_summary['calories_burned']} کالری)</p>
            </div>
            """
            
            self.health_card.setHtml(summary_text)
        except Exception as e:
            logger.error(f"Error loading health summary: {str(e)}")
            self.health_card.setValue("خطا در بارگذاری اطلاعات")
    
    def load_tasks_summary(self):
        """Load tasks summary for the dashboard"""
        try:
            today_tasks = self.calendar_service.get_today_tasks()
            
            completed = sum(1 for task in today_tasks if task.completed)
            total = len(today_tasks)
            
            if total == 0:
                self.tasks_card.setValue("امروز وظیفه‌ای ندارید")
                return
            
            summary_text = f"""
            <div style='text-align: center;'>
                <p>تعداد کل: {total} وظیفه</p>
                <p>تکمیل شده: {completed} وظیفه</p>
                <p>باقیمانده: {total - completed} وظیفه</p>
            </div>
            """
            
            self.tasks_card.setHtml(summary_text)
        except Exception as e:
            logger.error(f"Error loading tasks summary: {str(e)}")
            self.tasks_card.setValue("خطا در بارگذاری اطلاعات")
    
    def load_upcoming_events(self):
        """Load upcoming events for the dashboard"""
        try:
            events = self.calendar_service.get_upcoming_events(limit=5)
            
            # Clear the table
            self.events_table.setRowCount(0)
            
            # Populate table
            for idx, event in enumerate(events):
                self.events_table.insertRow(idx)
                
                # Get Persian date
                persian_date = gregorian_to_persian(event.date)
                
                # Set table items
                self.events_table.setItem(idx, 0, QTableWidgetItem(persian_date))
                
                if event.all_day:
                    time_item = QTableWidgetItem("تمام روز")
                else:
                    time_item = QTableWidgetItem(f"{event.start_time} - {event.end_time}")
                
                self.events_table.setItem(idx, 1, time_item)
                self.events_table.setItem(idx, 2, QTableWidgetItem(event.title))
                self.events_table.setItem(idx, 3, QTableWidgetItem(event.location))
        except Exception as e:
            logger.error(f"Error loading upcoming events: {str(e)}")
    
    def load_pending_tasks(self):
        """Load pending tasks for the dashboard"""
        try:
            tasks = self.calendar_service.get_pending_tasks(limit=5)
            
            # Clear the table
            self.tasks_table.setRowCount(0)
            
            # Populate table
            for idx, task in enumerate(tasks):
                self.tasks_table.insertRow(idx)
                
                self.tasks_table.setItem(idx, 0, QTableWidgetItem(task.title))
                
                # Get Persian date
                persian_date = gregorian_to_persian(task.due_date)
                self.tasks_table.setItem(idx, 1, QTableWidgetItem(persian_date))
                
                # Priority
                priority_map = {
                    "low": "کم",
                    "medium": "متوسط",
                    "high": "زیاد"
                }
                priority_item = QTableWidgetItem(priority_map.get(task.priority, "متوسط"))
                if task.priority == "high":
                    priority_item.setForeground(QColor(255, 0, 128))
                elif task.priority == "medium":
                    priority_item.setForeground(QColor(0, 170, 255))
                else:
                    priority_item.setForeground(QColor(0, 255, 170))
                    
                self.tasks_table.setItem(idx, 2, priority_item)
                
                # Status
                due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                today = datetime.now().date()
                
                if due_date < today:
                    status_item = QTableWidgetItem("تاخیر")
                    status_item.setForeground(QColor(255, 0, 128))
                elif due_date == today:
                    status_item = QTableWidgetItem("امروز")
                    status_item.setForeground(QColor(0, 255, 170))
                else:
                    days_left = (due_date - today).days
                    status_item = QTableWidgetItem(f"{days_left} روز مانده")
                
                self.tasks_table.setItem(idx, 3, status_item)
        except Exception as e:
            logger.error(f"Error loading pending tasks: {str(e)}")
    
    def load_charts(self):
        """Load charts for the dashboard"""
        self.load_finance_chart()
        self.load_health_chart()
    
    def load_finance_chart(self):
        """Load financial chart for the dashboard"""
        try:
            monthly_data = self.finance_service.get_monthly_comparison()
            
            months = [get_persian_month_name(m['month']) for m in monthly_data]
            income_values = [m['income'] for m in monthly_data]
            expense_values = [m['expense'] for m in monthly_data]
            
            self.finance_chart.update_bar_chart(
                months,
                [
                    {'label': 'درآمد', 'data': income_values, 'color': 'rgba(0, 255, 170, 0.7)'},
                    {'label': 'هزینه', 'data': expense_values, 'color': 'rgba(255, 0, 128, 0.7)'}
                ]
            )
        except Exception as e:
            logger.error(f"Error loading finance chart: {str(e)}")
    
    def load_health_chart(self):
        """Load health chart for the dashboard"""
        try:
            exercise_data = self.health_service.get_exercise_trend(days=7)
            
            dates = [gregorian_to_persian(d['date']) for d in exercise_data]
            durations = [d['duration'] for d in exercise_data]
            
            self.health_chart.update_line_chart(
                dates, 
                durations,
                "دقیقه ورزش",
                "rgba(0, 255, 170, 0.7)"
            )
        except Exception as e:
            logger.error(f"Error loading health chart: {str(e)}")
