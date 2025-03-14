"""
Firebase Configuration for Persian Life Manager Application
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import logging

logger = logging.getLogger(__name__)

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
        try:
            # بارگذاری کلید خصوصی
            cred_path = os.path.join(os.getcwd(), "serviceAccountKey.json")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            
            # اتصال به Firestore
            self.db = firestore.client()
            logger.info("🔥 Firebase connected successfully!")
            self.initialized = True
        except Exception as e:
            logger.error(f"Firebase initialization error: {str(e)}")
            self.initialized = False
    
    def is_initialized(self):
        """Check if Firebase is initialized"""
        return getattr(self, 'initialized', False)
    
    # ================ User Authentication Methods ================
    
    def register_user(self, email, password, name):
        """Register a new user
        
        Args:
            email (str): User email
            password (str): User password
            name (str): User name
            
        Returns:
            tuple: (success, user_id or error_message)
        """
        try:
            user = auth.create_user(email=email, password=password)
            
            # Create user document in Firestore
            user_ref = self.db.collection("users").document(user.uid)
            user_ref.set({
                "name": name,
                "email": email,
                "created_at": firestore.SERVER_TIMESTAMP
            })
            
            logger.info(f"User {email} created successfully!")
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
        try:
            users = auth.get_users_by_email(email)
            if users and len(users) > 0:
                user = users[0]
                return {
                    "uid": user.uid,
                    "email": user.email
                }
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            return None
    
    # ================ Data Management Methods ================
    
    def add_user_data(self, user_id, collection, data):
        """Add user data to a collection
        
        Args:
            user_id (str): User ID
            collection (str): Collection name
            data (dict): Data to add
            
        Returns:
            bool: Success status
        """
        try:
            # Add timestamp
            data["created_at"] = firestore.SERVER_TIMESTAMP
            
            # Add data to collection
            doc_ref = self.db.collection(collection).document(user_id)
            doc_ref.set(data, merge=True)
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
        try:
            doc_ref = self.db.collection(collection).document(user_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting user data: {str(e)}")
            return None
    
    # ================ Specific Collection Methods ================
    
    def add_transaction(self, user_id, transaction_data):
        """Add a financial transaction
        
        Args:
            user_id (str): User ID
            transaction_data (dict): Transaction data
            
        Returns:
            bool: Success status
        """
        try:
            # Add timestamp
            transaction_data["created_at"] = firestore.SERVER_TIMESTAMP
            
            # Add transaction to transactions subcollection
            doc_ref = self.db.collection("finances").document(user_id)
            doc_ref.collection("transactions").add(transaction_data)
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
        try:
            transactions = []
            docs = self.db.collection("finances").document(user_id) \
                .collection("transactions") \
                .order_by("created_at", direction=firestore.Query.DESCENDING) \
                .limit(limit) \
                .stream()
            
            for doc in docs:
                transaction = doc.to_dict()
                transaction["id"] = doc.id
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
        try:
            # Add timestamp
            metric_data["created_at"] = firestore.SERVER_TIMESTAMP
            
            # Add metric to metrics subcollection
            doc_ref = self.db.collection("health").document(user_id)
            doc_ref.collection("metrics").add(metric_data)
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
        try:
            metrics = []
            docs = self.db.collection("health").document(user_id) \
                .collection("metrics") \
                .order_by("created_at", direction=firestore.Query.DESCENDING) \
                .limit(limit) \
                .stream()
            
            for doc in docs:
                metric = doc.to_dict()
                metric["id"] = doc.id
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
        try:
            # Add timestamp
            event_data["created_at"] = firestore.SERVER_TIMESTAMP
            
            # Add event to events subcollection
            doc_ref = self.db.collection("schedules").document(user_id)
            doc_ref.collection("events").add(event_data)
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
        try:
            events = []
            docs = self.db.collection("schedules").document(user_id) \
                .collection("events") \
                .order_by("created_at", direction=firestore.Query.DESCENDING) \
                .limit(limit) \
                .stream()
            
            for doc in docs:
                event = doc.to_dict()
                event["id"] = doc.id
                events.append(event)
            
            return events
        except Exception as e:
            logger.error(f"Error getting calendar events: {str(e)}")
            return []