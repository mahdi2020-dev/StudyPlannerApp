#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Persian Financial, Health, and Time Management Application
Main entry point for the application
"""

import os
import sys
import logging
from pathlib import Path
import socket
import json
import http.server
import socketserver
import urllib.parse
import base64
from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import auth, credentials

# Check if running in Replit environment
IN_REPLIT = os.environ.get('REPL_ID') is not None

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    logger.info("Firebase Admin SDK initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
    firebase_admin = None

def run_desktop_app():
    """Run the standard PyQt desktop application"""
    # Import Qt dependencies only when needed
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QCoreApplication, Qt
    from PyQt6.QtGui import QFontDatabase, QIcon
    
    from app.ui.login_window import LoginWindow
    from app.core.database import DatabaseManager
    import app.ui.style as style
    
    # Create the application
    app = QApplication(sys.argv)
    
    # Set application details
    QCoreApplication.setOrganizationName("PersianLifeManager")
    QCoreApplication.setApplicationName("Persian Life Manager")
    QCoreApplication.setApplicationVersion("1.0.0")
    
    # Make sure application works with RTL languages
    QApplication.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    # Apply application stylesheet
    app.setStyleSheet(style.STYLESHEET)
    
    # Initialize the database
    db_path = os.path.join(Path.home(), '.persian_life_manager', 'database.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db_manager = DatabaseManager(db_path)
    
    # Show the login window
    login_window = LoginWindow()
    login_window.show()
    
    # Run application event loop
    sys.exit(app.exec())


def run_replit_web_preview():
    """Run a web interface for Persian Life Manager in Replit"""
    import http.server
    import json
    import urllib.parse
    import socketserver
    from app.core.database import DatabaseManager
    from app.core.auth import AuthService
    from app.services.finance_service import FinanceService
    from app.services.health_service import HealthService
    from app.services.calendar_service import CalendarService
    from app.services.ai_service import AIService
    
    # Check for Supabase credentials
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("SUPABASE_URL or SUPABASE_KEY environment variables not set")
        return  # Exit if Supabase credentials are missing
    
    # Initialize services
    db_path = os.path.join(Path.home(), '.persian_life_manager', 'database.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Initialize the auth service
    from app.core.auth import AuthService
    auth_service = AuthService()
    auth_service.initialize()
    
    # Initialize AI service
    ai_service = AIService()
    
    # Add OpenAI API key check
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY environment variable not set. AI features will be limited.")
    
    # Import AI chat service
    try:
        from app.services.ai_chat_service import AIChatService
        ai_chat_service = AIChatService()
        logger.info("AI Chat Service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AI Chat Service: {str(e)}")
        ai_chat_service = None
        
    # Import speech to text service
    try:
        from app.services.speech_to_text import SpeechToTextService
        speech_service = SpeechToTextService()
        logger.info("Speech-to-Text Service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Speech-to-Text Service: {str(e)}")
        speech_service = None
    
    # Current user info (for session management)
    current_user = {"user_id": None, "username": None}
    
    # Create a web server for the Persian Life Manager
    class PersianLifeManagerHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            # Parse URL
            parsed_url = urllib.parse.urlparse(self.path)
            path = parsed_url.path
            
            # Routes
            if path == '/':
                self.send_home_page()
            elif path == '/login':
                self.send_login_page()
            elif path == '/guest-login':
                self.handle_guest_login()
            elif path == '/dashboard' and current_user["user_id"]:
                self.send_dashboard_page()
            elif path == '/finance' and current_user["user_id"]:
                self.send_finance_page()
            elif path == '/health' and current_user["user_id"]:
                self.send_health_page()
            elif path == '/calendar' and current_user["user_id"]:
                self.send_calendar_page()
            elif path == '/religious' and current_user["user_id"]:
                self.send_religious_page()
            elif path == '/ai-chat' and current_user["user_id"]:
                self.send_ai_chat_page()
            elif path == '/logout':
                current_user["user_id"] = None
                current_user["username"] = None
                self.send_redirect('/login')
            elif path.startswith('/api/') and current_user["user_id"]:
                # API endpoints
                if path == '/api/chat':
                    self.handle_api_chat()
                elif path == '/api/suggest-activity':
                    self.handle_api_suggest_activity()
                elif path == '/api/speech-to-text':
                    self.handle_api_speech_to_text()
                else:
                    self.send_json_response({"error": "API endpoint not found"})
            else:
                # Default route or unauthorized access
                if current_user["user_id"] is None and path not in ['/', '/login']:
                    self.send_redirect('/login')
                else:
                    self.send_not_found()
        
        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            # Check if the request is JSON or form data
            content_type = self.headers.get('Content-Type', '')
            
            if 'application/json' in content_type:
                # Parse JSON data
                try:
                    json_data = json.loads(post_data)
                    
                    # Handle different JSON API endpoints
                    if self.path == '/api/chat' and current_user["user_id"]:
                        self.handle_api_chat_post(json_data)
                    elif self.path == '/api/suggest-activity' and current_user["user_id"]:
                        self.handle_api_suggest_activity_post(json_data)
                    elif self.path == '/api/speech-to-text' and current_user["user_id"]:
                        self.handle_api_speech_to_text_post(json_data)
                    else:
                        self.send_json_response({"error": "API endpoint not found"})
                except json.JSONDecodeError:
                    self.send_json_response({"error": "Invalid JSON data"})
                
            else:
                # Parse form data
                form_data = urllib.parse.parse_qs(post_data)
                
                # Handle different form submissions
                if self.path == '/login':
                    self.handle_login(form_data)
                elif self.path == '/register':
                    self.handle_register(form_data)
                elif self.path == '/activate':
                    self.handle_activate(form_data)
                elif self.path == '/resend_code':
                    self.handle_resend_code(form_data)
                elif self.path == '/guest-login':
                    self.handle_guest_login()
                elif self.path == '/add_transaction' and current_user["user_id"]:
                    self.handle_add_transaction(form_data)
                elif self.path == '/add_health_metric' and current_user["user_id"]:
                    self.handle_add_health_metric(form_data)
                elif self.path == '/add_event' and current_user["user_id"]:
                    self.handle_add_event(form_data)
                elif self.path == '/add_task' and current_user["user_id"]:
                    self.handle_add_task(form_data)
                elif self.path == '/api/health_advice' and current_user["user_id"]:
                    self.handle_health_advice(form_data)
                else:
                    self.send_error(404)
        
        def send_redirect(self, location):
            self.send_response(302)
            # URL encode all non-ASCII characters for proper handling
            import urllib.parse
            if not isinstance(location, str):
                location = str(location)
            # Ensure location is properly encoded for HTTP header
            # First, parse the URL to separate any query parameters
            url_parts = urllib.parse.urlparse(location)
            # Encode the path part
            path = url_parts.path
            # Encode the query part (if any)
            query = url_parts.query
            if query:
                # Parse the query string into a dictionary
                query_dict = urllib.parse.parse_qs(query)
                # Create a new query string with properly encoded values
                new_query = urllib.parse.urlencode(query_dict, doseq=True)
                # Reassemble the URL with the encoded components
                location = urllib.parse.urlunparse((
                    url_parts.scheme, url_parts.netloc, path,
                    url_parts.params, new_query, url_parts.fragment
                ))
            
            self.send_header('Location', location)
            self.end_headers()
        
        def send_json_response(self, data):
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=UTF-8')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        
        def send_home_page(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            
            # Define HTML content with triple quotes to properly handle CSS content
            html_content = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Persian Life Manager</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
    <style>
        :root {
            --main-bg-color: #121212;
            --card-bg-color: #1e1e1e;
            --sidebar-bg-color: #171717;
            --neon-color: #00ffaa;
            --neon-glow: 0 0 10px rgba(0, 255, 170, 0.7);
            --text-color: #ecf0f1;
            --border-color: #2d2d2d;
        }
        
        body {
            font-family: 'Vazirmatn', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: var(--main-bg-color);
            color: var(--text-color);
            direction: rtl;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .hero {
            text-align: center;
            padding: 80px 20px;
            background-color: rgba(0, 0, 0, 0.4);
            margin-bottom: 40px;
            border-radius: 10px;
            position: relative;
            overflow: hidden;
        }
        
        .hero::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at center, rgba(0, 255, 170, 0.1) 0%, rgba(0, 0, 0, 0) 70%);
            z-index: -1;
        }
        
        .logo {
            font-size: 3rem;
            font-weight: bold;
            color: var(--neon-color);
            text-shadow: var(--neon-glow);
            margin-bottom: 20px;
        }
        
        .subtitle {
            font-size: 1.5rem;
            color: var(--text-color);
            margin-bottom: 40px;
        }
        
        .features {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 30px;
            margin-bottom: 60px;
        }
        
        .feature-card {
            background-color: var(--card-bg-color);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 30px;
            width: 300px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2), 0 0 15px rgba(0, 255, 170, 0.3);
            border-color: var(--neon-color);
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 20px;
            color: var(--neon-color);
        }
        
        .feature-title {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 15px;
            color: var(--neon-color);
        }
        
        .cta-container {
            text-align: center;
            margin: 60px 0;
        }
        
        .neon-button {
            display: inline-block;
            background-color: transparent;
            color: var(--neon-color);
            border: 2px solid var(--neon-color);
            border-radius: 5px;
            padding: 15px 30px;
            font-size: 1.2rem;
            font-weight: bold;
            text-decoration: none;
            margin: 10px;
            box-shadow: 0 0 10px rgba(0, 255, 170, 0.5);
            transition: all 0.3s ease;
        }
        
        .neon-button:hover {
            background-color: rgba(0, 255, 170, 0.1);
            box-shadow: 0 0 20px rgba(0, 255, 170, 0.8);
        }
        
        .neon-button.alt {
            color: #00aaff;
            border-color: #00aaff;
            box-shadow: 0 0 10px rgba(0, 170, 255, 0.5);
        }
        
        .neon-button.alt:hover {
            background-color: rgba(0, 170, 255, 0.1);
            box-shadow: 0 0 20px rgba(0, 170, 255, 0.8);
        }
        
        .footer {
            text-align: center;
            padding: 40px 0;
            border-top: 1px solid var(--border-color);
            margin-top: 60px;
        }
        
        .copyright {
            color: rgba(255, 255, 255, 0.5);
        }
    </style>
</head>
<body>
    <div class="container">
        <section class="hero">
            <div class="logo">Persian Life Manager</div>
            <div class="subtitle">برنامه جامع مدیریت مالی، سلامت و زندگی با پشتیبانی از تقویم شمسی</div>
            <div class="cta-container">
                <a href="/login" class="neon-button">ورود به برنامه</a>
                <a href="/guest-login" class="neon-button alt">ورود به عنوان مهمان</a>
            </div>
        </section>
        
        <section class="features">
            <div class="feature-card">
                <div class="feature-icon">💰</div>
                <div class="feature-title">مدیریت مالی</div>
                <p>مدیریت هوشمند درآمدها و هزینه‌ها، دسته‌بندی تراکنش‌ها، گزارش‌های دوره‌ای و نمودارهای تحلیلی</p>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">❤️</div>
                <div class="feature-title">پیگیری سلامت</div>
                <p>ثبت و پیگیری فعالیت‌های ورزشی، وزن، فشار خون، و سایر معیارهای سلامتی به همراه توصیه‌های هوشمند</p>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">📅</div>
                <div class="feature-title">مدیریت زمان</div>
                <p>تقویم شمسی با امکان ثبت رویدادها، یادآوری، مدیریت وظایف و برنامه‌ریزی روزانه</p>
            </div>
        </section>
        
        <section class="cta-container">
            <a href="/login" class="neon-button">ورود به برنامه</a>
            <a href="/guest-login" class="neon-button alt">ورود به عنوان مهمان</a>
        </section>
        
        <footer class="footer">
            <div class="copyright">Persian Life Manager &copy; 2025</div>
        </footer>
    </div>
</body>
</html>
'''
            self.wfile.write(html_content.encode('utf-8'))
        
        def send_login_page(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            
            # Get Supabase configuration from environment variables
            supabase_url = os.environ.get('SUPABASE_URL')
            supabase_key = os.environ.get('SUPABASE_KEY')
            
            # Default values for template variables
            login_error = ''
            show_error = ''
            
            # Parse URL parameters
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            # Process error messages
            if 'error' in query_params:
                error_code = query_params['error'][0]
                if error_code == 'auth/invalid-credentials':
                    show_error = 'نام کاربری یا رمز عبور اشتباه است.'
                elif error_code == 'incomplete':
                    show_error = 'لطفاً تمام فیلدها را پر کنید.'    
                else:
                    show_error = 'خطا در ورود. لطفاً دوباره تلاش کنید.'
            
            # Define HTML content with triple quotes for proper formatting
            html_content = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود | Persian Life Manager</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
    <script>
        // با استفاده از window.onload مطمئن می‌شویم اسکریپت پس از لود کامل صفحه اجرا می‌شود
        window.onload = function() {
            console.log("صفحه لاگین کامل لود شد");
            
            // گرفتن المنت‌های مورد نیاز با بررسی وجود آنها
            var loginForm = document.getElementById('login-form');
            
            // بررسی وجود المنت‌ها و درج event listener ها
            if (loginForm) {
                loginForm.addEventListener('submit', function(e) {
                    var email = document.getElementById('login-email');
                    var password = document.getElementById('login-password');
                    var errorElement = document.getElementById('login-error');
                    
                    if (!email || !password || !email.value || !password.value) {
                        e.preventDefault();
                        if (errorElement) {
                            errorElement.textContent = 'لطفا ایمیل و رمز عبور را وارد کنید.';
                            errorElement.style.display = 'block';
                        }
                        return false;
                    }
                    
                    // اجازه ارسال عادی فرم به سرور
                    return true;
                });
            } else {
                console.error("فرم لاگین در صفحه پیدا نشد!");
            }
        };
        
        // ثبت‌نام غیرفعال شده - فقط توسط ادمین از طریق داشبورد Supabase
    </script>
    <style>
        :root {
            --main-bg-color: #121212;
            --card-bg-color: #1e1e1e;
            --sidebar-bg-color: #171717;
            --neon-color: #00ffaa;
            --neon-blue: #00aaff;
            --neon-glow: 0 0 10px rgba(0, 255, 170, 0.7);
            --text-color: #ecf0f1;
            --border-color: #2d2d2d;
            --input-bg: #1a1a1a;
        }
        
        body {
            font-family: 'Vazirmatn', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: var(--main-bg-color);
            color: var(--text-color);
            direction: rtl;
            line-height: 1.6;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .auth-container {
            max-width: 400px;
            width: 100%;
            padding: 40px;
            background-color: var(--card-bg-color);
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            position: relative;
            overflow: hidden;
        }
        
        .auth-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(to right, var(--neon-color), var(--neon-blue));
            box-shadow: 0 0 10px rgba(0, 255, 170, 0.7);
        }
        
        .auth-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .logo {
            font-size: 2rem;
            font-weight: bold;
            color: var(--neon-color);
            text-shadow: var(--neon-glow);
            margin-bottom: 10px;
        }
        
        .auth-tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid var(--border-color);
        }
        
        .auth-tab {
            flex: 1;
            text-align: center;
            padding: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .auth-tab.active {
            color: var(--neon-color);
            font-weight: bold;
            border-bottom: 2px solid var(--neon-color);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .form-input {
            width: 100%;
            padding: 12px;
            background-color: var(--input-bg);
            border: 1px solid var(--border-color);
            border-radius: 5px;
            color: var(--text-color);
            font-family: 'Vazirmatn', Arial, sans-serif;
            transition: all 0.3s ease;
        }
        
        .form-input:focus {
            border-color: var(--neon-color);
            box-shadow: 0 0 5px rgba(0, 255, 170, 0.3);
            outline: none;
        }
        
        .neon-button {
            display: block;
            width: 100%;
            padding: 12px;
            background-color: transparent;
            color: var(--neon-color);
            border: 2px solid var(--neon-color);
            border-radius: 5px;
            font-size: 1rem;
            font-weight: bold;
            text-decoration: none;
            text-align: center;
            margin-top: 30px;
            cursor: pointer;
            box-shadow: 0 0 10px rgba(0, 255, 170, 0.3);
            transition: all 0.3s ease;
            font-family: 'Vazirmatn', Arial, sans-serif;
        }
        
        .neon-button:hover {
            background-color: rgba(0, 255, 170, 0.1);
            box-shadow: 0 0 15px rgba(0, 255, 170, 0.5);
        }
        
        .form-footer {
            text-align: center;
            margin-top: 20px;
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.7);
        }
        
        .form-footer a {
            color: var(--neon-color);
            text-decoration: none;
        }
        
        .error-message {
            color: #ff5555;
            font-size: 0.9rem;
            margin-top: 5px;
            display: none;
        }
        
        #register-form {
            display: none;
        }
    </style>
</head>
<body>
    <div class="auth-container">
        <div class="auth-header">
            <div class="logo">Persian Life Manager</div>
        </div>
        
        <div class="auth-tabs">
            <div class="auth-tab active" id="login-tab">ورود</div>
            <!-- Hide registration tab -->
            <div class="auth-tab" id="register-tab" style="display: none;">ثبت نام</div>
            <div class="auth-tab" id="activate-tab" style="display: none;">فعال‌سازی</div>
        </div>
        
        <form action="/login" method="post" id="login-form">
            <div class="form-group">
                <label class="form-label" for="login-email">ایمیل</label>
                <input type="email" class="form-input" id="login-email" name="email" required>
            </div>
            
            <div class="form-group">
                <label class="form-label" for="login-password">رمز عبور</label>
                <input type="password" class="form-input" id="login-password" name="password" required>
                <div class="error-message" id="login-error"></div>
            </div>
            
            <button type="submit" class="neon-button">ورود</button>
            
            <!-- Removed registration link -->
            <div class="form-footer">
                برای ثبت نام با مدیر سیستم تماس بگیرید
            </div>
        </form>
        
        <!-- Guest Login Button -->
        <div class="guest-login-container" style="text-align: center; margin-top: 20px;">
            <button id="guest-login-btn" class="neon-button alt" style="background-color: #333; color: #ccc; border: 1px solid #444;">
                ورود به عنوان مهمان
            </button>
        </div>
        
        <form action="/register" method="post" id="register-form">
            <div class="form-group">
                <label class="form-label" for="register-name">نام</label>
                <input type="text" class="form-input" id="register-name" name="name" required>
            </div>
            
            <div class="form-group">
                <label class="form-label" for="register-email">ایمیل</label>
                <input type="email" class="form-input" id="register-email" name="email" required>
            </div>
            
            <div class="form-group">
                <label class="form-label" for="register-password">رمز عبور</label>
                <input type="password" class="form-input" id="register-password" name="password" required>
                <div class="error-message" id="register-error"></div>
            </div>
            
            <button type="submit" class="neon-button">ثبت نام</button>
            
            <div class="form-footer">
                حساب کاربری دارید؟ <a href="#" id="switch-to-login">وارد شوید</a>
            </div>
        </form>
        
        <form action="/activate" method="post" id="activate-form" style="display: none;">
            <div class="form-group">
                <label class="form-label" for="activate-email">ایمیل</label>
                <input type="email" class="form-input" id="activate-email" name="email" required>
            </div>
            
            <div class="form-group">
                <label class="form-label" for="activate-code">کد فعال‌سازی</label>
                <input type="text" class="form-input" id="activate-code" name="activation_code" required maxlength="6" placeholder="کد ۶ رقمی ارسال شده به ایمیل شما">
                <div class="error-message" id="activate-error"></div>
            </div>
            
            <button type="submit" class="neon-button">فعال‌سازی حساب کاربری</button>
            
            <div class="form-footer">
                کد فعال‌سازی را دریافت نکرده‌اید؟ <a href="#" id="resend-code">ارسال مجدد کد</a>
            </div>
        </form>
        
        <form action="/resend_code" method="post" id="resend-form" style="display: none;">
            <input type="hidden" id="resend-email" name="email">
        </form>
    </div>
</body>
</html>
'''
            self.wfile.write(html_content.encode('utf-8'))
        
        def send_ai_chat_page(self):
            """Send the AI chat interface page"""
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            
            # Define HTML content - using a simple approach to avoid syntax issues
            username = current_user["username"] if current_user["username"] else "کاربر"
            
            html_content = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>چت هوشمند</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #121212;
            color: #ecf0f1;
            direction: rtl;
            margin: 0;
            padding: 0;
        }
        .navbar {
            background-color: #1e1e1e;
            padding: 15px;
            text-align: center;
        }
        .content {
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }
        .chat-container {
            background-color: #1e1e1e;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
        }
        .ai-message {
            background-color: rgba(0, 255, 170, 0.1);
            border: 1px solid #00ffaa;
        }
        .user-message {
            background-color: rgba(0, 170, 255, 0.1);
            border: 1px solid #00aaff;
            text-align: left;
        }
        .input-area {
            display: flex;
            margin-top: 20px;
        }
        input {
            flex: 1;
            padding: 10px;
            border: 1px solid #2d2d2d;
            background-color: #1a1a1a;
            color: #ecf0f1;
            border-radius: 4px;
            margin-left: 10px;
        }
        button {
            padding: 10px 20px;
            background-color: transparent;
            color: #00ffaa;
            border: 1px solid #00ffaa;
            border-radius: 4px;
            cursor: pointer;
        }
        h1, h2 {
            color: #00ffaa;
        }
        a {
            color: #ecf0f1;
            text-decoration: none;
            margin: 0 10px;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>Persian Life Manager</h1>
        <div>
            <a href="/dashboard">داشبورد</a>
            <a href="/finance">مالی</a>
            <a href="/health">سلامت</a>
            <a href="/calendar">تقویم</a>
            <a href="/ai-chat">چت هوشمند</a>
            <a href="/logout">خروج</a>
        </div>
    </div>
    
    <div class="content">
        <h2>چت هوشمند</h2>
        
        <div class="chat-container" id="chat-container">
            <div class="message ai-message">سلام ''' + username + '''! من دستیار هوشمند Persian Life Manager هستم. چطور می‌توانم به شما کمک کنم؟</div>
        </div>
        
        <div class="input-area">
            <input type="text" id="user-input" placeholder="پیام خود را بنویسید...">
            <button id="send-button">ارسال</button>
        </div>
    </div>
    
    <script>
        // منتظر می‌مانیم تا همه‌ی عناصر صفحه بارگذاری شوند
        document.addEventListener('DOMContentLoaded', function() {
            console.log("صفحه چت هوشمند کامل لود شد");
            
            // بررسی وجود المنت‌های مورد نیاز
            var checkElements = function() {
                var chatContainer = document.getElementById('chat-container');
                var userInput = document.getElementById('user-input');
                var sendButton = document.getElementById('send-button');
                
                console.log("چک کردن المنت‌ها:", 
                    "chatContainer:", chatContainer !== null, 
                    "userInput:", userInput !== null,
                    "sendButton:", sendButton !== null
                );
                
                // اگر همه‌ی المنت‌ها موجود باشند
                if (chatContainer && userInput && sendButton) {
                    initChat(chatContainer, userInput, sendButton);
                } else {
                    console.error("المنت‌های مورد نیاز یافت نشدند");
                    // تلاش مجدد پس از 100 میلی‌ثانیه
                    setTimeout(checkElements, 100);
                }
            };
            
            // تابع راه‌اندازی چت
            function initChat(chatContainer, userInput, sendButton) {
                var chatHistory = [];
                
                function addMessage(content, isUser) {
                    var messageDiv = document.createElement('div');
                    messageDiv.classList.add('message');
                    messageDiv.classList.add(isUser ? 'user-message' : 'ai-message');
                    messageDiv.textContent = content;
                    chatContainer.appendChild(messageDiv);
                }
                
                async function sendMessage(message) {
                    if (!message.trim()) return;
                    
                    addMessage(message, true);
                    
                    try {
                        var response = await fetch('/api/chat', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                message: message,
                                history: chatHistory
                            })
                        });
                        
                        var data = await response.json();
                        
                        if (data.error) {
                            addMessage('متأسفانه خطایی رخ داد: ' + data.error, false);
                        } else {
                            addMessage(data.response, false);
                            
                            chatHistory.push({
                                role: 'user',
                                content: message
                            });
                            
                            chatHistory.push({
                                role: 'assistant',
                                content: data.response
                            });
                        }
                    } catch (error) {
                        console.error('Error:', error);
                        addMessage('متأسفانه خطایی رخ داد. لطفاً دوباره تلاش کنید.', false);
                    }
                }
                
                // اضافه کردن ایونت‌ها
                sendButton.addEventListener('click', function() {
                    var message = userInput.value;
                    if (message.trim()) {
                        sendMessage(message);
                        userInput.value = '';
                    }
                });
                
                userInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        var message = userInput.value;
                        if (message.trim()) {
                            sendMessage(message);
                            userInput.value = '';
                        }
                    }
                });
                
                console.log("چت هوشمند با موفقیت راه‌اندازی شد");
            }
            
            // شروع بررسی المنت‌ها
            checkElements();
        });
    </script>
</body>
</html>
'''
            self.wfile.write(html_content.encode('utf-8'))

        def handle_login(self, form_data):
            """Handle login form submission with Supabase"""
            # Get credentials from form data
            email = form_data.get('email', [''])[0]
            password = form_data.get('password', [''])[0]
            
            if not email or not password:
                self.send_redirect('/login?error=incomplete')
                return
                
            try:
                # Use the auth service to login
                success, session_id, error_message = auth_service.login(email, password)
                
                if success and session_id:
                    # Get user details from session
                    user = auth_service.get_user_by_session(session_id)
                    if user:
                        # User is authenticated, set session
                        current_user["user_id"] = user.id
                        current_user["username"] = user.name
                    
                    # Redirect to dashboard
                    self.send_redirect('/dashboard')
                else:
                    # Login failed, redirect with error
                    self.send_redirect('/login?error=auth/invalid-credentials')
                
            except Exception as e:
                logger.error(f"Login error: {str(e)}")
                self.send_redirect('/login?error=unknown')
        
        def handle_register(self, form_data):
            """Handle registration form submission with Firebase"""
            name = form_data.get('name', [''])[0]
            email = form_data.get('email', [''])[0]
            password = form_data.get('password', [''])[0]
            
            if not name or not email or not password:
                self.send_redirect('/login?error=incomplete')
                return
            
            try:
                auth = firebase_admin.auth
                # Check if user already exists
                try:
                    auth.get_user_by_email(email)
                    self.send_redirect('/login?error=email-exists')
                    return
                except firebase_admin._auth_utils.UserNotFoundError:
                    pass
                
                # Create new user
                user = auth.create_user(
                    email=email,
                    password=password,
                    display_name=name,
                    email_verified=False
                )
                
                # Send verification email
                verification_link = auth.generate_email_verification_link(email)
                
                # Import and use email service
                try:
                    from app.services.email_service import EmailService
                    email_service = EmailService()
                    email_sent = email_service.send_verification_email(email, name, verification_link)
                    
                    if email_sent:
                        logger.info(f"Verification email sent to {email}")
                        self.send_redirect('/login?registered=success&email=' + urllib.parse.quote(email))
                    else:
                        logger.error(f"Failed to send verification email to {email}")
                        # Create user anyway but inform about email issue
                        self.send_redirect('/login?registered=success&email=' + urllib.parse.quote(email) + '&email_error=true')
                except Exception as e:
                    logger.error(f"Email service error: {str(e)}")
                    # Create user anyway but inform about email issue
                    self.send_redirect('/login?registered=success&email=' + urllib.parse.quote(email) + '&email_error=true')
                
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                self.send_redirect('/login?error=unknown')
                
        def handle_activate(self, form_data):
            """Handle email verification confirmation
            
            This function is called when the user confirms their email
            by clicking the verification link sent to their email.
            """
            # Firebase automatically handles email verification
            # This function is kept for compatibility with the old system
            # and potential future customization
            
            # Just redirect to login page with success message
            self.send_redirect('/login?verified=success')
                
        def handle_resend_code(self, form_data):
            """Handle resending verification email"""
            email = form_data.get('email', [''])[0]
            
            if not email:
                self.send_redirect('/login?resend_error=incomplete')
                return
                
            try:
                # Verify if the user exists
                auth = firebase_admin.auth
                try:
                    user = auth.get_user_by_email(email)
                except:
                    self.send_redirect('/login?resend_error=not_found')
                    return
                
                # Generate and send a new verification link
                verification_link = auth.generate_email_verification_link(email)
                
                # Use the email service to send the verification email
                try:
                    from app.services.email_service import EmailService
                    email_service = EmailService()
                    email_sent = email_service.send_verification_email(email, user.display_name, verification_link)
                    
                    if email_sent:
                        logger.info(f"Verification email resent to {email}")
                        self.send_redirect(f'/login?resend=success&email={urllib.parse.quote(email)}')
                    else:
                        logger.error(f"Failed to resend verification email to {email}")
                        self.send_redirect('/login?resend_error=email')
                except Exception as e:
                    logger.error(f"Email service error on resend: {str(e)}")
                    self.send_redirect('/login?resend_error=email')
                    
            except Exception as e:
                logger.error(f"Resend verification error: {str(e)}")
                self.send_redirect('/login?resend_error=error')
                
        def handle_guest_login(self):
            """Handle guest login request using Supabase guest account"""
            try:
                # Use the auth service to create a guest session
                success, session_id, guest_user = auth_service.create_guest_session()
                
                if success and guest_user:
                    # Set session for guest user
                    current_user["user_id"] = guest_user.id
                    current_user["username"] = guest_user.name
                    
                    logger.info("Guest user logged in")
                else:
                    raise Exception("Failed to create guest session")
                    
                self.send_redirect('/dashboard')
            except Exception as e:
                logger.error(f"Guest login error: {str(e)}")
                # Fallback to simple guest login if service fails
                current_user["user_id"] = "guest-user-id"
                current_user["username"] = "کاربر مهمان"
                self.send_redirect('/dashboard')
        
        def handle_api_chat_post(self, json_data):
            if ai_chat_service is None:
                self.send_json_response({"error": "AI Chat Service is not available"})
                return
            
            message = json_data.get('message', '')
            history = json_data.get('history', [])
            
            if not message:
                self.send_json_response({"error": "Message is required"})
                return
            
            try:
                # Get user data for context
                finance_service = FinanceService(current_user["user_id"])
                health_service = HealthService(current_user["user_id"])
                calendar_service = CalendarService(current_user["user_id"])
                
                # Collect user data for context
                user_data = {
                    "username": current_user["username"],
                    "finance": {
                        "transactions": finance_service.get_transactions(limit=10),
                        "balance": finance_service.get_balance()
                    },
                    "health": {
                        "metrics": health_service.get_metrics(limit=5),
                        "exercises": health_service.get_exercises(limit=5)
                    },
                    "calendar": {
                        "events": calendar_service.get_upcoming_events(limit=5),
                        "tasks": calendar_service.get_pending_tasks(limit=5)
                    }
                }
                
                # Use the AI chat service to get a response
                response = ai_chat_service.chat(message, user_data, history)
                
                # Send the response to the client
                self.send_json_response({"response": response})
                
            except Exception as e:
                logger.error(f"Error in chat API: {str(e)}")
                self.send_json_response({"error": "An error occurred while processing your request"})
        
        def handle_api_suggest_activity_post(self, json_data):
            if ai_chat_service is None:
                self.send_json_response({"error": "AI Chat Service is not available"})
                return
            
            time_of_day = json_data.get('time_of_day', 'afternoon')
            energy_level = json_data.get('energy_level', 'medium')
            available_time = int(json_data.get('available_time', 30))
            
            try:
                # Collect user data for context
                health_service = HealthService(current_user["user_id"])
                calendar_service = CalendarService(current_user["user_id"])
                
                user_data = {
                    "username": current_user["username"],
                    "health": {
                        "metrics": health_service.get_metrics(limit=1),
                        "exercises": health_service.get_exercises(limit=5)
                    },
                    "calendar": {
                        "events": calendar_service.get_upcoming_events(limit=3),
                        "tasks": calendar_service.get_pending_tasks(limit=3)
                    }
                }
                
                # Use the AI chat service to suggest an activity
                suggestion = ai_chat_service.suggest_activity(
                    time_of_day, energy_level, available_time, user_data
                )
                
                # Send the suggestion to the client
                self.send_json_response(suggestion)
                
            except Exception as e:
                logger.error(f"Error in suggest activity API: {str(e)}")
                self.send_json_response({"error": "An error occurred while processing your request"})
        
        def handle_api_speech_to_text_post(self, json_data):
            if speech_service is None:
                self.send_json_response({"error": "Speech-to-Text Service is not available"})
                return
            
            audio_base64 = json_data.get('audio', '')
            
            if not audio_base64:
                self.send_json_response({"error": "Audio data is required"})
                return
            
            try:
                # Transcribe the audio to text
                transcription = speech_service.transcribe_audio(audio_base64)
                
                # Send the transcription to the client
                self.send_json_response({"text": transcription})
                
            except Exception as e:
                logger.error(f"Error in speech-to-text API: {str(e)}")
                self.send_json_response({"error": "An error occurred while processing your request"})

        def send_dashboard_page(self):
            # To be implemented
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            
            html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>داشبورد</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #121212;
            color: #ecf0f1;
            direction: rtl;
            margin: 0;
            padding: 0;
        }}
        .navbar {{
            background-color: #1e1e1e;
            padding: 15px;
            text-align: center;
        }}
        .content {{
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1, h2 {{
            color: #00ffaa;
        }}
        a {{
            color: #ecf0f1;
            text-decoration: none;
            margin: 0 10px;
        }}
    </style>
</head>
<body>
    <div class="navbar">
        <h1>Persian Life Manager</h1>
        <div>
            <a href="/dashboard">داشبورد</a>
            <a href="/finance">مالی</a>
            <a href="/health">سلامت</a>
            <a href="/calendar">تقویم</a>
            <a href="/religious">اطلاعات مذهبی</a>
            <a href="/ai-chat">چت هوشمند</a>
            <a href="/logout">خروج</a>
        </div>
    </div>
    
    <div class="content">
        <h2>داشبورد</h2>
        <p>خوش آمدید {current_user["username"]}!</p>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
            <div style="background-color: #1e1e1e; border-radius: 10px; padding: 20px; border: 1px solid #2d2d2d;">
                <h3 style="color: #00ffaa; margin-top: 0;">آمار سلامت</h3>
                <p>وضعیت کلی: سالم</p>
                <p>قدم‌های امروز: 6,580</p>
                <p>آخرین ورزش: پیاده‌روی (30 دقیقه)</p>
                <a href="/health" style="display: inline-block; margin-top: 10px; padding: 5px 10px; background-color: rgba(0, 255, 170, 0.1); color: #00ffaa; border: 1px solid #00ffaa; border-radius: 5px; text-decoration: none;">مشاهده جزئیات</a>
            </div>
            
            <div style="background-color: #1e1e1e; border-radius: 10px; padding: 20px; border: 1px solid #2d2d2d;">
                <h3 style="color: #00ffaa; margin-top: 0;">خلاصه مالی</h3>
                <p>درآمد ماه: 12,500,000 تومان</p>
                <p>هزینه‌های ماه: 8,200,000 تومان</p>
                <p>پس‌انداز: 4,300,000 تومان</p>
                <a href="/finance" style="display: inline-block; margin-top: 10px; padding: 5px 10px; background-color: rgba(0, 255, 170, 0.1); color: #00ffaa; border: 1px solid #00ffaa; border-radius: 5px; text-decoration: none;">مشاهده جزئیات</a>
            </div>
            
            <div style="background-color: #1e1e1e; border-radius: 10px; padding: 20px; border: 1px solid #2d2d2d;">
                <h3 style="color: #00ffaa; margin-top: 0;">رویدادهای امروز</h3>
                <p>جلسه کاری: 10:30 - 12:00</p>
                <p>ورزش: 17:00 - 18:00</p>
                <p>مطالعه: 21:00 - 22:00</p>
                <a href="/calendar" style="display: inline-block; margin-top: 10px; padding: 5px 10px; background-color: rgba(0, 255, 170, 0.1); color: #00ffaa; border: 1px solid #00ffaa; border-radius: 5px; text-decoration: none;">مشاهده تقویم</a>
            </div>
            
            <div style="background-color: #1e1e1e; border-radius: 10px; padding: 20px; border: 1px solid #2d2d2d;">
                <h3 style="color: #00ffaa; margin-top: 0;">یادآوری‌های مهم</h3>
                <p>پرداخت قبض برق: 2 روز مانده</p>
                <p>نوبت دکتر: 5 روز مانده</p>
                <p>سالگرد ازدواج: 12 روز مانده</p>
                <a href="/calendar" style="display: inline-block; margin-top: 10px; padding: 5px 10px; background-color: rgba(0, 255, 170, 0.1); color: #00ffaa; border: 1px solid #00ffaa; border-radius: 5px; text-decoration: none;">مدیریت یادآوری‌ها</a>
            </div>
        </div>
    </div>
</body>
</html>
'''
            self.wfile.write(html_content.encode('utf-8'))
        
        def send_finance_page(self):
            # To be implemented
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            
            html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>مدیریت مالی</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #121212;
            color: #ecf0f1;
            direction: rtl;
            margin: 0;
            padding: 0;
        }}
        .navbar {{
            background-color: #1e1e1e;
            padding: 15px;
            text-align: center;
        }}
        .content {{
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1, h2 {{
            color: #00ffaa;
        }}
        a {{
            color: #ecf0f1;
            text-decoration: none;
            margin: 0 10px;
        }}
    </style>
</head>
<body>
    <div class="navbar">
        <h1>Persian Life Manager</h1>
        <div>
            <a href="/dashboard">داشبورد</a>
            <a href="/finance">مالی</a>
            <a href="/health">سلامت</a>
            <a href="/calendar">تقویم</a>
            <a href="/religious">اطلاعات مذهبی</a>
            <a href="/ai-chat">چت هوشمند</a>
            <a href="/logout">خروج</a>
        </div>
    </div>
    
    <div class="content">
        <h2>مدیریت مالی</h2>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
            <!-- خلاصه مالی -->
            <div style="background-color: #1e1e1e; border-radius: 10px; padding: 20px; border: 1px solid #2d2d2d; grid-column: 1 / -1;">
                <h3 style="color: #00ffaa; margin-top: 0;">خلاصه وضعیت مالی</h3>
                <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 200px; padding: 15px; background-color: rgba(0, 255, 170, 0.05); border-radius: 8px; margin: 5px;">
                        <p style="margin: 0; font-size: 14px;">موجودی کل</p>
                        <p style="margin: 5px 0; font-size: 24px; font-weight: bold; color: #00ffaa;">24,500,000 تومان</p>
                    </div>
                    <div style="flex: 1; min-width: 200px; padding: 15px; background-color: rgba(0, 255, 170, 0.05); border-radius: 8px; margin: 5px;">
                        <p style="margin: 0; font-size: 14px;">مجموع درآمد ماه</p>
                        <p style="margin: 5px 0; font-size: 24px; font-weight: bold; color: #00ffaa;">12,500,000 تومان</p>
                    </div>
                    <div style="flex: 1; min-width: 200px; padding: 15px; background-color: rgba(0, 255, 170, 0.05); border-radius: 8px; margin: 5px;">
                        <p style="margin: 0; font-size: 14px;">مجموع هزینه ماه</p>
                        <p style="margin: 5px 0; font-size: 24px; font-weight: bold; color: #ff5555;">8,200,000 تومان</p>
                    </div>
                    <div style="flex: 1; min-width: 200px; padding: 15px; background-color: rgba(0, 255, 170, 0.05); border-radius: 8px; margin: 5px;">
                        <p style="margin: 0; font-size: 14px;">پس‌انداز ماه</p>
                        <p style="margin: 5px 0; font-size: 24px; font-weight: bold; color: #00ffaa;">4,300,000 تومان</p>
                    </div>
                </div>
            </div>
            
            <!-- افزودن تراکنش جدید -->
            <div style="background-color: #1e1e1e; border-radius: 10px; padding: 20px; border: 1px solid #2d2d2d;">
                <h3 style="color: #00ffaa; margin-top: 0;">افزودن تراکنش جدید</h3>
                <form id="add-transaction-form" style="display: flex; flex-direction: column; gap: 15px;">
                    <div>
                        <label for="transaction-type" style="display: block; margin-bottom: 5px;">نوع تراکنش</label>
                        <select id="transaction-type" name="type" style="width: 100%; padding: 10px; background-color: #2d2d2d; color: #ecf0f1; border: none; border-radius: 5px;">
                            <option value="income">درآمد</option>
                            <option value="expense">هزینه</option>
                        </select>
                    </div>
                    <div>
                        <label for="transaction-amount" style="display: block; margin-bottom: 5px;">مبلغ (تومان)</label>
                        <input id="transaction-amount" name="amount" type="number" placeholder="مبلغ را وارد کنید" style="width: 100%; padding: 10px; background-color: #2d2d2d; color: #ecf0f1; border: none; border-radius: 5px;">
                    </div>
                    <div>
                        <label for="transaction-category" style="display: block; margin-bottom: 5px;">دسته‌بندی</label>
                        <select id="transaction-category" name="category" style="width: 100%; padding: 10px; background-color: #2d2d2d; color: #ecf0f1; border: none; border-radius: 5px;">
                            <option value="salary">حقوق</option>
                            <option value="food">خوراک</option>
                            <option value="transportation">حمل و نقل</option>
                            <option value="shopping">خرید</option>
                            <option value="entertainment">تفریح</option>
                            <option value="bills">قبوض</option>
                            <option value="other">سایر</option>
                        </select>
                    </div>
                    <div>
                        <label for="transaction-description" style="display: block; margin-bottom: 5px;">توضیحات</label>
                        <input id="transaction-description" name="description" type="text" placeholder="توضیحات تراکنش" style="width: 100%; padding: 10px; background-color: #2d2d2d; color: #ecf0f1; border: none; border-radius: 5px;">
                    </div>
                    <button type="submit" style="padding: 10px; background-color: #00ffaa; color: #121212; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; margin-top: 10px;">ثبت تراکنش</button>
                </form>
            </div>
            
            <!-- آخرین تراکنش‌ها -->
            <div style="background-color: #1e1e1e; border-radius: 10px; padding: 20px; border: 1px solid #2d2d2d; grid-column: span 2;">
                <h3 style="color: #00ffaa; margin-top: 0;">آخرین تراکنش‌ها</h3>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                        <thead>
                            <tr style="border-bottom: 1px solid #2d2d2d;">
                                <th style="padding: 10px; text-align: right;">تاریخ</th>
                                <th style="padding: 10px; text-align: right;">مبلغ</th>
                                <th style="padding: 10px; text-align: right;">دسته‌بندی</th>
                                <th style="padding: 10px; text-align: right;">توضیحات</th>
                                <th style="padding: 10px; text-align: right;">نوع</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom: 1px solid #2d2d2d;">
                                <td style="padding: 10px;">۱۴۰۴/۰۱/۱۵</td>
                                <td style="padding: 10px; color: #00ffaa;">12,500,000 تومان</td>
                                <td style="padding: 10px;">حقوق</td>
                                <td style="padding: 10px;">حقوق فروردین ماه</td>
                                <td style="padding: 10px;"><span style="padding: 3px 8px; background-color: rgba(0, 255, 170, 0.1); color: #00ffaa; border-radius: 3px;">درآمد</span></td>
                            </tr>
                            <tr style="border-bottom: 1px solid #2d2d2d;">
                                <td style="padding: 10px;">۱۴۰۴/۰۱/۱۲</td>
                                <td style="padding: 10px; color: #ff5555;">2,500,000 تومان</td>
                                <td style="padding: 10px;">خرید</td>
                                <td style="padding: 10px;">خرید لوازم خانه</td>
                                <td style="padding: 10px;"><span style="padding: 3px 8px; background-color: rgba(255, 85, 85, 0.1); color: #ff5555; border-radius: 3px;">هزینه</span></td>
                            </tr>
                            <tr style="border-bottom: 1px solid #2d2d2d;">
                                <td style="padding: 10px;">۱۴۰۴/۰۱/۱۰</td>
                                <td style="padding: 10px; color: #ff5555;">1,200,000 تومان</td>
                                <td style="padding: 10px;">قبوض</td>
                                <td style="padding: 10px;">پرداخت قبوض</td>
                                <td style="padding: 10px;"><span style="padding: 3px 8px; background-color: rgba(255, 85, 85, 0.1); color: #ff5555; border-radius: 3px;">هزینه</span></td>
                            </tr>
                            <tr style="border-bottom: 1px solid #2d2d2d;">
                                <td style="padding: 10px;">۱۴۰۴/۰۱/۰۵</td>
                                <td style="padding: 10px; color: #ff5555;">850,000 تومان</td>
                                <td style="padding: 10px;">خوراک</td>
                                <td style="padding: 10px;">خرید هفتگی</td>
                                <td style="padding: 10px;"><span style="padding: 3px 8px; background-color: rgba(255, 85, 85, 0.1); color: #ff5555; border-radius: 3px;">هزینه</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''
            self.wfile.write(html_content.encode('utf-8'))
        
        def send_health_page(self):
            # To be implemented
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            
            html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>مدیریت سلامت</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #121212;
            color: #ecf0f1;
            direction: rtl;
            margin: 0;
            padding: 0;
        }}
        .navbar {{
            background-color: #1e1e1e;
            padding: 15px;
            text-align: center;
        }}
        .content {{
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1, h2 {{
            color: #00ffaa;
        }}
        a {{
            color: #ecf0f1;
            text-decoration: none;
            margin: 0 10px;
        }}
    </style>
</head>
<body>
    <div class="navbar">
        <h1>Persian Life Manager</h1>
        <div>
            <a href="/dashboard">داشبورد</a>
            <a href="/finance">مالی</a>
            <a href="/health">سلامت</a>
            <a href="/calendar">تقویم</a>
            <a href="/religious">اطلاعات مذهبی</a>
            <a href="/ai-chat">چت هوشمند</a>
            <a href="/logout">خروج</a>
        </div>
    </div>
    
    <div class="content">
        <h2>مدیریت سلامت</h2>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
            <!-- خلاصه سلامت -->
            <div style="background-color: #1e1e1e; border-radius: 10px; padding: 20px; border: 1px solid #2d2d2d; grid-column: 1 / -1;">
                <h3 style="color: #00ffaa; margin-top: 0;">خلاصه وضعیت سلامت</h3>
                <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 200px; padding: 15px; background-color: rgba(0, 255, 170, 0.05); border-radius: 8px; margin: 5px;">
                        <p style="margin: 0; font-size: 14px;">شاخص توده بدنی (BMI)</p>
                        <p style="margin: 5px 0; font-size: 24px; font-weight: bold; color: #00ffaa;">22.4</p>
                        <p style="margin: 0; font-size: 12px; opacity: 0.7;">طبیعی</p>
                    </div>
                    <div style="flex: 1; min-width: 200px; padding: 15px; background-color: rgba(0, 255, 170, 0.05); border-radius: 8px; margin: 5px;">
                        <p style="margin: 0; font-size: 14px;">قدم‌های امروز</p>
                        <p style="margin: 5px 0; font-size: 24px; font-weight: bold; color: #00ffaa;">6,580</p>
                        <p style="margin: 0; font-size: 12px; opacity: 0.7;">از هدف 10,000</p>
                    </div>
                    <div style="flex: 1; min-width: 200px; padding: 15px; background-color: rgba(0, 255, 170, 0.05); border-radius: 8px; margin: 5px;">
                        <p style="margin: 0; font-size: 14px;">ساعات خواب</p>
                        <p style="margin: 5px 0; font-size: 24px; font-weight: bold; color: #00ffaa;">7.5</p>
                        <p style="margin: 0; font-size: 12px; opacity: 0.7;">ساعت (دیشب)</p>
                    </div>
                    <div style="flex: 1; min-width: 200px; padding: 15px; background-color: rgba(0, 255, 170, 0.05); border-radius: 8px; margin: 5px;">
                        <p style="margin: 0; font-size: 14px;">کالری مصرفی روزانه</p>
                        <p style="margin: 5px 0; font-size: 24px; font-weight: bold; color: #00ffaa;">1,850</p>
                        <p style="margin: 0; font-size: 12px; opacity: 0.7;">از هدف 2,200</p>
                    </div>
                </div>
            </div>
            
            <!-- افزودن فعالیت ورزشی -->
            <div style="background-color: #1e1e1e; border-radius: 10px; padding: 20px; border: 1px solid #2d2d2d;">
                <h3 style="color: #00ffaa; margin-top: 0;">افزودن فعالیت ورزشی</h3>
                <form id="add-exercise-form" style="display: flex; flex-direction: column; gap: 15px;">
                    <div>
                        <label for="exercise-type" style="display: block; margin-bottom: 5px;">نوع فعالیت</label>
                        <select id="exercise-type" name="type" style="width: 100%; padding: 10px; background-color: #2d2d2d; color: #ecf0f1; border: none; border-radius: 5px;">
                            <option value="walking">پیاده روی</option>
                            <option value="running">دویدن</option>
                            <option value="cycling">دوچرخه سواری</option>
                            <option value="swimming">شنا</option>
                            <option value="gym">تمرین با وزنه</option>
                            <option value="yoga">یوگا</option>
                            <option value="other">سایر</option>
                        </select>
                    </div>
                    <div>
                        <label for="exercise-duration" style="display: block; margin-bottom: 5px;">مدت زمان (دقیقه)</label>
                        <input id="exercise-duration" name="duration" type="number" placeholder="مدت زمان را وارد کنید" style="width: 100%; padding: 10px; background-color: #2d2d2d; color: #ecf0f1; border: none; border-radius: 5px;">
                    </div>
                    <div>
                        <label for="exercise-calories" style="display: block; margin-bottom: 5px;">کالری سوزانده شده (تخمینی)</label>
                        <input id="exercise-calories" name="calories" type="number" placeholder="کالری را وارد کنید" style="width: 100%; padding: 10px; background-color: #2d2d2d; color: #ecf0f1; border: none; border-radius: 5px;">
                    </div>
                    <div>
                        <label for="exercise-notes" style="display: block; margin-bottom: 5px;">یادداشت</label>
                        <input id="exercise-notes" name="notes" type="text" placeholder="یادداشت اختیاری" style="width: 100%; padding: 10px; background-color: #2d2d2d; color: #ecf0f1; border: none; border-radius: 5px;">
                    </div>
                    <button type="submit" style="padding: 10px; background-color: #00ffaa; color: #121212; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; margin-top: 10px;">ثبت فعالیت</button>
                </form>
            </div>
            
            <!-- ثبت شاخص‌های سلامت -->
            <div style="background-color: #1e1e1e; border-radius: 10px; padding: 20px; border: 1px solid #2d2d2d;">
                <h3 style="color: #00ffaa; margin-top: 0;">ثبت شاخص‌های سلامت</h3>
                <form id="add-metrics-form" style="display: flex; flex-direction: column; gap: 15px;">
                    <div>
                        <label for="metric-weight" style="display: block; margin-bottom: 5px;">وزن (کیلوگرم)</label>
                        <input id="metric-weight" name="weight" type="number" step="0.1" placeholder="وزن را وارد کنید" style="width: 100%; padding: 10px; background-color: #2d2d2d; color: #ecf0f1; border: none; border-radius: 5px;">
                    </div>
                    <div>
                        <label for="metric-height" style="display: block; margin-bottom: 5px;">قد (سانتی‌متر)</label>
                        <input id="metric-height" name="height" type="number" placeholder="قد را وارد کنید" style="width: 100%; padding: 10px; background-color: #2d2d2d; color: #ecf0f1; border: none; border-radius: 5px;">
                    </div>
                    <div>
                        <label for="metric-blood-pressure" style="display: block; margin-bottom: 5px;">فشار خون (سیستولیک/دیاستولیک)</label>
                        <div style="display: flex; gap: 10px;">
                            <input id="metric-systolic" name="systolic" type="number" placeholder="سیستولیک" style="width: 50%; padding: 10px; background-color: #2d2d2d; color: #ecf0f1; border: none; border-radius: 5px;">
                            <input id="metric-diastolic" name="diastolic" type="number" placeholder="دیاستولیک" style="width: 50%; padding: 10px; background-color: #2d2d2d; color: #ecf0f1; border: none; border-radius: 5px;">
                        </div>
                    </div>
                    <button type="submit" style="padding: 10px; background-color: #00ffaa; color: #121212; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; margin-top: 10px;">ثبت شاخص‌ها</button>
                </form>
            </div>
            
            <!-- آخرین فعالیت‌های ورزشی -->
            <div style="background-color: #1e1e1e; border-radius: 10px; padding: 20px; border: 1px solid #2d2d2d; grid-column: span 2;">
                <h3 style="color: #00ffaa; margin-top: 0;">آخرین فعالیت‌های ورزشی</h3>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                        <thead>
                            <tr style="border-bottom: 1px solid #2d2d2d;">
                                <th style="padding: 10px; text-align: right;">تاریخ</th>
                                <th style="padding: 10px; text-align: right;">نوع فعالیت</th>
                                <th style="padding: 10px; text-align: right;">مدت (دقیقه)</th>
                                <th style="padding: 10px; text-align: right;">کالری</th>
                                <th style="padding: 10px; text-align: right;">یادداشت</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom: 1px solid #2d2d2d;">
                                <td style="padding: 10px;">۱۴۰۴/۰۱/۱۶</td>
                                <td style="padding: 10px;">پیاده‌روی</td>
                                <td style="padding: 10px;">30</td>
                                <td style="padding: 10px;">150</td>
                                <td style="padding: 10px;">در پارک ملت</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #2d2d2d;">
                                <td style="padding: 10px;">۱۴۰۴/۰۱/۱۴</td>
                                <td style="padding: 10px;">تمرین با وزنه</td>
                                <td style="padding: 10px;">45</td>
                                <td style="padding: 10px;">320</td>
                                <td style="padding: 10px;">تمرین بالاتنه</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #2d2d2d;">
                                <td style="padding: 10px;">۱۴۰۴/۰۱/۱۳</td>
                                <td style="padding: 10px;">دویدن</td>
                                <td style="padding: 10px;">25</td>
                                <td style="padding: 10px;">280</td>
                                <td style="padding: 10px;">دویدن با شدت متوسط</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #2d2d2d;">
                                <td style="padding: 10px;">۱۴۰۴/۰۱/۱۱</td>
                                <td style="padding: 10px;">یوگا</td>
                                <td style="padding: 10px;">40</td>
                                <td style="padding: 10px;">120</td>
                                <td style="padding: 10px;">تمرین آرامش ذهن</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''
            self.wfile.write(html_content.encode('utf-8'))
        
        def send_calendar_page(self):
            # To be implemented
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            
            html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>تقویم و مدیریت زمان</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #121212;
            color: #ecf0f1;
            direction: rtl;
            margin: 0;
            padding: 0;
        }}
        .navbar {{
            background-color: #1e1e1e;
            padding: 15px;
            text-align: center;
        }}
        .content {{
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1, h2 {{
            color: #00ffaa;
        }}
        a {{
            color: #ecf0f1;
            text-decoration: none;
            margin: 0 10px;
        }}
    </style>
</head>
<body>
    <div class="navbar">
        <h1>Persian Life Manager</h1>
        <div>
            <a href="/dashboard">داشبورد</a>
            <a href="/finance">مالی</a>
            <a href="/health">سلامت</a>
            <a href="/calendar">تقویم</a>
            <a href="/religious">اطلاعات مذهبی</a>
            <a href="/ai-chat">چت هوشمند</a>
            <a href="/logout">خروج</a>
        </div>
    </div>
    
    <div class="content">
        <h2>تقویم و مدیریت زمان</h2>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
            <!-- تقویم ماهانه -->
            <div style="background-color: #1e1e1e; border-radius: 10px; padding: 20px; border: 1px solid #2d2d2d; grid-column: 1 / -1;">
                <h3 style="color: #00ffaa; margin-top: 0;">تقویم فروردین ۱۴۰۴</h3>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <button style="padding: 5px 10px; background-color: rgba(0, 255, 170, 0.1); color: #00ffaa; border: 1px solid #00ffaa; border-radius: 5px; cursor: pointer;">ماه قبل</button>
                    <span style="color: #00ffaa; font-weight: bold;">فروردین ۱۴۰۴</span>
                    <button style="padding: 5px 10px; background-color: rgba(0, 255, 170, 0.1); color: #00ffaa; border: 1px solid #00ffaa; border-radius: 5px; cursor: pointer;">ماه بعد</button>
                </div>
                <table style="width: 100%; border-collapse: collapse; text-align: center;">
                    <thead>
                        <tr>
                            <th style="padding: 8px; color: #ff5555;">شنبه</th>
                            <th style="padding: 8px;">یکشنبه</th>
                            <th style="padding: 8px;">دوشنبه</th>
                            <th style="padding: 8px;">سه‌شنبه</th>
                            <th style="padding: 8px;">چهارشنبه</th>
                            <th style="padding: 8px;">پنجشنبه</th>
                            <th style="padding: 8px; color: #ff5555;">جمعه</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۱</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۲</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۳</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۴</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۵</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۶</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d; color: #ff5555;">۷</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #2d2d2d; color: #ff5555;">۸</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۹</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۱۰</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۱۱</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۱۲</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۱۳</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d; color: #ff5555;">۱۴</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #2d2d2d; color: #ff5555;">۱۵</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۱۶</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d; background-color: rgba(0, 255, 170, 0.1);">۱۷</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۱۸</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۱۹</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۲۰</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d; color: #ff5555;">۲۱</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #2d2d2d; color: #ff5555;">۲۲</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۲۳</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۲۴</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۲۵</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۲۶</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۲۷</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d; color: #ff5555;">۲۸</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #2d2d2d; color: #ff5555;">۲۹</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۳۰</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d;">۳۱</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d; opacity: 0.3;">۱</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d; opacity: 0.3;">۲</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d; opacity: 0.3;">۳</td>
                            <td style="padding: 10px; border: 1px solid #2d2d2d; color: #ff5555; opacity: 0.3;">۴</td>
                        </tr>
                    </tbody>
                </table>
                <div style="margin-top: 10px; text-align: left;">
                    <div style="display: inline-block; width: 12px; height: 12px; background-color: rgba(0, 255, 170, 0.1); margin-left: 5px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">امروز</span>
                    <div style="display: inline-block; width: 12px; height: 12px; background-color: #ff5555; margin-right: 10px; margin-left: 5px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">تعطیل</span>
                </div>
            </div>
            
            <!-- رویدادهای امروز -->
            <div style="background-color: #1e1e1e; border-radius: 10px; padding: 20px; border: 1px solid #2d2d2d;">
                <h3 style="color: #00ffaa; margin-top: 0;">رویدادهای امروز</h3>
                <div style="margin-top: 15px;">
                    <div style="background-color: rgba(0, 255, 170, 0.05); border-radius: 8px; padding: 15px; margin-bottom: 10px; border-right: 3px solid #00ffaa;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4 style="margin: 0; color: #00ffaa;">جلسه کاری</h4>
                            <span style="font-size: 14px;">10:30 - 12:00</span>
                        </div>
                        <p style="margin: 5px 0 0 0; font-size: 14px;">جلسه با تیم طراحی محصول</p>
                    </div>
                    <div style="background-color: rgba(0, 255, 170, 0.05); border-radius: 8px; padding: 15px; margin-bottom: 10px; border-right: 3px solid #00ffaa;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4 style="margin: 0; color: #00ffaa;">ورزش</h4>
                            <span style="font-size: 14px;">17:00 - 18:00</span>
                        </div>
                        <p style="margin: 5px 0 0 0; font-size: 14px;">پیاده‌روی در پارک ملت</p>
                    </div>
                    <div style="background-color: rgba(0, 255, 170, 0.05); border-radius: 8px; padding: 15px; margin-bottom: 10px; border-right: 3px solid #00ffaa;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4 style="margin: 0; color: #00ffaa;">مطالعه</h4>
                            <span style="font-size: 14px;">21:00 - 22:00</span>
                        </div>
                        <p style="margin: 5px 0 0 0; font-size: 14px;">مطالعه کتاب روانشناسی</p>
                    </div>
                </div>
                <button style="width: 100%; padding: 10px; background-color: rgba(0, 255, 170, 0.1); color: #00ffaa; border: 1px solid #00ffaa; border-radius: 5px; cursor: pointer; margin-top: 15px;">افزودن رویداد جدید</button>
            </div>
            
            <!-- افزودن یادآوری -->
            <div style="background-color: #1e1e1e; border-radius: 10px; padding: 20px; border: 1px solid #2d2d2d;">
                <h3 style="color: #00ffaa; margin-top: 0;">افزودن یادآوری</h3>
                <form id="add-reminder-form" style="display: flex; flex-direction: column; gap: 15px;">
                    <div>
                        <label for="reminder-title" style="display: block; margin-bottom: 5px;">عنوان یادآوری</label>
                        <input id="reminder-title" name="title" type="text" placeholder="عنوان را وارد کنید" style="width: 100%; padding: 10px; background-color: #2d2d2d; color: #ecf0f1; border: none; border-radius: 5px;">
                    </div>
                    <div>
                        <label for="reminder-date" style="display: block; margin-bottom: 5px;">تاریخ یادآوری</label>
                        <input id="reminder-date" name="date" type="date" style="width: 100%; padding: 10px; background-color: #2d2d2d; color: #ecf0f1; border: none; border-radius: 5px;">
                    </div>
                    <div>
                        <label for="reminder-time" style="display: block; margin-bottom: 5px;">زمان یادآوری</label>
                        <input id="reminder-time" name="time" type="time" style="width: 100%; padding: 10px; background-color: #2d2d2d; color: #ecf0f1; border: none; border-radius: 5px;">
                    </div>
                    <div>
                        <label for="reminder-description" style="display: block; margin-bottom: 5px;">توضیحات</label>
                        <textarea id="reminder-description" name="description" placeholder="توضیحات یادآوری" style="width: 100%; padding: 10px; background-color: #2d2d2d; color: #ecf0f1; border: none; border-radius: 5px; height: 100px; resize: vertical;"></textarea>
                    </div>
                    <button type="submit" style="padding: 10px; background-color: #00ffaa; color: #121212; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">ثبت یادآوری</button>
                </form>
            </div>
            
            <!-- کارهای در انتظار -->
            <div style="background-color: #1e1e1e; border-radius: 10px; padding: 20px; border: 1px solid #2d2d2d; grid-column: span 2;">
                <h3 style="color: #00ffaa; margin-top: 0;">کارهای در انتظار</h3>
                <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 15px;">
                    <div style="display: flex; align-items: center; padding: 10px; background-color: rgba(0, 255, 170, 0.05); border-radius: 5px;">
                        <input type="checkbox" style="margin-left: 10px;">
                        <div style="flex-grow: 1;">
                            <div style="font-weight: bold;">تکمیل گزارش پروژه</div>
                            <div style="font-size: 12px; opacity: 0.7;">تا ۱۸ فروردین</div>
                        </div>
                        <div style="display: flex; gap: 5px;">
                            <button style="background-color: transparent; border: none; color: #00ffaa; cursor: pointer;">ویرایش</button>
                            <button style="background-color: transparent; border: none; color: #ff5555; cursor: pointer;">حذف</button>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; padding: 10px; background-color: rgba(0, 255, 170, 0.05); border-radius: 5px;">
                        <input type="checkbox" style="margin-left: 10px;">
                        <div style="flex-grow: 1;">
                            <div style="font-weight: bold;">پرداخت قبض برق</div>
                            <div style="font-size: 12px; opacity: 0.7;">تا ۲۰ فروردین</div>
                        </div>
                        <div style="display: flex; gap: 5px;">
                            <button style="background-color: transparent; border: none; color: #00ffaa; cursor: pointer;">ویرایش</button>
                            <button style="background-color: transparent; border: none; color: #ff5555; cursor: pointer;">حذف</button>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; padding: 10px; background-color: rgba(0, 255, 170, 0.05); border-radius: 5px;">
                        <input type="checkbox" style="margin-left: 10px;">
                        <div style="flex-grow: 1;">
                            <div style="font-weight: bold;">نوبت دکتر</div>
                            <div style="font-size: 12px; opacity: 0.7;">تا ۲۲ فروردین</div>
                        </div>
                        <div style="display: flex; gap: 5px;">
                            <button style="background-color: transparent; border: none; color: #00ffaa; cursor: pointer;">ویرایش</button>
                            <button style="background-color: transparent; border: none; color: #ff5555; cursor: pointer;">حذف</button>
                        </div>
                    </div>
                </div>
                <div style="display: flex; margin-top: 20px; gap: 10px;">
                    <input type="text" placeholder="کار جدید..." style="flex-grow: 1; padding: 10px; background-color: #2d2d2d; color: #ecf0f1; border: none; border-radius: 5px;">
                    <button style="padding: 10px; background-color: #00ffaa; color: #121212; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">افزودن</button>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''
            self.wfile.write(html_content.encode('utf-8'))
            
        def send_religious_page(self):
            """Send the religious information page"""
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            
            try:
                # Import necessary modules
                from datetime import datetime
                import jdatetime
                import requests
                import json
                
                # Get current date for default prayer times
                current_date = datetime.now().strftime("%Y-%m-%d")
                
                # Get prayer times for today (simplified implementation)
                prayer_times = self._get_prayer_times()
                
                # Get daily prayer
                daily_prayer = self._get_daily_prayer()
                
                # Get religious quote
                religious_quote = self._get_religious_quote()
                
                # Convert to Persian date
                try:
                    gregorian_date = datetime.strptime(current_date, "%Y-%m-%d")
                    persian_date = jdatetime.date.fromgregorian(date=gregorian_date)
                    persian_date_str = persian_date.strftime("%Y/%m/%d")
                except Exception as e:
                    persian_date_str = "تاریخ نامشخص"
                    persian_date = None
                
                # Get religious events for current Persian month
                religious_events = self._get_religious_events()
                
                html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>اطلاعات مذهبی</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #121212;
            color: #ecf0f1;
            direction: rtl;
            margin: 0;
            padding: 0;
        }}
        .navbar {{
            background-color: #1e1e1e;
            padding: 15px;
            text-align: center;
        }}
        .content {{
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1, h2, h3 {{
            color: #00aaff;
        }}
        a {{
            color: #ecf0f1;
            text-decoration: none;
            margin: 0 10px;
        }}
        .card {{
            background-color: #1e1e1e;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #2d2d2d;
        }}
        .prayer-times {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 10px;
        }}
        .prayer-time {{
            background-color: rgba(0, 170, 255, 0.1);
            border: 1px solid rgba(0, 170, 255, 0.3);
            border-radius: 5px;
            padding: 10px;
            text-align: center;
        }}
        .prayer-time h3 {{
            margin-top: 0;
            font-size: 16px;
        }}
        .daily-prayer {{
            background-color: rgba(0, 170, 255, 0.05);
            border: 1px solid rgba(0, 170, 255, 0.2);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
        }}
        .prayer-arabic {{
            font-size: 24px;
            margin: 15px 0;
            font-weight: bold;
        }}
        .event-item {{
            display: flex;
            align-items: center;
            padding: 10px;
            margin-bottom: 10px;
            background-color: rgba(30, 30, 30, 0.7);
            border-radius: 5px;
        }}
        .event-date {{
            padding: 8px 12px;
            background-color: rgba(0, 170, 255, 0.2);
            border-radius: 5px;
            margin-left: 15px;
            font-weight: bold;
            color: #00aaff;
        }}
        .quote-card {{
            background-color: rgba(0, 170, 255, 0.05);
            border: 1px solid rgba(0, 170, 255, 0.2);
            border-radius: 8px;
            padding: 25px;
            position: relative;
        }}
        .quote-text {{
            font-size: 18px;
            margin-bottom: 15px;
            line-height: 1.8;
        }}
        .quote-source {{
            text-align: left;
            font-style: italic;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="navbar">
        <h1>Persian Life Manager</h1>
        <div>
            <a href="/dashboard">داشبورد</a>
            <a href="/finance">مالی</a>
            <a href="/health">سلامت</a>
            <a href="/calendar">تقویم</a>
            <a href="/religious">اطلاعات مذهبی</a>
            <a href="/ai-chat">چت هوشمند</a>
            <a href="/logout">خروج</a>
        </div>
    </div>
    
    <div class="content">
        <h2>اطلاعات مذهبی</h2>
        
        <div class="daily-prayer">
            <h3>{daily_prayer['title']} روز</h3>
            <div class="prayer-arabic">{daily_prayer['arabic']}</div>
            <div class="prayer-translation">{daily_prayer['persian']}</div>
        </div>
        
        <div class="card">
            <h2>اوقات شرعی - {persian_date_str}</h2>
            <div class="prayer-times">
                <div class="prayer-time">
                    <h3>اذان صبح</h3>
                    <p>{prayer_times.get('fajr', 'نامشخص')}</p>
                </div>
                <div class="prayer-time">
                    <h3>طلوع آفتاب</h3>
                    <p>{prayer_times.get('sunrise', 'نامشخص')}</p>
                </div>
                <div class="prayer-time">
                    <h3>اذان ظهر</h3>
                    <p>{prayer_times.get('dhuhr', 'نامشخص')}</p>
                </div>
                <div class="prayer-time">
                    <h3>اذان عصر</h3>
                    <p>{prayer_times.get('asr', 'نامشخص')}</p>
                </div>
                <div class="prayer-time">
                    <h3>اذان مغرب</h3>
                    <p>{prayer_times.get('maghrib', 'نامشخص')}</p>
                </div>
                <div class="prayer-time">
                    <h3>اذان عشاء</h3>
                    <p>{prayer_times.get('isha', 'نامشخص')}</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>مناسبت‌های مذهبی ماه جاری</h2>
'''
                
                # Add religious events
                if religious_events:
                    for event in religious_events:
                        html_content += f'''
            <div class="event-item">
                <div class="event-date">{event['date']}</div>
                <div class="event-description">{event['description']}</div>
            </div>'''
                else:
                    html_content += '''
            <p>مناسبت خاصی در این ماه ثبت نشده است.</p>'''
                
                html_content += f'''
        </div>
        
        <div class="card">
            <h2>جمله حکیمانه</h2>
            <div class="quote-card">
                <div class="quote-text">{religious_quote['text']}</div>
                <div class="quote-source">{religious_quote['source']}</div>
            </div>
        </div>
    </div>
</body>
</html>
'''
                self.wfile.write(html_content.encode('utf-8'))
            except Exception as e:
                # If any error occurs, send a simple page
                html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>اطلاعات مذهبی</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #121212;
            color: #ecf0f1;
            direction: rtl;
            margin: 0;
            padding: 0;
        }}
        .navbar {{
            background-color: #1e1e1e;
            padding: 15px;
            text-align: center;
        }}
        .content {{
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1, h2 {{
            color: #00aaff;
        }}
        a {{
            color: #ecf0f1;
            text-decoration: none;
            margin: 0 10px;
        }}
        .error {{
            background-color: rgba(255, 0, 0, 0.1);
            border: 1px solid rgba(255, 0, 0, 0.3);
            padding: 15px;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="navbar">
        <h1>Persian Life Manager</h1>
        <div>
            <a href="/dashboard">داشبورد</a>
            <a href="/finance">مالی</a>
            <a href="/health">سلامت</a>
            <a href="/calendar">تقویم</a>
            <a href="/religious">اطلاعات مذهبی</a>
            <a href="/ai-chat">چت هوشمند</a>
            <a href="/logout">خروج</a>
        </div>
    </div>
    
    <div class="content">
        <h2>اطلاعات مذهبی</h2>
        <div class="error">
            <p>متأسفانه در بارگذاری اطلاعات مذهبی خطایی رخ داده است. لطفاً بعداً دوباره تلاش کنید.</p>
            <p>جزئیات خطا: {str(e)}</p>
        </div>
    </div>
</body>
</html>
'''
                self.wfile.write(html_content.encode('utf-8'))
        
        def _get_prayer_times(self):
            """Get prayer times (simplified implementation)"""
            prayer_times = {
                'fajr': '05:30',
                'sunrise': '06:45',
                'dhuhr': '12:15',
                'asr': '15:45',
                'maghrib': '18:30',
                'isha': '19:45'
            }
            return prayer_times
        
        def _get_daily_prayer(self):
            """Get a daily prayer"""
            prayers = [
                {
                    'arabic': 'سُبْحَانَ اللهِ',
                    'persian': 'پاک و منزه است خداوند',
                    'title': 'تسبیح'
                },
                {
                    'arabic': 'اَلْحَمْدُ لِلّٰهِ',
                    'persian': 'ستایش برای خداست',
                    'title': 'حمد'
                },
                {
                    'arabic': 'لَا إِلَٰهَ إِلَّا ٱللَّٰهُ',
                    'persian': 'نیست معبودی جز الله',
                    'title': 'تهلیل'
                }
            ]
            
            # Use the current day to select a prayer
            from datetime import datetime
            day = datetime.now().day
            return prayers[day % len(prayers)]
        
        def _get_religious_quote(self):
            """Get a religious quote"""
            quotes = [
                {
                    'text': 'هر کس در راه خدا تقوا پیشه کند، خداوند برای او راه نجاتی قرار می‌دهد',
                    'source': 'قرآن کریم، سوره طلاق، آیه ۲'
                },
                {
                    'text': 'به راستی که انسان در زیان است، مگر کسانی که ایمان آورده و کارهای شایسته انجام داده‌اند و یکدیگر را به حق و صبر سفارش کرده‌اند',
                    'source': 'قرآن کریم، سوره عصر، آیات ۲-۳'
                },
                {
                    'text': 'با دانش‌ترین مردم کسی است که دانش دیگران را به دانش خود بیفزاید',
                    'source': 'امام علی (ع)'
                }
            ]
            
            # Use the current day to select a quote
            from datetime import datetime
            day = datetime.now().day
            return quotes[day % len(quotes)]
        
        def _get_religious_events(self):
            """Get religious events (simplified implementation)"""
            return [
                {
                    'date': '1404/01/01',
                    'description': 'عید نوروز'
                },
                {
                    'date': '1404/01/13',
                    'description': 'سیزده بدر'
                }
            ]
        
        def send_not_found(self):
            self.send_response(404)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            
            html_content = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>صفحه یافت نشد</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #121212;
            color: #ecf0f1;
            direction: rtl;
            margin: 0;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }
        .error-container {
            text-align: center;
            padding: 30px;
            background-color: #1e1e1e;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
        }
        h1 {
            color: #00ffaa;
            font-size: 3rem;
            margin-bottom: 10px;
        }
        p {
            font-size: 1.2rem;
            margin-bottom: 30px;
        }
        a {
            display: inline-block;
            padding: 10px 20px;
            background-color: transparent;
            color: #00ffaa;
            border: 2px solid #00ffaa;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        a:hover {
            background-color: rgba(0, 255, 170, 0.1);
            box-shadow: 0 0 15px rgba(0, 255, 170, 0.5);
        }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>404</h1>
        <p>صفحه مورد نظر یافت نشد</p>
        <a href="/">بازگشت به صفحه اصلی</a>
    </div>
</body>
</html>
'''
            self.wfile.write(html_content.encode('utf-8'))
    
    # Set up the HTTP server
    handler = PersianLifeManagerHandler
    
    # Try to find an available port
    port = 5000
    max_attempts = 10
    attempt = 0
    
    while attempt < max_attempts:
        try:
            server = socketserver.TCPServer(("0.0.0.0", port), handler)
            break
        except OSError as e:
            if e.errno == 98:  # Address already in use
                logger.warning(f"Port {port} is already in use, trying next port")
                port += 1
                attempt += 1
            else:
                raise
    
    if attempt >= max_attempts:
        logger.error(f"Failed to find an available port after {max_attempts} attempts")
        raise RuntimeError(f"Failed to find an available port after {max_attempts} attempts")
        
    print(f"Started web server at http://0.0.0.0:{port}")
    server.serve_forever()

if __name__ == "__main__":
    # Determine which version to run based on environment
    if IN_REPLIT:
        print("Running in Replit environment, starting web preview...")
        run_replit_web_preview()
    else:
        print("Running in desktop environment, starting PyQt application...")
        run_desktop_app()