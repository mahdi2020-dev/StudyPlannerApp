#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Date utilities for Persian Life Manager Application
"""

import logging
from datetime import datetime, timedelta
import jdatetime

logger = logging.getLogger(__name__)

def get_current_persian_date():
    """Get current date in Persian calendar format (YYYY/MM/DD)
    
    Returns:
        str: Current date in Persian calendar format
    """
    try:
        today = jdatetime.date.today()
        return today.strftime("%Y/%m/%d")
    except Exception as e:
        logger.error(f"Error getting current Persian date: {str(e)}")
        # Fallback to returning gregorian date
        return datetime.now().strftime("%Y/%m/%d")

def gregorian_to_persian(date_str):
    """Convert Gregorian date to Persian date
    
    Args:
        date_str (str): Gregorian date string in YYYY-MM-DD format
        
    Returns:
        str: Persian date string in YYYY/MM/DD format
    """
    try:
        if not date_str:
            return ""
            
        if isinstance(date_str, datetime):
            gregorian_date = date_str.date()
        elif isinstance(date_str, str):
            gregorian_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            gregorian_date = date_str
            
        persian_date = jdatetime.date.fromgregorian(date=gregorian_date)
        return persian_date.strftime("%Y/%m/%d")
    except Exception as e:
        logger.error(f"Error converting Gregorian to Persian date: {str(e)}")
        return date_str

def persian_to_gregorian(date_str):
    """Convert Persian date to Gregorian date
    
    Args:
        date_str (str): Persian date string in YYYY/MM/DD format
        
    Returns:
        str: Gregorian date string in YYYY-MM-DD format
    """
    try:
        if not date_str:
            return ""
            
        # Parse Persian date
        year, month, day = map(int, date_str.split('/'))
        persian_date = jdatetime.date(year, month, day)
        
        # Convert to Gregorian
        gregorian_date = persian_date.togregorian()
        return gregorian_date.strftime("%Y-%m-%d")
    except Exception as e:
        logger.error(f"Error converting Persian to Gregorian date: {str(e)}")
        return date_str

def get_persian_month_start_end(year, month):
    """Get start and end dates of a Persian month in Gregorian calendar
    
    Args:
        year (int): Persian year
        month (int): Persian month
        
    Returns:
        tuple: (start_date, end_date) as Gregorian dates in YYYY-MM-DD format
    """
    try:
        # Create Persian date for first day of month
        persian_start = jdatetime.date(year, month, 1)
        
        # Get last day of month
        if month <= 6:
            last_day = 31
        elif month <= 11:
            last_day = 30
        else:  # month == 12
            if jdatetime.date(year, month, 1).isleap():
                last_day = 30
            else:
                last_day = 29
        
        persian_end = jdatetime.date(year, month, last_day)
        
        # Convert to Gregorian
        greg_start = persian_start.togregorian()
        greg_end = persian_end.togregorian()
        
        return (
            greg_start.strftime("%Y-%m-%d"),
            greg_end.strftime("%Y-%m-%d")
        )
    except Exception as e:
        logger.error(f"Error getting Persian month range: {str(e)}")
        # Return current month as fallback
        today = datetime.now()
        first_day = today.replace(day=1)
        last_day = (first_day.replace(month=first_day.month % 12 + 1, day=1) if first_day.month < 12 
                    else first_day.replace(year=first_day.year + 1, month=1, day=1)) - timedelta(days=1)
        return (
            first_day.strftime("%Y-%m-%d"),
            last_day.strftime("%Y-%m-%d")
        )

def get_persian_week_start_end(date_str=None):
    """Get start and end dates of the Persian week containing the given date
    
    In Persian calendar, week starts on Saturday and ends on Friday
    
    Args:
        date_str (str, optional): Date string in YYYY-MM-DD format.
                                 If None, uses current date.
    
    Returns:
        tuple: (start_date, end_date) as Gregorian dates in YYYY-MM-DD format
    """
    try:
        # Get reference date
        if date_str:
            ref_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            ref_date = datetime.now().date()
        
        # Convert to Persian
        persian_date = jdatetime.date.fromgregorian(date=ref_date)
        
        # Calculate days to Saturday (weekday 0 in Persian calendar)
        days_to_start = (persian_date.weekday()) % 7
        
        # Calculate start and end dates
        persian_start = persian_date - jdatetime.timedelta(days=days_to_start)
        persian_end = persian_start + jdatetime.timedelta(days=6)
        
        # Convert back to Gregorian
        greg_start = persian_start.togregorian()
        greg_end = persian_end.togregorian()
        
        return (
            greg_start.strftime("%Y-%m-%d"),
            greg_end.strftime("%Y-%m-%d")
        )
    except Exception as e:
        logger.error(f"Error getting Persian week range: {str(e)}")
        # Return current week as fallback (Monday to Sunday in Gregorian)
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        return (
            monday.strftime("%Y-%m-%d"),
            sunday.strftime("%Y-%m-%d")
        )

def format_relative_date(date_str):
    """Format a date relative to today (e.g., "امروز", "دیروز", "فردا")
    
    Args:
        date_str (str): Date string in YYYY-MM-DD format
        
    Returns:
        str: Relative date description in Persian
    """
    try:
        if not date_str:
            return ""
            
        # Parse date
        if isinstance(date_str, str):
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            date = date_str
            
        # Get today, yesterday, and tomorrow
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        # Compare dates
        if date == today:
            return "امروز"
        elif date == yesterday:
            return "دیروز"
        elif date == tomorrow:
            return "فردا"
        else:
            # Return Persian date
            return gregorian_to_persian(date)
    except Exception as e:
        logger.error(f"Error formatting relative date: {str(e)}")
        return date_str

def is_future_date(date_str):
    """Check if a date is in the future
    
    Args:
        date_str (str): Date string in YYYY-MM-DD format
        
    Returns:
        bool: True if date is in the future, False otherwise
    """
    try:
        if isinstance(date_str, str):
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            date = date_str
            
        today = datetime.now().date()
        return date > today
    except Exception as e:
        logger.error(f"Error checking future date: {str(e)}")
        return False

def is_past_date(date_str):
    """Check if a date is in the past
    
    Args:
        date_str (str): Date string in YYYY-MM-DD format
        
    Returns:
        bool: True if date is in the past, False otherwise
    """
    try:
        if isinstance(date_str, str):
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            date = date_str
            
        today = datetime.now().date()
        return date < today
    except Exception as e:
        logger.error(f"Error checking past date: {str(e)}")
        return False

def get_days_difference(date1, date2=None):
    """Get the number of days between two dates
    
    Args:
        date1 (str): First date in YYYY-MM-DD format
        date2 (str, optional): Second date in YYYY-MM-DD format. 
                              If None, uses current date.
        
    Returns:
        int: Number of days between dates
    """
    try:
        if isinstance(date1, str):
            date1 = datetime.strptime(date1, "%Y-%m-%d").date()
        
        if date2:
            if isinstance(date2, str):
                date2 = datetime.strptime(date2, "%Y-%m-%d").date()
        else:
            date2 = datetime.now().date()
            
        return abs((date2 - date1).days)
    except Exception as e:
        logger.error(f"Error calculating days difference: {str(e)}")
        return 0
