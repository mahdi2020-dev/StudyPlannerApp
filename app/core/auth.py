#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Authentication service for Persian Life Manager
"""

import logging
import hashlib
import os
import secrets
import time
from typing import Tuple, Optional

from app.core.database import DatabaseManager

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service for user management and authentication"""
    
    def __init__(self, db_path=None):
        """Initialize the authentication service
        
        Args:
            db_path (str, optional): Path to the database file. If None, uses default path.
        """
        if not db_path:
            db_path = os.path.join(os.path.expanduser("~"), '.persian_life_manager', 'database.db')
        
        self.db_manager = DatabaseManager(db_path)
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize the database schema for authentication"""
        try:
            # Create users table if not exists
            self.db_manager.execute_query("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE,
                    password_hash TEXT,
                    name TEXT,
                    salt TEXT,
                    created_at TEXT,
                    last_login TEXT
                )
            """)
        except Exception as e:
            logger.error(f"Error initializing authentication database: {str(e)}")
            raise
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash a password with a salt
        
        Args:
            password (str): Plain text password
            salt (str, optional): Salt to use. If None, a new salt is generated.
            
        Returns:
            tuple: (password_hash, salt)
        """
        if not salt:
            salt = secrets.token_hex(16)
        
        # Use SHA-256 for password hashing
        hash_obj = hashlib.sha256((password + salt).encode())
        password_hash = hash_obj.hexdigest()
        
        return password_hash, salt
    
    def register_user(self, email: str, password: str, name: str) -> Tuple[bool, str]:
        """Register a new user
        
        Args:
            email (str): User's email
            password (str): Plain text password
            name (str): User's name
            
        Returns:
            tuple: (success, user_id or error_message)
        """
        try:
            # Check if email already exists
            query = "SELECT id FROM users WHERE email = ?"
            results = self.db_manager.execute_query(query, (email,))
            
            if results:
                return False, "Email already exists"
            
            # Hash the password
            password_hash, salt = self._hash_password(password)
            
            # Insert the new user
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            query = """
                INSERT INTO users (email, password_hash, name, salt, created_at, last_login)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            user_id = self.db_manager.execute_insert(
                query, (email, password_hash, name, salt, now, now)
            )
            
            return True, str(user_id)
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            return False, str(e)
    
    def login_user(self, email: str, password: str) -> Tuple[bool, str]:
        """Authenticate a user
        
        Args:
            email (str): User's email
            password (str): Plain text password
            
        Returns:
            tuple: (success, user_id or error_message)
        """
        try:
            # Get the user's info
            query = "SELECT id, password_hash, salt FROM users WHERE email = ?"
            results = self.db_manager.execute_query(query, (email,))
            
            if not results:
                return False, "Invalid email or password"
            
            user_id = results[0]['id']
            password_hash = results[0]['password_hash']
            salt = results[0]['salt']
            
            # Check the password
            calculated_hash, _ = self._hash_password(password, salt)
            
            if calculated_hash != password_hash:
                return False, "Invalid email or password"
            
            # Update last login time
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            update_query = "UPDATE users SET last_login = ? WHERE id = ?"
            self.db_manager.execute_update(update_query, (now, user_id))
            
            return True, str(user_id)
        except Exception as e:
            logger.error(f"Error logging in user: {str(e)}")
            return False, str(e)
    
    def get_user_by_id(self, user_id: str) -> dict:
        """Get user information by ID
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: User information (excluding password and salt)
        """
        try:
            query = "SELECT id, email, name, created_at, last_login FROM users WHERE id = ?"
            results = self.db_manager.execute_query(query, (user_id,))
            
            if not results:
                return None
            
            return results[0]
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> dict:
        """Get user information by email
        
        Args:
            email (str): User email
            
        Returns:
            dict: User information (excluding password and salt)
        """
        try:
            query = "SELECT id, email, name, created_at, last_login FROM users WHERE email = ?"
            results = self.db_manager.execute_query(query, (email,))
            
            if not results:
                return None
            
            return results[0]
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            return None
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change a user's password
        
        Args:
            user_id (str): User ID
            current_password (str): Current password
            new_password (str): New password
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Verify current password
            query = "SELECT password_hash, salt FROM users WHERE id = ?"
            results = self.db_manager.execute_query(query, (user_id,))
            
            if not results:
                return False
            
            password_hash = results[0]['password_hash']
            salt = results[0]['salt']
            
            calculated_hash, _ = self._hash_password(current_password, salt)
            
            if calculated_hash != password_hash:
                return False
            
            # Hash the new password
            new_password_hash, new_salt = self._hash_password(new_password)
            
            # Update the password
            update_query = "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?"
            result = self.db_manager.execute_update(
                update_query, (new_password_hash, new_salt, user_id)
            )
            
            return result > 0
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            return False
    
    def update_user_profile(self, user_id: str, name: str) -> bool:
        """Update a user's profile information
        
        Args:
            user_id (str): User ID
            name (str): New name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            update_query = "UPDATE users SET name = ? WHERE id = ?"
            result = self.db_manager.execute_update(update_query, (name, user_id))
            
            return result > 0
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return False