"""
Firebase Adapter for Persian Life Manager Application
Provides compatibility layer between existing SQLite implementation and Firebase
"""

import os
import logging
import json
from datetime import datetime

# Firebase dependencies
try:
    from app.firebase_config import FirebaseManager
    firebase_available = True
except ImportError:
    firebase_available = False

# Local dependencies
from app.models.user import User
from app.models.finance import Transaction, Category
from app.models.health import Exercise, HealthMetric, HealthGoal
from app.models.calendar import Event, Task, Reminder
from app.core.auth import AuthService
from app.utils.date_utils import get_current_persian_date, gregorian_to_persian, persian_to_gregorian

logger = logging.getLogger(__name__)

class FirebaseAdapter:
    """Adapter for Firebase integration with existing SQLite implementation"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one adapter instance"""
        if cls._instance is None:
            cls._instance = super(FirebaseAdapter, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        """Initialize the Firebase adapter"""
        self.enabled = False
        
        # Check if Firebase is available and initialized
        try:
            self.firebase = FirebaseManager()
            self.enabled = self.firebase.is_initialized()
            if self.enabled:
                logger.info("Firebase adapter initialized successfully")
            else:
                logger.warning("Firebase manager initialized but not fully enabled")
        except Exception as e:
            logger.error(f"Error initializing Firebase adapter: {str(e)}")
            self.firebase = None
        
        # Keep track of which data has been migrated
        self.migration_status = {
            "users": False,
            "finance": False,
            "health": False,
            "calendar": False
        }
        
        # Initialize auth service for user data
        self.auth_service = AuthService()
    
    # ================ User Management ================
    
    def migrate_users(self):
        """Migrate users from SQLite to Firebase"""
        if not self.enabled:
            logger.warning("Firebase not enabled, skipping user migration")
            return False
        
        try:
            # Get all users from SQLite
            connection = self.auth_service._get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT id, username, password_hash, salt FROM users")
            users = cursor.fetchall()
            
            success_count = 0
            for user_id, username, password_hash, salt in users:
                try:
                    # Check if user already exists in Firebase
                    firebase_user = self.firebase.get_user_by_email(f"{username}@persian-life-manager.com")
                    if firebase_user:
                        logger.info(f"User {username} already exists in Firebase with ID: {firebase_user['uid']}")
                        continue
                    
                    # Create user in Firebase
                    # For security, we generate a random password initially
                    import uuid
                    import hashlib
                    random_password = hashlib.md5(uuid.uuid4().bytes).hexdigest()[:12] + "A1!"
                    
                    success, firebase_uid = self.firebase.register_user(
                        email=f"{username}@persian-life-manager.com",
                        password=random_password,
                        name=username
                    )
                    
                    if success:
                        # Store mapping between SQLite ID and Firebase ID
                        self.firebase.add_user_data(firebase_uid, "user_mapping", {
                            "sqlite_id": user_id,
                            "username": username
                        })
                        success_count += 1
                except Exception as e:
                    logger.error(f"Error migrating user {username}: {str(e)}")
            
            self.migration_status["users"] = True
            logger.info(f"Successfully migrated {success_count}/{len(users)} users to Firebase")
            return True
        except Exception as e:
            logger.error(f"Error during user migration: {str(e)}")
            return False
    
    def firebase_login(self, username, password):
        """Login user with Firebase
        
        Args:
            username (str): Username
            password (str): Password
            
        Returns:
            User or None: User object if login successful
        """
        if not self.enabled:
            return None
        
        try:
            # For simplicity, we use email format username@persian-life-manager.com
            email = f"{username}@persian-life-manager.com"
            
            # Get user by email
            firebase_user = self.firebase.get_user_by_email(email)
            if not firebase_user:
                logger.warning(f"User {username} not found in Firebase")
                return None
            
            # For actual login, we would need the Firebase web API key
            # This is just a simplified version
            user_data = self.firebase.get_user_data(firebase_user["uid"], "user_mapping")
            if not user_data:
                logger.warning(f"User mapping not found for {username}")
                return None
            
            # Create User object with Firebase UID and SQLite ID
            user = User(user_data.get("sqlite_id", 0), username)
            user.firebase_uid = firebase_user["uid"]
            
            return user
        except Exception as e:
            logger.error(f"Error during Firebase login: {str(e)}")
            return None
    
    def firebase_register(self, username, password):
        """Register user with Firebase
        
        Args:
            username (str): Username
            password (str): Password
            
        Returns:
            User or None: User object if registration successful
        """
        if not self.enabled:
            return None
        
        try:
            # First, register with SQLite to get a SQLite ID
            user = self.auth_service.register(username, password)
            if not user:
                logger.error(f"Error registering user {username} in SQLite")
                return None
            
            # Then register with Firebase
            email = f"{username}@persian-life-manager.com"
            success, firebase_uid = self.firebase.register_user(
                email=email,
                password=password,
                name=username
            )
            
            if success:
                # Store mapping between SQLite ID and Firebase ID
                self.firebase.add_user_data(firebase_uid, "user_mapping", {
                    "sqlite_id": user.id,
                    "username": username
                })
                
                # Add Firebase UID to user object
                user.firebase_uid = firebase_uid
                
                return user
            else:
                logger.error(f"Error registering user {username} in Firebase")
                return None
        except Exception as e:
            logger.error(f"Error during Firebase registration: {str(e)}")
            return None
    
    # ================ Finance Data ================
    
    def migrate_finance_data(self, user_id, firebase_uid):
        """Migrate finance data from SQLite to Firebase
        
        Args:
            user_id (int): SQLite user ID
            firebase_uid (str): Firebase user ID
            
        Returns:
            bool: True if migration successful
        """
        if not self.enabled:
            return False
        
        try:
            from app.core.database import DatabaseManager
            db_manager = DatabaseManager(os.path.join(os.path.expanduser("~"), ".persian_life_manager", "database.db"))
            
            # Migrate categories
            categories = db_manager.execute_query(
                "SELECT id, name, type FROM finance_categories WHERE user_id = ?",
                (user_id,)
            )
            
            category_data = []
            for cat_id, name, cat_type in categories:
                category_data.append({
                    "id": cat_id,
                    "name": name,
                    "type": cat_type
                })
            
            if category_data:
                self.firebase.add_user_data(firebase_uid, "finances", {
                    "categories": category_data
                })
            
            # Migrate transactions
            transactions = db_manager.execute_query(
                "SELECT id, title, amount, date, type, category_id, description FROM finance_transactions WHERE user_id = ?",
                (user_id,)
            )
            
            for tr_id, title, amount, date, tr_type, category_id, description in transactions:
                transaction_data = {
                    "id": tr_id,
                    "title": title,
                    "amount": amount,
                    "date": date,
                    "type": tr_type,
                    "category_id": category_id,
                    "description": description or ""
                }
                
                self.firebase.add_transaction(firebase_uid, transaction_data)
            
            logger.info(f"Successfully migrated finance data for user {user_id} to Firebase")
            return True
        except Exception as e:
            logger.error(f"Error migrating finance data: {str(e)}")
            return False
    
    def add_transaction_to_firebase(self, transaction, firebase_uid):
        """Add a transaction to Firebase
        
        Args:
            transaction (Transaction): Transaction object
            firebase_uid (str): Firebase user ID
            
        Returns:
            bool: True if successful
        """
        if not self.enabled:
            return False
        
        try:
            transaction_data = {
                "id": transaction.id,
                "title": transaction.title,
                "amount": transaction.amount,
                "date": transaction.date,
                "type": transaction.type,
                "category_id": transaction.category_id,
                "description": transaction.description or ""
            }
            
            return self.firebase.add_transaction(firebase_uid, transaction_data)
        except Exception as e:
            logger.error(f"Error adding transaction to Firebase: {str(e)}")
            return False
    
    def get_transactions_from_firebase(self, firebase_uid, limit=50):
        """Get transactions from Firebase
        
        Args:
            firebase_uid (str): Firebase user ID
            limit (int): Maximum number of transactions to return
            
        Returns:
            list: List of Transaction objects
        """
        if not self.enabled:
            return []
        
        try:
            firebase_transactions = self.firebase.get_transactions(firebase_uid, limit)
            
            transactions = []
            for tr_data in firebase_transactions:
                transaction = Transaction(
                    id=tr_data.get("id"),
                    user_id=0,  # We don't use SQLite user ID here
                    title=tr_data.get("title", ""),
                    amount=tr_data.get("amount", 0),
                    date=tr_data.get("date", ""),
                    type=tr_data.get("type", "expense"),
                    category_id=tr_data.get("category_id", 0),
                    description=tr_data.get("description", "")
                )
                transactions.append(transaction)
            
            return transactions
        except Exception as e:
            logger.error(f"Error getting transactions from Firebase: {str(e)}")
            return []
    
    # ================ Health Data ================
    
    def migrate_health_data(self, user_id, firebase_uid):
        """Migrate health data from SQLite to Firebase
        
        Args:
            user_id (int): SQLite user ID
            firebase_uid (str): Firebase user ID
            
        Returns:
            bool: True if migration successful
        """
        if not self.enabled:
            return False
        
        try:
            from app.core.database import DatabaseManager
            db_manager = DatabaseManager(os.path.join(os.path.expanduser("~"), ".persian_life_manager", "database.db"))
            
            # Migrate exercises
            exercises = db_manager.execute_query(
                "SELECT id, date, exercise_type, duration, calories_burned, notes FROM health_exercises WHERE user_id = ?",
                (user_id,)
            )
            
            for ex_id, date, ex_type, duration, calories, notes in exercises:
                exercise_data = {
                    "id": ex_id,
                    "date": date,
                    "exercise_type": ex_type,
                    "duration": duration,
                    "calories_burned": calories,
                    "notes": notes or ""
                }
                
                self.firebase.add_health_metric(firebase_uid, {
                    "type": "exercise",
                    "data": exercise_data
                })
            
            # Migrate health metrics
            metrics = db_manager.execute_query(
                "SELECT id, date, weight, systolic, diastolic, heart_rate, sleep_hours, notes FROM health_metrics WHERE user_id = ?",
                (user_id,)
            )
            
            for m_id, date, weight, systolic, diastolic, heart_rate, sleep_hours, notes in metrics:
                metric_data = {
                    "id": m_id,
                    "date": date,
                    "weight": weight,
                    "systolic": systolic,
                    "diastolic": diastolic,
                    "heart_rate": heart_rate,
                    "sleep_hours": sleep_hours,
                    "notes": notes or ""
                }
                
                self.firebase.add_health_metric(firebase_uid, {
                    "type": "metrics",
                    "data": metric_data
                })
            
            # Migrate health goals
            goals = db_manager.execute_query(
                "SELECT id, goal_type, target_value, deadline, progress, notes FROM health_goals WHERE user_id = ?",
                (user_id,)
            )
            
            goal_data = []
            for g_id, g_type, target, deadline, progress, notes in goals:
                goal_data.append({
                    "id": g_id,
                    "goal_type": g_type,
                    "target_value": target,
                    "deadline": deadline,
                    "progress": progress,
                    "notes": notes or ""
                })
            
            if goal_data:
                self.firebase.add_user_data(firebase_uid, "health", {
                    "goals": goal_data
                })
            
            logger.info(f"Successfully migrated health data for user {user_id} to Firebase")
            return True
        except Exception as e:
            logger.error(f"Error migrating health data: {str(e)}")
            return False
    
    # ================ Calendar Data ================
    
    def migrate_calendar_data(self, user_id, firebase_uid):
        """Migrate calendar data from SQLite to Firebase
        
        Args:
            user_id (int): SQLite user ID
            firebase_uid (str): Firebase user ID
            
        Returns:
            bool: True if migration successful
        """
        if not self.enabled:
            return False
        
        try:
            from app.core.database import DatabaseManager
            db_manager = DatabaseManager(os.path.join(os.path.expanduser("~"), ".persian_life_manager", "database.db"))
            
            # Migrate events
            events = db_manager.execute_query(
                "SELECT id, title, date, start_time, end_time, location, description, all_day, has_reminder FROM calendar_events WHERE user_id = ?",
                (user_id,)
            )
            
            for e_id, title, date, start_time, end_time, location, description, all_day, has_reminder in events:
                event_data = {
                    "id": e_id,
                    "title": title,
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "location": location or "",
                    "description": description or "",
                    "all_day": all_day == 1,
                    "has_reminder": has_reminder == 1
                }
                
                self.firebase.add_calendar_event(firebase_uid, event_data)
            
            # Migrate tasks
            tasks = db_manager.execute_query(
                "SELECT id, title, due_date, priority, description, completed, completion_date, has_reminder FROM tasks WHERE user_id = ?",
                (user_id,)
            )
            
            for t_id, title, due_date, priority, description, completed, completion_date, has_reminder in tasks:
                task_data = {
                    "id": t_id,
                    "title": title,
                    "due_date": due_date,
                    "priority": priority,
                    "description": description or "",
                    "completed": completed == 1,
                    "completion_date": completion_date or "",
                    "has_reminder": has_reminder == 1
                }
                
                self.firebase.add_calendar_event(firebase_uid, {
                    "type": "task",
                    "data": task_data
                })
            
            logger.info(f"Successfully migrated calendar data for user {user_id} to Firebase")
            return True
        except Exception as e:
            logger.error(f"Error migrating calendar data: {str(e)}")
            return False
    
    # ================ Utility Functions ================
    
    def migrate_all_data(self, user_id, firebase_uid):
        """Migrate all data for a user from SQLite to Firebase
        
        Args:
            user_id (int): SQLite user ID
            firebase_uid (str): Firebase user ID
            
        Returns:
            bool: True if all migrations successful
        """
        if not self.enabled:
            return False
        
        try:
            finance_success = self.migrate_finance_data(user_id, firebase_uid)
            health_success = self.migrate_health_data(user_id, firebase_uid)
            calendar_success = self.migrate_calendar_data(user_id, firebase_uid)
            
            all_success = finance_success and health_success and calendar_success
            
            if all_success:
                logger.info(f"Successfully migrated all data for user {user_id} to Firebase")
            else:
                logger.warning(f"Partial data migration for user {user_id}: Finance={finance_success}, Health={health_success}, Calendar={calendar_success}")
            
            return all_success
        except Exception as e:
            logger.error(f"Error during full data migration: {str(e)}")
            return False