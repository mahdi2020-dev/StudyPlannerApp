"""
Firebase Configuration for Persian Life Manager Application
"""

import os
import json
import logging
import firebase_admin
from firebase_admin import credentials, firestore, auth

logger = logging.getLogger(__name__)

# Firebase Web API Key for client-side authentication
FIREBASE_WEB_API_KEY = "AIzaSyDNJlCgkKyEg_9ndH4H27PSv9DAWpEswNA"

class FirebaseManager:
    """Firebase database and authentication manager"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one Firebase connection"""
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        """Initialize Firebase connection"""
        self.app = None
        self.db = None
        self.initialized = False
        
        try:
            # Look for service account file in different locations
            service_account_locations = [
                'serviceAccountKey.json',
                'attached_assets/persian-life-manager-firebase-adminsdk-fbsvc-df2a5fea2d.json',
                os.path.join(os.path.expanduser('~'), '.persian_life_manager', 'serviceAccountKey.json')
            ]
            
            cred_path = None
            for location in service_account_locations:
                if os.path.exists(location):
                    cred_path = location
                    break
            
            if cred_path:
                logger.info(f"Using Firebase service account from: {cred_path}")
                cred = credentials.Certificate(cred_path)
                self.app = firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self.initialized = True
                logger.info("Firebase initialized successfully")
            else:
                logger.error("Firebase service account file not found in any location")
        except Exception as e:
            logger.error(f"Error initializing Firebase: {str(e)}")
    
    def is_initialized(self):
        """Check if Firebase is initialized"""
        return self.initialized
    
    def register_user(self, email, password, name):
        """Register a new user
        
        Args:
            email (str): User email
            password (str): User password
            name (str): User name
            
        Returns:
            tuple: (success, user_id or error_message)
        """
        if not self.initialized:
            return False, "Firebase not initialized"
        
        try:
            user = auth.create_user(
                email=email,
                password=password,
                display_name=name
            )
            return True, user.uid
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            return False, str(e)
    
    def get_user_by_email(self, email):
        """Get user by email
        
        Args:
            email (str): User email
            
        Returns:
            dict: User data or None
        """
        if not self.initialized:
            return None
        
        try:
            user = auth.get_user_by_email(email)
            return {
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name
            }
        except auth.UserNotFoundError:
            logger.warning(f"User with email {email} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            return None
    
    def add_user_data(self, user_id, collection, data):
        """Add user data to a collection
        
        Args:
            user_id (str): User ID
            collection (str): Collection name
            data (dict): Data to add
            
        Returns:
            bool: Success status
        """
        if not self.initialized:
            return False
        
        try:
            self.db.collection('users').document(user_id).collection(collection).add(data)
            return True
        except Exception as e:
            logger.error(f"Error adding user data: {str(e)}")
            return False
    
    def get_user_data(self, user_id, collection):
        """Get user data from a collection
        
        Args:
            user_id (str): User ID
            collection (str): Collection name
            
        Returns:
            dict: User data or None
        """
        if not self.initialized:
            return None
        
        try:
            data = {}
            docs = self.db.collection('users').document(user_id).collection(collection).get()
            for doc in docs:
                data[doc.id] = doc.to_dict()
            return data
        except Exception as e:
            logger.error(f"Error getting user data: {str(e)}")
            return None
    
    def add_transaction(self, user_id, transaction_data):
        """Add a financial transaction
        
        Args:
            user_id (str): User ID
            transaction_data (dict): Transaction data
            
        Returns:
            bool: Success status
        """
        if not self.initialized:
            return False
        
        try:
            self.db.collection('users').document(user_id).collection('transactions').add(transaction_data)
            return True
        except Exception as e:
            logger.error(f"Error adding transaction: {str(e)}")
            return False
    
    def get_transactions(self, user_id, limit=50):
        """Get financial transactions
        
        Args:
            user_id (str): User ID
            limit (int): Maximum number of transactions to return
            
        Returns:
            list: List of transactions
        """
        if not self.initialized:
            return []
        
        try:
            transactions = []
            docs = self.db.collection('users').document(user_id).collection('transactions').limit(limit).get()
            for doc in docs:
                transaction = doc.to_dict()
                transaction['id'] = doc.id
                transactions.append(transaction)
            return transactions
        except Exception as e:
            logger.error(f"Error getting transactions: {str(e)}")
            return []
    
    def add_health_metric(self, user_id, metric_data):
        """Add a health metric
        
        Args:
            user_id (str): User ID
            metric_data (dict): Health metric data
            
        Returns:
            bool: Success status
        """
        if not self.initialized:
            return False
        
        try:
            self.db.collection('users').document(user_id).collection('health_metrics').add(metric_data)
            return True
        except Exception as e:
            logger.error(f"Error adding health metric: {str(e)}")
            return False
    
    def get_health_metrics(self, user_id, limit=50):
        """Get health metrics
        
        Args:
            user_id (str): User ID
            limit (int): Maximum number of metrics to return
            
        Returns:
            list: List of health metrics
        """
        if not self.initialized:
            return []
        
        try:
            metrics = []
            docs = self.db.collection('users').document(user_id).collection('health_metrics').limit(limit).get()
            for doc in docs:
                metric = doc.to_dict()
                metric['id'] = doc.id
                metrics.append(metric)
            return metrics
        except Exception as e:
            logger.error(f"Error getting health metrics: {str(e)}")
            return []
    
    def add_calendar_event(self, user_id, event_data):
        """Add a calendar event
        
        Args:
            user_id (str): User ID
            event_data (dict): Event data
            
        Returns:
            bool: Success status
        """
        if not self.initialized:
            return False
        
        try:
            self.db.collection('users').document(user_id).collection('calendar_events').add(event_data)
            return True
        except Exception as e:
            logger.error(f"Error adding calendar event: {str(e)}")
            return False
    
    def get_calendar_events(self, user_id, limit=50):
        """Get calendar events
        
        Args:
            user_id (str): User ID
            limit (int): Maximum number of events to return
            
        Returns:
            list: List of calendar events
        """
        if not self.initialized:
            return []
        
        try:
            events = []
            docs = self.db.collection('users').document(user_id).collection('calendar_events').limit(limit).get()
            for doc in docs:
                event = doc.to_dict()
                event['id'] = doc.id
                events.append(event)
            return events
        except Exception as e:
            logger.error(f"Error getting calendar events: {str(e)}")
            return []