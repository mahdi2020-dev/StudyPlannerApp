#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Health Module UI for Health Tracking and Management
"""

import logging
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QDateEdit, QSpinBox, QDoubleSpinBox, QTabWidget, 
    QFormLayout, QScrollArea, QFrame, QGridLayout, QSplitter,
    QMessageBox, QHeaderView, QSlider, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSlot, QDate, QSize
from PyQt6.QtGui import QColor, QFont

from app.services.health_service import HealthService
from app.models.health import Exercise, HealthMetric, HealthGoal
from app.models.user import User
from app.ui.widgets import NeonButton, NeonLineEdit, ChartWidget, NeonCard, GlowLabel
from app.utils.date_utils import get_current_persian_date, gregorian_to_persian
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

class HealthModule(QWidget):
    """Health module for tracking exercises, metrics, and health status"""
    
    def __init__(self, user: User):
        super().__init__()
        
        self.user = user
        self.health_service = HealthService(user.id)
        self.ai_service = AIService()
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        """Initialize the UI components"""
        self.setObjectName("healthModule")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Module title
        title = QLabel("مدیریت سلامتی")
        title.setObjectName("moduleTitle")
        main_layout.addWidget(title)
        
        # Tab widget for different health sections
        self.tabs = QTabWidget()
        self.tabs.setObjectName("healthTabs")
        
        # Create tabs
        self.dashboard_tab = QWidget()
        self.exercise_tab = QWidget()
        self.metrics_tab = QWidget()
        self.goals_tab = QWidget()
        self.ai_advice_tab = QWidget()
        
        self.tabs.addTab(self.dashboard_tab, "داشبورد سلامتی")
        self.tabs.addTab(self.exercise_tab, "ثبت فعالیت")
        self.tabs.addTab(self.metrics_tab, "شاخص‌های سلامتی")
        self.tabs.addTab(self.goals_tab, "اهداف سلامتی")
        self.tabs.addTab(self.ai_advice_tab, "مشاور هوشمند")
        
        # Setup tab contents
        self.setup_dashboard_tab()
        self.setup_exercise_tab()
        self.setup_metrics_tab()
        self.setup_goals_tab()
        self.setup_ai_advice_tab()
        
        main_layout.addWidget(self.tabs)
        
    def setup_dashboard_tab(self):
        """Setup the health dashboard tab"""
        layout = QVBoxLayout(self.dashboard_tab)
        
        # Summary cards row
        cards_layout = QHBoxLayout()
        
        # Exercise count card
        self.exercise_card = NeonCard("تعداد فعالیت‌ها این هفته", "0", QColor(0, 255, 170))
        
        # Calories burned card
        self.calories_card = NeonCard("کالری مصرفی این هفته", "0 کالری", QColor(255, 0, 128))
        
        # Average metrics card
        self.metrics_card = NeonCard("میانگین فشار خون", "-- / --", QColor(0, 170, 255))
        
        cards_layout.addWidget(self.exercise_card)
        cards_layout.addWidget(self.calories_card)
        cards_layout.addWidget(self.metrics_card)
        
        layout.addLayout(cards_layout)
        
        # Goals progress section
        goals_frame = QFrame()
        goals_frame.setObjectName("goalsFrame")
        goals_layout = QVBoxLayout(goals_frame)
        
        goals_title = QLabel("پیشرفت اهداف")
        goals_title.setObjectName("sectionTitle")
        goals_layout.addWidget(goals_title)
        
        self.goals_grid = QGridLayout()
        goals_layout.addLayout(self.goals_grid)
        
        layout.addWidget(goals_frame)
        
        # Charts section
        charts_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Exercise trend chart
        self.exercise_chart = ChartWidget("روند فعالیت‌های ورزشی")
        
        # Weight trend chart
        self.weight_chart = ChartWidget("روند وزن")
        
        charts_splitter.addWidget(self.exercise_chart)
        charts_splitter.addWidget(self.weight_chart)
        
        layout.addWidget(charts_splitter)
        
        # Recent activities
        activities_container = QWidget()
        activities_layout = QVBoxLayout(activities_container)
        
        recent_exercise_label = QLabel("فعالیت‌های اخیر")
        recent_exercise_label.setObjectName("sectionTitle")
        
        self.recent_exercises_table = QTableWidget()
        self.recent_exercises_table.setColumnCount(5)
        self.recent_exercises_table.setHorizontalHeaderLabels(["تاریخ", "نوع فعالیت", "مدت (دقیقه)", "کالری مصرفی", "توضیحات"])
        self.recent_exercises_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        activities_layout.addWidget(recent_exercise_label)
        activities_layout.addWidget(self.recent_exercises_table)
        
        layout.addWidget(activities_container)
        
    def setup_exercise_tab(self):
        """Setup the exercise tracking tab"""
        layout = QVBoxLayout(self.exercise_tab)
        
        # Exercise form
        form_card = QFrame()
        form_card.setObjectName("formCard")
        form_layout = QFormLayout(form_card)
        form_layout.setSpacing(15)
        
        # Exercise date
        self.exercise_date = QDateEdit()
        self.exercise_date.setCalendarPopup(True)
        self.exercise_date.setDate(QDate.currentDate())
        
        # Exercise type
        self.exercise_type = QComboBox()
        exercise_types = ["پیاده‌روی", "دویدن", "دوچرخه‌سواری", "شنا", "یوگا", "بدنسازی", "فوتبال", "بسکتبال", "والیبال", "سایر"]
        for ex_type in exercise_types:
            self.exercise_type.addItem(ex_type)
        
        # Duration
        self.exercise_duration = QSpinBox()
        self.exercise_duration.setRange(1, 300)
        self.exercise_duration.setSuffix(" دقیقه")
        self.exercise_duration.setValue(30)
        
        # Calories burned
        self.exercise_calories = QSpinBox()
        self.exercise_calories.setRange(0, 2000)
        self.exercise_calories.setSuffix(" کالری")
        self.exercise_calories.setValue(100)
        
        # Auto-calculate calories checkbox
        self.calculate_btn = NeonButton("محاسبه کالری")
        self.calculate_btn.clicked.connect(self.calculate_calories)
        
        # Notes
        self.exercise_notes = NeonLineEdit()
        
        # Add form fields
        form_layout.addRow("تاریخ:", self.exercise_date)
        form_layout.addRow("نوع فعالیت:", self.exercise_type)
        form_layout.addRow("مدت زمان:", self.exercise_duration)
        
        calories_layout = QHBoxLayout()
        calories_layout.addWidget(self.exercise_calories)
        calories_layout.addWidget(self.calculate_btn)
        form_layout.addRow("کالری مصرفی:", calories_layout)
        
        form_layout.addRow("یادداشت:", self.exercise_notes)
        
        # Add exercise button
        self.add_exercise_btn = NeonButton("ثبت فعالیت")
        self.add_exercise_btn.clicked.connect(self.add_exercise)
        
        layout.addWidget(QLabel("ثبت فعالیت ورزشی جدید"))
        layout.addWidget(form_card)
        layout.addWidget(self.add_exercise_btn)
        
        # Exercises list
        exercises_label = QLabel("سابقه فعالیت‌های ورزشی")
        exercises_label.setObjectName("sectionTitle")
        
        self.exercises_table = QTableWidget()
        self.exercises_table.setColumnCount(6)
        self.exercises_table.setHorizontalHeaderLabels(
            ["تاریخ", "نوع فعالیت", "مدت (دقیقه)", "کالری مصرفی", "یادداشت", "عملیات"]
        )
        self.exercises_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(exercises_label)
        layout.addWidget(self.exercises_table)
        
    def setup_metrics_tab(self):
        """Setup the health metrics tab"""
        layout = QVBoxLayout(self.metrics_tab)
        
        # Metrics form
        form_card = QFrame()
        form_card.setObjectName("formCard")
        form_layout = QFormLayout(form_card)
        form_layout.setSpacing(15)
        
        # Metrics date
        self.metrics_date = QDateEdit()
        self.metrics_date.setCalendarPopup(True)
        self.metrics_date.setDate(QDate.currentDate())
        
        # Weight
        self.weight_value = QDoubleSpinBox()
        self.weight_value.setRange(30, 200)
        self.weight_value.setSuffix(" کیلوگرم")
        self.weight_value.setValue(70)
        self.weight_value.setDecimals(1)
        
        # Blood pressure
        blood_pressure_layout = QHBoxLayout()
        
        self.systolic_pressure = QSpinBox()
        self.systolic_pressure.setRange(70, 200)
        self.systolic_pressure.setValue(120)
        
        self.diastolic_pressure = QSpinBox()
        self.diastolic_pressure.setRange(40, 120)
        self.diastolic_pressure.setValue(80)
        
        blood_pressure_layout.addWidget(self.systolic_pressure)
        blood_pressure_layout.addWidget(QLabel("/"))
        blood_pressure_layout.addWidget(self.diastolic_pressure)
        
        # Heart rate
        self.heart_rate = QSpinBox()
        self.heart_rate.setRange(30, 220)
        self.heart_rate.setSuffix(" ضربان در دقیقه")
        self.heart_rate.setValue(75)
        
        # Sleep hours
        self.sleep_hours = QDoubleSpinBox()
        self.sleep_hours.setRange(0, 24)
        self.sleep_hours.setSuffix(" ساعت")
        self.sleep_hours.setValue(7.5)
        self.sleep_hours.setDecimals(1)
        
        # Notes
        self.metrics_notes = NeonLineEdit()
        
        # Add form fields
        form_layout.addRow("تاریخ:", self.metrics_date)
        form_layout.addRow("وزن:", self.weight_value)
        form_layout.addRow("فشار خون:", blood_pressure_layout)
        form_layout.addRow("ضربان قلب:", self.heart_rate)
        form_layout.addRow("مدت خواب:", self.sleep_hours)
        form_layout.addRow("یادداشت:", self.metrics_notes)
        
        # Add metrics button
        self.add_metrics_btn = NeonButton("ثبت شاخص‌ها")
        self.add_metrics_btn.clicked.connect(self.add_metrics)
        
        layout.addWidget(QLabel("ثبت شاخص‌های سلامتی جدید"))
        layout.addWidget(form_card)
        layout.addWidget(self.add_metrics_btn)
        
        # Metrics history
        metrics_label = QLabel("تاریخچه شاخص‌های سلامتی")
        metrics_label.setObjectName("sectionTitle")
        
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(7)
        self.metrics_table.setHorizontalHeaderLabels(
            ["تاریخ", "وزن (کیلوگرم)", "فشار خون", "ضربان قلب", "مدت خواب (ساعت)", "یادداشت", "عملیات"]
        )
        self.metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(metrics_label)
        layout.addWidget(self.metrics_table)
        
    def setup_goals_tab(self):
        """Setup the health goals tab"""
        layout = QVBoxLayout(self.goals_tab)
        
        # Goals form
        form_card = QFrame()
        form_card.setObjectName("formCard")
        form_layout = QFormLayout(form_card)
        form_layout.setSpacing(15)
        
        # Goal type
        self.goal_type = QComboBox()
        goal_types = [
            "وزن", "ورزش هفتگی", "کالری مصرفی هفتگی", 
            "مدت خواب روزانه", "تعداد قدم روزانه"
        ]
        for g_type in goal_types:
            self.goal_type.addItem(g_type)
        
        self.goal_type.currentIndexChanged.connect(self.update_goal_input)
        
        # Goal target (value will change based on selected type)
        self.goal_target_layout = QHBoxLayout()
        self.goal_target = QDoubleSpinBox()
        self.goal_target.setRange(0, 1000)
        self.goal_target.setSuffix(" کیلوگرم")
        self.goal_target.setValue(65)
        self.goal_target.setDecimals(1)
        
        self.goal_target_layout.addWidget(self.goal_target)
        
        # Goal deadline
        self.goal_deadline = QDateEdit()
        self.goal_deadline.setCalendarPopup(True)
        self.goal_deadline.setDate(QDate.currentDate().addMonths(3))
        
        # Notes
        self.goal_notes = NeonLineEdit()
        
        # Add form fields
        form_layout.addRow("نوع هدف:", self.goal_type)
        form_layout.addRow("مقدار هدف:", self.goal_target_layout)
        form_layout.addRow("تاریخ مهلت:", self.goal_deadline)
        form_layout.addRow("یادداشت:", self.goal_notes)
        
        # Add goal button
        self.add_goal_btn = NeonButton("ثبت هدف")
        self.add_goal_btn.clicked.connect(self.add_goal)
        
        layout.addWidget(QLabel("تعریف هدف سلامتی جدید"))
        layout.addWidget(form_card)
        layout.addWidget(self.add_goal_btn)
        
        # Goals list
        goals_label = QLabel("اهداف سلامتی فعال")
        goals_label.setObjectName("sectionTitle")
        
        self.goals_table = QTableWidget()
        self.goals_table.setColumnCount(6)
        self.goals_table.setHorizontalHeaderLabels(
            ["نوع هدف", "مقدار هدف", "تاریخ مهلت", "پیشرفت", "یادداشت", "عملیات"]
        )
        self.goals_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(goals_label)
        layout.addWidget(self.goals_table)
    
    def setup_ai_advice_tab(self):
        """Setup the AI advice tab"""
        layout = QVBoxLayout(self.ai_advice_tab)
        
        # AI Advice header
        ai_title = GlowLabel("مشاور هوشمند سلامتی")
        ai_title.setObjectName("aiTitle")
        ai_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        ai_subtitle = QLabel("با استفاده از هوش مصنوعی، پیشنهادات شخصی‌سازی شده برای بهبود سلامتی دریافت کنید")
        ai_subtitle.setObjectName("aiSubtitle")
        ai_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(ai_title)
        layout.addWidget(ai_subtitle)
        
        # Profile section
        profile_card = QFrame()
        profile_card.setObjectName("profileCard")
        profile_layout = QFormLayout(profile_card)
        
        # Height
        self.user_height = QDoubleSpinBox()
        self.user_height.setRange(100, 220)
        self.user_height.setSuffix(" سانتی‌متر")
        self.user_height.setValue(170)
        self.user_height.setDecimals(0)
        
        # Current weight (pre-filled from metrics if available)
        self.user_weight = QDoubleSpinBox()
        self.user_weight.setRange(30, 200)
        self.user_weight.setSuffix(" کیلوگرم")
        self.user_weight.setValue(70)
        self.user_weight.setDecimals(1)
        
        # Activity level
        self.activity_level = QComboBox()
        activity_levels = [
            "کم تحرک (بدون ورزش)",
            "کمی فعال (1-3 روز در هفته)",
            "نسبتاً فعال (3-5 روز در هفته)",
            "بسیار فعال (6-7 روز در هفته)",
            "فوق العاده فعال (ورزش روزانه شدید)"
        ]
        for level in activity_levels:
            self.activity_level.addItem(level)
        
        # Health conditions
        self.health_conditions = NeonLineEdit()
        self.health_conditions.setPlaceholderText("مثلا: دیابت، فشار خون بالا، کلسترول و...")
        
        # Goal focus
        self.goal_focus = QComboBox()
        goal_focuses = [
            "کاهش وزن",
            "افزایش وزن",
            "حفظ وزن فعلی",
            "افزایش استقامت",
            "افزایش قدرت عضلانی",
            "بهبود سلامت قلب",
            "کاهش استرس"
        ]
        for focus in goal_focuses:
            self.goal_focus.addItem(focus)
        
        profile_layout.addRow("قد:", self.user_height)
        profile_layout.addRow("وزن فعلی:", self.user_weight)
        profile_layout.addRow("سطح فعالیت:", self.activity_level)
        profile_layout.addRow("شرایط سلامتی خاص:", self.health_conditions)
        profile_layout.addRow("هدف:", self.goal_focus)
        
        # Get advice button
        self.get_advice_btn = NeonButton("دریافت توصیه")
        self.get_advice_btn.clicked.connect(self.get_ai_advice)
        
        advice_container = QFrame()
        advice_container.setObjectName("adviceContainer")
        advice_layout = QVBoxLayout(advice_container)
        
        advice_label = QLabel("توصیه‌های هوشمند")
        advice_label.setObjectName("sectionTitle")
        
        self.advice_text = QLabel("لطفاً روی دکمه «دریافت توصیه» کلیک کنید تا توصیه‌های شخصی‌سازی شده دریافت کنید.")
        self.advice_text.setWordWrap(True)
        self.advice_text.setObjectName("adviceText")
        self.advice_text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        advice_layout.addWidget(advice_label)
        advice_layout.addWidget(self.advice_text)
        
        layout.addWidget(profile_card)
        layout.addWidget(self.get_advice_btn)
        layout.addWidget(advice_container)
    
    def load_data(self):
        """Load initial data for the module"""
        # Load exercises
        self.load_exercises()
        
        # Load metrics
        self.load_metrics()
        
        # Load goals
        self.load_goals()
        
        # Update dashboard
        self.update_dashboard()
        
        # Pre-fill user metrics in AI tab if available
        self.pre_fill_user_metrics()
    
    def load_exercises(self):
        """Load exercises to tables"""
        exercises = self.health_service.get_exercises()
        
        # Clear tables
        self.exercises_table.setRowCount(0)
        self.recent_exercises_table.setRowCount(0)
        
        # Populate exercises table
        for idx, exercise in enumerate(exercises):
            self.exercises_table.insertRow(idx)
            
            # Get Persian date
            persian_date = gregorian_to_persian(exercise.date)
            
            # Set table items
            self.exercises_table.setItem(idx, 0, QTableWidgetItem(persian_date))
            self.exercises_table.setItem(idx, 1, QTableWidgetItem(exercise.exercise_type))
            
            duration_item = QTableWidgetItem(str(exercise.duration))
            duration_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.exercises_table.setItem(idx, 2, duration_item)
            
            calories_item = QTableWidgetItem(str(exercise.calories_burned))
            calories_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.exercises_table.setItem(idx, 3, calories_item)
            
            self.exercises_table.setItem(idx, 4, QTableWidgetItem(exercise.notes))
            
            # Delete button
            delete_btn = NeonButton("حذف")
            delete_btn.setColor(QColor(255, 0, 128))
            delete_btn.clicked.connect(lambda checked, ex_id=exercise.id: self.delete_exercise(ex_id))
            
            self.exercises_table.setCellWidget(idx, 5, delete_btn)
        
        # Populate recent exercises table (show only last 5)
        recent_count = min(5, len(exercises))
        for idx in range(recent_count):
            exercise = exercises[idx]
            self.recent_exercises_table.insertRow(idx)
            
            persian_date = gregorian_to_persian(exercise.date)
            
            self.recent_exercises_table.setItem(idx, 0, QTableWidgetItem(persian_date))
            self.recent_exercises_table.setItem(idx, 1, QTableWidgetItem(exercise.exercise_type))
            
            duration_item = QTableWidgetItem(str(exercise.duration))
            duration_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.recent_exercises_table.setItem(idx, 2, duration_item)
            
            calories_item = QTableWidgetItem(str(exercise.calories_burned))
            calories_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.recent_exercises_table.setItem(idx, 3, calories_item)
            
            self.recent_exercises_table.setItem(idx, 4, QTableWidgetItem(exercise.notes))
    
    def load_metrics(self):
        """Load health metrics to table"""
        metrics = self.health_service.get_metrics()
        
        # Clear table
        self.metrics_table.setRowCount(0)
        
        # Populate metrics table
        for idx, metric in enumerate(metrics):
            self.metrics_table.insertRow(idx)
            
            # Get Persian date
            persian_date = gregorian_to_persian(metric.date)
            
            # Set table items
            self.metrics_table.setItem(idx, 0, QTableWidgetItem(persian_date))
            
            weight_item = QTableWidgetItem(f"{metric.weight:.1f}")
            weight_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.metrics_table.setItem(idx, 1, weight_item)
            
            bp_item = QTableWidgetItem(f"{metric.systolic}/{metric.diastolic}")
            bp_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.metrics_table.setItem(idx, 2, bp_item)
            
            hr_item = QTableWidgetItem(str(metric.heart_rate))
            hr_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.metrics_table.setItem(idx, 3, hr_item)
            
            sleep_item = QTableWidgetItem(f"{metric.sleep_hours:.1f}")
            sleep_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.metrics_table.setItem(idx, 4, sleep_item)
            
            self.metrics_table.setItem(idx, 5, QTableWidgetItem(metric.notes))
            
            # Delete button
            delete_btn = NeonButton("حذف")
            delete_btn.setColor(QColor(255, 0, 128))
            delete_btn.clicked.connect(lambda checked, metric_id=metric.id: self.delete_metric(metric_id))
            
            self.metrics_table.setCellWidget(idx, 6, delete_btn)
    
    def load_goals(self):
        """Load health goals to table"""
        goals = self.health_service.get_goals()
        
        # Clear table
        self.goals_table.setRowCount(0)
        
        # Clear dashboard goals
        for i in reversed(range(self.goals_grid.count())): 
            self.goals_grid.itemAt(i).widget().setParent(None)
        
        # Populate goals table
        for idx, goal in enumerate(goals):
            self.goals_table.insertRow(idx)
            
            # Set table items
            self.goals_table.setItem(idx, 0, QTableWidgetItem(goal.goal_type))
            
            target_text = f"{goal.target_value}"
            if goal.goal_type == "وزن":
                target_text += " کیلوگرم"
            elif goal.goal_type == "ورزش هفتگی":
                target_text += " جلسه"
            elif goal.goal_type == "کالری مصرفی هفتگی":
                target_text += " کالری"
            elif goal.goal_type == "مدت خواب روزانه":
                target_text += " ساعت"
            elif goal.goal_type == "تعداد قدم روزانه":
                target_text += " قدم"
                
            target_item = QTableWidgetItem(target_text)
            target_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.goals_table.setItem(idx, 1, target_item)
            
            deadline = gregorian_to_persian(goal.deadline)
            self.goals_table.setItem(idx, 2, QTableWidgetItem(deadline))
            
            # Progress bar
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(int(goal.progress))
            progress_bar.setFormat(f"{goal.progress:.1f}%")
            progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            progress_bar.setObjectName("neonProgressBar")
            
            self.goals_table.setCellWidget(idx, 3, progress_bar)
            
            self.goals_table.setItem(idx, 4, QTableWidgetItem(goal.notes))
            
            # Delete button
            delete_btn = NeonButton("حذف")
            delete_btn.setColor(QColor(255, 0, 128))
            delete_btn.clicked.connect(lambda checked, goal_id=goal.id: self.delete_goal(goal_id))
            
            self.goals_table.setCellWidget(idx, 5, delete_btn)
            
            # Add goal to dashboard (only show up to 4 goals)
            if idx < 4:
                self.add_goal_to_dashboard(goal, idx)
    
    def add_goal_to_dashboard(self, goal, idx):
        """Add a goal to the dashboard goals grid"""
        row = idx // 2
        col = idx % 2
        
        goal_widget = QFrame()
        goal_widget.setObjectName("goalWidget")
        goal_layout = QVBoxLayout(goal_widget)
        
        goal_title = QLabel(goal.goal_type)
        goal_title.setObjectName("goalTitle")
        
        target_text = f"هدف: {goal.target_value}"
        if goal.goal_type == "وزن":
            target_text += " کیلوگرم"
        elif goal.goal_type == "ورزش هفتگی":
            target_text += " جلسه"
        elif goal.goal_type == "کالری مصرفی هفتگی":
            target_text += " کالری"
        elif goal.goal_type == "مدت خواب روزانه":
            target_text += " ساعت"
        elif goal.goal_type == "تعداد قدم روزانه":
            target_text += " قدم"
        
        goal_target = QLabel(target_text)
        
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(int(goal.progress))
        progress_bar.setFormat(f"{goal.progress:.1f}%")
        progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_bar.setObjectName("neonProgressBar")
        
        deadline = gregorian_to_persian(goal.deadline)
        goal_deadline = QLabel(f"مهلت: {deadline}")
        
        goal_layout.addWidget(goal_title)
        goal_layout.addWidget(goal_target)
        goal_layout.addWidget(progress_bar)
        goal_layout.addWidget(goal_deadline)
        
        self.goals_grid.addWidget(goal_widget, row, col)
    
    def update_dashboard(self):
        """Update dashboard with current health data"""
        # Get weekly summary
        weekly_summary = self.health_service.get_weekly_summary()
        
        # Update summary cards
        self.exercise_card.setValue(str(weekly_summary['exercise_count']))
        self.calories_card.setValue(f"{weekly_summary['calories_burned']} کالری")
        
        # Get latest blood pressure
        latest_bp = self.health_service.get_latest_blood_pressure()
        if latest_bp:
            self.metrics_card.setValue(f"{latest_bp['systolic']} / {latest_bp['diastolic']}")
        
        # Update exercise trend chart
        exercise_data = self.health_service.get_exercise_trend()
        
        dates = [gregorian_to_persian(d['date']) for d in exercise_data]
        durations = [d['duration'] for d in exercise_data]
        
        self.exercise_chart.update_line_chart(
            dates, 
            durations,
            "دقیقه ورزش",
            "rgba(0, 255, 170, 0.7)"
        )
        
        # Update weight trend chart
        weight_data = self.health_service.get_weight_trend()
        
        weight_dates = [gregorian_to_persian(d['date']) for d in weight_data]
        weights = [d['weight'] for d in weight_data]
        
        self.weight_chart.update_line_chart(
            weight_dates, 
            weights,
            "وزن (کیلوگرم)",
            "rgba(255, 0, 128, 0.7)"
        )
    
    def update_goal_input(self, index):
        """Update goal input based on selected goal type"""
        goal_type = self.goal_type.currentText()
        
        # Remove current widget from layout
        for i in reversed(range(self.goal_target_layout.count())): 
            self.goal_target_layout.itemAt(i).widget().setParent(None)
        
        # Create appropriate input based on goal type
        if goal_type == "وزن":
            self.goal_target = QDoubleSpinBox()
            self.goal_target.setRange(30, 200)
            self.goal_target.setSuffix(" کیلوگرم")
            self.goal_target.setValue(65)
            self.goal_target.setDecimals(1)
        elif goal_type == "ورزش هفتگی":
            self.goal_target = QSpinBox()
            self.goal_target.setRange(1, 21)
            self.goal_target.setSuffix(" جلسه")
            self.goal_target.setValue(3)
        elif goal_type == "کالری مصرفی هفتگی":
            self.goal_target = QSpinBox()
            self.goal_target.setRange(100, 10000)
            self.goal_target.setSuffix(" کالری")
            self.goal_target.setValue(1000)
        elif goal_type == "مدت خواب روزانه":
            self.goal_target = QDoubleSpinBox()
            self.goal_target.setRange(4, 12)
            self.goal_target.setSuffix(" ساعت")
            self.goal_target.setValue(8)
            self.goal_target.setDecimals(1)
        elif goal_type == "تعداد قدم روزانه":
            self.goal_target = QSpinBox()
            self.goal_target.setRange(1000, 30000)
            self.goal_target.setSuffix(" قدم")
            self.goal_target.setValue(10000)
        
        self.goal_target_layout.addWidget(self.goal_target)
    
    def pre_fill_user_metrics(self):
        """Pre-fill user metrics in AI tab based on latest data"""
        # Get the latest metrics
        latest_metrics = self.health_service.get_latest_metrics()
        
        if latest_metrics:
            self.user_weight.setValue(latest_metrics.weight)
    
    @pyqtSlot()
    def add_exercise(self):
        """Add a new exercise"""
        exercise_type = self.exercise_type.currentText()
        duration = self.exercise_duration.value()
        calories = self.exercise_calories.value()
        
        if duration <= 0:
            QMessageBox.warning(self, "خطا", "مدت زمان فعالیت باید بیشتر از صفر باشد.")
            return
        
        # Create exercise object
        exercise = Exercise(
            id=None,
            user_id=self.user.id,
            date=self.exercise_date.date().toPyDate(),
            exercise_type=exercise_type,
            duration=duration,
            calories_burned=calories,
            notes=self.exercise_notes.text()
        )
        
        # Add exercise
        try:
            self.health_service.add_exercise(exercise)
            
            # Clear form
            self.exercise_notes.clear()
            
            # Reload data
            self.load_exercises()
            self.update_dashboard()
            
            QMessageBox.information(self, "موفقیت", "فعالیت ورزشی با موفقیت ثبت شد.")
        except Exception as e:
            logger.error(f"Error adding exercise: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در ثبت فعالیت: {str(e)}")
    
    @pyqtSlot()
    def add_metrics(self):
        """Add new health metrics"""
        weight = self.weight_value.value()
        systolic = self.systolic_pressure.value()
        diastolic = self.diastolic_pressure.value()
        heart_rate = self.heart_rate.value()
        sleep_hours = self.sleep_hours.value()
        
        # Validate blood pressure
        if systolic <= diastolic:
            QMessageBox.warning(self, "خطا", "فشار خون سیستولیک (عدد اول) باید بزرگتر از فشار دیاستولیک باشد.")
            return
        
        # Create metrics object
        metrics = HealthMetric(
            id=None,
            user_id=self.user.id,
            date=self.metrics_date.date().toPyDate(),
            weight=weight,
            systolic=systolic,
            diastolic=diastolic,
            heart_rate=heart_rate,
            sleep_hours=sleep_hours,
            notes=self.metrics_notes.text()
        )
        
        # Add metrics
        try:
            self.health_service.add_metrics(metrics)
            
            # Clear form
            self.metrics_notes.clear()
            
            # Reload data
            self.load_metrics()
            self.update_dashboard()
            
            # Update user weight in AI tab
            self.user_weight.setValue(weight)
            
            QMessageBox.information(self, "موفقیت", "شاخص‌های سلامتی با موفقیت ثبت شدند.")
        except Exception as e:
            logger.error(f"Error adding metrics: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در ثبت شاخص‌ها: {str(e)}")
    
    @pyqtSlot()
    def add_goal(self):
        """Add a new health goal"""
        goal_type = self.goal_type.currentText()
        target_value = self.goal_target.value()
        deadline = self.goal_deadline.date().toPyDate()
        notes = self.goal_notes.text()
        
        # Validate deadline
        today = datetime.now().date()
        if deadline <= today:
            QMessageBox.warning(self, "خطا", "مهلت هدف باید تاریخی در آینده باشد.")
            return
        
        # Create goal object
        goal = HealthGoal(
            id=None,
            user_id=self.user.id,
            goal_type=goal_type,
            target_value=target_value,
            deadline=deadline,
            progress=0,
            notes=notes
        )
        
        # Add goal
        try:
            self.health_service.add_goal(goal)
            
            # Clear form
            self.goal_notes.clear()
            
            # Reload data
            self.load_goals()
            
            QMessageBox.information(self, "موفقیت", "هدف سلامتی با موفقیت اضافه شد.")
        except Exception as e:
            logger.error(f"Error adding goal: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در افزودن هدف: {str(e)}")
    
    @pyqtSlot()
    def calculate_calories(self):
        """Calculate estimated calories burned based on exercise type and duration"""
        exercise_type = self.exercise_type.currentText()
        duration = self.exercise_duration.value()
        
        # MET values for different exercises (metabolic equivalents)
        met_values = {
            "پیاده‌روی": 3.5,
            "دویدن": 9.8,
            "دوچرخه‌سواری": 7.5,
            "شنا": 8.0,
            "یوگا": 3.0,
            "بدنسازی": 5.0,
            "فوتبال": 7.0,
            "بسکتبال": 6.5,
            "والیبال": 4.0,
            "سایر": 4.5
        }
        
        # Get latest weight or use default
        weight = 70  # Default weight in kg
        latest_metrics = self.health_service.get_latest_metrics()
        if latest_metrics:
            weight = latest_metrics.weight
        
        # Calculate calories: calories = MET * weight in kg * duration in hours
        met = met_values.get(exercise_type, 4.5)
        duration_hours = duration / 60.0  # Convert minutes to hours
        estimated_calories = int(met * weight * duration_hours)
        
        # Update calories field
        self.exercise_calories.setValue(estimated_calories)
    
    @pyqtSlot()
    def get_ai_advice(self):
        """Get AI-powered health advice based on user profile"""
        height = self.user_height.value()
        weight = self.user_weight.value()
        activity_level = self.activity_level.currentText()
        health_conditions = self.health_conditions.text()
        goal_focus = self.goal_focus.currentText()
        
        # Get user health data
        metrics = self.health_service.get_metrics()
        exercises = self.health_service.get_exercises()
        
        try:
            # Generate advice
            advice = self.ai_service.get_health_advice(
                height=height,
                weight=weight,
                activity_level=activity_level,
                health_conditions=health_conditions,
                goal_focus=goal_focus,
                metrics=metrics,
                exercises=exercises
            )
            
            # Update advice text
            self.advice_text.setText(advice)
            
        except Exception as e:
            logger.error(f"Error getting AI advice: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در دریافت توصیه‌های هوشمند: {str(e)}")
    
    @pyqtSlot(int)
    def delete_exercise(self, exercise_id):
        """Delete an exercise"""
        reply = QMessageBox.question(
            self, "تأیید حذف", 
            "آیا از حذف این فعالیت اطمینان دارید؟", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.health_service.delete_exercise(exercise_id)
                
                # Reload data
                self.load_exercises()
                self.update_dashboard()
                
                # Update goals (exercise might affect goals)
                self.health_service.update_goal_progress()
                self.load_goals()
                
                QMessageBox.information(self, "موفقیت", "فعالیت با موفقیت حذف شد.")
            except Exception as e:
                logger.error(f"Error deleting exercise: {str(e)}")
                QMessageBox.critical(self, "خطا", f"خطا در حذف فعالیت: {str(e)}")
    
    @pyqtSlot(int)
    def delete_metric(self, metric_id):
        """Delete a health metric"""
        reply = QMessageBox.question(
            self, "تأیید حذف", 
            "آیا از حذف این شاخص سلامتی اطمینان دارید؟", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.health_service.delete_metric(metric_id)
                
                # Reload data
                self.load_metrics()
                self.update_dashboard()
                
                # Update goals (metrics might affect goals)
                self.health_service.update_goal_progress()
                self.load_goals()
                
                QMessageBox.information(self, "موفقیت", "شاخص سلامتی با موفقیت حذف شد.")
            except Exception as e:
                logger.error(f"Error deleting metric: {str(e)}")
                QMessageBox.critical(self, "خطا", f"خطا در حذف شاخص سلامتی: {str(e)}")
    
    @pyqtSlot(int)
    def delete_goal(self, goal_id):
        """Delete a health goal"""
        reply = QMessageBox.question(
            self, "تأیید حذف", 
            "آیا از حذف این هدف اطمینان دارید؟", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.health_service.delete_goal(goal_id)
                
                # Reload goals
                self.load_goals()
                
                QMessageBox.information(self, "موفقیت", "هدف با موفقیت حذف شد.")
            except Exception as e:
                logger.error(f"Error deleting goal: {str(e)}")
                QMessageBox.critical(self, "خطا", f"خطا در حذف هدف: {str(e)}")
