"""
Data adapter for transitioning between SQLite and Firebase
"""

import os
import logging
from datetime import datetime
import json

from app.firebase_config import FirebaseManager
from app.core.database import DatabaseManager
from pathlib import Path

logger = logging.getLogger(__name__)

class DataAdapter:
    """Adapter to handle data operations between SQLite and Firebase"""
    
    def __init__(self, user_id=None):
        """Initialize the data adapter
        
        Args:
            user_id (int or str, optional): User ID
        """
        # Initialize Firebase connection
        self.firebase = FirebaseManager()
        
        # Initialize SQLite connection (legacy system)
        db_path = os.path.join(Path.home(), '.persian_life_manager', 'database.db')
        self.db_manager = DatabaseManager(db_path)
        
        self.user_id = user_id
        self.use_firebase = self.firebase.is_initialized()
        
        if self.use_firebase:
            logger.info("Using Firebase for data storage")
        else:
            logger.info("Using SQLite for data storage (Firebase not initialized)")
    
    def set_user_id(self, user_id):
        """Set the current user ID
        
        Args:
            user_id (int or str): User ID
        """
        self.user_id = user_id
    
    # ================ User Settings Methods ================
    
    def get_user_settings(self, user_id=None):
        """Get user settings
        
        Args:
            user_id (int or str, optional): User ID. If None, uses the current user_id.
            
        Returns:
            dict: User settings
        """
        user_id = user_id or self.user_id
        if not user_id:
            return {}
            
        if self.use_firebase:
            try:
                settings = self.firebase.get_user_data(user_id, "settings")
                return settings or {}
            except Exception as e:
                logger.error(f"Error getting user settings from Firebase: {str(e)}")
                # Fall back to SQLite
                
        # Get from SQLite
        try:
            query = "SELECT settings FROM user_settings WHERE user_id = ?"
            results = self.db_manager.execute_query(query, (user_id,))
            if results:
                return json.loads(results[0][0])
            return {}
        except Exception as e:
            logger.error(f"Error getting user settings from SQLite: {str(e)}")
            return {}
    
    def save_user_settings(self, settings, user_id=None):
        """Save user settings
        
        Args:
            settings (dict): User settings
            user_id (int or str, optional): User ID. If None, uses the current user_id.
            
        Returns:
            bool: Success status
        """
        user_id = user_id or self.user_id
        if not user_id:
            return False
            
        # Save to both Firebase and SQLite to ensure data consistency during migration
        success = True
        
        if self.use_firebase:
            try:
                # Add to Firebase
                firebase_success = self.firebase.add_user_data(user_id, "settings", settings)
                if not firebase_success:
                    logger.error("Failed to save user settings to Firebase")
                    success = False
            except Exception as e:
                logger.error(f"Error saving user settings to Firebase: {str(e)}")
                success = False
        
        # Save to SQLite as well
        try:
            settings_json = json.dumps(settings)
            query = """
                INSERT INTO user_settings (user_id, settings) 
                VALUES (?, ?) 
                ON CONFLICT(user_id) DO UPDATE SET settings = ?
            """
            self.db_manager.execute_update(query, (user_id, settings_json, settings_json))
        except Exception as e:
            logger.error(f"Error saving user settings to SQLite: {str(e)}")
            success = False
            
        return success
    
    # ================ Financial Data Methods ================
    
    def get_categories(self, category_type=None, user_id=None):
        """Get financial categories
        
        Args:
            category_type (str, optional): Filter by category type (expense, income, both)
            user_id (int or str, optional): User ID. If None, uses the current user_id.
            
        Returns:
            list: List of categories
        """
        user_id = user_id or self.user_id
        if not user_id:
            return []
            
        if self.use_firebase:
            try:
                # Get from Firebase
                categories_data = self.firebase.get_user_data(user_id, "finance_categories")
                if categories_data and "categories" in categories_data:
                    categories = categories_data["categories"]
                    
                    # Filter by type if needed
                    if category_type:
                        return [cat for cat in categories if cat["type"] == category_type]
                    return categories
            except Exception as e:
                logger.error(f"Error getting categories from Firebase: {str(e)}")
                # Fall back to SQLite
        
        # Get from SQLite
        try:
            query = "SELECT id, name, type FROM finance_categories WHERE user_id = ?"
            params = (user_id,)
            
            if category_type:
                query += " AND type = ?"
                params = (user_id, category_type)
                
            results = self.db_manager.execute_query(query, params)
            
            categories = []
            for row in results:
                categories.append({
                    "id": row[0],
                    "name": row[1],
                    "type": row[2]
                })
            
            return categories
        except Exception as e:
            logger.error(f"Error getting categories from SQLite: {str(e)}")
            return []
    
    def add_category(self, name, category_type, user_id=None):
        """Add a new category
        
        Args:
            name (str): Category name
            category_type (str): Category type (expense, income, both)
            user_id (int or str, optional): User ID. If None, uses the current user_id.
            
        Returns:
            int or str: The ID of the new category, or None if adding failed
        """
        user_id = user_id or self.user_id
        if not user_id:
            return None
            
        category_id = None
        
        # Add to SQLite first to get an ID
        try:
            query = "INSERT INTO finance_categories (user_id, name, type) VALUES (?, ?, ?)"
            category_id = self.db_manager.execute_insert(query, (user_id, name, category_type))
        except Exception as e:
            logger.error(f"Error adding category to SQLite: {str(e)}")
            return None
            
        if self.use_firebase and category_id:
            try:
                # Get existing categories
                categories_data = self.firebase.get_user_data(user_id, "finance_categories") or {}
                categories = categories_data.get("categories", [])
                
                # Add new category
                categories.append({
                    "id": str(category_id),
                    "name": name,
                    "type": category_type
                })
                
                # Update categories in Firebase
                self.firebase.add_user_data(user_id, "finance_categories", {"categories": categories})
            except Exception as e:
                logger.error(f"Error adding category to Firebase: {str(e)}")
                
        return category_id
    
    def get_transactions(self, limit=None, user_id=None):
        """Get financial transactions
        
        Args:
            limit (int, optional): Maximum number of transactions to return
            user_id (int or str, optional): User ID. If None, uses the current user_id.
            
        Returns:
            list: List of transactions
        """
        user_id = user_id or self.user_id
        if not user_id:
            return []
            
        if self.use_firebase:
            try:
                # Get from Firebase
                fb_limit = limit or 50  # Default limit for Firebase
                transactions = self.firebase.get_transactions(user_id, fb_limit)
                if transactions:
                    return transactions
            except Exception as e:
                logger.error(f"Error getting transactions from Firebase: {str(e)}")
                # Fall back to SQLite
        
        # Get from SQLite
        try:
            query = """
                SELECT t.id, t.title, t.amount, t.date, t.type, t.category_id, c.name 
                FROM finance_transactions t
                LEFT JOIN finance_categories c ON t.category_id = c.id
                WHERE t.user_id = ?
                ORDER BY t.date DESC
            """
            params = (user_id,)
            
            if limit:
                query += " LIMIT ?"
                params = (user_id, limit)
                
            results = self.db_manager.execute_query(query, params)
            
            transactions = []
            for row in results:
                transactions.append({
                    "id": row[0],
                    "title": row[1],
                    "amount": row[2],
                    "date": row[3],
                    "type": row[4],
                    "category_id": row[5],
                    "category_name": row[6]
                })
            
            return transactions
        except Exception as e:
            logger.error(f"Error getting transactions from SQLite: {str(e)}")
            return []
    
    def add_transaction(self, title, amount, date, transaction_type, category_id, description=None, user_id=None):
        """Add a new transaction
        
        Args:
            title (str): Transaction title
            amount (float): Transaction amount
            date (str): Transaction date (YYYY-MM-DD)
            transaction_type (str): Transaction type (expense or income)
            category_id (int): Category ID
            description (str, optional): Transaction description
            user_id (int or str, optional): User ID. If None, uses the current user_id.
            
        Returns:
            int or str: The ID of the new transaction, or None if adding failed
        """
        user_id = user_id or self.user_id
        if not user_id:
            return None
            
        transaction_id = None
        
        # Add to SQLite first to get an ID
        try:
            query = """
                INSERT INTO finance_transactions 
                (user_id, title, amount, date, type, category_id, description) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            transaction_id = self.db_manager.execute_insert(
                query, (user_id, title, amount, date, transaction_type, category_id, description)
            )
        except Exception as e:
            logger.error(f"Error adding transaction to SQLite: {str(e)}")
            return None
            
        if self.use_firebase and transaction_id:
            try:
                # Get category name
                category_name = ""
                query = "SELECT name FROM finance_categories WHERE id = ?"
                results = self.db_manager.execute_query(query, (category_id,))
                if results:
                    category_name = results[0][0]
                
                # Add to Firebase
                transaction_data = {
                    "title": title,
                    "amount": amount,
                    "date": date,
                    "type": transaction_type,
                    "category_id": category_id,
                    "category_name": category_name,
                    "description": description
                }
                self.firebase.add_transaction(user_id, transaction_data)
            except Exception as e:
                logger.error(f"Error adding transaction to Firebase: {str(e)}")
                
        return transaction_id
    
    # ================ Health Data Methods ================
    
    def get_health_metrics(self, limit=None, user_id=None):
        """Get health metrics
        
        Args:
            limit (int, optional): Maximum number of metrics to return
            user_id (int or str, optional): User ID. If None, uses the current user_id.
            
        Returns:
            list: List of health metrics
        """
        user_id = user_id or self.user_id
        if not user_id:
            return []
            
        if self.use_firebase:
            try:
                # Get from Firebase
                fb_limit = limit or 50  # Default limit for Firebase
                metrics = self.firebase.get_health_metrics(user_id, fb_limit)
                if metrics:
                    return metrics
            except Exception as e:
                logger.error(f"Error getting health metrics from Firebase: {str(e)}")
                # Fall back to SQLite
        
        # Get from SQLite
        try:
            query = """
                SELECT id, date, weight, systolic, diastolic, heart_rate, sleep_hours, notes
                FROM health_metrics
                WHERE user_id = ?
                ORDER BY date DESC
            """
            params = (user_id,)
            
            if limit:
                query += " LIMIT ?"
                params = (user_id, limit)
                
            results = self.db_manager.execute_query(query, params)
            
            metrics = []
            for row in results:
                metrics.append({
                    "id": row[0],
                    "date": row[1],
                    "weight": row[2],
                    "systolic": row[3],
                    "diastolic": row[4],
                    "heart_rate": row[5],
                    "sleep_hours": row[6],
                    "notes": row[7]
                })
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting health metrics from SQLite: {str(e)}")
            return []
    
    def add_health_metric(self, date, weight=None, systolic=None, diastolic=None, 
                         heart_rate=None, sleep_hours=None, notes=None, user_id=None):
        """Add health metrics
        
        Args:
            date (str): Measurement date (YYYY-MM-DD)
            weight (float, optional): Weight in kg
            systolic (int, optional): Systolic blood pressure
            diastolic (int, optional): Diastolic blood pressure
            heart_rate (int, optional): Heart rate (bpm)
            sleep_hours (float, optional): Hours of sleep
            notes (str, optional): Notes about the measurements
            user_id (int or str, optional): User ID. If None, uses the current user_id.
            
        Returns:
            int or str: The ID of the new metrics, or None if adding failed
        """
        user_id = user_id or self.user_id
        if not user_id:
            return None
            
        metric_id = None
        
        # Add to SQLite first to get an ID
        try:
            query = """
                INSERT INTO health_metrics 
                (user_id, date, weight, systolic, diastolic, heart_rate, sleep_hours, notes) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            metric_id = self.db_manager.execute_insert(
                query, (user_id, date, weight, systolic, diastolic, heart_rate, sleep_hours, notes)
            )
        except Exception as e:
            logger.error(f"Error adding health metric to SQLite: {str(e)}")
            return None
            
        if self.use_firebase and metric_id:
            try:
                # Add to Firebase
                metric_data = {
                    "date": date,
                    "weight": weight,
                    "systolic": systolic,
                    "diastolic": diastolic,
                    "heart_rate": heart_rate,
                    "sleep_hours": sleep_hours,
                    "notes": notes
                }
                self.firebase.add_health_metric(user_id, metric_data)
            except Exception as e:
                logger.error(f"Error adding health metric to Firebase: {str(e)}")
                
        return metric_id
    
    # ================ Calendar Data Methods ================
    
    def get_calendar_events(self, limit=None, user_id=None):
        """Get calendar events
        
        Args:
            limit (int, optional): Maximum number of events to return
            user_id (int or str, optional): User ID. If None, uses the current user_id.
            
        Returns:
            list: List of calendar events
        """
        user_id = user_id or self.user_id
        if not user_id:
            return []
            
        if self.use_firebase:
            try:
                # Get from Firebase
                fb_limit = limit or 50  # Default limit for Firebase
                events = self.firebase.get_calendar_events(user_id, fb_limit)
                if events:
                    return events
            except Exception as e:
                logger.error(f"Error getting calendar events from Firebase: {str(e)}")
                # Fall back to SQLite
        
        # Get from SQLite
        try:
            query = """
                SELECT id, title, date, start_time, end_time, location, description, all_day
                FROM calendar_events
                WHERE user_id = ?
                ORDER BY date DESC
            """
            params = (user_id,)
            
            if limit:
                query += " LIMIT ?"
                params = (user_id, limit)
                
            results = self.db_manager.execute_query(query, params)
            
            events = []
            for row in results:
                events.append({
                    "id": row[0],
                    "title": row[1],
                    "date": row[2],
                    "start_time": row[3],
                    "end_time": row[4],
                    "location": row[5],
                    "description": row[6],
                    "all_day": bool(row[7])
                })
            
            return events
        except Exception as e:
            logger.error(f"Error getting calendar events from SQLite: {str(e)}")
            return []
    
    def add_calendar_event(self, title, date, start_time=None, end_time=None, 
                         location=None, description=None, all_day=False, user_id=None):
        """Add a calendar event
        
        Args:
            title (str): Event title
            date (str): Event date (YYYY-MM-DD)
            start_time (str, optional): Start time (HH:MM)
            end_time (str, optional): End time (HH:MM)
            location (str, optional): Event location
            description (str, optional): Event description
            all_day (bool, optional): Whether the event is all-day
            user_id (int or str, optional): User ID. If None, uses the current user_id.
            
        Returns:
            int or str: The ID of the new event, or None if adding failed
        """
        user_id = user_id or self.user_id
        if not user_id:
            return None
            
        event_id = None
        
        # Add to SQLite first to get an ID
        try:
            query = """
                INSERT INTO calendar_events 
                (user_id, title, date, start_time, end_time, location, description, all_day) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            event_id = self.db_manager.execute_insert(
                query, (user_id, title, date, start_time, end_time, location, description, all_day)
            )
        except Exception as e:
            logger.error(f"Error adding calendar event to SQLite: {str(e)}")
            return None
            
        if self.use_firebase and event_id:
            try:
                # Add to Firebase
                event_data = {
                    "title": title,
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "location": location,
                    "description": description,
                    "all_day": all_day
                }
                self.firebase.add_calendar_event(user_id, event_data)
            except Exception as e:
                logger.error(f"Error adding calendar event to Firebase: {str(e)}")
                
        return event_id