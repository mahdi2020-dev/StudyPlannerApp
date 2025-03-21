"""
AI Chat Service for Interactive Conversation with Persian Life Manager using Hugging Face API
"""
import os
import logging
import json
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

class AIChatServiceHF:
    """Interactive AI Chat Service using Hugging Face API"""
    
    def __init__(self):
        """Initialize the AI Chat Service"""
        # Try multiple environment variable names to be flexible
        self.api_key = os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("XAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.api_url = "https://api-inference.huggingface.co/models/"
        self.default_model = "meta-llama/Meta-Llama-3-8B-Instruct"  # Good for multilingual support
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        
        if not self.api_key:
            logger.warning("Hugging Face API key not found in any environment variable (HUGGINGFACE_API_KEY, XAI_API_KEY, or OPENAI_API_KEY)")
        else:
            logger.info("Hugging Face client initialized successfully")
    
    def query_model(self, model, inputs, parameters=None):
        """Make API call to Hugging Face
        
        Args:
            model (str): Model ID
            inputs (str): Input text
            parameters (dict, optional): Optional parameters
            
        Returns:
            dict: API response
        """
        if not self.api_key:
            logger.error("Hugging Face API key not set")
            return {"error": "API key not set"}
        
        url = f"{self.api_url}{model}"
        payload = {"inputs": inputs}
        
        if parameters:
            payload["parameters"] = parameters
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()  # Raise exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error querying Hugging Face model: {str(e)}")
            return {"error": str(e)}
            
    def chat(self, user_message, user_data=None, chat_history=None):
        """Chat with the AI using Hugging Face
        
        Args:
            user_message (str): User's message
            user_data (dict, optional): User data to provide context
            chat_history (list, optional): Previous chat messages
            
        Returns:
            str: AI response in Persian
        """
        if not self.api_key:
            return "متأسفانه سرویس هوش مصنوعی در دسترس نیست. لطفاً بعداً دوباره تلاش کنید."
        
        try:
            # Create system prompt
            system_prompt = self._create_system_prompt(user_data)
            
            # Format chat history
            history_text = ""
            if chat_history and isinstance(chat_history, list):
                # Take last 5 messages to avoid token limits
                for msg in chat_history[-5:]:
                    if 'role' in msg and 'content' in msg:
                        role = "کاربر" if msg['role'] == "user" else "دستیار"
                        history_text += f"{role}: {msg['content']}\n\n"
            
            # Create the full prompt
            prompt = f"{system_prompt}\n\n{history_text}\nکاربر: {user_message}\n\nدستیار:"
            
            # Call Hugging Face API
            response = self.query_model(
                self.default_model,
                prompt,
                parameters={"max_new_tokens": 800, "temperature": 0.7}
            )
            
            if isinstance(response, list) and len(response) > 0:
                # Different response formats from different models
                if "generated_text" in response[0]:
                    result = response[0]["generated_text"]
                else:
                    result = str(response[0])
            elif isinstance(response, dict):
                if "error" in response:
                    return f"متأسفانه خطایی رخ داد: {response['error']}"
                elif "generated_text" in response:
                    result = response["generated_text"]
                else:
                    result = str(response)
            else:
                result = str(response)
            
            # Clean up the response if needed
            if result.startswith(prompt):
                result = result[len(prompt):]
            
            if "دستیار:" in result:
                result = result.split("دستیار:", 1)[1]
                
            return result.strip()
            
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
        if not self.api_key:
            return {
                "error": "سرویس هوش مصنوعی در دسترس نیست. لطفاً بعداً دوباره تلاش کنید."
            }
        
        try:
            # Convert time of day to Persian
            if time_of_day == "morning":
                time_persian = "صبح"
            elif time_of_day == "afternoon":
                time_persian = "بعد از ظهر"
            elif time_of_day == "evening":
                time_persian = "عصر/شب"
            else:
                time_persian = time_of_day
                
            # Convert energy level to Persian
            if energy_level == "low":
                energy_persian = "کم"
            elif energy_level == "medium":
                energy_persian = "متوسط"
            elif energy_level == "high":
                energy_persian = "زیاد"
            else:
                energy_persian = energy_level
            
            prompt = f"""من در زمان «{time_persian}» هستم، سطح انرژی من «{energy_persian}» است و {available_time} دقیقه وقت آزاد دارم.
لطفاً یک فعالیت مناسب با شرایط من پیشنهاد دهید و دلیل آن را توضیح دهید.

پاسخ را در قالب JSON به شکل زیر ارائه دهید:
{{
    "activity": "نام فعالیت",
    "reason": "دلیل پیشنهاد این فعالیت"
}}
"""
            
            # Add user context if available
            if user_data:
                user_context = self._format_user_data(user_data)
                prompt += f"\n\nاطلاعات بیشتر در مورد کاربر:\n{user_context}"
                
            # Call Hugging Face API
            response = self.query_model(
                self.default_model,
                prompt,
                parameters={"max_new_tokens": 400, "temperature": 0.7}
            )
            
            # Parse the response
            if isinstance(response, list) and len(response) > 0:
                result_text = response[0].get("generated_text", str(response[0]))
            elif isinstance(response, dict):
                if "error" in response:
                    return {"error": response["error"]}
                result_text = response.get("generated_text", str(response))
            else:
                result_text = str(response)
            
            # Extract the JSON from the response
            try:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    result = json.loads(json_str)
                    return {
                        "activity": result.get("activity", "پیاده‌روی"),
                        "reason": result.get("reason", "دلیل نامشخص")
                    }
                else:
                    # Fallback
                    return {
                        "activity": "پیاده‌روی",
                        "reason": "پیاده‌روی یک فعالیت سالم و مناسب برای اکثر زمان‌ها و سطوح انرژی است."
                    }
            except json.JSONDecodeError:
                # If JSON parsing fails, return a default response
                return {
                    "activity": "پیاده‌روی",
                    "reason": "پیاده‌روی یک فعالیت سالم و مناسب برای اکثر زمان‌ها و سطوح انرژی است."
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
        if not self.api_key:
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
            
            # Call Hugging Face API
            response = self.query_model(
                self.default_model,
                prompt,
                parameters={"max_new_tokens": 800, "temperature": 0.7}
            )
            
            # Parse the response
            if isinstance(response, list) and len(response) > 0:
                result_text = response[0].get("generated_text", str(response[0]))
            elif isinstance(response, dict):
                if "error" in response:
                    return {"error": response["error"]}
                result_text = response.get("generated_text", str(response))
            else:
                result_text = str(response)
            
            # Extract the JSON from the response
            try:
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    result = json.loads(json_str)
                    return {
                        "analysis": result.get("analysis", "تحلیل کلی برنامه"),
                        "issues": result.get("issues", []),
                        "suggestions": result.get("suggestions", [])
                    }
                else:
                    # Fallback
                    return {
                        "analysis": "تحلیل برنامه شما",
                        "issues": ["امکان تحلیل دقیق برنامه وجود ندارد"],
                        "suggestions": ["لطفاً اطلاعات بیشتری وارد کنید تا بتوانیم تحلیل دقیق‌تری ارائه دهیم"]
                    }
            except json.JSONDecodeError:
                # If JSON parsing fails, return a default response
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
        if not self.api_key:
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
            
            # Call Hugging Face API
            response = self.query_model(
                self.default_model,
                prompt,
                parameters={"max_new_tokens": 1000, "temperature": 0.7}
            )
            
            # Parse the response
            if isinstance(response, list) and len(response) > 0:
                result = response[0].get("generated_text", str(response[0]))
            elif isinstance(response, dict):
                if "error" in response:
                    return f"متأسفانه خطایی رخ داد: {response['error']}"
                result = response.get("generated_text", str(response))
            else:
                result = str(response)
            
            # Clean up the response
            if result.startswith(prompt):
                result = result[len(prompt):].strip()
                
            return result
                
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
                    
                    if hasattr(latest_metric, 'weight') and latest_metric.weight:
                        formatted_data += f"- وزن: {latest_metric.weight} کیلوگرم\n"
                    if hasattr(latest_metric, 'systolic') and hasattr(latest_metric, 'diastolic') and latest_metric.systolic and latest_metric.diastolic:
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
                    time_str = f" ساعت {event.start_time}" if hasattr(event, 'start_time') and event.start_time else ""
                    formatted_data += f"- {event.title}: {event.date}{time_str}\n"
            
            if 'tasks' in calendar and calendar['tasks']:
                tasks = calendar['tasks']
                formatted_data += "وظایف در انتظار:\n"
                
                for i, task in enumerate(tasks[:3]):  # Show 3 pending tasks
                    due_str = f" (موعد: {task.due_date})" if hasattr(task, 'due_date') and task.due_date else ""
                    formatted_data += f"- {task.title}{due_str}\n"
        
        return formatted_data