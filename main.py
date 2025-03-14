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
    """Run a simplified web preview for Replit"""
    import http.server
    import socketserver
    from app.core.database import DatabaseManager
    
    # Initialize the database (without Qt)
    db_path = os.path.join(Path.home(), '.persian_life_manager', 'database.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db_manager = DatabaseManager(db_path)
    db_manager.initialize_database()
    
    # Create a web server with Persian Life Manager information
    class PersianLifeManagerHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            
            # Define HTML content as a string and then encode it to UTF-8
            html_content = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Persian Life Manager</title>
    <style>
        @font-face {
            font-family: 'Vazir';
            src: url('https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v30.1.0/dist/Vazir-Regular.woff2') format('woff2');
            font-weight: normal;
            font-style: normal;
        }
        
        body {
            font-family: 'Vazir', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #121212;
            color: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            text-align: center;
            direction: rtl;
        }
        
        .container {
            max-width: 800px;
            width: 90%;
            padding: 30px;
            background-color: #1e1e1e;
            border: 2px solid #00ffaa;
            border-radius: 10px;
            box-shadow: 0 0 30px rgba(0, 255, 170, 0.3);
        }
        
        .logo {
            font-size: 32px;
            font-weight: bold;
            color: #00ffaa;
            margin-bottom: 20px;
            text-shadow: 0 0 10px rgba(0, 255, 170, 0.7);
        }
        
        h1 {
            color: #00ffaa;
            margin-bottom: 20px;
        }
        
        p {
            font-size: 18px;
            margin-bottom: 30px;
            line-height: 1.6;
        }
        
        .status {
            background-color: rgba(0, 255, 170, 0.1);
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        
        .features {
            text-align: right;
            margin-top: 30px;
        }
        
        .features ul {
            list-style-type: none;
            padding-right: 10px;
        }
        
        .features li {
            margin-bottom: 15px;
            position: relative;
            padding-right: 30px;
        }
        
        .features li:before {
            content: "\u2713";  /* Unicode checkmark */
            color: #00ffaa;
            position: absolute;
            right: 0;
        }
        
        .demo-section {
            margin-top: 40px;
            padding: 20px;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
        }
        
        .demo-image {
            max-width: 100%;
            height: auto;
            border-radius: 5px;
            margin: 20px 0;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .neon-button {
            display: inline-block;
            background-color: transparent;
            color: #00ffaa;
            border: 2px solid #00ffaa;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 16px;
            font-weight: bold;
            text-decoration: none;
            margin-top: 20px;
            box-shadow: 0 0 10px rgba(0, 255, 170, 0.5);
            transition: all 0.3s ease;
        }
        
        .neon-button:hover {
            background-color: rgba(0, 255, 170, 0.1);
            box-shadow: 0 0 20px rgba(0, 255, 170, 0.8);
        }
        
        .footer {
            margin-top: 40px;
            font-size: 14px;
            color: rgba(255, 255, 255, 0.5);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">Persian Life Manager</div>
        
        <p>A comprehensive life management application with Persian calendar support</p>
        
        <div class="status">
            <h3>Server Status: Active</h3>
            <p>The application is running in Replit environment and the database is ready to use.</p>
        </div>
        
        <div class="features">
            <h3>Main Features:</h3>
            <ul>
                <li>Personal financial management with reporting and categorization</li>
                <li>Health tracking and body metrics</li>
                <li>Time planning and activity reminders</li>
                <li>Persian calendar with event support</li>
                <li>Smart recommendations using artificial intelligence</li>
            </ul>
        </div>
        
        <div class="demo-section">
            <h3>Installation and Usage</h3>
            <p>This application is designed for local execution. Download it and run it locally.</p>
            <a href="#" class="neon-button">Download App</a>
        </div>
        
        <div class="footer">
            <p>Persian Life Manager &copy; 2025</p>
        </div>
    </div>
</body>
</html>
'''.encode('utf-8')
            
            self.wfile.write(html_content)
            
        def log_message(self, format, *args):
            # Custom logging to reduce output noise
            if args[0].startswith('GET /favicon.ico'):
                return
            logger.info("%s - %s" % (self.address_string(), format % args))
    
    # Start HTTP server on port 5000
    PORT = 5000
    handler = PersianLifeManagerHandler
    
    logger.info(f"Starting Persian Life Manager web preview on port {PORT}")
    
    with socketserver.TCPServer(("0.0.0.0", PORT), handler) as httpd:
        logger.info(f"Server started successfully on port {PORT}")
        logger.info("Visit the web preview to see Persian Life Manager")
        httpd.serve_forever()

def main():
    """Main application entry point"""
    logger.info("Starting Persian Life Manager...")
    
    if IN_REPLIT:
        logger.info("Running in Replit environment - starting web preview")
        run_replit_web_preview()
    else:
        logger.info("Running in desktop environment - starting Qt application")
        run_desktop_app()

if __name__ == "__main__":
    main()
