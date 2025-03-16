"""
Email service for Persian Life Manager Application using SMTP
"""
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        """Initialize email service with SMTP settings from environment"""
        self.smtp_server = os.environ.get('SMTP_SERVER')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        self.smtp_username = os.environ.get('SMTP_USERNAME')
        self.smtp_password = os.environ.get('SMTP_PASSWORD')
        self.sender_email = os.environ.get('SENDER_EMAIL')
        
        if not all([
            self.smtp_server,
            self.smtp_port,
            self.smtp_username,
            self.smtp_password,
            self.sender_email
        ]):
            logger.error("Missing required SMTP configuration")
            raise ValueError("Missing required SMTP configuration")
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email with HTML content
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            html_content (str): Email content in HTML format
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = to_email
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            message.attach(html_part)
            
            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
                
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_verification_email(self, to_email: str, name: str, verification_link: str) -> bool:
        """Send verification email with verification link
        
        Args:
            to_email (str): Recipient email address
            name (str): Recipient name
            verification_link (str): Email verification link
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        subject = "تأیید ایمیل - Persian Life Manager"
        
        html_content = f'''
        <!DOCTYPE html>
        <html dir="rtl" lang="fa">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, Tahoma, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: #fff;
                    border-radius: 5px;
                    padding: 20px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #00ffaa;
                    color: #000;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    font-size: 0.9em;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>به Persian Life Manager خوش آمدید</h2>
                <p>سلام {name}،</p>
                <p>از ثبت‌نام شما در Persian Life Manager متشکریم. برای تکمیل ثبت‌نام و فعال‌سازی حساب کاربری خود، لطفاً روی دکمه زیر کلیک کنید:</p>
                
                <a href="{verification_link}" class="button">تأیید ایمیل</a>
                
                <p>اگر دکمه بالا کار نمی‌کند، می‌توانید لینک زیر را در مرورگر خود کپی و جایگذاری کنید:</p>
                <p>{verification_link}</p>
                
                <p>این لینک تا 24 ساعت معتبر است.</p>
                
                <div class="footer">
                    <p>با تشکر،<br>تیم Persian Life Manager</p>
                    <p>اگر شما درخواست ایجاد حساب کاربری نداده‌اید، لطفاً این ایمیل را نادیده بگیرید.</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        return self.send_email(to_email, subject, html_content)
    
    def send_password_reset_email(self, to_email: str, name: str, reset_link: str) -> bool:
        """Send password reset email with reset link
        
        Args:
            to_email (str): Recipient email address
            name (str): Recipient name
            reset_link (str): Password reset link
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        subject = "بازنشانی رمز عبور - Persian Life Manager"
        
        html_content = f'''
        <!DOCTYPE html>
        <html dir="rtl" lang="fa">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, Tahoma, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: #fff;
                    border-radius: 5px;
                    padding: 20px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #00ffaa;
                    color: #000;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    font-size: 0.9em;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>درخواست بازنشانی رمز عبور</h2>
                <p>سلام {name}،</p>
                <p>شما درخواست بازنشانی رمز عبور خود را در Persian Life Manager داده‌اید. برای تنظیم رمز عبور جدید، لطفاً روی دکمه زیر کلیک کنید:</p>
                
                <a href="{reset_link}" class="button">بازنشانی رمز عبور</a>
                
                <p>اگر دکمه بالا کار نمی‌کند، می‌توانید لینک زیر را در مرورگر خود کپی و جایگذاری کنید:</p>
                <p>{reset_link}</p>
                
                <p>این لینک تا 1 ساعت معتبر است.</p>
                
                <div class="footer">
                    <p>با تشکر،<br>تیم Persian Life Manager</p>
                    <p>اگر شما درخواست بازنشانی رمز عبور نداده‌اید، لطفاً این ایمیل را نادیده بگیرید و به ما اطلاع دهید.</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        return self.send_email(to_email, subject, html_content)