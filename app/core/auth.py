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
import random
import string
from typing import Tuple, Optional, Dict

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
                    last_login TEXT,
                    is_active INTEGER DEFAULT 0,
                    activation_code TEXT,
                    activation_expiry TEXT
                )
            """)
            
            # Create a table for pending registrations
            self.db_manager.execute_query("""
                CREATE TABLE IF NOT EXISTS pending_registrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE,
                    password_hash TEXT,
                    name TEXT,
                    salt TEXT,
                    created_at TEXT,
                    activation_code TEXT,
                    activation_expiry TEXT
                )
            """)
        except Exception as e:
            logger.error(f"Error initializing authentication database: {str(e)}")
            raise
            
    def _generate_activation_code(self):
        """Generate a random 6-digit activation code
        
        Returns:
            str: 6-digit activation code
        """
        return ''.join(random.choices(string.digits, k=6))
    
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
            # Check if email already exists in users table
            query = "SELECT id FROM users WHERE email = ?"
            results = self.db_manager.execute_query(query, (email,))
            
            if results:
                return False, "email_exists"
                
            # Also check pending registrations
            query = "SELECT id FROM pending_registrations WHERE email = ?"
            results = self.db_manager.execute_query(query, (email,))
            
            # If already has a pending registration, we'll update it
            if results:
                # Delete the existing pending registration first
                delete_query = "DELETE FROM pending_registrations WHERE email = ?"
                self.db_manager.execute_update(delete_query, (email,))
            
            # Hash the password
            password_hash, salt = self._hash_password(password)
            
            # Generate activation code
            activation_code = self._generate_activation_code()
            
            # Set activation expiry (24 hours from now)
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            expiry = time.strftime(
                '%Y-%m-%d %H:%M:%S', 
                time.localtime(time.time() + 24 * 60 * 60)
            )
            
            # Insert into pending registrations
            query = """
                INSERT INTO pending_registrations (
                    email, password_hash, name, salt, created_at, 
                    activation_code, activation_expiry
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            registration_id = self.db_manager.execute_insert(
                query, 
                (email, password_hash, name, salt, now, activation_code, expiry)
            )
            
            if not registration_id:
                return False, "registration_failed"
                
            # In a real application, we would send the activation code via email
            # For testing purposes, we'll return the activation code
            return True, activation_code
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            return False, "system_error"
    
    def verify_activation(self, email: str, activation_code: str) -> Tuple[bool, str]:
        """Verify activation code and create the user account
        
        Args:
            email (str): User email
            activation_code (str): Activation code
            
        Returns:
            tuple: (success, user_id or error_message)
        """
        try:
            # Get the pending registration
            query = """
                SELECT * FROM pending_registrations 
                WHERE email = ? AND activation_code = ?
            """
            results = self.db_manager.execute_query(query, (email, activation_code))
            
            if not results:
                return False, "invalid_code"
                
            registration = results[0]
            
            # Check if code has expired
            expiry = registration['activation_expiry']
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            
            if expiry < now:
                return False, "code_expired"
                
            # Create the user account
            insert_query = """
                INSERT INTO users (
                    email, password_hash, name, salt, created_at, last_login,
                    is_active, activation_code, activation_expiry
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            user_id = self.db_manager.execute_insert(
                insert_query, 
                (
                    registration['email'], 
                    registration['password_hash'],
                    registration['name'],
                    registration['salt'],
                    registration['created_at'],
                    now,  # last_login
                    1,    # is_active
                    None, # activation_code (set to None once verified)
                    None  # activation_expiry (set to None once verified)
                )
            )
            
            if not user_id:
                return False, "activation_failed"
                
            # Delete the pending registration
            delete_query = "DELETE FROM pending_registrations WHERE id = ?"
            self.db_manager.execute_update(delete_query, (registration['id'],))
            
            return True, str(user_id)
        except Exception as e:
            logger.error(f"Error verifying activation: {str(e)}")
            return False, "system_error"
            
    def resend_activation_code(self, email: str) -> Tuple[bool, str]:
        """Resend activation code for a pending registration
        
        Args:
            email (str): User email
            
        Returns:
            tuple: (success, activation_code or error_message)
        """
        try:
            # Check if email exists in pending registrations
            query = "SELECT id FROM pending_registrations WHERE email = ?"
            results = self.db_manager.execute_query(query, (email,))
            
            if not results:
                return False, "not_found"
                
            # Generate new activation code
            activation_code = self._generate_activation_code()
            
            # Set new activation expiry (24 hours from now)
            expiry = time.strftime(
                '%Y-%m-%d %H:%M:%S', 
                time.localtime(time.time() + 24 * 60 * 60)
            )
            
            # Update the pending registration
            update_query = """
                UPDATE pending_registrations 
                SET activation_code = ?, activation_expiry = ?
                WHERE email = ?
            """
            
            result = self.db_manager.execute_update(
                update_query, (activation_code, expiry, email)
            )
            
            if not result:
                return False, "update_failed"
                
            # In a real application, we would send the activation code via email
            # For testing purposes, we'll return the activation code
            return True, activation_code
        except Exception as e:
            logger.error(f"Error resending activation code: {str(e)}")
            return False, "system_error"
    
    def login_user(self, email: str, password: str) -> Tuple[bool, str]:
        """Authenticate a user
        
        Args:
            email (str): User's email
            password (str): Plain text password
            
        Returns:
            tuple: (success, user_id or error_message)
        """
        try:
            # First check if this email has a pending registration
            query = "SELECT id FROM pending_registrations WHERE email = ?"
            results = self.db_manager.execute_query(query, (email,))
            
            if results:
                return False, "not_activated"
            
            # Get the user's info from active users
            query = "SELECT id, password_hash, salt, is_active FROM users WHERE email = ?"
            results = self.db_manager.execute_query(query, (email,))
            
            if not results:
                return False, "invalid_credentials"
            
            user_id = results[0]['id']
            password_hash = results[0]['password_hash']
            salt = results[0]['salt']
            is_active = results[0]['is_active']
            
            # Check if the account is active
            if not is_active:
                return False, "account_inactive"
            
            # Check the password
            calculated_hash, _ = self._hash_password(password, salt)
            
            if calculated_hash != password_hash:
                return False, "invalid_credentials"
            
            # Update last login time
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            update_query = "UPDATE users SET last_login = ? WHERE id = ?"
            self.db_manager.execute_update(update_query, (now, user_id))
            
            return True, str(user_id)
        except Exception as e:
            logger.error(f"Error logging in user: {str(e)}")
            return False, "system_error"
    
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