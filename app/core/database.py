#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database utilities for Persian Life Manager Application
"""

import os
import sqlite3
import logging
import time
from typing import List, Dict, Any, Union, Optional, Tuple

logger = logging.getLogger(__name__)

class DatabaseManager:
    """SQLite database manager for Persian Life Manager"""
    
    def __init__(self, db_path: str):
        """Initialize the database manager
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize the database file and structure"""
        # Create directory if it doesn't exist
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # Create database file if it doesn't exist
        if not os.path.exists(self.db_path):
            logger.info(f"Creating new database at {self.db_path}")
            self._create_schema()
        else:
            logger.info("Database already exists, skipping initialization")
    
    def _create_schema(self):
        """Create the initial database schema"""
        try:
            # Create users table
            self.execute_query("""
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
            
            # Create finance_categories table
            self.execute_query("""
                CREATE TABLE IF NOT EXISTS finance_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    type TEXT,
                    created_at TEXT
                )
            """)
            
            # Create finance_transactions table
            self.execute_query("""
                CREATE TABLE IF NOT EXISTS finance_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    category_id INTEGER,
                    title TEXT,
                    amount REAL,
                    type TEXT,
                    date TEXT,
                    description TEXT,
                    created_at TEXT,
                    FOREIGN KEY (category_id) REFERENCES finance_categories (id)
                )
            """)
            
            # Create health_exercises table
            self.execute_query("""
                CREATE TABLE IF NOT EXISTS health_exercises (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date TEXT,
                    exercise_type TEXT,
                    duration INTEGER,
                    calories_burned INTEGER,
                    notes TEXT,
                    created_at TEXT
                )
            """)
            
            # Create health_metrics table
            self.execute_query("""
                CREATE TABLE IF NOT EXISTS health_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date TEXT,
                    weight REAL,
                    systolic INTEGER,
                    diastolic INTEGER,
                    heart_rate INTEGER,
                    sleep_hours REAL,
                    stress_level INTEGER,
                    notes TEXT,
                    created_at TEXT
                )
            """)
            
            # Create health_goals table
            self.execute_query("""
                CREATE TABLE IF NOT EXISTS health_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    goal_type TEXT,
                    target_value REAL,
                    current_value REAL,
                    start_date TEXT,
                    target_date TEXT,
                    completed INTEGER,
                    notes TEXT,
                    created_at TEXT
                )
            """)
            
            # Create calendar_events table
            self.execute_query("""
                CREATE TABLE IF NOT EXISTS calendar_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT,
                    date TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    location TEXT,
                    description TEXT,
                    all_day INTEGER,
                    has_reminder INTEGER,
                    reminder_time TEXT,
                    created_at TEXT
                )
            """)
            
            # Create calendar_tasks table
            self.execute_query("""
                CREATE TABLE IF NOT EXISTS calendar_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT,
                    due_date TEXT,
                    priority TEXT,
                    completed INTEGER,
                    has_reminder INTEGER,
                    reminder_time TEXT,
                    notes TEXT,
                    created_at TEXT
                )
            """)
            
            # Create calendar_reminders table
            self.execute_query("""
                CREATE TABLE IF NOT EXISTS calendar_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    item_id INTEGER,
                    item_type TEXT,
                    reminder_time TEXT,
                    notified INTEGER,
                    created_at TEXT
                )
            """)
            
            # Create user_settings table
            self.execute_query("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    theme TEXT,
                    language TEXT,
                    reminder_default_time INTEGER,
                    reminder_default_unit TEXT,
                    backup_location TEXT,
                    backup_frequency TEXT,
                    last_backup TEXT,
                    created_at TEXT
                )
            """)
            
            # Create default categories
            self._create_default_categories()
            
            logger.info("Database schema created successfully")
        except Exception as e:
            logger.error(f"Error creating database schema: {str(e)}")
            raise
    
    def _create_default_categories(self):
        """Create default finance categories"""
        default_categories = [
            # Income categories
            (0, "حقوق", "income"),
            (0, "سود سرمایه‌گذاری", "income"),
            (0, "هدیه", "income"),
            (0, "درآمد فریلنسری", "income"),
            (0, "سایر درآمدها", "income"),
            
            # Expense categories
            (0, "مسکن", "expense"),
            (0, "خوراک", "expense"),
            (0, "حمل و نقل", "expense"),
            (0, "قبوض", "expense"),
            (0, "سلامت", "expense"),
            (0, "سرگرمی", "expense"),
            (0, "آموزش", "expense"),
            (0, "پوشاک", "expense"),
            (0, "سایر هزینه‌ها", "expense")
        ]
        
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        
        for category in default_categories:
            query = """
                INSERT INTO finance_categories (user_id, name, type, created_at)
                VALUES (?, ?, ?, ?)
            """
            self.execute_insert(query, (category[0], category[1], category[2], now))
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection
        
        Returns:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query and return the results
        
        Args:
            query (str): SQL query
            params (tuple, optional): Query parameters
            
        Returns:
            list: List of dictionaries with query results
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith(("SELECT", "PRAGMA")):
                results = [dict(row) for row in cursor.fetchall()]
                return results
            
            conn.commit()
            return []
        except Exception as e:
            conn.rollback()
            logger.error(f"Error executing query: {str(e)}")
            raise
        finally:
            conn.close()
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an insert query and return the new row ID
        
        Args:
            query (str): SQL insert query
            params (tuple, optional): Query parameters
            
        Returns:
            int: ID of the new row
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            logger.error(f"Error executing insert: {str(e)}")
            raise
        finally:
            conn.close()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an update query and return the number of affected rows
        
        Args:
            query (str): SQL update query
            params (tuple, optional): Query parameters
            
        Returns:
            int: Number of affected rows
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            logger.error(f"Error executing update: {str(e)}")
            raise
        finally:
            conn.close()
    
    def execute_batch(self, query: str, params_list: List[tuple]) -> int:
        """Execute a batch of queries
        
        Args:
            query (str): SQL query
            params_list (list): List of parameter tuples
            
        Returns:
            int: Number of operations
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            logger.error(f"Error executing batch: {str(e)}")
            raise
        finally:
            conn.close()
    
    def execute_script(self, script: str) -> None:
        """Execute a SQL script
        
        Args:
            script (str): SQL script with multiple statements
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.executescript(script)
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error executing script: {str(e)}")
            raise
        finally:
            conn.close()
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database
        
        Args:
            backup_path (str): Path for the backup file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            backup_dir = os.path.dirname(backup_path)
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Create a new connection to the backup file
            source_conn = self.get_connection()
            dest_conn = sqlite3.connect(backup_path)
            
            # Copy data
            source_conn.backup(dest_conn)
            
            # Close connections
            source_conn.close()
            dest_conn.close()
            
            logger.info(f"Database backup created at {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error backing up database: {str(e)}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """Restore database from a backup
        
        Args:
            backup_path (str): Path to the backup file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Create a new connection to the backup file
            source_conn = sqlite3.connect(backup_path)
            dest_conn = self.get_connection()
            
            # Copy data
            source_conn.backup(dest_conn)
            
            # Close connections
            source_conn.close()
            dest_conn.close()
            
            logger.info(f"Database restored from {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error restoring database: {str(e)}")
            return False