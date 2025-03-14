#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI service for Persian Life Manager Application
Provides AI-powered recommendations and insights
"""

import os
import logging
import numpy as np
from datetime import datetime, timedelta
import pickle
import json
from pathlib import Path

# Import TensorFlow Lite
try:
    import tflite_runtime.interpreter as tflite
    using_tflite_runtime = True
except ImportError:
    try:
        import tensorflow as tf
        using_tflite_runtime = False
    except ImportError:
        # If neither is available, we'll handle this gracefully
        tf = None
        using_tflite_runtime = False

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered recommendations and insights"""
    
    def __init__(self):
        """Initialize the AI service"""
        self.model_loaded = False
        self.interpreter = None
        self.model_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'resources', 'ai_model', 'model.tflite'
        )
        
        # Try to load the model
        try:
            self.load_model()
        except Exception as e:
            logger.warning(f"Failed to load AI model: {str(e)}")
    
    def load_model(self):
        """Load the TensorFlow Lite model"""
        model_dir = os.path.dirname(self.model_path)
        
        # Ensure model directory exists
        if not os.path.exists(model_dir):
            os.makedirs(model_dir, exist_ok=True)
        
        # Check if model file exists
        if not os.path.exists(self.model_path):
            # Create a simple model since we don't have one
            self._create_simple_model()
        
        try:
            # Load the model
            if using_tflite_runtime:
                self.interpreter = tflite.Interpreter(model_path=self.model_path)
            else:
                self.interpreter = tf.lite.Interpreter(model_path=self.model_path)
            
            self.interpreter.allocate_tensors()
            self.model_loaded = True
            logger.info("AI model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading AI model: {str(e)}")
            self.model_loaded = False
    
    def _create_simple_model(self):
        """Create a simple model for health recommendations
        
        This is a placeholder for when the actual model isn't available.
        It creates a very basic model that predicts health activity recommendations.
        """
        if tf is None:
            # Write a dummy model file as a placeholder
            with open(self.model_path, 'wb') as f:
                f.write(b'PLACEHOLDER_MODEL')
            return
        
        try:
            # Define a simple model
            model = tf.keras.Sequential([
                tf.keras.layers.Input(shape=(5,)),  # 5 features: height, weight, age, activity_level, goal
                tf.keras.layers.Dense(16, activation='relu'),
                tf.keras.layers.Dense(8, activation='relu'),
                tf.keras.layers.Dense(4)  # 4 outputs: recommended exercise minutes, calories, steps, sleep hours
            ])
            
            # Compile the model
            model.compile(optimizer='adam', loss='mse')
            
            # Create some dummy data and train briefly
            x = np.random.random((100, 5))
            y = np.random.random((100, 4))
            model.fit(x, y, epochs=1, verbose=0)
            
            # Convert to TFLite
            converter = tf.lite.TFLiteConverter.from_keras_model(model)
            tflite_model = converter.convert()
            
            # Save the model
            with open(self.model_path, 'wb') as f:
                f.write(tflite_model)
            
            logger.info("Created simple AI model as placeholder")
        except Exception as e:
            logger.error(f"Error creating simple model: {str(e)}")
            # Create empty file as placeholder
            with open(self.model_path, 'wb') as f:
                f.write(b'PLACEHOLDER_MODEL')
    
    def get_health_advice(self, height, weight, activity_level, health_conditions, goal_focus, metrics=None, exercises=None):
        """Get personalized health advice based on user data
        
        Args:
            height (float): User's height in cm
            weight (float): User's weight in kg
            activity_level (str): User's activity level
            health_conditions (str): User's health conditions
            goal_focus (str): User's health goal
            metrics (list, optional): List of user's health metrics
            exercises (list, optional): List of user's exercises
            
        Returns:
            str: Personalized health advice
        """
        try:
            # If we have the model loaded, use it for predictions
            if self.model_loaded and self.interpreter:
                # Prepare input data
                input_data = self._prepare_health_input_data(
                    height, weight, activity_level, health_conditions, goal_focus,
                    metrics, exercises
                )
                
                # Make prediction
                prediction = self._predict_health_recommendation(input_data)
                
                # Generate advice based on prediction
                advice = self._generate_health_advice_from_prediction(
                    prediction, height, weight, activity_level, 
                    health_conditions, goal_focus
                )
            else:
                # Fall back to rule-based recommendations
                advice = self._generate_rule_based_health_advice(
                    height, weight, activity_level, health_conditions, goal_focus,
                    metrics, exercises
                )
            
            return advice
        except Exception as e:
            logger.error(f"Error generating health advice: {str(e)}")
            return self._generate_fallback_health_advice(height, weight, goal_focus)
    
    def _prepare_health_input_data(self, height, weight, activity_level, health_conditions, goal_focus, metrics, exercises):
        """Prepare input data for the health recommendation model
        
        Args:
            height (float): User's height in cm
            weight (float): User's weight in kg
            activity_level (str): User's activity level
            health_conditions (str): User's health conditions
            goal_focus (str): User's health goal
            metrics (list): List of user's health metrics
            exercises (list): List of user's exercises
            
        Returns:
            numpy.ndarray: Input data for the model
        """
        # Map activity level to a numerical value
        activity_map = {
            "کم تحرک (بدون ورزش)": 1,
            "کمی فعال (1-3 روز در هفته)": 2,
            "نسبتاً فعال (3-5 روز در هفته)": 3,
            "بسیار فعال (6-7 روز در هفته)": 4,
            "فوق العاده فعال (ورزش روزانه شدید)": 5
        }
        
        # Map goal focus to a numerical value
        goal_map = {
            "کاهش وزن": 1,
            "افزایش وزن": 2,
            "حفظ وزن فعلی": 3,
            "افزایش استقامت": 4,
            "افزایش قدرت عضلانی": 5,
            "بهبود سلامت قلب": 6,
            "کاهش استرس": 7
        }
        
        # Calculate BMI
        bmi = weight / ((height / 100) ** 2)
        
        # Get activity level as number
        activity_score = activity_map.get(activity_level, 2)
        
        # Get goal as number
        goal_score = goal_map.get(goal_focus, 3)
        
        # Check for health conditions (binary flags)
        has_heart_condition = 1 if "قلب" in health_conditions else 0
        has_diabetes = 1 if "دیابت" in health_conditions else 0
        has_high_bp = 1 if "فشار خون" in health_conditions else 0
        
        # Create input data array
        input_data = np.array([[
            bmi, activity_score, goal_score, 
            has_heart_condition, has_diabetes, has_high_bp
        ]], dtype=np.float32)
        
        return input_data
    
    def _predict_health_recommendation(self, input_data):
        """Make a prediction using the health recommendation model
        
        Args:
            input_data (numpy.ndarray): Input data for the model
            
        Returns:
            numpy.ndarray: Model prediction
        """
        try:
            # Get input and output details
            input_details = self.interpreter.get_input_details()
            output_details = self.interpreter.get_output_details()
            
            # Set the input tensor
            self.interpreter.set_tensor(input_details[0]['index'], input_data)
            
            # Run inference
            self.interpreter.invoke()
            
            # Get output tensor
            output_data = self.interpreter.get_tensor(output_details[0]['index'])
            
            return output_data
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            # Return dummy prediction as fallback
            return np.array([[30, 1500, 8000, 7.5]], dtype=np.float32)
    
    def _generate_health_advice_from_prediction(self, prediction, height, weight, activity_level, health_conditions, goal_focus):
        """Generate health advice based on model prediction
        
        Args:
            prediction (numpy.ndarray): Model prediction
            height (float): User's height in cm
            weight (float): User's weight in kg
            activity_level (str): User's activity level
            health_conditions (str): User's health conditions
            goal_focus (str): User's health goal
            
        Returns:
            str: Personalized health advice
        """
        try:
            # Unpack prediction
            # [exercise_minutes, daily_calories, daily_steps, sleep_hours]
            exercise_minutes = max(10, min(120, int(prediction[0][0])))
            daily_calories = max(1000, min(3000, int(prediction[0][1])))
            daily_steps = max(3000, min(15000, int(prediction[0][2])))
            sleep_hours = max(6, min(9, float(prediction[0][3])))
            
            # Calculate BMI
            bmi = weight / ((height / 100) ** 2)
            bmi_status = self._get_bmi_status(bmi)
            
            # Generate advice text
            advice = f"""<div dir="rtl" style="line-height: 1.6;">
            <h3>توصیه‌های سلامتی شخصی‌سازی شده</h3>
            
            <p>با توجه به اطلاعات شما (قد: {height} سانتی‌متر، وزن: {weight} کیلوگرم، BMI: {bmi:.1f} - {bmi_status})
            و با در نظر گرفتن هدف شما ({goal_focus}) و سطح فعالیت ({activity_level})، توصیه‌های زیر ارائه می‌شود:</p>
            
            <h4>برنامه ورزشی پیشنهادی:</h4>
            <ul>
                <li>میزان فعالیت روزانه: حداقل {exercise_minutes} دقیقه در روز</li>
                <li>تعداد قدم‌های روزانه: حدود {daily_steps:,} قدم</li>
            """
            
            # Add exercise recommendations based on goal
            if goal_focus == "کاهش وزن":
                advice += f"""
                <li>ترکیبی از تمرینات هوازی (مانند پیاده‌روی سریع، دوچرخه‌سواری) به مدت ۳۰ دقیقه، ۵ روز در هفته</li>
                <li>تمرینات قدرتی ۲-۳ روز در هفته (تمرینات با وزن بدن مانند اسکوات و پلانک)</li>
                """
            elif goal_focus == "افزایش قدرت عضلانی":
                advice += f"""
                <li>تمرینات قدرتی ۳-۴ روز در هفته، با تمرکز بر گروه‌های مختلف عضلانی در هر جلسه</li>
                <li>تمرینات هوازی سبک ۲ روز در هفته برای بهبود گردش خون و ریکاوری</li>
                """
            elif goal_focus == "بهبود سلامت قلب":
                advice += f"""
                <li>فعالیت هوازی متوسط تا شدید ۱۵۰ دقیقه در هفته (مانند پیاده‌روی سریع، شنا یا دوچرخه‌سواری)</li>
                <li>تمرینات تناوبی با شدت بالا (HIIT) ۱-۲ روز در هفته (در صورت نداشتن مشکلات قلبی)</li>
                """
            elif goal_focus == "کاهش استرس":
                advice += f"""
                <li>یوگا یا تمرینات کششی ۳-۴ روز در هفته، ۲۰-۳۰ دقیقه در هر جلسه</li>
                <li>پیاده‌روی آرام در طبیعت، ۳۰-۴۵ دقیقه، ۴-۵ روز در هفته</li>
                <li>تمرینات تنفسی عمیق، ۵-۱۰ دقیقه، روزانه</li>
                """
            
            advice += """
            </ul>
            
            <h4>توصیه‌های تغذیه‌ای:</h4>
            <ul>
            """
            
            # Add nutrition recommendations based on goal and BMI
            if bmi > 25 and goal_focus == "کاهش وزن":
                advice += f"""
                <li>مصرف روزانه حدود {daily_calories:,} کالری (کسری ۵۰۰-۷۵۰ کالری نسبت به نیاز پایه)</li>
                <li>افزایش مصرف پروتئین (۲۵-۳۰٪ کالری روزانه) برای حفظ توده عضلانی</li>
                <li>کاهش مصرف کربوهیدرات‌های تصفیه‌شده و قندهای ساده</li>
                <li>افزایش مصرف سبزیجات و میوه‌ها (حداقل ۵ وعده در روز)</li>
                """
            elif bmi < 18.5 and goal_focus == "افزایش وزن":
                advice += f"""
                <li>مصرف روزانه حدود {daily_calories:,} کالری (مازاد ۳۰۰-۵۰۰ کالری نسبت به نیاز پایه)</li>
                <li>افزایش مصرف پروتئین (۱.۶-۲ گرم به ازای هر کیلوگرم وزن بدن)</li>
                <li>مصرف کربوهیدرات‌های پیچیده و چربی‌های سالم</li>
                <li>وعده‌های غذایی کوچک اما متعدد (۵-۶ وعده در روز)</li>
                """
            elif goal_focus == "بهبود سلامت قلب":
                advice += f"""
                <li>مصرف روزانه حدود {daily_calories:,} کالری</li>
                <li>محدود کردن نمک مصرفی (کمتر از ۲۳۰۰ میلی‌گرم در روز)</li>
                <li>افزایش مصرف امگا-۳ (ماهی‌های چرب، گردو، تخم کتان)</li>
                <li>مصرف غلات کامل، حبوبات و روغن زیتون</li>
                <li>محدود کردن چربی‌های اشباع و ترانس</li>
                """
            else:
                advice += f"""
                <li>مصرف روزانه حدود {daily_calories:,} کالری</li>
                <li>توازن در مصرف ماکرونوترینت‌ها (۵۰-۵۵٪ کربوهیدرات، ۲۰-۲۵٪ پروتئین، ۲۵-۳۰٪ چربی)</li>
                <li>حداقل ۵ وعده میوه و سبزیجات در روز</li>
                <li>نوشیدن کافی آب (۸-۱۰ لیوان در روز)</li>
                """
            
            # Add special considerations for health conditions
            if health_conditions:
                advice += """
                </ul>
                
                <h4>توصیه‌های ویژه با توجه به شرایط سلامتی:</h4>
                <ul>
                """
                
                if "دیابت" in health_conditions:
                    advice += """
                    <li>کنترل منظم قند خون</li>
                    <li>محدود کردن قندهای ساده و کربوهیدرات‌های تصفیه‌شده</li>
                    <li>وعده‌های غذایی کوچک و منظم</li>
                    """
                
                if "فشار خون" in health_conditions:
                    advice += """
                    <li>کاهش مصرف نمک (کمتر از ۱۵۰۰ میلی‌گرم در روز)</li>
                    <li>مصرف منظم پتاسیم، منیزیم و کلسیم</li>
                    <li>اجتناب از فعالیت‌های شدید ناگهانی</li>
                    """
                
                if "قلب" in health_conditions:
                    advice += """
                    <li>تمرینات ورزشی با شدت کم تا متوسط و مدت طولانی‌تر</li>
                    <li>محدود کردن چربی‌های اشباع و ترانس</li>
                    <li>مشورت با پزشک قبل از شروع برنامه ورزشی جدید</li>
                    """
                
                if "کلسترول" in health_conditions:
                    advice += """
                    <li>افزایش مصرف فیبر محلول (جو دوسر، حبوبات، میوه‌ها)</li>
                    <li>محدود کردن چربی‌های حیوانی</li>
                    <li>مصرف بیشتر ماهی‌های چرب، آجیل و روغن زیتون</li>
                    """
            
            advice += f"""
            </ul>
            
            <h4>توصیه‌های خواب و استراحت:</h4>
            <ul>
                <li>خواب منظم و کافی: {sleep_hours:.1f}-{sleep_hours+0.5:.1f} ساعت در شب</li>
                <li>خوابیدن و بیدار شدن در ساعات منظم</li>
                <li>اجتناب از صفحه‌های نمایش ۱ ساعت قبل از خواب</li>
                <li>محیط خواب آرام، خنک و تاریک</li>
            </ul>
            
            <p><b>توجه:</b> این توصیه‌ها عمومی هستند و برای دریافت برنامه دقیق‌تر و تخصصی‌تر، با متخصصان سلامت مشورت کنید.</p>
            </div>
            """
            
            return advice
        except Exception as e:
            logger.error(f"Error generating advice from prediction: {str(e)}")
            return self._generate_fallback_health_advice(height, weight, goal_focus)
    
    def _generate_rule_based_health_advice(self, height, weight, activity_level, health_conditions, goal_focus, metrics, exercises):
        """Generate health advice based on rules when model is not available
        
        Args:
            height (float): User's height in cm
            weight (float): User's weight in kg
            activity_level (str): User's activity level
            health_conditions (str): User's health conditions
            goal_focus (str): User's health goal
            metrics (list): List of user's health metrics
            exercises (list): List of user's exercises
            
        Returns:
            str: Personalized health advice
        """
        # Calculate BMI
        bmi = weight / ((height / 100) ** 2)
        bmi_status = self._get_bmi_status(bmi)
        
        # Determine exercise frequency based on activity level
        exercise_frequency = 3  # Default value
        if activity_level == "کم تحرک (بدون ورزش)":
            exercise_frequency = 2
        elif activity_level == "کمی فعال (1-3 روز در هفته)":
            exercise_frequency = 3
        elif activity_level == "نسبتاً فعال (3-5 روز در هفته)":
            exercise_frequency = 4
        elif activity_level == "بسیار فعال (6-7 روز در هفته)":
            exercise_frequency = 5
        elif activity_level == "فوق العاده فعال (ورزش روزانه شدید)":
            exercise_frequency = 6
        
        # Determine recommended daily steps
        if goal_focus == "کاهش وزن":
            daily_steps = 10000
        elif goal_focus == "افزایش استقامت":
            daily_steps = 12000
        elif goal_focus == "بهبود سلامت قلب":
            daily_steps = 8000
        else:
            daily_steps = 7000
        
        # Adjust based on health conditions
        if "قلب" in health_conditions:
            daily_steps = min(daily_steps, 8000)
            exercise_frequency = min(exercise_frequency, 4)
        
        # Calculate base calorie needs using Harris-Benedict formula
        if bmi < 18.5:
            calorie_adjustment = 500  # Surplus for underweight
        elif bmi >= 25:
            calorie_adjustment = -500  # Deficit for overweight
        else:
            calorie_adjustment = 0  # Maintenance for normal weight
        
        # Generate advice
        advice = f"""<div dir="rtl" style="line-height: 1.6;">
        <h3>توصیه‌های سلامتی شخصی‌سازی شده</h3>
        
        <p>با توجه به اطلاعات شما (قد: {height} سانتی‌متر، وزن: {weight} کیلوگرم، BMI: {bmi:.1f} - {bmi_status})
        و با در نظر گرفتن هدف شما ({goal_focus}) و سطح فعالیت ({activity_level})، توصیه‌های زیر ارائه می‌شود:</p>
        
        <h4>برنامه ورزشی پیشنهادی:</h4>
        <ul>
            <li>تعداد روزهای ورزش در هفته: {exercise_frequency} روز</li>
            <li>مدت هر جلسه ورزش: ۳۰-۴۵ دقیقه</li>
            <li>تعداد قدم‌های روزانه: حدود {daily_steps:,} قدم</li>
        """
        
        # Add exercise recommendations based on goal
        if goal_focus == "کاهش وزن":
            advice += """
            <li>ترکیبی از تمرینات هوازی (۶۰٪) و قدرتی (۴۰٪)</li>
            <li>تمرینات هوازی: پیاده‌روی سریع، دویدن آرام، شنا یا دوچرخه‌سواری</li>
            <li>تمرینات قدرتی ساده با وزن بدن یا وزنه‌های سبک</li>
            """
        elif goal_focus == "افزایش وزن":
            advice += """
            <li>تمرکز بر تمرینات قدرتی (۷۰٪) و هوازی سبک (۳۰٪)</li>
            <li>جلسات کوتاه‌تر اما با شدت بیشتر</li>
            <li>استراحت کافی بین ست‌ها و جلسات تمرینی</li>
            """
        elif goal_focus == "افزایش استقامت":
            advice += """
            <li>تمرینات هوازی با مدت طولانی‌تر و شدت متوسط</li>
            <li>افزایش تدریجی مدت تمرین هر هفته</li>
            <li>تمرینات تناوبی یک روز در میان</li>
            """
        elif goal_focus == "افزایش قدرت عضلانی":
            advice += """
            <li>تمرینات قدرتی با وزنه‌های متوسط تا سنگین</li>
            <li>تمرکز بر گروه‌های عضلانی بزرگ</li>
            <li>۳-۴ ست با ۸-۱۲ تکرار برای هر حرکت</li>
            """
        elif goal_focus == "بهبود سلامت قلب":
            advice += """
            <li>تمرینات هوازی منظم با شدت متوسط</li>
            <li>پیاده‌روی روزانه به مدت حداقل ۳۰ دقیقه</li>
            <li>تمرینات تنفسی و کششی برای کاهش استرس</li>
            """
        elif goal_focus == "کاهش استرس":
            advice += """
            <li>یوگا و مدیتیشن، ۲۰-۳۰ دقیقه روزانه</li>
            <li>پیاده‌روی آرام در فضای باز</li>
            <li>تمرینات تنفس عمیق، ۵-۱۰ دقیقه، چند بار در روز</li>
            """
        
        advice += """
        </ul>
        
        <h4>توصیه‌های تغذیه‌ای:</h4>
        <ul>
        """
        
        # Add nutrition recommendations based on BMI and goal
        if bmi > 25:
            advice += f"""
            <li>ایجاد کسری کالری حدود {abs(calorie_adjustment)} کالری در روز</li>
            <li>کاهش مصرف کربوهیدرات‌های تصفیه‌شده و قندهای ساده</li>
            <li>افزایش مصرف پروتئین برای حفظ توده عضلانی</li>
            <li>افزایش مصرف فیبر (سبزیجات، میوه‌ها و غلات کامل)</li>
            <li>نوشیدن آب کافی (۸-۱۰ لیوان در روز)</li>
            """
        elif bmi < 18.5:
            advice += f"""
            <li>افزایش کالری دریافتی روزانه حدود {abs(calorie_adjustment)} کالری</li>
            <li>مصرف وعده‌های غذایی کوچک اما متعدد (۵-۶ وعده در روز)</li>
            <li>افزایش مصرف پروتئین و کربوهیدرات‌های پیچیده</li>
            <li>استفاده از میان‌وعده‌های مغذی و پرکالری (آجیل، میوه‌های خشک)</li>
            """
        else:
            advice += """
            <li>حفظ تعادل در مصرف ماکرونوترینت‌ها</li>
            <li>مصرف پروتئین کافی (۰.۸-۱.۲ گرم به ازای هر کیلوگرم وزن بدن)</li>
            <li>توجه به کیفیت غذا بیش از کمیت آن</li>
            <li>محدود کردن غذاهای فرآوری شده و فست‌فود</li>
            """
        
        # Add health condition specific advice
        if health_conditions:
            advice += """
            </ul>
            
            <h4>توصیه‌های ویژه با توجه به شرایط سلامتی:</h4>
            <ul>
            """
            
            if "دیابت" in health_conditions:
                advice += """
                <li>کنترل منظم قند خون</li>
                <li>مصرف کربوهیدرات‌های با شاخص گلیسمی پایین</li>
                <li>وعده‌های غذایی کوچک و منظم</li>
                <li>ورزش منظم برای کنترل قند خون</li>
                """
            
            if "فشار خون" in health_conditions:
                advice += """
                <li>کاهش مصرف نمک به کمتر از ۲ گرم در روز</li>
                <li>مصرف بیشتر پتاسیم، منیزیم و کلسیم</li>
                <li>تمرینات هوازی منظم با شدت متوسط</li>
                <li>کنترل منظم فشار خون</li>
                """
            
            if "قلب" in health_conditions:
                advice += """
                <li>محدود کردن چربی‌های اشباع و ترانس</li>
                <li>مصرف بیشتر امگا-۳ (ماهی‌های چرب، گردو)</li>
                <li>شروع آرام فعالیت ورزشی و افزایش تدریجی</li>
                <li>مشورت با پزشک قبل از شروع برنامه ورزشی جدید</li>
                """
        
        advice += """
        </ul>
        
        <h4>توصیه‌های خواب و استراحت:</h4>
        <ul>
            <li>خواب منظم و کافی (۷-۸ ساعت در شب)</li>
            <li>خوابیدن و بیدار شدن در ساعات منظم</li>
            <li>اجتناب از کافئین در ۶ ساعت قبل از خواب</li>
            <li>اجتناب از صفحه‌های نمایش ۱ ساعت قبل از خواب</li>
            <li>محیط خواب آرام، خنک و تاریک</li>
        </ul>
        
        <p><b>توجه:</b> این توصیه‌ها عمومی هستند و برای دریافت برنامه دقیق‌تر و تخصصی‌تر، با متخصصان سلامت مشورت کنید.</p>
        </div>
        """
        
        return advice
    
    def _generate_fallback_health_advice(self, height, weight, goal_focus):
        """Generate basic health advice when other methods fail
        
        Args:
            height (float): User's height in cm
            weight (float): User's weight in kg
            goal_focus (str): User's health goal
            
        Returns:
            str: Basic health advice
        """
        # Calculate BMI
        bmi = weight / ((height / 100) ** 2)
        bmi_status = self._get_bmi_status(bmi)
        
        # Generate simple advice
        advice = f"""<div dir="rtl" style="line-height: 1.6;">
        <h3>توصیه‌های پایه سلامتی</h3>
        
        <p>با توجه به اطلاعات شما (قد: {height} سانتی‌متر، وزن: {weight} کیلوگرم، BMI: {bmi:.1f} - {bmi_status})
        و با در نظر گرفتن هدف شما ({goal_focus})، توصیه‌های عمومی زیر ارائه می‌شود:</p>
        
        <h4>توصیه‌های عمومی سلامتی:</h4>
        <ul>
            <li>حداقل ۱۵۰ دقیقه فعالیت فیزیکی متوسط در هفته (مثلاً ۳۰ دقیقه، ۵ روز در هفته)</li>
            <li>مصرف حداقل ۵ وعده میوه و سبزیجات در روز</li>
            <li>محدود کردن غذاهای فرآوری شده، شکر و نمک اضافه</li>
            <li>نوشیدن ۸-۱۰ لیوان آب در روز</li>
            <li>خواب منظم و کافی (۷-۸ ساعت در شب)</li>
            <li>تکنیک‌های مدیریت استرس مانند تنفس عمیق یا مدیتیشن</li>
        </ul>
        
        <p><b>توجه:</b> این توصیه‌ها عمومی هستند و برای دریافت برنامه دقیق‌تر و تخصصی‌تر، با متخصصان سلامت مشورت کنید.</p>
        </div>
        """
        
        return advice
    
    def _get_bmi_status(self, bmi):
        """Get BMI status description
        
        Args:
            bmi (float): BMI value
            
        Returns:
            str: BMI status description in Persian
        """
        if bmi < 18.5:
            return "کمبود وزن"
        elif bmi < 25:
            return "وزن سالم"
        elif bmi < 30:
            return "اضافه وزن"
        elif bmi < 35:
            return "چاقی درجه ۱"
        elif bmi < 40:
            return "چاقی درجه ۲"
        else:
            return "چاقی درجه ۳"
    
    def get_financial_advice(self, income, expenses, savings, financial_goals):
        """Get personalized financial advice based on user data
        
        Args:
            income (float): Monthly income
            expenses (float): Monthly expenses
            savings (float): Current savings
            financial_goals (dict): Dictionary of financial goals
            
        Returns:
            str: Personalized financial advice
        """
        try:
            # Calculate basic financial metrics
            monthly_balance = income - expenses
            savings_ratio = (income - expenses) / income if income > 0 else 0
            expenses_to_income = expenses / income if income > 0 else 0
            
            # Generate advice
            advice = f"""<div dir="rtl" style="line-height: 1.6;">
            <h3>توصیه‌های مالی شخصی‌سازی شده</h3>
            
            <p>با توجه به اطلاعات مالی شما:</p>
            
            <h4>تحلیل وضعیت فعلی:</h4>
            <ul>
                <li>نسبت هزینه به درآمد: {expenses_to_income:.1%}</li>
                <li>نسبت پس‌انداز: {savings_ratio:.1%}</li>
                <li>مانده ماهانه: {monthly_balance:,} تومان</li>
            </ul>
            """
            
            # Budget recommendations
            advice += """
            <h4>توصیه‌های بودجه‌بندی:</h4>
            <ul>
            """
            
            if expenses_to_income > 0.7:
                advice += """
                <li>هزینه‌های شما نسبت به درآمد بالاست. بررسی دقیق طبقه‌بندی هزینه‌ها و شناسایی موارد قابل کاهش توصیه می‌شود.</li>
                <li>اولویت‌بندی هزینه‌ها به ضروری (مسکن، خوراک، حمل‌ونقل) و غیرضروری</li>
                <li>هدف: کاهش نسبت هزینه به درآمد به زیر ۷۰٪</li>
                """
            else:
                advice += """
                <li>نسبت هزینه به درآمد شما در محدوده مناسبی است. ادامه مدیریت خوب هزینه‌ها را توصیه می‌کنیم.</li>
                <li>بررسی دوره‌ای هزینه‌ها برای جلوگیری از افزایش تدریجی</li>
                """
            
            if savings_ratio < 0.1 and monthly_balance > 0:
                advice += """
                <li>پس‌انداز شما کمتر از ۱۰٪ درآمد است. توصیه می‌شود حداقل ۱۰-۲۰٪ درآمد را به پس‌انداز اختصاص دهید.</li>
                <li>استفاده از روش پس‌انداز خودکار: انتقال اتوماتیک بخشی از درآمد به حساب پس‌انداز در ابتدای ماه</li>
                """
            elif monthly_balance <= 0:
                advice += """
                <li>مانده ماهانه شما منفی یا صفر است. کاهش هزینه‌ها یا افزایش درآمد ضروری است.</li>
                <li>شناسایی و حذف هزینه‌های غیرضروری</li>
                <li>بررسی امکان‌های افزایش درآمد</li>
                """
            else:
                advice += """
                <li>نسبت پس‌انداز شما مناسب است. ادامه این روند به ساخت ثروت و امنیت مالی کمک می‌کند.</li>
                <li>بررسی گزینه‌های سرمایه‌گذاری برای بخشی از پس‌انداز</li>
                """
            
            advice += """
            </ul>
            
            <h4>استراتژی‌های پیشنهادی:</h4>
            <ul>
                <li>ایجاد صندوق اضطراری معادل ۳-۶ ماه هزینه‌ها</li>
                <li>تنظیم بودجه ماهانه و پایبندی به آن</li>
                <li>حذف یا کاهش بدهی‌های پرهزینه (مانند بدهی کارت اعتباری)</li>
                <li>بررسی و بهینه‌سازی هزینه‌های ثابت (بیمه، اشتراک‌ها، قبوض)</li>
                <li>استفاده از روش‌های کاهش هزینه در خرید روزانه (خرید اقلام فصلی، تخفیف‌ها)</li>
            </ul>
            
            <p><b>توجه:</b> این توصیه‌ها بر اساس اطلاعات کلی ارائه شده‌اند. برای مشاوره دقیق‌تر، با متخصصان مالی مشورت کنید.</p>
            </div>
            """
            
            return advice
        except Exception as e:
            logger.error(f"Error generating financial advice: {str(e)}")
            return """<div dir="rtl">
            <h3>توصیه‌های عمومی مالی</h3>
            <ul>
                <li>تنظیم بودجه ماهانه و پایبندی به آن</li>
                <li>ایجاد صندوق اضطراری معادل ۳-۶ ماه هزینه‌ها</li>
                <li>پس‌انداز حداقل ۱۰-۲۰٪ از درآمد ماهانه</li>
                <li>اولویت‌بندی و کاهش بدهی‌ها</li>
                <li>سرمایه‌گذاری هوشمندانه برای آینده</li>
            </ul>
            </div>"""
    
    def get_time_management_advice(self, tasks, schedule, productivity_preferences):
        """Get personalized time management advice
        
        Args:
            tasks (list): List of tasks to complete
            schedule (dict): Current schedule and commitments
            productivity_preferences (dict): User's productivity preferences
            
        Returns:
            str: Personalized time management advice
        """
        try:
            # Generate advice
            advice = """<div dir="rtl" style="line-height: 1.6;">
            <h3>توصیه‌های مدیریت زمان</h3>
            
            <h4>اصول کلیدی مدیریت زمان:</h4>
            <ul>
                <li><b>اولویت‌بندی:</b> از ماتریس فوری-مهم استفاده کنید. وظایف مهم و فوری را اول انجام دهید.</li>
                <li><b>تکنیک پومودورو:</b> کار در بازه‌های ۲۵ دقیقه‌ای با استراحت‌های ۵ دقیقه‌ای</li>
                <li><b>قانون ۲ دقیقه:</b> اگر انجام کاری کمتر از ۲ دقیقه طول می‌کشد، همان موقع انجامش دهید</li>
                <li><b>دسته‌بندی مشابه:</b> وظایف مشابه را در یک بازه زمانی انجام دهید تا از تغییر مداوم تمرکز جلوگیری شود</li>
                <li><b>برنامه‌ریزی شب قبل:</b> هر شب ۱۰ دقیقه برای برنامه‌ریزی روز بعد اختصاص دهید</li>
            </ul>
            
            <h4>توصیه‌های عملی:</h4>
            <ul>
                <li>زمان‌های اوج انرژی خود را شناسایی کرده و وظایف مهم‌تر را در آن زمان‌ها انجام دهید</li>
                <li>از تقویم برای تعیین زمان‌های مشخص برای وظایف مهم استفاده کنید، نه فقط برای جلسات</li>
                <li>حداقل ۳۰ دقیقه هر روز را به برنامه‌ریزی و مرور وظایف اختصاص دهید</li>
                <li>حواس‌پرتی‌ها را شناسایی و مدیریت کنید (اعلان‌های موبایل، شبکه‌های اجتماعی)</li>
                <li>برای هر وظیفه، زمان تخمینی را ۲۵٪ افزایش دهید تا استرس کمتری داشته باشید</li>
                <li>برای استراحت‌های کوتاه بین وظایف برنامه‌ریزی کنید</li>
                <li>مهارت "نه" گفتن را تقویت کنید تا از افزایش بیش از حد تعهدات جلوگیری شود</li>
            </ul>
            
            <h4>ابزارهای پیشنهادی:</h4>
            <ul>
                <li>استفاده از تقویم دیجیتال همراه با یادآوری‌ها</li>
                <li>استفاده از ابزارهای مدیریت وظایف (مانند تودویست، ترلو)</li>
                <li>یادداشت‌برداری منظم ایده‌ها و وظایف جدید</li>
                <li>استفاده از تایمرهای پومودورو برای تمرکز بهتر</li>
            </ul>
            
            <p><b>به یاد داشته باشید:</b> هدف مدیریت زمان، افزایش بهره‌وری همراه با کاهش استرس است، نه فقط انجام کارهای بیشتر در زمان کمتر.</p>
            </div>
            """
            
            return advice
        except Exception as e:
            logger.error(f"Error generating time management advice: {str(e)}")
            return """<div dir="rtl">
            <h3>توصیه‌های عمومی مدیریت زمان</h3>
            <ul>
                <li>اولویت‌بندی وظایف با استفاده از ماتریس فوری-مهم</li>
                <li>استفاده از تکنیک پومودورو (۲۵ دقیقه کار، ۵ دقیقه استراحت)</li>
                <li>برنامه‌ریزی روزانه و هفتگی</li>
                <li>مدیریت حواس‌پرتی‌ها</li>
                <li>تعیین اهداف واضح و قابل اندازه‌گیری</li>
            </ul>
            </div>"""
