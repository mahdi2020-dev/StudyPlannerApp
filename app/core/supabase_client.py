"""
Supabase Client for Persian Life Manager Application
Handles database operations and authentication with Supabase
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union

# Import the supabase-py client
try:
    from supabase import create_client, Client
except ImportError:
    logging.error("Supabase client not installed. Run 'pip install supabase'")
    raise

# Set up logging
logger = logging.getLogger(__name__)

class SupabaseManager:
    """Supabase database and authentication manager"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one Supabase connection"""
        if cls._instance is None:
            cls._instance = super(SupabaseManager, cls).__new__(cls)
            cls._instance.supabase = None
            cls._instance.initialized = False
        return cls._instance
    
    def initialize(self):
        """Initialize Supabase connection"""
        if self.initialized:
            return True
        
        try:
            # Get environment variables
            supabase_url = os.environ.get("SUPABASE_URL")
            supabase_key = os.environ.get("SUPABASE_KEY")
            
            if not supabase_url or not supabase_key:
                logger.error("SUPABASE_URL or SUPABASE_KEY environment variables not set")
                return False
            
            # Initialize Supabase client
            self.supabase = create_client(supabase_url, supabase_key)
            self.initialized = True
            logger.info("Supabase client initialized successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error initializing Supabase: {str(e)}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if Supabase is initialized"""
        return self.initialized
    
    def login_user(self, email: str, password: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """Login a user
        
        Args:
            email (str): User email
            password (str): User password
            
        Returns:
            tuple: (success, user_data or error_message)
        """
        if not self.is_initialized():
            return False, "Supabase not initialized"
        
        try:
            # Attempt to sign in
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            # Return user data
            if response.user:
                user_data = {
                    "id": response.user.id,
                    "email": response.user.email,
                    "created_at": response.user.created_at,
                    "last_sign_in_at": response.user.last_sign_in_at
                }
                return True, user_data
            else:
                return False, "Invalid email or password"
        
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False, str(e)
    
    def user_exists(self, email: str) -> bool:
        """Check if a user exists
        
        Args:
            email (str): User email
            
        Returns:
            bool: True if the user exists, False otherwise
        """
        if not self.is_initialized():
            return False
        
        try:
            # Query the users table
            response = self.supabase.table("user_profiles").select("email").eq("email", email).execute()
            
            # Check if any rows were returned
            return len(response.data) > 0
        
        except Exception as e:
            logger.error(f"Error checking if user exists: {str(e)}")
            return False
    
    def get_user_data(self, user_id: str, collection: str) -> Optional[Dict[str, Any]]:
        """Get user data from a collection
        
        Args:
            user_id (str): User ID
            collection (str): Collection name
            
        Returns:
            dict: User data or None
        """
        if not self.is_initialized():
            return None
        
        try:
            response = self.supabase.table(collection).select("*").eq("user_id", user_id).execute()
            
            if response.data:
                return response.data
            else:
                return None
        
        except Exception as e:
            logger.error(f"Error getting user data: {str(e)}")
            return None
    
    def add_user_data(self, user_id: str, collection: str, data: Dict[str, Any]) -> bool:
        """Add user data to a collection
        
        Args:
            user_id (str): User ID
            collection (str): Collection name
            data (dict): Data to add
            
        Returns:
            bool: Success status
        """
        if not self.is_initialized():
            return False
        
        try:
            # Add user_id to the data
            data["user_id"] = user_id
            
            # Add created_at timestamp if not present
            if "created_at" not in data:
                data["created_at"] = datetime.now().isoformat()
            
            # Insert the data
            response = self.supabase.table(collection).insert(data).execute()
            
            return len(response.data) > 0
        
        except Exception as e:
            logger.error(f"Error adding user data: {str(e)}")
            return False
    
    def update_user_data(self, user_id: str, collection: str, item_id: str, data: Dict[str, Any]) -> bool:
        """Update user data in a collection
        
        Args:
            user_id (str): User ID
            collection (str): Collection name
            item_id (str): Item ID
            data (dict): Data to update
            
        Returns:
            bool: Success status
        """
        if not self.is_initialized():
            return False
        
        try:
            # Add updated_at timestamp
            data["updated_at"] = datetime.now().isoformat()
            
            # Update the data
            response = self.supabase.table(collection).update(data).eq("id", item_id).eq("user_id", user_id).execute()
            
            return len(response.data) > 0
        
        except Exception as e:
            logger.error(f"Error updating user data: {str(e)}")
            return False
    
    def delete_user_data(self, user_id: str, collection: str, item_id: str) -> bool:
        """Delete user data from a collection
        
        Args:
            user_id (str): User ID
            collection (str): Collection name
            item_id (str): Item ID
            
        Returns:
            bool: Success status
        """
        if not self.is_initialized():
            return False
        
        try:
            # Delete the data
            response = self.supabase.table(collection).delete().eq("id", item_id).eq("user_id", user_id).execute()
            
            return len(response.data) > 0
        
        except Exception as e:
            logger.error(f"Error deleting user data: {str(e)}")
            return False
    
    def add_transaction(self, user_id: str, transaction_data: Dict[str, Any]) -> bool:
        """Add a financial transaction
        
        Args:
            user_id (str): User ID
            transaction_data (dict): Transaction data
            
        Returns:
            bool: Success status
        """
        return self.add_user_data(user_id, "transactions", transaction_data)
    
    def get_transactions(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get financial transactions
        
        Args:
            user_id (str): User ID
            limit (int): Maximum number of transactions to return
            
        Returns:
            list: List of transactions
        """
        if not self.is_initialized():
            return []
        
        try:
            response = self.supabase.table("transactions") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("date", ascending=False) \
                .limit(limit) \
                .execute()
            
            return response.data
        
        except Exception as e:
            logger.error(f"Error getting transactions: {str(e)}")
            return []
    
    def add_health_metric(self, user_id: str, metric_data: Dict[str, Any]) -> bool:
        """Add a health metric
        
        Args:
            user_id (str): User ID
            metric_data (dict): Health metric data
            
        Returns:
            bool: Success status
        """
        return self.add_user_data(user_id, "health_metrics", metric_data)
    
    def get_health_metrics(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get health metrics
        
        Args:
            user_id (str): User ID
            limit (int): Maximum number of metrics to return
            
        Returns:
            list: List of health metrics
        """
        if not self.is_initialized():
            return []
        
        try:
            response = self.supabase.table("health_metrics") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("date", ascending=False) \
                .limit(limit) \
                .execute()
            
            return response.data
        
        except Exception as e:
            logger.error(f"Error getting health metrics: {str(e)}")
            return []
    
    def add_calendar_event(self, user_id: str, event_data: Dict[str, Any]) -> bool:
        """Add a calendar event
        
        Args:
            user_id (str): User ID
            event_data (dict): Event data
            
        Returns:
            bool: Success status
        """
        return self.add_user_data(user_id, "calendar_events", event_data)
    
    def get_calendar_events(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get calendar events
        
        Args:
            user_id (str): User ID
            limit (int): Maximum number of events to return
            
        Returns:
            list: List of calendar events
        """
        if not self.is_initialized():
            return []
        
        try:
            response = self.supabase.table("calendar_events") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("start_date", ascending=True) \
                .limit(limit) \
                .execute()
            
            return response.data
        
        except Exception as e:
            logger.error(f"Error getting calendar events: {str(e)}")
            return []