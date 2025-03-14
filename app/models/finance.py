#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Finance-related data models for Persian Life Manager Application
"""

class Category:
    """Financial category model"""
    
    def __init__(self, id, user_id, name, type):
        """Initialize a financial category
        
        Args:
            id (int): Category ID (None for new categories)
            user_id (int): User ID
            name (str): Category name
            type (str): Category type (expense, income, or both)
        """
        self.id = id
        self.user_id = user_id
        self.name = name
        self.type = type  # 'expense', 'income', or 'both'
    
    def __str__(self):
        return f"Category({self.id}, {self.name}, {self.type})"


class Transaction:
    """Financial transaction model"""
    
    def __init__(self, id, user_id, title, amount, date, type, category_id, category_name=None, description=None):
        """Initialize a financial transaction
        
        Args:
            id (int): Transaction ID (None for new transactions)
            user_id (int): User ID
            title (str): Transaction title
            amount (float): Transaction amount
            date (str): Transaction date (YYYY-MM-DD)
            type (str): Transaction type (expense or income)
            category_id (int): Category ID
            category_name (str, optional): Category name for display purposes
            description (str, optional): Transaction description
        """
        self.id = id
        self.user_id = user_id
        self.title = title
        self.amount = amount
        self.date = date
        self.type = type  # 'expense' or 'income'
        self.category_id = category_id
        self.category_name = category_name
        self.description = description or ""
    
    def __str__(self):
        return f"Transaction({self.id}, {self.title}, {self.amount}, {self.date}, {self.type})"


class Budget:
    """Budget model"""
    
    def __init__(self, id, user_id, category_id, amount, period, start_date, end_date=None):
        """Initialize a budget
        
        Args:
            id (int): Budget ID (None for new budgets)
            user_id (int): User ID
            category_id (int): Category ID (or None for overall budget)
            amount (float): Budget amount
            period (str): Budget period (monthly, weekly, etc.)
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str, optional): End date (YYYY-MM-DD)
        """
        self.id = id
        self.user_id = user_id
        self.category_id = category_id
        self.amount = amount
        self.period = period  # 'monthly', 'weekly', 'yearly', etc.
        self.start_date = start_date
        self.end_date = end_date
    
    def __str__(self):
        return f"Budget({self.id}, {self.amount}, {self.period}, {self.start_date}, {self.end_date})"


class FinancialReport:
    """Financial report model"""
    
    def __init__(self, report_type, period, data):
        """Initialize a financial report
        
        Args:
            report_type (str): Report type (expense, income, comparison, etc.)
            period (str): Report period (daily, weekly, monthly, yearly)
            data (dict): Report data
        """
        self.report_type = report_type
        self.period = period
        self.data = data
    
    def __str__(self):
        return f"FinancialReport({self.report_type}, {self.period})"
