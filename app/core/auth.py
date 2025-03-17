"""
Authentication Service for Persian Life Manager Application
Handles authentication with Supabase
"""
import os
import logging
import uuid
import json
import time
from typing import Dict, Optional, List, Any, Tuple

from app.core.supabase_client import SupabaseManager

# Setup logger
logger = logging.getLogger(__name__)

class User:
    """
    User class to store user data
    """
    def __init__(self, user_id: str, name: str, email: str, is_guest: bool = False):
        """
        Initialize a User object
        
        Args:
            user_id (str): User ID
            name (str): User name
            email (str): User email
            is_guest (bool, optional): Whether this is a guest user. Defaults to False.
        """
        self.id = user_id
        self.name = name
        self.email = email
        self.is_guest = is_guest
        self.created_at = time.time()
        self.last_login = time.time()
    
    def to_dict(self) -> Dict:
        """
        Convert user to dictionary
        
        Returns:
            Dict: Dictionary representation of user
        """
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'is_guest': self.is_guest,
            'created_at': self.created_at,
            'last_login': self.last_login
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """
        Create a User object from a dictionary
        
        Args:
            data (Dict): Dictionary with user data
            
        Returns:
            User: User object
        """
        user = cls(
            user_id=data.get('id', ''),
            name=data.get('name', ''),
            email=data.get('email', ''),
            is_guest=data.get('is_guest', False)
        )
        user.created_at = data.get('created_at', time.time())
        user.last_login = data.get('last_login', time.time())
        return user

class Session:
    """
    Session class to store session data
    """
    def __init__(self, session_id: str, user_id: str, expiry: float = None):
        """
        Initialize a Session object
        
        Args:
            session_id (str): Session ID
            user_id (str): User ID
            expiry (float, optional): Session expiry timestamp. Defaults to 24 hours from now.
        """
        self.id = session_id
        self.user_id = user_id
        self.created_at = time.time()
        self.expiry = expiry if expiry else time.time() + (24 * 60 * 60)  # 24 hours
    
    def is_valid(self) -> bool:
        """
        Check if session is valid (not expired)
        
        Returns:
            bool: True if valid, False otherwise
        """
        return time.time() < self.expiry
    
    def to_dict(self) -> Dict:
        """
        Convert session to dictionary
        
        Returns:
            Dict: Dictionary representation of session
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at,
            'expiry': self.expiry
        }

class AuthService:
    """
    Authentication service for Persian Life Manager
    """
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one authentication service"""
        if cls._instance is None:
            cls._instance = super(AuthService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def initialize(self):
        """
        Initialize the authentication service
        """
        if self._initialized:
            return
            
        self.supabase = SupabaseManager()
        self.active_sessions = {}  # Dictionary of session_id -> Session
        self._initialized = True
    
    def login(self, email: str, password: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Login a user with email and password
        
        Args:
            email (str): User email
            password (str): User password
            
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: 
                - Success status
                - Session ID if successful, None otherwise
                - Error message if unsuccessful, None otherwise
        """
        if not self.supabase.is_initialized():
            if not self.supabase.initialize():
                return False, None, "Failed to initialize Supabase client"
        
        try:
            # Authenticate with Supabase
            auth_response = self.supabase.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            user = auth_response.user
            
            if not user:
                return False, None, "Invalid credentials"
            
            # Create session
            session_id = str(uuid.uuid4())
            self.active_sessions[session_id] = Session(
                session_id=session_id,
                user_id=user.id
            )
            
            return True, session_id, None
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False, None, str(e)
    
    def user_exists(self, email: str) -> bool:
        """
        Check if a user exists by email
        
        Args:
            email (str): User email
            
        Returns:
            bool: True if user exists, False otherwise
        """
        user_data = self.supabase.get_user_by_email(email)
        return user_data is not None
    
    def get_user_by_session(self, session_id: str) -> Optional[User]:
        """
        Get user by session ID
        
        Args:
            session_id (str): Session ID
            
        Returns:
            Optional[User]: User object if session is valid, None otherwise
        """
        if session_id not in self.active_sessions:
            return None
            
        session = self.active_sessions[session_id]
        
        if not session.is_valid():
            # Session expired
            del self.active_sessions[session_id]
            return None
        
        # Get user data from Supabase
        user_data = self.supabase.get_user(session.user_id)
        
        if not user_data:
            return None
            
        return User(
            user_id=user_data.get('id', ''),
            name=user_data.get('name', ''),
            email=user_data.get('email', ''),
            is_guest=user_data.get('is_guest', False)
        )
    
    def logout(self, session_id: str) -> bool:
        """
        Logout a user session
        
        Args:
            session_id (str): Session ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        return False
    
    def create_guest_session(self) -> Tuple[bool, Optional[str], Optional[User]]:
        """
        Create a guest session
        
        Returns:
            Tuple[bool, Optional[str], Optional[User]]:
                - Success status
                - Session ID if successful, None otherwise
                - User object if successful, None otherwise
        """
        session_id = str(uuid.uuid4())
        user_id = f"guest-{uuid.uuid4()}"
        
        guest_user = User(
            user_id=user_id,
            name="Guest User",
            email=f"{user_id}@guest.persianlifemanager.app",
            is_guest=True
        )
        
        self.active_sessions[session_id] = Session(
            session_id=session_id,
            user_id=user_id
        )
        
        return True, session_id, guest_user
    
    def get_all_sessions(self) -> List[Dict]:
        """
        Get all active sessions
        
        Returns:
            List[Dict]: List of active sessions
        """
        valid_sessions = []
        invalid_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if session.is_valid():
                valid_sessions.append(session.to_dict())
            else:
                invalid_sessions.append(session_id)
        
        # Clean up invalid sessions
        for session_id in invalid_sessions:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
        
        return valid_sessions
    
    def invalidate_all_sessions(self) -> int:
        """
        Invalidate all sessions
        
        Returns:
            int: Number of invalidated sessions
        """
        count = len(self.active_sessions)
        self.active_sessions.clear()
        return count
    
    def is_valid_session(self, session_id: str) -> bool:
        """
        Check if a session is valid
        
        Args:
            session_id (str): Session ID
            
        Returns:
            bool: True if valid, False otherwise
        """
        if session_id not in self.active_sessions:
            return False
            
        session = self.active_sessions[session_id]
        
        if not session.is_valid():
            # Session expired
            del self.active_sessions[session_id]
            return False
            
        return True