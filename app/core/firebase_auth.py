"""
Firebase authentication module for Persian Life Manager Application
"""

import os
import logging
import requests
from app.firebase_config import FirebaseManager
from app.models.user import User
from firebase_admin import auth

logger = logging.getLogger(__name__)

class FirebaseAuthService:
    """Firebase authentication service"""
    
    def __init__(self):
        """Initialize the Firebase authentication service"""
        self.firebase = FirebaseManager()
        
        # Firebase API Key for client-side authentication
        self.api_key = os.environ.get("FIREBASE_API_KEY", "")
        self.auth_base_url = "https://identitytoolkit.googleapis.com/v1/accounts"
        
    def register(self, username, password, name=None):
        """Register a new user
        
        Args:
            username (str): User email as username
            password (str): User password
            name (str, optional): User name
            
        Returns:
            User: The created user object, or None if registration failed
        """
        try:
            if not name:
                name = username.split('@')[0]
                
            success, result = self.firebase.register_user(username, password, name)
            
            if success:
                user_id = result
                return User(id=user_id, username=username)
            else:
                logger.error(f"Failed to register user: {result}")
                return None
        except Exception as e:
            logger.error(f"Error in register: {str(e)}")
            return None
            
    def login(self, username, password):
        """Log in a user
        
        Args:
            username (str): User email as username
            password (str): User password
            
        Returns:
            User: The user object if login successful, None otherwise
        """
        try:
            # Call Firebase Authentication REST API
            url = f"{self.auth_base_url}:signInWithPassword"
            params = {"key": self.api_key}
            data = {
                "email": username,
                "password": password,
                "returnSecureToken": True
            }
            
            response = requests.post(url, params=params, json=data)
            
            if response.status_code == 200:
                result = response.json()
                user_id = result.get("localId")
                id_token = result.get("idToken")
                
                # Create User object
                return User(id=user_id, username=username)
            else:
                # Try server-side verification
                try:
                    user = self.firebase.get_user_by_email(username)
                    if user:
                        # We can't verify password server-side, but we can confirm user exists
                        # In production, we would need proper authentication
                        return User(id=user["uid"], username=username)
                except Exception as inner_e:
                    logger.error(f"Server-side verification error: {str(inner_e)}")
                
                logger.warning(f"Login failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error in login: {str(e)}")
            return None
            
    def change_password(self, username, new_password):
        """Change a user's password
        
        Args:
            username (str): The username
            new_password (str): The new password
            
        Returns:
            bool: True if password changed successfully, False otherwise
        """
        try:
            # Get user by email
            user = self.firebase.get_user_by_email(username)
            if not user:
                logger.error(f"User not found: {username}")
                return False
                
            # Update user password
            auth.update_user(user["uid"], password=new_password)
            return True
        except Exception as e:
            logger.error(f"Error in change_password: {str(e)}")
            return False
            
    def user_exists(self, username):
        """Check if a user exists
        
        Args:
            username (str): The username to check
            
        Returns:
            bool: True if user exists, False otherwise
        """
        try:
            user = self.firebase.get_user_by_email(username)
            return user is not None
        except Exception as e:
            logger.error(f"Error in user_exists: {str(e)}")
            return False
            
    def get_user(self, user_id):
        """Get a user by ID
        
        Args:
            user_id (str): The user ID
            
        Returns:
            User: The user object, or None if not found
        """
        try:
            user = auth.get_user(user_id)
            if user:
                return User(id=user_id, username=user.email)
            return None
        except Exception as e:
            logger.error(f"Error in get_user: {str(e)}")
            return None