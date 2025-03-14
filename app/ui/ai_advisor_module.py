"""
AI Advisor Module UI for Persian Life Manager
"""

import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QLabel, QPushButton, QTextEdit, QComboBox, 
                           QScrollArea, QFrame, QSpinBox, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWebEngineWidgets import QWebEngineView

from app.services.ai_advisor import AIAdvisor
from app.models.user import User
from app.ui.widgets import NeonButton, GlowLabel
from app.utils.date_utils import get_current_persian_date, persian_to_gregorian

logger = logging.getLogger(__name__)

class AIAdvisorModule(QWidget):
    """AI Advisor Module for personalized AI-powered advice"""
    
    def __init__(self, user: User):
        """Initialize the AI Advisor Module
        
        Args:
            user (User): Current user object
        """
        super().__init__()
        self.user = user
        self.ai_advisor = AIAdvisor()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title_label = GlowLabel("مشاور هوش مصنوعی", glow_color="#00e6e6")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Add tabs
        self.setup_health_advice_tab()
        self.setup_finance_advice_tab()
        self.setup_time_advice_tab()
        self.setup_comprehensive_advice_tab()
        self.setup_weekly_plan_tab()
        self.setup_yearly_goals_tab()
        
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.tab_widget)
        
        self.setLayout(main_layout)
    
    def setup_health_advice_tab(self):
        """Setup the health advice tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Form for health data
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Height and weight
        height_layout = QHBoxLayout()
        height_label = QLabel("قد (سانتی‌متر):")
        self.height_input = QSpinBox()
        self.height_input.setRange(100, 250)
        self.height_input.setValue(170)
        height_layout.addWidget(self.height_input)
        height_layout.addWidget(height_label)
        
        weight_layout = QHBoxLayout()
        weight_label = QLabel("وزن (کیلوگرم):")
        self.weight_input = QSpinBox()
        self.weight_input.setRange(30, 200)
        self.weight_input.setValue(70)
        weight_layout.addWidget(self.weight_input)
        weight_layout.addWidget(weight_label)
        
        # Activity level
        activity_layout = QHBoxLayout()
        activity_label = QLabel("سطح فعالیت:")
        self.activity_input = QComboBox()
        self.activity_input.addItems([
            "کم تحرک (بدون ورزش)",
            "کمی فعال (1-3 روز در هفته)",
            "نسبتاً فعال (3-5 روز در هفته)",
            "بسیار فعال (6-7 روز در هفته)",
            "فوق العاده فعال (ورزش روزانه شدید)"
        ])
        activity_layout.addWidget(self.activity_input)
        activity_layout.addWidget(activity_label)
        
        # Health conditions
        conditions_layout = QHBoxLayout()
        conditions_label = QLabel("شرایط سلامتی:")
        self.conditions_input = QTextEdit()
        self.conditions_input.setPlaceholderText("شرایط سلامتی خود را وارد کنید (مثال: دیابت، فشار خون بالا)")
        self.conditions_input.setMaximumHeight(60)
        conditions_layout.addWidget(self.conditions_input)
        conditions_layout.addWidget(conditions_label)
        
        # Goal focus
        goal_layout = QHBoxLayout()
        goal_label = QLabel("هدف اصلی:")
        self.goal_input = QComboBox()
        self.goal_input.addItems([
            "کاهش وزن",
            "افزایش وزن",
            "حفظ وزن فعلی",
            "افزایش استقامت",
            "افزایش قدرت عضلانی",
            "بهبود سلامت قلب",
            "کاهش استرس"
        ])
        goal_layout.addWidget(self.goal_input)
        goal_layout.addWidget(goal_label)
        
        # Get advice button
        button_layout = QHBoxLayout()
        get_advice_btn = NeonButton("دریافت توصیه‌های سلامتی")
        get_advice_btn.setColor("#00e6e6")
        get_advice_btn.clicked.connect(self.get_health_advice)
        button_layout.addStretch()
        button_layout.addWidget(get_advice_btn)
        button_layout.addStretch()
        
        # Add all layouts to form
        form_layout.addLayout(height_layout)
        form_layout.addLayout(weight_layout)
        form_layout.addLayout(activity_layout)
        form_layout.addLayout(conditions_layout)
        form_layout.addLayout(goal_layout)
        form_layout.addLayout(button_layout)
        
        # Advice display area
        advice_label = QLabel("توصیه‌های سلامتی:")
        advice_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        
        self.health_advice_view = QWebEngineView()
        self.health_advice_view.setMinimumHeight(300)
        self.health_advice_view.setHtml("""
        <html dir="rtl">
        <head>
            <style>
                body {
                    font-family: 'Vazir', 'Tahoma', sans-serif;
                    background-color: #1a1a2e;
                    color: #e6e6e6;
                    padding: 15px;
                }
                h3 {
                    color: #00e6e6;
                    border-bottom: 1px solid #00e6e6;
                    padding-bottom: 5px;
                }
                ul {
                    list-style-type: square;
                }
                li {
                    margin: 10px 0;
                }
                .advice-container {
                    background-color: #16213e;
                    border-radius: 8px;
                    padding: 15px;
                    border-left: 4px solid #00e6e6;
                }
            </style>
        </head>
        <body>
            <div class="advice-container">
                <h3>توصیه‌های سلامتی</h3>
                <p>برای دریافت توصیه‌های شخصی‌سازی شده، اطلاعات خود را وارد کرده و دکمه «دریافت توصیه‌های سلامتی» را بزنید.</p>
            </div>
        </body>
        </html>
        """)
        
        # Add widgets to layout
        layout.addLayout(form_layout)
        layout.addWidget(advice_label)
        layout.addWidget(self.health_advice_view)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "توصیه‌های سلامتی")
    
    def setup_finance_advice_tab(self):
        """Setup the finance advice tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Form for finance data
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Income
        income_layout = QHBoxLayout()
        income_label = QLabel("درآمد ماهانه (تومان):")
        self.income_input = QSpinBox()
        self.income_input.setRange(0, 1000000000)
        self.income_input.setSingleStep(1000000)
        self.income_input.setValue(5000000)
        income_layout.addWidget(self.income_input)
        income_layout.addWidget(income_label)
        
        # Savings
        savings_layout = QHBoxLayout()
        savings_label = QLabel("پس‌انداز فعلی (تومان):")
        self.savings_input = QSpinBox()
        self.savings_input.setRange(0, 10000000000)
        self.savings_input.setSingleStep(1000000)
        self.savings_input.setValue(10000000)
        savings_layout.addWidget(self.savings_input)
        savings_layout.addWidget(savings_label)
        
        # Expenses categories
        expenses_layout = QHBoxLayout()
        expenses_label = QLabel("دسته‌بندی‌های هزینه اصلی:")
        self.expenses_input = QTextEdit()
        self.expenses_input.setPlaceholderText("دسته‌بندی‌های هزینه را وارد کنید (مثال: مسکن، خوراک، حمل و نقل)")
        self.expenses_input.setMaximumHeight(60)
        expenses_layout.addWidget(self.expenses_input)
        expenses_layout.addWidget(expenses_label)
        
        # Financial goals
        goals_layout = QHBoxLayout()
        goals_label = QLabel("اهداف مالی:")
        self.finance_goals_input = QTextEdit()
        self.finance_goals_input.setPlaceholderText("اهداف مالی خود را وارد کنید (مثال: خرید خانه، پس‌انداز بازنشستگی)")
        self.finance_goals_input.setMaximumHeight(60)
        goals_layout.addWidget(self.finance_goals_input)
        goals_layout.addWidget(goals_label)
        
        # Get advice button
        button_layout = QHBoxLayout()
        get_advice_btn = NeonButton("دریافت توصیه‌های مالی")
        get_advice_btn.setColor("#0ee66f")
        get_advice_btn.clicked.connect(self.get_finance_advice)
        button_layout.addStretch()
        button_layout.addWidget(get_advice_btn)
        button_layout.addStretch()
        
        # Add all layouts to form
        form_layout.addLayout(income_layout)
        form_layout.addLayout(savings_layout)
        form_layout.addLayout(expenses_layout)
        form_layout.addLayout(goals_layout)
        form_layout.addLayout(button_layout)
        
        # Advice display area
        advice_label = QLabel("توصیه‌های مالی:")
        advice_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        
        self.finance_advice_view = QWebEngineView()
        self.finance_advice_view.setMinimumHeight(300)
        self.finance_advice_view.setHtml("""
        <html dir="rtl">
        <head>
            <style>
                body {
                    font-family: 'Vazir', 'Tahoma', sans-serif;
                    background-color: #1a1a2e;
                    color: #e6e6e6;
                    padding: 15px;
                }
                h3 {
                    color: #0ee66f;
                    border-bottom: 1px solid #0ee66f;
                    padding-bottom: 5px;
                }
                ul {
                    list-style-type: square;
                }
                li {
                    margin: 10px 0;
                }
                .advice-container {
                    background-color: #16213e;
                    border-radius: 8px;
                    padding: 15px;
                    border-left: 4px solid #0ee66f;
                }
            </style>
        </head>
        <body>
            <div class="advice-container">
                <h3>توصیه‌های مالی</h3>
                <p>برای دریافت توصیه‌های مالی شخصی‌سازی شده، اطلاعات خود را وارد کرده و دکمه «دریافت توصیه‌های مالی» را بزنید.</p>
            </div>
        </body>
        </html>
        """)
        
        # Add widgets to layout
        layout.addLayout(form_layout)
        layout.addWidget(advice_label)
        layout.addWidget(self.finance_advice_view)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "توصیه‌های مالی")
    
    def setup_time_advice_tab(self):
        """Setup the time management advice tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Form for time management data
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Tasks
        tasks_layout = QHBoxLayout()
        tasks_label = QLabel("وظایف در انتظار:")
        self.tasks_input = QTextEdit()
        self.tasks_input.setPlaceholderText("وظایف مهم خود را وارد کنید (مثال: پروژه کاری، خرید هفتگی)")
        self.tasks_input.setMaximumHeight(80)
        tasks_layout.addWidget(self.tasks_input)
        tasks_layout.addWidget(tasks_label)
        
        # Events
        events_layout = QHBoxLayout()
        events_label = QLabel("رویدادهای پیش رو:")
        self.events_input = QTextEdit()
        self.events_input.setPlaceholderText("رویدادهای مهم پیش رو را وارد کنید (مثال: جلسه کاری، مهمانی خانوادگی)")
        self.events_input.setMaximumHeight(80)
        events_layout.addWidget(self.events_input)
        events_layout.addWidget(events_label)
        
        # Priorities
        priorities_layout = QHBoxLayout()
        priorities_label = QLabel("اولویت‌های اصلی:")
        self.priorities_input = QTextEdit()
        self.priorities_input.setPlaceholderText("اولویت‌های اصلی زندگی خود را وارد کنید (مثال: خانواده، کار، سلامتی)")
        self.priorities_input.setMaximumHeight(60)
        priorities_layout.addWidget(self.priorities_input)
        priorities_layout.addWidget(priorities_label)
        
        # Get advice button
        button_layout = QHBoxLayout()
        get_advice_btn = NeonButton("دریافت توصیه‌های مدیریت زمان")
        get_advice_btn.setColor("#e600e6")
        get_advice_btn.clicked.connect(self.get_time_management_advice)
        button_layout.addStretch()
        button_layout.addWidget(get_advice_btn)
        button_layout.addStretch()
        
        # Add all layouts to form
        form_layout.addLayout(tasks_layout)
        form_layout.addLayout(events_layout)
        form_layout.addLayout(priorities_layout)
        form_layout.addLayout(button_layout)
        
        # Advice display area
        advice_label = QLabel("توصیه‌های مدیریت زمان:")
        advice_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        
        self.time_advice_view = QWebEngineView()
        self.time_advice_view.setMinimumHeight(300)
        self.time_advice_view.setHtml("""
        <html dir="rtl">
        <head>
            <style>
                body {
                    font-family: 'Vazir', 'Tahoma', sans-serif;
                    background-color: #1a1a2e;
                    color: #e6e6e6;
                    padding: 15px;
                }
                h3 {
                    color: #e600e6;
                    border-bottom: 1px solid #e600e6;
                    padding-bottom: 5px;
                }
                ul {
                    list-style-type: square;
                }
                li {
                    margin: 10px 0;
                }
                .advice-container {
                    background-color: #16213e;
                    border-radius: 8px;
                    padding: 15px;
                    border-left: 4px solid #e600e6;
                }
            </style>
        </head>
        <body>
            <div class="advice-container">
                <h3>توصیه‌های مدیریت زمان</h3>
                <p>برای دریافت توصیه‌های مدیریت زمان شخصی‌سازی شده، اطلاعات خود را وارد کرده و دکمه «دریافت توصیه‌های مدیریت زمان» را بزنید.</p>
            </div>
        </body>
        </html>
        """)
        
        # Add widgets to layout
        layout.addLayout(form_layout)
        layout.addWidget(advice_label)
        layout.addWidget(self.time_advice_view)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "مدیریت زمان")
    
    def setup_comprehensive_advice_tab(self):
        """Setup the comprehensive advice tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Description
        description = QLabel("دریافت توصیه‌های جامع در تمام زمینه‌های زندگی بر اساس داده‌های شما")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet("margin: 10px 0;")
        
        # Get advice button
        get_advice_btn = NeonButton("دریافت توصیه‌های جامع")
        get_advice_btn.setColor("#e6e600")
        get_advice_btn.clicked.connect(self.get_comprehensive_advice)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(get_advice_btn)
        button_layout.addStretch()
        
        # Advice display area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.comprehensive_advice_view = QWebEngineView()
        self.comprehensive_advice_view.setMinimumHeight(400)
        self.comprehensive_advice_view.setHtml("""
        <html dir="rtl">
        <head>
            <style>
                body {
                    font-family: 'Vazir', 'Tahoma', sans-serif;
                    background-color: #1a1a2e;
                    color: #e6e6e6;
                    padding: 15px;
                }
                h2 {
                    color: #e6e600;
                    border-bottom: 1px solid #e6e600;
                    padding-bottom: 5px;
                }
                h3 {
                    color: #e6e6e6;
                    margin-top: 20px;
                }
                ul {
                    list-style-type: square;
                }
                li {
                    margin: 10px 0;
                }
                .advice-container {
                    background-color: #16213e;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 20px;
                    border-left: 4px solid #e6e600;
                }
            </style>
        </head>
        <body>
            <div class="advice-container">
                <h2>توصیه‌های جامع زندگی</h2>
                <p>برای دریافت توصیه‌های جامع شخصی‌سازی شده در تمام زمینه‌های زندگی، دکمه «دریافت توصیه‌های جامع» را بزنید.</p>
                <p>این توصیه‌ها بر اساس داده‌های شما در بخش‌های سلامتی، مالی و مدیریت زمان ارائه می‌شوند.</p>
            </div>
        </body>
        </html>
        """)
        
        scroll_area.setWidget(self.comprehensive_advice_view)
        
        # Add widgets to layout
        layout.addWidget(description)
        layout.addLayout(button_layout)
        layout.addWidget(scroll_area)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "توصیه‌های جامع")
    
    def setup_weekly_plan_tab(self):
        """Setup the weekly plan tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Description
        description = QLabel("دریافت برنامه هفتگی شخصی‌سازی شده بر اساس اهداف و برنامه‌های شما")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet("margin: 10px 0;")
        
        # Date selection
        date_layout = QHBoxLayout()
        date_label = QLabel("هفته شروع از تاریخ:")
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(date_label)
        
        # Get plan button
        get_plan_btn = NeonButton("دریافت برنامه هفتگی")
        get_plan_btn.setColor("#ff9900")
        get_plan_btn.clicked.connect(self.get_weekly_plan)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(get_plan_btn)
        button_layout.addStretch()
        
        # Plan display area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.weekly_plan_view = QWebEngineView()
        self.weekly_plan_view.setMinimumHeight(400)
        self.weekly_plan_view.setHtml("""
        <html dir="rtl">
        <head>
            <style>
                body {
                    font-family: 'Vazir', 'Tahoma', sans-serif;
                    background-color: #1a1a2e;
                    color: #e6e6e6;
                    padding: 15px;
                }
                h2 {
                    color: #ff9900;
                    border-bottom: 1px solid #ff9900;
                    padding-bottom: 5px;
                }
                h3 {
                    color: #ff9900;
                    margin-top: 20px;
                }
                .day-container {
                    background-color: #16213e;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-left: 4px solid #ff9900;
                }
                ul {
                    list-style-type: square;
                }
                li {
                    margin: 5px 0;
                }
            </style>
        </head>
        <body>
            <h2>برنامه هفتگی شخصی‌سازی شده</h2>
            <p>برای دریافت برنامه هفتگی شخصی‌سازی شده، دکمه «دریافت برنامه هفتگی» را بزنید.</p>
            <p>این برنامه بر اساس اهداف، رویدادها و وظایف شما تنظیم می‌شود.</p>
        </body>
        </html>
        """)
        
        scroll_area.setWidget(self.weekly_plan_view)
        
        # Add widgets to layout
        layout.addWidget(description)
        layout.addLayout(date_layout)
        layout.addLayout(button_layout)
        layout.addWidget(scroll_area)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "برنامه هفتگی")
    
    def setup_yearly_goals_tab(self):
        """Setup the yearly goals tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Description
        description = QLabel("دریافت پیشنهاد اهداف سالانه بر اساس داده‌های شما")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet("margin: 10px 0;")
        
        # Year selection
        year_layout = QHBoxLayout()
        year_label = QLabel("سال:")
        self.year_input = QSpinBox()
        current_year = QDate.currentDate().year()
        self.year_input.setRange(current_year, current_year + 5)
        self.year_input.setValue(current_year)
        year_layout.addWidget(self.year_input)
        year_layout.addWidget(year_label)
        
        # Get goals button
        get_goals_btn = NeonButton("دریافت پیشنهاد اهداف سالانه")
        get_goals_btn.setColor("#7e3ff2")
        get_goals_btn.clicked.connect(self.get_yearly_goals)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(get_goals_btn)
        button_layout.addStretch()
        
        # Goals display area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.yearly_goals_view = QWebEngineView()
        self.yearly_goals_view.setMinimumHeight(400)
        self.yearly_goals_view.setHtml("""
        <html dir="rtl">
        <head>
            <style>
                body {
                    font-family: 'Vazir', 'Tahoma', sans-serif;
                    background-color: #1a1a2e;
                    color: #e6e6e6;
                    padding: 15px;
                }
                h2 {
                    color: #7e3ff2;
                    border-bottom: 1px solid #7e3ff2;
                    padding-bottom: 5px;
                }
                h3 {
                    color: #7e3ff2;
                    margin-top: 20px;
                }
                .goals-section {
                    background-color: #16213e;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-left: 4px solid #7e3ff2;
                }
                ul {
                    list-style-type: square;
                }
                li {
                    margin: 5px 0;
                }
            </style>
        </head>
        <body>
            <h2>اهداف سالانه پیشنهادی</h2>
            <p>برای دریافت پیشنهاد اهداف سالانه شخصی‌سازی شده، دکمه «دریافت پیشنهاد اهداف سالانه» را بزنید.</p>
            <p>این اهداف بر اساس داده‌های موجود شما و در راستای بهبود کیفیت زندگی ارائه می‌شوند.</p>
        </body>
        </html>
        """)
        
        scroll_area.setWidget(self.yearly_goals_view)
        
        # Add widgets to layout
        layout.addWidget(description)
        layout.addLayout(year_layout)
        layout.addLayout(button_layout)
        layout.addWidget(scroll_area)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "اهداف سالانه")
    
    # Event handlers
    def get_health_advice(self):
        """Get health advice from AI advisor"""
        try:
            # Gather health data
            health_data = {
                'height': self.height_input.value(),
                'weight': self.weight_input.value(),
                'activity_level': self.activity_input.currentText(),
                'health_conditions': self.conditions_input.toPlainText(),
                'goal_focus': self.goal_input.currentText()
            }
            
            # Get advice
            advice_html = self.ai_advisor.get_health_advice(health_data)
            
            # Apply styling
            styled_html = f"""
            <html dir="rtl">
            <head>
                <style>
                    body {{
                        font-family: 'Vazir', 'Tahoma', sans-serif;
                        background-color: #1a1a2e;
                        color: #e6e6e6;
                        padding: 15px;
                    }}
                    h3 {{
                        color: #00e6e6;
                        border-bottom: 1px solid #00e6e6;
                        padding-bottom: 5px;
                    }}
                    ul {{
                        list-style-type: square;
                    }}
                    li {{
                        margin: 10px 0;
                    }}
                    .advice-container {{
                        background-color: #16213e;
                        border-radius: 8px;
                        padding: 15px;
                        border-left: 4px solid #00e6e6;
                    }}
                </style>
            </head>
            <body>
                {advice_html}
            </body>
            </html>
            """
            
            # Display advice
            self.health_advice_view.setHtml(styled_html)
        except Exception as e:
            logger.error(f"Error getting health advice: {str(e)}")
            self.health_advice_view.setHtml(f"""
            <html dir="rtl">
            <head>
                <style>
                    body {{
                        font-family: 'Vazir', 'Tahoma', sans-serif;
                        background-color: #1a1a2e;
                        color: #e6e6e6;
                        padding: 15px;
                    }}
                    .error {{
                        background-color: #331111;
                        border-radius: 8px;
                        padding: 15px;
                        border-left: 4px solid #e60000;
                    }}
                    h3 {{
                        color: #e60000;
                    }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h3>خطا در دریافت توصیه‌ها</h3>
                    <p>متأسفانه در دریافت توصیه‌های سلامتی خطایی رخ داد. لطفاً دوباره تلاش کنید.</p>
                </div>
            </body>
            </html>
            """)
    
    def get_finance_advice(self):
        """Get finance advice from AI advisor"""
        try:
            # Parse expenses
            expense_text = self.expenses_input.toPlainText()
            expense_list = [item.strip() for item in expense_text.split(',') if item.strip()]
            expenses = []
            for i, category in enumerate(expense_list):
                expenses.append({
                    'category': category,
                    'amount': 1000000  # Placeholder amount
                })
            
            # Parse goals
            goals_text = self.finance_goals_input.toPlainText()
            goals_list = [item.strip() for item in goals_text.split(',') if item.strip()]
            
            # Gather finance data
            finance_data = {
                'income': self.income_input.value(),
                'savings': self.savings_input.value(),
                'expenses': expenses,
                'goals': goals_list
            }
            
            # Get advice
            advice_html = self.ai_advisor.get_finance_advice(finance_data)
            
            # Apply styling
            styled_html = f"""
            <html dir="rtl">
            <head>
                <style>
                    body {{
                        font-family: 'Vazir', 'Tahoma', sans-serif;
                        background-color: #1a1a2e;
                        color: #e6e6e6;
                        padding: 15px;
                    }}
                    h3 {{
                        color: #0ee66f;
                        border-bottom: 1px solid #0ee66f;
                        padding-bottom: 5px;
                    }}
                    ul {{
                        list-style-type: square;
                    }}
                    li {{
                        margin: 10px 0;
                    }}
                    .advice-container {{
                        background-color: #16213e;
                        border-radius: 8px;
                        padding: 15px;
                        border-left: 4px solid #0ee66f;
                    }}
                </style>
            </head>
            <body>
                {advice_html}
            </body>
            </html>
            """
            
            # Display advice
            self.finance_advice_view.setHtml(styled_html)
        except Exception as e:
            logger.error(f"Error getting finance advice: {str(e)}")
            self.finance_advice_view.setHtml(f"""
            <html dir="rtl">
            <head>
                <style>
                    body {{
                        font-family: 'Vazir', 'Tahoma', sans-serif;
                        background-color: #1a1a2e;
                        color: #e6e6e6;
                        padding: 15px;
                    }}
                    .error {{
                        background-color: #331111;
                        border-radius: 8px;
                        padding: 15px;
                        border-left: 4px solid #e60000;
                    }}
                    h3 {{
                        color: #e60000;
                    }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h3>خطا در دریافت توصیه‌ها</h3>
                    <p>متأسفانه در دریافت توصیه‌های مالی خطایی رخ داد. لطفاً دوباره تلاش کنید.</p>
                </div>
            </body>
            </html>
            """)
    
    def get_time_management_advice(self):
        """Get time management advice from AI advisor"""
        try:
            # Parse tasks
            tasks_text = self.tasks_input.toPlainText()
            tasks_list = [item.strip() for item in tasks_text.split(',') if item.strip()]
            tasks = []
            for i, task in enumerate(tasks_list):
                priority = "medium"
                if i < len(tasks_list) // 3:
                    priority = "high"
                elif i >= 2 * len(tasks_list) // 3:
                    priority = "low"
                
                tasks.append({
                    'title': task,
                    'priority': priority
                })
            
            # Parse events
            events_text = self.events_input.toPlainText()
            events_list = [item.strip() for item in events_text.split(',') if item.strip()]
            events = []
            for i, event in enumerate(events_list):
                # Generate future dates
                from datetime import datetime, timedelta
                event_date = (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d')
                
                events.append({
                    'title': event,
                    'date': event_date
                })
            
            # Parse priorities
            priorities_text = self.priorities_input.toPlainText()
            priorities = [item.strip() for item in priorities_text.split(',') if item.strip()]
            
            # Gather calendar data
            calendar_data = {
                'tasks': tasks,
                'events': events,
                'priorities': priorities
            }
            
            # Get advice
            advice_html = self.ai_advisor.get_time_management_advice(calendar_data)
            
            # Apply styling
            styled_html = f"""
            <html dir="rtl">
            <head>
                <style>
                    body {{
                        font-family: 'Vazir', 'Tahoma', sans-serif;
                        background-color: #1a1a2e;
                        color: #e6e6e6;
                        padding: 15px;
                    }}
                    h3 {{
                        color: #e600e6;
                        border-bottom: 1px solid #e600e6;
                        padding-bottom: 5px;
                    }}
                    ul {{
                        list-style-type: square;
                    }}
                    li {{
                        margin: 10px 0;
                    }}
                    .advice-container {{
                        background-color: #16213e;
                        border-radius: 8px;
                        padding: 15px;
                        border-left: 4px solid #e600e6;
                    }}
                </style>
            </head>
            <body>
                {advice_html}
            </body>
            </html>
            """
            
            # Display advice
            self.time_advice_view.setHtml(styled_html)
        except Exception as e:
            logger.error(f"Error getting time management advice: {str(e)}")
            self.time_advice_view.setHtml(f"""
            <html dir="rtl">
            <head>
                <style>
                    body {{
                        font-family: 'Vazir', 'Tahoma', sans-serif;
                        background-color: #1a1a2e;
                        color: #e6e6e6;
                        padding: 15px;
                    }}
                    .error {{
                        background-color: #331111;
                        border-radius: 8px;
                        padding: 15px;
                        border-left: 4px solid #e60000;
                    }}
                    h3 {{
                        color: #e60000;
                    }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h3>خطا در دریافت توصیه‌ها</h3>
                    <p>متأسفانه در دریافت توصیه‌های مدیریت زمان خطایی رخ داد. لطفاً دوباره تلاش کنید.</p>
                </div>
            </body>
            </html>
            """)
    
    def get_comprehensive_advice(self):
        """Get comprehensive advice from AI advisor"""
        try:
            # Gather user data from all modules
            user_data = self._gather_user_data()
            
            # Get advice
            advice = self.ai_advisor.get_comprehensive_advice(user_data)
            
            # Apply styling
            styled_html = f"""
            <html dir="rtl">
            <head>
                <style>
                    body {{
                        font-family: 'Vazir', 'Tahoma', sans-serif;
                        background-color: #1a1a2e;
                        color: #e6e6e6;
                        padding: 15px;
                    }}
                    h2 {{
                        color: #e6e600;
                        border-bottom: 1px solid #e6e600;
                        padding-bottom: 5px;
                    }}
                    h3 {{
                        color: #e6e6e6;
                        margin-top: 20px;
                    }}
                    ul {{
                        list-style-type: square;
                    }}
                    li {{
                        margin: 10px 0;
                    }}
                    .health-section {{
                        background-color: #16213e;
                        border-radius: 8px;
                        padding: 15px;
                        margin-bottom: 20px;
                        border-left: 4px solid #00e6e6;
                    }}
                    .finance-section {{
                        background-color: #16213e;
                        border-radius: 8px;
                        padding: 15px;
                        margin-bottom: 20px;
                        border-left: 4px solid #0ee66f;
                    }}
                    .time-section {{
                        background-color: #16213e;
                        border-radius: 8px;
                        padding: 15px;
                        margin-bottom: 20px;
                        border-left: 4px solid #e600e6;
                    }}
                </style>
            </head>
            <body>
                <h2>توصیه‌های جامع زندگی</h2>
                
                <div class="health-section">
                    <h3>توصیه‌های سلامتی</h3>
                    {advice['health']}
                </div>
                
                <div class="finance-section">
                    <h3>توصیه‌های مالی</h3>
                    {advice['finance']}
                </div>
                
                <div class="time-section">
                    <h3>توصیه‌های مدیریت زمان</h3>
                    {advice['time_management']}
                </div>
            </body>
            </html>
            """
            
            # Display advice
            self.comprehensive_advice_view.setHtml(styled_html)
        except Exception as e:
            logger.error(f"Error getting comprehensive advice: {str(e)}")
            self.comprehensive_advice_view.setHtml(f"""
            <html dir="rtl">
            <head>
                <style>
                    body {{
                        font-family: 'Vazir', 'Tahoma', sans-serif;
                        background-color: #1a1a2e;
                        color: #e6e6e6;
                        padding: 15px;
                    }}
                    .error {{
                        background-color: #331111;
                        border-radius: 8px;
                        padding: 15px;
                        border-left: 4px solid #e60000;
                    }}
                    h3 {{
                        color: #e60000;
                    }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h3>خطا در دریافت توصیه‌ها</h3>
                    <p>متأسفانه در دریافت توصیه‌های جامع خطایی رخ داد. لطفاً دوباره تلاش کنید.</p>
                </div>
            </body>
            </html>
            """)
    
    def get_weekly_plan(self):
        """Get weekly plan from AI advisor"""
        try:
            # Gather user data
            user_data = self._gather_user_data()
            
            # Get weekly plan
            plan_html = self.ai_advisor.generate_weekly_plan(user_data)
            
            # Apply styling
            styled_html = f"""
            <html dir="rtl">
            <head>
                <style>
                    body {{
                        font-family: 'Vazir', 'Tahoma', sans-serif;
                        background-color: #1a1a2e;
                        color: #e6e6e6;
                        padding: 15px;
                    }}
                    h2 {{
                        color: #ff9900;
                        border-bottom: 1px solid #ff9900;
                        padding-bottom: 5px;
                    }}
                    h3 {{
                        color: #ff9900;
                        margin-top: 20px;
                    }}
                    .day-container {{
                        background-color: #16213e;
                        border-radius: 8px;
                        padding: 15px;
                        margin-bottom: 15px;
                        border-left: 4px solid #ff9900;
                    }}
                    ul {{
                        list-style-type: square;
                    }}
                    li {{
                        margin: 5px 0;
                    }}
                </style>
            </head>
            <body>
                {plan_html}
            </body>
            </html>
            """
            
            # Display plan
            self.weekly_plan_view.setHtml(styled_html)
        except Exception as e:
            logger.error(f"Error generating weekly plan: {str(e)}")
            self.weekly_plan_view.setHtml(f"""
            <html dir="rtl">
            <head>
                <style>
                    body {{
                        font-family: 'Vazir', 'Tahoma', sans-serif;
                        background-color: #1a1a2e;
                        color: #e6e6e6;
                        padding: 15px;
                    }}
                    .error {{
                        background-color: #331111;
                        border-radius: 8px;
                        padding: 15px;
                        border-left: 4px solid #e60000;
                    }}
                    h3 {{
                        color: #e60000;
                    }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h3>خطا در ایجاد برنامه هفتگی</h3>
                    <p>متأسفانه در ایجاد برنامه هفتگی خطایی رخ داد. لطفاً دوباره تلاش کنید.</p>
                </div>
            </body>
            </html>
            """)
    
    def get_yearly_goals(self):
        """Get yearly goals from AI advisor"""
        try:
            # Gather user data
            user_data = self._gather_user_data()
            
            # Get yearly goals
            goals_html = self.ai_advisor.generate_yearly_goals(user_data)
            
            # Apply styling
            styled_html = f"""
            <html dir="rtl">
            <head>
                <style>
                    body {{
                        font-family: 'Vazir', 'Tahoma', sans-serif;
                        background-color: #1a1a2e;
                        color: #e6e6e6;
                        padding: 15px;
                    }}
                    h2 {{
                        color: #7e3ff2;
                        border-bottom: 1px solid #7e3ff2;
                        padding-bottom: 5px;
                    }}
                    h3 {{
                        color: #7e3ff2;
                        margin-top: 20px;
                    }}
                    .goals-section {{
                        background-color: #16213e;
                        border-radius: 8px;
                        padding: 15px;
                        margin-bottom: 15px;
                        border-left: 4px solid #7e3ff2;
                    }}
                    ul {{
                        list-style-type: square;
                    }}
                    li {{
                        margin: 5px 0;
                    }}
                </style>
            </head>
            <body>
                {goals_html}
            </body>
            </html>
            """
            
            # Display goals
            self.yearly_goals_view.setHtml(styled_html)
        except Exception as e:
            logger.error(f"Error generating yearly goals: {str(e)}")
            self.yearly_goals_view.setHtml(f"""
            <html dir="rtl">
            <head>
                <style>
                    body {{
                        font-family: 'Vazir', 'Tahoma', sans-serif;
                        background-color: #1a1a2e;
                        color: #e6e6e6;
                        padding: 15px;
                    }}
                    .error {{
                        background-color: #331111;
                        border-radius: 8px;
                        padding: 15px;
                        border-left: 4px solid #e60000;
                    }}
                    h3 {{
                        color: #e60000;
                    }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h3>خطا در ایجاد اهداف سالانه</h3>
                    <p>متأسفانه در ایجاد اهداف سالانه پیشنهادی خطایی رخ داد. لطفاً دوباره تلاش کنید.</p>
                </div>
            </body>
            </html>
            """)
    
    def _gather_user_data(self):
        """Gather user data from all modules
        
        Returns:
            dict: Combined user data from all modules
        """
        # Health data
        health_data = {
            'height': self.height_input.value(),
            'weight': self.weight_input.value(),
            'activity_level': self.activity_input.currentText(),
            'health_conditions': self.conditions_input.toPlainText(),
            'goal_focus': self.goal_input.currentText(),
            'metrics': [],  # Would be populated from actual user data
            'exercises': []  # Would be populated from actual user data
        }
        
        # Finance data
        finance_data = {
            'income': self.income_input.value(),
            'savings': self.savings_input.value(),
            'expenses': [],  # Would be populated from actual user data
            'goals': []  # Would be populated from actual user data
        }
        
        # Calendar data
        calendar_data = {
            'tasks': [],  # Would be populated from actual user data
            'events': [],  # Would be populated from actual user data
            'priorities': []  # Would be populated from actual user data
        }
        
        # TODO: In a real implementation, we would retrieve this data from the database
        
        return {
            'health': health_data,
            'finance': finance_data,
            'calendar': calendar_data
        }