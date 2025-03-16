"""
AI Chat Service for Interactive Conversation with Persian Life Manager
"""
import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class AIChatService:
    """Interactive AI Chat Service using OpenAI"""
    
    def __init__(self):
        """Initialize the AI Chat Service"""
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(api_key=self.api_key)
        logger.info("AI Chat Service initialized")
        
    def chat(self, user_message, user_data=None, chat_history=None):
        """Chat with the AI using OpenAI
        
        Args:
            user_message (str): User's message
            user_data (dict, optional): User data to provide context
            chat_history (list, optional): Previous chat messages
            
        Returns:
            str: AI response in Persian
        """
        if not self.api_key:
            return "متأسفانه، در حال حاضر دسترسی به چت هوشمند امکان‌پذیر نیست. لطفاً بعداً تلاش کنید."
        
        chat_history = chat_history or []
        
        # Create system prompt with user context
        system_prompt = self._create_system_prompt(user_data)
        
        # Format messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add chat history
        for msg in chat_history:
            messages.append(msg)
            
        # Add the current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error in AIChatService.chat: {str(e)}")
            return "متأسفانه خطایی در ارتباط با سرویس هوش مصنوعی رخ داد. لطفاً بعداً تلاش کنید."
            
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
        if not self.api_key:
            return {
                "activity": "متأسفانه، در حال حاضر امکان ارائه پیشنهاد وجود ندارد.",
                "reason": "دسترسی به سرویس هوش مصنوعی امکان‌پذیر نیست."
            }
        
        # Prepare user context
        context = ""
        if user_data:
            if "health" in user_data and "exercises" in user_data["health"]:
                recent_exercises = user_data["health"]["exercises"]
                if recent_exercises:
                    context += "فعالیت‌های اخیر: "
                    for exercise in recent_exercises:
                        context += f"{exercise.exercise_type} ({exercise.duration} دقیقه), "
                    context = context[:-2] + "\\n"
            
            if "calendar" in user_data and "events" in user_data["calendar"]:
                upcoming_events = user_data["calendar"]["events"]
                if upcoming_events:
                    context += "رویدادهای آینده: "
                    for event in upcoming_events:
                        context += f"{event.title} (تاریخ: {event.date}), "
                    context = context[:-2] + "\\n"
                    
        # Map English time of day to Persian
        time_of_day_persian = {
            "morning": "صبح",
            "afternoon": "بعد از ظهر",
            "evening": "عصر/شب"
        }.get(time_of_day, "نامشخص")
        
        # Map English energy level to Persian  
        energy_level_persian = {
            "low": "کم",
            "medium": "متوسط",
            "high": "زیاد"
        }.get(energy_level, "نامشخص")
        
        prompt = f"""لطفاً با توجه به اطلاعات زیر، یک فعالیت مناسب پیشنهاد دهید:

زمان روز: {time_of_day_persian}
سطح انرژی: {energy_level_persian}
زمان در دسترس: {available_time} دقیقه

{context}

لطفاً پیشنهاد خود را به صورت یک فعالیت مشخص در قالب JSON با فرمت زیر ارائه دهید:
{{
  "activity": "نام فعالیت",
  "reason": "دلیل پیشنهاد این فعالیت"
}}
"""
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "شما یک دستیار هوشمند برای مدیریت زندگی هستید."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return {
                "activity": result.get("activity", "فعالیت نامشخص"),
                "reason": result.get("reason", "دلیلی ارائه نشده است")
            }
            
        except Exception as e:
            logger.error(f"Error in AIChatService.suggest_activity: {str(e)}")
            return {
                "activity": "متأسفانه، در حال حاضر امکان ارائه پیشنهاد وجود ندارد.",
                "reason": f"خطا: {str(e)}"
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
        if not self.api_key:
            return {
                "analysis": "متأسفانه، در حال حاضر امکان تحلیل برنامه وجود ندارد.",
                "suggestions": ["دسترسی به سرویس هوش مصنوعی امکان‌پذیر نیست."]
            }
        
        # Format events
        events_str = ""
        for event in events:
            time_info = ""
            if event.all_day:
                time_info = "تمام روز"
            else:
                time_info = f"{event.start_time or ''} - {event.end_time or ''}"
            events_str += f"• {event.title}: {event.date} {time_info}\\n"
            if event.description:
                events_str += f"  توضیحات: {event.description}\\n"
        
        # Format tasks
        tasks_str = ""
        for task in tasks:
            priority = {
                "high": "اولویت بالا",
                "medium": "اولویت متوسط", 
                "low": "اولویت پایین"
            }.get(task.priority, "")
            
            status = "انجام شده" if task.completed else "در انتظار"
            tasks_str += f"• {task.title}: {priority}, {status}, تاریخ: {task.due_date}\\n"
        
        # Format goals (if provided)
        goals_str = ""
        if goals:
            for goal in goals:
                goals_str += f"• {goal.title}\\n"
        
        prompt = f"""لطفاً برنامه زمانی زیر را تحلیل کرده و پیشنهادهایی برای بهینه‌سازی آن ارائه دهید.

رویدادها:
{events_str or "هیچ رویدادی موجود نیست"}

وظایف:
{tasks_str or "هیچ وظیفه‌ای موجود نیست"}

{'اهداف:\\n' + goals_str if goals_str else ''}

لطفاً تحلیل خود را در مورد وضعیت فعلی برنامه و پیشنهادهایی برای بهبود آن در قالب JSON با فرمت زیر ارائه دهید:
{{
  "analysis": "تحلیل کلی از برنامه",
  "suggestions": ["پیشنهاد 1", "پیشنهاد 2", "پیشنهاد 3"]
}}
"""
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "شما یک متخصص مدیریت زمان و بهره‌وری هستید."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return {
                "analysis": result.get("analysis", "تحلیلی ارائه نشده است"),
                "suggestions": result.get("suggestions", ["پیشنهادی ارائه نشده است"])
            }
            
        except Exception as e:
            logger.error(f"Error in AIChatService.analyze_schedule: {str(e)}")
            return {
                "analysis": "متأسفانه، در حال حاضر امکان تحلیل برنامه وجود ندارد.",
                "suggestions": [f"خطا: {str(e)}"]
            }

    def generate_daily_plan(self, date, user_data=None):
        """Generate a daily plan for the user
        
        Args:
            date (str): Date for the plan (YYYY-MM-DD)
            user_data (dict, optional): User data for context
            
        Returns:
            str: Daily plan in HTML format
        """
        if not self.api_key:
            return "<p>متأسفانه، در حال حاضر امکان ایجاد برنامه روزانه وجود ندارد. لطفاً بعداً تلاش کنید.</p>"
        
        # Format user data for context
        context = self._format_user_data(user_data) if user_data else ""
        
        prompt = f"""لطفاً یک برنامه روزانه برای تاریخ {date} با توجه به اطلاعات زیر ایجاد کنید:

{context}

برنامه باید شامل توصیه‌هایی برای فعالیت‌های بدنی، تغذیه، کارهای مهم و زمان استراحت باشد. لطفاً برنامه را به صورت ساعتی و با جزئیات ارائه دهید.

لطفاً پاسخ را به صورت HTML با تگ‌های <h3> برای بخش‌ها و <ul> و <li> برای لیست‌ها ارائه دهید.
"""
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "شما یک متخصص برنامه‌ریزی روزانه و مدیریت زمان هستید."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in AIChatService.generate_daily_plan: {str(e)}")
            return "<p>متأسفانه، در حال حاضر امکان ایجاد برنامه روزانه وجود ندارد. لطفاً بعداً تلاش کنید.</p>"
    
    def _create_system_prompt(self, user_data):
        """Create a system prompt with user context
        
        Args:
            user_data (dict): User data for context
            
        Returns:
            str: System prompt
        """
        base_prompt = """شما دستیار هوشمند Persian Life Manager هستید. 
وظیفه شما پاسخ‌گویی به سوالات کاربر در مورد مدیریت مالی، سلامت و زمان‌بندی است.
پاسخ‌های خود را به زبان فارسی و با لحنی دوستانه ارائه دهید.
از اطلاعات زیر برای شخصی‌سازی پاسخ‌های خود استفاده کنید.
"""
        
        if not user_data:
            return base_prompt
        
        user_context = "\\n\\nاطلاعات کاربر:\\n"
        
        # Add username
        if "username" in user_data:
            user_context += f"نام کاربری: {user_data['username']}\\n"
        
        # Add financial data
        if "finances" in user_data and "transactions" in user_data["finances"]:
            transactions = user_data["finances"]["transactions"]
            if transactions:
                user_context += "\\nتراکنش‌های اخیر:\\n"
                for transaction in transactions[:5]:  # Limit to 5 recent transactions
                    transaction_type = "هزینه" if transaction.type == "expense" else "درآمد"
                    user_context += f"- {transaction.title}: {transaction.amount} ({transaction_type})\\n"
        
        # Add health data
        if "health" in user_data:
            if "metrics" in user_data["health"] and user_data["health"]["metrics"]:
                metrics = user_data["health"]["metrics"]
                user_context += "\\nمعیارهای سلامتی اخیر:\\n"
                for metric in metrics[:3]:  # Limit to 3 recent metrics
                    if metric.weight:
                        user_context += f"- وزن: {metric.weight} کیلوگرم\\n"
                    if metric.systolic and metric.diastolic:
                        user_context += f"- فشار خون: {metric.systolic}/{metric.diastolic}\\n"
            
            if "exercises" in user_data["health"] and user_data["health"]["exercises"]:
                exercises = user_data["health"]["exercises"]
                user_context += "\\nفعالیت‌های ورزشی اخیر:\\n"
                for exercise in exercises[:3]:  # Limit to 3 recent exercises
                    user_context += f"- {exercise.exercise_type}: {exercise.duration} دقیقه\\n"
        
        # Add calendar data
        if "calendar" in user_data:
            if "events" in user_data["calendar"] and user_data["calendar"]["events"]:
                events = user_data["calendar"]["events"]
                user_context += "\\nرویدادهای آینده:\\n"
                for event in events[:3]:  # Limit to 3 upcoming events
                    user_context += f"- {event.title}: {event.date}\\n"
            
            if "tasks" in user_data["calendar"] and user_data["calendar"]["tasks"]:
                tasks = user_data["calendar"]["tasks"]
                user_context += "\\nوظایف در انتظار:\\n"
                for task in tasks[:3]:  # Limit to 3 pending tasks
                    user_context += f"- {task.title}: {task.due_date}\\n"
        
        return base_prompt + user_context
    
    def _format_user_data(self, user_data):
        """Format user data for the prompt
        
        Args:
            user_data (dict): User data
            
        Returns:
            str: Formatted user data
        """
        if not user_data:
            return ""
            
        formatted_data = ""
        
        # Format financial data
        if "finances" in user_data and "transactions" in user_data["finances"]:
            transactions = user_data["finances"]["transactions"]
            if transactions:
                formatted_data += "اطلاعات مالی:\\n"
                income = sum(t.amount for t in transactions if t.type == "income")
                expenses = sum(t.amount for t in transactions if t.type == "expense")
                formatted_data += f"مجموع درآمد: {income}\\n"
                formatted_data += f"مجموع هزینه‌ها: {expenses}\\n"
        
        # Format health data
        if "health" in user_data:
            formatted_data += "\\nاطلاعات سلامتی:\\n"
            
            if "metrics" in user_data["health"] and user_data["health"]["metrics"]:
                latest_metric = user_data["health"]["metrics"][0]
                if latest_metric.weight:
                    formatted_data += f"وزن فعلی: {latest_metric.weight} کیلوگرم\\n"
                if latest_metric.height:
                    formatted_data += f"قد: {latest_metric.height} سانتی‌متر\\n"
                if latest_metric.systolic and latest_metric.diastolic:
                    formatted_data += f"فشار خون: {latest_metric.systolic}/{latest_metric.diastolic}\\n"
            
            if "exercises" in user_data["health"] and user_data["health"]["exercises"]:
                formatted_data += "فعالیت‌های ورزشی اخیر:\\n"
                for exercise in user_data["health"]["exercises"][:3]:
                    formatted_data += f"- {exercise.exercise_type}: {exercise.duration} دقیقه\\n"
        
        # Format calendar data
        if "calendar" in user_data:
            formatted_data += "\\nاطلاعات تقویم:\\n"
            
            if "events" in user_data["calendar"] and user_data["calendar"]["events"]:
                formatted_data += "رویدادهای امروز و فردا:\\n"
                for event in user_data["calendar"]["events"][:3]:
                    formatted_data += f"- {event.title}: {event.date}\\n"
            
            if "tasks" in user_data["calendar"] and user_data["calendar"]["tasks"]:
                formatted_data += "وظایف مهم:\\n"
                for task in user_data["calendar"]["tasks"][:3]:
                    priority = "اولویت بالا" if task.priority == "high" else "اولویت متوسط" if task.priority == "medium" else "اولویت پایین"
                    formatted_data += f"- {task.title}: {priority}, تاریخ: {task.due_date}\\n"
        
        return formatted_data