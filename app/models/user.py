#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
User-related data models for Persian Life Manager Application
"""

class User:
    """User model compatible with auth.User"""
    
    def __init__(self, user_id, name=None, email=None, username=None, is_guest=False):
        """Initialize a user
        
        Args:
            user_id (str): User ID
            name (str, optional): User's full name. Defaults to None.
            email (str, optional): User's email address. Defaults to None.
            username (str, optional): Username. Defaults to None.
            is_guest (bool, optional): Whether this is a guest user. Defaults to False.
        """
        import time
        
        self.id = user_id
        self.user_id = user_id  # متغیر مترادف با id
        self.name = name or username or "کاربر"
        self.username = username or name or "کاربر" 
        self.email = email or f"{user_id}@guest.persianlifemanager.app"
        self.is_guest = is_guest
        self.created_at = time.time()
        self.last_login = time.time()
        self.login_time = None  # زمان ورود به فرمت رشته‌ای
        self.preferences = {}   # تنظیمات کاربر
        self.metadata = {}      # داده‌های اضافی
    
    def __str__(self):
        return f"User({self.id}, {self.name}, {self.email}, Guest={self.is_guest})"


class UserSettings:
    """User settings model"""
    
    def __init__(self, user_id, settings_dict=None):
        """Initialize user settings
        
        Args:
            user_id (int): User ID
            settings_dict (dict, optional): Dictionary of settings
        """
        self.user_id = user_id
        self.settings = settings_dict or {}
    
    def get(self, key, default=None):
        """Get a setting value
        
        Args:
            key (str): Setting key
            default: Default value if setting doesn't exist
            
        Returns:
            The setting value or default
        """
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value
        
        Args:
            key (str): Setting key
            value: Setting value
        """
        self.settings[key] = value
    
    def delete(self, key):
        """Delete a setting
        
        Args:
            key (str): Setting key
            
        Returns:
            bool: True if the setting was deleted, False if it didn't exist
        """
        if key in self.settings:
            del self.settings[key]
            return True
        return False
    
    def __str__(self):
        return f"UserSettings({self.user_id}, {len(self.settings)} settings)"
