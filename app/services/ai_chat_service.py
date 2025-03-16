"""
AI Chat Service for Interactive Conversation with Persian Life Manager
"""

import os
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class AIChatService:
    """Interactive AI Chat Service using OpenAI"""
    
    def __init__(self):
        """Initialize the AI Chat Service"""
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
        self.system_prompt = """
        شما یک دستیار مجازی هوشمند هستید که به مدیریت زندگی کاربران فارسی‌زبان کمک می‌کنید.
        شما می‌توانید در زمینه‌های مدیریت زمان، برنامه‌ریزی مالی، سلامت و تندرستی، اهداف شخصی و حرفه‌ای راهنمایی ارائه دهید.
        پاسخ‌های شما باید مختصر، کاربردی و به زبان فارسی باشد.
        
        قابلیت‌های شما:
        1. پیشنهاد فعالیت‌های بهینه براساس زمان روز، انرژی و اهداف کاربر
        2. کمک به اولویت‌بندی وظایف و برنامه‌ریزی زمان
        3. ارائه‌ی توصیه‌های مالی، سلامتی و مدیریت زمان
        4. برنامه‌ریزی روزانه، هفتگی و ماهانه
        5. تنظیم اهداف SMART و پیگیری پیشرفت
        
        لحن شما باید دوستانه و انگیزه‌بخش باشد. از اصول روانشناسی مثبت استفاده کنید تا کاربر احساس توانمندی کند.
        """
    
    def chat(self, user_message, user_data=None, chat_history=None):
        """Chat with the AI using OpenAI
        
        Args:
            user_message (str): User's message
            user_data (dict, optional): User data to provide context
            chat_history (list, optional): Previous chat messages
            
        Returns:
            str: AI response in Persian
        """
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add chat history if available
            if chat_history:
                messages.extend(chat_history[-10:])  # Keep last 10 messages for context
            
            # Add user data for context if available
            if user_data:
                context = self._format_user_data(user_data)
                messages.append({"role": "system", "content": f"اطلاعات کاربر: {context}"})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in AI chat: {str(e)}")
            return "متأسفانه در برقراری ارتباط با هوش مصنوعی خطایی رخ داد. لطفاً دوباره تلاش کنید."
    
    def suggest_activity(self, time_of_day, energy_level, available_time, user_data=None):
        """Suggest an activity based on time of day, energy level and available time
        
        Args:
            time_of_day (str): Time of day (morning, afternoon, evening)
            energy_level (str): Energy level (low, medium, high)
            available_time (int): Available time in minutes
            user_data (dict, optional): User data to provide context
            
        Returns:
            dict: Suggested activity with reason
        """
        try:
            context = ""
            if user_data:
                context = self._format_user_data(user_data)
                
            prompt = f"""
            با توجه به شرایط کاربر، یک فعالیت مناسب پیشنهاد دهید:
            
            زمان روز: {time_of_day}
            سطح انرژی: {energy_level}
            زمان در دسترس: {available_time} دقیقه
            
            {context}
            
            پاسخ را به صورت JSON با فرمت زیر برگردانید:
            {{
                "activity": "نام فعالیت",
                "duration": زمان به دقیقه (عدد),
                "reason": "دلیل پیشنهاد این فعالیت",
                "benefit": "مزایای این فعالیت"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"Error suggesting activity: {str(e)}")
            return {
                "activity": "استراحت کوتاه",
                "duration": min(available_time, 15),
                "reason": "در حال حاضر سیستم پیشنهاددهنده با مشکل مواجه شده است",
                "benefit": "استراحت کوتاه به شما کمک می‌کند انرژی خود را بازیابی کنید"
            }
    
    def analyze_schedule(self, events, tasks, goals=None):
        """Analyze a user's schedule and provide optimization suggestions
        
        Args:
            events (list): List of calendar events
            tasks (list): List of tasks
            goals (list, optional): User's goals
            
        Returns:
            dict: Schedule analysis and suggestions
        """
        try:
            events_text = "\n".join([f"- {event.get('title')}: {event.get('date')} {event.get('start_time', '')}-{event.get('end_time', '')}" for event in events[:10]])
            tasks_text = "\n".join([f"- {task.get('title')} (اولویت: {task.get('priority')}, موعد: {task.get('due_date')})" for task in tasks[:10]])
            goals_text = ""
            if goals:
                goals_text = "\n".join([f"- {goal.get('title')}" for goal in goals[:5]])
            
            prompt = f"""
            برنامه کاربر را تحلیل کرده و پیشنهادهایی برای بهینه‌سازی ارائه دهید:
            
            رویدادها:
            {events_text}
            
            وظایف:
            {tasks_text}
            
            {"اهداف:" if goals else ""}
            {goals_text}
            
            پاسخ را به صورت JSON با فرمت زیر برگردانید:
            {{
                "overbooked_days": ["تاریخ‌های شلوغ"],
                "optimization_tips": ["پیشنهادات بهینه‌سازی"],
                "task_prioritization": ["پیشنهادات اولویت‌بندی وظایف"],
                "balance_suggestions": ["پیشنهادات تعادل کار و زندگی"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing schedule: {str(e)}")
            return {
                "overbooked_days": [],
                "optimization_tips": ["تقسیم کارهای بزرگ به وظایف کوچکتر", "استفاده از تکنیک پومودورو برای تمرکز بهتر"],
                "task_prioritization": ["اولویت‌بندی وظایف بر اساس اهمیت و فوریت"],
                "balance_suggestions": ["اختصاص زمان مشخص برای استراحت و تفریح"]
            }
    
    def generate_daily_plan(self, date, user_data=None):
        """Generate a daily plan for the user
        
        Args:
            date (str): Date for the plan (YYYY-MM-DD)
            user_data (dict, optional): User data for context
            
        Returns:
            str: Daily plan in HTML format
        """
        try:
            context = ""
            if user_data:
                context = self._format_user_data(user_data)
                
            prompt = f"""
            یک برنامه روزانه برای کاربر در تاریخ {date} ایجاد کنید.
            
            {context}
            
            برنامه باید شامل:
            1. زمان بیدار شدن و خوابیدن
            2. وعده‌های غذایی
            3. زمان‌های کار و استراحت
            4. فعالیت‌های ورزشی
            5. وظایف و کارهای مهم
            
            پاسخ باید به زبان فارسی و با تگ‌های HTML مناسب برای نمایش در وب باشد.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating daily plan: {str(e)}")
            return f"""<div dir="rtl" class="daily-plan">
            <h3>برنامه پیشنهادی روزانه</h3>
            <p>متأسفانه در ایجاد برنامه روزانه خطایی رخ داد. لطفاً دوباره تلاش کنید.</p>
            </div>"""
    
    def _format_user_data(self, user_data):
        """Format user data for the prompt
        
        Args:
            user_data (dict): User data
            
        Returns:
            str: Formatted user data
        """
        result = []
        
        if 'health' in user_data:
            health = user_data['health']
            health_info = []
            
            if 'metrics' in health and health['metrics']:
                latest = health['metrics'][0]
                if 'weight' in latest:
                    health_info.append(f"وزن: {latest['weight']} کیلوگرم")
                if 'height' in latest:
                    health_info.append(f"قد: {latest['height']} سانتی‌متر")
            
            if 'exercises' in health:
                health_info.append(f"تعداد ورزش‌های اخیر: {len(health['exercises'])}")
            
            if health_info:
                result.append("اطلاعات سلامتی: " + "، ".join(health_info))
        
        if 'finance' in user_data:
            finance = user_data['finance']
            finance_info = []
            
            if 'income' in finance:
                finance_info.append(f"درآمد ماهانه: {finance['income']:,} تومان")
            
            if 'expenses' in finance:
                total_expenses = sum(exp['amount'] for exp in finance['expenses'])
                finance_info.append(f"هزینه‌های اخیر: {total_expenses:,} تومان")
            
            if finance_info:
                result.append("اطلاعات مالی: " + "، ".join(finance_info))
        
        if 'calendar' in user_data:
            calendar = user_data['calendar']
            calendar_info = []
            
            if 'events' in calendar:
                calendar_info.append(f"تعداد رویدادهای آینده: {len(calendar['events'])}")
            
            if 'tasks' in calendar:
                pending = len([t for t in calendar['tasks'] if not t.get('completed', False)])
                calendar_info.append(f"وظایف در انتظار: {pending}")
            
            if calendar_info:
                result.append("اطلاعات تقویم: " + "، ".join(calendar_info))
        
        return "\n".join(result)