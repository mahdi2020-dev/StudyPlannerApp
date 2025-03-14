#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Finance Module UI for Personal Finance Management
"""

import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QDateEdit, QSpinBox, QDoubleSpinBox, QTabWidget, 
    QFormLayout, QScrollArea, QFrame, QGridLayout, QSplitter,
    QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSlot, QDate
from PyQt6.QtGui import QColor

from app.services.finance_service import FinanceService
from app.models.finance import Transaction, Category
from app.models.user import User
from app.ui.widgets import NeonButton, NeonLineEdit, ChartWidget, NeonCard
from app.utils.date_utils import get_current_persian_date, gregorian_to_persian
from app.utils.persian_utils import get_persian_month_name

logger = logging.getLogger(__name__)

class FinanceModule(QWidget):
    """Finance module for expense and income tracking"""
    
    def __init__(self, user: User):
        super().__init__()
        
        self.user = user
        self.finance_service = FinanceService(user.id)
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        """Initialize the UI components"""
        self.setObjectName("financeModule")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Module title
        title = QLabel("مدیریت مالی")
        title.setObjectName("moduleTitle")
        main_layout.addWidget(title)
        
        # Tab widget for different finance sections
        self.tabs = QTabWidget()
        self.tabs.setObjectName("financeTabs")
        
        # Create tabs
        self.dashboard_tab = QWidget()
        self.transactions_tab = QWidget()
        self.reports_tab = QWidget()
        self.categories_tab = QWidget()
        
        self.tabs.addTab(self.dashboard_tab, "داشبورد مالی")
        self.tabs.addTab(self.transactions_tab, "ثبت تراکنش")
        self.tabs.addTab(self.reports_tab, "گزارش‌ها")
        self.tabs.addTab(self.categories_tab, "دسته‌بندی‌ها")
        
        # Setup tab contents
        self.setup_dashboard_tab()
        self.setup_transactions_tab()
        self.setup_reports_tab()
        self.setup_categories_tab()
        
        main_layout.addWidget(self.tabs)
        
    def setup_dashboard_tab(self):
        """Setup the finance dashboard tab"""
        layout = QVBoxLayout(self.dashboard_tab)
        
        # Summary cards row
        cards_layout = QHBoxLayout()
        
        # Income card
        self.income_card = NeonCard("درآمد ماه جاری", "0 تومان", QColor(0, 255, 170))
        
        # Expense card
        self.expense_card = NeonCard("هزینه ماه جاری", "0 تومان", QColor(255, 0, 128))
        
        # Balance card
        self.balance_card = NeonCard("مانده", "0 تومان", QColor(0, 170, 255))
        
        cards_layout.addWidget(self.income_card)
        cards_layout.addWidget(self.expense_card)
        cards_layout.addWidget(self.balance_card)
        
        layout.addLayout(cards_layout)
        
        # Charts section
        charts_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Expense by category chart
        self.category_chart = ChartWidget("نمودار هزینه‌ها بر اساس دسته‌بندی")
        
        # Income vs Expense chart
        self.income_expense_chart = ChartWidget("مقایسه درآمد و هزینه")
        
        charts_splitter.addWidget(self.category_chart)
        charts_splitter.addWidget(self.income_expense_chart)
        
        layout.addWidget(charts_splitter)
        
        # Recent transactions
        transaction_container = QWidget()
        transaction_layout = QVBoxLayout(transaction_container)
        
        recent_trans_label = QLabel("تراکنش‌های اخیر")
        recent_trans_label.setObjectName("sectionTitle")
        
        self.recent_transactions_table = QTableWidget()
        self.recent_transactions_table.setColumnCount(5)
        self.recent_transactions_table.setHorizontalHeaderLabels(["تاریخ", "عنوان", "دسته‌بندی", "مبلغ", "نوع"])
        self.recent_transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        transaction_layout.addWidget(recent_trans_label)
        transaction_layout.addWidget(self.recent_transactions_table)
        
        layout.addWidget(transaction_container)
        
    def setup_transactions_tab(self):
        """Setup the transactions tab"""
        layout = QVBoxLayout(self.transactions_tab)
        
        # Transaction form
        form_card = QFrame()
        form_card.setObjectName("formCard")
        form_layout = QFormLayout(form_card)
        form_layout.setSpacing(15)
        
        # Transaction date
        self.transaction_date = QDateEdit()
        self.transaction_date.setCalendarPopup(True)
        self.transaction_date.setDate(QDate.currentDate())
        
        # Transaction title
        self.transaction_title = NeonLineEdit()
        
        # Transaction amount
        self.transaction_amount = QDoubleSpinBox()
        self.transaction_amount.setRange(0, 1000000000)
        self.transaction_amount.setSuffix(" تومان")
        self.transaction_amount.setGroupSeparatorShown(True)
        
        # Transaction type
        self.transaction_type = QComboBox()
        self.transaction_type.addItem("هزینه")
        self.transaction_type.addItem("درآمد")
        
        # Transaction category
        self.transaction_category = QComboBox()
        
        # Description
        self.transaction_description = NeonLineEdit()
        
        # Add form fields
        form_layout.addRow("تاریخ:", self.transaction_date)
        form_layout.addRow("عنوان:", self.transaction_title)
        form_layout.addRow("مبلغ:", self.transaction_amount)
        form_layout.addRow("نوع:", self.transaction_type)
        form_layout.addRow("دسته‌بندی:", self.transaction_category)
        form_layout.addRow("توضیحات:", self.transaction_description)
        
        # Add transaction button
        self.add_transaction_btn = NeonButton("ثبت تراکنش")
        self.add_transaction_btn.clicked.connect(self.add_transaction)
        
        layout.addWidget(QLabel("ثبت تراکنش جدید"))
        layout.addWidget(form_card)
        layout.addWidget(self.add_transaction_btn)
        
        # Transactions list
        transactions_label = QLabel("لیست تراکنش‌ها")
        transactions_label.setObjectName("sectionTitle")
        
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(7)
        self.transactions_table.setHorizontalHeaderLabels(
            ["تاریخ", "عنوان", "دسته‌بندی", "مبلغ", "نوع", "توضیحات", "عملیات"]
        )
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(transactions_label)
        layout.addWidget(self.transactions_table)
        
    def setup_reports_tab(self):
        """Setup the reports tab"""
        layout = QVBoxLayout(self.reports_tab)
        
        # Filter section
        filter_frame = QFrame()
        filter_frame.setObjectName("filterFrame")
        filter_layout = QHBoxLayout(filter_frame)
        
        # Date range filters
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        
        # Category filter
        self.filter_category = QComboBox()
        self.filter_category.addItem("همه دسته‌ها")
        
        # Type filter
        self.filter_type = QComboBox()
        self.filter_type.addItem("همه")
        self.filter_type.addItem("هزینه")
        self.filter_type.addItem("درآمد")
        
        # Apply filter button
        self.apply_filter_btn = NeonButton("اعمال فیلتر")
        self.apply_filter_btn.clicked.connect(self.apply_filters)
        
        filter_layout.addWidget(QLabel("از تاریخ:"))
        filter_layout.addWidget(self.from_date)
        filter_layout.addWidget(QLabel("تا تاریخ:"))
        filter_layout.addWidget(self.to_date)
        filter_layout.addWidget(QLabel("دسته‌بندی:"))
        filter_layout.addWidget(self.filter_category)
        filter_layout.addWidget(QLabel("نوع:"))
        filter_layout.addWidget(self.filter_type)
        filter_layout.addWidget(self.apply_filter_btn)
        
        layout.addWidget(filter_frame)
        
        # Charts section
        self.reports_charts_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Monthly trend chart
        self.monthly_trend_chart = ChartWidget("روند ماهانه درآمد و هزینه")
        
        # Daily trend chart
        self.daily_trend_chart = ChartWidget("روند روزانه هزینه‌ها")
        
        self.reports_charts_splitter.addWidget(self.monthly_trend_chart)
        self.reports_charts_splitter.addWidget(self.daily_trend_chart)
        
        layout.addWidget(self.reports_charts_splitter)
        
        # Filtered transactions table
        self.filtered_transactions_table = QTableWidget()
        self.filtered_transactions_table.setColumnCount(6)
        self.filtered_transactions_table.setHorizontalHeaderLabels(
            ["تاریخ", "عنوان", "دسته‌بندی", "مبلغ", "نوع", "توضیحات"]
        )
        self.filtered_transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(QLabel("تراکنش‌های فیلتر شده"))
        layout.addWidget(self.filtered_transactions_table)
        
    def setup_categories_tab(self):
        """Setup the categories tab"""
        layout = QVBoxLayout(self.categories_tab)
        
        # Add category form
        form_layout = QHBoxLayout()
        
        self.category_name = NeonLineEdit()
        self.category_name.setPlaceholderText("نام دسته‌بندی جدید")
        
        self.category_type = QComboBox()
        self.category_type.addItem("هزینه")
        self.category_type.addItem("درآمد")
        self.category_type.addItem("هر دو")
        
        self.add_category_btn = NeonButton("افزودن دسته‌بندی")
        self.add_category_btn.clicked.connect(self.add_category)
        
        form_layout.addWidget(self.category_name)
        form_layout.addWidget(self.category_type)
        form_layout.addWidget(self.add_category_btn)
        
        layout.addLayout(form_layout)
        
        # Categories table
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(3)
        self.categories_table.setHorizontalHeaderLabels(["نام", "نوع", "عملیات"])
        self.categories_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(QLabel("دسته‌بندی‌های موجود"))
        layout.addWidget(self.categories_table)
    
    def load_data(self):
        """Load initial data for the module"""
        # Load categories
        self.load_categories()
        
        # Load transactions
        self.load_transactions()
        
        # Update dashboard
        self.update_dashboard()
        
        # Load reports
        self.apply_filters()
    
    def load_categories(self):
        """Load categories to UI components"""
        categories = self.finance_service.get_categories()
        
        # Clear current items
        self.transaction_category.clear()
        self.filter_category.clear()
        self.filter_category.addItem("همه دسته‌ها")
        
        # Clear categories table
        self.categories_table.setRowCount(0)
        
        for idx, category in enumerate(categories):
            # Add to category dropdowns
            self.transaction_category.addItem(category.name, category.id)
            self.filter_category.addItem(category.name, category.id)
            
            # Add to categories table
            self.categories_table.insertRow(idx)
            self.categories_table.setItem(idx, 0, QTableWidgetItem(category.name))
            
            category_type = ""
            if category.type == "expense":
                category_type = "هزینه"
            elif category.type == "income":
                category_type = "درآمد"
            else:
                category_type = "هر دو"
                
            self.categories_table.setItem(idx, 1, QTableWidgetItem(category_type))
            
            # Delete button
            delete_btn = NeonButton("حذف")
            delete_btn.setColor(QColor(255, 0, 128))
            delete_btn.clicked.connect(lambda checked, cat_id=category.id: self.delete_category(cat_id))
            
            self.categories_table.setCellWidget(idx, 2, delete_btn)
    
    def load_transactions(self):
        """Load transactions to tables"""
        transactions = self.finance_service.get_transactions()
        
        # Clear tables
        self.transactions_table.setRowCount(0)
        self.recent_transactions_table.setRowCount(0)
        
        # Populate transactions table
        for idx, transaction in enumerate(transactions):
            self.transactions_table.insertRow(idx)
            
            # Get Persian date
            persian_date = gregorian_to_persian(transaction.date)
            
            # Set table items
            self.transactions_table.setItem(idx, 0, QTableWidgetItem(persian_date))
            self.transactions_table.setItem(idx, 1, QTableWidgetItem(transaction.title))
            self.transactions_table.setItem(idx, 2, QTableWidgetItem(transaction.category_name))
            
            amount_item = QTableWidgetItem(f"{transaction.amount:,} تومان")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.transactions_table.setItem(idx, 3, amount_item)
            
            trans_type = "هزینه" if transaction.type == "expense" else "درآمد"
            type_item = QTableWidgetItem(trans_type)
            type_item.setForeground(QColor(255, 0, 128) if trans_type == "هزینه" else QColor(0, 255, 170))
            self.transactions_table.setItem(idx, 4, type_item)
            
            self.transactions_table.setItem(idx, 5, QTableWidgetItem(transaction.description))
            
            # Delete button
            delete_btn = NeonButton("حذف")
            delete_btn.setColor(QColor(255, 0, 128))
            delete_btn.clicked.connect(lambda checked, trans_id=transaction.id: self.delete_transaction(trans_id))
            
            self.transactions_table.setCellWidget(idx, 6, delete_btn)
        
        # Populate recent transactions table (show only last 5)
        recent_count = min(5, len(transactions))
        for idx in range(recent_count):
            transaction = transactions[idx]
            self.recent_transactions_table.insertRow(idx)
            
            persian_date = gregorian_to_persian(transaction.date)
            
            self.recent_transactions_table.setItem(idx, 0, QTableWidgetItem(persian_date))
            self.recent_transactions_table.setItem(idx, 1, QTableWidgetItem(transaction.title))
            self.recent_transactions_table.setItem(idx, 2, QTableWidgetItem(transaction.category_name))
            
            amount_item = QTableWidgetItem(f"{transaction.amount:,} تومان")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.recent_transactions_table.setItem(idx, 3, amount_item)
            
            trans_type = "هزینه" if transaction.type == "expense" else "درآمد"
            type_item = QTableWidgetItem(trans_type)
            type_item.setForeground(QColor(255, 0, 128) if trans_type == "هزینه" else QColor(0, 255, 170))
            self.recent_transactions_table.setItem(idx, 4, type_item)
    
    def update_dashboard(self):
        """Update dashboard with current financial data"""
        # Get financial summary
        summary = self.finance_service.get_monthly_summary()
        
        # Update summary cards
        self.income_card.setValue(f"{summary['income']:,} تومان")
        self.expense_card.setValue(f"{summary['expense']:,} تومان")
        self.balance_card.setValue(f"{summary['income'] - summary['expense']:,} تومان")
        
        # Update category distribution chart
        category_data = self.finance_service.get_expense_by_category()
        self.category_chart.update_pie_chart(
            [c['category'] for c in category_data],
            [c['amount'] for c in category_data]
        )
        
        # Update income vs expense chart
        monthly_data = self.finance_service.get_monthly_comparison()
        
        months = [get_persian_month_name(m['month']) for m in monthly_data]
        income_values = [m['income'] for m in monthly_data]
        expense_values = [m['expense'] for m in monthly_data]
        
        self.income_expense_chart.update_bar_chart(
            months,
            [
                {'label': 'درآمد', 'data': income_values, 'color': 'rgba(0, 255, 170, 0.7)'},
                {'label': 'هزینه', 'data': expense_values, 'color': 'rgba(255, 0, 128, 0.7)'}
            ]
        )
    
    @pyqtSlot()
    def add_transaction(self):
        """Add a new transaction"""
        title = self.transaction_title.text().strip()
        amount = self.transaction_amount.value()
        
        if not title:
            QMessageBox.warning(self, "خطا", "لطفا عنوان تراکنش را وارد کنید.")
            return
            
        if amount <= 0:
            QMessageBox.warning(self, "خطا", "مبلغ تراکنش باید بیشتر از صفر باشد.")
            return
            
        if self.transaction_category.count() == 0:
            QMessageBox.warning(self, "خطا", "لطفا ابتدا یک دسته‌بندی ایجاد کنید.")
            return
        
        # Create transaction object
        transaction = Transaction(
            id=None,
            user_id=self.user.id,
            title=title,
            amount=amount,
            date=self.transaction_date.date().toPyDate(),
            type="expense" if self.transaction_type.currentText() == "هزینه" else "income",
            category_id=self.transaction_category.currentData(),
            category_name=self.transaction_category.currentText(),
            description=self.transaction_description.text()
        )
        
        # Add transaction
        try:
            self.finance_service.add_transaction(transaction)
            
            # Clear form
            self.transaction_title.clear()
            self.transaction_amount.setValue(0)
            self.transaction_description.clear()
            
            # Reload data
            self.load_transactions()
            self.update_dashboard()
            
            QMessageBox.information(self, "موفقیت", "تراکنش با موفقیت ثبت شد.")
        except Exception as e:
            logger.error(f"Error adding transaction: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در ثبت تراکنش: {str(e)}")
    
    @pyqtSlot()
    def add_category(self):
        """Add a new category"""
        name = self.category_name.text().strip()
        
        if not name:
            QMessageBox.warning(self, "خطا", "لطفا نام دسته‌بندی را وارد کنید.")
            return
        
        # Determine category type
        type_text = self.category_type.currentText()
        if type_text == "هزینه":
            category_type = "expense"
        elif type_text == "درآمد":
            category_type = "income"
        else:
            category_type = "both"
        
        # Create category object
        category = Category(
            id=None,
            user_id=self.user.id,
            name=name,
            type=category_type
        )
        
        # Add category
        try:
            self.finance_service.add_category(category)
            
            # Clear form
            self.category_name.clear()
            
            # Reload categories
            self.load_categories()
            
            QMessageBox.information(self, "موفقیت", "دسته‌بندی با موفقیت اضافه شد.")
        except Exception as e:
            logger.error(f"Error adding category: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در افزودن دسته‌بندی: {str(e)}")
    
    @pyqtSlot(int)
    def delete_transaction(self, transaction_id):
        """Delete a transaction"""
        reply = QMessageBox.question(
            self, "تأیید حذف", 
            "آیا از حذف این تراکنش اطمینان دارید؟", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.finance_service.delete_transaction(transaction_id)
                
                # Reload data
                self.load_transactions()
                self.update_dashboard()
                
                QMessageBox.information(self, "موفقیت", "تراکنش با موفقیت حذف شد.")
            except Exception as e:
                logger.error(f"Error deleting transaction: {str(e)}")
                QMessageBox.critical(self, "خطا", f"خطا در حذف تراکنش: {str(e)}")
    
    @pyqtSlot(int)
    def delete_category(self, category_id):
        """Delete a category"""
        reply = QMessageBox.question(
            self, "تأیید حذف", 
            "آیا از حذف این دسته‌بندی اطمینان دارید؟ تمام تراکنش‌های مرتبط نیز حذف خواهند شد.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.finance_service.delete_category(category_id)
                
                # Reload data
                self.load_categories()
                self.load_transactions()
                self.update_dashboard()
                
                QMessageBox.information(self, "موفقیت", "دسته‌بندی با موفقیت حذف شد.")
            except Exception as e:
                logger.error(f"Error deleting category: {str(e)}")
                QMessageBox.critical(self, "خطا", f"خطا در حذف دسته‌بندی: {str(e)}")
    
    @pyqtSlot()
    def apply_filters(self):
        """Apply filters to reports"""
        from_date = self.from_date.date().toPyDate()
        to_date = self.to_date.date().toPyDate()
        
        category_id = None
        if self.filter_category.currentIndex() > 0:
            category_id = self.filter_category.currentData()
        
        transaction_type = None
        if self.filter_type.currentIndex() > 0:
            transaction_type = "expense" if self.filter_type.currentText() == "هزینه" else "income"
        
        # Get filtered transactions
        transactions = self.finance_service.get_filtered_transactions(
            from_date=from_date,
            to_date=to_date,
            category_id=category_id,
            transaction_type=transaction_type
        )
        
        # Clear filtered table
        self.filtered_transactions_table.setRowCount(0)
        
        # Populate filtered table
        for idx, transaction in enumerate(transactions):
            self.filtered_transactions_table.insertRow(idx)
            
            persian_date = gregorian_to_persian(transaction.date)
            
            self.filtered_transactions_table.setItem(idx, 0, QTableWidgetItem(persian_date))
            self.filtered_transactions_table.setItem(idx, 1, QTableWidgetItem(transaction.title))
            self.filtered_transactions_table.setItem(idx, 2, QTableWidgetItem(transaction.category_name))
            
            amount_item = QTableWidgetItem(f"{transaction.amount:,} تومان")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.filtered_transactions_table.setItem(idx, 3, amount_item)
            
            trans_type = "هزینه" if transaction.type == "expense" else "درآمد"
            type_item = QTableWidgetItem(trans_type)
            type_item.setForeground(QColor(255, 0, 128) if trans_type == "هزینه" else QColor(0, 255, 170))
            self.filtered_transactions_table.setItem(idx, 4, type_item)
            
            self.filtered_transactions_table.setItem(idx, 5, QTableWidgetItem(transaction.description))
        
        # Update the charts in reports tab
        self.update_report_charts(from_date, to_date, category_id, transaction_type)
    
    def update_report_charts(self, from_date, to_date, category_id=None, transaction_type=None):
        """Update the charts in reports tab"""
        # Get daily trend data
        daily_data = self.finance_service.get_daily_trend(from_date, to_date, category_id, transaction_type)
        
        days = [gregorian_to_persian(d['date']) for d in daily_data]
        amounts = [d['amount'] for d in daily_data]
        
        self.daily_trend_chart.update_line_chart(
            days, 
            amounts,
            "روند هزینه‌ها",
            "rgba(255, 0, 128, 0.7)"
        )
        
        # Get monthly trend data
        monthly_data = self.finance_service.get_monthly_trend(from_date, to_date, category_id, transaction_type)
        
        months = [get_persian_month_name(m['month']) for m in monthly_data]
        income_values = [m.get('income', 0) for m in monthly_data]
        expense_values = [m.get('expense', 0) for m in monthly_data]
        
        self.monthly_trend_chart.update_bar_chart(
            months,
            [
                {'label': 'درآمد', 'data': income_values, 'color': 'rgba(0, 255, 170, 0.7)'},
                {'label': 'هزینه', 'data': expense_values, 'color': 'rgba(255, 0, 128, 0.7)'}
            ]
        )
