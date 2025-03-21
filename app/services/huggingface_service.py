"""
HuggingFace integration service for Persian Life Manager Application
"""

import os
import logging
import json
import requests
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class HuggingFaceService:
    """Service for HuggingFace API integration"""
    
    def __init__(self):
        """Initialize HuggingFace service"""
        self.api_key = os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("XAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.api_url = "https://api-inference.huggingface.co/models/"
        self.default_model = "meta-llama/Llama-2-70b-chat-hf"  # Default model, can be changed
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        
        if not self.api_key:
            logger.warning("HuggingFace API key not set. Service will not work properly.")
        else:
            logger.info("HuggingFace service initialized successfully.")
    
    def query_model(self, model: str, inputs: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Query a HuggingFace model
        
        Args:
            model (str): Model identifier on HuggingFace
            inputs (str): The input text
            parameters (Dict, optional): Parameters for the model
            
        Returns:
            Dict: The model response
        """
        if not self.api_key:
            logger.error("HuggingFace API key not set")
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
            logger.error(f"Error querying HuggingFace model: {str(e)}")
            return {"error": str(e)}
    
    def generate_text(self, prompt: str, model: Optional[str] = None) -> str:
        """Generate text using a language model
        
        Args:
            prompt (str): The prompt text
            model (str, optional): Model to use. Defaults to self.default_model.
            
        Returns:
            str: Generated text
        """
        model = model or self.default_model
        
        try:
            response = self.query_model(model, prompt)
            
            if isinstance(response, list) and len(response) > 0:
                # Handle different response formats
                if "generated_text" in response[0]:
                    return response[0]["generated_text"]
                else:
                    return str(response[0])
            elif isinstance(response, dict):
                if "error" in response:
                    logger.error(f"Error from HuggingFace API: {response['error']}")
                    return f"Error: {response['error']}"
                if "generated_text" in response:
                    return response["generated_text"]
                
            # Fallback
            return str(response)
            
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return f"Error generating text: {str(e)}"
    
    def get_health_advice(self, user_data: Dict[str, Any]) -> str:
        """Get personalized health advice using HuggingFace
        
        Args:
            user_data (dict): Dictionary containing user health data
                
        Returns:
            str: Personalized health advice in Persian
        """
        try:
            # Prepare the prompt in Persian
            prompt = f"""به عنوان یک متخصص سلامت و تناسب اندام، لطفاً توصیه‌های شخصی‌سازی شده برای کاربر با مشخصات زیر ارائه دهید:

قد: {user_data.get('height', 'نامشخص')} سانتی‌متر
وزن: {user_data.get('weight', 'نامشخص')} کیلوگرم
سطح فعالیت: {user_data.get('activity_level', 'نامشخص')}
شرایط سلامتی: {user_data.get('health_conditions', 'بدون مشکل خاص')}
هدف: {user_data.get('goal_focus', 'نامشخص')}

لطفاً توصیه‌های عملی در زمینه‌های تغذیه، ورزش و سبک زندگی ارائه دهید که مناسب شرایط این فرد باشد.
"""
            
            # Use a Persian-language model if available, or default
            model = "meta-llama/Meta-Llama-3-8B-Instruct"  # Better for multilingual support
            
            response = self.generate_text(prompt, model)
            return response
            
        except Exception as e:
            logger.error(f"Error getting health advice: {str(e)}")
            return f"متأسفانه در دریافت توصیه‌های سلامتی خطایی رخ داد: {str(e)}"
    
    def chat(self, user_message: str, user_data: Optional[Dict[str, Any]] = None, 
             chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Chat with the AI
        
        Args:
            user_message (str): User's message
            user_data (dict, optional): User data
            chat_history (list, optional): Chat history
            
        Returns:
            str: AI response in Persian
        """
        try:
            # Create a context from user data if available
            context = "توجه کنید که شما یک دستیار شخصی چت برای برنامه «پرشین لایف منیجر» هستید که به فارسی با کاربر صحبت می‌کنید و کمک می‌کنید."
            
            if user_data:
                context += "\n\nاطلاعات کاربر:\n"
                if 'name' in user_data:
                    context += f"• نام: {user_data['name']}\n"
                if 'health' in user_data and isinstance(user_data['health'], dict):
                    health = user_data['health']
                    context += f"• قد: {health.get('height', 'نامشخص')} سانتی‌متر\n"
                    context += f"• وزن: {health.get('weight', 'نامشخص')} کیلوگرم\n"
            
            # Format chat history if available
            history_text = ""
            if chat_history and isinstance(chat_history, list):
                for message in chat_history:
                    if 'role' in message and 'content' in message:
                        role = "کاربر" if message['role'] == "user" else "دستیار"
                        history_text += f"{role}: {message['content']}\n"
            
            # Create the full prompt
            prompt = f"{context}\n\n{history_text}\nکاربر: {user_message}\n\nدستیار:"
            
            # Use the best model available for this task
            model = "mistralai/Mistral-7B-Instruct-v0.2"  # Good multilingual performance
            
            response = self.generate_text(prompt, model)
            
            # Clean up the response if needed
            if response.startswith("دستیار:"):
                response = response[len("دستیار:"):].strip()
                
            return response
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return f"متأسفانه در پردازش درخواست شما خطایی رخ داد: {str(e)}"
    
    def suggest_activity(self, time_of_day: str, energy_level: str, 
                         available_time: int, user_data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Suggest an activity based on parameters
        
        Args:
            time_of_day (str): Time of day (morning, afternoon, evening)
            energy_level (str): Energy level (low, medium, high)
            available_time (int): Available time in minutes
            user_data (dict, optional): User data
            
        Returns:
            dict: Suggested activity with reason
        """
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
            
            # Use a model good at following JSON format instructions
            model = "mistralai/Mistral-7B-Instruct-v0.2"
            
            response = self.generate_text(prompt, model)
            
            try:
                # Try to extract JSON from response
                # Find JSON in response (might be wrapped in code blocks or other text)
                import re
                json_match = re.search(r'\{.*?\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    result = json.loads(json_str)
                    return result
                
                # If no JSON found or parsing failed, return a formatted response
                return {
                    "activity": "پیاده‌روی کوتاه",
                    "reason": "اطلاعات کافی برای پیشنهاد دقیق وجود ندارد. پیاده‌روی یک فعالیت مناسب برای اکثر شرایط است."
                }
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from response: {response}")
                return {
                    "activity": "استراحت و تمدد اعصاب",
                    "reason": "به دلیل خطا در پردازش، یک پیشنهاد عمومی ارائه می‌شود."
                }
            
        except Exception as e:
            logger.error(f"Error suggesting activity: {str(e)}")
            return {
                "activity": "مطالعه",
                "reason": f"خطا در دریافت پیشنهاد: {str(e)}"
            }