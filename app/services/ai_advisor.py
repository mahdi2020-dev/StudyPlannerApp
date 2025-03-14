"""
AI Advisor service for Persian Life Manager Application
Integrates local AI models with OpenAI for comprehensive life management advice
"""

import os
import logging
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)

class AIAdvisor:
    """Service for AI-powered recommendations across all life domains"""
    
    def __init__(self):
        """Initialize the AI advisor service"""
        self.openai_service = OpenAIService()
        
    def get_comprehensive_advice(self, user_data):
        """Get comprehensive life advice covering all domains
        
        Args:
            user_data (dict): User data including health, finance, and calendar info
            
        Returns:
            dict: Dictionary with advice for all domains
        """
        try:
            # Gather advice for each domain
            health_advice = self.get_health_advice(user_data.get('health', {}))
            finance_advice = self.get_finance_advice(user_data.get('finance', {}))
            time_advice = self.get_time_management_advice(user_data.get('calendar', {}))
            
            # Combine all advice into a comprehensive response
            return {
                'health': health_advice,
                'finance': finance_advice,
                'time_management': time_advice
            }
        except Exception as e:
            logger.error(f"Error getting comprehensive advice: {str(e)}")
            return {
                'health': self._get_fallback_health_advice(),
                'finance': self._get_fallback_finance_advice(),
                'time_management': self._get_fallback_time_advice()
            }
    
    def get_health_advice(self, health_data):
        """Get personalized health advice
        
        Args:
            health_data (dict): User health data
            
        Returns:
            str: HTML-formatted health advice
        """
        try:
            return self.openai_service.get_health_advice(health_data)
        except Exception as e:
            logger.error(f"Error getting health advice: {str(e)}")
            return self._get_fallback_health_advice()
    
    def get_finance_advice(self, finance_data):
        """Get personalized financial advice
        
        Args:
            finance_data (dict): User financial data
            
        Returns:
            str: HTML-formatted financial advice
        """
        try:
            return self.openai_service.get_financial_advice(finance_data)
        except Exception as e:
            logger.error(f"Error getting financial advice: {str(e)}")
            return self._get_fallback_finance_advice()
    
    def get_time_management_advice(self, calendar_data):
        """Get personalized time management advice
        
        Args:
            calendar_data (dict): User calendar data
            
        Returns:
            str: HTML-formatted time management advice
        """
        try:
            return self.openai_service.get_time_management_advice(calendar_data)
        except Exception as e:
            logger.error(f"Error getting time management advice: {str(e)}")
            return self._get_fallback_time_advice()
    
    def generate_weekly_plan(self, user_data):
        """Generate a personalized weekly plan for the user
        
        Args:
            user_data (dict): User data including health, finance, and calendar info
            
        Returns:
            str: HTML-formatted weekly plan
        """
        try:
            # Prepare the prompt for weekly plan in Persian
            prompt = f"""به عنوان یک برنامه‌ریز هوشمند، برنامه هفتگی شخصی‌سازی شده برای هفته آینده کاربر تهیه کنید.

اطلاعات کاربر:
- برنامه‌های تقویم: {self._format_calendar_events(user_data.get('calendar', {}).get('events', []))}
- وظایف: {self._format_tasks(user_data.get('calendar', {}).get('tasks', []))}
- اهداف سلامتی: {self._format_health_goals(user_data.get('health', {}).get('goals', []))}
- برنامه مالی: {self._format_finance_goals(user_data.get('finance', {}).get('goals', []))}

لطفاً یک برنامه هفتگی روز به روز (شنبه تا جمعه) با فرمت HTML با بخش‌های زیر ارائه دهید:
1. برنامه‌های ثابت روزانه
2. وظایف برای هر روز
3. فعالیت‌های ورزشی پیشنهادی
4. یادآوری‌های مالی
5. نکات موفقیت روزانه

پاسخ باید به زبان فارسی و با تگ‌های HTML مناسب برای نمایش در وب باشد."""
            
            # Get weekly plan from OpenAI
            response = self.openai_service.client.chat.completions.create(
                model=self.openai_service.model,
                messages=[
                    {"role": "system", "content": "شما یک برنامه‌ریز هوشمند هستید که برنامه هفتگی شخصی‌سازی شده به زبان فارسی ارائه می‌دهد."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating weekly plan: {str(e)}")
            return self._get_fallback_weekly_plan()
    
    def generate_yearly_goals(self, user_data):
        """Generate suggested yearly goals based on user history
        
        Args:
            user_data (dict): User data including history and preferences
            
        Returns:
            str: HTML-formatted yearly goals suggestion
        """
        try:
            # Prepare the prompt for yearly goals in Persian
            prompt = f"""به عنوان یک مشاور زندگی، لطفاً پیشنهادهایی برای اهداف سالانه کاربر با توجه به داده‌های موجود ارائه دهید.

داده‌های کاربر:
- سلامت: {self._format_health_data(user_data.get('health', {}))}
- مالی: {self._format_finance_data(user_data.get('finance', {}))}
- زمان و برنامه‌ریزی: {self._format_calendar_data(user_data.get('calendar', {}))}

لطفاً اهداف سالانه پیشنهادی را در قالب HTML و در بخش‌های زیر ارائه دهید:
1. اهداف سلامتی (۳-۵ هدف)
2. اهداف مالی (۳-۵ هدف)
3. اهداف شخصی و حرفه‌ای (۳-۵ هدف)
4. برنامه کلی برای دستیابی به این اهداف

پاسخ باید به زبان فارسی و با تگ‌های HTML مناسب برای نمایش در وب باشد."""
            
            # Get yearly goals from OpenAI
            response = self.openai_service.client.chat.completions.create(
                model=self.openai_service.model,
                messages=[
                    {"role": "system", "content": "شما یک مشاور زندگی هستید که اهداف سالانه پیشنهادی به زبان فارسی ارائه می‌دهد."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating yearly goals: {str(e)}")
            return self._get_fallback_yearly_goals()
    
    # Helper methods for formatting data
    def _format_calendar_events(self, events):
        """Format calendar events for prompt
        
        Args:
            events (list): List of calendar events
            
        Returns:
            str: Formatted calendar events
        """
        if not events:
            return "هیچ رویدادی ثبت نشده است"
        
        return ", ".join([f"{event.get('title')} ({event.get('date')})" for event in events[:5]])
    
    def _format_tasks(self, tasks):
        """Format tasks for prompt
        
        Args:
            tasks (list): List of tasks
            
        Returns:
            str: Formatted tasks
        """
        if not tasks:
            return "هیچ وظیفه‌ای ثبت نشده است"
        
        return ", ".join([f"{task.get('title')} (اولویت: {task.get('priority')})" for task in tasks[:5]])
    
    def _format_health_goals(self, goals):
        """Format health goals for prompt
        
        Args:
            goals (list): List of health goals
            
        Returns:
            str: Formatted health goals
        """
        if not goals:
            return "هیچ هدف سلامتی ثبت نشده است"
        
        return ", ".join([f"{goal.get('goal_type')}: {goal.get('target_value')}" for goal in goals[:5]])
    
    def _format_finance_goals(self, goals):
        """Format finance goals for prompt
        
        Args:
            goals (list): List of finance goals
            
        Returns:
            str: Formatted finance goals
        """
        if not goals:
            return "هیچ هدف مالی ثبت نشده است"
        
        return ", ".join([f"{goal.get('title')}: {goal.get('amount')} تومان" for goal in goals[:5]])
    
    def _format_health_data(self, health_data):
        """Format health data for prompt
        
        Args:
            health_data (dict): Health data
            
        Returns:
            str: Formatted health data
        """
        if not health_data:
            return "اطلاعات سلامتی موجود نیست"
        
        metrics = health_data.get('metrics', [])
        exercises = health_data.get('exercises', [])
        goals = health_data.get('goals', [])
        
        result = []
        if metrics:
            latest_metric = metrics[0]
            result.append(f"آخرین اندازه‌گیری: وزن {latest_metric.get('weight')} کیلوگرم")
        
        if exercises:
            result.append(f"ورزش‌های اخیر: {len(exercises)} مورد")
        
        if goals:
            result.append(f"اهداف سلامتی: {len(goals)} مورد")
        
        return ", ".join(result) if result else "اطلاعات سلامتی موجود نیست"
    
    def _format_finance_data(self, finance_data):
        """Format finance data for prompt
        
        Args:
            finance_data (dict): Finance data
            
        Returns:
            str: Formatted finance data
        """
        if not finance_data:
            return "اطلاعات مالی موجود نیست"
        
        transactions = finance_data.get('transactions', [])
        income = sum([t.get('amount', 0) for t in transactions if t.get('type') == 'income'])
        expenses = sum([t.get('amount', 0) for t in transactions if t.get('type') == 'expense'])
        
        result = []
        if transactions:
            result.append(f"تعداد تراکنش‌ها: {len(transactions)}")
        
        if income > 0:
            result.append(f"درآمد: {income:,} تومان")
        
        if expenses > 0:
            result.append(f"هزینه‌ها: {expenses:,} تومان")
        
        return ", ".join(result) if result else "اطلاعات مالی موجود نیست"
    
    def _format_calendar_data(self, calendar_data):
        """Format calendar data for prompt
        
        Args:
            calendar_data (dict): Calendar data
            
        Returns:
            str: Formatted calendar data
        """
        if not calendar_data:
            return "اطلاعات تقویم موجود نیست"
        
        events = calendar_data.get('events', [])
        tasks = calendar_data.get('tasks', [])
        
        result = []
        if events:
            result.append(f"تعداد رویدادها: {len(events)}")
        
        if tasks:
            completed = len([t for t in tasks if t.get('completed', False)])
            result.append(f"وظایف: {len(tasks)} مورد ({completed} انجام شده)")
        
        return ", ".join(result) if result else "اطلاعات تقویم موجود نیست"
    
    # Fallback methods in case of errors
    def _get_fallback_health_advice(self):
        """Get fallback health advice when API fails
        
        Returns:
            str: HTML-formatted fallback health advice
        """
        return """<div dir="rtl" class="advice-container">
            <h3>توصیه‌های سلامتی عمومی</h3>
            <ul>
                <li>روزانه حداقل ۳۰ دقیقه فعالیت بدنی داشته باشید</li>
                <li>حداقل ۸ ساعت خواب منظم در شب داشته باشید</li>
                <li>روزانه ۸ لیوان آب بنوشید</li>
                <li>از مصرف غذاهای فرآوری شده و قند زیاد پرهیز کنید</li>
                <li>حداقل ۵ وعده میوه و سبزیجات در روز مصرف کنید</li>
            </ul>
            <p>توجه: این توصیه‌ها عمومی هستند. برای توصیه‌های دقیق‌تر، اطلاعات سلامتی خود را کامل کنید.</p>
        </div>"""
    
    def _get_fallback_finance_advice(self):
        """Get fallback finance advice when API fails
        
        Returns:
            str: HTML-formatted fallback finance advice
        """
        return """<div dir="rtl" class="advice-container">
            <h3>توصیه‌های مالی عمومی</h3>
            <ul>
                <li>قانون ۵۰/۳۰/۲۰: ۵۰٪ برای نیازهای اساسی، ۳۰٪ برای خواسته‌ها، ۲۰٪ برای پس‌انداز</li>
                <li>صندوق اضطراری معادل ۳ تا ۶ ماه هزینه‌های زندگی ایجاد کنید</li>
                <li>برای خریدهای بزرگ، قانون ۲۴ ساعت را رعایت کنید (قبل از خرید ۲۴ ساعت صبر کنید)</li>
                <li>درآمد و هزینه‌های خود را به طور منظم پیگیری کنید</li>
                <li>بدهی‌های با بهره بالا را در اولویت پرداخت قرار دهید</li>
            </ul>
            <p>توجه: این توصیه‌ها عمومی هستند. برای توصیه‌های دقیق‌تر، اطلاعات مالی خود را کامل کنید.</p>
        </div>"""
    
    def _get_fallback_time_advice(self):
        """Get fallback time management advice when API fails
        
        Returns:
            str: HTML-formatted fallback time management advice
        """
        return """<div dir="rtl" class="advice-container">
            <h3>توصیه‌های مدیریت زمان عمومی</h3>
            <ul>
                <li>تکنیک پومودورو: ۲۵ دقیقه کار متمرکز، ۵ دقیقه استراحت</li>
                <li>قانون ۲ دقیقه: اگر انجام کاری کمتر از ۲ دقیقه طول می‌کشد، همان لحظه انجامش دهید</li>
                <li>ماتریس آیزنهاور: کارها را بر اساس اهمیت و فوریت اولویت‌بندی کنید</li>
                <li>زمان‌های مشخصی برای چک کردن ایمیل و پیام‌ها تعیین کنید</li>
                <li>برنامه روز بعد را شب قبل آماده کنید</li>
            </ul>
            <p>توجه: این توصیه‌ها عمومی هستند. برای توصیه‌های دقیق‌تر، اطلاعات تقویم خود را کامل کنید.</p>
        </div>"""
    
    def _get_fallback_weekly_plan(self):
        """Get fallback weekly plan when API fails
        
        Returns:
            str: HTML-formatted fallback weekly plan
        """
        return """<div dir="rtl" class="advice-container">
            <h3>برنامه هفتگی پیشنهادی</h3>
            <div class="day-container">
                <h4>شنبه</h4>
                <ul>
                    <li>۳۰ دقیقه ورزش صبحگاهی</li>
                    <li>برنامه‌ریزی کارهای هفته</li>
                    <li>رسیدگی به ایمیل‌ها و پیام‌ها</li>
                </ul>
            </div>
            <div class="day-container">
                <h4>یکشنبه</h4>
                <ul>
                    <li>۳۰ دقیقه پیاده‌روی</li>
                    <li>کارهای با اولویت بالا</li>
                    <li>بررسی وضعیت مالی هفتگی</li>
                </ul>
            </div>
            <div class="day-container">
                <h4>دوشنبه تا چهارشنبه</h4>
                <ul>
                    <li>۳۰-۴۵ دقیقه ورزش</li>
                    <li>رسیدگی به کارهای روزانه</li>
                    <li>یک ساعت برای یادگیری مهارت جدید</li>
                </ul>
            </div>
            <div class="day-container">
                <h4>پنج‌شنبه</h4>
                <ul>
                    <li>۳۰ دقیقه ورزش</li>
                    <li>جمع‌بندی کارهای هفته</li>
                    <li>برنامه‌ریزی برای هفته آینده</li>
                </ul>
            </div>
            <div class="day-container">
                <h4>جمعه</h4>
                <ul>
                    <li>استراحت و تفریح</li>
                    <li>گذراندن وقت با خانواده و دوستان</li>
                    <li>فعالیت‌های مورد علاقه</li>
                </ul>
            </div>
            <p>توجه: این برنامه عمومی است. برای برنامه شخصی‌سازی شده، اطلاعات تقویم خود را کامل کنید.</p>
        </div>"""
    
    def _get_fallback_yearly_goals(self):
        """Get fallback yearly goals when API fails
        
        Returns:
            str: HTML-formatted fallback yearly goals
        """
        return """<div dir="rtl" class="advice-container">
            <h3>اهداف سالانه پیشنهادی</h3>
            <div class="goals-section">
                <h4>اهداف سلامتی</h4>
                <ul>
                    <li>ورزش منظم (حداقل ۳ روز در هفته، ۳۰ دقیقه)</li>
                    <li>بهبود کیفیت خواب (خواب منظم ۷-۸ ساعته)</li>
                    <li>افزایش مصرف آب و سبزیجات</li>
                </ul>
            </div>
            <div class="goals-section">
                <h4>اهداف مالی</h4>
                <ul>
                    <li>ایجاد صندوق اضطراری</li>
                    <li>پس‌انداز حداقل ۱۰٪ از درآمد ماهانه</li>
                    <li>کاهش هزینه‌های غیرضروری</li>
                </ul>
            </div>
            <div class="goals-section">
                <h4>اهداف شخصی و حرفه‌ای</h4>
                <ul>
                    <li>یادگیری یک مهارت جدید</li>
                    <li>مطالعه حداقل ۱۲ کتاب در سال</li>
                    <li>گذراندن وقت با کیفیت با خانواده و دوستان</li>
                </ul>
            </div>
            <p>توجه: این اهداف عمومی هستند. برای اهداف شخصی‌سازی شده، اطلاعات خود را کامل کنید.</p>
        </div>"""