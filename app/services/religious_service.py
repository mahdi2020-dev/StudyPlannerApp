"""
Religious Service for Persian Life Manager Application
Provides prayer times, religious events and daily prayers
"""
import os
import requests
import json
import logging
from datetime import datetime, timedelta
import jdatetime

logger = logging.getLogger(__name__)

class ReligiousService:
    """Service for religious information and prayers"""
    
    def __init__(self):
        """Initialize the Religious Service"""
        self.cache_dir = "app/data/cache"
        self.city = "Tehran"  # Default city
        self.country = "Iran"  # Default country
        self.prayer_times_cache = {}
        self.prayer_times_cache_expiry = {}
        self.prayer_times_api_url = "http://api.aladhan.com/v1/timingsByCity"
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def set_location(self, city, country):
        """Set the location for prayer times
        
        Args:
            city (str): City name
            country (str): Country name
        """
        self.city = city
        self.country = country
        # Clear cache when location changes
        self.prayer_times_cache = {}
        self.prayer_times_cache_expiry = {}
        
    def get_prayer_times(self, date_str=None):
        """Get prayer times for a specific date
        
        Args:
            date_str (str, optional): Date in YYYY-MM-DD format. If None, uses current date.
            
        Returns:
            dict: Prayer times for the specified date
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Check if cached data is available and valid
        if date_str in self.prayer_times_cache and datetime.now() < self.prayer_times_cache_expiry.get(date_str, datetime.now()):
            return self.prayer_times_cache[date_str]
        
        try:
            params = {
                "city": self.city,
                "country": self.country,
                "method": 7,  # 7 is Institute of Geophysics, University of Tehran
                "date": date_str
            }
            
            response = requests.get(self.prayer_times_api_url, params=params)
            data = response.json()
            
            if response.status_code == 200 and data.get("code") == 200:
                times = data.get("data", {}).get("timings", {})
                result = {
                    "fajr": times.get("Fajr", ""),
                    "sunrise": times.get("Sunrise", ""),
                    "dhuhr": times.get("Dhuhr", ""),
                    "asr": times.get("Asr", ""),
                    "maghrib": times.get("Maghrib", ""),
                    "isha": times.get("Isha", ""),
                    "midnight": times.get("Midnight", ""),
                    "date": date_str
                }
                
                # Cache the results for 24 hours
                self.prayer_times_cache[date_str] = result
                self.prayer_times_cache_expiry[date_str] = datetime.now() + timedelta(hours=24)
                
                return result
            else:
                logger.error(f"Error getting prayer times: {data.get('data')}")
                return self._get_fallback_prayer_times(date_str)
                
        except Exception as e:
            logger.error(f"Error in get_prayer_times: {str(e)}")
            return self._get_fallback_prayer_times(date_str)
    
    def _get_fallback_prayer_times(self, date_str):
        """Get fallback prayer times if API call fails
        
        Args:
            date_str (str): Date in YYYY-MM-DD format
            
        Returns:
            dict: Fallback prayer times
        """
        return {
            "fajr": "05:00",
            "sunrise": "06:30",
            "dhuhr": "12:00",
            "asr": "15:30",
            "maghrib": "18:00",
            "isha": "19:30",
            "midnight": "00:00",
            "date": date_str,
            "is_fallback": True
        }
    
    def get_daily_prayer(self):
        """Get a random daily prayer or dhikr
        
        Returns:
            dict: Prayer with translation
        """
        prayers = [
            {
                "arabic": "سُبْحَانَ اللهِ",
                "persian": "پاک و منزه است خداوند",
                "title": "تسبیح"
            },
            {
                "arabic": "اَلْحَمْدُ لِلّٰهِ",
                "persian": "ستایش برای خداست",
                "title": "حمد"
            },
            {
                "arabic": "لَا إِلَٰهَ إِلَّا ٱللَّٰهُ",
                "persian": "نیست معبودی جز الله",
                "title": "تهلیل"
            },
            {
                "arabic": "اللَّهُ أَكْبَرُ",
                "persian": "خدا بزرگتر است",
                "title": "تکبیر"
            },
            {
                "arabic": "لَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِٱللَّٰهِ",
                "persian": "هیچ نیرو و توانی نیست مگر از جانب خداوند",
                "title": "حوقله"
            },
            {
                "arabic": "أَسْتَغْفِرُ ٱللَّٰهَ",
                "persian": "از خداوند آمرزش می‌طلبم",
                "title": "استغفار"
            },
            {
                "arabic": "اللَّهُمَّ صَلِّ عَلَىٰ مُحَمَّدٍ وَآلِ مُحَمَّدٍ",
                "persian": "خدایا بر محمد و خاندان محمد درود فرست",
                "title": "صلوات"
            }
        ]
        
        # Use the current date to pick a prayer deterministically
        date = datetime.now()
        day_of_year = int(date.strftime("%j"))
        
        index = day_of_year % len(prayers)
        return prayers[index]
    
    def get_religious_events(self, year=None, month=None):
        """Get religious events for a specific month
        
        Args:
            year (int, optional): Persian year. If None, uses current year.
            month (int, optional): Persian month. If None, uses current month.
            
        Returns:
            list: Religious events for the specified month
        """
        if year is None or month is None:
            persian_date = jdatetime.date.today()
            if year is None:
                year = persian_date.year
            if month is None:
                month = persian_date.month
        
        # Hardcoded religious events based on Persian calendar
        events = []
        
        # Basic religious events (this is a simplified example, a complete implementation
        # would need a more comprehensive database with hijri calendar conversion)
        if month == 1:  # Farvardin
            events.append({
                "date": f"{year}/01/01",
                "title": "عید نوروز",
                "type": "cultural"
            })
            events.append({
                "date": f"{year}/01/13",
                "title": "سیزده بدر",
                "type": "cultural"
            })
        elif month == 9:  # Azar
            events.append({
                "date": f"{year}/09/30",
                "title": "شب یلدا",
                "type": "cultural"
            })
        
        # This is a simplified approach. A complete implementation would:
        # 1. Use a proper hijri-to-shamsi conversion
        # 2. Have a full database of religious events
        # 3. Calculate the exact dates for each year
        
        return events
    
    def get_religious_quote(self):
        """Get a random religious quote
        
        Returns:
            dict: Religious quote with source
        """
        quotes = [
            {
                "text": "هر کس در راه خدا تقوا پیشه کند، خداوند برای او راه نجاتی قرار می‌دهد",
                "source": "قرآن کریم، سوره طلاق، آیه ۲"
            },
            {
                "text": "به راستی که انسان در زیان است، مگر کسانی که ایمان آورده و کارهای شایسته انجام داده‌اند و یکدیگر را به حق و صبر سفارش کرده‌اند",
                "source": "قرآن کریم، سوره عصر، آیات ۲-۳"
            },
            {
                "text": "با دانش‌ترین مردم کسی است که دانش دیگران را به دانش خود بیفزاید",
                "source": "امام علی (ع)"
            },
            {
                "text": "برترین عبادت‌ها اندیشیدن مداوم درباره خدا و قدرت اوست",
                "source": "امام صادق (ع)"
            },
            {
                "text": "بهترین دوست تو آن کسی است که تو را به کار نیک وادارد و بر انجام آن یاریت کند",
                "source": "امام علی (ع)"
            }
        ]
        
        # Use the current date to pick a quote deterministically
        date = datetime.now()
        day_of_year = int(date.strftime("%j"))
        
        index = day_of_year % len(quotes)
        return quotes[index]