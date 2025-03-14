#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Authentication and user management for Persian Life Manager Application
"""

import os
import logging
import hashlib
import secrets
from datetime import datetime

from app.models.user import User
from app.core.database import DatabaseManager

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication and user management service"""
    
    def __init__(self, db_path=None):
        """Initialize the authentication service
        
        Args:
            db_path (str, optional): Path to the database file. If None, uses default path.
        """
        if not db_path:
            db_path = os.path.join(os.path.expanduser("~"), '.persian_life_manager', 'database.db')
        
        self.db_manager = DatabaseManager(db_path)
    
    def hash_password(self, password, salt=None):
        """Create a secure hash of the password
        
        Args:
            password (str): The password to hash
            salt (bytes, optional): Salt for hashing. If None, generates new salt.
            
        Returns:
            tuple: (hashed_password, salt)
        """
        if not salt:
            salt = secrets.token_bytes(32)
            
        # Create hash using PBKDF2 with 100,000 iterations
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        
        # Combine salt and hash for storage
        return salt + password_hash, salt
    
    def verify_password(self, username, password):
        """Verify if the provided password is correct for the user
        
        Args:
            username (str): The username
            password (str): The password to verify
            
        Returns:
            bool: True if password is correct, False otherwise
        """
        try:
            # Get the stored hash
            query = "SELECT password_hash FROM users WHERE username = ?"
            results = self.db_manager.execute_query(query, (username,))
            
            if not results:
                logger.warning(f"User {username} not found during password verification")
                return False
            
            stored_hash = results[0]['password_hash']
            
            # Extract salt from stored hash (first 32 bytes)
            salt = stored_hash[:32]
            
            # Hash the provided password with the same salt
            hashed_pw, _ = self.hash_password(password, salt)
            
            # Compare the hashes
            return hashed_pw == stored_hash
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False
    
    def register(self, username, password):
        """Register a new user
        
        Args:
            username (str): The username
            password (str): The password
            
        Returns:
            User: The created user object, or None if registration failed
        """
        try:
            # Check if username already exists
            if self.user_exists(username):
                logger.warning(f"Cannot register: Username {username} already exists")
                return None
            
            # Hash the password
            password_hash, _ = self.hash_password(password)
            
            # Create the user
            now = datetime.now().isoformat()
            query = """
                INSERT INTO users (username, password_hash, created_at, last_login)
                VALUES (?, ?, ?, ?)
            """
            
            user_id = self.db_manager.execute_insert(
                query, (username, password_hash, now, now)
            )
            
            if user_id:
                # Create user object
                user = User(user_id, username)
                logger.info(f"User {username} registered successfully")
                return user
            
            return None
        except Exception as e:
            logger.error(f"User registration error: {str(e)}")
            return None
    
    def login(self, username, password):
        """Log in a user
        
        Args:
            username (str): The username
            password (str): The password
            
        Returns:
            User: The user object if login successful, None otherwise
        """
        try:
            # Verify password
            if not self.verify_password(username, password):
                logger.warning(f"Login failed for user {username}: incorrect password")
                return None
            
            # Get user ID
            query = "SELECT id FROM users WHERE username = ?"
            results = self.db_manager.execute_query(query, (username,))
            
            if not results:
                logger.warning(f"Login failed: User {username} not found")
                return None
            
            user_id = results[0]['id']
            
            # Update last login time
            now = datetime.now().isoformat()
            update_query = "UPDATE users SET last_login = ? WHERE id = ?"
            self.db_manager.execute_update(update_query, (now, user_id))
            
            # Create user object
            user = User(user_id, username)
            logger.info(f"User {username} logged in successfully")
            
            return user
        except Exception as e:
            logger.error(f"User login error: {str(e)}")
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
            # Check if user exists
            if not self.user_exists(username):
                logger.warning(f"Cannot change password: User {username} does not exist")
                return False
            
            # Hash the new password
            password_hash, _ = self.hash_password(new_password)
            
            # Update the password
            query = "UPDATE users SET password_hash = ? WHERE username = ?"
            result = self.db_manager.execute_update(query, (password_hash, username))
            
            success = result > 0
            if success:
                logger.info(f"Password changed for user {username}")
            
            return success
        except Exception as e:
            logger.error(f"Password change error: {str(e)}")
            return False
    
    def user_exists(self, username):
        """Check if a user exists
        
        Args:
            username (str): The username to check
            
        Returns:
            bool: True if user exists, False otherwise
        """
        try:
            query = "SELECT id FROM users WHERE username = ?"
            results = self.db_manager.execute_query(query, (username,))
            
            return len(results) > 0
        except Exception as e:
            logger.error(f"User existence check error: {str(e)}")
            return False
    
    def get_user(self, user_id):
        """Get a user by ID
        
        Args:
            user_id (int): The user ID
            
        Returns:
            User: The user object, or None if not found
        """
        try:
            query = "SELECT id, username FROM users WHERE id = ?"
            results = self.db_manager.execute_query(query, (user_id,))
            
            if not results:
                logger.warning(f"User with ID {user_id} not found")
                return None
            
            user_data = results[0]
            user = User(user_data['id'], user_data['username'])
            
            return user
        except Exception as e:
            logger.error(f"Get user error: {str(e)}")
            return None
