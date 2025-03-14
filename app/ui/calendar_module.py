#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Calendar Module UI for Time Management with Persian Calendar
"""

import logging
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QDateEdit, QTimeEdit, QSpinBox, QCheckBox, QTabWidget, 
    QFormLayout, QScrollArea, QFrame, QGridLayout, QSplitter,
    QMessageBox, QHeaderView, QCalendarWidget, QDialog,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSlot, QDate, QTime, QSize
from PyQt6.QtGui import QColor, QFont, QIcon

from app.services.calendar_service import CalendarService
from app.models.calendar import Event, Task, Reminder
from app.models.user import User
from app.ui.widgets import NeonButton, NeonLineEdit, NeonCard, GlowLabel, PersianCalendarWidget
from app.utils.date_utils import gregorian_to_persian, persian_to_gregorian, get_current_persian_date
from app.utils.persian_utils import get_persian_month_name, get_persian_weekday_name

logger = logging.getLogger(__name__)

class EventDialog(QDialog):
    """Dialog for adding/editing calendar events"""
    
    def __init__(self, parent=None, event=None):
        super().__init__(parent)
        self.event = event
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle("رویداد جدید" if not self.event else "ویرایش رویداد")
        self.setMinimumWidth(400)
        self.setObjectName("eventDialog")
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Event title
        self.title_input = NeonLineEdit()
        if self.event:
            self.title_input.setText(self.event.title)
        
        # Event date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        if self.event:
            self.date_input.setDate(QDate.fromString(self.event.date, "yyyy-MM-dd"))
        else:
            self.date_input.setDate(QDate.currentDate())
        
        # Event time
        time_layout = QHBoxLayout()
        
        self.start_time = QTimeEdit()
        if self.event:
            self.start_time.setTime(QTime.fromString(self.event.start_time, "HH:mm"))
        else:
            self.start_time.setTime(QTime.currentTime())
        
        self.end_time = QTimeEdit()
        if self.event:
            self.end_time.setTime(QTime.fromString(self.event.end_time, "HH:mm"))
        else:
            self.end_time.setTime(QTime.currentTime().addSecs(3600))  # Add 1 hour
        
        time_layout.addWidget(self.start_time)
        time_layout.addWidget(QLabel("تا"))
        time_layout.addWidget(self.end_time)
        
        # Location
        self.location_input = NeonLineEdit()
        if self.event:
            self.location_input.setText(self.event.location)
        
        # Description
        self.description_input = NeonLineEdit()
        if self.event:
            self.description_input.setText(self.event.description)
        
        # Is all-day event
        self.all_day = QCheckBox("رویداد تمام روز")
        if self.event:
            self.all_day.setChecked(self.event.all_day)
        
        # Add reminder
        self.reminder = QCheckBox("یادآوری")
        if self.event:
            self.reminder.setChecked(self.event.has_reminder)
        
        # Reminder time
        reminder_layout = QHBoxLayout()
        
        self.reminder_value = QSpinBox()
        self.reminder_value.setRange(1, 60)
        self.reminder_value.setValue(15)
        
        self.reminder_unit = QComboBox()
        self.reminder_unit.addItem("دقیقه")
        self.reminder_unit.addItem("ساعت")
        self.reminder_unit.addItem("روز")
        
        reminder_layout.addWidget(self.reminder_value)
        reminder_layout.addWidget(self.reminder_unit)
        
        # Add fields to form
        form_layout.addRow("عنوان:", self.title_input)
        form_layout.addRow("تاریخ:", self.date_input)
        form_layout.addRow("زمان:", time_layout)
        form_layout.addRow("مکان:", self.location_input)
        form_layout.addRow("توضیحات:", self.description_input)
        form_layout.addRow("", self.all_day)
        form_layout.addRow("", self.reminder)
        form_layout.addRow("یادآوری:", reminder_layout)
        
        # Connect signals
        self.all_day.stateChanged.connect(self.toggle_time_inputs)
        self.reminder.stateChanged.connect(self.toggle_reminder_inputs)
        
        # Initial states
        self.toggle_time_inputs(self.all_day.checkState())
        self.toggle_reminder_inputs(self.reminder.checkState())
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = NeonButton("انصراف")
        self.cancel_btn.setColor(QColor(255, 0, 128))
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = NeonButton("ذخیره")
        self.save_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
    
    def toggle_time_inputs(self, state):
        """Enable/disable time inputs based on all-day checkbox"""
        is_checked = state == Qt.CheckState.Checked
        self.start_time.setEnabled(not is_checked)
        self.end_time.setEnabled(not is_checked)
    
    def toggle_reminder_inputs(self, state):
        """Enable/disable reminder inputs based on reminder checkbox"""
        is_checked = state == Qt.CheckState.Checked
        self.reminder_value.setEnabled(is_checked)
        self.reminder_unit.setEnabled(is_checked)
    
    def get_event_data(self):
        """Get event data from the form"""
        title = self.title_input.text().strip()
        date = self.date_input.date().toString("yyyy-MM-dd")
        start_time = self.start_time.time().toString("HH:mm")
        end_time = self.end_time.time().toString("HH:mm")
        location = self.location_input.text().strip()
        description = self.description_input.text().strip()
        all_day = self.all_day.isChecked()
        has_reminder = self.reminder.isChecked()
        
        reminder_value = self.reminder_value.value()
        reminder_unit = self.reminder_unit.currentText()
        
        return {
            "title": title,
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "location": location,
            "description": description,
            "all_day": all_day,
            "has_reminder": has_reminder,
            "reminder_value": reminder_value,
            "reminder_unit": reminder_unit
        }


class TaskDialog(QDialog):
    """Dialog for adding/editing tasks"""
    
    def __init__(self, parent=None, task=None):
        super().__init__(parent)
        self.task = task
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle("وظیفه جدید" if not self.task else "ویرایش وظیفه")
        self.setMinimumWidth(400)
        self.setObjectName("taskDialog")
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Task title
        self.title_input = NeonLineEdit()
        if self.task:
            self.title_input.setText(self.task.title)
        
        # Due date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        if self.task:
            self.date_input.setDate(QDate.fromString(self.task.due_date, "yyyy-MM-dd"))
        else:
            self.date_input.setDate(QDate.currentDate())
        
        # Priority
        self.priority = QComboBox()
        self.priority.addItem("کم")
        self.priority.addItem("متوسط")
        self.priority.addItem("زیاد")
        if self.task:
            if self.task.priority == "low":
                self.priority.setCurrentIndex(0)
            elif self.task.priority == "medium":
                self.priority.setCurrentIndex(1)
            else:
                self.priority.setCurrentIndex(2)
        
        # Description
        self.description_input = NeonLineEdit()
        if self.task:
            self.description_input.setText(self.task.description)
        
        # Add reminder
        self.reminder = QCheckBox("یادآوری")
        if self.task:
            self.reminder.setChecked(self.task.has_reminder)
        
        # Reminder time
        reminder_layout = QHBoxLayout()
        
        self.reminder_value = QSpinBox()
        self.reminder_value.setRange(1, 60)
        self.reminder_value.setValue(15)
        
        self.reminder_unit = QComboBox()
        self.reminder_unit.addItem("دقیقه")
        self.reminder_unit.addItem("ساعت")
        self.reminder_unit.addItem("روز")
        
        reminder_layout.addWidget(self.reminder_value)
        reminder_layout.addWidget(self.reminder_unit)
        
        # Add fields to form
        form_layout.addRow("عنوان:", self.title_input)
        form_layout.addRow("تاریخ مهلت:", self.date_input)
        form_layout.addRow("اولویت:", self.priority)
        form_layout.addRow("توضیحات:", self.description_input)
        form_layout.addRow("", self.reminder)
        form_layout.addRow("یادآوری:", reminder_layout)
        
        # Connect signals
        self.reminder.stateChanged.connect(self.toggle_reminder_inputs)
        
        # Initial states
        self.toggle_reminder_inputs(self.reminder.checkState())
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = NeonButton("انصراف")
        self.cancel_btn.setColor(QColor(255, 0, 128))
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = NeonButton("ذخیره")
        self.save_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
    
    def toggle_reminder_inputs(self, state):
        """Enable/disable reminder inputs based on reminder checkbox"""
        is_checked = state == Qt.CheckState.Checked
        self.reminder_value.setEnabled(is_checked)
        self.reminder_unit.setEnabled(is_checked)
    
    def get_task_data(self):
        """Get task data from the form"""
        title = self.title_input.text().strip()
        due_date = self.date_input.date().toString("yyyy-MM-dd")
        
        priority_map = {
            0: "low",
            1: "medium",
            2: "high"
        }
        priority = priority_map.get(self.priority.currentIndex(), "medium")
        
        description = self.description_input.text().strip()
        has_reminder = self.reminder.isChecked()
        
        reminder_value = self.reminder_value.value()
        reminder_unit = self.reminder_unit.currentText()
        
        return {
            "title": title,
            "due_date": due_date,
            "priority": priority,
            "description": description,
            "has_reminder": has_reminder,
            "reminder_value": reminder_value,
            "reminder_unit": reminder_unit
        }


class CalendarModule(QWidget):
    """Calendar module for time management with Persian calendar"""
    
    def __init__(self, user: User):
        super().__init__()
        
        self.user = user
        self.calendar_service = CalendarService(user.id)
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        """Initialize the UI components"""
        self.setObjectName("calendarModule")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Module title
        title = QLabel("تقویم و مدیریت زمان")
        title.setObjectName("moduleTitle")
        main_layout.addWidget(title)
        
        # Tab widget for calendar sections
        self.tabs = QTabWidget()
        self.tabs.setObjectName("calendarTabs")
        
        # Create tabs
        self.calendar_tab = QWidget()
        self.tasks_tab = QWidget()
        self.reminders_tab = QWidget()
        
        self.tabs.addTab(self.calendar_tab, "تقویم")
        self.tabs.addTab(self.tasks_tab, "وظایف")
        self.tabs.addTab(self.reminders_tab, "یادآوری‌ها")
        
        # Setup tab contents
        self.setup_calendar_tab()
        self.setup_tasks_tab()
        self.setup_reminders_tab()
        
        main_layout.addWidget(self.tabs)
        
    def setup_calendar_tab(self):
        """Setup the calendar tab"""
        layout = QVBoxLayout(self.calendar_tab)
        
        # Date navigation
        nav_layout = QHBoxLayout()
        
        self.today_btn = NeonButton("امروز")
        self.today_btn.clicked.connect(self.go_to_today)
        
        self.prev_month_btn = NeonButton("ماه قبل")
        self.prev_month_btn.clicked.connect(self.go_to_prev_month)
        
        self.month_year_label = GlowLabel("", glow_color=QColor(0, 170, 255))
        self.month_year_label.setObjectName("monthYearLabel")
        self.month_year_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.next_month_btn = NeonButton("ماه بعد")
        self.next_month_btn.clicked.connect(self.go_to_next_month)
        
        nav_layout.addWidget(self.today_btn)
        nav_layout.addWidget(self.prev_month_btn)
        nav_layout.addWidget(self.month_year_label)
        nav_layout.addWidget(self.next_month_btn)
        
        layout.addLayout(nav_layout)
        
        # Calendar and events split view
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Persian Calendar widget
        self.calendar_widget = PersianCalendarWidget()
        self.calendar_widget.selectionChanged.connect(self.update_selected_date_events)
        
        # Events for selected date
        events_container = QWidget()
        events_layout = QVBoxLayout(events_container)
        
        self.selected_date_label = QLabel()
        self.selected_date_label.setObjectName("selectedDateLabel")
        
        self.add_event_btn = NeonButton("افزودن رویداد")
        self.add_event_btn.clicked.connect(self.add_event)
        
        self.events_list = QListWidget()
        self.events_list.setObjectName("eventsList")
        
        events_layout.addWidget(self.selected_date_label)
        events_layout.addWidget(self.add_event_btn)
        events_layout.addWidget(QLabel("رویدادهای امروز"))
        events_layout.addWidget(self.events_list)
        
        # Add widgets to splitter
        splitter.addWidget(self.calendar_widget)
        splitter.addWidget(events_container)
        
        # Set initial splitter sizes
        splitter.setSizes([int(self.width() * 0.7), int(self.width() * 0.3)])
        
        layout.addWidget(splitter)
        
        # Upcoming events section
        upcoming_container = QWidget()
        upcoming_layout = QVBoxLayout(upcoming_container)
        
        upcoming_label = QLabel("رویدادهای پیش رو")
        upcoming_label.setObjectName("sectionTitle")
        
        self.upcoming_events_table = QTableWidget()
        self.upcoming_events_table.setColumnCount(6)
        self.upcoming_events_table.setHorizontalHeaderLabels(["تاریخ", "زمان", "عنوان", "مکان", "توضیحات", "عملیات"])
        self.upcoming_events_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        upcoming_layout.addWidget(upcoming_label)
        upcoming_layout.addWidget(self.upcoming_events_table)
        
        layout.addWidget(upcoming_container)
    
    def setup_tasks_tab(self):
        """Setup the tasks tab"""
        layout = QVBoxLayout(self.tasks_tab)
        
        # Create task section
        form_container = QFrame()
        form_container.setObjectName("formCard")
        form_layout = QHBoxLayout(form_container)
        
        self.task_title = NeonLineEdit()
        self.task_title.setPlaceholderText("عنوان وظیفه جدید")
        
        self.task_date = QDateEdit()
        self.task_date.setCalendarPopup(True)
        self.task_date.setDate(QDate.currentDate())
        
        self.task_priority = QComboBox()
        self.task_priority.addItem("کم")
        self.task_priority.addItem("متوسط")
        self.task_priority.addItem("زیاد")
        self.task_priority.setCurrentIndex(1)  # Default to medium
        
        self.add_task_btn = NeonButton("افزودن وظیفه")
        self.add_task_btn.clicked.connect(self.quick_add_task)
        
        form_layout.addWidget(self.task_title)
        form_layout.addWidget(QLabel("تاریخ:"))
        form_layout.addWidget(self.task_date)
        form_layout.addWidget(QLabel("اولویت:"))
        form_layout.addWidget(self.task_priority)
        form_layout.addWidget(self.add_task_btn)
        
        layout.addWidget(QLabel("افزودن وظیفه سریع"))
        layout.addWidget(form_container)
        
        # Tasks tabs (by status)
        tasks_tabs = QTabWidget()
        
        # Pending tasks
        self.pending_tasks_tab = QWidget()
        pending_layout = QVBoxLayout(self.pending_tasks_tab)
        
        self.pending_tasks_table = QTableWidget()
        self.pending_tasks_table.setColumnCount(6)
        self.pending_tasks_table.setHorizontalHeaderLabels(["عنوان", "تاریخ مهلت", "اولویت", "توضیحات", "تکمیل", "عملیات"])
        self.pending_tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        pending_layout.addWidget(self.pending_tasks_table)
        
        # Completed tasks
        self.completed_tasks_tab = QWidget()
        completed_layout = QVBoxLayout(self.completed_tasks_tab)
        
        self.completed_tasks_table = QTableWidget()
        self.completed_tasks_table.setColumnCount(5)
        self.completed_tasks_table.setHorizontalHeaderLabels(["عنوان", "تاریخ مهلت", "اولویت", "توضیحات", "عملیات"])
        self.completed_tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        completed_layout.addWidget(self.completed_tasks_table)
        
        tasks_tabs.addTab(self.pending_tasks_tab, "وظایف در انتظار")
        tasks_tabs.addTab(self.completed_tasks_tab, "وظایف تکمیل شده")
        
        layout.addWidget(tasks_tabs)
        
        # Add detailed task button
        self.add_detailed_task_btn = NeonButton("افزودن وظیفه با جزئیات")
        self.add_detailed_task_btn.clicked.connect(self.add_detailed_task)
        
        layout.addWidget(self.add_detailed_task_btn)
    
    def setup_reminders_tab(self):
        """Setup the reminders tab"""
        layout = QVBoxLayout(self.reminders_tab)
        
        # Today's reminders
        today_container = QWidget()
        today_layout = QVBoxLayout(today_container)
        
        today_label = QLabel("یادآوری‌های امروز")
        today_label.setObjectName("sectionTitle")
        
        self.today_reminders_list = QListWidget()
        self.today_reminders_list.setObjectName("remindersList")
        
        today_layout.addWidget(today_label)
        today_layout.addWidget(self.today_reminders_list)
        
        # Upcoming reminders
        upcoming_container = QWidget()
        upcoming_layout = QVBoxLayout(upcoming_container)
        
        upcoming_label = QLabel("یادآوری‌های آینده")
        upcoming_label.setObjectName("sectionTitle")
        
        self.upcoming_reminders_table = QTableWidget()
        self.upcoming_reminders_table.setColumnCount(5)
        self.upcoming_reminders_table.setHorizontalHeaderLabels(["تاریخ", "زمان", "عنوان", "نوع", "عملیات"])
        self.upcoming_reminders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        upcoming_layout.addWidget(upcoming_label)
        upcoming_layout.addWidget(self.upcoming_reminders_table)
        
        # Reminder settings
        settings_container = QFrame()
        settings_container.setObjectName("formCard")
        settings_layout = QHBoxLayout(settings_container)
        
        self.enable_notifications = QCheckBox("فعال‌سازی اعلان‌ها")
        self.enable_notifications.setChecked(True)
        
        self.default_reminder_time = QSpinBox()
        self.default_reminder_time.setRange(5, 60)
        self.default_reminder_time.setValue(15)
        self.default_reminder_time.setSuffix(" دقیقه قبل")
        
        self.save_reminder_settings = NeonButton("ذخیره تنظیمات")
        self.save_reminder_settings.clicked.connect(self.save_reminder_preferences)
        
        settings_layout.addWidget(self.enable_notifications)
        settings_layout.addWidget(QLabel("یادآوری پیش‌فرض:"))
        settings_layout.addWidget(self.default_reminder_time)
        settings_layout.addWidget(self.save_reminder_settings)
        
        # Add all sections to layout
        layout.addWidget(today_container)
        layout.addWidget(upcoming_container)
        layout.addWidget(QLabel("تنظیمات یادآوری"))
        layout.addWidget(settings_container)
    
    def load_data(self):
        """Load initial data for the calendar module"""
        # Set current month/year in calendar
        current_date = QDate.currentDate()
        self.calendar_widget.setSelectedDate(current_date)
        
        # Update month/year label
        self.update_month_year_label()
        
        # Load events
        self.load_events()
        
        # Load tasks
        self.load_tasks()
        
        # Load reminders
        self.load_reminders()
        
        # Update selected date events
        self.update_selected_date_events()
        
        # Load reminder preferences
        self.load_reminder_preferences()
    
    def update_month_year_label(self):
        """Update the month and year label"""
        selected_date = self.calendar_widget.selectedDate()
        persian_date = gregorian_to_persian(selected_date.toPyDate())
        
        # Parse Persian date to get month and year
        parts = persian_date.split("/")
        year = parts[0]
        month = int(parts[1])
        
        month_name = get_persian_month_name(month)
        
        self.month_year_label.setText(f"{month_name} {year}")
    
    def update_selected_date_events(self):
        """Update the events list for the selected date"""
        selected_date = self.calendar_widget.selectedDate()
        persian_date = gregorian_to_persian(selected_date.toPyDate())
        weekday = get_persian_weekday_name(selected_date.dayOfWeek())
        
        self.selected_date_label.setText(f"{weekday} {persian_date}")
        
        # Get events for selected date
        date_str = selected_date.toString("yyyy-MM-dd")
        events = self.calendar_service.get_events_for_date(date_str)
        
        # Clear the list
        self.events_list.clear()
        
        # Add events to the list
        for event in events:
            time_str = ""
            if not event.all_day:
                time_str = f"{event.start_time} - {event.end_time} | "
            
            item = QListWidgetItem(f"{time_str}{event.title}")
            
            # Set item data
            item.setData(Qt.ItemDataRole.UserRole, event.id)
            
            # Set color based on time
            if event.all_day:
                item.setForeground(QColor(0, 255, 170))
            else:
                item.setForeground(QColor(0, 170, 255))
            
            self.events_list.addItem(item)
        
        # Connect double-click event
        self.events_list.itemDoubleClicked.connect(self.edit_event)
    
    def load_events(self):
        """Load events to the upcoming events table"""
        events = self.calendar_service.get_upcoming_events()
        
        # Clear the table
        self.upcoming_events_table.setRowCount(0)
        
        # Populate table
        for idx, event in enumerate(events):
            self.upcoming_events_table.insertRow(idx)
            
            # Get Persian date
            persian_date = gregorian_to_persian(event.date)
            
            # Set table items
            self.upcoming_events_table.setItem(idx, 0, QTableWidgetItem(persian_date))
            
            if event.all_day:
                time_item = QTableWidgetItem("تمام روز")
            else:
                time_item = QTableWidgetItem(f"{event.start_time} - {event.end_time}")
            
            self.upcoming_events_table.setItem(idx, 1, time_item)
            self.upcoming_events_table.setItem(idx, 2, QTableWidgetItem(event.title))
            self.upcoming_events_table.setItem(idx, 3, QTableWidgetItem(event.location))
            self.upcoming_events_table.setItem(idx, 4, QTableWidgetItem(event.description))
            
            # Actions buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = NeonButton("ویرایش")
            edit_btn.clicked.connect(lambda checked, event_id=event.id: self.edit_event_by_id(event_id))
            
            delete_btn = NeonButton("حذف")
            delete_btn.setColor(QColor(255, 0, 128))
            delete_btn.clicked.connect(lambda checked, event_id=event.id: self.delete_event(event_id))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.upcoming_events_table.setCellWidget(idx, 5, actions_widget)
    
    def load_tasks(self):
        """Load tasks to the tasks tables"""
        pending_tasks = self.calendar_service.get_pending_tasks()
        completed_tasks = self.calendar_service.get_completed_tasks()
        
        # Clear tables
        self.pending_tasks_table.setRowCount(0)
        self.completed_tasks_table.setRowCount(0)
        
        # Populate pending tasks table
        for idx, task in enumerate(pending_tasks):
            self.pending_tasks_table.insertRow(idx)
            
            self.pending_tasks_table.setItem(idx, 0, QTableWidgetItem(task.title))
            
            # Get Persian date
            persian_date = gregorian_to_persian(task.due_date)
            self.pending_tasks_table.setItem(idx, 1, QTableWidgetItem(persian_date))
            
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
                
            self.pending_tasks_table.setItem(idx, 2, priority_item)
            self.pending_tasks_table.setItem(idx, 3, QTableWidgetItem(task.description))
            
            # Complete checkbox
            complete_btn = NeonButton("تکمیل شد")
            complete_btn.clicked.connect(lambda checked, task_id=task.id: self.complete_task(task_id))
            
            self.pending_tasks_table.setCellWidget(idx, 4, complete_btn)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = NeonButton("ویرایش")
            edit_btn.clicked.connect(lambda checked, task_id=task.id: self.edit_task(task_id))
            
            delete_btn = NeonButton("حذف")
            delete_btn.setColor(QColor(255, 0, 128))
            delete_btn.clicked.connect(lambda checked, task_id=task.id: self.delete_task(task_id))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.pending_tasks_table.setCellWidget(idx, 5, actions_widget)
        
        # Populate completed tasks table
        for idx, task in enumerate(completed_tasks):
            self.completed_tasks_table.insertRow(idx)
            
            self.completed_tasks_table.setItem(idx, 0, QTableWidgetItem(task.title))
            
            # Get Persian date
            persian_date = gregorian_to_persian(task.due_date)
            self.completed_tasks_table.setItem(idx, 1, QTableWidgetItem(persian_date))
            
            # Priority
            priority_map = {
                "low": "کم",
                "medium": "متوسط",
                "high": "زیاد"
            }
            self.completed_tasks_table.setItem(idx, 2, QTableWidgetItem(priority_map.get(task.priority, "متوسط")))
            self.completed_tasks_table.setItem(idx, 3, QTableWidgetItem(task.description))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            restore_btn = NeonButton("بازگرداندن")
            restore_btn.clicked.connect(lambda checked, task_id=task.id: self.restore_task(task_id))
            
            delete_btn = NeonButton("حذف")
            delete_btn.setColor(QColor(255, 0, 128))
            delete_btn.clicked.connect(lambda checked, task_id=task.id: self.delete_task(task_id))
            
            actions_layout.addWidget(restore_btn)
            actions_layout.addWidget(delete_btn)
            
            self.completed_tasks_table.setCellWidget(idx, 4, actions_widget)
    
    def load_reminders(self):
        """Load reminders to the reminders list and table"""
        today_reminders = self.calendar_service.get_today_reminders()
        upcoming_reminders = self.calendar_service.get_upcoming_reminders()
        
        # Clear the list and table
        self.today_reminders_list.clear()
        self.upcoming_reminders_table.setRowCount(0)
        
        # Populate today's reminders list
        for reminder in today_reminders:
            item_text = f"{reminder.time} | {reminder.title}"
            if reminder.source_type == "event":
                item_text = f"{item_text} (رویداد)"
            else:
                item_text = f"{item_text} (وظیفه)"
                
            item = QListWidgetItem(item_text)
            
            # Set item data
            item.setData(Qt.ItemDataRole.UserRole, reminder.id)
            
            # Set color based on source type
            if reminder.source_type == "event":
                item.setForeground(QColor(0, 170, 255))
            else:
                item.setForeground(QColor(0, 255, 170))
            
            self.today_reminders_list.addItem(item)
        
        # Populate upcoming reminders table
        for idx, reminder in enumerate(upcoming_reminders):
            self.upcoming_reminders_table.insertRow(idx)
            
            # Get Persian date
            persian_date = gregorian_to_persian(reminder.date)
            
            # Set table items
            self.upcoming_reminders_table.setItem(idx, 0, QTableWidgetItem(persian_date))
            self.upcoming_reminders_table.setItem(idx, 1, QTableWidgetItem(reminder.time))
            self.upcoming_reminders_table.setItem(idx, 2, QTableWidgetItem(reminder.title))
            
            source_type = "رویداد" if reminder.source_type == "event" else "وظیفه"
            type_item = QTableWidgetItem(source_type)
            if reminder.source_type == "event":
                type_item.setForeground(QColor(0, 170, 255))
            else:
                type_item.setForeground(QColor(0, 255, 170))
                
            self.upcoming_reminders_table.setItem(idx, 3, type_item)
            
            # Delete button
            delete_btn = NeonButton("حذف")
            delete_btn.setColor(QColor(255, 0, 128))
            delete_btn.clicked.connect(lambda checked, rem_id=reminder.id: self.delete_reminder(rem_id))
            
            self.upcoming_reminders_table.setCellWidget(idx, 4, delete_btn)
    
    def load_reminder_preferences(self):
        """Load reminder preferences"""
        prefs = self.calendar_service.get_reminder_preferences()
        
        self.enable_notifications.setChecked(prefs.get('enable_notifications', True))
        self.default_reminder_time.setValue(prefs.get('default_reminder_time', 15))
    
    @pyqtSlot()
    def go_to_today(self):
        """Go to today in calendar"""
        self.calendar_widget.setSelectedDate(QDate.currentDate())
        self.update_month_year_label()
        self.update_selected_date_events()
    
    @pyqtSlot()
    def go_to_prev_month(self):
        """Go to previous month in calendar"""
        current_date = self.calendar_widget.selectedDate()
        prev_month = current_date.addMonths(-1)
        self.calendar_widget.setSelectedDate(prev_month)
        self.update_month_year_label()
    
    @pyqtSlot()
    def go_to_next_month(self):
        """Go to next month in calendar"""
        current_date = self.calendar_widget.selectedDate()
        next_month = current_date.addMonths(1)
        self.calendar_widget.setSelectedDate(next_month)
        self.update_month_year_label()
    
    @pyqtSlot()
    def add_event(self):
        """Add a new event"""
        dialog = EventDialog(self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            event_data = dialog.get_event_data()
            
            # Validate data
            if not event_data["title"]:
                QMessageBox.warning(self, "خطا", "لطفا عنوان رویداد را وارد کنید.")
                return
            
            try:
                # Create event object
                event = Event(
                    id=None,
                    user_id=self.user.id,
                    title=event_data["title"],
                    date=event_data["date"],
                    start_time=event_data["start_time"],
                    end_time=event_data["end_time"],
                    location=event_data["location"],
                    description=event_data["description"],
                    all_day=event_data["all_day"],
                    has_reminder=event_data["has_reminder"]
                )
                
                # Add reminder data
                reminder_data = {
                    "value": event_data["reminder_value"],
                    "unit": event_data["reminder_unit"]
                }
                
                # Add event
                self.calendar_service.add_event(event, reminder_data if event_data["has_reminder"] else None)
                
                # Reload data
                self.load_events()
                self.update_selected_date_events()
                self.load_reminders()
                
                QMessageBox.information(self, "موفقیت", "رویداد با موفقیت اضافه شد.")
            except Exception as e:
                logger.error(f"Error adding event: {str(e)}")
                QMessageBox.critical(self, "خطا", f"خطا در افزودن رویداد: {str(e)}")
    
    @pyqtSlot(QListWidgetItem)
    def edit_event(self, item):
        """Edit an event from list item"""
        event_id = item.data(Qt.ItemDataRole.UserRole)
        self.edit_event_by_id(event_id)
    
    def edit_event_by_id(self, event_id):
        """Edit an event by its ID"""
        event = self.calendar_service.get_event(event_id)
        
        if not event:
            QMessageBox.warning(self, "خطا", "رویداد مورد نظر یافت نشد.")
            return
        
        dialog = EventDialog(self, event)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            event_data = dialog.get_event_data()
            
            # Validate data
            if not event_data["title"]:
                QMessageBox.warning(self, "خطا", "لطفا عنوان رویداد را وارد کنید.")
                return
            
            try:
                # Update event object
                event.title = event_data["title"]
                event.date = event_data["date"]
                event.start_time = event_data["start_time"]
                event.end_time = event_data["end_time"]
                event.location = event_data["location"]
                event.description = event_data["description"]
                event.all_day = event_data["all_day"]
                event.has_reminder = event_data["has_reminder"]
                
                # Add reminder data
                reminder_data = {
                    "value": event_data["reminder_value"],
                    "unit": event_data["reminder_unit"]
                }
                
                # Update event
                self.calendar_service.update_event(event, reminder_data if event_data["has_reminder"] else None)
                
                # Reload data
                self.load_events()
                self.update_selected_date_events()
                self.load_reminders()
                
                QMessageBox.information(self, "موفقیت", "رویداد با موفقیت به‌روزرسانی شد.")
            except Exception as e:
                logger.error(f"Error updating event: {str(e)}")
                QMessageBox.critical(self, "خطا", f"خطا در به‌روزرسانی رویداد: {str(e)}")
    
    @pyqtSlot(int)
    def delete_event(self, event_id):
        """Delete an event"""
        reply = QMessageBox.question(
            self, "تأیید حذف", 
            "آیا از حذف این رویداد اطمینان دارید؟", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.calendar_service.delete_event(event_id)
                
                # Reload data
                self.load_events()
                self.update_selected_date_events()
                self.load_reminders()
                
                QMessageBox.information(self, "موفقیت", "رویداد با موفقیت حذف شد.")
            except Exception as e:
                logger.error(f"Error deleting event: {str(e)}")
                QMessageBox.critical(self, "خطا", f"خطا در حذف رویداد: {str(e)}")
    
    @pyqtSlot()
    def quick_add_task(self):
        """Quickly add a task with minimal info"""
        title = self.task_title.text().strip()
        due_date = self.task_date.date().toString("yyyy-MM-dd")
        
        priority_map = {
            0: "low",
            1: "medium",
            2: "high"
        }
        priority = priority_map.get(self.task_priority.currentIndex(), "medium")
        
        if not title:
            QMessageBox.warning(self, "خطا", "لطفا عنوان وظیفه را وارد کنید.")
            return
        
        try:
            # Create task object
            task = Task(
                id=None,
                user_id=self.user.id,
                title=title,
                due_date=due_date,
                priority=priority,
                description="",
                completed=False,
                completion_date=None,
                has_reminder=False
            )
            
            # Add task
            self.calendar_service.add_task(task)
            
            # Clear form
            self.task_title.clear()
            
            # Reload tasks
            self.load_tasks()
            
            QMessageBox.information(self, "موفقیت", "وظیفه با موفقیت اضافه شد.")
        except Exception as e:
            logger.error(f"Error adding task: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در افزودن وظیفه: {str(e)}")
    
    @pyqtSlot()
    def add_detailed_task(self):
        """Add a new task with detailed info"""
        dialog = TaskDialog(self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            task_data = dialog.get_task_data()
            
            # Validate data
            if not task_data["title"]:
                QMessageBox.warning(self, "خطا", "لطفا عنوان وظیفه را وارد کنید.")
                return
            
            try:
                # Create task object
                task = Task(
                    id=None,
                    user_id=self.user.id,
                    title=task_data["title"],
                    due_date=task_data["due_date"],
                    priority=task_data["priority"],
                    description=task_data["description"],
                    completed=False,
                    completion_date=None,
                    has_reminder=task_data["has_reminder"]
                )
                
                # Add reminder data
                reminder_data = {
                    "value": task_data["reminder_value"],
                    "unit": task_data["reminder_unit"]
                }
                
                # Add task
                self.calendar_service.add_task(task, reminder_data if task_data["has_reminder"] else None)
                
                # Reload data
                self.load_tasks()
                self.load_reminders()
                
                QMessageBox.information(self, "موفقیت", "وظیفه با موفقیت اضافه شد.")
            except Exception as e:
                logger.error(f"Error adding task: {str(e)}")
                QMessageBox.critical(self, "خطا", f"خطا در افزودن وظیفه: {str(e)}")
    
    @pyqtSlot(int)
    def edit_task(self, task_id):
        """Edit a task"""
        task = self.calendar_service.get_task(task_id)
        
        if not task:
            QMessageBox.warning(self, "خطا", "وظیفه مورد نظر یافت نشد.")
            return
        
        dialog = TaskDialog(self, task)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            task_data = dialog.get_task_data()
            
            # Validate data
            if not task_data["title"]:
                QMessageBox.warning(self, "خطا", "لطفا عنوان وظیفه را وارد کنید.")
                return
            
            try:
                # Update task object
                task.title = task_data["title"]
                task.due_date = task_data["due_date"]
                task.priority = task_data["priority"]
                task.description = task_data["description"]
                task.has_reminder = task_data["has_reminder"]
                
                # Add reminder data
                reminder_data = {
                    "value": task_data["reminder_value"],
                    "unit": task_data["reminder_unit"]
                }
                
                # Update task
                self.calendar_service.update_task(task, reminder_data if task_data["has_reminder"] else None)
                
                # Reload data
                self.load_tasks()
                self.load_reminders()
                
                QMessageBox.information(self, "موفقیت", "وظیفه با موفقیت به‌روزرسانی شد.")
            except Exception as e:
                logger.error(f"Error updating task: {str(e)}")
                QMessageBox.critical(self, "خطا", f"خطا در به‌روزرسانی وظیفه: {str(e)}")
    
    @pyqtSlot(int)
    def complete_task(self, task_id):
        """Mark a task as completed"""
        try:
            self.calendar_service.complete_task(task_id)
            
            # Reload tasks
            self.load_tasks()
            
            QMessageBox.information(self, "موفقیت", "وظیفه با موفقیت تکمیل شد.")
        except Exception as e:
            logger.error(f"Error completing task: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در تکمیل وظیفه: {str(e)}")
    
    @pyqtSlot(int)
    def restore_task(self, task_id):
        """Restore a completed task to pending"""
        try:
            self.calendar_service.restore_task(task_id)
            
            # Reload tasks
            self.load_tasks()
            
            QMessageBox.information(self, "موفقیت", "وظیفه با موفقیت بازگردانی شد.")
        except Exception as e:
            logger.error(f"Error restoring task: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در بازگردانی وظیفه: {str(e)}")
    
    @pyqtSlot(int)
    def delete_task(self, task_id):
        """Delete a task"""
        reply = QMessageBox.question(
            self, "تأیید حذف", 
            "آیا از حذف این وظیفه اطمینان دارید؟", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.calendar_service.delete_task(task_id)
                
                # Reload data
                self.load_tasks()
                self.load_reminders()
                
                QMessageBox.information(self, "موفقیت", "وظیفه با موفقیت حذف شد.")
            except Exception as e:
                logger.error(f"Error deleting task: {str(e)}")
                QMessageBox.critical(self, "خطا", f"خطا در حذف وظیفه: {str(e)}")
    
    @pyqtSlot(int)
    def delete_reminder(self, reminder_id):
        """Delete a reminder"""
        reply = QMessageBox.question(
            self, "تأیید حذف", 
            "آیا از حذف این یادآوری اطمینان دارید؟", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.calendar_service.delete_reminder(reminder_id)
                
                # Reload reminders
                self.load_reminders()
                
                QMessageBox.information(self, "موفقیت", "یادآوری با موفقیت حذف شد.")
            except Exception as e:
                logger.error(f"Error deleting reminder: {str(e)}")
                QMessageBox.critical(self, "خطا", f"خطا در حذف یادآوری: {str(e)}")
    
    @pyqtSlot()
    def save_reminder_preferences(self):
        """Save reminder preferences"""
        prefs = {
            'enable_notifications': self.enable_notifications.isChecked(),
            'default_reminder_time': self.default_reminder_time.value()
        }
        
        try:
            self.calendar_service.save_reminder_preferences(prefs)
            QMessageBox.information(self, "موفقیت", "تنظیمات یادآوری با موفقیت ذخیره شد.")
        except Exception as e:
            logger.error(f"Error saving reminder preferences: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره تنظیمات یادآوری: {str(e)}")
