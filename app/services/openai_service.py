"""
OpenAI integration service for Persian Life Manager Application
"""

import os
import json
from openai import OpenAI

class OpenAIService:
    """Service for OpenAI API integration"""
    
    def __init__(self):
        """Initialize OpenAI service"""
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
    
    def get_health_advice(self, user_data):
        """Get personalized health advice using OpenAI
        
        Args:
            user_data (dict): Dictionary containing user health data
                - height (float): Height in cm
                - weight (float): Weight in kg
                - activity_level (str): Activity level description
                - health_conditions (str): Health conditions
                - goal_focus (str): Health goal
                - metrics (list, optional): Recent health metrics
                - exercises (list, optional): Recent exercises
                
        Returns:
            str: Personalized health advice in Persian
        """
        try:
            # Prepare the prompt in Persian
            prompt = f"""به عنوان یک متخصص سلامت و تناسب اندام، لطفاً توصیه‌های شخصی‌سازی شده برای کاربر با مشخصات زیر ارائه دهید:

قد: {user_data['height']} سانتی‌متر
وزن: {user_data['weight']} کیلوگرم
سطح فعالیت: {user_data['activity_level']}
شرایط سلامتی: {user_data['health_conditions']}
هدف: {user_data['goal_focus']}

لطفاً توصیه‌های خود را در قالب HTML و در بخش‌های زیر ارائه دهید:
1. برنامه ورزشی (شامل نوع، مدت و تکرار تمرینات)
2. توصیه‌های تغذیه‌ای (شامل کالری روزانه و ماکرونوترینت‌ها)
3. توصیه‌های خواب و استراحت
4. نکات ویژه با توجه به شرایط سلامتی

پاسخ باید به زبان فارسی و با تگ‌های HTML مناسب برای نمایش در وب باشد."""

            # Get advice from OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "شما یک متخصص سلامت و تناسب اندام هستید که توصیه‌های شخصی‌سازی شده به زبان فارسی ارائه می‌دهد."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"""<div dir="rtl" class="error-message">
            متأسفانه در دریافت توصیه‌های هوش مصنوعی خطایی رخ داد. لطفاً بعداً دوباره امتحان کنید.
            </div>"""
    
    def get_financial_advice(self, user_data):
        """Get personalized financial advice using OpenAI
        
        Args:
            user_data (dict): Dictionary containing user financial data
                - income (float): Monthly income
                - expenses (list): Recent expenses
                - savings (float): Current savings
                - goals (list): Financial goals
                
        Returns:
            str: Personalized financial advice in Persian
        """
        try:
            # Prepare the prompt in Persian
            expenses_text = "\n".join([f"- {exp['category']}: {exp['amount']:,} تومان" for exp in user_data['expenses']])
            goals_text = "\n".join([f"- {goal}" for goal in user_data['goals']])
            
            prompt = f"""به عنوان یک مشاور مالی، لطفاً توصیه‌های شخصی‌سازی شده برای کاربر با شرایط مالی زیر ارائه دهید:

درآمد ماهانه: {user_data['income']:,} تومان
پس‌انداز فعلی: {user_data['savings']:,} تومان

هزینه‌های اخیر:
{expenses_text}

اهداف مالی:
{goals_text}

لطفاً توصیه‌های خود را در قالب HTML و در بخش‌های زیر ارائه دهید:
1. مدیریت هزینه‌ها و بودجه‌بندی
2. استراتژی‌های پس‌انداز
3. توصیه‌های سرمایه‌گذاری
4. برنامه‌ریزی برای رسیدن به اهداف مالی

پاسخ باید به زبان فارسی و با تگ‌های HTML مناسب برای نمایش در وب باشد."""

            # Get advice from OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "شما یک مشاور مالی حرفه‌ای هستید که توصیه‌های شخصی‌سازی شده به زبان فارسی ارائه می‌دهد."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"""<div dir="rtl" class="error-message">
            متأسفانه در دریافت توصیه‌های مالی خطایی رخ داد. لطفاً بعداً دوباره امتحان کنید.
            </div>"""
    
    def get_time_management_advice(self, user_data):
        """Get personalized time management advice using OpenAI
        
        Args:
            user_data (dict): Dictionary containing user schedule data
                - tasks (list): Pending tasks
                - events (list): Upcoming events
                - priorities (list): User's priorities
                
        Returns:
            str: Personalized time management advice in Persian
        """
        try:
            # Prepare the prompt in Persian
            tasks_text = "\n".join([f"- {task['title']} (اولویت: {task['priority']})" for task in user_data['tasks']])
            events_text = "\n".join([f"- {event['title']} ({event['date']})" for event in user_data['events']])
            priorities_text = "\n".join([f"- {priority}" for priority in user_data['priorities']])
            
            prompt = f"""به عنوان یک متخصص مدیریت زمان، لطفاً توصیه‌های شخصی‌سازی شده برای کاربر با برنامه زیر ارائه دهید:

وظایف در انتظار:
{tasks_text}

رویدادهای پیش رو:
{events_text}

اولویت‌های کاربر:
{priorities_text}

لطفاً توصیه‌های خود را در قالب HTML و در بخش‌های زیر ارائه دهید:
1. اولویت‌بندی وظایف و زمان‌بندی
2. مدیریت رویدادها و جلسات
3. تکنیک‌های بهره‌وری و تمرکز
4. توصیه‌های تعادل کار و زندگی

پاسخ باید به زبان فارسی و با تگ‌های HTML مناسب برای نمایش در وب باشد."""

            # Get advice from OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "شما یک متخصص مدیریت زمان هستید که توصیه‌های شخصی‌سازی شده به زبان فارسی ارائه می‌دهد."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"""<div dir="rtl" class="error-message">
            متأسفانه در دریافت توصیه‌های مدیریت زمان خطایی رخ داد. لطفاً بعداً دوباره امتحان کنید.
            </div>"""