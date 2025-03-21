"""
Authentication Service for Persian Life Manager Application
Handles authentication with Supabase
"""
import os
import logging
import uuid
import json
import time
from typing import Dict, Optional, List, Any, Tuple

from app.core.supabase_client import SupabaseManager

# Setup logger
logger = logging.getLogger(__name__)

class User:
    """
    User class to store user data
    """
    def __init__(self, user_id: str, name: str, email: str, is_guest: bool = False):
        """
        Initialize a User object
        
        Args:
            user_id (str): User ID
            name (str): User name
            email (str): User email
            is_guest (bool, optional): Whether this is a guest user. Defaults to False.
        """
        self.id = user_id
        self.user_id = user_id  # اضافه کردن user_id به عنوان مترادف برای id
        self.name = name
        self.email = email
        self.is_guest = is_guest
        self.created_at = time.time()
        self.last_login = time.time()
        self.login_time = None  # زمان ورود به فرمت رشته‌ای - برای استفاده آسان‌تر
        self.preferences = {}   # تنظیمات کاربر
        self.metadata = {}      # داده‌های اضافی
    
    def to_dict(self) -> Dict:
        """
        Convert user to dictionary
        
        Returns:
            Dict: Dictionary representation of user
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'is_guest': self.is_guest,
            'created_at': self.created_at,
            'login_time': self.login_time,
            'last_login': self.last_login
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """
        Create a User object from a dictionary
        
        Args:
            data (Dict): Dictionary with user data
            
        Returns:
            User: User object
        """
        # اول user_id را بررسی می‌کنیم، سپس id را
        user_id = data.get('user_id', data.get('id', ''))
        
        user = cls(
            user_id=user_id,
            name=data.get('name', ''),
            email=data.get('email', ''),
            is_guest=data.get('is_guest', False)
        )
        
        # اضافه کردن فیلدهای جدید
        user.created_at = data.get('created_at', time.time())
        user.last_login = data.get('last_login', time.time())
        user.login_time = data.get('login_time')
        
        # اضافه کردن داده‌های اضافی
        if 'preferences' in data:
            user.preferences = data.get('preferences', {})
        if 'metadata' in data:
            user.metadata = data.get('metadata', {})
            
        return user

class Session:
    """
    Session class to store session data
    """
    def __init__(self, session_id: str, user_id: str, expiry: float = None):
        """
        Initialize a Session object
        
        Args:
            session_id (str): Session ID
            user_id (str): User ID
            expiry (float, optional): Session expiry timestamp. Defaults to 24 hours from now.
        """
        self.id = session_id
        self.user_id = user_id
        self.created_at = time.time()
        self.expiry = expiry if expiry else time.time() + (24 * 60 * 60)  # 24 hours
    
    def is_valid(self) -> bool:
        """
        Check if session is valid (not expired)
        
        Returns:
            bool: True if valid, False otherwise
        """
        return time.time() < self.expiry
    
    def to_dict(self) -> Dict:
        """
        Convert session to dictionary
        
        Returns:
            Dict: Dictionary representation of session
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at,
            'expiry': self.expiry
        }

class AuthService:
    """
    Authentication service for Persian Life Manager
    """
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one authentication service"""
        if cls._instance is None:
            cls._instance = super(AuthService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def initialize(self):
        """
        Initialize the authentication service
        """
        if self._initialized:
            return
            
        self.supabase = SupabaseManager()
        self.active_sessions = {}  # Dictionary of session_id -> Session
        self._initialized = True
    
    def login(self, email: str, password: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Login a user with email and password
        
        Args:
            email (str): User email
            password (str): User password
            
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: 
                - Success status
                - Session ID if successful, None otherwise
                - Error message if unsuccessful, None otherwise
        """
        # اطمینان از راه‌اندازی سرویس
        if not hasattr(self, '_initialized') or not self._initialized:
            try:
                self.initialize()
            except Exception as e:
                logger.error(f"Failed to initialize AuthService: {str(e)}")
                return False, None, "خطا در راه‌اندازی سرویس احراز هویت"
                
        # اطمینان از راه‌اندازی Supabase
        if not hasattr(self, 'supabase'):
            logger.error("Supabase attribute not found in AuthService")
            return False, None, "خطا در پیکربندی Supabase"
            
        # تلاش برای راه‌اندازی Supabase اگر هنوز فعال نشده است
        if not self.supabase.is_initialized():
            try:
                if not self.supabase.initialize():
                    # اگر راه‌اندازی موفق نبود، لاگین مهمان را پیشنهاد بده
                    logger.error("Failed to initialize Supabase client for login")
                    return False, None, "خطا در اتصال به Supabase. لطفاً از گزینه 'ورود به عنوان مهمان' استفاده کنید یا تنظیمات Supabase را بررسی کنید."
            except Exception as e:
                logger.error(f"Error initializing Supabase: {str(e)}")
                return False, None, f"خطا در اتصال به Supabase: {str(e)}. لطفاً از گزینه 'ورود به عنوان مهمان' استفاده کنید."
        
        try:
            # احراز هویت با Supabase
            auth_response = self.supabase.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            user = auth_response.user
            
            if not user:
                return False, None, "نام کاربری یا رمز عبور اشتباه است"
            
            # ایجاد جلسه جدید
            session_id = str(uuid.uuid4())
            
            # اطمینان از راه‌اندازی جلسات فعال
            if not hasattr(self, 'active_sessions'):
                self.active_sessions = {}
                
            self.active_sessions[session_id] = Session(
                session_id=session_id,
                user_id=user.id
            )
            
            logger.info(f"User {email} logged in successfully with session {session_id}")
            return True, session_id, None
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            # بررسی خطاهای رایج با پیغام‌های مناسب
            error_msg = str(e).lower()
            if "invalid login credentials" in error_msg:
                return False, None, "نام کاربری یا رمز عبور اشتباه است"
            elif "network" in error_msg or "connection" in error_msg:
                return False, None, "خطا در اتصال به سرور. لطفاً اتصال اینترنت خود را بررسی کنید."
            else:
                return False, None, f"خطا در ورود: {str(e)}"
    
    def login_with_google(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        ورود با حساب گوگل
        
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: 
                - وضعیت موفقیت
                - شناسه جلسه در صورت موفقیت، None در غیر این صورت
                - پیام خطا در صورت عدم موفقیت، None در غیر این صورت
        """
        # اطمینان از راه‌اندازی سرویس
        if not hasattr(self, '_initialized') or not self._initialized:
            try:
                self.initialize()
            except Exception as e:
                logger.error(f"Failed to initialize AuthService: {str(e)}")
                return False, None, "خطا در راه‌اندازی سرویس احراز هویت"
                
        # اطمینان از راه‌اندازی Supabase
        if not hasattr(self, 'supabase'):
            logger.error("Supabase attribute not found in AuthService")
            return False, None, "خطا در پیکربندی Supabase"
            
        # تلاش برای راه‌اندازی Supabase اگر هنوز فعال نشده است
        if not self.supabase.is_initialized():
            try:
                if not self.supabase.initialize():
                    logger.error("Failed to initialize Supabase client for Google login")
                    return False, None, "خطا در اتصال به Supabase. لطفاً اتصال اینترنت خود را بررسی کنید."
            except Exception as e:
                logger.error(f"Error initializing Supabase: {str(e)}")
                return False, None, f"خطا در اتصال به Supabase: {str(e)}"
        
        try:
            # برای ورود با گوگل، URL بازگشت (redirect URL) را ایجاد می‌کنیم
            # دریافت دامنه Replit از متغیرهای محیطی
            replit_domain = os.environ.get("REPLIT_DEV_DOMAIN")
            
            # استفاده از دامنه Replit برای URL بازگشت، در غیر این صورت از localhost استفاده کن
            callback_url = f"https://{replit_domain}/auth/callback" if replit_domain else "http://localhost:5000/auth/callback"
            
            redirect_url = self.supabase.client.auth.get_url_for_provider(
                "google",
                options={
                    "redirect_to": callback_url
                }
            )
            
            # URL بازگشت را برمی‌گردانیم تا کاربر به صفحه احراز هویت گوگل هدایت شود
            logger.info(f"Generated Google login URL: {redirect_url}")
            return True, redirect_url, None
            
        except Exception as e:
            logger.error(f"Google login error: {str(e)}")
            return False, None, f"خطا در ورود با گوگل: {str(e)}"
    
    def process_google_auth_callback(self, code: str) -> Tuple[bool, Optional[str], Optional[User], Optional[str]]:
        """
        پردازش بازگشت از احراز هویت گوگل
        
        Args:
            code (str): کد دریافتی از گوگل
            
        Returns:
            Tuple[bool, Optional[str], Optional[User], Optional[str]]:
                - وضعیت موفقیت
                - شناسه جلسه در صورت موفقیت، None در غیر این صورت
                - کاربر در صورت موفقیت، None در غیر این صورت
                - پیام خطا در صورت عدم موفقیت، None در غیر این صورت
        """
        if not self.supabase.is_initialized():
            if not self.supabase.initialize():
                return False, None, None, "خطا در اتصال به Supabase"
        
        try:
            # دریافت توکن با استفاده از کد
            session = self.supabase.client.auth.exchange_code_for_session(code)
            
            # دریافت اطلاعات کاربر
            user = session.user
            
            if not user:
                return False, None, None, "اطلاعات کاربر دریافت نشد"
            
            # ایجاد جلسه جدید
            session_id = str(uuid.uuid4())
            
            # اطمینان از راه‌اندازی جلسات فعال
            if not hasattr(self, 'active_sessions'):
                self.active_sessions = {}
                
            self.active_sessions[session_id] = Session(
                session_id=session_id,
                user_id=user.id
            )
            
            # ایجاد شیء کاربر
            new_user = User(
                user_id=user.id,
                name=user.user_metadata.get('full_name', user.email),
                email=user.email,
                is_guest=False
            )
            
            logger.info(f"User {user.email} logged in via Google with session {session_id}")
            return True, session_id, new_user, None
            
        except Exception as e:
            logger.error(f"Error processing Google auth callback: {str(e)}")
            return False, None, None, f"خطا در پردازش احراز هویت گوگل: {str(e)}"
            
    def user_exists(self, email: str) -> bool:
        """
        Check if a user exists by email
        
        Args:
            email (str): User email
            
        Returns:
            bool: True if user exists, False otherwise
        """
        user_data = self.supabase.get_user_by_email(email)
        return user_data is not None
    
    def get_user_by_session(self, session_id: str) -> Optional[User]:
        """
        Get user by session ID
        
        Args:
            session_id (str): Session ID
            
        Returns:
            Optional[User]: User object if session is valid, None otherwise
        """
        # بررسی اعتبار جلسه
        if session_id not in self.active_sessions:
            logger.warning(f"Session {session_id} not found in active sessions")
            return None
            
        session = self.active_sessions[session_id]
        
        if not session.is_valid():
            # Session expired
            logger.warning(f"Session {session_id} has expired")
            del self.active_sessions[session_id]
            return None
        
        # بررسی کاربر مهمان
        user_id = session.user_id
        if user_id.startswith('guest-'):
            # کاربر مهمان را مستقیم برگردان
            logger.info(f"Returning guest user for session {session_id}")
            return User(
                user_id=user_id,
                name="کاربر مهمان",
                email=f"{user_id}@guest.persianlifemanager.app",
                is_guest=True
            )
        
        # اطمینان از راه‌اندازی Supabase
        if not hasattr(self, 'supabase') or not self.supabase.is_initialized():
            logger.error("Supabase is not initialized for non-guest users")
            return None
            
        try:
            # Get user data from Supabase
            user_data = self.supabase.get_user(user_id)
            
            if not user_data:
                logger.warning(f"No user data found for user ID {user_id}")
                return None
                
            return User(
                user_id=user_data.get('id', ''),
                name=user_data.get('name', ''),
                email=user_data.get('email', ''),
                is_guest=user_data.get('is_guest', False)
            )
        except Exception as e:
            logger.error(f"Error getting user by session: {str(e)}")
            return None
    
    def logout(self, session_id: str) -> bool:
        """
        Logout a user session
        
        Args:
            session_id (str): Session ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        return False
    
    def create_guest_session(self) -> Tuple[bool, Optional[str], Optional[User]]:
        """
        Create a guest session
        
        Returns:
            Tuple[bool, Optional[str], Optional[User]]:
                - Success status
                - Session ID if successful, None otherwise
                - User object if successful, None otherwise
        """
        # اطمینان از راه‌اندازی سرویس
        if not hasattr(self, '_initialized') or not self._initialized:
            self.initialize()
        
        # اطمینان از راه‌اندازی جلسات فعال
        if not hasattr(self, 'active_sessions'):
            self.active_sessions = {}
        
        # ایجاد شناسه‌های یکتا
        session_id = str(uuid.uuid4())
        user_id = f"guest-{uuid.uuid4()}"
        
        # ایجاد کاربر مهمان پارسی
        guest_user = User(
            user_id=user_id,
            name="کاربر مهمان",  # به فارسی تغییر داده شد
            email=f"{user_id}@guest.persianlifemanager.app",
            is_guest=True
        )
        
        # ذخیره جلسه
        self.active_sessions[session_id] = Session(
            session_id=session_id,
            user_id=user_id
        )
        
        logger.info(f"Created guest session with ID: {session_id}")
        return True, session_id, guest_user
    
    def get_all_sessions(self) -> List[Dict]:
        """
        Get all active sessions
        
        Returns:
            List[Dict]: List of active sessions
        """
        valid_sessions = []
        invalid_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if session.is_valid():
                valid_sessions.append(session.to_dict())
            else:
                invalid_sessions.append(session_id)
        
        # Clean up invalid sessions
        for session_id in invalid_sessions:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
        
        return valid_sessions
    
    def invalidate_all_sessions(self) -> int:
        """
        Invalidate all sessions
        
        Returns:
            int: Number of invalidated sessions
        """
        count = len(self.active_sessions)
        self.active_sessions.clear()
        return count
    
    def is_valid_session(self, session_id: str) -> bool:
        """
        Check if a session is valid
        
        Args:
            session_id (str): Session ID
            
        Returns:
            bool: True if valid, False otherwise
        """
        if session_id not in self.active_sessions:
            return False
            
        session = self.active_sessions[session_id]
        
        if not session.is_valid():
            # Session expired
            del self.active_sessions[session_id]
            return False
            
        return True