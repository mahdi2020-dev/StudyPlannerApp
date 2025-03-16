"""
Calendar Converter Service for Persian Life Manager Application
Provides conversion between Persian (Jalali) and Gregorian calendars
"""
import logging
import jdatetime
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CalendarConverter:
    """Service for calendar date conversion and management"""
    
    def __init__(self):
        """Initialize the Calendar Converter Service"""
        pass
    
    def gregorian_to_persian(self, date_str):
        """Convert Gregorian date to Persian date
        
        Args:
            date_str (str): Gregorian date string in YYYY-MM-DD format
            
        Returns:
            str: Persian date string in YYYY/MM/DD format
        """
        try:
            if isinstance(date_str, str):
                # Parse the Gregorian date
                year, month, day = map(int, date_str.split('-'))
                gregorian_date = datetime(year, month, day)
            else:
                gregorian_date = date_str
                
            # Convert to Persian date
            persian_date = jdatetime.date.fromgregorian(date=gregorian_date)
            
            # Format as string YYYY/MM/DD
            return persian_date.strftime("%Y/%m/%d")
        except Exception as e:
            logger.error(f"Error converting to Persian date: {str(e)}")
            return None
    
    def persian_to_gregorian(self, date_str):
        """Convert Persian date to Gregorian date
        
        Args:
            date_str (str): Persian date string in YYYY/MM/DD format
            
        Returns:
            str: Gregorian date string in YYYY-MM-DD format
        """
        try:
            if isinstance(date_str, str):
                # Parse the Persian date
                year, month, day = map(int, date_str.split('/'))
                persian_date = jdatetime.date(year, month, day)
            else:
                persian_date = date_str
                
            # Convert to Gregorian date
            gregorian_date = persian_date.togregorian()
            
            # Format as string YYYY-MM-DD
            return gregorian_date.strftime("%Y-%m-%d")
        except Exception as e:
            logger.error(f"Error converting to Gregorian date: {str(e)}")
            return None
    
    def get_persian_month_days(self, year, month):
        """Get number of days in a Persian month
        
        Args:
            year (int): Persian year
            month (int): Persian month
            
        Returns:
            int: Number of days in the month
        """
        try:
            if month == 12:
                # Check if it's a leap year
                last_day = 29 if jdatetime.date(year, 12, 29).togregorian() < jdatetime.date(year, 12, 30).togregorian() else 30
                return last_day
            elif month <= 6:
                return 31
            else:
                return 30
        except Exception as e:
            logger.error(f"Error getting Persian month days: {str(e)}")
            return 30  # Default to 30 days
    
    def get_persian_weekday(self, date_str):
        """Get Persian weekday name for a date
        
        Args:
            date_str (str): Date string in YYYY/MM/DD or YYYY-MM-DD format
            
        Returns:
            str: Persian weekday name
        """
        try:
            # Determine format and parse date
            if '/' in date_str:
                # Persian format
                year, month, day = map(int, date_str.split('/'))
                date_obj = jdatetime.date(year, month, day)
            else:
                # Gregorian format
                year, month, day = map(int, date_str.split('-'))
                gregorian = datetime(year, month, day)
                date_obj = jdatetime.date.fromgregorian(date=gregorian)
            
            # Get weekday name in Persian
            weekday_names = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه", "یکشنبه"]
            return weekday_names[date_obj.weekday()]
        except Exception as e:
            logger.error(f"Error getting Persian weekday: {str(e)}")
            return None
    
    def get_persian_month_name(self, month):
        """Get Persian month name from month number
        
        Args:
            month (int): Month number (1-12)
            
        Returns:
            str: Persian month name
        """
        try:
            month_names = [
                "فروردین", "اردیبهشت", "خرداد",
                "تیر", "مرداد", "شهریور",
                "مهر", "آبان", "آذر", 
                "دی", "بهمن", "اسفند"
            ]
            return month_names[month - 1]
        except Exception as e:
            logger.error(f"Error getting Persian month name: {str(e)}")
            return None
    
    def get_persian_month_range(self, year, month):
        """Get start and end dates of a Persian month in Gregorian calendar
        
        Args:
            year (int): Persian year
            month (int): Persian month
            
        Returns:
            tuple: (start_date, end_date) as Gregorian dates in YYYY-MM-DD format
        """
        try:
            # Create Persian dates for first and last day of month
            first_day = jdatetime.date(year, month, 1)
            last_day = jdatetime.date(year, month, self.get_persian_month_days(year, month))
            
            # Convert to Gregorian
            start_date = first_day.togregorian().strftime("%Y-%m-%d")
            end_date = last_day.togregorian().strftime("%Y-%m-%d")
            
            return (start_date, end_date)
        except Exception as e:
            logger.error(f"Error getting Persian month range: {str(e)}")
            return None
    
    def get_current_persian_date(self):
        """Get current date in Persian calendar format
        
        Returns:
            str: Current date in Persian calendar format YYYY/MM/DD
        """
        try:
            today = jdatetime.date.today()
            return today.strftime("%Y/%m/%d")
        except Exception as e:
            logger.error(f"Error getting current Persian date: {str(e)}")
            return None
    
    def get_persian_holidays(self, year, month=None):
        """Get Persian holidays for a year or month
        
        Args:
            year (int): Persian year
            month (int, optional): Persian month. If None, returns for whole year.
            
        Returns:
            list: List of holiday dates with descriptions
        """
        # This is a simplified approach. A complete implementation would:
        # 1. Have a full database of official holidays
        # 2. Have both fixed (e.g., Nowruz) and lunar-based holidays (e.g., Eid al-Fitr)
        # 3. Calculate the exact dates for each year

        # Some fixed Persian holidays
        fixed_holidays = [
            {"month": 1, "day": 1, "description": "عید نوروز"},
            {"month": 1, "day": 2, "description": "عید نوروز"},
            {"month": 1, "day": 3, "description": "عید نوروز"},
            {"month": 1, "day": 4, "description": "عید نوروز"},
            {"month": 1, "day": 12, "description": "روز جمهوری اسلامی"},
            {"month": 1, "day": 13, "description": "روز طبیعت"},
            {"month": 3, "day": 14, "description": "رحلت امام خمینی"},
            {"month": 3, "day": 15, "description": "قیام ۱۵ خرداد"},
            {"month": 11, "day": 22, "description": "پیروزی انقلاب اسلامی"},
            {"month": 12, "day": 29, "description": "ملی شدن صنعت نفت"}
        ]
        
        # Filter by month if specified
        if month:
            holidays = [h for h in fixed_holidays if h["month"] == month]
        else:
            holidays = fixed_holidays
        
        # Format the dates as YYYY/MM/DD
        result = []
        for holiday in holidays:
            date_str = f"{year}/{holiday['month']:02d}/{holiday['day']:02d}"
            result.append({
                "date": date_str,
                "description": holiday["description"]
            })
        
        # In a complete implementation, lunar-based holidays would be calculated here
        # based on the specific year
        
        return result