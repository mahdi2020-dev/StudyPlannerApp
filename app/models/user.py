#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
User-related data models for Persian Life Manager Application
"""

class User:
    """User model"""
    
    def __init__(self, id, username):
        """Initialize a user
        
        Args:
            id (int): User ID
            username (str): Username
        """
        self.id = id
        self.username = username
    
    def __str__(self):
        return f"User({self.id}, {self.username})"


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
