#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database management for Persian Life Manager Application
"""

import os
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manage SQLite database connections and operations"""
    
    def __init__(self, db_path):
        """Initialize the database manager
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.ensure_dir_exists()
    
    def ensure_dir_exists(self):
        """Ensure the directory for the database exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_connection(self):
        """Get a database connection
        
        Returns:
            sqlite3.Connection: SQLite connection object
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def execute_query(self, query, params=None):
        """Execute a query and return the results
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Parameters for the query. Defaults to None.
            
        Returns:
            list: List of rows matching the query
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Database query error: {str(e)}")
            raise
    
    def execute_update(self, query, params=None):
        """Execute an update query (INSERT, UPDATE, DELETE)
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Parameters for the query. Defaults to None.
            
        Returns:
            int: Number of rows affected
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            row_count = cursor.rowcount
            conn.commit()
            conn.close()
            return row_count
        except Exception as e:
            logger.error(f"Database update error: {str(e)}")
            raise
    
    def execute_insert(self, query, params=None):
        """Execute an insert query and return the last row ID
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Parameters for the query. Defaults to None.
            
        Returns:
            int: ID of the last inserted row
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            last_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return last_id
        except Exception as e:
            logger.error(f"Database insert error: {str(e)}")
            raise
    
    def execute_script(self, script):
        """Execute multiple SQL statements
        
        Args:
            script (str): SQL script containing multiple statements
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.executescript(script)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Database script error: {str(e)}")
            raise
    
    def initialize_database(self):
        """Initialize the database schema if it doesn't exist"""
        # Check if database already exists
        if os.path.exists(self.db_path) and os.path.getsize(self.db_path) > 0:
            logger.info("Database already exists, skipping initialization")
            return
        
        logger.info("Initializing database schema")
        
        # Define database schema
        schema = """
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_login TEXT
        );
        
        -- Financial categories
        CREATE TABLE IF NOT EXISTS finance_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,  -- 'expense', 'income', or 'both'
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        
        -- Financial transactions
        CREATE TABLE IF NOT EXISTS finance_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,  -- 'expense' or 'income'
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES finance_categories (id) ON DELETE CASCADE
        );
        
        -- Health exercises
        CREATE TABLE IF NOT EXISTS health_exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            exercise_type TEXT NOT NULL,
            duration INTEGER NOT NULL,  -- Minutes
            calories_burned INTEGER NOT NULL,
            date TEXT NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        
        -- Health metrics
        CREATE TABLE IF NOT EXISTS health_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            weight REAL,
            systolic INTEGER,  -- Blood pressure (upper number)
            diastolic INTEGER,  -- Blood pressure (lower number)
            heart_rate INTEGER,
            sleep_hours REAL,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        
        -- Health goals
        CREATE TABLE IF NOT EXISTS health_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            goal_type TEXT NOT NULL,
            target_value REAL NOT NULL,
            deadline TEXT NOT NULL,  -- Date
            progress REAL NOT NULL DEFAULT 0,  -- Percentage
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        
        -- Calendar events
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            date TEXT NOT NULL,  -- Date
            start_time TEXT,  -- Time (HH:MM)
            end_time TEXT,  -- Time (HH:MM)
            location TEXT,
            description TEXT,
            all_day BOOLEAN NOT NULL DEFAULT 0,
            has_reminder BOOLEAN NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        
        -- Tasks
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            due_date TEXT NOT NULL,  -- Date
            priority TEXT NOT NULL,  -- 'low', 'medium', 'high'
            description TEXT,
            completed BOOLEAN NOT NULL DEFAULT 0,
            completion_date TEXT,  -- Date
            has_reminder BOOLEAN NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        
        -- Reminders
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            source_type TEXT NOT NULL,  -- 'event' or 'task'
            source_id INTEGER NOT NULL,  -- event_id or task_id
            reminder_time TEXT NOT NULL,  -- DateTime (YYYY-MM-DD HH:MM)
            status TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'triggered', 'dismissed'
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        
        -- User settings
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            setting_key TEXT NOT NULL,
            setting_value TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        
        -- Insert default categories
        INSERT INTO finance_categories (user_id, name, type, created_at)
        VALUES
            (1, 'خوراک', 'expense', datetime('now')),
            (1, 'مسکن', 'expense', datetime('now')),
            (1, 'حمل و نقل', 'expense', datetime('now')),
            (1, 'قبوض', 'expense', datetime('now')),
            (1, 'تفریح', 'expense', datetime('now')),
            (1, 'پوشاک', 'expense', datetime('now')),
            (1, 'آموزش', 'expense', datetime('now')),
            (1, 'درمان', 'expense', datetime('now')),
            (1, 'حقوق', 'income', datetime('now')),
            (1, 'پاداش', 'income', datetime('now')),
            (1, 'درآمد متفرقه', 'income', datetime('now'));
        """
        
        try:
            self.execute_script(schema)
            logger.info("Database schema initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {str(e)}")
            raise
    
    def backup_database(self, backup_path):
        """Create a backup of the database
        
        Args:
            backup_path (str): Path to save the backup file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.db_path):
                logger.error("Database does not exist, cannot create backup")
                return False
            
            # Ensure backup directory exists
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Open the database and backup file
            source_conn = sqlite3.connect(self.db_path)
            backup_conn = sqlite3.connect(backup_path)
            
            # Create backup
            source_conn.backup(backup_conn)
            
            # Close connections
            source_conn.close()
            backup_conn.close()
            
            logger.info(f"Database backup created at {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Database backup error: {str(e)}")
            return False
    
    def restore_database(self, backup_path):
        """Restore database from a backup
        
        Args:
            backup_path (str): Path to the backup file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup file {backup_path} does not exist")
                return False
            
            # Ensure database directory exists
            self.ensure_dir_exists()
            
            # Open the backup and database files
            backup_conn = sqlite3.connect(backup_path)
            target_conn = sqlite3.connect(self.db_path)
            
            # Restore database
            backup_conn.backup(target_conn)
            
            # Close connections
            backup_conn.close()
            target_conn.close()
            
            logger.info(f"Database restored from {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Database restore error: {str(e)}")
            return False
