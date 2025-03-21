#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simplified User Module for Persian Life Manager
This module provides a consistent user model for the desktop application
"""

import uuid
import time
import datetime
import logging
import json
import os

logger = logging.getLogger(__name__)

class SimpleUser:
    """
    Universal Simple User class that works across all modules
    without external dependencies on Supabase or Firebase
    """
    
    def __init__(self, id=None, username=None, email=None, name=None, is_guest=False):
        """
        Initialize a user with all required fields across the application
        
        Args:
            id (str, optional): User ID. If None, a UUID will be generated.
            username (str, optional): Username. If None, will use name or "Guest".
            email (str, optional): Email. If None, a placeholder will be used.
            name (str, optional): Full name. If None, will use username.
            is_guest (bool, optional): Whether the user is a guest. Defaults to False.
        """
        # Essential identifiers
        self.id = id or str(uuid.uuid4())
        self.user_id = self.id  # For compatibility with some modules
        
        # Essential attributes
        self.username = username or name or "کاربر"  # username is required
        self.name = name or username or "کاربر"      # name is also required
        self.email = email or f"{self.id}@guest.persianlifemanager.app"
        self.is_guest = is_guest
        
        # Time tracking
        self.created_at = time.time()
        self.last_login = time.time()
        self.login_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Settings and data
        self.preferences = {}
        self.metadata = {}
    
    def to_dict(self):
        """
        Convert user to dictionary for serialization
        
        Returns:
            dict: User data as dictionary
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'is_guest': self.is_guest,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'login_time': self.login_time,
            'preferences': self.preferences,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a user from dictionary data
        
        Args:
            data (dict): User data dictionary
            
        Returns:
            SimpleUser: User object
        """
        user = cls(
            id=data.get('id') or data.get('user_id'),
            username=data.get('username'),
            email=data.get('email'),
            name=data.get('name'),
            is_guest=data.get('is_guest', False)
        )
        
        # Set additional attributes if available
        if 'created_at' in data:
            user.created_at = data['created_at']
        
        if 'last_login' in data:
            user.last_login = data['last_login']
        
        if 'login_time' in data:
            user.login_time = data['login_time']
        
        if 'preferences' in data and data['preferences']:
            user.preferences = data['preferences']
        
        if 'metadata' in data and data['metadata']:
            user.metadata = data['metadata']
        
        return user
    
    def save_to_file(self, filepath=None):
        """
        Save user data to a JSON file
        
        Args:
            filepath (str, optional): Path to save file. If None, uses default location.
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if filepath is None:
                # Default user data location
                user_data_dir = os.path.join(os.path.expanduser('~'), '.persian_life_manager', 'user_data')
                os.makedirs(user_data_dir, exist_ok=True)
                filepath = os.path.join(user_data_dir, f"user_{self.id}.json")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
            
            logger.info(f"User data saved to {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving user data: {str(e)}")
            return False
    
    @classmethod
    def load_from_file(cls, user_id=None, filepath=None):
        """
        Load user data from a JSON file
        
        Args:
            user_id (str, optional): User ID to load. Required if filepath is None.
            filepath (str, optional): Path to load file from. If None, uses default location.
            
        Returns:
            SimpleUser: User object or None if loading failed
        """
        try:
            if filepath is None:
                if user_id is None:
                    logger.error("Either user_id or filepath must be provided")
                    return None
                
                # Default user data location
                user_data_dir = os.path.join(os.path.expanduser('~'), '.persian_life_manager', 'user_data')
                filepath = os.path.join(user_data_dir, f"user_{user_id}.json")
            
            if not os.path.exists(filepath):
                logger.warning(f"User data file not found: {filepath}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            return cls.from_dict(user_data)
        
        except Exception as e:
            logger.error(f"Error loading user data: {str(e)}")
            return None
    
    @staticmethod
    def create_guest_user():
        """
        Create a new guest user
        
        Returns:
            SimpleUser: Guest user object
        """
        guest_id = f"guest-{int(time.time())}"
        return SimpleUser(
            id=guest_id,
            username="کاربر مهمان",
            name="کاربر مهمان",
            email=f"{guest_id}@guest.persianlifemanager.app",
            is_guest=True
        )
    
    def __str__(self):
        return f"SimpleUser(id={self.id}, username={self.username}, is_guest={self.is_guest})"
    
    def __repr__(self):
        return self.__str__()