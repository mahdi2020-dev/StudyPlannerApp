"""
Supabase Client for Persian Life Manager Application
"""
import os
import logging
import json
from typing import Dict, List, Optional, Any, Union

try:
    from supabase import create_client, Client
except ImportError:
    # Will be handled in initialize()
    pass

# Setup logger
logger = logging.getLogger(__name__)

class SupabaseManager:
    """
    Singleton manager for Supabase client
    """
    _instance = None
    _client = None
    _initialized = False

    def __new__(cls):
        """Singleton pattern to ensure only one Supabase connection"""
        if cls._instance is None:
            cls._instance = super(SupabaseManager, cls).__new__(cls)
        return cls._instance

    def initialize(self) -> bool:
        """
        Initialize Supabase client connection
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        if self._initialized:
            return True
            
        try:
            # Get Supabase credentials from environment
            supabase_url = os.environ.get('SUPABASE_URL')
            supabase_key = os.environ.get('SUPABASE_KEY')
            
            if not supabase_url or not supabase_key:
                logger.error("Supabase credentials not found in environment variables")
                return False
                
            # Create Supabase client
            self._client = create_client(supabase_url, supabase_key)
            self._initialized = True
            logger.info("Supabase client initialized successfully")
            return True
            
        except ImportError:
            logger.error("Supabase Python package not installed. Install with 'pip install supabase'")
            return False
        except Exception as e:
            logger.error(f"Error initializing Supabase client: {str(e)}")
            return False
    
    @property
    def client(self) -> Optional[Client]:
        """
        Get the Supabase client instance
        
        Returns:
            Optional[Client]: The Supabase client or None if not initialized
        """
        if not self._initialized:
            success = self.initialize()
            if not success:
                return None
        return self._client

    def is_initialized(self) -> bool:
        """
        Check if Supabase client is initialized
        
        Returns:
            bool: True if initialized, False otherwise
        """
        return self._initialized

    def get_user(self, user_id: str) -> Optional[Dict]:
        """
        Get user data by ID
        
        Args:
            user_id (str): The user ID
            
        Returns:
            Optional[Dict]: User data dictionary or None if not found
        """
        if not self.client:
            return None
            
        try:
            # First try to get user data from the auth.users metadata
            user = self.client.auth.admin.get_user_by_id(user_id)
            if user and user.user:
                # If metadata doesn't exist or we need additional fields, try to get from custom users table
                try:
                    response = self.client.from_('users').select('*').eq('id', user_id).execute()
                    if response.data and len(response.data) > 0:
                        return response.data[0]
                
                    # If not in custom table but exists in auth, create entry in custom table
                    user_data = {
                        'id': user_id,
                        'email': user.user.email,
                        'name': user.user.user_metadata.get('name', 'User'),
                        'is_guest': False
                    }
                    self.create_user(user_data)
                    return user_data
                except Exception as table_error:
                    # If custom table doesn't exist yet, return basic user data from auth
                    logger.warning(f"Custom users table error: {str(table_error)}")
                    return {
                        'id': user_id,
                        'email': user.user.email, 
                        'name': user.user.user_metadata.get('name', 'User'),
                        'is_guest': False
                    }
            return None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            return None
            
    def create_user(self, user_data: Dict) -> bool:
        """
        Create user in custom users table
        
        Args:
            user_data (Dict): User data to create
            
        Returns:
            bool: Success status
        """
        if not self.client:
            return False
            
        try:
            # Try to insert into custom users table
            response = self.client.from_('users').insert(user_data).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return False

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Get user by email
        
        Args:
            email (str): User email
            
        Returns:
            Optional[Dict]: User data or None if not found
        """
        if not self.client:
            return None
            
        try:
            # First try to get from auth user
            response = self.client.auth.admin.list_users()
            if response and response.users:
                for auth_user in response.users:
                    if auth_user.email and auth_user.email.lower() == email.lower():
                        # User found in auth, try to get additional data from custom table
                        try:
                            table_response = self.client.from_('users').select('*').eq('email', email).execute()
                            if table_response.data and len(table_response.data) > 0:
                                return table_response.data[0]
                            
                            # If not found in custom table, create an entry
                            user_data = {
                                'id': auth_user.id,
                                'email': auth_user.email,
                                'name': auth_user.user_metadata.get('name', 'User'),
                                'is_guest': False
                            }
                            self.create_user(user_data)
                            return user_data
                        except Exception as table_error:
                            # Return basic user data
                            logger.warning(f"Custom users table error: {str(table_error)}")
                            return {
                                'id': auth_user.id,
                                'email': auth_user.email,
                                'name': auth_user.user_metadata.get('name', 'User'),
                                'is_guest': False
                            }
            
            # Fallback to directly query the custom table
            try:
                response = self.client.from_('users').select('*').eq('email', email).execute()
                if response.data and len(response.data) > 0:
                    return response.data[0]
            except Exception as e:
                logger.warning(f"Fallback query error: {str(e)}")
                
            return None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            return None
    
    def add_user_data(self, user_id: str, collection: str, data: Dict) -> bool:
        """
        Add user data to a collection
        
        Args:
            user_id (str): User ID
            collection (str): Collection name
            data (dict): Data to add
            
        Returns:
            bool: Success status
        """
        if not self.client:
            return False
            
        try:
            # Add user_id to the data
            data['user_id'] = user_id
            
            # Insert data into the table
            response = self.client.from_(collection).insert(data).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error adding user data to {collection}: {str(e)}")
            return False
    
    def get_user_data(self, user_id: str, collection: str, limit: int = 50) -> List[Dict]:
        """
        Get user data from a collection
        
        Args:
            user_id (str): User ID
            collection (str): Collection name
            limit (int, optional): Maximum number of records to return. Defaults to 50.
            
        Returns:
            List[Dict]: List of user data items
        """
        if not self.client:
            return []
            
        try:
            response = self.client.from_(collection) \
                .select('*') \
                .eq('user_id', user_id) \
                .order('created_at', desc=True) \
                .limit(limit) \
                .execute()
                
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting user data from {collection}: {str(e)}")
            return []
    
    def add_transaction(self, user_id: str, transaction_data: Dict) -> bool:
        """
        Add a financial transaction
        
        Args:
            user_id (str): User ID
            transaction_data (dict): Transaction data
            
        Returns:
            bool: Success status
        """
        return self.add_user_data(user_id, 'finance_transactions', transaction_data)
    
    def get_transactions(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Get financial transactions
        
        Args:
            user_id (str): User ID
            limit (int, optional): Maximum number of transactions to return. Defaults to 50.
            
        Returns:
            List[Dict]: List of transactions
        """
        return self.get_user_data(user_id, 'finance_transactions', limit)
    
    def add_health_metric(self, user_id: str, metric_data: Dict) -> bool:
        """
        Add a health metric
        
        Args:
            user_id (str): User ID
            metric_data (dict): Health metric data
            
        Returns:
            bool: Success status
        """
        return self.add_user_data(user_id, 'health_metrics', metric_data)
    
    def get_health_metrics(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Get health metrics
        
        Args:
            user_id (str): User ID
            limit (int, optional): Maximum number of metrics to return. Defaults to 50.
            
        Returns:
            List[Dict]: List of health metrics
        """
        return self.get_user_data(user_id, 'health_metrics', limit)
    
    def add_calendar_event(self, user_id: str, event_data: Dict) -> bool:
        """
        Add a calendar event
        
        Args:
            user_id (str): User ID
            event_data (dict): Event data
            
        Returns:
            bool: Success status
        """
        return self.add_user_data(user_id, 'calendar_events', event_data)
    
    def get_calendar_events(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Get calendar events
        
        Args:
            user_id (str): User ID
            limit (int, optional): Maximum number of events to return. Defaults to 50.
            
        Returns:
            List[Dict]: List of calendar events
        """
        return self.get_user_data(user_id, 'calendar_events', limit)