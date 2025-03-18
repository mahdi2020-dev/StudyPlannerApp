import os
from supabase import create_client

# دریافت متغیرهای محیطی
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# بررسی مقدار متغیرها
if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ خطا: SUPABASE_URL یا SUPABASE_KEY تعریف نشده!")
else:
    # اتصال به Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    try:
        response = supabase.table("users").select("*").limit(5).execute()
        print("✅ اتصال موفق! نمونه داده‌ها:", response.data)
    except Exception as e:
        print("❌ خطا در اتصال:", e)