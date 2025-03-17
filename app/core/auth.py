"""
Authentication module for Persian Life Manager Application
Handles user authentication and session management
"""

import os
import json
import logging
import secrets
import time
from typing import Dict, Optional, Tuple, Any, Union

from app.core.supabase_client import SupabaseManager

# Set up logging
logger = logging.getLogger(__name__)

class User:
    """User class for storing user information"""
    
    def __init__(self, user_id: str, email: str, name: Optional[str] = None, is_guest: bool = False):
        """Initialize a user
        
        Args:
            user_id (str): User ID
            email (str): User email
            name (str, optional): User name
            is_guest (bool, optional): Whether this is a guest user
        """
        self.id = user_id
        self.email = email
        self.name = name if name else email.split('@')[0]
        self.is_guest = is_guest
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        self.session_token = secrets.token_hex(16)
        self.login_time = time.time()
    
    def get_id(self) -> str:
        """Get user ID for Flask-Login
        
        Returns:
            str: User ID
        """
        return self.id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary
        
        Returns:
            dict: User dictionary
        """
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'is_guest': self.is_guest,
            'session_token': self.session_token,
            'login_time': self.login_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary
        
        Args:
            data (dict): User dictionary
            
        Returns:
            User: User object
        """
        user = cls(
            user_id=data['id'],
            email=data['email'],
            name=data.get('name'),
            is_guest=data.get('is_guest', False)
        )
        user.session_token = data.get('session_token', '')
        user.login_time = data.get('login_time', time.time())
        return user


class AuthService:
    """Authentication service for user login and registration"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure only one Auth service"""
        if cls._instance is None:
            cls._instance = super(AuthService, cls).__new__(cls)
            cls._instance.supabase = SupabaseManager()
            cls._instance.active_sessions = {}  # Store active sessions
        return cls._instance
        
    def __init__(self, db_path=None):
        """Initialize the Auth Service
        
        Args:
            db_path (str, optional): Database path, not used in Supabase implementation
        """
        # db_path is ignored as we're using Supabase now
        pass
    
    def initialize(self) -> bool:
        """Initialize the authentication manager
        
        Returns:
            bool: Whether initialization was successful
        """
        return self.supabase.initialize()
    
    def login(self, email: str, password: str) -> Tuple[bool, Union[User, str]]:
        """Login a user
        
        Args:
            email (str): User email
            password (str): User password
            
        Returns:
            tuple: (success, User object or error message)
        """
        success, result = self.supabase.login_user(email, password)
        
        if success:
            # Create User object
            user = User(
                user_id=result['id'],
                email=result['email'],
                name=result.get('name')
            )
            
            # Add to active sessions
            self.active_sessions[user.session_token] = user
            
            return True, user
        else:
            return False, result
    
    def user_exists(self, email: str) -> bool:
        """Check if a user exists
        
        Args:
            email (str): User email
            
        Returns:
            bool: Whether the user exists
        """
        return self.supabase.user_exists(email)
    
    def create_guest_user(self) -> User:
        """Create a guest user
        
        Returns:
            User: Guest user object
        """
        guest_id = f"guest_{secrets.token_hex(8)}"
        guest_email = f"{guest_id}@guest.local"
        
        user = User(
            user_id=guest_id,
            email=guest_email,
            name="مهمان",
            is_guest=True
        )
        
        # Add to active sessions
        self.active_sessions[user.session_token] = user
        
        return user
    
    def validate_session(self, user_id: str, session_token: str) -> bool:
        """Validate a user session
        
        Args:
            user_id (str): User ID
            session_token (str): Session token
            
        Returns:
            bool: Whether the session is valid
        """
        # Check if session exists
        if session_token not in self.active_sessions:
            return False
        
        # Get user from active sessions
        user = self.active_sessions[session_token]
        
        # Check if user ID matches
        if user.id != user_id:
            return False
        
        # Check if session has expired (24 hours)
        if time.time() - user.login_time > 24 * 60 * 60:
            # Remove expired session
            del self.active_sessions[session_token]
            return False
        
        return True
    
    def get_user_by_session(self, session_token: str) -> Optional[User]:
        """Get user by session token
        
        Args:
            session_token (str): Session token
            
        Returns:
            User: User object or None
        """
        # Check if session exists
        if session_token not in self.active_sessions:
            return None
        
        # Get user from active sessions
        user = self.active_sessions[session_token]
        
        # Check if session has expired (24 hours)
        if time.time() - user.login_time > 24 * 60 * 60:
            # Remove expired session
            del self.active_sessions[session_token]
            return None
        
        return user
    
    def logout(self, session_token: str) -> bool:
        """Logout a user
        
        Args:
            session_token (str): Session token
            
        Returns:
            bool: Whether logout was successful
        """
        # Check if session exists
        if session_token in self.active_sessions:
            # Remove session
            del self.active_sessions[session_token]
            return True
        
        return False