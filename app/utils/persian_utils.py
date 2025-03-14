#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Persian language and culture utilities for Persian Life Manager Application
"""

import logging
from datetime import datetime
import jdatetime

logger = logging.getLogger(__name__)

def get_persian_month_name(month_number):
    """Get Persian month name from month number (1-12)
    
    Args:
        month_number (int): Month number (1-12)
        
    Returns:
        str: Persian month name
    """
    persian_months = [
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    ]
    
    try:
        # Adjust month number to 0-based index
        if isinstance(month_number, str):
            month_number = int(month_number)
            
        month_index = month_number - 1
        
        if 0 <= month_index < len(persian_months):
            return persian_months[month_index]
        else:
            logger.warning(f"Invalid month number: {month_number}")
            return "نامشخص"
    except (ValueError, TypeError) as e:
        logger.error(f"Error getting Persian month name: {str(e)}")
        return "نامشخص"

def get_persian_weekday_name(weekday):
    """Get Persian weekday name from Qt weekday number (1-7, Monday=1)
    
    Args:
        weekday (int): Qt weekday number (1-7, Monday=1)
        
    Returns:
        str: Persian weekday name
    """
    # Convert Qt weekdays (Monday=1) to Python weekdays (Monday=0)
    python_weekday = weekday - 1 if weekday > 0 else 6
    
    # Convert to Persian weekdays (Saturday=0)
    persian_weekday = (python_weekday + 2) % 7
    
    persian_weekdays = [
        "شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"
    ]
    
    try:
        return persian_weekdays[persian_weekday]
    except IndexError:
        logger.error(f"Invalid weekday number: {weekday}")
        return "نامشخص"

def format_currency(amount):
    """Format a number as Persian currency (Toman)
    
    Args:
        amount (float): Amount to format
        
    Returns:
        str: Formatted amount
    """
    try:
        return f"{int(amount):,} تومان"
    except (ValueError, TypeError) as e:
        logger.error(f"Error formatting currency: {str(e)}")
        return "0 تومان"

def convert_latin_numbers_to_persian(text):
    """Convert Latin numbers in a text to Persian numbers
    
    Args:
        text (str): Text containing Latin numbers
        
    Returns:
        str: Text with Persian numbers
    """
    if not text:
        return ""
        
    persian_numbers = "۰۱۲۳۴۵۶۷۸۹"
    latin_numbers = "0123456789"
    
    translation_table = str.maketrans(latin_numbers, persian_numbers)
    return text.translate(translation_table)

def convert_persian_numbers_to_latin(text):
    """Convert Persian numbers in a text to Latin numbers
    
    Args:
        text (str): Text containing Persian numbers
        
    Returns:
        str: Text with Latin numbers
    """
    if not text:
        return ""
        
    persian_numbers = "۰۱۲۳۴۵۶۷۸۹"
    latin_numbers = "0123456789"
    
    translation_table = str.maketrans(persian_numbers, latin_numbers)
    return text.translate(translation_table)

def get_persian_ordinal_suffix(number):
    """Get Persian ordinal suffix for numbers
    
    Args:
        number (int): Number to get suffix for
        
    Returns:
        str: Number with Persian ordinal suffix
    """
    try:
        return f"{number}م"
    except (ValueError, TypeError) as e:
        logger.error(f"Error getting Persian ordinal suffix: {str(e)}")
        return "0م"

def get_season_from_month(month):
    """Get Persian season name from month number
    
    Args:
        month (int): Month number (1-12)
        
    Returns:
        str: Persian season name
    """
    try:
        if 1 <= month <= 3:
            return "بهار"
        elif 4 <= month <= 6:
            return "تابستان"
        elif 7 <= month <= 9:
            return "پاییز"
        elif 10 <= month <= 12:
            return "زمستان"
        else:
            logger.warning(f"Invalid month number: {month}")
            return "نامشخص"
    except (ValueError, TypeError) as e:
        logger.error(f"Error getting season from month: {str(e)}")
        return "نامشخص"

def is_persian_holiday(date):
    """Check if a date is a Persian holiday
    
    Args:
        date (jdatetime.date): Persian date to check
        
    Returns:
        bool: True if the date is a holiday, False otherwise
    """
    try:
        # This is a simplified version, a real implementation would have a 
        # database or API for Persian holidays
        
        # Check for Fridays (weekday 6)
        if date.weekday() == 6:
            return True
        
        # Check for some major holidays (very simplified)
        if date.month == 1 and 1 <= date.day <= 4:  # Nowruz
            return True
        if date.month == 1 and date.day == 13:  # Sizdah Bedar
            return True
        
        # Add more holidays as needed
        
        return False
    except Exception as e:
        logger.error(f"Error checking Persian holiday: {str(e)}")
        return False
