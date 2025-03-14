#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Custom widgets for Persian Life Manager application
"""

import sys
import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy, QGridLayout, QScrollArea, QCalendarWidget
)
from PyQt6.QtCore import (
    Qt, QSize, QPoint, QRect, QDate, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QTimer, QObject
)
# Custom Property implementation since PyQt6 doesn't expose Property directly
# PyQt6 doesn't expose Property directly, use Python's property instead
# Use PyQt6's native pyqtProperty for proper property animation support
from PyQt6.QtCore import pyqtProperty as Property
from PyQt6.QtGui import (
    QColor, QPainter, QFont, QFontMetrics, QGradient,
    QLinearGradient, QPen, QBrush, QPainterPath, QRadialGradient, QIcon
)
# Removed WebEngine dependencies

import jdatetime

logger = logging.getLogger(__name__)


class NeonLineEdit(QWidget):
    """Custom line edit with neon glow effect"""
    
    textChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._line_edit = QPushButton()
        self._line_edit.setObjectName("neonLineEdit")
        self._line_edit.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                border: 1px solid #2d2d2d;
                border-radius: 5px;
                padding: 8px;
                color: #ecf0f1;
                text-align: left;
            }
            
            QPushButton:hover {
                border: 1px solid #444444;
            }
            
            QPushButton:focus {
                border: 1px solid #00ffaa;
            }
        """)
        
        self._text = ""
        self._placeholder_text = ""
        self._echo_mode = Qt.TextFormat.PlainText
        
        # Connect button click to start editing
        self._line_edit.clicked.connect(self._start_editing)
        
        layout.addWidget(self._line_edit)
        
        # Initially not in edit mode
        self._editing = False
        self._update_display()
    
    def _start_editing(self):
        """Start text editing mode"""
        if not self._editing:
            from PyQt6.QtWidgets import QInputDialog, QLineEdit
            
            input_type = QLineEdit.EchoMode.Normal
            if self._echo_mode == QLineEdit.EchoMode.Password:
                input_type = QLineEdit.EchoMode.Password
            
            text, ok = QInputDialog.getText(
                self,
                "ویرایش متن",
                "متن:",
                input_type,
                self._text
            )
            
            if ok:
                self.setText(text)
                self.textChanged.emit(text)
    
    def text(self):
        """Get the current text"""
        return self._text
    
    def setText(self, text):
        """Set the text"""
        if self._text != text:
            self._text = text
            self._update_display()
            self.textChanged.emit(text)
    
    def placeholderText(self):
        """Get the placeholder text"""
        return self._placeholder_text
    
    def setPlaceholderText(self, text):
        """Set the placeholder text"""
        self._placeholder_text = text
        self._update_display()
    
    def echoMode(self):
        """Get the echo mode"""
        return self._echo_mode
    
    def setEchoMode(self, mode):
        """Set the echo mode"""
        self._echo_mode = mode
        self._update_display()
    
    def _update_display(self):
        """Update the display based on current settings"""
        if not self._text and self._placeholder_text:
            # Show placeholder
            self._line_edit.setText(self._placeholder_text)
            self._line_edit.setStyleSheet("""
                QPushButton {
                    background-color: #1a1a1a;
                    border: 1px solid #2d2d2d;
                    border-radius: 5px;
                    padding: 8px;
                    color: #555555;
                    text-align: left;
                }
                
                QPushButton:hover {
                    border: 1px solid #444444;
                }
            """)
        else:
            # Show text or masked text
            display_text = self._text
            if self._echo_mode == Qt.TextFormat.RichText:
                display_text = "•" * len(self._text)
            
            self._line_edit.setText(display_text)
            self._line_edit.setStyleSheet("""
                QPushButton {
                    background-color: #1a1a1a;
                    border: 1px solid #2d2d2d;
                    border-radius: 5px;
                    padding: 8px;
                    color: #ecf0f1;
                    text-align: left;
                }
                
                QPushButton:hover {
                    border: 1px solid #444444;
                }
                
                QPushButton:focus {
                    border: 1px solid #00ffaa;
                }
            """)
    
    def clear(self):
        """Clear the text"""
        self.setText("")


class NeonButton(QPushButton):
    """Custom button with neon glow effect"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        
        self.setObjectName("neonButton")
        self._glow_color = QColor(0, 255, 170)  # Default neon green
        self._glow_opacity_value = 0.0  # Initialize the opacity value
        self._animation = QPropertyAnimation(self, b"_glow_opacity")
        self._animation.setDuration(300)
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        
        # Connect events
        self.enterEvent = self._enter_event
        self.leaveEvent = self._leave_event
    
    def _enter_event(self, event):
        """Handle mouse enter event"""
        self._animation.setDirection(QPropertyAnimation.Direction.Forward)
        self._animation.start()
    
    def _leave_event(self, event):
        """Handle mouse leave event"""
        self._animation.setDirection(QPropertyAnimation.Direction.Backward)
        self._animation.start()
    
    def setColor(self, color):
        """Set the glow color"""
        self._glow_color = color
        self.update()
    
    def color(self):
        """Get the glow color"""
        return self._glow_color
    
    def _get_glow_opacity(self):
        return self._glow_opacity_value
    
    def _set_glow_opacity(self, opacity):
        self._glow_opacity_value = opacity
        self.update()
    
    # Initialize the internal value
    _glow_opacity_value = 0.0
    # Create property
    _glow_opacity = Property(float, _get_glow_opacity, _set_glow_opacity)
    
    def paintEvent(self, event):
        """Custom paint event for neon effect"""
        super().paintEvent(event)
        
        if self._glow_opacity_value > 0:
            # Draw glow effect
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Create a glow color with opacity
            glow_color = QColor(self._glow_color)
            glow_color.setAlphaF(self._glow_opacity_value * 0.6)
            
            # Draw outer glow
            pen = QPen(glow_color, 2)
            painter.setPen(pen)
            painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 5, 5)
            
            # Draw border
            border_color = QColor(self._glow_color)
            border_color.setAlphaF(0.8 + self._glow_opacity_value * 0.2)
            pen = QPen(border_color, 1)
            painter.setPen(pen)
            painter.drawRoundedRect(self.rect().adjusted(0, 0, 0, 0), 5, 5)


class NeonIconButton(QPushButton):
    """Custom icon button with neon effect for sidebar"""
    
    def __init__(self, text="", icon="", parent=None):
        super().__init__(text, parent)
        
        self.setObjectName("neonIconButton")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Set icon if provided
        if icon:
            self.setText(f"{icon}  {text}")
        
        self._active = False
    
    def setActive(self, active):
        """Set if the button is active"""
        self._active = active
        self.setChecked(active)
        self.update()
    
    def isActive(self):
        """Get if the button is active"""
        return self._active


class GlowLabel(QLabel):
    """Custom label with neon glow effect"""
    
    def __init__(self, text="", parent=None, glow_color=None):
        super().__init__(text, parent)
        
        self.setObjectName("glowLabel")
        self._glow_color = glow_color or QColor(0, 255, 170)  # Default neon green
        self._glow_radius = 10
        self._glow_strength_value = 0.8  # Initialize the strength value
        
        # Create glow animation
        # Note: Using correct property path for animation
        self._glow_animation = QPropertyAnimation(self, b"_glow_strength")
        self._glow_animation.setDuration(1500)
        self._glow_animation.setStartValue(0.6)
        self._glow_animation.setEndValue(1.0)
        self._glow_animation.setLoopCount(-1)  # Infinite loop
        self._glow_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        
        # Start animation
        self._glow_animation.start()
    
    def _get_glow_strength(self):
        return self._glow_strength_value
    
    def _set_glow_strength(self, strength):
        self._glow_strength_value = strength
        self.update()
    
    # Initialize the internal value
    _glow_strength_value = 0.8
    # Create property
    _glow_strength = Property(float, _get_glow_strength, _set_glow_strength)
    
    def paintEvent(self, event):
        """Custom paint event for glow effect"""
        text = self.text()
        if not text:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate text position
        font = self.font()
        font.setBold(True)
        metrics = QFontMetrics(font)
        
        rect = self.rect()
        alignment = self.alignment()
        
        if alignment & Qt.AlignmentFlag.AlignHCenter:
            x = rect.width() / 2 - metrics.horizontalAdvance(text) / 2
        elif alignment & Qt.AlignmentFlag.AlignRight:
            x = rect.width() - metrics.horizontalAdvance(text) - 5
        else:
            x = 5
            
        if alignment & Qt.AlignmentFlag.AlignVCenter:
            y = rect.height() / 2 + metrics.height() / 3
        elif alignment & Qt.AlignmentFlag.AlignBottom:
            y = rect.height() - 5
        else:
            y = metrics.height()
        
        # Draw glow
        glow_color = QColor(self._glow_color)
        glow_color.setAlphaF(self._glow_strength_value * 0.4)
        
        for i in range(5):
            painter.setPen(QPen(glow_color, 1 + i))
            painter.setFont(font)
            painter.drawText(QPoint(int(x), int(y)), text)
        
        # Draw text
        painter.setPen(self._glow_color)
        painter.setFont(font)
        painter.drawText(QPoint(int(x), int(y)), text)


class NeonCard(QFrame):
    """Custom card widget with neon glow effect"""
    
    def __init__(self, title="", value="", color=None, parent=None):
        super().__init__(parent)
        
        self.setObjectName("neonCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumHeight(150)
        
        # Store color
        self._color = color or QColor(0, 255, 170)  # Default neon green
        
        # Set up layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setObjectName("cardValue")
        self.value_label.setWordWrap(True)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.title_label, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.value_label, 1, Qt.AlignmentFlag.AlignCenter)
        
        # Set color-specific styles
        self._update_style()
    
    def _update_style(self):
        """Update the card style with the current color"""
        color_str = f"rgb({self._color.red()}, {self._color.green()}, {self._color.blue()})"
        
        self.setStyleSheet(f"""
            QFrame#neonCard {{
                background-color: rgba(20, 20, 20, 0.8);
                border: 1px solid {color_str};
                border-radius: 8px;
                padding: 10px;
            }}
            
            QLabel#cardTitle {{
                font-size: 12pt;
                color: {color_str};
                font-weight: bold;
            }}
            
            QLabel#cardValue {{
                font-size: 16pt;
                font-weight: bold;
                color: #ecf0f1;
            }}
        """)
    
    def setValue(self, value):
        """Set the card value"""
        self.value_label.setText(value)
    
    def setHtml(self, html):
        """Set HTML content for the value label"""
        self.value_label.setText(html)
    
    def setColor(self, color):
        """Set the card color"""
        self._color = color
        self._update_style()
    

class ChartWidget(QFrame):
    """Chart widget using native Qt drawing capabilities"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        
        self.setObjectName("chartWidget")
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )
        self.setMinimumHeight(250)
        
        # Set up layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("chartTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        # Import SimpleChartView from visualization
        from app.utils.visualization import SimpleChartView
        
        # Create chart view
        self.chart_view = SimpleChartView(self)
        
        # Show empty chart initially
        self.chart_view.set_empty()
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.chart_view)
    
    def _load_empty_chart(self):
        """Load an empty chart as placeholder"""
        self.chart_view.set_empty()
    
    def update_bar_chart(self, labels, datasets):
        """
        Update the chart with bar chart data
        
        Parameters:
            labels (list): List of labels for X axis
            datasets (list): List of dataset objects with the following format:
                [
                    {
                        'label': 'Dataset 1 Label',
                        'data': [dataset1_values],
                        'color': 'rgba(0, 255, 170, 0.7)'
                    },
                    {
                        'label': 'Dataset 2 Label',
                        'data': [dataset2_values],
                        'color': 'rgba(255, 0, 128, 0.7)'
                    }
                ]
        """
        if not labels or not datasets:
            self._load_empty_chart()
            return

        # Use new SimpleChartView system
        self.chart_view.set_bar_chart(labels, datasets, self.title_label.text())
    
    def update_line_chart(self, labels, values, label="داده", color="rgba(0, 255, 170, 0.7)"):
        """
        Update the chart with line chart data
        
        Parameters:
            labels (list): List of labels for X axis
            values (list): List of values
            label (str): Dataset label
            color (str): Line color in rgba format
        """
        if not labels or not values:
            self._load_empty_chart()
            return
        
        # Create dataset for line chart
        dataset = {
            'label': label,
            'data': values
        }
        
        # Use new SimpleChartView system
        self.chart_view.set_line_chart(labels, [dataset], self.title_label.text())
    
    def update_pie_chart(self, labels, values):
        """
        Update the chart with pie chart data
        
        Parameters:
            labels (list): List of labels for segments
            values (list): List of values
        """
        if not labels or not values:
            self._load_empty_chart()
            return
        
        # Use new SimpleChartView system
        self.chart_view.set_pie_chart(labels, values, self.title_label.text())


class UserProfileWidget(QFrame):
    """User profile widget for sidebar"""
    
    def __init__(self, user, parent=None):
        super().__init__(parent)
        
        self.setObjectName("userProfileWidget")
        self.setMinimumHeight(80)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Username
        self.username_label = QLabel(user.username)
        self.username_label.setObjectName("usernameLabel")
        
        # Status/Last login
        self.status_label = QLabel("آنلاین")
        self.status_label.setObjectName("userEmailLabel")
        
        layout.addWidget(self.username_label)
        layout.addWidget(self.status_label)


class PersianCalendarWidget(QWidget):
    """Custom Persian calendar widget"""
    
    selectionChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setObjectName("persianCalendar")
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Current selection
        self._selected_date = QDate.currentDate()
        
        # Dates with events
        self._event_dates = []
        
        # Calendar header (month/year selection)
        header_layout = QHBoxLayout()
        
        self._prev_month_btn = QPushButton("◀")
        self._prev_month_btn.clicked.connect(self._go_prev_month)
        
        self._month_year_label = QLabel()
        self._month_year_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self._next_month_btn = QPushButton("▶")
        self._next_month_btn.clicked.connect(self._go_next_month)
        
        header_layout.addWidget(self._prev_month_btn)
        header_layout.addWidget(self._month_year_label, 1)
        header_layout.addWidget(self._next_month_btn)
        
        layout.addLayout(header_layout)
        
        # Weekday headers
        weekday_layout = QHBoxLayout()
        weekdays = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]
        
        for day in weekdays:
            label = QLabel(day)
            label.setObjectName("weekdayHeader")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            weekday_layout.addWidget(label)
        
        layout.addLayout(weekday_layout)
        
        # Calendar grid
        self._calendar_grid = QGridLayout()
        self._calendar_grid.setSpacing(1)
        
        # Create date buttons
        self._date_buttons = []
        for i in range(6):  # 6 rows
            for j in range(7):  # 7 columns
                btn = QPushButton()
                btn.setObjectName("dateButton")
                btn.setCheckable(True)
                btn.clicked.connect(lambda checked, row=i, col=j: self._date_clicked(row, col))
                self._calendar_grid.addWidget(btn, i, j)
                self._date_buttons.append(btn)
        
        layout.addLayout(self._calendar_grid)
        
        # Update calendar
        self._update_calendar()
    
    def _update_calendar(self):
        """Update the calendar based on selected date"""
        g_date = self._selected_date.toPyDate()
        p_date = jdatetime.date.fromgregorian(date=g_date)
        
        # Update month/year label
        month_names = [
            "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", 
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
        ]
        
        self._month_year_label.setText(f"{month_names[p_date.month - 1]} {p_date.year}")
        
        # Clear previous buttons
        for btn in self._date_buttons:
            btn.setText("")
            btn.setChecked(False)
            btn.setProperty("date", None)
            btn.setObjectName("dateButton")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        # Get first day of month
        first_day = jdatetime.date(p_date.year, p_date.month, 1)
        
        # Convert to gregorian to get day of week (0=Monday, 6=Sunday)
        g_first_day = first_day.togregorian()
        first_day_of_week = g_first_day.weekday()
        
        # Adjust for Persian calendar (0=Saturday, 6=Friday)
        first_day_of_week = (first_day_of_week + 2) % 7
        
        # Get number of days in month
        if p_date.month <= 6:
            days_in_month = 31
        elif p_date.month <= 11:
            days_in_month = 30
        else:  # month == 12
            if p_date.isleap():
                days_in_month = 30
            else:
                days_in_month = 29
        
        # Fill calendar
        day_counter = 1
        for i in range(6):  # 6 rows
            for j in range(7):  # 7 columns
                index = i * 7 + j
                btn = self._date_buttons[index]
                
                if (i == 0 and j < first_day_of_week) or day_counter > days_in_month:
                    btn.setText("")
                    btn.setProperty("date", None)
                    btn.setEnabled(False)
                else:
                    btn.setText(str(day_counter))
                    
                    # Store date in button
                    p_btn_date = jdatetime.date(p_date.year, p_date.month, day_counter)
                    g_btn_date = p_btn_date.togregorian()
                    q_btn_date = QDate(g_btn_date.year, g_btn_date.month, g_btn_date.day)
                    btn.setProperty("date", q_btn_date)
                    btn.setEnabled(True)
                    
                    # Check if this is current date
                    if day_counter == p_date.day and p_date.month == jdatetime.date.today().month and p_date.year == jdatetime.date.today().year:
                        btn.setObjectName("currentDateButton")
                        btn.style().unpolish(btn)
                        btn.style().polish(btn)
                    
                    # Check if this is selected date
                    if day_counter == p_date.day:
                        btn.setChecked(True)
                    
                    # Check if date has events
                    if q_btn_date in self._event_dates:
                        btn.setObjectName("eventDateButton")
                        btn.style().unpolish(btn)
                        btn.style().polish(btn)
                    
                    day_counter += 1
    
    def _date_clicked(self, row, col):
        """Handle date button click"""
        index = row * 7 + col
        btn = self._date_buttons[index]
        date = btn.property("date")
        
        if date:
            self._selected_date = date
            
            # Update selection
            for b in self._date_buttons:
                if b != btn:
                    b.setChecked(False)
            
            # Emit signal
            self.selectionChanged.emit()
    
    def _go_prev_month(self):
        """Go to previous month"""
        current_date = self._selected_date
        self._selected_date = current_date.addMonths(-1)
        self._update_calendar()
        self.selectionChanged.emit()
    
    def _go_next_month(self):
        """Go to next month"""
        current_date = self._selected_date
        self._selected_date = current_date.addMonths(1)
        self._update_calendar()
        self.selectionChanged.emit()
    
    def selectedDate(self):
        """Get the currently selected date"""
        return self._selected_date
    
    def setSelectedDate(self, date):
        """Set the currently selected date"""
        self._selected_date = date
        self._update_calendar()
    
    def setEventDates(self, dates):
        """Set dates that have events"""
        self._event_dates = dates
        self._update_calendar()
