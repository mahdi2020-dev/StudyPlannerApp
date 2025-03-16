#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Finance service for Persian Life Manager Application
"""

import os
import logging
from datetime import datetime, timedelta
import calendar

from app.core.database import DatabaseManager
from app.models.finance import Category, Transaction, Budget, FinancialReport

logger = logging.getLogger(__name__)

class FinanceService:
    """Service for managing financial data"""
    
    def __init__(self, user_id, db_path=None):
        """Initialize the finance service
        
        Args:
            user_id (int): User ID
            db_path (str, optional): Path to the database file. If None, uses default path.
        """
        if not db_path:
            db_path = os.path.join(os.path.expanduser("~"), '.persian_life_manager', 'database.db')
        
        self.db_manager = DatabaseManager(db_path)
        self.user_id = user_id
    
    def get_categories(self, category_type=None):
        """Get categories for the user
        
        Args:
            category_type (str, optional): Filter by category type (expense, income, both)
            
        Returns:
            list: List of Category objects
        """
        try:
            if category_type:
                query = """
                    SELECT id, user_id, name, type
                    FROM finance_categories
                    WHERE user_id = ? AND (type = ? OR type = 'both')
                    ORDER BY name
                """
                results = self.db_manager.execute_query(query, (self.user_id, category_type))
            else:
                query = """
                    SELECT id, user_id, name, type
                    FROM finance_categories
                    WHERE user_id = ?
                    ORDER BY name
                """
                results = self.db_manager.execute_query(query, (self.user_id,))
            
            categories = []
            for row in results:
                category = Category(
                    id=row['id'],
                    user_id=row['user_id'],
                    name=row['name'],
                    type=row['type']
                )
                categories.append(category)
            
            return categories
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            return []
    
    def add_category(self, category):
        """Add a new category
        
        Args:
            category (Category): The category to add
            
        Returns:
            int: The ID of the new category, or None if adding failed
        """
        try:
            # Validate category type
            if category.type not in ['expense', 'income', 'both']:
                raise ValueError("Invalid category type. Must be 'expense', 'income', or 'both'.")
            
            # Check if category with same name already exists
            query = "SELECT id FROM finance_categories WHERE user_id = ? AND name = ?"
            results = self.db_manager.execute_query(query, (self.user_id, category.name))
            
            if results:
                raise ValueError(f"Category '{category.name}' already exists.")
            
            # Add the category
            query = """
                INSERT INTO finance_categories (user_id, name, type, created_at)
                VALUES (?, ?, ?, ?)
            """
            
            now = datetime.now().isoformat()
            category_id = self.db_manager.execute_insert(
                query, (self.user_id, category.name, category.type, now)
            )
            
            category.id = category_id
            return category_id
        except Exception as e:
            logger.error(f"Error adding category: {str(e)}")
            raise
    
    def update_category(self, category):
        """Update a category
        
        Args:
            category (Category): The category to update
            
        Returns:
            bool: True if update was successful
        """
        try:
            # Validate category type
            if category.type not in ['expense', 'income', 'both']:
                raise ValueError("Invalid category type. Must be 'expense', 'income', or 'both'.")
            
            # Check if category exists
            query = "SELECT id FROM finance_categories WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (category.id, self.user_id))
            
            if not results:
                raise ValueError(f"Category with ID {category.id} not found.")
            
            # Update the category
            query = """
                UPDATE finance_categories
                SET name = ?, type = ?
                WHERE id = ? AND user_id = ?
            """
            
            result = self.db_manager.execute_update(
                query, (category.name, category.type, category.id, self.user_id)
            )
            
            return result > 0
        except Exception as e:
            logger.error(f"Error updating category: {str(e)}")
            raise
    
    def delete_category(self, category_id):
        """Delete a category and its associated transactions
        
        Args:
            category_id (int): The category ID to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Check if category exists
            query = "SELECT id FROM finance_categories WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (category_id, self.user_id))
            
            if not results:
                raise ValueError(f"Category with ID {category_id} not found.")
            
            # Delete associated transactions
            query = "DELETE FROM finance_transactions WHERE category_id = ? AND user_id = ?"
            self.db_manager.execute_update(query, (category_id, self.user_id))
            
            # Delete the category
            query = "DELETE FROM finance_categories WHERE id = ? AND user_id = ?"
            result = self.db_manager.execute_update(query, (category_id, self.user_id))
            
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting category: {str(e)}")
            raise
    
    def get_transactions(self, limit=None, offset=0):
        """Get transactions for the user
        
        Args:
            limit (int, optional): Maximum number of transactions to return
            offset (int, optional): Offset for pagination
            
        Returns:
            list: List of Transaction objects
        """
        try:
            query = """
                SELECT t.id, t.user_id, t.category_id, t.title, t.amount, t.type, 
                       t.date, t.description, c.name as category_name
                FROM finance_transactions t
                JOIN finance_categories c ON t.category_id = c.id
                WHERE t.user_id = ?
                ORDER BY t.date DESC, t.id DESC
            """
            
            if limit:
                query += " LIMIT ? OFFSET ?"
                results = self.db_manager.execute_query(query, (self.user_id, limit, offset))
            else:
                results = self.db_manager.execute_query(query, (self.user_id,))
            
            transactions = []
            for row in results:
                transaction = Transaction(
                    id=row['id'],
                    user_id=row['user_id'],
                    title=row['title'],
                    amount=row['amount'],
                    date=row['date'],
                    type=row['type'],
                    category_id=row['category_id'],
                    category_name=row['category_name'],
                    description=row['description']
                )
                transactions.append(transaction)
            
            return transactions
        except Exception as e:
            logger.error(f"Error getting transactions: {str(e)}")
            return []
    
    def add_transaction(self, transaction):
        """Add a new transaction
        
        Args:
            transaction (Transaction): The transaction to add
            
        Returns:
            int: The ID of the new transaction, or None if adding failed
        """
        try:
            # Validate transaction type
            if transaction.type not in ['expense', 'income']:
                raise ValueError("Invalid transaction type. Must be 'expense' or 'income'.")
            
            # Validate amount
            if transaction.amount <= 0:
                raise ValueError("Transaction amount must be positive.")
            
            # Check if category exists
            query = "SELECT id, type FROM finance_categories WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (transaction.category_id, self.user_id))
            
            if not results:
                raise ValueError(f"Category with ID {transaction.category_id} not found.")
            
            # Check if category type matches transaction type
            category_type = results[0]['type']
            if category_type != 'both' and category_type != transaction.type:
                raise ValueError(f"Category type '{category_type}' does not match transaction type '{transaction.type}'.")
            
            # Add the transaction
            query = """
                INSERT INTO finance_transactions (
                    user_id, category_id, title, amount, type, date, description, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            now = datetime.now().isoformat()
            transaction_id = self.db_manager.execute_insert(
                query, (
                    self.user_id, transaction.category_id, transaction.title,
                    transaction.amount, transaction.type, transaction.date,
                    transaction.description, now
                )
            )
            
            transaction.id = transaction_id
            return transaction_id
        except Exception as e:
            logger.error(f"Error adding transaction: {str(e)}")
            raise
    
    def update_transaction(self, transaction):
        """Update a transaction
        
        Args:
            transaction (Transaction): The transaction to update
            
        Returns:
            bool: True if update was successful
        """
        try:
            # Validate transaction type
            if transaction.type not in ['expense', 'income']:
                raise ValueError("Invalid transaction type. Must be 'expense' or 'income'.")
            
            # Validate amount
            if transaction.amount <= 0:
                raise ValueError("Transaction amount must be positive.")
            
            # Check if transaction exists
            query = "SELECT id FROM finance_transactions WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (transaction.id, self.user_id))
            
            if not results:
                raise ValueError(f"Transaction with ID {transaction.id} not found.")
            
            # Check if category exists
            query = "SELECT id, type FROM finance_categories WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (transaction.category_id, self.user_id))
            
            if not results:
                raise ValueError(f"Category with ID {transaction.category_id} not found.")
            
            # Check if category type matches transaction type
            category_type = results[0]['type']
            if category_type != 'both' and category_type != transaction.type:
                raise ValueError(f"Category type '{category_type}' does not match transaction type '{transaction.type}'.")
            
            # Update the transaction
            query = """
                UPDATE finance_transactions
                SET category_id = ?, title = ?, amount = ?, type = ?, date = ?, description = ?
                WHERE id = ? AND user_id = ?
            """
            
            result = self.db_manager.execute_update(
                query, (
                    transaction.category_id, transaction.title, transaction.amount,
                    transaction.type, transaction.date, transaction.description,
                    transaction.id, self.user_id
                )
            )
            
            return result > 0
        except Exception as e:
            logger.error(f"Error updating transaction: {str(e)}")
            raise
    
    def delete_transaction(self, transaction_id):
        """Delete a transaction
        
        Args:
            transaction_id (int): The transaction ID to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Check if transaction exists
            query = "SELECT id FROM finance_transactions WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (transaction_id, self.user_id))
            
            if not results:
                raise ValueError(f"Transaction with ID {transaction_id} not found.")
            
            # Delete the transaction
            query = "DELETE FROM finance_transactions WHERE id = ? AND user_id = ?"
            result = self.db_manager.execute_update(query, (transaction_id, self.user_id))
            
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting transaction: {str(e)}")
            raise
    
    def get_filtered_transactions(self, from_date=None, to_date=None, category_id=None, transaction_type=None):
        """Get filtered transactions
        
        Args:
            from_date (str, optional): Start date (YYYY-MM-DD)
            to_date (str, optional): End date (YYYY-MM-DD)
            category_id (int, optional): Filter by category ID
            transaction_type (str, optional): Filter by transaction type (expense or income)
            
        Returns:
            list: List of Transaction objects
        """
        try:
            query_parts = [
                """
                SELECT t.id, t.user_id, t.category_id, t.title, t.amount, t.type, 
                       t.date, t.description, c.name as category_name
                FROM finance_transactions t
                JOIN finance_categories c ON t.category_id = c.id
                WHERE t.user_id = ?
                """
            ]
            params = [self.user_id]
            
            if from_date:
                query_parts.append("AND t.date >= ?")
                params.append(from_date)
            
            if to_date:
                query_parts.append("AND t.date <= ?")
                params.append(to_date)
            
            if category_id:
                query_parts.append("AND t.category_id = ?")
                params.append(category_id)
            
            if transaction_type:
                query_parts.append("AND t.type = ?")
                params.append(transaction_type)
            
            query_parts.append("ORDER BY t.date DESC, t.id DESC")
            
            query = " ".join(query_parts)
            results = self.db_manager.execute_query(query, tuple(params))
            
            transactions = []
            for row in results:
                transaction = Transaction(
                    id=row['id'],
                    user_id=row['user_id'],
                    title=row['title'],
                    amount=row['amount'],
                    date=row['date'],
                    type=row['type'],
                    category_id=row['category_id'],
                    category_name=row['category_name'],
                    description=row['description']
                )
                transactions.append(transaction)
            
            return transactions
        except Exception as e:
            logger.error(f"Error getting filtered transactions: {str(e)}")
            return []
    
    def get_balance(self):
        """Get the current balance (income - expenses)
        
        Returns:
            dict: Dictionary with total_income, total_expenses, and balance
        """
        try:
            # Get total income
            query = """
                SELECT SUM(amount) as total
                FROM finance_transactions
                WHERE user_id = ? AND type = 'income'
            """
            income_result = self.db_manager.execute_query(query, (self.user_id,))
            total_income = income_result[0]['total'] if income_result[0]['total'] else 0
            
            # Get total expenses
            query = """
                SELECT SUM(amount) as total
                FROM finance_transactions
                WHERE user_id = ? AND type = 'expense'
            """
            expense_result = self.db_manager.execute_query(query, (self.user_id,))
            total_expenses = expense_result[0]['total'] if expense_result[0]['total'] else 0
            
            # Calculate balance
            balance = total_income - total_expenses
            
            return {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'balance': balance
            }
        except Exception as e:
            logger.error(f"Error getting balance: {str(e)}")
            return {
                'total_income': 0,
                'total_expenses': 0,
                'balance': 0
            }
    
    def get_monthly_summary(self):
        """Get summary of income and expenses for the current month
        
        Returns:
            dict: Dictionary with income and expense totals
        """
        try:
            # Get current month date range
            today = datetime.now()
            first_day = today.replace(day=1).strftime("%Y-%m-%d")
            
            # Get last day of month
            if today.month == 12:
                last_day = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            
            last_day = last_day.strftime("%Y-%m-%d")
            
            # Query for income
            income_query = """
                SELECT SUM(amount) as total
                FROM finance_transactions
                WHERE user_id = ? AND type = 'income' AND date BETWEEN ? AND ?
            """
            income_result = self.db_manager.execute_query(income_query, (self.user_id, first_day, last_day))
            
            # Query for expenses
            expense_query = """
                SELECT SUM(amount) as total
                FROM finance_transactions
                WHERE user_id = ? AND type = 'expense' AND date BETWEEN ? AND ?
            """
            expense_result = self.db_manager.execute_query(expense_query, (self.user_id, first_day, last_day))
            
            # Get totals
            income_total = income_result[0]['total'] if income_result[0]['total'] else 0
            expense_total = expense_result[0]['total'] if expense_result[0]['total'] else 0
            
            return {
                'income': income_total,
                'expense': expense_total
            }
        except Exception as e:
            logger.error(f"Error getting monthly summary: {str(e)}")
            return {'income': 0, 'expense': 0}
    
    def get_expense_by_category(self, period='month'):
        """Get expenses grouped by category
        
        Args:
            period (str, optional): Time period ('month', 'year', 'week')
            
        Returns:
            list: List of dictionaries with category and amount
        """
        try:
            # Determine date range based on period
            today = datetime.now()
            
            if period == 'week':
                # Start of the week (considering Monday as the first day)
                start_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
            elif period == 'month':
                # Start of the month
                start_date = today.replace(day=1).strftime("%Y-%m-%d")
            elif period == 'year':
                # Start of the year
                start_date = today.replace(month=1, day=1).strftime("%Y-%m-%d")
            else:
                raise ValueError(f"Invalid period: {period}")
            
            end_date = today.strftime("%Y-%m-%d")
            
            # Query for expenses by category
            query = """
                SELECT c.name as category, SUM(t.amount) as amount
                FROM finance_transactions t
                JOIN finance_categories c ON t.category_id = c.id
                WHERE t.user_id = ? AND t.type = 'expense' AND t.date BETWEEN ? AND ?
                GROUP BY t.category_id
                ORDER BY amount DESC
            """
            
            results = self.db_manager.execute_query(query, (self.user_id, start_date, end_date))
            
            # Format results
            categories = []
            for row in results:
                categories.append({
                    'category': row['category'],
                    'amount': row['amount']
                })
            
            return categories
        except Exception as e:
            logger.error(f"Error getting expenses by category: {str(e)}")
            return []
    
    def get_monthly_comparison(self, months=6):
        """Get monthly comparison of income and expenses
        
        Args:
            months (int, optional): Number of months to include
            
        Returns:
            list: List of dictionaries with month, income, and expense
        """
        try:
            # Generate list of months
            today = datetime.now()
            months_data = []
            
            for i in range(months - 1, -1, -1):
                # Calculate month
                if today.month - i <= 0:
                    year = today.year - 1
                    month = today.month - i + 12
                else:
                    year = today.year
                    month = today.month - i
                
                # Get first and last day of month
                first_day = datetime(year, month, 1).strftime("%Y-%m-%d")
                
                # Get last day of month
                if month == 12:
                    last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    last_day = datetime(year, month + 1, 1) - timedelta(days=1)
                
                last_day = last_day.strftime("%Y-%m-%d")
                
                # Query for income
                income_query = """
                    SELECT SUM(amount) as total
                    FROM finance_transactions
                    WHERE user_id = ? AND type = 'income' AND date BETWEEN ? AND ?
                """
                income_result = self.db_manager.execute_query(income_query, (self.user_id, first_day, last_day))
                
                # Query for expenses
                expense_query = """
                    SELECT SUM(amount) as total
                    FROM finance_transactions
                    WHERE user_id = ? AND type = 'expense' AND date BETWEEN ? AND ?
                """
                expense_result = self.db_manager.execute_query(expense_query, (self.user_id, first_day, last_day))
                
                # Get totals
                income_total = income_result[0]['total'] if income_result[0]['total'] else 0
                expense_total = expense_result[0]['total'] if expense_result[0]['total'] else 0
                
                # Add to results
                months_data.append({
                    'month': month,
                    'income': income_total,
                    'expense': expense_total
                })
            
            return months_data
        except Exception as e:
            logger.error(f"Error getting monthly comparison: {str(e)}")
            return []
    
    def get_daily_trend(self, from_date, to_date, category_id=None, transaction_type=None):
        """Get daily trend of transactions between dates
        
        Args:
            from_date (str): Start date (YYYY-MM-DD)
            to_date (str): End date (YYYY-MM-DD)
            category_id (int, optional): Filter by category ID
            transaction_type (str, optional): Filter by transaction type (expense or income)
            
        Returns:
            list: List of dictionaries with date and amount
        """
        try:
            query_parts = [
                """
                SELECT date, SUM(amount) as amount
                FROM finance_transactions
                WHERE user_id = ? AND date BETWEEN ? AND ?
                """
            ]
            params = [self.user_id, from_date, to_date]
            
            if category_id:
                query_parts.append("AND category_id = ?")
                params.append(category_id)
            
            if transaction_type:
                query_parts.append("AND type = ?")
                params.append(transaction_type)
            
            query_parts.append("GROUP BY date ORDER BY date")
            
            query = " ".join(query_parts)
            results = self.db_manager.execute_query(query, tuple(params))
            
            # Format results
            daily_data = []
            for row in results:
                daily_data.append({
                    'date': row['date'],
                    'amount': row['amount']
                })
            
            return daily_data
        except Exception as e:
            logger.error(f"Error getting daily trend: {str(e)}")
            return []
    
    def get_monthly_trend(self, from_date, to_date, category_id=None, transaction_type=None):
        """Get monthly trend between dates, split by income and expense
        
        Args:
            from_date (str): Start date (YYYY-MM-DD)
            to_date (str): End date (YYYY-MM-DD)
            category_id (int, optional): Filter by category ID
            transaction_type (str, optional): Filter by transaction type (expense or income)
            
        Returns:
            list: List of dictionaries with month, year, income, and expense
        """
        try:
            # Convert dates to datetime objects
            from_datetime = datetime.strptime(from_date, "%Y-%m-%d")
            to_datetime = datetime.strptime(to_date, "%Y-%m-%d")
            
            # Generate list of months between dates
            months_data = []
            current_date = from_datetime.replace(day=1)
            
            while current_date <= to_datetime:
                year = current_date.year
                month = current_date.month
                
                # Get first and last day of month
                first_day = current_date.strftime("%Y-%m-%d")
                
                # Get last day of month
                if month == 12:
                    last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    last_day = datetime(year, month + 1, 1) - timedelta(days=1)
                
                last_day = min(last_day, to_datetime).strftime("%Y-%m-%d")
                
                # Base query parts
                base_query_parts = [
                    """
                    SELECT SUM(amount) as total
                    FROM finance_transactions
                    WHERE user_id = ? AND date BETWEEN ? AND ?
                    """
                ]
                base_params = [self.user_id, first_day, last_day]
                
                if category_id:
                    base_query_parts.append("AND category_id = ?")
                    base_params.append(category_id)
                
                # Query for income
                if not transaction_type or transaction_type == 'income':
                    income_query_parts = base_query_parts.copy()
                    income_params = base_params.copy()
                    
                    income_query_parts.append("AND type = 'income'")
                    
                    income_query = " ".join(income_query_parts)
                    income_result = self.db_manager.execute_query(income_query, tuple(income_params))
                    income_total = income_result[0]['total'] if income_result[0]['total'] else 0
                else:
                    income_total = 0
                
                # Query for expenses
                if not transaction_type or transaction_type == 'expense':
                    expense_query_parts = base_query_parts.copy()
                    expense_params = base_params.copy()
                    
                    expense_query_parts.append("AND type = 'expense'")
                    
                    expense_query = " ".join(expense_query_parts)
                    expense_result = self.db_manager.execute_query(expense_query, tuple(expense_params))
                    expense_total = expense_result[0]['total'] if expense_result[0]['total'] else 0
                else:
                    expense_total = 0
                
                # Add to results
                months_data.append({
                    'year': year,
                    'month': month,
                    'income': income_total,
                    'expense': expense_total
                })
                
                # Move to next month
                if month == 12:
                    current_date = current_date.replace(year=year + 1, month=1)
                else:
                    current_date = current_date.replace(month=month + 1)
            
            return months_data
        except Exception as e:
            logger.error(f"Error getting monthly trend: {str(e)}")
            return []
