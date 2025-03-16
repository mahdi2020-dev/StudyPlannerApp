"""
AI Chat Service for Interactive Conversation with Persian Life Manager
"""
import os
import logging
import json
from datetime import datetime
from openai import OpenAI

logger = logging.getLogger(__name__)

class AIChatService:
    """Interactive AI Chat Service using OpenAI"""
    
    def __init__(self):
        """Initialize the AI Chat Service"""
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.client = None
        
        if self.openai_api_key:
            try:
                self.client = OpenAI(api_key=self.openai_api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {str(e)}")
                self.client = None
    
    def chat(self, user_message, user_data=None, chat_history=None):
        """Chat with the AI using OpenAI
        
        Args:
            user_message (str): User's message
            user_data (dict, optional): User data to provide context
            chat_history (list, optional): Previous chat messages
            
        Returns:
            str: AI response in Persian
        """
        if not self.client:
            return "متأسفانه سرویس هوش مصنوعی در دسترس نیست. لطفاً بعداً دوباره تلاش کنید."
        
        try:
            # Create messages array starting with system message
            messages = [
                {
                    "role": "system", 
                    "content": self._create_system_prompt(user_data)
                }
            ]
            
            # Add chat history if provided
            if chat_history and isinstance(chat_history, list):
                # Take last 10 messages to avoid token limits
                for msg in chat_history[-10:]:
                    if 'role' in msg and 'content' in msg:
                        messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
            
            # Add user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in chat method: {str(e)}")
            return f"متأسفانه خطایی رخ داد: {str(e)}"
    
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
        if not self.client:
            return {
                "error": "سرویس هوش مصنوعی در دسترس نیست. لطفاً بعداً دوباره تلاش کنید."
            }
        
        try:
            # Create a prompt for activity suggestion
            prompt = f"""با توجه به اطلاعات زیر، یک فعالیت مناسب پیشنهاد دهید:
- زمان روز: {time_of_day}
- سطح انرژی: {energy_level}
- زمان در دسترس: {available_time} دقیقه

لطفاً پاسخ را در قالب JSON با ساختار زیر ارائه دهید:
{{
    "activity": "عنوان فعالیت پیشنهادی",
    "reason": "دلیل این پیشنهاد"
}}
"""
            
            # Add user context if available
            if user_data:
                user_context = self._format_user_data(user_data)
                prompt += f"\n\nاطلاعات بیشتر در مورد کاربر:\n{user_context}"
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "شما دستیار هوشمند Persian Life Manager هستید که فعالیت‌های مناسب را برای کاربران پیشنهاد می‌دهید."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=400,
                response_format={"type": "json_object"}
            )
            
            try:
                result = json.loads(response.choices[0].message.content)
                return {
                    "activity": result.get("activity", "فعالیت پیشنهادی"),
                    "reason": result.get("reason", "دلیل نامشخص")
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw text
                logger.warning("Failed to parse JSON response from OpenAI")
                return {
                    "activity": "پیاده‌روی",
                    "reason": "متأسفانه نتوانستیم پیشنهاد دقیقی ارائه دهیم. پیاده‌روی یک فعالیت مفید برای اکثر زمان‌ها است."
                }
                
        except Exception as e:
            logger.error(f"Error in suggest_activity method: {str(e)}")
            return {
                "error": f"متأسفانه خطایی رخ داد: {str(e)}"
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
        if not self.client:
            return {
                "error": "سرویس هوش مصنوعی در دسترس نیست. لطفاً بعداً دوباره تلاش کنید."
            }
        
        try:
            # Format the events and tasks for the prompt
            events_text = "رویدادها:\n"
            if events:
                for i, event in enumerate(events):
                    events_text += f"{i+1}. {event.title} - {event.date}"
                    if event.start_time:
                        events_text += f" {event.start_time}"
                    events_text += "\n"
            else:
                events_text += "هیچ رویدادی وجود ندارد.\n"
            
            tasks_text = "وظایف:\n"
            if tasks:
                for i, task in enumerate(tasks):
                    completed = "تکمیل شده" if task.completed else "در انتظار"
                    tasks_text += f"{i+1}. {task.title} - موعد: {task.due_date} - وضعیت: {completed}\n"
            else:
                tasks_text += "هیچ وظیفه‌ای وجود ندارد.\n"
            
            goals_text = ""
            if goals:
                goals_text = "اهداف:\n"
                for i, goal in enumerate(goals):
                    goals_text += f"{i+1}. {goal.title}\n"
            
            # Create the prompt
            prompt = f"""لطفاً تقویم زیر را تحلیل کرده و پیشنهادهایی برای بهینه‌سازی برنامه و مدیریت زمان ارائه دهید:

{events_text}

{tasks_text}

{goals_text}

لطفاً تحلیل خود را در قالب JSON با ساختار زیر ارائه دهید:
{{
    "analysis": "تحلیل کلی برنامه",
    "issues": ["مشکل 1", "مشکل 2", ...],
    "suggestions": ["پیشنهاد 1", "پیشنهاد 2", ...]
}}
"""
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "شما یک متخصص مدیریت زمان و بهره‌وری هستید که به کاربران Persian Life Manager کمک می‌کنید."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw text
                logger.warning("Failed to parse JSON response from OpenAI")
                return {
                    "analysis": "تحلیل برنامه شما",
                    "issues": ["امکان تحلیل دقیق برنامه وجود ندارد"],
                    "suggestions": ["لطفاً اطلاعات بیشتری وارد کنید تا بتوانیم تحلیل دقیق‌تری ارائه دهیم"]
                }
                
        except Exception as e:
            logger.error(f"Error in analyze_schedule method: {str(e)}")
            return {
                "error": f"متأسفانه خطایی رخ داد: {str(e)}"
            }
    
    def generate_daily_plan(self, date, user_data=None):
        """Generate a daily plan for the user
        
        Args:
            date (str): Date for the plan (YYYY-MM-DD)
            user_data (dict, optional): User data for context
            
        Returns:
            str: Daily plan in HTML format
        """
        if not self.client:
            return "متأسفانه سرویس هوش مصنوعی در دسترس نیست. لطفاً بعداً دوباره تلاش کنید."
        
        try:
            # Create a prompt for daily plan generation
            prompt = f"""لطفاً یک برنامه روزانه کامل برای تاریخ {date} ایجاد کنید که شامل موارد زیر باشد:
- برنامه صبحگاهی
- پیشنهادات ورزشی
- برنامه غذایی (صبحانه، ناهار، شام و میان‌وعده‌ها)
- زمان‌های کار و استراحت
- فعالیت‌های عصرگاهی
- برنامه شبانگاهی و آماده‌سازی برای خواب

لطفاً برنامه را طوری طراحی کنید که بهینه و متعادل باشد و سلامت جسمی و روانی کاربر را در نظر بگیرد.
"""
            
            # Add user context if available
            if user_data:
                user_context = self._format_user_data(user_data)
                prompt += f"\n\nاطلاعات بیشتر در مورد کاربر:\n{user_context}"
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "شما دستیار هوشمند Persian Life Manager هستید که برنامه‌های روزانه متعادل و بهینه را برای کاربران طراحی می‌کنید."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"Error in generate_daily_plan method: {str(e)}")
            return f"متأسفانه خطایی رخ داد: {str(e)}"
    
    def _create_system_prompt(self, user_data):
        """Create a system prompt with user context
        
        Args:
            user_data (dict): User data for context
            
        Returns:
            str: System prompt
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        system_prompt = f"""شما دستیار هوشمند Persian Life Manager هستید که به کاربران در مدیریت زندگی، سلامت، امور مالی و برنامه‌ریزی کمک می‌کنید.

امروز {current_date} است.

دستورالعمل‌های مهم:
1. همیشه به فارسی پاسخ دهید (مگر اینکه کاربر به زبان دیگری سؤال کند).
2. پاسخ‌هایتان باید دقیق، مفید و مرتبط با درخواست کاربر باشد.
3. پاسخ‌های خود را کوتاه و مختصر نگه دارید (حداکثر 3-4 پاراگراف).
4. همیشه صادق باشید. اگر اطلاعات کافی ندارید، این را اعلام کنید.
5. محتوای نامناسب، غیراخلاقی یا تبلیغاتی ارائه ندهید.
6. در مورد مسائل مالی و سلامت احتیاط کنید و تأکید کنید که توصیه‌های شما جایگزین مشاوره تخصصی نیست.

"""
        
        # Add user context if available
        if user_data:
            user_context = self._format_user_data(user_data)
            system_prompt += f"\nاطلاعات کاربر:\n{user_context}\n"
        
        return system_prompt
    
    def _format_user_data(self, user_data):
        """Format user data for the prompt
        
        Args:
            user_data (dict): User data
            
        Returns:
            str: Formatted user data
        """
        if not user_data:
            return "اطلاعاتی در مورد کاربر در دسترس نیست."
        
        formatted_data = f"نام کاربری: {user_data.get('username', 'نامشخص')}\n\n"
        
        # Format finances
        if 'finances' in user_data and user_data['finances']:
            finances = user_data['finances']
            formatted_data += "اطلاعات مالی:\n"
            
            if 'transactions' in finances and finances['transactions']:
                transactions = finances['transactions']
                formatted_data += "تراکنش‌های اخیر:\n"
                
                for i, transaction in enumerate(transactions[:5]):  # Show last 5 transactions
                    type_str = "هزینه" if transaction.type == "expense" else "درآمد"
                    formatted_data += f"- {transaction.title}: {transaction.amount:,} تومان ({type_str})\n"
        
        # Format health
        if 'health' in user_data and user_data['health']:
            health = user_data['health']
            formatted_data += "\nاطلاعات سلامتی:\n"
            
            if 'metrics' in health and health['metrics']:
                metrics = health['metrics']
                if metrics:
                    latest_metric = metrics[0]  # Assuming they are sorted by date
                    formatted_data += f"آخرین معیارهای سلامتی (تاریخ: {latest_metric.date}):\n"
                    
                    if latest_metric.weight:
                        formatted_data += f"- وزن: {latest_metric.weight} کیلوگرم\n"
                    if latest_metric.systolic and latest_metric.diastolic:
                        formatted_data += f"- فشار خون: {latest_metric.systolic}/{latest_metric.diastolic}\n"
            
            if 'exercises' in health and health['exercises']:
                exercises = health['exercises']
                formatted_data += "تمرینات اخیر:\n"
                
                for i, exercise in enumerate(exercises[:3]):  # Show last 3 exercises
                    formatted_data += f"- {exercise.exercise_type}: {exercise.duration} دقیقه ({exercise.date})\n"
        
        # Format calendar
        if 'calendar' in user_data and user_data['calendar']:
            calendar = user_data['calendar']
            formatted_data += "\nاطلاعات تقویم:\n"
            
            if 'events' in calendar and calendar['events']:
                events = calendar['events']
                formatted_data += "رویدادهای آینده:\n"
                
                for i, event in enumerate(events[:3]):  # Show next 3 events
                    time_str = f" ساعت {event.start_time}" if event.start_time else ""
                    formatted_data += f"- {event.title}: {event.date}{time_str}\n"
            
            if 'tasks' in calendar and calendar['tasks']:
                tasks = calendar['tasks']
                formatted_data += "وظایف در انتظار:\n"
                
                for i, task in enumerate(tasks[:3]):  # Show 3 pending tasks
                    formatted_data += f"- {task.title} (موعد: {task.due_date})\n"
        
        return formatted_data