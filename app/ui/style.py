#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Stylesheet definitions for the Persian Life Manager Application
"""

# Main application stylesheet
STYLESHEET = """
/* Global Settings */
QWidget {
    font-family: 'Segoe UI', 'Vazirmatn', 'Vazir', 'Tahoma', sans-serif;
    font-size: 10pt;
    color: #ecf0f1;
    border: none;
    background-color: transparent;
}

/* Main Windows and Containers */
QMainWindow, QDialog {
    background-color: #121212;
}

QScrollArea, QWidget#dashboard, QWidget#financeModule, QWidget#healthModule, 
QWidget#calendarModule, QWidget#settingsWidget, QTabWidget::pane {
    background-color: #121212;
}

QSplitter::handle {
    background-color: #2d2d2d;
}

QFrame#leftPanel {
    background-color: #0a0a0a;
    border-right: 1px solid #2d2d2d;
}

QFrame#rightPanel, QFrame#sidebar {
    background-color: #171717;
}

/* Neon Card Widget */
QFrame#neonCard {
    background-color: rgba(20, 20, 20, 0.8);
    border: 1px solid #00ffaa;
    border-radius: 8px;
    padding: 10px;
}

QFrame#neonCard QLabel#cardTitle {
    font-size: 12pt;
    color: #00ffaa;
    font-weight: bold;
}

QFrame#neonCard QLabel#cardValue {
    font-size: 16pt;
    font-weight: bold;
}

/* Form Card */
QFrame#formCard {
    background-color: rgba(25, 25, 25, 0.8);
    border: 1px solid #2d2d2d;
    border-radius: 8px;
    padding: 15px;
    margin: 5px;
}

/* Headers and Titles */
QLabel#moduleTitle {
    font-size: 18pt;
    font-weight: bold;
    color: #00ffaa;
    margin-bottom: 15px;
}

QLabel#sectionTitle {
    font-size: 14pt;
    font-weight: bold;
    color: #ecf0f1;
    margin-top: 10px;
    margin-bottom: 5px;
}

QLabel#welcomeLabel {
    font-size: 16pt;
    font-weight: bold;
    color: #00ffaa;
}

QLabel#dateLabel {
    font-size: 12pt;
    color: #ecf0f1;
}

QLabel#appTitle {
    font-size: 20pt;
    font-weight: bold;
    color: #00ffaa;
    margin: 20px;
}

QLabel#appTitleLarge {
    font-size: 24pt;
    font-weight: bold;
    color: #00ffaa;
    margin: 20px;
}

QLabel#appSubtitle {
    font-size: 12pt;
    color: #ecf0f1;
    margin-bottom: 20px;
}

QLabel#loginTitle {
    font-size: 18pt;
    font-weight: bold;
    color: #ecf0f1;
    margin: 20px;
}

QLabel#aiTitle {
    font-size: 18pt;
    font-weight: bold;
    color: #00ffaa;
    margin: 15px;
}

QLabel#aiSubtitle {
    font-size: 11pt;
    color: #ecf0f1;
    margin-bottom: 20px;
}

QLabel#monthYearLabel {
    font-size: 14pt;
    font-weight: bold;
    color: #00ffaa;
}

QLabel#selectedDateLabel {
    font-size: 12pt;
    font-weight: bold;
    color: #ecf0f1;
    margin: 10px 0;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #2d2d2d;
    border-radius: 5px;
    top: -1px;
}

QTabBar::tab {
    background-color: #1a1a1a;
    color: #ecf0f1;
    padding: 8px 16px;
    margin-right: 2px;
    border: 1px solid #2d2d2d;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
}

QTabBar::tab:selected {
    background-color: #121212;
    border-bottom-color: #121212;
    color: #00ffaa;
}

QTabBar::tab:hover:!selected {
    background-color: #222222;
}

/* Table Widget */
QTableWidget {
    background-color: #171717;
    border: 1px solid #2d2d2d;
    border-radius: 5px;
    gridline-color: #2d2d2d;
    selection-background-color: rgba(0, 255, 170, 0.3);
}

QTableWidget::item {
    padding: 5px;
}

QTableWidget::item:selected {
    background-color: rgba(0, 255, 170, 0.3);
    color: #ffffff;
}

QHeaderView::section {
    background-color: #1a1a1a;
    color: #ecf0f1;
    padding: 5px;
    border: none;
    border-right: 1px solid #2d2d2d;
    border-bottom: 1px solid #2d2d2d;
}

/* List Widget */
QListWidget {
    background-color: #171717;
    border: 1px solid #2d2d2d;
    border-radius: 5px;
    padding: 5px;
}

QListWidget::item {
    padding: 5px;
    border-radius: 3px;
}

QListWidget::item:selected {
    background-color: rgba(0, 255, 170, 0.3);
    color: #ffffff;
}

QListWidget::item:hover:!selected {
    background-color: rgba(0, 255, 170, 0.1);
}

/* Line Edit */
QLineEdit {
    background-color: #1a1a1a;
    border: 1px solid #2d2d2d;
    border-radius: 5px;
    padding: 8px;
    color: #ecf0f1;
}

QLineEdit:focus {
    border: 1px solid #00ffaa;
}

QLineEdit:hover:!focus {
    border: 1px solid #444444;
}

QLineEdit:disabled {
    background-color: #1a1a1a;
    color: #555555;
}

/* Buttons */
QPushButton {
    background-color: #2d2d2d;
    color: #ecf0f1;
    border: none;
    border-radius: 5px;
    padding: 8px 16px;
    min-width: 100px;
}

QPushButton:hover {
    background-color: #3a3a3a;
}

QPushButton:pressed {
    background-color: #1a1a1a;
}

QPushButton:disabled {
    background-color: #1a1a1a;
    color: #555555;
}

/* Neon Button */
QPushButton#neonButton {
    background-color: rgba(0, 0, 0, 0.7);
    color: #00ffaa;
    border: 1px solid #00ffaa;
    border-radius: 5px;
    padding: 8px 16px;
    min-width: 100px;
}

QPushButton#neonButton:hover {
    background-color: rgba(0, 255, 170, 0.2);
    color: #ffffff;
}

QPushButton#neonButton:pressed {
    background-color: rgba(0, 255, 170, 0.4);
}

/* Neon Blue Button */
QPushButton#neonBlueButton {
    background-color: rgba(0, 0, 0, 0.7);
    color: #00aaff;
    border: 1px solid #00aaff;
    border-radius: 5px;
    padding: 8px 16px;
    min-width: 100px;
}

QPushButton#neonBlueButton:hover {
    background-color: rgba(0, 170, 255, 0.2);
    color: #ffffff;
}

QPushButton#neonBlueButton:pressed {
    background-color: rgba(0, 170, 255, 0.4);
}

/* Neon Pink Button */
QPushButton#neonPinkButton {
    background-color: rgba(0, 0, 0, 0.7);
    color: #ff0080;
    border: 1px solid #ff0080;
    border-radius: 5px;
    padding: 8px 16px;
    min-width: 100px;
}

QPushButton#neonPinkButton:hover {
    background-color: rgba(255, 0, 128, 0.2);
    color: #ffffff;
}

QPushButton#neonPinkButton:pressed {
    background-color: rgba(255, 0, 128, 0.4);
}

/* Neon Icon Button */
QPushButton#neonIconButton {
    background-color: transparent;
    color: #ecf0f1;
    border: none;
    border-radius: 5px;
    padding: 10px;
    text-align: left;
    font-size: 12pt;
}

QPushButton#neonIconButton:hover {
    background-color: rgba(0, 255, 170, 0.1);
    color: #00ffaa;
}

QPushButton#neonIconButton:pressed {
    background-color: rgba(0, 255, 170, 0.2);
}

QPushButton#neonIconButton:checked {
    background-color: rgba(0, 255, 170, 0.2);
    color: #00ffaa;
    border-left: 3px solid #00ffaa;
    font-weight: bold;
}

/* ComboBox */
QComboBox {
    background-color: #1a1a1a;
    border: 1px solid #2d2d2d;
    border-radius: 5px;
    padding: 8px;
    color: #ecf0f1;
    min-width: 100px;
}

QComboBox:hover {
    border: 1px solid #444444;
}

QComboBox:focus {
    border: 1px solid #00ffaa;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #2d2d2d;
}

QComboBox::down-arrow {
    image: url('app/resources/icons/down-arrow.svg');
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #1a1a1a;
    border: 1px solid #2d2d2d;
    border-radius: 0px;
    selection-background-color: rgba(0, 255, 170, 0.3);
}

/* SpinBox */
QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit {
    background-color: #1a1a1a;
    border: 1px solid #2d2d2d;
    border-radius: 5px;
    padding: 8px;
    color: #ecf0f1;
    min-width: 100px;
}

QSpinBox:hover, QDoubleSpinBox:hover, QDateEdit:hover, QTimeEdit:hover {
    border: 1px solid #444444;
}

QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QTimeEdit:focus {
    border: 1px solid #00ffaa;
}

QSpinBox::up-button, QDoubleSpinBox::up-button, QDateEdit::up-button, QTimeEdit::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #2d2d2d;
    border-bottom: 1px solid #2d2d2d;
}

QSpinBox::down-button, QDoubleSpinBox::down-button, QDateEdit::down-button, QTimeEdit::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 20px;
    border-left: 1px solid #2d2d2d;
}

/* CheckBox */
QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #2d2d2d;
    border-radius: 3px;
    background-color: #1a1a1a;
}

QCheckBox::indicator:checked {
    background-color: #00ffaa;
    border: 1px solid #00ffaa;
}

QCheckBox::indicator:unchecked:hover {
    border: 1px solid #00ffaa;
}

/* Progress Bar */
QProgressBar {
    background-color: #1a1a1a;
    border: 1px solid #2d2d2d;
    border-radius: 5px;
    text-align: center;
    color: #ecf0f1;
}

QProgressBar::chunk {
    background-color: rgba(0, 255, 170, 0.7);
    border-radius: 3px;
}

QProgressBar#neonProgressBar {
    background-color: #1a1a1a;
    border: 1px solid #2d2d2d;
    border-radius: 5px;
    text-align: center;
    color: #ecf0f1;
    font-weight: bold;
}

QProgressBar#neonProgressBar::chunk {
    background-color: rgba(0, 255, 170, 0.7);
    border-radius: 3px;
}

/* ScrollBar */
QScrollBar:vertical {
    background-color: #121212;
    width: 12px;
    margin: 15px 0px 15px 0px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #2d2d2d;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #3a3a3a;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    background: none;
    height: 15px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    background-color: #121212;
    height: 12px;
    margin: 0px 15px 0px 15px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #2d2d2d;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #3a3a3a;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    background: none;
    width: 15px;
    subcontrol-position: right;
    subcontrol-origin: margin;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}

/* Slider */
QSlider::groove:horizontal {
    border: 1px solid #2d2d2d;
    height: 6px;
    background: #1a1a1a;
    margin: 0px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #00ffaa;
    border: 1px solid #00ffaa;
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background: #00ccaa;
}

/* Calendar Widget */
QCalendarWidget {
    background-color: #171717;
    border: 1px solid #2d2d2d;
}

QCalendarWidget QToolButton {
    color: #ecf0f1;
    background-color: transparent;
    border: none;
}

QCalendarWidget QMenu {
    background-color: #1a1a1a;
    border: 1px solid #2d2d2d;
}

QCalendarWidget QSpinBox {
    background-color: #1a1a1a;
    border: 1px solid #2d2d2d;
    color: #ecf0f1;
}

QCalendarWidget QAbstractItemView {
    background-color: #171717;
    padding: 10px;
    selection-background-color: rgba(0, 255, 170, 0.3);
    selection-color: #ecf0f1;
}

QCalendarWidget QWidget {
    background-color: #171717;
}

QCalendarWidget QWidget#qt_calendar_navigationbar {
    background-color: #1a1a1a;
}

/* Persian Calendar Widget */
QFrame#persianCalendar {
    background-color: #171717;
    border: 1px solid #2d2d2d;
    padding: 5px;
}

QLabel#weekdayHeader {
    font-weight: bold;
    color: #ecf0f1;
    padding: 5px;
    background-color: #1a1a1a;
    border-bottom: 1px solid #2d2d2d;
}

QPushButton#dateButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 5px;
    font-size: 10pt;
    min-width: 30px;
    min-height: 30px;
    padding: 5px;
}

QPushButton#dateButton:hover {
    background-color: rgba(0, 255, 170, 0.1);
    border: 1px solid rgba(0, 255, 170, 0.3);
}

QPushButton#dateButton:checked {
    background-color: rgba(0, 255, 170, 0.3);
    color: #ffffff;
    font-weight: bold;
}

QPushButton#currentDateButton {
    background-color: rgba(0, 170, 255, 0.2);
    border: 1px solid rgba(0, 170, 255, 0.5);
    color: #ffffff;
}

QPushButton#eventDateButton {
    color: #00ffaa;
    font-weight: bold;
}

/* Chart Widget */
QFrame#chartWidget {
    background-color: #171717;
    border: 1px solid #2d2d2d;
    border-radius: 5px;
    padding: 10px;
}

QLabel#chartTitle {
    font-size: 12pt;
    color: #ecf0f1;
    font-weight: bold;
    margin-bottom: 5px;
}

/* User Profile Widget */
QFrame#userProfileWidget {
    background-color: rgba(0, 0, 0, 0.3);
    border-bottom: 1px solid #2d2d2d;
    padding: 15px;
}

QLabel#usernameLabel {
    font-size: 14pt;
    font-weight: bold;
    color: #00ffaa;
}

QLabel#userEmailLabel {
    font-size: 10pt;
    color: #ecf0f1;
}

/* Filter Frame */
QFrame#filterFrame {
    background-color: rgba(25, 25, 25, 0.8);
    border: 1px solid #2d2d2d;
    border-radius: 8px;
    padding: 10px;
    margin: 5px;
}

/* Advice Container */
QFrame#adviceContainer {
    background-color: rgba(25, 25, 25, 0.8);
    border: 1px solid #2d2d2d;
    border-radius: 8px;
    padding: 15px;
    margin: 10px;
}

QLabel#adviceText {
    font-size: 11pt;
    line-height: 1.4;
    color: #ecf0f1;
}

/* Goals Widget */
QFrame#goalWidget {
    background-color: rgba(25, 25, 25, 0.8);
    border: 1px solid #2d2d2d;
    border-radius: 8px;
    padding: 10px;
    margin: 5px;
}

QLabel#goalTitle {
    font-size: 12pt;
    font-weight: bold;
    color: #00ffaa;
}

/* About Text */
QLabel#aboutText {
    font-size: 11pt;
    line-height: 1.4;
    color: #ecf0f1;
}

QLabel#versionLabel {
    font-size: 12pt;
    color: #888888;
}

QLabel#contactInfo {
    font-size: 11pt;
    color: #888888;
    margin-top: 20px;
}

/* Event Dialog */
QDialog#eventDialog, QDialog#taskDialog {
    background-color: #121212;
    border: 1px solid #2d2d2d;
    border-radius: 5px;
}

/* Login Window Specific */
QFrame#glowFrame {
    border: 2px solid #00ffaa;
    border-radius: 10px;
    background-color: transparent;
}

/* Context Menu */
QMenu {
    background-color: #1a1a1a;
    border: 1px solid #2d2d2d;
    border-radius: 3px;
    padding: 5px;
}

QMenu::item {
    padding: 5px 30px 5px 20px;
    border-radius: 3px;
}

QMenu::item:selected {
    background-color: rgba(0, 255, 170, 0.2);
    color: #00ffaa;
}

QMenu::separator {
    height: 1px;
    background-color: #2d2d2d;
    margin: 5px 10px;
}

/* Message Boxes */
QMessageBox {
    background-color: #121212;
}

QMessageBox QLabel {
    color: #ecf0f1;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* Tooltip */
QToolTip {
    background-color: #1a1a1a;
    color: #ecf0f1;
    border: 1px solid #2d2d2d;
    border-radius: 3px;
    padding: 5px;
}
"""
