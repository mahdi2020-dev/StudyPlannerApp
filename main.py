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
    db_manager.initialize_database()
    
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
    
    # Initialize services
    db_path = os.path.join(Path.home(), '.persian_life_manager', 'database.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db_manager = DatabaseManager(db_path)
    db_manager.initialize_database()
    
    auth_service = AuthService(db_path)
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
            elif path == '/dashboard' and current_user["user_id"]:
                self.send_dashboard_page()
            elif path == '/finance' and current_user["user_id"]:
                self.send_finance_page()
            elif path == '/health' and current_user["user_id"]:
                self.send_health_page()
            elif path == '/calendar' and current_user["user_id"]:
                self.send_calendar_page()
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
            
            # Define HTML content with triple quotes for proper formatting
            html_content = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود | Persian Life Manager</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
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
            <div class="auth-tab" id="register-tab">ثبت نام</div>
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
            
            <div class="form-footer">
                حساب کاربری ندارید؟ <a href="#" id="switch-to-register">ثبت نام کنید</a>
            </div>
        </form>
        
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
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const loginTab = document.getElementById('login-tab');
            const registerTab = document.getElementById('register-tab');
            const loginForm = document.getElementById('login-form');
            const registerForm = document.getElementById('register-form');
            const switchToRegister = document.getElementById('switch-to-register');
            const switchToLogin = document.getElementById('switch-to-login');
            
            // Switch to register tab/form
            function showRegisterForm() {
                loginTab.classList.remove('active');
                registerTab.classList.add('active');
                loginForm.style.display = 'none';
                registerForm.style.display = 'block';
            }
            
            // Switch to login tab/form
            function showLoginForm() {
                registerTab.classList.remove('active');
                loginTab.classList.add('active');
                registerForm.style.display = 'none';
                loginForm.style.display = 'block';
            }
            
            // Event listeners
            registerTab.addEventListener('click', showRegisterForm);
            loginTab.addEventListener('click', showLoginForm);
            switchToRegister.addEventListener('click', function(e) {
                e.preventDefault();
                showRegisterForm();
            });
            switchToLogin.addEventListener('click', function(e) {
                e.preventDefault();
                showLoginForm();
            });
            
            // URL parameters handling for error messages
            const urlParams = new URLSearchParams(window.location.search);
            const loginError = urlParams.get('login_error');
            const registerError = urlParams.get('register_error');
            const registered = urlParams.get('registered');
            
            if (loginError) {
                const errorElem = document.getElementById('login-error');
                errorElem.textContent = loginError;
                errorElem.style.display = 'block';
            }
            
            if (registerError) {
                showRegisterForm();
                const errorElem = document.getElementById('register-error');
                errorElem.textContent = registerError;
                errorElem.style.display = 'block';
            }
            
            if (registered === 'success') {
                const errorElem = document.getElementById('login-error');
                errorElem.textContent = 'ثبت نام با موفقیت انجام شد. اکنون می‌توانید وارد شوید.';
                errorElem.style.display = 'block';
                errorElem.style.color = '#00ffaa';
            }
        });
    </script>
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
        document.addEventListener('DOMContentLoaded', function() {
            const chatContainer = document.getElementById('chat-container');
            const userInput = document.getElementById('user-input');
            const sendButton = document.getElementById('send-button');
            let chatHistory = [];
            
            function addMessage(content, isUser) {
                const messageDiv = document.createElement('div');
                messageDiv.classList.add('message');
                messageDiv.classList.add(isUser ? 'user-message' : 'ai-message');
                messageDiv.textContent = content;
                chatContainer.appendChild(messageDiv);
            }
            
            async function sendMessage(message) {
                if (!message.trim()) return;
                
                addMessage(message, true);
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            message: message,
                            history: chatHistory
                        })
                    });
                    
                    const data = await response.json();
                    
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
            
            sendButton.addEventListener('click', function() {
                const message = userInput.value;
                if (message.trim()) {
                    sendMessage(message);
                    userInput.value = '';
                }
            });
            
            userInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    const message = userInput.value;
                    if (message.trim()) {
                        sendMessage(message);
                        userInput.value = '';
                    }
                }
            });
        });
    </script>
</body>
</html>
'''
            self.wfile.write(html_content.encode('utf-8'))

        def handle_login(self, form_data):
            email = form_data.get('email', [''])[0]
            password = form_data.get('password', [''])[0]
            
            if not email or not password:
                self.send_redirect('/login?login_error=لطفا تمام فیلدها را تکمیل کنید')
                return
            
            success, user_id = auth_service.login_user(email, password)
            
            if success:
                # Set user info in the session
                current_user["user_id"] = user_id
                current_user["username"] = email.split('@')[0]  # Simple username extraction
                
                # Redirect to dashboard
                self.send_redirect('/dashboard')
            else:
                self.send_redirect('/login?login_error=ایمیل یا رمز عبور نادرست است')
        
        def handle_register(self, form_data):
            name = form_data.get('name', [''])[0]
            email = form_data.get('email', [''])[0]
            password = form_data.get('password', [''])[0]
            
            if not name or not email or not password:
                self.send_redirect('/login?register_error=لطفا تمام فیلدها را تکمیل کنید')
                return
            
            success, user_id_or_error = auth_service.register_user(email, password, name)
            
            if success:
                self.send_redirect('/login?registered=success')
            else:
                self.send_redirect(f'/login?register_error={user_id_or_error}')
        
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
            <a href="/ai-chat">چت هوشمند</a>
            <a href="/logout">خروج</a>
        </div>
    </div>
    
    <div class="content">
        <h2>داشبورد</h2>
        <p>خوش آمدید {current_user["username"]}!</p>
        <p>این صفحه در حال توسعه است...</p>
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
            <a href="/ai-chat">چت هوشمند</a>
            <a href="/logout">خروج</a>
        </div>
    </div>
    
    <div class="content">
        <h2>مدیریت مالی</h2>
        <p>این صفحه در حال توسعه است...</p>
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
            <a href="/ai-chat">چت هوشمند</a>
            <a href="/logout">خروج</a>
        </div>
    </div>
    
    <div class="content">
        <h2>مدیریت سلامت</h2>
        <p>این صفحه در حال توسعه است...</p>
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
            <a href="/ai-chat">چت هوشمند</a>
            <a href="/logout">خروج</a>
        </div>
    </div>
    
    <div class="content">
        <h2>تقویم و مدیریت زمان</h2>
        <p>این صفحه در حال توسعه است...</p>
    </div>
</body>
</html>
'''
            self.wfile.write(html_content.encode('utf-8'))
        
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
    
    server = socketserver.TCPServer(("0.0.0.0", port), handler)
    
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